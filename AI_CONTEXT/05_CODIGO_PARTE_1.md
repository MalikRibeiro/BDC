# CÓDIGO PARTE 1


---
## 0_obter_e_triar.py
Linhas: 516
Classes: -
Funções: criar_pastas, gerar_assinatura, obter_assinaturas_locais, copiar_sem_sobrescrever, main
```python
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
from common import abrir_pasta, fechar_pasta
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
```


---
## src\app\consumidores\orquestrador.py
Linhas: 709
Classes: -
Funções: disco_cheio_erro, criar_run_id, criar_alvo_nome, resolver_subpasta_bronze, mover_para_rejeitados, mover_para_processados, criar_info_pd, criar_fila_processamento, processar_arquivo_individual, processar_fichas_consumidores
```python
"""Serviço principal refatorado do pipeline de fichas de consumidores."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.context import AppContext
from common.excel import fechar_pasta, abrir_pasta
from common.hashing import arquivo_hash
from common.json import ler_json
from control.logger import obter_logger
from silver.normalizadores import padronizar_cnpj
from common.paths import sanitizar_nome_da_pasta

from control.layout_catalog import carregar_layouts_consumidores
from control.carregador_de_mapeamento import mapeamento_de_carga_fichas_consumidores
from control.quality_loader import carregar_regras_de_qualidade_de_dados_consumidores
from domain.contrapartes.segmentacao import definir_segmento_metodologico
from domain.credito.pd_motor import calcular_pd_ajustada
from common.servico_desduplicacao import (
    tem_chave_de_negocio_duplicada,
    tem_hash_duplicado,
    virar_chave_de_negocio_no_historico,
)
from domain.fichas.validador import validar_registro_consumidor
from app.consumidores.classificacao import (
    classificar_consumidor,
    criar_classificacao_registro,
    VERSAO_REGRA_ATUAL,
)
from silver.documentos_classificados import criar_documento_classificado
from silver.normalizador_de_tipo_de_campo import normalizar_registro
from staging.descoberta import detectar_arquivos_excel_pendentes
from staging.staging_arquivo import copiar_para_staging
from storage.bronze_arquivo import publicar_arquivo_bruto
from storage.operacao_arquivo import mover_arquivo_com_tentativa_adicional
from storage.armazenamento_manifest import (
    anexar_registro_de_manifesto,
    historico_de_ingestao_de_carga,
)
from storage.escrever_dados import (
    mesclar_conjunto_de_dados_prata_por_chave_de_negocio,
    escrever_conjunto_de_dados_silver,
)
from storage.estado_armazenamento import DocumentManifest

def disco_cheio_erro(exc: Exception) -> bool:
    """Indica se a exceção representa falta de espaço em disco."""
    if not isinstance(exc, OSError):
        return False

    text = str(exc).lower()
    return (
        getattr(exc, "winerror", None) == 112
        or getattr(exc, "errno", None) == 28
        or "no space left on device" in text
        or "espaço insuficiente no disco" in text
    )


def criar_run_id(context: AppContext) -> str:
    """Monta o identificador textual da execução."""
    prefix = context.naming.get("run_id_prefix", "BDC")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"


def criar_alvo_nome(
    original_name: str,
    versao_ficha: str | None,
    cnpj: str | None,
    data_df: str | None,
    hash_value: str | None,
) -> str:
    source = Path(original_name)
    stem = source.stem[:40]

    parts: list[str] = [stem]

    if versao_ficha:
        parts.append(versao_ficha)

    if cnpj:
        safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit())
        parts.append(safe_cnpj)

    if data_df:
        safe_data_df = "".join(ch for ch in str(data_df) if ch.isdigit())
        parts.append(safe_data_df[:8])

    if hash_value:
        parts.append(hash_value[:8])

    return "__".join(parts) + source.suffix.lower()


def resolver_subpasta_bronze(
    cnpj: str | None,
    sigla: str | None,
) -> str:
    """Resolve a subpasta da bronze organizada por CNPJ e sigla."""
    if not cnpj:
        raise ValueError("Não é possível publicar em bronze sem CNPJ válido.")
    safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit())
    safe_sigla = sanitizar_nome_da_pasta(sigla or "")
    if safe_sigla:
        return f"{safe_cnpj}__{safe_sigla}"

    return safe_cnpj


def mover_para_rejeitados(
    source_file: Path,
    rejected_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
) -> None:
    """Move o arquivo para rejeitados e grava o manifest."""
    target = rejected_dir / source_file.name

    try:
        if source_file.exists():
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para rejeitados: {exc}")
        logger.exception("Falha ao mover %s para rejeitados.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
    except Exception as exc:
        logger.exception(
            "Falha ao gravar manifest de rejeição para %s.", source_file.name
        )
        raise


def mover_para_processados(
    source_file: Path,
    processed_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
) -> None:
    """Move o arquivo para processadas e grava o manifest."""
    target = processed_dir / source_file.name

    try:
        if source_file.exists():
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para processadas: {exc}")
        logger.exception("Falha ao mover %s para processadas.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
    except Exception as exc:
        logger.exception(
            "Falha ao gravar manifest de processamento para %s.", source_file.name
        )
        raise


def criar_info_pd(
    normalized: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    logger: Any,
    source_file: Path,
    manifest: DocumentManifest,
) -> dict[str, Any]:
    """Calcula a PD ajustada para o registro normalizado de consumidor."""
    segmento_pd: str | None = None

    try:
        registro_pd = dict(normalized)
        registro_pd["TIPO_FICHA"] = "CONSUMIDOR"

        segmento_pd = definir_segmento_metodologico(registro_pd)
        registro_pd["SEGMENTO_PD"] = segmento_pd

        pd_info = calcular_pd_ajustada(
            registro=registro_pd,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=None,
            score_cpura_config=None,
            logger=logger,
        )

        logger.info(
            "PD ajustada calculada para %s. Segmento=%s RATING_FINAL=%s PD_FINAL=%s",
            source_file.name,
            pd_info.get("SEGMENTO_PD"),
            pd_info.get("RATING_FINAL"),
            pd_info.get("PD_FINAL"),
        )
        return pd_info

    except Exception as exc:
        logger.warning(
            "PD ajustada não calculada para %s. Motivo: %s",
            source_file.name,
            exc,
        )
        manifest.avisos.append(f"PD ajustada não calculada: {exc}")

        return {
            "SEGMENTO_PD": segmento_pd,
            "PD_BASE": None,
            "RATING_FINAL": None,
            "PD_MIN_FAIXA": None,
            "PD_MAX_FAIXA": None,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": None,
            "PD_METODO": None,
            "PD_Q_NORMALIZADA": None,
            "PD_Q_CAP": None,
            "PD_Z_T": None,
            "PD_Z_ESCALADO": None,
            "PD_U_INTERPOLACAO": None,
        }


def criar_fila_processamento(
    context: AppContext,
) -> list[tuple[Path, str, Path, Path]]:
    """Monta a fila de processamento normal e reprocessamento."""
    normal_files = detectar_arquivos_excel_pendentes(
        context.path("input_fichas_consumidores_pendentes")
    )
    reprocess_files = detectar_arquivos_excel_pendentes(
        context.path("input_reprocessamento_consumidores_pendentes")
    )

    queue: list[tuple[Path, str, Path, Path]] = []

    for file_path in normal_files:
        queue.append(
            (
                file_path,
                "incremental",
                context.path("input_fichas_consumidores_processadas"),
                context.path("input_fichas_consumidores_rejeitadas"),
            )
        )

    for file_path in reprocess_files:
        queue.append(
            (
                file_path,
                "reprocess",
                context.path("input_reprocessamento_consumidores_processados"),
                context.path("input_reprocessamento_consumidores_rejeitados"),
            )
        )

    return queue


def processar_arquivo_individual(
    source_file: Path,
    load_mode: str,
    processed_dir: Path,
    rejected_dir: Path,
    context: AppContext,
    layouts: dict[str, Any],
    required_fields: Any,
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    quality_rules: dict[str, Any],
) -> Optional[dict[str, Any]]:
    """Processa isoladamente um único arquivo de ficha de consumidor."""
    workbook = None
    manifest = DocumentManifest(
        documento_id=str(uuid.uuid4()),
        run_id=run_id,
        ambiente=context.app_config["env"],
        tipo_ficha="consumidor",
        arquivo_nome=source_file.name,
        caminho_origem=str(source_file),
        load_mode=load_mode,
    )

    try:
        logger.info(
            "Iniciando processamento do arquivo %s em modo %s.",
            source_file.name,
            load_mode,
        )

        manifest.hash_arquivo = arquivo_hash(source_file)

        # 1. Duplicidade por Hash
        if load_mode == "incremental" and tem_hash_duplicado(
            history, manifest.hash_arquivo
        ):
            manifest.status_extracao = "ERRO_DUPLICIDADE_HASH"
            manifest.erros.append("Hash já processado anteriormente.")
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        # 2. Copia para Staging
        staging_dir = context.path("staging_fichas_consumidores")
        staging_name = criar_alvo_nome(
            original_name=source_file.name,
            versao_ficha=None,
            cnpj=None,
            data_df=None,
            hash_value=manifest.hash_arquivo,
        )
        staging_file = copiar_para_staging(source_file, staging_dir, staging_name)
        manifest.caminho_staging = str(staging_file)

        # 3 & 4. Extração Competitiva (Tournament Extraction)
        workbook = abrir_pasta(staging_file)
        from domain.fichas.extrator import extrair_registro_do_vencedor

        raw_record, metadata_list, winner_layout = extrair_registro_do_vencedor(workbook, layouts, quality_rules)

        if winner_layout == "DOC_001_ESTRUTURA_INCOMPATIVEL":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("DOC_001_ESTRUTURA_INCOMPATIVEL: Nenhuma aba compativel com o layout esperada foi encontrada.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        if not winner_layout or winner_layout == "NENHUM":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("Nenhum layout obteve score suficiente.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        manifest.versao_ficha = winner_layout
        manifest.status_classificacao = "CLASSIFICADO"

        logger.info(
            "Extração competitiva: Vencedor %s identificado para %s.",
            winner_layout,
            source_file.name,
        )

        classification = type("MockClassification", (), {"versao_ficha": winner_layout})()
        
        # Registrar linhagem se directory control existir (omitido para consumidor ou implementado se necessário)
        
        slug = "field_types_fichas_consumidores"
        normalized = normalizar_registro(raw_record, context, slug, logger)
        normalized.pop("DADOS_CADASTRAIS", None)
        
        # 4a. Normalização Semântica de Domínio (Negócio)
        from common.domain_normalizer import aplicar_normalizacao_de_dominio
        normalized = aplicar_normalizacao_de_dominio(normalized, context, logger)

        manifest.cnpj_extraido = normalized.get("CNPJ")
        manifest.data_demonstracao_financeira = normalized.get(
            "DATA_DEMONSTRACAO_FINANCEIRA"
        )
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        # 4b. Classificação Documental
        classificacao = classificar_consumidor(
            record=normalized,
            versao_layout=classification.versao_ficha,
        )

        logger.info(
            "Classificação documental para %s: tipo=%s analise=%s confianca=%s",
            source_file.name,
            classificacao.tipo_consumidor,
            classificacao.tipo_analise_exigida,
            classificacao.confianca_classificacao,
        )

        # Regra de Negócio: Consumidores < 5 MWm não possuem DF.
        if getattr(classificacao, "tipo_analise_exigida", "") == "simplificada":
            campos_df = [
                "ATIVO_CIRCULANTE", "ATIVO_TOTAL", "PASSIVO_CIRCULANTE", "PATRIMONIO_LIQUIDO",
                "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "ROA", "ROE", "FCO_ROL"
            ]
            for campo in campos_df:
                if campo not in normalized or normalized[campo] is None:
                    normalized[campo] = None

        # 5. Validações Técnicas e CNPJ (com regras condicionais por tipo de consumidor)
        req_fields_dict = quality_rules.get("required_fields_by_version", {})
        validate_fields = req_fields_dict.get(classification.versao_ficha, [])
        errors, warnings = validar_registro_consumidor(
            normalized,
            validate_fields,
            classificacao=classificacao,
            logger=logger,
            quality_rules=quality_rules,
        )
        
        integridade = normalized.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        if integridade >= 40.0:
            # Tolerância a missing se a integridade geral for satisfatória
            critical_errors = []
            for e in errors:
                if "ausente" in e.lower() or "não informado" in e.lower() or "não informada" in e.lower():
                    warnings.append(f"Ignorado por Integridade >= 40%: {e}")
                else:
                    critical_errors.append(e)
            errors = critical_errors

        manifest.erros.extend(errors)
        manifest.avisos.extend(warnings)

        if integridade < 40.0:
            manifest.status_extracao = "ERRO_INTEGRIDADE"
            manifest.erros.append(f"Integridade baixa: {integridade}% (mínimo 40%). Ficha rejeitada.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        if not manifest.cnpj_extraido:
            manifest.status_extracao = "ERRO_SEM_CNPJ"
            manifest.erros.append("Ficha sem CNPJ válido.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        if not padronizar_cnpj(manifest.cnpj_extraido):
            manifest.status_extracao = "ERRO_CNPJ_INVALIDO"
            manifest.erros.append(f"CNPJ inválido: {manifest.cnpj_extraido}")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO"
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        # 6. Checagem de Duplicidade de Negócio
        duplicate_business = tem_chave_de_negocio_duplicada(
            history,
            manifest.cnpj_extraido,
            manifest.data_demonstracao_financeira,
        )

        if duplicate_business and load_mode == "incremental":
            manifest.status_extracao = "ERRO_DUPLICIDADE_NEGOCIO"
            manifest.erros.append(
                "Já existe documento com mesmo CNPJ e data da DF."
            )
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
            return None

        if duplicate_business and load_mode == "reprocess":
            manifest.reprocessed = True
            manifest.previous_record_found = True
        elif load_mode == "reprocess":
            manifest.reprocessed = False
            manifest.previous_record_found = False

        fechar_pasta(workbook)
        workbook = None

        # 7. Cálculo das Regras de Negócio (PD)
        pd_info = criar_info_pd(
            normalized=normalized,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            logger=logger,
            source_file=source_file,
            manifest=manifest,
        )

        # 8. Movimentação para Bronze e Processadas
        bronze_root_dir = context.path("bronze_fichas_consumidores_raw")
        bronze_name = criar_alvo_nome(
            original_name=source_file.name,
            versao_ficha=manifest.versao_ficha,
            cnpj=manifest.cnpj_extraido,
            data_df=manifest.data_demonstracao_financeira,
            hash_value=manifest.hash_arquivo,
        )

        bronze_subfolder = resolver_subpasta_bronze(
            manifest.cnpj_extraido,
            normalized.get("EMPRESA"),
        )

        bronze_staging = copiar_para_staging(
            staging_file, staging_dir, bronze_name
        )
        bronze_file = publicar_arquivo_bruto(
            source_file=bronze_staging,
            bronze_root_dir=bronze_root_dir / bronze_subfolder,
        )
        manifest.caminho_bronze = str(bronze_file)
        manifest.status_extracao = "SUCESSO"

        mover_para_processados(
            source_file, processed_dir, manifest, ingestion_log_path, logger
        )
        virar_chave_de_negocio_no_historico(history, manifest.to_dict())

        logger.info("Ficha processada com sucesso: %s.", source_file.name)

        # 9. Retorno dos Dados Estruturados
        classificacao_record = criar_classificacao_registro(classificacao)

        silver_record = {
            **normalized,
            **pd_info,
            **classificacao_record,
            "documento_id": manifest.documento_id,
            "run_id": run_id,
            "ambiente": manifest.ambiente,
            "tipo_ficha": manifest.tipo_ficha,
            "versao_ficha": manifest.versao_ficha,
            "arquivo_nome": manifest.arquivo_nome,
            "hash_arquivo": manifest.hash_arquivo,
            "load_mode": load_mode,
            "dt_processamento": datetime.now().isoformat(timespec="seconds"),
            "versao_regra_enquadramento": VERSAO_REGRA_ATUAL,
            "METADADOS_EXTRACAO": metadata_list,
        }

        classified_document = criar_documento_classificado(
            documento_id=manifest.documento_id,
            run_id=run_id,
            ambiente=manifest.ambiente,
            arquivo_nome=manifest.arquivo_nome or "",
            versao_ficha=manifest.versao_ficha or "",
            tipo_ficha=manifest.tipo_ficha,
            hash_arquivo=manifest.hash_arquivo or "",
        )

        return {
            "silver_record": silver_record,
            "classified_document": classified_document,
        }

    except Exception as exc:
        if workbook:
            fechar_pasta(workbook)

        manifest.status_extracao = "ERRO_PROCESSAMENTO"
        manifest.erros.append(str(exc))

        if disco_cheio_erro(exc):
            logger.exception(
                "Execução interrompida por falta de espaço em disco ao processar %s.",
                source_file.name,
            )
            raise

        try:
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger
            )
        except Exception as move_exc:
            if disco_cheio_erro(move_exc):
                logger.exception(
                    "Execução interrompida por falta de espaço em disco ao registrar rejeição do arquivo %s.",
                    source_file.name,
                )
                raise

            logger.exception(
                "Falha adicional ao mover/gravar rejeição do arquivo %s.",
                source_file.name,
            )
            raise

        logger.exception("Falha inesperada ao processar %s.", source_file.name)
        return None


def processar_fichas_consumidores(
    context: AppContext,
) -> dict[str, Any]:
    """Executa o pipeline completo das fichas de consumidores."""
    run_id = criar_run_id(context)

    log_file = (
        context.path("log_runner") / f"{run_id}__fichas_consumidores.log"
    )
    logger = obter_logger("bdc.consumidores", log_file)

    _ = mapeamento_de_carga_fichas_consumidores(context, logger)

    layouts = carregar_layouts_consumidores(context, logger)
    quality_rules = carregar_regras_de_qualidade_de_dados_consumidores(context, logger)

    required_fields = quality_rules.get("required_fields")

    ingestion_log_path = (
        context.path("bronze_ingestion_log")
        / "fichas_consumidores_ingestion.jsonl"
    )
    history = historico_de_ingestao_de_carga(ingestion_log_path)

    silver_records: list[dict[str, Any]] = []
    classified_documents: list[dict[str, Any]] = []

    queue = criar_fila_processamento(context)

    normal_count = sum(1 for _, mode, _, _ in queue if mode == "incremental")
    reprocess_count = sum(1 for _, mode, _, _ in queue if mode == "reprocess")

    logger.info(
        "Iniciando processamento de %s fichas (%s normais, %s reprocessamento).",
        len(queue),
        normal_count,
        reprocess_count,
    )

    try:
        pd_faixas = ler_json(context.control_file("pd_faixas"))
        logger.info("Faixas de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_faixas.")
        raise

    try:
        pd_transform_rules = ler_json(
            context.control_file("pd_transform_rules")
        )
        logger.info("Regras de transformação de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_transform_rules.")
        raise

    # Processa os arquivos da fila
    for source_file, load_mode, processed_dir, rejected_dir in queue:
        result = processar_arquivo_individual(
            source_file=source_file,
            load_mode=load_mode,
            processed_dir=processed_dir,
            rejected_dir=rejected_dir,
            context=context,
            layouts=layouts,
            required_fields=required_fields,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            history=history,
            ingestion_log_path=ingestion_log_path,
            logger=logger,
            run_id=run_id,
            quality_rules=quality_rules,
        )

        if result:
            silver_records.append(result["silver_record"])
            classified_documents.append(result["classified_document"])

    # Gravação na Camada Silver e Arquivo de Controle
    silver_output_dir = context.path("silver_fichas_consumidores_extraidas")
    docs_output_dir = context.path("silver_documentos_classificados")

    if silver_records:
        mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
            records=silver_records,
            output_dir=silver_output_dir,
            filename="fichas_consumidores_extraidas.csv",
            business_keys=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA"],
        )

    if classified_documents:
        escrever_conjunto_de_dados_silver(
            records=classified_documents,
            output_dir=docs_output_dir,
            filename=f"documentos_classificados__{run_id}",
        )

    summary = {
        "run_id": run_id,
        "arquivos_recebidos": len(queue),
        "arquivos_normais": normal_count,
        "arquivos_reprocessamento": reprocess_count,
        "registros_silver": len(silver_records),
        "documentos_classificados": len(classified_documents),
    }

    logger.info("Resumo do processamento: %s", summary)
    return summary
```


---
## src\control\logger.py
Linhas: 34
Classes: -
Funções: obter_logger
```python
"""Configuração padronizada de loggers do sistema BDC."""

from __future__ import annotations

import logging
from pathlib import Path


def obter_logger(name: str, file_path: str | Path) -> logging.Logger:
    """Cria ou devolve um logger com saída em arquivo e console."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    target = Path(file_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(target, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger

```


---
## src\domain\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\auditoria\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\auditoria\servico_auditoria.py
Linhas: 162
Classes: -
Funções: registrar_inicio_pipeline, registrar_fim_pipeline, registrar_documento, registrar_linhagem_campos
```python
"""Serviços de Auditoria do Pipeline (§11.5 — Tabelas de Controle).

Registra cada execução do pipeline (ctl_run_pipeline) e cada documento
processado (ctl_documento) em tabelas persistentes.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from storage.escrever_dados import escrever_conjunto_de_dados_silver


LOGGER = logging.getLogger("bdc.auditoria")


# ==============================================================================
# ctl_run_pipeline — Uma linha por execução do pipeline
# ==============================================================================
def registrar_inicio_pipeline(
    run_id: str,
    etapas_planejadas: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o início de uma execução do pipeline."""
    registro = {
        "RUN_ID": run_id,
        "DT_INICIO": datetime.now().isoformat(timespec="seconds"),
        "DT_FIM": None,
        "STATUS_GERAL": "EM_EXECUCAO",
        "TOTAL_ETAPAS": etapas_planejadas,
        "ETAPAS_OK": 0,
        "ETAPAS_FALHA": 0,
        "VERSAO_SISTEMA": "BDC_v06",
    }
    LOGGER.info("Pipeline iniciado (run_id=%s).", run_id)
    return registro


def registrar_fim_pipeline(
    registro_inicio: dict[str, Any],
    etapas_ok: int,
    etapas_falha: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o fim de uma execução do pipeline e persiste em ctl_run_pipeline."""
    registro = registro_inicio.copy()
    registro["DT_FIM"] = datetime.now().isoformat(timespec="seconds")
    registro["STATUS_GERAL"] = "SUCESSO" if etapas_falha == 0 else "PARCIAL"
    registro["ETAPAS_OK"] = etapas_ok
    registro["ETAPAS_FALHA"] = etapas_falha

    control_dir.mkdir(parents=True, exist_ok=True)

    # Append-only: cada execução é uma nova linha no arquivo de controle
    ctl_path = control_dir / "ctl_run_pipeline.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    csv_path = control_dir / "ctl_run_pipeline.csv"
    df_combined.to_csv(csv_path, index=False, encoding="utf-8-sig", sep=";")

    LOGGER.info(
        "Pipeline finalizado (run_id=%s). Status=%s. OK=%d, Falha=%d.",
        registro["RUN_ID"], registro["STATUS_GERAL"],
        etapas_ok, etapas_falha,
    )
    return registro


# ==============================================================================
# ctl_documento — Uma linha por documento processado
# ==============================================================================
def registrar_documento(
    documento_id: str,
    run_id: str,
    arquivo_origem: str,
    hash_arquivo: str | None,
    tipo_ficha: str,
    status_classificacao: str,
    status_extracao: str,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra um documento processado na tabela ctl_documento (append-only)."""
    registro = {
        "DOCUMENTO_ID": documento_id,
        "RUN_ID": run_id,
        "ARQUIVO_ORIGEM": arquivo_origem,
        "HASH_ARQUIVO": hash_arquivo,
        "TIPO_FICHA": tipo_ficha,
        "STATUS_CLASSIFICACAO": status_classificacao,
        "STATUS_EXTRACAO": status_extracao,
        "DT_PROCESSAMENTO": datetime.now().isoformat(timespec="seconds"),
    }

    control_dir.mkdir(parents=True, exist_ok=True)

    ctl_path = control_dir / "ctl_documento.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    LOGGER.info(
        "Documento registrado: %s (tipo=%s, status=%s).",
        documento_id, tipo_ficha, status_extracao,
    )
    return registro


# ==============================================================================
# ctl_campo_origem — Uma linha por campo extraído (Linhagem)
# ==============================================================================
def registrar_linhagem_campos(
    documento_id: str,
    run_id: str,
    campos_metadata: list[dict[str, Any]],
    control_dir: Path,
) -> None:
    """Registra a linhagem (aba, célula, método) de cada campo extraído."""
    if not campos_metadata:
        return

    registros = []
    dt_proc = datetime.now().isoformat(timespec="seconds")
    for cm in campos_metadata:
        registros.append({
            "DOCUMENTO_ID": documento_id,
            "RUN_ID": run_id,
            "CAMPO": cm.get("campo"),
            "ABA_ORIGEM": cm.get("aba_origem"),
            "CELULA_ORIGEM": cm.get("celula_origem"),
            "METODO_EXTRACAO": cm.get("metodo"),
            "VALOR_EXTRAIDO": str(cm.get("valor"))[:255] if cm.get("valor") is not None else None,
            "DT_PROCESSAMENTO": dt_proc,
        })

    control_dir.mkdir(parents=True, exist_ok=True)
    ctl_path = control_dir / "ctl_campo_origem.parquet"
    
    df_new = pd.DataFrame(registros)
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_parquet(ctl_path, index=False)
    LOGGER.debug("Registrada linhagem de %d campos para documento %s.", len(registros), documento_id)

```


---
## src\domain\contrapartes\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\contrapartes\segmentacao.py
Linhas: 50
Classes: -
Funções: definir_segmento_metodologico
```python
"""Segmentação metodológica da contraparte para cálculo de PD."""

from __future__ import annotations

from typing import Any

from silver.normalizadores import normalizar_string, normalizar_float


def definir_segmento_metodologico(
    registro: dict[str, Any],
) -> str:
    """Define o segmento metodológico da contraparte."""
    tipo_ficha = normalizar_string(
        registro.get("TIPO_FICHA"),
        upper=True,
    )
    
    if tipo_ficha == "COMERCIALIZADORA":
        tipo_comercializadora = normalizar_string(
            registro.get("TIPO_COMERCIALIZADORA"),
            upper=True,
        )
        if tipo_comercializadora == "CPURA":
            return "CPURA"

        if tipo_comercializadora == "CGRUPO":
            return "CGRUPO"

        raise ValueError(
            "Comercializadora sem TIPO_COMERCIALIZADORA válido."
        )

    if tipo_ficha == "CONSUMIDOR":
        # Extrai o volume de enquadramento (em MWm)
        volume_mwm = normalizar_float(registro.get("VOLUME_ENQUADRAMENTO_MWM"))
        
        # Critério de Aceite: Consumidor sem volume retorna NAO_ENQUADRADO
        if volume_mwm is None:
            return "NAO_ENQUADRADO"
            
        # Critério de Aceite: Bifurcação baseada no limite de 5 MWm
        if volume_mwm >= 5.0:
            return "CONSUMIDOR_GT_5"
        else:
            return "CONSUMIDOR_LE_5"

    raise ValueError(
        f"TIPO_FICHA inválido para segmentação: {tipo_ficha!r}"
    )
```


---
## src\domain\contrapartes\servico_dim_contraparte.py
Linhas: 87
Classes: -
Funções: criar_dim_contraparte
```python
"""Serviço de consolidação da Dimensão de Contraparte."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def criar_dim_contraparte(
    context: AppContext, 
    df_silver_receita: pd.DataFrame, 
    df_silver_segmentacao: pd.DataFrame,
    df_silver_salesforce_account: pd.DataFrame = None,
    df_silver_fichas: pd.DataFrame = None
) -> dict[str, Any]:
    run_id = f"DIM_CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.gold.dim_contraparte")

    if df_silver_receita.empty:
        df_silver_receita = pd.DataFrame(columns=["CNPJ", "SITUACAO_CADASTRAL", "NATUREZA_JURIDICA", "CNAE_PRINCIPAL"])
    if df_silver_segmentacao.empty:
        df_silver_segmentacao = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"])

    df_silver_receita["CNPJ"] = df_silver_receita["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
    df_silver_segmentacao["CNPJ"] = df_silver_segmentacao["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)

    # 1. Junta Receita + Segmentação
    df_dim = pd.merge(df_silver_receita, df_silver_segmentacao, on="CNPJ", how="outer")

    # 2. Resgata Identidade das Fichas
    if df_silver_fichas is not None and not df_silver_fichas.empty:
        df_fichas = df_silver_fichas.copy()
        df_fichas["CNPJ"] = df_fichas["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
        df_fichas["NOME_FICHA"] = df_fichas.get("EMPRESA", None)
        df_fichas["SIGLA_FICHA"] = df_fichas.get("SIGLA", None)
        
        # Pega o nome mais recente caso haja múltiplas fichas
        col_sort = "DT_PROCESSAMENTO" if "DT_PROCESSAMENTO" in df_fichas.columns else "CNPJ"
        df_id_fichas = df_fichas.sort_values(col_sort).drop_duplicates("CNPJ", keep="last")[["CNPJ", "NOME_FICHA", "SIGLA_FICHA"]]
        df_dim = pd.merge(df_dim, df_id_fichas, on="CNPJ", how="outer")
    else:
        df_dim["NOME_FICHA"] = None
        df_dim["SIGLA_FICHA"] = None

    # 3. Integra Salesforce (NOME e SIGLA)
    if df_silver_salesforce_account is not None and not df_silver_salesforce_account.empty:
        df_sf = df_silver_salesforce_account.copy()
        df_sf["CNPJ"] = df_sf["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
        sf_cols = {"CNPJ": "CNPJ", "Name": "NOME_SF", "Sigla__c": "SIGLA_SF"}
        df_sf_id = df_sf[[c for c in sf_cols.keys() if c in df_sf.columns]].rename(columns=sf_cols)
        df_sf_id = df_sf_id.drop_duplicates(subset=["CNPJ"], keep="last")
        df_dim = pd.merge(df_dim, df_sf_id, on="CNPJ", how="outer")
    else:
        df_dim["NOME_SF"] = None
        df_dim["SIGLA_SF"] = None

    # Garante que as colunas existam mesmo se as bases originais não as tiverem
    for col_safe in ["NOME_SF", "SIGLA_SF", "NOME_FICHA", "SIGLA_FICHA"]:
        if col_safe not in df_dim.columns:
            df_dim[col_safe] = None

    # 4. COALESCE (Salesforce tem prioridade, Ficha é o Fallback)
    df_dim["NOME"] = df_dim["NOME_SF"].combine_first(df_dim["NOME_FICHA"])
    df_dim["SIGLA"] = df_dim["SIGLA_SF"].combine_first(df_dim["SIGLA_FICHA"])

    df_dim = df_dim.dropna(subset=["CNPJ"])
    df_dim["CNPJ_RAIZ"] = df_dim["CNPJ"].str[:8]
    df_dim["SITUACAO_CADASTRAL"] = df_dim["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADO")
    df_dim["SEGMENTO_METODOLOGICO"] = df_dim["SEGMENTO_METODOLOGICO"].fillna("NAO_ENQUADRADO")

    schema_dim = {
        "CNPJ": "CNPJ", "NOME": "NOME", "SIGLA": "SIGLA", "CNPJ_RAIZ": "CNPJ_RAIZ", 
        "SITUACAO_CADASTRAL": "SITUACAO_CADASTRAL", "CNAE_PRINCIPAL": "SETOR", 
        "SEGMENTO_METODOLOGICO": "SEGMENTO_METODOLOGICO"
    }
    
    df_final = df_dim[list(schema_dim.keys())].rename(columns=schema_dim).copy()
    
    relational_dir = context.path("relational_dimensions")
    relational_dir.mkdir(parents=True, exist_ok=True)
    escrever_conjunto_de_dados_silver(df_final.to_dict(orient="records"), relational_dir, f"dim_contraparte_{run_id}")
    df_final.to_parquet(relational_dir / "dim_contraparte.parquet", index=False)

    logger.info("Dimensão Contraparte construída com COALESCE. Registros: %d", len(df_final))
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}
```


---
## src\domain\credito\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\credito\ead_engine.py
Linhas: 64
Classes: -
Funções: calcular_ead
```python
"""Motor de Exposure at Default (EAD).

feat(T3.2.1): Adicionados fator de conversão parametrizado e rastreabilidade
com calculo_id e config_snapshot_id.
Ref: §6.7 (Exposição), §7.1, §11.2 (Identificadores) do Planejamento Funcional.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import uuid4


def calcular_ead(
    mtm_positivo_total: float | None,
    fator_conversao: float = 1.0,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Cálculo de EAD baseado na exposição positiva de MtM.

    Regra: EAD = max(MtM favorável à Copel, 0) × fator_conversao (§6.7).

    Args:
        mtm_positivo_total: MtM positivo consolidado por contraparte.
        fator_conversao: Fator de conversão de crédito (CCF), default 1.0.
            Deve ser lido de config (ex: config["ead"]["fator_conversao"]).
        config: Dicionário de configuração para snapshot de rastreabilidade (§11.2).

    Returns:
        Dict com calculo_id, ead_valor, config_snapshot_id e metadados.
    """
    calculo_id = f"EAD_{uuid4().hex[:12]}"

    # Snapshot da configuração usada no cálculo (§11.2)
    config_usada = {"fator_conversao": fator_conversao}
    config_snapshot_id = hashlib.sha256(
        json.dumps(config_usada, sort_keys=True).encode()
    ).hexdigest()[:16]

    if mtm_positivo_total is None:
        return {
            "calculo_id": calculo_id,
            "ead_valor": None,
            "fator_conversao": fator_conversao,
            "config_snapshot_id": config_snapshot_id,
            "dt_calculo": datetime.now().isoformat(timespec="seconds"),
            "status": "SEM_DADOS_MTM",
        }

    ead_valor = max(float(mtm_positivo_total), 0.0) * fator_conversao

    return {
        "calculo_id": calculo_id,
        "ead_valor": ead_valor,
        "mtm_positivo_input": float(mtm_positivo_total),
        "fator_conversao": fator_conversao,
        "config_snapshot_id": config_snapshot_id,
        "dt_calculo": datetime.now().isoformat(timespec="seconds"),
        "status": "CALCULADO",
    }
```


---
## src\domain\credito\lgd_engine.py
Linhas: 90
Classes: -
Funções: calcular_lgd
```python
"""Motor de Loss Given Default (LGD).

feat(T3.3.1): Adicionados lookup de LGD bruta por segmento via config e
rastreabilidade com calculo_id.
Ref: §6.8, §7.1, Apêndice C do Planejamento Funcional.

Nota: A redução por garantias é recebida como parâmetro (cobertura_garantias).
A integração com a base real de garantias é um TODO — quando disponível,
o percentual será calculado automaticamente a partir de garantias_service.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import uuid4

# LGD bruta padrão por segmento metodológico (§6.8)
# Estes valores devem migrar para config.json quando homologados pelo negócio.
LGD_BRUTA_POR_SEGMENTO: dict[str, float] = {
    "CPURA": 0.45,
    "CGRUPO": 0.45,
    "CONSUMIDOR_GT_5": 0.45,
    "CONSUMIDOR_LE_5": 0.75,
}


def calcular_lgd(
    segmento: str,
    cobertura_garantias: float = 0.0,
    lgd_bruta_override: float | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Cálculo da LGD líquida após mitigação por garantias.

    Fórmula: LGD_liquida = LGD_bruta × (1 - cobertura_garantias) (§6.8).

    Args:
        segmento: Segmento metodológico (CPURA, CGRUPO, etc.).
        cobertura_garantias: Percentual de cobertura de garantias elegíveis [0, 1].
            Default 0.0 — TODO: será alimentado automaticamente pela base de garantias.
        lgd_bruta_override: Se informado, sobrescreve o lookup por segmento.
        config: Dict de configuração para lookup customizado.

    Returns:
        Dict rastreável com calculo_id, lgd_bruta, lgd_liquida e metadados.
    """
    calculo_id = f"LGD_{uuid4().hex[:12]}"

    # Lookup de LGD bruta por segmento (§6.8)
    if lgd_bruta_override is not None:
        lgd_bruta = lgd_bruta_override
        fonte_lgd_bruta = "OVERRIDE"
    elif config and "lgd_bruta_por_segmento" in config:
        lgd_bruta = config["lgd_bruta_por_segmento"].get(segmento, LGD_BRUTA_POR_SEGMENTO.get(segmento, 0.45))
        fonte_lgd_bruta = "CONFIG"
    else:
        lgd_bruta = LGD_BRUTA_POR_SEGMENTO.get(segmento, 0.45)
        fonte_lgd_bruta = "PADRAO_SISTEMA"

    # Trava matemática para não gerar LGD negativa (§6.8)
    cobertura_efetiva = max(0.0, min(float(cobertura_garantias), 1.0))

    lgd_liquida = lgd_bruta * (1.0 - cobertura_efetiva)

    # Snapshot da configuração usada (§11.2)
    config_usada = {
        "segmento": segmento,
        "lgd_bruta": lgd_bruta,
        "fonte_lgd_bruta": fonte_lgd_bruta,
        "cobertura_garantias": cobertura_efetiva,
    }
    config_snapshot_id = hashlib.sha256(
        json.dumps(config_usada, sort_keys=True).encode()
    ).hexdigest()[:16]

    return {
        "calculo_id": calculo_id,
        "segmento": segmento,
        "lgd_bruta": lgd_bruta,
        "fonte_lgd_bruta": fonte_lgd_bruta,
        "cobertura_garantias": cobertura_efetiva,
        "lgd_liquida": lgd_liquida,
        "config_snapshot_id": config_snapshot_id,
        "dt_calculo": datetime.now().isoformat(timespec="seconds"),
        "status": "CALCULADO",
    }
```


---
## src\domain\credito\pd_base.py
Linhas: 43
Classes: -
Funções: calcular_pd_base
```python
"""Cálculo ou leitura da PD base."""

from __future__ import annotations

from typing import Any

from silver.normalizadores import normalizar_float
from domain.credito.pd_exceptions import PdInputValidationError


def calcular_pd_base(
    registro: dict[str, Any],
    segmento_pd: str,
) -> float:
    """Calcula ou lê a PD base do registro."""
    valor = registro.get("PROBABILIDADE_DEFAULT")
    pd_base = normalizar_float(valor)
    
    if segmento_pd == "CONSUMIDOR_LE_5":
        # Para consumidores abaixo de 5 MWm, a PD base não é utilizada
        return 0.0
    
    valor = registro.get("PROBABILIDADE_DEFAULT")

    if pd_base is None:
        raise PdInputValidationError(
            f"Registro sem PROBABILIDADE_DEFAULT para {segmento_pd}."
        )

    if pd_base < 0:
        raise PdInputValidationError(
            f"PD base negativa: {pd_base}"
        )

    if pd_base > 1:
        pd_base = pd_base / 100.0

    if pd_base > 1:
        raise PdInputValidationError(
            f"PD base fora do intervalo após normalização: {pd_base}"
        )

    return pd_base

```


---
## src\domain\credito\pd_consumidor_gt5.py
Linhas: 121
Classes: -
Funções: _inv_t_aproximado, _normalize_pd_input, calcular_pd_final_consumidor_gt5
```python
"""Transformação da PD para consumidores acima de 5 MWm."""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

from domain.credito.pd_exceptions import (
    PdCalculationError,
    PdConfigurationError,
)


def _inv_t_aproximado(prob: float, df: float) -> float:
    """Aproxima o quantil da t de Student a partir do quantil normal."""
    if not 0 < prob < 1:
        raise PdCalculationError(
            f"Probabilidade inválida para inversa t: {prob!r}"
        )

    z = NormalDist().inv_cdf(prob)

    g1 = (z**3 + z) / (4 * df)
    g2 = (5 * z**5 + 16 * z**3 + 3 * z) / (96 * (df**2))
    g3 = (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * (df**3))

    return z + g1 + g2 + g3


def _normalize_pd_input(
    value: float,
    normalize_percent_if_gt_1: bool,
) -> float:
    q = float(value)
    if normalize_percent_if_gt_1 and q > 1:
        q = q / 100.0
    return q


def calcular_pd_final_consumidor_gt5(
    registro: dict[str, Any],
    pd_base: float,
    rating_final: str,
    pd_min: float,
    pd_max: float,
    regras_segmento: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada para consumidor acima de 5 MWm."""
    try:
        regras_pd = regras_segmento["pd_final_rules"]
        metodo = str(regras_pd.get("method", "")).strip().lower()

        if metodo != "t_dist_logistic":
            raise PdConfigurationError(
                f"Método inválido para CONSUMIDOR_GT_5: {metodo!r}"
            )

        df = float(regras_pd["df"])
        scale = float(regras_pd["scale"])
        eps = float(regras_pd["eps"])
        normalize_percent_if_gt_1 = bool(
            regras_pd.get("normalize_input_percent_if_gt_1", True)
        )

        q = _normalize_pd_input(
            value=float(pd_base),
            normalize_percent_if_gt_1=normalize_percent_if_gt_1,
        )

        q_cap = min(1 - eps, max(eps, q))

        z_t = _inv_t_aproximado(q_cap, df)
        z = scale * z_t
        u = 1.0 / (1.0 + math.exp(-z))

        pd_final = pd_min + u * (pd_max - pd_min)

        resultado = {
            "RATING_FINAL": rating_final,
            "PD_BASE": pd_base,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": pd_final,
            "PD_METODO": "T_DIST_LOGISTIC",
            "PD_Q_NORMALIZADA": q,
            "PD_Q_CAP": q_cap,
            "PD_Z_T": z_t,
            "PD_Z_ESCALADO": z,
            "PD_U_INTERPOLACAO": u,
        }

        if logger is not None:
            logger.info(
                "PD ajustada CONSUMIDOR_GT_5 calculada. "
                "CNPJ=%s RATING=%s PD_BASE=%s Q=%s Q_CAP=%s "
                "PD_MIN=%s PD_MAX=%s Z_T=%s Z=%s U=%s PD_FINAL=%s",
                registro.get("CNPJ"),
                rating_final,
                pd_base,
                q,
                q_cap,
                pd_min,
                pd_max,
                z_t,
                z,
                u,
                pd_final,
            )

        return resultado

    except Exception as exc:
        if isinstance(exc, (PdCalculationError, PdConfigurationError)):
            raise
        raise PdCalculationError(
            "Falha no cálculo da PD ajustada de CONSUMIDOR_GT_5: "
            f"{exc}"
        ) from exc

```


---
## src\domain\credito\pd_cpura.py
Linhas: 282
Classes: -
Funções: _clamp, _obter_score_total, _obter_faixa_score_rating, _obter_estabilizacao, _calcular_score_truncado, _calcular_posicao_relativa, _calcular_pd_bruta, _estabilizar_pd, calcular_pd_final_cpura
```python
"""Transformação de PD para comercializadoras puras."""

from __future__ import annotations

import math
from typing import Any

from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _clamp(valor: float, minimo: float, maximo: float) -> float:
    """Restringe valor ao intervalo informado."""
    return max(min(valor, maximo), minimo)


def _obter_score_total(registro: dict[str, Any]) -> float:
    """Obtém o score total S do registro."""
    score_total = registro.get("SCORE_TOTAL")

    if score_total is None:
        raise PdInputValidationError(
            "Registro sem SCORE_TOTAL para cálculo de PD de CPURA."
        )

    try:
        score_total = float(score_total)
    except (TypeError, ValueError) as exc:
        raise PdInputValidationError(
            f"SCORE_TOTAL inválido: {score_total!r}"
        ) from exc

    if score_total < 0 or score_total > 10:
        raise PdInputValidationError(
            f"SCORE_TOTAL fora do intervalo esperado [0, 10]: {score_total}"
        )

    return score_total


def _obter_faixa_score_rating(
    rating_final: str,
    score_faixas: dict[str, dict[str, float]],
) -> tuple[float, float]:
    """Obtém a faixa de score do rating."""
    if not score_faixas:
        raise PdConfigurationError(
            "Configuração 'score_faixas' não informada para CPURA."
        )

    if rating_final not in score_faixas:
        raise PdConfigurationError(
            f"Rating inválido para CPURA: {rating_final}"
        )

    faixa = score_faixas[rating_final]

    if "min" not in faixa or "max" not in faixa:
        raise PdConfigurationError(
            f"Faixa de score inválida para rating {rating_final}."
        )

    try:
        score_min = float(faixa["min"])
        score_max = float(faixa["max"])
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            f"Faixa de score não numérica para rating {rating_final}."
        ) from exc

    if score_min > score_max:
        raise PdConfigurationError(
            f"Faixa de score inválida para rating {rating_final}: min > max."
        )

    return score_min, score_max


def _obter_estabilizacao(
    cpura_config: dict[str, Any],
) -> tuple[float, float, float]:
    """Obtém os parâmetros de estabilização numérica."""
    estabilizacao = cpura_config.get("estabilizacao")

    if not isinstance(estabilizacao, dict):
        raise PdConfigurationError(
            "Bloco 'estabilizacao' ausente ou inválido em cpura_config."
        )

    try:
        epsilon = float(estabilizacao["epsilon"])
        z_min = float(estabilizacao["z_min"])
        z_max = float(estabilizacao["z_max"])
    except KeyError as exc:
        raise PdConfigurationError(
            f"Parâmetro de estabilização ausente: {exc}"
        ) from exc
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            "Parâmetros de estabilização inválidos."
        ) from exc

    if epsilon <= 0 or epsilon >= 0.5:
        raise PdConfigurationError(
            f"Epsilon inválido para estabilização: {epsilon}"
        )

    if z_min > z_max:
        raise PdConfigurationError(
            f"Intervalo de logit inválido: z_min={z_min}, z_max={z_max}"
        )

    return epsilon, z_min, z_max


def _calcular_score_truncado(
    score_total: float,
    score_min: float,
    score_max: float,
) -> float:
    """Aplica truncamento do score dentro da faixa do rating."""
    return _clamp(score_total, score_min, score_max)


def _calcular_posicao_relativa(
    score_truncado: float,
    score_min: float,
    score_max: float,
) -> float:
    """Calcula a posição relativa intra-rating."""
    if score_max == score_min:
        return 0.0

    u = (score_max - score_truncado) / (score_max - score_min)
    return _clamp(u, 0.0, 1.0)


def _calcular_pd_bruta(
    pd_min: float,
    pd_max: float,
    posicao_relativa: float,
) -> float:
    """Interpola a PD bruta dentro da faixa do rating."""
    pd_bruta = pd_min + posicao_relativa * (pd_max - pd_min)
    return _clamp(pd_bruta, 0.0, 1.0)


def _estabilizar_pd(
    pd_bruta: float,
    epsilon: float,
    z_min: float,
    z_max: float,
) -> tuple[float, float, float]:
    """Aplica estabilização numérica via logit."""
    p = _clamp(pd_bruta, epsilon, 1.0 - epsilon)
    z = math.log(p / (1.0 - p))
    z_truncado = _clamp(z, z_min, z_max)
    pd_final = 1.0 / (1.0 + math.exp(-z_truncado))
    return p, z_truncado, pd_final


def calcular_pd_final_cpura(
    registro: dict[str, Any],
    pd_base: float,
    rating_final: str,
    pd_min: float,
    pd_max: float,
    cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD final de CPURA por interpolação intra-rating."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo de PD final CPURA. "
                "CNPJ=%s rating=%s pd_min=%s pd_max=%s",
                registro.get("CNPJ"),
                rating_final,
                pd_min,
                pd_max,
            )

        if not cpura_config:
            raise PdConfigurationError(
                "Configuração de CPURA não informada."
            )

        if pd_min < 0 or pd_max < 0 or pd_min > 1 or pd_max > 1:
            raise PdInputValidationError(
                f"Faixa de PD inválida: pd_min={pd_min}, pd_max={pd_max}"
            )

        if pd_min > pd_max:
            raise PdInputValidationError(
                f"Faixa de PD inválida: pd_min > pd_max "
                f"({pd_min} > {pd_max})"
            )

        score_total = _obter_score_total(registro)
        score_faixas = cpura_config.get("score_faixas", {})
        score_min, score_max = _obter_faixa_score_rating(
            rating_final=rating_final,
            score_faixas=score_faixas,
        )
        epsilon, z_min, z_max = _obter_estabilizacao(cpura_config)

        score_truncado = _calcular_score_truncado(
            score_total=score_total,
            score_min=score_min,
            score_max=score_max,
        )

        posicao_relativa = _calcular_posicao_relativa(
            score_truncado=score_truncado,
            score_min=score_min,
            score_max=score_max,
        )

        pd_bruta = _calcular_pd_bruta(
            pd_min=pd_min,
            pd_max=pd_max,
            posicao_relativa=posicao_relativa,
        )

        p_estabilizado, z_truncado, pd_final = _estabilizar_pd(
            pd_bruta=pd_bruta,
            epsilon=epsilon,
            z_min=z_min,
            z_max=z_max,
        )

        resultado = {
            "SCORE_TOTAL": score_total,
            "SCORE_MIN_RATING": score_min,
            "SCORE_MAX_RATING": score_max,
            "SCORE_TRUNCADO": score_truncado,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            "PD_PERCENTIL_INTERNO": posicao_relativa,
            "PD_BRUTA": pd_bruta,
            "PD_ESTABILIZADA": p_estabilizado,
            "PD_FINAL": pd_final,
            "PD_METODO": "INTERPOLACAO_INTRA_RATING_CPURA",
            "LOGIT_TRUNCADO": z_truncado,
        }

        if logger is not None:
            logger.info(
                "PD final CPURA calculada com sucesso. "
                "CNPJ=%s score_total=%s score_truncado=%s "
                "u=%s pd_bruta=%s pd_final=%s",
                registro.get("CNPJ"),
                resultado["SCORE_TOTAL"],
                resultado["SCORE_TRUNCADO"],
                resultado["PD_PERCENTIL_INTERNO"],
                resultado["PD_BRUTA"],
                resultado["PD_FINAL"],
            )

        return resultado

    except (PdInputValidationError, PdConfigurationError):
        if logger is not None:
            logger.exception(
                "Erro controlado no cálculo de PD final CPURA. "
                "CNPJ=%s rating=%s",
                registro.get("CNPJ"),
                rating_final,
            )
        raise

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha inesperada no cálculo de PD final CPURA. "
                "CNPJ=%s rating=%s",
                registro.get("CNPJ"),
                rating_final,
            )
        raise

```


---
## src\domain\credito\score_qualitativo.py
Linhas: 161
Classes: -
Funções: _obter_nota_auditoria, _obter_peso_nota, calcular_score_qualitativo_cpura
```python
"""Cálculo do score qualitativo para CPURA."""

from __future__ import annotations

from typing import Any

from silver.normalizadores import normalizar_string
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_nota_auditoria(
    auditor: Any,
    auditor_para_nota: dict[str, str],
) -> str:
    """Converte o auditor em nota qualitativa."""
    auditor_normalizado = normalizar_string(auditor, upper=True)

    if not auditor_normalizado:
        raise PdInputValidationError("AUDITOR não informado.")

    nota = auditor_para_nota.get(auditor_normalizado)

    if nota is None:
        raise PdInputValidationError(
            f"AUDITOR sem mapeamento qualitativo: {auditor!r}"
        )

    return nota


def _obter_peso_nota(
    nota: Any,
    nota_para_peso: dict[str, Any],
    nome_campo: str,
) -> float:
    """Obtém o peso numérico da nota qualitativa."""
    nota_normalizada = normalizar_string(nota, upper=True)

    if not nota_normalizada:
        raise PdInputValidationError(
            f"{nome_campo} não informada."
        )

    if nota_normalizada not in nota_para_peso:
        raise PdInputValidationError(
            f"{nome_campo} inválida: {nota!r}"
        )

    try:
        return float(nota_para_peso[nota_normalizada])
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            f"Peso inválido para nota {nota_normalizada}."
        ) from exc


def calcular_score_qualitativo_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score qualitativo de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando score qualitativo CPURA. CNPJ=%s",
                registro.get("CNPJ"),
            )

        nota_para_peso = score_cpura_config.get("nota_para_peso")
        pesos_qualitativos = score_cpura_config.get("pesos_qualitativos")
        auditor_para_nota = score_cpura_config.get("auditor_para_nota")

        if not isinstance(nota_para_peso, dict):
            raise PdConfigurationError(
                "Bloco 'nota_para_peso' ausente ou inválido."
            )

        if not isinstance(pesos_qualitativos, dict):
            raise PdConfigurationError(
                "Bloco 'pesos_qualitativos' ausente ou inválido."
            )

        if not isinstance(auditor_para_nota, dict):
            raise PdConfigurationError(
                "Bloco 'auditor_para_nota' ausente ou inválido."
            )

        nota_board = registro.get("NOTA_BOARD")
        nota_bureau = registro.get("NOTA_BUREAU")
        auditor = registro.get("AUDITOR")

        nota_auditoria = _obter_nota_auditoria(
            auditor,
            auditor_para_nota,
        )

        peso_board = _obter_peso_nota(
            nota_board,
            nota_para_peso,
            "NOTA_BOARD",
        )
        peso_bureau = _obter_peso_nota(
            nota_bureau,
            nota_para_peso,
            "NOTA_BUREAU",
        )
        peso_auditoria = _obter_peso_nota(
            nota_auditoria,
            nota_para_peso,
            "NOTA_AUDITORIA",
        )

        try:
            w_board = float(pesos_qualitativos["BOARD"])
            w_auditoria = float(pesos_qualitativos["AUDITORIA"])
            w_bureau = float(pesos_qualitativos["BUREAU"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Peso qualitativo ausente: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                "Pesos qualitativos inválidos."
            ) from exc

        score_qualitativo = (
            w_board * peso_board
            + w_auditoria * peso_auditoria
            + w_bureau * peso_bureau
        )

        resultado = {
            "NOTA_AUDITORIA": nota_auditoria,
            "PESO_BOARD": peso_board,
            "PESO_AUDITORIA": peso_auditoria,
            "PESO_BUREAU": peso_bureau,
            "SCORE_QUALITATIVO": score_qualitativo,
        }

        if logger is not None:
            logger.info(
                "Score qualitativo CPURA calculado. "
                "CNPJ=%s SCORE_QUALITATIVO=%s",
                registro.get("CNPJ"),
                score_qualitativo,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score qualitativo CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )
        raise

```


---
## src\domain\credito\servico_override.py
Linhas: 88
Classes: -
Funções: processar_solicitacao_override
```python
"""Serviço de Gestão de Overrides e Exceções (Módulo de Governança)."""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from domain.enums import StatusAprovacao
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def processar_solicitacao_override(context: AppContext) -> dict[str, Any]:
    run_id = f"OVR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.governanca.override")

    input_dir = context.path("entradas") / "overrides" / "pendentes"
    input_dir.mkdir(parents=True, exist_ok=True)

    arquivos = list(input_dir.glob("*.csv")) + list(input_dir.glob("*.xlsx"))
    if not arquivos:
        return {"run_id": run_id, "processados": 0, "status": "SEM_DADOS"}

    campos_obrigatorios = [
        "CNPJ", "TIPO_OVERRIDE", "VALOR_ANTES", "VALOR_DEPOIS",
        "JUSTIFICATIVA", "EVIDENCIA", "SOLICITANTE", "APROVADOR", "DATA_EXPIRACAO"
    ]

    processados = []
    hoje = datetime.now()

    for arquivo in arquivos:
        try:
            if arquivo.suffix == ".csv":
                df = pd.read_csv(arquivo, sep=";", dtype=str)
            else:
                df = pd.read_excel(arquivo, dtype=str)

            registros = df.to_dict(orient="records")

            for idx, solicitacao in enumerate(registros):
                valido = True
                for campo in campos_obrigatorios:
                    if campo not in solicitacao or pd.isna(solicitacao[campo]) or str(solicitacao[campo]).strip() == "":
                        logger.warning("Campo '%s' ausente na linha %d. Rejeitado.", campo, idx)
                        valido = False
                        break
                if not valido:
                    continue

                solicitante = str(solicitacao["SOLICITANTE"]).strip().upper()
                aprovador = str(solicitacao["APROVADOR"]).strip().upper()

                if solicitante == aprovador:
                    logger.warning("Conflito de Segregação (CNPJ %s): Solicitante = Aprovador.", solicitacao['CNPJ'])
                    continue

                expiracao = pd.to_datetime(solicitacao["DATA_EXPIRACAO"], errors="coerce")
                if pd.isna(expiracao) or expiracao < hoje:
                    logger.warning("Data de expiração inválida/passada (CNPJ %s).", solicitacao['CNPJ'])
                    continue

                registro = solicitacao.copy()
                registro["STATUS"] = StatusAprovacao.APROVADO.value
                registro["DATA_APROVACAO"] = hoje.isoformat(timespec="seconds")
                registro["RUN_ID"] = run_id
                processados.append(registro)

            target_dir = context.path("entradas") / "overrides" / "processados"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.rename(target_dir / arquivo.name)
            
        except Exception as e:
            logger.error("Erro no arquivo %s: %s", arquivo.name, e)
            target_dir = context.path("entradas") / "overrides" / "rejeitados"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.rename(target_dir / arquivo.name)

    if processados:
        silver_dir = context.path("silver") / "governanca_overrides"
        escrever_conjunto_de_dados_silver(
            records=processados,
            output_dir=silver_dir,
            filename=f"solicitacao_override_{run_id}"
        )

    logger.info("Overrides processados: %d.", len(processados))
    return {"run_id": run_id, "processados": len(processados), "status": "SUCESSO"}
```


---
## src\domain\enums.py
Linhas: 126
Classes: TipoFicha, LoadMode, StatusIngestao, StatusClassificacao, StatusExtracao, SegmentoMetodologico, TipoAnalise, SeveridadeAlerta, StatusGarantia, StatusAnalise, StatusDocumento, StatusAlerta, StatusAprovacao
Funções: -
```python
"""Domínios controlados e enumeradores do sistema BDC."""

from enum import Enum, unique


@unique
class TipoFicha(str, Enum):
    """Domínio para os tipos de fichas processadas."""
    COMERCIALIZADORA = "comercializadora"
    CONSUMIDOR = "consumidor"


@unique
class LoadMode(str, Enum):
    """Domínio para os modos de carga do orquestrador."""
    INCREMENTAL = "incremental"
    REPROCESS = "reprocess"


@unique
class StatusIngestao(str, Enum):
    """Domínio para o status de movimentação dos arquivos na camada Bronze."""
    INICIADO = "INICIADO"
    SUCESSO = "SUCESSO"
    ERRO = "ERRO"
    REJEITADO = "REJEITADO"


@unique
class StatusClassificacao(str, Enum):
    """Domínio para os resultados do motor de classificação de layouts."""
    CLASSIFICADO = "CLASSIFICADO"
    REJEITADO = "REJEITADO"
    NAO_CLASSIFICADO = "NAO_CLASSIFICADO"


@unique
class StatusExtracao(str, Enum):
    """Domínio detalhado para os estados de extração e validação técnica."""
    NAO_EXECUTADO = "NAO_EXECUTADO"
    SUCESSO = "SUCESSO"
    ERRO = "ERRO"
    ERRO_VALIDACAO = "ERRO_VALIDACAO"
    ERRO_DUPLICIDADE_HASH = "ERRO_DUPLICIDADE_HASH"
    ERRO_DUPLICIDADE_NEGOCIO = "ERRO_DUPLICIDADE_NEGOCIO"
    ERRO_PROCESSAMENTO = "ERRO_PROCESSAMENTO"
    ERRO_LAYOUT = "ERRO_LAYOUT"
    ERRO_SEM_CNPJ = "ERRO_SEM_CNPJ"
    ERRO_CNPJ_INVALIDO = "ERRO_CNPJ_INVALIDO"


@unique
class SegmentoMetodologico(str, Enum):
    """Domínio das segmentações metodológicas de crédito."""
    CPURA = "CPURA"
    CGRUPO = "CGRUPO"
    CONSUMIDOR_GT_5 = "CONSUMIDOR_GT_5"
    CONSUMIDOR_LE_5 = "CONSUMIDOR_LE_5"


@unique
class TipoAnalise(str, Enum):
    """Domínio para a origem ou tipo de análise gerada."""
    AUTOMATICA = "AUTOMATICA"
    MANUAL = "MANUAL"
    MANUAL_AJUSTADA = "MANUAL_AJUSTADA"


@unique
class SeveridadeAlerta(str, Enum):
    """Domínio para a classificação de alertas do sistema."""
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"
    
@unique
class StatusGarantia(str, Enum):
    """Domínio para os estados de vigência de garantias (§6.8)."""
    VIGENTE = "VIGENTE"
    PROXIMA_VENCIMENTO = "PROXIMA_VENCIMENTO"
    VENCIDA = "VENCIDA"
    CANCELADA = "CANCELADA"
    NAO_ELEGIVEL = "NAO_ELEGIVEL"


@unique
class StatusAnalise(str, Enum):
    """Domínio para o ciclo de vida de uma análise de crédito (§4.2, Apêndice A)."""
    VIGENTE = "VIGENTE"
    PROXIMA_VENCIMENTO = "PROXIMA_VENCIMENTO"
    VENCIDA = "VENCIDA"
    EM_RENOVACAO = "EM_RENOVACAO"
    SUSPENSA = "SUSPENSA"


@unique
class StatusDocumento(str, Enum):
    """Domínio para o estado de processamento de um documento/ficha (§4.2, Apêndice A)."""
    DESCOBERTO = "DESCOBERTO"
    EM_STAGING = "EM_STAGING"
    INGERIDO = "INGERIDO"
    CLASSIFICADO = "CLASSIFICADO"
    EXTRAIDO = "EXTRAIDO"
    VALIDADO = "VALIDADO"
    PUBLICADO = "PUBLICADO"
    PENDENTE = "PENDENTE"
    REJEITADO = "REJEITADO"


@unique
class StatusAlerta(str, Enum):
    """Domínio para os estados de resolução de alertas (§6.10)."""
    ABERTO = "ABERTO"
    EM_TRATAMENTO = "EM_TRATAMENTO"
    RESOLVIDO = "RESOLVIDO"
    IGNORADO = "IGNORADO"


@unique
class StatusAprovacao(str, Enum):
    """Domínio para o fluxo de aprovação de carga manual e overrides (§11.7)."""
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"
    EXPIRADO = "EXPIRADO"
```


---
## src\domain\fichas\extrator.py
Linhas: 505
Classes: -
Funções: analisar_data_com_seguranca, valor_extraido_limpo, _tipo_extraido_valido, busca_omnidirecional, extrair_registro, extrair_registro_do_vencedor, norm_tab
```python
# -*- coding: utf-8 -*-
"""Serviço de extração de dados dinâmico e omnidirecional das fichas Excel."""

from __future__ import annotations

import re
import math
import logging
import warnings
import openpyxl
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils.datetime import from_excel
from openpyxl.utils import get_column_letter
from common.excel import ler_celula

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

logger = logging.getLogger(__name__)

CUTOFF_DATE_LAYOUT_CHANGE = datetime(2025, 4, 30)

SMART_SEMANTIC_MAP = {
    "CNPJ": r"^\s*CNPJ\b(?!.*(?:BBCE|CONTROLADOR))",
    "SIGLA": r"SIGLA",
    "FCO": r"FCO|MARGEM\s*DE\s*FLUXO\s*DE\s*CAIXA",
    "PATRIMONIO_LIQUIDO": r"PATRIM[OÔ]NIO\s*L[IÍ]QUIDO",
    "LUCRO_LIQUIDO": r"LUCRO\s*L[IÍ]QUIDO|RESULTADO\s*L[IÍ]QUIDO|LUCRO/PREJUIZO DO EXERCICIO",
    "PROBABILIDADE_DEFAULT": r"PROBABILIDADE\s*DEFAULT|PD\b|PD\s*=",
    "DATA_DEMONSTRACAO_FINANCEIRA": r"DATA\s*DA\s*DEMONSTRA[CÇ][AÃ]O|DATA\s*BASE|DATA\s*DA\s*DF",
    "RECEITA_LIQUIDA": r"RECEITA\s*L[IÍ]QUIDA|VENDAS\s*L[IÍ]QUIDAS|ROL",
    "VENDAS_LIQUIDAS": r"VENDAS\s*L[IÍ]QUIDAS|ROL|RECEITA\s*OPERACIONAL\s*L[IÍ]QUIDA",
    "ATIVO_TOTAL": r"ATIVO\s*TOTAL",
    "PASSIVO_CIRCULANTE": r"PASSIVO\s*CIRCULANTE",
    "ATIVO_CIRCULANTE": r"ATIVO\s*CIRCULANTE",
    "LUCRO_BRUTO": r"LUCRO\s*BRUTO",
    "LAJIR": r"LAJIR|RESULTADO\s*OPERACIONAL",
    "LAIR": r"LAIR|LUCRO\s*ANTES\s*DO\s*IMPOSTO",
    "ATIVO_CIRCULANTE_FINANCEIRO": r"ATIVO\s*CIRCULANTE\s*FINANCEIRO",
    "PASSIVO_CIRCULANTE_FINANCEIRO": r"PASSIVO\s*CIRCULANTE\s*FINANCEIRO",
    "PASSIVO_NAO_CIRCULANTE_FINANCEIRO": r"PASSIVO\s*N[AÃ]O\s*CIRCULANTE\s*FINANCEIRO",
    "EMPRESA": r"EMPRESA|RAZ[AÃ]O\s*SOCIAL",
    "TIPO_COMERCIALIZADORA": r"TIPO\s*DE\s*COMERCIALIZADORA",
    "DATA_ADESAO_CCEE": r"DATA\s*DE\s*ADES[AÃ]O",
    "CODIGO_CCEE": r"C[OÓ]DIGO\s*CCEE",
    "DATA_CALCULO": r"DATA\s*DA\s*FICHA",
    "SCORE_BUREAU": r"SCORE\s*BUREAU|SCORE\b",
    "QUANTIDADE_RESTRITIVOS": r"QUANTIDADE\s*DE\s*RESTRITIVOS",
    "CAPITAL_SOCIAL": r"CAPITAL\s*SOCIAL",
    "LUCROS_ACUMULADOS": r"LUCROS\s*ACUMULADOS",
    "RESERVA_DE_LUCROS": r"RESERVA\s*DE\s*LUCROS",
    "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS": r"FLUXO\s*DE\s*CAIXA\s*OPERACIONAL|CAIXA\s*L[IÍ]QUIDO\s*GERADO",
    "AGENCIA": r"AG[EÊ]NCIA",
    "NOTA_CREDITO": r"NOTA\s*DE\s*CR[EÉ]DITO",
    "ROL": r"RECEITA\s*OPERACIONAL\s*L[IÍ]QUIDA|ROL",
    "AC_PC": r"AC\s*/\s*PC|ATIVO\s*CIRCULANTE\s*/\s*PASSIVO\s*CIRCULANTE",
    "AT_PT": r"AT\s*/\s*PT|ATIVO\s*TOTAL\s*/\s*PASSIVO\s*TOTAL",
    "MTM_TOTAL_PL": r"MTM\s*TOTAL\s*/\s*PL|MTM\s*/\s*PATRIM[OÔ]NIO",
    "DIVIDENDOS_JCP_LUCRO_LIQUIDO": r"\(?DIVIDENDOS\s*\+\s*JCP\)?\s*/\s*LUCRO\s*L[IÍ]QUIDO|DIVIDENDOS\s*E\s*JCP",
    "CAPITAL_CIRCULANTE_LIQUIDO": r"CAPITAL\s*CIRCULANTE\s*L[IÍ]QUIDO|CCL\b",
    "RESTRITIVOS": r"RESTRITIVOS|APONTAMENTOS\s*RESTRITIVOS",
    "CNAE": r"CNAE\b|C[OÓ]DIGO\s*DE\s*ATIVIDADE",
    "NATUREZA_JURIDICA": r"NATUREZA\s*JUR[IÍ]DICA",
    "ENDERECO": r"ENDERE[CÇ]O|LOGRADOURO",
    "ROA": r"ROA\b|RETORNO\s*SOBRE\s*ATIVO",
    "ROE": r"ROE\b|RETORNO\s*SOBRE\s*PATRIM[OÔ]NIO",
    "FCO_ROL": r"FCO\s*/\s*ROL|FLUXO\s*DE\s*CAIXA\s*/\s*RECEITA",
    "CNPJ_BBCE": r"CNPJ\s*BBCE",
    "RATING_COPEL": r"RATING\s*COPEL",
    "RATING_PUBLICO": r"RATING\s*P[UÚ]BLICO",
    "SCORE_QUANTITATIVO": r"SCORE\s*QUANTITATIVO",
    "SCORE_QUALITATIVO": r"SCORE\s*QUALITATIVO"
}

def analisar_data_com_seguranca(date_val: Any) -> Optional[datetime]:
    if isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, (int, float)):
        try:
            return from_excel(date_val)
        except Exception:
            return None
    if isinstance(date_val, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_val.strip(), fmt)
            except ValueError:
                pass
    return None

def valor_extraido_limpo(val: Any, data_type: Optional[str] = None) -> Any:
    """Higieniza o valor extraído e garante o casting correto."""
    if val is None:
        return None
    
    dt_str = str(data_type).lower() if data_type else ""
    
    if isinstance(val, str):
        s_upper = val.strip().upper()
        if not s_upper or s_upper.startswith("#") or s_upper in ("NAN", "NONE", "<NA>", "N/A", "NULL", "N/D", "-", "--"):
            return None

    if any(t in dt_str for t in ("float", "num", "dec", "int", "moeda", "percent", "taxa", "valor", "score")):
        if isinstance(val, (int, float)):
            if math.isnan(val) or math.isinf(val):
                return None
            return float(val)
        
        clean = str(val).strip()
        # Notação contábil negativa (1.500) -> -1.500
        if clean.startswith("(") and clean.endswith(")"):
            clean = "-" + clean[1:-1].strip()
        
        # Limpa tudo que não for dígito, vírgula, ponto ou sinal de menos (remove R$, $, %, letras)
        clean = re.sub(r"[^\d\,\.-]", "", clean)
        
        if not clean:
            return None
            
        # Resolução de pontuação (milhar vs decimal)
        last_comma = clean.rfind(",")
        last_dot = clean.rfind(".")
        
        try:
            if last_comma > last_dot:
                # Padrão Brasileiro: 1.500,50 -> 1500.50
                clean = clean.replace(".", "").replace(",", ".")
            elif last_dot > last_comma:
                # Padrão Americano: 1,500.50 -> 1500.50
                if "," in clean:
                    clean = clean.replace(",", "")
                else:
                    # Só tem ponto: "1.500" ou "1.5"
                    if clean.count(".") > 1:
                        # Vários pontos: "1.500.000" -> "1500000"
                        clean = clean.replace(".", "")
                    else:
                        # Exatamente um ponto. Se tiver 3 dígitos depois do ponto, no Brasil quase sempre é milhar se a origem for string suja de excel.
                        # Exceções: taxas ou percentuais (onde 1.500 pode ser 1.5%)
                        parts = clean.split(".")
                        if len(parts[1]) == 3 and not any(t in dt_str for t in ("percent", "taxa")):
                            clean = clean.replace(".", "")
            
            return float(clean)
        except ValueError:
            return None

    if any(t in dt_str for t in ("date", "data")):
        return analisar_data_com_seguranca(val)

    if isinstance(val, float) and val.is_integer():
        val = int(val) 
    return str(val).strip()

def _tipo_extraido_valido(val: Any, data_type: str, field_name: str = "") -> bool:
    if val is None:
        return False
        
    dt_str = str(data_type).lower() if data_type else ""
    fn_lower = field_name.lower()
    
    if any(t in dt_str for t in ("float", "num", "dec", "int", "moeda", "percent", "taxa", "valor", "score", "pd")):
        if not isinstance(val, (int, float)):
            return False
            
        if val > 10000000 and str(int(val)).startswith(("20", "31", "30", "01")):
            return False
            
        if val == 0.0 and any(k in fn_lower for k in ("ativo_total", "passivo_circulante", "vendas_liquidas")):
            return False
            
        return True

    if any(t in dt_str for t in ("date", "data")):
        return isinstance(val, datetime)
        
    if isinstance(val, str):
        v = val.lower().strip()
        if not v or v in ("tipo", "valor", "data", "descrição", "ajustado", "-", "0"):
            return False
            
        if len(v) > 60 and "endereco" not in fn_lower and "endereço" not in fn_lower:
            return False
            
        if fn_lower in ("auditor", "empresa", "sigla") and v.replace(".", "").replace(",", "").isdigit():
            return False
            
        if "agencia" in fn_lower or "agência" in fn_lower:
            if not any(k in v for k in ("fitch", "mood", "s&p", "sp", "standard")): 
                return False
                
        if "nota" in fn_lower or "rating" in fn_lower:
            if len(v) > 5 or any(k in v for k in ("menor", "qualidade", "classificação", "agência", "risco")): 
                return False
                
        if "auditor" in fn_lower:
            if len(v) > 40: return False
            
    return True

def busca_omnidirecional(workbook: openpyxl.workbook.workbook.Workbook, search_pattern: str, data_type: str, sheet_hint: str = None, field_name: str = "", grid_cache: Dict[str, List[Tuple]] = None, offset_col: int = None, offset_row: int = None) -> Tuple[Any, dict]:
    """
    Caçador Universal (Refatorado para Performance in-memory RAM GRID):
    Varre TODAS as abas do Excel atrás da Regex através de uma matriz em memória.
    """
    if grid_cache is None:
        grid_cache = {}

    try:
        regex = re.compile(search_pattern, re.IGNORECASE)
    except re.error:
        return None, {}

    sheet_names = workbook.sheetnames
    if sheet_hint:
        hint_clean = str(sheet_hint).replace(" ", "").lower()
        sheet_names = sorted(sheet_names, key=lambda x: 0 if hint_clean in x.replace(" ", "").lower() else 1)

    for sheet_name in sheet_names:
        if sheet_name not in grid_cache:
            ws = workbook[sheet_name]
            # Convert worksheet to in-memory grid
            grid_cache[sheet_name] = list(ws.iter_rows(min_row=1, max_row=150, min_col=1, max_col=30, values_only=True))
            
        grid = grid_cache[sheet_name]
        
        for r_idx, row_tuple in enumerate(grid):
            for c_idx, cell_value in enumerate(row_tuple):
                if cell_value and isinstance(cell_value, str):
                    if regex.search(cell_value.strip()):
                        # Alvos: aplica offset_col/row primeiro se existirem, depois os 6 colunas à direita e 2 linhas abaixo
                        targets = []
                        if offset_col is not None or offset_row is not None:
                            o_col = int(offset_col) if offset_col is not None else 0
                            o_row = int(offset_row) if offset_row is not None else 0
                            targets.append((r_idx + o_row, c_idx + o_col))
                            
                        default_targets = [(r_idx, c_idx + offset) for offset in range(1, 7)]
                        default_targets.extend([(r_idx + offset, c_idx) for offset in range(1, 3)])
                        
                        for dt in default_targets:
                            if dt not in targets:
                                targets.append(dt)
                        
                        for tr, tc in targets:
                            if 0 <= tr < len(grid) and 0 <= tc < len(grid[tr]):
                                raw_val = grid[tr][tc]
                                cleaned_val = valor_extraido_limpo(raw_val, data_type)
                                
                                if cleaned_val is not None and _tipo_extraido_valido(cleaned_val, data_type, field_name):
                                    col_letter = get_column_letter(tc + 1)
                                    coord = f"{col_letter}{tr + 1}"
                                    return cleaned_val, {
                                        "celula_origem": coord,
                                        "aba_origem": sheet_name,
                                        "metodo": "omnidirectional_regex"
                                    }
    return None, {}

def extrair_registro(workbook: openpyxl.workbook.workbook.Workbook, layout_schema: Dict[str, Any], master_catalog: Dict[str, Any] = None, grid_cache: Dict[str, List[Tuple]] = None, allow_semantic: bool = True) -> Tuple[Dict[str, Any], List[dict[str, Any]]]:
    extracted_data = {}
    metadata_list = []
    
    fields_to_extract = {}
    max_score = 0.0
    gates_to_check = []
    
    # 3. PROTEÇÃO AO LEGADO (Fallback)
    if master_catalog and "fields" in master_catalog:
        for mc_field, mc_config in master_catalog["fields"].items():
            if mc_config.get("nature") == "OBSERVED":
                fields_to_extract[mc_field] = dict(mc_config)
                max_score += float(mc_config.get("weight", 0))
                if mc_config.get("criticality") == "GATE_ENGINE":
                    gates_to_check.append(mc_field)
    else:
        # Fallback Consumidores
        field_map = layout_schema.get("field_map", {})
        fields_to_extract = dict(field_map)
        for sm_field in SMART_SEMANTIC_MAP.keys():
            if sm_field not in fields_to_extract:
                fields_to_extract[sm_field] = {}
        max_score = len(fields_to_extract) # each field weight = 1
        
    score_obtido = 0.0

    for field_name, field_config in fields_to_extract.items():
        data_type = field_config.get("data_type") or field_config.get("type")
        if not data_type:
            # Inferência de tipagem semântica para impedir que a busca omnidirecional aceite lixo (strings) no lugar de números
            fn_lower = field_name.lower()
            if any(t in fn_lower for t in ("ativo", "passivo", "lucro", "patrimonio", "capital", "venda", "receita", "lair", "lajir", "fco", "fluxo", "probabilidade", "pd", "rol", "reserva", "imposto", "resultado", "score", "ac_pc", "at_pt", "mtm", "dividendos")):
                data_type = "float"
            elif any(t in fn_lower for t in ("data", "dt")):
                data_type = "date"
            else:
                data_type = "string"
                
        # Dicionário de tradução para retrocompatibilidade com JSONs antigos
        LEGACY_ALIASES = {
            "FCO": ["SCORE_FCO_ROL", "FCO_ROL", "MARGEM_FLUXO_CAIXA"],
            "ROA": ["SCORE_ROA"],
            "ROE": ["SCORE_ROE"],
            "PATRIMONIO_LIQUIDO": ["PL", "TOTAL_PATRIMONIO_LIQUIDO"],
            "ATIVO_TOTAL_AJUSTADO": ["ATIVO_TOTAL", "TOTAL_ATIVOS"],
            "ATIVO_CIRCULANTE_AJUSTADO": ["ATIVO_CIRCULANTE"],
            "PASSIVO_CIRCULANTE_AJUSTADO": ["PASSIVO_CIRCULANTE"],
            "PASSIVO_NAO_CIRCULANTE_FINANCEIRO_AJUSTADO": ["PASSIVO_NAO_CIRCULANTE", "PASSIVO_N_CIRCULANTE"],
            "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS": ["FCO", "FLUXO_DE_CAIXA_OPERACIONAL"],
            "LUCRO_LIQUIDO": ["RESULTADO_LIQUIDO", "LUCRO_PREJUIZO"],
            "ROL": ["RECEITA_OPERACIONAL_LIQUIDA", "RECEITA_LIQUIDA"]
        }

        # 1. Tenta achar a configuração no layout pelo nome oficial novo
        layout_field_config = layout_schema.get("field_map", {}).get(field_name)
        
        # 2. Se não achou, tenta pelos nomes legados (Aliases)
        if not layout_field_config and field_name in LEGACY_ALIASES:
            for alias in LEGACY_ALIASES[field_name]:
                layout_field_config = layout_schema.get("field_map", {}).get(alias)
                if layout_field_config:
                    break
                    
        layout_field_config = layout_field_config or {}
        
        # 2. Resgata a topografia do layout correspondente
        sheet_hint = layout_field_config.get("sheet") or field_config.get("sheet")
        offset_col = layout_field_config.get("offset_col")
        offset_row = layout_field_config.get("offset_row")
        
        static_cell = layout_field_config.get("value_cell") or layout_field_config.get("cell") or field_config.get("value_cell") or field_config.get("cell")
        
        val = None
        meta = {
            "campo": field_name,
            "aba_origem": None,
            "celula_origem": None,
            "metodo": "falha_extracao",
            "valor": None
        }

        # 1. TENTA PRIMEIRO EXTRAÇÃO ESTÁTICA (STATIC FIRST)
        if static_cell and str(static_cell).strip() not in ("0", ""):
            try:
                # Usa a aba sugerida no JSON ou a ativa
                ws_estatico = workbook.active
                if sheet_hint:
                    hint_clean = str(sheet_hint).replace(" ", "").lower()
                    for aba_real in workbook.sheetnames:
                        if hint_clean in aba_real.replace(" ", "").lower():
                            ws_estatico = workbook[aba_real]
                            break

                raw_val, static_meta = ler_celula(ws_estatico, static_cell, return_meta=True)
                clean_val = valor_extraido_limpo(raw_val, data_type)
                if clean_val is not None and _tipo_extraido_valido(clean_val, data_type, field_name):
                    val = clean_val
                    meta.update({
                        "aba_origem": ws_estatico.title,
                        "celula_origem": static_cell,
                        "metodo": "estatico_layout",
                        "valor": val
                    })
            except Exception:
                pass

        # 2. SE ESTÁTICO FALHAR, TENTA BUSCA DINÂMICA IN-MEMORY (DYNAMIC FALLBACK)
        if val is None and allow_semantic:
            if master_catalog and "fields" in master_catalog:
                patterns = field_config.get("search_patterns")
                if patterns and isinstance(patterns, list) and len(patterns) > 0:
                    search_pattern = "|".join(patterns)
                else:
                    search_pattern = field_name.replace("_", r"\s*")
            else:
                search_pattern = SMART_SEMANTIC_MAP.get(field_name) or field_config.get("search_pattern")
                if not search_pattern:
                    search_pattern = field_name.replace("_", r"\s*")
                    
            val_dinamico, meta_inf = busca_omnidirecional(
                workbook, 
                search_pattern, 
                data_type, 
                sheet_hint, 
                field_name, 
                grid_cache,
                offset_col=offset_col,
                offset_row=offset_row
            )
            if val_dinamico is not None:
                val = val_dinamico
                meta.update({
                    "aba_origem": meta_inf.get("aba_origem"),
                    "celula_origem": meta_inf.get("celula_origem"),
                    "metodo": meta_inf.get("metodo", "omnidirectional_regex"),
                    "valor": val
                })

        extracted_data[field_name] = val
        if meta["metodo"] != "falha_extracao":
            metadata_list.append(meta)
            
        if val is not None:
            if master_catalog and "fields" in master_catalog:
                score_obtido += float(field_config.get("weight", 0))
            else:
                score_obtido += 1

    # Calcula a Integridade da Ficha
    score = (score_obtido / max_score) * 100 if max_score > 0 else 0
    extracted_data["INTEGRIDADE_EXTRAIDA_PERCENTUAL"] = round(score, 2)
    
    # 4. GATES de Segurança
    falha_gate = False
    for gate in gates_to_check:
        if extracted_data.get(gate) is None:
            falha_gate = True
            logger.warning(f"[GATE_ENGINE] Falha Crítica! Campo {gate} (GATE) ausente.")
            break
            
    extracted_data["_FALHA_GATE_CRITICO"] = falha_gate
    
    if falha_gate:
        # Penaliza severamente (zera o score) se o gate crítico falhou
        score = 0.0
        extracted_data["INTEGRIDADE_EXTRAIDA_PERCENTUAL"] = 0.0
        logger.warning("[INTEGRIDADE] Ficha recusada: Falha no GATE Crítico.")
    elif score >= 40.0:
        logger.info(f"[INTEGRIDADE] Ficha aprovada com {score:.2f}% de integridade (Score: {score_obtido}/{max_score}).")
    else:
        logger.warning(f"[INTEGRIDADE] Ficha recusada: apenas {score:.2f}% de integridade (Score: {score_obtido}/{max_score}).")

    return extracted_data, metadata_list

def extrair_registro_do_vencedor(
    workbook: openpyxl.workbook.workbook.Workbook,
    layouts: Dict[str, Any],
    master_catalog: Dict[str, Any] = None,
) -> Tuple[Dict[str, Any], List[dict[str, Any]], str]:
    """
    Motor Competitivo (Tournament Extraction):
    Espia a data primeiro para decidir se usa semântica e a ordem de teste.
    """
    from silver.normalizadores import normalizar_string

    # Veto por tipo de documento baseado em abas esperadas (Crítico #3)
    expected_tabs_raw = {
        "V0", "Para_Limite_Comercializadoras", "Premissas", 
        "FichaIndividual", "Memória de Cálculo", "Conf. Puras_DRE", 
        "Dados Gerais e Qualitativos", "DRE", "Dem.Fin."
    }
    
    def norm_tab(t: str) -> str:
        s = normalizar_string(t, upper=True)
        return s.replace(" ", "") if s else ""
        
    expected_tabs_norm = {norm_tab(t) for t in expected_tabs_raw}
    workbook_tabs_norm = {norm_tab(t) for t in workbook.sheetnames}
    
    if not expected_tabs_norm.intersection(workbook_tabs_norm):
        logger.warning(f"[VETO] Documento rejeitado. Nenhuma aba bate com as abas de layout: {workbook.sheetnames}")
        return {}, [], "DOC_001_ESTRUTURA_INCOMPATIVEL"

    grid_cache = {}
    
    # 1. Espiar a Data (Peek Data DF)
    data_df = None
    search_regex = SMART_SEMANTIC_MAP.get("DATA_DEMONSTRACAO_FINANCEIRA", r"DATA\s*DA\s*DEMONSTRA[CÇ][AÃ]O|DATA\s*BASE|DATA\s*DA\s*DF")
    val_date, _ = busca_omnidirecional(workbook, search_regex, "date", None, "DATA_DEMONSTRACAO_FINANCEIRA", grid_cache)
    
    if isinstance(val_date, datetime):
        data_df = val_date
        
    is_new_format = data_df and data_df >= CUTOFF_DATE_LAYOUT_CHANGE
    
    layouts_to_test = list(layouts.items())
    if is_new_format:
        layouts_to_test.reverse()
        allow_semantic = True
        logger.info(f"[TORNEIO] Ficha recente ({data_df.strftime('%d/%m/%Y')}). Testando layouts reversamente (padrao_7->padrao_1) COM semântica.")
    else:
        allow_semantic = False
        date_str = data_df.strftime('%d/%m/%Y') if data_df else "Desconhecida"
        logger.info(f"[TORNEIO] Ficha antiga ({date_str}). Testando layouts na ordem padrão SEM semântica.")

    best_score = -1.0
    champion_data = {}
    champion_meta = []
    champion_name = "NENHUM"

    for layout_name, layout_schema in layouts_to_test:
        extracted, metadata = extrair_registro(workbook, layout_schema, master_catalog, grid_cache, allow_semantic=allow_semantic)
        score = extracted.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        
        logger.info(f"Challenger {layout_name} obteve score: {score:.2f}%")
        
        if score > best_score:
            best_score = score
            champion_data = extracted
            champion_meta = metadata
            champion_name = layout_name

    logger.info(f"[CHAMPION] Torneio finalizado. Vencedor: '{champion_name}' com score de {best_score:.2f}%.")
    return champion_data, champion_meta, champion_name
```


---
## src\domain\salesforce\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\salesforce\servico_salesforce.py
Linhas: 134
Classes: SalesforceIngestionError
Funções: inserir_dados_salesforce, enriquecer_com_cnpj
```python
"""Serviço de ingestão e normalização da base do Salesforce."""

from __future__ import annotations

import shutil
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from services.connectors.salesforce_connector import buscar_salesforce_dados
from storage.escrever_dados import escrever_conjunto_de_dados_silver


class SalesforceIngestionError(Exception):
    """Exceção para falhas na ingestão da base do Salesforce."""


def inserir_dados_salesforce(context: AppContext) -> dict[str, Any]:
    """
    Lê o arquivo do Salesforce (via conector), salva o snapshot na Bronze,
    deduplica os registros, enriquece as tabelas filhas com o CNPJ da Conta
    e persiste na camada Silver.
    """
    run_id = f"SF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__ingestao_salesforce.log"
    logger = obter_logger("bdc.salesforce", log_file)

    try:
        logger.info("Iniciando processo de ingestão da base do Salesforce.")

        input_dir = context.path("entradas") / "salesforce"
        arquivo_bruto = input_dir / "salesforce.xlsx"

        if not arquivo_bruto.exists():
            logger.warning("Arquivo salesforce.xlsx não encontrado na entrada.")
            return {"run_id": run_id, "status": "SEM_DADOS"}

        # 1. Copia o snapshot bruto intacto para a Bronze
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "salesforce"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_salesforce_{datetime.now().strftime('%Y%m%d')}_{arquivo_bruto.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(arquivo_bruto, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze.name)

        # 2. Extração via Conector
        dfs_sf = buscar_salesforce_dados(input_dir=input_dir, logger=logger)
        
        df_account = dfs_sf.get("Account", pd.DataFrame())
        df_cotacao = dfs_sf.get("Cotacao", pd.DataFrame())
        df_chamado = dfs_sf.get("Chamado", pd.DataFrame())
        df_contrato = dfs_sf.get("Contrato", pd.DataFrame())

        # 3. Deduplicação (Mantém apenas o último registro de cada Id inserido pelo Power Query)
        df_account = df_account.drop_duplicates(subset=["Id"], keep="last") if not df_account.empty else df_account
        df_cotacao = df_cotacao.drop_duplicates(subset=["Id"], keep="last") if not df_cotacao.empty else df_cotacao
        df_chamado = df_chamado.drop_duplicates(subset=["Id"], keep="last") if not df_chamado.empty else df_chamado
        df_contrato = df_contrato.drop_duplicates(subset=["Id"], keep="last") if not df_contrato.empty else df_contrato

        # Padroniza nome da coluna CNPJ na Account para facilitar os cruzamentos
        if "CNPJ__c" in df_account.columns:
            df_account = df_account.rename(columns={"CNPJ__c": "CNPJ"})

        # 4. Enriquecimento: Traz o CNPJ da Conta (Account) para os objetos filhos
        if not df_account.empty and "CNPJ" in df_account.columns:
            account_map = df_account[["Id", "CNPJ"]].rename(columns={"Id": "AccountId_Join"})
            
            def enriquecer_com_cnpj(df_filho: pd.DataFrame) -> pd.DataFrame:
                if df_filho.empty or "AccountId" not in df_filho.columns:
                    return df_filho
                
                # Faz o Procv/Join: Filho[AccountId] == Conta[Id]
                df_merged = pd.merge(
                    df_filho, 
                    account_map, 
                    left_on="AccountId", 
                    right_on="AccountId_Join", 
                    how="left"
                )
                df_merged = df_merged.drop(columns=["AccountId_Join"])
                
                # Se não encontrou CNPJ (conta órfã), preenche com zeros para evitar quebra de contrato
                if "CNPJ" in df_merged.columns:
                    df_merged["CNPJ"] = df_merged["CNPJ"].fillna("00000000000000")
                return df_merged

            df_cotacao = enriquecer_com_cnpj(df_cotacao)
            df_chamado = enriquecer_com_cnpj(df_chamado)
            df_contrato = enriquecer_com_cnpj(df_contrato)

        # Adiciona metadados de rastreabilidade
        for df in [df_account, df_cotacao, df_chamado, df_contrato]:
            if not df.empty:
                df["RUN_ID"] = run_id
                df["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        # 5. Persistência na Silver (CSV + Parquet) separada por objeto
        silver_dir = context.path("silver") / "salesforce_silver"
        
        datasets = {
            "account": df_account,
            "cotacao": df_cotacao,
            "chamado": df_chamado,
            "contrato": df_contrato
        }

        arquivos_salvos = []
        for nome, df in datasets.items():
            if not df.empty:
                csv_p, pqt_p = escrever_conjunto_de_dados_silver(
                    records=df.to_dict(orient="records"),
                    output_dir=silver_dir / nome,
                    filename=f"salesforce_{nome}"
                )
                arquivos_salvos.append(nome)

        logger.info("Ingestão do Salesforce concluída. Objetos salvos: %s", ", ".join(arquivos_salvos))

        return {
            "run_id": run_id,
            "linhas_account": len(df_account),
            "linhas_cotacao": len(df_cotacao),
            "linhas_chamado": len(df_chamado),
            "linhas_contrato": len(df_contrato),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão do Salesforce.")
        raise SalesforceIngestionError(f"Erro ao ingerir base do Salesforce: {exc}") from exc
```


---
## src\relational\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\services\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Serviços de processamento do sistema BDC."""

```


---
## src\services\connectors\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\services\connectors\denodo_connector.py
Linhas: 144
Classes: DenodoConnectionError
Funções: _solicitacao_com_tentativa, _encontrar_arquivo_bronze_recente, buscar_denodo
```python
"""Conector central para o virtualizador Denodo via API RESTful.

feat(T2.1.1): Adicionados retry com backoff exponencial e fallback para
último snapshot Bronze em caso de indisponibilidade.
Ref: §3.4 do Planejamento Funcional.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Desativa alertas de certificado SSL interno da rede corporativa
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = logging.getLogger(__name__)

# Parâmetros de retry (§3.4 — tratamento de indisponibilidade)
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 2.0


class DenodoConnectionError(Exception):
    """Exceção levantada para falhas de conexão na API do Denodo."""


def _solicitacao_com_tentativa(url: str, params, auth, max_retries: int = MAX_RETRIES) -> requests.Response:
    """Executa GET com retry e backoff exponencial."""
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                auth=auth,
                verify=False,
                timeout=300,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            if attempt < max_retries:
                wait = BACKOFF_BASE_SECONDS ** attempt
                LOGGER.warning(
                    "Tentativa %s/%s falhou para '%s'. Retry em %.1fs. Erro: %s",
                    attempt, max_retries, url, wait, exc,
                )
                time.sleep(wait)
            else:
                LOGGER.error("Todas as %s tentativas falharam para '%s'.", max_retries, url)
    raise last_exc  # type: ignore[misc]


def _encontrar_arquivo_bronze_recente(bronze_dir: Path, prefix: str = "raw_contratos") -> Path | None:
    """Localiza o snapshot Bronze mais recente para fallback."""
    if not bronze_dir.exists():
        return None
    snapshots = [
        f for f in bronze_dir.iterdir()
        if f.is_file() and f.name.startswith(prefix) and f.suffix == ".parquet"
    ]
    if not snapshots:
        return None
    return max(snapshots, key=lambda f: f.stat().st_mtime)


def buscar_denodo(
    view_name: str,
    params: dict[str, Any] | None = None,
    bronze_fallback_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Consome uma view do Denodo via API REST (JSON).
    Gerencia paginação automaticamente, retornando um DataFrame consolidado.

    Se todas as tentativas falharem e `bronze_fallback_dir` for informado,
    tenta ler o último snapshot Bronze disponível (§3.4 — fallback para
    snapshot anterior em caso de indisponibilidade).
    """
    base_url = os.getenv("DENODO_REST_BASE_URL", "https://vidgcpprd.copel.nt:9443/denodo-restfulws/com/views")
    url = f"{base_url}/{view_name}"

    user = os.getenv("DENODO_USER")
    pwd = os.getenv("DENODO_PWD")

    if not all([user, pwd]):
        raise ValueError("Credenciais DENODO_USER ou DENODO_PWD não encontradas no arquivo .env.")

    req_params: dict[str, Any] | None = {"$format": "json"}
    if params:
        req_params.update(params)

    auth = HTTPBasicAuth(user, pwd)
    all_elements: list[dict[str, Any]] = []

    try:
        LOGGER.info("Iniciando extração da view '%s' via REST API...", view_name)

        while url:
            response = _solicitacao_com_tentativa(url, params=req_params, auth=auth)

            data = response.json()
            elements = data.get("elements", [])

            if not elements:
                break

            all_elements.extend(elements)

            links = data.get("links", [])
            next_link = next((link["href"] for link in links if link.get("rel") == "next"), None)

            if next_link:
                url = next_link
                req_params = None
            else:
                url = None  # type: ignore[assignment]

        LOGGER.info("Extração via REST finalizada. %s registros carregados.", len(all_elements))
        return pd.DataFrame(all_elements)

    except (requests.exceptions.RequestException, DenodoConnectionError) as exc:
        LOGGER.exception("Falha na comunicação com a API REST do Denodo.")

        # Fallback: tenta ler último snapshot Bronze (§3.4)
        if bronze_fallback_dir:
            snapshot = _encontrar_arquivo_bronze_recente(bronze_fallback_dir)
            if snapshot:
                LOGGER.warning(
                    "Usando fallback: lendo último snapshot Bronze '%s'.", snapshot.name
                )
                return pd.read_parquet(snapshot)
            LOGGER.error("Nenhum snapshot Bronze encontrado para fallback em '%s'.", bronze_fallback_dir)

        raise DenodoConnectionError(f"Erro ao acessar endpoint '{view_name}': {exc}") from exc
```


---
## src\services\connectors\receita_connector.py
Linhas: 181
Classes: -
Funções: _cache_path, _load_cache, _save_cache, _is_same_day_cache, _consultar_cnpj_brasilapi, buscar_receita_dados_lote
```python
# -*- coding: utf-8 -*-
"""Conector e cache da BrasilAPI para consulta cadastral de Receita Federal."""

from __future__ import annotations
from silver.normalizadores import padronizar_cnpj

import json
import logging
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from app.context import AppContext

LOGGER = logging.getLogger(__name__)
BRASIL_API_BASE_URL = "https://brasilapi.com.br/api/cnpj/v1"

def _cache_path(context: AppContext) -> Path:
    return context.path("entradas") / "receita" / "cache" / "receita_cache.json"

def _load_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists(): return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError): return {}
    if not isinstance(payload, dict): return {}
    
    cache: dict[str, dict[str, Any]] = {}
    for cnpj, record in payload.items():
        if record.get("STATUS") == "OK_BYPASS" or "Simulacao" in str(record.get("NATUREZA_JURIDICA", "")):
            continue
        normalized = padronizar_cnpj(cnpj)
        if normalized and isinstance(record, dict):
            cache[normalized[0]] = record
    return cache

def _save_cache(path: Path, cache: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = {cnpj: cache[cnpj] for cnpj in sorted(cache)}
    path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")

def _is_same_day_cache(record: dict[str, Any]) -> bool:
    quando = record.get("DATA_CONSULTA")
    if not quando: return False
    try:
        return str(quando)[:10] == date.today().isoformat()
    except Exception: return False

def _consultar_cnpj_brasilapi(cnpj: str, session: requests.Session) -> dict[str, Any]:
    url = f"{BRASIL_API_BASE_URL}/{cnpj}"
    resultado = {
        "CNPJ": cnpj, "SITUACAO_CADASTRAL": "ERRO_API", "DATA_ABERTURA": "N/D",
        "CNAE_PRINCIPAL": "N/D", "NATUREZA_JURIDICA": "N/D",
        "DATA_CONSULTA": datetime.now().isoformat(timespec="seconds"),
        "STATUS": "FALHA", "MENSAGEM": ""
    }
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BDC_Pipeline/1.0",
    }
    
    tentativas_maximas = 4
    espera_base = 3.0 # Segundos

    for tentativa in range(1, tentativas_maximas + 1):
        try:
            resp = session.get(url, headers=headers, timeout=15, verify=False)
            
            if resp.status_code == 200:
                data = resp.json()
                resultado["SITUACAO_CADASTRAL"] = str(data.get("descricao_situacao_cadastral", "N/D")).strip().upper()
                resultado["DATA_ABERTURA"] = str(data.get("data_inicio_atividade", "N/D")).strip()
                resultado["CNAE_PRINCIPAL"] = str(data.get("cnae_fiscal", "N/D")).strip()
                resultado["NATUREZA_JURIDICA"] = str(data.get("natureza_juridica", "N/D")).strip()
                resultado["STATUS"] = "SUCESSO"
                resultado["MENSAGEM"] = "Consulta via BrasilAPI com sucesso"
                return resultado
                
            if resp.status_code in (404, 400):
                resultado["SITUACAO_CADASTRAL"] = "NAO_ENCONTRADO"
                resultado["MENSAGEM"] = f"CNPJ inexistente (HTTP {resp.status_code})"
                return resultado
                
            if resp.status_code == 429 or resp.status_code >= 500:
                if tentativa < tentativas_maximas:
                    tempo_espera = espera_base * (2 ** (tentativa - 1)) # Backoff Exponencial (3s, 6s, 12s...)
                    print(f" [API bloqueou - HTTP {resp.status_code}] Pausando {tempo_espera}s...", end="", flush=True)
                    time.sleep(tempo_espera)
                    continue
                else:
                    resultado["SITUACAO_CADASTRAL"] = "RATE_LIMIT"
                    resultado["MENSAGEM"] = "Bloqueio persistente após múltiplas tentativas."
                    return resultado

            # Outros erros HTTP (401, 403, etc)
            resultado["SITUACAO_CADASTRAL"] = f"ERRO_HTTP_{resp.status_code}"
            return resultado

        except requests.exceptions.Timeout:
            if tentativa < tentativas_maximas:
                time.sleep(espera_base * tentativa)
                continue
            resultado["SITUACAO_CADASTRAL"] = "TIMEOUT"
            return resultado
            
        except requests.exceptions.RequestException as e:
            if tentativa < tentativas_maximas:
                time.sleep(espera_base * tentativa)
                continue
            resultado["SITUACAO_CADASTRAL"] = "ERRO_CONEXAO"
            return resultado

    return resultado

def buscar_receita_dados_lote(cnpjs: list[str], context: AppContext) -> pd.DataFrame:
    cache_path = _cache_path(context)
    cache = _load_cache(cache_path)
    
    list_normalizada = []
    seen = set()
    for cnpj in cnpjs or []:
        normalized = normalizar_cnpj(cnpj)
        if normalized and normalized not in seen:
            seen.add(normalized)
            list_normalizada.append(normalized)

    results = []
    total = len(list_normalizada)
    qtd_cache = 0
    qtd_api = 0
    qtd_erro = 0
    
    LOGGER.info("[RECEITA FEDERAL] Processando %d CNPJs...", total)
    print(f"\n--- INICIANDO CONSULTA RECEITA FEDERAL ({total} CNPJs) ---")

    # Usando Session para otimizar conexões TCP
    with requests.Session() as sessao:
        for index, cnpj in enumerate(list_normalizada):
            cached = cache.get(cnpj)
            
            if cached and _is_same_day_cache(cached):
                if cached.get("SITUACAO_CADASTRAL") not in ["TIMEOUT", "RATE_LIMIT", "ERRO_CONEXAO", "ERRO_API"]:
                    print(f"[{index + 1}/{total}] CNPJ {cnpj} -> CACHE ({cached.get('SITUACAO_CADASTRAL')})")
                    results.append(cached)
                    qtd_cache += 1
                    continue

            print(f"[{index + 1}/{total}] CNPJ {cnpj} -> Consultando API...", end=" ", flush=True)
            api_result = _consultar_cnpj_brasilapi(cnpj, sessao)
            status_obtido = api_result.get("SITUACAO_CADASTRAL")
            print(f"Resultado: {status_obtido}")
            
            qtd_api += 1
            if api_result.get("STATUS") == "FALHA":
                qtd_erro += 1
                
            if status_obtido not in ["TIMEOUT", "RATE_LIMIT", "ERRO_CONEXAO"]:
                cache[cnpj] = api_result
                
            results.append(api_result)
            
            # Pausa padrão gentil de 0.8s entre requisições de sucesso para não irritar a BrasilAPI
            time.sleep(0.8)

            if qtd_api > 0 and qtd_api % 50 == 0:
                _save_cache(cache_path, cache)

    if qtd_api > 0:
        _save_cache(cache_path, cache)

    print(f"\n--- RESUMO RECEITA: {qtd_cache} Cache | {qtd_api} API | {qtd_erro} Erros ---")

    df = pd.DataFrame(results)
    return df.drop_duplicates(subset=["CNPJ"], keep="last").reset_index(drop=True)
```


---
## src\services\connectors\salesforce_connector.py
Linhas: 74
Classes: SalesforceConnectionError
Funções: buscar_salesforce_dados
```python
"""Conector de integração de arquivos extraídos do Salesforce (via Power Query)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

class SalesforceConnectionError(Exception):
    """Exceção levantada quando a base do Salesforce não pode ser obtida."""


def buscar_salesforce_dados(
    input_dir: Path | str,
    logger: Any | None = None,
) -> Dict[str, pd.DataFrame]:
    """
    Lê o arquivo salesforce.xlsx atualizado via Power Query contendo as abas:
    Conta, Cotação, Chamado e Contrato. Retorna um dicionário de DataFrames.
    """
    diretorio = Path(input_dir)
    arquivo_sf = diretorio / "salesforce.xlsx"
    
    if logger:
        logger.info("Iniciando leitura da base local do Salesforce: %s", arquivo_sf)
        
    if not arquivo_sf.exists():
        if logger:
            logger.error("Arquivo %s não encontrado.", arquivo_sf)
        raise FileNotFoundError(f"Arquivo Salesforce não encontrado na pasta: {arquivo_sf}")

    resultados_df = {}
    
    # Mapeamento das abas do Excel para os nomes lógicos exigidos pelo sistema
    mapa_abas = {
        "Conta": "Account",
        "Cotação": "Cotacao",
        "Chamado": "Chamado",
        "Contrato": "Contrato"
    }

    try:
        for aba_excel, chave_dict in mapa_abas.items():
            if logger:
                logger.info("Lendo aba '%s' do Salesforce...", aba_excel)
            
            # Lendo tudo como string (dtype=str) para não corromper 'Id' e 'AccountId'
            df = pd.read_excel(arquivo_sf, sheet_name=aba_excel, dtype=str)
            
            # Tratamento de nulos vindos do Excel (transforma "nan" string em real None ou string vazia)
            df = df.fillna("")
            df = df.replace("nan", "")
            
            # Normalização específica da máscara de CNPJ na aba Conta
            if chave_dict == "Account" and "CNPJ__c" in df.columns:
                df["CNPJ__c"] = (
                    df["CNPJ__c"]
                    .astype(str)
                    .str.replace(r"\D", "", regex=True) # Remove pontos, traços e barras
                    .str.zfill(14) # Garante os 14 dígitos com zeros à esquerda
                )
            
            resultados_df[chave_dict] = df
            
            if logger:
                logger.info("Aba '%s' carregada com sucesso. %s registros processados.", aba_excel, len(df))

        return resultados_df

    except Exception as exc:
        if logger:
            logger.exception("Falha crítica ao ler o arquivo local do Salesforce.")
        raise SalesforceConnectionError(f"Erro ao processar as planilhas do Salesforce: {exc}") from exc
```


---
## src\silver\normalizadores.py
Linhas: 182
Classes: -
Funções: normalizar_string, normalizar_float, normalize_date, normalize_data_demonstracao_financeira, padronizar_cnpj, calc_digit
```python
"""Orquestrador Central de Normalizadores do Projeto BDC."""

from __future__ import annotations

import re
import math
from datetime import datetime
from typing import Any


def normalizar_string(value: Any, upper: bool = False) -> str | None:
    """Normaliza um valor textual."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    return text.upper() if upper else text


def normalizar_float(value: Any) -> float | None:
    """Converte um valor textual ou numérico em ``float``."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    text = text.replace("R$", "").replace("%", "").strip()
    
    # Notação contábil negativa (1.500) -> -1.500
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1].strip()
    
    # Tratamento seguro para formatação brasileira
    if "." in text and "," in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text and "." not in text:
        text = text.replace(",", ".")
    elif text.count(".") > 1:
        text = text.replace(".", "")

    try:
        return float(text)
    except ValueError:
        return None


def normalize_date(value: Any) -> str | None:
    """Normaliza uma data para o formato ISO ``YYYY-MM-DD``."""
    if value is None:
        return None

    if isinstance(value, datetime):
        # Resgate de datas corrompidas por digitação de "Ano" em célula de Data no Excel
        if 1900 <= value.year <= 1920:
            dias = (value - datetime(1899, 12, 30)).days
            if 1950 <= dias <= 2100:  # O número de dias é na verdade o ano digitado!
                return f"{dias}-12-31"
        return value.date().isoformat()

    text = str(value).strip()
    if not text:
        return None

    patterns = (
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d.%m.%Y",
    )

    for pattern in patterns:
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue

    return None


def normalize_data_demonstracao_financeira(value: Any) -> tuple[str | None, str | None, bool]:
    """Normaliza DATA_DEMONSTRACAO_FINANCEIRA para dd/mm/aaaa.
    Retorna: (data_normalizada, valor_original_corrompido, flag_corrigida)
    """
    if value is None:
        return None, None, False

    # Resgate de datas corrompidas por digitação de "Ano" em célula de Data no Excel
    if isinstance(value, datetime) and 1900 <= value.year <= 1920:
        dias = (value - datetime(1899, 12, 30)).days
        if 1950 <= dias <= 2100:  # O número de dias é na verdade o ano digitado!
            return f"31/12/{dias}", value.strftime("%Y-%m-%d %H:%M:%S"), True

    text = str(value).strip()
    if not text:
        return None, None, False

    if re.fullmatch(r"\d{4}", text):
        return f"31/12/{text}", text, True

    text = text.split()[0]

    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]

    for fmt in formatos:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%d/%m/%Y"), None, False
        except ValueError:
            continue

    return None, None, False


def padronizar_cnpj(cnpj_raw: Any) -> tuple[str | None, str | None, str]:
    """
    Normaliza CNPJ garantindo 14 dígitos e extraindo a Raiz de 8 dígitos.
    Retorna: (CNPJ_14, CNPJ_RAIZ, STATUS_CNPJ)
    """
    if cnpj_raw is None:
        return None, None, "CNPJ_AUSENTE"
        
    tipo_original = type(cnpj_raw)
    
    # 1. Tratamento seguro de NaN e Floats (.0)
    if isinstance(cnpj_raw, float):
        if math.isnan(cnpj_raw):
            return None, None, "CNPJ_AUSENTE"
        cnpj_raw = int(cnpj_raw)  # Remove o .0 antes de virar string
        
    cnpj_str = str(cnpj_raw).strip()
    
    # 2. Literais vazios ou textuais inválidos
    if not cnpj_str or cnpj_str.upper() in ["ISENTO", "NAN", "NONE", "NULL", "NA"]:
        return None, None, "CNPJ_AUSENTE"
        
    # 3. Remoção de máscaras e pontuações
    numeros = re.sub(r"\D", "", cnpj_str)
    
    if not numeros:
        return None, None, "CNPJ_AUSENTE"
        
    tamanho = len(numeros)
    
    if tamanho > 14:
        return None, None, "CNPJ_INVALIDO"
        
    # 4. Regra de Recuperação (Zfill) vs CNPJ Incompleto
    if tamanho < 14:
        # Recuperamos com zeros à esquerda (se a pessoa digitou texto sem zeros ou o Pandas comeu os zeros numéricos)
        cnpj_14 = numeros.zfill(14)
    else:
        cnpj_14 = numeros

    # 5. Validação de Lixo (CNPJ Zerado)
    if cnpj_14 == "00000000000000":
        return None, None, "CNPJ_INVALIDO"

    # 6. Validação Módulo 11
    def calc_digit(base: str, weights: list[int]) -> str:
        total = sum(int(num) * weight for num, weight in zip(base, weights))
        remainder = total % 11
        return "0" if remainder < 2 else str(11 - remainder)

    first_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    second_weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    first_digit = calc_digit(cnpj_14[:12], first_weights)
    second_digit = calc_digit(cnpj_14[:12] + first_digit, second_weights)

    if cnpj_14[-2:] != first_digit + second_digit:
        return None, None, "CNPJ_INVALIDO"

    cnpj_raiz = cnpj_14[:8]
    return cnpj_14, cnpj_raiz, "CNPJ_VALIDO"

```


---
## src\storage\estado_armazenamento.py
Linhas: 72
Classes: DocumentManifest
Funções: __post_init__, to_dict
```python
"""Estruturas de estado e manifesto do processamento."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from domain.enums import (
    LoadMode,
    StatusClassificacao,
    StatusExtracao,
    TipoFicha,
)

@dataclass
class DocumentManifest:
    """Representa o manifesto técnico de uma ficha processada."""

    documento_id: str
    run_id: str
    ambiente: str
    tipo_ficha: TipoFicha | str
    arquivo_nome: str | None = None
    caminho_origem: str | None = None
    caminho_staging: str | None = None
    caminho_bronze: str | None = None
    hash_arquivo: str | None = None
    versao_ficha: str | None = None
    cnpj_extraido: str | None = None
    data_demonstracao_financeira: str | None = None
    data_calculo: str | None = None
    status_classificacao: StatusClassificacao | str | None = None
    status_extracao: StatusExtracao | str | None = None
    load_mode: LoadMode | str | None = None
    reprocessed: bool | None = None
    previous_record_found: bool | None = None
    erros: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Garante que os atributos controlados pertençam aos domínios nativos."""
        if isinstance(self.tipo_ficha, str):
            try:
                self.tipo_ficha = TipoFicha(self.tipo_ficha.lower())
            except ValueError:
                raise ValueError(f"Valor rejeitado para tipo_ficha: '{self.tipo_ficha}'. Domínios válidos: {[e.value for e in TipoFicha]}")

        if isinstance(self.status_classificacao, str):
            try:
                self.status_classificacao = StatusClassificacao(self.status_classificacao.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para status_classificacao: '{self.status_classificacao}'. Domínios válidos: {[e.value for e in StatusClassificacao]}")

        if isinstance(self.status_extracao, str):
            try:
                self.status_extracao = StatusExtracao(self.status_extracao.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para status_extracao: '{self.status_extracao}'. Domínios válidos: {[e.value for e in StatusExtracao]}")
                
        if isinstance(self.load_mode, str):
            try:
                self.load_mode = LoadMode(self.load_mode.lower())
            except ValueError:
                raise ValueError(f"Valor rejeitado para load_mode: '{self.load_mode}'. Domínios válidos: {[e.value for e in LoadMode]}")

    def to_dict(self) -> dict[str, Any]:
        """Serializa o manifesto convertendo os Enums para seus valores primitivos (strings)."""
        manifest_dict = asdict(self)
        for key, value in manifest_dict.items():
            if hasattr(value, "value"):
                manifest_dict[key] = value.value
        return manifest_dict
```
