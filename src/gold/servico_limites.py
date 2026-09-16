import logging
from pathlib import Path
from typing import Any
import pandas as pd
from datetime import datetime

from control.logger import obter_logger

def exportar_arquivo_limites(context: Any) -> dict[str, Any]:
    run_id = f"LIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold.limites", Path("LOGS/gold") / f"{run_id}__exportacao_limites.log")
    logger.info("Iniciando geração do arquivo de exportação de limites...")
    
    gold_dir = context.path("saidas") / "gold" / "visao_operacional_negocio"
    path_gold = gold_dir / "Visao_Operacional_BDC_LATEST.parquet"
    
    if not path_gold.exists():
        logger.error("Visão Gold LATEST não encontrada. O arquivo de limites não será gerado.")
        return {"status": "ERRO", "mensagem": "Visão Gold não encontrada."}
        
    df_gold = pd.read_parquet(path_gold)
    
    # 1. Filtrar registros inválidos
    df_limites = df_gold[df_gold["CNPJ"].notna() & (df_gold["CNPJ"] != "")].copy()
    
    # 2. Mapeamento de colunas exigido pela Seção 7.3 do Planejamento Funcional
    mapa_colunas = {
        "NOME": "Nome do agente",
        "CNPJ": "CNPJ",
        "METODOLOGIA_EXIGIDA": "Tipo",
        "PATRIMONIO_LIQUIDO": "Patrimônio líquido",
        "PATRIMONIO_LIQUIDO_AJUSTADO": "Patrimônio líquido ajustado",
        "RATING_FINAL": "Rating",
        "DATA_DA_ANALISE": "Data da DF",
        "CONTRAPARTE_ID": "contraparte_id",
        "ANALISE_ID": "analise_id",
        "DATA_GERACAO": "data de geração",
        "VERSAO_LAYOUT_LIMITE": "versão do layout",
        "RUN_ID": "run_id",
        "STATUS_CONTRATUAL": "possui_contrato_corrente_copel",
        "VOLUME_MWM": "volume_enquadramento_mwm",
        "METODOLOGIA_EXIGIDA": "segmento_metodologico",
        "FONTE_VOLUME": "fonte_volume",
        "DATA_REFERENCIA_VOLUME": "data_referencia_volume",
        "SITUACAO_DF": "situacao_df",
        "MOTIVO_AUSENCIA_DF": "motivo_ausencia_df",
        "ORIGEM_ANALISE": "origem_analise",
        "INDICADOR_DADO_MANUAL": "indicador_dado_manual",
        "VALIDADE_EXCECAO": "validade_excecao"
    }
    
    for col_origem in mapa_colunas.keys():
        if col_origem not in df_limites.columns:
            logger.warning(f"Coluna {col_origem} ausente na Gold. Preenchendo com Nulo.")
            df_limites[col_origem] = pd.NA
            
    df_limites["STATUS_CONTRATUAL"] = df_limites["STATUS_CONTRATUAL"].apply(lambda x: True if str(x) in ["CONTRATO_VIGENTE"] else False)
    
    df_interface = df_limites[list(mapa_colunas.keys())].rename(columns=mapa_colunas)
    
    if "segmento_metodologico" not in df_interface.columns and "METODOLOGIA_EXIGIDA" in df_limites.columns:
        df_interface["segmento_metodologico"] = df_limites["METODOLOGIA_EXIGIDA"]
        
    if "Tipo" not in df_interface.columns and "METODOLOGIA_EXIGIDA" in df_limites.columns:
        df_interface["Tipo"] = df_limites["METODOLOGIA_EXIGIDA"]
    
    colunas_data = ["Data da DF", "data de geração", "data_referencia_volume", "validade_excecao"]
    for col in colunas_data:
        if col in df_interface.columns:
            df_interface[col] = pd.to_datetime(df_interface[col], errors='coerce').dt.strftime('%Y-%m-%d')
            df_interface[col] = df_interface[col].replace('NaT', pd.NA)

    output_dir = context.path("saidas") / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    hoje = datetime.now()
    nome_arquivo = f"entrada_limites_credito_{hoje.strftime('%Y%m%d')}.xlsx"
    out_excel = output_dir / nome_arquivo
    out_latest = output_dir / "entrada_limites_credito_LATEST.xlsx"
    
    try:
        df_interface.to_excel(out_excel, index=False, engine="openpyxl")
        df_interface.to_excel(out_latest, index=False, engine="openpyxl")
        logger.info(f"Arquivo de limites exportado com sucesso: {out_excel}")
    except Exception as e:
        logger.error(f"Falha ao escrever Excel de limites: {e}")
        out_csv = output_dir / f"entrada_limites_credito_{hoje.strftime('%Y%m%d')}.csv"
        df_interface.to_csv(out_csv, index=False, sep=";", encoding="utf-8-sig")

    return {
        "status": "SUCESSO",
        "registros_limite": len(df_interface),
        "arquivo": str(out_excel)
    }
