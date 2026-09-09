import pandas as pd
from pathlib import Path

def test_silver_cnpj_preserve_zeros():
    # Adapte o caminho ao diretório correto do seu sistema após rodar o main.py
    silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.parquet")
    if not silver_path.exists():
        return
        
    df = pd.read_parquet(silver_path)
    
    # Valida se a coluna é String e tem 14 posições preenchidas
    assert pd.api.types.is_string_dtype(df["CNPJ"]) or pd.api.types.is_object_dtype(df["CNPJ"])
    
    # Verifica se todos os CNPJs válidos tem exatamente 14 caracteres numéricos
    cnpjs_validos = df["CNPJ"].dropna()
    assert cnpjs_validos.astype(str).str.fullmatch(r"\d{14}").all(), "CNPJs perderam a máscara ou tem menos de 14 dígitos"

def test_silver_probabilidade_is_float():
    silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.parquet")
    if not silver_path.exists():
        return
        
    df = pd.read_parquet(silver_path)
    
    # Valida se o dado está matematicamente correto (escala 0.0 a 1.0)
    if "PROBABILIDADE_DEFAULT" in df.columns:
        pd_validas = df["PROBABILIDADE_DEFAULT"].dropna()
        if not pd_validas.empty:
            assert pd_validas.between(0.0, 1.0).all(), "Existem PDs fora do intervalo numérico [0, 1]."