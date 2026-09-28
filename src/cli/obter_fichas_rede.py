"""CLI para Obtenção e Classificação de Fichas Cadastrais da Rede Corporativa."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.connectors.fichas_connector import obter_fichas_rede
from control.logger import obter_logger


def criar_analisador() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Obtém e classifica fichas cadastrais da rede para as pastas pendentes locais."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="ENTRADAS/configs/catalogo_fontes_rede.json",
        help="Caminho do catálogo JSON com as fontes de rede.",
    )
    return parser


def main() -> int:
    parser = criar_analisador()
    args, _ = parser.parse_known_args()

    logger = obter_logger("cli.obter_fichas_rede", Path("LOGS/ingestion/cli_obter_fichas_rede.log"))
    logger.info("Iniciando obtenção de fichas da rede corporativa.")

    try:
        resultado = obter_fichas_rede(caminho_config_json=args.config, logger_inst=logger)
        logger.info("Resultado final: %s", resultado)

        print("\n" + "=" * 70)
        print("RELATÓRIO DE OBTENÇÃO E VALIDAÇÃO DE FICHAS CADASTRAIS (BDC):")
        print("=" * 70)
        print(f"Status da operação:                               {resultado.get('status', 'desconhecido').upper()}")
        print(f"Fichas locais restauradas para Consumidores:      {resultado.get('redistribuidos_locais_consumidores', 0)}")
        print(f"Fichas locais restauradas para Comercializadoras: {resultado.get('redistribuidos_locais_comercializadoras', 0)}")
        print(f"Total atual na pasta Comercializadoras:           {resultado.get('total_local_comercializadoras', 0)}")
        print(f"Total atual na pasta Consumidores:                {resultado.get('total_local_consumidores', 0)}")
        print(f"Novas fichas sincronizadas da rede:               {resultado.get('arquivos_novos_total', 0)}")
        print(f"  - Comercializadoras novas da rede:              {resultado.get('comercializadoras_novas', 0)}")
        print(f"  - Consumidores novos da rede:                   {resultado.get('consumidores_novos', 0)}")
        print(f"Fichas idênticas mantidas (sem reprocessamento):  {resultado.get('arquivos_ignorados', 0)}")
        print(f"Planilhas descartadas por não serem fichas (Veto):{resultado.get('arquivos_descartados_veto', 0)}")
        print("=" * 70 + "\n")

        return 0 if resultado.get("status") in ("sucesso", "desabilitado", "rede_inacessivel") else 1
    except Exception as exc:
        logger.exception("Falha crítica ao obter fichas da rede: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
