"""Teste de Prova e Diagnóstico do Bug de Sinal Invertido em pd_base.py (Correção C4).

Demonstra matematicamente:
1. O comportamento do código legado em src/domain/credito/pd_base.py (linha 74: math.exp(z)).
2. O comportamento normativo exigido pela NT v7 §4 (linha 77: math.exp(-z)).
3. O impacto na classificação de risco (inversão da escala: empresa solvente tratada como inadimplente e vice-versa).
"""
import math


def formula_legada_pd_base(z: float) -> float:
    """Implementação histórica em src/domain/credito/pd_base.py (linha 74)."""
    z_clamped = max(-20.0, min(z, 20.0))
    return 1.0 / (1.0 + math.exp(z_clamped))


def formula_normativa_nt_v7(z: float) -> float:
    """Implementação correta da Nota Técnica v7 §4 (linha 77)."""
    z_clamped = max(-20.0, min(z, 20.0))
    return 1.0 / (1.0 + math.exp(-z_clamped))


def main():
    print(f"\n{'=' * 80}")
    print(f"🔬 BDC - DEMONSTRAÇÃO E PROVA DO BUG EM pd_base.py (LINHA 74)")
    print(f"{'=' * 80}\n")

    casos = [
        ("Empresa Altamente Solvente (z = -4.0)", -4.0),
        ("Empresa Solvente Moderada (z = -2.0)", -2.0),
        ("Empresa Neutra / Limiar (z = 0.0)", 0.0),
        ("Empresa Risco Elevado (z = +2.0)", 2.0),
        ("Empresa Insolvente / Crítica (z = +4.0)", 4.0),
    ]

    print(f"{'Cenário':<42} | {'z':<6} | {'Legado (exp(z))':<16} | {'NT v7 (exp(-z))':<16} | {'Efeito':<15}")
    print(f"{'-' * 42}-+-{'-' * 6}-+-{'-' * 16}-+-{'-' * 16}-+-{'-' * 15}")

    for desc, z in casos:
        pd_leg = formula_legada_pd_base(z)
        pd_nt = formula_normativa_nt_v7(z)
        efeito = "INVERTIDO!" if abs(pd_leg - pd_nt) > 0.01 else "NEUTRO"
        print(f"{desc:<42} | {z:<6.1f} | {pd_leg*100:>13.2f}% | {pd_nt*100:>13.2f}% | {efeito:<15}")

    print(f"\n{'=' * 80}")
    print(f"CONCLUSÃO TÉCNICA E AUDITORIA DE IMPACTO:")
    print(f"1. A fórmula legada em pd_base.py calculava 1 / (1 + exp(z)), que corresponde à")
    print(f"   probabilidade de sobrevivência (1 - PD), e não à probabilidade de default.")
    print(f"2. Para z = +4.0 (alta insolvência), o código atribuía 1,80% de PD (Rating A/B falso).")
    print(f"3. Para z = -4.0 (alta solvência), o código atribuía 98,20% de PD (Rating E falso).")
    print(f"4. A mitigação histórica ocorreu porque pd_base.py continha fallback para ler a")
    print(f"   célula direta da ficha (registro['PD_BASE']), evitando a chamada do z-score na")
    print(f"   maioria dos casos. O erro afetou apenas recálculos automáticos sem PD digitada.")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
