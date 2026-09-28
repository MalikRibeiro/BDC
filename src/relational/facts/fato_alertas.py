"""Serviço de geração de alertas de crédito no padrão Star Schema (Fato Alerta).

Consome exclusivamente as Camadas Relacional (Dimensões e Fatos) e Silver padronizada,
eliminando dependências circulares com a Camada Gold e garantindo a linhagem medalhão estrita.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from common.identificadores import normalizar_cnpj_coluna
from control.logger import obter_logger
from relational.facts.fato_alerta_util import registrar_alertas_em_lote


def gerar_fato_alertas_credito(context: Any) -> dict[str, Any]:
    run_id = f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.alertas", Path("LOGS/relational") / f"{run_id}__servico_alertas.log")
    logger.info("Iniciando geração da Fato Alerta de Crédito (Arquitetura Medalhão Estrita)...")

    agora = datetime.now()
    hoje = agora

    # =========================================================================
    # 1. CARREGAMENTO DE DIMENSÕES E FATOS RELACIONAIS BASE
    # =========================================================================
    
    # 1.1 Dimensão Contraparte (Cadastro mestre, RFB e Salesforce)
    path_dim = context.path("relational_dimensions") / "contrapartes" / "dim_contraparte.parquet"
    if not path_dim.exists():
        path_dim = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"
    df_dim = pd.read_parquet(path_dim) if path_dim.exists() else pd.DataFrame()
    if not df_dim.empty and "CNPJ" in df_dim.columns:
        df_dim["CNPJ"] = df_dim["CNPJ"].apply(normalizar_cnpj_coluna)

    # 1.2 Fato Análise de Crédito (Risco, Rating, PD, Validade)
    path_anl = context.path("relational_facts") / "credito" / "fato_analise_credito.parquet"
    df_anl = pd.read_parquet(path_anl) if path_anl.exists() else pd.DataFrame()
    if not df_anl.empty and "CNPJ" in df_anl.columns:
        df_anl["CNPJ"] = df_anl["CNPJ"].apply(normalizar_cnpj_coluna)
        if "_STATUS_REGISTRO" in df_anl.columns:
            df_anl = df_anl[df_anl["_STATUS_REGISTRO"] == "VIGENTE"].copy()
        else:
            df_anl = df_anl.drop_duplicates(subset=["CNPJ"], keep="last").copy()

    # 1.3 Contratos Silver (Denodo) - Extração direta de status de fornecimento e volume
    path_ctr = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_ctr.exists():
        path_ctr = context.path("silver") / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
    df_ctr = pd.read_parquet(path_ctr) if path_ctr.exists() else pd.DataFrame()

    contratos_info: dict[str, dict[str, Any]] = {}
    if not df_ctr.empty and "CNPJ" in df_ctr.columns:
        df_ctr["CNPJ"] = df_ctr["CNPJ"].apply(normalizar_cnpj_coluna)
        col_vol = (
            "VOLUME_CONTRATADO_MENSAL_MWM"
            if "VOLUME_CONTRATADO_MENSAL_MWM" in df_ctr.columns
            else "VOLUME_MWM"
        )
        df_ctr["_VOL"] = pd.to_numeric(df_ctr.get(col_vol), errors="coerce").fillna(0.0) if col_vol in df_ctr.columns else 0.0

        col_in = "SUPRIMENTO_INICIO" if "SUPRIMENTO_INICIO" in df_ctr.columns else ("VIGENCIA_INICIO" if "VIGENCIA_INICIO" in df_ctr.columns else "inicio_suprimento")
        col_out = "SUPRIMENTO_TERMINO" if "SUPRIMENTO_TERMINO" in df_ctr.columns else ("VIGENCIA_FIM" if "VIGENCIA_FIM" in df_ctr.columns else "fim_suprimento")
        df_ctr["_DT_IN"] = pd.to_datetime(df_ctr.get(col_in), errors="coerce")
        df_ctr["_DT_OUT"] = pd.to_datetime(df_ctr.get(col_out), errors="coerce")

        df_ctr["_EH_VIGENTE"] = (
            (df_ctr.get("STATUS", df_ctr.get("id_status", "")).astype(str).str.upper().str.contains("ATIVO|EM SUPRIMENTO|2"))
            & (df_ctr["_DT_IN"] <= hoje)
            & (df_ctr["_DT_OUT"] >= hoje)
        )
        df_ctr["_EH_FUTURO"] = df_ctr["_DT_IN"] > hoje

        for cnpj, grp in df_ctr.groupby("CNPJ"):
            tem_vig = grp["_EH_VIGENTE"].any()
            tem_fut = grp["_EH_FUTURO"].any()
            status_ctr = "CONTRATO_VIGENTE" if tem_vig else ("CONTRATO_FUTURO" if tem_fut else "SEM_CONTRATO")
            vol_max = float(grp["_VOL"].max())
            contratos_info[cnpj] = {"STATUS_CONTRATUAL": status_ctr, "VOLUME_MWM": vol_max}

    # 1.4 Fato Reconciliação MtM e Risco
    path_mtm = context.path("relational_facts") / "reconciliacao" / "fato_reconciliacao_contrato_mtm.parquet"
    df_mtm = pd.read_parquet(path_mtm) if path_mtm.exists() else pd.DataFrame()

    # 1.5 Fato Garantia
    path_gar = context.path("relational_facts") / "credito" / "fato_garantia.parquet"
    df_gar = pd.read_parquet(path_gar) if path_gar.exists() else pd.DataFrame()

    # 1.6 Eventos Manuais e Overrides
    path_man = context.path("silver") / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"
    df_man = pd.read_parquet(path_man) if path_man.exists() else pd.DataFrame()

    # 1.7 Receita Federal Cadastral
    path_rfb = context.path("silver") / "receita" / "dados_cadastrais_rfb.parquet"
    if not path_rfb.exists():
        path_rfb = context.path("silver") / "receita_silver" / "receita_cadastral_silver.parquet"
    df_rfb = pd.read_parquet(path_rfb) if path_rfb.exists() else pd.DataFrame()

    alertas: list[dict[str, Any]] = []

    # =========================================================================
    # 2. REGRAS DE CARGA MANUAL (MAN_003)
    # =========================================================================
    if not df_man.empty and "_STATUS_REGISTRO" in df_man.columns:
        df_man_vigentes = df_man[df_man["_STATUS_REGISTRO"] == "VIGENTE"]
        for _, row_man in df_man_vigentes.iterrows():
            cnpj_man = row_man.get("CNPJ")
            campo = str(row_man.get("CAMPO_AFETADO", "")).upper()
            try:
                v_ant = float(row_man.get("VALOR_ANTERIOR")) if row_man.get("VALOR_ANTERIOR") is not None else 0.0
                v_nov = float(row_man.get("VALOR_NOVO")) if row_man.get("VALOR_NOVO") is not None else 0.0
                diff = abs(v_nov - v_ant)

                alerta_disparado = False
                # 1 bp (0.0001) para Taxas e %
                if campo in ["PD", "TAXA_RISCO", "PD_FINAL"]:
                    if diff > 0.0001:
                        alerta_disparado = True
                # 0.01 para Scores e Notas
                elif "SCORE" in campo or "NOTA" in campo:
                    if diff > 0.01:
                        alerta_disparado = True
                # 0.1% e R$ 100 para valores Nominais/Monetários
                else:
                    if diff > 100.0 and (v_ant != 0 and diff / abs(v_ant) > 0.001):
                        alerta_disparado = True

                if alerta_disparado:
                    alertas.append({
                        "CNPJ": cnpj_man,
                        "CODIGO_ALERTA": "MAN_003",
                        "SEVERIDADE": "MEDIO",
                        "REGRA": "Sobrescrita Manual Excede Tolerância",
                        "MENSAGEM_DESCRITIVA": f"Carga manual no campo {campo} excedeu tolerância da régua (diff: {diff:.4f}).",
                        "DATA_DETECCAO": agora,
                        "CAMPO_AFETADO": campo,
                        "VALOR_OBSERVADO": f"{v_ant} -> {v_nov}",
                        "LIMITE_ESPERADO": "Tolerância Aprovada",
                    })
            except (ValueError, TypeError) as e:
                logger.debug("Tolerância Carga Manual: skip conversão para CNPJ %s, campo %s: %s", cnpj_man, campo, e)

    # =========================================================================
    # 3. LOOKUPS O(1) PARA RECONCILIAÇÃO E CRÍTICAS EXTERNAS
    # =========================================================================
    rfb_situacao: dict[str, str] = {}
    if not df_rfb.empty and "CNPJ" in df_rfb.columns:
        rfb_situacao = df_rfb.drop_duplicates("CNPJ", keep="last").set_index("CNPJ")["SITUACAO_CADASTRAL"].to_dict()

    mtm_dados: dict[str, dict[str, Any]] = {}
    if not df_mtm.empty and "CNPJ" in df_mtm.columns:
        mtm_dados = df_mtm.drop_duplicates("CNPJ", keep="last").set_index("CNPJ").to_dict(orient="index")

    gar_vencidas_por_cnpj: set[str] = set()
    if not df_gar.empty and "CNPJ" in df_gar.columns and "STATUS_GARANTIA" in df_gar.columns:
        gar_vencidas_por_cnpj = set(df_gar.loc[df_gar["STATUS_GARANTIA"] == "VENCIDA", "CNPJ"].dropna().unique())

    # =========================================================================
    # 4. AVALIAÇÃO DE ALERTAS BASEADA NA LINHAGEM RELACIONAL
    # =========================================================================
    cnpjs_todos: set[str] = set()
    if not df_dim.empty:
        cnpjs_todos.update(df_dim["CNPJ"].dropna().unique())
    if not df_anl.empty:
        cnpjs_todos.update(df_anl["CNPJ"].dropna().unique())
    cnpjs_todos.update(contratos_info.keys())

    df_dim_unicos = df_dim.drop_duplicates(subset=["CNPJ"], keep="last") if not df_dim.empty else df_dim
    if not df_anl.empty:
        sort_cols = [c for c in ["DATA_ANALISE", "DT_PROCESSAMENTO", "_VERSAO_REGISTRO"] if c in df_anl.columns]
        if sort_cols:
            df_anl_sorted = df_anl.sort_values(by=sort_cols, na_position="first")
        else:
            df_anl_sorted = df_anl
        df_anl_unicos = df_anl_sorted.drop_duplicates(subset=["CNPJ"], keep="last")
    else:
        df_anl_unicos = df_anl

    dim_dict = df_dim_unicos.set_index("CNPJ").to_dict(orient="index") if not df_dim_unicos.empty else {}
    anl_dict = df_anl_unicos.set_index("CNPJ").to_dict(orient="index") if not df_anl_unicos.empty else {}

    for cnpj in sorted(cnpjs_todos):
        if not str(cnpj).strip():
            continue

        c_dim = dim_dict.get(cnpj, {})
        c_anl = anl_dict.get(cnpj, {})
        c_ctr = contratos_info.get(cnpj, {"STATUS_CONTRATUAL": "SEM_CONTRATO", "VOLUME_MWM": 0.0})

        status_contratual = c_ctr.get("STATUS_CONTRATUAL", "SEM_CONTRATO")
        vol_mwm = float(c_ctr.get("VOLUME_MWM", 0.0))

        sit_analise = str(c_anl.get("SITUACAO_ANALISE", ""))
        status_calculo_pd = str(c_anl.get("STATUS_CALCULO_PD", ""))
        rating_final = str(c_anl.get("RATING", ""))
        data_df = c_anl.get("DATA_BALANCO_USADO")

        seg_metodologico = str(c_dim.get("SEGMENTO_METODOLOGICO", c_anl.get("SEGMENTO_METODOLOGICO_FICHA", ""))).upper()

        # Classificação da Exigência
        if "COMERCIALIZADORA" in seg_metodologico or seg_metodologico in ["CPURA", "CGRUPO"]:
            metodologia = "DF_DETALHADA"
        elif vol_mwm >= 5.0:
            metodologia = "DF_DETALHADA"
        elif vol_mwm > 0.0:
            metodologia = "BUREAU"
        else:
            metodologia = "DISPENSADA"

        # EXC_001
        if status_calculo_pd == "PENDENTE":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "EXC_001", "SEVERIDADE": "ALTO",
                "REGRA": "Cálculo de PD Suspenso",
                "MENSAGEM_DESCRITIVA": "Motor suspendeu cálculo por falta de insumos.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_CALCULO_PD",
                "VALOR_OBSERVADO": status_calculo_pd, "LIMITE_ESPERADO": "CONCLUIDO",
            })

        # DOC_001
        if sit_analise == "PENDENTE_DOC":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "DOC_001", "SEVERIDADE": "MEDIO",
                "REGRA": "Documentação Faltante",
                "MENSAGEM_DESCRITIVA": "A análise está suspensa por falta de documentação.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_ANALISE",
                "VALOR_OBSERVADO": sit_analise, "LIMITE_ESPERADO": "VIGENTE",
            })

        # ANA_001
        if status_contratual == "CONTRATO_VIGENTE" and sit_analise == "VENCIDA":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "ANA_001", "SEVERIDADE": "ALTO",
                "REGRA": "Análise Vencida com Contrato Vigente",
                "MENSAGEM_DESCRITIVA": "Contraparte com contrato ativo e análise expirada.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_ANALISE",
                "VALOR_OBSERVADO": sit_analise, "LIMITE_ESPERADO": "VIGENTE",
            })

        # VOL_001
        if status_contratual == "CONTRATO_VIGENTE" and metodologia == "DF_DETALHADA" and sit_analise != "VIGENTE":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "VOL_001", "SEVERIDADE": "CRITICO",
                "REGRA": ">= 5MWm sem DF Vigente",
                "MENSAGEM_DESCRITIVA": "Volume exige DF (>= 5 MWm), mas análise não vigente.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "METODOLOGIA_EXIGIDA",
                "VALOR_OBSERVADO": f"Volume: {vol_mwm:.2f}", "LIMITE_ESPERADO": "DF Vigente",
            })

        # DF_001
        if metodologia == "DF_DETALHADA" and (pd.isna(data_df) or str(data_df).strip() in ("", "None", "nan", "NaT")):
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "DF_001", "SEVERIDADE": "CRITICO",
                "REGRA": "DF Ausente",
                "MENSAGEM_DESCRITIVA": "Balanço contábil não recebido para segmento elegível.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "DATA_DEMONSTRACAO_FINANCEIRA",
                "VALOR_OBSERVADO": "Nulo", "LIMITE_ESPERADO": "Data Preenchida",
            })

        # RAT_001 (PD Substituta)
        if status_calculo_pd == "CONCLUIDO_COM_PD_SUB":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "RAT_001", "SEVERIDADE": "ALTO",
                "REGRA": "Uso de PD Substituta (Dados Antigos)",
                "MENSAGEM_DESCRITIVA": "O Rating foi penalizado pelo acionamento de PD Substituta (DF Vencida).",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_CALCULO_PD",
                "VALOR_OBSERVADO": "CONCLUIDO_COM_PD_SUB", "LIMITE_ESPERADO": "CONCLUIDO",
            })

        # RAT_002 (Rating Deteriorado)
        if rating_final == "E":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "RAT_002", "SEVERIDADE": "ALTO",
                "REGRA": "Rating Deteriorado (E)",
                "MENSAGEM_DESCRITIVA": "Contraparte atingiu rating E (Alerta de Default ou Rejeição).",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "RATING_FINAL",
                "VALOR_OBSERVADO": rating_final, "LIMITE_ESPERADO": "A, B, C, D",
            })

        # CAD_001 (Receita Federal)
        sit_cad = str(rfb_situacao.get(cnpj, c_dim.get("SITUACAO_CADASTRAL", ""))).upper()
        if sit_cad and sit_cad not in ("ATIVA", "ATIVO", "NAO_INFORMADO"):
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "CAD_001", "SEVERIDADE": "CRITICO",
                "REGRA": "Situação Cadastral Irregular",
                "MENSAGEM_DESCRITIVA": "Situação na Receita Federal não é ATIVA.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_CADASTRAL",
                "VALOR_OBSERVADO": sit_cad, "LIMITE_ESPERADO": "ATIVA",
            })

        # EXP_001 e CTR_001 (MtM)
        mtm_info = mtm_dados.get(cnpj)
        if mtm_info:
            try:
                perc_uso = float(mtm_info.get("PERCENTUAL_USO_LIMITE", 0.0))
                if perc_uso > 100.0:
                    alertas.append({
                        "CNPJ": cnpj, "CODIGO_ALERTA": "EXP_001", "SEVERIDADE": "CRITICO",
                        "REGRA": "Estouro de Limite (MtM)",
                        "MENSAGEM_DESCRITIVA": "Uso de limite ultrapassou 100% da exposição aprovada.",
                        "DATA_DETECCAO": agora, "CAMPO_AFETADO": "PERCENTUAL_USO_LIMITE",
                        "VALOR_OBSERVADO": f"{perc_uso}%", "LIMITE_ESPERADO": "<= 100%",
                    })
            except (ValueError, TypeError) as e:
                logger.debug("Skip cálculo PERCENTUAL_USO_LIMITE para CNPJ %s: %s", cnpj, e)

            status_rec = str(mtm_info.get("STATUS_RECONCILIACAO", "")).upper()
            if status_rec == "DIVERGENTE":
                alertas.append({
                    "CNPJ": cnpj, "CODIGO_ALERTA": "CTR_001", "SEVERIDADE": "MEDIO",
                    "REGRA": "Divergência Contratual",
                    "MENSAGEM_DESCRITIVA": "O contrato Denodo diverge da carga MtM.",
                    "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_RECONCILIACAO",
                    "VALOR_OBSERVADO": status_rec, "LIMITE_ESPERADO": "CONVERGENTE",
                })

        # GAR_001 (Garantia Vencida)
        if cnpj in gar_vencidas_por_cnpj:
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "GAR_001", "SEVERIDADE": "MEDIO",
                "REGRA": "Garantia Vencida",
                "MENSAGEM_DESCRITIVA": "Existe garantia atrelada ao CNPJ que está vencida.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_GARANTIA",
                "VALOR_OBSERVADO": "VENCIDA", "LIMITE_ESPERADO": "VIGENTE",
            })

        # GRP_001 (CGRUPO sem Holding)
        holding_cnpj = c_dim.get("CNPJ_CONTROLADORA")
        if seg_metodologico == "CGRUPO" and (pd.isna(holding_cnpj) or not str(holding_cnpj).strip()):
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "GRP_001", "SEVERIDADE": "MEDIO",
                "REGRA": "CGRUPO sem Holding",
                "MENSAGEM_DESCRITIVA": "Classificado como CGRUPO mas sem holding declarada.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "HOLDING_CNPJ",
                "VALOR_OBSERVADO": "Nulo", "LIMITE_ESPERADO": "CNPJ Válido",
            })

    # =========================================================================
    # 5. PERSISTÊNCIA DA FATO ALERTA EM LOTE
    # =========================================================================
    if alertas:
        alertas_formatados = []
        for alerta in alertas:
            alertas_formatados.append({
                "contraparte_id": alerta.get("CNPJ"),
                "codigo": alerta.get("CODIGO_ALERTA"),
                "severidade": alerta.get("SEVERIDADE"),
                "regra": alerta.get("REGRA"),
                "mensagem": alerta.get("MENSAGEM_DESCRITIVA"),
                "campo_afetado": alerta.get("CAMPO_AFETADO"),
                "valor_observado": str(alerta.get("VALOR_OBSERVADO")),
                "limite_esperado": str(alerta.get("LIMITE_ESPERADO")),
                "status_tratamento": alerta.get("STATUS_TRATAMENTO", "ABERTO") if pd.notna(alerta.get("STATUS_TRATAMENTO")) else "ABERTO",
                "responsavel": str(alerta.get("RESPONSAVEL")) if pd.notna(alerta.get("RESPONSAVEL")) else None,
                "evidencia_encerramento": str(alerta.get("EVIDENCIA_ENCERRAMENTO")) if pd.notna(alerta.get("EVIDENCIA_ENCERRAMENTO")) else None,
            })
        registrar_alertas_em_lote(alertas_formatados, run_id, context)

    logger.info("Fato Alerta gerada com sucesso via Camada Relacional. Total de alertas: %d", len(alertas))

    return {
        "status": "SUCESSO",
        "total_alertas": len(alertas),
    }
