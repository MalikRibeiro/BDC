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
