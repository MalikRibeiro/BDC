"""
Definição canônica de valores textuais que devem ser tratados como nulos (vazios).
Centraliza as verificações que antes estavam espalhadas pelo código.
"""

# Conjunto canônico de representações textuais de valor nulo/vazio.
# Importante: Todas as strings devem estar em letras maiúsculas e sem espaços nas bordas.
VALORES_NULOS_TEXTUAIS = frozenset({
    "",
    "NAN",
    "NONE",
    "<NA>",
    "N/A",
    "NA",
    "NULL",
    "N/D",
    "ND",
    "-",
    "--",
    "NAT",
    "NAO APLICAVEL",
    "NÃO APLICÁVEL",
    "NAO_APLICAVEL"
})

def is_nulo_textual(valor: str | None | float) -> bool:
    """Verifica se uma string (ou qualquer valor convertido para string) é um nulo textual."""
    import pandas as pd
    if valor is None or pd.isna(valor):
        return True
    return str(valor).strip().upper() in VALORES_NULOS_TEXTUAIS


def is_missing(val) -> bool:
    """Retorna True se val for None ou NaN (numérico). Para uso nos motores de cálculo."""
    import math
    if val is None:
        return True
    try:
        return math.isnan(float(val))
    except (TypeError, ValueError):
        return False
