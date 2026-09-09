"""Serviço principal refatorado do pipeline de fichas de consumidores."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.context import AppContext
from relational.facts.fato_alerta_util import registrar_alerta
from common.excel import fechar_pasta, abrir_pasta
from common.hashing import arquivo_hash
from common.json import ler_json
from control.logger import obter_logger
from common.identificadores import normalizar_cnpj

from control.layout_catalog import carregar_layouts_consumidores
from control.carregador_de_mapeamento import mapeamento_de_carga_fichas_consumidores
from control.quality_loader import carregar_regras_de_qualidade_de_dados_consumidores
from common.servico_desduplicacao import (
    tem_chave_de_negocio_duplicada,
    tem_hash_duplicado,
    virar_chave_de_negocio_no_historico,
)
from domain.fichas.validador import validar_registro_consumidor
from domain.consumidores.classificacao import (
    classificar_consumidor,
    criar_classificacao_registro,
    VERSAO_REGRA_ATUAL,
)
from silver.documentos_classificados import criar_documento_classificado
from silver.formatador_silver import normalizar_registro
from staging.staging_arquivo import copiar_para_staging
from storage.bronze_arquivo import publicar_arquivo_bruto
from storage.armazenamento_manifest import (
    historico_de_ingestao_de_carga,
)
from storage.escrever_dados import (
    mesclar_conjunto_de_dados_prata_por_chave_de_negocio,
    escrever_conjunto_de_dados_silver,
)
from storage.estado_armazenamento import DocumentManifest
from common.utils_orquestracao import (
    disco_cheio_erro,
    criar_run_id,
    criar_nome_arquivo_padronizado,
    resolver_subpasta_bronze,
    criar_fila_processamento,
    mover_para_rejeitados,
    mover_para_processados
)

def carregar_overrides_manuais(eventos_manuais_path: Path, logger: Any) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """Carrega de forma segura os dados de overrides manuais armazenados em formato Parquet."""
    overrides_dict: dict[tuple[str, str], list[dict[str, Any]]] = {}
    if not eventos_manuais_path.exists():
        logger.info("Nenhuma base de Carga Manual encontrada em %s", eventos_manuais_path)
        return overrides_dict
        
    try:
        import pandas as pd
        df_overrides = pd.read_parquet(eventos_manuais_path)
        
        if df_overrides.empty:
            return overrides_dict
            
        if "_STATUS_REGISTRO" in df_overrides.columns:
            df_overrides = df_overrides[df_overrides["_STATUS_REGISTRO"] == "VIGENTE"]
            
        df_overrides = df_overrides.dropna(subset=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "CAMPO_AFETADO"])
        
        from common.identificadores import normalizar_cnpj as _normalizar_cnpj
        from common.datas import normalizar_data
        
        for row in df_overrides.to_dict(orient="records"):
            res_cnpj = _normalizar_cnpj(row.get("CNPJ"))
            cnpj_over = res_cnpj.cnpj if res_cnpj.valido else None
            data_over = normalizar_data(row.get("DATA_DEMONSTRACAO_FINANCEIRA"))
            
            if not cnpj_over or not data_over:
                continue
                
            chave = (cnpj_over, data_over)
            
            if chave not in overrides_dict:
                overrides_dict[chave] = []
                
            valor_salvo = row.get("VALOR_NOVO")
            valor_tratado = valor_salvo
            
            if isinstance(valor_salvo, str):
                try:
                    valor_tratado = float(valor_salvo)
                except ValueError:
                    pass
                
            campo_afetado = str(row.get("CAMPO_AFETADO", "")).strip().upper().replace(" ", "_")
            
            overrides_dict[chave].append({
                "campo": campo_afetado if campo_afetado and campo_afetado != "NONE" else row.get("CAMPO_AFETADO"),
                "valor": valor_tratado
            })
            
        logger.info("Base de Overrides carregada: %d chaves vigentes.", len(overrides_dict))
    except Exception:
        logger.exception("Falha ao carregar overrides Parquet. Ignorando carga manual.")
        
    return overrides_dict

def aplicar_overrides_manuais(
    registro: dict[str, Any], 
    overrides_dict: dict[tuple[str, str], list[dict[str, Any]]], 
    logger: Any
) -> None:
    """Aplica as atualizações manuais injetando os valores na ficha normalizada."""
    from common.identificadores import normalizar_cnpj as _normalizar_cnpj
    from common.datas import normalizar_data
    
    cnpj_atual = registro.get("CNPJ")
    data_bruta = registro.get("DATA_DEMONSTRACAO_FINANCEIRA")
    
    if not cnpj_atual:
        return
        
    res_cnpj = _normalizar_cnpj(cnpj_atual)
    cnpj_normalizado = res_cnpj.cnpj if res_cnpj.valido else None
    
    if not cnpj_normalizado:
        return
    
    data_normalizada = normalizar_data(data_bruta) if data_bruta else None
    
    if data_normalizada:
        chave_atual = (cnpj_normalizado, data_normalizada)
        if chave_atual in overrides_dict:
            for override in overrides_dict[chave_atual]:
                campo = override["campo"]
                novo_valor = override["valor"]
                if campo:
                    valor_antigo = registro.get(campo)
                    registro[campo] = novo_valor
                    registro[f"_INDICADOR_DADO_MANUAL_{campo}"] = True
                    logger.warning(
                        "[OVERRIDE MANUAL] CNPJ %s | %s alterado de '%s' para '%s'.", 
                        cnpj_normalizado, campo, valor_antigo, novo_valor
                    )
            return
    
    cnpjs_no_override = {k[0] for k in overrides_dict.keys()}
    if cnpj_normalizado in cnpjs_no_override:
        chaves_deste_cnpj = [k for k in overrides_dict.keys() if k[0] == cnpj_normalizado]
        for chave_override in chaves_deste_cnpj:
            data_override = chave_override[1]
            if data_normalizada is None:
                logger.warning(
                    "[OVERRIDE IGNORADO] CNPJ encontrado (%s), mas DATA_DEMONSTRACAO_FINANCEIRA da ficha é nula. Override esperava data: %s.",
                    cnpj_normalizado, data_override
                )
            else:
                logger.warning(
                    "[OVERRIDE IGNORADO] CNPJ encontrado (%s), mas divergência de data. Ficha: %s | Override: %s.",
                    cnpj_normalizado, data_normalizada, data_override
                )

def processar_arquivo_individual(
    source_file: Path,
    load_mode: str,
    processed_dir: Path,
    rejected_dir: Path,
    context: AppContext,
    layouts: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    master_catalog: dict[str, Any],
    overrides_dict: dict[tuple[str, str], list[dict[str, Any]]],
    control_dir: Path | None = None,
) -> Optional[dict[str, Any]]:
    """Processa isoladamente um único arquivo de ficha de consumidor."""
    workbook = None
    manifest = DocumentManifest(
        documento_id=str(uuid.uuid4()),
        run_id=run_id,
        ambiente=context.app_config["env"],
        tipo_ficha="CONSUMIDOR",
        arquivo_nome=source_file.name,
        caminho_origem=str(source_file),
        load_mode=load_mode,
    )

    try:
        logger.info(
            "Iniciando processamento do arquivo %s em modo %s.",
            source_file.name,
            load_mode,
        )

        manifest.hash_arquivo = arquivo_hash(source_file)

        if load_mode == "incremental" and tem_hash_duplicado(
            history, manifest.hash_arquivo
        ):
            manifest.status_extracao = "ERRO_DUPLICIDADE_HASH"
            manifest.erros.append("Hash já processado anteriormente.")
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        staging_dir = context.path("staging_fichas_consumidores")
        staging_name = criar_nome_arquivo_padronizado(
            original_name=source_file.name,
            versao_ficha=None,
            cnpj=None,
            data_df=None,
            hash_value=manifest.hash_arquivo,
        )
        staging_file = copiar_para_staging(source_file, staging_dir, staging_name)
        manifest.caminho_staging = str(staging_file)

        workbook = abrir_pasta(staging_file)
        from domain.fichas.extrator import extrair_registro_do_vencedor

        raw_record, metadata_list, winner_layout = extrair_registro_do_vencedor(workbook, layouts, master_catalog)

        if winner_layout == "DOC_001_ESTRUTURA_INCOMPATIVEL":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            msg = "DOC_001_ESTRUTURA_INCOMPATIVEL: Nenhuma aba compativel com o layout esperada foi encontrada."
            manifest.erros.append(msg)
            registrar_alerta(
                codigo="DOC_001",
                severidade="ALTO",
                regra="Estrutura de Ficha Incompatível",
                mensagem=msg,
                campo_afetado="CLASSIFICACAO_DOCUMENTO",
                valor_observado="Desconhecido",
                limite_esperado="Layout mapeado",
                contraparte_id=None,
                run_id=run_id,
                context=context
            )
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if not winner_layout or winner_layout == "NENHUM":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("Nenhum layout obteve score suficiente.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        manifest.versao_ficha = winner_layout
        manifest.status_classificacao = "CLASSIFICADO"

        logger.info(
            "Extração competitiva: Vencedor %s identificado para %s.",
            winner_layout,
            source_file.name,
        )

        classification = type("MockClassification", (), {"versao_ficha": winner_layout})()
        
        if control_dir and metadata_list:
            from domain.auditoria.servico_auditoria import registrar_linhagem_campos
            registrar_linhagem_campos(manifest.documento_id, manifest.run_id, metadata_list, control_dir)
        
        normalized = normalizar_registro(raw_record, master_catalog, logger)
        normalized.pop("DADOS_CADASTRAIS", None)
        normalized["TIPO_FICHA"] = "CONSUMIDOR"
        
        from silver.mapeador_dominio import aplicar_normalizacao_de_dominio
        normalized = aplicar_normalizacao_de_dominio(normalized, context, logger)

        from domain.fichas.derivador_financeiro import calcular_indicadores_derivados
        normalized = calcular_indicadores_derivados(normalized)

        aplicar_overrides_manuais(normalized, overrides_dict, logger)

        manifest.cnpj_extraido = normalized.get("CNPJ")
        manifest.data_demonstracao_financeira = normalized.get(
            "DATA_DEMONSTRACAO_FINANCEIRA"
        )
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        classificacao = classificar_consumidor(
            record=normalized,
            versao_layout=classification.versao_ficha,
        )

        logger.info(
            "Classificação documental para %s: tipo=%s analise=%s confianca=%s",
            source_file.name,
            classificacao.tipo_consumidor,
            classificacao.tipo_analise_exigida,
            classificacao.confianca_classificacao,
        )

        if getattr(classificacao, "tipo_analise_exigida", "") == "simplificada":
            campos_df = [
                "ATIVO_CIRCULANTE", "ATIVO_TOTAL", "PASSIVO_CIRCULANTE", "PATRIMONIO_LIQUIDO",
                "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "ROA", "ROE", "FCO_ROL"
            ]
            for campo in campos_df:
                if campo not in normalized or normalized[campo] is None:
                    normalized[campo] = None

        errors, warnings = validar_registro_consumidor(
            record=normalized,
            master_catalog=master_catalog,
            classificacao=classificacao,
            logger=logger,
        )
        
        integridade = normalized.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        if integridade >= 40.0:
            critical_errors = []
            for e in errors:
                if "ausente" in e.lower() or "não informado" in e.lower() or "não informada" in e.lower():
                    warnings.append(f"Ignorado por Integridade >= 40%: {e}")
                else:
                    critical_errors.append(e)
            errors = critical_errors

        manifest.erros.extend(errors)
        manifest.avisos.extend(warnings)

        if integridade < 40.0:
            manifest.status_extracao = "ERRO_INTEGRIDADE"
            manifest.erros.append(f"Integridade baixa: {integridade}% (mínimo 40%). Ficha rejeitada.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if not manifest.cnpj_extraido:
            manifest.status_extracao = "ERRO_SEM_CNPJ"
            manifest.erros.append("Ficha sem CNPJ válido.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        resultado_cnpj = normalizar_cnpj(manifest.cnpj_extraido)
        if not resultado_cnpj.valido:
            manifest.status_extracao = "ERRO_CNPJ_INVALIDO"
            manifest.erros.append(f"CNPJ inválido: {manifest.cnpj_extraido}")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        manifest.cnpj_extraido = resultado_cnpj.cnpj
        normalized["CNPJ"] = resultado_cnpj.cnpj
        normalized["CNPJ_RAIZ"] = resultado_cnpj.raiz

        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO"
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        duplicate_business = tem_chave_de_negocio_duplicada(
            history,
            manifest.cnpj_extraido,
            manifest.data_demonstracao_financeira,
        )

        if duplicate_business and load_mode == "incremental":
            manifest.status_extracao = "ERRO_DUPLICIDADE_NEGOCIO"
            manifest.erros.append(
                "Já existe documento com mesmo CNPJ e data da DF."
            )
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if duplicate_business and load_mode == "reprocess":
            manifest.reprocessed = True
            manifest.previous_record_found = True
        elif load_mode == "reprocess":
            manifest.reprocessed = False
            manifest.previous_record_found = False

        fechar_pasta(workbook)
        workbook = None

        bronze_root_dir = context.path("bronze_fichas_consumidores_raw")
        bronze_name = criar_nome_arquivo_padronizado(
            original_name=source_file.name,
            versao_ficha=manifest.versao_ficha,
            cnpj=manifest.cnpj_extraido,
            data_df=manifest.data_demonstracao_financeira,
            hash_value=manifest.hash_arquivo,
        )

        bronze_subfolder = resolver_subpasta_bronze(
            manifest.cnpj_extraido,
            normalized.get("EMPRESA"),
        )

        bronze_staging = copiar_para_staging(
            staging_file, staging_dir, bronze_name
        )
        bronze_file = publicar_arquivo_bruto(
            source_file=bronze_staging,
            bronze_root_dir=bronze_root_dir / bronze_subfolder,
        )
        manifest.caminho_bronze = str(bronze_file)
        manifest.status_extracao = "SUCESSO"

        mover_para_processados(
            source_file, processed_dir, manifest, ingestion_log_path, logger, control_dir
        )
        virar_chave_de_negocio_no_historico(history, manifest.to_dict())

        logger.info("Ficha processada com sucesso: %s.", source_file.name)

        classificacao_record = criar_classificacao_registro(classificacao)

        silver_record = {
            **normalized,
            **classificacao_record,
            "documento_id": manifest.documento_id,
            "run_id": run_id,
            "ambiente": manifest.ambiente,
            "versao_ficha": manifest.versao_ficha,
            "arquivo_nome": manifest.arquivo_nome,
            "hash_arquivo": manifest.hash_arquivo,
            "load_mode": load_mode,
            "dt_processamento": datetime.now().isoformat(timespec="seconds"),
        }

        from domain.fichas.validador import validar_schema
        schema_errors = validar_schema(silver_record, logger)
        if schema_errors:
            manifest.status_extracao = "ERRO_CONTRATO_SILVER"
            manifest.erros.extend(schema_errors)
            logger.warning("Violação de contrato Silver para CNPJ=%s: %s", manifest.cnpj_extraido, schema_errors)

        classified_document = criar_documento_classificado(
            documento_id=manifest.documento_id,
            run_id=run_id,
            ambiente=manifest.ambiente,
            arquivo_nome=manifest.arquivo_nome or "",
            versao_ficha=manifest.versao_ficha or "",
            TIPO_FICHA=manifest.tipo_ficha,
            hash_arquivo=manifest.hash_arquivo or "",
        )

        return {
            "silver_record": silver_record,
            "classified_document": classified_document,
        }

    except Exception as exc:
        if workbook:
            fechar_pasta(workbook)

        manifest.status_extracao = "ERRO_PROCESSAMENTO"
        manifest.erros.append(str(exc))

        if disco_cheio_erro(exc):
            logger.exception(
                "Execução interrompida por falta de espaço em disco ao processar %s.",
                source_file.name,
            )
            raise

        try:
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
        except Exception as move_exc:
            if disco_cheio_erro(move_exc):
                logger.exception(
                    "Execução interrompida por falta de espaço em disco ao registrar rejeição do arquivo %s.",
                    source_file.name,
                )
                raise

            logger.exception(
                "Falha adicional ao mover/gravar rejeição do arquivo %s.",
                source_file.name,
            )
            raise

        logger.exception("Falha inesperada ao processar %s.", source_file.name)
        return None


def processar_fichas_consumidores(
    context: AppContext,
) -> dict[str, Any]:
    """Executa o pipeline completo das fichas de consumidores."""
    run_id = criar_run_id(context)

    log_file = (
        Path("LOGS/execucao") / f"{run_id}__fichas_consumidores.log"
    )
    logger = obter_logger("bdc.consumidores", log_file)

    _ = mapeamento_de_carga_fichas_consumidores(context, logger)

    layouts = carregar_layouts_consumidores(context, logger)
    master_catalog = carregar_regras_de_qualidade_de_dados_consumidores(context, logger)

    ingestion_log_path = (
        context.path("bronze_ingestion_log")
        / "fichas_consumidores_ingestion.jsonl"
    )
    history = historico_de_ingestao_de_carga(ingestion_log_path)

    silver_records: list[dict[str, Any]] = []
    classified_documents: list[dict[str, Any]] = []

    eventos_manuais_path = context.path("silver") / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"
    overrides_dict = carregar_overrides_manuais(eventos_manuais_path, logger)

    queue = criar_fila_processamento(context, "consumidores")

    normal_count = sum(1 for _, mode, _, _ in queue if mode == "incremental")
    reprocess_count = sum(1 for _, mode, _, _ in queue if mode == "reprocess")

    logger.info(
        "Iniciando processamento de %s fichas (%s normais, %s reprocessamento).",
        len(queue),
        normal_count,
        reprocess_count,
    )

    for source_file, load_mode, processed_dir, rejected_dir in queue:
        result = processar_arquivo_individual(
            source_file=source_file,
            load_mode=load_mode,
            processed_dir=processed_dir,
            rejected_dir=rejected_dir,
            context=context,
            layouts=layouts,
            history=history,
            ingestion_log_path=ingestion_log_path,
            logger=logger,
            run_id=run_id,
            master_catalog=master_catalog,
            overrides_dict=overrides_dict,
            control_dir=context.path("relational_control"),
        )

        if result:
            silver_records.append(result["silver_record"])
            classified_documents.append(result["classified_document"])

    silver_output_dir = context.path("silver_fichas_consumidores_extraidas")
    docs_output_dir = context.path("silver_documentos_classificados")

    if silver_records:
        mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
            records=silver_records,
            output_dir=silver_output_dir,
            filename="fichas_consumidores_extraidas.csv",
            business_keys=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA"],
        )

    if classified_documents:
        escrever_conjunto_de_dados_silver(
            records=classified_documents,
            output_dir=docs_output_dir,
            filename=f"documentos_classificados__{run_id}",
        )

    summary = {
        "run_id": run_id,
        "arquivos_recebidos": len(queue),
        "arquivos_normais": normal_count,
        "arquivos_reprocessamento": reprocess_count,
        "registros_silver": len(silver_records),
        "documentos_classificados": len(classified_documents),
    }

    logger.info("Resumo do processamento: %s", summary)
    return summary