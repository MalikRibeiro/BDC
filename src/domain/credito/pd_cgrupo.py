from __future__ import annotations

from typing import Any

from domain.credito.pd_exceptions import PdCalculationError


RATING_ORDER = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


def _norm(value: Any) -> str:
    return str(value or "").strip().upper()


def _norm_agencia(value: Any) -> str:
    agencia = _norm(value)

    # A normalização de aliases já ocorreu na camada Silver via domain_dictionaries.json.
    # Aqui, garantimos apenas a consistência básica.
    return agencia


def _norm_rating(value: Any) -> str:
    return _norm(value)


def _mapear_rating_externo(
    agencia: str,
    rating_externo: str,
    regras_rating: dict[str, Any],
) -> str | None:
    ag = _norm_agencia(agencia)
    rt = _norm(rating_externo)

    if not rt or not ag:
        return None

    short_default = {_norm(x)
                     for x in regras_rating.get("short_term_or_default_markers", [])}
    if rt in short_default:
        return regras_rating.get("default_class", "E")

    agencias = regras_rating.get("agencias", {})
    if ag not in agencias:
        return None

    for rating_copel, lista_externa in agencias[ag].items():
        if rt in {_norm(x) for x in lista_externa}:
            return rating_copel

    return None


def _resolver_rating_cgrupo(
    registro: dict[str, Any],
    regras_segmento: dict[str, Any],
) -> tuple[str | None, str | None]:
    # Prioridade 1: Rating interno / Copel já determinado na Ficha Silver
    rating_copel = _norm(registro.get("RATING_COPEL") or registro.get("RATING"))
    if rating_copel in {"A", "B", "C", "D", "E"}:
        return rating_copel, "RATING_INTERNO"

    regras_rating = regras_segmento.get("rating_externo", {})

    agencia = registro.get("AGENCIA")
    rating = registro.get("NOTA_CREDITO")

    if agencia and rating and regras_rating:
        rating_convertido = _mapear_rating_externo(
            agencia=agencia,
            rating_externo=rating,
            regras_rating=regras_rating,
        )
        if rating_convertido:
            return rating_convertido, "RATING_PUBLICO"

    rating_interno = _norm(registro.get("RATING_FINAL") or registro.get("RATING_PUBLICO"))
    if rating_interno in {"A", "B", "C", "D", "E"}:
        return rating_interno, "RATING_INTERNO"

    # Ausência de rating não é mascarada: retorna nulo para governança e carga manual
    return None, None


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
    rating_macro, fonte_rating = _resolver_rating_cgrupo(registro, regras_segmento)
    regras_pd = regras_segmento.get("pd_final_rules", {})
    pd_tabela = regras_pd.get("pd_tabela", {})

    pd_raw = registro.get("PROBABILIDADE_DEFAULT")
    pd_ficha = None
    if pd_raw is not None and str(pd_raw).strip() not in ("", "None", "nan", "<NA>"):
        try:
            from common.numeros import to_float_br
            pd_parsed = to_float_br(pd_raw)
            if pd_parsed is not None and pd_parsed >= 0:
                pd_ficha = pd_parsed
        except Exception:
            pass

    if rating_macro is None:
        return {
            "RATING_FINAL": None,
            "FONTE_RATING": None,
            "PD_MIN_FAIXA": None,
            "PD_MAX_FAIXA": None,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": None,
            "PD_METODO": "SEM_DADOS",
        }

    if fonte_rating == "RATING_PUBLICO":
        rating_lookup = str(registro.get("NOTA_CREDITO") or "").strip().upper()
    else:
        rating_lookup = rating_macro

    if rating_lookup in pd_tabela:
        pd_final = float(pd_tabela[rating_lookup])
        metodo = "LOOKUP_TABELA"
    else:
        pd_final = None
        metodo = "RATING_SEM_PD"

    if pd_ficha is not None:
        pd_final = pd_ficha
        metodo = "FICHA_ORIGEM"

    return {
        "RATING_FINAL": rating_macro,
        "FONTE_RATING": fonte_rating,
        "PD_MIN_FAIXA": pd_final,
        "PD_MAX_FAIXA": pd_final,
        "PERCENTIL_PD_BASE": None,
        "PD_FINAL": pd_final,
        "PD_METODO": metodo,
    }
