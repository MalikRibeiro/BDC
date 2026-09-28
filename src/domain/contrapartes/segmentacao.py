"""Segmentação metodológica e enquadramento de contrapartes e consumidores.

Centraliza regras de segmentação (CPURA, CGRUPO, Consumidor <=5MWm vs >5MWm)
e classificação documental conforme planejamento v1.2.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Optional

import json
from pathlib import Path

from common.numeros import to_float_br
from common.texto import normalizar_texto


def _carregar_parametros_segmentacao() -> tuple[float, str]:
    """Carrega parâmetros metodológicos do JSON de governança com fallback."""
    config_path = Path("ENTRADAS/control/configs/segmentacao_config.json")
    padrao_limiar = 5.0
    padrao_versao = "v1.2"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return float(dados.get("limiar_mwm_detalhado", padrao_limiar)), str(dados.get("versao_regra_atual", padrao_versao))
        except Exception:
            pass
    return padrao_limiar, padrao_versao


LIMIAR_MWM_DETALHADO, VERSAO_REGRA_ATUAL = _carregar_parametros_segmentacao()


@dataclass
class ClassificacaoDocumental:
    """Resultado da classificação documental de um consumidor."""

    tipo_consumidor: str
    presenca_df: bool
    tipo_analise_exigida: str
    versao_layout: str
    campos_obrigatorios: list[str]
    compatibilidade_ficha_segmento: bool


CAMPOS_DF_COMPLETA = [
    "ATIVO_CIRCULANTE", "ATIVO_CIRCULANTE_FINANCEIRO", "ATIVO_TOTAL",
    "PASSIVO_CIRCULANTE", "PASSIVO_CIRCULANTE_FINANCEIRO",
    "PASSIVO_NAO_CIRCULANTE_FINANCEIRO", "PATRIMONIO_LIQUIDO",
    "LUCROS_ACUMULADOS", "RESERVA_DE_LUCROS", "VENDAS_LIQUIDAS",
    "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
]

CAMPOS_OBRIGATORIOS_DETALHADA = [
    "CNPJ", "RAZAO_SOCIAL", "DATA_DEMONSTRACAO_FINANCEIRA",
    "PATRIMONIO_LIQUIDO", "ATIVO_CIRCULANTE", "ATIVO_TOTAL",
    "PASSIVO_CIRCULANTE", "LUCRO_LIQUIDO",
    "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
    "FCO", "ROA", "ROE", "PROBABILIDADE_DEFAULT",
]

CAMPOS_OBRIGATORIOS_SIMPLIFICADA = [
    "CNPJ", "RAZAO_SOCIAL", "SCORE_BUREAU",
]


def definir_segmento_metodologico(
    registro: dict[str, Any],
) -> str:
    """Define o segmento metodológico da contraparte."""
    tipo_ficha = normalizar_texto(registro.get("TIPO_FICHA"))
    
    if tipo_ficha == "COMERCIALIZADORA":
        tipo_comercializadora = normalizar_texto(registro.get("TIPO_COMERCIALIZADORA"))
        if tipo_comercializadora == "CPURA":
            return "CPURA"

        if tipo_comercializadora == "CGRUPO":
            return "CGRUPO"

        raise ValueError(
            "Comercializadora sem TIPO_COMERCIALIZADORA válido."
        )

    if tipo_ficha == "CONSUMIDOR":
        volume_mwm = to_float_br(registro.get("VOLUME_ENQUADRAMENTO_MWM"))
        
        if volume_mwm is None:
            return "NAO_ENQUADRADO"
            
        if volume_mwm >= LIMIAR_MWM_DETALHADO:
            return "CONSUMIDOR_GT_5"
        else:
            return "CONSUMIDOR_LE_5"

    raise ValueError(
        f"TIPO_FICHA inválido para segmentação: {tipo_ficha!r}"
    )


def _esta_vazio(value: Any) -> bool:
    """Indica se o valor deve ser tratado como vazio."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _normalizar_aba(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    # Maiúsculas, remove acentos
    t = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").upper()
    t = t.strip()
    t = re.sub(r"[\.\_\-]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t


def _avaliar_ficha_com_df(record: dict[str, Any], abas_planilha: list[str]) -> bool:
    abas_norm = [_normalizar_aba(aba) for aba in abas_planilha]
    
    tem_dem_fin = "DEM FIN" in abas_norm
    tem_conf_dem_fin = "CONF DEM FIN" in abas_norm
    tem_dre = "DRE" in abas_norm
    
    if tem_dem_fin and tem_conf_dem_fin and tem_dre:
        record["FICHA_COM_DF"] = "SIM"
        record["SCORE_CLASSIFICACAO_DF"] = 9
        record["SINAIS_DF_IDENTIFICADOS"] = "Abas Dem.Fin, Conf.Dem.Fin e DRE presentes simultaneamente"
        return True

    score = 0
    sinais = []
    
    if tem_dem_fin:
        score += 3
        sinais.append("Aba Dem.Fin")
    if tem_conf_dem_fin:
        score += 3
        sinais.append("Aba Conf.Dem.Fin")
    if tem_dre:
        score += 3
        sinais.append("Aba DRE")
    if "PD% ASSAF" in abas_norm or "PD ASSAF" in abas_norm:
        score += 1
        sinais.append("Aba PD% Assaf")
    if "INPUT MODE" in abas_norm:
        score += 1
        sinais.append("Aba Input Mode")
        
    if not _esta_vazio(record.get("ATIVO_TOTAL")):
        score += 1
        sinais.append("Ativo Total")
    if not _esta_vazio(record.get("PASSIVO_CIRCULANTE")):
        score += 1
        sinais.append("Passivo Circulante")
    if not _esta_vazio(record.get("PATRIMONIO_LIQUIDO")):
        score += 1
        sinais.append("Patrimônio Líquido")
    if not _esta_vazio(record.get("LUCRO_LIQUIDO")):
        score += 1
        sinais.append("Lucro Líquido")
    if not _esta_vazio(record.get("FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS")):
        score += 1
        sinais.append("Caixa Líquido Operacional")
        
    for var_name in ["X12", "X16", "X19", "X22"]:
        if not _esta_vazio(record.get(var_name)):
            score += 1
            sinais.append(f"Variável {var_name}")
            break

    record["SCORE_CLASSIFICACAO_DF"] = score
    record["SINAIS_DF_IDENTIFICADOS"] = ", ".join(sinais) if sinais else "Nenhum sinal estrutural"
    record["ABAS_IDENTIFICADAS"] = ", ".join(abas_planilha[:5]) # apenas para log
    
    if score >= 7:
        record["FICHA_COM_DF"] = "SIM"
        record["MOTIVO_CLASSIFICACAO_DF"] = "Score estrutural >= 7"
        return True
    else:
        record["FICHA_COM_DF"] = "NAO"
        record["MOTIVO_CLASSIFICACAO_DF"] = "Score estrutural < 7"
        return False


def _avaliar_confianca(
    record: dict[str, Any],
    tipo_consumidor: str,
    presenca_df: bool,
) -> str:
    """Avalia a confiança da classificação com base na consistência dos dados."""
    problemas = 0

    if tipo_consumidor == ">=5MWm" and not presenca_df:
        problemas += 2

    if _esta_vazio(record.get("CNPJ")):
        problemas += 1

    if _esta_vazio(record.get("RAZAO_SOCIAL")):
        problemas += 1

    if problemas == 0:
        return "alta"
    elif problemas == 1:
        return "media"
    else:
        return "baixa"


def classificar_consumidor(
    record: dict[str, Any],
    versao_layout: str,
    volume_mwm: float | None = None,
    abas_planilha: list[str] | None = None,
) -> ClassificacaoDocumental:
    """Classifica um consumidor conforme a metodologia aplicável.

    Args:
        record: Registro normalizado extraído da ficha.
        versao_layout: Versão do layout utilizado (e.g. "v3").
        volume_mwm: Volume contratado em MWm. Se None, tenta obter do record.
        abas_planilha: Lista de abas da planilha excel para extração estrutural de DFs.

    Returns:
        ClassificacaoDocumental com todos os campos preenchidos.
    """
    if abas_planilha is None:
        abas_planilha = []
    if volume_mwm is None:
        volume_mwm = record.get("VOLUME_CONTRATADO")
        if volume_mwm is not None:
            try:
                volume_mwm = float(volume_mwm)
            except (ValueError, TypeError):
                volume_mwm = None

    if volume_mwm is not None and volume_mwm >= LIMIAR_MWM_DETALHADO:
        tipo_consumidor = ">=5MWm"
    elif volume_mwm is not None and volume_mwm < LIMIAR_MWM_DETALHADO:
        tipo_consumidor = "<5MWm"
    else:
        presenca_df = _avaliar_ficha_com_df(record, abas_planilha)
        tipo_consumidor = ">=5MWm" if presenca_df else "<5MWm"

    presenca_df = _avaliar_ficha_com_df(record, abas_planilha)
    
    record["TIPO_CONSUMIDOR"] = tipo_consumidor
    record["VERSAO_LAYOUT"] = versao_layout

    if tipo_consumidor == ">=5MWm":
        tipo_analise = "detalhada"
        campos_obrigatorios = list(CAMPOS_OBRIGATORIOS_DETALHADA)
    else:
        tipo_analise = "simplificada"
        campos_obrigatorios = list(CAMPOS_OBRIGATORIOS_SIMPLIFICADA)

    campos_nao_aplicavel: list[str] = []
    if tipo_consumidor == "<5MWm":
        for campo in CAMPOS_DF_COMPLETA:
            val = record.get(campo)
            if _esta_vazio(val) or str(val).upper() == "NAO_APLICAVEL":
                campos_nao_aplicavel.append(campo)

    if tipo_consumidor == ">=5MWm":
        compativel = presenca_df
    else:
        compativel = not _esta_vazio(record.get("SCORE_BUREAU"))

    confianca = _avaliar_confianca(record, tipo_consumidor, presenca_df)
    
    record["TIPO_ANALISE_EXIGIDA"] = tipo_analise
    record["CONFIANCA_CLASSIFICACAO"] = confianca
    record["COMPATIBILIDADE_FICHA_SEGMENTO"] = str(compativel)

    return ClassificacaoDocumental(
        tipo_consumidor=tipo_consumidor,
        presenca_df=presenca_df,
        tipo_analise_exigida=tipo_analise,
        versao_layout=versao_layout,
        campos_obrigatorios=campos_obrigatorios,
        compatibilidade_ficha_segmento=compativel,
    )


def criar_classificacao_registro(
    classificacao: ClassificacaoDocumental,
) -> dict[str, Any]:
    """Converte a classificação documental em dict para o silver_record."""
    return {
        "tipo_consumidor": classificacao.tipo_consumidor,
        "presenca_df": classificacao.presenca_df,
        "tipo_analise_exigida": classificacao.tipo_analise_exigida,
        "versao_layout": classificacao.versao_layout,
        "campos_obrigatorios": ",".join(classificacao.campos_obrigatorios),
        "compatibilidade_ficha_segmento": classificacao.compatibilidade_ficha_segmento,
    }