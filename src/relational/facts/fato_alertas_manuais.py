"""Serviço de geração de alertas da esteira de Carga Manual e Exceções (MAN_* e EXC_*)."""
from typing import Any
import pandas as pd
from datetime import datetime
from pathlib import Path

from control.logger import obter_logger
from relational.facts.fato_alerta_util import registrar_alertas_em_lote

def gerar_fato_alertas_manuais(context: Any) -> dict[str, Any]:
    run_id = f"MAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.alertas_manuais", Path("LOGS/relacional") / f"{run_id}__alertas_manuais.log")
    logger.info("Iniciando varredura da camada Silver para Alertas de Carga Manual...")

    alertas = []
    
    # Paths da Silver
    dir_silver = context.path("silver")
    path_comerc = dir_silver / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    path_consum = dir_silver / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet"
    
    dfs_para_varrer = []
    
    if path_comerc.exists():
        df_com = pd.read_parquet(path_comerc)
        df_com["_tipo_base"] = "COMERCIALIZADORA"
        dfs_para_varrer.append(df_com)
    else:
        logger.warning(f"Base Silver de Comercializadoras não encontrada: {path_comerc}")
        
    if path_consum.exists():
        df_con = pd.read_parquet(path_consum)
        df_con["_tipo_base"] = "CONSUMIDOR"
        dfs_para_varrer.append(df_con)
    else:
        logger.warning(f"Base Silver de Consumidores não encontrada: {path_consum}")
        
    if not dfs_para_varrer:
        logger.warning("Nenhuma base Silver encontrada. Abortando varredura de Carga Manual.")
        return {"run_id": run_id, "alertas_gerados": 0, "status": "SEM_BASE"}
        
    df_silver = pd.concat(dfs_para_varrer, ignore_index=True)
    logger.info(f"Total de registros a varrer na Silver: {len(df_silver)}")
    
    for _, row in df_silver.iterrows():
        cnpj = row.get("CNPJ")
        tipo_base = row.get("_tipo_base")
        tipo_ficha = str(row.get("TIPO_FICHA", "PENDENTE")).upper()
        
        # 1. MAN_002: Identificação Crítica Vazia (Fichas sem CNPJ)
        if pd.isna(cnpj) or not str(cnpj).strip():
            alertas.append({
                "codigo": "MAN_002",
                "severidade": "CRITICO",
                "regra": "Ficha sem Identificação (CNPJ)",
                "mensagem": "Extrator não conseguiu ler o CNPJ da ficha. Exige Override/Carga Manual.",
                "campo_afetado": "CNPJ",
                "valor_observado": "VAZIO",
                "limite_esperado": "CNPJ Válido",
                "contraparte_id": "DESCONHECIDO",
                "run_id": run_id
            })
            continue # Sem CNPJ, nem avalia o resto.
            
        cnpj_str = str(cnpj)
            
        # 2. MAN_003: Tipo de Ficha Pendente (Classificação Documental Falhou)
        if tipo_ficha in ("PENDENTE", "DESCONHECIDA", "DESCONHECIDO"):
            alertas.append({
                "codigo": "MAN_003",
                "severidade": "ALTO",
                "regra": "Classificação Documental Pendente",
                "mensagem": "O Motor Semântico não conseguiu classificar o tipo do documento.",
                "campo_afetado": "TIPO_FICHA",
                "valor_observado": tipo_ficha,
                "limite_esperado": "COMERCIALIZADORA / CONSUMIDOR",
                "contraparte_id": cnpj_str,
                "run_id": run_id
            })
            
        # 3. MAN_001 e DF_001: Data da DF Vazia
        data_df = row.get("DATA_DEMONSTRACAO_FINANCEIRA")
        
        if tipo_base == "COMERCIALIZADORA":
            if pd.isna(data_df) or str(data_df).strip() in ("", "NaT", "None"):
                alertas.append({
                    "codigo": "MAN_001",
                    "severidade": "ALTO",
                    "regra": "Data de Demonstração Financeira Ausente",
                    "mensagem": "Comercializadoras obrigatoriamente precisam de Data da DF válida.",
                    "campo_afetado": "DATA_DEMONSTRACAO_FINANCEIRA",
                    "valor_observado": "VAZIO",
                    "limite_esperado": "Data Válida",
                    "contraparte_id": cnpj_str,
                    "run_id": run_id
                })
                
        elif tipo_base == "CONSUMIDOR":
            vol_mwm = pd.to_numeric(row.get("VOLUME_MWM", 0), errors="coerce")
            if pd.isna(vol_mwm): vol_mwm = 0.0
            
            # Consumidores >= 5 MWm precisam ter DF
            if vol_mwm >= 5.0:
                if pd.isna(data_df) or str(data_df).strip() in ("", "NaT", "None"):
                    alertas.append({
                        "codigo": "DF_001",
                        "severidade": "CRITICO",
                        "regra": "Consumidor >= 5MWm Sem DF",
                        "mensagem": "A ficha não apresentou DF estruturada, mas o enquadramento (>5MWm) exige.",
                        "campo_afetado": "DATA_DEMONSTRACAO_FINANCEIRA",
                        "valor_observado": "VAZIO",
                        "limite_esperado": "Data Válida",
                        "contraparte_id": cnpj_str,
                        "run_id": run_id
                    })
                    
        # 4. MAN_004: Outros Campos Obrigatórios Vazios
        # Verificando PL (Patrimônio Líquido) que é crítico para Rating.
        pl = row.get("PATRIMONIO_LIQUIDO")
        if (pd.isna(pl) or str(pl).strip() in ("", "None")) and not (tipo_base == "CONSUMIDOR" and vol_mwm < 5.0):
            alertas.append({
                "codigo": "MAN_004",
                "severidade": "MEDIO",
                "regra": "Campo Crítico de Risco Vazio (PL)",
                "mensagem": "O Patrimônio Líquido não foi lido ou está nulo. Pode corromper o cálculo de PD.",
                "campo_afetado": "PATRIMONIO_LIQUIDO",
                "valor_observado": "VAZIO",
                "limite_esperado": "Valor Numérico",
                "contraparte_id": cnpj_str,
                "run_id": run_id
            })

    if alertas:
        registrar_alertas_em_lote(alertas, run_id, context)
        logger.info(f"Varredura concluída. Foram gravados {len(alertas)} alertas de Carga Manual/Exceção.")
    else:
        logger.info("Varredura concluída. Nenhum alerta de Carga Manual detectado na Silver.")

    return {
        "status": "SUCESSO",
        "total_alertas_manuais": len(alertas)
    }
