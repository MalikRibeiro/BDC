"""Carregamento e validação estrita das regras de qualidade da entidade.

feat(T1.1.2): Integra validação contra JSON Schema (mesmo padrão de mapping_loader.py).
Regras malformadas geram erro descritivo antes do processamento de qualquer ficha.
Ref: §5.2, §5.3 do Planejamento Funcional.
"""
from __future__ import annotations

from typing import Any
from pathlib import Path

from app.context import AppContext
from common.json import ler_json
from common.json import validar_esquema_json


def _carregar_e_validar_regras_de_qualidade(
    rules_path: Path,
    schema_path: Path,
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

        content = ler_json(rules_path)
        schema = ler_json(schema_path)

        validar_esquema_json(instance=content, schema=schema, label=descricao)

        if not isinstance(content, dict):
            raise ValueError(f"O {descricao} deve ser um objeto JSON.")

        logger.info("%s carregado e validado com sucesso.", descricao)

        return content

    except Exception:
        logger.exception("Falha crítica ao carregar e validar %s", descricao)
        raise


def carregar_regras_de_qualidade_de_dados_comercializadoras(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega as regras de qualidade das fichas de comercializadoras usando o novo master_catalog."""
    
    master_catalog_path = context.path("control_quality") / "master_catalog_comercializadoras.json"
    
    logger.info("Lendo master catalog: %s", master_catalog_path)
    return ler_json(master_catalog_path)


def carregar_regras_de_qualidade_de_dados_consumidores(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega as regras de qualidade das fichas de consumidores usando o novo master_catalog."""
    
    master_catalog_path = context.path("control_quality") / "master_catalog_consumidores.json"
    
    logger.info("Lendo master catalog consumidores: %s", master_catalog_path)
    return ler_json(master_catalog_path)
