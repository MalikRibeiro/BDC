"""Serviço principal refatorado do pipeline de fichas de comercializadoras."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json

from app.context import AppContext
from common.excel import  abrir_pasta, fechar_pasta
from common.hashing import arquivo_hash
from common.json import ler_json
from control.logger import obter_logger
from silver.normalizadores import padronizar_cnpj
from common.paths import sanitizar_nome_da_pasta

from control.layout_catalog import carregar_layouts_comercializadoras
from control.carregador_de_mapeamento import mapeamento_de_carga_fichas_comercializadoras
from domain.contrapartes.segmentacao import definir_segmento_metodologico
from domain.credito.pd_motor import calcular_pd_ajustada
from domain.auditoria.servico_auditoria import registrar_documento, registrar_linhagem_campos
from common.servico_desduplicacao import (
    tem_chave_de_negocio_duplicada,
    tem_hash_duplicado,
    virar_chave_de_negocio_no_historico,
)
from domain.fichas.validador import validar_registro
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

def registrar_rejeicao_json(manifest: DocumentManifest, source_file: Path) -> None:
    """Grava metadados de rejeição de forma estruturada para reprocessamento."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    dir_rejeitados = Path("LOGS/rejeitados")
    dir_rejeitados.mkdir(parents=True, exist_ok=True)
    arquivo_json = dir_rejeitados / f"{hoje}_rejeicoes.json"
    
    registro = {
        "timestamp": datetime.now().isoformat(),
        "arquivo": str(source_file.name),
        "status": getattr(manifest, "status_extracao", "ERRO_DESCONHECIDO"),
        "erros": getattr(manifest, "erros", [])
    }
    try:
        dados = json.loads(arquivo_json.read_text(encoding="utf-8")) if arquivo_json.exists() else []
        dados.append(registro)
        arquivo_json.write_text(json.dumps(dados, indent=4, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass # Ignora falha de IO para não derrubar o motor principal

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


def criar_nome_arquivo(
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


def resolver_subpasta_bronze(
    cnpj: str | None,
    sigla: str | None,
) -> str:
    """Resolve a subpasta da bronze organizada por CNPJ e sigla."""
    if not cnpj:
        raise ValueError("Não é possível publicar em bronze sem CNPJ válido.")
    safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
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
    control_dir: Path | None = None,
) -> None:
    """Move o arquivo para rejeitados e grava o manifest."""
    target = rejected_dir / source_file.name
    
    registrar_rejeicao_json(manifest, source_file)

    try:
        if source_file.exists():
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para rejeitados: {exc}")
        logger.exception("Falha ao mover %s para rejeitados.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
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


def mover_para_processados(
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
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para processadas: {exc}")
        logger.exception("Falha ao mover %s para processadas.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
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


def criar_info_pd(
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
        
    except Exception as exc:
        logger.error("Falha bloqueante no motor de crédito para %s. Motivo: %s", source_file.name, exc)
        manifest.avisos.append(f"PD ajustada não calculada: {exc}")
        raise ValueError(f"Insumo obrigatório ausente ou falha no motor: {exc}")


def criar_fila_processamento(
    context: AppContext,
) -> list[tuple[Path, str, Path, Path]]:
    """Monta a fila de processamento normal e reprocessamento."""
    normal_files = detectar_arquivos_excel_pendentes(
        context.path("input_fichas_comercializadoras_pendentes")
    )
    reprocess_files = detectar_arquivos_excel_pendentes(
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


def processar_arquivo_individual(
    source_file: Path,
    load_mode: str,
    processed_dir: Path,
    rejected_dir: Path,
    context: AppContext,
    layouts: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_cpura_config: dict[str, Any],
    score_cpura_config: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    master_catalog: dict[str, Any],
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

        manifest.hash_arquivo = arquivo_hash(source_file)

        # 1. Checagem de Hash em Carga Incremental
        if load_mode == "incremental" and tem_hash_duplicado(
            history, manifest.hash_arquivo
        ):
            manifest.status_extracao = "ERRO_DUPLICIDADE_HASH"
            manifest.erros.append("Hash já processado anteriormente.")
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        # 2. Copia para Staging
        staging_dir = context.path("staging_fichas_comercializadoras")
        staging_name = criar_nome_arquivo(
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
        raw_record, metadata_list, winner_layout = extrair_registro_do_vencedor(workbook, layouts, master_catalog)
        
        if winner_layout == "DOC_001_ESTRUTURA_INCOMPATIVEL":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("DOC_001_ESTRUTURA_INCOMPATIVEL: Nenhuma aba compativel com o layout esperada foi encontrada.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None
            
        score_campeao = raw_record.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        
        # Validar aprovação (GATES e Score Ponderado)
        if raw_record.get("_FALHA_GATE_CRITICO"):
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_DADOS_CRITICOS_AUSENTES"
            manifest.erros.append("Ficha falhou nos GATES de segurança (Campos obrigatórios ausentes).")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None
            
        if not winner_layout or winner_layout == "NENHUM" or score_campeao < 40.0:
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_INTEGRIDADE"
            manifest.erros.append(f"Score insuficiente: {score_campeao}%. Minimo exigido: 40.0%.")
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
            registrar_linhagem_campos(
                manifest.documento_id,
                manifest.run_id,
                metadata_list,
                control_dir
            )
            
        slug = "master_catalog_comercializadoras"
        normalized = normalizar_registro(raw_record, context, slug, logger)
        
        # 4b. Normalização Semântica de Domínio (Negócio)
        from common.domain_normalizer import aplicar_normalizacao_de_dominio
        normalized = aplicar_normalizacao_de_dominio(normalized, context, logger)
        
        # 4c. Derivação Financeira (Calcula DERIVED fields caso não existam)
        from domain.fichas.derivador_financeiro import calcular_indicadores_derivados
        normalized = calcular_indicadores_derivados(normalized)

        manifest.cnpj_extraido = normalized.get("CNPJ")

        manifest.data_demonstracao_financeira = normalized.get(
            "DATA_DEMONSTRACAO_FINANCEIRA"
        )
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        # 5. Validação Técnica (GATES e Sanity Checks)
        errors, warnings = validar_registro(
            record=normalized,
            master_catalog=master_catalog,
            logger=logger
        )
        
        integridade = normalized.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        
        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO_GATES"
        
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

        # CORREÇÃO DA AVALIAÇÃO DA TUPLA DO CNPJ:
        if not manifest.cnpj_extraido:
            manifest.status_extracao = "ERRO_SEM_CNPJ"
            manifest.erros.append("Ficha sem CNPJ válido na extração.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        c_14, c_raiz, c_status = padronizar_cnpj(manifest.cnpj_extraido)
        if c_14 is None or c_status != "CNPJ_VALIDO":
            manifest.status_extracao = "ERRO_CNPJ_INVALIDO"
            manifest.erros.append(f"CNPJ inválido detectado na validação: {manifest.cnpj_extraido}")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None
        
        # Garante que o CNPJ validado flua para o manifesto e registro
        manifest.cnpj_extraido = c_14
        normalized["CNPJ"] = c_14
        normalized["CNPJ_RAIZ"] = c_raiz

        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO_GATES"
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        # 6. Checagem de Duplicidade de Negócio e Versionamento
        duplicate_business = tem_chave_de_negocio_duplicada(
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

        fechar_pasta(workbook)
        workbook = None

        # 7. Regras de Negócio de Crédito (PD / Scoring)
        try:
            pd_info = criar_info_pd(
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
        except ValueError as pd_error:
            manifest.status_extracao = "ERRO_MOTOR_CREDITO"
            manifest.erros.append(str(pd_error))
            fechar_pasta(workbook)
            mover_para_rejeitados(source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir)
            return None

        # 8. Verificação de Caminhos e Publicação Bronze
        bronze_root_dir = context.path("bronze_fichas_comercializadoras_raw")
        bronze_name = criar_nome_arquivo(
            original_name=source_file.name,
            versao_ficha=manifest.versao_ficha,
            cnpj=manifest.cnpj_extraido,
            data_df=manifest.data_demonstracao_financeira,
            hash_value=manifest.hash_arquivo,
        )

        bronze_subfolder = resolver_subpasta_bronze(
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

        bronze_staging = copiar_para_staging(staging_file, staging_dir, bronze_name)
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


def processar_fichas_comercializadoras(
    context: AppContext,
) -> dict[str, Any]:
    """Executa o pipeline completo das fichas de comercializadoras."""
    run_id = criar_run_id(context)

    log_file = (
        context.path("log_runner") / f"{run_id}__fichas_comercializadoras.log"
    )
    logger = obter_logger("bdc.comercializadoras", log_file)

    _ = mapeamento_de_carga_fichas_comercializadoras(context, logger)

    layouts = carregar_layouts_comercializadoras(context, logger)
    
    catalog_path = context.path("control_quality") / "master_catalog_comercializadoras.json"
    logger.info("Carregando Master Catalog definitivo: %s", catalog_path)
    master_catalog = ler_json(catalog_path)

    try:
        pd_faixas = ler_json(context.control_file("pd_faixas"))
        logger.info("Faixas de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_faixas.")
        raise

    try:
        pd_cpura_config = ler_json(context.control_file("pd_cpura_config"))
        logger.info("Configuração de CPURA carregada com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_cpura_config.")
        raise

    try:
        score_cpura_config = ler_json(
            context.control_file("score_cpura_config")
        )
        logger.info("Configuração de score de CPURA carregada com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar score_cpura_config.")
        raise

    try:
        pd_transform_rules = ler_json(
            context.control_file("pd_transform_rules")
        )
        logger.info("Regras de transformação de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_transform_rules.")
        raise

    ingestion_log_path = (
        context.path("bronze_ingestion_log")
        / "fichas_comercializadoras_ingestion.jsonl"
    )
    history = historico_de_ingestao_de_carga(ingestion_log_path)

    silver_records: list[dict[str, Any]] = []
    classified_documents: list[dict[str, Any]] = []

    queue = criar_fila_processamento(context)

    normal_count = sum(1 for _, mode, _, _ in queue if mode == "incremental")
    reprocess_count = sum(1 for _, mode, _, _ in queue if mode == "reprocess")

    logger.info("Descoberta: Total de arquivos identificados na Staging: %s", len(queue))
    logger.info("Iniciando processamento: %s fichas incrementais e %s reprocessamentos.", normal_count, reprocess_count)

    # Processa cada item da fila isoladamente
    for source_file, load_mode, processed_dir, rejected_dir in queue:
        result = processar_arquivo_individual(
            source_file=source_file,
            load_mode=load_mode,
            processed_dir=processed_dir,
            rejected_dir=rejected_dir,
            context=context,
            layouts=layouts,
            pd_faixas=pd_faixas,
            pd_cpura_config=pd_cpura_config,
            score_cpura_config=score_cpura_config,
            pd_transform_rules=pd_transform_rules,
            history=history,
            ingestion_log_path=ingestion_log_path,
            logger=logger,
            run_id=run_id,
            master_catalog=master_catalog,
            control_dir=context.path("relational_control") if hasattr(context, "path") and context.path("relational_control") else Path("SAIDAS/relational/control"),
        )

        if result:
            silver_records.append(result["silver_record"])
            classified_documents.append(result["classified_document"])

    silver_output_dir = context.path("silver_fichas_comercializadoras_extraidas")
    docs_output_dir = context.path("silver_documentos_classificados")

    if silver_records:
        mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
            records=silver_records,
            output_dir=silver_output_dir,
            filename="fichas_comercializadoras_extraidas.csv",
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