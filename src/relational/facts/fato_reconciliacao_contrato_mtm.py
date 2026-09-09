"""Serviço de reconciliação entre contratos do Denodo e posições consolidadas de MtM."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from domain.enums import StatusAlerta
from relational.facts.fato_alerta_util import registrar_alerta
from storage.escrever_dados import escrever_conjunto_de_dados_silver


class ReconciliacaoDataError(Exception):
    """Exceção levantada quando os dados fonte para a reconciliação estão inacessíveis ou vazios."""

def executar_reconciliacao_denodo_mtm(context: AppContext) -> dict[str, Any]:
    """
    Cruza o consolidado de contratos do Denodo com posições do MtM na camada Silver por CNPJ.
    Classifica as contrapartes e dispara os alertas CTR_001 e CTR_002.
    """
    run_id = f"REC_MTM_DENODO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/auditoria") / f"{run_id}__reconciliacao.log"
    logger = obter_logger("bdc.reconciliacao", log_file)

    try:
        logger.info("Iniciando reconciliação entre Denodo e MtM por Contraparte.")

        silver_mtm_path = context.path("silver") / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
        silver_denodo_path = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"

        if not silver_mtm_path.exists() or not silver_denodo_path.exists():
            raise ReconciliacaoDataError("As bases Silver do Denodo ou MtM não foram encontradas para a reconciliação.")

        df_mtm = pd.read_parquet(silver_mtm_path)
        df_denodo_full = pd.read_parquet(silver_denodo_path)

        if df_mtm.empty or df_denodo_full.empty:
            logger.warning("Uma das bases Silver está vazia. Cancelando reconciliação.")
            return {"run_id": run_id, "linhas_conciliadas": 0, "status": "SEM_DADOS"}

        df_denodo_full["CNPJ"] = df_denodo_full["CNPJ"].astype(str).str.replace(r"\D", "", regex=True)
        df_denodo_full["CNPJ"] = df_denodo_full["CNPJ"].apply(lambda x: x if len(x) == 14 else None)

        df_mtm["CNPJ"] = df_mtm["CNPJ"].astype(str).str.replace(r"\D", "", regex=True)
        df_mtm["CNPJ"] = df_mtm["CNPJ"].apply(lambda x: x if len(x) == 14 else None)

        df_denodo = df_denodo_full[["CNPJ"]].drop_duplicates()
        df_denodo["TEM_CONTRATO"] = True

        df_merged = pd.merge(
            df_denodo, 
            df_mtm, 
            on="CNPJ", 
            how="outer", 
            indicator=True
        )

        conditions = [
            df_merged["_merge"] == "both",
            df_merged["_merge"] == "left_only",
            df_merged["_merge"] == "right_only"
        ]
        choices = ["CONCILIADO", "CONTRATO_SEM_MTM", "MTM_SEM_CONTRATO"]
        
        df_merged["STATUS_CONCILIACAO"] = np.select(conditions, choices, default="DIVERGENTE")

        alertas = []
        alertas_db = []
        
        mask_ctr_001 = df_merged["STATUS_CONCILIACAO"] == "CONTRATO_SEM_MTM"
        for row in df_merged[mask_ctr_001].to_dict(orient="records"):
            msg = f"A contraparte (CNPJ {row['CNPJ']}) possui contrato(s) no Denodo, mas não tem posição na base de MtM."
            alertas.append({
                "CODIGO": "CTR_001",
                "CNPJ": row["CNPJ"],
                "SEVERIDADE": "MEDIO",
                "MENSAGEM": msg
            })
            alertas_db.append({
                "codigo": "CTR_001",
                "severidade": "MEDIO",
                "regra": "Contrato sem MtM",
                "mensagem": msg,
                "campo_afetado": "STATUS_CONCILIACAO",
                "valor_observado": "CONTRATO_SEM_MTM",
                "limite_esperado": "CONCILIADO",
                "contraparte_id": row["CNPJ"]
            })

        mask_ctr_002 = df_merged["STATUS_CONCILIACAO"] == "MTM_SEM_CONTRATO"
        for row in df_merged[mask_ctr_002].to_dict(orient="records"):
            msg = f"Posição de MtM identificada para a contraparte {row['CNPJ']}, mas nenhum contrato corrente consta no Denodo."
            alertas.append({
                "CODIGO": "CTR_002",
                "CNPJ": row["CNPJ"],
                "SEVERIDADE": "ALTO",
                "MENSAGEM": msg
            })
            alertas_db.append({
                "codigo": "CTR_002",
                "severidade": "ALTO",
                "regra": "MtM sem Contrato",
                "mensagem": msg,
                "campo_afetado": "STATUS_CONCILIACAO",
                "valor_observado": "MTM_SEM_CONTRATO",
                "limite_esperado": "CONCILIADO",
                "contraparte_id": row["CNPJ"]
            })

        if alertas_db:
            from relational.facts.fato_alerta_util import registrar_alertas_em_lote
            registrar_alertas_em_lote(alertas_db, run_id, context)

        if alertas:
            df_alertas = pd.DataFrame(alertas)
            df_alertas["RUN_ID"] = run_id
            df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
            df_alertas["STATUS_ALERTA"] = StatusAlerta.ABERTO.value
            
            alertas_output_dir = context.path("silver") / "alertas_credito"
            escrever_conjunto_de_dados_silver(
                records=df_alertas.to_dict(orient="records"),
                output_dir=alertas_output_dir,
                filename=f"alertas_reconciliacao_{run_id}"
            )
            logger.info("Gerados %s alertas de negócio na reconciliação.", len(alertas))

        colunas_saida = [
            "CNPJ", "STATUS_CONCILIACAO", 
            "MTM_POSITIVO_TOTAL", "MTM_NEGATIVO_TOTAL", "NOTIONAL_TOTAL"
        ]
        
        colunas_disponiveis = [col for col in colunas_saida if col in df_merged.columns]
        df_reconciliacao = df_merged[colunas_disponiveis].copy()
        
        df_reconciliacao["RUN_ID"] = run_id
        df_reconciliacao["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        reconciliacao_output_dir = context.path("silver") / "reconciliacao_contratos_mtm"
        csv_path, parquet_path = escrever_conjunto_de_dados_silver(
            records=df_reconciliacao.to_dict(orient="records"),
            output_dir=reconciliacao_output_dir,
            filename="fato_reconciliacao_contrato_mtm"
        )
        
        relational_output_dir = context.path("relational_facts") / "reconciliacao"
        escrever_conjunto_de_dados_silver(
            records=df_reconciliacao.to_dict(orient="records"),
            output_dir=relational_output_dir,
            filename="fato_reconciliacao_contrato_mtm"
        )

        logger.info(
            "Reconciliação Denodo x MtM finalizada. %s contrapartes cruzadas. Relatórios: \n - %s\n - %s",
            len(df_reconciliacao), csv_path.name, parquet_path.name
        )

        return {
            "run_id": run_id,
            "linhas_conciliadas": len(df_reconciliacao),
            "alertas_gerados_ctr001": mask_ctr_001.sum(),
            "alertas_gerados_ctr002": mask_ctr_002.sum(),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica no serviço de reconciliação Denodo x MtM.")
        raise ReconciliacaoDataError(f"Erro ao processar reconciliação: {exc}") from exc