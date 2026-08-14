"""Serviço de reconciliação entre contratos do Denodo e posições consolidadas de MtM."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from app.context import AppContext
from common.logging_utils import get_logger
from domain.enums import StatusAlerta
from storage.silver_store import write_silver_dataset


class ReconciliacaoDataError(Exception):
    """Exceção levantada quando os dados fonte para a reconciliação estão inacessíveis ou vazios."""

def executar_reconciliacao_denodo_mtm(context: AppContext) -> dict[str, Any]:
    """
    Cruza o consolidado de contratos do Denodo com posições do MtM na camada Silver por CNPJ.
    Classifica as contrapartes e dispara os alertas CTR_001 e CTR_002.
    """
    run_id = f"REC_MTM_DENODO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__reconciliacao.log"
    logger = get_logger("bdc.reconciliacao", log_file)

    try:
        logger.info("Iniciando reconciliação entre Denodo e MtM por Contraparte.")

        # 1. Carregamento das bases Silver
        silver_mtm_path = context.path("silver") / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
        silver_denodo_path = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"

        if not silver_mtm_path.exists() or not silver_denodo_path.exists():
            raise ReconciliacaoDataError("As bases Silver do Denodo ou MtM não foram encontradas para a reconciliação.")

        df_mtm = pd.read_parquet(silver_mtm_path)
        df_denodo_full = pd.read_parquet(silver_denodo_path)

        if df_mtm.empty or df_denodo_full.empty:
            logger.warning("Uma das bases Silver está vazia. Cancelando reconciliação.")
            return {"run_id": run_id, "linhas_conciliadas": 0, "status": "SEM_DADOS"}

        # 2. Padronização: Como o MtM está agregado por CNPJ, agregamos o Denodo por CNPJ
        df_denodo_full["CNPJ"] = df_denodo_full["CNPJ"].astype(str).str.zfill(14)
        df_mtm["CNPJ"] = df_mtm["CNPJ"].astype(str).str.zfill(14)

        # Para conciliação, basta saber se a contraparte tem AO MENOS UM contrato ativo
        df_denodo = df_denodo_full[["CNPJ"]].drop_duplicates()
        df_denodo["TEM_CONTRATO"] = True

        # 3. Cruzamento (Outer Join por CNPJ)
        df_merged = pd.merge(
            df_denodo, 
            df_mtm, 
            on="CNPJ", 
            how="outer", 
            indicator=True
        )

        # 4. Classificação de Reconciliação
        conditions = [
            df_merged["_merge"] == "both",
            df_merged["_merge"] == "left_only",
            df_merged["_merge"] == "right_only"
        ]
        choices = ["CONCILIADO", "CONTRATO_SEM_MTM", "MTM_SEM_CONTRATO"]
        
        df_merged["STATUS_CONCILIACAO"] = np.select(conditions, choices, default="DIVERGENTE")

        # 5. Geração de Alertas
        alertas = []
        
        # CTR_001: Contrato corrente no Denodo sem posição correspondente no MtM
        mask_ctr_001 = df_merged["STATUS_CONCILIACAO"] == "CONTRATO_SEM_MTM"
        for _, row in df_merged[mask_ctr_001].iterrows():
            alertas.append({
                "CODIGO": "CTR_001",
                "CNPJ": row["CNPJ"],
                "SEVERIDADE": "MEDIO",
                "MENSAGEM": f"A contraparte (CNPJ {row['CNPJ']}) possui contrato(s) no Denodo, mas não tem posição na base de MtM."
            })

        # CTR_002: Posição no MtM sem contrato corrente identificado no Denodo
        mask_ctr_002 = df_merged["STATUS_CONCILIACAO"] == "MTM_SEM_CONTRATO"
        for _, row in df_merged[mask_ctr_002].iterrows():
            alertas.append({
                "CODIGO": "CTR_002",
                "CNPJ": row["CNPJ"],
                "SEVERIDADE": "ALTO",
                "MENSAGEM": f"Posição de MtM identificada para a contraparte {row['CNPJ']}, mas nenhum contrato corrente consta no Denodo."
            })

        if alertas:
            df_alertas = pd.DataFrame(alertas)
            df_alertas["RUN_ID"] = run_id
            df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
            df_alertas["STATUS_ALERTA"] = StatusAlerta.ABERTO.value
            
            alertas_output_dir = context.path("silver") / "alertas_credito"
            write_silver_dataset(
                records=df_alertas.to_dict(orient="records"),
                output_dir=alertas_output_dir,
                filename=f"alertas_reconciliacao_{run_id}"
            )
            logger.info("Gerados %s alertas de negócio na reconciliação.", len(alertas))

        # 6. Organização e Persistência do resultado
        colunas_saida = [
            "CNPJ", "STATUS_CONCILIACAO", 
            "MTM_POSITIVO_TOTAL", "MTM_NEGATIVO_TOTAL", "NOTIONAL_TOTAL"
        ]
        
        colunas_disponiveis = [col for col in colunas_saida if col in df_merged.columns]
        df_reconciliacao = df_merged[colunas_disponiveis].copy()
        
        df_reconciliacao["RUN_ID"] = run_id
        df_reconciliacao["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        reconciliacao_output_dir = context.path("silver") / "reconciliacao_contratos_mtm"
        csv_path, parquet_path = write_silver_dataset(
            records=df_reconciliacao.to_dict(orient="records"),
            output_dir=reconciliacao_output_dir,
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