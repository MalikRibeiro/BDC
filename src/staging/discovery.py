"""Descoberta de arquivos pendentes para processamento."""

from __future__ import annotations

from pathlib import Path


def discover_pending_excels(input_dir: str | Path) -> list[Path]:
    """Lista arquivos Excel pendentes em um diretório."""
    base_dir = Path(input_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    return sorted(
        file_path
        for file_path in base_dir.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower() in {".xlsx", ".xlsm", ".xls"}
    )
