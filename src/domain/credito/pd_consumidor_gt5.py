"""Transformação da PD para consumidores acima de 5 MWm."""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

from domain.credito.pd_exceptions import (
    PdCalculationError,
    PdConfigurationError,
)


def _inv_t_approx(prob: float, df: float) -> float:
    """Aproxima o quantil da t de Student a partir do quantil normal."""
    if not 0 < prob < 1:
        raise PdCalculationError(
            f"Probabilidade inválida para inversa t: {prob!r}"
        )

    z = NormalDist().inv_cdf(prob)

    g1 = (z**3 + z) / (4 * df)
    g2 = (5 * z**5 + 16 * z**3 + 3 * z) / (96 * (df**2))
    g3 = (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * (df**3))

    return z + g1 + g2 + g3


def _normalize_pd_input(
    value: float,
    normalize_percent_if_gt_1: bool,
) -> float:
    q = float(value)
    if normalize_percent_if_gt_1 and q > 1:
        q = q / 100.0
    return q


def calcular_pd_final_consumidor_gt5(
    registro: dict[str, Any],
    pd_base: float,
    rating_final: str,
    pd_min: float,
    pd_max: float,
    regras_segmento: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada para consumidor acima de 5 MWm."""
    try:
        regras_pd = regras_segmento["pd_final_rules"]
        metodo = str(regras_pd.get("method", "")).strip().lower()

        if metodo != "t_dist_logistic":
            raise PdConfigurationError(
                f"Método inválido para CONSUMIDOR_GT_5: {metodo!r}"
            )

        df = float(regras_pd["df"])
        scale = float(regras_pd["scale"])
        eps = float(regras_pd["eps"])
        normalize_percent_if_gt_1 = bool(
            regras_pd.get("normalize_input_percent_if_gt_1", True)
        )

        q = _normalize_pd_input(
            value=float(pd_base),
            normalize_percent_if_gt_1=normalize_percent_if_gt_1,
        )

        q_cap = min(1 - eps, max(eps, q))

        z_t = _inv_t_approx(q_cap, df)
        z = scale * z_t
        u = 1.0 / (1.0 + math.exp(-z))

        pd_final = pd_min + u * (pd_max - pd_min)

        resultado = {
            "RATING_FINAL": rating_final,
            "PD_BASE": pd_base,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": pd_final,
            "PD_METODO": "T_DIST_LOGISTIC",
            "PD_Q_NORMALIZADA": q,
            "PD_Q_CAP": q_cap,
            "PD_Z_T": z_t,
            "PD_Z_ESCALADO": z,
            "PD_U_INTERPOLACAO": u,
        }

        if logger is not None:
            logger.info(
                "PD ajustada CONSUMIDOR_GT_5 calculada. "
                "CNPJ=%s RATING=%s PD_BASE=%s Q=%s Q_CAP=%s "
                "PD_MIN=%s PD_MAX=%s Z_T=%s Z=%s U=%s PD_FINAL=%s",
                registro.get("CNPJ"),
                rating_final,
                pd_base,
                q,
                q_cap,
                pd_min,
                pd_max,
                z_t,
                z,
                u,
                pd_final,
            )

        return resultado

    except Exception as exc:
        if isinstance(exc, (PdCalculationError, PdConfigurationError)):
            raise
        raise PdCalculationError(
            "Falha no cálculo da PD ajustada de CONSUMIDOR_GT_5: "
            f"{exc}"
        ) from exc
