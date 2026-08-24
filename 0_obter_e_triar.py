"""RPA Unificado: Coleta na Rede e Triagem Automática de Fichas de Crédito."""

from __future__ import annotations

import sys
import shutil
import logging
import warnings
from pathlib import Path
from datetime import datetime
import pandas as pd

# --------------------------------------------------------------------
# 1. Configuração de Infraestrutura e Imports
# --------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
logging.getLogger("openpyxl").setLevel(logging.WARNING)

from app.context import carregar_contexto  # type: ignore
from control.layout_catalog import (
    carregar_layouts_comercializadoras,
    carregar_layouts_consumidores,
)
from common.excel import abrir_pasta, fechar_pasta
from domain.fichas.classificador import classificar_pasta_de_trabalho



# --------------------------------------------------------------------
# 2. Configuração das Origens da Rede
# --------------------------------------------------------------------
PASTAS_RAIZ_REDE = [
    r"S:\COM_CPR\3 ATIVIDADES E PROJETOS DA CPR\Limite Comercializadoras\Agentes_Demonstrações Financeiras\Fichas\2025",
    r"S:\COM_CPR\3 ATIVIDADES E PROJETOS DA CPR\Limite Comercializadoras\Agentes_Demonstrações Financeiras\Fichas\2026",
    r"S:\COM_CPR\3 ATIVIDADES E PROJETOS DA CPR\.Chamados SalesForce\2025",
    r"S:\COM_CPR\3 ATIVIDADES E PROJETOS DA CPR\.Chamados SalesForce\2026\.CONSUMIDORES LIVRES",
    r"S:\COM_CPR\3 ATIVIDADES E PROJETOS DA CPR\.Chamados SalesForce\2026\.COMERCIALIZADORAS E GERADORAS",
]

EXTENSOES_EXCEL = {".xlsx", ".xls", ".xlsm"}


# --------------------------------------------------------------------
# 3. Área externa de coleta
# --------------------------------------------------------------------
#
# Esta pasta NÃO depende do app_config.json.
# Ela fica diretamente na raiz do projeto.
#
PASTA_ARQUIVOS_FICHAS = ROOT / "arquivos_fichas"

PASTA_COMERCIALIZADORAS = (
    PASTA_ARQUIVOS_FICHAS / "comercializadoras"
)

PASTA_CONSUMIDORES = (
    PASTA_ARQUIVOS_FICHAS / "consumidores"
)

PASTA_NAO_IDENTIFICADOS = (
    PASTA_ARQUIVOS_FICHAS / "nao_identificados"
)

PASTA_DUPLICADOS = (
    PASTA_ARQUIVOS_FICHAS / "duplicados"
)


def criar_pastas():
    """Cria a estrutura externa de armazenamento das fichas."""

    for pasta in [
        PASTA_COMERCIALIZADORAS,
        PASTA_CONSUMIDORES,
        PASTA_NAO_IDENTIFICADOS,
        PASTA_DUPLICADOS,
    ]:
        pasta.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------
# 4. Antiduplicidade
# --------------------------------------------------------------------
def gerar_assinatura(caminho: Path) -> str | None:
    """
    Gera assinatura simples baseada em:
        nome do arquivo + tamanho em bytes

    Retorna None caso não consiga consultar o arquivo.
    """
    try:
        return f"{caminho.name}_{caminho.stat().st_size}"
    except OSError:
        return None


def obter_assinaturas_locais() -> set[str]:
    """
    Varre toda a pasta arquivos_fichas e obtém as assinaturas
    dos arquivos que já foram coletados.
    """

    assinaturas = set()

    if not PASTA_ARQUIVOS_FICHAS.exists():
        return assinaturas

    for arquivo in PASTA_ARQUIVOS_FICHAS.rglob("*"):

        if (
            not arquivo.is_file()
            or arquivo.suffix.lower() not in EXTENSOES_EXCEL
            or arquivo.name.startswith("~$")
        ):
            continue

        assinatura = gerar_assinatura(arquivo)

        if assinatura:
            assinaturas.add(assinatura)

    return assinaturas


# --------------------------------------------------------------------
# 5. Cópia segura
# --------------------------------------------------------------------
def copiar_sem_sobrescrever(
    origem: Path,
    destino: Path,
    assinatura: str,
) -> str:
    """
    Copia o arquivo somente se ele ainda não existir na área de coleta.

    Retorna:
        COPIADO
        DUPLICADO
    """

    destino.mkdir(parents=True, exist_ok=True)

    destino_final = destino / origem.name

    # --------------------------------------------------------------
    # Caso 1: já existe arquivo com mesmo nome
    # --------------------------------------------------------------
    if destino_final.exists():

        assinatura_existente = gerar_assinatura(destino_final)

        if assinatura_existente == assinatura:
            return "DUPLICADO"

        # Mesmo nome, porém conteúdo/tamanho diferente.
        # Não sobrescreve.
        # Joga para uma área específica para análise manual.
        destino_duplicado = PASTA_DUPLICADOS / origem.name

        contador = 1

        while destino_duplicado.exists():
            destino_duplicado = (
                PASTA_DUPLICADOS
                / f"{origem.stem}__duplicado_{contador}{origem.suffix}"
            )
            contador += 1

        shutil.copy2(origem, destino_duplicado)
        return "DUPLICADO"

    # --------------------------------------------------------------
    # Caso 2: arquivo ainda não existe
    # --------------------------------------------------------------
    shutil.copy2(origem, destino_final)

    return "COPIADO"


# --------------------------------------------------------------------
# 6. Motor Principal
# --------------------------------------------------------------------
def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    logger = logging.getLogger("rpa_triagem")

    logger.info("==================================================")
    logger.info("RPA - COLETA E TRIAGEM DE FICHAS")
    logger.info("==================================================")

    logger.info("Carregando contexto e regras do motor oficial...")

    configs_dir = ROOT / "ENTRADAS" / "configs"
    context = carregar_contexto(configs_dir)

    # --------------------------------------------------------------
    # Criação da estrutura externa
    # --------------------------------------------------------------
    criar_pastas()

    logger.info(
        "Área externa de coleta: %s",
        PASTA_ARQUIVOS_FICHAS,
    )

    # --------------------------------------------------------------
    # Carrega layouts oficiais
    # --------------------------------------------------------------
    logger.info("Carregando layouts de comercializadoras...")

    layouts_com = carregar_layouts_comercializadoras(
        context,
        logger=logging.getLogger("dummy"),
    )

    logger.info("Carregando layouts de consumidores...")

    layouts_cons = carregar_layouts_consumidores(
        context,
        logger=logging.getLogger("dummy"),
    )

    # --------------------------------------------------------------
    # Obtém arquivos já conhecidos
    # --------------------------------------------------------------
    assinaturas_conhecidas = obter_assinaturas_locais()

    logger.info(
        "Arquivos já existentes na área externa: %s",
        len(assinaturas_conhecidas),
    )

    # --------------------------------------------------------------
    # Contadores
    # --------------------------------------------------------------
    cont_com = 0
    cont_cons = 0
    cont_falha = 0
    cont_ignorados = 0
    cont_erros = 0

    registros_relatorio = []

    # --------------------------------------------------------------
    # Varredura das redes
    # --------------------------------------------------------------
    for pasta_raiz in PASTAS_RAIZ_REDE:

        raiz = Path(pasta_raiz)

        logger.info("--------------------------------------------------")
        logger.info("Verificando: %s", raiz)

        if not raiz.exists():
            logger.warning(
                "Pasta da rede não encontrada: %s",
                raiz,
            )
            continue

        for caminho in raiz.rglob("*"):

            if (
                not caminho.is_file()
                or caminho.suffix.lower() not in EXTENSOES_EXCEL
                or caminho.name.startswith("~$")
            ):
                continue

            nome_original = caminho.name

            assinatura_rede = gerar_assinatura(caminho)

            if not assinatura_rede:
                logger.warning(
                    "Não foi possível obter assinatura: %s",
                    caminho,
                )
                continue

            # ------------------------------------------------------
            # ANTIDUPLICIDADE
            # ------------------------------------------------------
            if assinatura_rede in assinaturas_conhecidas:

                cont_ignorados += 1

                logger.info(
                    "IGNORADO - arquivo já coletado: %s",
                    nome_original,
                )

                registros_relatorio.append(
                    {
                        "Origem_Rede": str(caminho),
                        "Nome_Arquivo": nome_original,
                        "Classificacao": "DUPLICADO_IGNORADO",
                        "Destino_Local": "",
                        "Data_Coleta": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                )

                continue

            logger.info(
                "NOVO arquivo detectado: %s",
                nome_original,
            )

            workbook = None

            destino_final = ""
            tipo_identificado = "FALHA/DESCONHECIDO"
            status_copia = "ERRO"

            try:

                # --------------------------------------------------
                # Abertura da planilha
                # --------------------------------------------------
                workbook = abrir_pasta(str(caminho))

                # --------------------------------------------------
                # Teste Comercializadora
                # --------------------------------------------------
                match_com = classificar_pasta_de_trabalho(
                    workbook,
                    layouts_com,
                    logger=logging.getLogger("dummy_classifier"),
                )

                # --------------------------------------------------
                # Teste Consumidor
                # --------------------------------------------------
                match_cons = None

                if not match_com:

                    match_cons = classificar_pasta_de_trabalho(
                        workbook,
                        layouts_cons,
                        logger=logging.getLogger("dummy_classifier"),
                    )

                fechar_pasta(workbook)
                workbook = None

                # --------------------------------------------------
                # Define destino
                # --------------------------------------------------
                if match_com:

                    destino = PASTA_COMERCIALIZADORAS

                    tipo_identificado = "COMERCIALIZADORA"

                    cont_com += 1

                elif match_cons:

                    destino = PASTA_CONSUMIDORES

                    tipo_identificado = "CONSUMIDOR"

                    cont_cons += 1

                else:

                    destino = PASTA_NAO_IDENTIFICADOS

                    tipo_identificado = "NAO_IDENTIFICADO"

                    cont_falha += 1

                # --------------------------------------------------
                # Cópia segura
                # --------------------------------------------------
                status_copia = copiar_sem_sobrescrever(
                    origem=caminho,
                    destino=destino,
                    assinatura=assinatura_rede,
                )

                if status_copia == "COPIADO":

                    destino_final = str(destino)

                    logger.info(
                        "COPIADO -> %s",
                        destino,
                    )

                else:

                    destino_final = str(PASTA_DUPLICADOS)

                    logger.info(
                        "DUPLICADO -> não sobrescrito: %s",
                        nome_original,
                    )

                # --------------------------------------------------
                # Adiciona à memória
                # --------------------------------------------------
                assinaturas_conhecidas.add(assinatura_rede)

            except Exception as e:

                cont_erros += 1

                if workbook is not None:
                    fechar_pasta(workbook)

                logger.error(
                    "Erro ao ler %s: %s",
                    nome_original,
                    e,
                )

                try:

                    status_copia = copiar_sem_sobrescrever(
                        origem=caminho,
                        destino=PASTA_NAO_IDENTIFICADOS,
                        assinatura=assinatura_rede,
                    )

                    destino_final = str(
                        PASTA_NAO_IDENTIFICADOS
                    )

                    tipo_identificado = "ERRO_LEITURA"

                    cont_falha += 1

                except Exception as erro_copia:

                    logger.error(
                        "Erro ao copiar arquivo com falha: %s",
                        erro_copia,
                    )

            # ------------------------------------------------------
            # Relatório
            # ------------------------------------------------------
            registros_relatorio.append(
                {
                    "Origem_Rede": str(caminho),
                    "Nome_Arquivo": nome_original,
                    "Classificacao": tipo_identificado,
                    "Destino_Local": destino_final,
                    "Status_Copia": status_copia,
                    "Data_Coleta": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )

    # ----------------------------------------------------------------
    # 7. Relatório
    # ----------------------------------------------------------------
    if registros_relatorio:

        df = pd.DataFrame(registros_relatorio)

        nome_relatorio = (
            ROOT
            / f"relatorio_triagem_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )

        df.to_excel(
            nome_relatorio,
            index=False,
        )

        logger.info(
            "Relatório gerado: %s",
            nome_relatorio,
        )

    # ----------------------------------------------------------------
    # 8. Resumo
    # ----------------------------------------------------------------
    print()
    print("=" * 60)
    print("RESUMO DA TRIAGEM")
    print("=" * 60)
    print(f"✅ Comercializadoras novas : {cont_com}")
    print(f"✅ Consumidores novos      : {cont_cons}")
    print(f"⚠️ Não identificados       : {cont_falha}")
    print(f"🔁 Duplicados ignorados    : {cont_ignorados}")
    print(f"❌ Erros                   : {cont_erros}")
    print("=" * 60)
    print(f"📁 Arquivos: {PASTA_ARQUIVOS_FICHAS}")
    print("=" * 60)


# --------------------------------------------------------------------
# 9. Execução
# --------------------------------------------------------------------
if __name__ == "__main__":
    main()