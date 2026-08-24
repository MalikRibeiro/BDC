"""Serviço de Gestão de Overrides e Exceções (Módulo de Governança)."""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from domain.enums import StatusAprovacao
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def processar_solicitacao_override(context: AppContext) -> dict[str, Any]:
    run_id = f"OVR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.governanca.override")

    input_dir = context.path("entradas") / "overrides" / "pendentes"
    input_dir.mkdir(parents=True, exist_ok=True)

    arquivos = list(input_dir.glob("*.csv")) + list(input_dir.glob("*.xlsx"))
    if not arquivos:
        return {"run_id": run_id, "processados": 0, "status": "SEM_DADOS"}

    campos_obrigatorios = [
        "CNPJ", "TIPO_OVERRIDE", "VALOR_ANTES", "VALOR_DEPOIS",
        "JUSTIFICATIVA", "EVIDENCIA", "SOLICITANTE", "APROVADOR", "DATA_EXPIRACAO"
    ]

    processados = []
    hoje = datetime.now()

    for arquivo in arquivos:
        try:
            if arquivo.suffix == ".csv":
                df = pd.read_csv(arquivo, sep=";", dtype=str)
            else:
                df = pd.read_excel(arquivo, dtype=str)

            registros = df.to_dict(orient="records")

            for idx, solicitacao in enumerate(registros):
                valido = True
                for campo in campos_obrigatorios:
                    if campo not in solicitacao or pd.isna(solicitacao[campo]) or str(solicitacao[campo]).strip() == "":
                        logger.warning("Campo '%s' ausente na linha %d. Rejeitado.", campo, idx)
                        valido = False
                        break
                if not valido:
                    continue

                solicitante = str(solicitacao["SOLICITANTE"]).strip().upper()
                aprovador = str(solicitacao["APROVADOR"]).strip().upper()

                if solicitante == aprovador:
                    logger.warning("Conflito de Segregação (CNPJ %s): Solicitante = Aprovador.", solicitacao['CNPJ'])
                    continue

                expiracao = pd.to_datetime(solicitacao["DATA_EXPIRACAO"], errors="coerce")
                if pd.isna(expiracao) or expiracao < hoje:
                    logger.warning("Data de expiração inválida/passada (CNPJ %s).", solicitacao['CNPJ'])
                    continue

                registro = solicitacao.copy()
                registro["STATUS"] = StatusAprovacao.APROVADO.value
                registro["DATA_APROVACAO"] = hoje.isoformat(timespec="seconds")
                registro["RUN_ID"] = run_id
                processados.append(registro)

            target_dir = context.path("entradas") / "overrides" / "processados"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.rename(target_dir / arquivo.name)
            
        except Exception as e:
            logger.error("Erro no arquivo %s: %s", arquivo.name, e)
            target_dir = context.path("entradas") / "overrides" / "rejeitados"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.rename(target_dir / arquivo.name)

    if processados:
        silver_dir = context.path("silver") / "governanca_overrides"
        escrever_conjunto_de_dados_silver(
            records=processados,
            output_dir=silver_dir,
            filename=f"solicitacao_override_{run_id}"
        )

    logger.info("Overrides processados: %d.", len(processados))
    return {"run_id": run_id, "processados": len(processados), "status": "SUCESSO"}