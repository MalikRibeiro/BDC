import sys
import json
import logging
import pytest
from pathlib import Path

# Ajuste do path para a raiz do código fonte
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from silver.field_type_normalizer import normalize_record

logger = logging.getLogger("test_logger")

@pytest.fixture
def mock_context(tmp_path):
    """Cria um contexto falso simulando a presença de um JSON de fallback."""
    control_dir = tmp_path / "control" / "quality"
    control_dir.mkdir(parents=True)
    
    fallback_json = control_dir / "field_types_teste.json"
    fallback_data = {
        "date_fields": ["DATA_TESTE"],
        "float_fields": ["VALOR_TESTE"],
        "text_fields": ["NOME_TESTE"],
        "cnpj_fields": ["CNPJ_TESTE"]
    }
    fallback_json.write_text(json.dumps(fallback_data))
    
    class MockContext:
        def control_file(self, key):
            if key == "field_types_teste":
                return fallback_json
            return fallback_json
            
    return MockContext()

def test_t131_normalizer_using_python_class(mock_context):
    """Cenário 1: Usa o slug mapeado e consome a tipagem via Classe Python."""
    slug = "field_types_fichas_comercializadoras"
    
    raw_record = {
        "CNPJ": "12.345.678/0001-90",
        "DATA_DEMONSTRACAO_FINANCEIRA": "2024",
        "PATRIMONIO_LIQUIDO": "1500.5",
        "SIGLA": "  EMPRESA X  "
    }
    
    normalized = normalize_record(raw_record, mock_context, slug, logger)
    
    assert normalized["CNPJ"] == "12345678000190"
    assert normalized["DATA_DEMONSTRACAO_FINANCEIRA"] == "31/12/2024"
    assert normalized["PATRIMONIO_LIQUIDO"] == 1500.5
    assert normalized["SIGLA"] == "EMPRESA X"

def test_t131_normalizer_fallback_json(mock_context):
    """Cenário 2: Usa um slug inexistente na classe e força a leitura do JSON."""
    slug = "field_types_teste"
    
    raw_record = {
        "CNPJ_TESTE": "98.765.432/0001-10",
        "DATA_TESTE": "15/10/2023",
        "VALOR_TESTE": " 300.0 ",
        "NOME_TESTE": "  TESTE  "
    }
    
    normalized = normalize_record(raw_record, mock_context, slug, logger)
    
    assert normalized["CNPJ_TESTE"] == "98765432000110"
    assert normalized["DATA_TESTE"] == "2023-10-15"
    assert normalized["VALOR_TESTE"] == 300.0
    assert normalized["NOME_TESTE"] == "TESTE"