"""Cálculo do valor elegível e haircut de garantias (Item 8)."""

from __future__ import annotations

import logging
from typing import Any
import pandas as pd
from datetime import datetime
from common.numeros import to_float_br
from common.texto import normalizar_texto

def _garantia_esta_vencida(data_vencimento: Any, data_referencia: datetime) -> bool:
    """Verifica se a garantia está vencida na data de referência."""
    if pd.isna(data_vencimento) or not data_vencimento:
        return False  # Sem data de vencimento assumimos como não vencida (ex: Imóveis podem não ter validade)
    try:
        dt_venc = datetime.fromisoformat(str(data_vencimento)[:10])
        return dt_venc < data_referencia
    except Exception:
        return True # Se tem data e é inválida, descartar por segurança

def calcular_cobertura_garantias(
    cnpj_raiz: str,
    df_garantias: pd.DataFrame,
    ead_valor: float,
    config: dict[str, Any],
    data_referencia: str | None = None,
    logger: logging.Logger | None = None
) -> dict[str, Any]:
    """Calcula a cobertura efetiva considerando elegibilidade e haircuts."""
    if df_garantias.empty:
        return {"cobertura_aplicada": 0.0, "garantia_reconhecida": 0.0, "garantias_processadas": []}
        
    dt_ref = datetime.fromisoformat(data_referencia[:10]) if data_referencia else datetime.now()
    
    status_inativos = config.get("status_inativos", [])
    haircuts = config.get("haircuts", {})
    piso_lgd_residual = float(config.get("piso_lgd_residual", 0.0))
    rating_tier_1 = set(r.upper() for r in config.get("rating_garantidor_tier_1", []))

    # Filtrar garantias deste CNPJ Raiz
    filtro_cnpj = df_garantias["CNPJ_CONTRAPARTE"].astype(str).str[:8] == cnpj_raiz
    df_cnpj = df_garantias.loc[filtro_cnpj]
    
    garantia_reconhecida_total = 0.0
    garantias_processadas = []

    for _, row in df_cnpj.iterrows():
        motivo_rejeicao = None
        haircut_aplicado = 1.0 # 100% de desconto por padrão
        
        status = normalizar_texto(row.get("STATUS", ""))
        tipo_raw = str(row.get("TIPO_GARANTIA", "")).strip().upper()
        tipo_normalizado = normalizar_texto(tipo_raw) if tipo_raw else "DESCONHECIDO"
        nocional = to_float_br(row.get("VALOR_NOCIONAL")) or 0.0
        
        data_venc = row.get("DATA_VENCIMENTO")
        rj_garantidor = normalizar_texto(row.get("RECUPERACAO_JUDICIAL_GARANTIDOR", ""))
        rating_garantidor = normalizar_texto(row.get("RATING_GARANTIDOR", ""))
        
        # 1. Filtro Temporal
        if _garantia_esta_vencida(data_venc, dt_ref):
            motivo_rejeicao = "VENCIDA"
            
        # 2. Filtro de Status
        elif status in status_inativos:
            motivo_rejeicao = f"STATUS_INELEGIVEL ({status})"
            
        # 3. Filtro Jurídico/Documental (Simplificado aqui como Valor Nulo ou Tipo Desconhecido)
        elif nocional <= 0:
            motivo_rejeicao = "VALOR_NOCIONAL_ZERADO_OU_AUSENTE"
            
        # 4. Curto-Circuito: Garantidor em RJ
        elif rj_garantidor == "SIM":
            motivo_rejeicao = "GARANTIDOR_EM_RJ"
            
        # 4.5 Curto-Circuito: Garantidor com Rating E (Extensão por analogia às NCEs)
        elif rating_garantidor == "E":
            motivo_rejeicao = "RATING_GARANTIDOR_INACEITAVEL (E)"
            
        else:
            # 5. Aplicação do Haircut
            if "FIANCA" in tipo_normalizado:
                if rating_garantidor and rating_garantidor.upper() in rating_tier_1:
                    haircut_aplicado = haircuts.get("FIANCA_BANCARIA_TIER_1", 0.0)
                else:
                    haircut_aplicado = haircuts.get("FIANCA_BANCARIA_TIER_INFERIOR", 0.20)
            elif "SEGURO" in tipo_normalizado:
                haircut_aplicado = haircuts.get("SEGURO_GARANTIA", 0.10)
            elif "IMOVEL" in tipo_normalizado or "HIPOTECA" in tipo_normalizado:
                haircut_aplicado = haircuts.get("IMOVEL", 0.40)
            elif "PENHOR" in tipo_normalizado and "RECEB" in tipo_normalizado:
                haircut_aplicado = haircuts.get("PENHOR_RECEBIVEIS", 0.50)
            elif "PENHOR" in tipo_normalizado and "DUPLICATA" in tipo_normalizado:
                haircut_aplicado = haircuts.get("PENHOR_DUPLICATAS", 0.50)
            elif "ACAO" in tipo_normalizado or "ACOES" in tipo_normalizado:
                indice_principal = str(row.get("INDICE_PRINCIPAL", "")).strip().upper() == "SIM"
                haircut_aplicado = haircuts.get("ACOES_INDICE_PRINCIPAL", 0.15) if indice_principal else haircuts.get("ACOES_DEMAIS", 0.25)
            elif "FUNDO" in tipo_normalizado:
                haircut_aplicado = haircuts.get("FUNDO_INVESTIMENTO", 0.10)
            else:
                # Se o tipo não for reconhecido, assumimos 100% de haircut (inelegível)
                motivo_rejeicao = f"TIPO_GARANTIA_NAO_HOMOLOGADO ({tipo_raw})"
                haircut_aplicado = 1.0
                
        if motivo_rejeicao:
            haircut_aplicado = 1.0 # 100% de desconto se rejeitado
            
        valor_reconhecido = nocional * (1.0 - haircut_aplicado)
        garantia_reconhecida_total += valor_reconhecido
        
        garantias_processadas.append({
            "ID_GARANTIA": row.get("ID_GARANTIA"),
            "TIPO_GARANTIA": tipo_raw,
            "VALOR_NOCIONAL": nocional,
            "HAIRCUT_APLICADO": haircut_aplicado,
            "VALOR_RECONHECIDO": valor_reconhecido,
            "MOTIVO_REJEICAO": motivo_rejeicao
        })
        
    cobertura_calculada = 0.0
    if ead_valor > 0:
        cobertura_calculada = garantia_reconhecida_total / ead_valor
        
    # Cobertura não pode exceder o teto definido pelo piso de LGD (ex: 1.0 se piso = 0.0, 0.95 se piso = 0.05)
    teto_cobertura = max(0.0, 1.0 - piso_lgd_residual)
    cobertura_aplicada = min(cobertura_calculada, teto_cobertura)
    
    if logger:
        logger.info(
            "Cálculo de garantias CNPJ_RAIZ=%s | NOCIONAL_TOTAL=%s RECONHECIDO=%s COBERTURA=%s",
            cnpj_raiz, sum(g["VALOR_NOCIONAL"] for g in garantias_processadas), garantia_reconhecida_total, cobertura_aplicada
        )

    return {
        "cobertura_aplicada": cobertura_aplicada,
        "garantia_reconhecida_total": garantia_reconhecida_total,
        "piso_lgd_residual": piso_lgd_residual,
        "garantias_processadas": garantias_processadas
    }
