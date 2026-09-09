"""Segmentação metodológica da contraparte para cálculo de PD."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from common.numeros import to_float_br

def definir_segmento_metodologico(
    registro: dict[str, Any],
) -> str:
    """Define o segmento metodológico da contraparte."""
    tipo_ficha = normalizar_texto(registro.get("TIPO_FICHA"))
    
    if tipo_ficha == "COMERCIALIZADORA":
        tipo_comercializadora = normalizar_texto(registro.get("TIPO_COMERCIALIZADORA"))
        if tipo_comercializadora == "CPURA":
            return "CPURA"

        if tipo_comercializadora == "CGRUPO":
            return "CGRUPO"

        raise ValueError(
            "Comercializadora sem TIPO_COMERCIALIZADORA válido."
        )

    if tipo_ficha == "CONSUMIDOR":
        volume_mwm = to_float_br(registro.get("VOLUME_ENQUADRAMENTO_MWM"))
        
        if volume_mwm is None:
            return "NAO_ENQUADRADO"
            
        if volume_mwm >= 5.0:
            return "CONSUMIDOR_GT_5"
        else:
            return "CONSUMIDOR_LE_5"

    raise ValueError(
        f"TIPO_FICHA inválido para segmentação: {tipo_ficha!r}"
    )