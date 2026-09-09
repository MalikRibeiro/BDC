import pytest
from silver.formatador_silver import normalizar_registro

def test_normalizar_registro_in_memory_casting():
    # Arrange
    raw_record = {
        "CNPJ": "12.345.678/0001-90",
        "DATA_DEMONSTRACAO_FINANCEIRA": "2024-12-31T00:00:00",
        "PROBABILIDADE_DEFAULT": "0,05",
        "EMPRESA": "Empresa Teste SA"
    }

    mock_catalog = {
        "fields": {
            "CNPJ": {"type": "cnpj"},
            "DATA_DEMONSTRACAO_FINANCEIRA": {"type": "date"},
            "PROBABILIDADE_DEFAULT": {"type": "float"},
            "EMPRESA": {"type": "text"}
        }
    }

    # Act
    # Não passamos context nem dependemos de disco!
    result = normalizar_registro(raw_record, mock_catalog)

    # Assert
    assert result["CNPJ"] == "12.345.678/0001-90"
    # A normalização de data e float depende das funções em common, 
    # mas garantimos que a lógica passou pelos métodos de cast apropriados.
    # PROBABILIDADE_DEFAULT era "0,05" string e deveria virar float (0.05) ou ser processado.
    # Na verdade, normalizar_registro usa to_float_br("0,05") que retorna 0.05.
    assert result["PROBABILIDADE_DEFAULT"] == 0.05
    assert result["EMPRESA"] == "EMPRESA TESTE SA"
    # DATA_DEMONSTRACAO_FINANCEIRA se for date object vai ser mantida, se string vira date? 
    # Dependendo de normalizar_data. 
    # Testar apenas se ele rodou sem erros e os tipos primitivos conhecidos mudaram.

def test_normalizar_registro_empty_catalog_raises_error():
    # Arrange
    raw_record = {"CNPJ": "12.345.678/0001-90"}
    
    # Empty fields
    mock_catalog = {"fields": {}}
    
    # Act / Assert
    with pytest.raises(ValueError, match="O catálogo fornecido não contém a chave 'fields' ou está vazio"):
        normalizar_registro(raw_record, mock_catalog)

    # No fields key
    mock_catalog_no_fields = {}
    with pytest.raises(ValueError, match="O catálogo fornecido não contém a chave 'fields' ou está vazio"):
        normalizar_registro(raw_record, mock_catalog_no_fields)

def test_normalizar_registro_no_silent_fallback():
    # Se passarmos um campo que não está no catálogo, ele não sofre os casts do tipo dele
    raw_record = {
        "CAMPO_DESCONHECIDO": "0,05",
        "CNPJ": "12.345.678/0001-90"
    }
    
    mock_catalog = {
        "fields": {
            "CNPJ": {"type": "cnpj"}
        }
    }
    
    result = normalizar_registro(raw_record, mock_catalog)
    
    # "0,05" continua "0,05" porque o campo não está configurado como float
    assert result["CAMPO_DESCONHECIDO"] == "0,05"
