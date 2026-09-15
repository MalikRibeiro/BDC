"""
=============================================================================
  MOTOR DE DETECÇÃO DE ANOMALIAS – CAMADA SILVER (Data Profiling)
  Versão: 1.0
  Autor: Engenharia de Dados / BD Crédito
=============================================================================
  Executa 4 blocos de testes lógico-contábeis sobre os Parquets Silver
  de Comercializadoras e Consumidores, imprimindo anomalias formatadas.

  Uso:
      python scripts/auditar_anomalias_silver.py
=============================================================================
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO DE CAMINHOS
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SILVER_DIR = PROJECT_ROOT / "SAIDAS" / "silver"

FONTES = {
    "COMERCIALIZADORAS": SILVER_DIR / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet",
    "CONSUMIDORES": SILVER_DIR / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet",
}

# Colunas de identificação para o relatório de anomalias
ID_COLS = ["CNPJ", "arquivo_nome"]

# ---------------------------------------------------------------------------
# REGRAS DE AUDITORIA
# ---------------------------------------------------------------------------

# BLOCO 1 – Microvalores em contas macro de balanço (escala monetária absurda)
CONTAS_MACRO_MONETARIAS = [
    "ATIVO_TOTAL",
    "ATIVO_CIRCULANTE",
    "PASSIVO_CIRCULANTE",
    "PATRIMONIO_LIQUIDO",
    "VENDAS_LIQUIDAS",
    "LUCRO_LIQUIDO",
    "ROL",
]
MICROVALOR_MIN = -10.0
MICROVALOR_MAX = 10.0

# BLOCO 2 – Inconsistência contábil: subgrupo > grupo
REGRAS_SUBGRUPO = [
    ("ATIVO_CIRCULANTE_FINANCEIRO", "ATIVO_CIRCULANTE"),
    ("PASSIVO_CIRCULANTE_FINANCEIRO", "PASSIVO_CIRCULANTE"),
]

# BLOCO 3 – Outliers extremos em ratios/percentuais
RATIOS_PERCENTUAIS = {
    "ROA": (-10.0, 10.0),
    "ROE": (-10.0, 10.0),
    "FCO": (-10.0, 10.0),
    "PROBABILIDADE_DEFAULT": (-10.0, 10.0),
}

# BLOCO 4 – Poluição textual
COLUNAS_TEXTO = ["SIGLA", "EMPRESA", "AUDITOR"]
TEXTO_MAX_LEN = 60
PALAVRAS_TEMPLATE = ["DADOS", "EXEMPLO", "MIL", "PREENCHIMENTO", "DEMONSTRAÇÕES", "FINANCEIRAS", "INSTRUÇÕES"]


# ---------------------------------------------------------------------------
# UTILITÁRIOS DE FORMATAÇÃO
# ---------------------------------------------------------------------------

SEPARATOR = "=" * 100
SUBSEPARATOR = "-" * 100

def _header(titulo: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {titulo}")
    print(SEPARATOR)

def _subheader(subtitulo: str) -> None:
    print(f"\n{SUBSEPARATOR}")
    print(f"  {subtitulo}")
    print(SUBSEPARATOR)

def _print_anomalias(df_anom: pd.DataFrame, colunas_exibir: list[str], max_rows: int = 30) -> None:
    """Imprime as anomalias de forma tabular e legível."""
    if df_anom.empty:
        print("  ✅ Nenhuma anomalia encontrada.")
        return

    total = len(df_anom)
    print(f"  ⚠️  Total de anomalias: {total}")
    
    cols_disponiveis = [c for c in colunas_exibir if c in df_anom.columns]
    if not cols_disponiveis:
        print("  (colunas de exibição não encontradas no DataFrame)")
        return

    df_show = df_anom[cols_disponiveis].head(max_rows).copy()

    for col in df_show.columns:
        if pd.api.types.is_float_dtype(df_show[col]):
            df_show[col] = df_show[col].apply(lambda x: f"{x:,.4f}" if pd.notna(x) else "NaN")
        else:
            df_show[col] = df_show[col].astype(str).str[:80]

    print(df_show.to_string(index=False))

    if total > max_rows:
        print(f"\n  ... e mais {total - max_rows} registros omitidos.")


def _cols_presentes(df: pd.DataFrame, cols: list[str]) -> list[str]:
    return [c for c in cols if c in df.columns]


# ---------------------------------------------------------------------------
# BLOCOS DE TESTES
# ---------------------------------------------------------------------------

def teste_microvalores(df: pd.DataFrame, segmento: str) -> int:
    """BLOCO 1: Contas macro com valores entre -10 e 10 (excluindo zero)."""
    _subheader(f"BLOCO 1 – Microvalores Monetários Absurdos [{segmento}]")
    
    total_anomalias = 0
    cols = _cols_presentes(df, CONTAS_MACRO_MONETARIAS)
    
    if not cols:
        print("  (nenhuma coluna macro monetária encontrada)")
        return 0
    
    for col in cols:
        serie = pd.to_numeric(df[col], errors="coerce")
        mask = (serie.abs() > 0) & (serie.abs() < abs(MICROVALOR_MAX))
        df_anom = df[mask].copy()
        
        if not df_anom.empty:
            df_anom["_VALOR_SUSPEITO"] = serie[mask]
            print(f"\n  📌 Coluna: {col}  →  {len(df_anom)} registro(s) com valor entre ({MICROVALOR_MIN}, {MICROVALOR_MAX}), excl. zero")
            id_cols_disp = _cols_presentes(df_anom, ID_COLS)
            _print_anomalias(df_anom, id_cols_disp + ["_VALOR_SUSPEITO", "versao_ficha"])
            total_anomalias += len(df_anom)
    
    if total_anomalias == 0:
        print("  ✅ Nenhuma anomalia encontrada neste bloco.")
    
    return total_anomalias


def teste_subgrupo_maior_que_grupo(df: pd.DataFrame, segmento: str) -> int:
    """BLOCO 2: Subgrupo financeiro > grupo principal."""
    _subheader(f"BLOCO 2 – Inconsistência Contábil: Subgrupo > Grupo [{segmento}]")
    
    total_anomalias = 0
    
    for col_sub, col_grupo in REGRAS_SUBGRUPO:
        if col_sub not in df.columns or col_grupo not in df.columns:
            continue
        
        sub = pd.to_numeric(df[col_sub], errors="coerce")
        grupo = pd.to_numeric(df[col_grupo], errors="coerce")
        
        # Ambos devem ser positivos e não-nulos para a comparação fazer sentido
        mask = (sub.notna()) & (grupo.notna()) & (grupo > 0) & (sub > grupo)
        df_anom = df[mask].copy()
        
        if not df_anom.empty:
            df_anom["_SUBGRUPO"] = sub[mask]
            df_anom["_GRUPO"] = grupo[mask]
            df_anom["_RAZAO"] = (sub[mask] / grupo[mask]).round(2)
            print(f"\n  📌 Regra: {col_sub} > {col_grupo}  →  {len(df_anom)} registro(s)")
            id_cols_disp = _cols_presentes(df_anom, ID_COLS)
            _print_anomalias(df_anom, id_cols_disp + ["_SUBGRUPO", "_GRUPO", "_RAZAO", "versao_ficha"])
            total_anomalias += len(df_anom)
    
    if total_anomalias == 0:
        print("  ✅ Nenhuma anomalia encontrada neste bloco.")
    
    return total_anomalias


def teste_outliers_ratios(df: pd.DataFrame, segmento: str) -> int:
    """BLOCO 3: Ratios/percentuais fora de limites razoáveis."""
    _subheader(f"BLOCO 3 – Outliers Extremos em Ratios/Percentuais [{segmento}]")
    
    total_anomalias = 0
    
    for col, (lim_inf, lim_sup) in RATIOS_PERCENTUAIS.items():
        if col not in df.columns:
            continue
        
        serie = pd.to_numeric(df[col], errors="coerce")
        mask = serie.notna() & ((serie > lim_sup) | (serie < lim_inf))
        df_anom = df[mask].copy()
        
        if not df_anom.empty:
            df_anom["_VALOR_OUTLIER"] = serie[mask]
            print(f"\n  📌 Coluna: {col}  →  {len(df_anom)} registro(s) fora de [{lim_inf}, {lim_sup}]")
            id_cols_disp = _cols_presentes(df_anom, ID_COLS)
            _print_anomalias(df_anom, id_cols_disp + ["_VALOR_OUTLIER", "versao_ficha"])
            total_anomalias += len(df_anom)
    
    if total_anomalias == 0:
        print("  ✅ Nenhuma anomalia encontrada neste bloco.")
    
    return total_anomalias


def teste_poluicao_textual(df: pd.DataFrame, segmento: str) -> int:
    """BLOCO 4: Textos longos ou com palavras de template/instrução."""
    _subheader(f"BLOCO 4 – Poluição Textual em Campos de String [{segmento}]")
    
    total_anomalias = 0
    cols = _cols_presentes(df, COLUNAS_TEXTO)
    
    if not cols:
        print("  (nenhuma coluna textual alvo encontrada)")
        return 0
    
    for col in cols:
        serie = df[col].astype(str).replace({"nan": "", "None": "", "NaT": ""})
        
        # Sub-teste A: Texto suspeitamente longo
        mask_longo = serie.str.len() > TEXTO_MAX_LEN
        df_longo = df[mask_longo].copy()
        
        if not df_longo.empty:
            df_longo["_TEXTO_SUSPEITO"] = serie[mask_longo].str[:80]
            df_longo["_TAMANHO"] = serie[mask_longo].str.len()
            print(f"\n  📌 Coluna: {col}  →  {len(df_longo)} registro(s) com texto > {TEXTO_MAX_LEN} caracteres")
            id_cols_disp = _cols_presentes(df_longo, ID_COLS)
            _print_anomalias(df_longo, id_cols_disp + ["_TEXTO_SUSPEITO", "_TAMANHO"])
            total_anomalias += len(df_longo)
        
        # Sub-teste B: Palavras típicas de template/instrução
        pattern = "|".join(PALAVRAS_TEMPLATE)
        mask_template = serie.str.contains(pattern, case=False, na=False) & (serie.str.len() > 5)
        df_template = df[mask_template].copy()
        
        if not df_template.empty:
            df_template["_TEXTO_CONTAMINADO"] = serie[mask_template].str[:80]
            print(f"\n  📌 Coluna: {col}  →  {len(df_template)} registro(s) com palavras de template ({pattern})")
            id_cols_disp = _cols_presentes(df_template, ID_COLS)
            _print_anomalias(df_template, id_cols_disp + ["_TEXTO_CONTAMINADO"])
            total_anomalias += len(df_template)
    
    if total_anomalias == 0:
        print("  ✅ Nenhuma anomalia encontrada neste bloco.")
    
    return total_anomalias


# ---------------------------------------------------------------------------
# ORQUESTRADOR PRINCIPAL
# ---------------------------------------------------------------------------

def auditar_segmento(path: Path, segmento: str) -> dict:
    """Executa todos os 4 blocos de testes para um segmento."""
    _header(f"AUDITORIA SILVER – {segmento}")
    
    if not path.exists():
        print(f"  ⏭️  Arquivo não encontrado: {path}. Pulando segmento.")
        return {"segmento": segmento, "status": "ARQUIVO_NAO_ENCONTRADO", "total_anomalias": 0}
    
    df = pd.read_parquet(path)
    
    # Filtrar apenas registros VIGENTES se a coluna existir
    if "_STATUS_REGISTRO" in df.columns:
        df = df[df["_STATUS_REGISTRO"] == "VIGENTE"].copy()
    
    print(f"  📊 Registros vigentes carregados: {len(df)}")
    print(f"  📊 Colunas disponíveis: {len(df.columns)}")
    
    resultados = {
        "segmento": segmento,
        "registros": len(df),
        "bloco_1_microvalores": teste_microvalores(df, segmento),
        "bloco_2_subgrupo": teste_subgrupo_maior_que_grupo(df, segmento),
        "bloco_3_outliers": teste_outliers_ratios(df, segmento),
        "bloco_4_poluicao": teste_poluicao_textual(df, segmento),
    }
    
    resultados["total_anomalias"] = sum([
        resultados["bloco_1_microvalores"],
        resultados["bloco_2_subgrupo"],
        resultados["bloco_3_outliers"],
        resultados["bloco_4_poluicao"],
    ])
    
    return resultados


def main():
    print(SEPARATOR)
    print("  MOTOR DE DETECÇÃO DE ANOMALIAS – CAMADA SILVER (Data Profiling)")
    print(f"  Diretório Silver: {SILVER_DIR}")
    print(SEPARATOR)
    
    resumo_global = []
    
    for segmento, path in FONTES.items():
        resultado = auditar_segmento(path, segmento)
        resumo_global.append(resultado)
    
    # -----------------------------------------------------------------------
    # RESUMO CONSOLIDADO
    # -----------------------------------------------------------------------
    _header("RESUMO CONSOLIDADO DA AUDITORIA")
    
    total_geral = 0
    for r in resumo_global:
        seg = r["segmento"]
        total = r.get("total_anomalias", 0)
        total_geral += total
        
        status_icon = "🔴" if total > 0 else "🟢"
        print(f"  {status_icon} {seg}: {total} anomalia(s) detectada(s)")
        
        if total > 0:
            print(f"      ├─ Bloco 1 (Microvalores):     {r.get('bloco_1_microvalores', 0)}")
            print(f"      ├─ Bloco 2 (Subgrupo > Grupo): {r.get('bloco_2_subgrupo', 0)}")
            print(f"      ├─ Bloco 3 (Outliers Ratios):  {r.get('bloco_3_outliers', 0)}")
            print(f"      └─ Bloco 4 (Poluição Texto):   {r.get('bloco_4_poluicao', 0)}")
    
    print(f"\n  {'🔴 TOTAL GERAL DE ANOMALIAS' if total_geral > 0 else '🟢 NENHUMA ANOMALIA DETECTADA'}: {total_geral}")
    print(SEPARATOR)
    
    return 1 if total_geral > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
