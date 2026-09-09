import os
from pathlib import Path
from typing import Optional, Union

from src.app.context import AppContext, carregar_contexto
from dotenv import load_dotenv

load_dotenv()

CONFIGS_DIR_ENV_VAR = "BDC_CONFIGS_DIR"


def resolve_configs_dir(explicit_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Resolve o diretório de configurações utilizando a seguinte hierarquia:
    1. Caminho explícito fornecido (ex.: via flag CLI --configs-dir).
    2. Variável de ambiente `BDC_CONFIGS_DIR`.
    3. Diretório relativo à raiz do projeto (`<project_root>/ENTRADAS/configs`).

    Args:
        explicit_path: Caminho explícito opcional (string ou Path).

    Returns:
        Path: Objeto Path do diretório de configurações validado.

    Raises:
        FileNotFoundError: Caso o diretório de configurações não exista.
    """
    if explicit_path:
        configs_dir = Path(explicit_path).resolve()
    elif os.environ.get(CONFIGS_DIR_ENV_VAR):
        configs_dir = Path(os.environ[CONFIGS_DIR_ENV_VAR]).resolve()
    else:
        project_root = Path(__file__).resolve().parents[2]
        configs_dir = project_root / "ENTRADAS" / "configs"

    if not configs_dir.exists() or not configs_dir.is_dir():
        raise FileNotFoundError(
            f"Diretório de configurações não encontrado em: '{configs_dir}'.\n"
            f"Por favor, verifique se o caminho existe ou especifique o caminho correto via:\n"
            f"  - Flag CLI: --configs-dir /caminho/para/configs\n"
            f"  - Variável de ambiente: export {CONFIGS_DIR_ENV_VAR}=/caminho/para/configs"
        )

    return configs_dir


def aplicativo_bootstrap(configs_dir: Optional[Union[str, Path]] = None) -> AppContext:
    """
    Realiza o bootstrap da aplicação e carrega o AppContext.

    Args:
        configs_dir: Caminho explícito ou opcional para o diretório de configurações.

    Returns:
        AppContext: Contexto inicializado da aplicação.
    """
    resolved_dir = resolve_configs_dir(configs_dir)
    return carregar_contexto(resolved_dir)