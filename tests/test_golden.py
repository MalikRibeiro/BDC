import os
import sys
import json
from pathlib import Path
from pprint import pprint
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(".", "src")))

from domain.credito.pd_motor import calcular_pd_ajustada
from domain.credito.motor_lgd import calcular_lgd
from domain.credito.motor_garantias import calcular_cobertura_garantias
from common.json import ler_json
import pandas as pd

def carregar_configs():
    base_dir = Path("ENTRADAS/control/configs")
    return {
        "pd_faixas": ler_json(base_dir / "pd_faixas.json"),
        "pd_transform_rules": ler_json(base_dir / "pd_transform_rules.json"),
        "pd_cpura_config": ler_json(base_dir / "pd_cpura_config.json"),
        "score_cpura_config": ler_json(base_dir / "score_cpura_config.json"),
        "pd_zscore_config": ler_json(base_dir / "pd_zscore_config.json"),
    }

def executar_testes():
    configs = carregar_configs()
    print("=== INICIANDO GOLDEN TESTS ===\n")
    
    # 1. Teste de RJ e Manutenção de LGD
    print("1. TESTE RECUPERAÇÃO JUDICIAL")
    reg_rj = {
        "CNPJ": "00000000000000",
        "SEGMENTO_PD": "CPURA",
        "TIPO_COMERCIALIZADORA": "CPURA",
        "RECUPERACAO_JUDICIAL": "Sim",
        "PROBABILIDADE_DEFAULT": 0.05
    }
    res_rj = calcular_pd_ajustada(reg_rj, **configs)
    res_lgd_rj = calcular_lgd("CPURA", cobertura_garantias=0.0)
    print("PD_FINAL:", res_rj.get("PD_FINAL"))
    print("RATING_FINAL:", res_rj.get("RATING_FINAL"))
    print("LGD_LIQUIDA:", res_lgd_rj.get("lgd_liquida"))
    print("--------------------------------------------------\n")

    # 2. Teste de Fallback (Validade DF > 18 meses)
    print("2. TESTE FALLBACK VALIDADE")
    dt_vencida = (datetime.now() - timedelta(days=600)).isoformat()
    reg_validade = {
        "CNPJ": "11111111111111",
        "SEGMENTO_PD": "CPURA",
        "TIPO_COMERCIALIZADORA": "CPURA",
        "DATA_DEMONSTRACAO_FINANCEIRA": dt_vencida,
        "DATA_BUREAU": datetime.now().isoformat(),
        "PD_RISK3": 0.12,
        "RATING_FINAL": "C"
    }
    res_val = calcular_pd_ajustada(reg_validade, **configs)
    print("STATUS:", res_val.get("STATUS_CALCULO_PD"))
    print("PD_FINAL:", res_val.get("PD_FINAL"))
    print("MOTIVO:", res_val.get("MOTIVO_PD_SUB"))
    print("FONTE:", res_val.get("FONTE_PD_SUB"))
    print("VALOR:", res_val.get("VALOR_PD_SUB"))
    print("DATA:", res_val.get("DATA_ACIONAMENTO_PD_SUB"))
    print("--------------------------------------------------\n")

    # 3. Teste Z-Score
    print("3. TESTE Z-SCORE (CPURA)")
    reg_zscore = {
        "CNPJ": "22222222222222",
        "SEGMENTO_PD": "CPURA",
        "TIPO_COMERCIALIZADORA": "CPURA",
        "DATA_DEMONSTRACAO_FINANCEIRA": datetime.now().isoformat(),
        "DATA_BUREAU": datetime.now().isoformat(),
        "LUCROS_ACUMULADOS": 1000,
        "RESERVA_DE_LUCROS": 500,
        "ATIVO_TOTAL": 10000,
        "PASSIVO_CIRCULANTE_FINANCEIRO": 2000,
        "PASSIVO_NAO_CIRCULANTE_FINANCEIRO": 3000,
        "ATIVO_CIRCULANTE": 4000,
        "PASSIVO_CIRCULANTE": 3000,
        "ATIVO_CIRCULANTE_FINANCEIRO": 1500,
        "VENDAS_LIQUIDAS": 12000,
        "FCO": 2000, "ROL": 12000, "ROA": 0.10, "ROE": 0.15,
        "RATING_BOARD_COPEL": "A", "AUDITOR": "PWC", "RATING_BUREAU": "A",
        "RATING_COPEL": "A"
    }
    res_zscore = calcular_pd_ajustada(reg_zscore, **configs)
    print("PD_BASE (Z-Score):", res_zscore.get("PD_BASE"))
    print("PD_FINAL (Interpolada):", res_zscore.get("PD_FINAL"))
    print("--------------------------------------------------\n")

    # 4. Teste CGRUPO Tabela Lookup
    print("4. TESTE CGRUPO (Lookup Tabela)")
    reg_cgrupo = {
        "CNPJ": "33333333333333",
        "SEGMENTO_PD": "CGRUPO",
        "TIPO_COMERCIALIZADORA": "CGRUPO",
        "DATA_DEMONSTRACAO_FINANCEIRA": datetime.now().isoformat(),
        "DATA_RATING_PUBLICO": datetime.now().isoformat(),
        "NOTA_CREDITO": "BB+",
        "AGENCIA": "FITCH"
    }
    res_cgrupo = calcular_pd_ajustada(reg_cgrupo, **configs)
    print("RATING_FINAL:", res_cgrupo.get("RATING_FINAL"))
    print("PD_FINAL:", res_cgrupo.get("PD_FINAL"))
    print("--------------------------------------------------\n")

    # 5. Teste Consumidor LE 5 (Risk3)
    print("5. TESTE CONSUMIDOR LE 5 (Risk3)")
    reg_le5 = {
        "CNPJ": "44444444000144",
        "SEGMENTO_PD": "CONSUMIDOR_LE_5",
        "DATA_DEMONSTRACAO_FINANCEIRA": datetime.now().isoformat(),
        "SCORE_BUREAU": 880,
    }
    res_le5 = calcular_pd_ajustada(reg_le5, **configs)
    print(f"PD_FINAL (Fórmula Risk3): {res_le5.get('PD_FINAL')}")
    print("--------------------------------------------------\n")
    
    # 6. Teste Consumidor GT 5 (t-Student Interp.)
    print("6. TESTE CONSUMIDOR GT 5 (t-Student Interp.)")
    reg_gt5 = {
        "CNPJ": "55555555000155",
        "SEGMENTO_PD": "CONSUMIDOR_GT_5",
        "DATA_DEMONSTRACAO_FINANCEIRA": datetime.now().isoformat(),
        "PROBABILIDADE_DEFAULT": 0.05, 
        "FCO": 200, 
        "ROL": 1000, 
        "ROE": 0.28, 
        "ROA": 0.22, 
        "RATING_BOARD_COPEL": "A",
        "RATING_BUREAU": "A",
        "AUDITOR": "PWC"
    }
    res_gt5 = calcular_pd_ajustada(reg_gt5, **configs)
    print(f"SCORE_TOTAL: {res_gt5.get('SCORE_TOTAL')}")
    print(f"RATING_FINAL: {res_gt5.get('RATING_FINAL')}")
    print(f"PD_FINAL (t-Student): {res_gt5.get('PD_FINAL')}")
    print("--------------------------------------------------\n")

def executar_testes_garantias():
    print("\n=== INICIANDO TESTES DE GARANTIAS ===")
    config_garantias = ler_json(Path("ENTRADAS/control/configs/garantias_config.json"))
    dt_ref = datetime.now().isoformat()
    cnpj_teste = "99999999"
    ead_valor = 200000.0

    garantias_mock = [
        # 1. Vencida
        {"CNPJ_CONTRAPARTE": f"{cnpj_teste}000100", "ID_GARANTIA": "G1", "STATUS": "VIGENTE", "DATA_VENCIMENTO": (datetime.now() - timedelta(days=10)).isoformat(), "TIPO_GARANTIA": "IMOVEL", "VALOR_NOCIONAL": 50000},
        # 2. Garantidor em RJ
        {"CNPJ_CONTRAPARTE": f"{cnpj_teste}000100", "ID_GARANTIA": "G2", "STATUS": "VIGENTE", "TIPO_GARANTIA": "FIANCA BANCARIA", "VALOR_NOCIONAL": 50000, "RECUPERACAO_JUDICIAL_GARANTIDOR": "SIM"},
        # 3. Fiança Tier 1 (0% haircut)
        {"CNPJ_CONTRAPARTE": f"{cnpj_teste}000100", "ID_GARANTIA": "G3", "STATUS": "VIGENTE", "TIPO_GARANTIA": "FIANCA BANCARIA", "VALOR_NOCIONAL": 100000, "RATING_GARANTIDOR": "AAA"},
        # 4. Imóvel (40% haircut)
        {"CNPJ_CONTRAPARTE": f"{cnpj_teste}000100", "ID_GARANTIA": "G4", "STATUS": "VIGENTE", "TIPO_GARANTIA": "IMOVEL HIPOTECA", "VALOR_NOCIONAL": 100000},
        # 5. Fundo de Investimento (10% haircut)
        {"CNPJ_CONTRAPARTE": f"{cnpj_teste}000100", "ID_GARANTIA": "G5", "STATUS": "VIGENTE", "TIPO_GARANTIA": "FUNDO INVESTIMENTO", "VALOR_NOCIONAL": 200000}
    ]
    df_g = pd.DataFrame(garantias_mock)
    
    res = calcular_cobertura_garantias(cnpj_teste, df_g, ead_valor, config_garantias, dt_ref)
    
    print(f"EAD: R$ {ead_valor:,.2f}")
    for g in res["garantias_processadas"]:
        print(f"Garantia {g['ID_GARANTIA']} ({g['TIPO_GARANTIA']}): Nocional = R$ {g['VALOR_NOCIONAL']:,.2f} | Haircut = {g['HAIRCUT_APLICADO']*100}% | Reconhecido = R$ {g['VALOR_RECONHECIDO']:,.2f} | Motivo = {g['MOTIVO_REJEICAO']}")
    
    print(f"\nGARANTIA RECONHECIDA TOTAL: R$ {res['garantia_reconhecida_total']:,.2f}")
    print(f"COBERTURA APLICADA NA EAD: {res['cobertura_aplicada']*100:.2f}%")
    print("-" * 50)

if __name__ == "__main__":
    executar_testes()
    executar_testes_garantias()
