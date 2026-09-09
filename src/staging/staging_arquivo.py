from __future__ import annotations

import shutil
from pathlib import Path


def copiar_para_staging(
    source_file: str | Path,
    staging_dir: str | Path,
    target_name: str,
) -> Path:
    """Copia um arquivo para o staging com nome técnico."""
    source_path = Path(source_file)
    target_dir = Path(staging_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / target_name
    shutil.copy2(source_path, target_path)
    return target_path
