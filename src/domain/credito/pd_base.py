"""Cálculo ou leitura da PD base."""

from __future__ import annotations

from typing import Any

from silver.normalizadores import normalizar_float
from domain.credito.pd_exceptions import PdInputValidationError


def calcular_pd_base(
    registro: dict[str, Any],
    segmento_pd: str,
) -> float:
    """Calcula ou lê a PD base do registro."""
    valor = registro.get("PROBABILIDADE_DEFAULT")
    pd_base = normalizar_float(valor)
    
    if segmento_pd == "CONSUMIDOR_LE_5":
        # Para consumidores abaixo de 5 MWm, a PD base não é utilizada
        return 0.0
    
    valor = registro.get("PROBABILIDADE_DEFAULT")

    if pd_base is None:
        raise PdInputValidationError(
            f"Registro sem PROBABILIDADE_DEFAULT para {segmento_pd}."
        )

    if pd_base < 0:
        raise PdInputValidationError(
            f"PD base negativa: {pd_base}"
        )

    if pd_base > 1:
        pd_base = pd_base / 100.0

    if pd_base > 1:
        raise PdInputValidationError(
            f"PD base fora do intervalo após normalização: {pd_base}"
        )

    return pd_base
