"""Leitura e escrita de arquivos JSON do sistema BDC."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ler_json(path: str | Path) -> Any:
    """Lê um arquivo JSON e devolve seu conteúdo."""
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)
