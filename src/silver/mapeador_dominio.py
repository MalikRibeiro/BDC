from __future__ import annotations

import json
from typing import Any

from app.context import AppContext
from common.dominio import (
    normalizar_agencia,
    normalizar_auditor,
    normalizar_rating,
)


def aplicar_normalizacao_de_dominio(
    registro: dict[str, Any],
    context: AppContext,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Aplica regras semânticas de domínio (auditor, agência, etc.) sobre o registro."""
    out = dict(registro)

    try:
        dict_path = context.control_file("domain_dictionaries")
        with open(dict_path, encoding="utf-8") as f:
            dicionarios = json.load(f)
    except Exception as exc:
        if logger:
            logger.warning("Não foi possível carregar dicionários de domínio: %s", exc)
        return out

    if "AUDITOR" in out and out["AUDITOR"] is not None:
        try:
            out["AUDITOR"] = normalizar_auditor(
                out["AUDITOR"],
                dicionarios.get("AUDITOR", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar AUDITOR: %s", exc)

    if "AGENCIA" in out and out["AGENCIA"] is not None:
        try:
            out["AGENCIA"] = normalizar_agencia(
                out["AGENCIA"],
                dicionarios.get("AGENCIA", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar AGENCIA: %s", exc)

    if "NOTA_CREDITO" in out and out["NOTA_CREDITO"] is not None:
        try:
            out["NOTA_CREDITO"] = normalizar_rating(
                out["NOTA_CREDITO"],
                dicionarios.get("NOTA_CREDITO", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar NOTA_CREDITO: %s", exc)
                
    if "RATING_COPEL" in out and out["RATING_COPEL"] is not None:
        try:
            out["RATING_COPEL"] = normalizar_rating(
                out["RATING_COPEL"],
                dicionarios.get("RATING_COPEL", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar RATING_COPEL: %s", exc)

    if "RATING_BOARD_COPEL" in out and out["RATING_BOARD_COPEL"] is not None:
        try:
            out["RATING_BOARD_COPEL"] = normalizar_rating(
                out["RATING_BOARD_COPEL"],
                dicionarios.get("RATING_BOARD_COPEL", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar RATING_BOARD_COPEL: %s", exc)

    if "RATING_BUREAU" in out and out["RATING_BUREAU"] is not None:
        try:
            out["RATING_BUREAU"] = normalizar_rating(
                out["RATING_BUREAU"],
                dicionarios.get("RATING_BUREAU", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar RATING_BUREAU: %s", exc)

    return out
