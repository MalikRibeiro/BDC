"""Motor de Taxa de Risco de Crédito.

feat(T3.4.2): Cálculo de Taxa_Risco = PE_total / Notional_total.
Trata divisão por zero gerando alerta QLT_002.
Ref: §7.1, §8.3 (QLT_002), §11.6 do Planejamento Funcional.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

LOGGER = logging.getLogger(__name__)


def calcular_taxa_risco(
    pe_total: float | None,
    notional_total: float | None,
) -> dict[str, Any]:
    """
    Cálculo da Taxa de Risco de Crédito da carteira.

    Fórmula: Taxa_Risco = PE_total / Notional_total (§7.1).

    Args:
        pe_total: Somatório da Perda Esperada em Reais.
        notional_total: Somatório do Notional (Exposição Bruta).

    Returns:
        Dict com taxa_risco, calculo_id e potenciais alertas.
    """
    calculo_id = f"TAXA_{uuid4().hex[:12]}"
    dt_calculo = datetime.now().isoformat(timespec="seconds")

    if pe_total is None or notional_total is None:
        return {
            "calculo_id": calculo_id,
            "taxa_risco": None,
            "dt_calculo": dt_calculo,
            "status": "DADOS_INSUFICIENTES",
            "alertas": []
        }

    alertas = []
    
    # Tratamento de divisão por zero / Notional inválido (§8.3 — QLT_002)
    if float(notional_total) <= 0:
        LOGGER.warning(
            "Cálculo de Taxa de Risco não executado: Notional Total inválido ou zero (%.2f).", 
            notional_total
        )
        alertas.append({
            "CODIGO": "QLT_002",
            "SEVERIDADE": "ALTO",
            "MENSAGEM": f"Divisão por zero: Notional total ({notional_total}) <= 0 durante cálculo da Taxa de Risco."
        })
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
