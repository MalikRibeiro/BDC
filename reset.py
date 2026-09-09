from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENTRADAS_DIR = ROOT / "ENTRADAS"
SAIDAS_DIR = ROOT / "SAIDAS"
LOGS_DIR = ROOT / "LOGS"


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

def move_generic_back_to_pending(base_path: Path) -> int:
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
    print("Reiniciando o pipeline BDC...")

    targets = [
        SAIDAS_DIR / "staging",
        SAIDAS_DIR / "bronze" / "fichas_comercializadoras_raw",
        SAIDAS_DIR / "bronze" / "fichas_consumidores_raw",
        SAIDAS_DIR / "bronze" / "snapshots_fontes",
        SAIDAS_DIR / "silver",
        SAIDAS_DIR / "relational",
        SAIDAS_DIR / "gold",
        SAIDAS_DIR / "output",
        LOGS_DIR
    ]

    for path in targets:
        if path.exists():
            cleared = clear_directory_contents(path)
            print(f"Limpo: {path} ({cleared} itens removidos)")

    ingestion_log_dir = SAIDAS_DIR / "bronze" / "ingestion_log"
    jsonl_removed = clear_jsonl_files(ingestion_log_dir)
    print(f"Arquivos .jsonl removidos em {ingestion_log_dir}: {jsonl_removed}")

    moved_comercializadoras = move_files_back_to_pending("comercializadoras")
    moved_consumidores = move_files_back_to_pending("consumidores")
    moved_overrides = move_generic_back_to_pending(ENTRADAS_DIR / "overrides")
    moved_manual = move_generic_back_to_pending(ENTRADAS_DIR / "atualizacoes_manuais")

    print(f"Comercializadoras movidas para pendentes: {moved_comercializadoras}")
    print(f"Consumidores movidos para pendentes: {moved_consumidores}")
    print(f"Overrides movidos para pendentes: {moved_overrides}")
    print(f"Carga Manual movidas para pendentes: {moved_manual}")
    print("Reset concluído. Agora você pode executar novamente o main.py.")


if __name__ == "__main__":
    main()