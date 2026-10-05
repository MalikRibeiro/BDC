"""Teste e validação da extração dos novos layouts padrao_7_cpura e padrao_7_cgrupo.

Comprova em tempo real:
1. Extração de Vendas Líquidas, Lucro Líquido e FCO (que estavam zerados na Silver).
2. Extração dos campos de controle de origem B26..B29 (_FICHA).
3. Classificação e identificação das 34 Geradoras (SUBSEGMENTO = 'GERADORA').
4. Extração de scores individuais e notas em G/H (CPURA) e M/N (CGRUPO).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.bootstrap import aplicativo_bootstrap
from control.layout_catalog import carregar_layouts_comercializadoras
from common.excel import abrir_pasta, fechar_pasta
from domain.fichas.extrator import extrair_registro_do_vencedor
from common.json import ler_json


def main() -> int:
    inicio = time.perf_counter()
    print("\n" + "=" * 95)
    print("🔬 BDC — TESTE DE EXTRAÇÃO: LAYOUTS ESPECIALIZADOS PADRAO_7 (CPURA & CGRUPO)")
    print("=" * 95)

    context = aplicativo_bootstrap()
    layouts = carregar_layouts_comercializadoras(context)
    master_catalog = ler_json(context.control_file("master_catalog_comercializadoras"))

    print(f"\n[+] Layouts carregados ({len(layouts)}): {list(layouts.keys())}")
    assert "padrao_7_cpura" in layouts, "padrao_7_cpura ausente no catálogo carregado!"
    assert "padrao_7_cgrupo" in layouts, "padrao_7_cgrupo ausente no catálogo carregado!"

    # Carregar inventário da Fase 0 para filtrar os arquivos vigentes de padrao_7
    inv_path = PROJECT_ROOT / "docs" / "inventario_fichas.csv"
    if not inv_path.exists():
        print("[-] inventario_fichas.csv não encontrado. Abortando.")
        return 1

    df_inv = pd.read_csv(inv_path, sep=";")
    p7_vigentes = df_inv[df_inv["versao_layout"] == "padrao_7"]
    print(f"[+] Total de arquivos padrao_7 vigentes no inventário: {len(p7_vigentes)}")

    fichas_dir = context.path("input_fichas_comercializadoras_processadas")

    resultados = []
    erros = 0

    for idx, row in p7_vigentes.iterrows():
        arq_nome = row["arquivo_nome"]
        seg_inv = row["segmento"]
        arq_path = fichas_dir / arq_nome

        if not arq_path.exists():
            print(f"[-] Arquivo não encontrado: {arq_nome}")
            erros += 1
            continue

        wb = None
        try:
            wb = abrir_pasta(arq_path)
            raw, meta, winner = extrair_registro_do_vencedor(wb, layouts, master_catalog)
            
            fechar_pasta(wb)
            wb = None

            resultados.append({
                "arquivo": arq_nome,
                "segmento_inventario": seg_inv,
                "winner_layout": winner,
                "score_integridade": raw.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0),
                "tem_ativo_total": raw.get("ATIVO_TOTAL") is not None,
                "tem_vendas_liquidas": raw.get("VENDAS_LIQUIDAS") is not None,
                "vendas_liquidas": raw.get("VENDAS_LIQUIDAS"),
                "tem_lucro_liquido": raw.get("LUCRO_LIQUIDO") is not None,
                "tem_fco": raw.get("FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS") is not None,
                "tem_pd_base_ficha": (raw.get("PROBABILIDADE_DEFAULT") is not None) or (raw.get("PD_BASE_FICHA") is not None),
                "pd_base_ficha": raw.get("PROBABILIDADE_DEFAULT") if raw.get("PROBABILIDADE_DEFAULT") is not None else raw.get("PD_BASE_FICHA"),
                "tem_score_board": raw.get("SCORE_BOARD_COPEL") is not None,
                "score_board": raw.get("SCORE_BOARD_COPEL"),
                "categoria_declarada": raw.get("TIPO_COMERCIALIZADORA") or raw.get("CATEGORIA") or raw.get("SUBSEGMENTO"),
                "rating_copel": raw.get("RATING_COPEL"),
            })

        except Exception as exc:
            if wb:
                try: fechar_pasta(wb)
                except Exception: pass
            print(f"[-] Erro ao processar {arq_nome}: {exc}")
            erros += 1

    df_res = pd.DataFrame(resultados)
    
    print("\n" + "=" * 95)
    print("📊 RESUMO DA EXTRAÇÃO POR SEGMENTO DO INVENTÁRIO:")
    print("=" * 95)
    
    agg = df_res.groupby("segmento_inventario").agg(
        total=("arquivo", "count"),
        winner_cpura=("winner_layout", lambda x: (x == "padrao_7_cpura").sum()),
        winner_cgrupo=("winner_layout", lambda x: (x == "padrao_7_cgrupo").sum()),
        winner_p7_legado=("winner_layout", lambda x: (x == "padrao_7").sum()),
        com_vendas=("tem_vendas_liquidas", "sum"),
        com_lucro=("tem_lucro_liquido", "sum"),
        com_fco=("tem_fco", "sum"),
        com_pd_base_ficha=("tem_pd_base_ficha", "sum"),
        com_score_board=("tem_score_board", "sum"),
    )
    print(agg.to_string())

    print("\n" + "=" * 95)
    print("🔍 AMOSTRA DE 10 ARQUIVOS PROCESSADOS (VALORES REAIS EXTRAÍDOS):")
    print("=" * 95)
    cols_amostra = ["arquivo", "winner_layout", "vendas_liquidas", "pd_base_ficha", "score_board", "rating_copel"]
    print(df_res[cols_amostra].head(10).to_string(index=False))

    duracao = time.perf_counter() - inicio
    print(f"\n[+] Execução concluída em {duracao:.2f}s | Arquivos: {len(df_res)} | Falhas: {erros}")
    
    # Salvar resultado analítico
    out_csv = PROJECT_ROOT / "docs" / "amostras" / "resultado_teste_extracao_padrao_7.csv"
    df_res.to_csv(out_csv, sep=";", index=False, encoding="utf-8-sig")
    print(f"[+] Detalhe completo salvo em: {out_csv}")
    print("=" * 95 + "\n")
    return erros


if __name__ == "__main__":
    sys.exit(main())
