"""Motor de Exposure at Default (EAD).

feat(T3.2.1): Adicionados fator de conversão parametrizado e rastreabilidade
com calculo_id e config_snapshot_id.
Ref: §6.7 (Exposição), §7.1, §11.2 (Identificadores) do Planejamento Funcional.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import uuid4


def calcular_ead(
    mtm_positivo_total: float | None,
    fator_conversao: float = 1.0,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Cálculo de EAD baseado na exposição positiva de MtM.

    Regra: EAD = max(MtM favorável à Copel, 0) × fator_conversao (§6.7).

    Args:
        mtm_positivo_total: MtM positivo consolidado por contraparte.
        fator_conversao: Fator de conversão de crédito (CCF), default 1.0.
            Deve ser lido de config (ex: config["ead"]["fator_conversao"]).
        config: Dicionário de configuração para snapshot de rastreabilidade (§11.2).

    Returns:
        Dict com calculo_id, ead_valor, config_snapshot_id e metadados.
    """
    calculo_id = f"EAD_{uuid4().hex[:12]}"

    config_usada = {"fator_conversao": fator_conversao}
    config_snapshot_id = hashlib.sha256(
        json.dumps(config_usada, sort_keys=True).encode()
    ).hexdigest()[:16]

    if mtm_positivo_total is None:
        return {
            "calculo_id": calculo_id,
            "ead_valor": None,
            "fator_conversao": fator_conversao,
            "config_snapshot_id": config_snapshot_id,
            "dt_calculo": datetime.now().isoformat(timespec="seconds"),
            "status": "SEM_DADOS_MTM",
        }

    ead_valor = max(float(mtm_positivo_total), 0.0) * fator_conversao

    return {
        "calculo_id": calculo_id,
        "ead_valor": ead_valor,
        "mtm_positivo_input": float(mtm_positivo_total),
        "fator_conversao": fator_conversao,
        "config_snapshot_id": config_snapshot_id,
        "dt_calculo": datetime.now().isoformat(timespec="seconds"),
        "status": "CALCULADO",
    }