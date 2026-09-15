import logging
import pandas as pd
from pathlib import Path
from typing import Any

from src.common.identificadores import normalizar_cnpj

logger = logging.getLogger(__name__)

class ControladorErro(Exception):
    """Exceção levantada quando a base de dados de Controlador possui problemas estruturais ou de leitura."""
    pass

def buscar_planilha_controlador(input_dir: str | None = None, logger_arg: Any | None = None) -> pd.DataFrame:
    """
    Lê a planilha local 'Controladora e Subsidiaria.csv', valida colunas e normaliza CNPJs.
    """
    log = logger_arg or logger
    data_path = Path(input_dir or "ENTRADAS/controlador")
    arquivo_alvo = data_path / "Controladora e Subsidiaria.csv"
    
    if not arquivo_alvo.exists():
        raise ControladorErro(f"Arquivo não encontrado: {arquivo_alvo}")
    
    try:
        log.info(f"Carregando planilha de Controladoras local: {arquivo_alvo}")
        
        try:
            df = pd.read_csv(arquivo_alvo, sep=";", encoding="utf-8-sig")
        except:
            df = pd.read_csv(arquivo_alvo, sep=",", encoding="utf-8-sig")
        
        df.columns = df.columns.str.strip().str.upper()
        
        mapa_colunas = {
            "CONTROLADOR": "CONTA_ATRELADA",
            "CNPJ CONTROLADOR": "CNPJ_CONTA_ATRELADA",
            "SUBSIDIARIA": "SUBSIDIARIA",
            "CNPJ SUBSIDIÁRIA": "CNPJ_SUBSIDIARIA",
            "CNPJ SUBSIDIARIA": "CNPJ_SUBSIDIARIA" # Fallback sem acento
        }
        
        df = df.rename(columns=mapa_colunas)
        
        colunas_esperadas = ["SUBSIDIARIA", "CNPJ_SUBSIDIARIA", "CONTA_ATRELADA", "CNPJ_CONTA_ATRELADA"]
        
        colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
        if colunas_faltantes:
            raise ControladorErro(f"Colunas obrigatórias ausentes na planilha de controladoras: {colunas_faltantes}")
        
        df = df[colunas_esperadas].copy()
        
        log.info("Normalizando CNPJs das Controladoras e Subsidiárias...")
        df["CNPJ_SUBSIDIARIA"] = df["CNPJ_SUBSIDIARIA"].apply(normalizar_cnpj)
        df["CNPJ_CONTA_ATRELADA"] = df["CNPJ_CONTA_ATRELADA"].apply(normalizar_cnpj)
        
        df = df.dropna(subset=["CNPJ_SUBSIDIARIA", "CNPJ_CONTA_ATRELADA"], how="all")
        
        log.info(f"Planilha de Controladoras processada com sucesso. Total de vínculos ativos extraídos: {len(df)}")
        return df
        
    except Exception as e:
        log.error("Erro ao ler ou processar a planilha de Controladoras local: %s", e)
        raise ControladorErro(f"Erro no processamento da base de Controladoras: {e}")