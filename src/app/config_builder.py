"""Builder programático para resolução de caminhos do sistema."""

from pathlib import Path
from typing import Any

class AppConfigBuilder:
    """Construtor responsável por aplicar o diretório base à topologia relativa."""
    
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir).resolve()

    def resolve_dict(self, paths_dict: dict[str, Any]) -> dict[str, str]:
        """Resolve todos os caminhos relativos de um dicionário contra o diretório base."""
        resolved = {}
        for key, relative_path in paths_dict.items():
            resolved[key] = str(self.base_dir / relative_path)
        return resolved