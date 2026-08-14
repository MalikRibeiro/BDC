import sys
import logging
import pytest
from pathlib import Path

# Ajuste do path: como o arquivo está em src/tests/,
# .parent é 'tests' e .parent.parent é a pasta 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from control.layout_catalog import _validate_layout_structure

# Criação de um logger simulado para o teste
logger = logging.getLogger("test_logger")

def test_cenario_1_layout_valido():
    """Cenário 1: Layout possui field_map e campos com pelo menos uma âncora válida."""
    layout_valido = {
        "field_map": {
            "CNPJ": {"value_cell": "B13"},
            "DATA_DF": {"search_pattern": "^DATA"},
            "MISTO": {"value_cell": "A1", "search_pattern": "PADRAO"}
        }
    }
    # Se a validação passar, nenhuma exceção é lançada e o teste tem sucesso
    _validate_layout_structure(layout_valido, "layout_mock_valido", logger)

def test_cenario_2_layout_sem_field_map():
    """Cenário 2: Layout está corrompido e perdeu a raiz 'field_map'."""
    layout_invalido = {
        "outra_chave": "valor_qualquer"
    }
    with pytest.raises(SystemExit) as e:
        _validate_layout_structure(layout_invalido, "layout_mock_corrompido", logger)
    assert e.value.code == 1

def test_cenario_3_layout_com_campo_vazio():
    """Cenário 3: Um campo específico perdeu as âncoras 'value_cell' e 'search_pattern'."""
    layout_invalido = {
        "field_map": {
            "CNPJ": {"value_cell": "B13"},
            "CAMPO_FALTANDO_ANCORA": {"alguma_outra_coisa": "X"} # Falha aqui
        }
    }
    with pytest.raises(SystemExit) as e:
        _validate_layout_structure(layout_invalido, "layout_mock_campo_vazio", logger)
    assert e.value.code == 1