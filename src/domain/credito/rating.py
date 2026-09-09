"""Determinação do rating final para o cálculo de PD ajustada."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _calcular_rating_final_cpura(
    registro: dict[str, Any],
    cpura_score_faixas: dict[str, Any],
) -> str:
    """Calcula o rating final de CPURA a partir do SCORE_TOTAL."""
    score_total = registro.get("SCORE_TOTAL")

    if score_total is None:
        raise PdInputValidationError(
            "SCORE_TOTAL não informado para cálculo do rating de CPURA."
        )

    try:
        score_total = float(score_total)
    except (TypeError, ValueError) as exc:
        raise PdInputValidationError(
            f"SCORE_TOTAL inválido: {score_total!r}"
        ) from exc

    if not isinstance(cpura_score_faixas, dict) or not cpura_score_faixas:
        raise PdConfigurationError(
            "Configuração de score_faixas de CPURA ausente ou inválida."
        )

    for rating, faixa in cpura_score_faixas.items():
        try:
            score_min = float(faixa["min"])
            score_max = float(faixa["max"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Faixa de score incompleta para rating {rating}."
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                f"Faixa de score inválida para rating {rating}."
            ) from exc

        if score_min <= score_total <= score_max:
            return rating

    raise PdInputValidationError(
        f"SCORE_TOTAL fora das faixas esperadas para CPURA: {score_total}"
    )


def _obter_rating_pronto(
    registro: dict[str, Any],
    segmento_pd: str,
) -> str:
    """Obtém rating já existente no registro."""
    rating = (
        registro.get("RATING_COPEL")
        or registro.get("NOTA_CREDITO")
        or registro.get("RATING_FINAL")
    )

    if rating is None:
        raise PdInputValidationError(
            f"Registro sem rating para {segmento_pd}."
        )

    rating_final = normalizar_texto(rating)

    validos = {"A", "B","C", "D", "E"} if segmento_pd == "CGRUPO" else {
        "A", "B", "C", "D", "E", "F"
    }

    if rating_final not in validos:
        raise PdInputValidationError(
            f"Rating inválido para {segmento_pd}: {rating_final}"
        )

    return rating_final


def calcular_rating_final(
    registro: dict[str, Any],
    segmento_pd: str,
    pd_cpura_config: dict[str, Any] | None = None,
) -> str:
    """Determina o rating final conforme o segmento."""
    segmento_pd = str(segmento_pd).strip().upper()

    if segmento_pd == "CPURA":
        if not pd_cpura_config:
            raise PdConfigurationError(
                "pd_cpura_config não informado para cálculo do rating de CPURA."
            )

        score_faixas = pd_cpura_config.get("score_faixas")
        return _calcular_rating_final_cpura(
            registro=registro,
            cpura_score_faixas=score_faixas,
        )

    return _obter_rating_pronto(
        registro=registro,
        segmento_pd=segmento_pd,
    )
