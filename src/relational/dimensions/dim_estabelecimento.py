"""Serviço de consolidação da Dimensão de Estabelecimentos.

Grão: 1 linha por CNPJ completo de 14 dígitos (permitindo distinção de Matriz e Filiais).

Implementa as duas bases legais autorizadas de herança de risco:
1. Matriz/Filial (mesma pessoa jurídica, CNPJ[:8] idêntico, herança automática determinística).
2. Controladora/Subsidiária (pessoas jurídicas distintas, com garantia formal, estritamente
   restrita aos pares da planilha homologada 'Controladora e Subsidiaria.xlsx').
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from common.identificadores import normalizar_cnpj_coluna
from common.dados import carregar_fichas_silver_consolidadas


def processar_dim_estabelecimento(context: AppContext) -> dict[str, Any]:
    """Orquestra a montagem da Dimensão de Estabelecimentos."""
    run_id = f"DIM_EST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.dim_estabelecimento", Path("LOGS/relational") / f"{run_id}__dim_estabelecimento.log")
    logger.info("Iniciando consolidação da Dimensão de Estabelecimentos (run_id=%s)...", run_id)

    silver_dir = context.path("silver")

    # 1. Carregar bases de entrada para capturar todos os CNPJs do universo BDC
    # A) Receita Federal
    rec_path = silver_dir / "receita_silver" / "receita_cadastral_silver.parquet"
    df_rec = pd.read_parquet(rec_path) if rec_path.exists() else pd.DataFrame()

    # B) Contratos Denodo
    ctr_path = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not ctr_path.exists():
        ctr_path = silver_dir / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
    df_ctr = pd.read_parquet(ctr_path) if ctr_path.exists() else pd.DataFrame()

    # C) Fichas Consolidadas
    df_fichas = carregar_fichas_silver_consolidadas(silver_dir)

    # D) Salesforce Accounts
    sf_path = silver_dir / "salesforce_silver" / "account" / "salesforce_account.parquet"
    df_sf = pd.read_parquet(sf_path) if sf_path.exists() else pd.DataFrame()

    # E) Planilha Homologada de Controladoras
    ctrl_path = silver_dir / "mapeamento_controladoras" / "mapeamento_controladoras.parquet"
    df_ctrl = pd.read_parquet(ctrl_path) if ctrl_path.exists() else pd.DataFrame()
    if not df_ctrl.empty and "_STATUS_REGISTRO" in df_ctrl.columns:
        df_ctrl = df_ctrl[df_ctrl["_STATUS_REGISTRO"] == "VIGENTE"]

    # F) Bureau de Crédito (Risk3)
    bureau_path = silver_dir / "bureau_silver" / "bureau_cadastral_silver.parquet"
    df_bureau = pd.read_parquet(bureau_path) if bureau_path.exists() else pd.DataFrame()

    # 2. Consolidar universo de CNPJs únicos de 14 dígitos
    todos_cnpjs = set()
    mapa_nomes: dict[str, str] = {}
    mapa_situacao: dict[str, str] = {}
    mapa_cnae: dict[str, str] = {}

    if not df_rec.empty and "CNPJ" in df_rec.columns:
        df_rec["CNPJ"] = df_rec["CNPJ"].apply(normalizar_cnpj_coluna)
        for _, r in df_rec.iterrows():
            c = r["CNPJ"]
            if c:
                todos_cnpjs.add(c)
                if pd.notna(r.get("RAZAO_SOCIAL")): mapa_nomes[c] = str(r["RAZAO_SOCIAL"]).strip()
                if pd.notna(r.get("SITUACAO_CADASTRAL")): mapa_situacao[c] = str(r["SITUACAO_CADASTRAL"]).strip()
                if pd.notna(r.get("CNAE_PRINCIPAL")): mapa_cnae[c] = str(r["CNAE_PRINCIPAL"]).strip()

    col_cnpj_ctr = "CNPJ" if "CNPJ" in df_ctr.columns else ("CONTRAPARTE_CNPJ" if "CONTRAPARTE_CNPJ" in df_ctr.columns else None)
    if col_cnpj_ctr and not df_ctr.empty:
        df_ctr[col_cnpj_ctr] = df_ctr[col_cnpj_ctr].apply(normalizar_cnpj_coluna)
        for _, r in df_ctr.iterrows():
            c = r[col_cnpj_ctr]
            if c:
                todos_cnpjs.add(c)
                col_n = "CONTRAPARTE_NOME_FANTASIA" if "CONTRAPARTE_NOME_FANTASIA" in df_ctr.columns else "CONTRAPARTE"
                if c not in mapa_nomes and col_n in df_ctr.columns and pd.notna(r[col_n]):
                    mapa_nomes[c] = str(r[col_n]).strip()

    if not df_fichas.empty and "CNPJ" in df_fichas.columns:
        df_fichas["CNPJ"] = df_fichas["CNPJ"].apply(normalizar_cnpj_coluna)
        for _, r in df_fichas.iterrows():
            c = r["CNPJ"]
            if c:
                todos_cnpjs.add(c)
                if c not in mapa_nomes and pd.notna(r.get("RAZAO_SOCIAL")):
                    mapa_nomes[c] = str(r["RAZAO_SOCIAL"]).strip()

    if not df_sf.empty and "CNPJ" in df_sf.columns:
        df_sf["CNPJ"] = df_sf["CNPJ"].apply(normalizar_cnpj_coluna)
        for _, r in df_sf.iterrows():
            c = r["CNPJ"]
            if c:
                todos_cnpjs.add(c)
                if c not in mapa_nomes and pd.notna(r.get("Name")):
                    mapa_nomes[c] = str(r["Name"]).strip()

    if not df_ctrl.empty:
        for col_c in ["CNPJ_SUBSIDIARIA", "CNPJ_CONTA_ATRELADA"]:
            if col_c in df_ctrl.columns:
                df_ctrl[col_c] = df_ctrl[col_c].apply(normalizar_cnpj_coluna)
                todos_cnpjs.update(df_ctrl[col_c].dropna().unique())

    # 3. Mapear quem tem ANÁLISE PRÓPRIA DIRETA EFETIVA (expurgando análises herdadas e registros vazios)
    cnpjs_com_analise_propria = set()
    fato_path = context.path("relational_facts") / "credito" / "fato_analise_credito.parquet"
    if fato_path.exists():
        df_fato_temp = pd.read_parquet(fato_path)
        if not df_fato_temp.empty and "CNPJ" in df_fato_temp.columns:
            if "ANALISE_HERDADA" in df_fato_temp.columns:
                df_fato_temp = df_fato_temp[df_fato_temp["ANALISE_HERDADA"] != True]
            if "ORIGEM_ANALISE" in df_fato_temp.columns:
                df_fato_temp = df_fato_temp[~df_fato_temp["ORIGEM_ANALISE"].astype(str).str.contains("HERDADA", case=False, na=False)]
            
            # Exigir Rating ou PD efetivo para ser considerado análise própria válida
            col_r = "RATING" if "RATING" in df_fato_temp.columns else ("RATING_FINAL" if "RATING_FINAL" in df_fato_temp.columns else None)
            col_p = "PD_PERCENTUAL" if "PD_PERCENTUAL" in df_fato_temp.columns else ("PD_FINAL" if "PD_FINAL" in df_fato_temp.columns else None)
            mask_val = pd.Series(True, index=df_fato_temp.index)
            if col_r and col_p:
                r_val = df_fato_temp[col_r].notna() & (~df_fato_temp[col_r].astype(str).str.strip().isin(["", "None", "nan", "<NA>"]))
                p_val = df_fato_temp[col_p].notna() & (~df_fato_temp[col_p].isna())
                mask_val = r_val | p_val
            elif col_r:
                mask_val = df_fato_temp[col_r].notna() & (~df_fato_temp[col_r].astype(str).str.strip().isin(["", "None", "nan", "<NA>"]))
            
            df_fato_temp = df_fato_temp[mask_val]
            df_fato_temp["CNPJ"] = df_fato_temp["CNPJ"].apply(normalizar_cnpj_coluna)
            cnpjs_com_analise_propria.update(df_fato_temp["CNPJ"].dropna().unique())

    # Mapear CNPJs com análise estritamente VIGENTE hoje
    hoje = pd.Timestamp.now().normalize()
    cnpjs_com_analise_vigente = set()
    if fato_path.exists() and not df_fato_temp.empty:
        col_fim = "FIM_VIGENCIA_ANALISE" if "FIM_VIGENCIA_ANALISE" in df_fato_temp.columns else None
        col_dt = "DATA_ANALISE" if "DATA_ANALISE" in df_fato_temp.columns else None
        if col_fim:
            mask_vig = pd.to_datetime(df_fato_temp[col_fim], errors="coerce").dt.normalize() >= hoje
            cnpjs_com_analise_vigente.update(df_fato_temp.loc[mask_vig, "CNPJ"].dropna().unique())
        elif col_dt:
            mask_vig = pd.to_datetime(df_fato_temp[col_dt], errors="coerce").dt.normalize() + pd.DateOffset(months=18) >= hoje
            cnpjs_com_analise_vigente.update(df_fato_temp.loc[mask_vig, "CNPJ"].dropna().unique())

    if not cnpjs_com_analise_propria:
        if not df_fichas.empty and "CNPJ" in df_fichas.columns:
            cnpjs_com_analise_propria.update(df_fichas["CNPJ"].dropna().unique())
        if not df_bureau.empty and "CNPJ" in df_bureau.columns:
            df_bureau["CNPJ"] = df_bureau["CNPJ"].apply(normalizar_cnpj_coluna)
            cnpjs_com_analise_propria.update(df_bureau["CNPJ"].dropna().unique())

    # 4. Mapear Matriz Canônica e CNPJ com Análise por Raiz (priorizando matriz 0001)
    mapa_raiz_para_matriz: dict[str, str] = {}
    todos_cnpjs_ordenados = sorted(list(todos_cnpjs), key=lambda x: (x[8:12] != "0001", x))
    for c in todos_cnpjs_ordenados:
        r = c[:8]
        if r not in mapa_raiz_para_matriz:
            mapa_raiz_para_matriz[r] = c

    mapa_raiz_com_analise: dict[str, str] = {}
    for c in sorted(list(cnpjs_com_analise_propria), key=lambda x: (x[8:12] != "0001", x)):
        r = c[:8]
        if r not in mapa_raiz_com_analise:
            mapa_raiz_com_analise[r] = c

    # 5. Mapear Pares Homologados da Planilha de Controladoras (ESTRITO - SEM INFERÊNCIA)
    mapa_sub_para_ctrl: dict[str, str] = {}
    if not df_ctrl.empty and "CNPJ_SUBSIDIARIA" in df_ctrl.columns and "CNPJ_CONTA_ATRELADA" in df_ctrl.columns:
        for _, r in df_ctrl.iterrows():
            c_sub = r["CNPJ_SUBSIDIARIA"]
            c_mat = r["CNPJ_CONTA_ATRELADA"]
            if c_sub and c_mat and c_sub != c_mat:
                mapa_sub_para_ctrl[c_sub] = c_mat

    # 6. Construir Registros da Dimensão com a Precedência Societária Estrita
    registros_estab = []
    for cnpj in sorted(list(todos_cnpjs)):
        raiz = cnpj[:8]
        eh_matriz = (len(cnpj) >= 12 and cnpj[8:12] == "0001")
        contraparte_id = f"CPT_{raiz}"
        nome_est = mapa_nomes.get(cnpj, f"ESTABELECIMENTO {cnpj}")
        sit_cad = mapa_situacao.get(cnpj, "NAO_INFORMADO")
        cnae = mapa_cnae.get(cnpj, "N/D")

        # Regra de Precedência Societária e Legal
        if cnpj in mapa_sub_para_ctrl:
            # 2ª Base Legal: Controladora Homologada (planilha oficial Copel)
            ctrl_alvo = mapa_sub_para_ctrl[cnpj]
            ctrl_doador = mapa_raiz_com_analise.get(ctrl_alvo[:8], ctrl_alvo)
            ctrl_tem_vigente = (ctrl_alvo in cnpjs_com_analise_vigente) or (ctrl_doador in cnpjs_com_analise_vigente)
            sub_tem_vigente = cnpj in cnpjs_com_analise_vigente

            # Se a controladora estiver VENCIDA ou SEM ANÁLISE, e a subsidiária tiver análise VIGENTE:
            # A análise própria vigente da subsidiária assume para não mascarar o risco ativo da carteira.
            if not ctrl_tem_vigente and sub_tem_vigente:
                origem_heranca = "ANALISE_PROPRIA_DIRETA"
                cnpj_doador = cnpj
            else:
                origem_heranca = "CONTROLADORA_HOMOLOGADA_PLANILHA"
                cnpj_doador = ctrl_doador
        elif not eh_matriz and raiz in mapa_raiz_para_matriz and mapa_raiz_para_matriz[raiz] != cnpj:
            # 1ª Base Legal: Matriz/Filial (mesma raiz)
            origem_heranca = "MATRIZ_FILIAL_CNPJ_RAIZ"
            cnpj_doador = mapa_raiz_com_analise.get(raiz, mapa_raiz_para_matriz[raiz])
        elif cnpj in cnpjs_com_analise_propria:
            # Análise Própria Direta (não requer herança societária)
            origem_heranca = "ANALISE_PROPRIA_DIRETA"
            cnpj_doador = cnpj
        else:
            origem_heranca = "NAO_HERDADO"
            cnpj_doador = None

        registros_estab.append({
            "CNPJ": cnpj,
            "CONTRAPARTE_ID": contraparte_id,
            "CNPJ_RAIZ": raiz,
            "EH_MATRIZ": eh_matriz,
            "NOME_ESTABELECIMENTO": nome_est,
            "SITUACAO_CADASTRAL": sit_cad,
            "CNAE_PRINCIPAL": cnae,
            "ORIGEM_HERANCA_RISCO": origem_heranca,
            "CNPJ_DOADOR_RISCO": cnpj_doador,
            "DATA_ATUALIZACAO": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "_STATUS_REGISTRO": "VIGENTE"
        })

    df_estab = pd.DataFrame(registros_estab)
    relational_dir = context.path("relational_dimensions") / "estabelecimentos"
    relational_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = relational_dir / "dim_estabelecimento.parquet"
    csv_path = relational_dir / "dim_estabelecimento.csv"

    df_estab.to_parquet(parquet_path, index=False)
    df_estab.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")

    logger.info("Dimensão Estabelecimentos salva com sucesso em %s (%d registros).", parquet_path, len(df_estab))
    return {"run_id": run_id, "linhas": len(df_estab), "status": "SUCESSO"}
