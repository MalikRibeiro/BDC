import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.enquadramento_service import calcular_enquadramento_consumidor

def test_t213_calculo_volume_enquadramento(tmp_path):
    """Valida se o sistema calcula corretamente o maior volume mensal e o corte de 5 MWm."""
    
    silver_dir = tmp_path / "SAIDAS" / "silver" / "denodo_contratos_padronizados"
    silver_dir.mkdir(parents=True)
    
    dados_mock = pd.DataFrame([
        {"CNPJ": "11111111000111", "CONTRATO": "C1", "COMPETENCIA": "202608", "VOLUME_MWM": 4.0, "STATUS": "Ativo"},
        {"CNPJ": "11111111000111", "CONTRATO": "C2", "COMPETENCIA": "202608", "VOLUME_MWM": 2.0, "STATUS": "Ativo"},
        {"CNPJ": "22222222000222", "CONTRATO": "C3", "COMPETENCIA": "202608", "VOLUME_MWM": 2.5, "STATUS": "Ativo"},
    ])
    
    competencia = "202608"
    dados_mock.to_parquet(silver_dir / f"contratos_correntes_{competencia}.parquet", index=False)
    
    class MockContext:
        def path(self, key):
            if key == "silver":
                return tmp_path / "SAIDAS" / "silver"
            if key == "relational_configs":
                return tmp_path / "SAIDAS" / "relational" / "configs"
            return tmp_path

    df_res = calcular_enquadramento_consumidor(competencia, MockContext())
    
    cons_a = df_res[df_res["CNPJ"] == "11111111000111"].iloc[0]
    cons_b = df_res[df_res["CNPJ"] == "22222222000222"].iloc[0]
    
    assert cons_a["VOLUME_ENQUADRAMENTO_MWM"] == 6.0
    assert bool(cons_a["POSSUI_PELO_MENOS_5_MWM"]) is True  # Conversão explícita para bool nativo
    
    assert cons_b["VOLUME_ENQUADRAMENTO_MWM"] == 2.5
    assert bool(cons_b["POSSUI_PELO_MENOS_5_MWM"]) is False