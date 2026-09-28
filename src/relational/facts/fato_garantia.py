"""Serviço de construção da tabela Fato Garantia (Star Schema)."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import numpy as np
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
    logger = obter_logger("bdc.fato_garantia", Path("LOGS/relational") / f"{run_id}__fato_garantia.log")
    logger.info("Iniciando construção da Fato Garantia (run_id=%s)", run_id)
    
    silver_path = context.path("silver") / "garantias_silver" / "garantia_silver.parquet"
    if not silver_path.exists():
        logger.warning("Base Silver de garantias não encontrada em %s. Abortando.", silver_path)
        return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_BASE"}

    df_garantias = pd.read_parquet(silver_path)
    
    if df_garantias.empty:
        return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

    hoje = pd.Timestamp(datetime.now().date())

    # --- Vetorização de STATUS via np.select (substitui iterrows) ---
    df_garantias["VENCIMENTO_DT"] = pd.to_datetime(df_garantias["VENCIMENTO"], errors="coerce")
    df_garantias["DIAS_P_VENCIMENTO"] = (df_garantias["VENCIMENTO_DT"] - hoje).dt.days
    df_garantias["DIAS_P_VENCIMENTO"] = df_garantias["DIAS_P_VENCIMENTO"].fillna(-1).astype(int)
    df_garantias["PERCENTUAL_COBERTURA"] = pd.to_numeric(
        df_garantias.get("PERCENTUAL_COBERTURA", pd.Series(dtype="float64")), errors="coerce"
    ).fillna(1.0)

    conditions = [
        df_garantias["DIAS_P_VENCIMENTO"] < 0,
        df_garantias["DIAS_P_VENCIMENTO"].between(0, 30),
    ]
    choices = [StatusGarantia.VENCIDA.value, StatusGarantia.PROXIMA_VENCIMENTO.value]
    df_garantias["STATUS"] = np.select(conditions, choices, default=StatusGarantia.VIGENTE.value)

    # --- Geração de alertas via máscaras (subsets tipicamente pequenos) ---
    alertas_fato = []

    # GAR_001: Vencidas (ALTO)
    for _, row in df_garantias[df_garantias["STATUS"] == StatusGarantia.VENCIDA.value].iterrows():
        data_fmt = row["VENCIMENTO_DT"].strftime('%Y-%m-%d') if pd.notnull(row["VENCIMENTO_DT"]) else "N/A"
        alertas_fato.append({
            "codigo": "GAR_001", "severidade": "ALTO",
            "regra": "Garantia Vencida",
            "mensagem": f"Garantia {row.get('GARANTIA_ID')} está vencida desde {data_fmt}.",
            "campo_afetado": "VENCIMENTO", "valor_observado": data_fmt,
            "limite_esperado": "VIGENTE", "contraparte_id": row.get("CNPJ_CONTRAPARTE")
        })

    # GAR_001: Próximas do vencimento (MEDIO)
    for _, row in df_garantias[df_garantias["STATUS"] == StatusGarantia.PROXIMA_VENCIMENTO.value].iterrows():
        alertas_fato.append({
            "codigo": "GAR_001", "severidade": "MEDIO",
            "regra": "Garantia Próxima ao Vencimento",
            "mensagem": f"Garantia {row.get('GARANTIA_ID')} próxima do vencimento ({row['DIAS_P_VENCIMENTO']} dias).",
            "campo_afetado": "VENCIMENTO", "valor_observado": row["DIAS_P_VENCIMENTO"],
            "limite_esperado": "> 30 dias", "contraparte_id": row.get("CNPJ_CONTRAPARTE")
        })

    # GAR_002: Cobertura insuficiente
    for _, row in df_garantias[df_garantias["PERCENTUAL_COBERTURA"] < COBERTURA_MINIMA].iterrows():
        alertas_fato.append({
            "codigo": "GAR_002", "severidade": "MEDIO",
            "regra": "Cobertura Insuficiente",
            "mensagem": f"Garantia {row.get('GARANTIA_ID')} com cobertura insuficiente ({row['PERCENTUAL_COBERTURA']*100:.1f}%).",
            "campo_afetado": "PERCENTUAL_COBERTURA", "valor_observado": row["PERCENTUAL_COBERTURA"],
            "limite_esperado": COBERTURA_MINIMA, "contraparte_id": row.get("CNPJ_CONTRAPARTE")
        })

    # Gravação apenas via Fato Alerta (fonte da verdade) — removida a dupla Silver
    if alertas_fato:
        registrar_alertas_em_lote(alertas_fato, run_id, context)
        logger.info("Registrados %s alertas de garantias no Fato Alertas.", len(alertas_fato))

    # --- Persistência da Fato Garantia ---
    df_garantias["VENCIMENTO"] = df_garantias["VENCIMENTO_DT"].dt.strftime("%Y-%m-%d")
    df_garantias["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
    df_garantias["RUN_ID"] = run_id
    # Limpa colunas auxiliares de cálculo
    df_garantias = df_garantias.drop(columns=["VENCIMENTO_DT", "DIAS_P_VENCIMENTO"], errors="ignore")

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
        "alertas_gerados": len(alertas_fato),
        "status": "SUCESSO"
    }
