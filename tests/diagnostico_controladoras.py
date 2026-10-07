"""Diagnóstico investigativo sobre a base de controladoras homologadas e cruzamentos reais."""
import pandas as pd
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from common.identificadores import normalizar_cnpj_coluna

def main():
    silver_dir = PROJECT_ROOT / "SAIDAS" / "silver"
    rel_dir = PROJECT_ROOT / "SAIDAS" / "relational"

    ctrl_path = silver_dir / "mapeamento_controladoras" / "mapeamento_controladoras.parquet"
    df_ctrl = pd.read_parquet(ctrl_path) if ctrl_path.exists() else pd.DataFrame()
    print(f"[+] Total de linhas em mapeamento_controladoras: {len(df_ctrl)}")
    print("Colunas:", df_ctrl.columns.tolist() if not df_ctrl.empty else "VAZIO")
    if not df_ctrl.empty:
        print("\nPrimeiros 5 registros de mapeamento_controladoras:")
        print(df_ctrl[["CNPJ_SUBSIDIARIA", "CNPJ_CONTA_ATRELADA", "SUBSIDIARIA", "CONTA_ATRELADA"]].head(5))

    # Verificar contratos correntes
    ctr_path = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    df_ctr = pd.read_parquet(ctr_path) if ctr_path.exists() else pd.DataFrame()
    print(f"\n[+] Total de linhas em contratos_correntes: {len(df_ctr)}")
    col_cnpj = "CONTRAPARTE_CNPJ" if "CONTRAPARTE_CNPJ" in df_ctr.columns else "CNPJ"
    df_ctr["CNPJ_NORM"] = df_ctr[col_cnpj].apply(normalizar_cnpj_coluna)
    cnpjs_contratos = set(df_ctr["CNPJ_NORM"].dropna().unique())
    print(f"[+] CNPJs distintos em contratos_correntes: {len(cnpjs_contratos)}")

    # Verificar fato analise credito
    fato_path = rel_dir / "facts" / "credito" / "fato_analise_credito.parquet"
    df_fato = pd.read_parquet(fato_path) if fato_path.exists() else pd.DataFrame()
    print(f"\n[+] Total de linhas em fato_analise_credito: {len(df_fato)}")
    if not df_fato.empty and "CNPJ" in df_fato.columns:
        df_fato["CNPJ_NORM"] = df_fato["CNPJ"].apply(normalizar_cnpj_coluna)
        print("Distribuição de ORIGEM_FONTE na fato:")
        if "ORIGEM_FONTE" in df_fato.columns:
            print(df_fato["ORIGEM_FONTE"].value_counts(dropna=False))
        if "TIPO_ANALISE" in df_fato.columns:
            print("\nDistribuição de TIPO_ANALISE na fato:")
            print(df_fato["TIPO_ANALISE"].value_counts(dropna=False))

    # Cruzar subsidiárias com contratos e com fatos
    if not df_ctrl.empty:
        subs = set(df_ctrl["CNPJ_SUBSIDIARIA"].apply(normalizar_cnpj_coluna).dropna().unique())
        ctrls = set(df_ctrl["CNPJ_CONTA_ATRELADA"].apply(normalizar_cnpj_coluna).dropna().unique())
        print(f"\n[+] Subsidiárias distintas na planilha: {len(subs)}")
        print(f"[+] Controladoras distintas na planilha: {len(ctrls)}")
        print(f"  • Quantas subsidiárias estão nos contratos? {len(subs.intersection(cnpjs_contratos))}")
        print(f"  • Quantas controladoras estão nos contratos? {len(ctrls.intersection(cnpjs_contratos))}")
        if not df_fato.empty:
            cnpjs_fato = set(df_fato["CNPJ_NORM"].dropna().unique())
            print(f"  • Quantas subsidiárias estão na fato_analise_credito? {len(subs.intersection(cnpjs_fato))}")
            print(f"  • Quantas controladoras estão na fato_analise_credito? {len(ctrls.intersection(cnpjs_fato))}")

            # Amostra das subsidiárias que estão nos contratos
            subs_em_contratos = subs.intersection(cnpjs_contratos)
            print("\nDetalhes das subsidiárias que estão nos contratos:")
            for s in list(subs_em_contratos)[:5]:
                sub_rows = df_ctrl[df_ctrl["CNPJ_SUBSIDIARIA"].apply(normalizar_cnpj_coluna) == s]
                c_mat = sub_rows["CNPJ_CONTA_ATRELADA"].iloc[0] if not sub_rows.empty else None
                sub_nome = sub_rows["SUBSIDIARIA"].iloc[0] if not sub_rows.empty else ""
                ctrl_nome = sub_rows["CONTA_ATRELADA"].iloc[0] if not sub_rows.empty else ""
                tem_na_fato_s = s in cnpjs_fato
                tem_na_fato_c = normalizar_cnpj_coluna(c_mat) in cnpjs_fato if c_mat else False
                print(f"  - Sub: {s} ({sub_nome}) -> Ctrl: {c_mat} ({ctrl_nome})")
                print(f"    Sub na fato? {tem_na_fato_s} | Ctrl na fato? {tem_na_fato_c}")

    # Verificar filiais nos contratos
    print("\n[+] Análise de Matriz/Filial nos contratos:")
    df_ctr["CNPJ_RAIZ"] = df_ctr["CNPJ_NORM"].str[:8]
    df_ctr["EH_MATRIZ"] = df_ctr["CNPJ_NORM"].str[8:12] == "0001"
    cnpjs_filiais = set(df_ctr.loc[~df_ctr["EH_MATRIZ"], "CNPJ_NORM"].dropna().unique())
    cnpjs_matrizes = set(df_ctr.loc[df_ctr["EH_MATRIZ"], "CNPJ_NORM"].dropna().unique())
    print(f"  • CNPJs Matriz (0001) nos contratos: {len(cnpjs_matrizes)}")
    print(f"  • CNPJs Filiais (não-0001) nos contratos: {len(cnpjs_filiais)}")
    
    # Quantas filiais têm a matriz nos contratos ou nas fichas?
    raizes_com_matriz = {c[:8] for c in cnpjs_matrizes}
    filiais_com_matriz_em_contratos = {c for c in cnpjs_filiais if c[:8] in raizes_com_matriz}
    print(f"  • Filiais cuja matriz também tem contrato ativo: {len(filiais_com_matriz_em_contratos)}")

    # Verificar quantas filiais têm matriz com análise na fato
    if not df_fato.empty:
        df_fato["EH_MATRIZ"] = df_fato["CNPJ_NORM"].str[8:12] == "0001"
        raizes_com_analise_matriz = {c[:8] for c in df_fato.loc[df_fato["EH_MATRIZ"], "CNPJ_NORM"].dropna().unique()}
        filiais_com_matriz_analisada = {c for c in cnpjs_filiais if c[:8] in raizes_com_analise_matriz}
        print(f"  • Filiais cuja matriz possui análise na fato: {len(filiais_com_matriz_analisada)}")

if __name__ == "__main__":
    main()
