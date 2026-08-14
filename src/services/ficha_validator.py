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

        # 1. Validação de Campos Obrigatórios (Estática)
        for field in required_fields:
            if _is_empty(record.get(field)):
                errors.append(f"Campo obrigatório ausente: {field}")

        # 2. Validações de Domínio Universais (Fallback / Plausibilidade Básica)
        pl = record.get("PATRIMONIO_LIQUIDO")
        if _is_empty(pl):
            warnings.append("PATRIMONIO_LIQUIDO não informado.")
        elif not isinstance(pl, (int, float)):
            errors.append("PATRIMONIO_LIQUIDO inválido: valor não numérico.")

        data_df = record.get("DATA_DEMONSTRACAO_FINANCEIRA")
        data_calculo = record.get("DATA_CALCULO")
        if _is_empty(data_df):
            warnings.append("DATA_DEMONSTRACAO_FINANCEIRA não informada.")
        if _is_empty(data_calculo):
            warnings.append("DATA_CALCULO não informada.")

        # Trata a PD se não houver regra dinâmica explícita (para não quebrar comercializadoras)
        has_pd_rule = any(r.get("field") == "PROBABILIDADE_DEFAULT" for r in self.dynamic_rules)
        if not has_pd_rule and "PROBABILIDADE_DEFAULT" in record:
            pd_val = record.get("PROBABILIDADE_DEFAULT")
            if _is_empty(pd_val):
                warnings.append("PROBABILIDADE_DEFAULT não informada.")
            elif not isinstance(pd_val, (int, float)):
                errors.append("PROBABILIDADE_DEFAULT inválida: valor não numérico.")
            elif pd_val < 0 or pd_val > 100:
                errors.append("PROBABILIDADE_DEFAULT inválida: fora do intervalo [0, 100].")

        # 3. Validações Dinâmicas (Data Quality Rules JSON)
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


def validate_record(
    record: dict[str, Any],
    required_fields: list[str],
    logger: Any | None = None,
    quality_rules: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """Valida o registro normalizado da ficha usando o DomainRuleEngine."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando validação unificada do registro. CNPJ=%s EMPRESA=%s",
                record.get("CNPJ"),
                record.get("EMPRESA"),
            )

        engine = DomainRuleEngine(quality_rules)
        errors, warnings = engine.validate(record, required_fields)

        if logger is not None:
            logger.info(
                "Validação concluída. CNPJ=%s ERROS=%s AVISOS=%s",
                record.get("CNPJ"),
                len(errors),
                len(warnings),
            )
            if errors:
                logger.warning("Erros de validação para CNPJ=%s: %s", record.get("CNPJ"), errors)
            if warnings:
                logger.warning("Avisos de validação para CNPJ=%s: %s", record.get("CNPJ"), warnings)

        return errors, warnings

    except Exception:
        if logger is not None:
            logger.exception("Falha inesperada na validação do registro. CNPJ=%s", record.get("CNPJ"))
        raise