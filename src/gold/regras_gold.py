"""Regras de Negócio e Classificação da Visão Consolidada Gold."""

from __future__ import annotations
from typing import Any
import pandas as pd

import json
from pathlib import Path
from app.context import AppContext

def _load_status_domains() -> dict[str, list[str]]:
    try:
        # Pega do path padrao
        path = Path("ENTRADAS/control/quality/domain_dictionaries.json")
        if path.exists():
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
                return {
                    "SITUACAO_DF": list(d.get("SITUACAO_DF", {}).keys()),
                    "SITUACAO_ANALISE": list(d.get("SITUACAO_ANALISE", {}).keys()),
                    "STATUS_CONTRATUAL": list(d.get("STATUS_CONTRATUAL", {}).keys())
                }
    except Exception:
        pass
    return {
        "SITUACAO_DF": ["RECEBIDA", "NAO_RECEBIDA", "DISPENSADA"],
        "SITUACAO_ANALISE": ["VIGENTE", "VENCIDA", "NAO_POSSUI"],
        "STATUS_CONTRATUAL": ["CONTRATO_VIGENTE", "CONTRATO_FUTURO", "SEM_CONTRATO"]
    }

_STATUS_DOMAINS = _load_status_domains()

def _safe_str(val: Any) -> str:
    """Extrai string segura lidando com pd.NA."""
    if pd.isna(val):
        return ""
    return str(val).strip().upper()

def checar_contrato_obrigatorio(df: pd.DataFrame, colunas_obrigatorias: list[str], nome_dataset: str) -> None:
    """Valida se as colunas obrigatórias estão presentes no DataFrame."""
    if df is None or df.empty:
        return
    colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
    if colunas_faltantes:
        raise ValueError(
            f"Dataset '{nome_dataset}' viola o contrato de dados da Gold. "
            f"Colunas obrigatórias faltantes: {', '.join(colunas_faltantes)}"
        )

def resolver_situacao_df(row: Any) -> str:
    """Determina a situação da Demonstração Financeira (RECEBIDA, NAO_RECEBIDA, DISPENSADA)."""
    sit_atual = _safe_str(row.get("SITUACAO_DF"))
    if sit_atual in _STATUS_DOMAINS["SITUACAO_DF"]:
        return sit_atual
        
    data_df = row.get("DATA_BALANCO_USADO")
    if pd.isna(data_df):
        data_df = row.get("DATA_DEMONSTRACAO_FINANCEIRA")
    if pd.isna(data_df):
        data_df = row.get("DATA_DF")
        
    from common.nulos import is_nulo_textual
    if pd.notna(data_df) and not is_nulo_textual(data_df):
        return "RECEBIDA"
        
    tem_analise = _safe_str(row.get("TEM_ANALISE"))
    if tem_analise == "SIM":
        return "RECEBIDA"
        
    return "NAO_RECEBIDA"

def resolver_situacao_analise(row: Any) -> str:
    """Determina se a análise de crédito é VIGENTE, VENCIDA ou NAO_POSSUI."""
    sit_atual = _safe_str(row.get("SITUACAO_ANALISE"))
    if sit_atual in _STATUS_DOMAINS["SITUACAO_ANALISE"]:
        return sit_atual

    tem_analise = _safe_str(row.get("TEM_ANALISE"))
    if tem_analise != "SIM":
        return "NAO_POSSUI"

    data_anl = row.get("DATA_ANALISE")
    if pd.isna(data_anl):
        data_anl = row.get("DATA_CALCULO")
        
    from common.nulos import is_nulo_textual
    if is_nulo_textual(data_anl) or pd.isna(data_anl):
        return "VIGENTE"

    try:
        dt = pd.to_datetime(data_anl, errors="coerce")
        if pd.isna(dt):
            return "VIGENTE"
        hoje = pd.Timestamp.now().normalize()
        # Validade de 365 dias para análise de crédito
        if (hoje - dt).days <= 365:
            return "VIGENTE"
        else:
            return "VENCIDA"
    except Exception:
        return "VIGENTE"

def classificar_exigencia(row: Any) -> str:
    """Classifica a exigência metodológica de crédito (DF_DETALHADA, BUREAU, DISPENSADA)."""
    seg = _safe_str(row.get("SEGMENTO_METODOLOGICO"))
    if not seg:
        seg = _safe_str(row.get("TIPO_FICHA"))
        
    vol = row.get("VOLUME_MWM")
    try:
        vol_float = float(vol) if pd.notna(vol) else 0.0
    except (ValueError, TypeError):
        vol_float = 0.0

    if "COMERCIALIZADORA" in seg:
        return "DF_DETALHADA"

    if vol_float >= 5.0:
        return "DF_DETALHADA"
    elif vol_float > 0.0:
        return "BUREAU"
    else:
        return "DISPENSADA"

def status_metodologia(row: Any) -> str:
    """Calcula o status de conformidade metodológica (COMPLIANT, PENDENTE, IRREGULAR)."""
    exigencia = classificar_exigencia(row)
    sit_analise = resolver_situacao_analise(row)
    status_ctr = _safe_str(row.get("STATUS_CONTRATUAL"))

    if status_ctr not in _STATUS_DOMAINS["STATUS_CONTRATUAL"][:2]: # CONTRATO_VIGENTE, CONTRATO_FUTURO
        return "COMPLIANT"

    if exigencia == "DISPENSADA":
        return "COMPLIANT"

    if sit_analise == "VIGENTE":
        return "COMPLIANT"
    elif exigencia == "DF_DETALHADA":
        return "IRREGULAR"
    else:
        return "PENDENTE"
