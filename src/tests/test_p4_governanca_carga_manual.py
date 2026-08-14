import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.carga_manual_service import ingest_carga_manual
from services.override_service import processar_solicitacao_override

@pytest.fixture
def mock_context_gov(tmp_path):
    entradas_dir = tmp_path / "ENTRADAS"
    (entradas_dir / "atualizacoes_manuais" / "pendentes").mkdir(parents=True, exist_ok=True)
    (entradas_dir / "overrides" / "pendentes").mkdir(parents=True, exist_ok=True)
    
    silver_dir = tmp_path / "SAIDAS" / "silver"
    control_schemas = tmp_path / "ENTRADAS" / "control" / "schemas"
    control_schemas.mkdir(parents=True, exist_ok=True)
    
    import json
    schema_path = control_schemas / "schema_carga_manual.json"
    schema_path.write_text(json.dumps({
        "type": "object",
        "required": ["CNPJ", "TIPO_EVENTO"]
    }))
    
    class MockContext:
        def path(self, key):
            mapping = {
                "entradas": entradas_dir,
                "silver": silver_dir,
                "control_schemas": control_schemas
            }
            return mapping.get(key, tmp_path)
            
    return MockContext()

def test_p4_ingest_carga_manual(mock_context_gov):
    """PRIORIDADE 4: Valida fluxo de pastas físicas para a Carga Manual."""
    entradas_dir = mock_context_gov.path("entradas")
    csv_path = entradas_dir / "atualizacoes_manuais" / "pendentes" / "carga_teste.csv"
    df = pd.DataFrame([{"CNPJ": "111", "TIPO_EVENTO": "AJUSTE_BALANCO"}])
    df.to_csv(csv_path, sep=";", index=False)
    
    res = ingest_carga_manual(mock_context_gov)
    assert res["status"] == "SUCESSO"
    assert res["eventos_processados"] == 1
    assert not csv_path.exists(), "O arquivo deve ser movido para as pastas de controle."
    
def test_p4_processar_solicitacao_override(mock_context_gov):
    """PRIORIDADE 4: Valida bloqueios de Alçada e expiração via fluxo físico para Overrides."""
    entradas_dir = mock_context_gov.path("entradas")
    csv_path = entradas_dir / "overrides" / "pendentes" / "override_teste.csv"
    df = pd.DataFrame([{
        "CNPJ": "222", "TIPO_OVERRIDE": "RATING", "VALOR_ANTES": "B", "VALOR_DEPOIS": "A",
        "JUSTIFICATIVA": "Melhora no balanço", "EVIDENCIA": "Ata X", "SOLICITANTE": "USER1",
        "APROVADOR": "USER2", "DATA_EXPIRACAO": "2030-01-01"
    }])
    df.to_csv(csv_path, sep=";", index=False)
    
    res = processar_solicitacao_override(mock_context_gov)
    assert res["status"] == "SUCESSO"
    assert res["processados"] == 1
    assert not csv_path.exists(), "O arquivo deve ser movido após o processamento."