"""Funções utilitárias compartilhadas entre os orquestradores do BDC."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.context import AppContext
from common.paths import sanitizar_nome_da_pasta
from storage.estado_armazenamento import DocumentManifest
from staging.descoberta import detectar_arquivos_excel_pendentes
from storage.operacao_arquivo import mover_arquivo_com_tentativa_adicional
from storage.armazenamento_manifest import anexar_registro_de_manifesto

try:
    from domain.auditoria.servico_auditoria import registrar_documento
except ImportError:
    registrar_documento = None

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
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Falha ao registrar JSON de rejeição para %s: %s", source_file.name, exc)


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

def criar_nome_arquivo_padronizado(
    original_name: str,
    versao_ficha: str | None,
    cnpj: str | None,
    data_df: str | None,
    hash_value: str | None,
) -> str:
    """Monta o nome técnico do arquivo processado (Substitui criar_nome_arquivo e criar_alvo_nome)."""
    source = Path(original_name)
    stem = source.stem[:40]

    parts: list[str] = [stem]

    if versao_ficha:
        parts.append(versao_ficha)

    if cnpj:
        safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
        if safe_cnpj:
            parts.append(safe_cnpj)

    if data_df:
        safe_data_df = "".join(ch for ch in str(data_df) if ch.isdigit())
        if safe_data_df:
            parts.append(safe_data_df[:8])

    if hash_value:
        parts.append(hash_value[:8])

    return "__".join(parts) + source.suffix.lower()


def resolver_subpasta_bronze(cnpj: str | None, sigla: str | None) -> str:
    """Resolve a subpasta da bronze organizada por CNPJ e sigla."""
    if not cnpj:
        raise ValueError("Não é possível publicar em bronze sem CNPJ válido.")
    safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
    safe_sigla = sanitizar_nome_da_pasta(sigla or "")
    if safe_sigla:
        return f"{safe_cnpj}__{safe_sigla}"

    return safe_cnpj or "SEM_CNPJ"

def criar_fila_processamento(
    context: AppContext,
    tipo_ficha: str
) -> list[tuple[Path, str, Path, Path]]:
    """Monta a fila de processamento de forma dinâmica baseada no tipo da ficha."""
    
    normal_files = detectar_arquivos_excel_pendentes(context.path(f"input_fichas_{tipo_ficha}_pendentes"))
    reprocess_files = detectar_arquivos_excel_pendentes(context.path(f"input_reprocessamento_{tipo_ficha}_pendentes"))

    queue: list[tuple[Path, str, Path, Path]] = []

    for file_path in normal_files:
        queue.append((
            file_path,
            "incremental",
            context.path(f"input_fichas_{tipo_ficha}_processadas"),
            context.path(f"input_fichas_{tipo_ficha}_rejeitadas"),
        ))

    for file_path in reprocess_files:
        queue.append((
            file_path,
            "reprocess",
            context.path(f"input_reprocessamento_{tipo_ficha}_processadas"),
            context.path(f"input_reprocessamento_{tipo_ficha}_rejeitadas"),
        ))

    return queue


def mover_para_rejeitados(
    source_file: Path,
    rejected_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
    control_dir: Path | None = None,
) -> None:
    """Move o arquivo para rejeitados, gera log estruturado e grava manifest."""
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
        if control_dir and registrar_documento:
            registrar_documento(
                manifest.documento_id, manifest.run_id, manifest.arquivo_nome,
                manifest.hash_arquivo, manifest.tipo_ficha, manifest.status_classificacao or "N/A",
                manifest.status_extracao or "N/A", control_dir
            )
    except Exception:
        logger.exception("Falha ao gravar manifest de rejeição para %s.", source_file.name)
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
        if control_dir and registrar_documento:
            registrar_documento(
                manifest.documento_id, manifest.run_id, manifest.arquivo_nome,
                manifest.hash_arquivo, manifest.tipo_ficha, manifest.status_classificacao or "N/A",
                manifest.status_extracao or "N/A", control_dir
            )
    except Exception:
        logger.exception("Falha ao gravar manifest de processamento para %s.", source_file.name)
        raise