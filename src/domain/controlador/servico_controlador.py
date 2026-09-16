import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
import shutil

from src.app.context import AppContext
from src.storage.escrever_dados import mesclar_conjunto_de_dados_prata_por_chave_de_negocio
from src.services.connectors.controlador_connector import buscar_planilha_controlador
from src.control.logger import obter_logger

logger = logging.getLogger(__name__)

def inserir_dados_controladoras(context: AppContext) -> dict[str, Any]:
    """
    Pipeline step para ingestão do arquivo estático de Controladoras.
    Lê o CSV, salva um snapshot na Bronze e o processado na Silver.
    """
    run_id = f"CTRL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    log_path = context.path("log_runner") / f"{run_id}__ingestao_controladoras.log"
    log_ctrl = obter_logger("bdc.controladoras", log_path)
    log_ctrl.info("Iniciando ingestão de dados de Controladoras (Herança de Risco).")
    
    try:
        # Puxa o dado normalizado do conector
        df_ctrl = buscar_planilha_controlador(logger_arg=log_ctrl)
        
        # Salvar cópia bruta na Bronze (Audit)
        arquivo_origem = Path("ENTRADAS/controlador/Controladora e Subsidiaria.csv")
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "controladoras"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        
        if arquivo_origem.exists():
            nome_bronze = f"raw_controladoras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            shutil.copy2(arquivo_origem, bronze_dir / nome_bronze)
            log_ctrl.info(f"Snapshot Bronze salvo: {nome_bronze}")

        # Salvar na Silver
        if not df_ctrl.empty:
            silver_dir = context.path("silver") / "mapeamento_controladoras"
            silver_dir.mkdir(parents=True, exist_ok=True)
            mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
                records=df_ctrl.to_dict(orient="records"),
                output_dir=silver_dir,
                filename="mapeamento_controladoras",
                business_keys=["CNPJ_SUBSIDIARIA", "CNPJ_CONTA_ATRELADA"]
            )
            log_ctrl.info(f"Ingestão finalizada. {len(df_ctrl)} vínculos de Controladoras salvos na Silver (SCD2).")
            return {"run_id": run_id, "linhas": len(df_ctrl), "status": "SUCESSO"}
        else:
            log_ctrl.warning("A base de Controladoras está vazia.")
            return {"run_id": run_id, "linhas": 0, "status": "SEM_DADOS"}

    except Exception as e:
        log_ctrl.error(f"Falha na ingestão de Controladoras: {e}")
        raise


def herdar_risco_controladoras(df_fato: pd.DataFrame, df_controladoras: pd.DataFrame, col_cnpj: str = "CNPJ") -> pd.DataFrame:
    """
    Aplica a regra de herança de risco de crédito das Contas Atreladas para as Subsidiárias diretamente na Fato.
    
    Regra estrita: 
    Só recebe herança se o CNPJ existir na coluna CNPJ_SUBSIDIARIA do mapping 
    E se NÃO tiver análise (Rating/PD/Score) própria.
    """
    logger.info("Iniciando processo restrito de Herança de Risco (Controladoras) na Camada Relacional...")
    
    if df_fato is None or df_fato.empty:
        return df_fato
        
    df_result = df_fato.copy()
    
    if "ANALISE_HERDADA" not in df_result.columns:
        df_result["ANALISE_HERDADA"] = False
    
    if "TIPO_ANALISE" not in df_result.columns:
        df_result["TIPO_ANALISE"] = "Ficha Própria"
        
    if df_controladoras is None or df_controladoras.empty:
        logger.warning("Base de controladoras vazia. Herança abortada.")
        return df_result
        
    colunas_risco = ["RATING_FINAL", "PD_FINAL", "SCORE_FINAL", "SCORE", "SCORE_TOTAL", "RESTRITIVOS", "DATA_ANALISE", "DATA_REFERENCIA"]
    col_disponiveis = [c for c in colunas_risco if c in df_result.columns]
    
    if not col_disponiveis:
        return df_result
        
    df_controladoras = df_controladoras.dropna(subset=["CNPJ_SUBSIDIARIA", "CNPJ_CONTA_ATRELADA"])
    
    # Criar um Set dos CNPJs que são comprovadamente subsidiárias (para evitar inferências falsas)
    set_subsidiarias = set(df_controladoras["CNPJ_SUBSIDIARIA"].unique())
    
    # Regra 1: Está no arquivo de controladoras como Subsidiária?
    mask_subsidiaria_oficial = df_result[col_cnpj].isin(set_subsidiarias)
    
    # Regra 2: Identificar quem já está na base Fato mas sem Rating
    mask_presente_mas_orfao = pd.Series(False, index=df_result.index)
    if "RATING_FINAL" in df_result.columns:
        mask_presente_mas_orfao = df_result["RATING_FINAL"].isna() | (df_result["RATING_FINAL"] == "")
    elif "PD_FINAL" in df_result.columns:
        mask_presente_mas_orfao = df_result["PD_FINAL"].isna()
        
    mask_elegivel_atualizacao = mask_subsidiaria_oficial & mask_presente_mas_orfao
    linhas_atualizar = df_result[mask_elegivel_atualizacao].index
        
    # Indexa a tabela fato para buscas rápidas do CNPJ Matriz
    df_fato_indexed = df_result.set_index(col_cnpj)
    
    novas_linhas = []
    count_herdados = 0
    count_inseridos = 0
    
    for _, row in df_controladoras.iterrows():
        cnpj_sub = row["CNPJ_SUBSIDIARIA"]
        cnpj_matriz = row["CNPJ_CONTA_ATRELADA"]
        
        # A Matriz precisa estar na Fato (foi analisada)
        if cnpj_matriz in df_fato_indexed.index:
            dados_matriz = df_fato_indexed.loc[cnpj_matriz]
            
            if isinstance(dados_matriz, pd.DataFrame):
                linha_valida = None
                for _, d_row in dados_matriz.iterrows():
                    for col in ["RATING_FINAL", "PD_FINAL", "SCORE_TOTAL", "SCORE", "RATING"]:
                        if col in d_row and pd.notna(d_row.get(col)) and str(d_row.get(col)).strip() not in ("", "None", "nan", "<NA>"):
                            linha_valida = d_row
                            break
                    if linha_valida is not None:
                        break
                dados_matriz = linha_valida if linha_valida is not None else dados_matriz.iloc[-1]
                
            # Verifica se a matriz (linha final escolhida) realmente gerou risco
            tem_risco = False
            for col in ["RATING_FINAL", "PD_FINAL", "SCORE_TOTAL", "SCORE", "RATING"]:
                if col in dados_matriz and pd.notna(dados_matriz.get(col)) and str(dados_matriz.get(col)).strip() not in ("", "None", "nan", "<NA>"):
                    tem_risco = True
                    break
                    
            if tem_risco:
                dados_herdados = dados_matriz.to_dict()
                dados_herdados["ANALISE_HERDADA"] = True
                dados_herdados["ORIGEM_ANALISE"] = "HERDADA DA CONTROLADORA"
                dados_herdados["TIPO_ANALISE"] = "Análise Herdada"
                dados_herdados[col_cnpj] = cnpj_sub 
                dados_herdados["CNPJ_RAIZ"] = str(cnpj_sub)[:8]
                
                # A Subsidiária já está na Fato?
                mask_sub = df_result[col_cnpj] == cnpj_sub
                if mask_sub.any():
                    # Atualiza in-place nas linhas onde ela era órfã
                    idx_sub = df_result[mask_sub].index
                    for idx in idx_sub:
                        if idx in linhas_atualizar:
                            for c, v in dados_herdados.items():
                                df_result.at[idx, c] = v
                            count_herdados += 1
                else:
                    # Inserção de Nova Linha (Subsidiária não enviou Ficha, não estava na Fato)
                    novas_linhas.append(dados_herdados)
                    count_inseridos += 1
                    
    # Adicionar as subsidiárias 100% órfãs que nem existiam na tabela
    if novas_linhas:
        df_novos = pd.DataFrame(novas_linhas)
        df_result = pd.concat([df_result, df_novos], ignore_index=True)
            
    logger.info(f"Herança Relacional: {count_herdados} atualizadas, {count_inseridos} subsidiárias inseridas na Fato.")
    return df_result


def herdar_risco_filiais(df_fato: pd.DataFrame, df_contratos: pd.DataFrame) -> pd.DataFrame:
    """
    Filiais ativas (com contrato) que não possuem análise herdam a análise da Matriz (mesma raiz CNPJ)
    se a matriz possuir análise válida na Fato. Prioriza a matriz com terminação 0001 (ou semelhante) se houver conflito.
    """
    logger.info("Iniciando processo de Herança de Risco de Filiais (Raiz CNPJ)...")
    
    if df_fato is None or df_fato.empty or df_contratos is None or df_contratos.empty:
        return df_fato
        
    df_result = df_fato.copy()
    
    # 1. Identificar CNPJs com contrato ativo
    status_excluidos = ["CANCELADO", "DISTRATADO", "ENCERRADO", "REJEITADO", "INATIVO"]
    if "STATUS" in df_contratos.columns:
        df_ativos = df_contratos[~df_contratos["STATUS"].astype(str).str.upper().isin(status_excluidos)]
    else:
        df_ativos = df_contratos
        
    cnpjs_com_contrato = set(df_ativos["CNPJ"].dropna().unique())
    
    # 2. Identificar quem já está na Fato
    cnpjs_na_fato = set(df_result["CNPJ"].dropna().unique())
    
    # 3. Filiais orfãs = tem contrato mas NÃO estão na fato (ou estão mas não têm rating)
    mask_presente_mas_orfao = pd.Series(False, index=df_result.index)
    if "RATING_FINAL" in df_result.columns:
        mask_presente_mas_orfao = df_result["RATING_FINAL"].isna() | (df_result["RATING_FINAL"] == "")
        
    cnpjs_orfaos = cnpjs_com_contrato - cnpjs_na_fato
    linhas_atualizar = df_result[df_result["CNPJ"].isin(cnpjs_com_contrato) & mask_presente_mas_orfao].index
    
    if not cnpjs_orfaos and linhas_atualizar.empty:
        logger.info("Nenhuma filial órfã com contrato identificada para herança.")
        return df_result
        
    # 4. Criar dicionário de doadores potenciais (Raiz -> DataFrame com Ratings)
    df_fato["CNPJ_RAIZ_TEMP"] = df_fato["CNPJ"].astype(str).str[:8]
    df_doadores = df_fato[~mask_presente_mas_orfao].copy()
    
    novas_linhas = []
    count_herdados = 0
    count_inseridos = 0
    
    todas_orfas = list(cnpjs_orfaos) + df_result.loc[linhas_atualizar, "CNPJ"].tolist()
    todas_orfas = list(set(todas_orfas))
    
    for cnpj_filial in todas_orfas:
        raiz = str(cnpj_filial)[:8]
        # Procurar doador
        doadores_potenciais = df_doadores[df_doadores["CNPJ_RAIZ_TEMP"] == raiz]
        if not doadores_potenciais.empty:
            # Prioriza a filial mais "matriz" que é 0001 (e.g. 0001-XX)
            matrizes = doadores_potenciais[doadores_potenciais["CNPJ"].astype(str).str[8:12] == "0001"]
            if not matrizes.empty:
                doador = matrizes.iloc[0]
            else:
                doador = doadores_potenciais.iloc[0]
                
            dados_herdados = doador.to_dict()
            dados_herdados["ANALISE_HERDADA"] = True
            dados_herdados["ORIGEM_ANALISE"] = "HERDADA DA MATRIZ (RAIZ CNPJ)"
            dados_herdados["TIPO_ANALISE"] = "Herança de Raiz"
            dados_herdados["CNPJ"] = cnpj_filial
            dados_herdados["CNPJ_RAIZ"] = raiz
            
            # Remover chaves temporárias
            if "CNPJ_RAIZ_TEMP" in dados_herdados:
                del dados_herdados["CNPJ_RAIZ_TEMP"]
                
            mask_sub = df_result["CNPJ"] == cnpj_filial
            if mask_sub.any():
                idx_sub = df_result[mask_sub].index
                for idx in idx_sub:
                    if idx in linhas_atualizar:
                        for c, v in dados_herdados.items():
                            df_result.at[idx, c] = v
                        count_herdados += 1
            else:
                novas_linhas.append(dados_herdados)
                count_inseridos += 1
                
    if novas_linhas:
        df_novos = pd.DataFrame(novas_linhas)
        df_result = pd.concat([df_result, df_novos], ignore_index=True)
        
    df_fato.drop(columns=["CNPJ_RAIZ_TEMP"], errors="ignore", inplace=True)
    if "CNPJ_RAIZ_TEMP" in df_result.columns:
        df_result.drop(columns=["CNPJ_RAIZ_TEMP"], inplace=True)
        
    logger.info(f"Herança de Filiais: {count_herdados} atualizadas, {count_inseridos} inseridas na Fato.")
    return df_result
