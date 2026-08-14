"""Segmentação metodológica da contraparte para cálculo de PD."""

from __future__ import annotations

from typing import Any

from common.strings import normalize_string
from common.types import normalize_float


def definir_segmento_metodologico(
    registro: dict[str, Any],
) -> str:
    """Define o segmento metodológico da contraparte."""
    tipo_ficha = normalize_string(
        registro.get("TIPO_FICHA"),
        upper=True,
    )
    
    if tipo_ficha == "COMERCIALIZADORA":
        tipo_comercializadora = normalize_string(
            registro.get("TIPO_COMERCIALIZADORA"),
            upper=True,
        )
        if tipo_comercializadora == "CPURA":
            return "CPURA"

        if tipo_comercializadora == "CGRUPO":
            return "CGRUPO"

        raise ValueError(
            "Comercializadora sem TIPO_COMERCIALIZADORA válido."
        )

    if tipo_ficha == "CONSUMIDOR":
        # Extrai o volume de enquadramento (em MWm)
        volume_mwm = normalize_float(registro.get("VOLUME_ENQUADRAMENTO_MWM"))
        
        # Critério de Aceite: Consumidor sem volume retorna NAO_ENQUADRADO
        if volume_mwm is None:
            return "NAO_ENQUADRADO"
            
        # Critério de Aceite: Bifurcação baseada no limite de 5 MWm
        if volume_mwm >= 5.0:
            return "CONSUMIDOR_GT_5"
        else:
            return "CONSUMIDOR_LE_5"

    raise ValueError(
        f"TIPO_FICHA inválido para segmentação: {tipo_ficha!r}"
    )