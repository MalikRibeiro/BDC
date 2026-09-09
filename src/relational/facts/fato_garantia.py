"""Serviço de construção da tabela Fato Garantia (Star Schema)."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from pathlib import Path

from app.context import AppContext
from control.logger import obter_logger
from domain.enums import StatusGarantia
from relational.facts.fato_alerta_util import registrar_alertas_em_lote
from storage.escrever_dados import escrever_conjunto_de_dados_silver

COBERTURA_MINIMA = 0.5

def gerar_fato_garantia(context: AppContext) -> dict[str, Any]:
    run_id = f"F_GAR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.fato_garantia", Path("LOGS/relacional") / f"{run_id}__fato_garantia.log")
    logger.info("Iniciando construção da Fato Garantia (run_id=%s)", run_id)
    
    silver_path = context.path("silver") / "garantias_silver" / "garantia_silver.parquet"
    if not silver_path.exists():
        logger.warning("Base Silver de garantias não encontrada em %s. Abortando.", silver_path)
        return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_BASE"}

    df_garantias = pd.read_parquet(silver_path)
    
    if df_garantias.empty:
        return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

    hoje = pd.Timestamp(datetime.now().date())
    alertas = []
    alertas_fato = []
    status_list = []

    for _, row in df_garantias.iterrows():
        garantia_id = row.get("GARANTIA_ID")
        cnpj = row.get("CNPJ_CONTRAPARTE")
        data_fim = pd.to_datetime(row.get("VENCIMENTO"), errors="coerce")
        cobertura = float(row.get("PERCENTUAL_COBERTURA", 1.0))

        dias_para_vencimento = (data_fim - hoje).days if pd.notnull(data_fim) else -1

        if dias_para_vencimento < 0:
            status_garantia = StatusGarantia.VENCIDA.value
            data_fmt = data_fim.strftime('%Y-%m-%d') if pd.notnull(data_fim) else "N/A"
            msg = f"Garantia {garantia_id} está vencida desde {data_fmt}."
            alertas.append({
                "CODIGO": "GAR_001",
                "CNPJ": cnpj,
                "SEVERIDADE": "ALTO",
                "MENSAGEM": msg
            })
            alertas_fato.append({
                "codigo": "GAR_001",
                "severidade": "ALTO",
                "regra": "Garantia Vencida",
                "mensagem": msg,
                "campo_afetado": "VENCIMENTO",
                "valor_observado": data_fmt,
                "limite_esperado": "VIGENTE",
                "contraparte_id": cnpj
            })
        elif 0 <= dias_para_vencimento <= 30:
            status_garantia = StatusGarantia.PROXIMA_VENCIMENTO.value
            msg = f"Garantia {garantia_id} próxima do vencimento ({dias_para_vencimento} dias)."
            alertas.append({
                "CODIGO": "GAR_001",
                "CNPJ": cnpj,
                "SEVERIDADE": "MEDIO",
                "MENSAGEM": msg
            })
            alertas_fato.append({
                "codigo": "GAR_001",
                "severidade": "MEDIO",
                "regra": "Garantia Próxima ao Vencimento",
                "mensagem": msg,
                "campo_afetado": "VENCIMENTO",
                "valor_observado": dias_para_vencimento,
                "limite_esperado": "> 30 dias",
                "contraparte_id": cnpj
            })
        else:
            status_garantia = StatusGarantia.VIGENTE.value

        if cobertura < COBERTURA_MINIMA:
            msg = f"Garantia {garantia_id} com cobertura insuficiente ({cobertura*100:.1f}%)."
            alertas.append({
                "CODIGO": "GAR_002",
                "CNPJ": cnpj,
                "SEVERIDADE": "MEDIO",
                "MENSAGEM": msg
            })
            alertas_fato.append({
                "codigo": "GAR_002",
                "severidade": "MEDIO",
                "regra": "Cobertura Insuficiente",
                "mensagem": msg,
                "campo_afetado": "PERCENTUAL_COBERTURA",
                "valor_observado": cobertura,
                "limite_esperado": COBERTURA_MINIMA,
                "contraparte_id": cnpj
            })

        status_list.append(status_garantia)

    df_garantias["STATUS"] = status_list
    df_garantias["VENCIMENTO"] = pd.to_datetime(df_garantias["VENCIMENTO"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_garantias["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
    df_garantias["RUN_ID"] = run_id

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        df_alertas["RUN_ID"] = run_id
        df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
        df_alertas["STATUS_ALERTA"] = "ABERTO"

        escrever_conjunto_de_dados_silver(
            records=df_alertas.to_dict(orient="records"),
            output_dir=context.path("silver") / "alertas_credito",
            filename=f"alertas_garantias_{run_id}"
        )
        logger.info("Gerados %s alertas de garantias na Silver.", len(alertas))
        
        if alertas_fato:
            registrar_alertas_em_lote(alertas_fato, run_id, context)
            logger.info("Registrados %s alertas de garantias no Fato Alertas.", len(alertas_fato))

    relational_dir = context.path("relational_facts") / "garantias"
    relational_dir.mkdir(parents=True, exist_ok=True)
    
    escrever_conjunto_de_dados_silver(
        records=df_garantias.to_dict(orient="records"),
        output_dir=relational_dir,
        filename=f"fato_garantia_{run_id}"
    )
    escrever_conjunto_de_dados_silver(
        records=df_garantias.to_dict(orient="records"),
        output_dir=relational_dir,
        filename="fato_garantia"
    )

    logger.info("Construção da Fato Garantia concluída. Registros salvos: %s", len(df_garantias))

    return {
        "run_id": run_id,
        "linhas_processadas": len(df_garantias),
        "alertas_gerados": len(alertas),
        "status": "SUCESSO"
    }
