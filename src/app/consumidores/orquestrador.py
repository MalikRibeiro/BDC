"""Serviço principal refatorado do pipeline de fichas de consumidores."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.context import AppContext
from common.excel import fechar_pasta, abrir_pasta
from common.hashing import arquivo_hash
from common.json import ler_json
from control.logger import obter_logger
from silver.normalizadores import padronizar_cnpj
from common.paths import sanitizar_nome_da_pasta

from control.layout_catalog import carregar_layouts_consumidores
from control.carregador_de_mapeamento import mapeamento_de_carga_fichas_consumidores
from control.quality_loader import carregar_regras_de_qualidade_de_dados_consumidores
from domain.contrapartes.segmentacao import definir_segmento_metodologico
from domain.credito.pd_motor import calcular_pd_ajustada
from common.servico_desduplicacao import (
    tem_chave_de_negocio_duplicada,
    tem_hash_duplicado,
    virar_chave_de_negocio_no_historico,
)
from domain.fichas.validador import validar_registro_consumidor
from app.consumidores.classificacao import (
    classificar_consumidor,
    criar_classificacao_registro,
    VERSAO_REGRA_ATUAL,
)
from silver.documentos_classificados import criar_documento_classificado
from silver.normalizador_de_tipo_de_campo import normalizar_registro
from staging.descoberta import detectar_arquivos_excel_pendentes
from staging.staging_arquivo import copiar_para_staging
from storage.bronze_arquivo import publicar_arquivo_bruto
from storage.operacao_arquivo import mover_arquivo_com_tentativa_adicional
from storage.armazenamento_manifest import (
    anexar_registro_de_manifesto,
    historico_de_ingestao_de_carga,
)
from storage.escrever_dados import (
    mesclar_conjunto_de_dados_prata_por_chave_de_negocio,
    escrever_conjunto_de_dados_silver,
)
from storage.estado_armazenamento import DocumentManifest

def disco_cheio_erro(exc: Exception) -> bool:
    """Indica se a exceção representa falta de espaço em disco."""
    if not isinstance(exc, OSError):
        return False

    text = str(exc).lower()
    return (
        getattr(exc, "winerror", None) == 112
        or getattr(exc, "errno", None) == 28
        or "no space left on device" in text
        or "espaço insuficiente no disco" in text
    )


def criar_run_id(context: AppContext) -> str:
    """Monta o identificador textual da execução."""
    prefix = context.naming.get("run_id_prefix", "BDC")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"


def criar_alvo_nome(
    original_name: str,
    versao_ficha: str | None,
    cnpj: str | None,
    data_df: str | None,
    hash_value: str | None,
) -> str:
    source = Path(original_name)
    stem = source.stem[:40]

    parts: list[str] = [stem]

    if versao_ficha:
        parts.append(versao_ficha)

    if cnpj:
        safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit())
        parts.append(safe_cnpj)

    if data_df:
        safe_data_df = "".join(ch for ch in str(data_df) if ch.isdigit())
        parts.append(safe_data_df[:8])

    if hash_value:
        parts.append(hash_value[:8])

    return "__".join(parts) + source.suffix.lower()


def resolver_subpasta_bronze(
    cnpj: str | None,
    sigla: str | None,
) -> str:
    """Resolve a subpasta da bronze organizada por CNPJ e sigla."""
    if not cnpj:
        raise ValueError("Não é possível publicar em bronze sem CNPJ válido.")
    safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit())
    safe_sigla = sanitizar_nome_da_pasta(sigla or "")
    if safe_sigla:
        return f"{safe_cnpj}__{safe_sigla}"

    return safe_cnpj


def mover_para_rejeitados(
    source_file: Path,
    rejected_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
) -> None:
    """Move o arquivo para rejeitados e grava o manifest."""
    target = rejected_dir / source_file.name

    try:
        if source_file.exists():
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para rejeitados: {exc}")
        logger.exception("Falha ao mover %s para rejeitados.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
    except Exception as exc:
        logger.exception(
            "Falha ao gravar manifest de rejeição para %s.", source_file.name
        )
        raise


def mover_para_processados(
    source_file: Path,
    processed_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
) -> None:
    """Move o arquivo para processadas e grava o manifest."""
    target = processed_dir / source_file.name

    try:
        if source_file.exists():
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para processadas: {exc}")
        logger.exception("Falha ao mover %s para processadas.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
    except Exception as exc:
        logger.exception(
            "Falha ao gravar manifest de processamento para %s.", source_file.name
        )
        raise


def criar_info_pd(
    normalized: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    logger: Any,
    source_file: Path,
    manifest: DocumentManifest,
) -> dict[str, Any]:
    """Calcula a PD ajustada para o registro normalizado de consumidor."""
    segmento_pd: str | None = None

    try:
        registro_pd = dict(normalized)
        registro_pd["TIPO_FICHA"] = "CONSUMIDOR"

        segmento_pd = definir_segmento_metodologico(registro_pd)
        registro_pd["SEGMENTO_PD"] = segmento_pd

        pd_info = calcular_pd_ajustada(
            registro=registro_pd,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=None,
            score_cpura_config=None,
            logger=logger,
        )

        logger.info(
            "PD ajustada calculada para %s. Segmento=%s RATING_FINAL=%s PD_FINAL=%s",
            source_file.name,
            pd_info.get("SEGMENTO_PD"),
            pd_info.get("RATING_FINAL"),
            pd_info.get("PD_FINAL"),
        )
        return pd_info

    except Exception as exc:
        logger.warning(
            "PD ajustada não calculada para %s. Motivo: %s",
            source_file.name,
            exc,
        )
        manifest.avisos.append(f"PD ajustada não calculada: {exc}")

        return {
            "SEGMENTO_PD": segmento_pd,
            "PD_BASE": None,
            "RATING_FINAL": None,
            "PD_MIN_FAIXA": None,
            "PD_MAX_FAIXA": None,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": None,
            "PD_METODO": None,
            "PD_Q_NORMALIZADA": None,
            "PD_Q_CAP": None,
            "PD_Z_T": None,
            "PD_Z_ESCALADO": None,
            "PD_U_INTERPOLACAO": None,
        }


def criar_fila_processamento(
    context: AppContext,
) -> list[tuple[Path, str, Path, Path]]:
    """Monta a fila de processamento normal e reprocessamento."""
    normal_files = detectar_arquivos_excel_pendentes(
        context.path("input_fichas_consumidores_pendentes")
    )
    reprocess_files = detectar_arquivos_excel_pendentes(
        context.path("input_reprocessamento_consumidores_pendentes")
    )

    queue: list[tuple[Path, str, Path, Path]] = []

    for file_path in normal_files:
        queue.append(
            (
                file_path,
                "incremental",
                context.path("input_fichas_consumidores_processadas"),
                context.path("input_fichas_consumidores_rejeitadas"),
            )
        )

    for file_path in reprocess_files:
        queue.append(
            (
                file_path,
                "reprocess",
                context.path("input_reprocessamento_consumidores_processados"),
                context.path("input_reprocessamento_consumidores_rejeitados"),
            )
        )

    return queue


def processar_arquivo_individual(
    source_file: Path,
    load_mode: str,
    processed_dir: Path,
    rejected_dir: Path,
    context: AppContext,
    layouts: dict[str, Any],
    required_fields: Any,
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    quality_rules: dict[str, Any],
) -> Optional[dict[str, Any]]:
    """Processa isoladamente um único arquivo de ficha de consumidor."""
    workbook = None
    manifest = DocumentManifest(
        documento_id=str(uuid.uuid4()),
        run_id=run_id,
        ambiente=context.app_config["env"],
        tipo_ficha="consumidor",
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

        # 1. Duplicidade por Hash
        if load_mode == "incremental" and tem_hash_duplicado(
            history, manifest.hash_arquivo
        ):
            manifest.status_extracao = "ERRO_DUPLICIDADE_HASH"
            manifest.erros.append("Hash já processado anteriormente.")
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        # 2. Copia para Staging
        staging_dir = context.path("staging_fichas_consumidores")
        staging_name = criar_alvo_nome(
            original_name=source_file.name,
            versao_ficha=None,
            cnpj=None,
            data_df=None,
            hash_value=manifest.hash_arquivo,
        )
        staging_file = copiar_para_staging(source_file, staging_dir, staging_name)
        manifest.caminho_staging = str(staging_file)

        # 3 & 4. Extração Competitiva (Tournament Extraction)
        workbook = abrir_pasta(staging_file)
        from domain.fichas.extrator import extrair_registro_do_vencedor

        raw_record, metadata_list, winner_layout = extrair_registro_do_vencedor(workbook, layouts, quality_rules)

        if winner_layout == "DOC_001_ESTRUTURA_INCOMPATIVEL":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("DOC_001_ESTRUTURA_INCOMPATIVEL: Nenhuma aba compativel com o layout esperada foi encontrada.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        if not winner_layout or winner_layout == "NENHUM":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("Nenhum layout obteve score suficiente.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
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
        
        # Registrar linhagem se directory control existir (omitido para consumidor ou implementado se necessário)
        
        slug = "field_types_fichas_consumidores"
        normalized = normalizar_registro(raw_record, context, slug, logger)
        normalized.pop("DADOS_CADASTRAIS", None)
        
        # 4a. Normalização Semântica de Domínio (Negócio)
        from common.domain_normalizer import aplicar_normalizacao_de_dominio
        normalized = aplicar_normalizacao_de_dominio(normalized, context, logger)

        manifest.cnpj_extraido = normalized.get("CNPJ")
        manifest.data_demonstracao_financeira = normalized.get(
            "DATA_DEMONSTRACAO_FINANCEIRA"
        )
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        # 4b. Classificação Documental
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

        # Regra de Negócio: Consumidores < 5 MWm não possuem DF.
        if getattr(classificacao, "tipo_analise_exigida", "") == "simplificada":
            campos_df = [
                "ATIVO_CIRCULANTE", "ATIVO_TOTAL", "PASSIVO_CIRCULANTE", "PATRIMONIO_LIQUIDO",
                "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "ROA", "ROE", "FCO_ROL"
            ]
            for campo in campos_df:
                if campo not in normalized or normalized[campo] is None:
                    normalized[campo] = None

        # 5. Validações Técnicas e CNPJ (com regras condicionais por tipo de consumidor)
        req_fields_dict = quality_rules.get("required_fields_by_version", {})
        validate_fields = req_fields_dict.get(classification.versao_ficha, [])
        errors, warnings = validar_registro_consumidor(
            normalized,
            validate_fields,
            classificacao=classificacao,
            logger=logger,
            quality_rules=quality_rules,
        )
        
        integridade = normalized.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        if integridade >= 40.0:
            # Tolerância a missing se a integridade geral for satisfatória
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
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        if not manifest.cnpj_extraido:
            manifest.status_extracao = "ERRO_SEM_CNPJ"
            manifest.erros.append("Ficha sem CNPJ válido.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        if not padronizar_cnpj(manifest.cnpj_extraido):
            manifest.status_extracao = "ERRO_CNPJ_INVALIDO"
            manifest.erros.append(f"CNPJ inválido: {manifest.cnpj_extraido}")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO"
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        # 6. Checagem de Duplicidade de Negócio
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
                source_file, rejected_dir, manifest, ingestion_log_path, logger
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

        # 7. Cálculo das Regras de Negócio (PD)
        pd_info = criar_info_pd(
            normalized=normalized,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            logger=logger,
            source_file=source_file,
            manifest=manifest,
        )

        # 8. Movimentação para Bronze e Processadas
        bronze_root_dir = context.path("bronze_fichas_consumidores_raw")
        bronze_name = criar_alvo_nome(
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
            source_file, processed_dir, manifest, ingestion_log_path, logger
        )
        virar_chave_de_negocio_no_historico(history, manifest.to_dict())

        logger.info("Ficha processada com sucesso: %s.", source_file.name)

        # 9. Retorno dos Dados Estruturados
        classificacao_record = criar_classificacao_registro(classificacao)

        silver_record = {
            **normalized,
            **pd_info,
            **classificacao_record,
            "documento_id": manifest.documento_id,
            "run_id": run_id,
            "ambiente": manifest.ambiente,
            "tipo_ficha": manifest.tipo_ficha,
            "versao_ficha": manifest.versao_ficha,
            "arquivo_nome": manifest.arquivo_nome,
            "hash_arquivo": manifest.hash_arquivo,
            "load_mode": load_mode,
            "dt_processamento": datetime.now().isoformat(timespec="seconds"),
            "versao_regra_enquadramento": VERSAO_REGRA_ATUAL,
            "METADADOS_EXTRACAO": metadata_list,
        }

        classified_document = criar_documento_classificado(
            documento_id=manifest.documento_id,
            run_id=run_id,
            ambiente=manifest.ambiente,
            arquivo_nome=manifest.arquivo_nome or "",
            versao_ficha=manifest.versao_ficha or "",
            tipo_ficha=manifest.tipo_ficha,
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
                source_file, rejected_dir, manifest, ingestion_log_path, logger
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
        context.path("log_runner") / f"{run_id}__fichas_consumidores.log"
    )
    logger = obter_logger("bdc.consumidores", log_file)

    _ = mapeamento_de_carga_fichas_consumidores(context, logger)

    layouts = carregar_layouts_consumidores(context, logger)
    quality_rules = carregar_regras_de_qualidade_de_dados_consumidores(context, logger)

    required_fields = quality_rules.get("required_fields")

    ingestion_log_path = (
        context.path("bronze_ingestion_log")
        / "fichas_consumidores_ingestion.jsonl"
    )
    history = historico_de_ingestao_de_carga(ingestion_log_path)

    silver_records: list[dict[str, Any]] = []
    classified_documents: list[dict[str, Any]] = []

    queue = criar_fila_processamento(context)

    normal_count = sum(1 for _, mode, _, _ in queue if mode == "incremental")
    reprocess_count = sum(1 for _, mode, _, _ in queue if mode == "reprocess")

    logger.info(
        "Iniciando processamento de %s fichas (%s normais, %s reprocessamento).",
        len(queue),
        normal_count,
        reprocess_count,
    )

    try:
        pd_faixas = ler_json(context.control_file("pd_faixas"))
        logger.info("Faixas de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_faixas.")
        raise

    try:
        pd_transform_rules = ler_json(
            context.control_file("pd_transform_rules")
        )
        logger.info("Regras de transformação de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_transform_rules.")
        raise

    # Processa os arquivos da fila
    for source_file, load_mode, processed_dir, rejected_dir in queue:
        result = processar_arquivo_individual(
            source_file=source_file,
            load_mode=load_mode,
            processed_dir=processed_dir,
            rejected_dir=rejected_dir,
            context=context,
            layouts=layouts,
            required_fields=required_fields,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            history=history,
            ingestion_log_path=ingestion_log_path,
            logger=logger,
            run_id=run_id,
            quality_rules=quality_rules,
        )

        if result:
            silver_records.append(result["silver_record"])
            classified_documents.append(result["classified_document"])

    # Gravação na Camada Silver e Arquivo de Controle
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