from __future__ import annotations

import math
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


def _texto_numerico(valor: Any) -> str | None:
    if valor is None:
        return None

    if isinstance(valor, float) and math.isnan(valor):
        return None

    texto = str(valor).strip()

    from common.nulos import is_nulo_textual
    if is_nulo_textual(texto):
        return None

    return texto

def to_decimal_br(valor: Any, *, casas_decimais: int | None = None) -> Decimal | None:
    """Converte padrão brasileiro para Decimal puro."""
    texto = _texto_numerico(valor)

    if texto is None:
        return None

    texto = texto.replace("R$", "").replace(" ", "")

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")

    elif "," in texto:
        texto = texto.replace(",", ".")

    texto = re.sub(r"[^0-9eE+\-.]", "", texto)

    try:
        numero = Decimal(texto)
    except InvalidOperation:
        return None

    if casas_decimais is not None:
        numero = numero.quantize(Decimal("1.000000"), rounding=ROUND_HALF_UP)

    return numero

def to_float_br(valor: Any) -> float | None:
    """Converte padrão brasileiro para Float puro."""
    dec = to_decimal_br(valor)
    return float(dec) if dec is not None else None

def to_int_br(valor: Any) -> int | None:
    """Converte padrão brasileiro para Int puro (apenas se não houver perda fracionária)."""
    dec = to_decimal_br(valor)
    if dec is None or dec != dec.to_integral_value():
        return None
    return int(dec)

def to_percentual_br(valor: Any, *, casas_decimais: int = 6) -> float | None:
    """Converte padrão brasileiro para percentual (divide por 100 se houver '%'). NÃO impõe limite de 0 a 1."""
    texto = _texto_numerico(valor)
    if texto is None:
        return None
    
    possui_percentual = "%" in texto
    dec = to_decimal_br(texto.replace("%", ""))
    
    if dec is None:
        return None
        
    if possui_percentual:
        dec /= Decimal("100")
        
    quantizador = Decimal("1").scaleb(-casas_decimais)
    dec = dec.quantize(quantizador, rounding=ROUND_HALF_UP)
    
    return float(dec)