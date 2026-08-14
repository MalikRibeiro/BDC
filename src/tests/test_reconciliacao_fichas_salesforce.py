import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.reconciliacao_fichas_salesforce_service import executar_reconciliacao_fichas_salesforce


def test_t232_reconciliacao_fichas_salesforce_cenarios(tmp_path):
    """
    Testa o cruzamento entre Fichas e Salesforce.
    Cobre a geração do alerta CAD_002 para divergência de Grupo Econômico 
    e o armazenamento de ratings concorrentes.
    """
    
    # 1. Estrutura mock
    silver_dir = tmp_path / "SAIDAS" / "silver"
    dir_fichas_com = silver_dir / "fichas_comercializadoras"
    dir_sf_account = silver_dir / "salesforce_silver" / "account"
    
    dir_fichas_com.mkdir(parents=True)
    dir_sf_account.mkdir(parents=True)

    class MockContext:
        def path(self, key):
            if key == "silver":
                return silver_dir
            if key == "log_runner":
                p = tmp_path / "LOGS"
                p.mkdir(parents=True, exist_ok=True)
                return p
            return tmp_path

    context = MockContext()

    # 2. Mock de Fichas
    # C1: Divergência de grupo. C2: Consistente.
    df_fichas = pd.DataFrame([
        {"CNPJ": "11111111111111", "GRUPO_ECONOMICO": "Grupo A", "RATING": "A"},
        {"CNPJ": "22222222222222", "GRUPO_ECONOMICO": "Grupo B", "RATING": "B+"},
    ])
    df_fichas.to_parquet(dir_fichas_com / "fichas_padronizadas.parquet", index=False)

    # 3. Mock de Salesforce (Account)
    df_sf = pd.DataFrame([
        {"CNPJ": "11111111111111", "Grupo_economico__c": "Grupo Diferente", "Risk3_Rating__c": "A-"},
        {"CNPJ": "22222222222222", "Grupo_economico__c": "Grupo B", "Risk3_Rating__c": "B+"},
        {"CNPJ": "33333333333333", "Grupo_economico__c": "Grupo C", "Risk3_Rating__c": "C"},
    ])
    df_sf.to_parquet(dir_sf_account / "salesforce_account.parquet", index=False)

    # 4. Executa Reconciliação
    res = executar_reconciliacao_fichas_salesforce(context)

    # 5. Asserções
    assert res["status"] == "SUCESSO"
    assert res["linhas_conciliadas"] == 2  # Somente 111... e 222... (Inner join)
    assert res["alertas_gerados_cad002"] == 1  # Divergência no 111...
    
    # Valida arquivo de alertas
    path_alertas_dir = silver_dir / "alertas_credito"
    arquivos_alerta = list(path_alertas_dir.glob("*.parquet"))
    assert len(arquivos_alerta) == 1
    
    df_alertas = pd.read_parquet(arquivos_alerta[0])
    assert df_alertas["CODIGO"].iloc[0] == "CAD_002"
    assert df_alertas["CNPJ"].iloc[0] == "11111111111111"
    
    # Valida armazenamento de Rating Concorrente
    path_ratings = silver_dir / "reconciliacao_fichas_salesforce" / "fato_concorrencia_rating.parquet"
    assert path_ratings.exists()
    
    df_rating = pd.read_parquet(path_ratings)
    assert len(df_rating) == 2
    assert "RATING_FICHA" in df_rating.columns
    assert "RATING_SF" in df_rating.columns