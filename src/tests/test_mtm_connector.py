import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.mtm_connector import fetch_mtm_consolidado

def test_t221_leitura_mtm_local(tmp_path):
    """Valida se o conector de MtM lê o arquivo CSV real, mapeia colunas e normaliza os dados."""
    
    # 1. Simula a pasta de entrada ENTRADAS/mtm
    mtm_dir = tmp_path / "mtm"
    mtm_dir.mkdir(parents=True)
    
    # 2. Cria um arquivo CSV de exemplo com o layout real fornecido
    csv_content = (
        "COD_CONTRATO;CONTRAPARTE;CNPJ;TIPO_CONTRATO;SUBMERCADO;FONTE;PORTFOLIO;DATA_FECHAMENTO;MES_SUPRIMENTO;ENERGIA_MWM;ENERGIA_MWH;PRECO_REAJUSTADO;PRECO_MERCADO;MTM_UNITARIA;MTM_TOTAL;TAXA_DESCONTO;MTM_VPL;DATA_AVALIACAO\n"
        "GERENCIAL 2024-00007552;COPEL COM - GERENCIAL;19125927000186;Compra;S;convencional;direcional;2026-04-14;2027-07-01;4,5;3348,0;155,02;286,41;131,38;439876,53;1,121572;392196,42;2026-08-10\n"
        "GERENCIAL 2024-00007553;OUTRA EMPRESA;123456780001;Venda;S;convencional;direcional;2026-04-14;2027-07-01;2,0;1000,0;100,0;200,0;50,0;-1000,0;1,0;-900,0;2026-08-10"
    )
    
    arquivo_csv = mtm_dir / "mtm_amostra_real.csv"
    arquivo_csv.write_text(csv_content, encoding="utf-8-sig")
    
    # 3. Executa a função do conector apontando para a pasta temporária
    df = fetch_mtm_consolidado(input_dir=mtm_dir)
    
    # 4. Validações Estruturais e de Regra de Negócio
    assert not df.empty, "O DataFrame do MtM não deveria estar vazio."
    
    colunas_esperadas = ["CNPJ", "CONTRATO", "DATA_BASE", "MTM_POSITIVO", "MTM_NEGATIVO", "NOTIONAL"]
    for col in colunas_esperadas:
        assert col in df.columns, f"A coluna obrigatória '{col}' está ausente."
        
    # Valida normalização estrita do CNPJ (14 dígitos, preservando zeros à esquerda)
    assert df.iloc[0]["CNPJ"] == "19125927000186"
    assert df.iloc[1]["CNPJ"] == "00123456780001", "Deveria ter preenchido os zeros à esquerda com zfill(14)."
    
    # Valida mapeamento do contrato
    assert df.iloc[0]["CONTRATO"] == "GERENCIAL 2024-00007552"
    
    # Valida tratamento de MTM Positivo (valores negativos na base original devem virar 0.0 no positivo puro)
    assert df.iloc[0]["MTM_POSITIVO"] == 439876.53
    assert df.iloc[1]["MTM_POSITIVO"] == 0.0, "Valores negativos no MTM_TOTAL devem ser isolados no MTM_POSITIVO."