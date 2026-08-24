"""Classificação de fichas conforme os layouts conhecidos."""

from __future__ import annotations

import re
from typing import Any
from openpyxl.worksheet.worksheet import Worksheet

from dataclasses import dataclass
from common.excel import ler_celula
from silver.normalizadores import normalizar_string


@dataclass
class ClassificationResult:
    """Representa o resultado da classificação de layout."""

    versao_ficha: str
    matched_fields: list[str]
    missing_fields: list[str]

def normalizar_rotulo(value: Any) -> str:
    """Normaliza texto de label para comparação."""
    if value is None:
        return ""

    return normalizar_string(str(value), upper=True)

def localizar_celula_por_regex(
    worksheet: Worksheet,
    search_pattern: str,
    max_rows: int = 150,
    max_cols: int = 30,
) -> bool:
    """
    Verifica se um label correspondente ao padrão regex existe na planilha.

    Args:
        worksheet: Aba do openpyxl.
        search_pattern: Expressão regular para buscar o rótulo.
        max_rows: Limite de linhas para a busca.
        max_cols: Limite de colunas para a busca.

    Returns:
        True se o padrão for encontrado, False caso contrário.
    """
    if not search_pattern:
        return False

    try:
        regex = re.compile(search_pattern, re.IGNORECASE)
    except re.error:
        # Se o padrão for inválido, não pode haver match.
        return False

    # Itera nas células dentro do limite de busca
    for row in worksheet.iter_rows(
        min_row=1, max_row=max_rows, min_col=1, max_col=max_cols
    ):
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                if regex.search(cell.value.strip()):
                    # Encontrou o label, a verificação é bem-sucedida.
                    return True

    return False

def verificar_label(
    workbook: Any,
    field_name: str,
    meta: dict[str, Any],
    logger: Any,
    versao_ficha: str,
) -> bool:
    """Verifica se o label do campo coincide com o esperado."""
    sheet_name = meta.get("sheet_name", workbook.active.title)
    ws = workbook[sheet_name] if sheet_name in workbook.sheetnames else workbook.active

    label_cell = meta.get("label_cell")
    search_pattern = meta.get("search_pattern")
    expected_label = meta.get("expected_label")

    # Estratégia 1: Verificação por coordenada fixa (label_cell)
    if label_cell:
        if expected_label is None:
            expected_label = field_name

        actual_label = ler_celula(ws, label_cell)
        expected_normalized = normalizar_rotulo(expected_label)
        actual_normalized = normalizar_rotulo(actual_label)

        # Lógica de exceção para o layout "padrao_3"
        if expected_normalized == "CNPJ" and versao_ficha == "padrao_3":
            categoria_label = ler_celula(ws, "A19")
            if expected_normalized == actual_normalized and categoria_label == "Categoria":
                return False

        matched = expected_normalized in actual_normalized
        logger.info(
            "Verificação (estática) '%s': label_cell=%s, expected='%s', actual='%s', matched=%s",
            field_name, label_cell, expected_normalized, actual_normalized, matched
        )
        return matched

    # Estratégia 2: Verificação por busca de padrão (search_pattern)
    if search_pattern:
        matched = localizar_celula_por_regex(ws, search_pattern) is not None
        logger.info(
            "Verificação (dinâmica) '%s': pattern='%s', matched=%s",
            field_name, search_pattern, matched
        )
        return matched

    raise ValueError(
        f"Campo de verificação '{field_name}' no layout '{versao_ficha}' "
        "não possui 'label_cell' nem 'search_pattern' para classificação."
    )

def classificar_pasta_de_trabalho(
    workbook: Any,
    layouts: dict[str, dict[str, Any]],
    logger: Any,
) -> ClassificationResult | None:
    """Classifica um workbook pelos verify_fields.

    Um layout só é aceito se todos os campos em verify_fields
    coincidirem no label_cell com o expected_label.
    """
    try:
        logger.info(
            "Iniciando classificação do workbook com %s layouts.",
            len(layouts),
        )

        for versao_ficha, layout in layouts.items():
            verify_fields = layout.get("verify_fields", [])

            logger.info(
                "Testando layout '%s' com %s verify_fields.",
                versao_ficha,
                len(verify_fields),
            )

            if not verify_fields:
                raise ValueError(
                    f"Layout '{versao_ficha}' sem verify_fields."
                )

            matched_fields: list[str] = []
            missing_fields: list[str] = []

            all_match = True

            for field_name in verify_fields:
                if field_name not in layout.get("field_map", {}):
                    raise ValueError(
                        f"Campo '{field_name}' está em verify_fields, "
                        f"mas não existe em 'field_map' no layout "
                        f"'{versao_ficha}'."
                    )

                meta = layout["field_map"][field_name]

                if verificar_label(workbook, field_name, meta, logger, versao_ficha):
                    matched_fields.append(field_name)
                else:
                    missing_fields.append(field_name)
                    all_match = False

                    logger.info(
                        "Layout '%s' rejeitado. Campo de verificação "
                        "'%s' não coincidiu.",
                        versao_ficha,
                        field_name,
                    )
                    break

            if all_match:
                logger.info(
                    "Layout '%s' classificado com sucesso. "
                    "Campos verificados: %s",
                    versao_ficha,
                    matched_fields,
                )
                return ClassificationResult(
                    versao_ficha=versao_ficha,
                    matched_fields=matched_fields,
                    missing_fields=missing_fields,
                )

        logger.warning("Nenhum layout compatível foi identificado.")
        return None

    except Exception:
        logger.exception("Falha durante a classificação do workbook.")
        raise