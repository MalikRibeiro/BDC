"""Carregamento do contexto de execução do sistema BDC."""

from __future__ import annotations

import os
import sys
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app.config_builder import AppConfigBuilder
from common.io_json import read_json
from common.validation import validate_json_schema

logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class AppContext:
    app_config: dict[str, Any]
    config: dict[str, Any]
    paths: dict[str, Any]
    control_files: dict[str, Any]
    naming: dict[str, Any]

    def path(self, key: str) -> Path:
        return Path(self.paths[key])

    def control_file(self, key: str) -> Path:
        return Path(self.control_files[key])


def load_context(configs_dir: str | Path) -> AppContext:
    configs_path = Path(configs_dir)

    base_dir_env = os.getenv("BDC_BASE_DIR")
    if not base_dir_env:
        logger.critical("Variavel BDC_BASE_DIR nao encontrada no arquivo .env!")
        sys.exit(1)

    if not configs_path.exists():
        logger.critical("Diretório de configs não encontrado: %s", configs_path)
        sys.exit(1)

    app_config_path = configs_path / "app_config.json"
    config_path = configs_path / "config.json"

    if not app_config_path.exists() or not config_path.exists():
        logger.critical("Arquivos de configuração base não encontrados.")
        sys.exit(1)

    app_config = read_json(app_config_path)
    config = read_json(config_path)

    try:
        raw_paths = app_config["paths"]
        raw_control_files = app_config["control_files"]
    except KeyError as e:
        logger.critical("app_config.json malformado. Chave ausente: %s", e)
        sys.exit(1)

    # Resolve os caminhos usando o Builder
    builder = AppConfigBuilder(base_dir_env)
    resolved_paths = builder.resolve_dict(raw_paths)
    resolved_control_files = builder.resolve_dict(raw_control_files)

    schema_app_config_path = Path(resolved_control_files["schema_app_config"])
    schema_config_path = Path(resolved_control_files["schema_config"])

    if not schema_app_config_path.exists() or not schema_config_path.exists():
        logger.critical("Arquivos de schema de configuração não encontrados.")
        sys.exit(1)

    schema_app_config = read_json(schema_app_config_path)
    schema_config = read_json(schema_config_path)

    # Validação estrutural do JSON original (Fail-Fast)
    validate_json_schema(app_config, schema_app_config, "app_config.json")
    validate_json_schema(config, schema_config, "config.json")

    # Injeta valores resolvidos para manter coerência nos serviços
    app_config["base_dir"] = str(builder.base_dir)
    app_config["paths"] = resolved_paths
    app_config["control_files"] = resolved_control_files

    return AppContext(
        app_config=app_config,
        config=config,
        paths=resolved_paths,
        control_files=resolved_control_files,
        naming=app_config.get("naming", {}),
    )