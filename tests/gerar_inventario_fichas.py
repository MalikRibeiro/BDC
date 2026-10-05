"""Script de Inventário Quantitativo de Fichas (Fase 0 - BDC).

Examina o repositório de fichas de comercializadoras extraídas e ativas,
classificando por Tipo x Versão de Layout e auditando a presença física
e preenchimento das células de balanço, scores e ratings para CPURA.

Gera: docs/inventario_fichas.csv e resumo estruturado.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def limpar_str(val: Any) -> str:
    if val is None or pd.isna(val):
        return ""
    s = str(val).strip()
    return "" if s in ("None", "nan", "<NA>", "-", "0,0", "0") else s


def e_numerico_valido(val: Any) -> bool:
    if val is None or pd.isna(val):
        return False
    s = str(val).strip().replace(".", "").replace(",", ".")
    try:
        f = float(s)
        return abs(f) > 0.000001
    except ValueError:
        return False


def main() -> int:
    print(f"\n{'=' * 85}")
    print(f"📊 BDC - INVENTÁRIO QUANTITATIVO DE FICHAS CADASTRAIS (FASE 0)")
    print(f"{'=' * 85}\n")

    path_csv_silver = PROJECT_ROOT / "SAIDAS" / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.csv"
    if not path_csv_silver.exists():
        print(f"[ERRO] Arquivo Silver não encontrado: {path_csv_silver}")
        return 1

    print(f"[*] Carregando base Silver: {path_csv_silver.name}...")
    df_silver = pd.read_csv(path_csv_silver, sep=";", dtype=str)
    print(f"    Total de registros processados: {len(df_silver)}")

    # Filtrar apenas registros vigentes se existir coluna de status
    if "_STATUS_REGISTRO" in df_silver.columns:
        df_vigentes = df_silver[df_silver["_STATUS_REGISTRO"] == "VIGENTE"].copy()
        print(f"    Registros vigentes (última versão de cada arquivo): {len(df_vigentes)}")
    else:
        df_vigentes = df_silver.copy()

    # Mapeamento de campos contábeis de balanço
    col_at = "ATIVO_TOTAL"
    col_ac = "ATIVO_CIRCULANTE"
    col_acf = "ATIVO_CIRCULANTE_FINANCEIRO"
    col_pc = "PASSIVO_CIRCULANTE"
    col_pcf = "PASSIVO_CIRCULANTE_FINANCEIRO"
    col_pncf = "PASSIVO_NAO_CIRCULANTE_FINANCEIRO"
    col_pl = "PATRIMONIO_LIQUIDO"
    col_la = "LUCROS_ACUMULADOS"
    col_rl = "RESERVA_DE_LUCROS"
    col_vl = "VENDAS_LIQUIDAS"
    col_ll = "LUCRO_LIQUIDO"
    col_fco = "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS"
    col_pd = "PROBABILIDADE_DEFAULT"
    col_rtg = "RATING_COPEL"
    col_score_tot = "SCORE_TOTAL" if "SCORE_TOTAL" in df_vigentes.columns else None

    inventario_linhas: list[dict[str, Any]] = []

    for _, row in df_vigentes.iterrows():
        arq = row.get("arquivo_nome", "")
        versao = row.get("versao_ficha", "desconhecido")
        tipo_com = str(row.get("TIPO_COMERCIALIZADORA", "")).strip().upper()
        if "PURA" in tipo_com or tipo_com == "CPURA":
            segmento = "CPURA"
        elif "GRUPO" in tipo_com or tipo_com == "CGRUPO":
            segmento = "CGRUPO"
        else:
            segmento = "INDEFINIDO"

        cnpj = row.get("CNPJ", "")
        contraparte = row.get("SIGLA", "")

        tem_at = e_numerico_valido(row.get(col_at))
        tem_ac = e_numerico_valido(row.get(col_ac))
        tem_acf = e_numerico_valido(row.get(col_acf))
        tem_pc = e_numerico_valido(row.get(col_pc))
        tem_pcf = e_numerico_valido(row.get(col_pcf))
        tem_pncf = e_numerico_valido(row.get(col_pncf))
        tem_pl = e_numerico_valido(row.get(col_pl))
        tem_la = e_numerico_valido(row.get(col_la))
        tem_rl = e_numerico_valido(row.get(col_rl))
        tem_vl = e_numerico_valido(row.get(col_vl))
        tem_ll = e_numerico_valido(row.get(col_ll))
        tem_fco = e_numerico_valido(row.get(col_fco)) or e_numerico_valido(row.get("FCO"))
        tem_pd = e_numerico_valido(row.get(col_pd))
        tem_rtg = bool(limpar_str(row.get(col_rtg)))
        tem_score_indiv = e_numerico_valido(row.get("SCORE_PD")) or e_numerico_valido(row.get("SCORE_BOARD_COPEL"))

        # Balanço completo = AT, AC, PC, PL, VL e (FCO ou LL)
        balanco_completo = tem_at and tem_ac and tem_pc and tem_pl and tem_vl and (tem_fco or tem_ll)
        balanco_parcial = (tem_at or tem_ac or tem_pl) and not balanco_completo

        status_balanco = "COMPLETO" if balanco_completo else ("PARCIAL" if balanco_parcial else "AUSENTE")

        obs = []
        if not tem_at:
            obs.append("SEM_ATIVO_TOTAL")
        if not tem_vl:
            obs.append("SEM_VENDAS_LIQUIDAS")
        if not tem_pd:
            obs.append("SEM_PD_DECLARADA")
        if not tem_rtg:
            obs.append("SEM_RATING")

        inventario_linhas.append({
            "arquivo_nome": arq,
            "cnpj": cnpj,
            "contraparte": contraparte,
            "segmento": segmento,
            "versao_layout": versao,
            "status_balanco": status_balanco,
            "tem_ativo_total": "Sim" if tem_at else "Nao",
            "tem_ativo_circulante": "Sim" if tem_ac else "Nao",
            "tem_passivo_circulante": "Sim" if tem_pc else "Nao",
            "tem_patrimonio_liquido": "Sim" if tem_pl else "Nao",
            "tem_vendas_liquidas": "Sim" if tem_vl else "Nao",
            "tem_lucro_liquido": "Sim" if tem_ll else "Nao",
            "tem_fco": "Sim" if tem_fco else "Nao",
            "tem_pd_declarada": "Sim" if tem_pd else "Nao",
            "tem_rating_copel": "Sim" if tem_rtg else "Nao",
            "tem_scores_individuais": "Sim" if tem_score_indiv else "Nao",
            "observacoes": "|".join(obs) if obs else "OK"
        })

    df_inv = pd.DataFrame(inventario_linhas)

    # Exportar CSV
    path_saida = PROJECT_ROOT / "docs" / "inventario_fichas.csv"
    path_saida.parent.mkdir(parents=True, exist_ok=True)
    df_inv.to_csv(path_saida, sep=";", decimal=",", index=False, encoding="utf-8-sig")
    print(f"\n[+] Arquivo analítico gerado com sucesso em:")
    print(f"    {path_saida} ({len(df_inv)} linhas)\n")

    # --------------------------------------------------------------------------
    # RELATÓRIO EXECUTIVO POR LAYOUT E SEGMENTO
    # --------------------------------------------------------------------------
    print(f"{'=' * 85}")
    print(f"📈 1. DISTRIBUIÇÃO GERAL POR VERSÃO DE LAYOUT E SEGMENTO")
    print(f"{'=' * 85}")
    tabela_dist = pd.crosstab(df_inv["versao_layout"], df_inv["segmento"], margins=True)
    print(tabela_dist.to_string())

    # --------------------------------------------------------------------------
    # FOCO CPURA (PRIORIDADE 1)
    # --------------------------------------------------------------------------
    df_cpura = df_inv[df_inv["segmento"] == "CPURA"]
    print(f"\n{'=' * 85}")
    print(f"🎯 2. DIAGNÓSTICO PROFUNDO DE COMERCIALIZADORAS PURAS (CPURA) — Total: {len(df_cpura)}")
    print(f"{'=' * 85}")

    tabela_cpura_status = pd.crosstab(df_cpura["versao_layout"], df_cpura["status_balanco"], margins=True)
    print("\n[A] Status do Balanço Contábil por Versão de Layout em CPURA:")
    print(tabela_cpura_status.to_string())

    tot_cpura = len(df_cpura)
    cpura_comp = (df_cpura["status_balanco"] == "COMPLETO").sum()
    cpura_parc = (df_cpura["status_balanco"] == "PARCIAL").sum()
    cpura_aus = (df_cpura["status_balanco"] == "AUSENTE").sum()
    cpura_pd = (df_cpura["tem_pd_declarada"] == "Sim").sum()
    cpura_rtg = (df_cpura["tem_rating_copel"] == "Sim").sum()
    cpura_scores = (df_cpura["tem_scores_individuais"] == "Sim").sum()

    print(f"\n[B] Métricas Agregadas CPURA:")
    print(f"    • Total de fichas CPURA vigentes:               {tot_cpura:4d} (100.0%)")
    print(f"    • Fichas com Balanço Completo (apto recálculo): {cpura_comp:4d} ({cpura_comp/tot_cpura*100:5.1f}%)")
    print(f"    • Fichas com Balanço Parcial:                   {cpura_parc:4d} ({cpura_parc/tot_cpura*100:5.1f}%)")
    print(f"    • Fichas com Balanço Ausente / Zerado:          {cpura_aus:4d} ({cpura_aus/tot_cpura*100:5.1f}%)")
    print(f"    • Fichas com PD Declarada preenchida:           {cpura_pd:4d} ({cpura_pd/tot_cpura*100:5.1f}%)")
    print(f"    • Fichas com Rating Copel preenchido:           {cpura_rtg:4d} ({cpura_rtg/tot_cpura*100:5.1f}%)")
    print(f"    • Fichas com Scores Individuais preenchidos:    {cpura_scores:4d} ({cpura_scores/tot_cpura*100:5.1f}%)")

    # --------------------------------------------------------------------------
    # MAPA DE MUDANÇA DE CÉLULAS ENTRE LAYOUTS (V1..V7)
    # --------------------------------------------------------------------------
    print(f"\n{'=' * 85}")
    print(f"📍 3. MAPA DE MUDANÇA DAS CÉLULAS DE BALANÇO ENTRE VERSÕES (V1 A V7)")
    print(f"{'=' * 85}")
    mapa_celulas = [
        {"Campo": "ATIVO_CIRCULANTE", "v1": "Nao Impl.", "v2": "Y9", "v3": "P14", "v4": "P13", "v5": "P15", "v6/v7": "G14"},
        {"Campo": "ATIVO_CIRC_FINANC", "v1": "Nao Impl.", "v2": "Y10", "v3": "P15", "v4": "P14", "v5": "P16", "v6/v7": "G15"},
        {"Campo": "ATIVO_TOTAL", "v1": "Nao Impl.", "v2": "Y11", "v3": "P16", "v4": "P15", "v5": "P17", "v6/v7": "G16"},
        {"Campo": "PASSIVO_CIRCULANTE", "v1": "Nao Impl.", "v2": "Y12", "v3": "P17", "v4": "P16", "v5": "P18", "v6/v7": "G17"},
        {"Campo": "PASSIVO_CIRC_FINANC", "v1": "Nao Impl.", "v2": "Y13", "v3": "P18", "v4": "P17", "v5": "P19", "v6/v7": "Q18"},
        {"Campo": "PASSIVO_NAO_CIRC_FINANC", "v1": "Nao Impl.", "v2": "Y14", "v3": "P19", "v4": "P18", "v5": "P20", "v6/v7": "Q19"},
        {"Campo": "PATRIMONIO_LIQUIDO", "v1": "Nao Impl.", "v2": "Y15", "v3": "B30", "v4": "B29", "v5": "B31", "v6/v7": "G20"},
        {"Campo": "LUCROS_ACUMULADOS", "v1": "Nao Impl.", "v2": "Y17", "v3": "P22", "v4": "P21", "v5": "P23", "v6/v7": "Q22"},
        {"Campo": "RESERVA_DE_LUCROS", "v1": "Nao Impl.", "v2": "Y18", "v3": "P23", "v4": "P22", "v5": "P24", "v6/v7": "Q23"},
        {"Campo": "VENDAS_LIQUIDAS", "v1": "Nao Impl.", "v2": "Y19", "v3": "P24", "v4": "P23", "v5": "P25", "v6/v7": "Q24"},
        {"Campo": "LUCRO_LIQUIDO", "v1": "Nao Impl.", "v2": "Y20", "v3": "P25", "v4": "P24", "v5": "P26", "v6/v7": "Q25"},
        {"Campo": "FCO", "v1": "Nao Impl.", "v2": "Y21", "v3": "P26", "v4": "P25", "v5": "P27", "v6/v7": "Q26"},
        {"Campo": "PD_DECLARADA", "v1": "Premissas!Q27", "v2": "U37", "v3": "B31", "v4": "B30", "v5": "B32", "v6/v7": "B26"},
        {"Campo": "RATING_COPEL", "v1": "Nao Impl.", "v2": "Nao Impl.", "v3": "B53", "v4": "B52", "v5": "B54", "v6/v7": "B49"}
    ]
    df_mapa = pd.DataFrame(mapa_celulas)
    print(df_mapa.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
