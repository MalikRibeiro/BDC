"""Script utilitário para auditar rejeições de fichas por GATE_ENGINE ou CNPJ."""
import json
from pathlib import Path
from collections import Counter

def main():
    p = Path("LOGS/rejeitados/2026-10-06_rejeicoes.json")
    if not p.exists():
        print(f"Arquivo {p} não encontrado.")
        return

    with open(p, "r", encoding="utf-8") as f:
        rejeicoes = json.load(f)

    print(f"Total de registros de rejeição no log: {len(rejeicoes)}")
    
    # Filtrar arquivos únicos mais recentes
    ultimas_rejeicoes = {}
    for item in rejeicoes:
        arq = item.get("arquivo")
        ultimas_rejeicoes[arq] = item

    print(f"Arquivos únicos rejeitados: {len(ultimas_rejeicoes)}")
    print("=" * 80)
    print("📌 ARQUIVOS REJEITADOS POR 'GATE_ENGINE ausente: CNPJ':")
    print("=" * 80)

    cnpjs_faltando = []
    por_status = Counter()

    for arq, item in sorted(ultimas_rejeicoes.items()):
        status = item.get("status")
        erros = item.get("erros", [])
        por_status[status] += 1
        
        erros_str = " | ".join(str(e) for e in erros)
        if any("CNPJ" in str(e).upper() for e in erros):
            cnpjs_faltando.append((arq, status, erros_str))
            print(f"  • {arq} [{status}] -> {erros_str}")

    print("\n" + "=" * 80)
    print(f"Total de arquivos com pendência de CNPJ: {len(cnpjs_faltando)}")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("📌 DISTRIBUIÇÃO GERAL POR STATUS DE REJEIÇÃO:")
    print("=" * 80)
    for st, count in por_status.most_common():
        print(f"  • {st}: {count} arquivos")

if __name__ == "__main__":
    main()
