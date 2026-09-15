import json
import warnings
from pathlib import Path
import pandas as pd
from typing import Any, Dict, List, Union

_KNOWN_EXTENSIONS = (".parquet", ".csv")

def _normalize_filename(filename: str) -> str:
    """Remove extensões conhecidas (.csv, .parquet) do filename recebido."""
    stem = filename.strip()
    for ext in _KNOWN_EXTENSIONS:
        if stem.lower().endswith(ext):
            stem = stem[: -len(ext)]
            break
    return stem

def escrever_conjunto_de_dados_silver(
    records: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    filename: str,
    sep: str = ";",
    decimal: str = ",",
    encoding: str = "utf-8-sig",
) -> tuple[Path, Path]:
    """Persiste a lista de registros normalizados em CSV e Parquet."""
    filename = _normalize_filename(filename)

    if not records:
        csv_path = Path(output_dir) / f"{filename}.csv"
        parquet_path = Path(output_dir) / f"{filename}.parquet"
        return csv_path, parquet_path

    df = pd.DataFrame(records)

    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False, default=str) if isinstance(x, (list, dict)) else x)
            
        elif pd.api.types.is_datetime64_any_dtype(df[col]) or "data" in col.lower() or "date" in col.lower() or col.lower().startswith("dt_") or col.startswith("_DT_") or "vencimento" in col.lower():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True).dt.strftime("%Y-%m-%d")
            
        elif not (pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col])):
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
        elif pd.api.types.is_object_dtype(df[col]):
            df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else None)

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    csv_path = target_dir / f"{filename}.csv"
    parquet_path = target_dir / f"{filename}.parquet"

    df.to_csv(
        csv_path, 
        index=False, 
        sep=sep, 
        decimal=decimal, 
        encoding=encoding, 
        date_format="%d/%m/%Y"
    )
    df.to_parquet(parquet_path, index=False, engine="pyarrow", compression="snappy")

    return csv_path, parquet_path

def mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
    records: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    filename: str,
    business_keys: List[str],
    sep: str = ";",
    decimal: str = ",",
    encoding: str = "utf-8-sig",
) -> tuple[Path, Path]:
    """Realiza o merge incremental preservando histórico completo (SCD Tipo 2)."""
    filename = _normalize_filename(filename)
    target_dir = Path(output_dir)
    parquet_path = target_dir / f"{filename}.parquet"

    if not records:
        return parquet_path, parquet_path

    df_new = pd.DataFrame(records)
    df_new["_DT_CARGA"] = pd.Timestamp.now()

    for col in df_new.columns:
        if df_new[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df_new[col] = df_new[col].apply(lambda x: json.dumps(x, ensure_ascii=False, default=str) if isinstance(x, (list, dict)) else x)
        
        if "data" in col.lower() or "date" in col.lower() or col.lower().startswith("dt_"):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                df_new[col] = pd.to_datetime(df_new[col], errors="coerce", dayfirst=True)

    if parquet_path.exists():
        df_existing = pd.read_parquet(parquet_path)

        if "_VERSAO_REGISTRO" not in df_existing.columns:
            df_existing["_VERSAO_REGISTRO"] = 1
        
        if "_DT_CARGA" not in df_existing.columns:
            df_existing["_DT_CARGA"] = pd.NaT
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                df_existing["_DT_CARGA"] = pd.to_datetime(df_existing["_DT_CARGA"], errors="coerce", dayfirst=True)
            
        if "_STATUS_REGISTRO" not in df_existing.columns:
            df_existing["_STATUS_REGISTRO"] = "VIGENTE"

        for b_key in business_keys:
            if b_key in df_existing.columns and b_key in df_new.columns:
                if pd.api.types.is_datetime64_any_dtype(df_existing[b_key]) and not pd.api.types.is_datetime64_any_dtype(df_new[b_key]):
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        df_new[b_key] = pd.to_datetime(df_new[b_key], errors="coerce", dayfirst=True)
                elif not pd.api.types.is_datetime64_any_dtype(df_existing[b_key]) and pd.api.types.is_datetime64_any_dtype(df_new[b_key]):
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        df_existing[b_key] = pd.to_datetime(df_existing[b_key], errors="coerce", dayfirst=True)
                else:
                    df_new[b_key] = df_new[b_key].astype(df_existing[b_key].dtype)

        df_existing_keys = df_existing[business_keys].drop_duplicates()
        df_new_keys = df_new[business_keys].drop_duplicates()
        
        keys_to_replace = pd.merge(df_existing_keys, df_new_keys, on=business_keys, how='inner')
        if not keys_to_replace.empty:
            cond_atualizacao = df_existing.set_index(business_keys).index.isin(keys_to_replace.set_index(business_keys).index)
            df_existing.loc[cond_atualizacao, "_STATUS_REGISTRO"] = "SUBSTITUIDO"

        max_versoes = (
            df_existing.groupby(business_keys, dropna=False)["_VERSAO_REGISTRO"]
            .max()
            .reset_index()
            .rename(columns={"_VERSAO_REGISTRO": "_MAX_VERSAO"})
        )

        df_new = pd.merge(df_new, max_versoes, on=business_keys, how="left")
        df_new["_MAX_VERSAO"] = df_new["_MAX_VERSAO"].fillna(0).astype(int)
    else:
        df_existing = pd.DataFrame()
        df_new["_MAX_VERSAO"] = 0

    if "dt_processamento" in df_new.columns:
        df_new = df_new.sort_values(by=business_keys + ["dt_processamento"])

    df_new["rank_interno"] = df_new.groupby(business_keys).cumcount() + 1
    df_new["_VERSAO_REGISTRO"] = df_new["_MAX_VERSAO"] + df_new["rank_interno"]
    df_new = df_new.drop(columns=["_MAX_VERSAO", "rank_interno"])

    df_new["_STATUS_REGISTRO"] = "SUBSTITUIDO"
    idx_vigentes = df_new.groupby(business_keys)["_VERSAO_REGISTRO"].idxmax()
    df_new.loc[idx_vigentes, "_STATUS_REGISTRO"] = "VIGENTE"

    if not df_existing.empty:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
        
    df_new["_STATUS_REGISTRO"] = "SUBSTITUIDO"
    idx_vigentes = df_new.groupby(business_keys)["_VERSAO_REGISTRO"].idxmax()
    df_new.loc[idx_vigentes, "_STATUS_REGISTRO"] = "VIGENTE"

    if not df_existing.empty:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    qtd_inseridos = len(df_new)
    qtd_atualizados = len(keys_to_replace) if 'keys_to_replace' in locals() and not keys_to_replace.empty else 0
    
    import logging
    temp_logger = logging.getLogger("bdc.comercializadoras")

    return escrever_conjunto_de_dados_silver(
        records=df_combined.to_dict(orient="records"),
        output_dir=output_dir,
        filename=filename,
        sep=sep,
        decimal=decimal,
        encoding=encoding
    )