"""Serviço de Carga Manual e Eventos de Negócio."""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from pathlib import Path

from app.context import AppContext
from common.validation import validate_json_schema
from common.io_json import read_json
from storage.silver_store import write_silver_dataset

def ingest_carga_manual(context: AppContext) -> dict[str, Any]:
    run_id = f"MAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.governanca.carga_manual")
    
    input_dir = context.path("entradas") / "atualizacoes_manuais" / "pendentes"
    input_dir.mkdir(parents=True, exist_ok=True)

    arquivos = list(input_dir.glob("*.csv")) + list(input_dir.glob("*.xlsx"))
    if not arquivos:
        return {"run_id": run_id, "processados": 0, "status": "SEM_DADOS"}

    schema_path = context.path("control_schemas") / "schema_carga_manual.json"
    schema = read_json(schema_path) if schema_path.exists() else None

    processados = []
    agora = datetime.now().isoformat(timespec="seconds")

    for arquivo in arquivos:
        try:
            if arquivo.suffix == ".csv":
                df = pd.read_csv(arquivo, sep=";", dtype=str)
            else:
                df = pd.read_excel(arquivo, dtype=str)

            registros = df.to_dict(orient="records")

            for idx, reg in enumerate(registros):
                if schema:
                    try:
                        validate_json_schema(reg, schema, f"Registro [{idx}] do arquivo {arquivo.name}")
                    except Exception as exc:
                        logger.warning("Registro %s inválido: %s. Ignorando.", idx, exc)
                        continue

                novo_reg = reg.copy()
                novo_reg["DATA_REGISTRO_SISTEMA"] = agora
                novo_reg["RUN_ID"] = run_id
                processados.append(novo_reg)

            # Move para aprovadas
            target_dir = context.path("entradas") / "atualizacoes_manuais" / "aprovadas"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.rename(target_dir / arquivo.name)
            
        except Exception as e:
            logger.error("Erro ao processar arquivo %s: %s", arquivo.name, e)
            target_dir = context.path("entradas") / "atualizacoes_manuais" / "rejeitadas"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.rename(target_dir / arquivo.name)

    if processados:
        silver_dir = context.path("silver") / "governanca_carga_manual"
        df_manual = pd.DataFrame(processados)
        write_silver_dataset(
            records=df_manual.to_dict(orient="records"),
            output_dir=silver_dir,
            filename=f"eventos_manuais_{run_id}"
        )

    logger.info("Carga manual concluída. %d eventos registrados.", len(processados))
    return {"run_id": run_id, "eventos_processados": len(processados), "status": "SUCESSO"}