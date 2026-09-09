from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from common.dominio import normalizar_auditor
from common.identificadores import ResultadoCNPJ, normalizar_cnpj
from common.numeros import to_percentual_br

def normalizar_coluna_cnpj(
    df: pd.DataFrame,
    *,
    coluna_origem: str = "CNPJ",
    coluna_cnpj: str = "CNPJ",
    coluna_raiz: str = "CNPJ_RAIZ",
    coluna_status: str = "CNPJ_STATUS",
    validar_digitos: bool = True,
) -> pd.DataFrame:
    if coluna_origem not in df.columns:
        raise KeyError(
            f"Coluna obrigatória não encontrada: {coluna_origem}"
        )

    resultado = df.copy()

    normalizados: pd.Series = resultado[coluna_origem].map(
        lambda valor: normalizar_cnpj(
            valor,
            preencher_zeros=True,
            validar_digitos=validar_digitos,
        )
    )

    resultado[coluna_cnpj] = pd.Series(
        [item.cnpj for item in normalizados],
        index=resultado.index,
        dtype="string",
    )

    resultado[coluna_raiz] = pd.Series(
        [item.raiz for item in normalizados],
        index=resultado.index,
        dtype="string",
    )

    resultado[coluna_status] = pd.Series(
        [item.status.value for item in normalizados],
        index=resultado.index,
        dtype="string",
    )

    return resultado

def normalizar_coluna_auditor(
    df: pd.DataFrame,
    dicionario: Mapping[str, Sequence[str]],
    *,
    coluna: str = "AUDITOR",
) -> pd.DataFrame:
    if coluna not in df.columns:
        return df.copy()

    resultado = df.copy()

    resultado[coluna] = (
        resultado[coluna]
        .map(lambda valor: normalizar_auditor(valor, dicionario))
        .astype("string")
    )

    return resultado

def normalizar_coluna_percentual(
    df: pd.DataFrame,
    *,
    coluna: str,
    casas_decimais: int = 6,
) -> pd.DataFrame:
    if coluna not in df.columns:
        return df.copy()

    resultado = df.copy()

    resultado[coluna] = resultado[coluna].map(
        lambda valor: to_percentual_br(
            valor,
            casas_decimais=casas_decimais,
        )
    )

    resultado[coluna] = pd.to_numeric(
        resultado[coluna],
        errors="coerce",
    ).astype("Float64")

    return resultado

def validar_coluna_cnpj_canonica(
    df: pd.DataFrame,
    coluna: str = "CNPJ",
) -> list[str]:
    erros = []
    
    if coluna not in df.columns:
        return [f"A coluna '{coluna}' não existe no DataFrame."]

    if not isinstance(df[coluna].dtype, pd.StringDtype):
        erros.append(f"A coluna '{coluna}' não está com o tipo de dado 'string'.")

    inconsistentes = df[~df[coluna].isna() & ~df[coluna].astype(str).str.match(r"^\d{14}$")]
    
    if not inconsistentes.empty:
        erros.append(f"A coluna '{coluna}' possui {len(inconsistentes)} registros com formato inválido (deve ser exatamente 14 dígitos numéricos).")

    return erros

def aplicar_schema_dataframe(df: pd.DataFrame, colunas_schema: list[str]) -> pd.DataFrame:
    cols = [col for col in colunas_schema if col in df.columns]
    return df[cols].copy()

def validar_schema_dataframe(df: pd.DataFrame, colunas_obrigatorias: list[str]) -> list[str]:
    erros = []
    for col in colunas_obrigatorias:
        if col not in df.columns:
            erros.append(f"Coluna obrigatória não encontrada no DataFrame: '{col}'.")
    return erros