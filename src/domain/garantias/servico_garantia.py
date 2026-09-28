"""Serviço de ingestão, validação e alertas de Garantias.

Lê o CSV extraído da query customizada do Denodo, salva na Bronze,
valida regras de vigência e cobertura, gera alertas e publica na Silver.
Ref: §2 (Módulo Garantias), §6.8 do Planejamento Funcional.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

class GarantiaIngestionError(Exception):
    """Exceção levantada para falhas na ingestão de garantias."""

COBERTURA_MINIMA = 0.5

def inserir_dados_garantias(
    context: AppContext,
    df_garantias_externo: pd.DataFrame | None = None,
) -> dict[str, Any]:
    run_id = f"GAR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/ingestion") / f"{run_id}__ingestao_garantias.log"
    logger = obter_logger("bdc.garantias", log_file)

    try:
        logger.info("Iniciando ingestão de Garantias (Modo CSV Local).")

        if df_garantias_externo is not None:
            df_raw = df_garantias_externo.copy()
            logger.info("Usando DataFrame externo fornecido.")
        else:
            try:
                from services.connectors.denodo_connector import buscar_denodo
                processadas_dir = context.path("entradas") / "garantias" / "processadas"
                processadas_dir.mkdir(parents=True, exist_ok=True)
                hoje_str = datetime.now().strftime("%Y%m%d")
                arquivos_processados_hoje = list(processadas_dir.glob(f"denodo_garantias_odbc_GAR_{hoje_str}*.csv"))
                
                if arquivos_processados_hoje:
                    source_file = max(arquivos_processados_hoje, key=lambda f: f.stat().st_mtime)
                    logger.info("Cache diario encontrado: %s (Ignorando consulta ODBC para evitar duplicidade)", source_file.name)
                    df_raw = pd.read_csv(source_file, sep=";", encoding="utf-8-sig")
                else:
                    logger.info("Iniciando extração de Garantias via ODBC.")
                    query_garantias = """
                SELECT
                    dg.codigo AS garantia_id,
                    contraparte.cnpj_sem_formatacao AS cnpj_contraparte,
                    empresa_pai.razao_social AS grupo_economico,
                    dg.codigo_contrato AS contrato_vinculado,
                    dg.forma_garantia_selecionada AS tipo,
                    dg.opcao_receber_emitir AS modalidade,
                    dg.emitente_garantia AS garantidor_emissor,
                    NULL AS cnpj_garantidor,
                    COALESCE(dg.banco_emissor, dg.banco_gestor) AS instituicao_financeira,
                    COALESCE(beneficiario.razao_social, beneficiario.nome_fantasia, beneficiario.apelido) AS beneficiario,
                    fg.valor_calculado AS valor_nominal,
                    fg.valor_garantia AS valor_atualizado,
                    NULL AS moeda,
                    COALESCE(dg.data_envio_calculo, dgg.data_apresentacao_geral, dg.data_apresentacao) AS data_avaliacao,
                    NULL AS percentual_cobertura,
                    COALESCE(dg.periodo_inicio, dgg.inicio_vigencia_geral) AS data_inicio,
                    COALESCE(dg.periodo_fim, dgg.fim_vigencia_geral) AS vencimento,
                    CASE
                        WHEN COALESCE(dg.eh_excluido, dgg.eh_excluido, FALSE) = TRUE THEN 'CANCELADA'
                        WHEN COALESCE(dg.periodo_fim, dgg.fim_vigencia_geral) IS NOT NULL AND COALESCE(dg.periodo_fim, dgg.fim_vigencia_geral) < CURRENT_DATE THEN 'VENCIDA'
                        WHEN COALESCE(dg.periodo_inicio, dgg.inicio_vigencia_geral) IS NULL OR COALESCE(dg.periodo_fim, dgg.fim_vigencia_geral) IS NULL THEN 'PENDENTE'
                        WHEN COALESCE(dg.periodo_inicio, dgg.inicio_vigencia_geral) > CURRENT_DATE THEN 'PENDENTE'
                        ELSE 'VIGENTE'
                    END AS status,
                    CASE
                        WHEN COALESCE(dg.eh_excluido, dgg.eh_excluido, FALSE) = TRUE THEN 'NAO_ELEGIVEL'
                        WHEN COALESCE(dg.tem_garantia_apresentada, FALSE) = FALSE THEN 'NAO_ELEGIVEL'
                        WHEN COALESCE(dg.periodo_inicio, dgg.inicio_vigencia_geral) IS NULL OR COALESCE(dg.periodo_fim, dgg.fim_vigencia_geral) IS NULL THEN 'PENDENTE_VALIDACAO'
                        WHEN COALESCE(dg.periodo_inicio, dgg.inicio_vigencia_geral) > CURRENT_DATE THEN 'NAO_ELEGIVEL'
                        WHEN COALESCE(dg.periodo_fim, dgg.fim_vigencia_geral) < CURRENT_DATE THEN 'NAO_ELEGIVEL'
                        WHEN fg.valor_garantia IS NULL AND fg.valor_calculado IS NULL THEN 'PENDENTE_VALOR'
                        WHEN COALESCE(fg.valor_garantia, fg.valor_calculado) <= 0 THEN 'NAO_ELEGIVEL'
                        ELSE 'ELEGIVEL'
                    END AS elegibilidade,
                    COALESCE(dg.data_envio_calculo, dg.data_renovacao, dg.data_apresentacao, dgg.data_apresentacao_geral) AS data_ultima_validacao
                FROM com.dim_garantia dg
                LEFT JOIN com.fato_garantia fg ON fg.codigo_garantia = dg.codigo AND fg.codigo_contrato = dg.codigo_contrato
                LEFT JOIN com.dim_garantia_geral dgg ON dgg.codigo_contrato = dg.codigo_contrato
                LEFT JOIN com.dim_empresa contraparte ON contraparte.codigo = COALESCE(dg.codigo_empresa_afiancada, fg.codigo_empresa_afiancada)
                LEFT JOIN com.dim_empresa empresa_pai ON empresa_pai.codigo = contraparte.codigo_empresa_pai
                LEFT JOIN com.dim_empresa beneficiario ON beneficiario.codigo = COALESCE(dg.codigo_empresa_favorecida, fg.codigo_empresa_favorecida)
                """
                    df_raw = buscar_denodo(query=query_garantias)
                    if df_raw.empty:
                        raise ValueError("A extração ODBC de garantias retornou vazia.")
                        
                    processadas_dir = context.path("entradas") / "garantias" / "processadas"
                    processadas_dir.mkdir(parents=True, exist_ok=True)
                    csv_audit_file = processadas_dir / f"denodo_garantias_odbc_{run_id}.csv"
                    df_raw.to_csv(csv_audit_file, sep=";", index=False, encoding="utf-8-sig")
                    logger.info("Cópia CSV de auditoria salva em %s", csv_audit_file.name)

            except Exception as e:
                logger.warning(f"Erro na extração ODBC de garantias ({e}). Usando fallback de arquivo local.")
                input_dir = context.path("entradas") / "garantias"
                input_dir.mkdir(parents=True, exist_ok=True)
    
                arquivos = [
                    f for f in input_dir.iterdir()
                    if f.is_file() and f.suffix.lower() in {".xlsx", ".xls", ".csv"}
                    and not f.name.startswith("~$")
                ]
    
                if not arquivos:
                    logger.warning("Nenhum arquivo de garantias encontrado em %s.", input_dir)
                    return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}
    
                arquivo_fonte = max(arquivos, key=lambda f: f.stat().st_mtime)
                logger.info("Lendo garantias do arquivo local: %s", arquivo_fonte.name)
    
                if arquivo_fonte.suffix.lower() == ".csv":
                    df_raw = pd.read_csv(arquivo_fonte, dtype=str, sep=";", encoding="utf-8-sig")
                else:
                    df_raw = pd.read_excel(arquivo_fonte, dtype=str)
                    
                processadas_dir = context.path("entradas") / "garantias" / "processadas"
                processadas_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(arquivo_fonte), str(processadas_dir / f"{arquivo_fonte.stem}_{run_id}{arquivo_fonte.suffix}"))

        if df_raw.empty:
            return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "garantias"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        caminho_bronze = bronze_dir / f"raw_garantias_{datetime.now().strftime('%Y%m%d')}.parquet"
        
        df_raw.to_parquet(caminho_bronze, index=False)

        df_garantias = df_raw.copy()
        df_garantias.columns = [str(c).strip().upper() for c in df_garantias.columns]

        from common.identificadores import normalizar_cnpj_coluna
        df_garantias["CNPJ_CONTRAPARTE"] = df_garantias["CNPJ_CONTRAPARTE"].apply(normalizar_cnpj_coluna)
        df_garantias["VENCIMENTO"] = pd.to_datetime(df_garantias["VENCIMENTO"], errors="coerce")

        if "PERCENTUAL_COBERTURA" not in df_garantias.columns:
            df_garantias["PERCENTUAL_COBERTURA"] = 1.0
        else:
            df_garantias["PERCENTUAL_COBERTURA"] = pd.to_numeric(
                df_garantias["PERCENTUAL_COBERTURA"], errors="coerce"
            ).fillna(1.0)

        df_garantias["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
        df_garantias["RUN_ID"] = run_id

        silver_dir = context.path("silver") / "garantias_silver"
        escrever_conjunto_de_dados_silver(
            records=df_garantias.to_dict(orient="records"),
            output_dir=silver_dir,
            filename="garantia_silver"
        )

        logger.info("Ingestão de garantias na Silver concluída. Registros salvos: %s", len(df_garantias))

        return {
            "run_id": run_id,
            "linhas_processadas": len(df_garantias),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão de garantias.")
        raise GarantiaIngestionError(f"Erro ao ingerir base de garantias: {exc}") from exc