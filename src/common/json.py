"""Leitura, escrita e validação estrutural de arquivos JSON do sistema BDC."""

from __future__ import annotations

import json
import sys
import logging
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema.exceptions import ValidationError

logger = logging.getLogger(__name__)


def ler_json(path: str | Path) -> Any:
    """Lê um arquivo JSON e devolve seu conteúdo."""
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def validar_esquema_json(instance: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    """Valida um dicionário contra um JSON Schema e aborta a execução em caso de falha."""
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except ValidationError as e:
        logger.critical(
            "Falha de validação estrutural no arquivo %s. Caminho do erro: %s. Motivo: %s",
            label, e.json_path, e.message,
        )
        sys.exit(1)
