"""Script utilitário para execução direta das camadas corrigidas e auditoria imediata."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
SCRATCH = ROOT / "scratch"
if str(SCRATCH) not in sys.path:
    sys.path.insert(0, str(SCRATCH))

from app.bootstrap import carregar_contexto
from relational.facts.fato_analise_credito import processar_fato_analise_credito
from gold.servico_carteira_contratos import processar_visao_contratos_risco
from scratch_auditoria_carteira import auditar_visao_carteira

def main():
    import time
    t0 = time.time()
    print("=" * 60)
    print("EXECUTANDO PROCESSAMENTO DA FATO E GOLD DE CARTEIRA")
    print("=" * 60)
    
    context = carregar_contexto(ROOT / "ENTRADAS" / "configs")
    
    print("\n[1/2] Processando Fato Análise de Crédito com Bureau Risk3...")
    t_f0 = time.time()
    res_fato = processar_fato_analise_credito(context)
    print(f"-> Fato concluída com sucesso em {time.time() - t_f0:.1f}s: {res_fato}")
    
    print("\n[2/2] Processando Visão Carteira Contratos (As-Of Join e Deduplicação)...")
    t_g0 = time.time()
    res_gold = processar_visao_contratos_risco(context)
    print(f"-> Gold Carteira concluída com sucesso em {time.time() - t_g0:.1f}s: {res_gold}")
    
    print("\n" + "=" * 60)
    print("EXECUTANDO AUDITORIA FORENSE AUTOMÁTICA")
    print("=" * 60)
    auditar_visao_carteira()
    print(f"\nTempo total de execução: {time.time() - t0:.1f}s")

if __name__ == "__main__":
    main()
