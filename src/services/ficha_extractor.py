"""Serviço de extração de dados das fichas Excel."""

from datetime import datetime
from typing import Dict, Any, Optional
import openpyxl

from common.excel import find_cell_by_regex, read_cell
from openpyxl.utils.datetime import from_excel

CUTOFF_DATE_LAYOUT_CHANGE = datetime(2025, 4, 30)

def parse_date_safely(date_val: Any) -> Optional[datetime]:
    """Converte valores heterogêneos de data para o tipo datetime, incluindo seriais do Excel."""
    if isinstance(date_val, datetime):
        return date_val
        
    if isinstance(date_val, (int, float)):
        try:
            return from_excel(date_val)
        except ValueError:
            return None

    if isinstance(date_val, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d"):
            try:
                return datetime.strptime(date_val.strip(), fmt)
            except ValueError:
                pass
    return None


def extract_field_value(
    worksheet: openpyxl.worksheet.worksheet.Worksheet,
    field_config: Dict[str, Any],
    ficha_date: Optional[datetime],
    field_name: str,
) -> tuple[Any, dict[str, Any]]:
    """
    Extrai o valor de um campo aplicando a estratégia híbrida e retorna (valor, meta).
    """
    static_cell = field_config.get("value_cell")
    search_pattern = field_config.get("search_pattern")
    
    offset_col = field_config.get("offset_col", 1)
    offset_row = field_config.get("offset_row", 0)
    
    is_post_cutoff = ficha_date is not None and ficha_date > CUTOFF_DATE_LAYOUT_CHANGE
    
    val = None
    meta = {"campo": field_name, "aba_origem": worksheet.title, "celula_origem": None, "metodo": None, "valor": None}
    
    # 1. Estratégia Dinâmica (Para fichas pós-abril/2025 ou se não houver célula estática)
    if (is_post_cutoff or not static_cell) and search_pattern:
        val, meta_inf = find_cell_by_regex(
            worksheet=worksheet,
            search_pattern=search_pattern,
            offset_col=offset_col,
            offset_row=offset_row,
            return_meta=True
        )
        if val is not None:
            meta.update({"metodo": "dinamico_regex", "valor": val})
            if meta_inf:
                meta.update({"aba_origem": meta_inf["aba"], "celula_origem": meta_inf["celula"]})
            return val, meta
            
    # 2. Estratégia Estática (Legado <= 04/2025)
    if static_cell:
        val, meta_inf = read_cell(worksheet, static_cell, return_meta=True)
        if val is not None and str(val).strip() != "":
            meta.update({"metodo": "estatico_fixo", "valor": val})
            if meta_inf:
                meta.update({"aba_origem": meta_inf["aba"], "celula_origem": meta_inf["celula"]})
            return val, meta
            
    # 3. Fallback Dinâmico (Se a coordenada estática falhou em ficha antiga)
    if not is_post_cutoff and search_pattern:
        val, meta_inf = find_cell_by_regex(
            worksheet=worksheet,
            search_pattern=search_pattern,
            offset_col=offset_col,
            offset_row=offset_row,
            return_meta=True
        )
        if val is not None:
            meta.update({"metodo": "dinamico_fallback", "valor": val})
            if meta_inf:
                meta.update({"aba_origem": meta_inf["aba"], "celula_origem": meta_inf["celula"]})
            return val, meta
        
    return val, meta


def extract_record(
    workbook: openpyxl.workbook.workbook.Workbook, 
    layout_schema: Dict[str, Any]
) -> tuple[Dict[str, Any], list[dict[str, Any]]]:
    """
    Executa a extração completa de uma ficha Excel utilizando o catálogo de layout.
    Retorna os dados extraídos e a lista de metadados da linhagem.
    """
    extracted_data = {}
    metadata_list = []
    
    # A chave correta nos seus JSONs é field_map, não fields.
    field_map = layout_schema.get("field_map", {})
    
    # Extrai primeiro a data da DF para definir a estratégia de corte do layout
    date_config = field_map.get("DATA_DEMONSTRACAO_FINANCEIRA", {})
    
    # Define a aba correta para buscar a data
    date_sheet_name = date_config.get("sheet")
    if date_sheet_name and date_sheet_name in workbook.sheetnames:
        ws_date = workbook[date_sheet_name]
    else:
        ws_date = workbook.active
        
    # Extrai a data baseando-se no value_cell (pois a config usa value_cell, não cell)
    raw_date = read_cell(ws_date, date_config.get("value_cell", "A1")) if date_config else None
    ficha_date = parse_date_safely(raw_date)
    
    for field_name, field_config in field_map.items():
        # Define a aba correta dinamicamente para cada campo
        sheet_name = field_config.get("sheet")
        if sheet_name and sheet_name in workbook.sheetnames:
            ws = workbook[sheet_name]
        else:
            ws = workbook.active
            
        val, meta = extract_field_value(
            worksheet=ws,
            field_config=field_config,
            ficha_date=ficha_date,
            field_name=field_name
        )
        extracted_data[field_name] = val
        if meta:
            metadata_list.append(meta)
        
    return extracted_data, metadata_list