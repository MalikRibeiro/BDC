"""Cálculo ou leitura da PD base."""

from __future__ import annotations

from typing import Any

from common.numeros import to_float_br
from domain.credito.pd_exceptions import PdInputValidationError


def calcular_pd_base(
    registro: dict[str, Any],
    segmento_pd: str,
    pd_zscore_config: dict[str, Any] | None = None,
    logger: Any | None = None,
) -> float | None:
    """Calcula a PD base via regressão logística (Z-Score) ou lê o input direto."""
    # Para públicos que não possuem PD contábil ou já recebem via fallback (ou Risk3)
    if segmento_pd in {"CONSUMIDOR_LE_5", "CONSUMIDOR_LT_5", "CGRUPO"}:
        return None

    if segmento_pd in {"CONSUMIDOR_GT_5", "CONSUMIDOR_GE_5"}:
        raw_pd = registro.get("PROBABILIDADE_DEFAULT")
        return to_float_br(raw_pd) if raw_pd is not None else None

    try:
        if not pd_zscore_config:
            raw_pd = registro.get("PROBABILIDADE_DEFAULT")
            if raw_pd is not None:
                return to_float_br(raw_pd)
            raise PdInputValidationError("Falta pd_zscore_config para cálculo da PD base.")

        la = to_float_br(registro.get("LUCROS_ACUMULADOS")) or 0.0
        rl = to_float_br(registro.get("RESERVA_DE_LUCROS")) or 0.0
        at = to_float_br(registro.get("ATIVO_TOTAL"))
        
        pcf = to_float_br(registro.get("PASSIVO_CIRCULANTE_FINANCEIRO")) or 0.0
        pncf = to_float_br(registro.get("PASSIVO_NAO_CIRCULANTE_FINANCEIRO")) or 0.0

        ac = to_float_br(registro.get("ATIVO_CIRCULANTE")) or 0.0
        pc = to_float_br(registro.get("PASSIVO_CIRCULANTE")) or 0.0

        acf = to_float_br(registro.get("ATIVO_CIRCULANTE_FINANCEIRO")) or 0.0
        vl = to_float_br(registro.get("VENDAS_LIQUIDAS"))

        if at is None or at <= 0.0:
            raise PdInputValidationError("ATIVO_TOTAL nulo ou zero (impossível calcular X12, X16, X19).")
        if vl is None or vl <= 0.0:
            raise PdInputValidationError("VENDAS_LIQUIDAS nulo ou zero (impossível calcular X22).")

        x12 = (la + rl) / at
        x16 = (pcf + pncf) / at
        x19 = (ac - pc) / at
        x22 = (acf - pcf) / vl

        try:
            intercept = pd_zscore_config["intercept"]
            coef_x12 = pd_zscore_config["coef_x12"]
            coef_x16 = pd_zscore_config["coef_x16"]
            coef_x19 = pd_zscore_config["coef_x19"]
            coef_x22 = pd_zscore_config["coef_x22"]
        except KeyError as k:
            raise PdInputValidationError(f"Falta parâmetro obrigatório no pd_zscore_config: {str(k)}")

        import math
        z = intercept + (coef_x12 * x12) + (coef_x16 * x16) + (coef_x19 * x19) + (coef_x22 * x22)
        
        z_clamped = max(-20.0, min(z, 20.0))
        # Fórmula exata da Nota Técnica v7 §4: PD = 1 / (1 + exp(-z))
        pd_base = 1.0 / (1.0 + math.exp(-z_clamped))

        if pd_base < 0.0 or pd_base > 1.0:
            raise PdInputValidationError(f"PD base fora do intervalo após cálculo logístico: {pd_base}")

        return pd_base

    except Exception as e:
        if logger is not None:
            logger.warning("Falha tratada no cálculo do Z-Score para CNPJ=%s: %s", registro.get("CNPJ"), str(e))
        return None

