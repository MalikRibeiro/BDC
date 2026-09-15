import pandas as pd
import logging

logger = logging.getLogger(__name__)

def herdar_risco_controladoras(df_carteira: pd.DataFrame, df_controladoras: pd.DataFrame, col_cnpj_carteira: str = "CNPJ") -> pd.DataFrame:
    """
    Aplica a regra de herança de risco de crédito das Contas Atreladas para as Subsidiárias.
    
    1. Identifica CNPJs órfãos (sem RATING_FINAL/PD_FINAL preenchido, mas que existem na carteira).
    2. Cruza com a base de controladoras via CNPJ_SUBSIDIARIA para descobrir o CNPJ_CONTA_ATRELADA.
    3. Busca os dados da CONTA_ATRELADA na própria carteira.
    4. Transfere os atributos quantitativos (RATING_FINAL, PD_FINAL, SCORE, DATA_ANALISE, etc.) para a subsidiária órfã.
    5. Marca ANALISE_HERDADA = True.
    """
    logger.info("Iniciando processo de Herança de Risco por Controladoras...")
    
    if df_carteira is None or df_carteira.empty:
        logger.warning("Carteira vazia. Nenhuma herança aplicada.")
        return df_carteira
        
    df_result = df_carteira.copy()
    
    if "ANALISE_HERDADA" not in df_result.columns:
        df_result["ANALISE_HERDADA"] = False
        
    if df_controladoras is None or df_controladoras.empty:
        logger.warning("Base de controladoras vazia ou nula. Nenhuma herança aplicada.")
        return df_result
        
    colunas_risco_possiveis = ["RATING_FINAL", "PD_FINAL", "SCORE_FINAL", "SCORE", "DATA_ANALISE", "DATA_REFERENCIA"]
    colunas_herdaveis = [c for c in colunas_risco_possiveis if c in df_result.columns]
    
    if not colunas_herdaveis:
        logger.warning("Nenhuma coluna de risco alvo encontrada na carteira para herdar. Abortando herança.")
        return df_result
        
    df_controladoras = df_controladoras.dropna(subset=["CNPJ_SUBSIDIARIA", "CNPJ_CONTA_ATRELADA"])
    
    if "RATING_FINAL" in df_result.columns:
        mask_orfao = df_result["RATING_FINAL"].isna() | (df_result["RATING_FINAL"] == "")
    elif "PD_FINAL" in df_result.columns:
        mask_orfao = df_result["PD_FINAL"].isna()
    else:
        if "SCORE" in df_result.columns:
            mask_orfao = df_result["SCORE"].isna()
        else:
            return df_result
            
    df_carteira_indexed = df_result.set_index(col_cnpj_carteira)[colunas_herdaveis]
    
    mapa_heranca = {}
    
    for _, row in df_controladoras.iterrows():
        cnpj_sub = row["CNPJ_SUBSIDIARIA"]
        cnpj_matriz = row["CNPJ_CONTA_ATRELADA"]
        
        if cnpj_matriz in df_carteira_indexed.index:
            dados_matriz = df_carteira_indexed.loc[cnpj_matriz]
            
            if isinstance(dados_matriz, pd.DataFrame):
                dados_matriz = dados_matriz.iloc[0]
                
            tem_risco = False
            for col in ["RATING_FINAL", "PD_FINAL", "SCORE"]:
                if col in dados_matriz and pd.notna(dados_matriz.get(col)):
                    tem_risco = True
                    break
                    
            if tem_risco:
                mapa_heranca[cnpj_sub] = dados_matriz.to_dict()
                
    count_herdados = 0
    linhas_orfaos = df_result[mask_orfao].index
    
    for idx in linhas_orfaos:
        cnpj_orfao = df_result.at[idx, col_cnpj_carteira]
        
        if cnpj_orfao in mapa_heranca:
            dados_herdados = mapa_heranca[cnpj_orfao]
            
            for col, val in dados_herdados.items():
                df_result.at[idx, col] = val
                
            df_result.at[idx, "ANALISE_HERDADA"] = True
            
            if "ORIGEM_ANALISE" in df_result.columns:
                df_result.at[idx, "ORIGEM_ANALISE"] = "HERDADA DA CONTROLADORA"
                
            count_herdados += 1
            
    logger.info(f"Processo de herança finalizado com sucesso. {count_herdados} subsidiárias receberam análise herdada de controladora.")
    return df_result
