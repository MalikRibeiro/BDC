"""Persistência do manifest de ingestão em formato JSONL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_manifest_record(
    output_file: str | Path,
    record: dict[str, Any],
) -> None:
    """Acrescenta um registro no arquivo JSONL de ingestão."""
    target = Path(output_file)
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_ingestion_history(
    input_file: str | Path,
) -> list[dict[str, Any]]:
    """Carrega o histórico de ingestão a partir do arquivo JSONL."""
    source = Path(input_file)
    if not source.exists():
        return []

    history: list[dict[str, Any]] = []

    with source.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            line = line.strip()
            if not line:
                continue
            history.append(json.loads(line))

    return history
