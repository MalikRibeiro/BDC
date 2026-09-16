import logging
import pandas as pd
import hashlib
from pathlib import Path
from typing import Any
from datetime import datetime

from src.common.identificadores import normalizar_cnpj

logger = logging.getLogger(__name__)

class ControladorErro(Exception):
    """Exceção levantada quando a base de dados de Controlador possui problemas estruturais ou de leitura."""
    pass

def _calcular_hash(caminho_arquivo: Path) -> str:
    hash_sha256 = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def buscar_planilha_controlador(input_dir: str | None = None, logger_arg: Any | None = None) -> pd.DataFrame:
    """
    Lê a planilha local 'Controladora e Subsidiaria.csv', valida colunas, normaliza CNPJs e insere rastreabilidade.
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
        except (pd.errors.ParserError, UnicodeDecodeError):
            try:
                df = pd.read_csv(arquivo_alvo, sep=",", encoding="utf-8-sig")
            except Exception as inner_e:
                raise ControladorErro(f"Falha de parser (formato/encoding) ao ler o arquivo CSV: {inner_e}")
        
        df.columns = df.columns.str.strip().str.upper()
        
        mapa_colunas = {
            "CONTROLADOR": "CONTA_ATRELADA",
            "CNPJ CONTROLADOR": "CNPJ_CONTA_ATRELADA",
            "SUBSIDIARIA": "SUBSIDIARIA",
            "CNPJ SUBSIDIÁRIA": "CNPJ_SUBSIDIARIA",
            "CNPJ SUBSIDIARIA": "CNPJ_SUBSIDIARIA"
        }
        
        df = df.rename(columns=mapa_colunas)
        
        colunas_esperadas = ["SUBSIDIARIA", "CNPJ_SUBSIDIARIA", "CONTA_ATRELADA", "CNPJ_CONTA_ATRELADA"]
        
        colunas_faltantes = [col for col in colunas_esperadas if col not in df.columns]
        if colunas_faltantes:
            raise ControladorErro(f"Colunas obrigatórias ausentes na planilha de controladoras: {colunas_faltantes}")
        
        df = df[colunas_esperadas].copy()
        
        log.info("Normalizando CNPJs das Controladoras e Subsidiárias...")
        def _extrair_cnpj(val):
            resultado = normalizar_cnpj(val)
            return resultado.cnpj if resultado.valido else None
        df["CNPJ_SUBSIDIARIA"] = df["CNPJ_SUBSIDIARIA"].apply(_extrair_cnpj)
        df["CNPJ_CONTA_ATRELADA"] = df["CNPJ_CONTA_ATRELADA"].apply(_extrair_cnpj)
        
        df = df.dropna(subset=["CNPJ_SUBSIDIARIA", "CNPJ_CONTA_ATRELADA"], how="all")
        
        # ---------------------------------------------------------
        # Trilha de Auditoria (Governança Silver)
        # ---------------------------------------------------------
        df["SOURCE_FILE_HASH"] = _calcular_hash(arquivo_alvo)
        df["DATA_PROCESSAMENTO"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df["SOURCE_NAME"] = arquivo_alvo.name
        
        log.info(f"Planilha de Controladoras processada com sucesso. Total de vínculos ativos extraídos: {len(df)}")
        return df
        
    except ControladorErro:
        raise
    except Exception as e:
        log.error("Erro desconhecido ao processar a planilha de Controladoras local: %s", e)
        raise ControladorErro(f"Erro no processamento da base de Controladoras: {e}")