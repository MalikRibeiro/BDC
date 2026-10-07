"""Script de Rastreamento de Linhagem de Dados (Data Lineage Tracing) de Ponta a Ponta.

Investiga os seguintes CNPJs críticos:
- 21812954000179: EDF EN DO BRASIL
- 36205095000127: SERRA DO MATO III
- 35823536000191: JANDAIRA III
- 02016507000169: AXIA ENERGIA
- 35742218000196: QAIR BRASIL
- 37427691000180: THOPEN ENERGIA
"""
from pathlib import Path
import json
import pandas as pd

CNPJS_ALVO = {
    "21812954000179": "EDF EN DO BRASIL",
    "36205095000127": "SERRA DO MATO III",
    "35823536000191": "JANDAIRA III",
    "02016507000169": "AXIA ENERGIA",
    "35742218000196": "QAIR BRASIL",
    "37427691000180": "THOPEN ENERGIA"
}

def normalizar_cnpj(c):
    if not c or pd.isna(c):
        return ""
    import re
    s = re.sub(r"\D", "", str(c))
    return s.zfill(14) if len(s) > 8 else s

def main():
    print("=" * 90)
    print("🔍 BDC — DATA LINEAGE TRACING DE PONTA A PONTA (REVERSE AUDIT)")
    print("=" * 90)

    # --------------------------------------------------------------------------
    # ETAPA 1: BUREAU DE CRÉDITO (BRONZE CACHE & SILVER)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("📌 ETAPA 1: BUREAU RISK3 (ENTRADAS/cache vs SAIDAS/silver/fato_bureau_silver)")
    print("=" * 90)
    
    p_risk_cache = Path("ENTRADAS/bureau/cache/risk3_cache.json")
    dados_cache = {}
    if p_risk_cache.exists():
        with open(p_risk_cache, "r", encoding="utf-8") as f:
            dados_cache = json.load(f)

    p_bur_silver = Path("SAIDAS/silver/fato_bureau_silver/fato_bureau_silver.parquet")
    df_bur_silver = pd.read_parquet(p_bur_silver) if p_bur_silver.exists() else pd.DataFrame()
    if not df_bur_silver.empty and "CNPJ" in df_bur_silver.columns:
        df_bur_silver["CNPJ"] = df_bur_silver["CNPJ"].apply(normalizar_cnpj)

    for cnpj, nome in CNPJS_ALVO.items():
        print(f"\n--- [{nome}] (CNPJ: {cnpj}) ---")
        if cnpj in dados_cache:
            item = dados_cache[cnpj]
            print(f"  • ENTRADAS/risk3_cache: ENCONTRADO! Rating={item.get('RATING_BUREAU')}, Score={item.get('SCORE_BUREAU')}, Validade={item.get('DATA_VALIDADE')}, Status={item.get('STATUS')}")
        else:
            print(f"  • ENTRADAS/risk3_cache: ❌ NÃO CONSTA NO CACHE BRONZE")

        if not df_bur_silver.empty and cnpj in df_bur_silver["CNPJ"].values:
            row_s = df_bur_silver[df_bur_silver["CNPJ"] == cnpj].iloc[-1]
            print(f"  • Silver fato_bureau_silver: ENCONTRADO! Rating={row_s.get('RATING_BUREAU')}, Score={row_s.get('SCORE_BUREAU')}, Validade={row_s.get('DATA_VALIDADE')}")
        else:
            print(f"  • Silver fato_bureau_silver: ❌ NÃO ENCONTRADO NA SILVER")

    # --------------------------------------------------------------------------
    # ETAPA 2: SALESFORCE & PLANILHA DE CONTROLADORAS
    # --------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("📌 ETAPA 2: HERANÇA SOCIETÁRIA & SALESFORCE")
    print("=" * 90)

    p_ctrl_silver = Path("SAIDAS/silver/mapeamento_controladoras/mapeamento_controladoras.parquet")
    df_ctrl = pd.read_parquet(p_ctrl_silver) if p_ctrl_silver.exists() else pd.DataFrame()
    if not df_ctrl.empty and "CNPJ_SUBSIDIARIA" in df_ctrl.columns:
        df_ctrl["CNPJ_SUBSIDIARIA"] = df_ctrl["CNPJ_SUBSIDIARIA"].apply(normalizar_cnpj)
        df_ctrl["CNPJ_CONTA_ATRELADA"] = df_ctrl["CNPJ_CONTA_ATRELADA"].apply(normalizar_cnpj)

    p_sf_acc = Path("SAIDAS/silver/salesforce_silver/account/salesforce_account.parquet")
    df_acc = pd.read_parquet(p_sf_acc) if p_sf_acc.exists() else pd.DataFrame()
    if not df_acc.empty and "CNPJ" in df_acc.columns:
        df_acc["CNPJ"] = df_acc["CNPJ"].apply(normalizar_cnpj)

    p_sf_ch = Path("SAIDAS/silver/salesforce_silver/chamado/salesforce_chamado.parquet")
    df_ch = pd.read_parquet(p_sf_ch) if p_sf_ch.exists() else pd.DataFrame()
    if not df_ch.empty and "CNPJ" in df_ch.columns:
        df_ch["CNPJ"] = df_ch["CNPJ"].apply(normalizar_cnpj)

    for cnpj, nome in CNPJS_ALVO.items():
        print(f"\n--- [{nome}] (CNPJ: {cnpj}) ---")
        if not df_ctrl.empty and cnpj in df_ctrl["CNPJ_SUBSIDIARIA"].values:
            r_c = df_ctrl[df_ctrl["CNPJ_SUBSIDIARIA"] == cnpj].iloc[0]
            print(f"  • Planilha Controladoras: VINCULADO! Controladora CNPJ={r_c.get('CNPJ_CONTA_ATRELADA')}, Nome={r_c.get('CONTA_ATRELADA')}")
        else:
            print(f"  • Planilha Controladoras: ❌ Sem vínculo cadastrado como subsidiária")

        if not df_acc.empty and cnpj in df_acc["CNPJ"].values:
            r_a = df_acc[df_acc["CNPJ"] == cnpj].iloc[0]
            print(f"  • Salesforce Account: ENCONTRADO! Grupo={r_a.get('Grupo_economico__c')}, Rating={r_a.get('Risk3_Rating__c') or r_a.get('RatingCreditoMiddle__c')}")
        else:
            print(f"  • Salesforce Account: ❌ Não cadastrado no Salesforce Account")

        if not df_ch.empty and cnpj in df_ch["CNPJ"].values:
            r_ch = df_ch[df_ch["CNPJ"] == cnpj].iloc[-1]
            print(f"  • Salesforce Chamado: ENCONTRADO! Status={r_ch.get('Status_Analise_de_Credito__c')}, Rating={r_ch.get('Rating_final__c')}")
        else:
            print(f"  • Salesforce Chamado: ❌ Sem chamado de crédito cadastrado")

    # --------------------------------------------------------------------------
    # ETAPA 3: FICHAS EXCEL (EXTRAÍDAS vs REJEITADAS)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("📌 ETAPA 3: FICHAS EXCEL (EXTRAÍDAS vs REJEITADAS)")
    print("=" * 90)

    p_fichas_com = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.parquet")
    p_fichas_cons = Path("SAIDAS/silver/fichas_consumidores_extraidas/fichas_consumidores_extraidas.parquet")
    fichas_cnpjs = set()
    for pf in [p_fichas_com, p_fichas_cons]:
        if pf.exists():
            dff = pd.read_parquet(pf)
            if "CNPJ" in dff.columns:
                fichas_cnpjs.update(dff["CNPJ"].apply(normalizar_cnpj).unique())

    # Checar rejeitados
    p_rej = Path("ENTRADAS/rejeitados")
    arquivos_rej = list(p_rej.rglob("*.*")) if p_rej.exists() else []

    for cnpj, nome in CNPJS_ALVO.items():
        print(f"\n--- [{nome}] (CNPJ: {cnpj}) ---")
        if cnpj in fichas_cnpjs:
            print(f"  • Ficha Extraída (Silver): ✅ Ficha processada com sucesso!")
        else:
            print(f"  • Ficha Extraída (Silver): ❌ Nenhuma ficha processada para este CNPJ.")

        # Verificar se algum arquivo em rejeitados possui o CNPJ no nome
        matches_rej = [str(ar.name) for ar in arquivos_rej if cnpj in str(ar.name)]
        if matches_rej:
            print(f"  • Arquivos Rejeitados: ⚠️ ENCONTRADO EM REJEITADOS: {matches_rej}")
        else:
            print(f"  • Arquivos Rejeitados: Nenhum arquivo rejeitado com este CNPJ no nome.")

    # --------------------------------------------------------------------------
    # ETAPA 4: RELACIONAL (FATO_ANALISE_CREDITO & DIM_ESTABELECIMENTO)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("📌 ETAPA 4: RELACIONAL (fato_analise_credito & dim_estabelecimento)")
    print("=" * 90)

    p_fato = Path("SAIDAS/relational/facts/credito/fato_analise_credito.parquet")
    df_fato = pd.read_parquet(p_fato) if p_fato.exists() else pd.DataFrame()
    if not df_fato.empty and "CNPJ" in df_fato.columns:
        df_fato["CNPJ"] = df_fato["CNPJ"].apply(normalizar_cnpj)

    p_estab = Path("SAIDAS/relational/dimensions/estabelecimentos/dim_estabelecimento.parquet")
    df_estab = pd.read_parquet(p_estab) if p_estab.exists() else pd.DataFrame()
    if not df_estab.empty and "CNPJ" in df_estab.columns:
        df_estab["CNPJ"] = df_estab["CNPJ"].apply(normalizar_cnpj)

    for cnpj, nome in CNPJS_ALVO.items():
        print(f"\n--- [{nome}] (CNPJ: {cnpj}) ---")
        if not df_fato.empty and cnpj in df_fato["CNPJ"].values:
            r_fat = df_fato[df_fato["CNPJ"] == cnpj].iloc[-1]
            print(f"  • fato_analise_credito: ✅ PRESENTE! Rating={r_fat.get('RATING')}, PD={r_fat.get('PD_PERCENTUAL')}, DataAnalise={r_fat.get('DATA_ANALISE')}, Validade={r_fat.get('FIM_VIGENCIA_ANALISE')}, Tipo={r_fat.get('TIPO_ANALISE')}, Fonte={r_fat.get('FONTE_ANALISE')}")
        else:
            print(f"  • fato_analise_credito: ❌ AUSENTE NA FATO!")

        if not df_estab.empty and cnpj in df_estab["CNPJ"].values:
            r_est = df_estab[df_estab["CNPJ"] == cnpj].iloc[0]
            print(f"  • dim_estabelecimento: ✅ PRESENTE! OrigemHeranca={r_est.get('ORIGEM_HERANCA_RISCO')}, Doador={r_est.get('CNPJ_DOADOR_RISCO')}")
        else:
            print(f"  • dim_estabelecimento: ❌ AUSENTE NA DIMENSÃO ESTABELECIMENTO!")

    # --------------------------------------------------------------------------
    # ETAPA 5: GOLD (Visao_Carteira_Contratos)
    # --------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("📌 ETAPA 5: GOLD (Visao_Carteira_Contratos)")
    print("=" * 90)

    p_gold = Path("SAIDAS/gold/visao_operacional_negocio/Visao_Carteira_Contratos.parquet")
    df_gold = pd.read_parquet(p_gold) if p_gold.exists() else pd.DataFrame()
    if not df_gold.empty and "CONTRAPARTE_CNPJ" in df_gold.columns:
        df_gold["CONTRAPARTE_CNPJ"] = df_gold["CONTRAPARTE_CNPJ"].apply(normalizar_cnpj)

    for cnpj, nome in CNPJS_ALVO.items():
        print(f"\n--- [{nome}] (CNPJ: {cnpj}) ---")
        if not df_gold.empty and cnpj in df_gold["CONTRAPARTE_CNPJ"].values:
            sub_g = df_gold[df_gold["CONTRAPARTE_CNPJ"] == cnpj]
            print(f"  • Total Contratos na Gold: {len(sub_g)}, MtM Total: R$ {sub_g['MTM_TOTAL_R$'].sum():,.2f}")
            amostra = sub_g.iloc[0]
            print(f"  • Rating Gold: '{amostra.get('RATING')}' | StatusVigencia: '{amostra.get('STATUS_VIGENCIA_ANALISE')}'")
            print(f"  • FonteAnalise: '{amostra.get('FONTE_ANALISE')}' | Doador: '{amostra.get('CNPJ_DOADOR_RISCO')}'")
            print(f"  • DataAnalise: '{amostra.get('DATA_ANALISE')}' | FimVigencia: '{amostra.get('FIM_VIGENCIA_ANALISE')}'")
            print(f"  • NomeGrupo: '{amostra.get('NOME_GRUPO')}'")
        else:
            print(f"  • Visao_Carteira_Contratos: ❌ Não possui contratos ativos na Gold")

    print("\n" + "=" * 90)
    print("🏁 RASTREAMENTO CONCLUÍDO COM SUCESSO")
    print("=" * 90)

if __name__ == "__main__":
    main()
