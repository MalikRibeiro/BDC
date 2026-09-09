"""Motor de Loss Given Default (LGD).

feat(T3.3.1): Adicionados lookup de LGD bruta por segmento via config e
rastreabilidade com calculo_id.
Ref: §6.8, §7.1, Apêndice C do Planejamento Funcional.

Nota: A redução por garantias é recebida como parâmetro (cobertura_garantias).
A integração com a base real de garantias é um TODO — quando disponível,
o percentual será calculado automaticamente a partir de garantias_service.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import uuid4

LGD_BRUTA_POR_SEGMENTO: dict[str, float] = {
    "CPURA": 0.45,
    "CGRUPO": 0.45,
    "CONSUMIDOR_GT_5": 0.45,
    "CONSUMIDOR_LE_5": 0.75,
}


def calcular_lgd(
    segmento: str,
    cobertura_garantias: float = 0.0,
    lgd_bruta_override: float | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Cálculo da LGD líquida após mitigação por garantias.

    Fórmula: LGD_liquida = LGD_bruta × (1 - cobertura_garantias) (§6.8).

    Args:
        segmento: Segmento metodológico (CPURA, CGRUPO, etc.).
        cobertura_garantias: Percentual de cobertura de garantias elegíveis [0, 1].
            Default 0.0 — TODO: será alimentado automaticamente pela base de garantias.
        lgd_bruta_override: Se informado, sobrescreve o lookup por segmento.
        config: Dict de configuração para lookup customizado.

    Returns:
        Dict rastreável com calculo_id, lgd_bruta, lgd_liquida e metadados.
    """
    calculo_id = f"LGD_{uuid4().hex[:12]}"

    if lgd_bruta_override is not None:
        lgd_bruta = lgd_bruta_override
        fonte_lgd_bruta = "OVERRIDE"
    elif config and "lgd_bruta_por_segmento" in config:
        lgd_bruta = config["lgd_bruta_por_segmento"].get(segmento, LGD_BRUTA_POR_SEGMENTO.get(segmento, 0.45))
        fonte_lgd_bruta = "CONFIG"
    else:
        lgd_bruta = LGD_BRUTA_POR_SEGMENTO.get(segmento, 0.45)
        fonte_lgd_bruta = "PADRAO_SISTEMA"

    cobertura_efetiva = max(0.0, min(float(cobertura_garantias), 1.0))

    lgd_liquida = lgd_bruta * (1.0 - cobertura_efetiva)

    config_usada = {
        "segmento": segmento,
        "lgd_bruta": lgd_bruta,
        "fonte_lgd_bruta": fonte_lgd_bruta,
        "cobertura_garantias": cobertura_efetiva,
    }
    config_snapshot_id = hashlib.sha256(
        json.dumps(config_usada, sort_keys=True).encode()
    ).hexdigest()[:16]

    return {
        "calculo_id": calculo_id,
        "segmento": segmento,
        "lgd_bruta": lgd_bruta,
        "fonte_lgd_bruta": fonte_lgd_bruta,
        "cobertura_garantias": cobertura_efetiva,
        "lgd_liquida": lgd_liquida,
        "config_snapshot_id": config_snapshot_id,
        "dt_calculo": datetime.now().isoformat(timespec="seconds"),
        "status": "CALCULADO",
    }