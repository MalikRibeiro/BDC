import pandas as pd
import json
from pathlib import Path
import warnings

def generate_audit_report():
    # Ignorar warnings do pandas para to_numeric
    warnings.filterwarnings('ignore')

    # 1. Carregar catálogo
    catalog_path = Path("ENTRADAS/control/quality/master_catalog_comercializadoras.json")
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    
    fields = catalog.get("fields", {})
    observed_fields = {k: v for k, v in fields.items() if v.get("nature") == "OBSERVED"}
    
    # 2. Carregar dados da Silver
    silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.parquet")
    if not silver_path.exists():
        silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.csv")
        if not silver_path.exists():
            print("Base Silver não encontrada (nem Parquet, nem CSV).")
            return
            
    if silver_path.suffix == ".parquet":
        df = pd.read_parquet(silver_path)
    else:
        df = pd.read_csv(silver_path, sep=";")
        
    N = len(df)
    
    # 3. Gerar relatório
    report_lines = []
    report_lines.append("# Relatório de Auditoria - Silver Comercializadoras")
    report_lines.append(f"Total de registros na base (N): {N}\n")
    
    for field_name, metadata in observed_fields.items():
        f_type = metadata.get("type", "text")
        f_enum = metadata.get("enum", [])
        
        report_lines.append(f"## Campo: `{field_name}`")
        report_lines.append(f"- **Tipo de Dado (Catálogo):** {f_type}")
        
        if field_name not in df.columns:
            report_lines.append("- **Status:** Ausente na base Silver.\n")
            continue
            
        s = df[field_name]
        nulos = s.isna().sum()
        pct_nulo = (nulos / N) * 100 if N > 0 else 0
        report_lines.append(f"- **Total Nulos:** {nulos} ({pct_nulo:.2f}%)")
        
        if f_type in ["float", "integer", "number"]:
            # Força numérico para estatísticas
            s_num = pd.to_numeric(s, errors="coerce")
            
            zeros = (s_num == 0).sum()
            pct_zero = (zeros / N) * 100 if N > 0 else 0
            negativos = (s_num < 0).sum()
            
            report_lines.append(f"- **Total Zeros:** {zeros} ({pct_zero:.2f}%)")
            report_lines.append(f"- **Total Negativos:** {negativos}")
            
            s_dropna = s_num.dropna()
            if not s_dropna.empty:
                v_min = s_dropna.min()
                v_max = s_dropna.max()
                v_mean = s_dropna.mean()
                report_lines.append(f"- **Mínimo:** {v_min:.4f}")
                report_lines.append(f"- **Máximo:** {v_max:.4f}")
                report_lines.append(f"- **Média:** {v_mean:.4f}")
            else:
                report_lines.append("- **Estatísticas:** Todos os valores numéricos são nulos ou inválidos.")
                
        else: # Categórico, Data, Texto, CNPJ
            distintos = s.nunique(dropna=True)
            report_lines.append(f"- **Valores Distintos:** {distintos}")
            
            if f_enum:
                # Converte o enum para string p/ garantir comparabilidade
                enum_str = [str(e) for e in f_enum]
                fora_enum = s.dropna()[~s.dropna().astype(str).isin(enum_str)].count()
                report_lines.append(f"- **Valores fora do enum {f_enum}:** {fora_enum}")
            
            top_15 = s.value_counts(dropna=True).head(15)
            if not top_15.empty:
                report_lines.append("- **Top 15 valores mais frequentes:**")
                for val, count in top_15.items():
                    report_lines.append(f"  - `{val}`: {count} ocorrências")
            
        report_lines.append("")
        
    report_text = "\n".join(report_lines)
    
    # 4. Salvar saída
    out_file = Path("auditoria_silver_comercializadoras.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print(f"[+] Auditoria concluída! Relatório salvo em: {out_file.absolute()}")
    print("-" * 40)
    print("Previa dos primeiros campos:")
    print("\n".join(report_lines[:25]))

if __name__ == "__main__":
    generate_audit_report()
