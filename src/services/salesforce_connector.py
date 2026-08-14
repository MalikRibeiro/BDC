"""Conector de integração de arquivos extraídos do Salesforce (via Power Query)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

class SalesforceConnectionError(Exception):
    """Exceção levantada quando a base do Salesforce não pode ser obtida."""


def fetch_salesforce_data(
    input_dir: Path | str,
    logger: Any | None = None,
) -> Dict[str, pd.DataFrame]:
    """
    Lê o arquivo salesforce.xlsx atualizado via Power Query contendo as abas:
    Conta, Cotação, Chamado e Contrato. Retorna um dicionário de DataFrames.
    """
    diretorio = Path(input_dir)
    arquivo_sf = diretorio / "salesforce.xlsx"
    
    if logger:
        logger.info("Iniciando leitura da base local do Salesforce: %s", arquivo_sf)
        
    if not arquivo_sf.exists():
        if logger:
            logger.error("Arquivo %s não encontrado.", arquivo_sf)
        raise FileNotFoundError(f"Arquivo Salesforce não encontrado na pasta: {arquivo_sf}")

    resultados_df = {}
    
    # Mapeamento das abas do Excel para os nomes lógicos exigidos pelo sistema
    mapa_abas = {
        "Conta": "Account",
        "Cotação": "Cotacao",
        "Chamado": "Chamado",
        "Contrato": "Contrato"
    }

    try:
        for aba_excel, chave_dict in mapa_abas.items():
            if logger:
                logger.info("Lendo aba '%s' do Salesforce...", aba_excel)
            
            # Lendo tudo como string (dtype=str) para não corromper 'Id' e 'AccountId'
            df = pd.read_excel(arquivo_sf, sheet_name=aba_excel, dtype=str)
            
            # Tratamento de nulos vindos do Excel (transforma "nan" string em real None ou string vazia)
            df = df.fillna("")
            df = df.replace("nan", "")
            
            # Normalização específica da máscara de CNPJ na aba Conta
            if chave_dict == "Account" and "CNPJ__c" in df.columns:
                df["CNPJ__c"] = (
                    df["CNPJ__c"]
                    .astype(str)
                    .str.replace(r"\D", "", regex=True) # Remove pontos, traços e barras
                    .str.zfill(14) # Garante os 14 dígitos com zeros à esquerda
                )
            
            resultados_df[chave_dict] = df
            
            if logger:
                logger.info("Aba '%s' carregada com sucesso. %s registros processados.", aba_excel, len(df))

        return resultados_df

    except Exception as exc:
        if logger:
            logger.exception("Falha crítica ao ler o arquivo local do Salesforce.")
        raise SalesforceConnectionError(f"Erro ao processar as planilhas do Salesforce: {exc}") from exc