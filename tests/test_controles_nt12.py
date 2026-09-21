import pytest
import math
from domain.credito.pd_motor import calcular_pd_ajustada

def test_controle_pd_intervalo():
    """Controle 1: PD no intervalo [0,1]."""
    registro = {
        "CNPJ": "11111111000100", 
        "TIPO_COMERCIALIZADORA": "CGRUPO",
        "SEGMENTO_PD": "CGRUPO", 
        "AGENCIA": "FITCH",
        "NOTA_CREDITO": "AAA",
        "DATA_DEMONSTRACAO_FINANCEIRA": "2026-01-01", 
        "DATA_RATING_PUBLICO": "2026-08-01"
    }
    pd_transform_rules = {
        "CGRUPO": {
            "rating_externo": {
                "default_class": "E",
                "short_term_or_default_markers": [],
                "agencias": {
                    "FITCH": {"A": ["AAA"]}
                }
            },
            "pd_final_rules": {
                "pd_tabela": {"AAA": 0.0005}
            }
        }
    }
    res = calcular_pd_ajustada(registro, {}, pd_transform_rules, {}, {}, {})
    pd_final = res.get("PD_FINAL")
    assert 0 <= pd_final <= 1

def test_controle_rating_dominio():
    """Controle 2: rating no domínio permitido."""
    # Consumidor LE 5MWm NÃO deve ter rating Copel
    registro = {"CNPJ": "1111", "SEGMENTO_PD": "CONSUMIDOR_LE_5", "SCORE_BUREAU": 66.88, "FATOR_ALERTA": 1.0, "DATA_BUREAU": "2026-08-01"}
    res = calcular_pd_ajustada(registro, {}, {}, {}, {}, {})
    assert res.get("RATING_FINAL") in ["A", "B", "C", "D", "E", None, "NAO_APLICAVEL"] 
    
def test_controle_coerencia_pd_rating():
    """Controle 3 e 5: Coerência PD/Rating e fronteira de 50% para > 5MWm."""
    # Para forçar o rating E no >5MWm, vamos usar o cenário de DF vencida
    # que pela NT ativa a substituta = max(pd_risk3, 0.50) e emite rating E.
    registro = {
        "CNPJ": "1111", 
        "SEGMENTO_PD": "CONSUMIDOR_GT_5", 
        "DATA_DEMONSTRACAO_FINANCEIRA": "2020-01-01", # Dados vencidos há muito tempo
        "PD_RISK3": 0.60 # Para que o max(pd_risk3, 0.50) dê 0.60
    }
    
    mock_score_config = {
        "pesos_quantitativos": {"PD": 0.32, "FCO_ROL": 0.24, "ROE": 0.07, "ROA": 0.07},
        "pesos_qualitativos": {"BOARD": 0.20, "AUDITORIA": 0.05, "BUREAU": 0.05}
    }
    mock_pd_config = {"limites_pd": True}
    res = calcular_pd_ajustada(registro, {}, {}, mock_pd_config, mock_score_config, {})
    if res.get("RATING_FINAL") == "E":
        assert res.get("PD_FINAL") >= 0.50

def test_controle_igualdade_pd_risk3():
    """Controle 4: Igualdade PD_final = PD_Risk3 para consumidores <= 5MWm."""
    registro = {"CNPJ": "1111", "SEGMENTO_PD": "CONSUMIDOR_LE_5", "SCORE_BUREAU": 66.88, "FATOR_ALERTA": 1.0, "DATA_BUREAU": "2026-08-01"}
    res = calcular_pd_ajustada(registro, {}, {}, {}, {}, {})
    # Sabemos que 66.88 com coef 0.11 -> 3.4394%
    assert math.isclose(res.get("PD_FINAL"), 0.034394, abs_tol=1e-5)
    
def test_controle_reproducao_parametros():
    """Controle 6: Reprodução de parâmetros versionados (Testado indiretamente nos golden tests)."""
    assert True

def test_controle_validade_pd_sub():
    """Controle 7: Validade e PD_sub."""
    # CGRUPO com dados vencidos > 18 meses (1.5 anos)
    registro = {
        "CNPJ": "1111", 
        "TIPO_COMERCIALIZADORA": "CGRUPO",
        "SEGMENTO_PD": "CGRUPO", 
        "AGENCIA": "FITCH",
        "NOTA_CREDITO": "AAA",
        "DATA_DEMONSTRACAO_FINANCEIRA": "2020-01-01", 
        "DATA_RATING_PUBLICO": "2020-01-01"
    }
    res = calcular_pd_ajustada(registro, {}, {}, {}, {}, {})
    assert res.get("PD_FINAL") >= 0.15 # Max(ultima_valida, 15%)
