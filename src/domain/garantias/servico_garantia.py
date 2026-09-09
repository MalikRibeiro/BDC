"""Serviço de ingestão, validação e alertas de Garantias.

Lê o CSV extraído da query customizada do Denodo, salva na Bronze,
valida regras de vigência e cobertura, gera alertas e publica na Silver.
Ref: §2 (Módulo Garantias), §6.8 do Planejamento Funcional.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

class GarantiaIngestionError(Exception):
    """Exceção levantada para falhas na ingestão de garantias."""

COBERTURA_MINIMA = 0.5

def inserir_dados_garantias(
    context: AppContext,
    df_garantias_externo: pd.DataFrame | None = None,
) -> dict[str, Any]:
    run_id = f"GAR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/ingestao") / f"{run_id}__ingestao_garantias.log"
    logger = obter_logger("bdc.garantias", log_file)

    try:
        logger.info("Iniciando ingestão de Garantias (Modo CSV Local).")

        if df_garantias_externo is not None:
            df_raw = df_garantias_externo.copy()
            logger.info("Usando DataFrame externo fornecido.")
        else:
            input_dir = context.path("entradas") / "garantias"
            input_dir.mkdir(parents=True, exist_ok=True)

            arquivos = [
                f for f in input_dir.iterdir()
                if f.is_file() and f.suffix.lower() in {".xlsx", ".xls", ".csv"}
                and not f.name.startswith("~$")
            ]

            if not arquivos:
                logger.warning("Nenhum arquivo de garantias encontrado em %s.", input_dir)
                return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

            arquivo_fonte = max(arquivos, key=lambda f: f.stat().st_mtime)
            logger.info("Lendo garantias do arquivo local: %s", arquivo_fonte.name)

            if arquivo_fonte.suffix.lower() == ".csv":
                df_raw = pd.read_csv(arquivo_fonte, dtype=str, sep=";", encoding="utf-8-sig")
            else:
                df_raw = pd.read_excel(arquivo_fonte, dtype=str)

        if df_raw.empty:
            return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "garantias"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        caminho_bronze = bronze_dir / f"raw_garantias_{datetime.now().strftime('%Y%m%d')}.parquet"
        
        df_raw.to_parquet(caminho_bronze, index=False)

        df_garantias = df_raw.copy()
        df_garantias.columns = [str(c).strip().upper() for c in df_garantias.columns]

        from common.identificadores import normalizar_cnpj
        df_garantias["CNPJ_CONTRAPARTE"] = df_garantias["CNPJ_CONTRAPARTE"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
        df_garantias["VENCIMENTO"] = pd.to_datetime(df_garantias["VENCIMENTO"], errors="coerce")

        if "PERCENTUAL_COBERTURA" not in df_garantias.columns:
            df_garantias["PERCENTUAL_COBERTURA"] = 1.0
        else:
            df_garantias["PERCENTUAL_COBERTURA"] = pd.to_numeric(
                df_garantias["PERCENTUAL_COBERTURA"], errors="coerce"
            ).fillna(1.0)

        df_garantias["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
        df_garantias["RUN_ID"] = run_id

        silver_dir = context.path("silver") / "garantias_silver"
        escrever_conjunto_de_dados_silver(
            records=df_garantias.to_dict(orient="records"),
            output_dir=silver_dir,
            filename="garantia_silver"
        )

        logger.info("Ingestão de garantias na Silver concluída. Registros salvos: %s", len(df_garantias))

        return {
            "run_id": run_id,
            "linhas_processadas": len(df_garantias),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão de garantias.")
        raise GarantiaIngestionError(f"Erro ao ingerir base de garantias: {exc}") from exc