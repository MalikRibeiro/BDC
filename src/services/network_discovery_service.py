"""Serviço de Coleta na Rede e Triagem Automática de Fichas de Crédito."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from common.excel import close_workbook_safely, open_workbook
from common.logging_utils import get_logger
from control.layout_catalog import (
    load_layouts_comercializadoras,
    load_layouts_consumidores,
)
from services.ficha_classifier import classify_workbook

EXTENSOES_EXCEL = {".xlsx", ".xls", ".xlsm"}

class NetworkDiscoveryError(Exception):
    """Exceção levantada para falhas na varredura de arquivos de rede."""

def _obter_assinaturas_locais(entradas_dir: Path) -> set[str]:
    """
    Varre a pasta local ENTRADAS/fichas (abrangendo pendentes, processadas, 
    rejeitadas e nao_identificados) e gera uma assinatura 'Nome_Tamanho' 
    para cada arquivo. Isso evita downloads redundantes da rede.
    """
    assinaturas = set()
    fichas_dir = entradas_dir / "fichas"
    
    if not fichas_dir.exists():
        return assinaturas

    for f in fichas_dir.rglob("*"):
        if f.is_file() and f.suffix.lower() in EXTENSOES_EXCEL and not f.name.startswith("~$"):
            try:
                # Assinatura rápida e leve: Nome do arquivo + Tamanho em bytes
                assinatura = f"{f.name}_{f.stat().st_size}"
                assinaturas.add(assinatura)
            except OSError:
                continue
                
    return assinaturas

def run_network_discovery(context: AppContext) -> dict[str, Any]:
    """
    Varre os diretórios de rede parametrizados, ignora arquivos já existentes localmente,
    classifica as novas fichas e as copia para as pastas de 'pendentes'.
    """
    run_id = f"DISC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__discovery.log"
    logger = get_logger("bdc.discovery", log_file)

    try:
        logger.info("Iniciando varredura inteligente na rede...")

        # 1. Carrega caminhos de rede e lista de arquivos já conhecidos
        network_paths = context.config.get("network_paths", {})
        if not network_paths:
            logger.warning("Nenhum 'network_paths' configurado no config.json.")
            return {"run_id": run_id, "status": "SEM_CONFIGURACAO"}

        assinaturas_conhecidas = _obter_assinaturas_locais(context.path("entradas"))
        logger.info("Encontrados %s arquivos já cacheados localmente. Eles serão ignorados na rede.", len(assinaturas_conhecidas))

        # 2. Carrega catálogos de layouts silenciosamente
        dummy_logger = logging.getLogger("dummy")
        dummy_logger.setLevel(logging.CRITICAL)
        layouts_com = load_layouts_comercializadoras(context, logger=dummy_logger)
        layouts_cons = load_layouts_consumidores(context, logger=dummy_logger)

        # 3. Prepara diretórios de destino
        dest_com = context.path("input_fichas_comercializadoras_pendentes")
        dest_cons = context.path("input_fichas_consumidores_pendentes")
        dest_falha = context.path("entradas") / "fichas" / "nao_identificados"

        dest_com.mkdir(parents=True, exist_ok=True)
        dest_cons.mkdir(parents=True, exist_ok=True)
        dest_falha.mkdir(parents=True, exist_ok=True)

        registros_relatorio = []
        cont_com, cont_cons, cont_falha, cont_ignorados = 0, 0, 0, 0

        # 4. Varredura na Rede
        for key, pasta_raiz in network_paths.items():
            raiz = Path(pasta_raiz)
            if not raiz.exists():
                logger.warning("Pasta de rede inacessível: %s", raiz)
                continue

            for caminho in raiz.rglob("*"):
                if not caminho.is_file() or caminho.suffix.lower() not in EXTENSOES_EXCEL or caminho.name.startswith("~$"):
                    continue

                nome_original = caminho.name
                
                # Filtro Antiduplicidade de Rede (Aderente à Seção 4.1 do Planejamento)
                try:
                    assinatura_rede = f"{nome_original}_{caminho.stat().st_size}"
                except OSError:
                    continue

                if assinatura_rede in assinaturas_conhecidas:
                    cont_ignorados += 1
                    continue

                logger.info("Novo arquivo detectado na rede: %s", nome_original)

                workbook = None
                destino_final = "ERRO_LEITURA"
                tipo_identificado = "FALHA/DESCONHECIDO"

                try:
                    # Trazemos para a memória (via openpyxl) SOMENTE se for um arquivo novo
                    workbook = open_workbook(caminho)

                    match_com = classify_workbook(workbook, layouts_com, logger=dummy_logger)
                    match_cons = None
                    if not match_com:
                        match_cons = classify_workbook(workbook, layouts_cons, logger=dummy_logger)

                    close_workbook_safely(workbook)

                    if match_com:
                        shutil.copy2(caminho, dest_com / nome_original)
                        tipo_identificado = "COMERCIALIZADORA"
                        destino_final = str(dest_com)
                        cont_com += 1
                    elif match_cons:
                        shutil.copy2(caminho, dest_cons / nome_original)
                        tipo_identificado = "CONSUMIDOR"
                        destino_final = str(dest_cons)
                        cont_cons += 1
                    else:
                        shutil.copy2(caminho, dest_falha / nome_original)
                        destino_final = str(dest_falha)
                        cont_falha += 1

                except Exception as e:
                    if workbook is not None:
                        close_workbook_safely(workbook)
                    logger.error("Erro ao ler %s: %s", nome_original, e)
                    shutil.copy2(caminho, dest_falha / f"[ERRO_LEITURA] {nome_original}")
                    destino_final = str(dest_falha)
                    cont_falha += 1

                # Adiciona a assinatura aos conhecidos em memória para evitar que
                # o mesmo arquivo repetido em duas pastas de rede seja copiado duas vezes no mesmo run.
                assinaturas_conhecidas.add(assinatura_rede)

                registros_relatorio.append({
                    "Origem_Rede": str(caminho),
                    "Nome_Arquivo": nome_original,
                    "Classificacao": tipo_identificado,
                    "Destino_Local": destino_final,
                    "Data_Coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        # 5. Geração de Relatório
        if registros_relatorio:
            df = pd.DataFrame(registros_relatorio)
            output_dir = context.path("output")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            nome_relatorio = output_dir / f"relatorio_triagem_{run_id}.xlsx"
            df.to_excel(nome_relatorio, index=False)
            logger.info("Relatório de triagem de rede gerado: %s", nome_relatorio.name)

        summary = {
            "run_id": run_id,
            "arquivos_ignorados_ja_locais": cont_ignorados,
            "comercializadoras_novas": cont_com,
            "consumidores_novos": cont_cons,
            "falhas_identificacao": cont_falha,
            "status": "SUCESSO"
        }
        
        logger.info("Discovery concluído. Resumo: %s", summary)
        return summary

    except Exception as exc:
        logger.exception("Falha crítica durante a triagem de rede.")
        raise NetworkDiscoveryError(f"Erro na varredura: {exc}") from exc