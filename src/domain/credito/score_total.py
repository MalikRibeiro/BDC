# -*- coding: utf-8 -*-
"""Cálculo do score total de CPURA."""

from __future__ import annotations

from typing import Any

from domain.credito.pd_exceptions import PdInputValidationError


def calcular_score_total_cpura(
    score_quant_info: dict[str, Any],
    score_qual_info: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score total de CPURA."""
    try:
        score_quant = score_quant_info.get("SCORE_QUANTITATIVO")
        score_qual = score_qual_info.get("SCORE_QUALITATIVO")

        if score_quant is None:
            raise PdInputValidationError(
                "SCORE_QUANTITATIVO não informado."
            )

        if score_qual is None:
            raise PdInputValidationError(
                "SCORE_QUALITATIVO não informado."
            )

        score_total = float(score_quant) + float(score_qual)

        resultado = {
            "SCORE_TOTAL": score_total,
        }

        if logger is not None:
            logger.info(
                "Score total CPURA calculado. SCORE_TOTAL=%s",
                score_total,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score total CPURA."
            )
        raise
