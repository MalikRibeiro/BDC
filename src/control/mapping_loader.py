"""Carregamento e validação estrita dos mappings das fichas."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.context import AppContext
from common.io_json import read_json
from common.validation import validate_json_schema

def _load_and_validate_mapping(
    mapping_path: Path,
    schema_path: Path,
    descricao: str,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega um mapping de fichas e valida estritamente contra seu JSON Schema."""
    try:
        logger.info("Carregando %s: %s", descricao, mapping_path)

        if not mapping_path.exists():
            raise FileNotFoundError(f"Arquivo de mapping não encontrado: {mapping_path}")
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_path}")

        # Leitura dos arquivos
        content = read_json(mapping_path)
        schema = read_json(schema_path)

        # Validação Estrita (Fail-Fast)
        validate_json_schema(instance=content, schema=schema, label=descricao)

        if not isinstance(content, list):
            raise ValueError(f"O {descricao} deve ser uma lista.")

        logger.info(
            "%s carregado e validado com sucesso. Quantidade de registros: %s",
            descricao,
            len(content),
        )

        return content

    except Exception:
        logger.exception("Falha crítica ao carregar e validar %s", descricao)
        raise


def load_mapping_fichas_comercializadoras(
    context: AppContext,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega e valida o mapping de fichas de comercializadoras."""
    return _load_and_validate_mapping(
        mapping_path=context.control_file("mapping_fichas_comercializadoras"),
        schema_path=context.control_file("schema_mapping_fichas_comercializadoras"),
        descricao="Mapping de Comercializadoras",
        logger=logger,
    )


def load_mapping_fichas_consumidores(
    context: AppContext,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega e valida o mapping de fichas de consumidores."""
    return _load_and_validate_mapping(
        mapping_path=context.control_file("mapping_fichas_consumidores"),
        schema_path=context.control_file("schema_mapping_fichas_consumidores"),
        descricao="Mapping de Consumidores",
        logger=logger,
    )