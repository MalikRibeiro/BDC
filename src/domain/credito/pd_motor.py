"""Orquestração do cálculo de PD ajustada."""

from __future__ import annotations

from typing import Any

from domain.credito.notas_quantitativas_cpura import (
    calcular_notas_quantitativas_cpura,
)
from domain.credito.pd_base import calcular_pd_base
from domain.credito.pd_exceptions import (
    PdCalculationError,
    PdConfigurationError,
)
from domain.credito.pd_transform import transformar_pd_por_segmento
from domain.credito.pd_validator import validar_insumos_pd
from domain.credito.rating import calcular_rating_final
from domain.credito.score_qualitativo import calcular_score_qualitativo_cpura
from domain.credito.score_quantitativo import calcular_score_quantitativo_cpura
from domain.credito.score_total import calcular_score_total_cpura


def calcular_pd_ajustada(
    registro: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any] | None = None,
    pd_cpura_config: dict[str, Any] | None = None,
    score_cpura_config: dict[str, Any] | None = None,
    peer_group: list[float] | None = None,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada/final da contraparte."""
    segmento_pd = str(registro.get("SEGMENTO_PD", "")).strip().upper()

    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo de PD ajustada. "
                "CNPJ=%s SEGMENTO_PD=%s",
                registro.get("CNPJ"),
                segmento_pd,
            )

        validar_insumos_pd(registro, segmento_pd)

        pd_base = calcular_pd_base(registro, segmento_pd)

        registro_calculo = dict(registro)
        registro_calculo["PD_BASE"] = pd_base

        resultado_scores: dict[str, Any] = {}

        if segmento_pd == "CPURA":
            if not score_cpura_config:
                raise PdConfigurationError(
                    "score_cpura_config não informado para CPURA."
                )

            if not pd_cpura_config:
                raise PdConfigurationError(
                    "pd_cpura_config não informado para CPURA."
                )

            notas_quant_info = calcular_notas_quantitativas_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(notas_quant_info)

            score_qual_info = calcular_score_qualitativo_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(score_qual_info)

            score_quant_info = calcular_score_quantitativo_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(score_quant_info)

            score_total_info = calcular_score_total_cpura(
                score_quant_info=score_quant_info,
                score_qual_info=score_qual_info,
                logger=logger,
            )
            registro_calculo.update(score_total_info)

            rating_final = calcular_rating_final(
                registro=registro_calculo,
                segmento_pd=segmento_pd,
                pd_cpura_config=pd_cpura_config,
            )
            registro_calculo["RATING_FINAL"] = rating_final

            resultado_scores.update(notas_quant_info)
            resultado_scores.update(score_qual_info)
            resultado_scores.update(score_quant_info)
            resultado_scores.update(score_total_info)

        if segmento_pd in {"CGRUPO", "CONSUMIDOR_GT_5"} and not pd_transform_rules:
            raise PdConfigurationError(
                f"pd_transform_rules não informado para {segmento_pd}."
            )
        resultado_transformacao = transformar_pd_por_segmento(
            registro=registro_calculo,
            segmento_pd=segmento_pd,
            pd_base=pd_base,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=pd_cpura_config,
            peer_group=peer_group,
            logger=logger,
            rating_final=(
                registro_calculo.get("RATING_FINAL")
                or registro_calculo.get("RATING_COPEL")
            ),
        )

        resultado = {
            "SEGMENTO_PD": segmento_pd,
            "PD_BASE": pd_base,
            **resultado_scores,
            **resultado_transformacao,
        }

        if logger is not None:
            logger.info(
                "PD ajustada calculada com sucesso. "
                "CNPJ=%s SEGMENTO_PD=%s PD_BASE=%s "
                "RATING_FINAL=%s SCORE_TOTAL=%s PD_FINAL=%s METODO=%s",
                registro.get("CNPJ"),
                segmento_pd,
                resultado.get("PD_BASE"),
                resultado.get("RATING_FINAL"),
                resultado.get("SCORE_TOTAL"),
                resultado.get("PD_FINAL"),
                resultado.get("PD_METODO"),
            )

        return resultado

    except PdCalculationError:
        if logger is not None:
            logger.exception("Erro controlado no cálculo de PD ajustada. CNPJ=%s SEGMENTO_PD=%s", registro.get('CNPJ'), segmento_pd)
        raise

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha crítica no cálculo de PD ajustada. "
                "CNPJ=%s SEGMENTO_PD=%s",
                registro.get("CNPJ"),
                segmento_pd,
            )
        raise
