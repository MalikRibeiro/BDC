"""Orquestrador Central de Normalizadores do Projeto BDC."""

from __future__ import annotations

import re
import math
from datetime import datetime
from typing import Any


def normalizar_string(value: Any, upper: bool = False) -> str | None:
    """Normaliza um valor textual."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    return text.upper() if upper else text

def normalizar_float(valor: Any) -> float | None:
    """Normaliza strings monetárias e percentuais para float decimal puro."""
    if valor is None or str(valor).strip() == "":
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

    v_str = str(valor).strip()
    
    # Identifica se é porcentagem
    is_percent = "%" in v_str
    
    # Remove máscaras financeiras e espaços
    v_str = re.sub(r'[R\$\%\s]', '', v_str)

    try:
        # Tratamento de pontuação brasileira (milhar vs decimal)
        if ',' in v_str and '.' in v_str:
            v_str = v_str.replace('.', '').replace(',', '.')
        elif ',' in v_str:
            v_str = v_str.replace(',', '.')
            
        numero = float(v_str)
        
        # Converte percentual para notação decimal (ex: 14.4 -> 0.144)
        if is_percent:
            numero = numero / 100.0
            
        # Limita a 12 casas decimais para precisão de crédito
        return round(numero, 12)
        
    except ValueError:
        return None

def padronizar_cnpj(cnpj_bruto: str | int | None) -> tuple[str | None, str | None, str]:
    """
    Limpa caracteres, extrai números, valida tamanho e preenche com zeros.
    Rejeita CNPJs com mais de 14 dígitos por risco de concatenação na extração.
    Retorna (CNPJ_14_DIGITOS, RAIZ_8_DIGITOS, STATUS).
    """
    if cnpj_bruto is None or str(cnpj_bruto).strip() == "":
        return None, None, "CNPJ_VAZIO"

    # Remove qualquer caractere que não seja número
    numeros = re.sub(r'\D', '', str(cnpj_bruto))

    if not numeros:
        return None, None, "CNPJ_INVALIDO_SEM_NUMEROS"

    # Regra de descarte estrito
    if len(numeros) > 14:
        return None, None, "CNPJ_INVALIDO_TAMANHO_EXCEDIDO"

    # Força exatamente 14 dígitos (preenche com zeros à esquerda se tiver menos)
    numeros = numeros.zfill(14)

    cnpj_raiz = numeros[:8]
    return numeros, cnpj_raiz, "CNPJ_VALIDO"

def normalizar_data_demonstracao_financeira(value: Any) -> tuple[str | None, str | None, bool]:
    """Normaliza DATA_DEMONSTRACAO_FINANCEIRA para dd/mm/aaaa.
    Retorna: (data_normalizada, valor_original_corrompido, flag_corrigida)
    """
    if value is None:
        return None, None, False

    # Resgate de datas corrompidas por digitação de "Ano" em célula de Data no Excel
    if isinstance(value, datetime) and 1900 <= value.year <= 1920:
        dias = (value - datetime(1899, 12, 30)).days
        if 1950 <= dias <= 2100:  # O número de dias é na verdade o ano digitado!
            return f"31/12/{dias}", value.strftime("%Y-%m-%d %H:%M:%S"), True

    text = str(value).strip()
    if not text:
        return None, None, False

    if re.fullmatch(r"\d{4}", text):
        return f"31/12/{text}", text, True

    text = text.split()[0]

    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]

    for fmt in formatos:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%d/%m/%Y"), None, False
        except ValueError:
            continue

    return None, None, False

def padronizar_cnpj(cnpj_bruto: str | int | None) -> tuple[str | None, str | None, str]:
    """
    Limpa caracteres, extrai apenas números, valida tamanho e preenche com zeros.
    Retorna (CNPJ_14_DIGITOS, RAIZ_8_DIGITOS, STATUS).
    """
    if cnpj_bruto is None or str(cnpj_bruto).strip() == "":
        return None, None, "CNPJ_VAZIO"

    # Remove qualquer coisa que não seja número
    numeros = re.sub(r'\D', '', str(cnpj_bruto))

    if not numeros:
        return None, None, "CNPJ_INVALIDO_SEM_NUMEROS"

    # Força exatamente 14 dígitos (preenche com zeros à esquerda se menor)
    if len(numeros) <= 14:
        numeros = numeros.zfill(14)
    else:
        # Trade-off: se for maior que 14, pode ser lixo de extração. Bloqueamos.
        return None, None, "CNPJ_INVALIDO_TAMANHO_EXCEDIDO"

    cnpj_raiz = numeros[:8]
    return numeros, cnpj_raiz, "CNPJ_VALIDO"