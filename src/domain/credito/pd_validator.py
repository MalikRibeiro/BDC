"""Validação dos insumos do cálculo de PD ajustada."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from common.numeros import to_percentual_br
from domain.credito.pd_exceptions import PdInputValidationError, PdCalculationError


def validar_probabilidade(valor: Any) -> float | None:
    """Aplica regra de negócio: normaliza e garante range de [0, 1]."""
    perc = to_percentual_br(valor)
    if perc is None:
        return None
    if perc > 1.0:
        return None
    return perc


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    texto = str(value).strip().upper()
    return texto in {"", "N/A", "NA", "N.D.", "ND", "NONE", "NULL"}


def validar_insumos_pd(
    registro: dict[str, Any],
    segmento_pd: str,
) -> None:
    """Valida os insumos mínimos para cálculo de PD ajustada."""
    if not segmento_pd:
        raise PdInputValidationError("SEGMENTO_PD não informado.")
    
    if segmento_pd == "CONSUMIDOR_LE_5":
        if registro.get("SCORE_BUREAU") is None:
            raise PdInputValidationError("SCORE_BUREAU não informado para CONSUMIDOR_LE_5.")
        return

    pd_base_raw = registro.get("PROBABILIDADE_DEFAULT")
    pd_base = validar_probabilidade(pd_base_raw)

    if pd_base is None:
        raise PdInputValidationError("PROBABILIDADE_DEFAULT não informada.")

    if pd_base < 0:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT negativa: {pd_base_raw!r}"
        )

    if segmento_pd == "CGRUPO":
        agencia = registro.get("AGENCIA")
        nota_credito = registro.get("NOTA_CREDITO")
        rating_interno = registro.get(
            "RATING_FINAL") or registro.get("RATING_COPEL")

        tem_rating_publico = not _is_blank(
            agencia) and not _is_blank(nota_credito)
        tem_rating_interno = not _is_blank(rating_interno)

        if not tem_rating_publico and not tem_rating_interno:
            raise PdInputValidationError(
                "CGRUPO sem rating público (AGENCIA/NOTA_CREDITO) "
                "e sem rating interno (RATING_FINAL/RATING_COPEL)."
            )

    else:
        rating = (
            registro.get("RATING_COPEL")
            or registro.get("NOTA_CREDITO")
            or registro.get("RATING_FINAL")
        )

        if not _is_blank(rating):
            rating_normalizado = normalizar_texto(str(rating))
            ratings_validos = {"A", "B", "C", "D", "E"}

            if rating_normalizado not in ratings_validos:
                raise PdInputValidationError(
                    f"Rating inválido para {segmento_pd}: {rating_normalizado!r}"
                )

    if segmento_pd in {"CPURA", "CGRUPO"}:
        tipo_comercializadora = normalizar_texto(
            str(registro.get("TIPO_COMERCIALIZADORA", ""))
        )
        if tipo_comercializadora not in {"CPURA", "CGRUPO"}:
            raise PdInputValidationError(
                "TIPO_COMERCIALIZADORA inválido ou ausente."
            )
    if segmento_pd == "CONSUMIDOR_GT_5":
        pd_base = registro.get("PROBABILIDADE_DEFAULT")
        rating = registro.get("RATING_FINAL") or registro.get("RATING_COPEL")

        if _is_blank(pd_base):
            raise PdCalculationError(
                "PROBABILIDADE_DEFAULT não informada para CONSUMIDOR_GT_5."
            )

        if _is_blank(rating):
            raise PdCalculationError(
                "RATING_FINAL/RATING_COPEL não informado para CONSUMIDOR_GT_5."
            )

        rating_norm = normalizar_texto(rating)
        if rating_norm not in {"A", "B", "C", "D", "E"}:
            raise PdCalculationError(
                f"Rating inválido para CONSUMIDOR_GT_5: {rating_norm!r}"
            )
        return
