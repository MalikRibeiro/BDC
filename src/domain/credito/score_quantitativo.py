"""Cálculo do score quantitativo para CPURA."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_peso_nota(
    nota: Any,
    nota_para_peso: dict[str, Any],
    nome_campo: str,
) -> float:
    """Obtém o peso numérico da nota."""
    nota_normalizada = normalizar_texto(nota)

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


def calcular_score_quantitativo_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score quantitativo de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando score quantitativo CPURA. CNPJ=%s",
                registro.get("CNPJ"),
            )

        nota_para_peso = score_cpura_config.get("nota_para_peso")
        pesos_quantitativos = score_cpura_config.get("pesos_quantitativos")

        if not isinstance(nota_para_peso, dict):
            raise PdConfigurationError(
                "Bloco 'nota_para_peso' ausente ou inválido."
            )

        if not isinstance(pesos_quantitativos, dict):
            raise PdConfigurationError(
                "Bloco 'pesos_quantitativos' ausente ou inválido."
            )

        nota_pd = registro.get("NOTA_PD")
        nota_fco_rol = registro.get("NOTA_FCO_ROL")
        nota_roe = registro.get("NOTA_ROE")
        nota_roa = registro.get("NOTA_ROA")

        peso_pd = _obter_peso_nota(nota_pd, nota_para_peso, "NOTA_PD")
        peso_fco_rol = _obter_peso_nota(
            nota_fco_rol,
            nota_para_peso,
            "NOTA_FCO_ROL",
        )
        peso_roe = _obter_peso_nota(nota_roe, nota_para_peso, "NOTA_ROE")
        peso_roa = _obter_peso_nota(nota_roa, nota_para_peso, "NOTA_ROA")

        try:
            w_pd = float(pesos_quantitativos["PD"])
            w_fco_rol = float(pesos_quantitativos["FCO_ROL"])
            w_roe = float(pesos_quantitativos["ROE"])
            w_roa = float(pesos_quantitativos["ROA"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Peso quantitativo ausente: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                "Pesos quantitativos inválidos."
            ) from exc

        score_quantitativo = (
            w_pd * peso_pd
            + w_fco_rol * peso_fco_rol
            + w_roe * peso_roe
            + w_roa * peso_roa
        )

        resultado = {
            "PESO_PD": peso_pd,
            "PESO_FCO_ROL": peso_fco_rol,
            "PESO_ROE": peso_roe,
            "PESO_ROA": peso_roa,
            "SCORE_QUANTITATIVO": score_quantitativo,
        }

        if logger is not None:
            logger.info(
                "Score quantitativo CPURA calculado. "
                "CNPJ=%s SCORE_QUANTITATIVO=%s",
                registro.get("CNPJ"),
                score_quantitativo,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score quantitativo CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )
        raise
