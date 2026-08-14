"""Geração de hash para arquivos do sistema BDC."""

from __future__ import annotations

import hashlib
from pathlib import Path


def hash_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Calcula o hash SHA-256 de um arquivo."""
    file_path = Path(path)
    hasher = hashlib.sha256()

    with file_path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()
