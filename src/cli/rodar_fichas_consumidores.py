import argparse
import sys
from pathlib import Path

from src.app.bootstrap import aplicativo_bootstrap
from app.consumidores.orquestrador_consumidores import processar_fichas_consumidores
from control.logger import obter_logger


def criar_analisador() -> argparse.ArgumentParser:
    """
    Constrói o parser de argumentos de linha de comando para o script de consumidores.
    """
    parser = argparse.ArgumentParser(
        description="Processamento e geração de fichas de consumidores."
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
        logger = obter_logger("bdc.cli", Path("LOGS/execucao") / "cli_consumidores.log")
        logger.info("Contexto da aplicacao inicializado a partir de: %s", app_ctx.path('configs'))
        
        processar_fichas_consumidores(app_ctx)

    except Exception as exc:
        if 'logger' in locals():
            logger.error("Falha na execucao: %s", exc)
        else:
            sys.stderr.write(f"[ERRO] Falha na execucao: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()