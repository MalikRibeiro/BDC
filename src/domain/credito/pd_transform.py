"""Despacho da transformação de PD por segmento."""

from __future__ import annotations

from typing import Any

from domain.credito.pd_cgrupo import calcular_pd_final_cgrupo
from domain.credito.pd_consumidor_gt5 import calcular_pd_final_consumidor_gt5
from domain.credito.pd_consumidor_le5 import calcular_pd_final_consumidor_le5
from domain.credito.pd_cpura import calcular_pd_final_cpura
from domain.credito.pd_exceptions import PdCalculationError, PdConfigurationError


def _obter_faixa_pd(
    pd_faixas: dict[str, Any],
    segmento_pd: str,
    rating_final: str,
) -> tuple[float, float]:
    """Obtém a faixa de PD parametrizada para segmento e rating."""
    if not pd_faixas:
        raise PdConfigurationError("Faixas de PD não informadas.")

    if segmento_pd not in pd_faixas:
        raise PdConfigurationError(
            f"Segmento não encontrado nas faixas de PD: {segmento_pd}"
        )

    faixas_segmento = pd_faixas[segmento_pd]

    if rating_final not in faixas_segmento:
        raise PdConfigurationError(
            f"Rating {rating_final} não encontrado para {segmento_pd}"
        )

    faixa = faixas_segmento[rating_final]

    if "min" not in faixa or "max" not in faixa:
        raise PdConfigurationError(
            f"Faixa inválida para {segmento_pd}/{rating_final}."
        )

    pd_min = float(faixa["min"])
    pd_max = float(faixa["max"])

    if pd_min > pd_max:
        raise PdConfigurationError(
            f"Faixa inválida: min > max para {segmento_pd}/{rating_final}."
        )

    return pd_min, pd_max


def transformar_pd_por_segmento(
    registro: dict[str, Any],
    segmento_pd: str,
    pd_base: float,
    pd_faixas: dict[str, Any],
    pd_cpura_config: dict[str, Any] | None = None,
    logger: Any | None = None,
    peer_group: list[float] | None = None,
    pd_transform_rules: dict[str, Any] | None = None,
    rating_final: str | None = None,
) -> dict[str, Any]:
    """Transforma a PD base conforme a metodologia do segmento."""
    segmento = str(segmento_pd or "").strip().upper()

    if segmento == "CPURA":
        rating = str(
            registro.get("RATING_FINAL") or rating_final or ""
        ).strip().upper()

        if not rating:
            raise PdConfigurationError(
                "RATING_FINAL não informado para CPURA.")

        pd_min, pd_max = _obter_faixa_pd(
            pd_faixas=pd_faixas,
            segmento_pd=segmento,
            rating_final=rating,
        )

        return calcular_pd_final_cpura(
            registro=registro,
            pd_base=pd_base,
            rating_final=rating,
            pd_min=pd_min,
            pd_max=pd_max,
            cpura_config=pd_cpura_config or {},
            logger=logger,
        )

    if segmento == "CGRUPO":
        if not pd_transform_rules:
            raise PdConfigurationError(
                "pd_transform_rules não informado para CGRUPO."
            )

        registro_calculo = dict(registro)
        registro_calculo["PD_BASE"] = pd_base

        return calcular_pd_final_cgrupo(
            registro=registro_calculo,
            regras_segmento=pd_transform_rules["CGRUPO"],
            logger=logger,
        )

    if segmento == "CONSUMIDOR_GT_5":
        rating = str(
            registro.get("RATING_FINAL")
            or registro.get("RATING_COPEL")
            or rating_final
            or ""
        ).strip().upper()

        if not rating:
            raise PdConfigurationError(
                "RATING_FINAL não informado para CONSUMIDOR_GT_5."
            )

        pd_min, pd_max = _obter_faixa_pd(
            pd_faixas=pd_faixas,
            segmento_pd=segmento,
            rating_final=rating,
        )

        if not pd_transform_rules or segmento not in pd_transform_rules:
            raise PdConfigurationError(
                "pd_transform_rules não informado para CONSUMIDOR_GT_5."
            )

        return calcular_pd_final_consumidor_gt5(
            registro=registro,
            pd_base=pd_base,
            rating_final=rating,
            pd_min=pd_min,
            pd_max=pd_max,
            regras_segmento=pd_transform_rules[segmento],
            logger=logger,
        )
        
    if segmento == "CONSUMIDOR_LE_5":
        rating = str(
            registro.get("RATING_FINAL")
            or registro.get("RATING_COPEL")
            or rating_final
            or ""
        ).strip().upper()

        if not rating:
            raise PdConfigurationError(
                "RATING_FINAL não informado para CONSUMIDOR_LE_5."
            )

        pd_min, pd_max = _obter_faixa_pd(
            pd_faixas=pd_faixas,
            segmento_pd=segmento,
            rating_final=rating,
        )

        if not pd_transform_rules or segmento not in pd_transform_rules:
            raise PdConfigurationError(
                "pd_transform_rules não informado para CONSUMIDOR_LE_5."
            )

        return calcular_pd_final_consumidor_le5(
            registro=registro,
            pd_faixas=pd_faixas,
            logger=logger,
        )

    raise PdCalculationError(
        f"Segmento PD não suportado para transformação: {segmento}"
    )
