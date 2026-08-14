"""
Testes de Arquitetura, Contratos de Schemas e Integridade do BDC.
Valida se as estruturas físicas e os metadados estão estritamente aderentes ao Planejamento.
"""

import sys
import json
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.context import load_context
from common.validation import validate_json_schema
from services.garantias_service import ingest_garantias_data
from services.carga_manual_service import ingest_carga_manual


@pytest.fixture
def project_context():
    """Carrega o contexto real do projeto apontando para as ENTRADAS padrão."""
    root = Path(__file__).resolve().parent.parent.parent
    configs_dir = root / "ENTRADAS" / "configs"
    if not configs_dir.exists():
        pytest.skip("Diretório de configurações de produção não encontrado no ambiente.")
    return load_context(configs_dir)


def test_integridade_schema_carga_manual(project_context):
    """Valida se o schema original de carga manual está íntegro e aceita o template correto."""
    schema_path = project_context.path("control_schemas") / "schema_carga_manual.json"
    assert schema_path.exists(), "O schema_carga_manual.json original deve existir."

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    
    # Instância válida conforme o schema original recuperado
    instancia_valida = {
        "CNPJ": "12345678000199",
        "COMPETENCIA": "202607",
        "CAMPO_ALTERADO": "PATRIMONIO_LIQUIDO",
        "VALOR_APLICADO": 1500000.0,
        "MOTIVO": "Correção de balanço enviada com atraso",
        "EVIDENCIA": "protocolo_123.pdf",
        "SOLICITANTE": "joao.silva",
        "TIPO_EVENTO": "AJUSTE_BALANCO",
        "DATA_REFERENCIA_NEGOCIO": "2026-07-31"
    }

    # Deve passar sem disparar SystemExit
    try:
        validate_json_schema(instancia_valida, schema, "Teste Unitário Carga Manual")
    except SystemExit:
        pytest.fail("O schema rejeitou uma instância estruturalmente válida.")


def test_integridade_servico_garantias_csv(tmp_path):
    """Valida se o serviço de garantias processa o CSV local gerando alertas e fatos sem conector extra."""
    silver_dir = tmp_path / "silver"
    bronze_dir = tmp_path / "bronze"
    log_runner = tmp_path / "LOGS"
    
    for d in [silver_dir, bronze_dir, log_runner]:
        d.mkdir(parents=True, exist_ok=True)

    class MockContext:
        def path(self, key):
            mapping = {
                "silver": silver_dir,
                "bronze": bronze_dir,
                "log_runner": log_runner,
                "entradas": tmp_path / "entradas"
            }
            return mapping.get(key, tmp_path)

    # Simula o arquivo garantias.csv na pasta correta
    garantias_dir = tmp_path / "entradas" / "garantias"
    garantias_dir.mkdir(parents=True, exist_ok=True)
    
    csv_content = (
        "GARANTIA_ID;CNPJ_CONTRAPARTE;VENCIMENTO;PERCENTUAL_COBERTURA;STATUS\n"
        "G01;12345678000199;2025-01-01;0.30;VIGENTE\n" # Vencida + Cobertura baixa
        "G02;98765432000188;2030-12-31;1.00;VIGENTE"
    )
    (garantias_dir / "garantias.csv").write_text(csv_content, encoding="utf-8")

    # Injeta mock direto para isolar o teste do serviço de garantias
    df_mock = pd.read_csv(garantias_dir / "garantias.csv", sep=";")
    res = ingest_garantias_data(MockContext(), df_garantias_externo=df_mock)

    assert res["status"] == "SUCESSO"
    assert res["linhas_processadas"] == 2
    assert res["alertas_gerados"] > 0, "Deveria gerar alertas para garantia vencida e cobertura baixa."

    # Valida persistência física na Silver
    fato_path = silver_dir / "garantias_silver" / "fato_garantia.parquet"
    assert fato_path.exists(), "A fato_garantia.parquet deve ser persistida."


def test_idempotencia_pipeline_files(project_context):
    """Garante que a descoberta e triagem de arquivos respeitam o ecossistema de diretórios."""
    from staging.discovery import discover_pending_excels
    
    pendentes_com = project_context.path("input_fichas_comercializadoras_pendentes")
    pendentes_com.mkdir(parents=True, exist_ok=True)
    
    # Lista arquivos pendentes (deve retornar lista, mesmo que vazia, sem exceções)
    arquivos = discover_pending_excels(pendentes_com)
    assert isinstance(arquivos, list)