"""Normalização de textos e documentos no sistema BDC."""

from __future__ import annotations

import re
from typing import Any


def normalize_string(value: Any, upper: bool = False) -> str | None:
    """Normaliza um valor textual."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    return text.upper() if upper else text


def normalize_cnpj(value: Any) -> str | None:
    """Normaliza um CNPJ para 14 dígitos numéricos."""
    if value is None:
        return None

    digits = re.sub(r"\D", "", str(value))

    if not digits:
        return None

    return digits.zfill(14)
