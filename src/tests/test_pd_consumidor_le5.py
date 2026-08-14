import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.credito.pd_consumidor_le5 import calcular_pd_final_consumidor_le5

def test_t142_calculo_pd_bureau_sem_restritivo():
    """Score 700 = Rating B (Faixa de B: 1% a 3%). Deve interpolar corretamente."""
    pd_faixas = {
        "CONSUMIDOR_LE_5": {
            "B": {"min": 0.0100, "max": 0.0300}
        }
    }
    registro = {"SCORE_BUREAU": 700.0, "QUANTIDADE_RESTRITIVOS": 0}
    
    res = calcular_pd_final_consumidor_le5(registro, pd_faixas)
    
    assert res["RATING_FINAL"] == "B"
    assert res["PATRIMONIO_LIQUIDO"] == "NAO_APLICAVEL"
    # Uso do pytest.approx para evitar quebra por conversão de floating point em binário
    assert res["PD_FINAL"] == pytest.approx(0.02, abs=1e-5)

def test_t142_calculo_pd_bureau_com_restritivo():
    """Mesmo com score alto, se houver restritivo, vai para Rating E."""
    pd_faixas = {"CONSUMIDOR_LE_5": {"E": {"min": 0.1100, "max": 1.0000}}}
    registro = {"SCORE_BUREAU": 950.0, "QUANTIDADE_RESTRITIVOS": 2}
    
    res = calcular_pd_final_consumidor_le5(registro, pd_faixas)
    
    assert res["RATING_FINAL"] == "E"
    assert res["PD_METODO"] == "SCORE_BUREAU"