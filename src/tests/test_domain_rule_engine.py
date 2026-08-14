import sys
import pytest
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.ficha_validator import validate_record

logger = logging.getLogger("test_logger")

def test_t132_engine_com_regras_dinamicas():
    """Cenário 1: Engine consome regras parametrizadas diretamente do JSON."""
    quality_rules = {
        "rules": [
            {"field": "PROBABILIDADE_DEFAULT", "type": "range", "min": 0, "max": 100},
            {"field": "SCORE_BUREAU", "type": "min", "value": 0}
        ]
    }
    
    # Injetando um registro falho para testar a captura unificada
    record_invalido = {
        "CNPJ": "123", "EMPRESA": "TESTE",
        "PROBABILIDADE_DEFAULT": 105, # Viola max=100
        "SCORE_BUREAU": -5 # Viola min=0
    }
    
    erros, avisos = validate_record(record_invalido, ["CNPJ"], logger, quality_rules)
    
    assert any("PROBABILIDADE_DEFAULT" in e and "maior que o limite (100)" in e for e in erros)
    assert any("SCORE_BUREAU" in e and "menor que o limite (0)" in e for e in erros)

def test_t132_engine_fallback_nativo():
    """Cenário 2: Engine aplica regras nativas (fallback) se a comercializadora não possuir a chave rules."""
    quality_rules = None 
    
    record_invalido = {
        "CNPJ": "123", "EMPRESA": "TESTE",
        "PROBABILIDADE_DEFAULT": -10 # Regra nativa deve capturar o erro menor que zero
    }
    
    erros, avisos = validate_record(record_invalido, ["CNPJ"], logger, quality_rules)
    assert any("PROBABILIDADE_DEFAULT" in e and "fora do intervalo" in e for e in erros)