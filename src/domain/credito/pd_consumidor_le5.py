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
    """Calcula PD via fórmula direta da Risk3 (Sem DFs, sem Rating Copel)."""
    try:
        import math
        score = to_float_br(registro.get("SCORE_BUREAU"))
        
        _alerta = registro.get("FATOR_ALERTA") or registro.get("FATOR_DE_ALERTA")
        alerta = to_float_br(_alerta) if _alerta is not None else 0.0

        if score is None:
            raise PdInputValidationError("SCORE_BUREAU não informado para consumidor <= 5 MWm.")

        # Fórmula Risk3: min{1,9·exp[-0,5·(0,11·Score - Alerta/3 + 1)], 0,9999}
        expoente = -0.5 * (0.11 * score - (alerta / 3.0) + 1.0)
        # Evitar overflow no math.exp
        expoente_clamped = max(-500.0, min(expoente, 500.0))
        pd_risk3 = 1.9 * math.exp(expoente_clamped)
        
        pd_final = min(pd_risk3, 0.9999)

        resultado = {
            "RATING_FINAL": "NAO_APLICAVEL",
            "PD_FINAL": pd_final,
            "PD_METODO": "FORMULA_RISK3",
            "SCORE_BUREAU_UTILIZADO": score,
            "FATOR_ALERTA_UTILIZADO": alerta,
            "PD_MIN_FAIXA": pd_final,
            "PD_MAX_FAIXA": pd_final,
            "PATRIMONIO_LIQUIDO": "NAO_APLICAVEL",
            "LUCRO_LIQUIDO": "NAO_APLICAVEL",
            "ATIVO_TOTAL": "NAO_APLICAVEL",
            "PASSIVO_CIRCULANTE": "NAO_APLICAVEL"
        }

        if logger:
            logger.info("PD LE_5 calculada (Risk3). CNPJ=%s SCORE=%s ALERTA=%s PD=%s", registro.get("CNPJ"), score, alerta, pd_final)

        return resultado

    except Exception as exc:
        if logger: logger.exception("Falha no cálculo LE_5.")
        raise PdCalculationError(f"Falha LE_5: {exc}") from exc