"""Validação técnica e de domínio unificada dos registros extraídos."""

from __future__ import annotations
from typing import Any

def _is_empty(value: Any) -> bool:
    """Indica se o valor deve ser tratado como vazio."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False

class DomainRuleEngine:
    """Motor unificado que aplica validações nativas e regras do JSON em um único passo."""

    def __init__(self, quality_rules: dict[str, Any] | None = None):
        self.quality_rules = quality_rules or {}
        self.dynamic_rules = self.quality_rules.get("rules", [])

    def validate(
        self, record: dict[str, Any], required_fields: list[str]
    ) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        for field in required_fields:
            if _is_empty(record.get(field)):
                errors.append(f"Campo obrigatório ausente: {field}")

        pl = record.get("PATRIMONIO_LIQUIDO")
        if _is_empty(pl):
            warnings.append("PATRIMONIO_LIQUIDO não informado.")
        elif str(pl).upper() != "NAO_APLICAVEL" and not isinstance(pl, (int, float)):
            errors.append("PATRIMONIO_LIQUIDO inválido: valor não numérico.")


        has_pd_rule = any(r.get("field") == "PROBABILIDADE_DEFAULT" for r in self.dynamic_rules)
        if not has_pd_rule and "PROBABILIDADE_DEFAULT" in record:
            pd_val = record.get("PROBABILIDADE_DEFAULT")
            if _is_empty(pd_val):
                warnings.append("PROBABILIDADE_DEFAULT não informada.")
            elif str(pd_val).upper() != "NAO_APLICAVEL" and not isinstance(pd_val, (int, float)):
                errors.append("PROBABILIDADE_DEFAULT inválida: valor não numérico.")
            elif isinstance(pd_val, (int, float)) and (pd_val < 0 or pd_val > 100):
                errors.append("PROBABILIDADE_DEFAULT inválida: fora do intervalo [0, 100].")

        for rule in self.dynamic_rules:
            field = rule.get("field")
            val = record.get(field)

            if _is_empty(val):
                continue

            if not isinstance(val, (int, float)):
                errors.append(f"{field} inválido: valor não numérico.")
                continue

            rule_type = rule.get("type")
            if rule_type == "range":
                r_min, r_max = rule.get("min"), rule.get("max")
                if r_min is not None and val < r_min:
                    errors.append(f"{field} inválido: valor {val} menor que o limite ({r_min}).")
                if r_max is not None and val > r_max:
                    errors.append(f"{field} inválido: valor {val} maior que o limite ({r_max}).")
            elif rule_type == "min":
                r_val = rule.get("value")
                if r_val is not None and val < r_val:
                    errors.append(f"{field} inválido: valor {val} menor que o limite ({r_val}).")
            elif rule_type == "max":
                r_val = rule.get("value")
                if r_val is not None and val > r_val:
                    errors.append(f"{field} inválido: valor {val} maior que o limite ({r_val}).")

        return errors, warnings


import jsonschema
import json
from pathlib import Path

def validar_schema(record: dict[str, Any], logger: Any | None = None) -> list[str]:
    tipo_ficha = record.get("TIPO_FICHA")
    if tipo_ficha == "CONSUMIDOR":
        schema_path = Path("ENTRADAS/control/schemas/schema_ficha_consumidor_extraida.json")
    elif tipo_ficha == "COMERCIALIZADORA":
        schema_path = Path("ENTRADAS/control/schemas/schema_ficha_comercializadora_extraida.json")
    else:
        return []

    if not schema_path.exists():
        return []

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        # Chaves temporárias de runtime que NÃO pertencem ao contrato da Silver.
        # São subprodutos do extrator/classificador e devem ser descartadas
        # antes da validação de schema (Fail-Safe estrito).
        _RUNTIME_KEYS = {
            "STATUS_CNPJ",
        }

        clean_record = {}
        from common.nulos import is_nulo_textual
        import pandas as pd
        for k, v in record.items():
            if k in _RUNTIME_KEYS:
                continue
            if is_nulo_textual(v):
                clean_record[k] = None
            elif isinstance(v, pd.Timestamp):
                clean_record[k] = v.strftime("%Y-%m-%d")
            else:
                clean_record[k] = v

        jsonschema.validate(instance=clean_record, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        return [f"Violação de contrato (Schema): {e.message}"]
    except Exception as e:
        if logger:
            logger.warning("Falha na validação de schema: %s", e)
    return []


def validar_registro(
    record: dict[str, Any],
    master_catalog: dict[str, Any] | None = None,
    logger: Any | None = None,
    required_fields: list[str] | None = None,
    quality_rules: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """Valida o registro normalizado da ficha usando o Master Catalog ou fallback para legados."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando validação unificada do registro. CNPJ=%s",
                record.get("CNPJ"),
            )

        errors: list[str] = []
        warnings: list[str] = []

        if master_catalog and "fields" in master_catalog:
            for field, config in master_catalog["fields"].items():
                if config.get("criticality") == "GATE_ENGINE":
                    if _is_empty(record.get(field)):
                        errors.append(f"GATE_ENGINE ausente: {field}")

            ativo_total = record.get("ATIVO_TOTAL")
            pl = record.get("PATRIMONIO_LIQUIDO")
            passivo_circulante = record.get("PASSIVO_CIRCULANTE")
            passivo_nao_circulante = record.get("PASSIVO_NAO_CIRCULANTE_FINANCEIRO")
            
            if ativo_total is not None and pl is not None:
                pc = float(passivo_circulante) if passivo_circulante is not None else 0.0
                pnc = float(passivo_nao_circulante) if passivo_nao_circulante is not None else 0.0
                
                passivo_exigivel = pc + pnc
                ativo_t = float(ativo_total)
                patrimonio = float(pl)
                
                diferenca = abs(ativo_t - (passivo_exigivel + patrimonio))
                if diferenca > (0.05 * ativo_t):
                    warnings.append(f"ALERTA_CONTABIL: Balanço não fecha. Ativo difere de Passivo+PL. (Diferença: {diferenca:.2f})")
        else:
            engine = DomainRuleEngine(quality_rules)
            err, warn = engine.validate(record, required_fields or [])
            errors.extend(err)
            warnings.extend(warn)

        if logger is not None:
            logger.info(
                "Validação concluída. CNPJ=%s ERROS=%s AVISOS=%s",
                record.get("CNPJ"),
                len(errors),
                len(warnings),
            )
            if errors:
                logger.warning("Erros de validação para CNPJ=%s: %s", record.get("CNPJ"), errors)

        return errors, warnings

    except Exception:
        if logger is not None:
            logger.exception("Falha inesperada na validação do registro. CNPJ=%s", record.get("CNPJ"))
        raise


def validar_registro_consumidor(
    record: dict[str, Any],
    master_catalog: dict[str, Any] | None = None,
    classificacao: Any | None = None,
    logger: Any | None = None,
) -> tuple[list[str], list[str]]:
    """Valida o registro de consumidor com regras condicionais por tipo de análise.

    Estende a validação padrão com regras específicas de consumidores:
    - ≥5 MWm (detalhada): valida presença obrigatória dos campos financeiros.
    - <5 MWm (simplificada): valida que campos financeiros são NAO_APLICAVEL,
      e exige score de bureau.
    """
    errors, warnings = validar_registro(
        record=record,
        master_catalog=master_catalog,
        logger=logger,
    )

    if classificacao is None:
        return errors, warnings

    tipo_analise = getattr(classificacao, "tipo_analise_exigida", None)

    if tipo_analise == "detalhada":
        campos_financeiros_obrigatorios = [
            "PATRIMONIO_LIQUIDO", "ATIVO_CIRCULANTE", "ATIVO_TOTAL",
            "PASSIVO_CIRCULANTE", "LUCRO_LIQUIDO",
            "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        ]
        for campo in campos_financeiros_obrigatorios:
            val = record.get(campo)
            if _is_empty(val):
                errors.append(
                    f"Campo financeiro obrigatório ausente para consumidor ≥5 MWm: {campo}"
                )

        if _is_empty(record.get("AUDITOR")):
            warnings.append("AUDITOR não informado para consumidor ≥5 MWm.")

    elif tipo_analise == "simplificada":
        if _is_empty(record.get("DATA_DEMONSTRACAO_FINANCEIRA")):
            record["DATA_DEMONSTRACAO_FINANCEIRA"] = "NAO_APLICAVEL"
            if "DATA_DEMONSTRACAO_FINANCEIRA não informada." in warnings:
                warnings.remove("DATA_DEMONSTRACAO_FINANCEIRA não informada.")

        if _is_empty(record.get("SCORE_BUREAU")):
            errors.append(
                "SCORE_BUREAU obrigatório para consumidor <5 MWm não informado."
            )

        campos_df = [
            "ATIVO_CIRCULANTE", "ATIVO_TOTAL", "PASSIVO_CIRCULANTE",
            "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        ]
        for campo in campos_df:
            val = record.get(campo)
            if not _is_empty(val) and str(val).upper() != "NAO_APLICAVEL":
                warnings.append(
                    f"Campo {campo} preenchido em ficha simplificada (<5 MWm). "
                    f"Valor: {val}"
                )

    if hasattr(classificacao, "compatibilidade_ficha_segmento"):
        if not classificacao.compatibilidade_ficha_segmento:
            warnings.append(
                f"Incompatibilidade detectada: ficha para tipo "
                f"'{classificacao.tipo_consumidor}' não contém os dados esperados. "
            )

    if logger is not None:
        logger.info(
            "Validação condicional concluída para %s. "
            "Tipo=%s ERROS=%s AVISOS=%s",
            record.get("CNPJ"),
            tipo_analise,
            len(errors),
            len(warnings),
        )

    return errors, warnings