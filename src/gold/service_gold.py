# -*- coding: utf-8 -*-
"""
Serviço da Camada Gold.
Responsável por realizar o Master Join entre Contratos (Denodo), Fichas (Análise), Risco (MtM), e Cadastro.
Aplica as agregações mensais de volume e regras de negócio temporais para criar a Tabela Analítica Oficial.
"""

import logging
from pathlib import Path
from typing import Any
import pandas as pd
from datetime import datetime

from silver.normalizadores import padronizar_cnpj

LOGGER = logging.getLogger(__name__)

def exportar_visao_consolidada_gold(context: Any) -> dict[str, Any]:
    logger = logging.getLogger("bdc.gold")
    logger.info("Construindo Visão Consolidada Gold (Master Join)...")
    hoje = pd.Timestamp("today").normalize()

    # 1. Resolução de Caminhos (Paths)
    silver_dir = Path("SAIDAS/silver")
    rel_dim_dir = Path("SAIDAS/relational/dimensions")
    rel_fact_dir = Path("SAIDAS/relational/facts")
    gold_dir = Path("SAIDAS/gold/visao_operacional_negocio")
    gold_dir.mkdir(parents=True, exist_ok=True)

    path_contraparte = rel_dim_dir / "dim_contraparte.parquet"
    path_contratos = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_contratos.exists():
        path_contratos = silver_dir / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
        
    path_risco = rel_fact_dir / "fato_exposicao_risco_LATEST.parquet"
    if not path_risco.exists():
        path_risco = silver_dir / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"

    path_analises = rel_fact_dir / "fato_analise_credito.parquet"
    
    # Bloqueio de Falha Segura
    if not path_contratos.exists():
        logger.critical("Bloqueio de Falha Segura: Base Silver de contratos não encontrada (%s).", path_contratos)
        raise FileNotFoundError(f"Base crítica de contratos inexistente na Silver: {path_contratos}")

    # 2. Carregamento dos Datasets
    df_contraparte = pd.read_parquet(path_contraparte) if path_contraparte.exists() else pd.DataFrame()
    df_contratos = pd.read_parquet(path_contratos) if path_contratos.exists() else pd.DataFrame()
    df_analises = pd.read_parquet(path_analises) if path_analises.exists() else pd.DataFrame()
    df_risco = pd.read_parquet(path_risco) if path_risco.exists() else pd.DataFrame()

    # 3. Master Join (Âncora na Dimensão Contraparte para garantir volumetria total)
    if not df_contraparte.empty:
        parsed_ct = df_contraparte["CNPJ"].map(padronizar_cnpj)
        df_contraparte["CNPJ"]      = parsed_ct.map(lambda t: t[0])
        df_contraparte["CNPJ_RAIZ"] = parsed_ct.map(lambda t: t[1])
        df_contraparte = df_contraparte[parsed_ct.map(lambda t: t[2]) == "CNPJ_VALIDO"]
        cols_contra = [c for c in ["CNPJ", "CNPJ_RAIZ", "SIGLA", "NOME", "SEGMENTO_METODOLOGICO", "SITUACAO_CADASTRAL"] if c in df_contraparte.columns]
        df_gold = df_contraparte[cols_contra].copy()
    else:
        df_gold = pd.DataFrame(columns=["CNPJ", "CNPJ_RAIZ", "SEGMENTO_METODOLOGICO"])

    # 4. Agregação das Análises (Fichas) com Cascata CNPJ 14 dígitos -> CNPJ Raiz 8 dígitos (Matriz/Filial)
    if not df_analises.empty:
        parsed_an = df_analises["CNPJ"].map(padronizar_cnpj)
        df_analises["CNPJ"]      = parsed_an.map(lambda t: t[0])
        df_analises["CNPJ_RAIZ"] = parsed_an.map(lambda t: t[1])
        
        # Mapeamento e normalização flexível de nomes de colunas (Silver / Fato)
        if "DATA_CALCULO" in df_analises.columns and "DATA_ANALISE" not in df_analises.columns:
            df_analises["DATA_ANALISE"] = df_analises["DATA_CALCULO"]
        if "DATA_DEMONSTRACAO_FINANCEIRA" in df_analises.columns and "DATA_BALANCO_USADO" not in df_analises.columns:
            df_analises["DATA_BALANCO_USADO"] = df_analises["DATA_DEMONSTRACAO_FINANCEIRA"]
        if "DATA_DF" in df_analises.columns and "DATA_BALANCO_USADO" not in df_analises.columns:
            df_analises["DATA_BALANCO_USADO"] = df_analises["DATA_DF"]
            
        if "RATING" in df_analises.columns and "RATING_FINAL" not in df_analises.columns:
            df_analises["RATING_FINAL"] = df_analises["RATING"]
        if "RATING_COPEL" in df_analises.columns and "RATING_FINAL" not in df_analises.columns:
            df_analises["RATING_FINAL"] = df_analises["RATING_COPEL"]
            
        if "PD_PERCENTUAL" in df_analises.columns and "PD_FINAL" not in df_analises.columns:
            df_analises["PD_FINAL"] = df_analises["PD_PERCENTUAL"]
        if "PD" in df_analises.columns and "PD_FINAL" not in df_analises.columns:
            df_analises["PD_FINAL"] = df_analises["PD"]
            
        if "MODELO" in df_analises.columns and "MODELO_METODOLOGICO" not in df_analises.columns:
            df_analises["MODELO_METODOLOGICO"] = df_analises["MODELO"]
        if "versao_ficha" in df_analises.columns and "MODELO_METODOLOGICO" not in df_analises.columns:
            df_analises["MODELO_METODOLOGICO"] = df_analises["versao_ficha"]

        # Ordena para pegar a análise mais recente por CNPJ
        col_sort = "DATA_ANALISE" if "DATA_ANALISE" in df_analises.columns else ("DATA_BALANCO_USADO" if "DATA_BALANCO_USADO" in df_analises.columns else "CNPJ")
        if col_sort in df_analises.columns and col_sort != "CNPJ":
            df_analises["_DT_SORT"] = pd.to_datetime(df_analises[col_sort], errors="coerce")
            df_analises = df_analises.sort_values("_DT_SORT", na_position="first").drop_duplicates("CNPJ", keep="last")
        else:
            df_analises = df_analises.drop_duplicates("CNPJ", keep="last")

        # Cálculo da validade temporal da Ficha de Crédito (Metodologia BDC / Copel)
        # Regra: DF + 16 meses (1 ano e 4 meses) ou Data da Análise + 12 meses (1 ano)
        dt_balanco = pd.to_datetime(df_analises.get("DATA_BALANCO_USADO"), errors="coerce")
        dt_analise = pd.to_datetime(df_analises.get("DATA_ANALISE"), errors="coerce")
        
        mask_balanco = (dt_balanco.dt.year > 1900) & (dt_balanco.notna())
        mask_analise = (dt_analise.dt.year > 1900) & (dt_analise.notna())
        
        df_analises["VALIDADE_DT"] = pd.NaT
        df_analises.loc[mask_balanco, "VALIDADE_DT"] = dt_balanco.loc[mask_balanco] + pd.DateOffset(years=1, months=4)
        df_analises.loc[~mask_balanco & mask_analise, "VALIDADE_DT"] = dt_analise.loc[~mask_balanco & mask_analise] + pd.DateOffset(years=1)

        # Determinação da SITUACAO_ANALISE para as fichas existentes
        if "SITUACAO_ANALISE" not in df_analises.columns:
            df_analises["SITUACAO_ANALISE"] = df_analises["VALIDADE_DT"].apply(
                lambda dt: "VIGENTE" if pd.notnull(dt) and dt >= hoje else ("VENCIDA" if pd.notnull(dt) else "VENCIDA")
            )
        else:
            mask_null = df_analises["SITUACAO_ANALISE"].isna() | (df_analises["SITUACAO_ANALISE"].astype(str).str.strip().isin(["", "None", "nan", "<NA>"]))
            df_analises.loc[mask_null, "SITUACAO_ANALISE"] = df_analises.loc[mask_null, "VALIDADE_DT"].apply(
                lambda dt: "VIGENTE" if pd.notnull(dt) and dt >= hoje else ("VENCIDA" if pd.notnull(dt) else "VENCIDA")
            )

        # Determinação da SITUACAO_DF para as fichas existentes
        if "SITUACAO_DF" not in df_analises.columns:
            df_analises["SITUACAO_DF"] = "RECEBIDA"
        else:
            df_analises["SITUACAO_DF"] = df_analises["SITUACAO_DF"].fillna("RECEBIDA")

        # Garante flag TEM_ANALISE
        df_analises["TEM_ANALISE"] = "SIM"
            
        cols_analise_payload = [
            c for c in [
                "SITUACAO_ANALISE", "SITUACAO_DF", "RATING_FINAL", "PD_FINAL", 
                "MODELO_METODOLOGICO", "PATRIMONIO_LIQUIDO", "DATA_ANALISE", "DATA_BALANCO_USADO", "TEM_ANALISE"
            ] if c in df_analises.columns
        ]

        # 4.1. MATCHING PRIMÁRIO: Cruzamento exato pelo CNPJ de 14 dígitos
        df_gold = pd.merge(
            df_gold, 
            df_analises[["CNPJ"] + cols_analise_payload], 
            on="CNPJ", 
            how="left"
        )

        # 4.2. MATCHING SECUNDÁRIO (FALLBACK): Herança de Análise da Matriz para Filiais por CNPJ_RAIZ
        # Identifica e prioriza a Ficha da Matriz (final 0001) e/ou a ficha mais recente da mesma raiz
        df_analises["_EH_MATRIZ"] = df_analises["CNPJ"].str[8:12] == "0001"
        sort_raiz = ["_EH_MATRIZ"]
        if "_DT_SORT" in df_analises.columns:
            sort_raiz.append("_DT_SORT")
            
        df_analises_raiz = (
            df_analises.sort_values(sort_raiz, ascending=[True] * len(sort_raiz))
            .drop_duplicates(subset=["CNPJ_RAIZ"], keep="last")
        )
        
        df_fallback = df_analises_raiz[["CNPJ_RAIZ"] + cols_analise_payload].copy()
        df_fallback.columns = ["CNPJ_RAIZ"] + [f"{c}_RAIZ" for c in cols_analise_payload]

        df_gold = pd.merge(df_gold, df_fallback, on="CNPJ_RAIZ", how="left")

        # 4.3. COMBINAÇÃO E HERANÇA: Preenche filiais sem análise com os dados consolidados da Matriz
        for col in cols_analise_payload:
            col_raiz = f"{col}_RAIZ"
            if col_raiz in df_gold.columns:
                df_gold[col] = df_gold[col].combine_first(df_gold[col_raiz])
                df_gold = df_gold.drop(columns=[col_raiz])
    
    if "TEM_ANALISE" not in df_gold.columns:
        df_gold["TEM_ANALISE"] = "NÃO"
    df_gold["TEM_ANALISE"] = df_gold["TEM_ANALISE"].fillna("NÃO")

    # 5. Matemática de Contratos e Agregação de Volume (Enquadramento MWm)
    if not df_contratos.empty:
        parsed_ctr = df_contratos["CNPJ"].map(padronizar_cnpj)
        df_contratos["CNPJ"]      = parsed_ctr.map(lambda t: t[0])
        df_contratos["CNPJ_RAIZ"] = parsed_ctr.map(lambda t: t[1])
        df_contratos = df_contratos[parsed_ctr.map(lambda t: t[2]) == "CNPJ_VALIDO"].copy()

        col_vol = "VOLUME_CONTRATADO_MENSAL_MWM" if "VOLUME_CONTRATADO_MENSAL_MWM" in df_contratos.columns else "VOLUME_MWM"
        if col_vol in df_contratos.columns:
            df_contratos["VOLUME_MWM"] = pd.to_numeric(df_contratos[col_vol], errors="coerce").fillna(0.0)
        else:
            df_contratos["VOLUME_MWM"] = 0.0
        
        # AGREGAÇÃO REGRA DE NEGÓCIO: Soma as competências (Ano/Mês) de contratos paralelos, depois acha o MÁXIMO daquele CNPJ
        if "ano" in df_contratos.columns and "mes" in df_contratos.columns:
            df_mensal = df_contratos.groupby(["CNPJ_RAIZ", "ano", "mes"], as_index=False)["VOLUME_MWM"].sum()
            df_vol_enquadramento = df_mensal.groupby("CNPJ_RAIZ", as_index=False)["VOLUME_MWM"].max()
        else:
            df_vol_enquadramento = df_contratos.groupby("CNPJ_RAIZ", as_index=False)["VOLUME_MWM"].max()

        # Busca das colunas de temporalidade
        col_id = "CONTRATO" if "CONTRATO" in df_contratos.columns else "CONTRATO_ID"
        col_in = "SUPRIMENTO_INICIO"
        if col_in not in df_contratos.columns:
            col_in = "VIGENCIA_INICIO" if "VIGENCIA_INICIO" in df_contratos.columns else "inicio_suprimento"
            
        col_out = "SUPRIMENTO_TERMINO"
        if col_out not in df_contratos.columns:
            col_out = "VIGENCIA_FIM" if "VIGENCIA_FIM" in df_contratos.columns else "fim_suprimento"

        df_contratos["DT_INICIO"] = pd.to_datetime(df_contratos.get(col_in), errors="coerce")
        df_contratos["DT_FIM"] = pd.to_datetime(df_contratos.get(col_out), errors="coerce")
        
        # Avalia se a janela de datas do contrato envolve o dia de Hoje
        df_contratos["EH_VIGENTE"] = (
            (df_contratos.get("STATUS", df_contratos.get("id_status", "")).astype(str).str.upper().str.contains("ATIVO|EM SUPRIMENTO|2")) &
            (df_contratos["DT_INICIO"] <= hoje) &
            (df_contratos["DT_FIM"] >= hoje)
        )
        df_contratos["EH_FUTURO"] = (df_contratos["DT_INICIO"] > hoje)

        resumo_contratos = df_contratos.groupby("CNPJ").agg(
            QTD_CONTRATOS=(col_id, "nunique") if col_id in df_contratos.columns else ("CNPJ", "count"),
            STATUS_CONTRATUAL=("EH_VIGENTE", lambda x: "CONTRATO_VIGENTE" if x.any() else ("CONTRATO_FUTURO" if df_contratos.loc[x.index, "EH_FUTURO"].any() else "SEM_CONTRATO")),
            PROXIMO_INICIO=("DT_INICIO", "min"),
            PROXIMO_FIM=("DT_FIM", "max")
        ).reset_index()

        resumo_contratos["CNPJ_RAIZ"] = resumo_contratos["CNPJ"].str[:8]
        df_contratos_gold = pd.merge(resumo_contratos, df_vol_enquadramento[["CNPJ_RAIZ", "VOLUME_MWM"]], on="CNPJ_RAIZ", how="left")
        df_gold = pd.merge(df_gold, df_contratos_gold, on="CNPJ", how="left")
    else:
        df_gold["STATUS_CONTRATUAL"] = "SEM_CONTRATO"
        df_gold["VOLUME_MWM"] = 0.0
        
    df_gold["TEM_CONTRATO"] = df_gold["STATUS_CONTRATUAL"].apply(lambda x: "SIM" if x in ["CONTRATO_VIGENTE", "CONTRATO_FUTURO"] else "NÃO")

    # 6. Agregação de Risco / Exposição (MtM)
    if not df_risco.empty:
        parsed_risco = df_risco["CNPJ"].map(padronizar_cnpj)
        df_risco["CNPJ"] = parsed_risco.map(lambda t: t[0])
        df_risco = df_risco[parsed_risco.map(lambda t: t[2]) == "CNPJ_VALIDO"]
        df_risco = df_risco.drop_duplicates(subset=["CNPJ"], keep="last")
        
        if "PE_REAIS" in df_risco.columns:
            cols_risco = [c for c in ["CNPJ", "EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"] if c in df_risco.columns]
            df_gold = pd.merge(df_gold, df_risco[cols_risco], on="CNPJ", how="left")
        else:
            # Fallback direto da silver mtm
            col_mtm = "FINANCEIRO_MTM" if "FINANCEIRO_MTM" in df_risco.columns else ("MTM" if "MTM" in df_risco.columns else None)
            if col_mtm:
                df_gold = pd.merge(df_gold, df_risco[["CNPJ", col_mtm]].rename(columns={col_mtm: "EAD_VALOR"}), on="CNPJ", how="left")
                df_gold["PE_REAIS"] = 0.0

    # 7. Tratamento Final e Enquadramento Metodológico
    # Em vez de preencher com zero ou N/A, garantimos a integridade de NULOS VERDADEIROS e Governança
    colunas_esperadas = [
        "VOLUME_MWM", "EAD_VALOR", "PE_REAIS", "PATRIMONIO_LIQUIDO", "QTD_CONTRATOS", 
        "STATUS_CONTRATUAL", "SITUACAO_ANALISE", "SITUACAO_DF", "SITUACAO_CADASTRAL"
    ]
    for col in colunas_esperadas:
        if col not in df_gold.columns:
            df_gold[col] = pd.NA  # Nulo verdadeiro

    # Preenche STATUS_CONTRATUAL e SITUACAO_CADASTRAL onde realmente ausente
    df_gold["STATUS_CONTRATUAL"] = df_gold["STATUS_CONTRATUAL"].fillna("SEM_CONTRATO")
    df_gold["SITUACAO_CADASTRAL"] = df_gold["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADA")

    # Tratamento de governança para contrapartes SEM FICHA (TEM_ANALISE == "NÃO")
    def resolver_situacao_df(row):
        sit = row.get("SITUACAO_DF")
        if pd.notna(sit) and str(sit).strip() not in ["", "None", "nan", "<NA>"]:
            return sit
        
        status_ct = row.get("STATUS_CONTRATUAL")
        if status_ct in ["CONTRATO_VIGENTE", "CONTRATO_FUTURO"]:
            vol = pd.to_numeric(row.get("VOLUME_MWM"), errors='coerce')
            if pd.isna(vol): vol = 0.0
            if vol >= 5.0:
                return "NAO_RECEBIDA"
            else:
                return "NAO_APLICAVEL"
        return pd.NA

    def resolver_situacao_analise(row):
        sit = row.get("SITUACAO_ANALISE")
        if pd.notna(sit) and str(sit).strip() not in ["", "None", "nan", "<NA>"]:
            return sit
            
        status_ct = row.get("STATUS_CONTRATUAL")
        if status_ct in ["CONTRATO_VIGENTE", "CONTRATO_FUTURO"]:
            vol = pd.to_numeric(row.get("VOLUME_MWM"), errors='coerce')
            if pd.isna(vol): vol = 0.0
            if vol >= 5.0:
                return "IRREGULAR"  # Exigência de DF >= 5MWm sem ficha processada
        return pd.NA  # Nulo verdadeiro para demais casos sem ficha

    df_gold["SITUACAO_DF"] = df_gold.apply(resolver_situacao_df, axis=1)
    df_gold["SITUACAO_ANALISE"] = df_gold.apply(resolver_situacao_analise, axis=1)

    def classificar_exigencia(row):
        if row.get("STATUS_CONTRATUAL") == "SEM_CONTRATO": return "NAO_APLICAVEL"
        vol = pd.to_numeric(row.get("VOLUME_MWM"), errors='coerce')
        if pd.isna(vol): vol = 0.0
        return "DF_DETALHADA" if vol >= 5 else "BUREAU"
        
    df_gold["METODOLOGIA_EXIGIDA"] = df_gold.apply(classificar_exigencia, axis=1)
    
    def status_metodologia(row):
        if row.get("METODOLOGIA_EXIGIDA") == "NAO_APLICAVEL": return "NAO_APLICAVEL"
        sit_analise = str(row.get("SITUACAO_ANALISE") or "").upper()
        if sit_analise == "VIGENTE": return "COMPLIANT"
        if sit_analise == "VENCIDA": return "VENCIDA (ALERTA)"
        return "PENDENTE"

    df_gold["STATUS_METODOLOGIA"] = df_gold.apply(status_metodologia, axis=1)

    # 8. Exportação dos Arquivos da Visão
    out_parquet = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.parquet"
    out_latest = gold_dir / "Visao_Operacional_BDC_LATEST.parquet"
    out_csv = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.csv"
    
    df_gold.to_parquet(out_parquet, index=False)
    df_gold.to_parquet(out_latest, index=False)
    # Formatação especial do CSV para abrir no Excel do Brasil perfeitamente
    df_gold.to_csv(out_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

    logger.info("Visão Gold gerada. Total Contrapartes consolidadas: %d", len(df_gold))

    # 9. Retorno do Dicionário Matemático de KPIs para Orquestrador
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
        "ead_descoberto": float(df_gold.loc[mask_irregular, "EAD_VALOR"].sum(skipna=True)),
    }