from __future__ import annotations

import re
import unicodedata
from typing import Any


_VALORES_NULOS_TEXTUAIS = {
    "",
    "NAN",
    "NONE",
    "NULL",
    "N/A",
    "NA",
    "-",
    "--",
}


def texto_ou_none(valor: Any) -> str | None:
    """
    Converte um valor em texto, preservando nulos como None.
    """
    if valor is None:
        return None

    texto = str(valor).strip()

    if texto.upper() in _VALORES_NULOS_TEXTUAIS:
        return None

    return texto


def remover_acentos(valor: Any) -> str | None:
    """
    Remove acentos sem aplicar outras regras de normalização.
    """
    texto = texto_ou_none(valor)

    if texto is None:
        return None

    normalizado = unicodedata.normalize("NFKD", texto)

    return "".join(
        caractere
        for caractere in normalizado
        if not unicodedata.combining(caractere)
    )


def normalizar_texto(
    valor: Any,
    *,
    caixa_alta: bool = True,
    remover_acentuacao: bool = False,
) -> str | None:
    """
    Normaliza espaços e, opcionalmente, caixa e acentuação.
    """
    texto = texto_ou_none(valor)

    if texto is None:
        return None

    texto = re.sub(r"\s+", " ", texto).strip()

    if remover_acentuacao:
        texto = remover_acentos(texto)

    if texto is None:
        return None

    return texto.upper() if caixa_alta else texto


def normalizar_chave_textual(valor: Any) -> str | None:
    """
    Gera uma chave textual para comparações de domínio.

    Exemplo:
        "Deloitte Touche & Tohmatsu Ltda."
        -> "DELOITTE TOUCHE E TOHMATSU LTDA"
    """
    texto = normalizar_texto(
        valor,
        caixa_alta=True,
        remover_acentuacao=True,
    )

    if texto is None:
        return None

    texto = texto.replace("&", " E ")
    texto = re.sub(r"[^A-Z0-9]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto or None