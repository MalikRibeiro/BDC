"""Configuração padronizada de loggers do sistema BDC."""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

def obter_logger(name: str, file_path: str | Path | None = None) -> logging.Logger:
    """Cria ou devolve um logger com saída centralizada em arquivo e console."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    logger.propagate = False 

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Handler do Console (Apenas INFO, limpa a sujeira do terminal)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # 2. Handler de Arquivo Centralizado (Salva tudo, incluindo DEBUG)
    hoje = datetime.now().strftime("%Y-%m-%d")
    log_dir = Path("LOGS/execucoes")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Ignora o log_file legado passado pelo orquestrador e força o arquivo diário
    target = log_dir / f"{hoje}_execucao_comercializadoras.log"
    
    file_handler = logging.FileHandler(target, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger