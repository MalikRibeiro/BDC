import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.denodo_connector import fetch_contratos_competencia

def test_t211_leitura_denodo_local():
    """Garante que o conector offline formata o DataFrame estruturalmente."""
    pasta_entradas = Path(__file__).resolve().parents[2] / "ENTRADAS" / "contratos_denodo"
    
    df = fetch_contratos_competencia("202608", input_dir=pasta_entradas)
    
    assert not df.empty, "O DataFrame não deveria estar vazio para 202608."
    
    colunas_esperadas = ["CNPJ", "CONTRATO", "COMPETENCIA", "VOLUME_MWM", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]
    for col in colunas_esperadas:
        assert col in df.columns, f"Coluna {col} ausente no DataFrame retornado."
        
    # Verifica se o filtro de competência funcionou perfeitamente
    assert (df["COMPETENCIA"] == "202608").all(), "O filtro de competência falhou."
    
    # Verifica tipagem do Volume e CNPJ com as APIs modernas do Pandas
    assert pd.api.types.is_numeric_dtype(df["VOLUME_MWM"]), "VOLUME_MWM não é numérico."
    assert pd.api.types.is_string_dtype(df["CNPJ"]), "CNPJ deveria ser string."