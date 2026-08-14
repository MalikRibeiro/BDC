import argparse
import sys
from pathlib import Path

from src.app.bootstrap import bootstrap_application
from src.services.fichas_consumidores_service import process_fichas_consumidores


def build_parser() -> argparse.ArgumentParser:
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
    parser = build_parser()
    args = parser.parse_args()

    try:
        app_ctx = bootstrap_application(configs_dir=args.configs_dir)
        print(f"[INFO] Contexto da aplicacao inicializado a partir de: {app_ctx.path('configs')}")
        
        # Inicia o processamento real da fila
        summary = process_fichas_consumidores(app_ctx)
        print(f"[INFO] Resumo do processamento: {summary}")

    except Exception as exc:
        print(f"[ERRO] Falha na execucao: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()