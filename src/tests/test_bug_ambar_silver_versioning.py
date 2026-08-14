import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from storage.silver_store import merge_silver_dataset_by_business_key

def test_bug_ambar_resolvido(tmp_path):
    """Valida se múltiplas versões da mesma chave são versionadas sequencialmente sem sobreposição."""
    silver_dir = tmp_path / "silver"
    silver_dir.mkdir(parents=True, exist_ok=True)
    
    business_keys = ["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA"]
    
    # 1. Primeira Ingestão (AMBAR Original)
    lote_1 = [
        {"CNPJ": "123", "DATA_DEMONSTRACAO_FINANCEIRA": "2023-12-31", "PL": 11989, "dt_processamento": "2026-08-14T10:00:00"}
    ]
    merge_silver_dataset_by_business_key(lote_1, silver_dir, "fichas_extraidas", business_keys)
    
    # 2. Segunda Ingestão (AMBAR Corrigida entrando no reprocessamento)
    # Simulamos até o pior cenário: duas correções submetidas no MESMO lote
    lote_2 = [
        {"CNPJ": "123", "DATA_DEMONSTRACAO_FINANCEIRA": "2023-12-31", "PL": 11995, "dt_processamento": "2026-08-14T11:00:00"},
        {"CNPJ": "123", "DATA_DEMONSTRACAO_FINANCEIRA": "2023-12-31", "PL": 12000, "dt_processamento": "2026-08-14T12:00:00"}
    ]
    merge_silver_dataset_by_business_key(lote_2, silver_dir, "fichas_extraidas", business_keys)
    
    # 3. Leitura do Parquet Final
    df_final = pd.read_parquet(silver_dir / "fichas_extraidas.parquet")
    
    # 4. Asserções
    assert len(df_final) == 3, "As 3 linhas (1 original + 2 correções) devem ser preservadas."
    
    versoes = df_final["_VERSAO_REGISTRO"].tolist()
    assert versoes == [1, 2, 3], "As versões devem ser estritamente sequenciais."
    
    status = df_final["_STATUS_REGISTRO"].tolist()
    assert status == ["SUBSTITUIDO", "SUBSTITUIDO", "VIGENTE"], "Apenas a última versão deve estar VIGENTE."
    
    pl_vigente = df_final.loc[df_final["_STATUS_REGISTRO"] == "VIGENTE", "PL"].iloc[0]
    assert pl_vigente == 12000, "A versão VIGENTE deve refletir a correção mais recente."