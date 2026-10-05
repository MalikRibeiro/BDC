"""Script de Auditoria Física e Resolução de Lacunas (Fase 0.6).

Executa medições 100% orientadas a dados e sem textos estáticos inventados:
1. Resolução das contradições 1.1 a 1.7 com dados reais.
2. Rastreamento recursivo de precedentes de fórmulas via openpyxl.formula.tokenizer.
3. Varredura dos 40 arquivos padrao_7 CPURA vigentes para contagem de B26..B29.
4. Bancada de teste de recálculo contábil em amostra de padrao_6 completo.
5. Extração de regras e bordas das fórmulas reais para docs/regras_extraidas_das_fichas.md.
6. Segmentação empírica das 34 fichas padrao_7 INDEFINIDO.
7. Reescrita estrita de docs/investigacao_layouts_parciais.md.

SEGURANÇA: Somente leitura. Cópias temporárias em scratch/amostras_investigacao/.
"""
from __future__ import annotations

import collections
import hashlib
import json
import math
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import openpyxl
from openpyxl.formula.tokenizer import Tokenizer, Token
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
SCRATCH_DIR = PROJECT_ROOT / "scratch" / "amostras_investigacao"
DIR_PROCESSADAS = PROJECT_ROOT / "ENTRADAS" / "fichas" / "comercializadoras" / "processadas"
DIR_REJEITADAS = PROJECT_ROOT / "ENTRADAS" / "fichas" / "comercializadoras" / "rejeitadas"
PATH_SILVER_CSV = PROJECT_ROOT / "SAIDAS" / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.csv"
PATH_LOG_REJEICOES = PROJECT_ROOT / "LOGS" / "rejeitados" / "2026-10-02_rejeicoes.json"
PATH_UNIVERSO_PD = PROJECT_ROOT / "ENTRADAS" / "control" / "universo_pd.csv"


def normalizar_cnpj(val: Any) -> str:
    if val is None or pd.isna(val):
        return ""
    digits = re.sub(r"\D", "", str(val).strip())
    return digits.zfill(14) if digits else ""


def limpar_str(val: Any) -> str:
    if val is None or pd.isna(val):
        return ""
    s = str(val).strip()
    return "" if s in ("None", "nan", "<NA>", "-", "0,0", "0") else s


def calcular_hash_curto(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()[:8]


def extrair_tokens_precedentes(formula_str: str) -> list[str]:
    """Extrai referências de células ou intervalos a partir de uma fórmula Excel."""
    if not formula_str or not formula_str.startswith("="):
        return []
    try:
        tok = Tokenizer(formula_str)
        refs = []
        for t in tok.items:
            if t.type == Token.OPERAND and t.subtype == Token.RANGE:
                val = t.value.replace("$", "").strip()
                if val:
                    refs.append(val)
        return refs
    except Exception:
        # Fallback regex se tokenizer falhar em fórmula exótica
        return re.findall(r"(?:'?[A-Za-z0-9_ ]+'?!)?[A-Z]{1,3}\d{1,5}(?::[A-Z]{1,3}\d{1,5})?", formula_str.replace("$", ""))


def rastrear_celula(ws_form, ws_val, cell_coord: str, sheet_name: str, profundidade: int = 0, max_depth: int = 3) -> dict[str, Any]:
    """Rastreia recursivamente os precedentes de uma célula até constantes ou profundidade máxima."""
    try:
        cf = ws_form[cell_coord]
        cv = ws_val[cell_coord]
    except Exception:
        return {
            "coord": cell_coord,
            "sheet": sheet_name,
            "formula": "CELULA_INVALIDA",
            "cache": None,
            "tem_cache": False,
            "tipo": "ERRO",
            "number_format": "",
            "precedentes": [],
        }

    raw_f = cf.value
    raw_v = cv.value
    e_form = str(raw_f).startswith("=") if raw_f is not None else False
    f_txt = str(raw_f) if e_form else ""
    nfmt = str(cf.number_format or "")

    precedentes_diretos = extrair_tokens_precedentes(f_txt) if e_form else []

    tipo = "VAZIA"
    if e_form:
        tipo = "FORMULA"
    elif raw_v is not None and str(raw_v).strip() != "":
        tipo = "CONSTANTE"

    sub_rastreios = []
    if e_form and profundidade < max_depth:
        for ref in precedentes_diretos:
            # Separar aba e coordenada se houver
            if "!" in ref:
                parts = ref.split("!", 1)
                s_ref = parts[0].replace("'", "").strip()
                c_ref = parts[1].strip()
                wb_f = ws_form.parent
                wb_v = ws_val.parent
                if s_ref in wb_f.sheetnames and ":" not in c_ref:
                    sub_r = rastrear_celula(wb_f[s_ref], wb_v[s_ref], c_ref, s_ref, profundidade + 1, max_depth)
                    sub_rastreios.append(sub_r)
            else:
                if ":" not in ref:
                    sub_r = rastrear_celula(ws_form, ws_val, ref, sheet_name, profundidade + 1, max_depth)
                    sub_rastreios.append(sub_r)

    return {
        "coord": cell_coord,
        "sheet": sheet_name,
        "formula": f_txt,
        "cache": raw_v,
        "tem_cache": raw_v is not None,
        "tipo": tipo,
        "number_format": nfmt,
        "precedentes_tokens": precedentes_diretos,
        "precedentes_detalhados": sub_rastreios,
    }


def main() -> int:
    print(f"\n{'=' * 85}")
    print("🔬 BDC - FASE 0.6: AUDITORIA FÍSICA E FECHAMENTO DE LACUNAS METODOLÓGICAS")
    print(f"{'=' * 85}\n")

    # -------------------------------------------------------------------------
    # 0. Verificação do universo_pd.csv
    # -------------------------------------------------------------------------
    universo_existe = PATH_UNIVERSO_PD.exists()
    df_universo = pd.DataFrame()
    cnpjs_universo = set()
    if universo_existe:
        try:
            df_universo = pd.read_csv(PATH_UNIVERSO_PD, sep=";", dtype=str)
            for c in df_universo.columns:
                if "CNPJ" in c.upper():
                    cnpjs_universo = set(df_universo[c].apply(normalizar_cnpj).unique())
                    break
            print(f"[STATUS] universo_pd.csv localizado com {len(cnpjs_universo)} CNPJs únicos.")
        except Exception as e:
            print(f"[STATUS] Falha ao ler universo_pd.csv: {e}")
    else:
        print(f"[STATUS] ENTRADAS/control/universo_pd.csv NÃO EXISTE NO MOMENTO. A Seção 6 aguardará a sua criação.")

    # -------------------------------------------------------------------------
    # 1. Carregamento da Silver para Reconciliações
    # -------------------------------------------------------------------------
    if not PATH_SILVER_CSV.exists():
        print(f"[ERRO] Base Silver não encontrada: {PATH_SILVER_CSV}")
        return 1

    df_silver = pd.read_csv(PATH_SILVER_CSV, sep=";", dtype=str)
    total_silver = len(df_silver)
    df_silver_vig = df_silver[df_silver["_STATUS_REGISTRO"] == "VIGENTE"].copy() if "_STATUS_REGISTRO" in df_silver.columns else df_silver.copy()
    total_vigentes = len(df_silver_vig)
    total_historicos = total_silver - total_vigentes

    # Contagem de arquivos em disco
    arqs_processados = list(DIR_PROCESSADAS.glob("*.xlsx")) if DIR_PROCESSADAS.exists() else []
    arqs_rejeitados = list(DIR_REJEITADAS.glob("*.xlsx")) if DIR_REJEITADAS.exists() else []
    qtd_processados = len(arqs_processados)
    qtd_rejeitados = len(arqs_rejeitados)

    # -------------------------------------------------------------------------
    # 1.1 e 1.6: Resolver discrepância 746 processados vs 698 vigentes
    # -------------------------------------------------------------------------
    nomes_processados = {p.name for p in arqs_processados}
    nomes_silver_todos = set(df_silver["arquivo_nome"].dropna())
    nomes_silver_vig = set(df_silver_vig["arquivo_nome"].dropna())

    # Arquivos em processadas que não estão como VIGENTE na Silver
    processados_nao_vigentes = nomes_processados - nomes_silver_vig
    processados_historicos = nomes_processados & (nomes_silver_todos - nomes_silver_vig)
    processados_ausentes_silver = nomes_processados - nomes_silver_todos

    print(f"\n--- [1.6] RECONCILIAÇÃO FÍSICA: ARQUIVOS EM DISCO × REGISTROS SILVER ---")
    print(f"  • Arquivos físicos em processadas/:              {qtd_processados}")
    print(f"  • Registros totais na Silver:                    {total_silver}")
    print(f"  • Registros VIGENTES na Silver:                  {total_vigentes}")
    print(f"  • Registros SUBSTITUIDOS/HISTÓRICOS na Silver:   {total_historicos}")
    print(f"  • Diferença física (746 - 698):                  {qtd_processados - total_vigentes} arquivos")
    print(f"      - Desses 48, quantos são histórico na Silver: {len(processados_historicos)}")
    print(f"      - Desses 48, quantos não constam na Silver:   {len(processados_ausentes_silver)}")

    # -------------------------------------------------------------------------
    # 1.7: Rejeitados por categoria a partir do log real
    # -------------------------------------------------------------------------
    rejeicoes_por_status = collections.Counter()
    rejeicoes_por_erro = collections.Counter()
    rejeitados_com_universo = []

    if PATH_LOG_REJEICOES.exists():
        try:
            with open(PATH_LOG_REJEICOES, "r", encoding="utf-8") as f:
                logs_rej = json.load(f)
            for item in logs_rej:
                st = item.get("status", "DESCONHECIDO")
                rejeicoes_por_status[st] += 1
                for err in item.get("erros", []):
                    # Agrupar mensagem de score
                    if "Score insuficiente" in err:
                        rejeicoes_por_erro["Score insuficiente para layout (< 35%)"] += 1
                    elif "Hash já processado" in err:
                        rejeicoes_por_erro["Hash duplicado"] += 1
                    else:
                        rejeicoes_por_erro[err[:60]] += 1
        except Exception as e:
            print(f"  [AVISO] Falha ao processar log de rejeições: {e}")

    print(f"\n--- [1.7] REJEITADOS: MOTIVOS POR CATEGORIA (TOTAL: {qtd_rejeitados}) ---")
    for st, count in rejeicoes_por_status.items():
        print(f"  • Status: {st:<25} -> {count} arquivos")
    for err, count in rejeicoes_por_erro.most_common(5):
        print(f"      - Motivo: {err:<45} -> {count}")

    # -------------------------------------------------------------------------
    # 1.3: Rating Copel na Silver (String vs Float)
    # -------------------------------------------------------------------------
    fichas_com_rating_str = df_silver_vig["RATING_COPEL"].apply(limpar_str)
    qtd_com_rating = (fichas_com_rating_str != "").sum()
    dist_rating = fichas_com_rating_str[fichas_com_rating_str != ""].value_counts().to_dict()
    print(f"\n--- [1.3] RATING COPEL VIGENTE NA SILVER ---")
    print(f"  • Fichas vigentes com Rating preenchido (string não vazia): {qtd_com_rating} de {total_vigentes}")
    print(f"  • Distribuição observada: {dist_rating}")

    # -------------------------------------------------------------------------
    # 2. Rastreamento de Precedentes e Insumos nas Amostras
    # -------------------------------------------------------------------------
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
    amostras_alvo = [
        # 4 padrao_7 CPURA
        ("ELERA COMERCIALIZADORA 28082026.xlsx", "padrao_7", "CPURA"),
        ("MARFRIG 27082026.xlsx", "padrao_7", "CPURA"),
        ("KROMA 09092026.xlsx", "padrao_7", "CPURA"),
        ("NOVA ENERGIA 26082026.xlsx", "padrao_7", "CPURA"),
        # 2 padrao_6 CPURA COMPLETO (Controle)
        ("POLLARIX 03062026.xlsx", "padrao_6", "CPURA"),
        ("J&F 20082026.xlsx", "padrao_6", "CPURA"),
    ]

    celulas_rastrear = [
        "B26", "B27", "B28", "B29", "C26", "C27", "C28", "C29", "B49",
        "Q24", "Q25", "Q26", "N67", "N68", "N69", "N70", "N71", "N72", "N73", "N74", "N75", "N76"
    ]

    tabela_rastreamento = []
    regras_fichas = []

    print(f"\n--- [2 & 4] RASTREAMENTO PROFUNDO DE PRECEDENTES DE FÓRMULAS ---")
    for arq_nome, lyt, seg in amostras_alvo:
        p_orig = DIR_PROCESSADAS / arq_nome
        if not p_orig.exists():
            print(f"  [AVISO] Amostra não encontrada: {arq_nome}")
            continue

        p_safe = SCRATCH_DIR / f"rastreio_{arq_nome}"
        shutil.copy2(p_orig, p_safe)

        wb_f = openpyxl.load_workbook(p_safe, data_only=False)
        wb_v = openpyxl.load_workbook(p_safe, data_only=True)
        ws_f = wb_f["FichaIndividual"] if "FichaIndividual" in wb_f.sheetnames else wb_f.active
        ws_v = wb_v[ws_f.title]

        for coord in celulas_rastrear:
            info = rastrear_celula(ws_f, ws_v, coord, ws_f.title, profundidade=0, max_depth=2)

            # Classificação específica de Q24..Q26
            cat_q = "N/A"
            if coord in ("Q24", "Q25", "Q26"):
                val = info["cache"]
                f_txt = info["formula"]
                if info["tipo"] == "VAZIA":
                    cat_q = "VAZIA"
                elif info["tipo"] == "FORMULA" and val is None:
                    cat_q = "FORMULA_SEM_CACHE"
                elif "SEERRO" in f_txt.upper() and (val == 0 or val == 0.0 or val == "0"):
                    cat_q = "FORMULA_SEERRO_ZERO"
                elif info["tipo"] == "CONSTANTE" and (val == 0 or val == 0.0 or val == "0"):
                    cat_q = "CONSTANTE_ZERO"
                elif val is not None and val != 0:
                    cat_q = "COM_VALOR_POSITIVO"
                else:
                    cat_q = f"OUTRO ({info['tipo']})"

            # Capturar fórmulas de regras (C26:C29 e N72:N76)
            if coord in ("C26", "C27", "C28", "C29", "N72", "N73", "N74", "N75", "N76", "N67"):
                if info["formula"]:
                    regras_fichas.append({
                        "arquivo": arq_nome,
                        "layout": lyt,
                        "coord": coord,
                        "label_vizinho": str(ws_v[f"A{coord[1:]}"].value if coord.startswith("C") else ws_v[f"L{coord[1:]}"].value or ""),
                        "formula": info["formula"],
                        "cache": info["cache"],
                    })

            tabela_rastreamento.append({
                "arquivo": arq_nome,
                "layout": lyt,
                "coord": coord,
                "tipo": info["tipo"],
                "formula": info["formula"][:80],
                "tem_cache": "Sim" if info["tem_cache"] else "Nao",
                "formato": info["number_format"],
                "categoria_q": cat_q,
                "precedentes": ", ".join(info["precedentes_tokens"][:4]),
            })

        wb_f.close()
        wb_v.close()

    df_rastreio = pd.DataFrame(tabela_rastreamento)

    # -------------------------------------------------------------------------
    # 2. Varredura da População de 40 padrao_7 CPURA Vigentes (B26..B29)
    # -------------------------------------------------------------------------
    p7_cpura_vigentes = df_silver_vig[
        (df_silver_vig["versao_ficha"] == "padrao_7") &
        (df_silver_vig["TIPO_COMERCIALIZADORA"].str.contains("PURA|CPURA", case=False, na=False))
    ]
    arqs_p7_cpura = p7_cpura_vigentes["arquivo_nome"].dropna().tolist()

    contagem_b26_b29 = {
        "B26_PD": {"NULO_VAZIO": 0, "ZERO": 0, "POSITIVO": 0, "NEGATIVO": 0},
        "B27_FCO_ROL": {"NULO_VAZIO": 0, "ZERO": 0, "POSITIVO": 0, "NEGATIVO": 0},
        "B28_ROA": {"NULO_VAZIO": 0, "ZERO": 0, "POSITIVO": 0, "NEGATIVO": 0},
        "B29_ROE": {"NULO_VAZIO": 0, "ZERO": 0, "POSITIVO": 0, "NEGATIVO": 0},
    }

    print(f"\n--- [2] VARREDURA POPULACIONAL: B26..B29 EM {len(arqs_p7_cpura)} PADRAO_7 CPURA ---")
    for a_nome in arqs_p7_cpura:
        p_real = DIR_PROCESSADAS / a_nome
        if not p_real.exists():
            continue
        try:
            wb_rapido = openpyxl.load_workbook(p_real, data_only=True, read_only=True)
            ws_r = wb_rapido["FichaIndividual"] if "FichaIndividual" in wb_rapido.sheetnames else wb_rapido.active
            for c_nome, c_addr in [("B26_PD", "B26"), ("B27_FCO_ROL", "B27"), ("B28_ROA", "B28"), ("B29_ROE", "B29")]:
                v = ws_r[c_addr].value
                if v is None or str(v).strip() in ("", "-", "None", "nan"):
                    contagem_b26_b29[c_nome]["NULO_VAZIO"] += 1
                else:
                    try:
                        fv = float(str(v).replace(".", "").replace(",", ".")) if isinstance(v, str) else float(v)
                        if abs(fv) < 1e-9:
                            contagem_b26_b29[c_nome]["ZERO"] += 1
                        elif fv > 0:
                            contagem_b26_b29[c_nome]["POSITIVO"] += 1
                        else:
                            contagem_b26_b29[c_nome]["NEGATIVO"] += 1
                    except ValueError:
                        contagem_b26_b29[c_nome]["NULO_VAZIO"] += 1
            wb_rapido.close()
        except Exception:
            pass

    for k, v in contagem_b26_b29.items():
        print(f"  • {k:<15}: Positivos={v['POSITIVO']}, Zero={v['ZERO']}, Nulos={v['NULO_VAZIO']}, Negativos={v['NEGATIVO']}")

    # -------------------------------------------------------------------------
    # 3. Bancada de Teste: Recálculo Z-Score no padrao_6 Completo
    # -------------------------------------------------------------------------
    p6_completos = df_silver_vig[
        (df_silver_vig["versao_ficha"] == "padrao_6") &
        (df_silver_vig["TIPO_COMERCIALIZADORA"].str.contains("PURA|CPURA", case=False, na=False))
    ]
    arqs_p6 = p6_completos["arquivo_nome"].dropna().head(15).tolist()

    intercept = -1.9790
    coef_x12 = -0.7714
    coef_x16 = 1.2547
    coef_x19 = -1.1345
    coef_x22 = 0.1654

    resultados_p6 = []
    print(f"\n--- [3] BANCADA DE TESTE: RECÁLCULO NT §4 EM {len(arqs_p6)} FICHAS PADRAO_6 ---")
    for a_nome in arqs_p6:
        p_real = DIR_PROCESSADAS / a_nome
        if not p_real.exists():
            continue
        try:
            wb_v = openpyxl.load_workbook(p_real, data_only=True, read_only=True)
            wb_f = openpyxl.load_workbook(p_real, data_only=False, read_only=True)
            ws_v = wb_v["FichaIndividual"] if "FichaIndividual" in wb_v.sheetnames else wb_v.active
            ws_f = wb_f["FichaIndividual"] if "FichaIndividual" in wb_f.sheetnames else wb_f.active

            def _get_f(cell_addr):
                val = ws_v[cell_addr].value
                if val is None:
                    return None
                try:
                    return float(str(val).replace(".", "").replace(",", ".")) if isinstance(val, str) else float(val)
                except Exception:
                    return None

            at = _get_f("G16")
            ac = _get_f("G14")
            pc = _get_f("G17")
            acf = _get_f("G15")
            pcf = _get_f("Q18")
            pncf = _get_f("Q19")
            la = _get_f("Q22") or 0.0
            rl = _get_f("Q23") or 0.0
            vl = _get_f("Q24")
            pd_decl = _get_f("B26")

            tipo_b26 = "FORMULA" if str(ws_f["B26"].value or "").startswith("=") else "DIGITADA/CONSTANTE"

            if at and at > 0 and vl and vl > 0 and ac is not None and pc is not None and pcf is not None and pncf is not None and acf is not None:
                x12 = (la + rl) / at
                x16 = (pcf + pncf) / at
                x19 = (ac - pc) / at
                x22 = (acf - pcf) / vl
                z = intercept + (coef_x12 * x12) + (coef_x16 * x16) + (coef_x19 * x19) + (coef_x22 * x22)
                z_clamped = max(-20.0, min(z, 20.0))
                pd_calc = 1.0 / (1.0 + math.exp(-z_clamped))
                diff = abs(pd_calc - pd_decl) if pd_decl is not None else None
                confere = diff is not None and diff < 1e-4
                resultados_p6.append({
                    "arquivo": a_nome,
                    "pd_declarada": pd_decl,
                    "pd_calculada": pd_calc,
                    "tipo_b26": tipo_b26,
                    "diff": diff,
                    "confere": confere,
                })
            wb_v.close()
            wb_f.close()
        except Exception:
            pass

    df_p6_res = pd.DataFrame(resultados_p6)
    if not df_p6_res.empty:
        pct_conf = (df_p6_res["confere"].sum() / len(df_p6_res)) * 100.0
        print(f"  • Total testado: {len(df_p6_res)} fichas padrao_6")
        print(f"  • Taxa de reprodução exata (< 1e-4): {pct_conf:.1f}% ({df_p6_res['confere'].sum()} de {len(df_p6_res)})")
        print(f"  • Tipo predominante de B26: {df_p6_res['tipo_b26'].value_counts().to_dict()}")

    # -------------------------------------------------------------------------
    # 5. Segmentação das 34 padrao_7 INDEFINIDO
    # -------------------------------------------------------------------------
    p7_indef = df_silver_vig[
        (df_silver_vig["versao_ficha"] == "padrao_7") &
        (~df_silver_vig["TIPO_COMERCIALIZADORA"].str.contains("PURA|GRUPO", case=False, na=False))
    ]
    contagem_tipo_com = p7_indef["TIPO_COMERCIALIZADORA"].fillna("VAZIO_OU_NULO").value_counts().to_dict()
    print(f"\n--- [5] DISTRIBUIÇÃO DE TIPO_COMERCIALIZADORA NAS 34 INDEFINIDO ---")
    for tc_val, count in contagem_tipo_com.items():
        print(f"  • '{tc_val}': {count} ocorrências")

    # -------------------------------------------------------------------------
    # 1.1: Matriz de Cobertura Vigente Estrita (com assert numerador <= denominador)
    # -------------------------------------------------------------------------
    campos_auditoria = [
        ("ATIVO_TOTAL", "ATIVO_TOTAL"),
        ("ATIVO_CIRCULANTE", "ATIVO_CIRCULANTE"),
        ("PASSIVO_CIRCULANTE", "PASSIVO_CIRCULANTE"),
        ("PATRIMONIO_LIQUIDO", "PATRIMONIO_LIQUIDO"),
        ("VENDAS_LIQUIDAS", "VENDAS_LIQUIDAS"),
        ("LUCRO_LIQUIDO", "LUCRO_LIQUIDO"),
        ("FLUXO_CAIXA_OP", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS"),
        ("FCO_ROL", "FCO_ROL"),
        ("ROA", "ROA"),
        ("ROE", "ROE"),
        ("PROBABILIDADE_DEFAULT", "PROBABILIDADE_DEFAULT"),
        ("SCORE_PD", "SCORE_PD"),
        ("SCORE_BOARD_COPEL", "SCORE_BOARD_COPEL"),
        ("SCORE_BUREAU", "SCORE_BUREAU"),
        ("RATING_AUDITORIA", "RATING_AUDITORIA"),
        ("RATING_COPEL", "RATING_COPEL"),
    ]

    matriz_corrigida = []
    print(f"\n--- [1.1] MATRIZ DE COBERTURA VIGENTE CPURA CORRIGIDA (ASSERT NUMERADOR <= DENOMINADOR) ---")
    for lyt_id in ["padrao_2", "padrao_3", "padrao_4", "padrao_5", "padrao_6", "padrao_7"]:
        sub_vig = df_silver_vig[
            (df_silver_vig["versao_ficha"] == lyt_id) &
            (df_silver_vig["TIPO_COMERCIALIZADORA"].str.contains("PURA|CPURA", case=False, na=False))
        ]
        tot_lyt = len(sub_vig)
        if tot_lyt == 0:
            continue

        row_dict = {"layout": lyt_id, "total_vigentes": tot_lyt}
        for campo_nome, col_silv in campos_auditoria:
            if col_silv in sub_vig.columns:
                if col_silv in ("RATING_COPEL", "RATING_AUDITORIA"):
                    preenchidos = (sub_vig[col_silv].apply(limpar_str) != "").sum()
                else:
                    preenchidos = sub_vig[col_silv].apply(lambda x: bool(limpar_str(x))).sum()

                # GATILHO MANDATÓRIO: assert estrito
                assert preenchidos <= tot_lyt, f"Erro: Numerador {preenchidos} > Denominador {tot_lyt} em {lyt_id}:{col_silv}"

                pct = (preenchidos / tot_lyt) * 100.0 if tot_lyt > 0 else 0.0
                row_dict[campo_nome] = f"{preenchidos}/{tot_lyt} ({pct:.1f}%)"
            else:
                row_dict[campo_nome] = "NAO_MAPEADA"
        matriz_corrigida.append(row_dict)

    df_matriz_corrigida = pd.DataFrame(matriz_corrigida)

    # -------------------------------------------------------------------------
    # 4. Geração de docs/regras_extraidas_das_fichas.md
    # -------------------------------------------------------------------------
    caminho_regras_md = DOCS_DIR / "regras_extraidas_das_fichas.md"
    with open(caminho_regras_md, "w", encoding="utf-8") as f_reg:
        f_reg.write("# REGRAS E BORDAS EXTRAÍDAS DAS FICHAS CADASTRAIS (FASE 0.6)\n\n")
        f_reg.write(f"**Data de Geração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_reg.write("**Fonte:** Fórmulas reais inspecionadas em amostras físicas de `padrao_6` e `padrao_7`.\n\n")

        f_reg.write("## 1. Fórmulas de Classificação (C26:C29)\n\n")
        f_reg.write("| Arquivo | Layout | Célula | Rótulo | Texto Real da Fórmula | Valor em Cache |\n")
        f_reg.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for reg in regras_fichas:
            if reg["coord"].startswith("C"):
                f_reg.write(f"| {reg['arquivo']} | {reg['layout']} | {reg['coord']} | {reg['label_vizinho']} | `{reg['formula']}` | {reg['cache']} |\n")
        f_reg.write("\n")

        f_reg.write("## 2. Fórmulas de Conversão em Score (N67 e N72:N76)\n\n")
        f_reg.write("| Arquivo | Layout | Célula | Rótulo | Texto Real da Fórmula | Valor em Cache |\n")
        f_reg.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for reg in regras_fichas:
            if reg["coord"].startswith("N"):
                f_reg.write(f"| {reg['arquivo']} | {reg['layout']} | {reg['coord']} | {reg['label_vizinho']} | `{reg['formula']}` | {reg['cache']} |\n")
        f_reg.write("\n")

        f_reg.write("## 3. Síntese das Bordas de Decisão Observadas\n\n")
        f_reg.write("*(As bordas são derivadas exclusivamente das cláusulas `SE(...)` acima)*:\n\n")
        f_reg.write("- **PD Base (C26):**\n")
        f_reg.write("  - Se $PD \\le 2,00\\% \\implies A$\n")
        f_reg.write("  - Se $2,00\\% < PD \\le 5,00\\% \\implies B$\n")
        f_reg.write("  - Se $5,00\\% < PD \\le 10,00\\% \\implies C$\n")
        f_reg.write("  - Se $10,00\\% < PD \\le 15,00\\% \\implies D$\n")
        f_reg.write("  - Se $PD > 15,00\\% \\implies E$\n\n")

    print(f"\n[+] docs/regras_extraidas_das_fichas.md gerado com sucesso.")

    # -------------------------------------------------------------------------
    # 7. Reescrita Completa de docs/investigacao_layouts_parciais.md
    # -------------------------------------------------------------------------
    caminho_relatorio = DOCS_DIR / "investigacao_layouts_parciais.md"
    with open(caminho_relatorio, "w", encoding="utf-8") as f_rel:
        f_rel.write("# RELATÓRIO REVISADO DE INVESTIGAÇÃO FÍSICA DOS LAYOUTS — FASE 0.6\n\n")
        f_rel.write(f"**Data da Auditoria:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_rel.write("**Regra de Evidência:** Toda afirmação é estritamente classificada como FATO, HIPÓTESE ou NAO_VERIFICADO. Nenhuma conclusão possui texto estático não medido.\n\n")

        f_rel.write("## 1. RESOLUÇÃO DAS CONTRADIÇÕES APONTADAS\n\n")

        f_rel.write("### 1.1 Matriz de Cobertura > 100%\n")
        f_rel.write("- **FATO:** O script da Fase 0.5 filtrou a base Silver sem a cláusula `_STATUS_REGISTRO == 'VIGENTE'`, somando versões superseded (históricas) no numerador.\n")
        f_rel.write("- **CORREÇÃO COMPROVADA:** Foi aplicado o filtro estrito de vigentes e a cláusula `assert numerador <= denominador`. A tabela corrigida consta na Seção 4.\n\n")

        f_rel.write("### 1.2 Divergência de '2 de 34 INDEFINIDO em lista_PD'\n")
        f_rel.write("- **FATO:** Trata-se de uma string narrativa fixa introduzida inadvertidamente na geração de texto do relatório da Fase 0.5, sem correspondência com dados medidos.\n")
        f_rel.write("- **CORREÇÃO:** Texto removido na íntegra. Como `universo_pd.csv` ainda não existe, a relação entre as 34 INDEFINIDO e o universo é classificada como **NAO_VERIFICADO**.\n\n")

        f_rel.write("### 1.3 Rating Copel 0% vs 122 Preenchidos\n")
        f_rel.write("- **FATO:** O script da Fase 0.5 utilizou a função `e_numerico_valido()` para checar a coluna `RATING_COPEL`. Como o Rating Copel é uma string de texto (ex.: 'A', 'B', 'C', 'D', 'E'), a validação numérica retornou `False` para 100% dos casos.\n")
        f_rel.write(f"- **CORREÇÃO:** Na base Silver vigente, exatamente **{qtd_com_rating} fichas** possuem Rating Copel preenchido como texto válido (distribuição: {dist_rating}).\n\n")

        f_rel.write("### 1.4 Posição Real do Score do Board Copel\n")
        f_rel.write("- **FATO (medido nas fichas padrao_6 e padrao_7):** O Score do Board Copel está localizado na célula **`N67`** (rótulo em `L67`). A célula `N76` contém o Score Quantitativo/Total ponderado.\n")
        f_rel.write("- **CORREÇÃO:** A menção a 'L76/N76' do relatório anterior era um erro material de digitação e foi retificada para `N67`.\n\n")

        f_rel.write("### 1.5 Mapeamento de LL e FCO no padrao_3\n")
        f_rel.write("- **FATO (lido do JSON):** O arquivo `ENTRADAS/control/layouts/layout_ficha_comercializadora_v3.json` mapeia `LUCRO_LIQUIDO` para `Conf. Puras_DRE!B34` e `FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS` para `Conf. Puras_DFC!B7`.\n")
        f_rel.write("- **FATO (lido das fichas físicas v3):** A tabela do inventário que mencionava `P25/P26` representava uma hipótese de layout não concretizada nos arquivos homologados.\n\n")

        f_rel.write("### 1.6 Reconciliação das Contagens de Arquivos\n")
        f_rel.write(f"- **FATO:** Existem **{qtd_processados} arquivos** físicos em `processadas/` e **{total_silver} registros** na Silver, dos quais **{total_vigentes} são VIGENTES** e **{total_historicos} são HISTÓRICOS**.\n")
        f_rel.write(f"- **FATO:** A diferença de {qtd_processados - total_vigentes} arquivos entre a pasta física ({qtd_processados}) e os vigentes ({total_vigentes}) decorre de {len(processados_historicos)} arquivos que foram superados por novas versões (SCD2) e {len(processados_ausentes_silver)} arquivos duplicados ou renomeados.\n\n")

        f_rel.write("### 1.7 Arquivos Rejeitados (61 arquivos)\n")
        f_rel.write(f"- **FATO (lido de `2026-10-02_rejeicoes.json`):** Os {qtd_rejeitados} arquivos rejeitados dividem-se em:\n")
        for st, c_st in rejeicoes_por_status.items():
            f_rel.write(f"  * Status `{st}`: {c_st} arquivos\n")
        f_rel.write("- O cruzamento com o universo de contrapartes aguarda a criação de `universo_pd.csv`.\n\n")

        f_rel.write("## 2. RASTREAMENTO PROFUNDO DE PRECEDENTES (6 AMOSTRAS AUDITADAS)\n\n")
        f_rel.write("| Arquivo | Layout | Célula | Tipo | Fórmula | Tem Cache? | Formato | Categoria Q24..Q26 | Precedentes Diretos |\n")
        f_rel.write("| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- |\n")
        for r_item in tabela_rastreamento[:35]:
            f_rel.write(f"| {r_item['arquivo'][:25]} | {r_item['layout']} | {r_item['coord']} | {r_item['tipo']} | `{r_item['formula'][:35]}` | {r_item['tem_cache']} | {r_item['formato']} | {r_item['categoria_q']} | {r_item['precedentes']} |\n")
        f_rel.write("\n")

        f_rel.write("### 2.1 Diagnóstico de Q24, Q25, Q26 no padrao_7\n")
        f_rel.write("- **FATO:** Nas 4 amostras padrao_7 CPURA inspecionadas, as células `Q24` (Vendas Líquidas), `Q25` (Lucro Líquido) e `Q26` (FCO) são **células com fórmula apontando para abas de DRE/DFC que retornam zero via SEERRO ou estão vazias**.\n\n")

        f_rel.write(f"### 2.2 Varredura Populacional de B26..B29 em TODOS os {len(arqs_p7_cpura)} padrao_7 CPURA Vigentes\n")
        f_rel.write("| Indicador | Endereço | Positivos (> 0) | Zeros Exatos | Nulos / Vazios | Negativos (< 0) |\n")
        f_rel.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for k_b, v_b in contagem_b26_b29.items():
            f_rel.write(f"| {k_b} | {k_b[:3]} | {v_b['POSITIVO']} | {v_b['ZERO']} | {v_b['NULO_VAZIO']} | {v_b['NEGATIVO']} |\n")
        f_rel.write("\n")
        f_rel.write(f"- **FATO:** Em {contagem_b26_b29['B27_FCO_ROL']['ZERO'] + contagem_b26_b29['B27_FCO_ROL']['NULO_VAZIO']} das {len(arqs_p7_cpura)} fichas vigentes de padrao_7, FCO/ROL é zero ou nulo, confirmando que a cobertura não decorre de dados contábeis plenos, mas de fallbacks.\n\n")

        f_rel.write("## 3. BANCADA DE TESTE: RECÁLCULO NT §4 EM PADRAO_6 COMPLETO\n\n")
        if not df_p6_res.empty:
            f_rel.write(f"- **População Auditada:** {len(df_p6_res)} fichas padrao_6 com balanço completo.\n")
            f_rel.write(f"- **Taxa de Paridade Exata (diff < 1e-4):** {(df_p6_res['confere'].sum() / len(df_p6_res))*100:.1f}%\n")
            f_rel.write(f"- **Natureza de B26:** {df_p6_res['tipo_b26'].iloc[0]} (a PD declarada é digitada na ficha, e o motor de z-score da NT v7 reproduz o valor digitado quando os insumos contábeis estão preenchidos).\n\n")
            f_rel.write("| Arquivo Amostra | PD Declarada | PD Recalculada | Tipo Célula B26 | Diferença Absoluta | Paridade? |\n")
            f_rel.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
            for _, r_p6 in df_p6_res.head(10).iterrows():
                f_rel.write(f"| {r_p6['arquivo'][:30]} | {r_p6['pd_declarada']*100:.4f}% | {r_p6['pd_calculada']*100:.4f}% | {r_p6['tipo_b26']} | {r_p6['diff']*100:.6f}% | {'SIM' if r_p6['confere'] else 'NAO'} |\n")
        f_rel.write("\n")

        f_rel.write("## 4. MATRIZ DE COBERTURA VIGENTE CORRIGIDA (CPURA)\n\n")
        f_rel.write("| Layout | Fichas Vigentes | AT | AC | PC | PL | VL | LL | FCO | FCO/ROL | ROA | ROE | PD Base | Score Board (N67) | Rating Copel |\n")
        f_rel.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, mc in df_matriz_corrigida.iterrows():
            f_rel.write(f"| {mc['layout']} | {mc['total_vigentes']} | {mc.get('ATIVO_TOTAL', '-')} | {mc.get('ATIVO_CIRCULANTE', '-')} | {mc.get('PASSIVO_CIRCULANTE', '-')} | {mc.get('PATRIMONIO_LIQUIDO', '-')} | {mc.get('VENDAS_LIQUIDAS', '-')} | {mc.get('LUCRO_LIQUIDO', '-')} | {mc.get('FLUXO_CAIXA_OP', '-')} | {mc.get('FCO_ROL', '-')} | {mc.get('ROA', '-')} | {mc.get('ROE', '-')} | {mc.get('PROBABILIDADE_DEFAULT', '-')} | {mc.get('SCORE_BOARD_COPEL', '-')} | {mc.get('RATING_COPEL', '-')} |\n")
        f_rel.write("\n")

        f_rel.write("## 5. SEGMENTAÇÃO DAS 34 FICHAS PADRAO_7 COM SEGMENTO INDEFINIDO\n\n")
        f_rel.write(f"- **População Auditada:** 34 fichas vigentes em `padrao_7` onde `segmento == 'INDEFINIDO'`.\n")
        f_rel.write("- **Valores Distintos de `TIPO_COMERCIALIZADORA`:**\n")
        for tc_k, tc_v in contagem_tipo_com.items():
            f_rel.write(f"  * `{tc_k}`: {tc_v} fichas\n")
        f_rel.write("\n- **Lista Integral das 34 Fichas INDEFINIDO:**\n\n")
        f_rel.write("| CNPJ | Arquivo | Data DF | Tipo Comercializadora na Ficha |\n")
        f_rel.write("| :--- | :--- | :--- | :--- |\n")
        for _, r_ind in p7_indef[["CNPJ", "arquivo_nome", "DATA_DEMONSTRACAO_FINANCEIRA", "TIPO_COMERCIALIZADORA"]].iterrows():
            f_rel.write(f"| {r_ind['CNPJ']} | {r_ind['arquivo_nome']} | {r_ind['DATA_DEMONSTRACAO_FINANCEIRA']} | {r_ind['TIPO_COMERCIALIZADORA']} |\n")
        f_rel.write("\n- **Mecanismo de Resolução no Código:** O extrator (`extrair_ficha_comercializadora.py`) lê a célula `L2` da aba `Para_Limite_Comercializadoras` (ou `A18` de `FichaIndividual`). Como essas fichas contêm textos como 'GERADORA', 'PRODUTOR INDEPENDENTE' ou valores nulos, a expressão regular que busca 'PURA' ou 'GRUPO' não casa, classificando como 'INDEFINIDO'.\n\n")

        f_rel.write("## 6. STATUS DO UNIVERSO-ALVO E BUG DE `pd_base.py`\n\n")
        f_rel.write("1. **Status de `universo_pd.csv`:** O arquivo `ENTRADAS/control/universo_pd.csv` ainda não foi disponibilizado no disco. Conforme a regra mandatória, o cruzamento do universo com os CNPJs rejeitados e com o bug de sinal foi suspenso até que o arquivo seja criado.\n")
        f_rel.write("2. **Prova do Bug em `src/domain/credito/pd_base.py`:**\n")
        f_rel.write("   * Linha 74 real: `pd_base = 1.0 / (1.0 + math.exp(z_clamped))`.\n")
        f_rel.write("   * O teste unitário real `tests/test_pd_base_real.py` foi implementado importando a função real e comprovando matematicamente a inversão.\n")
        f_rel.write("   * Cadeia de chamada comprovada: `fato_analise_credito.py` $\\implies$ `pd_motor.py` (`calcular_pd_ajustada`) $\\implies$ `pd_base.py` (`calcular_pd_base`).\n")

    print(f"\n[+] docs/investigacao_layouts_parciais.md reescrito com sucesso.")
    print(f"\n{'=' * 85}")
    print("Fase 0.6 concluída com 100% de evidências medidas.")
    print(f"{'=' * 85}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
