from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd


def normalizar_data(
    valor: Any,
    *,
    formato_saida: str = "%Y-%m-%d",
) -> str | None:
    if valor is None:
        return None

    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor.strftime(formato_saida)

    if isinstance(valor, datetime):
        return valor.date().strftime(formato_saida)

    texto = str(valor).strip()

    from common.nulos import is_nulo_textual
    if is_nulo_textual(texto):
        return None

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        convertido = pd.to_datetime(
            texto,
            dayfirst=True,
            errors="coerce",
        )

    if pd.isna(convertido):
        return None

    return convertido.date().strftime(formato_saida)

def normalizar_competencia(valor: Any) -> str | None:
    data_normalizada = normalizar_data(valor)

    if data_normalizada is None:
        return None

    return data_normalizada[:7]

import re

def normalizar_data_demonstracao_financeira(value: Any) -> tuple[str | None, str | None, bool]:
    """Normaliza DATA_DEMONSTRACAO_FINANCEIRA para dd/mm/aaaa.
    Retorna: (data_normalizada, valor_original_corrompido, flag_corrigida)
    """
    if value is None:
        return None, None, False

    if isinstance(value, datetime) and 1900 <= value.year <= 1920:
        dias = (value - datetime(1899, 12, 30)).days
        if 1950 <= dias <= 2100:
            return f"31/12/{dias}", value.strftime("%Y-%m-%d %H:%M:%S"), True

    texto = str(value).strip()
    if not texto:
        return None, None, False

    if re.fullmatch(r"\d{4}", texto):
        return f"31/12/{texto}", texto, True

    texto = texto.split()[0]

    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]

    for fmt in formatos:
        try:
            dt = datetime.strptime(texto, fmt)
            return dt.strftime("%d/%m/%Y"), None, False
        except ValueError:
            continue

    return None, None, False