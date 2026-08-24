from __future__ import annotations

from typing import Any

from domain.credito.pd_exceptions import PdCalculationError


RATING_ORDER = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


def _norm(value: Any) -> str:
    return str(value or "").strip().upper()


def _norm_agencia(value: Any) -> str:
    agencia = _norm(value)

    mapa = {
        "FITCH": "FITCH",
        "FITCH RATINGS": "FITCH",
        "MOODYS": "MOODYS",
        "MOODY'S": "MOODYS",
        "MOODY S": "MOODYS",
        "SP": "SP",
        "S&P": "SP",
        "STANDARD & POOR'S": "SP",
        "STANDARD & POORS": "SP",
        "STANDARD AND POOR'S": "SP",
        "STANDARD AND POORS": "SP",
    }
    return mapa.get(agencia, agencia)


def _norm_rating(value: Any) -> str:
    return _norm(value)


def _mapear_rating_externo(
    agencia: str,
    rating_externo: str,
    regras_rating: dict[str, Any],
) -> str:
    ag = _norm_agencia(agencia)
    rt = _norm(rating_externo)

    short_default = {_norm(x)
                     for x in regras_rating["short_term_or_default_markers"]}
    if rt in short_default:
        return regras_rating["default_class"]

    agencias = regras_rating["agencias"]
    if ag not in agencias:
        return regras_rating["default_class"]

    for rating_copel, lista_externa in agencias[ag].items():
        if rt in {_norm(x) for x in lista_externa}:
            return rating_copel

    return regras_rating["default_class"]


def _resolver_rating_cgrupo(
    registro: dict[str, Any],
    regras_segmento: dict[str, Any],
) -> tuple[str, str]:
    regras_rating = regras_segmento["rating_externo"]

    agencia = registro.get("AGENCIA")
    rating = registro.get("NOTA_CREDITO")

    if agencia and rating:
        rating_convertido = _mapear_rating_externo(
            agencia=agencia,
            rating_externo=rating,
            regras_rating=regras_rating,
        )
        return rating_convertido, "RATING_PUBLICO"

    rating_interno = _norm(registro.get("RATING_FINAL")
                           or registro.get("RATING_COPEL"))
    if rating_interno not in {"A", "B", "E"}:
        raise PdCalculationError(
            f"Rating interno inválido para CGRUPO: {rating_interno!r}"
        )

    return rating_interno, "RATING_INTERNO"


def _pior_rating(ratings: list[str]) -> str:
    validos = [r for r in ratings if r in RATING_ORDER]
    if not validos:
        raise PdCalculationError(
            "Nenhum rating válido encontrado para CGRUPO."
        )
    return max(validos, key=lambda x: RATING_ORDER[x])


def _percentil_empirico(pd_base, peer_group):
    n = len(peer_group)

    if n <= 1:
        return 0.5

    menores = sum(1 for x in peer_group if x < pd_base)
    iguais = sum(1 for x in peer_group if x == pd_base)

    return (menores + 0.5 * iguais) / n


def _interpolar_pd(pd_min: float, pd_max: float, u: float) -> float:
    return pd_min + u * (pd_max - pd_min)


def calcular_pd_final_cgrupo(
    registro: dict[str, Any],
    regras_segmento: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    pd_base = float(registro["PD_BASE"])
    rating, fonte_rating = _resolver_rating_cgrupo(registro, regras_segmento)

    regras_pd = regras_segmento["pd_final_rules"]
    fixed_pd = regras_pd.get("fixed_pd_by_rating", {})

    if rating in fixed_pd:
        pd_final = float(fixed_pd[rating])
        return {
            "RATING_FINAL": rating,
            "FONTE_RATING": fonte_rating,
            "PD_MIN_FAIXA": 0.0,
            "PD_MAX_FAIXA": pd_final,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": pd_final,
            "PD_METODO": "FIXED_PD",
        }

    faixa = regras_pd["faixas_pd"][rating]
    pd_min = float(faixa["min"])
    pd_max = float(faixa["max"])

    pd_final = min(max(pd_base, pd_min), pd_max)

    return {
        "RATING_FINAL": rating,
        "FONTE_RATING": fonte_rating,
        "PD_MIN_FAIXA": pd_min,
        "PD_MAX_FAIXA": pd_max,
        "PERCENTIL_PD_BASE": None,
        "PD_FINAL": pd_final,
        "PD_METODO": "CLAMP",
    }
