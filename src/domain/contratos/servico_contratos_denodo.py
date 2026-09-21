"""Serviço oficial de ingestão de Contratos Correntes do Denodo."""

from __future__ import annotations

import logging
import calendar
import pandas as pd
import shutil
import uuid

from datetime import datetime
from pathlib import Path
from typing import Any

from app.context import AppContext
from common.dados import normalizar_coluna_cnpj
from common.hashing import arquivo_hash
from common.servico_desduplicacao import tem_hash_duplicado
from storage.armazenamento_manifest import historico_de_ingestao_de_carga, anexar_registro_de_manifesto
from services.connectors.denodo_connector import buscar_denodo
from storage.escrever_dados import escrever_conjunto_de_dados_silver
from control.logger import obter_logger

LOGGER = logging.getLogger(__name__)

def aplicar_regras_negocio_pandas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    col_cnpj = "contraparte_cnpj" if "contraparte_cnpj" in df.columns else "cnpj"
    if col_cnpj in df.columns:
        df = normalizar_coluna_cnpj(df, coluna_origem=col_cnpj)
        if "STATUS_CNPJ" not in df.columns and "CNPJ_STATUS" in df.columns:
            df["STATUS_CNPJ"] = df["CNPJ_STATUS"]
    else:
        df["CNPJ"]       = None
        df["CNPJ_RAIZ"]  = None
        df["STATUS_CNPJ"] = "CNPJ_AUSENTE"
        
    colunas_numericas = ["ano", "mes", "id_parte", "id_tipo_contrato", "id_contraparte", "id_status", "quant_contratada"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    def calcular_horas(row):
        try:
            ano = int(row.get("ano", 0))
            mes = int(row.get("mes", 0))
            if 2000 <= ano <= 2100 and 1 <= mes <= 12:
                return calendar.monthrange(ano, mes)[1] * 24
        except:
            pass
        return 730

    df["HORAS_MES"] = df.apply(calcular_horas, axis=1)
    df["VOLUME_MWH"] = df["quant_contratada"]
    df["VOLUME_MWM"] = df["quant_contratada"] / df["HORAS_MES"]

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
        (df.get("quant_contratada", 0) > 0)
    )
    
    if "ncdempresaproprietaria" in df.columns: filtro = filtro & (df["ncdempresaproprietaria"] == 297)
    if "id_contraparte" in df.columns: filtro = filtro & (df["id_contraparte"] != 9057)
    filtro = filtro & (df["STATUS_CNPJ"] == "CNPJ_VALIDO")

    return df.loc[filtro].drop(columns=["DT_IN_TEMP"]).copy()

def processar_contratos_denodo(context: AppContext) -> dict[str, Any]:
    run_id = f"CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/ingestion") / f"{run_id}__ingestao_contratos.log"
    logger = obter_logger("bdc.contratos", log_file)

    try:
        input_dir = context.path("entradas") / "contratos_denodo"
        vigente_dir = input_dir / "vigente"
        processadas_dir = input_dir / "processadas"
        rejeitadas_dir = input_dir / "rejeitadas"
        
        vigente_dir.mkdir(parents=True, exist_ok=True)
        processadas_dir.mkdir(parents=True, exist_ok=True)
        rejeitadas_dir.mkdir(parents=True, exist_ok=True)
        
        staging_dir = context.path("staging") / "denodo"
        staging_dir.mkdir(parents=True, exist_ok=True)

        ingestion_log_path = context.path("bronze_ingestion_log") / "contratos_denodo_ingestion.jsonl"
        history = historico_de_ingestao_de_carga(ingestion_log_path)

        # Checa se existe um arquivo manual ou legado solto em entradas/contratos_denodo
        arquivos_legado = list(input_dir.glob("*.csv"))
        if arquivos_legado:
            for al in arquivos_legado:
                shutil.move(str(al), str(vigente_dir / al.name))

        hoje_str = datetime.now().strftime("%Y%m%d")
        arquivos_locais = list(vigente_dir.glob("*.csv"))
        arquivos_processados_hoje = list(processadas_dir.glob(f"denodo_api_export_CTR_{hoje_str}*.csv"))
        
        df_raw = pd.DataFrame()
        source_file = None
        staging_file = None
        
        if arquivos_locais:
            source_file = max(arquivos_locais, key=lambda f: f.stat().st_mtime)
            logger.info("Lendo contratos de arquivo local: %s (Ignorando API)", source_file.name)
            staging_file = staging_dir / source_file.name
            shutil.copy2(source_file, staging_file)
        elif arquivos_processados_hoje:
            source_file = max(arquivos_processados_hoje, key=lambda f: f.stat().st_mtime)
            logger.info("Cache diario encontrado: %s (Ignorando consulta ODBC para evitar duplicidade)", source_file.name)
            staging_file = staging_dir / source_file.name
            shutil.copy2(source_file, staging_file)
        else:
            logger.info("Iniciando extração da view vwi_exportar_contrato via ODBC.")
            query_denodo = """
               SELECT com.vwi_exportar_contrato.movimentacao AS movimentacao,
                      com.vwi_exportar_contrato.contraparte_nome_fantasia AS contraparte_nome_fantasia,
                      com.vwi_exportar_contrato.contraparte_cnpj AS contraparte_CNPJ,
                      com.vwi_exportar_contrato.id_parte AS id_parte,
                      com.vwi_exportar_contrato.nome_contrato AS nome_contrato,
                      com.vwi_exportar_contrato.id_tipo_contrato AS id_tipo_contrato,
                      com.vwi_exportar_contrato.tipo_contrato AS tipo_contrato,
                      com.vwi_exportar_contrato.subtipo_contrato AS subtipo_contrato,
                      com.vwi_exportar_contrato.suprimento_inicio AS suprimento_inicio,
                      com.vwi_exportar_contrato.suprimento_termino AS suprimento_termino,
                      com.vwi_exportar_contrato.sigla_ccee_parte AS sigla_ccee,
                      com.vwi_exportar_contrato.submercado AS submercado,
                      com.vwi_exportar_contrato.codigo_ccee AS codigo_ccee,
                      com.vwi_exportar_contrato.codigo_wbc AS codigo_wbc,
                      com.vwi_exportar_contrato.contrato_rateio_principal AS contrato_rateio_principal,
                      com.vwi_exportar_contrato.rateio AS rateio,
                      com.vwi_exportar_contrato.data_assinatura AS data_assinatura,
                      com.vwi_exportar_contrato.data_criacao AS data_criacao,
                      com.vwi_exportar_contrato.data_fechamento AS data_fechamento,
                      com.vwi_exportar_contrato.id_status AS id_status,
                      com.vwi_exportar_contrato.status AS status,
                      com.vwi_exportar_contrato.data_publicacao AS data_publicacao,
                      com.vwi_exportar_contrato.texto_publicacao AS texto_publicacao,
                      com.vwi_exportar_contrato.motivo_publicacao AS motivo_publicacao,
                      com.vwi_exportar_contrato.usuario_cadastro AS usuario_cadastro,
                      com.vwi_exportar_contrato.usuario_ultima_alteracao AS usuario_ultima_alteracao,
                      com.vwi_exportar_contrato.usuario_proposta AS usuario_proposta,
                      com.vwi_exportar_contrato.numero_proposta AS numero_proposta,
                      com.vwi_exportar_contrato.codigo_oportunidade AS codigo_oportunidade,
                      com.vwi_exportar_contrato.codigo_proposta AS codigo_proposta,
                      com.vwi_exportar_contrato.agrupador AS agrupador,
                      com.vwi_exportar_contrato.contrato_vinculado AS contrato_vinculado,
                      com.vwi_exportar_contrato.ano AS ano,
                      com.vwi_exportar_contrato.mes AS mes,
                      com.vwi_exportar_contrato.regra_valor_fixo_unitario AS regra_valor_fixo_unitario,
                      com.vwi_exportar_contrato.quant_contratada AS quant_Contratada,
                      com.vwi_exportar_contrato.quant_sazonalizada AS quant_sazonalizada,
                      com.vwi_exportar_contrato.quant_solicitada AS quant_solicitada,
                      com.vwi_exportar_contrato.quant_faturada AS quant_faturada,
                      com.vwi_exportar_contrato.regra_preco AS regra_preco,
                      com.vwi_exportar_contrato.id_regra_preco AS id_regra_preco,
                      com.vwi_exportar_contrato.preco_base AS valor,
                      com.vwi_exportar_contrato.preco_atualizado AS valorreajustado,
                      com.vwi_exportar_contrato.form_agio AS form_agio,
                      com.vwi_exportar_contrato.form_preco_fixo AS form_preco_fixo,
                      com.vwi_exportar_contrato.reajuste_data AS reajuste_Data,
                      com.vwi_exportar_contrato.reajuste_data_primeiro_reajuste AS reajuste_data_primeiro_reajuste,
                      com.vwi_exportar_contrato.reajuste_data_base AS reajuste_data_base,
                      com.vwi_exportar_contrato.reajuste_periodicidade AS reajuste_periodicidade,
                      com.vwi_exportar_contrato.reajuste_prorata AS reajuste_prorata,
                      com.vwi_exportar_contrato.reajuste_referencia AS reajuste_referencia,
                      com.vwi_exportar_contrato.reajuste_indice_economico AS reajuste_indice_economico,
                      com.vwi_exportar_contrato.situacao_publicacao AS situacao_publicacao,
                      com.vwi_exportar_contrato.portfolio_vendedor AS portfolio_Vendedor,
                      com.vwi_exportar_contrato.portfolio_comprador AS portfolio_Comprador,
                      com.vwi_exportar_contrato.numero_referencia_contrato AS numero_referencia_contrato,
                      com.vwi_exportar_contrato.fonte_contrato AS fonte_contrato,
                      com.vwi_exportar_contrato.flexibilidade_mensal_min AS flexibilidademensalmin,
                      com.vwi_exportar_contrato.flexibilidade_mensal_max AS flexibilidademensalmax,
                      com.vwi_exportar_contrato.observacao AS observacao,
                      com.vwi_exportar_contrato.contraparte_apelido AS contraparte_apelido,
                      com.vwi_exportar_contrato.parte_apelido AS parte_apelido
               FROM com.vwi_exportar_contrato
               WHERE (
                         ano >= 2024
                         AND parte_apelido = 'COPEL COM'
                         AND contraparte_apelido <> 'COPEL COM - Transferência de energia'
                         AND ncdempresaproprietaria = 297
                         AND id_parte = 297
                         AND id_tipo_contrato IN (1, 3, 33, 90)
                         AND id_contraparte <> 9057
                         AND contrato_vinculado IS NULL
                         AND id_status NOT IN (0, 1, 4, 5, 6, 9, 10, 11)
                         AND (
                                quant_contratada > 0
                             OR quant_sazonalizada > 0
                         )
                     )
            """
            df_api = buscar_denodo(query=query_denodo)
            
            if df_api.empty:
                return {"run_id": run_id, "status": "SEM_DADOS", "linhas": 0}
                
            staging_file = staging_dir / f"api_snapshot_{run_id}.parquet"
            df_api.to_parquet(staging_file, index=False)
            
            # Exporta uma cópia em CSV para a pasta processadas para facilitar a auditoria visual
            csv_audit_file = processadas_dir / f"denodo_api_export_{run_id}.csv"
            df_api.to_csv(csv_audit_file, sep=";", index=False, encoding="utf-8-sig")
            logger.info("Cópia CSV de auditoria salva em %s", csv_audit_file.name)
            
            source_file = staging_file

        hash_arquivo = arquivo_hash(staging_file)
        
        silver_dir_check = context.path("silver") / "denodo_contratos_silver"
        silver_file_check = silver_dir_check / "contratos_correntes.parquet"

        if tem_hash_duplicado(history, hash_arquivo) and silver_file_check.exists():
            logger.info("Hash de Contratos Denodo duplicado (%s). Ignorando pipeline por idempotência.", hash_arquivo)
            if arquivos_locais and source_file:
                shutil.move(str(source_file), str(processadas_dir / source_file.name))
            return {"run_id": run_id, "status": "IGNORADO_DUPLICADO", "linhas": 0}

        manifest_record = {
            "documento_id": str(uuid.uuid4()),
            "run_id": run_id,
            "tipo_ficha": "DENODO_CONTRATOS",
            "arquivo_nome": source_file.name,
            "hash_arquivo": hash_arquivo,
            "data_processamento": datetime.now().isoformat(timespec="seconds"),
            "status_extracao": "SUCESSO"
        }

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "denodo"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        bronze_file = bronze_dir / f"raw_contratos_{run_id}{staging_file.suffix}"
        shutil.copy2(staging_file, bronze_file)
        
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest_record)

        if staging_file.suffix == ".parquet":
            df_raw = pd.read_parquet(staging_file)
        else:
            try:
                df_raw = pd.read_csv(staging_file, sep=",", dtype=str)
                if len(df_raw.columns) < 5:
                    df_raw = pd.read_csv(staging_file, sep=";", dtype=str)
            except Exception:
                df_raw = pd.read_csv(staging_file, sep=";", dtype=str)

        df_silver = aplicar_regras_negocio_pandas(df_raw)
        df_silver.columns = [str(c).strip().upper() for c in df_silver.columns]
        
        rename_map = {
            "NOME_CONTRATO": "CONTRATO", 
            "SUPRIMENTO_INICIO": "VIGENCIA_INICIO", 
            "SUPRIMENTO_TERMINO": "VIGENCIA_FIM"
        }
        df_silver = df_silver.rename(columns=rename_map)
        
        df_silver["QUANT_CONTRATADA"] = df_silver["QUANT_CONTRATADA"]
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = df_silver["VOLUME_MWM"]
        df_silver["VOLUME_MWH_ORIGINAL"] = df_silver["VOLUME_MWH"]
        df_silver["COMPETENCIA"] = df_silver["ANO"].astype(str).str.replace(r"\.0", "", regex=True) + df_silver["MES"].astype(str).str.replace(r"\.0", "", regex=True).str.zfill(2)
        
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = pd.to_numeric(df_silver["VOLUME_CONTRATADO_MENSAL_MWM"], errors="coerce").fillna(0.0)
        if "STATUS" not in df_silver.columns: df_silver["STATUS"] = "ATIVO"

        for col in ["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]:
            if col not in df_silver.columns: df_silver[col] = "NAO_INFORMADO"

        group_cols = ["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]
        for extra_col in ["NUMERO_REFERENCIA_CONTRATO", "CONTRAPARTE_APELIDO", "CONTRAPARTE_NOME_FANTASIA"]:
            if extra_col in df_silver.columns and extra_col not in group_cols:
                group_cols.append(extra_col)

        df_silver_final = df_silver.groupby(group_cols, as_index=False).agg({"VOLUME_CONTRATADO_MENSAL_MWM": "sum"})

        cols_identidade = ["CNPJ", "CNPJ_RAIZ", "STATUS_CNPJ"]
        cols_identidade_presentes = [c for c in cols_identidade if c in df_silver.columns]
        df_identidade = df_silver[cols_identidade_presentes].drop_duplicates(subset=["CNPJ"])
        df_silver_final = pd.merge(df_silver_final, df_identidade, on="CNPJ", how="left")
        
        df_silver_final["RUN_ID"] = run_id
        df_silver_final["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        silver_dir = context.path("silver") / "denodo_contratos_padronizados"
        silver_dir.mkdir(parents=True, exist_ok=True)
        
        for comp in df_silver_final["COMPETENCIA"].unique():
            if str(comp) in ["000", "NAO_INFORMADONAO_INFORMADO", "00", "nan00"]: continue
            df_comp = df_silver_final[df_silver_final["COMPETENCIA"] == comp]
            escrever_conjunto_de_dados_silver(records=df_comp.to_dict(orient="records"), output_dir=silver_dir, filename=f"contratos_correntes_{comp}")

        dir_reconciliacao = context.path("silver") / "denodo_contratos_silver"
        escrever_conjunto_de_dados_silver(records=df_silver_final.to_dict(orient="records"), output_dir=dir_reconciliacao, filename="contratos_correntes")
        
        if arquivos_locais and source_file:
            shutil.move(str(source_file), str(processadas_dir / source_file.name))

        logger.info("Contratos agregados e sem duplicidades salvos. %d registros limpos", len(df_silver_final))
        return {"run_id": run_id, "linhas_processadas": len(df_silver_final), "status": "SUCESSO"}
    except Exception as exc:
        logger.exception("Falha crítica na ingestão de contratos do Denodo.")
        if 'source_file' in locals() and arquivos_locais and source_file:
             shutil.move(str(source_file), str(rejeitadas_dir / source_file.name))
        raise Exception(f"Erro na ingestão Denodo: {exc}") from exc