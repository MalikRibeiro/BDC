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


def derivar_rating_por_pd(
    pd_valor: float | None,
    segmento_pd: str,
    pd_faixas: dict[str, Any] | None = None,
) -> str | None:
    """Deriva a letra do Rating a partir do valor de PD e das réguas de pd_faixas.json."""
    if pd_valor is None:
        return None
    try:
        from common.numeros import to_float_br
        pd_num = to_float_br(pd_valor) if isinstance(pd_valor, str) else float(pd_valor)
    except (TypeError, ValueError):
        return None

    if pd_num is None:
        return None

    if not pd_faixas or not isinstance(pd_faixas, dict):
        return None

    seg = str(segmento_pd).strip().upper()
    faixas_seg = pd_faixas.get(seg)
    if not faixas_seg:
        if "CGRUPO" in seg or "GRUPO" in seg:
            faixas_seg = pd_faixas.get("CGRUPO")
        elif "GT_5" in seg:
            faixas_seg = pd_faixas.get("CONSUMIDOR_GT_5")
        elif "LE_5" in seg:
            faixas_seg = pd_faixas.get("CONSUMIDOR_LE_5")
        else:
            faixas_seg = pd_faixas.get("CPURA")

    if not isinstance(faixas_seg, dict):
        return None

    for r_letra, r_range in faixas_seg.items():
        try:
            r_min = float(r_range["min"])
            r_max = float(r_range["max"])
            if r_min <= pd_num <= r_max:
                return r_letra
        except Exception:
            continue

    if pd_num > 0.10:
        return "E"
    if pd_num >= 0.0:
        return "A"
    return None


def _obter_rating_pronto(
    registro: dict[str, Any],
    segmento_pd: str,
    pd_faixas: dict[str, Any] | None = None,
) -> str:
    """Obtém rating já existente no registro ou deriva da PD via faixas oficiais."""
    rating = (
        registro.get("RATING_COPEL")
        or registro.get("NOTA_CREDITO")
        or registro.get("RATING_FINAL")
    )

    if rating is None or str(rating).strip() in ("", "None", "nan", "<NA>"):
        # Fallback: derivar pela PD se presente no registro (caso Axia/Eletrobras)
        pd_candidata = (
            registro.get("PD_BASE")
            or registro.get("PD_PERCENTUAL")
            or registro.get("PROBABILIDADE_DEFAULT")
            or registro.get("PD_FINAL")
        )
        if pd_candidata is not None:
            r_derivado = derivar_rating_por_pd(pd_candidata, segmento_pd, pd_faixas)
            if r_derivado:
                return r_derivado

        raise PdInputValidationError(
            f"Registro sem rating para {segmento_pd}."
        )

    rating_final = normalizar_texto(rating)

    validos = {"A", "B", "C", "D", "E"} if segmento_pd == "CGRUPO" else {
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
    pd_faixas: dict[str, Any] | None = None,
) -> str:
    """Determina o rating final conforme o segmento."""
    segmento_pd = str(segmento_pd).strip().upper()

    if segmento_pd in ("CPURA", "CONSUMIDOR_GT_5"):
        if not pd_cpura_config:
            raise PdConfigurationError(
                f"pd_cpura_config não informado para cálculo do rating de {segmento_pd}."
            )

        score_faixas = pd_cpura_config.get("score_faixas")
        return _calcular_rating_final_cpura(
            registro=registro,
            cpura_score_faixas=score_faixas,
        )

    return _obter_rating_pronto(
        registro=registro,
        segmento_pd=segmento_pd,
        pd_faixas=pd_faixas,
    )

