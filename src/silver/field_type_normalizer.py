"""Normalização técnica das fichas."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from app.context import AppContext
from common.dates import normalize_date
from common.io_json import read_json
from common.strings import normalize_cnpj, normalize_string
from common.types import normalize_float
from control.field_types import get_field_type_config


def _get_fields(field_types: dict[str, Any], key: str) -> list[str]:
    """Obtém uma lista de campos do JSON de tipos (Usado apenas no fallback)."""
    value = field_types.get(key, [])

    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(
            f"Configuração inválida em '{key}': "
            f"esperado list, recebido {type(value).__name__}."
        )

    return [str(item).strip() for item in value if str(item).strip()]


def normalize_data_demonstracao_financeira(value: Any) -> str | None:
    """Normaliza DATA_DEMONSTRACAO_FINANCEIRA para dd/mm/aaaa."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    if re.fullmatch(r"\d{4}", text):
        return f"31/12/{text}"

    text = text.split()[0]

    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]

    for fmt in formatos:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            continue

    return None


def normalize_record(
    record: dict[str, Any],
    context: AppContext,
    slug: str,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Normaliza o registro bruto extraído da ficha."""
    try:
        # T1.3.1: Uso da Classe Python Tipada com prioridade sobre o JSON
        config_class = get_field_type_config(slug)

        if config_class:
            if logger is not None:
                logger.info("Carregando tipagem da classe Python: %s", slug)
            date_fields = config_class.date_fields
            float_fields = config_class.float_fields
            text_fields = config_class.text_fields
            cnpj_fields = config_class.cnpj_fields
        else:
            if logger is not None:
                logger.info("Classe Python não encontrada. Fallback para JSON: %s", slug)
            field_types_path = context.control_file(slug)
            field_types = read_json(field_types_path)

            date_fields = _get_fields(field_types, "date_fields")
            float_fields = _get_fields(field_types, "float_fields")
            text_fields = _get_fields(field_types, "text_fields")
            cnpj_fields = _get_fields(field_types, "cnpj_fields")

        out = dict(record)

        for field in cnpj_fields:
            if field in out:
                try:
                    out[field] = normalize_cnpj(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro CNPJ: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo CNPJ '{field}'.") from exc

        for field in date_fields:
            if field in out:
                try:
                    if field == "DATA_DEMONSTRACAO_FINANCEIRA":
                        out[field] = normalize_data_demonstracao_financeira(out.get(field))
                    else:
                        out[field] = normalize_date(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Data: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo de data '{field}'.") from exc

        for field in float_fields:
            if field in out:
                try:
                    out[field] = normalize_float(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Float: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo numérico '{field}'.") from exc

        for field in text_fields:
            if field in out and out.get(field) is not None:
                try:
                    out[field] = normalize_string(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Texto: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo textual '{field}'.") from exc

        if logger is not None:
            logger.info("Registro normalizado (Entrada: %s, Saída: %s).", len(record), len(out))
            
        return out

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha na normalização: CNPJ=%s EMPRESA=%s",
                record.get("CNPJ"), record.get("EMPRESA")
            )
        raise