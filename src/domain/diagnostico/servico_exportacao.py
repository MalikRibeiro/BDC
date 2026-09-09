import pandas as pd
from pathlib import Path
from datetime import datetime
from control.logger import obter_logger
from common.identificadores import normalizar_cnpj

def exportar_carga_manual(base_dir: str = ".") -> bool:
    """Exporta o rascunho para a pasta de atualizações manuais no formato oficial."""
    base_path = Path(base_dir)
    data_atual = datetime.now().strftime("%Y%m%d")
    log_path = base_path / "LOGS" / "atualizacoes_manuais" / f"UI_MANUAL_{data_atual}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = obter_logger("bdc.ui.carga_manual.exportacao", log_path)
    
    rascunho_path = base_path / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico" / "rascunho_carga_manual.csv"
    
    if not rascunho_path.exists():
        logger.warning("Rascunho não encontrado. Abortando exportação.")
        return False
        
    df = pd.read_csv(rascunho_path, sep=";")
    if df.empty:
        logger.warning("Rascunho vazio. Abortando exportação.")
        return False
        
    logger.info("Iniciando exportação de %d pendências do rascunho...", len(df))
        
    registros_carga = []
    
    for _, row in df.iterrows():
        # Converte para o Schema de Carga Manual
        # schema_carga_manual.json keys: CNPJ, DATA_DEMONSTRACAO_FINANCEIRA, CAMPO_AFETADO, 
        # VALOR_NOVO, MOTIVO, SOLICITANTE, TIPO_EVENTO, EVIDENCIA
        res_cnpj = normalizar_cnpj(row.get("CNPJ"))
        cnpj_norm = res_cnpj.cnpj if res_cnpj.cnpj else row.get("CNPJ")
        
        reg = {
            "CNPJ": cnpj_norm,
            "DATA_DEMONSTRACAO_FINANCEIRA": row.get("DATA_DEMONSTRACAO_FINANCEIRA"),
            "CAMPO_AFETADO": row.get("CAMPO_FALTANTE"),
            "VALOR_NOVO": row.get("VALOR_NOVO"),
            "MOTIVO": row.get("MOTIVO", "Complementação Assistida"),
            "SOLICITANTE": row.get("SOLICITANTE", "Operador de Qualidade"),
            "TIPO_EVENTO": row.get("TIPO_EVENTO", "COMPLEMENTACAO"),
            "EVIDENCIA": row.get("FONTE", "Desconhecida")
        }
        registros_carga.append(reg)
        
    df_export = pd.DataFrame(registros_carga)
    
    data_hoje = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = base_path / "ENTRADAS" / "atualizacoes_manuais" / "pendentes"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    export_path = export_dir / f"carga_manual_assistida_{data_hoje}.xlsx"
    
    # Força CNPJ como texto para evitar notação científica no Excel
    df_export["CNPJ"] = df_export["CNPJ"].astype(str)
    
    # Grava final
    df_export.to_excel(export_path, index=False, engine="openpyxl")
    logger.info("Carga manual gerada com sucesso: %s", export_path)
    
    # Limpa o rascunho após gerar
    rascunho_path.unlink()
    logger.info("Contrato Efêmero cumprido: Rascunho temporário excluído permanentemente.")
    
    return True
