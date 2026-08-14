"""Regras de deduplicação e atualização incremental do sistema."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def has_duplicate_hash(
    history: list[dict[str, Any]],
    hash_value: str | None,
) -> bool:
    """Indica se o hash já foi processado anteriormente."""
    if not hash_value:
        return False

    return any(item.get("hash_arquivo") == hash_value for item in history)


def has_duplicate_business_key(
    history: list[dict[str, Any]],
    cnpj: str | None,
    data_demonstracao_financeira: str | None,
) -> bool:
    """Indica se a chave de negócio já existe com sucesso."""
    if not cnpj or not data_demonstracao_financeira:
        return False

    for item in history:
        if item.get("status_extracao") != "SUCESSO":
            continue

        if item.get("cnpj_extraido") != cnpj:
            continue

        if (
            item.get("data_demonstracao_financeira")
            != data_demonstracao_financeira
        ):
            continue

        return True

    return False


def upsert_business_key_in_history(
    history: list[dict[str, Any]],
    manifest_record: dict[str, Any],
) -> None:
    """Atualiza o histórico em memória com a chave de negócio corrente.

    Em modo reprocess, MARCA registros anteriores como SUBSTITUIDO
    em vez de removê-los, preservando o histórico completo (§1.5 — imutabilidade).
    """
    load_mode = manifest_record.get("load_mode")
    cnpj = manifest_record.get("cnpj_extraido")
    data_df = manifest_record.get("data_demonstracao_financeira")

    if load_mode == "reprocess" and cnpj and data_df:
        for item in history:
            if (
                item.get("status_extracao") == "SUCESSO"
                and item.get("cnpj_extraido") == cnpj
                and item.get("data_demonstracao_financeira") == data_df
            ):
                item["status_extracao"] = "SUBSTITUIDO"
                item["dt_substituicao"] = datetime.now().isoformat(timespec="seconds")

    history.append(manifest_record)
