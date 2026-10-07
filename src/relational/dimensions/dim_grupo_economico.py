"""Serviço de consolidação da Dimensão de Grupo Econômico.

Em conformidade com a governança do BDC e regras homologadas:
1. Base legal prioritária e estrita de herança: Controladora e Subsidiaria.xlsx
   (ingerida via controlador_connector / servico_controlador).
2. Base cadastral secundária: Salesforce Accounts (apenas grupos comerciais conhecidos,
   sem inferir herança financeira entre CNPJs distintos fora da planilha homologada).
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from common.identificadores import normalizar_cnpj_coluna


def _gerar_grupo_id(nome_grupo: str, cnpj_controladora: str | None = None) -> str:
    """Gera chave canônica determinística para o grupo econômico."""
    if cnpj_controladora and str(cnpj_controladora).strip() not in ("", "None", "nan", "<NA>"):
        return f"GRP_{str(cnpj_controladora).strip()}"
    chave = str(nome_grupo).strip().upper()
    return f"GRP_{hashlib.md5(chave.encode('utf-8')).hexdigest()[:12]}"


def processar_dim_grupo_economico(context: AppContext) -> dict[str, Any]:
    """Orquestra a leitura das fontes de controladoras e Salesforce para montar dim_grupo_economico."""
    run_id = f"DIM_GRP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.dim_grupo_economico", Path("LOGS/relational") / f"{run_id}__dim_grupo_economico.log")
    logger.info("Iniciando construção da Dimensão de Grupo Econômico (run_id=%s)...", run_id)

    # 1. Carregar Planilha Homologada de Controladoras (Silver)
    ctrl_path = context.path("silver") / "mapeamento_controladoras" / "mapeamento_controladoras.parquet"
    df_ctrl = pd.read_parquet(ctrl_path) if ctrl_path.exists() else pd.DataFrame()
    if not df_ctrl.empty and "_STATUS_REGISTRO" in df_ctrl.columns:
        df_ctrl = df_ctrl[df_ctrl["_STATUS_REGISTRO"] == "VIGENTE"]

    # 2. Carregar Salesforce Accounts (Silver)
    salesforce_path = context.path("silver") / "salesforce_silver" / "account" / "salesforce_account.parquet"
    df_sf = pd.read_parquet(salesforce_path) if salesforce_path.exists() else pd.DataFrame()

    registros: list[dict[str, Any]] = []
    cnpjs_homologados_vistos = set()

    # 1. Processar Grupos Homologados da Planilha Oficial
    if not df_ctrl.empty:
        col_ctrl = "CNPJ_CONTA_ATRELADA" if "CNPJ_CONTA_ATRELADA" in df_ctrl.columns else "CNPJ_CONTROLADORA"
        col_nome_ctrl = "CONTA_ATRELADA" if "CONTA_ATRELADA" in df_ctrl.columns else "CONTROLADOR"

        df_homologados = df_ctrl[[col_ctrl, col_nome_ctrl]].dropna(subset=[col_ctrl]).drop_duplicates(subset=[col_ctrl])
        for _, row in df_homologados.iterrows():
            c_ctrl = normalizar_cnpj_coluna(row[col_ctrl])
            raw_nome = row.get(col_nome_ctrl)
            s_nome = str(raw_nome).strip() if (pd.notna(raw_nome) and raw_nome is not None) else ""
            if not s_nome or s_nome.upper() in ("", "NONE", "NAN", "<NA>", "NULL"):
                n_ctrl = f"GRUPO {c_ctrl}" if c_ctrl else f"CONTROLE INDEPENDENTE - {row.get('CNPJ', '')[:8]}"
            else:
                n_ctrl = s_nome

            if c_ctrl:
                cnpjs_homologados_vistos.add(c_ctrl)
                registros.append({
                    "GRUPO_ID": _gerar_grupo_id(n_ctrl, c_ctrl),
                    "NOME_GRUPO": n_ctrl,
                    "CNPJ_CONTROLADORA": c_ctrl,
                    "ORIGEM_MAPEAMENTO": "CONTROLADORA_HOMOLOGADA_PLANILHA",
                    "AVAL_HOMOLOGADO_COPEL": True,
                    "DATA_CRIACAO": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "_STATUS_REGISTRO": "VIGENTE"
                })

    # 2. Processar Grupos Conhecidos via Salesforce (Sem Aval Homologado de Herança)
    if not df_sf.empty and "Grupo_economico__c" in df_sf.columns:
        df_sf_grupos = df_sf[["Grupo_economico__c", "CNPJ"]].dropna(subset=["Grupo_economico__c"]).copy()
        df_sf_grupos["Grupo_economico__c"] = df_sf_grupos["Grupo_economico__c"].astype(str).str.strip()
        df_sf_grupos = df_sf_grupos[~df_sf_grupos["Grupo_economico__c"].isin(["", "None", "nan", "<NA>", "NULL"])]
        
        grupos_unicos = df_sf_grupos["Grupo_economico__c"].unique()
        nomes_homologados = {r["NOME_GRUPO"].upper() for r in registros}

        for grp_nome in grupos_unicos:
            if grp_nome.upper() not in nomes_homologados:
                registros.append({
                    "GRUPO_ID": _gerar_grupo_id(grp_nome, None),
                    "NOME_GRUPO": grp_nome,
                    "CNPJ_CONTROLADORA": None,
                    "ORIGEM_MAPEAMENTO": "SALESFORCE_CADASTRO",
                    "AVAL_HOMOLOGADO_COPEL": False,
                    "DATA_CRIACAO": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "_STATUS_REGISTRO": "VIGENTE"
                })

    df_grupo = pd.DataFrame(registros)
    if df_grupo.empty:
        df_grupo = pd.DataFrame(columns=[
            "GRUPO_ID", "NOME_GRUPO", "CNPJ_CONTROLADORA", "ORIGEM_MAPEAMENTO",
            "AVAL_HOMOLOGADO_COPEL", "DATA_CRIACAO", "_STATUS_REGISTRO"
        ])
    else:
        # Fallback severo: garantia absoluta de não haver strings vazias, None ou NaN
        mask_invalido = (
            df_grupo["NOME_GRUPO"].isna() | 
            df_grupo["NOME_GRUPO"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "NULL"])
        )
        if mask_invalido.any():
            for idx in df_grupo[mask_invalido].index:
                c_ctrl_val = df_grupo.at[idx, "CNPJ_CONTROLADORA"]
                g_id_val = df_grupo.at[idx, "GRUPO_ID"]
                df_grupo.at[idx, "NOME_GRUPO"] = f"CONTROLE INDEPENDENTE - {c_ctrl_val[:8]}" if c_ctrl_val else f"GRUPO - {g_id_val}"
        df_grupo = df_grupo.drop_duplicates(subset=["GRUPO_ID"]).reset_index(drop=True)

    relational_dir = context.path("relational_dimensions") / "grupos_economicos"
    relational_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = relational_dir / "dim_grupo_economico.parquet"
    csv_path = relational_dir / "dim_grupo_economico.csv"

    df_grupo.to_parquet(parquet_path, index=False)
    df_grupo.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")

    logger.info("Dimensão Grupo Econômico persistida com sucesso em %s (%d registros).", parquet_path, len(df_grupo))
    return {"run_id": run_id, "linhas": len(df_grupo), "status": "SUCESSO"}
