"""Serviço principal refatorado do pipeline de fichas de comercializadoras."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.context import AppContext
from common.excel import close_workbook_safely, open_workbook
from common.hashing import hash_file
from common.io_json import read_json
from common.logging_utils import get_logger
from common.paths import sanitize_folder_name
from common.strings import normalize_cnpj
from control.layout_catalog import load_layouts_comercializadoras
from control.mapping_loader import load_mapping_fichas_comercializadoras
from control.quality_loader import load_data_quality_rules_comercializadoras
from domain.contrapartes.segmentacao import definir_segmento_metodologico
from domain.credito.pd_engine import calcular_pd_ajustada
from services.audit_service import registrar_documento, registrar_linhagem_campos
from services.dedup_service import (
    has_duplicate_business_key,
    has_duplicate_hash,
    upsert_business_key_in_history,
)
from services.ficha_classifier import classify_workbook
from services.ficha_extractor import extract_record
from services.ficha_validator import validate_record
from silver.documentos_classificados import build_classified_document
from silver.field_type_normalizer import normalize_record
from staging.discovery import discover_pending_excels
from staging.staging_writer import copy_to_staging
from storage.bronze_store import publish_raw_file
from storage.file_ops import move_file_with_retry
from storage.manifest_store import (
    append_manifest_record,
    load_ingestion_history,
)
from storage.silver_store import (
    merge_silver_dataset_by_business_key,
    write_silver_dataset,
)
from storage.state_store import DocumentManifest


def is_valid_cnpj(digits: str | None) -> bool:
    """Valida se o valor é um CNPJ válido."""
    if digits is None:
        return False

    if digits == digits[0] * 14:
        return False

    def calc_digit(base: str, weights: list[int]) -> str:
        total = sum(int(num) * weight for num, weight in zip(base, weights))
        remainder = total % 11
        return "0" if remainder < 2 else str(11 - remainder)

    first_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    second_weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    first_digit = calc_digit(digits[:12], first_weights)
    second_digit = calc_digit(digits[:12] + first_digit, second_weights)

    return digits[-2:] == first_digit + second_digit


def _is_disk_full_error(exc: Exception) -> bool:
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


def _build_run_id(context: AppContext) -> str:
    """Monta o identificador textual da execução."""
    prefix = context.naming.get("run_id_prefix", "BDC")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"


def _build_target_name(
    original_name: str,
    versao_ficha: str | None,
    cnpj: str | None,
    data_df: str | None,
    hash_value: str | None,
) -> str:
    """Monta o nome técnico do arquivo processado."""
    source = Path(original_name)
    stem = source.stem[:40]

    parts: list[str] = [stem]

    if versao_ficha:
        parts.append(versao_ficha)

    if cnpj:
        safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
        parts.append(safe_cnpj)

    if data_df:
        safe_data_df = "".join(ch for ch in str(data_df) if ch.isdigit())
        parts.append(safe_data_df[:8])

    if hash_value:
        parts.append(hash_value[:8])

    return "__".join(parts) + source.suffix.lower()


def _resolve_bronze_subfolder(
    cnpj: str | None,
    sigla: str | None,
) -> str:
    """Resolve a subpasta da bronze organizada por CNPJ e sigla."""
    if not cnpj:
        raise ValueError("Não é possível publicar em bronze sem CNPJ válido.")
    safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
    safe_sigla = sanitize_folder_name(sigla or "")
    if safe_sigla:
        return f"{safe_cnpj}__{safe_sigla}"

    return safe_cnpj


def _move_to_rejected(
    source_file: Path,
    rejected_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
    control_dir: Path | None = None,
) -> None:
    """Move o arquivo para rejeitados e grava o manifest."""
    target = rejected_dir / source_file.name

    try:
        if source_file.exists():
            move_file_with_retry(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para rejeitados: {exc}")
        logger.exception("Falha ao mover %s para rejeitados.", source_file.name)

    try:
        append_manifest_record(str(ingestion_log_path), manifest.to_dict())
        if control_dir:
            registrar_documento(
                manifest.documento_id,
                manifest.run_id,
                manifest.arquivo_nome,
                manifest.hash_arquivo,
                manifest.tipo_ficha,
                manifest.status_classificacao or "N/A",
                manifest.status_extracao or "N/A",
                control_dir
            )
    except Exception as exc:
        logger.exception(
            "Falha ao gravar manifest de rejeição para %s.", source_file.name
        )
        raise


def _move_to_processed(
    source_file: Path,
    processed_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
    control_dir: Path | None = None,
) -> None:
    """Move o arquivo para processadas e grava o manifest."""
    target = processed_dir / source_file.name

    try:
        if source_file.exists():
            move_file_with_retry(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para processadas: {exc}")
        logger.exception("Falha ao mover %s para processadas.", source_file.name)

    try:
        append_manifest_record(str(ingestion_log_path), manifest.to_dict())
        if control_dir:
            registrar_documento(
                manifest.documento_id,
                manifest.run_id,
                manifest.arquivo_nome,
                manifest.hash_arquivo,
                manifest.tipo_ficha,
                manifest.status_classificacao or "N/A",
                manifest.status_extracao or "N/A",
                control_dir
            )
    except Exception as exc:
        logger.exception(
            "Falha ao gravar manifest de processamento para %s.", source_file.name
        )
        raise


def _build_pd_info(
    normalized: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    pd_cpura_config: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any,
    source_file: Path,
    manifest: DocumentManifest,
    peer_group: list[float] | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada para o registro normalizado de comercializadora."""
    segmento_pd: str | None = None

    try:
        registro_pd = dict(normalized)
        registro_pd["TIPO_FICHA"] = "COMERCIALIZADORA"

        segmento_pd = definir_segmento_metodologico(registro_pd)
        registro_pd["SEGMENTO_PD"] = segmento_pd

        pd_info = calcular_pd_ajustada(
            registro=registro_pd,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=pd_cpura_config,
            score_cpura_config=score_cpura_config,
            peer_group=peer_group,
            logger=logger,
        )

        logger.info(
            "PD ajustada calculada para %s. "
            "Segmento=%s SCORE_TOTAL=%s RATING_FINAL=%s PD_FINAL=%s",
            source_file.name,
            pd_info.get("SEGMENTO_PD"),
            pd_info.get("SCORE_TOTAL"),
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
            "NOTA_AUDITORIA": None,
            "PESO_BOARD": None,
            "PESO_AUDITORIA": None,
            "PESO_BUREAU": None,
            "SCORE_QUALITATIVO": None,
            "PESO_PD": None,
            "PESO_FCO_ROL": None,
            "PESO_ROE": None,
            "PESO_ROA": None,
            "SCORE_QUANTITATIVO": None,
            "SCORE_TOTAL": None,
            "SCORE_MIN_RATING": None,
            "SCORE_MAX_RATING": None,
            "SCORE_TRUNCADO": None,
            "PD_BASE": None,
            "RATING_FINAL": None,
            "FONTE_RATING": None,
            "PD_MIN_FAIXA": None,
            "PD_MAX_FAIXA": None,
            "PERCENTIL_PD_BASE": None,
            "PD_BRUTA": None,
            "PD_ESTABILIZADA": None,
            "PD_FINAL": None,
            "PD_METODO": None,
            "LOGIT_TRUNCADO": None,
        }


def _build_processing_queue(
    context: AppContext,
) -> list[tuple[Path, str, Path, Path]]:
    """Monta a fila de processamento normal e reprocessamento."""
    normal_files = discover_pending_excels(
        context.path("input_fichas_comercializadoras_pendentes")
    )
    reprocess_files = discover_pending_excels(
        context.path("input_reprocessamento_comercializadoras_pendentes")
    )

    queue: list[tuple[Path, str, Path, Path]] = []

    for file_path in normal_files:
        queue.append(
            (
                file_path,
                "incremental",
                context.path("input_fichas_comercializadoras_processadas"),
                context.path("input_fichas_comercializadoras_rejeitadas"),
            )
        )

    for file_path in reprocess_files:
        queue.append(
            (
                file_path,
                "reprocess",
                context.path("input_reprocessamento_comercializadoras_processados"),
                context.path("input_reprocessamento_comercializadoras_rejeitados"),
            )
        )

    return queue


def _process_single_file(
    source_file: Path,
    load_mode: str,
    processed_dir: Path,
    rejected_dir: Path,
    context: AppContext,
    layouts: dict[str, Any],
    required_fields: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_cpura_config: dict[str, Any],
    score_cpura_config: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    quality_rules: dict[str, Any],
    control_dir: Path | None = None,
) -> Optional[dict[str, Any]]:
    """Processa de ponta a ponta um único arquivo de ficha de comercializadora."""
    workbook = None
    manifest = DocumentManifest(
        documento_id=str(uuid.uuid4()),
        run_id=run_id,
        ambiente=context.app_config["env"],
        tipo_ficha="comercializadora",
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

        manifest.hash_arquivo = hash_file(source_file)

        # 1. Checagem de Hash em Carga Incremental
        if load_mode == "incremental" and has_duplicate_hash(
            history, manifest.hash_arquivo
        ):
            manifest.status_extracao = "ERRO_DUPLICIDADE_HASH"
            manifest.erros.append("Hash já processado anteriormente.")
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        # 2. Copia para Staging
        staging_dir = context.path("staging_fichas_comercializadoras")
        staging_name = _build_target_name(
            original_name=source_file.name,
            versao_ficha=None,
            cnpj=None,
            data_df=None,
            hash_value=manifest.hash_arquivo,
        )
        staging_file = copy_to_staging(source_file, staging_dir, staging_name)
        manifest.caminho_staging = str(staging_file)

        # 3. Abertura e Classificação do Layout
        workbook = open_workbook(staging_file)
        classification = classify_workbook(workbook, layouts, logger)

        if classification is None:
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("Layout não identificado.")
            close_workbook_safely(workbook)
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        manifest.versao_ficha = classification.versao_ficha
        manifest.status_classificacao = "CLASSIFICADO"

        logger.info(
            "Layout %s identificado para %s.",
            classification.versao_ficha,
            source_file.name,
        )

        # 4. Extração e Normalização
        layout = layouts[classification.versao_ficha]
        raw_record, metadata_list = extract_record(workbook, layout)
        
        if control_dir and metadata_list:
            registrar_linhagem_campos(
                manifest.documento_id,
                manifest.run_id,
                metadata_list,
                control_dir
            )
            
        slug = "field_types_fichas_comercializadoras"
        normalized = normalize_record(raw_record, context, slug, logger)

        manifest.cnpj_extraido = normalize_cnpj(normalized.get("CNPJ"))
        normalized["CNPJ"] = manifest.cnpj_extraido

        manifest.data_demonstracao_financeira = normalized.get(
            "DATA_DEMONSTRACAO_FINANCEIRA"
        )
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        # 5. Validação Técnica e CNPJ
        validate_fields = required_fields[classification.versao_ficha]
        errors, warnings = validate_record(
            normalized, validate_fields, logger=logger, quality_rules=quality_rules
        )
        manifest.erros.extend(errors)
        manifest.avisos.extend(warnings)

        if not manifest.cnpj_extraido:
            manifest.status_extracao = "ERRO_SEM_CNPJ"
            manifest.erros.append("Ficha sem CNPJ válido.")
            close_workbook_safely(workbook)
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if not is_valid_cnpj(manifest.cnpj_extraido):
            manifest.status_extracao = "ERRO_CNPJ_INVALIDO"
            manifest.erros.append(f"CNPJ inválido: {manifest.cnpj_extraido}")
            close_workbook_safely(workbook)
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO"
            close_workbook_safely(workbook)
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        # 6. Checagem de Duplicidade de Negócio e Versionamento
        duplicate_business = has_duplicate_business_key(
            history,
            manifest.cnpj_extraido,
            manifest.data_demonstracao_financeira,
        )

        # C0.1 - CORREÇÃO: Se o hash é novo (passou na etapa 1), mas a chave de negócio existe,
        # trata-se de uma nova versão factual da ficha. O sistema não rejeita, ele versiona.
        if duplicate_business:
            manifest.reprocessed = True
            manifest.previous_record_found = True
            logger.info("Nova versão identificada para CNPJ %s e DF %s. O registro será versionado na Silver.", manifest.cnpj_extraido, manifest.data_demonstracao_financeira)
        else:
            manifest.reprocessed = False
            manifest.previous_record_found = False

        close_workbook_safely(workbook)
        workbook = None

        # 7. Regras de Negócio de Crédito (PD / Scoring)
        pd_info = _build_pd_info(
            normalized=normalized,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=pd_cpura_config,
            score_cpura_config=score_cpura_config,
            logger=logger,
            source_file=source_file,
            manifest=manifest,
            peer_group=None,
        )

        # 8. Verificação de Caminhos e Publicação Bronze
        bronze_root_dir = context.path("bronze_fichas_comercializadoras_raw")
        bronze_name = _build_target_name(
            original_name=source_file.name,
            versao_ficha=manifest.versao_ficha,
            cnpj=manifest.cnpj_extraido,
            data_df=manifest.data_demonstracao_financeira,
            hash_value=manifest.hash_arquivo,
        )

        bronze_subfolder = _resolve_bronze_subfolder(
            manifest.cnpj_extraido,
            normalized.get("SIGLA"),
        )
        bronze_staging_target = staging_dir / bronze_name

        logger.info("Fonte bronze_staging: %s", staging_file)
        logger.info("Destino bronze_staging: %s", bronze_staging_target)
        logger.info(
            "Tamanho do caminho destino: %s", len(str(bronze_staging_target))
        )

        target_path = staging_dir / bronze_name
        if len(str(target_path)) > 240:
            raise ValueError(f"Caminho de destino muito longo: {target_path}")

        bronze_staging = copy_to_staging(staging_file, staging_dir, bronze_name)
        bronze_file = publish_raw_file(
            source_file=bronze_staging,
            bronze_root_dir=bronze_root_dir / bronze_subfolder,
        )
        manifest.caminho_bronze = str(bronze_file)
        manifest.status_extracao = "SUCESSO"

        _move_to_processed(
            source_file, processed_dir, manifest, ingestion_log_path, logger, control_dir
        )
        upsert_business_key_in_history(history, manifest.to_dict())

        logger.info("Ficha processada com sucesso: %s.", source_file.name)

        # 9. Retorno Estruturado
        silver_record = {
            **normalized,
            **pd_info,
            "documento_id": manifest.documento_id,
            "run_id": run_id,
            "ambiente": manifest.ambiente,
            "tipo_ficha": manifest.tipo_ficha,
            "versao_ficha": manifest.versao_ficha,
            "arquivo_nome": manifest.arquivo_nome,
            "hash_arquivo": manifest.hash_arquivo,
            "load_mode": load_mode,
            "dt_processamento": datetime.now().isoformat(timespec="seconds"),
        }

        classified_document = build_classified_document(
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
            close_workbook_safely(workbook)
        manifest.status_extracao = "ERRO_PROCESSAMENTO"
        manifest.erros.append(str(exc))

        if _is_disk_full_error(exc):
            logger.exception(
                "Execução interrompida por falta de espaço em disco ao processar %s.",
                source_file.name,
            )
            raise

        try:
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
        except Exception as move_exc:
            if _is_disk_full_error(move_exc):
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


def process_fichas_comercializadoras(
    context: AppContext,
) -> dict[str, Any]:
    """Executa o pipeline completo das fichas de comercializadoras."""
    run_id = _build_run_id(context)

    log_file = (
        context.path("log_runner") / f"{run_id}__fichas_comercializadoras.log"
    )
    logger = get_logger("bdc.comercializadoras", log_file)

    _ = load_mapping_fichas_comercializadoras(context, logger)

    layouts = load_layouts_comercializadoras(context, logger)
    quality_rules = load_data_quality_rules_comercializadoras(context, logger)

    try:
        pd_faixas = read_json(context.control_file("pd_faixas"))
        logger.info("Faixas de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_faixas.")
        raise

    try:
        pd_cpura_config = read_json(context.control_file("pd_cpura_config"))
        logger.info("Configuração de CPURA carregada com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_cpura_config.")
        raise

    try:
        score_cpura_config = read_json(
            context.control_file("score_cpura_config")
        )
        logger.info("Configuração de score de CPURA carregada com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar score_cpura_config.")
        raise

    try:
        pd_transform_rules = read_json(
            context.control_file("pd_transform_rules")
        )
        logger.info("Regras de transformação de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_transform_rules.")
        raise

    required_fields = quality_rules.get("required_fields_by_version")

    ingestion_log_path = (
        context.path("bronze_ingestion_log")
        / "fichas_comercializadoras_ingestion.jsonl"
    )
    history = load_ingestion_history(ingestion_log_path)

    silver_records: list[dict[str, Any]] = []
    classified_documents: list[dict[str, Any]] = []

    queue = _build_processing_queue(context)

    normal_count = sum(1 for _, mode, _, _ in queue if mode == "incremental")
    reprocess_count = sum(1 for _, mode, _, _ in queue if mode == "reprocess")

    logger.info(
        "Iniciando processamento de %s fichas (%s normais, %s reprocessamento).",
        len(queue),
        normal_count,
        reprocess_count,
    )

    # Processa cada item da fila isoladamente
    for source_file, load_mode, processed_dir, rejected_dir in queue:
        result = _process_single_file(
            source_file=source_file,
            load_mode=load_mode,
            processed_dir=processed_dir,
            rejected_dir=rejected_dir,
            context=context,
            layouts=layouts,
            required_fields=required_fields,
            pd_faixas=pd_faixas,
            pd_cpura_config=pd_cpura_config,
            score_cpura_config=score_cpura_config,
            pd_transform_rules=pd_transform_rules,
            history=history,
            ingestion_log_path=ingestion_log_path,
            logger=logger,
            run_id=run_id,
            quality_rules=quality_rules,
            control_dir=context.path("relational_control") if hasattr(context, "path") and context.path("relational_control") else Path("SAIDAS/relational/control"),
        )

        if result:
            silver_records.append(result["silver_record"])
            classified_documents.append(result["classified_document"])

    silver_output_dir = context.path("silver_fichas_comercializadoras_extraidas")
    docs_output_dir = context.path("silver_documentos_classificados")

    if silver_records:
        merge_silver_dataset_by_business_key(
            records=silver_records,
            output_dir=silver_output_dir,
            filename="fichas_comercializadoras_extraidas.csv",
            business_keys=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA"],
        )

    if classified_documents:
        write_silver_dataset(
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