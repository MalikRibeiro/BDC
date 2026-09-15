"""Normalização técnica das fichas."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from pathlib import Path

from app.context import AppContext
from common.datas import normalizar_data, normalizar_data_demonstracao_financeira
from common.numeros import to_percentual_br, to_float_br
from common.texto import normalizar_texto
from common.identificadores import normalizar_cnpj



def normalizar_registro(
    record: dict[str, Any],
    catalog: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Normaliza o registro bruto extraído da ficha."""
    try:
        fields = catalog.get("fields", {})
        if not fields:
            raise ValueError("O catálogo fornecido não contém a chave 'fields' ou está vazio. Sem configuração de tipos, a normalização é impossível.")

        date_fields = [k for k, v in fields.items() if v.get("type") == "date"]
        float_fields = [k for k, v in fields.items() if v.get("type") == "float"]
        text_fields = [k for k, v in fields.items() if v.get("type") in ("string", "text")]
        cnpj_fields = [k for k, v in fields.items() if v.get("type") == "cnpj"]

        out = dict(record)
        
        for field in cnpj_fields:
            if field in out:
                try:
                    resultado_cnpj = normalizar_cnpj(out.get(field))
                    if resultado_cnpj.valido:
                        out[field] = resultado_cnpj.cnpj
                        if field == "CNPJ":
                            out["CNPJ_RAIZ"] = resultado_cnpj.raiz
                            out["STATUS_CNPJ"] = resultado_cnpj.status.value
                    else:
                        out[field] = None
                        if field == "CNPJ":
                            out["CNPJ_RAIZ"] = None
                            out["STATUS_CNPJ"] = resultado_cnpj.status.value
                except Exception as exc:
                    if logger: logger.exception("Erro CNPJ: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo CNPJ '{field}'.") from exc

        for field in date_fields:
            if field in out:
                try:
                    if field == "DATA_DEMONSTRACAO_FINANCEIRA":
                        val_norm, epoch_orig, was_corrected = normalizar_data_demonstracao_financeira(out.get(field))
                        out[field] = val_norm
                    else:
                        out[field] = normalizar_data(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Data: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo de data '{field}'.") from exc

        for field in float_fields:
            if field in out:
                try:
                    if field in ("PROBABILIDADE_DEFAULT", "PD", "SCORE_PD"):
                        out[field] = to_percentual_br(out.get(field))
                    else:
                        out[field] = to_float_br(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Float: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo numérico '{field}'.") from exc

        for field in text_fields:
            if field in out and out.get(field) is not None:
                try:
                    out[field] = normalizar_texto(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Texto: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo textual '{field}'.") from exc

        if "CODIGO_CCEE" in out and out["CODIGO_CCEE"]:
            val = str(out["CODIGO_CCEE"]).strip()
            if not val.isnumeric():
                out["CODIGO_CCEE"] = None
            else:
                out["CODIGO_CCEE"] = val

        if "QUANTIDADE_RESTRITIVOS" in out and out["QUANTIDADE_RESTRITIVOS"] is not None:
            try:
                out["QUANTIDADE_RESTRITIVOS"] = int(float(out["QUANTIDADE_RESTRITIVOS"]))
            except (ValueError, TypeError):
                out["QUANTIDADE_RESTRITIVOS"] = None

        if "CATEGORIA" in out and out.get("CATEGORIA"):
            tipo_comercializadora = str(out.get("TIPO_COMERCIALIZADORA", "")).strip().upper()
            if tipo_comercializadora == "CPURA":
                out["CATEGORIA"] = None
            elif tipo_comercializadora == "CGRUPO":
                valor_categoria = str(out["CATEGORIA"]).strip().upper()
                try:
                    import json
                    from app.context import AppContext
                    domain_file = Path(r"C:\Users\C807951\Desktop\BDC\ENTRADAS\control\quality\domain_dictionaries.json")
                    if domain_file.exists():
                        domains = json.loads(domain_file.read_text(encoding="utf-8"))
                        categoria_dict = domains.get("CATEGORIA_GRUPO", {})
                        
                        encontrado = False
                        for chave, sinonimos in categoria_dict.items():
                            if any(sin in valor_categoria for sin in sinonimos):
                                out["CATEGORIA"] = chave
                                encontrado = True
                                break
                        
                        if not encontrado:
                            out["CATEGORIA"] = "DESCONHECIDO"
                except Exception as e:
                    if logger: logger.warning("Nao foi possivel carregar domain_dictionaries.json para normalizar CATEGORIA: %s", e)

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