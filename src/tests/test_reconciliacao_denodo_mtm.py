import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.reconciliacao_denodo_mtm_service import executar_reconciliacao_denodo_mtm

def test_t223_reconciliacao_denodo_mtm_cenarios_completos(tmp_path):
    """
    Testa a classificação de reconciliação cruzando Denodo x MtM e o disparo de alertas.
    Cobre: CONCILIADO, CONTRATO_SEM_MTM (CTR_001) e MTM_SEM_CONTRATO (CTR_002).
    """
    
    # 1. Estrutura mock de diretórios na Silver
    silver_dir = tmp_path / "SAIDAS" / "silver"
    dir_denodo = silver_dir / "denodo_contratos_silver"
    dir_mtm = silver_dir / "mtm_consolidado_silver"
    dir_denodo.mkdir(parents=True)
    dir_mtm.mkdir(parents=True)

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

    # 2. Criando massa de dados mockada
    
    # Base Denodo:
    # C1 vai cruzar perfeitamente com o MtM.
    # C2 existe só no Denodo (vai gerar CTR_001).
    df_denodo = pd.DataFrame([
        {"CNPJ": "11111111111111", "CONTRATO": "C1"},
        {"CNPJ": "22222222222222", "CONTRATO": "C2"},
    ])
    df_denodo.to_parquet(dir_denodo / "contratos_correntes.parquet", index=False)

    # Base MtM:
    # C1 vai cruzar perfeitamente com o Denodo.
    # C3 existe só no MtM (vai gerar CTR_002).
    df_mtm = pd.DataFrame([
        {
            "CNPJ": "11111111111111", "CONTRATO": "C1", 
            "MTM_POSITIVO_TOTAL": 1000.0, "MTM_NEGATIVO_TOTAL": 0.0, "NOTIONAL_TOTAL": 50.0
        },
        {
            "CNPJ": "33333333333333", "CONTRATO": "C3", 
            "MTM_POSITIVO_TOTAL": 500.0, "MTM_NEGATIVO_TOTAL": 10.0, "NOTIONAL_TOTAL": 20.0
        },
    ])
    df_mtm.to_parquet(dir_mtm / "mtm_agregado_contraparte.parquet", index=False)

    # 3. Executa o serviço de reconciliação
    res = executar_reconciliacao_denodo_mtm(context)

    # 4. Validações do dicionário de resposta
    assert res["status"] == "SUCESSO"
    assert res["linhas_conciliadas"] == 3  # Avaliou C1, C2 e C3 (Outer Join)
    assert res["alertas_gerados_ctr001"] == 1
    assert res["alertas_gerados_ctr002"] == 1

    # 5. Validação da Tabela de Fatos da Reconciliação
    path_reconciliacao = silver_dir / "reconciliacao_contratos_mtm" / "fato_reconciliacao_contrato_mtm.parquet"
    assert path_reconciliacao.exists(), "Tabela de fatos de reconciliação não foi gerada."
    
    df_rec = pd.read_parquet(path_reconciliacao)

    c1_status = df_rec.loc[df_rec["CONTRATO"] == "C1", "STATUS_CONCILIACAO"].iloc[0]
    c2_status = df_rec.loc[df_rec["CONTRATO"] == "C2", "STATUS_CONCILIACAO"].iloc[0]
    c3_status = df_rec.loc[df_rec["CONTRATO"] == "C3", "STATUS_CONCILIACAO"].iloc[0]

    # Valida se a regra de Outer Join inferiu corretamente os domínios de negócio
    assert c1_status == "CONCILIADO", "Contrato presente em ambas as pontas deveria estar CONCILIADO."
    assert c2_status == "CONTRATO_SEM_MTM", "Contrato órfão do Denodo classificado incorretamente."
    assert c3_status == "MTM_SEM_CONTRATO", "Contrato órfão do MtM classificado incorretamente."

    # 6. Validação dos Alertas (CTR_001 e CTR_002)
    path_alertas_dir = silver_dir / "alertas_credito"
    arquivos_alerta = list(path_alertas_dir.glob("*.parquet"))
    assert len(arquivos_alerta) == 1, "Arquivo físico de alertas não foi salvo."

    df_alertas = pd.read_parquet(arquivos_alerta[0])
    
    # Precisam existir exatamente 2 alertas na nossa massa de dados (C2 e C3)
    assert len(df_alertas) == 2 
    codigos_alerta = df_alertas["CODIGO"].tolist()
    
    assert "CTR_001" in codigos_alerta
    assert "CTR_002" in codigos_alerta