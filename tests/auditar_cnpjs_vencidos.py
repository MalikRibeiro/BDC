import pandas as pd
from pathlib import Path
from datetime import datetime

CNPJS_ALVO = [
    "30306294000226",  # BANCO BTG
    "18384740000134",  # BC ENERGIA
    "14609649000119",  # BOVEN ENERGIA
    "31864869000108",  # BP COMERCIALIZADORA
    "19572597000258",  # EMBALIXO
    "07685694000510",  # ENERGISA
    "31635668000139",  # ENGIE TRADING
    "09316105001877",  # FRIOVIX
    "08032643000129",  # MARACANA
    "04023261000188",  # NC ENERGIA
    "03538572000117",  # PETROBRAS
    "13338734000127",  # RBE
    "09495582000107",  # SAFIRA
    "04270778000171",  # SANTANDER
    "09149503000106",  # SERENA
    "39702802000189",  # SOL SERRA DO MEL III
    "13459301000120",  # SOLENERGIAS
    "08573833000153",  # STATKRAFT
    "68457727000136",  # VILA GERMANICA
]

data_hoje = datetime.now().date()

# 1. Carregar Fato Analise de Credito
p_fato = Path("SAIDAS/relational/fato_analise_credito/fato_analise_credito.parquet")
df_fato = pd.read_parquet(p_fato) if p_fato.exists() else pd.DataFrame()

# 2. Carregar Controladoras Silver
p_ctrl = Path("SAIDAS/silver/mapeamento_controladoras/mapeamento_controladoras.parquet")
df_ctrl = pd.read_parquet(p_ctrl) if p_ctrl.exists() else pd.DataFrame()

# 3. Carregar Salesforce Account Silver
p_sf_acc = Path("SAIDAS/silver/salesforce_silver/account/salesforce_account.parquet")
df_sf = pd.read_parquet(p_sf_acc) if p_sf_acc.exists() else pd.DataFrame()

# 4. Carregar Gold Carteira
p_gold = Path("SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet")
df_gold = pd.read_parquet(p_gold) if p_gold.exists() else pd.DataFrame()

print("="*100)
print(f"RELATÓRIO DE AUDITORIA DE CNPJs VENCIDOS / SEM ANÁLISE (DATA REF: {data_hoje})")
print("="*100)

for cnpj in CNPJS_ALVO:
    print(f"\n>>> CNPJ: {cnpj}")
    
    # Gold
    if not df_gold.empty:
        rows_g = df_gold[df_gold["CONTRAPARTE_CNPJ"].astype(str).str.strip() == cnpj]
        if not rows_g.empty:
            g = rows_g.iloc[0]
            print(f"  [GOLD] Contraparte: {g.get('CONTRAPARTE')} | Status Análise: {g.get('STATUS_ANALISE')} | Tipo: {g.get('TIPO_ANALISE')}")
            print(f"         Data Análise: {g.get('DATA_ANALISE')} | Fim Vigência: {g.get('DATA_FIM_VIGENCIA')} | Rating: {g.get('RATING')} | PD: {g.get('PD')}")
        else:
            print("  [GOLD] Não encontrado nos contratos da Gold.")

    # Fato Analise Credito
    if not df_fato.empty:
        rows_f = df_fato[df_fato["CNPJ"].astype(str).str.strip() == cnpj]
        if not rows_f.empty:
            f = rows_f.iloc[0]
            print(f"  [FATO] Segmento: {f.get('SEGMENTO_PD')} | Data DF: {f.get('DATA_DF')} | Fim Vigência: {f.get('DATA_FIM_VIGENCIA')} | Rating Final: {f.get('RATING_FINAL')}")
            print(f"         Herdada: {f.get('ANALISE_HERDADA')} | Origem: {f.get('ORIGEM_ANALISE')} | Fonte: {f.get('FONTE_ANALISE')}")
        else:
            print("  [FATO] CNPJ não possui registro próprio na fato_analise_credito.")

    # Controladoras CSV / Silver
    if not df_ctrl.empty:
        rows_c = df_ctrl[df_ctrl["CNPJ_SUBSIDIARIA"].astype(str).str.strip() == cnpj]
        if not rows_c.empty:
            for _, c_row in rows_c.iterrows():
                matriz_cnpj = str(c_row.get("CNPJ_CONTA_ATRELADA")).strip()
                matriz_nome = c_row.get("CONTA_ATRELADA")
                # Status da Matriz na Fato
                matriz_fato = df_fato[df_fato["CNPJ"].astype(str).str.strip() == matriz_cnpj] if not df_fato.empty else pd.DataFrame()
                if not matriz_fato.empty:
                    mf = matriz_fato.iloc[0]
                    print(f"  [CONTROLADORA] Mapeado para Matriz: {matriz_nome} (CNPJ {matriz_cnpj})")
                    print(f"                 Status Matriz na Fato -> Rating: {mf.get('RATING_FINAL')} | DF: {mf.get('DATA_DF')} | Vigência: {mf.get('DATA_FIM_VIGENCIA')}")
                else:
                    print(f"  [CONTROLADORA] Mapeado para Matriz: {matriz_nome} (CNPJ {matriz_cnpj}) -> Matriz SEM registro na Fato!")
        else:
            print("  [CONTROLADORA] Não mapeado no arquivo de Controladoras.")

    # Salesforce
    if not df_sf.empty:
        rows_s = df_sf[df_sf["CNPJ"].astype(str).str.strip() == cnpj]
        if not rows_s.empty:
            s = rows_s.iloc[0]
            print(f"  [SALESFORCE] Nome: {s.get('Name')} | Grupo Econômico: {s.get('Grupo_economico__c')} | Rating: {s.get('Rating_SF') if 'Rating_SF' in s else s.get('Rating__c')}")
        else:
            print("  [SALESFORCE] Sem registro de Conta no Salesforce.")

print("\n" + "="*100)
print("FIM DA AUDITORIA.")
print("="*100)
