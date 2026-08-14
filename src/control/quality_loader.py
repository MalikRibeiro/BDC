"""Carregamento e validação estrita das regras de qualidade da entidade.

feat(T1.1.2): Integra validação contra JSON Schema (mesmo padrão de mapping_loader.py).
Regras malformadas geram erro descritivo antes do processamento de qualquer ficha.
Ref: §5.2, §5.3 do Planejamento Funcional.
"""
from __future__ import annotations

from typing import Any

from app.context import AppContext
from common.io_json import read_json
from common.validation import validate_json_schema


def _load_and_validate_quality_rules(
    rules_path,
    schema_path,
    descricao: str,
    logger: Any,
) -> dict[str, Any]:
    """Carrega um arquivo de quality rules e valida contra seu JSON Schema."""
    try:
        logger.info("Carregando %s: %s", descricao, rules_path)

        if not rules_path.exists():
            raise FileNotFoundError(f"Arquivo de quality rules não encontrado: {rules_path}")

        if not schema_path.exists():
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_path}")

        content = read_json(rules_path)
        schema = read_json(schema_path)

        # Validação Estrita (Fail-Fast)
        validate_json_schema(instance=content, schema=schema, label=descricao)

        if not isinstance(content, dict):
            raise ValueError(f"O {descricao} deve ser um objeto JSON.")

        logger.info("%s carregado e validado com sucesso.", descricao)

        return content

    except Exception:
        logger.exception("Falha crítica ao carregar e validar %s", descricao)
        raise


def load_data_quality_rules_comercializadoras(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega e valida as regras de qualidade das fichas de comercializadoras."""
    return _load_and_validate_quality_rules(
        rules_path=context.control_file("data_quality_rules_fichas_comercializadoras"),
        schema_path=context.control_file("schema_data_quality_rules"),
        descricao="Regras de Qualidade de Comercializadoras",
        logger=logger,
    )


def load_data_quality_rules_consumidores(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega e valida as regras de qualidade das fichas de consumidores."""
    return _load_and_validate_quality_rules(
        rules_path=context.control_file("data_quality_rules_fichas_consumidores"),
        schema_path=context.control_file("schema_data_quality_rules"),
        descricao="Regras de Qualidade de Consumidores",
        logger=logger,
    )
