"""
Serviço de Reconciliação: Fichas de Crédito vs Salesforce.
Verifica se todas as contrapartes com ficha de crédito estão devidamente cadastradas no CRM.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from storage.silver_store import write_silver_dataset

LOGGER = logging.getLogger(__name__)

def executar_reconciliacao_fichas_salesforce(context: AppContext) -> dict[str, Any]:
    run_id = f"REC_SF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.reconciliacao_sf")
    
    silver_dir = context.path("silver")

    # 1. Carregar Fichas (Busca ampla nas pastas conhecidas)
    df_fichas = pd.DataFrame()
    for segmento in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        path_seg = silver_dir / segmento
        if path_seg.exists():
            parquets = list(path_seg.glob("*.parquet"))
            if parquets:
                df_seg = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg], ignore_index=True)

    # 2. Carregar Contas do Salesforce (Busca dinâmica e recursiva)
    df_sf = pd.DataFrame()
    
    # Varre a camada Silver inteira atrás de qualquer arquivo Parquet de Account do Salesforce
    arquivos_sf = list(silver_dir.rglob("account*.parquet"))
    if not arquivos_sf:
        # Tenta outro padrão comum de nomenclatura
        arquivos_sf = list(silver_dir.rglob("*salesforce*account*.parquet"))
        
    if arquivos_sf:
        arquivo_sf_mais_recente = max(arquivos_sf, key=lambda f: f.stat().st_mtime)
        df_sf = pd.read_parquet(arquivo_sf_mais_recente)

    # Validação Robusta
    if df_fichas.empty:
        print("\n[AVISO] Base de Fichas está vazia. Abortando reconciliação.")
        return {"run_id": run_id, "status": "SEM_DADOS_FICHAS"}
        
    if df_sf.empty:
        print("\n[AVISO] Base do Salesforce (Account) não foi encontrada na Silver. Abortando.")
        return {"run_id": run_id, "status": "SEM_DADOS_SF"}

    # 3. Normalização de CNPJs (Chave de Negócio)
    df_fichas["CNPJ_FICHAS"] = df_fichas["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
    df_fichas_unique = df_fichas.drop_duplicates(subset=["CNPJ_FICHAS"]).copy()

    # Caça a coluna que guarda o CNPJ dentro do CRM
    col_cnpj_sf = "CNPJ" if "CNPJ" in df_sf.columns else next((c for c in df_sf.columns if "CNPJ" in str(c).upper() or "DOCUMENTO" in str(c).upper()), None)
    
    if not col_cnpj_sf:
        print("\n[AVISO] Coluna de CNPJ não encontrada na base do Salesforce.")
        return {"run_id": run_id, "status": "FALHA_MAPEAMENTO_SF"}

    df_sf["CNPJ_SF"] = df_sf[col_cnpj_sf].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
    df_sf_unique = df_sf.drop_duplicates(subset=["CNPJ_SF"]).copy()

    # 4. Cruzamento Direcional (Left Join a partir das Fichas)
    df_merge = pd.merge(df_fichas_unique, df_sf_unique, left_on="CNPJ_FICHAS", right_on="CNPJ_SF", how="left", indicator=True)
    
    # 5. Geração de Alertas (Fichas sem CRM)
    alertas = []
    df_missing_in_sf = df_merge[df_merge["_merge"] == "left_only"]
    
    for _, row in df_missing_in_sf.iterrows():
        cnpj = row["CNPJ_FICHAS"]
        if cnpj == "00000000000000": continue
        
        alertas.append({
            "CODIGO": "SF_001",
            "CNPJ": cnpj,
            "MENSAGEM": "Contraparte possui Ficha de Crédito, mas NÃO foi encontrada na base de Contas do CRM (Salesforce).",
            "SEVERIDADE": "MÉDIA",
            "RUN_ID": run_id,
            "DT_DETECCAO": datetime.now().isoformat(timespec="seconds"),
            "STATUS_ALERTA": "ABERTO"
        })

    # 6. Salvar Tabela Fato de Reconciliação
    relational_dir = context.path("relational_facts")
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

    # 7. Disparo dos Alertas
    if alertas:
        df_alertas = pd.DataFrame(alertas)
        write_silver_dataset(
            records=df_alertas.to_dict(orient="records"), 
            output_dir=silver_dir / "alertas_credito", 
            filename=f"alertas_reconciliacao_sf_{run_id}"
        )

    # Imprime direto no console para você ver sem precisar abrir logs
    print(f"\n[RECONCILIAÇÃO CRM] Concluída! {len(alertas)} Fichas aprovadas não possuem cadastro correspondente no Salesforce.")
    
    return {
        "run_id": run_id, 
        "status": "SUCESSO", 
        "fichas_cruzadas": len(df_fichas_unique),
        "alertas_gerados": len(alertas)
    }