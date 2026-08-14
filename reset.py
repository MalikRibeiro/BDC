"""Utilitário simples para reiniciar o pipeline BDC e reprocessar as fichas."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENTRADAS_DIR = ROOT / "ENTRADAS"
SAIDAS_DIR = ROOT / "SAIDAS"


def clear_directory_contents(dir_path: Path) -> int:
    """Apaga o conteúdo interno de um diretório sem remover a pasta raiz."""
    removed = 0
    if not dir_path.exists() or not dir_path.is_dir():
        return removed

    for item in sorted(dir_path.iterdir()):
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                removed += 1
            elif item.is_dir():
                shutil.rmtree(item)
                removed += 1
        except Exception as exc:
            print(f"⚠️ Falha ao limpar {item}: {exc}")
    return removed


def clear_jsonl_files(dir_path: Path) -> int:
    """Remove apenas arquivos .jsonl de um diretório."""
    removed = 0
    if not dir_path.exists() or not dir_path.is_dir():
        return removed

    for file_path in sorted(dir_path.glob("*.jsonl")):
        try:
            file_path.unlink()
            removed += 1
        except Exception as exc:
            print(f"⚠️ Falha ao apagar {file_path.name}: {exc}")
    return removed


def move_files_back_to_pending(category: str) -> int:
    """Move os arquivos de processadas/rejeitadas para pendentes."""
    base_path = ENTRADAS_DIR / "fichas" / category
    pendentes_dir = base_path / "pendentes"
    processadas_dir = base_path / "processadas"
    rejeitadas_dir = base_path / "rejeitadas"

    pendentes_dir.mkdir(parents=True, exist_ok=True)
    moved = 0

    for source_dir in (processadas_dir, rejeitadas_dir):
        if not source_dir.exists():
            continue

        for source_file in sorted(source_dir.rglob("*")):
            if not source_file.is_file():
                continue

            rel_path = source_file.relative_to(source_dir)
            destination = pendentes_dir / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)

            if destination.exists():
                destination.unlink()

            shutil.move(str(source_file), str(destination))
            moved += 1

    return moved


def main() -> None:
    print("🧹 Reiniciando o pipeline BDC...")

    targets = [
        SAIDAS_DIR / "staging" / "fichas_comercializadoras",
        SAIDAS_DIR / "staging" / "fichas_consumidores",
        SAIDAS_DIR / "bronze" / "fichas_comercializadoras_raw",
        SAIDAS_DIR / "bronze" / "fichas_consumidores_raw",
        SAIDAS_DIR / "bronze" / "snapshots_fontes",
        SAIDAS_DIR / "silver" / "fichas_comercializadoras_extraidas",
        SAIDAS_DIR / "silver" / "fichas_consumidores_extraidas",
        SAIDAS_DIR / "silver" / "documentos_classificados",
        SAIDAS_DIR / "silver" / "mtm_consolidado_silver",
        SAIDAS_DIR / "silver" / "denodo_contratos_silver",
        SAIDAS_DIR / "silver" / "denodo_contratos_padronizados", 
        SAIDAS_DIR / "silver" / "salesforce_silver",
        SAIDAS_DIR / "silver" / "receita_silver", 
        SAIDAS_DIR / "silver" / "garantias_silver", 
        SAIDAS_DIR / "silver" / "reconciliacao_contratos_mtm",
        SAIDAS_DIR / "silver" / "reconciliacao_fichas_salesforce",
        SAIDAS_DIR / "silver" / "alertas_credito",
        SAIDAS_DIR / "silver" / "governanca_carga_manual", 
        SAIDAS_DIR / "silver" / "governanca_overrides", 
        SAIDAS_DIR / "relational" / "facts",
        SAIDAS_DIR / "relational" / "dimensions", 
        SAIDAS_DIR / "relational" / "configs", 
        SAIDAS_DIR / "gold" / "relatorio_credito_atual", 
        SAIDAS_DIR / "output", 
    ]

    for path in targets:
        if path.exists():
            cleared = clear_directory_contents(path)
            print(f"   - Limpo: {path} ({cleared} itens removidos)")

    ingestion_log_dir = SAIDAS_DIR / "bronze" / "ingestion_log"
    jsonl_removed = clear_jsonl_files(ingestion_log_dir)
    print(f"   - Arquivos .jsonl removidos em {ingestion_log_dir}: {jsonl_removed}")

    moved_comercializadoras = move_files_back_to_pending("comercializadoras")
    moved_consumidores = move_files_back_to_pending("consumidores")

    print(f"   - Comercializadoras movidas para pendentes: {moved_comercializadoras}")
    print(f"   - Consumidores movidos para pendentes: {moved_consumidores}")
    print("✨ Reset concluído. Agora você pode executar novamente o main.py.")


if __name__ == "__main__":
    main()