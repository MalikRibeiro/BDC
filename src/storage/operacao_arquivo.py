"""Operações robustas de arquivo para ambiente Windows."""

from __future__ import annotations

import shutil
import time
from pathlib import Path


def mover_arquivo_com_tentativa_adicional(
    source: str | Path,
    target: str | Path,
    attempts: int = 5,
    wait_seconds: float = 0.5,
) -> Path:
    """Move um arquivo com novas tentativas em caso de bloqueio."""
    source_path = Path(source)
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None

    for _ in range(attempts):
        try:
            shutil.move(str(source_path), str(target_path))
            return target_path
        except PermissionError as exc:
            last_error = exc
            time.sleep(wait_seconds)

    if last_error is not None:
        raise last_error

    return target_path
