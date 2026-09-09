from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from common.texto import normalizar_chave_textual


def _criar_indice_aliases(
    dicionario: Mapping[str, Sequence[str]],
) -> dict[str, str]:
    indice: dict[str, str] = {}

    for canonico, aliases in dicionario.items():
        chave_canonica = normalizar_chave_textual(canonico)

        if chave_canonica:
            indice[chave_canonica] = canonico

        for alias in aliases:
            chave_alias = normalizar_chave_textual(alias)

            if chave_alias:
                indice[chave_alias] = canonico

    return indice

def normalizar_valor_dominio(
    valor: Any,
    dicionario: Mapping[str, Sequence[str]],
    *,
    valor_desconhecido: str | None = None,
) -> str | None:
    chave = normalizar_chave_textual(valor)

    if chave is None:
        return None

    indice = _criar_indice_aliases(dicionario)

    if chave in indice:
        return indice[chave]

    candidatos: list[tuple[int, str]] = []

    for alias, canonico in indice.items():
        if len(alias) < 4:
            continue

        padrao = rf"(?<![A-Z0-9]){re.escape(alias)}(?![A-Z0-9])"

        if re.search(padrao, chave):
            candidatos.append((len(alias), canonico))

    if candidatos:
        candidatos.sort(reverse=True)
        return candidatos[0][1]

    return valor_desconhecido

def normalizar_auditor(
    valor: Any,
    dicionario: Mapping[str, Sequence[str]],
) -> str | None:
    return normalizar_valor_dominio(
        valor,
        dicionario,
        valor_desconhecido="OUTRO",
    )

def normalizar_agencia(
    valor: Any,
    dicionario: Mapping[str, Sequence[str]],
) -> str | None:
    return normalizar_valor_dominio(
        valor,
        dicionario,
        valor_desconhecido=None,
    )

def normalizar_rating(
    valor: Any,
    dicionario: Mapping[str, Sequence[str]],
) -> str | None:
    return normalizar_valor_dominio(
        valor,
        dicionario,
        valor_desconhecido=None,
    )