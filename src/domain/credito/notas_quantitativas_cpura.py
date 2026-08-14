# -*- coding: utf-8 -*-
"""Cálculo das notas quantitativas de CPURA."""

from __future__ import annotations

from typing import Any

from common.types import normalize_float
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_valor_numerico(
    registro: dict[str, Any],
    campo: str,
) -> float:
    """Obtém e valida um valor numérico do registro."""
    valor = normalize_float(registro.get(campo))

    if valor is None:
        raise PdInputValidationError(
            f"{campo} não informado."
        )

    return float(valor)


def _normalizar_pd(valor: float) -> float:
    """Normaliza PD para escala decimal [0, 1]."""
    if valor < 0:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT negativa: {valor}"
        )

    if valor > 1:
        valor = valor / 100.0

    if valor > 1:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT fora do intervalo após normalização: {valor}"
        )

    return valor


def _obter_faixas_notas(
    score_cpura_config: dict[str, Any],
    indicador: str,
) -> list[dict[str, Any]]:
    """Obtém as faixas de notas de um indicador."""
    faixas_root = score_cpura_config.get("faixas_notas_quantitativas")

    if not isinstance(faixas_root, dict):
        raise PdConfigurationError(
            "Bloco 'faixas_notas_quantitativas' ausente ou inválido."
        )

    faixas = faixas_root.get(indicador)

    if not isinstance(faixas, list) or not faixas:
        raise PdConfigurationError(
            f"Faixas quantitativas ausentes ou inválidas para {indicador}."
        )

    return faixas


def _atribuir_nota_por_faixa(
    valor: float,
    faixas: list[dict[str, Any]],
    indicador: str,
) -> str:
    """Atribui nota A-E conforme a faixa parametrizada."""
    for faixa in faixas:
        try:
            nota = str(faixa["nota"]).strip().upper()
            minimo = float(faixa["min"])
            maximo = float(faixa["max"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Faixa incompleta em {indicador}: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                f"Faixa inválida em {indicador}."
            ) from exc

        if minimo > maximo:
            raise PdConfigurationError(
                f"Faixa inválida em {indicador}: min > max."
            )

        if minimo <= valor <= maximo:
            return nota

    raise PdInputValidationError(
        f"Valor sem faixa configurada para {indicador}: {valor}"
    )


def calcular_notas_quantitativas_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula as notas quantitativas de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo das notas quantitativas CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )

        pd_valor = _obter_valor_numerico(registro, "PROBABILIDADE_DEFAULT")
        fco_rol_valor = _obter_valor_numerico(registro, "MFCO")
        roe_valor = _obter_valor_numerico(registro, "ROE")
        roa_valor = _obter_valor_numerico(registro, "ROA")

        pd_valor = _normalizar_pd(pd_valor)

        nota_pd = _atribuir_nota_por_faixa(
            valor=pd_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "PD"),
            indicador="PD",
        )
        nota_fco_rol = _atribuir_nota_por_faixa(
            valor=fco_rol_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "FCO_ROL"),
            indicador="FCO_ROL",
        )
        nota_roe = _atribuir_nota_por_faixa(
            valor=roe_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "ROE"),
            indicador="ROE",
        )
        nota_roa = _atribuir_nota_por_faixa(
            valor=roa_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "ROA"),
            indicador="ROA",
        )

        resultado = {
            "NOTA_PD": nota_pd,
            "NOTA_FCO_ROL": nota_fco_rol,
            "NOTA_ROE": nota_roe,
            "NOTA_ROA": nota_roa,
        }

        if logger is not None:
            logger.info(
                "Notas quantitativas CPURA calculadas. "
                "CNPJ=%s NOTA_PD=%s NOTA_FCO_ROL=%s NOTA_ROE=%s NOTA_ROA=%s",
                registro.get("CNPJ"),
                resultado["NOTA_PD"],
                resultado["NOTA_FCO_ROL"],
                resultado["NOTA_ROE"],
                resultado["NOTA_ROA"],
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo das notas quantitativas CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )
        raise
