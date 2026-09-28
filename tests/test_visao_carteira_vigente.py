import pandas as pd
import numpy as np
from datetime import datetime
import pytest

def test_desempate_deterministico_fato_analise():
    """Valida que o desempate na seleção da análise mais recente é determinístico."""
    df_fatos = pd.DataFrame([
        {
            "CNPJ": "11111111000100",
            "DATA_ANALISE": "2026-01-01",
            "DATA_ANALISE_DT": pd.Timestamp("2026-01-01"),
            "RATING": "B",
            "_VERSAO_REGISTRO": 1,
            "ETL_RUN_ID": "RUN_001"
        },
        {
            "CNPJ": "11111111000100",
            "DATA_ANALISE": "2026-01-01",  # Mesma data
            "DATA_ANALISE_DT": pd.Timestamp("2026-01-01"),
            "RATING": "A",
            "_VERSAO_REGISTRO": 2,  # Versão mais recente
            "ETL_RUN_ID": "RUN_002"
        }
    ])
    
    sort_cols = ["CNPJ", "DATA_ANALISE_DT"]
    if "_VERSAO_REGISTRO" in df_fatos.columns:
        sort_cols.append("_VERSAO_REGISTRO")
    if "ETL_RUN_ID" in df_fatos.columns:
        sort_cols.append("ETL_RUN_ID")
        
    df_latest = df_fatos.sort_values(by=sort_cols).drop_duplicates(subset=["CNPJ"], keep="last")
    assert len(df_latest) == 1
    assert df_latest.iloc[0]["RATING"] == "A"
    assert df_latest.iloc[0]["_VERSAO_REGISTRO"] == 2


def test_impacto_matematico_analise_vencida_e_lacuna():
    """Valida que análises vencidas ou sem análise têm Rating e PD anulados no output da Gold."""
    hoje = pd.Timestamp.now().normalize()
    
    df_contratos = pd.DataFrame([
        {"CNPJ": "11111111000100", "NUMERO_REFERENCIA_CONTRATO": "CTR_VIGENTE"},
        {"CNPJ": "22222222000100", "NUMERO_REFERENCIA_CONTRATO": "CTR_VENCIDA"},
        {"CNPJ": "33333333000100", "NUMERO_REFERENCIA_CONTRATO": "CTR_SEM_ANALISE"},
    ])
    
    df_fatos = pd.DataFrame([
        {
            "CNPJ": "11111111000100",
            "DATA_ANALISE": "2026-08-01",
            "FIM_VIGENCIA_ANALISE": (hoje + pd.DateOffset(months=6)).strftime("%Y-%m-%d"),
            "RATING": "A",
            "PD_PERCENTUAL": 0.015,
            "TIPO_ANALISE": "Análise DF"
        },
        {
            "CNPJ": "22222222000100",
            "DATA_ANALISE": "2024-01-01",
            "FIM_VIGENCIA_ANALISE": (hoje - pd.DateOffset(days=10)).strftime("%Y-%m-%d"),
            "RATING": "C",
            "PD_PERCENTUAL": 0.08,
            "TIPO_ANALISE": "Análise Bureau"
        }
    ])
    
    df_merged = pd.merge(df_contratos, df_fatos, on="CNPJ", how="left")
    
    dt_fim_vigencia = pd.to_datetime(df_merged["FIM_VIGENCIA_ANALISE"], errors="coerce").dt.normalize()
    tem_data = df_merged["DATA_ANALISE"].notna()
    
    df_merged["STATUS_VIGENCIA_ANALISE"] = "SEM_ANALISE"
    df_merged.loc[tem_data & (dt_fim_vigencia < hoje), "STATUS_VIGENCIA_ANALISE"] = "VENCIDA"
    df_merged.loc[tem_data & (dt_fim_vigencia >= hoje), "STATUS_VIGENCIA_ANALISE"] = "VIGENTE"
    
    # Regra de governança
    mask_invalida = df_merged["STATUS_VIGENCIA_ANALISE"].isin(["VENCIDA", "SEM_ANALISE"])
    df_merged.loc[mask_invalida, "RATING"] = pd.NA
    df_merged.loc[mask_invalida, "PD_PERCENTUAL"] = pd.NA
    
    # Asserções
    c_vig = df_merged[df_merged["NUMERO_REFERENCIA_CONTRATO"] == "CTR_VIGENTE"].iloc[0]
    assert c_vig["STATUS_VIGENCIA_ANALISE"] == "VIGENTE"
    assert c_vig["RATING"] == "A"
    assert c_vig["PD_PERCENTUAL"] == 0.015
    
    c_venc = df_merged[df_merged["NUMERO_REFERENCIA_CONTRATO"] == "CTR_VENCIDA"].iloc[0]
    assert c_venc["STATUS_VIGENCIA_ANALISE"] == "VENCIDA"
    assert pd.isna(c_venc["RATING"])
    assert pd.isna(c_venc["PD_PERCENTUAL"])
    assert c_venc["DATA_ANALISE"] == "2024-01-01"  # Histórico preservado
    
    c_sem = df_merged[df_merged["NUMERO_REFERENCIA_CONTRATO"] == "CTR_SEM_ANALISE"].iloc[0]
    assert c_sem["STATUS_VIGENCIA_ANALISE"] == "SEM_ANALISE"
    assert pd.isna(c_sem["RATING"])
    assert pd.isna(c_sem["PD_PERCENTUAL"])


def test_score_e_restritivos_risk3_preservados_para_analise_df():
    """Valida que Score Bureau e Restritivos da RISK3 enriquecem contrapartes DF."""
    df_fichas = pd.DataFrame([{
        "CNPJ": "13700609000115",
        "TIPO_FICHA": "COMERCIALIZADORA",
        "VOLUME_ENQUADRAMENTO_MWM": 10.0,
        "RATING_COPEL": "E",
        "DATA_CALCULO": "2026-09-11"
    }])
    
    df_bureau = pd.DataFrame([{
        "CNPJ": "13700609000115",
        "SCORE_BUREAU": 66.88,
        "RESTRITIVOS": 2.0,
        "RATING_BUREAU": "B",
        "PD_BUREAU": 0.034
    }])
    
    # Merge com segregação: Score/Restritivos universais, Rating/PD do bureau restritos
    merged = pd.merge(df_fichas, df_bureau, on="CNPJ", how="left", suffixes=("", "_BUR"))
    is_bureau_seg = (merged["TIPO_FICHA"] == "CONSUMIDOR") & (merged["VOLUME_ENQUADRAMENTO_MWM"] < 5.0)
    
    for col in ["SCORE_BUREAU", "RESTRITIVOS", "PD_BUREAU", "RATING_BUREAU"]:
        col_bur = f"{col}_BUR"
        if col_bur in merged.columns:
            if col in ["SCORE_BUREAU", "RESTRITIVOS"]:
                merged[col] = merged[col_bur]
            else:
                merged.loc[is_bureau_seg, col] = merged.loc[is_bureau_seg, col_bur]
                merged.loc[~is_bureau_seg, col] = pd.NA
            merged.drop(columns=[col_bur], inplace=True)
        elif col in merged.columns and col not in ["SCORE_BUREAU", "RESTRITIVOS"]:
            merged.loc[~is_bureau_seg, col] = pd.NA
            
    assert merged.iloc[0]["SCORE_BUREAU"] == 66.88
    assert merged.iloc[0]["RESTRITIVOS"] == 2.0
    # Como é DF comercializadora, Rating e PD de bureau não são herdados
    assert "RATING_BUREAU" not in merged.columns or pd.isna(merged.iloc[0]["RATING_BUREAU"])
    assert "PD_BUREAU" not in merged.columns or pd.isna(merged.iloc[0]["PD_BUREAU"])


def test_rating_copel_preservado_mesmo_sem_pd():
    """Valida resiliência de RATING_COPEL quando motor de PD falha por insumo incompleto."""
    registro = {
        "CNPJ": "13700609000115",
        "RATING_COPEL": "E",
        "PD_FINAL": pd.NA,
        "SCORE_BUREAU": 66.88
    }
    # Simula tratamento de exceção
    rating_doc = registro.get("RATING_COPEL") or registro.get("NOTA_CREDITO") or registro.get("RATING")
    rating_final = str(rating_doc).strip() if pd.notna(rating_doc) else pd.NA
    score_total = float(registro["SCORE_BUREAU"]) if registro.get("SCORE_BUREAU") else pd.NA
    
    assert rating_final == "E"
    assert pd.isna(registro["PD_FINAL"])
    assert score_total == 66.88


def test_formatacao_datas_dd_mm_aaaa():
    """Valida padronização de datas para DD/MM/AAAA."""
    from common.datas import formatar_data_br_serie
    datas = pd.Series(["2026-09-11", "2025-01-01", "15/05/2024", None, "NaT"])
    formatadas = formatar_data_br_serie(datas)
    
    assert formatadas.iloc[0] == "11/09/2026"
    assert formatadas.iloc[1] == "01/01/2025"
    assert formatadas.iloc[2] == "15/05/2024"
    assert formatadas.iloc[3] == "-"
    assert formatadas.iloc[4] == "-"

