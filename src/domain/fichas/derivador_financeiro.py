import logging

logger = logging.getLogger(__name__)

def divisao_segura(num, den):
    if num is None or den is None:
        return None
    try:
        f_num = float(num)
        f_den = float(den)
        if f_den == 0.0:
            return None
        return f_num / f_den
    except (ValueError, TypeError):
        return None

def calcular_indicadores_derivados(record: dict) -> dict:
    ativo_circulante = record.get("ATIVO_CIRCULANTE")
    passivo_circulante = record.get("PASSIVO_CIRCULANTE")
    ativo_total = record.get("ATIVO_TOTAL")
    passivo_nao_circulante = record.get("PASSIVO_NAO_CIRCULANTE_FINANCEIRO")
    lucro_liquido = record.get("LUCRO_LIQUIDO")
    patrimonio_liquido = record.get("PATRIMONIO_LIQUIDO")
    fluxo_caixa = record.get("FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS")
    
    rol = record.get("ROL")
    vendas = record.get("VENDAS_LIQUIDAS")
    receita_base = rol if rol is not None else vendas

    if record.get("AC_PC") is None:
        val = divisao_segura(ativo_circulante, passivo_circulante)
        if val is not None:
            record["AC_PC"] = val
            
    if record.get("AT_PT") is None:
        if passivo_circulante is not None and passivo_nao_circulante is not None:
            passivo_total = float(passivo_circulante) + float(passivo_nao_circulante)
            val = divisao_segura(ativo_total, passivo_total)
            if val is not None:
                record["AT_PT"] = val
                
    if record.get("ROA") is None:
        val = divisao_segura(lucro_liquido, ativo_total)
        if val is not None:
            record["ROA"] = val
            
    if record.get("ROE") is None:
        val = divisao_segura(lucro_liquido, patrimonio_liquido)
        if val is not None:
            record["ROE"] = val
            
    if record.get("FCO") is None:
        val = divisao_segura(fluxo_caixa, receita_base)
        if val is not None:
            record["FCO"] = val
                    
    return record
