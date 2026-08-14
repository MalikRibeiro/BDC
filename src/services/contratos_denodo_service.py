"""Serviço oficial de ingestão de Contratos Correntes do Denodo."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from services.denodo_connector import fetch_denodo_rest
from storage.silver_store import write_silver_dataset

LOGGER = logging.getLogger(__name__)

def aplicar_regras_negocio_pandas(df: pd.DataFrame) -> pd.DataFrame:
    # Garante que todas as colunas estão em minúsculo para a filtragem não quebrar (CSV vs API)
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    colunas_numericas = ["ano", "ncdempresaproprietaria", "id_parte", "id_tipo_contrato", "id_contraparte", "id_status", "quant_contratada", "quant_sazonalizada"]
    for col in colunas_numericas:
        if col in df.columns:
            # Troca vírgula por ponto caso venha formato brasileiro do CSV
            df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Filtro operacional seguro
    filtro = (
        (df.get("ano", 0) >= 2020) & 
        (df.get("parte_apelido", "") == "COPEL COM") &
        (df.get("contraparte_apelido", "") != "COPEL COM - Transferência de energia") &
        (df.get("ncdempresaproprietaria", 0) == 297) & 
        (df.get("id_parte", 0) == 297) &
        (df.get("id_tipo_contrato", 0).isin([1, 3, 33, 90])) & 
        (df.get("id_contraparte", 0) != 9057) &
        (df.get("contrato_vinculado", "").isna() | (df.get("contrato_vinculado", "") == "")) &
        (~df.get("id_status", 0).isin([0, 1, 4, 5, 6, 9, 10, 11])) &
        ((df.get("quant_contratada", 0) > 0) | (df.get("quant_sazonalizada", 0) > 0))
    )
    return df[filtro].copy()

def ingest_contratos_denodo(context: AppContext) -> dict[str, Any]:
    run_id = f"CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.contratos")

    try:
        # ESTRATÉGIA OFFLINE/LOCAL: Lê o CSV se existir para evitar Timeout na API da rede
        input_dir = context.path("entradas") / "contratos_denodo"
        arquivos_locais = list(input_dir.glob("*.csv"))
        
        df_raw = pd.DataFrame()
        if arquivos_locais:
            arquivo = max(arquivos_locais, key=lambda f: f.stat().st_mtime)
            logger.info("Lendo contratos de arquivo local: %s (Ignorando API para evitar timeout da rede)", arquivo.name)
            # Tenta ler separado por vírgula, se não der, tenta ponto e vírgula
            try:
                df_raw = pd.read_csv(arquivo, sep=",", dtype=str)
                if len(df_raw.columns) < 5:
                    df_raw = pd.read_csv(arquivo, sep=";", dtype=str)
            except Exception:
                df_raw = pd.read_csv(arquivo, sep=";", dtype=str)
        else:
            logger.info("Iniciando extração da view vwi_exportar_contrato via REST.")
            colunas_necessarias = "ano,mes,ncdempresaproprietaria,id_parte,id_tipo_contrato,id_contraparte,contrato_vinculado,id_status,quant_contratada,quant_sazonalizada,parte_apelido,contraparte_apelido,contraparte_cnpj,nome_contrato,suprimento_inicio,suprimento_termino,status"
            parametros_api = {
                "$select": colunas_necessarias, 
                "$filter": "ano >= 2024 AND parte_apelido = 'COPEL COM' AND id_parte = 297 AND ncdempresaproprietaria = 297"
            }
            df_raw = fetch_denodo_rest("vwi_exportar_contrato", params=parametros_api)
        
        if df_raw.empty: return {"run_id": run_id, "status": "SEM_DADOS", "linhas": 0}

        # Backup Bronze
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "denodo"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        df_raw.to_parquet(bronze_dir / f"raw_contratos_{run_id}.parquet", index=False)

        # Processamento e Limpeza
        df_silver = aplicar_regras_negocio_pandas(df_raw)
        df_silver.columns = [str(c).strip().upper() for c in df_silver.columns]
        
        # Mapeamento robusto para diferenças entre CSV e API
        rename_map = {
            "CONTRAPARTE_CNPJ": "CNPJ", 
            "NOME_CONTRATO": "CONTRATO", 
            "SUPRIMENTO_INICIO": "VIGENCIA_INICIO", 
            "SUPRIMENTO_TERMINO": "VIGENCIA_FIM"
        }
        df_silver = df_silver.rename(columns=rename_map)
        
        if "CNPJ" not in df_silver.columns and "CONTRAPARTE_CNPJ" in df_silver.columns:
            df_silver = df_silver.rename(columns={"CONTRAPARTE_CNPJ": "CNPJ"})
        
        # Volumes e Competências
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = df_silver["QUANT_SAZONALIZADA"].where(df_silver["QUANT_SAZONALIZADA"] > 0, df_silver["QUANT_CONTRATADA"])
        df_silver["COMPETENCIA"] = df_silver["ANO"].astype(str).str.replace(r"\.0", "", regex=True) + df_silver["MES"].astype(str).str.replace(r"\.0", "", regex=True).str.zfill(2)
        
        # NORMALIZAÇÃO DO CNPJ ESTREITA (Regex limpa pontuação)
        df_silver["CNPJ"] = df_silver["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = pd.to_numeric(df_silver["VOLUME_CONTRATADO_MENSAL_MWM"], errors="coerce").fillna(0.0)
        if "STATUS" not in df_silver.columns: df_silver["STATUS"] = "ATIVO"

        # Garantia de colunas para o groupby
        for col in ["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]:
            if col not in df_silver.columns: df_silver[col] = "NAO_INFORMADO"

        # RESOLUÇÃO DA EXPLOSÃO CARTESIANA: Agrupando o volume por Contrato Único
        df_silver_final = df_silver.groupby(["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"], as_index=False).agg({"VOLUME_CONTRATADO_MENSAL_MWM": "sum"})
        
        df_silver_final["RUN_ID"] = run_id
        df_silver_final["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        # Persistência Silver
        silver_dir = context.path("silver") / "denodo_contratos_padronizados"
        silver_dir.mkdir(parents=True, exist_ok=True)
        
        for comp in df_silver_final["COMPETENCIA"].unique():
            if str(comp) in ["000", "NAO_INFORMADONAO_INFORMADO", "00", "nan00"]: continue
            df_comp = df_silver_final[df_silver_final["COMPETENCIA"] == comp]
            write_silver_dataset(records=df_comp.to_dict(orient="records"), output_dir=silver_dir, filename=f"contratos_correntes_{comp}")

        dir_reconciliacao = context.path("silver") / "denodo_contratos_silver"
        write_silver_dataset(records=df_silver_final.to_dict(orient="records"), output_dir=dir_reconciliacao, filename="contratos_correntes")
        
        logger.info("Contratos agregados e sem duplicidades salvos. %d registros limpos", len(df_silver_final))
        return {"run_id": run_id, "linhas_processadas": len(df_silver_final), "status": "SUCESSO"}
    except Exception as exc:
        logger.exception("Falha crítica na ingestão de contratos do Denodo.")
        raise Exception(f"Erro na ingestão Denodo: {exc}") from exc