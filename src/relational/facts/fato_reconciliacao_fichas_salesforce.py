"""
Serviço de Reconciliação: Fichas de Crédito vs Salesforce.
Verifica se todas as contrapartes com ficha de crédito estão devidamente cadastradas no CRM.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from common.identificadores import normalizar_cnpj
from control.logger import obter_logger
from relational.facts.fato_alerta_util import registrar_alerta
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def executar_reconciliacao_fichas_salesforce(context: AppContext) -> dict[str, Any]:
    run_id = f"REC_SF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.reconciliacao.salesforce", Path("LOGS/auditoria") / f"{run_id}__salesforce_reconciliacao.log")
    
    silver_dir = context.path("silver")

    df_fichas = pd.DataFrame()
    for segmento in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        path_seg = silver_dir / segmento
        if path_seg.exists():
            parquets = list(path_seg.glob("*.parquet"))
            if parquets:
                df_seg = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg], ignore_index=True)

    df_sf = pd.DataFrame()
    
    arquivos_sf = list(silver_dir.rglob("account*.parquet"))
    if not arquivos_sf:
        arquivos_sf = list(silver_dir.rglob("*salesforce*account*.parquet"))
        
    if arquivos_sf:
        arquivo_sf_mais_recente = max(arquivos_sf, key=lambda f: f.stat().st_mtime)
        df_sf = pd.read_parquet(arquivo_sf_mais_recente)

    if df_fichas.empty:
        logger.warning("Base de Fichas está vazia. Abortando reconciliação.")
        return {"run_id": run_id, "status": "SEM_DADOS_FICHAS"}
        
    if df_sf.empty:
        logger.warning("Base do Salesforce (Account) não foi encontrada na Silver. Abortando.")
        return {"run_id": run_id, "status": "SEM_DADOS_SF"}

    from common.identificadores import normalizar_cnpj
    df_fichas["CNPJ_FICHAS"] = df_fichas["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    df_fichas_unique = df_fichas.drop_duplicates(subset=["CNPJ_FICHAS"]).copy()

    col_cnpj_sf = "CNPJ" if "CNPJ" in df_sf.columns else next((c for c in df_sf.columns if "CNPJ" in str(c).upper() or "DOCUMENTO" in str(c).upper()), None)
    
    if not col_cnpj_sf:
        logger.warning("Coluna de CNPJ não encontrada na base do Salesforce.")
        return {"run_id": run_id, "status": "FALHA_MAPEAMENTO_SF"}

    df_sf["CNPJ_SF"] = df_sf[col_cnpj_sf].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    df_sf_unique = df_sf.drop_duplicates(subset=["CNPJ_SF"]).copy()

    df_merge = pd.merge(df_fichas_unique, df_sf_unique, left_on="CNPJ_FICHAS", right_on="CNPJ_SF", how="left", indicator=True)
    
    alertas = []
    df_missing_in_sf = df_merge[df_merge["_merge"] == "left_only"]
    
    for _, row in df_missing_in_sf.iterrows():
        cnpj = row["CNPJ_FICHAS"]
        if cnpj == "00000000000000": continue
        
        msg = "Contraparte possui Ficha de Crédito, mas NÃO foi encontrada na base de Contas do CRM (Salesforce)."
        alertas.append({
            "CODIGO": "SF_001",
            "CNPJ": cnpj,
            "MENSAGEM": msg,
            "SEVERIDADE": "MÉDIA",
            "RUN_ID": run_id,
            "DT_DETECCAO": datetime.now().isoformat(timespec="seconds"),
            "STATUS_ALERTA": "ABERTO"
        })
        registrar_alerta(
            codigo="SF_001",
            severidade="MEDIO",
            regra="Ficha sem Conta CRM",
            mensagem=msg,
            campo_afetado="STATUS_RECONCILIACAO",
            valor_observado="PENDENTE_NO_SALESFORCE",
            limite_esperado="SINCRONIZADO",
            contraparte_id=cnpj,
            run_id=run_id,
            context=context
        )

    relational_dir = context.path("relational_facts") / "reconciliacao"
    relational_dir.mkdir(parents=True, exist_ok=True)
    
    df_resultado = df_merge[["CNPJ_FICHAS", "CNPJ_SF", "_merge"]].copy()
    df_resultado.columns = ["CNPJ", "CNPJ_SALESFORCE", "STATUS_RECONCILIACAO"]
    df_resultado["STATUS_RECONCILIACAO"] = df_resultado["STATUS_RECONCILIACAO"].map({
        "both": "SINCRONIZADO", 
        "left_only": "PENDENTE_NO_SALESFORCE", 
        "right_only": "SOMENTE_SALESFORCE"
    })

    df_resultado.to_csv(relational_dir / "fato_reconciliacao_fichas_salesforce.csv", index=False, sep=";", decimal=",")
    df_resultado.to_parquet(relational_dir / "fato_reconciliacao_fichas_salesforce.parquet", index=False)

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        escrever_conjunto_de_dados_silver(
            records=df_alertas.to_dict(orient="records"), 
            output_dir=silver_dir / "alertas_credito", 
            filename=f"alertas_reconciliacao_sf_{run_id}"
        )

    logger.info("Reconciliação CRM concluída. %d Fichas sem cadastro correspondente no Salesforce.", len(alertas))
    
    return {
        "run_id": run_id, 
        "status": "SUCESSO", 
        "fichas_cruzadas": len(df_fichas_unique),
        "alertas_gerados": len(alertas)
    }