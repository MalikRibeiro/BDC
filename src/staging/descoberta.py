"""Descoberta de arquivos pendentes para processamento."""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
import hashlib

@dataclass(frozen=True)
class ArquivoDescoberto:
    caminho_original: Path
    nome_arquivo: str
    extensao: str
    tamanho_bytes: int
    hash_sha256: str | None = None

def descobrir_arquivos_excel(input_dir: str | Path, calcular_hash: bool = False) -> list[ArquivoDescoberto]:
    """Lista arquivos Excel encapsulando os metadados de infraestrutura para evitar I/O repetitivo."""
    base_dir = Path(input_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    arquivos = []
    for file_path in base_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in {".xlsx", ".xlsm", ".xls"}:
            
            file_hash = None
            if calcular_hash:
                hasher = hashlib.sha256()
                with file_path.open("rb") as f:
                    for chunk in iter(lambda: f.read(1024 * 1024), b""):
                        hasher.update(chunk)
                file_hash = hasher.hexdigest()
                
            arquivos.append(ArquivoDescoberto(
                caminho_original=file_path,
                nome_arquivo=file_path.name,
                extensao=file_path.suffix.lower(),
                tamanho_bytes=file_path.stat().st_size,
                hash_sha256=file_hash
            ))
            
    return sorted(arquivos, key=lambda x: x.nome_arquivo)

def detectar_arquivos_excel_pendentes(input_dir: str | Path) -> list[Path]:
    """Adaptador legado: Lista arquivos Excel pendentes retornando lista de Paths."""
    descobertos = descobrir_arquivos_excel(input_dir, calcular_hash=False)
    return [arq.caminho_original for arq in descobertos]