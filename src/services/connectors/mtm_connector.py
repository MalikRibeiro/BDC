"""Conector de integração com a base de MtM (Risco de Mercado)."""

from __future__ import annotations
from pathlib import Path
from typing import Any
from datetime import datetime
import pandas as pd

from silver.normalizadores import padronizar_cnpj

class MtmConnectionError(Exception):
    """Exceção levantada quando a base de MtM não pode ser obtida."""

def _encontrar_arquivo_mtm_recente(diretorio: Path) -> Path:
    arquivos = [f for f in diretorio.iterdir() if f.is_file() and f.suffix.lower() in {".xlsx", ".xls", ".csv"} and not f.name.startswith("~$")]
    if not arquivos: raise FileNotFoundError(f"Nenhum arquivo de MtM encontrado na pasta: {diretorio}")
    return max(arquivos, key=lambda f: f.stat().st_mtime)

def buscar_mtm_consolidado(input_dir: Path | str, logger: Any | None = None) -> pd.DataFrame:
    diretorio = Path(input_dir)
    diretorio.mkdir(parents=True, exist_ok=True)
    
    try:
        arquivo_fonte = _encontrar_arquivo_mtm_recente(diretorio)
        if logger: logger.info("Lendo base de MtM a partir do arquivo local: %s", arquivo_fonte.name)
        
        if arquivo_fonte.suffix.lower() == ".csv":
            df_bruto = pd.read_csv(arquivo_fonte, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)
        else:
            df_bruto = pd.read_excel(arquivo_fonte, dtype=str)

        df_bruto.columns = [str(c).strip().upper() for c in df_bruto.columns]

        # 1. CNPJ — via validador centralizado
        col_cnpj = next((c for c in df_bruto.columns if "CNPJ" in c and "CONTROLADOR" not in c), None)
        if col_cnpj:
            parsed       = df_bruto[col_cnpj].map(padronizar_cnpj)
            cnpj_series  = parsed.map(lambda t: t[0])
            raiz_series  = parsed.map(lambda t: t[1])
            status_series = parsed.map(lambda t: t[2])
        else:
            cnpj_series   = pd.Series(["00000000000000"] * len(df_bruto), name="CNPJ")
            raiz_series   = pd.Series(["00000000"] * len(df_bruto), name="CNPJ_RAIZ")
            status_series = pd.Series(["CNPJ_AUSENTE"] * len(df_bruto), name="STATUS_CNPJ")

        # 2. MTM TOTAL (Reais)
        if "MTM_TOTAL" in df_bruto.columns:
            raw_mtm = df_bruto["MTM_TOTAL"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            valores_mtm = pd.to_numeric(raw_mtm, errors="coerce").fillna(0.0)
        else:
            valores_mtm = pd.Series([0.0] * len(df_bruto), name="MTM_TOTAL")

        # 3. NOTIONAL FINANCEIRO (MWh * Preço)
        if "ENERGIA_MWH" in df_bruto.columns and "PRECO_REAJUSTADO" in df_bruto.columns:
            vol = df_bruto["ENERGIA_MWH"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            px = df_bruto["PRECO_REAJUSTADO"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            valores_notional = pd.to_numeric(vol, errors="coerce").fillna(0.0) * pd.to_numeric(px, errors="coerce").fillna(0.0)
        else:
            valores_notional = pd.Series([0.0] * len(df_bruto), name="NOTIONAL")

        # 4. Dados Base
        contrato_series = df_bruto.get("COD_CONTRATO", pd.Series([None] * len(df_bruto)))
        data_base_series = df_bruto.get("DATA_AVALIACAO", pd.Series([datetime.now().strftime("%Y-%m-%d")] * len(df_bruto)))

        # 5. Output
        df_resultado = pd.DataFrame({
            "CNPJ":        cnpj_series,
            "CNPJ_RAIZ":   raiz_series,
            "STATUS_CNPJ": status_series,
            "CONTRATO":    contrato_series,
            "DATA_BASE":   data_base_series,
            "MTM_TOTAL":   valores_mtm,
            "NOTIONAL":    valores_notional
        })

        # Filtra registros com CNPJ inválido ou ausente
        df_resultado = df_resultado[df_resultado["STATUS_CNPJ"] == "CNPJ_VALIDO"].copy()

        if logger: logger.info("MtM lido. Notional convertido para Financeiro (R$).")
        return df_resultado

    except Exception as exc:
        if logger: logger.exception("Falha ao processar o arquivo local de MtM.")
        raise MtmConnectionError(f"Erro ao ler base de MtM: {exc}") from exc