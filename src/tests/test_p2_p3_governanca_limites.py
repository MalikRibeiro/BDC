import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.camada_gold_service import exportar_visao_consolidada_gold

@pytest.fixture
def mock_context_gold(tmp_path):
    """Cria arquivos Parquet simulando as camadas Silver e Relational."""
    silver_dir = tmp_path / "silver"
    relational_dir = tmp_path / "relational_facts"
    relational_configs = tmp_path / "relational_configs"
    relational_dims = tmp_path / "relational_dimensions"
    
    for d in [silver_dir, relational_dir, relational_configs, relational_dims]:
        d.mkdir(parents=True, exist_ok=True)
        
    (silver_dir / "denodo_contratos_silver").mkdir(exist_ok=True)

    # 1. Contratos (Denodo)
    df_contratos = pd.DataFrame([
        {"CNPJ": "11111111111111", "CONTRATO": "C1", "VIGENCIA_INICIO": "2020-01-01", "VIGENCIA_FIM": "2030-01-01", "VOLUME_CONTRATADO_MENSAL_MWM": 10.0, "STATUS": "ATIVO"},
        {"CNPJ": "22222222222222", "CONTRATO": "C2", "VIGENCIA_INICIO": "2020-01-01", "VIGENCIA_FIM": "2030-01-01", "VOLUME_CONTRATADO_MENSAL_MWM": 2.0, "STATUS": "ATIVO"}, 
        {"CNPJ": "33333333333333", "CONTRATO": "C3", "VIGENCIA_INICIO": "2020-01-01", "VIGENCIA_FIM": "2030-01-01", "VOLUME_CONTRATADO_MENSAL_MWM": 15.0, "STATUS": "ATIVO"} 
    ])
    df_contratos.to_parquet(silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet")

    # 2. Enquadramento de Volume
    df_enquadramento = pd.DataFrame([
        {"CNPJ": "11111111111111", "VOLUME_ENQUADRAMENTO_MWM": 10.0, "POSSUI_PELO_MENOS_5_MWM": True},
        {"CNPJ": "22222222222222", "VOLUME_ENQUADRAMENTO_MWM": 2.0, "POSSUI_PELO_MENOS_5_MWM": False}
    ])
    df_enquadramento.to_parquet(relational_configs / "enquadramento_consumidores_LATEST.parquet")

    # 3. Análises (Fichas Extraídas)
    df_analises = pd.DataFrame([
        {"CNPJ": "33333333333333", "DATA_ANALISE": "2026-08-01", "DATA_BALANCO_USADO": "2025-12-31", "RATING_FINAL": "A", "PD_FINAL": 0.005, "PATRIMONIO_LIQUIDO": 500000.0}
    ])
    df_analises.to_parquet(relational_dir / "fato_analise_credito.parquet")

    # 4. Dimensão Contraparte CORRIGIDA COM SITUACAO_CADASTRAL
    df_dim = pd.DataFrame([
        {"CNPJ": "11111111111111", "SEGMENTO_METODOLOGICO": "CONSUMIDOR_GT_5", "SITUACAO_CADASTRAL": "ATIVA"},
        {"CNPJ": "22222222222222", "SEGMENTO_METODOLOGICO": "CONSUMIDOR_LE_5", "SITUACAO_CADASTRAL": "BAIXADA"},
        {"CNPJ": "33333333333333", "SEGMENTO_METODOLOGICO": "CPURA", "SITUACAO_CADASTRAL": "ATIVA"}
    ])
    df_dim.to_parquet(relational_dims / "dim_contraparte.parquet")

    class MockContext:
        def path(self, key):
            mapping = {
                "silver": silver_dir, "relational_facts": relational_dir, 
                "relational_configs": relational_configs, "relational_dimensions": relational_dims,
                "gold": tmp_path / "gold"
            }
            return mapping.get(key, tmp_path)
    
    return MockContext()

def test_p2_governanca_ausencia_df(mock_context_gold):
    """PRIORIDADE 2: Valida se o sistema trata corretamente a ausência de DF baseando-se no Enquadramento."""
    res = exportar_visao_consolidada_gold(mock_context_gold)
    assert res["status"] == "SUCESSO"
    
    df_gold = pd.read_parquet(mock_context_gold.path("gold") / "visao_operacional_negocio" / "Visao_Operacional_BDC_LATEST.parquet")
    
    cons_gt5 = df_gold[df_gold["CNPJ"] == "11111111111111"].iloc[0]
    assert cons_gt5["SITUACAO_DF"] == "NAO_RECEBIDA", "> 5MWm sem ficha deve marcar DF como não recebida."
    assert cons_gt5["SITUACAO_ANALISE"] == "IRREGULAR", "> 5MWm sem ficha está a descoberto."
    
    cons_le5 = df_gold[df_gold["CNPJ"] == "22222222222222"].iloc[0]
    assert cons_le5["SITUACAO_DF"] == "NAO_APLICAVEL", "< 5MWm não exige DF (Usa Bureau)."

def test_p3_geracao_arquivo_limites(mock_context_gold):
    """PRIORIDADE 3: Valida se o Arquivo de Interface de Limites é gerado fisicamente na Gold e com os campos corretos."""
    exportar_visao_consolidada_gold(mock_context_gold)
    
    limites_path = mock_context_gold.path("gold") / "visao_operacional_negocio" / "Interface_Limites_BDC_LATEST.xlsx"
    assert limites_path.exists(), "O arquivo Excel de Interface de Limites deve ser gerado."
    
    df_limites = pd.read_excel(limites_path)
    colunas_obrigatorias = ["CNPJ", "SEGMENTO_METODOLOGICO", "PATRIMONIO_LIQUIDO", "RATING", "PD", "DATA_DF"]
    
    for col in colunas_obrigatorias:
        assert col in df_limites.columns, f"Coluna {col} faltando no Arquivo de Limites."