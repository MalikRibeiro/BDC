import logging
from pathlib import Path
from typing import Any
import pandas as pd
from datetime import datetime

from common.dados import validar_coluna_cnpj_canonica
from control.logger import obter_logger
from gold.regras_gold import (
    resolver_situacao_df,
    resolver_situacao_analise,
    classificar_exigencia,
    status_metodologia,
    checar_contrato_obrigatorio
)

def carregar_entradas_gold(context: Any, logger: logging.Logger) -> dict[str, pd.DataFrame]:
    silver_dir = context.path("silver")
    rel_dim_dir = context.path("relational_dimensions")
    rel_fact_dir = context.path("relational_facts")
    
    path_contraparte = rel_dim_dir / "contrapartes" / "dim_contraparte.parquet"
    path_contratos = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_contratos.exists():
        path_contratos = silver_dir / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
        
    path_risco = rel_fact_dir / "risco" / "fato_exposicao_risco_LATEST.parquet"
    if not path_risco.exists():
        path_risco = silver_dir / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"

    path_analises = rel_fact_dir / "credito" / "fato_analise_credito.parquet"
    path_eventos_manuais = silver_dir / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"

    if not path_contraparte.exists():
        logger.error(f"Fonte obrigatória ausente: {path_contraparte}")
        raise FileNotFoundError(f"Fonte obrigatória ausente: {path_contraparte}. A dimensão de contraparte deve existir.")
    df_contraparte = pd.read_parquet(path_contraparte)

    if path_contratos.exists():
        df_contratos = pd.read_parquet(path_contratos)
    else:
        logger.warning(f"Base opcional de contratos ausente: {path_contratos}. Prosseguindo sem contratos.")
        df_contratos = pd.DataFrame()

    if path_analises.exists():
        df_analises = pd.read_parquet(path_analises)
    else:
        logger.warning(f"Base opcional de análises ausente: {path_analises}. Prosseguindo sem análises.")
        df_analises = pd.DataFrame()

    if path_risco.exists():
        df_risco = pd.read_parquet(path_risco)
    else:
        logger.warning(f"Base opcional de risco ausente: {path_risco}. Prosseguindo sem risco.")
        df_risco = pd.DataFrame()

    path_reconciliacao = rel_fact_dir / "reconciliacao" / "fato_reconciliacao_contrato_mtm.parquet"
    if path_reconciliacao.exists():
        df_reconciliacao = pd.read_parquet(path_reconciliacao)
    else:
        logger.warning(f"Base de reconciliação ausente: {path_reconciliacao}. Prosseguindo sem reconciliação.")
        df_reconciliacao = pd.DataFrame()

    if path_eventos_manuais.exists():
        df_eventos = pd.read_parquet(path_eventos_manuais)
    else:
        df_eventos = pd.DataFrame()

    path_bureau = silver_dir / "fato_bureau_silver" / "fato_bureau_silver.parquet"
    if path_bureau.exists():
        df_bureau = pd.read_parquet(path_bureau)
    else:
        df_bureau = pd.DataFrame()

    return {
        "contraparte": df_contraparte,
        "contratos": df_contratos,
        "analises": df_analises,
        "risco": df_risco,
        "eventos": df_eventos,
        "bureau": df_bureau,
        "reconciliacao": df_reconciliacao
    }

def salvar_visao_gold(context: Any, df_gold: pd.DataFrame, hoje: datetime, run_id: str, logger: logging.Logger):
    gold_dir = context.path("saidas") / "gold" / "visao_operacional_negocio"
    gold_dir.mkdir(parents=True, exist_ok=True)
    
    # Prevenção e correção de Nulos Literais vazados por astype(str)
    df_gold = df_gold.replace(["None", "nan", "<NA>", "NaN", "NaT", "N/A"], pd.NA)
    
    out_parquet = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.parquet"
    out_latest = gold_dir / "Visao_Operacional_BDC_LATEST.parquet"
    out_csv = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.csv"
    out_latest_csv = gold_dir / "Visao_Operacional_BDC_LATEST.csv"
    
    df_gold.to_parquet(out_parquet, index=False)
    df_gold.to_parquet(out_latest, index=False)
    df_gold.to_csv(out_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    df_gold.to_csv(out_latest_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

    logger.info("Visão Gold gerada. Total Contrapartes consolidadas: %d", len(df_gold))

def construir_visao_consolidada(dfs: dict[str, pd.DataFrame], run_id: str, hoje: datetime) -> pd.DataFrame:
    df_contraparte = dfs["contraparte"]
    df_contratos = dfs["contratos"]
    df_analises = dfs["analises"]
    df_risco = dfs["risco"]
    df_eventos = dfs.get("eventos", pd.DataFrame())
    df_bureau = dfs.get("bureau", pd.DataFrame())
    df_reconciliacao = dfs.get("reconciliacao", pd.DataFrame())

    if df_contraparte.empty:
        raise ValueError("O DataFrame obrigatório 'contraparte' não pode estar vazio.")

    erros = validar_coluna_cnpj_canonica(df_contraparte)
    if erros:
        raise ValueError("Dataset Silver fora do contrato (contraparte): " + "; ".join(erros))
    
    checar_contrato_obrigatorio(df_contraparte, ["CNPJ"], "contraparte")
    
    cols_contra = [c for c in ["CNPJ", "CNPJ_RAIZ", "SIGLA", "NOME", "SEGMENTO_METODOLOGICO", "SITUACAO_CADASTRAL"] if c in df_contraparte.columns]
    df_gold = df_contraparte[cols_contra].copy()

    # 1. Integrar Contratos (Denodo e Volume Enquadramento)
    from gold.servico_contratos import integrar_contratos_gold
    df_gold = integrar_contratos_gold(df_gold, df_contratos, hoje)

    # 2. Integrar Análises de Crédito (PD, Rating, Validades)
    from gold.servico_analises import integrar_analises_gold, integrar_bureau_gold
    df_gold = integrar_analises_gold(df_gold, df_analises, hoje)

    # 3. Integrar Risco e Reconciliação (MtM)
    from gold.servico_risco import integrar_risco_gold
    df_gold = integrar_risco_gold(df_gold, df_risco, df_reconciliacao)

    # 4. Finalização e Regras de Negócio Básicas
    colunas_esperadas = [
        "VOLUME_MWM", "EAD_VALOR", "PE_REAIS", "PATRIMONIO_LIQUIDO", "QUANTIDADE_CONTRATOS", 
        "STATUS_CONTRATUAL", "SITUACAO_ANALISE", "SITUACAO_DF", "SITUACAO_CADASTRAL"
    ]
    for col in colunas_esperadas:
        if col not in df_gold.columns:
            logging.warning("Coluna esperada '%s' ausente no DataFrame Gold. Preenchida com fallback pd.NA.", col)
            df_gold[col] = pd.NA

    df_gold["STATUS_CONTRATUAL"] = df_gold["STATUS_CONTRATUAL"].fillna("SEM_CONTRATO")
    df_gold["SITUACAO_CADASTRAL"] = df_gold["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADA")

    df_gold["SITUACAO_DF"] = df_gold.apply(resolver_situacao_df, axis=1)
    df_gold["SITUACAO_ANALISE"] = df_gold.apply(resolver_situacao_analise, axis=1)
    df_gold["METODOLOGIA_EXIGIDA"] = df_gold.apply(classificar_exigencia, axis=1)
    df_gold["STATUS_METODOLOGIA"] = df_gold.apply(status_metodologia, axis=1)

    df_gold["CONTRAPARTE_ID"] = df_gold["CNPJ"].apply(lambda x: f"CPT_{x}")
    df_gold["ANALISE_ID"] = df_gold.apply(
        lambda row: f"ANA_{row['CNPJ']}_{str(row.get('DATA_ANALISE', '')).replace('-','')}" if row.get("TEM_ANALISE") == "SIM" and pd.notna(row.get("DATA_ANALISE")) else pd.NA, axis=1
    )
    df_gold["RUN_ID"] = run_id
    df_gold["REVISAO_LIMITE"] = (df_gold["STATUS_METODOLOGIA"] != "COMPLIANT")
    df_gold["DATA_GERACAO"] = hoje
    df_gold["VERSAO_LAYOUT_LIMITE"] = "v1.2"
    df_gold["FONTE_VOLUME"] = "DENODO_CONTRATOS"
    df_gold["DATA_REFERENCIA_VOLUME"] = hoje

    if "MOTIVO_AUSENCIA_DF" not in df_gold.columns:
        df_gold["MOTIVO_AUSENCIA_DF"] = df_gold["SITUACAO_DF"].apply(lambda x: "NAO_ENVIADA_PELA_CONTRAPARTE" if x == "NAO_RECEBIDA" else pd.NA)

    # 5. Aplicar Eventos Manuais (Overrides)
    from gold.servico_eventos_manuais import integrar_eventos_manuais_gold
    df_gold = integrar_eventos_manuais_gold(df_gold, df_eventos)

    if "ORIGEM_ANALISE" not in df_gold.columns:
        if "ORIGEM_REGISTRO" in df_gold.columns:
            df_gold["ORIGEM_ANALISE"] = df_gold["ORIGEM_REGISTRO"].fillna("FICHA")
        else:
            df_gold["ORIGEM_ANALISE"] = "FICHA"
    else:
        df_gold["ORIGEM_ANALISE"] = df_gold["ORIGEM_ANALISE"].fillna(
            df_gold["ORIGEM_REGISTRO"] if "ORIGEM_REGISTRO" in df_gold.columns else "FICHA"
        )

    if "VALIDADE_EXCECAO" not in df_gold.columns:
        df_gold["VALIDADE_EXCECAO"] = pd.NaT

    if "PATRIMONIO_LIQUIDO" in df_gold.columns:
        df_gold["PATRIMONIO_LIQUIDO_AJUSTADO"] = df_gold["PATRIMONIO_LIQUIDO"]
    else:
        df_gold["PATRIMONIO_LIQUIDO_AJUSTADO"] = pd.NA

    # 6. Integrar Bureau RISK3 (Local e Herança)
    df_gold = integrar_bureau_gold(df_gold, df_bureau)

    df_gold["DATA_DA_ANALISE"] = pd.NA
    if "DATA_BALANCO_USADO" in df_gold.columns:
        df_gold["DATA_DA_ANALISE"] = df_gold["DATA_BALANCO_USADO"]
        
    if "METODOLOGIA_EXIGIDA" in df_gold.columns and "DATA_CONSULTA" in df_gold.columns:
        mask_bureau = df_gold["METODOLOGIA_EXIGIDA"] == "BUREAU"
        df_gold.loc[mask_bureau, "DATA_DA_ANALISE"] = df_gold.loc[mask_bureau, "DATA_CONSULTA"]

    # A Herança de Controladoras agora ocorre nativamente na Camada Relacional (fato_analise_credito)
    # garantindo o Single Source of Truth para todas as visões.

    return df_gold

def exportar_visao_consolidada_gold(context: Any) -> dict[str, Any]:
    run_id = f"GOLD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold", Path("LOGS/gold") / f"{run_id}__service_gold.log")
    logger.info("Construindo Visão Consolidada Gold (Master Join)...")
    hoje = pd.Timestamp("today").normalize()

    dfs = carregar_entradas_gold(context, logger)
    df_gold = construir_visao_consolidada(dfs, run_id, hoje)
    
    salvar_visao_gold(context, df_gold, hoje, run_id, logger)

    sit_analise = df_gold["SITUACAO_ANALISE"].fillna("").astype(str)
    met_exigida  = df_gold["METODOLOGIA_EXIGIDA"].fillna("").astype(str)
    stat_ctr     = df_gold["STATUS_CONTRATUAL"].fillna("").astype(str)

    mask_descoberto     = (stat_ctr == "CONTRATO_VIGENTE") & (sit_analise != "VIGENTE")
    mask_irregular      = (stat_ctr == "CONTRATO_VIGENTE") & (met_exigida == "DF_DETALHADA") & (sit_analise != "VIGENTE")
    mask_pendente_bureau = (stat_ctr == "CONTRATO_VIGENTE") & (met_exigida == "BUREAU")      & (sit_analise != "VIGENTE")

    return {
        "status": "SUCESSO",
        "total_contrapartes": len(df_gold),
        "contrato_vigente": int((df_gold["STATUS_CONTRATUAL"] == "CONTRATO_VIGENTE").sum()),
        "contrato_futuro": int((df_gold["STATUS_CONTRATUAL"] == "CONTRATO_FUTURO").sum()),
        "analise_vigente": int((df_gold["SITUACAO_ANALISE"].fillna("").astype(str) == "VIGENTE").sum()),
        "analise_vencida": int((df_gold["SITUACAO_ANALISE"].fillna("").astype(str) == "VENCIDA").sum()),
        "contrato_vig_sem_analise_vig": int(mask_descoberto.sum()),
        "contrato_irregular_sem_df": int(mask_irregular.sum()),
        "contrato_pendente_bureau": int(mask_pendente_bureau.sum()),
        "ficha_sem_contrato": int(((df_gold["TEM_ANALISE"] == "SIM") & (df_gold["STATUS_CONTRATUAL"] == "SEM_CONTRATO")).sum()),
        "contrato_sem_ficha": int(((df_gold["STATUS_CONTRATUAL"].isin(["CONTRATO_VIGENTE", "CONTRATO_FUTURO"])) & (df_gold["TEM_ANALISE"] == "NÃO")).sum()),
        "dados_incompletos": int((df_gold["SITUACAO_CADASTRAL"].isin(["NAO_INFORMADA", "PENDENTE"])).sum()),
        "ead_descoberto": float(df_gold.loc[mask_irregular, "EAD_VALOR"].sum(skipna=True)) if "EAD_VALOR" in df_gold.columns else 0.0,
    }