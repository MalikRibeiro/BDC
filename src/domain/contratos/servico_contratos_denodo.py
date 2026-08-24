"""Serviço oficial de ingestão de Contratos Correntes do Denodo."""

from __future__ import annotations

import logging
import calendar
import pandas as pd

from datetime import datetime
from pathlib import Path
from typing import Any

from app.context import AppContext
from silver.normalizadores import padronizar_cnpj
from services.connectors.denodo_connector import buscar_denodo
from storage.escrever_dados import escrever_conjunto_de_dados_silver

LOGGER = logging.getLogger(__name__)

def aplicar_regras_negocio_pandas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # 1. TRATAMENTO DE CNPJ — via validador centralizado
    col_cnpj = "contraparte_cnpj" if "contraparte_cnpj" in df.columns else "cnpj"
    if col_cnpj in df.columns:
        parsed = df[col_cnpj].map(padronizar_cnpj)
        df["CNPJ"]       = parsed.map(lambda t: t[0])
        df["CNPJ_RAIZ"]  = parsed.map(lambda t: t[1])
        df["STATUS_CNPJ"] = parsed.map(lambda t: t[2])
    else:
        df["CNPJ"]       = None
        df["CNPJ_RAIZ"]  = None
        df["STATUS_CNPJ"] = "CNPJ_AUSENTE"
        
    # 2. TIPAGEM E NORMALIZAÇÃO
    colunas_numericas = ["ano", "mes", "id_parte", "id_tipo_contrato", "id_contraparte", "id_status", "quant_contratada"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 3. CÁLCULO DE MWh PARA MWm (Unidade Exclusiva: quant_contratada)
    def calcular_horas(row):
        try:
            ano = int(row.get("ano", 0))
            mes = int(row.get("mes", 0))
            if 2000 <= ano <= 2100 and 1 <= mes <= 12:
                return calendar.monthrange(ano, mes)[1] * 24
        except:
            pass
        return 730 # Fallback

    df["HORAS_MES"] = df.apply(calcular_horas, axis=1)
    df["VOLUME_MWH"] = df["quant_contratada"] # Preserva a origem auditável
    df["VOLUME_MWM"] = df["quant_contratada"] / df["HORAS_MES"] # Conversão Real

    # 4. IDENTIFICAÇÃO DE FUTUROS E GRANULARIDADE
    col_in = "suprimento_inicio" if "suprimento_inicio" in df.columns else ("vigencia_inicio" if "vigencia_inicio" in df.columns else "inicio_suprimento")
    df["DT_IN_TEMP"] = pd.to_datetime(df.get(col_in), errors="coerce")
    hoje = pd.Timestamp("today").normalize()
    filtro_futuros = (df["DT_IN_TEMP"] > hoje)

    filtro = (
        (df.get("ano", 0) >= 2020) & 
        (df.get("parte_apelido", "") == "COPEL COM") &
        (df.get("contraparte_apelido", "") != "COPEL COM - Transferência de energia") &
        (df.get("id_parte", 0) == 297) &
        (df.get("id_tipo_contrato", 0).isin([1, 3, 33, 90])) & 
        (df.get("contrato_vinculado", "").isna() | (df.get("contrato_vinculado", "") == "")) &
        ((~df.get("id_status", 0).isin([0, 1, 4, 5, 6, 9, 10, 11])) | filtro_futuros) & 
        (df.get("quant_contratada", 0) > 0) # Removido uso de quant_sazonalizada
    )
    
    if "ncdempresaproprietaria" in df.columns: filtro = filtro & (df["ncdempresaproprietaria"] == 297)
    if "id_contraparte" in df.columns: filtro = filtro & (df["id_contraparte"] != 9057)
    filtro = filtro & (df["STATUS_CNPJ"] == "CNPJ_VALIDO")

    return df.loc[filtro].drop(columns=["DT_IN_TEMP"]).copy()

def processar_contratos_denodo(context: AppContext) -> dict[str, Any]:
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
            df_raw = buscar_denodo("vwi_exportar_contrato", params=parametros_api)
        
        if df_raw.empty: return {"run_id": run_id, "status": "SEM_DADOS", "linhas": 0}

        # Backup Bronze
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "denodo"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        df_raw.to_parquet(bronze_dir / f"raw_contratos_{run_id}.parquet", index=False)

        # Processamento e Limpeza
        df_silver = aplicar_regras_negocio_pandas(df_raw)
        df_silver.columns = [str(c).strip().upper() for c in df_silver.columns]
        
        # O CNPJ já foi limpo e criado na função aplicar_regras_negocio_pandas!
        # Removida a conversão duplicada "CONTRAPARTE_CNPJ": "CNPJ"
        rename_map = {
            "NOME_CONTRATO": "CONTRATO", 
            "SUPRIMENTO_INICIO": "VIGENCIA_INICIO", 
            "SUPRIMENTO_TERMINO": "VIGENCIA_FIM"
        }
        df_silver = df_silver.rename(columns=rename_map)
        
        # Volumes e Competências
        df_silver["QUANT_CONTRATADA"] = df_silver["QUANT_CONTRATADA"]
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = df_silver["VOLUME_MWM"] # O valor já dividido e convertido em MWm
        df_silver["VOLUME_MWH_ORIGINAL"] = df_silver["VOLUME_MWH"] # Preserva a origem auditável
        df_silver["COMPETENCIA"] = df_silver["ANO"].astype(str).str.replace(r"\.0", "", regex=True) + df_silver["MES"].astype(str).str.replace(r"\.0", "", regex=True).str.zfill(2)
        
        # A normalização de regex do CNPJ foi removida daqui, pois já foi feita na origem.
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = pd.to_numeric(df_silver["VOLUME_CONTRATADO_MENSAL_MWM"], errors="coerce").fillna(0.0)
        if "STATUS" not in df_silver.columns: df_silver["STATUS"] = "ATIVO"

        # Garantia de colunas para o groupby
        for col in ["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]:
            if col not in df_silver.columns: df_silver[col] = "NAO_INFORMADO"

        # RESOLUÇÃO DA EXPLOSÃO CARTESIANA: Agrupando o volume por Contrato Único
        df_silver_final = df_silver.groupby(["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"], as_index=False).agg({"VOLUME_CONTRATADO_MENSAL_MWM": "sum"})

        # Preserva CNPJ_RAIZ e STATUS_CNPJ (descartadas pelo groupby) reinserindo via merge
        cols_identidade = ["CNPJ", "CNPJ_RAIZ", "STATUS_CNPJ"]
        cols_identidade_presentes = [c for c in cols_identidade if c in df_silver.columns]
        df_identidade = df_silver[cols_identidade_presentes].drop_duplicates(subset=["CNPJ"])
        df_silver_final = pd.merge(df_silver_final, df_identidade, on="CNPJ", how="left")
        
        df_silver_final["RUN_ID"] = run_id
        df_silver_final["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        # Persistência Silver
        silver_dir = context.path("silver") / "denodo_contratos_padronizados"
        silver_dir.mkdir(parents=True, exist_ok=True)
        
        for comp in df_silver_final["COMPETENCIA"].unique():
            if str(comp) in ["000", "NAO_INFORMADONAO_INFORMADO", "00", "nan00"]: continue
            df_comp = df_silver_final[df_silver_final["COMPETENCIA"] == comp]
            escrever_conjunto_de_dados_silver(records=df_comp.to_dict(orient="records"), output_dir=silver_dir, filename=f"contratos_correntes_{comp}")

        dir_reconciliacao = context.path("silver") / "denodo_contratos_silver"
        escrever_conjunto_de_dados_silver(records=df_silver_final.to_dict(orient="records"), output_dir=dir_reconciliacao, filename="contratos_correntes")
        
        logger.info("Contratos agregados e sem duplicidades salvos. %d registros limpos", len(df_silver_final))
        return {"run_id": run_id, "linhas_processadas": len(df_silver_final), "status": "SUCESSO"}
    except Exception as exc:
        logger.exception("Falha crítica na ingestão de contratos do Denodo.")
        raise Exception(f"Erro na ingestão Denodo: {exc}") from exc