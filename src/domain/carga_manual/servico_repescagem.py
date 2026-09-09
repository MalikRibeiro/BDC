import pandas as pd
import shutil
import logging
from pathlib import Path
from app.context import AppContext

def repescar_fichas_alteradas(context: AppContext, cnpjs_alterados: set[str], logger: logging.Logger | None = None) -> None:
    """Busca o arquivo original na pasta de processados e devolve para pendentes."""
    if not cnpjs_alterados:
        return
        
    if logger is None:
        logger = logging.getLogger("bdc.governanca.repescagem")
    
    silver_path_com = context.path("silver") / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    silver_path_cons = context.path("silver") / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet"
    
    df_silver_com = pd.read_parquet(silver_path_com) if silver_path_com.exists() else pd.DataFrame()
    df_silver_cons = pd.read_parquet(silver_path_cons) if silver_path_cons.exists() else pd.DataFrame()
    
    from common.identificadores import normalizar_cnpj
    if not df_silver_com.empty and "CNPJ" in df_silver_com.columns:
        df_silver_com["CNPJ"] = df_silver_com["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    if not df_silver_cons.empty and "CNPJ" in df_silver_cons.columns:
        df_silver_cons["CNPJ"] = df_silver_cons["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    
    repescados = 0
    for cnpj_raw in cnpjs_alterados:
        resultado = normalizar_cnpj(cnpj_raw)
        if not resultado.valido:
            continue
        cnpj = resultado.cnpj
        match_com = df_silver_com[df_silver_com["CNPJ"] == cnpj] if not df_silver_com.empty else pd.DataFrame()
        match_cons = df_silver_cons[df_silver_cons["CNPJ"] == cnpj] if not df_silver_cons.empty else pd.DataFrame()
        
        if not match_com.empty:
            nome_arquivo = match_com.iloc[-1].get("arquivo_nome")
            if nome_arquivo:
                proc_dir = context.path("input_fichas_comercializadoras_processadas")
                pend_dir = context.path("input_reprocessamento_comercializadoras_pendentes")
                pend_dir.mkdir(parents=True, exist_ok=True)
                arq_proc = proc_dir / nome_arquivo
                arq_pend = pend_dir / nome_arquivo
                
                if not arq_pend.exists() and arq_proc.exists():
                    shutil.copy2(arq_proc, arq_pend)
                    logger.info("[REPESCAGEM] Ficha comercializadora '%s' devolvida para a fila (CNPJ: %s).", nome_arquivo, cnpj)
                    repescados += 1
                elif arq_pend.exists():
                    logger.info("[REPESCAGEM] Ficha comercializadora '%s' já estava na fila de pendentes (CNPJ: %s).", nome_arquivo, cnpj)
                elif not arq_proc.exists():
                    logger.warning("[REPESCAGEM] Arquivo original '%s' não encontrado em processados (CNPJ: %s).", nome_arquivo, cnpj)
                    
        elif not match_cons.empty:
            nome_arquivo = match_cons.iloc[-1].get("arquivo_nome")
            if nome_arquivo:
                proc_dir = context.path("input_fichas_consumidores_processadas")
                pend_dir = context.path("input_reprocessamento_consumidores_pendentes")
                pend_dir.mkdir(parents=True, exist_ok=True)
                arq_proc = proc_dir / nome_arquivo
                arq_pend = pend_dir / nome_arquivo
                
                if not arq_pend.exists() and arq_proc.exists():
                    shutil.copy2(arq_proc, arq_pend)
                    logger.info("[REPESCAGEM] Ficha consumidor '%s' devolvida para a fila (CNPJ: %s).", nome_arquivo, cnpj)
                    repescados += 1
                elif arq_pend.exists():
                    logger.info("[REPESCAGEM] Ficha consumidor '%s' já estava na fila de pendentes (CNPJ: %s).", nome_arquivo, cnpj)
                elif not arq_proc.exists():
                    logger.warning("[REPESCAGEM] Arquivo original '%s' não encontrado em processados (CNPJ: %s).", nome_arquivo, cnpj)
                    
    if repescados > 0:
        logger.info("[REPESCAGEM] Sucesso! %d fichas enfileiradas para reprocessamento imediato.", repescados)