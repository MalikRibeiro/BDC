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
        elif str(pl).upper() != "NAO_APLICAVEL" and not isinstance(pl, (int, float)):
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
            elif str(pd_val).upper() != "NAO_APLICAVEL" and not isinstance(pd_val, (int, float)):
                errors.append("PROBABILIDADE_DEFAULT inválida: valor não numérico.")
            elif isinstance(pd_val, (int, float)) and (pd_val < 0 or pd_val > 100):
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


def validar_registro(
    record: dict[str, Any],
    master_catalog: dict[str, Any] | None = None,
    logger: Any | None = None,
    # Parâmetros Legados para Consumidores:
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
            # 1. LÓGICA DE GATES (Master Catalog)
            for field, config in master_catalog["fields"].items():
                if config.get("criticality") == "GATE_ENGINE":
                    if _is_empty(record.get(field)):
                        errors.append(f"GATE_ENGINE ausente: {field}")

            # 2. SANITY CHECK CONTÁBIL (Consistência)
            ativo_total = record.get("ATIVO_TOTAL_AJUSTADO")
            pl = record.get("PATRIMONIO_LIQUIDO")
            passivo_circulante = record.get("PASSIVO_CIRCULANTE_AJUSTADO")
            passivo_nao_circulante = record.get("PASSIVO_NAO_CIRCULANTE_FINANCEIRO_AJUSTADO")
            
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
            # Fallback Legacy (Consumidores)
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
            if warnings:
                logger.warning("Avisos de validação para CNPJ=%s: %s", record.get("CNPJ"), warnings)

        return errors, warnings

    except Exception:
        if logger is not None:
            logger.exception("Falha inesperada na validação do registro. CNPJ=%s", record.get("CNPJ"))
        raise


def validar_registro_consumidor(
    record: dict[str, Any],
    required_fields: list[str],
    classificacao: Any | None = None,
    logger: Any | None = None,
    quality_rules: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """Valida o registro de consumidor com regras condicionais por tipo de análise.

    Estende a validação padrão com regras específicas de consumidores:
    - ≥5 MWm (detalhada): valida presença obrigatória dos campos financeiros.
    - <5 MWm (simplificada): valida que campos financeiros são NAO_APLICAVEL,
      e exige score de bureau.
    """
    # Validação base (universal)
    errors, warnings = validar_registro(
        record=record,
        required_fields=required_fields,
        logger=logger,
        quality_rules=quality_rules,
    )

    if classificacao is None:
        return errors, warnings

    tipo_analise = getattr(classificacao, "tipo_analise_exigida", None)

    if tipo_analise == "detalhada":
        # Validar presença de campos financeiros obrigatórios para ≥5 MWm
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

        # Auditor deve estar presente em análise detalhada
        if _is_empty(record.get("AUDITOR")):
            warnings.append("AUDITOR não informado para consumidor ≥5 MWm.")

    elif tipo_analise == "simplificada":
        # Score de bureau é obrigatório para <5 MWm
        if _is_empty(record.get("SCORE_BUREAU")):
            errors.append(
                "SCORE_BUREAU obrigatório para consumidor <5 MWm não informado."
            )

        # Campos financeiros devem ser NAO_APLICAVEL ou vazios
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

    # Verificar compatibilidade ficha-segmento
    if hasattr(classificacao, "compatibilidade_ficha_segmento"):
        if not classificacao.compatibilidade_ficha_segmento:
            warnings.append(
                f"Incompatibilidade detectada: ficha para tipo "
                f"'{classificacao.tipo_consumidor}' não contém os dados esperados. "
                f"Confiança: {classificacao.confianca_classificacao}."
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