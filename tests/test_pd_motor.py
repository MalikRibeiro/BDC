import pytest
import math
from domain.credito.pd_motor import calcular_pd_ajustada

def test_risk3_consumidor_le5():
    """Golden test para a fórmula Risk3 de Consumidor <= 5MWm (Nota Técnica §8.1)."""
    registro = {
        "CNPJ": "11111111000100",
        "SEGMENTO_PD": "CONSUMIDOR_LE_5",
        "SCORE_BUREAU": 66.88,
        "FATOR_ALERTA": 1.0,
        "DATA_BUREAU": "2026-08-01"
    }
    
    # Resultado esperado: ~3.4394% com a correção para 0.11
    resultado = calcular_pd_ajustada(
        registro=registro,
        pd_faixas={}, 
        pd_transform_rules={},
        pd_cpura_config={},
        score_cpura_config={},
        pd_zscore_config={}
    )
    
    pd_final = resultado.get("PD_FINAL")
    assert pd_final is not None
    assert math.isclose(pd_final, 0.034394, abs_tol=1e-5), f"PD calculada incorreta: {pd_final}"
    assert resultado.get("RATING_FINAL") == "NAO_APLICAVEL"

def test_cgrupo_tabela_fixa():
    """Golden test para mapeamento de CGRUPO (Fitch/S&P/Moody's)."""
    registro = {
        "CNPJ": "22222222000100",
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
                "short_term_or_default_markers": ["D", "SD"],
                "agencias": {
                    "FITCH": {"A": ["AAA", "AA+"]}
                }
            },
            "pd_final_rules": {
                "pd_tabela": {"AAA": 0.0005, "AA+": 0.0008}
            }
        }
    }
    
    resultado = calcular_pd_ajustada(
        registro=registro,
        pd_faixas={},
        pd_transform_rules=pd_transform_rules,
        pd_cpura_config={},
        score_cpura_config={},
        pd_zscore_config={}
    )
    
    assert resultado.get("PD_FINAL") == 0.0005

def test_fluxo_rj():
    """Golden test para recuperação judicial."""
    registro = {
        "CNPJ": "33333333000100",
        "TIPO_COMERCIALIZADORA": "CPURA",
        "SEGMENTO_PD": "CPURA",
        "RECUPERACAO_JUDICIAL": "SIM"
    }
    
    resultado = calcular_pd_ajustada(
        registro=registro,
        pd_faixas={},
        pd_transform_rules={},
        pd_cpura_config={},
        score_cpura_config={},
        pd_zscore_config={}
    )
    
    assert resultado.get("STATUS_CALCULO_PD") == "RECUPERACAO_JUDICIAL"
    assert resultado.get("PD_FINAL") == 1.0
    assert resultado.get("RATING_FINAL") == "E"

def test_fluxo_pd_sub():
    """Golden test para validade e fallback PD_sub."""
    # Data muito antiga aciona o fallback
    registro = {
        "CNPJ": "44444444000100",
        "TIPO_COMERCIALIZADORA": "CPURA",
        "SEGMENTO_PD": "CPURA",
        "DATA_DEMONSTRACAO_FINANCEIRA": "2020-01-01",
        "PROBABILIDADE_DEFAULT": 0.01,
        "RATING_COPEL": "B",
        "PD_RISK3": 0.20
    }
    
    resultado = calcular_pd_ajustada(
        registro=registro,
        pd_faixas={},
        pd_transform_rules={},
        pd_cpura_config={},
        score_cpura_config={},
        pd_zscore_config={}
    )
    
    assert resultado.get("STATUS_CALCULO_PD") == "CONCLUIDO_COM_PD_SUB"
    assert resultado.get("PD_FINAL") == 0.20
    assert resultado.get("RATING_FINAL") == "E"
