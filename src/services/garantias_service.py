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
from common.logging_utils import get_logger
from domain.enums import StatusGarantia
from storage.silver_store import write_silver_dataset

class GarantiaIngestionError(Exception):
    """Exceção levantada para falhas na ingestão de garantias."""

# Limiar mínimo de cobertura para disparo de alerta GAR_002 (§6.8)
COBERTURA_MINIMA = 0.5

def ingest_garantias_data(
    context: AppContext,
    df_garantias_externo: pd.DataFrame | None = None,
) -> dict[str, Any]:
    run_id = f"GAR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__ingestao_garantias.log"
    logger = get_logger("bdc.garantias", log_file)

    try:
        logger.info("Iniciando ingestão de Garantias (Modo CSV Local).")

        # --- Obtenção dos dados ---
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

        # 1. Snapshot na Bronze (Imutabilidade — §11.5)
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "garantias"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        caminho_bronze = bronze_dir / f"raw_garantias_{datetime.now().strftime('%Y%m%d')}.parquet"
        
        # Salva o Parquet cru na Bronze
        df_raw.to_parquet(caminho_bronze, index=False)

        # Padroniza as colunas em maiúsculo (pois o CSV veio em minúsculo da query)
        df_garantias = df_raw.copy()
        df_garantias.columns = [str(c).strip().upper() for c in df_garantias.columns]

        # Limpa CNPJ, converte Datas e Valores Numéricos
        df_garantias["CNPJ_CONTRAPARTE"] = (
            df_garantias["CNPJ_CONTRAPARTE"]
            .astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
        )
        # O CSV usa VENCIMENTO, não VIGENCIA_FIM
        df_garantias["VENCIMENTO"] = pd.to_datetime(df_garantias["VENCIMENTO"], errors="coerce")

        if "PERCENTUAL_COBERTURA" not in df_garantias.columns:
            df_garantias["PERCENTUAL_COBERTURA"] = 1.0
        else:
            df_garantias["PERCENTUAL_COBERTURA"] = pd.to_numeric(
                df_garantias["PERCENTUAL_COBERTURA"], errors="coerce"
            ).fillna(1.0)

        hoje = pd.Timestamp(datetime.now().date())
        alertas = []
        status_list = []

        # 2. Validação de Regras de Negócio e Geração de Alertas
        for _, row in df_garantias.iterrows():
            garantia_id = row.get("GARANTIA_ID")
            cnpj = row.get("CNPJ_CONTRAPARTE")
            data_fim = row.get("VENCIMENTO")
            cobertura = float(row.get("PERCENTUAL_COBERTURA", 1.0))

            # Regra: GAR_001 (Vencida ou Próxima do Vencimento — §6.8)
            dias_para_vencimento = (data_fim - hoje).days if pd.notnull(data_fim) else -1

            if dias_para_vencimento < 0:
                status_garantia = StatusGarantia.VENCIDA.value
                data_fmt = data_fim.strftime('%Y-%m-%d') if pd.notnull(data_fim) else "N/A"
                alertas.append({
                    "CODIGO": "GAR_001",
                    "CNPJ": cnpj,
                    "SEVERIDADE": "ALTO",
                    "MENSAGEM": f"Garantia {garantia_id} está vencida desde {data_fmt}."
                })
            elif 0 <= dias_para_vencimento <= 30:
                status_garantia = StatusGarantia.PROXIMA_VENCIMENTO.value
                alertas.append({
                    "CODIGO": "GAR_001",
                    "CNPJ": cnpj,
                    "SEVERIDADE": "MEDIO",
                    "MENSAGEM": f"Garantia {garantia_id} próxima do vencimento ({dias_para_vencimento} dias)."
                })
            else:
                status_garantia = StatusGarantia.VIGENTE.value

            # Regra: GAR_002 (Cobertura abaixo do mínimo — §6.8)
            if cobertura < COBERTURA_MINIMA:
                alertas.append({
                    "CODIGO": "GAR_002",
                    "CNPJ": cnpj,
                    "SEVERIDADE": "MEDIO",
                    "MENSAGEM": f"Garantia {garantia_id} com cobertura insuficiente ({cobertura*100:.1f}%)."
                })

            status_list.append(status_garantia)

        # Sobrescrevemos o status da query SQL caso o Python perceba que venceu hoje
        df_garantias["STATUS"] = status_list
        df_garantias["VENCIMENTO"] = df_garantias["VENCIMENTO"].dt.strftime("%Y-%m-%d")
        df_garantias["RUN_ID"] = run_id
        df_garantias["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        # 3. Gravação de Alertas e Fatos
        if alertas:
            df_alertas = pd.DataFrame(alertas)
            df_alertas["RUN_ID"] = run_id
            df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
            df_alertas["STATUS_ALERTA"] = "ABERTO"

            write_silver_dataset(
                records=df_alertas.to_dict(orient="records"),
                output_dir=context.path("silver") / "alertas_credito",
                filename=f"alertas_garantias_{run_id}"
            )
            logger.info("Gerados %s alertas de garantias (GAR_001 / GAR_002).", len(alertas))

        silver_dir = context.path("silver") / "garantias_silver"
        write_silver_dataset(
            records=df_garantias.to_dict(orient="records"),
            output_dir=silver_dir,
            filename="fato_garantia"
        )

        logger.info("Ingestão de garantias concluída. Registros salvos: %s", len(df_garantias))

        return {
            "run_id": run_id,
            "linhas_processadas": len(df_garantias),
            "alertas_gerados": len(alertas),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão de garantias.")
        raise GarantiaIngestionError(f"Erro ao ingerir base de garantias: {exc}") from exc