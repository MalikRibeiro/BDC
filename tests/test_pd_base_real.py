"""Teste unitário executando a função real de src/domain/credito/pd_base.py.

Demonstra o comportamento real de calcular_pd_base() para z = -4.0, 0.0, +4.0
sem reimplementar a fórmula, importando o código real do repositório.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from domain.credito.pd_base import calcular_pd_base


def main() -> int:
    print(f"\n{'=' * 85}")
    print("🔬 BDC - EXECUÇÃO REAL DE src/domain/credito/pd_base.py (LINHAS 60-80)")
    print(f"{'=' * 85}\n")

    # Registro com balanço não-nulo para passar pelas validações de entrada (linhas 51-54)
    # ATIVO_TOTAL = 100.0, VENDAS_LIQUIDAS = 100.0, demais = 0.0
    registro_base = {
        "CNPJ": "00000000000000",
        "ATIVO_TOTAL": 100.0,
        "VENDAS_LIQUIDAS": 100.0,
        "LUCROS_ACUMULADOS": 0.0,
        "RESERVA_DE_LUCROS": 0.0,
        "PASSIVO_CIRCULANTE_FINANCEIRO": 0.0,
        "PASSIVO_NAO_CIRCULANTE_FINANCEIRO": 0.0,
        "ATIVO_CIRCULANTE": 0.0,
        "PASSIVO_CIRCULANTE": 0.0,
        "ATIVO_CIRCULANTE_FINANCEIRO": 0.0,
        # PD_BASE não informado para forçar o recálculo via Z-score
    }

    casos_z = [
        ("Empresa Altamente Solvente", -4.0, 0.017986, "PD baixa (< 2%), Solvente (Conforme NT v7)"),
        ("Empresa Neutra / Limiar", 0.0, 0.500000, "Ponto neutro 50% (Conforme NT v7)"),
        ("Empresa Crítica / Insolvente", 4.0, 0.982014, "PD alta (> 98%), Insolvente (Conforme NT v7)"),
    ]

    print(f"{'Cenário':<30} | {'z':<6} | {'PD Calculada':<15} | {'PD Esperada':<15} | {'Status'}")
    print(f"{'-' * 30}-+-{'-' * 6}-+-{'-' * 15}-+-{'-' * 15}-+-{'-' * 12}")

    erros = 0
    for desc, z_val, pd_esp, obs in casos_z:
        config_z = {
            "intercept": z_val,
            "coef_x12": 0.0,
            "coef_x16": 0.0,
            "coef_x19": 0.0,
            "coef_x22": 0.0,
        }
        pd_retornada = calcular_pd_base(
            registro=registro_base,
            segmento_pd="CPURA",
            pd_zscore_config=config_z,
        )

        delta = abs(pd_retornada - pd_esp) if pd_retornada is not None else 1.0
        status = "CORRETO" if delta < 1e-4 else "FALHA"
        if status == "FALHA":
            erros += 1

        pd_str = f"{pd_retornada * 100:.4f}%" if pd_retornada is not None else "ERRO/NULO"
        esp_str = f"{pd_esp * 100:.4f}%"
        print(f"{desc:<30} | {z_val:<6.1f} | {pd_str:<15} | {esp_str:<15} | {status} ({obs})")

    print(f"\n{'=' * 85}")
    if erros == 0:
        print("✅ SUCESSO: A função calcular_pd_base() está 100% conforme a Nota Técnica v7 §4.")
        print("   - z = -4.0 (solvente)   -> PD = 1.7986%")
        print("   - z =  0.0 (limiar)     -> PD = 50.0000%")
        print("   - z = +4.0 (insolvente) -> PD = 98.2014%")
    else:
        print(f"❌ FALHA: {erros} casos divergiram da fórmula esperada.")
    print(f"{'=' * 85}\n")
    return erros


if __name__ == "__main__":
    sys.exit(main())
