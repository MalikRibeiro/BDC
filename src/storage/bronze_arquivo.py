from __future__ import annotations

import shutil
from pathlib import Path


def publicar_arquivo_bruto(
    source_file: str | Path,
    bronze_root_dir: str | Path,
) -> Path:
    """Publica um arquivo na camada bronze."""
    source_path = Path(source_file)
    target_dir = Path(bronze_root_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / source_path.name
    shutil.copy2(source_path, target_path)
    return target_path
