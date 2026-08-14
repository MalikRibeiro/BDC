import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.salesforce_ingestion_service import ingest_salesforce_data


@pytest.fixture
def mock_context(tmp_path):
    """Fixture que cria o contexto de diretórios temporários para o teste."""
    class MockContext:
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


def criar_mock_excel_salesforce(diretorio_entradas: Path):
    """Cria um arquivo Excel simulando a saída do Power Query do Salesforce."""
    dir_sf = diretorio_entradas / "salesforce"
    dir_sf.mkdir(parents=True, exist_ok=True)
    
    arquivo_sf = dir_sf / "salesforce.xlsx"
    
    # 1. Conta (Com registros duplicados e CNPJ com máscara)
    df_conta = pd.DataFrame([
        {"Id": "A1", "Name": "Empresa 1 Antiga", "CNPJ__c": "05.276.991/0014-78"},
        {"Id": "A1", "Name": "Empresa 1 Atualizada", "CNPJ__c": "05.276.991/0014-78"}, # Deve sobrescrever a anterior
        {"Id": "A2", "Name": "Empresa 2", "CNPJ__c": "11111111000199"}
    ])
    
    # 2. Cotação (C1 ligada na A1, C2 ligada em conta inexistente)
    df_cotacao = pd.DataFrame([
        {"Id": "Q1", "AccountId": "A1", "Cotacao_Aprovada__c": "Sim"},
        {"Id": "Q2", "AccountId": "A99", "Cotacao_Aprovada__c": "Nao"} # Conta órfã
    ])
    
    # 3. Chamado
    df_chamado = pd.DataFrame([
        {"Id": "C1", "AccountId": "A2", "Risk3_Score__c": "85"}
    ])
    
    # 4. Contrato
    df_contrato = pd.DataFrame([
        {"Id": "CT1", "AccountId": "A1", "Status": "Ativo"}
    ])
    
    # Escreve todas as abas no Excel
    with pd.ExcelWriter(arquivo_sf) as writer:
        df_conta.to_excel(writer, sheet_name="Conta", index=False)
        df_cotacao.to_excel(writer, sheet_name="Cotação", index=False)
        df_chamado.to_excel(writer, sheet_name="Chamado", index=False)
        df_contrato.to_excel(writer, sheet_name="Contrato", index=False)


def test_t232_ingestao_salesforce_sucesso(mock_context):
    """Garante a leitura, normalização de CNPJ, deduplicação e enriquecimento das tabelas."""
    # Prepara massa de dados
    criar_mock_excel_salesforce(mock_context.path("entradas"))
    
    # Executa ingestão
    res = ingest_salesforce_data(mock_context)
    
    assert res["status"] == "SUCESSO"
    assert res["linhas_account"] == 2  # Deduplicou 3 linhas para 2 únicas
    assert res["linhas_cotacao"] == 2
    
    # Validações da Camada Silver
    silver_dir = mock_context.path("silver") / "salesforce_silver"
    
    # Validação da Account (Conta)
    df_silver_account = pd.read_parquet(silver_dir / "account" / "salesforce_account.parquet")
    assert len(df_silver_account) == 2
    
    empresa_1 = df_silver_account[df_silver_account["Id"] == "A1"].iloc[0]
    assert empresa_1["Name"] == "Empresa 1 Atualizada", "Deduplicação 'keep=last' falhou."
    assert empresa_1["CNPJ"] == "05276991001478", "Remoção da máscara do CNPJ falhou."
    
    # Validação da Cotação (Enriquecimento de CNPJ)
    df_silver_cotacao = pd.read_parquet(silver_dir / "cotacao" / "salesforce_cotacao.parquet")
    
    cotacao_valida = df_silver_cotacao[df_silver_cotacao["Id"] == "Q1"].iloc[0]
    assert cotacao_valida["CNPJ"] == "05276991001478", "Enriquecimento de CNPJ na Cotação falhou."
    
    cotacao_orfa = df_silver_cotacao[df_silver_cotacao["Id"] == "Q2"].iloc[0]
    assert cotacao_orfa["CNPJ"] == "00000000000000", "Fallback de CNPJ para contas órfãs falhou."


def test_t232_ingestao_salesforce_arquivo_inexistente(mock_context):
    """Garante que a ingestão não quebra se o Power Query não gerar o arquivo no dia."""
    
    # Executa ingestão SEM criar o arquivo Excel antes
    res = ingest_salesforce_data(mock_context)
    
    assert res["status"] == "SEM_DADOS"