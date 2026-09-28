from pathlib import Path
import pytest
import math
from domain.credito.pd_motor import calcular_pd_ajustada
from common.json import ler_json

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

def test_fluxo_validade_df():
    """Golden test para metadados de validade sem rebaixamento destrutivo."""
    registro = {
        "CNPJ": "44444444000100",
        "TIPO_COMERCIALIZADORA": "CPURA",
        "SEGMENTO_PD": "CPURA",
        "DATA_DEMONSTRACAO_FINANCEIRA": "2020-01-01",
        "DATA_BUREAU": "2026-08-01",
        "PROBABILIDADE_DEFAULT": 0.01,
        "PD_BASE": 0.01,
        "FCO": 2000,
        "ROL": 12000,
        "ROA": 0.10,
        "ROE": 0.15,
        "AUDITOR": "PWC",
        "RATING_BOARD_COPEL": "B",
        "RATING_BUREAU": "B",
        "RATING_COPEL": "B",
        "PD_RISK3": 0.20
    }
    
    cfg_dir = Path("ENTRADAS/control/configs")
    pd_faixas = ler_json(cfg_dir / "pd_faixas.json")
    pd_cpura_cfg = ler_json(cfg_dir / "pd_cpura_config.json")
    score_cfg = ler_json(cfg_dir / "score_cpura_config.json")
    pd_transform_rules = ler_json(cfg_dir / "pd_transform_rules.json")
    pd_zscore_config = ler_json(cfg_dir / "pd_zscore_config.json")

    resultado = calcular_pd_ajustada(
        registro=registro,
        pd_faixas=pd_faixas,
        pd_transform_rules=pd_transform_rules,
        pd_cpura_config=pd_cpura_cfg,
        score_cpura_config=score_cfg,
        pd_zscore_config=pd_zscore_config
    )
    
    assert resultado.get("STATUS_CALCULO_PD") == "CONCLUIDO"
    assert resultado.get("VALIDADE_DF") is not None


def test_cgrupo_sem_rating_retorna_nulo():
    """Garante que ausência de rating não seja mascarada com Rating E ou PD arbitrária."""
    registro = {
        "CNPJ": "55555555000100",
        "TIPO_COMERCIALIZADORA": "CGRUPO",
        "SEGMENTO_PD": "CGRUPO",
        "DATA_DEMONSTRACAO_FINANCEIRA": "2022-12-31",
        "PROBABILIDADE_DEFAULT": 0.005
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

    assert resultado.get("RATING_FINAL") is None
    assert resultado.get("PD_FINAL") is None
    assert resultado.get("PD_METODO") == "SEM_DADOS"


def test_risk3_consumidor_le5_sem_score():
    """Garante que consumidor <= 5MWm sem SCORE_BUREAU retorne status PENDENTE de forma limpa."""
    registro = {
        "CNPJ": "66666666000100",
        "SEGMENTO_PD": "CONSUMIDOR_LE_5",
        "SCORE_BUREAU": None,
        "FATOR_ALERTA": None,
    }
    resultado = calcular_pd_ajustada(
        registro=registro,
        pd_faixas={},
        pd_transform_rules={},
        pd_cpura_config={},
        score_cpura_config={},
        pd_zscore_config={}
    )
    assert resultado.get("STATUS_CALCULO_PD") == "PENDENTE"
    assert resultado.get("PD_FINAL") is None
    assert resultado.get("PD_METODO") == "SEM_DADOS_BUREAU"


def test_fim_vigencia_analise_df():
    """Valida regra de 18 meses para análise DF."""
    registro = {
        "CNPJ": "77777777000100",
        "SEGMENTO_PD": "CPURA",
        "DATA_DEMONSTRACAO_FINANCEIRA": "2025-01-01",
        "TIPO_COMERCIALIZADORA": "CPURA",
        "RECUPERACAO_JUDICIAL": "SIM"  # curto-circuito para validar data
    }
    resultado = calcular_pd_ajustada(
        registro=registro,
        pd_faixas={},
        pd_transform_rules={},
        pd_cpura_config={},
        score_cpura_config={},
        pd_zscore_config={}
    )
    assert resultado.get("FIM_VIGENCIA_ANALISE") == "2026-07-01"


def test_fim_vigencia_analise_bureau():
    """Valida regra de 12 meses para análise Bureau."""
    registro = {
        "CNPJ": "88888888000100",
        "SEGMENTO_PD": "CONSUMIDOR_LE_5",
        "SCORE_BUREAU": 66.88,
        "FATOR_ALERTA": 1.0,
        "DATA_BUREAU": "2026-03-15"
    }
    resultado = calcular_pd_ajustada(
        registro=registro,
        pd_faixas={},
        pd_transform_rules={},
        pd_cpura_config={},
        score_cpura_config={},
        pd_zscore_config={}
    )
    assert resultado.get("FIM_VIGENCIA_ANALISE") == "2027-03-15"



