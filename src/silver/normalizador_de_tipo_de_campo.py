"""Normalização técnica das fichas."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from pathlib import Path

from app.context import AppContext
from silver.normalizadores import (
    normalizar_data,
    normalizar_string,
    normalizar_float,
    normalizar_data_demonstracao_financeira,
    padronizar_cnpj
)
from common.json import ler_json
from control.field_types import obter_config_tipo_campo

def _obter_campos(field_types: dict[str, Any], key: str) -> list[str]:
    """Obtém uma lista de campos do JSON de tipos (Usado apenas no fallback)."""
    value = field_types.get(key, [])

    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(
            f"Configuração inválida em '{key}': esperado list, recebido {type(value).__name__}."
        )

    return [str(item).strip() for item in value if str(item).strip()]

def normalizar_registro(
    record: dict[str, Any],
    context: AppContext,
    slug: str,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Normaliza o registro bruto extraído da ficha."""
    try:
        config_class = obter_config_tipo_campo(slug)

        if config_class:
            if logger: logger.info("Carregando tipagem da classe Python: %s", slug)
            date_fields = config_class.date_fields
            float_fields = config_class.float_fields
            text_fields = config_class.text_fields
            cnpj_fields = config_class.cnpj_fields
        else:
            if logger: logger.info("Classe Python não encontrada. Fallback: %s", slug)
            
            # ADAPTAÇÃO PARA O MASTER CATALOG:
            if slug in ("field_types_fichas_comercializadoras", "master_catalog_comercializadoras"):
                try:
                    master_catalog_path = context.control_file("schema_data_quality_rules").parent / "master_catalog_comercializadoras.json"
                    catalog = ler_json(master_catalog_path)
                except Exception:
                    # Caminho rígido como fallback caso o context.control_file falhe
                    catalog = ler_json(Path("ENTRADAS/control/quality/master_catalog_comercializadoras.json"))
                
                fields = catalog.get("fields", {})
                date_fields = [k for k, v in fields.items() if v.get("type") == "date"]
                float_fields = [k for k, v in fields.items() if v.get("type") == "float"]
                text_fields = [k for k, v in fields.items() if v.get("type") in ("string", "text")]
                cnpj_fields = [k for k, v in fields.items() if v.get("type") == "cnpj"]
            else:
                field_types_path = context.control_file(slug)
                field_types = ler_json(field_types_path)

                date_fields = _obter_campos(field_types, "date_fields")
                float_fields = _obter_campos(field_types, "float_fields")
                text_fields = _obter_campos(field_types, "text_fields")
                cnpj_fields = _obter_campos(field_types, "cnpj_fields")

        out = dict(record)
        
        for field in cnpj_fields:
            if field in out:
                try:
                    c_14, c_raiz, c_status = padronizar_cnpj(out.get(field))
                    if c_14 is not None and c_status == "CNPJ_VALIDO":
                        out[field] = c_14
                        if field == "CNPJ":
                            out["CNPJ_RAIZ"] = c_raiz
                            out["STATUS_CNPJ"] = c_status
                    else:
                        out[field] = None
                        if field == "CNPJ":
                            out["CNPJ_RAIZ"] = None
                            out["STATUS_CNPJ"] = c_status
                except Exception as exc:
                    if logger: logger.exception("Erro CNPJ: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo CNPJ '{field}'.") from exc

        for field in date_fields:
            if field in out:
                try:
                    if field == "DATA_DEMONSTRACAO_FINANCEIRA":
                        val_norm, epoch_orig, was_corrected = normalizar_data_demonstracao_financeira(out.get(field))
                        out[field] = val_norm
                        out["FLAG_DATA_DF_CORRIGIDA"] = was_corrected
                        out["DATA_DF_EPOCH_ORIGINAL"] = epoch_orig
                    else:
                        out[field] = normalizar_data(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Data: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo de data '{field}'.") from exc

        for field in float_fields:
            if field in out:
                try:
                    out[field] = normalizar_float(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Float: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo numérico '{field}'.") from exc

        for field in text_fields:
            if field in out and out.get(field) is not None:
                try:
                    out[field] = normalizar_string(out.get(field))
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