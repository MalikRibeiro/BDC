"""Transformação da PD para consumidores abaixo de 5 MWm (Bureau)."""

from __future__ import annotations
from typing import Any

from common.numeros import to_float_br
from domain.credito.pd_exceptions import PdCalculationError, PdInputValidationError

def calcular_pd_final_consumidor_le5(
    registro: dict[str, Any],
    pd_faixas: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula PD via score de bureau e restritivos (Sem DFs)."""
    try:
        score = to_float_br(registro.get("SCORE_BUREAU"))
        
        _r = to_float_br(registro.get("QUANTIDADE_RESTRITIVOS"))
        restritivos = _r if _r is not None else 0.0

        if score is None:
            raise PdInputValidationError("SCORE_BUREAU não informado para consumidor < 5 MWm.")

        if score >= 800:
            rating = "A"
        elif score >= 600:
            rating = "B"
        elif score >= 400:
            rating = "C"
        elif score >= 200:
            rating = "D"
        else:
            rating = "E"

        if restritivos > 0:
            rating = "E"

        faixas = pd_faixas.get("CONSUMIDOR_LE_5", {})
        if rating not in faixas:
            raise PdCalculationError(f"Faixa de PD não encontrada para o rating {rating}.")

        pd_min = float(faixas[rating]["min"])
        pd_max = float(faixas[rating]["max"])

        limites = {"A": (800, 1000), "B": (600, 800), "C": (400, 600), "D": (200, 400), "E": (0, 200)}
        s_min, s_max = limites[rating]

        score_truncado = max(s_min, min(score, s_max))
        fator = 0.5 if s_max == s_min else 1.0 - ((score_truncado - s_min) / (s_max - s_min))
        pd_final = pd_min + (fator * (pd_max - pd_min))

        resultado = {
            "RATING_FINAL": rating,
            "PD_FINAL": pd_final,
            "PD_METODO": "SCORE_BUREAU",
            "SCORE_BUREAU_UTILIZADO": score,
            "QUANTIDADE_RESTRITIVOS": restritivos,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            "PATRIMONIO_LIQUIDO": "NAO_APLICAVEL",
            "LUCRO_LIQUIDO": "NAO_APLICAVEL",
            "ATIVO_TOTAL": "NAO_APLICAVEL",
            "PASSIVO_CIRCULANTE": "NAO_APLICAVEL"
        }

        if logger:
            logger.info("PD LE_5 calculada. CNPJ=%s SCORE=%s RATING=%s PD=%s", registro.get("CNPJ"), score, rating, pd_final)

        return resultado

    except Exception as exc:
        if logger: logger.exception("Falha no cálculo LE_5.")
        raise PdCalculationError(f"Falha LE_5: {exc}") from exc