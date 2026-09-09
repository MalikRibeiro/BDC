import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import os
from control.logger import obter_logger
from common.identificadores import normalizar_cnpj
from domain.diagnostico.servico_recuperacao import _encontrar_ficha_bronze

def _carregar_catalogo(catalog_path: Path) -> list[str]:
    """Retorna a lista de campos obrigatórios do catálogo JSON."""
    if not catalog_path.exists():
        return []
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    
    campos_obrigatorios = []
    fields = catalog.get("fields", {})
    for field_name, config in fields.items():
        if config.get("nature") == "DERIVED":
            continue
        if config.get("criticality") in ["GATE_ENGINE", "REQUIRED_FOR_CALCULATION"]:
            campos_obrigatorios.append(field_name)
            
    return campos_obrigatorios

def gerar_diagnostico(base_dir: str = ".") -> None:
    """Lê a Silver e gera a fila de pendências CSV."""
    base_path = Path(base_dir)
    data_atual = datetime.now().strftime("%Y%m%d")
    log_path = base_path / "LOGS" / "atualizacoes_manuais" / f"UI_MANUAL_{data_atual}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = obter_logger("bdc.ui.carga_manual.diagnostico", log_path)
    
    logger.info("Iniciando varredura da Silver para detecção de pendências...")
    
    saidas_dir = base_path / "SAIDAS"
    entradas_dir = base_path / "ENTRADAS"
    
    diagnostico_dir = base_path / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico"
    diagnostico_dir.mkdir(parents=True, exist_ok=True)
    
    fila_pendencias_path = diagnostico_dir / "fila_pendencias.csv"
    
    # Catálogos
    catalog_comercializadoras = entradas_dir / "control" / "quality" / "master_catalog_comercializadoras.json"
    catalog_consumidores = entradas_dir / "control" / "quality" / "master_catalog_consumidores.json"
    
    campos_com = _carregar_catalogo(catalog_comercializadoras)
    campos_cons = _carregar_catalogo(catalog_consumidores)
    
    pendencias = []
    
    # Comercializadoras
    silver_com_path = saidas_dir / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    if not silver_com_path.exists():
        silver_com_path = saidas_dir / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.csv"
        
    if silver_com_path.exists():
        if silver_com_path.suffix == '.csv':
            df_com = pd.read_csv(silver_com_path, sep=';', encoding='utf-8-sig')
        else:
            df_com = pd.read_parquet(silver_com_path)
            
        # Remove eventuais caracteres de BOM (Byte Order Mark) que corrompem o nome da primeira coluna (ex: \ufeffCNPJ)
        df_com.columns = [str(col).replace('\ufeff', '').strip() for col in df_com.columns]
            
        for _, row in df_com.iterrows():
            res_cnpj = normalizar_cnpj(row.get("CNPJ", ""))
            cnpj = res_cnpj.cnpj if res_cnpj.cnpj else str(row.get("CNPJ", ""))
            data_df = str(row.get("DATA_DEMONSTRACAO_FINANCEIRA", ""))
            empresa = str(row.get("SIGLA", row.get("EMPRESA", "")))
            ficha_path = _encontrar_ficha_bronze(cnpj, base_path)
            arquivo_str = str(ficha_path) if ficha_path else "Arquivo não localizado na Bronze"
            
            for campo in campos_com:
                val = row.get(campo)
                if pd.isna(val) or val is None or str(val).strip() == "":
                    pendencias.append({
                        "CNPJ": cnpj,
                        "DATA_DEMONSTRACAO_FINANCEIRA": data_df,
                        "EMPRESA": empresa,
                        "CAMPO_FALTANTE": campo,
                        "STATUS": "PENDENTE",
                        "ARQUIVO_ORIGEM": arquivo_str
                    })
                    
    # Consumidores
    silver_cons_path = saidas_dir / "silver" / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet"
    if not silver_cons_path.exists():
        silver_cons_path = saidas_dir / "silver" / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.csv"
        
    if silver_cons_path.exists():
        if silver_cons_path.suffix == '.csv':
            df_cons = pd.read_csv(silver_cons_path, sep=';', encoding='utf-8-sig')
        else:
            df_cons = pd.read_parquet(silver_cons_path)
            
        df_cons.columns = [str(col).replace('\ufeff', '').strip() for col in df_cons.columns]
            
        for _, row in df_cons.iterrows():
            res_cnpj = normalizar_cnpj(row.get("CNPJ", ""))
            cnpj = res_cnpj.cnpj if res_cnpj.cnpj else str(row.get("CNPJ", ""))
            data_df = str(row.get("DATA_DEMONSTRACAO_FINANCEIRA", ""))
            empresa = str(row.get("EMPRESA", ""))
            ficha_path = _encontrar_ficha_bronze(cnpj, base_path)
            arquivo_str = str(ficha_path) if ficha_path else "Arquivo não localizado na Bronze"
            
            for campo in campos_cons:
                val = row.get(campo)
                if pd.isna(val) or val is None or str(val).strip() == "":
                    pendencias.append({
                        "CNPJ": cnpj,
                        "DATA_DEMONSTRACAO_FINANCEIRA": data_df,
                        "EMPRESA": empresa,
                        "CAMPO_FALTANTE": campo,
                        "STATUS": "PENDENTE",
                        "ARQUIVO_ORIGEM": arquivo_str
                    })

    df_pendencias = pd.DataFrame(pendencias)
    if not df_pendencias.empty:
        # Remover duplicadas caso haja o mesmo CNPJ+DATA+CAMPO
        df_pendencias = df_pendencias.drop_duplicates(subset=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "CAMPO_FALTANTE"])
    else:
        df_pendencias = pd.DataFrame(columns=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA", "CAMPO_FALTANTE", "STATUS", "ARQUIVO_ORIGEM"])

    df_pendencias.to_csv(fila_pendencias_path, index=False, sep=";")
    logger.info("Diagnóstico concluído. %d pendências identificadas.", len(df_pendencias))
