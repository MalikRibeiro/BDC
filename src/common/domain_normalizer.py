"""Normalizador Semântico de Domínio.

Aplica padronização de valores baseado em dicionários de negócios unificados,
garantindo que strings equivalentes (ex: 'FITCH RATINGS' e 'FITCH') convirjam 
para a mesma chave primária definida pela área de risco.
"""
from __future__ import annotations

import logging
from typing import Any

from app.context import AppContext
from common.json import ler_json

logger = logging.getLogger(__name__)

def carregar_dicionarios_de_dominio(context: AppContext) -> dict[str, Any]:
    """Carrega o dicionário unificado de domínio."""
    # Como app_config.json pode não ter o caminho mapeado ainda, usamos um caminho fixo seguro
    dict_path = context.path("control_quality") / "domain_dictionaries.json"
    if not dict_path.exists():
        logger.warning("Dicionário de domínio não encontrado em %s", dict_path)
        return {}
    return ler_json(dict_path)

def _normalizar_string_por_dicionario(value: str, mapping: dict[str, list[str]]) -> str:
    """Procura a string bruta nas listas de apelidos do dicionário e retorna a chave oficial."""
    if not value or not isinstance(value, str):
        return value
        
    val_upper = value.strip().upper()
    
    # 1. Busca exata ou por substring segura
    for canonical_key, aliases in mapping.items():
        # Verifica se o próprio canonical key foi passado
        if val_upper == canonical_key.upper():
            return canonical_key
            
        for alias in aliases:
            if alias.upper() in val_upper or val_upper in alias.upper():
                return canonical_key
                
    return value

def aplicar_normalizacao_de_dominio(record: dict[str, Any], context: AppContext, log: logging.Logger = logger) -> dict[str, Any]:
    """
    Recebe o dicionário já com tipos primitivos (float, str, date) tratados pelo 
    field_type_normalizer e aplica as regras semânticas de negócio.
    """
    dictionaries = carregar_dicionarios_de_dominio(context)
    if not dictionaries:
        return record

    out = dict(record)

    # 1. Normalização de Agência
    if "AGENCIA" in out and out["AGENCIA"]:
        old_val = out["AGENCIA"]
        new_val = _normalizar_string_por_dicionario(old_val, dictionaries.get("AGENCIA", {}))
        out["AGENCIA"] = new_val
        if old_val != new_val:
            log.info("Semântica: AGENCIA normalizada de '%s' para '%s'", old_val, new_val)

    # 2. Normalização de Nota de Crédito (Rating)
    if "NOTA_CREDITO" in out and out["NOTA_CREDITO"]:
        old_val = out["NOTA_CREDITO"]
        new_val = _normalizar_string_por_dicionario(old_val, dictionaries.get("NOTA_CREDITO", {}))
        out["NOTA_CREDITO"] = new_val
        if old_val != new_val:
            log.info("Semântica: NOTA_CREDITO normalizada de '%s' para '%s'", old_val, new_val)

    # 3. Normalização de Auditor (Para extrair o peso da nota caso precise)
    # Se quiser que AUDITOR vire 'KPMG', mas também traga o PESO 'A':
    # Como o dicionário AUDITOR_PARA_NOTA é Key=Nota, Values=[Auditores]
    if "AUDITOR" in out and out["AUDITOR"]:
        old_val = out["AUDITOR"]
        nota_auditor = _normalizar_string_por_dicionario(old_val, dictionaries.get("AUDITOR_PARA_NOTA", {}))
        # O retorno será 'A', 'C', etc. 
        # Podemos criar um novo campo NOTA_AUDITORIA automaticamente!
        if nota_auditor in dictionaries.get("AUDITOR_PARA_NOTA", {}):
            out["NOTA_AUDITORIA"] = nota_auditor
            log.info("Semântica: Auditor '%s' gerou NOTA_AUDITORIA = '%s'", old_val, nota_auditor)

    return out
