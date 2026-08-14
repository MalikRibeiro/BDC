"""Carregamento e validação dos layouts de fichas."""

from __future__ import annotations

import sys
from typing import Any

from app.context import AppContext
from common.io_json import read_json


def _validate_layout_structure(layout: dict[str, Any], versao: str, logger: Any) -> None:
    """Valida se o layout possui a estrutura mínima para não quebrar o extrator."""
    if "field_map" not in layout:
        logger.critical("Layout '%s' inválido: chave 'field_map' ausente.", versao)
        sys.exit(1)
        
    for field_name, config in layout["field_map"].items():
        # Ignora campos que explicitamente não estão implementados nos layouts antigos (v1 ao v6)
        if not config.get("implemented", True):
            continue
            
        has_static = "value_cell" in config and config["value_cell"] not in [None, "0", 0]
        has_dynamic = "search_pattern" in config and config["search_pattern"] not in [None, ""]
        
        # Removemos o sys.exit(1) que estava quebrando os layouts antigos.
        # O extrator já está preparado para retornar None quando a âncora não existe.
        if not has_static and not has_dynamic:
            logger.debug(
                "Layout '%s' - Campo '%s': sem âncora estática ou dinâmica. Retornará vazio.", 
                versao, field_name
            )


def load_layout_catalog(
    catalog_path: str,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Carrega o catálogo consolidado de layouts."""
    try:
        if logger is not None:
            logger.info("Carregando catálogo de layouts: %s", catalog_path)

        catalog = read_json(catalog_path)

        if logger is not None:
            logger.info("Catálogo de layouts carregado com sucesso.")

        return catalog

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar catálogo de layouts: %s", catalog_path)
        raise


def load_layouts_comercializadoras(
    context: AppContext,
    logger: Any | None = None,
) -> dict[str, dict[str, Any]]:
    """Carrega e valida os layouts de fichas de comercializadoras."""
    layouts: dict[str, dict[str, Any]] = {}

    try:
        if logger is not None:
            logger.info("Iniciando carga dos layouts de comercializadoras.")

        for version in range(1, 8):
            key = f"layout_ficha_comercializadora_v{version}"
            layout_path = context.control_file(key)

            layout_data = read_json(layout_path)
            
            # Validação adaptada para não quebrar layouts antigos
            if logger is not None:
                _validate_layout_structure(layout_data, key, logger)

            layouts[f"padrao_{version}"] = layout_data

        if logger is not None:
            logger.info(
                "Layouts de comercializadoras carregados com sucesso. Quantidade: %s",
                len(layouts),
            )

        return layouts

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar layouts de comercializadoras.")
        raise


def load_layouts_consumidores(
    context: AppContext,
    logger: Any | None = None,
) -> dict[str, dict[str, Any]]:
    """Carrega e valida os layouts de fichas de consumidores."""
    layouts: dict[str, dict[str, Any]] = {}

    try:
        if logger is not None:
            logger.info("Iniciando carga dos layouts de consumidores.")

        for version in range(1, 4):
            key = f"layout_ficha_consumidor_v{version}"
            layout_path = context.control_file(key)

            layout_data = read_json(layout_path)
            
            # Validação adaptada para não quebrar layouts antigos
            if logger is not None:
                _validate_layout_structure(layout_data, key, logger)

            layouts[f"v{version}"] = layout_data

        if logger is not None:
            logger.info(
                "Layouts de consumidores carregados com sucesso. Quantidade: %s",
                len(layouts),
            )

        return layouts

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar layouts de consumidores.")
        raise