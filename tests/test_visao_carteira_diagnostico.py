import pandas as pd
import numpy as np
from pathlib import Path
from common.identificadores import normalizar_cnpj_coluna

def diagnostico():
    print("=" * 60)
    print("DIAGNÓSTICO ROOT-CAUSE: BURACOS NA VISÃO CARTEIRA")
    print("=" * 60)
    
    # 1. Carregar Dados
    base_dir = Path("SAIDAS")
    silver_contratos_path = base_dir / "silver" / "denodo_contratos_silver" / "contratos_correntes.parquet"
    fato_risco_path = base_dir / "relational" / "facts" / "fato_analise_credito.parquet"
    if not fato_risco_path.exists():
        fato_risco_path = base_dir / "relational" / "facts" / "credito" / "fato_analise_credito.parquet"
    mtm_path = base_dir / "silver" / "mtm_contratos_silver" / "mtm_contratos.parquet"
    visao_path = base_dir / "gold" / "visao_operacional_negocio" / "Visao_Carteira_Contratos.parquet"
    
    if not silver_contratos_path.exists():
        print(f"Erro: Arquivo não encontrado: {silver_contratos_path}")
        return
    if not fato_risco_path.exists():
        print(f"Erro: Arquivo não encontrado: {fato_risco_path}")
        return
    if not mtm_path.exists():
        print(f"Aviso: Arquivo MTM não encontrado: {mtm_path}")
    
    df_contratos = pd.read_parquet(silver_contratos_path)
    df_fatos = pd.read_parquet(fato_risco_path)
    df_mtm = pd.read_parquet(mtm_path) if mtm_path.exists() else pd.DataFrame()
    df_visao = pd.read_parquet(visao_path) if visao_path.exists() else pd.DataFrame()
    
    # Preparar df_contratos
    col_status = "STATUS" if "STATUS" in df_contratos.columns else ("id_status" if "id_status" in df_contratos.columns else "status")
    df_contratos_ativos = df_contratos[df_contratos[col_status].astype(str).str.upper().str.contains("ATIVO|EM SUPRIMENTO|2|VENCIDO", regex=True, na=False)].copy()
    col_cnpj = "CONTRAPARTE_CNPJ" if "CONTRAPARTE_CNPJ" in df_contratos_ativos.columns else "CNPJ"
    df_contratos_ativos["CNPJ_NORM"] = df_contratos_ativos[col_cnpj].apply(normalizar_cnpj_coluna)
    
    col_ref_contrato = "NUMERO_REFERENCIA_CONTRATO" if "NUMERO_REFERENCIA_CONTRATO" in df_contratos_ativos.columns else "CONTRATO"
    if col_ref_contrato in df_contratos_ativos.columns:
        df_contratos_ativos["NUMERO_REFERENCIA_CONTRATO_STR"] = df_contratos_ativos[col_ref_contrato].astype(str).str.strip()
    else:
        df_contratos_ativos["NUMERO_REFERENCIA_CONTRATO_STR"] = ""

    col_data_fech = None
    for c in ["DATA_FECHAMENTO", "data_fechamento", "DATA_ASSINATURA", "DATA_CRIACAO", "VIGENCIA_INICIO", "SUPRIMENTO_INICIO"]:
        if c in df_contratos_ativos.columns:
            col_data_fech = c
            break
    if col_data_fech:
        df_contratos_ativos["DATA_FECHAMENTO_DT"] = pd.to_datetime(df_contratos_ativos[col_data_fech], errors="coerce")
    else:
        df_contratos_ativos["DATA_FECHAMENTO_DT"] = pd.NaT

    df_fatos["CNPJ_NORM"] = df_fatos["CNPJ"].apply(normalizar_cnpj_coluna)
    df_fatos["DATA_ANALISE_DT"] = pd.to_datetime(df_fatos.get("DATA_ANALISE"), errors="coerce")

    # ----- HIPÓTESE 1 -----
    print("\n[ HIPÓTESE 1: fato_analise_credito não tem histórico, só estado atual ]")
    total_linhas_fatos = len(df_fatos)
    total_cnpjs_fatos = df_fatos["CNPJ_NORM"].nunique()
    print(f"Total de linhas em fato_analise_credito: {total_linhas_fatos}")
    print(f"CNPJs distintos em fato_analise_credito: {total_cnpjs_fatos}")
    print("Amostra de 5 CNPJs (qtd de linhas por CNPJ e datas de análise):")
    amostra_cnpjs = df_fatos["CNPJ_NORM"].dropna().unique()[:5]
    for c in amostra_cnpjs:
        subset = df_fatos[df_fatos["CNPJ_NORM"] == c]
        datas = subset["DATA_ANALISE"].tolist() if "DATA_ANALISE" in subset.columns else []
        print(f"  CNPJ {c}: {len(subset)} linha(s) - Datas: {datas}")

    # ----- HIPÓTESE 2 -----
    print("\n[ HIPÓTESE 2: Incompatibilidade de tipo/formato de CNPJ ]")
    dtype_contrato = df_contratos[col_cnpj].dtype
    dtype_fato = df_fatos["CNPJ"].dtype
    print(f"dtype em Contratos (Denodo): {dtype_contrato}")
    print(f"dtype em Fato (Risco): {dtype_fato}")
    
    # Encontrar CNPJs em comum
    cnpjs_comum = set(df_contratos_ativos["CNPJ_NORM"]).intersection(set(df_fatos["CNPJ_NORM"]))
    print(f"\nAmostra de 5 CNPJs em comum (comparação literal de valor antes de normalizar):")
    amostra_comum = list(cnpjs_comum)[:5]
    for c_norm in amostra_comum:
        v_contrato = df_contratos_ativos[df_contratos_ativos["CNPJ_NORM"] == c_norm][col_cnpj].iloc[0]
        v_fato = df_fatos[df_fatos["CNPJ_NORM"] == c_norm]["CNPJ"].iloc[0]
        print(f"  CNPJ normalizado {c_norm}:")
        print(f"    - Em Contratos: '{v_contrato}' (tipo: {type(v_contrato)})")
        print(f"    - Em Fatos:     '{v_fato}' (tipo: {type(v_fato)})")

    cnpjs_contratos = set(df_contratos_ativos["CNPJ_NORM"])
    cnpjs_fatos = set(df_fatos["CNPJ_NORM"])
    cnpjs_sem_ficha = cnpjs_contratos - cnpjs_fatos
    cnpjs_com_ficha = cnpjs_contratos.intersection(cnpjs_fatos)
    
    # Quantos contratos (linhas) isso afeta?
    contratos_sem_ficha = df_contratos_ativos[df_contratos_ativos["CNPJ_NORM"].isin(cnpjs_sem_ficha)]
    contratos_com_ficha = df_contratos_ativos[df_contratos_ativos["CNPJ_NORM"].isin(cnpjs_com_ficha)]
    
    # Dos contratos que TÊM ficha (CNPJ existe em fatos), quantos falham no merge_asof?
    df_fatos_validos = df_fatos.dropna(subset=["DATA_ANALISE_DT"]).sort_values("DATA_ANALISE_DT")
    df_contratos_validos = contratos_com_ficha.dropna(subset=["DATA_FECHAMENTO_DT"]).sort_values("DATA_FECHAMENTO_DT")
    
    if not df_fatos_validos.empty and not df_contratos_validos.empty:
        merge_asof_test = pd.merge_asof(
            df_contratos_validos,
            df_fatos_validos,
            by="CNPJ_NORM",
            left_on="DATA_FECHAMENTO_DT",
            right_on="DATA_ANALISE_DT",
            direction="backward",
            tolerance=pd.Timedelta(days=540)
        )
        
        # Coluna de interesse vinda da fato
        col_teste = "PD_BASE" if "PD_BASE" in df_fatos.columns else "PD_FINAL"
        contratos_falha_asof = merge_asof_test[merge_asof_test[col_teste].isna()]
        
        print(f"\nContratos totais (ativos): {len(df_contratos_ativos)}")
        print(f"Contratos sem nenhuma ficha no motor (CNPJ não existe em fatos): {len(contratos_sem_ficha)} (Afetados)")
        print(f"Contratos com ficha, mas que falham no merge_asof (ex: fora de 540 dias): {len(contratos_falha_asof)} (Afetados)")
    else:
        print("\nNão foi possível simular merge_asof (datas vazias).")

    # ----- HIPÓTESE 3 -----
    print("\n[ HIPÓTESE 3: Mesmo problema, na chave de contrato pro cruzamento de MtM ]")
    if not df_mtm.empty:
        col_contrato_mtm = "CONTRATO" if "CONTRATO" in df_mtm.columns else "NUMERO_REFERENCIA_CONTRATO"
        dtype_mtm = df_mtm[col_contrato_mtm].dtype
        print(f"dtype Contrato em Denodo: {df_contratos_ativos[col_ref_contrato].dtype}")
        print(f"dtype Contrato em MTM: {dtype_mtm}")
        
        df_mtm["CONTRATO_STR"] = df_mtm[col_contrato_mtm].astype(str).str.strip()
        mtm_contratos_set = set(df_mtm["CONTRATO_STR"])
        contratos_set = set(df_contratos_ativos["NUMERO_REFERENCIA_CONTRATO_STR"])
        comuns_mtm = contratos_set.intersection(mtm_contratos_set)
        
        print("Amostra de 5 Contratos em comum:")
        for c in list(comuns_mtm)[:5]:
            v_denodo = df_contratos_ativos[df_contratos_ativos["NUMERO_REFERENCIA_CONTRATO_STR"] == c][col_ref_contrato].iloc[0]
            v_mtm = df_mtm[df_mtm["CONTRATO_STR"] == c][col_contrato_mtm].iloc[0]
            print(f"  Chave limpa '{c}': Em Denodo '{v_denodo}' ({type(v_denodo)}) | Em MTM '{v_mtm}' ({type(v_mtm)})")
            
        print(f"Contratos em Denodo sem correspondência exata em MTM: {len(contratos_set - mtm_contratos_set)}")
        
        if not df_visao.empty:
            if "PD_FINAL" in df_visao.columns and "MTM_TOTAL" in df_visao.columns:
                risco_preenchido_mtm_vazio = df_visao[df_visao["PD_FINAL"].notna() & df_visao["MTM_TOTAL"].isna()]
                print(f"Contratos na Visão com Risco preenchido e MTM vazio: {len(risco_preenchido_mtm_vazio)}")
            else:
                print("Não foi possível verificar cruzamento na tabela Gold pois colunas faltam.")
    else:
        print("df_mtm está vazio.")

    # ----- HIPÓTESE 4 -----
    print("\n[ HIPÓTESE 4: Tolerância de 540 dias não reflete a validade real por segmento/fonte ]")
    if not df_fatos_validos.empty and not df_contratos_validos.empty:
        # Fazer asof sem tolerância
        merge_asof_no_tol = pd.merge_asof(
            df_contratos_validos,
            df_fatos_validos,
            by="CNPJ_NORM",
            left_on="DATA_FECHAMENTO_DT",
            right_on="DATA_ANALISE_DT",
            direction="backward"
        )
        
        # Calcular dias de diferença
        merge_asof_no_tol["DIAS_DIF"] = (merge_asof_no_tol["DATA_FECHAMENTO_DT"] - merge_asof_no_tol["DATA_ANALISE_DT"]).dt.days
        
        # Tolerância genérica 540 dias
        fora_da_tolerancia = merge_asof_no_tol[merge_asof_no_tol["DIAS_DIF"] > 540]
        dentro_da_tolerancia = merge_asof_no_tol[(merge_asof_no_tol["DIAS_DIF"] >= 0) & (merge_asof_no_tol["DIAS_DIF"] <= 540)]
        
        print(f"Registros que caem FORA de 540 dias (ignorados pela lógica atual): {len(fora_da_tolerancia)}")
        print(f"Registros que caem DENTRO de 540 dias: {len(dentro_da_tolerancia)}")
        # Nota: avaliar a regra exata de cada fonte seria complexo aqui porque exigiríamos as colunas DATA_DEMONSTRACAO_FINANCEIRA etc.
        # Mas podemos olhar se há registros entre 120 e 540 que estariam inválidos pelo motor.
        
        if "SEGMENTO_PD" in df_fatos.columns:
            # Emulação simples da regra do motor para registros DENTRO de 540 dias
            # Se fosse CPURA e dependesse de Bureau (120 dias) e o registro tivesse entre 121 e 540 dias
            cpura_entre_120_540 = dentro_da_tolerancia[(dentro_da_tolerancia["SEGMENTO_PD"] == "CPURA") & (dentro_da_tolerancia["DIAS_DIF"] > 120)]
            print(f"Desses DENTRO de 540 dias, quantos são CPURA com idade > 120 dias (possivelmente inválidos por bureau): {len(cpura_entre_120_540)}")
            
            # DF é 18 meses ~547 dias, então os que caem entre 541 e 547 são excluídos pela tolerância 540
            df_valido_excluido = fora_da_tolerancia[(fora_da_tolerancia["DIAS_DIF"] > 540) & (fora_da_tolerancia["DIAS_DIF"] <= 547)]
            print(f"Desses FORA de 540 dias, quantos tem idade <= 547 dias (válidos por DF mas excluídos pela tolerância de 540): {len(df_valido_excluido)}")
    else:
        print("Não foi possível simular merge_asof.")

    # ----- HIPÓTESE 5 -----
    print("\n[ HIPÓTESE 5: NaT em DATA_ANALISE quebrando a ordenação ]")
    qtd_nat = df_fatos["DATA_ANALISE_DT"].isna().sum()
    print(f"Linhas em fato_analise_credito com DATA_ANALISE nula/NaT: {qtd_nat}")
    print("Em `visao_contratos_risco.py`, existe `df_fatos.dropna(subset=['DATA_ANALISE_DT'])` antes do asof.")
    print("Portanto, exceções de ordenação devido a NaT NÃO ocorrem silenciosamente; as linhas com NaT são simplesmente EXCLUÍDAS do cruzamento.")
    print(f"Isso significa que {qtd_nat} registros de análise são completamente ignorados no momento de preencher a visão da carteira.")

    # ----- HIPÓTESE 6 -----
    print("\n[ HIPÓTESE 6: Volume real de dados ]")
    print(f"Contratos totais da base de Denodo (após filtro de ativos): {len(df_contratos_ativos)}")
    print(f"Destes, quantos CNPJs nunca tiveram ficha em lugar nenhum (não estão na fatos): {len(contratos_sem_ficha)}")
    print(f"Destes, quantos CNPJs TEM ficha, mas não cruzaram por questões de data (fora dos 540 dias): {len(contratos_falha_asof) if 'contratos_falha_asof' in locals() else 'N/A'}")
    print("=" * 60)

if __name__ == '__main__':
    diagnostico()
