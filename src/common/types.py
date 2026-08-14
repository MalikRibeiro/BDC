"""Conversões tipadas para valores numéricos do sistema BDC."""

from __future__ import annotations

from typing import Any


def normalize_float(value: Any) -> float | None:
    """Converte um valor textual ou numérico em ``float``."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None
