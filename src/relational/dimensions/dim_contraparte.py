"""Serviço de consolidação da Dimensão de Contraparte (Contraparte Lógica).

Grão: 1 linha por Contraparte Lógica (Empresa Consolidada por Raiz de CNPJ).
Atributos de estabelecimento (filiais) são normalizados na dim_estabelecimento.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver
from common.identificadores import normalizar_cnpj_coluna
from common.dados import carregar_fichas_silver_consolidadas


def processar_dim_contraparte(context: AppContext) -> dict[str, Any]:
    """Orquestra a leitura de dependências e construção da Dimensão de Contraparte Lógica."""
    run_id = f"DIM_CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.dim_contraparte", Path("LOGS/relational") / f"{run_id}__dim_contraparte.log")
    logger.info("Iniciando processamento da Dimensão de Contraparte Lógica (run_id=%s)...", run_id)

    receita_path = context.path("silver") / "receita_silver" / "receita_cadastral_silver.parquet"
    enquadra_path = context.path("relational_configs") / f"enquadramento_consumidores_{datetime.now().strftime('%Y%m')}.csv"
    salesforce_path = context.path("silver") / "salesforce_silver" / "account" / "salesforce_account.parquet"

    df_receita = pd.read_parquet(receita_path) if receita_path.exists() else pd.DataFrame()
    df_seg = pd.read_csv(enquadra_path) if enquadra_path.exists() else pd.DataFrame()
    df_sf_account = pd.read_parquet(salesforce_path) if salesforce_path.exists() else pd.DataFrame()

    ctrl_path = context.path("silver") / "mapeamento_controladoras" / "mapeamento_controladoras.parquet"
    df_ctrl = pd.read_parquet(ctrl_path) if ctrl_path.exists() else pd.DataFrame()
    if not df_ctrl.empty and "_STATUS_REGISTRO" in df_ctrl.columns:
        df_ctrl = df_ctrl[df_ctrl["_STATUS_REGISTRO"] == "VIGENTE"]

    df_fichas = carregar_fichas_silver_consolidadas(context.path("silver"))

    return criar_dim_contraparte(
        context,
        df_silver_receita=df_receita,
        df_silver_segmentacao=df_seg,
        df_silver_salesforce_account=df_sf_account,
        df_silver_fichas=df_fichas,
        df_controladoras=df_ctrl,
    )


def criar_dim_contraparte(
    context: AppContext,
    df_silver_receita: pd.DataFrame,
    df_silver_segmentacao: pd.DataFrame,
    df_silver_salesforce_account: pd.DataFrame = None,
    df_silver_fichas: pd.DataFrame = None,
    df_controladoras: pd.DataFrame = None,
) -> dict[str, Any]:
    run_id = f"DIM_CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.dim_contraparte", Path("LOGS/relational") / f"{run_id}__dim_contraparte.log")

    if df_silver_receita.empty:
        df_silver_receita = pd.DataFrame(columns=["CNPJ", "RAZAO_SOCIAL", "SITUACAO_CADASTRAL", "NATUREZA_JURIDICA", "CNAE_PRINCIPAL"])
    if df_silver_segmentacao.empty:
        df_silver_segmentacao = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"])

    df_silver_receita["CNPJ"] = df_silver_receita["CNPJ"].apply(normalizar_cnpj_coluna)
    df_silver_segmentacao["CNPJ"] = df_silver_segmentacao["CNPJ"].apply(normalizar_cnpj_coluna)

    df_dim = pd.merge(df_silver_receita, df_silver_segmentacao, on="CNPJ", how="outer")

    # Enriquecimento com Fichas
    if df_silver_fichas is not None and not df_silver_fichas.empty:
        df_fichas = df_silver_fichas.copy()
        df_fichas["CNPJ"] = df_fichas["CNPJ"].apply(normalizar_cnpj_coluna)
        df_fichas["NOME_FICHA"] = df_fichas.get("RAZAO_SOCIAL", None)
        df_fichas["SIGLA_FICHA"] = df_fichas.get("SIGLA", None)
        col_sort = "DT_PROCESSAMENTO" if "DT_PROCESSAMENTO" in df_fichas.columns else "CNPJ"
        df_id_fichas = df_fichas.sort_values(col_sort).drop_duplicates("CNPJ", keep="last")[["CNPJ", "NOME_FICHA", "SIGLA_FICHA"]]
        df_dim = pd.merge(df_dim, df_id_fichas, on="CNPJ", how="outer")
    else:
        df_dim["NOME_FICHA"] = None
        df_dim["SIGLA_FICHA"] = None

    # Enriquecimento com Salesforce Accounts
    if df_silver_salesforce_account is not None and not df_silver_salesforce_account.empty:
        df_sf = df_silver_salesforce_account.copy()
        df_sf["CNPJ"] = df_sf["CNPJ"].apply(normalizar_cnpj_coluna)
        sf_cols = {
            "CNPJ": "CNPJ",
            "Name": "NOME_SF",
            "Sigla__c": "SIGLA_SF",
            "Grupo_economico__c": "GRUPO_ECONOMICO_SF"
        }
        df_sf_id = df_sf[[c for c in sf_cols.keys() if c in df_sf.columns]].rename(columns=sf_cols)
        df_sf_id = df_sf_id.drop_duplicates(subset=["CNPJ"], keep="last")
        df_dim = pd.merge(df_dim, df_sf_id, on="CNPJ", how="outer")
    else:
        df_dim["NOME_SF"] = None
        df_dim["SIGLA_SF"] = None
        df_dim["GRUPO_ECONOMICO_SF"] = None

    for col_safe in ["NOME_SF", "SIGLA_SF", "NOME_FICHA", "SIGLA_FICHA", "GRUPO_ECONOMICO_SF", "RAZAO_SOCIAL"]:
        if col_safe not in df_dim.columns:
            df_dim[col_safe] = None

    df_dim["NOME"] = df_dim["RAZAO_SOCIAL"].combine_first(df_dim["NOME_SF"]).combine_first(df_dim["NOME_FICHA"])
    df_dim["SIGLA"] = df_dim["SIGLA_SF"].combine_first(df_dim["SIGLA_FICHA"])

    df_dim = df_dim.dropna(subset=["CNPJ"])
    df_dim["CNPJ_RAIZ"] = df_dim["CNPJ"].str[:8]
    df_dim["IS_MATRIZ"] = df_dim["CNPJ"].str[8:12] == "0001"

    # --- Enriquecimento com Grupo Econômico Homologado ---
    mapa_sub_homologada = {}
    if df_controladoras is not None and not df_controladoras.empty:
        col_c_sub = "CNPJ_SUBSIDIARIA" if "CNPJ_SUBSIDIARIA" in df_controladoras.columns else "CNPJ"
        col_c_mat = "CNPJ_CONTA_ATRELADA" if "CNPJ_CONTA_ATRELADA" in df_controladoras.columns else "CNPJ_CONTROLADORA"
        col_n_mat = "CONTA_ATRELADA" if "CONTA_ATRELADA" in df_controladoras.columns else "CONTROLADOR"

        for _, row_c in df_controladoras.iterrows():
            c_s = normalizar_cnpj_coluna(row_c.get(col_c_sub))
            c_m = normalizar_cnpj_coluna(row_c.get(col_c_mat))
            n_m = str(row_c.get(col_n_mat, "")).strip()
            if c_s and c_m:
                mapa_sub_homologada[c_s] = {
                    "CNPJ_CONTROLADORA": c_m,
                    "NOME_CONTROLADORA": n_m or f"GRUPO {c_m}",
                    "ORIGEM_VINCULO_GRUPO": "CONTROLADORA_HOMOLOGADA_PLANILHA"
                }

    df_dim["CNPJ_CONTROLADORA"] = None
    df_dim["NOME_CONTROLADORA"] = None
    df_dim["ORIGEM_VINCULO_GRUPO"] = "NAO_VINCULADO"

    for idx, r in df_dim.iterrows():
        c_ent = r["CNPJ"]
        if c_ent in mapa_sub_homologada:
            df_dim.at[idx, "CNPJ_CONTROLADORA"] = mapa_sub_homologada[c_ent]["CNPJ_CONTROLADORA"]
            df_dim.at[idx, "NOME_CONTROLADORA"] = mapa_sub_homologada[c_ent]["NOME_CONTROLADORA"]
            df_dim.at[idx, "ORIGEM_VINCULO_GRUPO"] = "CONTROLADORA_HOMOLOGADA_PLANILHA"
        elif pd.notna(r["GRUPO_ECONOMICO_SF"]) and str(r["GRUPO_ECONOMICO_SF"]).strip() not in ("", "None", "nan", "<NA>"):
            df_dim.at[idx, "NOME_CONTROLADORA"] = str(r["GRUPO_ECONOMICO_SF"]).strip()
            df_dim.at[idx, "ORIGEM_VINCULO_GRUPO"] = "SALESFORCE_CADASTRO"

    df_dim["GRUPO_ECONOMICO"] = df_dim["NOME_CONTROLADORA"].combine_first(df_dim["GRUPO_ECONOMICO_SF"]).combine_first(df_dim["NOME"])

    # Segmentação Metodológica Canônica
    if "SEGMENTO_METODOLOGICO" not in df_dim.columns:
        df_dim["SEGMENTO_METODOLOGICO"] = None

    if df_silver_fichas is not None and not df_silver_fichas.empty:
        df_fichas_seg = df_silver_fichas.copy()
        df_fichas_seg["CNPJ"] = df_fichas_seg["CNPJ"].apply(normalizar_cnpj_coluna)
        if "TIPO_FICHA" in df_fichas_seg.columns:
            mask_com = df_fichas_seg["TIPO_FICHA"].astype(str).str.upper() == "COMERCIALIZADORA"
            tipo_com_col = "TIPO_COMERCIALIZADORA" if "TIPO_COMERCIALIZADORA" in df_fichas_seg.columns else None
            df_fichas_seg["_SEG"] = None
            if tipo_com_col:
                df_fichas_seg.loc[mask_com & (df_fichas_seg[tipo_com_col].astype(str).str.upper() == "CPURA"), "_SEG"] = "CPURA"
                df_fichas_seg.loc[mask_com & (df_fichas_seg[tipo_com_col].astype(str).str.upper() == "CGRUPO"), "_SEG"] = "CGRUPO"
            df_fichas_seg.loc[mask_com & df_fichas_seg["_SEG"].isna(), "_SEG"] = "CGRUPO"

            mask_cons_ficha = df_fichas_seg["TIPO_FICHA"].astype(str).str.upper() == "CONSUMIDOR"
            df_fichas_seg.loc[mask_cons_ficha & df_fichas_seg["_SEG"].isna(), "_SEG"] = "CONSUMIDOR"

            df_com_map = df_fichas_seg.dropna(subset=["_SEG"]).drop_duplicates("CNPJ", keep="last")[["CNPJ", "_SEG"]]
            df_dim = pd.merge(df_dim, df_com_map, on="CNPJ", how="left")
            df_dim.loc[df_dim["_SEG"].isin(["CPURA", "CGRUPO"]), "SEGMENTO_METODOLOGICO"] = df_dim["_SEG"]
            df_dim.drop(columns=["_SEG"], inplace=True)

    vol_num = pd.to_numeric(df_dim.get("VOLUME_ENQUADRAMENTO_MWM"), errors="coerce")
    possui_5 = df_dim.get("POSSUI_PELO_MENOS_5_MWM")

    mask_nao_definido = df_dim["SEGMENTO_METODOLOGICO"].isna() | df_dim["SEGMENTO_METODOLOGICO"].isin(["NAO_ENQUADRADO", "CONSUMIDOR", ""])
    cond_gt5 = mask_nao_definido & ((possui_5 == True) | (vol_num >= 5.0))
    cond_le5 = mask_nao_definido & ((possui_5 == False) | ((vol_num < 5.0) & vol_num.notna()))

    df_dim.loc[cond_gt5, "SEGMENTO_METODOLOGICO"] = "CONSUMIDOR_GT_5"
    df_dim.loc[cond_le5, "SEGMENTO_METODOLOGICO"] = "CONSUMIDOR_LE_5"
    df_dim["SEGMENTO_METODOLOGICO"] = df_dim["SEGMENTO_METODOLOGICO"].fillna("NAO_ENQUADRADO")

    # --------------------------------------------------------------------------
    # CONSOLIDAÇÃO NO GRÃO DE CONTRAPARTE LÓGICA (1 LINHA POR CNPJ_RAIZ)
    # --------------------------------------------------------------------------
    # Ordenar priorizando Matriz (0001) para os dados cadastrais da contraparte
    df_dim_sorted = df_dim.sort_values(by=["CNPJ_RAIZ", "IS_MATRIZ"], ascending=[True, False])

    linhas_logicas = []
    for raiz, grp in df_dim_sorted.groupby("CNPJ_RAIZ"):
        row_matriz = grp.iloc[0]
        cnpj_matriz = row_matriz["CNPJ"]
        contraparte_id = f"CPT_{raiz}"

        # Volume consolidado da contraparte (máximo entre os estabelecimentos)
        vol_max = pd.to_numeric(grp["VOLUME_ENQUADRAMENTO_MWM"], errors="coerce").max()
        vol_max_val = vol_max if pd.notna(vol_max) else 0.0
        possui_5_mwm = bool(vol_max_val >= 5.0)

        # Prevalência de segmento metodológico se algum estabelecimento tiver CPURA/CGRUPO
        seg_final = row_matriz["SEGMENTO_METODOLOGICO"]
        if "CPURA" in grp["SEGMENTO_METODOLOGICO"].values:
            seg_final = "CPURA"
        elif "CGRUPO" in grp["SEGMENTO_METODOLOGICO"].values:
            seg_final = "CGRUPO"
        elif possui_5_mwm:
            seg_final = "CONSUMIDOR_GT_5"

        # Vínculo com Grupo Econômico
        ctrl_homologada = grp[grp["ORIGEM_VINCULO_GRUPO"] == "CONTROLADORA_HOMOLOGADA_PLANILHA"]
        if not ctrl_homologada.empty:
            r_ctrl = ctrl_homologada.iloc[0]
            grupo_id = f"GRP_{r_ctrl['CNPJ_CONTROLADORA']}"
            nome_grupo = r_ctrl["GRUPO_ECONOMICO"]
            cnpj_ctrl = r_ctrl["CNPJ_CONTROLADORA"]
            origem_grupo = "CONTROLADORA_HOMOLOGADA_PLANILHA"
        else:
            grupo_id = f"GRP_{raiz}"
            nome_grupo = row_matriz["GRUPO_ECONOMICO"]
            cnpj_ctrl = row_matriz["CNPJ_CONTROLADORA"]
            origem_grupo = row_matriz["ORIGEM_VINCULO_GRUPO"]

        linhas_logicas.append({
            "CONTRAPARTE_ID": contraparte_id,
            "CNPJ": cnpj_matriz,  # Chave retrocompatível apontando para a matriz
            "CNPJ_MATRIZ": cnpj_matriz,
            "CNPJ_RAIZ": raiz,
            "NOME": row_matriz["NOME"],
            "SIGLA": row_matriz["SIGLA"],
            "SITUACAO_CADASTRAL": row_matriz.get("SITUACAO_CADASTRAL", "NAO_INFORMADO"),
            "SETOR": row_matriz.get("CNAE_PRINCIPAL", "N/D"),
            "SEGMENTO_METODOLOGICO": seg_final,
            "VOLUME_ENQUADRAMENTO_MWM": vol_max_val,
            "POSSUI_PELO_MENOS_5_MWM": possui_5_mwm,
            "GRUPO_ID": grupo_id,
            "GRUPO_ECONOMICO": nome_grupo,
            "CNPJ_CONTROLADORA": cnpj_ctrl,
            "ORIGEM_VINCULO_GRUPO": origem_grupo,
            "_STATUS_REGISTRO": "VIGENTE"
        })

    df_final = pd.DataFrame(linhas_logicas)

    relational_dir = context.path("relational_dimensions") / "contrapartes"
    relational_dir.mkdir(parents=True, exist_ok=True)
    escrever_conjunto_de_dados_silver(df_final.to_dict(orient="records"), relational_dir, f"dim_contraparte_{run_id}")
    df_final.to_parquet(relational_dir / "dim_contraparte.parquet", index=False)
    try:
        df_final.to_parquet(context.path("relational_dimensions") / "dim_contraparte.parquet", index=False)
    except Exception:
        pass

    # Sincronização e Fechamento Referencial de dim_grupo_economico (100% de cobertura no Power BI)
    try:
        grp_dir = context.path("relational_dimensions") / "grupos_economicos"
        p_grp = grp_dir / "dim_grupo_economico.parquet"
        df_grp_existente = pd.read_parquet(p_grp) if p_grp.exists() else pd.DataFrame()
        grupos_conhecidos = set(df_grp_existente["GRUPO_ID"].dropna().unique()) if not df_grp_existente.empty else set()
        
        novos_grupos = []
        for _, r_cpt in df_final.iterrows():
            g_id = r_cpt["GRUPO_ID"]
            if g_id and g_id not in grupos_conhecidos:
                grupos_conhecidos.add(g_id)
                c_raiz = str(r_cpt.get("CNPJ_RAIZ") or str(r_cpt.get("CNPJ_MATRIZ", ""))[:8]).strip()
                
                # Regra de fallback severa para NOME_GRUPO:
                # row.get("NOME") or row.get("RAZAO_SOCIAL") or f"CONTROLE INDEPENDENTE - {cnpj_raiz}"
                # Nunca permitir string vazia, None ou NaN
                cands = [r_cpt.get("GRUPO_ECONOMICO"), r_cpt.get("NOME"), r_cpt.get("RAZAO_SOCIAL")]
                n_grp = None
                for cand in cands:
                    if cand is not None and pd.notna(cand):
                        s_c = str(cand).strip()
                        if s_c and s_c.upper() not in ("", "NONE", "NAN", "<NA>", "NULL"):
                            n_grp = s_c
                            break
                if not n_grp:
                    n_grp = f"CONTROLE INDEPENDENTE - {c_raiz}" if c_raiz else f"GRUPO - {g_id}"

                novos_grupos.append({
                    "GRUPO_ID": g_id,
                    "NOME_GRUPO": n_grp,
                    "CNPJ_CONTROLADORA": r_cpt.get("CNPJ_MATRIZ"),
                    "ORIGEM_MAPEAMENTO": "CONTRAPARTE_INDEPENDENTE",
                    "AVAL_HOMOLOGADO_COPEL": False,
                    "DATA_CRIACAO": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "_STATUS_REGISTRO": "VIGENTE"
                })
        
        df_novos_grp = pd.DataFrame(novos_grupos) if novos_grupos else pd.DataFrame()
        df_grp_atualizado = pd.concat([df_grp_existente, df_novos_grp], ignore_index=True).drop_duplicates(subset=["GRUPO_ID"])
        
        # Saneamento geral: nenhum registro em dim_grupo_economico pode ter NOME_GRUPO vazio
        if not df_grp_atualizado.empty:
            mask_inv_grp = (
                df_grp_atualizado["NOME_GRUPO"].isna() | 
                df_grp_atualizado["NOME_GRUPO"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "NULL"])
            )
            if mask_inv_grp.any():
                for idx_inv in df_grp_atualizado[mask_inv_grp].index:
                    c_m = df_grp_atualizado.at[idx_inv, "CNPJ_CONTROLADORA"]
                    gid = df_grp_atualizado.at[idx_inv, "GRUPO_ID"]
                    c_raiz_val = str(c_m)[:8] if c_m else str(gid).replace("GRP_", "")[:8]
                    df_grp_atualizado.at[idx_inv, "NOME_GRUPO"] = f"CONTROLE INDEPENDENTE - {c_raiz_val}"

            grp_dir.mkdir(parents=True, exist_ok=True)
            df_grp_atualizado.to_parquet(p_grp, index=False)
            df_grp_atualizado.to_csv(grp_dir / "dim_grupo_economico.csv", sep=";", index=False, encoding="utf-8-sig")
            logger.info("dim_grupo_economico sincronizada com %d grupos independentes adicionais (total=%d).", len(novos_grupos), len(df_grp_atualizado))
    except Exception as e_grp:
        logger.warning("Falha ao sincronizar dim_grupo_economico: %s", e_grp)

    logger.info("Dimensão Contraparte Lógica construída com sucesso. Contrapartes únicas: %d", len(df_final))
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}