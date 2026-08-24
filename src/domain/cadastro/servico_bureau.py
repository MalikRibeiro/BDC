"""Serviço de Ingestão e Persistência do Bureau RISK3."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from services.connectors.risk3_connector import buscar_bureau_risk3
from storage.escrever_dados import escrever_conjunto_de_dados_silver

LOGGER = logging.getLogger(__name__)

def inserir_dados_bureau(context: AppContext) -> dict[str, Any]:
    run_id = f"BUR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.bureau")

    try:
        # 1. Busca Consumidores enquadrados no motor de volume
        path_enq = context.path("relational_configs")
        arquivos = list(path_enq.glob("enquadramento_consumidores_*.parquet"))
        if not arquivos:
            logger.warning("Nenhum enquadramento encontrado para guiar o Bureau.")
            return {"run_id": run_id, "status": "SEM_DADOS_ENQUADRAMENTO"}
            
        df_enq = pd.read_parquet(max(arquivos, key=lambda f: f.stat().st_mtime))
        
        # 2. Filtra os clientes que exigem Bureau (< 5 MWm)
        df_le5 = df_enq[df_enq["POSSUI_PELO_MENOS_5_MWM"] == False]
        cnpjs_alvo = df_le5["CNPJ"].dropna().unique().tolist()
        
        if not cnpjs_alvo:
            return {"run_id": run_id, "status": "NENHUM_CLIENTE_ELEGIVEL"}

        # 3. Consulta a API RISK3
        df_bureau = buscar_bureau_risk3(cnpjs_alvo, context)

        if df_bureau.empty:
            return {"run_id": run_id, "status": "SEM_RETORNO_API"}

        # 4. Salva Snapshot na Bronze
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "bureau"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        df_bureau.to_parquet(bronze_dir / f"raw_bureau_{run_id}.parquet", index=False)

        # 5. Salva Fato na Silver (Para consumo pela Camada Gold)
        df_silver = df_bureau[df_bureau["STATUS"] == "SUCESSO"].copy()
        
        if df_silver.empty:
            return {"run_id": run_id, "status": "FALHA_OU_BLOQUEIO_DE_REDE"}
            
        df_silver["RUN_ID"] = run_id
        df_silver["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
        
        silver_dir = context.path("silver") / "fato_bureau_silver"
        escrever_conjunto_de_dados_silver(
            records=df_silver.to_dict(orient="records"), 
            output_dir=silver_dir, 
            filename="fato_bureau_silver"
        )

        logger.info("Ingestão do Bureau concluída. %d registros na Silver.", len(df_silver))
        return {"run_id": run_id, "status": "SUCESSO", "linhas": len(df_silver)}

    except Exception as e:
        logger.exception("Falha crítica na ingestão do Bureau RISK3.")
        raise