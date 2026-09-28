"""Conector de Rede Corporativa para Obtenção e Classificação de Fichas Cadastrais.

Responsável por:
1. Varrer diretórios de rede (S:\\...) conforme catálogo JSON.
2. Descartar lixo (PDFs, DOCs) e locks temporários do Excel (~$*).
3. Inspecionar e validar se a ficha pertence a Comercializadoras ou Consumidores.
4. Rotear e copiar de forma atômica para a pasta 'pendentes' correspondente:
   - ENTRADAS/fichas/comercializadoras/pendentes/
   - ENTRADAS/fichas/consumidores/pendentes/
5. Garantir idempotência estrita via hash SHA-256 e fail-safe de arquivos abertos.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
import re
import shutil
from typing import Any
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

from control.logger import obter_logger

LOGGER = logging.getLogger(__name__)

# Assinaturas estruturais de abas baseadas nos layouts oficiais do BDC (ENTRADAS/control/layouts/)
# 1. Abas exclusivas dos layouts de Consumidores (layout_ficha_consumidor_v1 e v2)
ABAS_EXCLUSIVAS_CONSUMIDORES = {
    "dadosgeraisequalitativos",
    "dadosgerais",
    "qualitativos",
    "premissasconsumidores",
    "fichaconsumidores",
    "fichaconsumidor",
    "consumidores",
}

# 2. Abas exclusivas dos layouts de Comercializadoras (layout_ficha_comercializadora_v1 a v6)
ABAS_EXCLUSIVAS_COMERCIALIZADORAS = {
    "v0",
    "paralimitecomercializadoras",
    "comercializadoras",
}

# 3. Aba principal de Comercializadoras (v2 a v6), presente na maioria das fichas de agentes
ABAS_ESTRUTURAIS_COMERCIALIZADORAS = {
    "fichaindividual",
}

# 4. Abas legítimas de suporte e análise financeira do BDC (presentes em fichas de ambos os segmentos)
ABAS_FINANCEIRAS_BDC = {
    "premissas",
    "memoriadecalculo",
    "dre",
    "demfin",
    "confdemfin",
    "confpurasdre",
    "questionario",
    "balanco",
    "balancopatrimonial",
    "inputmode",
    "pdassaf",
}

# Todas as abas que qualificam uma planilha como documento legítimo do BDC
TODAS_ABAS_BDC_VALIDAS = (
    ABAS_EXCLUSIVAS_CONSUMIDORES
    | ABAS_EXCLUSIVAS_COMERCIALIZADORAS
    | ABAS_ESTRUTURAIS_COMERCIALIZADORAS
    | ABAS_FINANCEIRAS_BDC
)


def normalizar_nome_aba(nome: str) -> str:
    """Normaliza nome de aba para comparação determinística: minúsculas, sem acentos, sem espaços ou pontuação."""
    if not isinstance(nome, str):
        return ""
    t = unicodedata.normalize("NFKD", nome).encode("ASCII", "ignore").decode("ASCII").lower()
    return re.sub(r"[^a-z0-9]", "", t)


def calcular_hash_arquivo(caminho: Path) -> str:
    """Calcula o hash SHA-256 do arquivo em blocos de 1MB para eficiência de memória."""
    hasher = hashlib.sha256()
    with caminho.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def obter_abas_planilha(caminho_arquivo: Path) -> list[str]:
    """
    Lê os nomes das abas de planilhas .xlsx/.xlsm via zipfile em < 5ms,
    sem carregar o conteúdo das células em memória.
    """
    if caminho_arquivo.suffix.lower() not in {".xlsx", ".xlsm"}:
        return []
    try:
        with zipfile.ZipFile(caminho_arquivo, "r") as z:
            if "xl/workbook.xml" not in z.namelist():
                return []
            tree = ET.fromstring(z.read("xl/workbook.xml"))
            sheets = tree.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet")
            return [s.attrib.get("name", "") for s in sheets]
    except Exception:
        return []


PADROES_ARQUIVOS_DESCARTADOS = (
    "ficha modelo",
    "ficha padrão",
    "ficha padrao",
    "ficha_puras_",
    "ficha_geradoras_v0",
    "comentários adicionais",
    "comentarios adicionais",
    "cnpj's bbce",
    "cnpjs bbce",
    "indicadores operacionais",
    "estudo ressazonalização",
    "estudo ressazonalizacao",
    "calculo_",
    "aditivo_",
    "preço médio",
    "preco medio",
    "empréstimos",
    "emprestimos",
    "multiplos fip",
    "múltiplos fip",
    "chamados_dppm",
    "backup",
)


def validar_se_eh_ficha_cadastral(
    caminho_arquivo: Path,
    segmento_sugerido: str | None = None,
) -> tuple[bool, str | None, str]:
    """
    Executa o Gate Rigoroso de Ingestão e Classificação por Layout:
    1. Veta templates vazios, arquivos de apoio, aditivos e memórias avulsas.
    2. Valida se a planilha possui abas esperadas pelos layouts oficiais do BDC.
    3. Classifica com precisão entre 'consumidores' e 'comercializadoras', usando
       evidências ponderadas de layout (abas exclusivas), rotas de origem e metadados.
    
    Retorna: (eh_valido, segmento, motivo)
    """
    nome_lower = caminho_arquivo.name.lower()

    # Gate 1: Veto por padrões conhecidos de lixo ou templates
    if any(padrao in nome_lower for padrao in PADROES_ARQUIVOS_DESCARTADOS):
        return False, None, "PADRAO_APOIO_OU_TEMPLATE"

    # Gate 2: Veto Estrutural Obrigatório por Abas
    abas_brutas = obter_abas_planilha(caminho_arquivo)
    if not abas_brutas:
        return False, None, "SEM_ABAS_OU_FORMATO_INVALIDO"

    abas_normalizadas = {normalizar_nome_aba(a) for a in abas_brutas}

    # Se a planilha NÃO contém nenhuma aba compatível com os layouts oficiais do BDC -> VETO ABSOLUTO!
    if not (abas_normalizadas & TODAS_ABAS_BDC_VALIDAS):
        return False, None, f"ABAS_NAO_COMPATIVEIS: {abas_brutas[:4]}"

    # Gate 3: Classificação Ponderada de Segmento por Layout e Rota
    score_consum = 0
    score_comerc = 0

    # Evidência de Abas Exclusivas dos Layouts Oficiais (Precedência Absoluta sobre Rotas de Rede)
    if abas_normalizadas & ABAS_EXCLUSIVAS_CONSUMIDORES:
        score_consum += 25
    if abas_normalizadas & ABAS_EXCLUSIVAS_COMERCIALIZADORAS:
        score_comerc += 25

    # Evidência de Aba FichaIndividual (layout comercializadora v2 a v6)
    if abas_normalizadas & ABAS_ESTRUTURAIS_COMERCIALIZADORAS:
        if not (abas_normalizadas & ABAS_EXCLUSIVAS_CONSUMIDORES):
            score_comerc += 8

    # Evidência da Rota de Origem Declarada (se veio de pasta específica de rede)
    if segmento_sugerido == "consumidores":
        score_consum += 10
    elif segmento_sugerido == "comercializadoras":
        score_comerc += 10

    # Evidência textual do caminho completo ou nome de arquivo
    caminho_completo_str = str(caminho_arquivo).lower()
    if any(k in caminho_completo_str for k in ("consumidor", "consumidores", "livre", "livres")):
        score_consum += 5
    if any(k in caminho_completo_str for k in ("comercializadora", "comercializadoras", "geradora", "geradoras", "trading")):
        score_comerc += 5

    # Decisão final de segmento
    if score_consum > score_comerc:
        return True, "consumidores", "LAYOUT_OU_ROTA_CONSUMIDOR"
    elif score_comerc > score_consum:
        return True, "comercializadoras", "LAYOUT_OU_ROTA_COMERCIALIZADORA"

    # Desempate estrito de segurança
    if segmento_sugerido in ("consumidores", "comercializadoras"):
        return True, segmento_sugerido, f"DESEMPATE_ROTA_{segmento_sugerido.upper()}"

    return True, "comercializadoras", "DESEMPATE_COMERCIALIZADORA_PADRAO"


def classificar_segmento_ficha(caminho_arquivo: Path, segmento_sugerido_rota: str | None = None) -> str | None:
    """Wrapper para compatibilidade retroativa."""
    eh_valido, seg, _ = validar_se_eh_ficha_cadastral(caminho_arquivo, segmento_sugerido=segmento_sugerido_rota)
    return seg if eh_valido else None


def _carregar_manifesto(caminho_manifesto: Path) -> dict[str, dict[str, Any]]:
    """Carrega o histórico de fichas já sincronizadas com migração transparente de caminhos legados."""
    if caminho_manifesto.exists():
        try:
            with caminho_manifesto.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    # Migração automática caso ainda esteja na pasta legada ENTRADAS/fichas/
    caminho_legado = Path("ENTRADAS/fichas/manifesto_fichas_rede.json")
    if caminho_legado.exists():
        try:
            with caminho_legado.open("r", encoding="utf-8") as f:
                dados = json.load(f)
            _salvar_manifesto(caminho_manifesto, dados)
            caminho_legado.unlink(missing_ok=True)
            return dados
        except Exception:
            return {}

    return {}


def _salvar_manifesto(caminho_manifesto: Path, dados: dict[str, dict[str, Any]]) -> None:
    """Persiste o histórico de fichas sincronizadas."""
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    with caminho_manifesto.open("w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def redistribuir_fichas_locais_por_layout(
    destinos: dict[str, str] | None = None,
    manifesto: dict[str, dict[str, Any]] | None = None,
    manifesto_path: Path | None = None,
    logger_inst: logging.Logger | None = None,
) -> dict[str, int]:
    """
    Higieniza e redistribui arquivos que estejam na pasta errada localmente.
    Examina as planilhas locais contra os layouts oficiais do BDC:
    - Se encontrar ficha com abas de Consumidor na pasta de Comercializadoras, move de volta para Consumidores.
    - Se encontrar ficha com abas de Comercializadora na pasta de Consumidores, move para Comercializadoras.
    Atualiza o manifesto bronze correspondente para manter integridade total.
    """
    log = logger_inst or LOGGER
    destinos_map = destinos or {
        "comercializadoras": "ENTRADAS/fichas/comercializadoras/pendentes",
        "consumidores": "ENTRADAS/fichas/consumidores/pendentes",
    }
    pasta_comerc = Path(destinos_map["comercializadoras"])
    pasta_consum = Path(destinos_map["consumidores"])

    pasta_comerc.mkdir(parents=True, exist_ok=True)
    pasta_consum.mkdir(parents=True, exist_ok=True)

    movidos_para_consum = 0
    movidos_para_comerc = 0

    # 1. Varre arquivos em Comercializadoras que possam ser Consumidores
    for arq in list(pasta_comerc.iterdir()):
        if not arq.is_file() or arq.name.startswith("~$") or arq.name.startswith(".~"):
            continue
        eh_ficha, seg, _ = validar_se_eh_ficha_cadastral(arq)
        if eh_ficha and seg == "consumidores":
            destino = pasta_consum / arq.name
            shutil.move(arq, destino)
            movidos_para_consum += 1
            log.info("[REDISTRIBUICAO] Ficha de Consumidor realocada: '%s' -> %s", arq.name, destino)
            if manifesto is not None:
                for v in manifesto.values():
                    if v.get("nome_arquivo") == arq.name:
                        v["segmento"] = "consumidores"
                        v["destino_local"] = str(destino)

    # 2. Varre arquivos em Consumidores que possam ser Comercializadoras
    for arq in list(pasta_consum.iterdir()):
        if not arq.is_file() or arq.name.startswith("~$") or arq.name.startswith(".~"):
            continue
        eh_ficha, seg, _ = validar_se_eh_ficha_cadastral(arq)
        if eh_ficha and seg == "comercializadoras":
            destino = pasta_comerc / arq.name
            shutil.move(arq, destino)
            movidos_para_comerc += 1
            log.info("[REDISTRIBUICAO] Ficha de Comercializadora realocada: '%s' -> %s", arq.name, destino)
            if manifesto is not None:
                for v in manifesto.values():
                    if v.get("nome_arquivo") == arq.name:
                        v["segmento"] = "comercializadoras"
                        v["destino_local"] = str(destino)

    if manifesto is not None and manifesto_path is not None and (movidos_para_consum > 0 or movidos_para_comerc > 0):
        _salvar_manifesto(manifesto_path, manifesto)

    return {
        "movidos_para_consumidores": movidos_para_consum,
        "movidos_para_comercializadoras": movidos_para_comerc,
    }


def obter_fichas_rede(
    caminho_config_json: Path | str | None = None,
    logger_inst: logging.Logger | None = None,
) -> dict[str, Any]:
    """
    Executa a obtenção e roteamento validado de fichas da rede corporativa.
    
    Salva diretamente em:
    - ENTRADAS/fichas/comercializadoras/pendentes/
    - ENTRADAS/fichas/consumidores/pendentes/
    """
    log = logger_inst or obter_logger("fichas_connector", Path("LOGS/ingestion/fichas_connector.log"))
    
    config_path = Path(caminho_config_json or "ENTRADAS/configs/catalogo_fontes_rede.json")
    if not config_path.exists():
        log.warning("Catálogo de fontes de rede não encontrado: %s", config_path)
        return {"status": "config_nao_encontrado", "arquivos_novos": 0}

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    if not config.get("habilitado", True):
        log.info("Conector de fichas de rede está desabilitado na configuração (habilitado=false).")
        return {"status": "desabilitado", "arquivos_novos": 0}

    destinos = config.get("destinos_locais", {
        "comercializadoras": "ENTRADAS/fichas/comercializadoras/pendentes",
        "consumidores": "ENTRADAS/fichas/consumidores/pendentes",
    })
    manifesto_path = Path(config.get("arquivo_manifesto", "SAIDAS/bronze/ingestion_log/manifesto_fichas_rede.json"))
    manifesto = _carregar_manifesto(manifesto_path)

    # Passo 1: Higienização e redistribuição imediata das fichas locais existentes
    log.info("Verificando consistência de layouts nas pastas de fichas locais...")
    res_redistribuicao = redistribuir_fichas_locais_por_layout(
        destinos=destinos,
        manifesto=manifesto,
        manifesto_path=manifesto_path,
        logger_inst=log,
    )
    if res_redistribuicao["movidos_para_consumidores"] > 0 or res_redistribuicao["movidos_para_comercializadoras"] > 0:
        log.info(
            "Redistribuição local concluída: %d movidas para Consumidores, %d movidas para Comercializadoras.",
            res_redistribuicao["movidos_para_consumidores"],
            res_redistribuicao["movidos_para_comercializadoras"],
        )

    drive_root_str = config.get("drive_root", "")
    drive_root = Path(drive_root_str)
    
    total_local_comerc = len([f for f in Path(destinos["comercializadoras"]).iterdir() if f.is_file() and not f.name.startswith("~")]) if Path(destinos["comercializadoras"]).exists() else 0
    total_local_consum = len([f for f in Path(destinos["consumidores"]).iterdir() if f.is_file() and not f.name.startswith("~")]) if Path(destinos["consumidores"]).exists() else 0

    # Fail-Safe de Conectividade com a Rede
    if not drive_root.exists():
        log.warning(
            "Ponto de montagem da rede inacessível ou desconectado: '%s'. "
            "A esteira prosseguirá utilizando a base de fichas local existente.",
            drive_root
        )
        return {
            "status": "rede_inacessivel",
            "motivo": f"Caminho não encontrado: {drive_root}",
            "arquivos_novos_total": 0,
            "redistribuidos_locais_consumidores": res_redistribuicao["movidos_para_consumidores"],
            "redistribuidos_locais_comercializadoras": res_redistribuicao["movidos_para_comercializadoras"],
            "total_local_comercializadoras": total_local_comerc,
            "total_local_consumidores": total_local_consum,
        }

    extensoes = set(config.get("extensoes_permitidas", [".xlsx", ".xlsm", ".xls"]))
    fontes = config.get("fontes", {})

    total_novos = {"comercializadoras": 0, "consumidores": 0}
    total_ignorados = 0
    total_bloqueados = 0
    total_descartados = 0

    log.info("Iniciando varredura e validação de fichas na raiz de rede: %s", drive_root)

    # Varre cada grupo declarado no catálogo
    for categoria_rota, subrotas in fontes.items():
        segmento_sugerido = (
            "consumidores" if "consumidor" in categoria_rota.lower()
            else ("comercializadoras" if "comercializadora" in categoria_rota.lower() else None)
        )

        for subrota in subrotas:
            origem_completa = drive_root / subrota if not Path(subrota).is_absolute() else Path(subrota)
            if not origem_completa.exists():
                log.info("Subpasta de rede não encontrada ou sem acesso: %s", origem_completa)
                continue

            log.info("Varrendo subpasta de rede: %s", origem_completa)
            for item in origem_completa.rglob("*"):
                if not item.is_file():
                    continue
                # Descarte estrito de arquivos de bloqueio e temporários do Excel
                if item.name.startswith("~$") or item.name.startswith(".~"):
                    continue
                # Descarte de lixo (PDFs, DOCs, TXTs)
                if item.suffix.lower() not in extensoes:
                    continue

                chave_manifesto = str(item.resolve())
                try:
                    stat_info = item.stat()
                    mtime_remoto = stat_info.st_mtime
                    tamanho_remoto = stat_info.st_size
                except Exception:
                    continue

                info_anterior = manifesto.get(chave_manifesto)
                # 1. Se o arquivo já foi VETADO anteriormente e não mudou na rede -> pular direto sem abrir zipfile!
                if (
                    info_anterior
                    and info_anterior.get("status") == "VETO"
                    and info_anterior.get("mtime") == mtime_remoto
                    and info_anterior.get("tamanho_bytes") == tamanho_remoto
                ):
                    total_descartados += 1
                    continue

                # 2. Se o arquivo já foi sincronizado com sucesso e o destino existe -> pular direto!
                if (
                    info_anterior
                    and info_anterior.get("status", "SUCESSO") == "SUCESSO"
                    and info_anterior.get("mtime") == mtime_remoto
                    and info_anterior.get("tamanho_bytes") == tamanho_remoto
                    and info_anterior.get("destino_local")
                    and Path(info_anterior.get("destino_local")).exists()
                ):
                    total_ignorados += 1
                    continue

                # Gate Rigoroso: Valida e classifica a ficha por layouts e rotas
                eh_ficha, segmento_destino, motivo = validar_se_eh_ficha_cadastral(
                    item, segmento_sugerido=segmento_sugerido
                )
                if not eh_ficha or not segmento_destino:
                    total_descartados += 1
                    # Persiste o veto no manifesto para nunca mais reabrir este arquivo na rede
                    manifesto[chave_manifesto] = {
                        "nome_arquivo": item.name,
                        "status": "VETO",
                        "motivo_veto": motivo,
                        "tamanho_bytes": tamanho_remoto,
                        "mtime": mtime_remoto,
                        "data_avaliacao": datetime.now().isoformat(),
                        "caminho_origem": str(item),
                    }
                    log.info("[VETO] Arquivo não é ficha cadastral (ignorado): '%s' (Motivo: %s)", item.name, motivo)
                    continue

                pasta_destino = Path(destinos.get(segmento_destino, f"ENTRADAS/fichas/{segmento_destino}/pendentes"))
                pasta_destino.mkdir(parents=True, exist_ok=True)

                status_proc = _processar_e_copiar_ficha(
                    item=item,
                    pasta_destino=pasta_destino,
                    segmento=segmento_destino,
                    manifesto=manifesto,
                    log=log,
                )

                if status_proc == "NOVO":
                    total_novos[segmento_destino] += 1
                elif status_proc == "IGNORADO":
                    total_ignorados += 1
                elif status_proc == "BLOQUEADO":
                    total_bloqueados += 1

    _salvar_manifesto(manifesto_path, manifesto)

    total_local_comerc = len([f for f in Path(destinos["comercializadoras"]).iterdir() if f.is_file() and not f.name.startswith("~")]) if Path(destinos["comercializadoras"]).exists() else 0
    total_local_consum = len([f for f in Path(destinos["consumidores"]).iterdir() if f.is_file() and not f.name.startswith("~")]) if Path(destinos["consumidores"]).exists() else 0

    total_sincronizados = total_novos["comercializadoras"] + total_novos["consumidores"]
    log.info(
        "Obtenção de fichas concluída: %d novas (%d comercializadoras, %d consumidores), "
        "%d inalteradas, %d bloqueadas por usuários, %d descartadas (não são fichas). "
        "Base local total: %d comercializadoras, %d consumidores.",
        total_sincronizados,
        total_novos["comercializadoras"],
        total_novos["consumidores"],
        total_ignorados,
        total_bloqueados,
        total_descartados,
        total_local_comerc,
        total_local_consum,
    )

    return {
        "status": "sucesso",
        "arquivos_novos_total": total_sincronizados,
        "comercializadoras_novas": total_novos["comercializadoras"],
        "consumidores_novos": total_novos["consumidores"],
        "arquivos_ignorados": total_ignorados,
        "arquivos_bloqueados": total_bloqueados,
        "arquivos_descartados_veto": total_descartados,
        "redistribuidos_locais_consumidores": res_redistribuicao["movidos_para_consumidores"],
        "redistribuidos_locais_comercializadoras": res_redistribuicao["movidos_para_comercializadoras"],
        "total_local_comercializadoras": total_local_comerc,
        "total_local_consumidores": total_local_consum,
    }


def _processar_e_copiar_ficha(
    item: Path,
    pasta_destino: Path,
    segmento: str,
    manifesto: dict[str, dict[str, Any]],
    log: logging.Logger,
) -> str:
    """Copia a ficha para o destino correto de forma atômica se for nova ou modificada."""
    chave_manifesto = str(item.resolve())

    try:
        stat_info = item.stat()
        mtime_remoto = stat_info.st_mtime
        tamanho_remoto = stat_info.st_size

        info_anterior = manifesto.get(chave_manifesto)
        if (
            info_anterior
            and info_anterior.get("mtime") == mtime_remoto
            and info_anterior.get("tamanho_bytes") == tamanho_remoto
            and info_anterior.get("segmento") == segmento
        ):
            return "IGNORADO"

        # Cálculo de Hash para garantia de idempotência
        hash_atual = calcular_hash_arquivo(item)
        if (
            info_anterior
            and info_anterior.get("hash_sha256") == hash_atual
            and info_anterior.get("segmento") == segmento
        ):
            manifesto[chave_manifesto]["mtime"] = mtime_remoto
            return "IGNORADO"

        # Cópia Atômica para a pasta pendentes correta
        arquivo_final = pasta_destino / item.name
        arquivo_tmp = pasta_destino / f"{item.name}.tmp_sync"

        shutil.copy2(item, arquivo_tmp)
        arquivo_tmp.replace(arquivo_final)

        manifesto[chave_manifesto] = {
            "nome_arquivo": item.name,
            "status": "SUCESSO",
            "segmento": segmento,
            "tamanho_bytes": tamanho_remoto,
            "mtime": mtime_remoto,
            "hash_sha256": hash_atual,
            "data_sincronizacao": datetime.now().isoformat(),
            "caminho_origem": str(item),
            "destino_local": str(arquivo_final),
        }

        log.info(
            "Ficha [%s] validada e copiada com sucesso: '%s' -> %s",
            segmento.upper(), item.name, arquivo_final
        )
        return "NOVO"

    except PermissionError:
        log.warning("Ficha aberta por analista no Excel (bloqueio temporário ignorado): %s", item.name)
        return "BLOQUEADO"
    except Exception as exc:
        log.error("Erro ao sincronizar ficha %s: %s", item.name, exc)
        return "ERRO"
