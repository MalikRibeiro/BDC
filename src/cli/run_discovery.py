"""CLI para disparar a varredura e triagem de fichas na rede corporativa."""

import argparse
import sys
from pathlib import Path

from app.bootstrap import bootstrap_application
from services.network_discovery_service import run_network_discovery


def build_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos para o script de discovery."""
    parser = argparse.ArgumentParser(
        description="Varre pastas de rede, classifica fichas e as copia para processamento."
    )
    parser.add_argument(
        "--configs-dir",
        type=str,
        default=None,
        help="Caminho para o diretório de configurações (opcional).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        app_ctx = bootstrap_application(configs_dir=args.configs_dir)
        print(f"[INFO] Contexto inicializado a partir de: {app_ctx.path('configs')}")
        
        print("\n" + "="*60)
        print("INICIANDO VARREDURA E TRIAGEM NA REDE")
        print("="*60)

        # Inicia a varredura real
        summary = run_network_discovery(app_ctx)
        
        print("\n" + "="*60)
        print("RESUMO DA TRIAGEM")
        print("="*60)
        print(f"✅ Comercializadoras (Movidas para pendentes): {summary.get('comercializadoras_encontradas', 0)}")
        print(f"✅ Consumidores (Movidas para pendentes)   : {summary.get('consumidores_encontrados', 0)}")
        print(f"❌ Não Identificados / Erros             : {summary.get('falhas_identificacao', 0)}")
        print(f"📄 Status Final                          : {summary.get('status')}")
        print("="*60)

    except Exception as exc:
        print(f"\n[ERRO CRÍTICO] Falha na execução do Discovery: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()