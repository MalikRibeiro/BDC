import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.receita_connector import consultar_cnpj_brasilapi, fetch_receita_data_batch
from services.receita_ingestion_service import ingest_receita_data


class MockContext:
    def __init__(self, root: Path):
        self.root = root

    def path(self, key: str) -> Path:
        mapping = {
            "entradas": self.root / "ENTRADAS",
            "bronze": self.root / "SAIDAS" / "bronze",
            "silver": self.root / "SAIDAS" / "silver",
            "log_runner": self.root / "LOGS" / "runner",
        }
        return mapping[key]


def _write_cnpj_list_file(base_dir: Path) -> Path:
    receita_dir = base_dir / "receita"
    receita_dir.mkdir(parents=True, exist_ok=True)
    csv_path = receita_dir / "lista_cnpjs.csv"
    pd.DataFrame({"CNPJ": ["12.345.678/0001-99"]}).to_csv(csv_path, index=False)
    return csv_path


def test_consulta_brasilapi_sucesso(monkeypatch):
    class DummyResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {
                "cnpj": "12345678000199",
                "data_abertura": "2020-01-15",
                "cnae_fiscal": "6201500",
                "natureza_juridica": "213-5 - SOCIEDADE EMPRESARIA LIMITADA",
                "descricao_situacao_cadastral": "ATIVA",
                "nome_fantasia": "Empresa Teste",
            }

    def fake_get(*args, **kwargs):
        return DummyResponse()

    monkeypatch.setattr("services.receita_connector.requests.get", fake_get)

    resultado = consultar_cnpj_brasilapi("12.345.678/0001-99")

    assert resultado["CNPJ"] == "12345678000199"
    assert resultado["SITUACAO_CADASTRAL"] == "ATIVA"
    assert resultado["DATA_ABERTURA"] == "2020-01-15"
    assert resultado["CNAE_PRINCIPAL"] == "6201500"
    assert resultado["NATUREZA_JURIDICA"] == "213-5 - SOCIEDADE EMPRESARIA LIMITADA"
    assert resultado["DATA_CONSULTA"]


def test_cache_local_receita(tmp_path, monkeypatch):
    entradas = tmp_path / "ENTRADAS" / "receita" / "cache"
    entradas.mkdir(parents=True, exist_ok=True)
    cache_path = entradas / "receita_cache.json"
    cache_path.write_text(
        json.dumps(
            {
                "12345678000199": {
                    "CNPJ": "12345678000199",
                    "SITUACAO_CADASTRAL": "ATIVA",
                    "DATA_ABERTURA": "2023-01-01",
                    "CNAE_PRINCIPAL": "6201500",
                    "NATUREZA_JURIDICA": "213-5",
                    "DATA_CONSULTA": "2026-08-11T12:00:00",
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    context = MockContext(tmp_path)
    called = {"value": False}

    def fake_get(*args, **kwargs):
        called["value"] = True
        raise AssertionError("Requisição HTTP não deveria ocorrer quando o CNPJ já está em cache valido")

    monkeypatch.setattr("services.receita_connector.requests.get", fake_get)

    df = fetch_receita_data_batch(["12.345.678/0001-99"], context)

    assert called["value"] is False
    assert len(df) == 1
    assert df.iloc[0]["CNPJ"] == "12345678000199"


def test_geracao_alerta_cad001(tmp_path, monkeypatch):
    context = MockContext(tmp_path)
    _write_cnpj_list_file(context.path("entradas"))

    df = pd.DataFrame(
        [
            {
                "CNPJ": "12345678000199",
                "SITUACAO_CADASTRAL": "BAIXADA",
                "DATA_ABERTURA": "2020-01-15",
                "CNAE_PRINCIPAL": "6201500",
                "NATUREZA_JURIDICA": "213-5 - SOCIEDADE EMPRESARIA LIMITADA",
                "DATA_CONSULTA": "2026-08-11T10:00:00",
            }
        ]
    )

    monkeypatch.setattr("services.receita_ingestion_service.fetch_receita_data_batch", lambda cnpjs, context: df)

    resultado = ingest_receita_data(context)

    assert resultado["status"] == "SUCESSO"
    assert resultado["alertas_gerados_cad001"] == 1

    alertas_dir = context.path("silver") / "alertas_credito"
    arquivos = sorted(alertas_dir.glob("*.csv"))
    assert arquivos, "Arquivo de alertas não foi persistido."

    df_alertas = pd.read_csv(arquivos[0])
    assert df_alertas.iloc[0]["CODIGO"] == "CAD_001"
    assert df_alertas.iloc[0]["CNPJ"] == "12345678000199"
