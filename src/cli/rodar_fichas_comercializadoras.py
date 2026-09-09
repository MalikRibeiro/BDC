import argparse
import sys
from pathlib import Path

from pyautogui import click

from src.app.bootstrap import aplicativo_bootstrap
from app.comercializadoras.orquestrador_comercializadoras import processar_fichas_comercializadoras
from control.logger import obter_logger


def criar_analisador() -> argparse.ArgumentParser:
    """
    Constrói o parser de argumentos de linha de comando para o script de comercializadoras.
    """
    parser = argparse.ArgumentParser(
        description="Processamento e geração de fichas de comercializadoras."
    )
    parser.add_argument(
        "--configs-dir",
        type=str,
        default=None,
        help=(
            "Caminho para o diretório de configurações (opcional). "
            "Se omitido, busca a variável de ambiente 'BDC_CONFIGS_DIR' "
            "ou utiliza o caminho relativo da raiz do projeto ('ENTRADAS/configs')."
        ),
    )
    return parser


def main() -> None:
    parser = criar_analisador()
    args, _ = parser.parse_known_args()

    try:
        app_ctx = aplicativo_bootstrap(configs_dir=args.configs_dir)
        logger = obter_logger("bdc.cli", Path("LOGS/execucao") / "cli_comercializadoras.log")
        logger.info("Contexto da aplicacao inicializado a partir de: %s", app_ctx.path('configs'))
        
        processar_fichas_comercializadoras(app_ctx)

    except Exception as exc:
        if 'logger' in locals():
            logger.error("Falha na execucao: %s", exc)
        else:
            sys.stderr.write(f"[ERRO] Falha na execucao: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()