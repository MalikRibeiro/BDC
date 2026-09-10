import pandas as pd
from pathlib import Path
import json

base = Path(r"c:\Users\C807951\Desktop\BDC")

# 1(a) main.py active blocks
with open(base / "main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
    
in_pipeline = False
active_steps = []
for line in lines:
    if "PIPELINE_STEPS = [" in line:
        in_pipeline = True
    elif in_pipeline and "]" in line and line.strip() == "]":
        break
    elif in_pipeline:
        if line.strip().startswith("PipelineStep"):
            active_steps.append(line.strip())
        elif line.strip().startswith("#"):
            active_steps.append(line.strip())

# 1(b) GAR_001
path_alertas = base / "SAIDAS" / "relational" / "facts" / "alertas" / "fato_alerta_credito.parquet"
if path_alertas.exists():
    df_al = pd.read_parquet(path_alertas)
    df_gar = df_al[df_al["CODIGO_ALERTA"] == "GAR_001"].head(5)
    amostra_gar = df_gar[["CNPJ", "VALOR_OBSERVADO", "MENSAGEM_DESCRITIVA"]].to_dict("records")
else:
    amostra_gar = "Não encontrado"

# 1(c) Counts
path_com_stg = base / "SAIDAS" / "staging" / "comercializadoras" / "extracted"
count_stg_com = len(list(path_com_stg.glob("*.json"))) if path_com_stg.exists() else 0

path_con_stg = base / "SAIDAS" / "staging" / "consumidores" / "extracted"
count_stg_con = len(list(path_con_stg.glob("*.json"))) if path_con_stg.exists() else 0

path_gold = base / "SAIDAS" / "gold" / "visao_operacional_negocio" / "Visao_Operacional_BDC_LATEST.parquet"
if path_gold.exists():
    df_gold = pd.read_parquet(path_gold)
    count_gold = len(df_gold)
else:
    count_gold = 0

# 5(a) fato_score_rating_pd e fato_migracao_rating
path_score = base / "SAIDAS" / "relational" / "facts" / "credito" / "fato_score_rating_pd.parquet"
path_mig = base / "SAIDAS" / "relational" / "facts" / "credito" / "fato_migracao_rating.parquet"

score_exists = path_score.exists()
mig_exists = path_mig.exists()

print("==== EVIDÊNCIAS ====")
print(f"1(a) Pipeline Ativo em main.py:")
for s in active_steps: print(s)

print(f"\n1(b) Amostra GAR_001: {amostra_gar}")

print(f"\n1(c) Staging Comerc: {count_stg_com} | Staging Consum: {count_stg_con} | Total: {count_stg_com+count_stg_con} | Gold: {count_gold}")

print(f"\n5(a) Fatos de Histórico existem? score_rating_pd={score_exists}, migracao_rating={mig_exists}")
