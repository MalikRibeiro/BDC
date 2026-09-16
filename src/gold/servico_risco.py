import pandas as pd
from common.dados import validar_coluna_cnpj_canonica
from gold.regras_gold import checar_contrato_obrigatorio

def integrar_risco_gold(df_gold: pd.DataFrame, df_risco: pd.DataFrame, df_reconciliacao: pd.DataFrame) -> pd.DataFrame:
    if not df_risco.empty:
        erros = validar_coluna_cnpj_canonica(df_risco)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (risco): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_risco, ["CNPJ"], "risco")
        df_risco = df_risco.drop_duplicates(subset=["CNPJ"], keep="last")
        
        if "PE_REAIS" in df_risco.columns:
            cols_risco = [c for c in ["CNPJ", "EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"] if c in df_risco.columns]
            df_gold = pd.merge(df_gold, df_risco[cols_risco], on="CNPJ", how="left")
        else:
            col_mtm = "FINANCEIRO_MTM" if "FINANCEIRO_MTM" in df_risco.columns else ("MTM" if "MTM" in df_risco.columns else None)
            if col_mtm:
                df_gold = pd.merge(df_gold, df_risco[["CNPJ", col_mtm]].rename(columns={col_mtm: "EAD_VALOR"}), on="CNPJ", how="left")
                df_gold["PE_REAIS"] = 0.0

    if not df_reconciliacao.empty:
        erros = validar_coluna_cnpj_canonica(df_reconciliacao)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (reconciliacao): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_reconciliacao, ["CNPJ"], "reconciliacao")
        df_reconciliacao = df_reconciliacao.drop_duplicates(subset=["CNPJ"], keep="last")
        
        cols_recon = [c for c in ["CNPJ", "STATUS_CONCILIACAO", "MTM_POSITIVO_TOTAL"] if c in df_reconciliacao.columns]
        df_gold = pd.merge(df_gold, df_reconciliacao[cols_recon], on="CNPJ", how="left")
        
        if "MTM_POSITIVO_TOTAL" in df_gold.columns:
            df_gold["POSICAO_MTM"] = pd.to_numeric(df_gold["MTM_POSITIVO_TOTAL"], errors="coerce").fillna(0.0)
            df_gold = df_gold.drop(columns=["MTM_POSITIVO_TOTAL"])
        else:
            df_gold["POSICAO_MTM"] = 0.0
            
        if "STATUS_CONCILIACAO" not in df_gold.columns:
            df_gold["STATUS_CONCILIACAO"] = "DIVERGENTE"
    else:
        df_gold["POSICAO_MTM"] = 0.0
        df_gold["STATUS_CONCILIACAO"] = "DIVERGENTE"
        
    return df_gold
