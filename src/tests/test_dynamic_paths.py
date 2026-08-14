import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config_builder import AppConfigBuilder

def test_config_builder_sem_json_t122(tmp_path):
    """
    Testa a resolução dinâmica sem depender da leitura do arquivo JSON em disco.
    """
    base_dir_simulado = tmp_path / "Z_DRIVE_CORPORATIVO"
    
    # Dicionário mock simulando a estrutura relativa contida no JSON
    mock_paths = {
        "entradas": "ENTRADAS",
        "staging": "SAIDAS/staging"
    }
    
    builder = AppConfigBuilder(base_dir_simulado)
    resolved_paths = builder.resolve_dict(mock_paths)
    
    # Validações
    assert resolved_paths["entradas"] == str(base_dir_simulado / "ENTRADAS")
    assert resolved_paths["staging"] == str(base_dir_simulado / "SAIDAS" / "staging")