import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.mtm_ingestion_service import ingest_mtm_data, MtmReconciliationError


@pytest.fixture
def mock_context_factory(tmp_path):
    """Factory para criar um MockContext com configurações de tolerância customizáveis."""
    def _create_mock_context(tolerancia=0.01):
        class MockContext:
            def __init__(self):
                self.config = {
                    "reconciliacao_mtm": {
                        "tolerancia_absoluta": tolerancia
                    }
                }

            def path(self, key):
                if key == "entradas":
                    return tmp_path / "ENTRADAS"
                if key == "bronze":
                    return tmp_path / "SAIDAS" / "bronze"
                if key == "silver":
                    return tmp_path / "SAIDAS" / "silver"
                if key == "log_runner":
                    p = tmp_path / "LOGS"
                    p.mkdir(parents=True, exist_ok=True)
                    return p
                return tmp_path
        return MockContext()
    return _create_mock_context


@pytest.mark.parametrize("tolerancia_teste", [0.01, 0.0])
def test_t222_ingestao_e_reconciliacao_mtm_sucesso(tmp_path, mock_context_factory, tolerancia_teste):
    """Garante que a ingestão cria a cópia na Bronze e agrega na Silver com reconciliação."""
    
    # 1. Estrutura mock de diretórios
    entradas_mtm = tmp_path / "ENTRADAS" / "mtm"
    entradas_mtm.mkdir(parents=True)
    
    # 2. CSV mock com MTM positivo, negativo e Notional (via ENERGIA_MWM)
    csv_content = (
        "COD_CONTRATO;CNPJ;MTM_TOTAL;DATA_AVALIACAO;ENERGIA_MWM\n"
        "C1;12345678000199;1000,50;2026-08-10;10\n"
        "C2;12345678000199;2000,50;2026-08-10;20\n"
        "C3;98765432000188;500,00;2026-08-10;5\n"
        "C4;12345678000199;-300,25;2026-08-10;3"  # Linha com MTM negativo
    )
    (entradas_mtm / "mtm_amostra.csv").write_text(csv_content, encoding="utf-8")
    
    # 3. Executa a ingestão com a tolerância parametrizada
    mock_context = mock_context_factory(tolerancia=tolerancia_teste)
    res = ingest_mtm_data(mock_context)
    
    # 4. Validações do resultado
    assert res["status"] == "SUCESSO"
    assert res["linhas_processadas"] == 4
    assert res["contrapartes_consolidadas"] == 2
    
    # Valida presença do snapshot na Bronze
    bronze_dir = tmp_path / "SAIDAS" / "bronze" / "snapshots_fontes" / "mtm"
    bronze_files = list(bronze_dir.glob("*.csv"))
    assert len(bronze_files) == 1, "Snapshot bruto deveria estar salvo na Bronze."
    
    # Valida arquivo de saída Silver
    silver_file = tmp_path / "SAIDAS" / "silver" / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
    assert silver_file.exists(), "Arquivo Parquet Silver deveria ter sido gerado."
    
    df_silver = pd.read_parquet(silver_file)
    assert not df_silver.empty
    
    # Valida agregação da EMPRESA A (CNPJ 12345678000199)
    empresa_a = df_silver[df_silver["CNPJ"] == "12345678000199"].iloc[0]
    # MTM Positivo: C1 (1000.50) + C2 (2000.50) = 3001.00
    assert empresa_a["MTM_POSITIVO_TOTAL"] == pytest.approx(3001.00)
    # MTM Negativo: C4 (-300.25)
    assert empresa_a["MTM_NEGATIVO_TOTAL"] == pytest.approx(300.25)
    # Notional: C1 (10) + C2 (20) + C4 (3) = 33
    assert empresa_a["NOTIONAL_TOTAL"] == pytest.approx(33.0)

    # Valida agregação da EMPRESA B (CNPJ 98765432000188)
    empresa_b = df_silver[df_silver["CNPJ"] == "98765432000188"].iloc[0]
    assert empresa_b["MTM_POSITIVO_TOTAL"] == pytest.approx(500.00)
    assert empresa_b["MTM_NEGATIVO_TOTAL"] == pytest.approx(0.0)
    assert empresa_b["NOTIONAL_TOTAL"] == pytest.approx(5.0)


@pytest.mark.parametrize(
    "campo_divergente, valor_mock_divergente, mensagem_erro_esperada",
    [
        ("MTM_POSITIVO_TOTAL", 1000.00, "Divergência de reconciliação no MTM Positivo Total"),
        ("MTM_NEGATIVO_TOTAL", 200.00, "Divergência de reconciliação no MTM Negativo Total"),
        ("NOTIONAL_TOTAL", 49.0, "Divergência de reconciliação no Notional Total"),
    ],
)
def test_t222_falha_reconciliacao_mtm(
    tmp_path, mock_context_factory, monkeypatch, campo_divergente, valor_mock_divergente, mensagem_erro_esperada
):
    """Valida se MtmReconciliationError é levantada quando a reconciliação falha."""
    # 1. Prepara o ambiente como no teste de sucesso
    entradas_mtm = tmp_path / "ENTRADAS" / "mtm"
    entradas_mtm.mkdir(parents=True)
    # CSV com valores para MTM positivo, negativo e notional
    csv_content = "COD_CONTRATO;CNPJ;MTM_TOTAL;ENERGIA_MWM\nC1;12345678000199;1000,50;50\nC2;12345678000199;-200,25;0"
    (entradas_mtm / "mtm_amostra.csv").write_text(csv_content, encoding="utf-8")

    mock_context = mock_context_factory(tolerancia=0.01)

    # 2. Usa monkeypatch para simular uma falha na agregação
    # O conector lê os valores originais, mas forçamos a agregação a produzir um valor diferente
    # para o campo parametrizado.
    mock_record = {
        "CNPJ": "12345678000199",
        "DATA_BASE": "2026-08-10",
        "MTM_POSITIVO_TOTAL": 1000.50,
        "MTM_NEGATIVO_TOTAL": 200.25,
        "NOTIONAL_TOTAL": 50.0,
    }
    mock_record[campo_divergente] = valor_mock_divergente
    df_agregado_mock = pd.DataFrame([mock_record])

    # Mocka o método 'agg' do GroupBy para retornar nosso DataFrame com divergência
    monkeypatch.setattr(pd.core.groupby.generic.DataFrameGroupBy, "agg", lambda *args, **kwargs: df_agregado_mock)

    # 3. Executa e valida se a exceção correta é levantada
    with pytest.raises(MtmReconciliationError) as excinfo:
        ingest_mtm_data(mock_context)

    assert mensagem_erro_esperada in str(excinfo.value)