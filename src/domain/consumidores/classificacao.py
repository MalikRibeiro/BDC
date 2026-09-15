"""Serviço de classificação documental de consumidores.

Determina o tipo de análise exigida (detalhada ou simplificada)
com base no volume contratado, conforme planejamento v1.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


LIMIAR_MWM_DETALHADO = 5.0
VERSAO_REGRA_ATUAL = "v1.2"


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
    "CNPJ", "EMPRESA", "DATA_DEMONSTRACAO_FINANCEIRA",
    "PATRIMONIO_LIQUIDO", "ATIVO_CIRCULANTE", "ATIVO_TOTAL",
    "PASSIVO_CIRCULANTE", "LUCRO_LIQUIDO",
    "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
    "FCO", "ROA", "ROE", "PROBABILIDADE_DEFAULT",
]

CAMPOS_OBRIGATORIOS_SIMPLIFICADA = [
    "CNPJ", "EMPRESA", "SCORE_BUREAU",
]


def _esta_vazio(value: Any) -> bool:
    """Indica se o valor deve ser tratado como vazio."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _tem_demonstracoes_financeiras(record: dict[str, Any]) -> bool:
    """Verifica se a ficha possui demonstrações financeiras preenchidas."""
    campos_presentes = 0
    for campo in CAMPOS_DF_COMPLETA:
        val = record.get(campo)
        if not _esta_vazio(val) and str(val).upper() != "NAO_APLICAVEL":
            campos_presentes += 1

    return campos_presentes >= len(CAMPOS_DF_COMPLETA) * 0.5


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

    if _esta_vazio(record.get("EMPRESA")):
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
) -> ClassificacaoDocumental:
    """Classifica um consumidor conforme a metodologia aplicável.

    Args:
        record: Registro normalizado extraído da ficha.
        versao_layout: Versão do layout utilizado (e.g. "v3").
        volume_mwm: Volume contratado em MWm. Se None, tenta obter do record.

    Returns:
        ClassificacaoDocumental com todos os campos preenchidos.
    """
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
        presenca_df = _tem_demonstracoes_financeiras(record)
        tipo_consumidor = ">=5MWm" if presenca_df else "<5MWm"

    presenca_df = _tem_demonstracoes_financeiras(record)

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