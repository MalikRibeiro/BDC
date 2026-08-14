"""Normalização de datas no sistema BDC."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def normalize_date(value: Any) -> str | None:
    """Normaliza uma data para o formato ISO ``YYYY-MM-DD``."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    text = str(value).strip()
    if not text:
        return None

    patterns = (
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d.%m.%Y",
    )

    for pattern in patterns:
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue

    return None
