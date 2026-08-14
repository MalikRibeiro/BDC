"""Motor de Perda Esperada (PE).

feat(T3.4.1): Retorno dual (pe_reais + pe_percentual) e rastreabilidade
com calculo_id.
Ref: §6.7, §11.2, §11.6 (Reconciliação PE) do Planejamento Funcional.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4


def calcular_perda_esperada(
    ead: float | None,
    lgd_liquida: float | None,
    pd_final: float | None,
    notional: float | None = None,
) -> dict[str, object]:
    """
    Cálculo da Perda Esperada.

    Fórmula: PE = EAD × LGD × PD (§6.7).

    Args:
        ead: Exposure at Default em R$.
        lgd_liquida: Loss Given Default líquida [0, 1].
        pd_final: Probability of Default [0, 1].
        notional: Notional total para cálculo do percentual (PE / Notional).

    Returns:
        Dict com pe_reais, pe_percentual, calculo_id e metadados.
    """
    calculo_id = f"PE_{uuid4().hex[:12]}"
    dt_calculo = datetime.now().isoformat(timespec="seconds")

    if ead is None or lgd_liquida is None or pd_final is None:
        return {
            "calculo_id": calculo_id,
            "pe_reais": None,
            "pe_percentual": None,
            "dt_calculo": dt_calculo,
            "status": "DADOS_INSUFICIENTES",
        }

    pe_reais = float(ead) * float(lgd_liquida) * float(pd_final)

    # PE percentual = PE / Notional (§11.6 — reconciliação)
    pe_percentual = None
    if notional is not None and float(notional) > 0:
        pe_percentual = pe_reais / float(notional)

    return {
        "calculo_id": calculo_id,
        "pe_reais": pe_reais,
        "pe_percentual": pe_percentual,
        "ead_input": float(ead),
        "lgd_input": float(lgd_liquida),
        "pd_input": float(pd_final),
        "notional_input": float(notional) if notional is not None else None,
        "dt_calculo": dt_calculo,
        "status": "CALCULADO",
    }