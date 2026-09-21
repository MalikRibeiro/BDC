"""Serviço de geração de alertas de crédito no padrão Star Schema (Fato Alerta)."""
import pandas as pd
from datetime import datetime
from typing import Any

from pathlib import Path
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def gerar_fato_alertas_credito(context: Any) -> dict[str, Any]:
    run_id = f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.alertas", Path("LOGS/relational") / f"{run_id}__servico_alertas.log")
    logger.info("Iniciando geração da Fato Alerta de Crédito (Star Schema)...")

    colunas_exigidas = [
        "CNPJ", "CODIGO_ALERTA", "SEVERIDADE", "REGRA", "MENSAGEM_DESCRITIVA", 
        "DATA_DETECCAO", "CAMPO_AFETADO", "VALOR_OBSERVADO", "LIMITE_ESPERADO", 
        "STATUS_TRATAMENTO", "RESPONSAVEL", "EVIDENCIA_ENCERRAMENTO"
    ]

    path_gold = context.path("saidas") / "gold" / "visao_operacional_negocio" / "Visao_Operacional_BDC_LATEST.parquet"
    if not path_gold.exists():
        logger.warning(f"Base Gold LATEST não encontrada em {path_gold}. Abortando alertas.")
        return {"run_id": run_id, "alertas_gerados": 0, "status": "SEM_BASE"}

    df_gold = pd.read_parquet(path_gold)
    
    # Left Joins Defensivos (Ação 2)
    path_rfb = context.path("silver") / "receita" / "dados_cadastrais_rfb.parquet"
    df_rfb = pd.read_parquet(path_rfb) if path_rfb.exists() else pd.DataFrame()
    
    path_mtm = context.path("relational_facts") / "reconciliacao" / "fato_reconciliacao_contrato_mtm.parquet"
    df_mtm = pd.read_parquet(path_mtm) if path_mtm.exists() else pd.DataFrame()
    
    path_gar = context.path("relational_facts") / "credito" / "fato_garantia.parquet"
    df_gar = pd.read_parquet(path_gar) if path_gar.exists() else pd.DataFrame()
    
    path_man = context.path("silver") / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"
    df_man = pd.read_parquet(path_man) if path_man.exists() else pd.DataFrame()
    
    alertas = []
    agora = datetime.now()

    # MAN_003: Avaliar tolerância de Carga Manual/Overrides (Ação 2)
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
                        "CNPJ": cnpj_man, "CODIGO_ALERTA": "MAN_003", "SEVERIDADE": "MEDIO",
                        "REGRA": "Sobrescrita Manual Excede Tolerância",
                        "MENSAGEM_DESCRITIVA": f"Carga manual no campo {campo} excedeu tolerância da régua (diff: {diff:.4f}).",
                        "DATA_DETECCAO": agora, "CAMPO_AFETADO": campo,
                        "VALOR_OBSERVADO": f"{v_ant} -> {v_nov}", "LIMITE_ESPERADO": "Tolerância Aprovada"
                    })
            except (ValueError, TypeError):
                pass
                
    for _, row in df_gold.iterrows():
        cnpj = row.get("CNPJ")
        if pd.isna(cnpj) or not str(cnpj).strip(): continue
            
        status_contratual = str(row.get("STATUS_CONTRATUAL", ""))
        sit_analise = str(row.get("SITUACAO_ANALISE", ""))
        metodologia = str(row.get("METODOLOGIA_EXIGIDA", ""))
        vol_mwm = pd.to_numeric(row.get("VOLUME_MWM"), errors="coerce")
        if pd.isna(vol_mwm): vol_mwm = 0.0
        status_calculo_pd = str(row.get("STATUS_CALCULO_PD", ""))
        rating_final = str(row.get("RATING_FINAL", ""))

        # EXC_001
        if status_calculo_pd == "PENDENTE":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "EXC_001", "SEVERIDADE": "ALTO",
                "REGRA": "Cálculo de PD Suspenso",
                "MENSAGEM_DESCRITIVA": "Motor suspendeu cálculo por falta de insumos.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_CALCULO_PD",
                "VALOR_OBSERVADO": status_calculo_pd, "LIMITE_ESPERADO": "CONCLUIDO"
            })

        # DOC_001
        if sit_analise == "PENDENTE_DOC":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "DOC_001", "SEVERIDADE": "MEDIO",
                "REGRA": "Documentação Faltante",
                "MENSAGEM_DESCRITIVA": "A análise está suspensa por falta de documentação.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_ANALISE",
                "VALOR_OBSERVADO": sit_analise, "LIMITE_ESPERADO": "VIGENTE"
            })

        # ANA_001
        if status_contratual == "CONTRATO_VIGENTE" and sit_analise == "VENCIDA":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "ANA_001", "SEVERIDADE": "ALTO",
                "REGRA": "Análise Vencida com Contrato Vigente",
                "MENSAGEM_DESCRITIVA": "Contraparte com contrato ativo e análise expirada.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_ANALISE",
                "VALOR_OBSERVADO": sit_analise, "LIMITE_ESPERADO": "VIGENTE"
            })
            
        # VOL_001
        if status_contratual == "CONTRATO_VIGENTE" and metodologia == "DF_DETALHADA" and sit_analise != "VIGENTE":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "VOL_001", "SEVERIDADE": "CRITICO",
                "REGRA": ">= 5MWm sem DF Vigente",
                "MENSAGEM_DESCRITIVA": "Volume exige DF (>= 5 MWm), mas análise não vigente.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "METODOLOGIA_EXIGIDA",
                "VALOR_OBSERVADO": f"Volume: {vol_mwm:.2f}", "LIMITE_ESPERADO": "DF Vigente"
            })
            
        # DF_001
        if metodologia == "DF_DETALHADA" and pd.isna(row.get("DATA_DEMONSTRACAO_FINANCEIRA")):
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "DF_001", "SEVERIDADE": "CRITICO",
                "REGRA": "DF Ausente",
                "MENSAGEM_DESCRITIVA": "Balanço contábil não recebido para segmento elegível.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "DATA_DEMONSTRACAO_FINANCEIRA",
                "VALOR_OBSERVADO": "Nulo", "LIMITE_ESPERADO": "Data Preenchida"
            })

        # RAT_001 (PD Substituta)
        if status_calculo_pd == "CONCLUIDO_COM_PD_SUB":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "RAT_001", "SEVERIDADE": "ALTO",
                "REGRA": "Uso de PD Substituta (Dados Antigos)",
                "MENSAGEM_DESCRITIVA": "O Rating foi penalizado pelo acionamento de PD Substituta (DF Vencida).",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_CALCULO_PD",
                "VALOR_OBSERVADO": "CONCLUIDO_COM_PD_SUB", "LIMITE_ESPERADO": "CONCLUIDO"
            })
            
        # RAT_002 (Rating Deteriorado)
        if rating_final == "E":
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "RAT_002", "SEVERIDADE": "ALTO",
                "REGRA": "Rating Deteriorado (E)",
                "MENSAGEM_DESCRITIVA": "Contraparte atingiu rating E (Alerta de Default ou Rejeição).",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "RATING_FINAL",
                "VALOR_OBSERVADO": rating_final, "LIMITE_ESPERADO": "A, B, C, D"
            })

        # CAD_001 (Receita Federal)
        if not df_rfb.empty and "CNPJ" in df_rfb.columns:
            rfb_matches = df_rfb[df_rfb["CNPJ"] == cnpj]
            if not rfb_matches.empty:
                sit_cad = str(rfb_matches.iloc[0].get("SITUACAO_CADASTRAL", "")).upper()
                if sit_cad not in ["ATIVA", "ATIVO"]:
                    alertas.append({
                        "CNPJ": cnpj, "CODIGO_ALERTA": "CAD_001", "SEVERIDADE": "CRITICO",
                        "REGRA": "Situação Cadastral Irregular",
                        "MENSAGEM_DESCRITIVA": "Situação na Receita Federal não é ATIVA.",
                        "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_CADASTRAL",
                        "VALOR_OBSERVADO": sit_cad, "LIMITE_ESPERADO": "ATIVA"
                    })
                    
        # EXP_001 (Exposição MtM)
        if not df_mtm.empty and "CNPJ" in df_mtm.columns:
            mtm_matches = df_mtm[df_mtm["CNPJ"] == cnpj]
            if not mtm_matches.empty:
                try:
                    perc_uso = float(mtm_matches.iloc[0].get("PERCENTUAL_USO_LIMITE", 0.0))
                    if perc_uso > 100.0:
                        alertas.append({
                            "CNPJ": cnpj, "CODIGO_ALERTA": "EXP_001", "SEVERIDADE": "CRITICO",
                            "REGRA": "Estouro de Limite (MtM)",
                            "MENSAGEM_DESCRITIVA": "Uso de limite ultrapassou 100% da exposição aprovada.",
                            "DATA_DETECCAO": agora, "CAMPO_AFETADO": "PERCENTUAL_USO_LIMITE",
                            "VALOR_OBSERVADO": f"{perc_uso}%", "LIMITE_ESPERADO": "<= 100%"
                        })
                except (ValueError, TypeError): pass
                
        # CTR_001 (Anomalias Reconciliação Contratos)
        if not df_mtm.empty and "CNPJ" in df_mtm.columns:
            mtm_matches = df_mtm[df_mtm["CNPJ"] == cnpj]
            if not mtm_matches.empty:
                status_rec = str(mtm_matches.iloc[0].get("STATUS_RECONCILIACAO", "")).upper()
                if status_rec == "DIVERGENTE":
                    alertas.append({
                        "CNPJ": cnpj, "CODIGO_ALERTA": "CTR_001", "SEVERIDADE": "MEDIO",
                        "REGRA": "Divergência Contratual",
                        "MENSAGEM_DESCRITIVA": "O contrato Denodo diverge da carga MtM.",
                        "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_RECONCILIACAO",
                        "VALOR_OBSERVADO": status_rec, "LIMITE_ESPERADO": "CONVERGENTE"
                    })

        # GAR_001 (Problemas em Garantias)
        if not df_gar.empty and "CNPJ" in df_gar.columns:
            gar_matches = df_gar[df_gar["CNPJ"] == cnpj]
            for _, r_gar in gar_matches.iterrows():
                if r_gar.get("STATUS_GARANTIA") == "VENCIDA":
                    alertas.append({
                        "CNPJ": cnpj, "CODIGO_ALERTA": "GAR_001", "SEVERIDADE": "MEDIO",
                        "REGRA": "Garantia Vencida",
                        "MENSAGEM_DESCRITIVA": "Existe garantia atrelada ao CNPJ que está vencida.",
                        "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_GARANTIA",
                        "VALOR_OBSERVADO": "VENCIDA", "LIMITE_ESPERADO": "VIGENTE"
                    })

        # GRP_001 (CGRUPO sem Holding)
        tipo_com = str(row.get("TIPO_COMERCIALIZADORA", ""))
        if tipo_com == "CGRUPO" and pd.isna(row.get("HOLDING_CNPJ")):
            alertas.append({
                "CNPJ": cnpj, "CODIGO_ALERTA": "GRP_001", "SEVERIDADE": "MEDIO",
                "REGRA": "CGRUPO sem Holding",
                "MENSAGEM_DESCRITIVA": "Classificado como CGRUPO mas sem holding declarada.",
                "DATA_DETECCAO": agora, "CAMPO_AFETADO": "HOLDING_CNPJ",
                "VALOR_OBSERVADO": "Nulo", "LIMITE_ESPERADO": "CNPJ Válido"
            })

    if alertas:
        from relational.facts.fato_alerta_util import registrar_alertas_em_lote
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
                "evidencia_encerramento": str(alerta.get("EVIDENCIA_ENCERRAMENTO")) if pd.notna(alerta.get("EVIDENCIA_ENCERRAMENTO")) else None
            })
        registrar_alertas_em_lote(alertas_formatados, run_id, context)

    logger.info(f"Fato Alerta gerada com sucesso. Total de alertas: {len(alertas)}")
    
    return {
        "status": "SUCESSO",
        "total_alertas": len(alertas)
    }
