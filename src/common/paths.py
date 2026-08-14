"""Funções utilitárias para nomes de paths e diretórios."""

from __future__ import annotations

import re


_INVALID_PATH_CHARS = r'[<>:"/\\|?*]+'


def sanitize_folder_name(value: str) -> str:
    """Sanitiza um texto para uso seguro em nome de pasta."""
    cleaned = re.sub(_INVALID_PATH_CHARS, "_", value.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("._ ")
