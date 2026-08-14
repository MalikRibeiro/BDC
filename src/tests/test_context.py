import json
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.context import load_context

@pytest.fixture
def setup_env(tmp_path):
    """Fixture que simula a estrutura de arquivos e schemas necessários para os testes."""
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    
    schema_dir = tmp_path / "control" / "schemas"
    schema_dir.mkdir(parents=True)
    
    schema_app_path = schema_dir / "schema_app_config.json"
    schema_config_path = schema_dir / "schema_config.json"
    
    # 1. Schemas de simulação (mock) com regras estritas
    schema_app_config = {
        "type": "object",
        "required": ["env", "control_files"],
        "properties": {
            "env": {"type": "string"},
            "control_files": {"type": "object"}
        }
    }
    schema_config = {
        "type": "object",
        "required": ["system_name"],
        "properties": {
            "system_name": {"type": "string"}
        }
    }
    schema_app_path.write_text(json.dumps(schema_app_config))
    schema_config_path.write_text(json.dumps(schema_config))
    
    # 2. Configurações válidas (Happy Path)
    valid_app_config = {
        "env": "dev",
        "paths": {},
        "naming": {},
        "control_files": {
            "schema_app_config": str(schema_app_path),
            "schema_config": str(schema_config_path)
        }
    }
    valid_config = {
        "system_name": "BDC"
    }
    
    app_config_file = configs_dir / "app_config.json"
    config_file = configs_dir / "config.json"
    
    app_config_file.write_text(json.dumps(valid_app_config))
    config_file.write_text(json.dumps(valid_config))
    
    return {
        "configs_dir": configs_dir,
        "app_config_file": app_config_file,
        "config_file": config_file,
        "valid_app_config": valid_app_config,
        "valid_config": valid_config
    }


# ==============================================================================
# CENÁRIOS DE TESTE T1.1.1
# ==============================================================================

def test_cenario_1_sucesso(setup_env):
    """Cenário 1: Configurações perfeitas passam na validação do schema."""
    ctx = load_context(setup_env["configs_dir"])
    assert ctx.app_config["env"] == "dev"
    assert ctx.config["system_name"] == "BDC"

def test_cenario_2_diretorio_inexistente(tmp_path):
    """Cenário 2: Diretório de configs passado não existe."""
    with pytest.raises(SystemExit) as e:
        load_context(tmp_path / "pasta_invalida")
    assert e.value.code == 1

def test_cenario_3_arquivo_config_ausente(setup_env):
    """Cenário 3: Faltando um dos arquivos base (config.json)."""
    setup_env["config_file"].unlink()
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1

def test_cenario_4_control_files_ausente(setup_env):
    """Cenário 4: app_config sem a chave control_files (quebra o boot do schema)."""
    bad_config = setup_env["valid_app_config"].copy()
    del bad_config["control_files"]
    setup_env["app_config_file"].write_text(json.dumps(bad_config))
    
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1

def test_cenario_5_schema_nao_encontrado_no_disco(setup_env):
    """Cenário 5: Os caminhos do schema no JSON apontam para lugar nenhum."""
    bad_config = setup_env["valid_app_config"].copy()
    bad_config["control_files"]["schema_app_config"] = "/caminho/falso/schema.json"
    setup_env["app_config_file"].write_text(json.dumps(bad_config))
    
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1

def test_cenario_6_schema_invalido_campo_ausente(setup_env):
    """Cenário 6: O JSON existe, mas falta um campo exigido pelo schema."""
    bad_config = setup_env["valid_app_config"].copy()
    del bad_config["env"] # O schema mock exige "env"
    setup_env["app_config_file"].write_text(json.dumps(bad_config))
    
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1

def test_cenario_7_schema_invalido_tipo_errado(setup_env):
    """Cenário 7: O JSON existe, o campo existe, mas o tipo de dado está errado."""
    bad_config = setup_env["valid_config"].copy()
    bad_config["system_name"] = 12345 # O schema mock exige string, não int
    setup_env["config_file"].write_text(json.dumps(bad_config))
    
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1