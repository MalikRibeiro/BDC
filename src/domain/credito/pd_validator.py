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
    try:
        import pandas as _pd
        if _pd.isna(value):
            return True
    except Exception:
        pass
    texto = str(value).strip().upper()
    return texto in {"", "N/A", "NA", "N.D.", "ND", "NONE", "NULL", "NAN", "NAT"}


def validar_insumos_pd(
    registro: dict[str, Any],
    segmento_pd: str,
) -> None:
    """Valida os insumos mínimos para cálculo de PD ajustada."""
    if not segmento_pd:
        raise PdInputValidationError("SEGMENTO_PD não informado.")
    
    if segmento_pd == "CONSUMIDOR_LE_5":
        # Ausência de SCORE_BUREAU em CONSUMIDOR_LE_5 não interrompe o motor com exceção;
        # Permite que o motor retorne status PENDENTE e PD nula, preservando a governança.
        return

    pd_base_raw = registro.get("PROBABILIDADE_DEFAULT")
    pd_base = validar_probabilidade(pd_base_raw) if pd_base_raw is not None else None

    if pd_base is not None and pd_base < 0:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT negativa: {pd_base_raw!r}"
        )

    if segmento_pd == "CGRUPO":
        # Ausência de rating ou PD em CGRUPO não interrompe o motor com exceção;
        # Permite que o motor retorne campos nulos preservando a auditoria.
        pass
    else:
        rating = (
            registro.get("RATING_COPEL")
            or registro.get("NOTA_CREDITO")
            or registro.get("RATING_FINAL")
        )

        if not _is_blank(rating):
            rating_normalizado = normalizar_texto(str(rating))
            ratings_validos = {"A", "B", "C", "D", "E"}

            if rating_normalizado is not None and rating_normalizado not in ratings_validos:
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
