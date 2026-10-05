"""Módulo de Validação Paralela (Auditoria Sombra) do Motor de Crédito.

Em conformidade com a Nota Técnica v7, o Planejamento Operacional v1.2 e as
regras de governança do BDC:
1. O valor extraído da ficha Excel é a autoridade soberana oficial para concessão e relatórios.
2. O recálculo estatístico e de réguas em Python atua como auditoria e contraprova.
3. Divergências numéricas geram status de conciliação e alertas sem interromper a esteira.
"""

from __future__ import annotations

import math
from typing import Any, Tuple


def validar_paralelamente_pd_e_rating(
    pd_calculada: float | None,
    pd_declarada: float | None,
    rating_calculado: str | None,
    rating_declarado: str | None,
    tol_absoluta: float = 1e-6,
    tol_arredondamento: float = 5e-4,
    logger: Any | None = None,
    cnpj: str | None = None,
) -> dict[str, Any]:
    """Confronta o cálculo em Python (NT v7) contra a declaração da ficha Excel.

    Retorna um dicionário com:
    - PD_OFICIAL: valor oficial soberano (ficha original)
    - RATING_OFICIAL: rating oficial soberano (ficha original)
    - PD_CALCULADA: valor recalculado pelo motor Python
    - RATING_CALCULADO: rating recalculado pelo motor Python
    - STATUS_CONCILIACAO_PD: 'CONCILIADO' | 'DIVERGENCIA_ARREDONDAMENTO' | 'DIVERGENCIA_ORIGEM' | 'NAO_VALIDAVEL'
    - STATUS_CONCILIACAO_RATING: 'CONCILIADO' | 'DIVERGENCIA_ORIGEM' | 'NAO_VALIDAVEL'
    - DELTA_PD: float | None
    """
    resultado = {
        "PD_OFICIAL": pd_declarada if pd_declarada is not None else pd_calculada,
        "RATING_OFICIAL": rating_declarado if rating_declarado is not None else rating_calculado,
        "PD_CALCULADA": pd_calculada,
        "RATING_CALCULADO": rating_calculado,
        "STATUS_CONCILIACAO_PD": "NAO_VALIDAVEL",
        "STATUS_CONCILIACAO_RATING": "NAO_VALIDAVEL",
        "DELTA_PD": None,
    }

    # Validação de PD
    if pd_calculada is not None and pd_declarada is not None:
        delta = abs(pd_calculada - pd_declarada)
        resultado["DELTA_PD"] = delta

        if delta <= tol_absoluta:
            resultado["STATUS_CONCILIACAO_PD"] = "CONCILIADO"
        elif delta <= tol_arredondamento:
            resultado["STATUS_CONCILIACAO_PD"] = "DIVERGENCIA_ARREDONDAMENTO"
            if logger is not None:
                logger.debug(
                    "[CONCILIACAO] CNPJ=%s: Leve divergência de arredondamento na PD: calc=%.6f vs decl=%.6f (delta=%.6f)",
                    cnpj, pd_calculada, pd_declarada, delta
                )
        else:
            resultado["STATUS_CONCILIACAO_PD"] = "DIVERGENCIA_ORIGEM"
            if logger is not None:
                logger.warning(
                    "[AUDITORIA_SOMBRA] CNPJ=%s: Divergência material na PD: calc=%.6f vs decl=%.6f (delta=%.6f). Origem mantida.",
                    cnpj, pd_calculada, pd_declarada, delta
                )
    elif pd_declarada is not None:
        resultado["STATUS_CONCILIACAO_PD"] = "APENAS_ORIGEM_PRESENTE"
    elif pd_calculada is not None:
        resultado["STATUS_CONCILIACAO_PD"] = "APENAS_CALCULO_PRESENTE"

    # Validação de Rating
    if rating_calculado and rating_declarado:
        if rating_calculado.strip().upper() == rating_declarado.strip().upper():
            resultado["STATUS_CONCILIACAO_RATING"] = "CONCILIADO"
        else:
            resultado["STATUS_CONCILIACAO_RATING"] = "DIVERGENCIA_ORIGEM"
            if logger is not None:
                logger.warning(
                    "[AUDITORIA_SOMBRA] CNPJ=%s: Divergência de Rating: calc=%s vs decl=%s. Origem mantida.",
                    cnpj, rating_calculado, rating_declarado
                )
    elif rating_declarado:
        resultado["STATUS_CONCILIACAO_RATING"] = "APENAS_ORIGEM_PRESENTE"
    elif rating_calculado:
        resultado["STATUS_CONCILIACAO_RATING"] = "APENAS_CALCULO_PRESENTE"

    return resultado
