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
        arquivo_origem = Path("ENTRADAS/controlador/Controladora e Subsidiaria.xlsx")
        if not arquivo_origem.exists():
            arquivo_origem = Path("ENTRADAS/controlador/Controladora e Subsidiaria.csv")
            
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "controladoras"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        
        if arquivo_origem.exists():
            ext = arquivo_origem.suffix
            nome_bronze = f"raw_controladoras_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
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
    [DEPRECATED - PARTE 3 DA REFATORAÇÃO DIMENSIONAL]
    Esta função foi descontinuada. A herança societária de risco não gera mais clonagem
    sintética de linhas na fato_analise_credito.
    
    A governança e herança de risco são agora tratadas de forma declarativa e relacional
    na dimensão canônica: src/relational/dimensions/dim_estabelecimento.py
    através das colunas CNPJ_DOADOR_RISCO e ORIGEM_HERANCA_RISCO.
    """
    logger.warning(
        "[DEPRECATED] herdar_risco_controladoras foi descontinuada. "
        "A herança de risco agora é resolvida dimensionalmente em dim_estabelecimento.py. "
        "Retornando DataFrame sem mutações sintéticas."
    )
    return df_fato


def herdar_risco_filiais(df_fato: pd.DataFrame, df_contratos: pd.DataFrame) -> pd.DataFrame:
    """
    [DEPRECATED - PARTE 3 DA REFATORAÇÃO DIMENSIONAL]
    Esta função foi descontinuada. A herança de matriz para filial (mesma raiz CNPJ)
    não gera mais clonagem sintética de linhas na fato_analise_credito.
    
    A governança e herança de risco são agora tratadas de forma declarativa e relacional
    na dimensão canônica: src/relational/dimensions/dim_estabelecimento.py
    através das colunas CNPJ_DOADOR_RISCO e ORIGEM_HERANCA_RISCO.
    """
    logger.warning(
        "[DEPRECATED] herdar_risco_filiais foi descontinuada. "
        "A herança de matriz para filial agora é resolvida dimensionalmente em dim_estabelecimento.py. "
        "Retornando DataFrame sem mutações sintéticas."
    )
    return df_fato
