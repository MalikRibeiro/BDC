import pandas as pd
from pathlib import Path
from common.excel import abrir_pasta, fechar_pasta
from common.json import ler_json
from domain.fichas.extrator import extrair_registro_do_vencedor
import glob
import os
from control.logger import obter_logger
from datetime import datetime

def _encontrar_ficha_bronze(cnpj: str, base_dir: Path) -> Path | None:
    """Busca o arquivo mais recente da ficha na camada Bronze para um CNPJ."""
    # A estrutura bronze geralmente tem o CNPJ na pasta ou no nome do arquivo
    # Vamos buscar iterativamente (sem assumir a estrutura profunda de pastas)
    bronze_dir = base_dir / "SAIDAS" / "bronze"
    if not bronze_dir.exists():
        return None
        
    cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
    if not cnpj_limpo:
        return None
        
    candidatos = []
    # Busca recursiva rápida apenas nas pastas raw
    for raw_dir in ["fichas_comercializadoras_raw", "fichas_consumidores_raw"]:
        search_path = bronze_dir / raw_dir
        if search_path.exists():
            for root, _, files in os.walk(search_path):
                for file in files:
                    if cnpj_limpo in file.replace(".", "").replace("-", "").replace("/", ""):
                        candidatos.append(Path(root) / file)
                        
    if not candidatos:
        return None
        
    # Ordena pelo tempo de modificação para pegar a mais recente
    candidatos.sort(key=os.path.getmtime, reverse=True)
    return candidatos[0]

def _carregar_layouts_dinamico(base_dir: Path, is_comercializadora: bool) -> dict:
    """Carrega os layouts sem precisar do AppContext completo."""
    layouts = {}
    control_dir = base_dir / "ENTRADAS" / "control" / "layouts"
    prefix = "layout_ficha_comercializadora" if is_comercializadora else "layout_ficha_consumidor"
    max_ver = 7 if is_comercializadora else 3
    
    for v in range(1, max_ver + 1):
        file_path = control_dir / f"{prefix}_v{v}.json"
        if file_path.exists():
            k = f"padrao_{v}" if is_comercializadora else f"v{v}"
            layouts[k] = ler_json(file_path)
            
    return layouts

def recuperar_pendencias_automaticamente(base_dir: str = ".") -> None:
    """Tenta recuperar dados ausentes re-executando a extração nas fichas Bronze."""
    base_path = Path(base_dir)
    data_atual = datetime.now().strftime("%Y%m%d")
    log_path = base_path / "LOGS" / "atualizacoes_manuais" / f"UI_MANUAL_{data_atual}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = obter_logger("bdc.ui.carga_manual.recuperacao", log_path)
    
    fila_path = base_path / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico" / "fila_pendencias.csv"
    
    if not fila_path.exists():
        logger.warning("Fila de pendências não encontrada.")
        return
        
    df = pd.read_csv(fila_path, sep=";")
    if df.empty:
        logger.info("Fila vazia. Nada a recuperar.")
        return
        
    logger.info("Iniciando tentativa de recuperação automática de %d pendências possíveis...", len(df))
        
    # Carrega catálogos
    cat_com = ler_json(base_path / "ENTRADAS" / "control" / "quality" / "master_catalog_comercializadoras.json")
    cat_cons = ler_json(base_path / "ENTRADAS" / "control" / "quality" / "master_catalog_consumidores.json")
    
    layouts_com = _carregar_layouts_dinamico(base_path, True)
    layouts_cons = _carregar_layouts_dinamico(base_path, False)
    
    recuperados = 0

    for idx, row in df.iterrows():
        if row["STATUS"] != "PENDENTE":
            continue
            
        cnpj = str(row["CNPJ"])
        campo = str(row["CAMPO_FALTANTE"])
        
        ficha_path = _encontrar_ficha_bronze(cnpj, base_path)
        if not ficha_path:
            continue
            
        is_comercializadora = "comercializadoras" in str(ficha_path)
        layouts = layouts_com if is_comercializadora else layouts_cons
        master_catalog = cat_com if is_comercializadora else cat_cons
        
        workbook = None
        try:
            workbook = abrir_pasta(ficha_path)
            raw_record, _, _ = extrair_registro_do_vencedor(workbook, layouts, master_catalog)
            
            valor_extraido = raw_record.get(campo)
            if valor_extraido is not None and str(valor_extraido).strip() != "":
                df.at[idx, "STATUS"] = "RECUPERADO_AUTOMATICAMENTE"
                df.at[idx, "VALOR_RECUPERADO"] = valor_extraido
                recuperados += 1
                
        except Exception:
            pass
        finally:
            if workbook:
                fechar_pasta(workbook)

    df.to_csv(fila_path, index=False, sep=";")
    logger.info("Recuperação automática concluída. %d valores resgatados da Bronze.", recuperados)
