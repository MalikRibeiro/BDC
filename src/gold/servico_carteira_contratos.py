"""Script responsável pela junção no nível de contrato e cruzamento de risco As-Of em 2 etapas."""
from __future__ import annotations
import pandas as pd
from pathlib import Path
from datetime import datetime

from app.context import AppContext
from control.logger import obter_logger
from common.identificadores import normalizar_cnpj_coluna
from common.datas import formatar_data_br_serie

def processar_visao_contratos_risco(context: AppContext) -> dict:
    run_id = f"VISAO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold.visao_contratos", Path("LOGS/gold") / f"{run_id}__visao_contratos.log")
    logger.info("Iniciando processamento da Visão Carteira Contratos (run_id=%s)", run_id)

    # 1. Carregar Bases
    silver_contratos_path = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not silver_contratos_path.exists():
        logger.error("Base de contratos não encontrada em: %s", silver_contratos_path)
        return {"status": "ERRO"}
    df_contratos = pd.read_parquet(silver_contratos_path)
    
    fato_risco_path = context.path("relational_facts") / "credito" / "fato_analise_credito.parquet"
    if not fato_risco_path.exists():
        logger.warning("Fato de análise não encontrada em %s. Usando vazio.", fato_risco_path)
        df_fatos = pd.DataFrame()
    else:
        df_fatos = pd.read_parquet(fato_risco_path)
    
    mtm_path = context.path("silver") / "mtm_contratos_silver" / "mtm_contratos.parquet"
    df_mtm = pd.read_parquet(mtm_path) if mtm_path.exists() else pd.DataFrame()

    dim_path = context.path("relational_dimensions") / "dim_contraparte.parquet"
    if not dim_path.exists():
        dim_path = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"
    if not dim_path.exists():
        dim_path = context.path("saidas") / "relational" / "dimensions" / "contrapartes" / "dim_contraparte.parquet"
    df_dim = pd.read_parquet(dim_path) if dim_path.exists() else pd.DataFrame()

    # Carregar dim_estabelecimento para resolução determinística de herança de risco
    estab_path = context.path("relational_dimensions") / "estabelecimentos" / "dim_estabelecimento.parquet"
    if not estab_path.exists():
        estab_path = context.path("saidas") / "relational" / "dimensions" / "estabelecimentos" / "dim_estabelecimento.parquet"
    df_estab = pd.read_parquet(estab_path) if estab_path.exists() else pd.DataFrame()

    # Carregar configurações declarativas de status ativo e prazo de validade
    try:
        cfg_status_path = context.path("control") / "configs" / "cfg_status_contrato_ativo.json"
    except Exception:
        cfg_status_path = Path("ENTRADAS/control/configs/cfg_status_contrato_ativo.json")
    if not cfg_status_path.exists():
        cfg_status_path = Path("ENTRADAS/control/configs/cfg_status_contrato_ativo.json")
    status_regex = "ATIVO|EM SUPRIMENTO|2|VENCIDO"
    if cfg_status_path.exists():
        try:
            import json
            import re
            with open(cfg_status_path, "r", encoding="utf-8") as f_st:
                cfg_st = json.load(f_st)
            s_ativos = cfg_st.get("status_ativos", [])
            if s_ativos:
                status_regex = "|".join(re.escape(s) for s in s_ativos)
        except Exception as e_cfg_st:
            logger.warning("Falha ao ler cfg_status_contrato_ativo.json, usando padrão regex: %s", e_cfg_st)

    try:
        cfg_prazo_path = context.path("control") / "configs" / "cfg_prazo_analise.json"
    except Exception:
        cfg_prazo_path = Path("ENTRADAS/control/configs/cfg_prazo_analise.json")
    if not cfg_prazo_path.exists():
        cfg_prazo_path = Path("ENTRADAS/control/configs/cfg_prazo_analise.json")
    meses_bureau = 12
    meses_df = 18
    if cfg_prazo_path.exists():
        try:
            import json
            with open(cfg_prazo_path, "r", encoding="utf-8") as f_pz:
                cfg_pz = json.load(f_pz)
            prazos_dict = cfg_pz.get("prazos_validade_meses", {})
            meses_bureau = int(prazos_dict.get("BUREAU", 12))
            meses_df = int(prazos_dict.get("DF", 18))
        except Exception as e_cfg_pz:
            logger.warning("Falha ao ler cfg_prazo_analise.json, usando padrão 12/18m: %s", e_cfg_pz)

    enq_dir = context.path("relational_configs")
    if not enq_dir.exists():
        enq_dir = context.path("saidas") / "relational" / "configs"
    arquivos_enq = list(enq_dir.glob("enquadramento_consumidores_*.csv")) if enq_dir.exists() else []
    df_enq = pd.DataFrame()
    if arquivos_enq:
        try:
            df_enq = pd.read_csv(max(arquivos_enq, key=lambda f: f.stat().st_mtime), sep=",", dtype={"CNPJ": str})
        except Exception:
            pass

    # 2. Preparar Contratos
    col_status = "STATUS" if "STATUS" in df_contratos.columns else ("id_status" if "id_status" in df_contratos.columns else "status")
    df_contratos = df_contratos[df_contratos[col_status].astype(str).str.upper().str.contains(status_regex, regex=True, na=False)].copy()
    
    col_cnpj = "CONTRAPARTE_CNPJ" if "CONTRAPARTE_CNPJ" in df_contratos.columns else "CNPJ"
    df_contratos["CNPJ"] = df_contratos[col_cnpj].apply(normalizar_cnpj_coluna)

    # Enriquecimento com dimensão de contrapartes e enquadramento de consumidores
    if not df_dim.empty and "CNPJ" in df_dim.columns:
        df_dim["CNPJ"] = df_dim["CNPJ"].apply(normalizar_cnpj_coluna)
        cols_dim = ["CNPJ"]
        if "SEGMENTO_METODOLOGICO" in df_dim.columns:
            cols_dim.append("SEGMENTO_METODOLOGICO")
        df_dim_sub = df_dim[cols_dim].drop_duplicates("CNPJ").rename(columns={"SEGMENTO_METODOLOGICO": "SEGMENTO_CADASTRO"})
        df_contratos = pd.merge(df_contratos, df_dim_sub, on="CNPJ", how="left")

    if not df_enq.empty and "CNPJ" in df_enq.columns:
        df_enq["CNPJ"] = df_enq["CNPJ"].apply(normalizar_cnpj_coluna)
        cols_enq = ["CNPJ"]
        if "POSSUI_PELO_MENOS_5_MWM" in df_enq.columns:
            cols_enq.append("POSSUI_PELO_MENOS_5_MWM")
        if "VOLUME_ENQUADRAMENTO_MWM" in df_enq.columns:
            cols_enq.append("VOLUME_ENQUADRAMENTO_MWM")
        df_contratos = pd.merge(df_contratos, df_enq[cols_enq].drop_duplicates("CNPJ"), on="CNPJ", how="left")
    
    col_ref_contrato = "NUMERO_REFERENCIA_CONTRATO" if "NUMERO_REFERENCIA_CONTRATO" in df_contratos.columns else "CONTRATO"
    if col_ref_contrato in df_contratos.columns:
        df_contratos["NUMERO_REFERENCIA_CONTRATO_STR"] = df_contratos[col_ref_contrato].astype(str).str.strip()
    else:
        df_contratos["NUMERO_REFERENCIA_CONTRATO_STR"] = ""

    # Preparar DATA_FECHAMENTO
    col_fechamento = "DATA_FECHAMENTO" if "DATA_FECHAMENTO" in df_contratos.columns else "VIGENCIA_INICIO"
    df_contratos["DATA_FECHAMENTO_DT"] = pd.to_datetime(df_contratos[col_fechamento], errors="coerce")
    mask_nat = df_contratos["DATA_FECHAMENTO_DT"].isna()
    if mask_nat.any() and "VIGENCIA_INICIO" in df_contratos.columns:
        df_contratos.loc[mask_nat, "DATA_FECHAMENTO_DT"] = pd.to_datetime(df_contratos.loc[mask_nat, "VIGENCIA_INICIO"], errors="coerce")

    df_contratos["DATA_FECHAMENTO_DT"] = df_contratos["DATA_FECHAMENTO_DT"].astype("datetime64[ns]")
    df_contratos["DATA_FECHAMENTO"] = df_contratos["DATA_FECHAMENTO_DT"].dt.strftime("%Y-%m-%d").fillna("")

    # Deduplicar contratos mantendo apenas a competência mais recente (LATEST) para evitar explosão cartesiana
    if "COMPETENCIA" in df_contratos.columns:
        df_contratos = df_contratos.sort_values(by=["NUMERO_REFERENCIA_CONTRATO_STR", "COMPETENCIA"])
    df_contratos = df_contratos.drop_duplicates(subset=["NUMERO_REFERENCIA_CONTRATO_STR"], keep="last")

    # 3. Cruzar com MTM
    if not df_mtm.empty:
        df_mtm["CONTRATO"] = df_mtm["CONTRATO"].astype(str).str.strip()
        agg_funcs = {}
        if "MTM_TOTAL" in df_mtm.columns: agg_funcs["MTM_TOTAL"] = "sum"
        if "MTM_VPL" in df_mtm.columns: agg_funcs["MTM_VPL"] = "sum"
        if "PORTFOLIO" in df_mtm.columns: agg_funcs["PORTFOLIO"] = "first"
        
        df_mtm_unico = df_mtm.groupby("CONTRATO", as_index=False).agg(agg_funcs)
        
        df_merged = pd.merge(
            df_contratos, 
            df_mtm_unico, 
            left_on="NUMERO_REFERENCIA_CONTRATO_STR", 
            right_on="CONTRATO", 
            how="left"
        )
    else:
        df_merged = df_contratos.copy()
        
    # 4. Cruzar com Risco: Análise de Crédito Vigente (N:1 - Estado Atual com Desempate Determinístico)
    if not df_fatos.empty:
        df_fatos["CNPJ"] = df_fatos["CNPJ"].apply(normalizar_cnpj_coluna)
        df_fatos["DATA_ANALISE_DT"] = pd.to_datetime(df_fatos["DATA_ANALISE"], errors="coerce").astype("datetime64[ns]")
        
        # Fallback de segurança: se DATA_ANALISE_DT for NaT mas houver FIM_VIGENCIA_ANALISE
        if "FIM_VIGENCIA_ANALISE" in df_fatos.columns:
            mask_dt_nat = df_fatos["DATA_ANALISE_DT"].isna() & df_fatos["FIM_VIGENCIA_ANALISE"].notna()
            if mask_dt_nat.any():
                is_bur = df_fatos["TIPO_ANALISE"].astype(str).str.contains("Bureau", na=False)
                df_fatos.loc[mask_dt_nat & is_bur, "DATA_ANALISE_DT"] = (
                    pd.to_datetime(df_fatos.loc[mask_dt_nat & is_bur, "FIM_VIGENCIA_ANALISE"], errors="coerce") - pd.DateOffset(months=12)
                ).astype("datetime64[ns]")
                df_fatos.loc[mask_dt_nat & (~is_bur), "DATA_ANALISE_DT"] = (
                    pd.to_datetime(df_fatos.loc[mask_dt_nat & (~is_bur), "FIM_VIGENCIA_ANALISE"], errors="coerce") - pd.DateOffset(months=18)
                ).astype("datetime64[ns]")
                df_fatos.loc[mask_dt_nat, "DATA_ANALISE"] = df_fatos.loc[mask_dt_nat, "DATA_ANALISE_DT"].dt.strftime("%Y-%m-%d")

        # Critério de ordenação com desempate determinístico:
        # 1. CNPJ
        # 2. DATA_ANALISE_DT (data da análise)
        # 3. _VERSAO_REGISTRO (versão SCD2)
        # 4. ETL_RUN_ID / ANALISE_ID (chave física de execução)
        sort_cols = ["CNPJ", "DATA_ANALISE_DT"]
        if "_VERSAO_REGISTRO" in df_fatos.columns:
            sort_cols.append("_VERSAO_REGISTRO")
        if "ETL_RUN_ID" in df_fatos.columns:
            sort_cols.append("ETL_RUN_ID")
        elif "ANALISE_ID" in df_fatos.columns:
            sort_cols.append("ANALISE_ID")
            
        df_fatos_validas = df_fatos.dropna(subset=["DATA_ANALISE_DT"]).sort_values(by=sort_cols)
        df_fatos_latest = df_fatos_validas.drop_duplicates(subset=["CNPJ"], keep="last").copy()
        
        cols_interesse_fato = [
            "CNPJ", "DATA_ANALISE", "DATA_ANALISE_DT", "RATING", "PD_PERCENTUAL", 
            "SCORE", "RESTRITIVOS", "TIPO_ANALISE", "FIM_VIGENCIA_ANALISE", 
            "ORIGEM_FONTE", "ANALISE_HERDADA", "SEGMENTO_METODOLOGICO_FICHA", "TIPO_FICHA",
            "FONTE_ANALISE", "PD_OFICIAL_FICHA", "PD_RECALCULADA_PYTHON", "DELTA_PD",
            "STATUS_AUDITORIA_PD", "STATUS_AUDITORIA_RATING"
        ]
        cols_presentes = [c for c in cols_interesse_fato if c in df_fatos_latest.columns]
        df_fatos_sub = df_fatos_latest[cols_presentes].copy()
        
        # Enriquecimento com dim_estabelecimento para mapear doador de risco e herança legal
        if not df_estab.empty and "CNPJ" in df_estab.columns:
            df_estab["CNPJ"] = df_estab["CNPJ"].apply(normalizar_cnpj_coluna)
            cols_est = ["CNPJ", "CONTRAPARTE_ID", "CNPJ_DOADOR_RISCO", "ORIGEM_HERANCA_RISCO", "EH_MATRIZ"]
            cols_pres = [c for c in cols_est if c in df_estab.columns]
            df_merged = pd.merge(
                df_merged,
                df_estab[cols_pres].drop_duplicates("CNPJ"),
                on="CNPJ",
                how="left"
            )

        if "CNPJ_DOADOR_RISCO" not in df_merged.columns:
            df_merged["CNPJ_DOADOR_RISCO"] = df_merged["CNPJ"]
        else:
            df_merged["CNPJ_DOADOR_RISCO"] = df_merged["CNPJ_DOADOR_RISCO"].combine_first(df_merged["CNPJ"])

        if "ORIGEM_HERANCA_RISCO" not in df_merged.columns:
            df_merged["ORIGEM_HERANCA_RISCO"] = "ANALISE_PROPRIA_DIRETA"
        else:
            df_merged["ORIGEM_HERANCA_RISCO"] = df_merged["ORIGEM_HERANCA_RISCO"].replace("NAO_APLICAVEL", "ANALISE_PROPRIA_DIRETA").fillna("ANALISE_PROPRIA_DIRETA")

        df_final = pd.merge(
            df_merged,
            df_fatos_sub,
            left_on="CNPJ_DOADOR_RISCO",
            right_on="CNPJ",
            suffixes=("", "_FATO"),
            how="left"
        )

        # Fallback de contingência: se o doador de risco herdado for nulo ou sem análise,
        # mas o CNPJ do próprio contrato tiver análise direta na Fato:
        mask_doador_falho = (df_final["RATING"].isna() | df_final["DATA_ANALISE"].isna()) & (df_final["CNPJ_DOADOR_RISCO"] != df_final["CNPJ"])
        if mask_doador_falho.any():
            df_proprios = pd.merge(
                df_merged.loc[mask_doador_falho, ["NUMERO_REFERENCIA_CONTRATO_STR", "CNPJ"]],
                df_fatos_sub,
                on="CNPJ",
                how="inner"
            )
            if not df_proprios.empty:
                for idx_m in df_final[mask_doador_falho].index:
                    ref_c = df_final.at[idx_m, "NUMERO_REFERENCIA_CONTRATO_STR"]
                    match_p = df_proprios[df_proprios["NUMERO_REFERENCIA_CONTRATO_STR"] == ref_c]
                    if not match_p.empty:
                        row_p = match_p.iloc[0]
                        for c_col in cols_presentes:
                            if c_col in row_p and pd.notna(row_p[c_col]):
                                df_final.at[idx_m, c_col] = row_p[c_col]
                        df_final.at[idx_m, "ORIGEM_HERANCA_RISCO"] = "ANALISE_PROPRIA_DIRETA"
                        df_final.at[idx_m, "CNPJ_DOADOR_RISCO"] = df_final.at[idx_m, "CNPJ"]
    else:
        df_final = df_merged.copy()
        for c in ["DATA_ANALISE", "DATA_ANALISE_DT", "RATING", "PD_PERCENTUAL", "SCORE", "RESTRITIVOS", "TIPO_ANALISE", "FIM_VIGENCIA_ANALISE", "ORIGEM_FONTE", "FONTE_ANALISE", "ORIGEM_HERANCA_RISCO", "CNPJ_DOADOR_RISCO"]:
            df_final[c] = pd.NA

    # 4.1 Enriquecimento Dimensional (Star Schema): Integrar CONTRAPARTE_ID, GRUPO_ID e NOME_GRUPO
    c_raiz_serie = df_final["CNPJ"].astype(str).str[:8]
    if "CONTRAPARTE_ID" not in df_final.columns:
        df_final["CONTRAPARTE_ID"] = "CPT_" + c_raiz_serie
    else:
        df_final["CONTRAPARTE_ID"] = df_final["CONTRAPARTE_ID"].fillna("CPT_" + c_raiz_serie)

    if not df_dim.empty and "CONTRAPARTE_ID" in df_dim.columns:
        cols_cpt_dim = [c for c in ["CONTRAPARTE_ID", "GRUPO_ID", "GRUPO_ECONOMICO"] if c in df_dim.columns]
        df_cpt_lookup = df_dim[cols_cpt_dim].drop_duplicates("CONTRAPARTE_ID")
        df_final = pd.merge(df_final, df_cpt_lookup, on="CONTRAPARTE_ID", how="left")

    if "GRUPO_ID" not in df_final.columns:
        df_final["GRUPO_ID"] = "GRP_" + c_raiz_serie
    else:
        df_final["GRUPO_ID"] = df_final["GRUPO_ID"].fillna("GRP_" + c_raiz_serie)

    col_nm_ctp = "CONTRAPARTE_NOME_FANTASIA" if "CONTRAPARTE_NOME_FANTASIA" in df_final.columns else "CONTRAPARTE"
    s_fallback_nm = df_final[col_nm_ctp] if col_nm_ctp in df_final.columns else ("CONTROLE INDEPENDENTE - " + c_raiz_serie)

    if "GRUPO_ECONOMICO" in df_final.columns:
        df_final["NOME_GRUPO"] = df_final["GRUPO_ECONOMICO"].combine_first(s_fallback_nm).fillna("CONTROLE INDEPENDENTE - " + c_raiz_serie)
    else:
        df_final["NOME_GRUPO"] = s_fallback_nm.fillna("CONTROLE INDEPENDENTE - " + c_raiz_serie)

    mask_nm_branco = (
        df_final["NOME_GRUPO"].isna() | 
        df_final["NOME_GRUPO"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "NULL"])
    )
    df_final.loc[mask_nm_branco, "NOME_GRUPO"] = "CONTROLE INDEPENDENTE - " + c_raiz_serie.loc[mask_nm_branco]

    # 5. Avaliação de Vigência da Análise contra a data de hoje
    hoje = pd.Timestamp.now().normalize()
    
    # Fallback de segurança para FIM_VIGENCIA_ANALISE caso ausente
    if "FIM_VIGENCIA_ANALISE" not in df_final.columns:
        df_final["FIM_VIGENCIA_ANALISE"] = pd.NA
        
    mask_calc_fim = df_final["FIM_VIGENCIA_ANALISE"].isna() & df_final["DATA_ANALISE"].notna()
    if mask_calc_fim.any():
        is_bur = df_final["TIPO_ANALISE"].astype(str).str.contains("Bureau", na=False)
        df_final.loc[mask_calc_fim & is_bur, "FIM_VIGENCIA_ANALISE"] = (
            pd.to_datetime(df_final.loc[mask_calc_fim & is_bur, "DATA_ANALISE"], errors="coerce") + pd.DateOffset(months=meses_bureau)
        ).dt.strftime("%Y-%m-%d")
        df_final.loc[mask_calc_fim & (~is_bur), "FIM_VIGENCIA_ANALISE"] = (
            pd.to_datetime(df_final.loc[mask_calc_fim & (~is_bur), "DATA_ANALISE"], errors="coerce") + pd.DateOffset(months=meses_df)
        ).dt.strftime("%Y-%m-%d")

    dt_fim_vigencia = pd.to_datetime(df_final["FIM_VIGENCIA_ANALISE"], errors="coerce").dt.normalize()
    tem_data_analise = df_final["DATA_ANALISE"].notna() & (~df_final["DATA_ANALISE"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "NaT", "-"]))

    cond_sem_analise = ~tem_data_analise
    cond_vencida = tem_data_analise & (dt_fim_vigencia.isna() | (hoje > dt_fim_vigencia))
    cond_vigente = tem_data_analise & dt_fim_vigencia.notna() & (hoje <= dt_fim_vigencia)

    df_final["STATUS_VIGENCIA_ANALISE"] = "SEM_ANALISE"
    df_final.loc[cond_vencida, "STATUS_VIGENCIA_ANALISE"] = "VENCIDA"
    df_final.loc[cond_vigente, "STATUS_VIGENCIA_ANALISE"] = "VIGENTE"

    # Regra de Governança BDC: Comercializadoras, Geradoras, CPURA, CGRUPO e Consumidores >= 5 MWm 
    # exigem obrigatoriamente DF contábil analisada pela mesa. Se a DF estiver pendente, ausente ou expirada,
    # o status de crédito deve ser estritamente 'VENCIDA' (acionando a PD_sub da NT v7 na visão de mercado).
    is_seg_obriga_df = (
        (df_final.get("TIPO_FICHA").astype(str).str.upper().isin(["COMERCIALIZADORA", "GERADORA"])) |
        (df_final.get("SEGMENTO_METODOLOGICO_FICHA").astype(str).str.upper().str.contains("CPURA|CGRUPO", na=False)) |
        (df_final.get("SEGMENTO_CADASTRO").astype(str).str.upper().str.contains("CPURA|CGRUPO", na=False)) |
        (df_final.get("POSSUI_PELO_MENOS_5_MWM") == True) |
        (df_final.get("SEGMENTO_METODOLOGICO_FICHA").astype(str).str.upper().str.contains("GT_5", na=False))
    )
    mask_df_nao_atendida = is_seg_obriga_df & (
        (df_final.get("SITUACAO_DF") == "PENDENTE_DF") |
        (df_final["STATUS_VIGENCIA_ANALISE"] == "SEM_ANALISE") |
        (~tem_data_analise)
    )
    df_final.loc[mask_df_nao_atendida, "STATUS_VIGENCIA_ANALISE"] = "VENCIDA"

    # 5.1 Identificação Declarativa de Contrapartes Intercompany (Isentas de Risco)
    cfg_intercompany_path = Path("ENTRADAS/control/configs/contrapartes_grupo_proprio.json")
    mask_intercompany = pd.Series(False, index=df_final.index)
    if cfg_intercompany_path.exists():
        try:
            import json
            with open(cfg_intercompany_path, "r", encoding="utf-8") as f:
                cfg_ic = json.load(f)
            raizes = tuple(cfg_ic.get("raizes_cnpj_isentas", []))
            cnpjs_exatos = set(cfg_ic.get("cnpjs_isentos", []))
            termos_nome = cfg_ic.get("termos_razao_social", [])

            s_cnpj = df_final["CNPJ"].astype(str).str.zfill(14)
            cond_raiz = s_cnpj.str.startswith(raizes) if raizes else pd.Series(False, index=df_final.index)
            cond_cnpj = s_cnpj.isin(cnpjs_exatos) if cnpjs_exatos else pd.Series(False, index=df_final.index)
            
            col_nome = "CONTRAPARTE_NOME_FANTASIA" if "CONTRAPARTE_NOME_FANTASIA" in df_final.columns else "CONTRAPARTE"
            s_nome = df_final[col_nome].astype(str).str.upper() if col_nome in df_final.columns else pd.Series("", index=df_final.index)
            cond_nome = s_nome.apply(lambda x: any(t in x for t in termos_nome)) if termos_nome else pd.Series(False, index=df_final.index)

            mask_intercompany = cond_raiz | cond_cnpj | cond_nome
            df_final.loc[mask_intercompany, "STATUS_VIGENCIA_ANALISE"] = "ISENTO_INTERCOMPANY"
        except Exception as e:
            logger.warning("Falha ao carregar config de contrapartes grupo próprio: %s", e)

    # 5.2 Identificação e Rastreabilidade Estrita de Herança de Risco
    mask_matriz = (df_final.get("ORIGEM_HERANCA_RISCO") == "MATRIZ_FILIAL_CNPJ_RAIZ") & df_final["RATING"].notna()
    mask_ctrl = (df_final.get("ORIGEM_HERANCA_RISCO") == "CONTROLADORA_HOMOLOGADA_PLANILHA") & df_final["RATING"].notna()

    df_final.loc[mask_matriz, "ANALISE_HERDADA"] = True
    df_final.loc[mask_matriz, "ORIGEM_ANALISE"] = "HERDADA DA MATRIZ (RAIZ CNPJ)"
    df_final.loc[mask_matriz, "FONTE_ANALISE"] = "Herança Matriz/Filial"

    df_final.loc[mask_ctrl, "ANALISE_HERDADA"] = True
    df_final.loc[mask_ctrl, "ORIGEM_ANALISE"] = "HERDADA DA CONTROLADORA (HOMOLOGADA)"
    df_final.loc[mask_ctrl, "FONTE_ANALISE"] = "Herança Societária Homologada"

    # Mapeamento do TIPO_ANALISE
    def determinar_metodologia_vigente(row):
        stat_vig = row.get("STATUS_VIGENCIA_ANALISE")
        if stat_vig in ["INTERCOMPANY", "ISENTO_INTERCOMPANY"]:
            return "Intercompany"
        if stat_vig == "SEM_ANALISE":
            return "Sem Análise"
            
        origem_h = row.get("ORIGEM_HERANCA_RISCO")
        if origem_h == "MATRIZ_FILIAL_CNPJ_RAIZ":
            base_tipo = "Análise Herdada (Matriz)"
        elif origem_h == "CONTROLADORA_HOMOLOGADA_PLANILHA":
            base_tipo = "Análise Herdada (Controladora)"
        else:
            tipo = str(row.get("TIPO_ANALISE", "")).strip()
            analise_herdada = row.get("ANALISE_HERDADA") is True or "Herdada" in tipo or "HERDADA" in tipo or "Raiz" in tipo
            if analise_herdada:
                base_tipo = "Análise Herdada"
            else:
                seg_ficha = str(row.get("SEGMENTO_METODOLOGICO_FICHA", "")).strip().upper()
                tipo_ficha = str(row.get("TIPO_FICHA", "")).strip().upper()
                seg_cad = str(row.get("SEGMENTO_CADASTRO", "")).strip().upper()
                portfolio = str(row.get("PORTFOLIO", "")).strip().upper()
                origem_fonte = str(row.get("ORIGEM_FONTE", "")).strip().upper()
                pelo_menos_5mwm = row.get("POSSUI_PELO_MENOS_5_MWM")

                # Comercializadoras e Geradoras são SEMPRE Análise DF
                is_comercializadora = (tipo_ficha in ["COMERCIALIZADORA", "GERADORA"]) or ("CPURA" in seg_ficha) or ("CGRUPO" in seg_ficha)
                
                if is_comercializadora or origem_fonte == "DF":
                    base_tipo = "Análise DF"
                else:
                    is_bureau = (
                        (seg_ficha == "CONSUMIDOR_LE_5") or ("LE_5" in seg_ficha) or
                        (tipo_ficha == "CONSUMIDOR" and seg_ficha != "CONSUMIDOR_GT_5") or
                        (seg_cad == "CONSUMIDOR_LE_5") or ("LE_5" in seg_cad) or
                        (origem_fonte == "BUREAU") or
                        (pelo_menos_5mwm is False and tipo_ficha == "CONSUMIDOR") or
                        ("CONSUMIDOR" in portfolio and seg_cad != "CONSUMIDOR_GT_5" and pelo_menos_5mwm is not True)
                    )
                    base_tipo = "Análise Bureau" if is_bureau else "Análise DF"

        if stat_vig == "VENCIDA":
            return f"{base_tipo} (Vencida)"
        return base_tipo

    df_final["TIPO_ANALISE"] = df_final.apply(determinar_metodologia_vigente, axis=1)

    # REGRA DE GOVERNANÇA NOTA TÉCNICA v7 (VISÃO DE CRÉDITO vs VISÃO DE RISCO DE MERCADO):
    # 1. Preservar o rating documental oficial da ficha para auditoria de crédito:
    df_final["RATING_OFICIAL_FICHA"] = df_final["RATING"]

    # 2. Casos SEM_ANALISE: mantêm-se estritamente nulos
    mask_sem_anl = df_final["STATUS_VIGENCIA_ANALISE"] == "SEM_ANALISE"
    df_final.loc[mask_sem_anl, "RATING"] = pd.NA
    df_final.loc[mask_sem_anl, "PD_PERCENTUAL"] = pd.NA
    df_final.loc[mask_sem_anl, "SCORE"] = pd.NA
    df_final.loc[mask_sem_anl, "RESTRITIVOS"] = pd.NA
    df_final.loc[mask_sem_anl, "RATING_OFICIAL_FICHA"] = pd.NA

    # 3. Casos VENCIDA:
    # - Visão de Crédito: RATING_OFICIAL_FICHA fica nulo e STATUS_VIGENCIA_ANALISE = 'VENCIDA'.
    # - Visão de Risco a Mercado: PD_PERCENTUAL é preenchida com a PD_sub da NT v7 para cálculo
    #   financeiro (TRC/Perda Esperada/MtM), e RATING_MERCADO deriva da faixa de PD correspondente.
    mask_vencida = df_final["STATUS_VIGENCIA_ANALISE"] == "VENCIDA"
    if mask_vencida.any():
        from domain.credito.rating import derivar_rating_por_pd
        pd_faixas_cfg = None
        try:
            from common.json import ler_json
            pd_faixas_cfg = ler_json(Path("ENTRADAS/control/configs/pd_faixas.json"))
        except Exception:
            pass

        df_final.loc[mask_vencida, "RATING_OFICIAL_FICHA"] = pd.NA

        for idx_v in df_final[mask_vencida].index:
            seg_f = str(df_final.at[idx_v, "SEGMENTO_METODOLOGICO_FICHA"] or "").strip().upper()
            tipo_f = str(df_final.at[idx_v, "TIPO_FICHA"] or "").strip().upper()
            pd_val_orig = df_final.at[idx_v, "PD_PERCENTUAL"]

            try:
                pd_num_orig = float(pd_val_orig) if pd.notna(pd_val_orig) else None
            except Exception:
                pd_num_orig = None

            # Cálculo estrito da PD_sub (NT v7 §§ 6.4, 7.2, 8.2, 9.4)
            if "CPURA" in seg_f or tipo_f == "COMERCIALIZADORA":
                pd_sub = max(pd_num_orig or 0.10, 0.10)
            elif "CGRUPO" in seg_f or "GRUPO" in seg_f:
                pd_sub = max(pd_num_orig or 0.15, 0.15)
            elif "GT_5" in seg_f:
                pd_sub = max(pd_num_orig or 0.50, 0.50)
            else:
                pd_sub = pd_num_orig if pd_num_orig is not None else 0.10

            df_final.at[idx_v, "PD_PERCENTUAL"] = pd_sub
            r_mercado = derivar_rating_por_pd(pd_sub, seg_f or tipo_f, pd_faixas_cfg) if pd_faixas_cfg else "E"
            df_final.at[idx_v, "RATING"] = r_mercado or "E"

    df_final["RATING_MERCADO"] = df_final["RATING"]

    # Intercompany: isento de risco de crédito de terceiros (rótulo oficial ISENTO_INTERCOMPANY)
    df_final.loc[mask_intercompany, "RATING"] = "ISENTO_INTERCOMPANY"
    df_final.loc[mask_intercompany, "RATING_MERCADO"] = "ISENTO_INTERCOMPANY"
    df_final.loc[mask_intercompany, "RATING_OFICIAL_FICHA"] = "ISENTO_INTERCOMPANY"
    df_final.loc[mask_intercompany, "PD_PERCENTUAL"] = 0.0
    df_final.loc[mask_intercompany, "SCORE"] = pd.NA
    df_final.loc[mask_intercompany, "RESTRITIVOS"] = 0

    # Padronização canônica de FONTE_ANALISE na Gold
    if "FONTE_ANALISE" not in df_final.columns:
        df_final["FONTE_ANALISE"] = pd.NA

    _mapa_fonte_gold = {
        "DF": "Ficha Interna",
        "BUREAU": "Bureau (Risk3)",
        "SALESFORCE": "Salesforce",
    }
    mask_fonte_na = df_final["FONTE_ANALISE"].isna() & df_final["ORIGEM_FONTE"].notna()
    if mask_fonte_na.any():
        df_final.loc[mask_fonte_na, "FONTE_ANALISE"] = (
            df_final.loc[mask_fonte_na, "ORIGEM_FONTE"]
            .astype(str)
            .str.strip()
            .str.upper()
            .map(_mapa_fonte_gold)
        )

    df_final.loc[mask_matriz, "FONTE_ANALISE"] = "Herança Matriz/Filial"
    df_final.loc[mask_ctrl, "FONTE_ANALISE"] = "Herança Societária Homologada"
    df_final.loc[mask_intercompany, "FONTE_ANALISE"] = "Intercompany"
    df_final.loc[df_final["STATUS_VIGENCIA_ANALISE"] == "SEM_ANALISE", "FONTE_ANALISE"] = pd.NA

    # 6. Cálculo da NOVA COLUNA: STATUS_CONTRATO
    col_sup_ini = "VIGENCIA_INICIO" if "VIGENCIA_INICIO" in df_final.columns else "SUPRIMENTO_INICIO"
    col_sup_fim = "VIGENCIA_FIM" if "VIGENCIA_FIM" in df_final.columns else "SUPRIMENTO_FIM"
    
    dt_inicio = pd.to_datetime(df_final[col_sup_ini], errors="coerce").dt.normalize()
    dt_fim = pd.to_datetime(df_final[col_sup_fim], errors="coerce").dt.normalize()
    
    cond_datas_validas = dt_inicio.notna() & dt_fim.notna()
    cond_a_fornecer = cond_datas_validas & (hoje < dt_inicio)
    cond_em_fornecimento = cond_datas_validas & (dt_inicio <= hoje) & (hoje <= dt_fim)
    cond_encerrado = cond_datas_validas & (hoje > dt_fim)
    
    df_final["STATUS_CONTRATO"] = "NAO_APLICAVEL"
    df_final.loc[cond_a_fornecer, "STATUS_CONTRATO"] = "A_FORNECER"
    df_final.loc[cond_em_fornecimento, "STATUS_CONTRATO"] = "EM_FORNECIMENTO"
    df_final.loc[cond_encerrado, "STATUS_CONTRATO"] = "ENCERRADO"

    # Ordenação por data e desduplicação final estrita sobre NUMERO_REFERENCIA_CONTRATO
    col_ref_final = "NUMERO_REFERENCIA_CONTRATO_STR" if "NUMERO_REFERENCIA_CONTRATO_STR" in df_final.columns else "NUMERO_REFERENCIA_CONTRATO"
    if col_ref_final in df_final.columns:
        if "DATA_FECHAMENTO_DT" in df_final.columns:
            df_final = df_final.sort_values(by=[col_ref_final, "DATA_FECHAMENTO_DT"])
        df_final = df_final.drop_duplicates(subset=[col_ref_final], keep="last")

    # Manter DATA_FECHAMENTO no formato canônico da Gold
    if "DATA_FECHAMENTO_DT" in df_final.columns:
        df_final["DATA_FECHAMENTO"] = df_final["DATA_FECHAMENTO_DT"].dt.strftime("%Y-%m-%d")

    # 7. Selecionar e Renomear Colunas (Schema Gold Oficial)
    rename_map = {
        "DATA_FECHAMENTO": "DATA_FECHAMENTO",
        "VIGENCIA_INICIO": "SUPRIMENTO_INICIO",
        "VIGENCIA_FIM": "SUPRIMENTO_FIM",
        "CONTRAPARTE_NOME_FANTASIA": "CONTRAPARTE_NOME_FANTASIA",
        "CNPJ": "CONTRAPARTE_CNPJ",
        "CONTRAPARTE_ID": "CONTRAPARTE_ID",
        "GRUPO_ID": "GRUPO_ID",
        "NOME_GRUPO": "NOME_GRUPO",
        "NUMERO_REFERENCIA_CONTRATO": "NUMERO_REFERENCIA_CONTRATO",
        "MOVIMENTACAO": "MOVIMENTACAO",
        "PORTFOLIO": "PORTFOLIO",
        "MTM_TOTAL": "MTM_TOTAL_R$",
        "MTM_VPL": "MTM_VPL_R$",
        "PD_PERCENTUAL": "PD",
        "RATING": "RATING",
        "SCORE": "SCORE",
        "RESTRITIVOS": "RESTRITIVOS",
        "DATA_ANALISE": "DATA_ANALISE",
        "FIM_VIGENCIA_ANALISE": "FIM_VIGENCIA_ANALISE",
        "STATUS_VIGENCIA_ANALISE": "STATUS_VIGENCIA_ANALISE",
        "TIPO_ANALISE": "TIPO_ANALISE",
        "STATUS_CONTRATO": "STATUS_CONTRATO",
        "FONTE_ANALISE": "FONTE_ANALISE",
        "ORIGEM_HERANCA_RISCO": "ORIGEM_HERANCA_RISCO",
        "CNPJ_DOADOR_RISCO": "CNPJ_DOADOR_RISCO",
        "PD_OFICIAL_FICHA": "PD_OFICIAL_FICHA",
        "PD_RECALCULADA_PYTHON": "PD_RECALCULADA_PYTHON",
        "DELTA_PD": "DELTA_PD",
        "STATUS_AUDITORIA_PD": "STATUS_AUDITORIA_PD",
        "STATUS_AUDITORIA_RATING": "STATUS_AUDITORIA_RATING",
        "SEGMENTO_METODOLOGICO_FICHA": "SEGMENTO_METODOLOGICO_FICHA"
    }
    
    for col in rename_map.keys():
        if col not in df_final.columns:
            df_final[col] = pd.NA

    df_final = df_final[list(rename_map.keys())].rename(columns=rename_map)

    # Garantir unicidade de 1 linha por contrato ativo após renomeação
    if "NUMERO_REFERENCIA_CONTRATO" in df_final.columns:
        df_final = df_final.drop_duplicates(subset=["NUMERO_REFERENCIA_CONTRATO"], keep="last")

    # Tipagem estrita para consistência Parquet / PyArrow
    for num_col in ["MTM_TOTAL_R$", "MTM_VPL_R$", "PD", "SCORE", "RESTRITIVOS", "PD_OFICIAL_FICHA", "PD_RECALCULADA_PYTHON", "DELTA_PD"]:
        if num_col in df_final.columns:
            df_final[num_col] = pd.to_numeric(df_final[num_col], errors="coerce")
            
    for str_col in [
        "CONTRAPARTE_NOME_FANTASIA", "CONTRAPARTE_CNPJ", "CONTRAPARTE_ID", "GRUPO_ID", "NOME_GRUPO",
        "NUMERO_REFERENCIA_CONTRATO", "MOVIMENTACAO", "PORTFOLIO", "RATING", 
        "STATUS_VIGENCIA_ANALISE", "TIPO_ANALISE", "STATUS_CONTRATO", "FONTE_ANALISE", 
        "ORIGEM_HERANCA_RISCO", "STATUS_AUDITORIA_PD", "STATUS_AUDITORIA_RATING", "SEGMENTO_METODOLOGICO_FICHA"
    ]:
        if str_col in df_final.columns:
            df_final[str_col] = df_final[str_col].astype(str).replace({"nan": None, "None": None, "<NA>": None, "NaT": None})

    for dt_col in ["DATA_FECHAMENTO", "SUPRIMENTO_INICIO", "SUPRIMENTO_FIM", "DATA_ANALISE", "FIM_VIGENCIA_ANALISE"]:
        if dt_col in df_final.columns:
            df_final[dt_col] = formatar_data_br_serie(df_final[dt_col]).replace({"-": None, "nan": None, "None": None, "<NA>": None, "NaT": None})

    # 8. Salvar na Gold
    gold_dir = context.path("gold") / "visao_operacional_negocio"
    gold_dir.mkdir(parents=True, exist_ok=True)
    out_path = gold_dir / "Visao_Carteira_Contratos.parquet"
    df_final.to_parquet(out_path, index=False)
    
    logger.info("Visão Carteira Contratos gerada com %d registros.", len(df_final))

    # 8.1 Exportação do Relatório de Ação Imediata: CNPJs a Mercado Descobertos de Análise
    try:
        export_dir = context.path("saidas") / "exportacoes"
    except Exception:
        export_dir = Path("SAIDAS/exportacoes")
    export_dir.mkdir(parents=True, exist_ok=True)

    mask_sem_rating = (
        df_final["RATING"].isna() | 
        df_final["RATING"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "SEM_ANALISE"])
    )
    mask_mercado = (
        (df_final["FONTE_ANALISE"].astype(str) != "Intercompany") &
        (df_final["STATUS_VIGENCIA_ANALISE"] != "ISENTO_INTERCOMPANY") &
        (df_final["RATING"].astype(str) != "ISENTO_INTERCOMPANY")
    )

    df_descobertos = df_final[mask_sem_rating & mask_mercado].copy()
    if not df_descobertos.empty:
        df_rel_acao = (
            df_descobertos.groupby(["CONTRAPARTE_CNPJ", "CONTRAPARTE_NOME_FANTASIA"], as_index=False)
            .agg({
                "MTM_TOTAL_R$": "sum",
                "NUMERO_REFERENCIA_CONTRATO": "count",
                "PORTFOLIO": lambda x: ", ".join(sorted(set(str(v) for v in x if pd.notna(v)))),
                "STATUS_VIGENCIA_ANALISE": "first"
            })
            .rename(columns={
                "NUMERO_REFERENCIA_CONTRATO": "TOTAL_CONTRATOS",
                "PORTFOLIO": "PORTFOLIOS",
                "STATUS_VIGENCIA_ANALISE": "STATUS_VIGENCIA"
            })
            .sort_values(by="MTM_TOTAL_R$", ascending=False)
        )
        
        csv_acao_path = export_dir / "CNPJs_Descobertos_Acao_Imediata.csv"
        df_rel_acao.to_csv(csv_acao_path, sep=";", index=False, encoding="utf-8-sig")
        logger.info(
            "Relatório de Ação Imediata exportado com sucesso: %s (%d CNPJs, R$ %.2f MtM).",
            csv_acao_path, len(df_rel_acao), df_rel_acao["MTM_TOTAL_R$"].sum()
        )

    return {"status": "SUCESSO", "linhas": len(df_final)}


if __name__ == "__main__":
    from app.bootstrap import carregar_contexto
    ctx = carregar_contexto(Path("ENTRADAS/configs"))
    processar_visao_contratos_risco(ctx)
