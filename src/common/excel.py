"""Operações de leitura e fechamento seguro de workbooks Excel."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter


def abrir_pasta(path: str | Path) -> Any:
    """Abre um workbook Excel em modo somente leitura."""
    return load_workbook(
        filename=Path(path),
        data_only=True,
        read_only=True,
        keep_links=False,
    )

def fechar_pasta(workbook: Any) -> None:
    """Fecha um workbook ignorando falhas de liberação."""
    if workbook is None:
        return
    try:
        workbook.close()
    except Exception:
        return

def ler_celula(worksheet: Worksheet, cell_ref: str, return_meta: bool = False) -> Any:
    """Lê o valor de uma célula a partir de uma referência A1 (ex: 'A19')."""
    if not cell_ref or cell_ref == "0":
        return (None, None) if return_meta else None
    val = worksheet[cell_ref].value
    if return_meta:
        return val, {"aba": worksheet.title, "celula": cell_ref}
    return val

def localizar_celula_por_regex(
    worksheet: Worksheet,
    search_pattern: str,
    offset_col: int = 1,
    offset_row: int = 0,
    max_search_rows: int = 150,
    max_search_cols: int = 30,
    return_meta: bool = False
) -> Optional[Any]:
    """
    Varre a aba procurando uma expressão e retorna a célula adjacente.
    """
    if not search_pattern:
        return (None, None) if return_meta else None

    try:
        regex = re.compile(search_pattern, re.IGNORECASE)
    except re.error:
        return (None, None) if return_meta else None

    # OTIMIZAÇÃO CRÍTICA: Extrai o bloco de dados de uma vez só 
    # para evitar travamentos de O(N^2) no modo read_only=True.
    max_r = max_search_rows + max(0, offset_row)
    max_c = max_search_cols + max(0, offset_col)
    
    grid = []
    for row_vals in worksheet.iter_rows(min_row=1, max_row=max_r, min_col=1, max_col=max_c, values_only=True):
        grid.append(row_vals)

    for r_idx in range(min(max_search_rows, len(grid))):
        row_data = grid[r_idx]
        for c_idx in range(min(max_search_cols, len(row_data))):
            cell_value = row_data[c_idx]
            
            if cell_value and isinstance(cell_value, str):
                if regex.search(cell_value.strip()):
                    target_r = r_idx + offset_row
                    target_c = c_idx + offset_col
                    
                    if target_r < len(grid) and target_c < len(grid[target_r]):
                        val = grid[target_r][target_c]
                        if return_meta:
                            celula_ref = f"{get_column_letter(target_c + 1)}{target_r + 1}"
                            return val, {"aba": worksheet.title, "celula": celula_ref}
                        return val

    return (None, None) if return_meta else None