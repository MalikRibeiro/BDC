from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any
from uuid import uuid4
from relational.facts.fato_alerta_util import registrar_alerta


def _is_missing(val) -> bool:
    """Retorna True se val for None ou NaN."""
    if val is None:
        return True
    try:
        return math.isnan(float(val))
    except (TypeError, ValueError):
        return False

LOGGER = logging.getLogger(__name__)


def calcular_taxa_risco(
    pe_total: float | None,
    notional_total: float | None,
    run_id: str | None = None,
    context: Any | None = None
) -> dict[str, Any]:
    calculo_id = f"TAXA_{uuid4().hex[:12]}"
    dt_calculo = datetime.now().isoformat(timespec="seconds")

    if _is_missing(pe_total) or _is_missing(notional_total):
        return {
            "calculo_id": calculo_id,
            "taxa_risco": None,
            "dt_calculo": dt_calculo,
            "status": "DADOS_INSUFICIENTES",
            "alertas": []
        }

    alertas = []
    
    if _is_missing(notional_total) or float(notional_total) <= 0:
        LOGGER.warning(
            "Cálculo de Taxa de Risco não executado: Notional Total inválido ou zero (%.2f).", 
            notional_total
        )
        msg = f"Divisão por zero: Notional total ({notional_total}) <= 0 durante cálculo da Taxa de Risco."
        alertas.append({
            "CODIGO": "QLT_002",
            "SEVERIDADE": "ALTO",
            "MENSAGEM": msg
        })
        
        if run_id and context:
            registrar_alerta(
                codigo="QLT_002",
                severidade="ALTO",
                regra="Notional Total Zerado",
                mensagem=msg,
                campo_afetado="NOTIONAL_TOTAL",
                valor_observado=notional_total,
                limite_esperado="> 0",
                contraparte_id="N/A (Carteira)",
                run_id=run_id,
                context=context
            )
        return {
            "calculo_id": calculo_id,
            "taxa_risco": None,
            "pe_total_input": float(pe_total),
            "notional_total_input": float(notional_total),
            "dt_calculo": dt_calculo,
            "status": "ERRO_MATEMATICO",
            "alertas": alertas
        }

    taxa_risco = float(pe_total) / float(notional_total)

    return {
        "calculo_id": calculo_id,
        "taxa_risco": taxa_risco,
        "pe_total_input": float(pe_total),
        "notional_total_input": float(notional_total),
        "dt_calculo": dt_calculo,
        "status": "CALCULADO",
        "alertas": alertas
    }
