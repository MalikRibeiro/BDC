import sys
import logging
from typing import Any
import jsonschema
from jsonschema.exceptions import ValidationError

logger = logging.getLogger(__name__)

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