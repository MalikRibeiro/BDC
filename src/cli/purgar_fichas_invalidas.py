"""Utilitário de Higienização e Purga de Fichas Inválidas nas Pastas Locais.

Varre as pastas:
- ENTRADAS/fichas/comercializadoras/pendentes/
- ENTRADAS/fichas/consumidores/pendentes/

Aplica o Gate Rigoroso de Abas Oficiais e Nomes:
1. Remove planilhas de aditivos, controles, memórias de cálculo avulsas e templates.
2. Corrige arquivos que estejam na pasta errada (ex: move consumidor para consumidor).
3. Atualiza e higieniza o manifesto_fichas_rede.json em SAIDAS/bronze/ingestion_log/.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import shutil
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.connectors.fichas_connector import validar_se_eh_ficha_cadastral, _carregar_manifesto, _salvar_manifesto
from control.logger import obter_logger

LOGGER = obter_logger("purgar_fichas", Path("LOGS/ingestion/purgar_fichas.log"))


def purgar_fichas_invalidas(mover_para_quarentena: bool = False) -> dict[str, Any]:
    pasta_comerc = Path("ENTRADAS/fichas/comercializadoras/pendentes")
    pasta_consum = Path("ENTRADAS/fichas/consumidores/pendentes")
    pasta_quarentena = Path("ENTRADAS/fichas/descartadas")
    
    manifesto_path = Path("SAIDAS/bronze/ingestion_log/manifesto_fichas_rede.json")
    if not manifesto_path.exists():
        manifesto_path = Path("ENTRADAS/fichas/manifesto_fichas_rede.json")
        
    manifesto = _carregar_manifesto(manifesto_path)

    removidos = []
    movidos_para_correto = []
    mantidos = {"comercializadoras": 0, "consumidores": 0}

    # 1. Varre Comercializadoras
    if pasta_comerc.exists():
        for arq in list(pasta_comerc.iterdir()):
            if not arq.is_file() or arq.name.startswith("~$"):
                continue

            eh_ficha, seg, motivo = validar_se_eh_ficha_cadastral(arq)
            if not eh_ficha:
                removidos.append((arq.name, "comercializadoras", motivo))
                if mover_para_quarentena:
                    pasta_quarentena.mkdir(parents=True, exist_ok=True)
                    shutil.move(arq, pasta_quarentena / arq.name)
                else:
                    arq.unlink(missing_ok=True)
            elif seg == "consumidores":
                # Ficha de consumidor que caiu em comercializadoras -> move para o lugar certo
                pasta_consum.mkdir(parents=True, exist_ok=True)
                destino = pasta_consum / arq.name
                shutil.move(arq, destino)
                movidos_para_correto.append((arq.name, "comercializadoras -> consumidores"))
                mantidos["consumidores"] += 1
            else:
                mantidos["comercializadoras"] += 1

    # 2. Varre Consumidores
    if pasta_consum.exists():
        for arq in list(pasta_consum.iterdir()):
            if not arq.is_file() or arq.name.startswith("~$"):
                continue

            eh_ficha, seg, motivo = validar_se_eh_ficha_cadastral(arq)
            if not eh_ficha:
                removidos.append((arq.name, "consumidores", motivo))
                if mover_para_quarentena:
                    pasta_quarentena.mkdir(parents=True, exist_ok=True)
                    shutil.move(arq, pasta_quarentena / arq.name)
                else:
                    arq.unlink(missing_ok=True)
            elif seg == "comercializadoras":
                # Ficha de comercializadora que caiu em consumidores -> move para o lugar certo
                pasta_comerc.mkdir(parents=True, exist_ok=True)
                destino = pasta_comerc / arq.name
                shutil.move(arq, destino)
                movidos_para_correto.append((arq.name, "consumidores -> comercializadoras"))
                mantidos["comercializadoras"] += 1
            else:
                mantidos["consumidores"] += 1

    # 3. Limpar entradas removidas do manifesto
    nomes_removidos = {item[0] for item in removidos}
    chaves_para_deletar = [k for k, v in manifesto.items() if v.get("nome_arquivo") in nomes_removidos]
    for k in chaves_para_deletar:
        del manifesto[k]

    _salvar_manifesto(manifesto_path, manifesto)

    print(f"\n{'=' * 70}")
    print("RELATÓRIO DE HIGIENIZAÇÃO DE FICHAS CADASTRAIS:")
    print(f"{'=' * 70}")
    print(f"Total de planilhas lixo/inválidas expurgadas: {len(removidos)}")
    print(f"Fichas redirecionadas para a pasta correta:   {len(movidos_para_correto)}")
    print(f"Fichas válidas mantidas em Comercializadoras: {mantidos['comercializadoras']}")
    print(f"Fichas válidas mantidas em Consumidores:      {mantidos['consumidores']}")
    print(f"Manifesto atualizado em: {manifesto_path}")
    print(f"{'=' * 70}\n")

    if removidos:
        print("Amostra de arquivos descartados por não serem fichas cadastrais:")
        for nome, pasta, motivo in removidos[:15]:
            print(f"  [X] ({pasta}) {nome} -> Motivo: {motivo}")
        if len(removidos) > 15:
            print(f"  ... e mais {len(removidos) - 15} arquivos purgados.")
    print(f"{'=' * 70}\n")

    return {
        "removidos": len(removidos),
        "movidos": len(movidos_para_correto),
        "mantidos": mantidos,
    }


if __name__ == "__main__":
    purgar_fichas_invalidas(mover_para_quarentena=False)
