import pandas as pd
from pathlib import Path
from common.identificadores import normalizar_cnpj_coluna

def run_diagnostico_parte2():
    print("=" * 60)
    print("DIAGNÓSTICO PARTE 2: RECONCILIAÇÃO E INVESTIGAÇÃO DE NaT")
    print("=" * 60)
    
    base_dir = Path("SAIDAS")
    silver_contratos_path = base_dir / "silver" / "denodo_contratos_silver" / "contratos_correntes.parquet"
    fato_risco_path = base_dir / "relational" / "facts" / "fato_analise_credito.parquet"
    if not fato_risco_path.exists():
        fato_risco_path = base_dir / "relational" / "facts" / "credito" / "fato_analise_credito.parquet"
    
    silver_comercializadoras_path = base_dir / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    silver_consumidores_path = base_dir / "silver" / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet"
    
    df_contratos = pd.read_parquet(silver_contratos_path)
    df_fatos = pd.read_parquet(fato_risco_path)
    
    # Preparar Contratos
    col_status = "STATUS" if "STATUS" in df_contratos.columns else ("id_status" if "id_status" in df_contratos.columns else "status")
    df_contratos_ativos = df_contratos[df_contratos[col_status].astype(str).str.upper().str.contains("ATIVO|EM SUPRIMENTO|2|VENCIDO", regex=True, na=False)].copy()
    col_cnpj = "CONTRAPARTE_CNPJ" if "CONTRAPARTE_CNPJ" in df_contratos_ativos.columns else "CNPJ"
    df_contratos_ativos["CNPJ_NORM"] = df_contratos_ativos[col_cnpj].apply(normalizar_cnpj_coluna)
    
    col_data_fech = None
    for c in ["DATA_FECHAMENTO", "data_fechamento", "DATA_ASSINATURA", "DATA_CRIACAO", "VIGENCIA_INICIO", "SUPRIMENTO_INICIO"]:
        if c in df_contratos_ativos.columns:
            col_data_fech = c
            break
    if col_data_fech:
        df_contratos_ativos["DATA_FECHAMENTO_DT"] = pd.to_datetime(df_contratos_ativos[col_data_fech], errors="coerce")
    else:
        df_contratos_ativos["DATA_FECHAMENTO_DT"] = pd.NaT

    # Preparar Fatos
    df_fatos["CNPJ_NORM"] = df_fatos["CNPJ"].apply(normalizar_cnpj_coluna)
    df_fatos["DATA_ANALISE_DT"] = pd.to_datetime(df_fatos.get("DATA_ANALISE"), errors="coerce")
    
    # --- PARTE 1: Reconciliação ---
    print("\n[ PARTE 1: RECONCILIAÇÃO MATEMÁTICA E GRUPOS DE CONTRATOS ]")
    cnpjs_na_fato = set(df_fatos["CNPJ_NORM"])
    
    # Classificar CNPJs baseados em suas fichas na Fato
    cnpjs_com_data_valida = set(df_fatos.dropna(subset=["DATA_ANALISE_DT"])["CNPJ_NORM"])
    cnpjs_so_com_nat = cnpjs_na_fato - cnpjs_com_data_valida
    
    print(f"Total de linhas na Fato: {len(df_fatos)}")
    print(f"Total de CNPJs distintos na Fato: {len(cnpjs_na_fato)}")
    print(f"CNPJs na Fato com pelo menos 1 data válida: {len(cnpjs_com_data_valida)}")
    print(f"CNPJs na Fato SOMENTE com NaT (sem data válida): {len(cnpjs_so_com_nat)}")
    
    df_fatos_validos = df_fatos.dropna(subset=["DATA_ANALISE_DT"]).sort_values("DATA_ANALISE_DT")
    df_contratos_validos = df_contratos_ativos.dropna(subset=["DATA_FECHAMENTO_DT"]).sort_values("DATA_FECHAMENTO_DT")
    
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
        
        # Para identificar contratos que cruzaram com sucesso (dentro da tolerância)
        col_teste = "PD_BASE" if "PD_BASE" in df_fatos.columns else "PD_FINAL"
        contratos_cruzados_com_sucesso = set(merge_asof_test[merge_asof_test[col_teste].notna()]["NUMERO_REFERENCIA_CONTRATO_STR" if "NUMERO_REFERENCIA_CONTRATO_STR" in merge_asof_test else "NUMERO_REFERENCIA_CONTRATO"])
    else:
        contratos_cruzados_com_sucesso = set()

    grupo_a = 0 # CNPJ nunca teve ficha
    grupo_b = 0 # CNPJ tem ficha, mas só NaT
    grupo_c = 0 # CNPJ tem ficha com data, mas fora da tolerância
    grupo_d = 0 # CNPJ tem ficha com data, dentro da tolerância
    
    id_col = "NUMERO_REFERENCIA_CONTRATO_STR" if "NUMERO_REFERENCIA_CONTRATO_STR" in df_contratos_ativos else ("NUMERO_REFERENCIA_CONTRATO" if "NUMERO_REFERENCIA_CONTRATO" in df_contratos_ativos else df_contratos_ativos.index)
    if "NUMERO_REFERENCIA_CONTRATO_STR" not in df_contratos_ativos.columns:
        col_ref = "NUMERO_REFERENCIA_CONTRATO" if "NUMERO_REFERENCIA_CONTRATO" in df_contratos_ativos.columns else "CONTRATO"
        df_contratos_ativos["NUMERO_REFERENCIA_CONTRATO_STR"] = df_contratos_ativos[col_ref].astype(str)
        id_col = "NUMERO_REFERENCIA_CONTRATO_STR"
        
    for _, row in df_contratos_ativos.iterrows():
        cnpj = row["CNPJ_NORM"]
        cid = row[id_col]
        
        if cnpj not in cnpjs_na_fato:
            grupo_a += 1
        elif cnpj in cnpjs_so_com_nat:
            grupo_b += 1
        else:
            # Tem data válida. Vamos ver se cruzou com sucesso no asof
            if cid in contratos_cruzados_com_sucesso:
                grupo_d += 1
            else:
                grupo_c += 1

    total_base = len(df_contratos_ativos)
    print("\nCategorização de Contratos (Mutuamente Exclusivos):")
    print(f"(a) CNPJ nunca teve nenhuma ficha: {grupo_a}")
    print(f"(b) CNPJ tem ficha, mas com DATA_ANALISE = NaT: {grupo_b}")
    print(f"(c) CNPJ tem ficha válida, mas fora da janela de 540 dias: {grupo_c}")
    print(f"(d) CNPJ cruzou com sucesso (dentro da tolerância): {grupo_d}")
    print(f"Total somado dos grupos: {grupo_a + grupo_b + grupo_c + grupo_d}")
    print(f"Total base de contratos: {total_base}")

    # --- PARTE 2: Investigação do NaT ---
    print("\n[ PARTE 2: INVESTIGAÇÃO DE NaT POR VERSÃO DE LAYOUT ]")
    fatos_nat = df_fatos[df_fatos["DATA_ANALISE_DT"].isna()].copy()
    print(f"Total de fichas (linhas na Fato) com DATA_ANALISE nula: {len(fatos_nat)}")
    
    df_silver_com = pd.read_parquet(silver_comercializadoras_path) if silver_comercializadoras_path.exists() else pd.DataFrame()
    df_silver_con = pd.read_parquet(silver_consumidores_path) if silver_consumidores_path.exists() else pd.DataFrame()
    
    cols_para_silver = ["CNPJ"]
    for c in ["VERSAO_LAYOUT", "DATA_CALCULO", "VERSAO", "versao_layout", "layout", "LAYOUT", "TEMPLATE_NAME"]:
        if c in df_silver_com.columns or c in df_silver_con.columns:
            cols_para_silver.append(c)
            
    df_silver_all = []
    if not df_silver_com.empty:
        com_cols = [c for c in cols_para_silver if c in df_silver_com.columns]
        if "CNPJ" not in com_cols and "CONTRAPARTE_CNPJ" in df_silver_com.columns:
            df_silver_com["CNPJ"] = df_silver_com["CONTRAPARTE_CNPJ"]
            com_cols.append("CNPJ")
        df_silver_all.append(df_silver_com[com_cols].copy())
        
    if not df_silver_con.empty:
        con_cols = [c for c in cols_para_silver if c in df_silver_con.columns]
        if "CNPJ" not in con_cols and "CONTRAPARTE_CNPJ" in df_silver_con.columns:
            df_silver_con["CNPJ"] = df_silver_con["CONTRAPARTE_CNPJ"]
            con_cols.append("CNPJ")
        df_silver_all.append(df_silver_con[con_cols].copy())

    if df_silver_all:
        df_silver = pd.concat(df_silver_all, ignore_index=True)
        df_silver["CNPJ_NORM"] = df_silver["CNPJ"].apply(normalizar_cnpj_coluna)
        
        # Encontrar a versão de layout para os NaTs
        fatos_nat_info = pd.merge(
            fatos_nat[["CNPJ_NORM"]], 
            df_silver, 
            on="CNPJ_NORM", 
            how="left"
        )
        
        col_layout = None
        for c in ["VERSAO_LAYOUT", "VERSAO", "versao_layout", "layout", "LAYOUT", "TEMPLATE_NAME"]:
            if c in fatos_nat_info.columns:
                col_layout = c
                break
                
        if col_layout:
            fatos_nat_info[col_layout] = fatos_nat_info[col_layout].fillna("DESCONHECIDO/SEM_MATCH")
            dist = fatos_nat_info[col_layout].value_counts()
            print("\nDistribuição das fichas com NaT por versão de layout:")
            for layout, count in dist.items():
                print(f"  {layout}: {count}")
        else:
            print("\nColuna de versão de layout não encontrada nas tabelas Silver.")
            print("Colunas disponíveis na Silver:", list(df_silver.columns))
    else:
        print("\nTabelas Silver de fichas não encontradas ou vazias.")
        
    print("=" * 60)

if __name__ == '__main__':
    run_diagnostico_parte2()
