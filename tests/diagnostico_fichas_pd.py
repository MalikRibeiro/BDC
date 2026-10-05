"""Script de diagnóstico e auditoria profunda de fichas cadastrais e PDs.

Investiga:
1. Divergência entre lista_PD_manual.xlsx e lista_PD_enriquecida.xlsx.
2. Causa da falha de leitura em ARAMART 28072026.xlsx (CNPJ 13416922000126).
3. Causa da falha de leitura em CASA DOS VENTOS 30072026.xlsx e perda da PD.
4. Vistoria em lote das fichas dos ~42 casos divergentes.
5. Diagnóstico de corrupção de CNPJ em 'Controladora e Subsidiaria.csv'.
"""
from __future__ import annotations

import sys
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
import openpyxl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.bootstrap import carregar_contexto
from common.identificadores import normalizar_cnpj_coluna
from common.excel import abrir_pasta, fechar_pasta
from common.json import ler_json
from domain.fichas.extrator import LeitorPlanilha, avaliar_vencedor_por_grid
from control.layout_catalog import carregar_layouts_comercializadoras, carregar_layouts_consumidores
from control.quality_loader import (
    carregar_regras_de_qualidade_de_dados_comercializadoras,
    carregar_regras_de_qualidade_de_dados_consumidores,
    obter_limiar_integridade_fichas
)


def inspecionar_celulas_planilha(wb: openpyxl.Workbook, termos_busca: list[str]) -> list[dict]:
    """Varre todas as abas da planilha buscando células que contenham termos-chave."""
    encontrados = []
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        for row in range(1, min(ws.max_row or 100, 100) + 1):
            for col in range(1, min(ws.max_column or 30, 30) + 1):
                val = ws.cell(row=row, column=col).value
                if val is not None:
                    str_val = str(val).strip()
                    val_lower = str_val.lower()
                    for termo in termos_busca:
                        if termo.lower() in val_lower:
                            # Tentar obter valor da célula adjacente (à direita ou abaixo)
                            val_direita = ws.cell(row=row, column=col + 1).value
                            val_abaixo = ws.cell(row=row + 1, column=col).value
                            encontrados.append({
                                "aba": sheet_name,
                                "celula": f"{openpyxl.utils.get_column_letter(col)}{row}",
                                "termo": termo,
                                "rotulo": str_val[:50],
                                "valor_direita": val_direita,
                                "celula_direita": f"{openpyxl.utils.get_column_letter(col + 1)}{row}",
                                "valor_abaixo": val_abaixo,
                                "celula_abaixo": f"{openpyxl.utils.get_column_letter(col)}{row + 1}"
                            })
                            break
    return encontrados


def main() -> int:
    print(f"\n{'=' * 80}")
    print(f"🔬 BDC - DIAGNÓSTICO PROFUNDO DE EXTRAÇÃO DE FICHAS E PDS")
    print(f"{'=' * 80}")

    ctx = carregar_contexto(PROJECT_ROOT / "ENTRADAS" / "configs")
    limiar = obter_limiar_integridade_fichas(ctx)
    print(f"[*] Limiar mínimo de integridade configurado: {limiar:.1f}%\n")

    # --------------------------------------------------------------------------
    # 1. COMPARAÇÃO: lista_PD_manual.xlsx vs lista_PD_enriquecida.xlsx
    # --------------------------------------------------------------------------
    print(f"{'=' * 80}")
    print(f"1. AUDITORIA: lista_PD_manual.xlsx vs lista_PD_enriquecida.xlsx")
    print(f"{'=' * 80}")

    path_manual = PROJECT_ROOT / "SAIDAS" / "exportacoes" / "lista_PD_manual.xlsx"
    path_enriq = PROJECT_ROOT / "SAIDAS" / "exportacoes" / "lista_PD_enriquecida.xlsx"

    divergentes = []
    if not path_manual.exists() or not path_enriq.exists():
        print(f"[!] Arquivos de lista não encontrados em SAIDAS/exportacoes:")
        print(f"    - manual: {path_manual.exists()} ({path_manual})")
        print(f"    - enriq:  {path_enriq.exists()} ({path_enriq})")
    else:
        df_man = pd.read_excel(path_manual, dtype=str)
        df_enr = pd.read_excel(path_enriq, dtype=str)

        # Encontrar coluna CNPJ
        col_c_man = [c for c in df_man.columns if "CNPJ" in str(c).upper()][0]
        col_c_enr = [c for c in df_enr.columns if "CNPJ" in str(c).upper()][0]

        df_man["_CNPJ_NORM"] = df_man[col_c_man].apply(normalizar_cnpj_coluna)
        df_enr["_CNPJ_NORM"] = df_enr[col_c_enr].apply(normalizar_cnpj_coluna)

        dict_enr = df_enr.set_index("_CNPJ_NORM").to_dict(orient="index")

        # Coluna de PD e Rating na manual
        col_pd_man = [c for c in df_man.columns if "PD" in str(c).upper()]
        col_rtg_man = [c for c in df_man.columns if "RATING" in str(c).upper()]

        print(f"    Total linhas manual: {len(df_man)} | Total linhas enriquecida: {len(df_enr)}")

        for _, row in df_man.iterrows():
            cnpj = row["_CNPJ_NORM"]
            enr_row = dict_enr.get(cnpj, {})

            # Verificar se manual tem valor
            val_pd_man = None
            for cp in col_pd_man:
                v = row.get(cp)
                if v and str(v).strip() not in ("", "None", "nan", "<NA>", "-"):
                    val_pd_man = str(v).strip()
                    break

            val_rtg_man = None
            for cr in col_rtg_man:
                v = row.get(cr)
                if v and str(v).strip() not in ("", "None", "nan", "<NA>", "-"):
                    val_rtg_man = str(v).strip()
                    break

            # Verificar valor na enriquecida
            pd_enr = enr_row.get("PD_VIGENTE_FORMATADA") or enr_row.get("ULTIMA_PD_FORMATADA")
            rtg_enr = enr_row.get("RATING_VIGENTE") or enr_row.get("ULTIMO_RATING_CALCULADO")

            tem_na_manual = (val_pd_man is not None and val_pd_man != "-") or (val_rtg_man is not None and val_rtg_man != "-")
            faltou_na_enr = (pd_enr is None or pd_enr == "-") and (rtg_enr is None or rtg_enr == "-")

            if tem_na_manual and faltou_na_enr:
                col_nome_cand = [c for c in df_man.columns if any(k in str(c).upper() for k in ["NOME", "CONTRAPARTE", "RAZAO"])][0]
                divergentes.append({
                    "CNPJ": cnpj,
                    "CONTRAPARTE": row.get(col_nome_cand, ""),
                    "PD_MANUAL": val_pd_man,
                    "RATING_MANUAL": val_rtg_man,
                    "OBS": row.get("OBS", "") if "OBS" in row else ""
                })

        print(f"    [DIVERGÊNCIA IDENTIFICADA] {len(divergentes)} contrapartes têm dados na manual mas vieram vazias no BDC!")
        if divergentes:
            print(f"\n    Amostra dos 10 primeiros casos divergentes:")
            for d in divergentes[:10]:
                print(f"      • CNPJ {d['CNPJ']} | {d['CONTRAPARTE'][:30]:30s} | PD_MANUAL={d['PD_MANUAL']} | RATING_MANUAL={d['RATING_MANUAL']}")

    # --------------------------------------------------------------------------
    # 2. CASO 1: ARAMART (CNPJ 13416922000126)
    # --------------------------------------------------------------------------
    print(f"\n{'=' * 80}")
    print(f"2. DIAGNÓSTICO DO CASO ARAMART (CNPJ 13416922000126)")
    print(f"{'=' * 80}")

    arquivo_aramart = PROJECT_ROOT / "ENTRADAS" / "fichas" / "consumidores" / "processadas" / "ARAMART 28072026.xlsx"
    if not arquivo_aramart.exists():
        # Buscar recursivamente
        cands = list(PROJECT_ROOT.glob("**/ARAMART*.xlsx"))
        if cands:
            arquivo_aramart = cands[0]

    if not arquivo_aramart.exists():
        print(f"[!] Arquivo de ARAMART não localizado.")
    else:
        print(f"[*] Analisando arquivo: {arquivo_aramart}")
        wb = openpyxl.load_workbook(arquivo_aramart, data_only=True)
        print(f"    Abas na planilha: {wb.sheetnames}")
        print(f"    Aba ativa: {wb.active.title if wb.active else 'Nenhuma'}")

        # Inspecionar células-chave
        termos = ["cnpj", "rating", "nota", "probabilidade", "pd", "balanço", "demonstração", "ativo total", "patrimônio líquido"]
        celulas = inspecionar_celulas_planilha(wb, termos)
        print(f"\n    Rótulos e células identificadas na planilha real:")
        for c in celulas[:15]:
            print(f"      - Aba '{c['aba']}' | Célula {c['celula']}: '{c['rotulo']}' ➔ Direita ({c['celula_direita']}): '{c['valor_direita']}' | Abaixo ({c['celula_abaixo']}): '{c['valor_abaixo']}'")

        # Testar execução do extrator oficial de consumidores
        print(f"\n    Testando extrator BDC com layouts de consumidores:")
        from control.logger import obter_logger
        logger_diag = obter_logger("diag.fichas")
        layouts_cons = carregar_layouts_consumidores(ctx, logger_diag)
        cat_cons = carregar_regras_de_qualidade_de_dados_consumidores(ctx, logger_diag)

        leitor_ara = LeitorPlanilha.do_workbook(wb)
        dados_ara, meta_ara, layout_ara = avaliar_vencedor_por_grid(leitor_ara, layouts_cons, cat_cons)

        print(f"    ➔ Layout vencedor detectado: '{layout_ara}'")
        print(f"    ➔ Integridade extraída: {dados_ara.get('INTEGRIDADE_EXTRAIDA_PERCENTUAL', 0)}%")
        print(f"    ➔ CNPJ extraído: {dados_ara.get('CNPJ')}")
        print(f"    ➔ RATING extraído: {dados_ara.get('RATING_COPEL') or dados_ara.get('NOTA_CREDITO') or dados_ara.get('RATING')}")
        print(f"    ➔ DATA DEMONSTRAÇÃO: {dados_ara.get('DATA_DEMONSTRACAO_FINANCEIRA')}")
        print(f"    ➔ ATIVO TOTAL: {dados_ara.get('ATIVO_TOTAL')}")
        print(f"    ➔ PATRIMÔNIO LÍQUIDO: {dados_ara.get('PATRIMONIO_LIQUIDO')}")

        # Inspecionar exatamente as linhas 12 a 22 da coluna H até N (Balanço em ARAMART)
        print(f"\n    [RAIO-X BALANÇO ARAMART] Linhas 12 a 22 da aba 'Dados Gerais e Qualitativos':")
        ws_ara = wb["Dados Gerais e Qualitativos"]
        for r in range(12, 23):
            valores_linha = [f"{openpyxl.utils.get_column_letter(c)}{r}:{ws_ara.cell(row=r, column=c).value}" for c in range(8, 15) if ws_ara.cell(row=r, column=c).value is not None]
            if valores_linha:
                print(f"      Linha {r:2d}: {' | '.join(valores_linha)}")

        # Se falhou, detalhar onde o padrao_2 procura cada campo
        if "padrao_2" in layouts_cons:
            fm = layouts_cons["padrao_2"].get("field_map", {})
            print(f"\n    Onde o 'padrao_2' procura campos essenciais:")
            for campo in ["CNPJ", "RATING_COPEL", "NOTA_CREDITO", "DATA_DEMONSTRACAO_FINANCEIRA", "ATIVO_TOTAL", "PATRIMONIO_LIQUIDO"]:
                cfg = fm.get(campo, {})
                cel = cfg.get("value_cell") or cfg.get("cell")
                sheet = cfg.get("sheet")
                raw = leitor_ara.ler_celula(sheet or leitor_ara.aba_ativa, cel) if cel else None
                print(f"      - {campo:30s}: aba='{sheet}' celula='{cel}' ➔ Valor encontrado na célula: '{raw}'")

    # --------------------------------------------------------------------------
    # 3. CASO 2: CASA DOS VENTOS (comercializadoras)
    # --------------------------------------------------------------------------
    print(f"\n{'=' * 80}")
    print(f"3. DIAGNÓSTICO DO CASO CASA DOS VENTOS")
    print(f"{'=' * 80}")

    arquivo_cdv = PROJECT_ROOT / "ENTRADAS" / "fichas" / "comercializadoras" / "processadas" / "CASA DOS VENTOS 30072026.xlsx"
    if not arquivo_cdv.exists():
        cands = list(PROJECT_ROOT.glob("**/CASA DOS VENTOS*.xlsx"))
        if cands:
            arquivo_cdv = cands[0]

    if not arquivo_cdv.exists():
        print(f"[!] Arquivo CASA DOS VENTOS não localizado.")
    else:
        print(f"[*] Analisando arquivo: {arquivo_cdv}")
        wb_cdv = openpyxl.load_workbook(arquivo_cdv, data_only=True)
        print(f"    Abas na planilha: {wb_cdv.sheetnames}")
        print(f"    Aba ativa: {wb_cdv.active.title if wb_cdv.active else 'Nenhuma'}")

        termos_cdv = ["pd", "probabilidade", "default", "rating", "score", "balanço", "ativo", "patrimônio"]
        celulas_cdv = inspecionar_celulas_planilha(wb_cdv, termos_cdv)
        print(f"\n    Rótulos e células de PD/Rating na planilha real:")
        for c in celulas_cdv[:15]:
            print(f"      - Aba '{c['aba']}' | Célula {c['celula']}: '{c['rotulo']}' ➔ Direita ({c['celula_direita']}): '{c['valor_direita']}' | Abaixo ({c['celula_abaixo']}): '{c['valor_abaixo']}'")

        # Testar extrator com layouts de comercializadoras
        layouts_com = carregar_layouts_comercializadoras(ctx, logger_diag)
        cat_com = carregar_regras_de_qualidade_de_dados_comercializadoras(ctx, logger_diag)

        leitor_cdv = LeitorPlanilha.do_workbook(wb_cdv)
        dados_cdv, meta_cdv, layout_cdv = avaliar_vencedor_por_grid(leitor_cdv, layouts_com, cat_com)

        print(f"\n    ➔ Layout vencedor detectado: '{layout_cdv}'")
        print(f"    ➔ Integridade extraída: {dados_cdv.get('INTEGRIDADE_EXTRAIDA_PERCENTUAL', 0)}%")
        print(f"    ➔ CNPJ extraído: {dados_cdv.get('CNPJ')}")
        print(f"    ➔ RATING extraído: {dados_cdv.get('RATING_COPEL') or dados_cdv.get('NOTA_CREDITO') or dados_cdv.get('RATING')}")
        print(f"    ➔ PROBABILIDADE_DEFAULT extraída: {dados_cdv.get('PROBABILIDADE_DEFAULT')}")
        print(f"    ➔ PD_FINAL extraída: {dados_cdv.get('PD_FINAL')}")

        if "padrao_7" in layouts_com:
            fm7 = layouts_com["padrao_7"].get("field_map", {})
            print(f"\n    Onde o 'padrao_7' procura PD e Balanço:")
            for campo in ["PROBABILIDADE_DEFAULT", "RATING_COPEL", "ATIVO_TOTAL", "PATRIMONIO_LIQUIDO", "DATA_DEMONSTRACAO_FINANCEIRA"]:
                cfg = fm7.get(campo, {})
                cel = cfg.get("value_cell") or cfg.get("cell")
                sheet = cfg.get("sheet")
                raw = leitor_cdv.ler_celula(sheet or leitor_cdv.aba_ativa, cel) if cel else None
                print(f"      - {campo:30s}: aba='{sheet}' celula='{cel}' ➔ Valor lido: '{raw}'")

        if "padrao_6" in layouts_com:
            fm6 = layouts_com["padrao_6"].get("field_map", {})
            print(f"\n    Onde o 'padrao_6' procura PD e Rating:")
            for campo in ["PROBABILIDADE_DEFAULT", "PD_FINAL", "RATING_COPEL", "NOTA_CREDITO", "SCORE_FINAL", "DATA_DEMONSTRACAO_FINANCEIRA"]:
                cfg = fm6.get(campo, {})
                cel = cfg.get("value_cell") or cfg.get("cell")
                sheet = cfg.get("sheet")
                raw = leitor_cdv.ler_celula(sheet or leitor_cdv.aba_ativa, cel) if cel else None
                print(f"      - {campo:30s}: aba='{sheet}' celula='{cel}' ➔ Valor lido: '{raw}'")

    # --------------------------------------------------------------------------
    # 4. INVESTIGAÇÃO EM LOTE DOS CASOS DIVERGENTES (EXISTÊNCIA DE FICHAS)
    # --------------------------------------------------------------------------
    print(f"\n{'=' * 80}")
    print(f"4. VARREDURA EM LOTE: LOCALIZANDO FICHAS DAS 49 CONTRAPARTES DIVERGENTES")
    print(f"{'=' * 80}")

    # Indexar todas as fichas no disco por CNPJ ou nome no título
    todas_fichas = list((PROJECT_ROOT / "ENTRADAS" / "fichas").rglob("*.xlsx"))
    print(f"[*] Total de arquivos .xlsx encontrados em ENTRADAS/fichas: {len(todas_fichas)}")

    # Carregar Fato de Análise de Crédito consolidada para checar status
    path_fato = PROJECT_ROOT / "SAIDAS" / "relational" / "facts" / "credito" / "fato_analise_credito.parquet"
    df_fato = pd.read_parquet(path_fato) if path_fato.exists() else pd.DataFrame()
    if not df_fato.empty:
        df_fato["_CNPJ_NORM"] = df_fato["CNPJ"].apply(normalizar_cnpj_coluna)

    resumo_divergentes = []
    for d in divergentes:
        cnpj_alvo = d["CNPJ"]
        nome_alvo = d["CONTRAPARTE"]

        # 1. Procurar ficha pelo CNPJ no nome do arquivo ou conteúdo
        fichas_encontradas = []
        for f in todas_fichas:
            f_str = f.name.upper()
            # Testar se o CNPJ está no nome
            if cnpj_alvo in f_str or (cnpj_alvo[:8] in f_str and len(cnpj_alvo[:8]) >= 8):
                fichas_encontradas.append(f)
            # Testar primeiros termos do nome
            primeiro_termo = str(nome_alvo).strip().split(" ")[0].upper()
            if len(primeiro_termo) > 3 and primeiro_termo in f_str:
                if f not in fichas_encontradas:
                    fichas_encontradas.append(f)

        # 2. Checar se está na Silver / Fato
        status_fato = "NÃO_CONSTA_FATO"
        if not df_fato.empty:
            registros_fato = df_fato[df_fato["_CNPJ_NORM"] == cnpj_alvo]
            if not registros_fato.empty:
                ult = registros_fato.iloc[-1]
                status_fato = f"FATO: Rating={ult.get('RATING')} | PD={ult.get('PD_PERCENTUAL')} | StatCalc={ult.get('STATUS_CALCULO_PD')} | Tipo={ult.get('TIPO_ANALISE')}"

        resumo_divergentes.append({
            "CNPJ": cnpj_alvo,
            "CONTRAPARTE": nome_alvo[:30],
            "PD_MANUAL": d["PD_MANUAL"],
            "FICHAS_ACHADAS": [f.name for f in fichas_encontradas[:2]],
            "STATUS_FATO": status_fato
        })

    print(f"\n    Status cadastral e documental dos casos divergentes (amostra de 15):")
    for r in resumo_divergentes[:15]:
        print(f"      • CNPJ {r['CNPJ']} ({r['CONTRAPARTE']})")
        print(f"        - Fichas localizadas no disco: {r['FICHAS_ACHADAS'] if r['FICHAS_ACHADAS'] else 'NENHUMA FICHA COM ESSE NOME/CNPJ'}")
        print(f"        - Situação na Fato de Crédito: {r['STATUS_FATO']}")

    # --------------------------------------------------------------------------
    # 5. DIAGNÓSTICO: 'Controladora e Subsidiaria' (.xlsx e .csv)
    # --------------------------------------------------------------------------
    print(f"\n{'=' * 80}")
    print(f"5. DIAGNÓSTICO DE 'Controladora e Subsidiaria'")
    print(f"{'=' * 80}")

    arquivo_ctrl_xlsx = PROJECT_ROOT / "ENTRADAS" / "controlador" / "Controladora e Subsidiaria.xlsx"
    arquivo_ctrl_csv = PROJECT_ROOT / "ENTRADAS" / "controlador" / "Controladora e Subsidiaria.csv"

    if arquivo_ctrl_xlsx.exists():
        print(f"[OK] Arquivo XLSX detectado: {arquivo_ctrl_xlsx.name}")
        df_x = pd.read_excel(arquivo_ctrl_xlsx, dtype=str)
        print(f"     Total de linhas carregadas: {len(df_x)}")
        print(f"     Colunas: {list(df_x.columns)}")
        for col in [c for c in df_x.columns if "CNPJ" in str(c).upper()]:
            amostra_cnpjs = df_x[col].dropna().head(3).tolist()
            print(f"     Amostra coluna '{col}': {amostra_cnpjs}")
            com_e = df_x[df_x[col].astype(str).str.contains("E\\+", na=False, regex=True)]
            if not com_e.empty:
                print(f"     [ALERTA] Coluna '{col}' possui {len(com_e)} linhas com notação científica!")
            else:
                print(f"     [SUCESSO] Coluna '{col}' imune a notação científica (0 linhas com E+).")

    if arquivo_ctrl_csv.exists():
        print(f"\n[*] Analisando linhas brutas do CSV legado: {arquivo_ctrl_csv.name}")
        linhas_corrompidas = []
        with open(arquivo_ctrl_csv, "r", encoding="utf-8-sig", errors="replace") as f:
            cabecalho = f.readline().strip()
            for idx, linha in enumerate(f, start=2):
                linha_clean = linha.strip()
                if re.search(r"\b\d+\.?\d*[eE]\+\d+\b", linha_clean) or "00000000" in linha_clean or "358356" in linha_clean:
                    linhas_corrompidas.append((idx, linha_clean))

        print(f"    Cabeçalho: {cabecalho}")
        print(f"    Linhas com suspeita de notação científica ou truncamento no CSV: {len(linhas_corrompidas)}")

    print(f"\n{'=' * 80}")
    print(f"DIAGNÓSTICO CONCLUÍDO. Copie e cole os outputs deste teste para a validação.")
    print(f"{'=' * 80}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
