"""Script de validação de impacto: Fato Alertas Atual (via Gold) vs Refatorada (via Relational)."""
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.bootstrap import carregar_contexto
from relational.facts.fato_alerta_util import COLUNAS_FATO_ALERTA

def gerar_alertas_logica_legada(context):
    """Executa a lógica legada baseada em Visao_Operacional_BDC_LATEST.parquet."""
    path_gold = context.path("saidas") / "gold" / "visao_operacional_negocio" / "Visao_Operacional_BDC_LATEST.parquet"
    if not path_gold.exists():
        print(f"❌ Gold LATEST não encontrada em {path_gold}")
        return []

    df_gold = pd.read_parquet(path_gold)
    
    path_rfb = context.path("silver") / "receita" / "dados_cadastrais_rfb.parquet"
    if not path_rfb.exists():
        path_rfb = context.path("silver") / "receita_silver" / "receita_cadastral_silver.parquet"
    df_rfb = pd.read_parquet(path_rfb) if path_rfb.exists() else pd.DataFrame()
    
    path_mtm = context.path("relational_facts") / "reconciliacao" / "fato_reconciliacao_contrato_mtm.parquet"
    df_mtm = pd.read_parquet(path_mtm) if path_mtm.exists() else pd.DataFrame()
    
    path_gar = context.path("relational_facts") / "credito" / "fato_garantia.parquet"
    df_gar = pd.read_parquet(path_gar) if path_gar.exists() else pd.DataFrame()
    
    path_man = context.path("silver") / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"
    df_man = pd.read_parquet(path_man) if path_man.exists() else pd.DataFrame()
    
    alertas = []
    agora = datetime(2026, 9, 24, 12, 0, 0)

    # MAN_003
    if not df_man.empty and "_STATUS_REGISTRO" in df_man.columns:
        df_man_vigentes = df_man[df_man["_STATUS_REGISTRO"] == "VIGENTE"]
        for _, row_man in df_man_vigentes.iterrows():
            cnpj_man = row_man.get("CNPJ")
            campo = str(row_man.get("CAMPO_AFETADO", "")).upper()
            try:
                v_ant = float(row_man.get("VALOR_ANTERIOR")) if row_man.get("VALOR_ANTERIOR") is not None else 0.0
                v_nov = float(row_man.get("VALOR_NOVO")) if row_man.get("VALOR_NOVO") is not None else 0.0
                diff = abs(v_nov - v_ant)
                alerta_disparado = False
                if campo in ["PD", "TAXA_RISCO", "PD_FINAL"]:
                    if diff > 0.0001: alerta_disparado = True
                elif "SCORE" in campo or "NOTA" in campo:
                    if diff > 0.01: alerta_disparado = True
                else: 
                    if diff > 100.0 and (v_ant != 0 and diff / abs(v_ant) > 0.001): alerta_disparado = True
                if alerta_disparado:
                    alertas.append({
                        "CNPJ": cnpj_man, "CODIGO_ALERTA": "MAN_003", "SEVERIDADE": "MEDIO",
                        "REGRA": "Sobrescrita Manual Excede Tolerância",
                        "MENSAGEM_DESCRITIVA": f"Carga manual no campo {campo} excedeu tolerância da régua (diff: {diff:.4f}).",
                        "DATA_DETECCAO": agora, "CAMPO_AFETADO": campo,
                        "VALOR_OBSERVADO": f"{v_ant} -> {v_nov}", "LIMITE_ESPERADO": "Tolerância Aprovada"
                    })
            except Exception:
                pass

    rfb_situacao = {}
    if not df_rfb.empty and "CNPJ" in df_rfb.columns:
        rfb_situacao = df_rfb.drop_duplicates("CNPJ", keep="last").set_index("CNPJ")["SITUACAO_CADASTRAL"].to_dict()

    mtm_dados = {}
    if not df_mtm.empty and "CNPJ" in df_mtm.columns:
        mtm_dados = df_mtm.drop_duplicates("CNPJ", keep="last").set_index("CNPJ").to_dict(orient="index")

    gar_vencidas_por_cnpj = set()
    if not df_gar.empty and "CNPJ" in df_gar.columns and "STATUS_GARANTIA" in df_gar.columns:
        gar_vencidas_por_cnpj = set(df_gar.loc[df_gar["STATUS_GARANTIA"] == "VENCIDA", "CNPJ"].dropna().unique())

    for _, row in df_gold.iterrows():
        cnpj = row.get("CNPJ")
        if pd.isna(cnpj) or not str(cnpj).strip(): continue
            
        status_contratual = str(row.get("STATUS_CONTRATUAL", ""))
        sit_analise = str(row.get("SITUACAO_ANALISE", ""))
        metodologia = str(row.get("METODOLOGIA_EXIGIDA", ""))
        vol_mwm = pd.to_numeric(row.get("VOLUME_MWM"), errors="coerce")
        if pd.isna(vol_mwm): vol_mwm = 0.0
        status_calculo_pd = str(row.get("STATUS_CALCULO_PD", ""))
        rating_final = str(row.get("RATING_FINAL", ""))

        if status_calculo_pd == "PENDENTE":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "EXC_001", "SEVERIDADE": "ALTO", "REGRA": "Cálculo de PD Suspenso", "MENSAGEM_DESCRITIVA": "Motor suspendeu cálculo por falta de insumos.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_CALCULO_PD", "VALOR_OBSERVADO": status_calculo_pd, "LIMITE_ESPERADO": "CONCLUIDO"})

        if sit_analise == "PENDENTE_DOC":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "DOC_001", "SEVERIDADE": "MEDIO", "REGRA": "Documentação Faltante", "MENSAGEM_DESCRITIVA": "A análise está suspensa por falta de documentação.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_ANALISE", "VALOR_OBSERVADO": sit_analise, "LIMITE_ESPERADO": "VIGENTE"})

        if status_contratual == "CONTRATO_VIGENTE" and sit_analise == "VENCIDA":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "ANA_001", "SEVERIDADE": "ALTO", "REGRA": "Análise Vencida com Contrato Vigente", "MENSAGEM_DESCRITIVA": "Contraparte com contrato ativo e análise expirada.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_ANALISE", "VALOR_OBSERVADO": sit_analise, "LIMITE_ESPERADO": "VIGENTE"})
            
        if status_contratual == "CONTRATO_VIGENTE" and metodologia == "DF_DETALHADA" and sit_analise != "VIGENTE":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "VOL_001", "SEVERIDADE": "CRITICO", "REGRA": ">= 5MWm sem DF Vigente", "MENSAGEM_DESCRITIVA": "Volume exige DF (>= 5 MWm), mas análise não vigente.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "METODOLOGIA_EXIGIDA", "VALOR_OBSERVADO": f"Volume: {vol_mwm:.2f}", "LIMITE_ESPERADO": "DF Vigente"})
            
        if metodologia == "DF_DETALHADA" and pd.isna(row.get("DATA_DEMONSTRACAO_FINANCEIRA")):
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "DF_001", "SEVERIDADE": "CRITICO", "REGRA": "DF Ausente", "MENSAGEM_DESCRITIVA": "Balanço contábil não recebido para segmento elegível.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "DATA_DEMONSTRACAO_FINANCEIRA", "VALOR_OBSERVADO": "Nulo", "LIMITE_ESPERADO": "Data Preenchida"})

        if status_calculo_pd == "CONCLUIDO_COM_PD_SUB":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "RAT_001", "SEVERIDADE": "ALTO", "REGRA": "Uso de PD Substituta (Dados Antigos)", "MENSAGEM_DESCRITIVA": "O Rating foi penalizado pelo acionamento de PD Substituta (DF Vencida).", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_CALCULO_PD", "VALOR_OBSERVADO": "CONCLUIDO_COM_PD_SUB", "LIMITE_ESPERADO": "CONCLUIDO"})
            
        if rating_final == "E":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "RAT_002", "SEVERIDADE": "ALTO", "REGRA": "Rating Deteriorado (E)", "MENSAGEM_DESCRITIVA": "Contraparte atingiu rating E (Alerta de Default ou Rejeição).", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "RATING_FINAL", "VALOR_OBSERVADO": rating_final, "LIMITE_ESPERADO": "A, B, C, D"})

        sit_cad = str(rfb_situacao.get(cnpj, "")).upper()
        if sit_cad and sit_cad not in ("ATIVA", "ATIVO"):
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "CAD_001", "SEVERIDADE": "CRITICO", "REGRA": "Situação Cadastral Irregular", "MENSAGEM_DESCRITIVA": "Situação na Receita Federal não é ATIVA.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_CADASTRAL", "VALOR_OBSERVADO": sit_cad, "LIMITE_ESPERADO": "ATIVA"})
                    
        mtm_info = mtm_dados.get(cnpj)
        if mtm_info:
            try:
                perc_uso = float(mtm_info.get("PERCENTUAL_USO_LIMITE", 0.0))
                if perc_uso > 100.0:
                    alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "EXP_001", "SEVERIDADE": "CRITICO", "REGRA": "Estouro de Limite (MtM)", "MENSAGEM_DESCRITIVA": "Uso de limite ultrapassou 100% da exposição aprovada.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "PERCENTUAL_USO_LIMITE", "VALOR_OBSERVADO": f"{perc_uso}%", "LIMITE_ESPERADO": "<= 100%"})
            except Exception:
                pass

            status_rec = str(mtm_info.get("STATUS_RECONCILIACAO", "")).upper()
            if status_rec == "DIVERGENTE":
                alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "CTR_001", "SEVERIDADE": "MEDIO", "REGRA": "Divergência Contratual", "MENSAGEM_DESCRITIVA": "O contrato Denodo diverge da carga MtM.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_RECONCILIACAO", "VALOR_OBSERVADO": status_rec, "LIMITE_ESPERADO": "CONVERGENTE"})

        if cnpj in gar_vencidas_por_cnpj:
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "GAR_001", "SEVERIDADE": "MEDIO", "REGRA": "Garantia Vencida", "MENSAGEM_DESCRITIVA": "Existe garantia atrelada ao CNPJ que está vencida.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_GARANTIA", "VALOR_OBSERVADO": "VENCIDA", "LIMITE_ESPERADO": "VIGENTE"})

        tipo_com = str(row.get("TIPO_COMERCIALIZADORA", ""))
        if tipo_com == "CGRUPO" and pd.isna(row.get("HOLDING_CNPJ")):
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "GRP_001", "SEVERIDADE": "MEDIO", "REGRA": "CGRUPO sem Holding", "MENSAGEM_DESCRITIVA": "Classificado como CGRUPO mas sem holding declarada.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "HOLDING_CNPJ", "VALOR_OBSERVADO": "Nulo", "LIMITE_ESPERADO": "CNPJ Válido"})

    return alertas


def gerar_alertas_logica_refatorada(context):
    """Executa a lógica refatorada baseada exclusivamente na Camada Relacional e Silver."""
    from common.identificadores import normalizar_cnpj_coluna
    agora = datetime(2026, 9, 24, 12, 0, 0)
    hoje = agora

    # 1. Dimensão Contraparte (Single Source of Truth de Cadastro)
    path_dim = context.path("relational_dimensions") / "contrapartes" / "dim_contraparte.parquet"
    if not path_dim.exists():
        path_dim = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"
    df_dim = pd.read_parquet(path_dim) if path_dim.exists() else pd.DataFrame()
    if not df_dim.empty and "CNPJ" in df_dim.columns:
        df_dim["CNPJ"] = df_dim["CNPJ"].apply(normalizar_cnpj_coluna)

    # 2. Fato Análise de Crédito (Single Source of Truth de Risco/PD)
    path_anl = context.path("relational_facts") / "credito" / "fato_analise_credito.parquet"
    df_anl = pd.read_parquet(path_anl) if path_anl.exists() else pd.DataFrame()
    if not df_anl.empty and "CNPJ" in df_anl.columns:
        df_anl["CNPJ"] = df_anl["CNPJ"].apply(normalizar_cnpj_coluna)
        if "_STATUS_REGISTRO" in df_anl.columns:
            df_anl = df_anl[df_anl["_STATUS_REGISTRO"] == "VIGENTE"]
        else:
            df_anl = df_anl.drop_duplicates(subset=["CNPJ"], keep="last")

    # 3. Contratos Silver (Denodo) - Construção local do status contratual e volume
    path_ctr = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_ctr.exists():
        path_ctr = context.path("silver") / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
    df_ctr = pd.read_parquet(path_ctr) if path_ctr.exists() else pd.DataFrame()

    contratos_info = {}
    if not df_ctr.empty and "CNPJ" in df_ctr.columns:
        df_ctr["CNPJ"] = df_ctr["CNPJ"].apply(normalizar_cnpj_coluna)
        col_vol = "VOLUME_CONTRATADO_MENSAL_MWM" if "VOLUME_CONTRATADO_MENSAL_MWM" in df_ctr.columns else "VOLUME_MWM"
        df_ctr["_VOL"] = pd.to_numeric(df_ctr.get(col_vol), errors="coerce").fillna(0.0) if col_vol in df_ctr.columns else 0.0

        col_in = "SUPRIMENTO_INICIO" if "SUPRIMENTO_INICIO" in df_ctr.columns else ("VIGENCIA_INICIO" if "VIGENCIA_INICIO" in df_ctr.columns else "inicio_suprimento")
        col_out = "SUPRIMENTO_TERMINO" if "SUPRIMENTO_TERMINO" in df_ctr.columns else ("VIGENCIA_FIM" if "VIGENCIA_FIM" in df_ctr.columns else "fim_suprimento")
        df_ctr["_DT_IN"] = pd.to_datetime(df_ctr.get(col_in), errors="coerce")
        df_ctr["_DT_OUT"] = pd.to_datetime(df_ctr.get(col_out), errors="coerce")

        df_ctr["_EH_VIGENTE"] = (
            (df_ctr.get("STATUS", df_ctr.get("id_status", "")).astype(str).str.upper().str.contains("ATIVO|EM SUPRIMENTO|2"))
            & (df_ctr["_DT_IN"] <= hoje)
            & (df_ctr["_DT_OUT"] >= hoje)
        )
        df_ctr["_EH_FUTURO"] = df_ctr["_DT_IN"] > hoje

        for cnpj, grp in df_ctr.groupby("CNPJ"):
            tem_vig = grp["_EH_VIGENTE"].any()
            tem_fut = grp["_EH_FUTURO"].any()
            status_ctr = "CONTRATO_VIGENTE" if tem_vig else ("CONTRATO_FUTURO" if tem_fut else "SEM_CONTRATO")
            vol_max = grp["_VOL"].max()
            contratos_info[cnpj] = {"STATUS_CONTRATUAL": status_ctr, "VOLUME_MWM": vol_max}

    # 4. Outras fontes Silver/Relational
    path_rfb = context.path("silver") / "receita" / "dados_cadastrais_rfb.parquet"
    if not path_rfb.exists():
        path_rfb = context.path("silver") / "receita_silver" / "receita_cadastral_silver.parquet"
    df_rfb = pd.read_parquet(path_rfb) if path_rfb.exists() else pd.DataFrame()
    
    path_mtm = context.path("relational_facts") / "reconciliacao" / "fato_reconciliacao_contrato_mtm.parquet"
    df_mtm = pd.read_parquet(path_mtm) if path_mtm.exists() else pd.DataFrame()
    
    path_gar = context.path("relational_facts") / "credito" / "fato_garantia.parquet"
    df_gar = pd.read_parquet(path_gar) if path_gar.exists() else pd.DataFrame()
    
    path_man = context.path("silver") / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"
    df_man = pd.read_parquet(path_man) if path_man.exists() else pd.DataFrame()

    alertas = []

    # MAN_003
    if not df_man.empty and "_STATUS_REGISTRO" in df_man.columns:
        df_man_vigentes = df_man[df_man["_STATUS_REGISTRO"] == "VIGENTE"]
        for _, row_man in df_man_vigentes.iterrows():
            cnpj_man = row_man.get("CNPJ")
            campo = str(row_man.get("CAMPO_AFETADO", "")).upper()
            try:
                v_ant = float(row_man.get("VALOR_ANTERIOR")) if row_man.get("VALOR_ANTERIOR") is not None else 0.0
                v_nov = float(row_man.get("VALOR_NOVO")) if row_man.get("VALOR_NOVO") is not None else 0.0
                diff = abs(v_nov - v_ant)
                alerta_disparado = False
                if campo in ["PD", "TAXA_RISCO", "PD_FINAL"]:
                    if diff > 0.0001: alerta_disparado = True
                elif "SCORE" in campo or "NOTA" in campo:
                    if diff > 0.01: alerta_disparado = True
                else: 
                    if diff > 100.0 and (v_ant != 0 and diff / abs(v_ant) > 0.001): alerta_disparado = True
                if alerta_disparado:
                    alertas.append({
                        "CNPJ": cnpj_man, "CODIGO_ALERTA": "MAN_003", "SEVERIDADE": "MEDIO",
                        "REGRA": "Sobrescrita Manual Excede Tolerância",
                        "MENSAGEM_DESCRITIVA": f"Carga manual no campo {campo} excedeu tolerância da régua (diff: {diff:.4f}).",
                        "DATA_DETECCAO": agora, "CAMPO_AFETADO": campo,
                        "VALOR_OBSERVADO": f"{v_ant} -> {v_nov}", "LIMITE_ESPERADO": "Tolerância Aprovada"
                    })
            except Exception:
                pass

    rfb_situacao = {}
    if not df_rfb.empty and "CNPJ" in df_rfb.columns:
        rfb_situacao = df_rfb.drop_duplicates("CNPJ", keep="last").set_index("CNPJ")["SITUACAO_CADASTRAL"].to_dict()

    mtm_dados = {}
    if not df_mtm.empty and "CNPJ" in df_mtm.columns:
        mtm_dados = df_mtm.drop_duplicates("CNPJ", keep="last").set_index("CNPJ").to_dict(orient="index")

    gar_vencidas_por_cnpj = set()
    if not df_gar.empty and "CNPJ" in df_gar.columns and "STATUS_GARANTIA" in df_gar.columns:
        gar_vencidas_por_cnpj = set(df_gar.loc[df_gar["STATUS_GARANTIA"] == "VENCIDA", "CNPJ"].dropna().unique())

    # Universo de CNPJs: união de dim_contraparte, fato_analise_credito e contratos
    cnpjs_todos = set()
    if not df_dim.empty: cnpjs_todos.update(df_dim["CNPJ"].dropna().unique())
    if not df_anl.empty: cnpjs_todos.update(df_anl["CNPJ"].dropna().unique())
    cnpjs_todos.update(contratos_info.keys())

    dim_dict = df_dim.set_index("CNPJ").to_dict(orient="index") if not df_dim.empty else {}
    anl_dict = df_anl.set_index("CNPJ").to_dict(orient="index") if not df_anl.empty else {}

    for cnpj in sorted(cnpjs_todos):
        c_dim = dim_dict.get(cnpj, {})
        c_anl = anl_dict.get(cnpj, {})
        c_ctr = contratos_info.get(cnpj, {"STATUS_CONTRATUAL": "SEM_CONTRATO", "VOLUME_MWM": 0.0})

        status_contratual = c_ctr.get("STATUS_CONTRATUAL", "SEM_CONTRATO")
        vol_mwm = float(c_ctr.get("VOLUME_MWM", 0.0))

        sit_analise = str(c_anl.get("SITUACAO_ANALISE", ""))
        status_calculo_pd = str(c_anl.get("STATUS_CALCULO_PD", ""))
        rating_final = str(c_anl.get("RATING", ""))
        data_df = c_anl.get("DATA_BALANCO_USADO")

        seg_metodologico = str(c_dim.get("SEGMENTO_METODOLOGICO", c_anl.get("SEGMENTO_METODOLOGICO_FICHA", ""))).upper()
        
        # Classificação da Exigência
        if "COMERCIALIZADORA" in seg_metodologico or seg_metodologico in ["CPURA", "CGRUPO"]:
            metodologia = "DF_DETALHADA"
        elif vol_mwm >= 5.0:
            metodologia = "DF_DETALHADA"
        elif vol_mwm > 0.0:
            metodologia = "BUREAU"
        else:
            metodologia = "DISPENSADA"

        if status_calculo_pd == "PENDENTE":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "EXC_001", "SEVERIDADE": "ALTO", "REGRA": "Cálculo de PD Suspenso", "MENSAGEM_DESCRITIVA": "Motor suspendeu cálculo por falta de insumos.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_CALCULO_PD", "VALOR_OBSERVADO": status_calculo_pd, "LIMITE_ESPERADO": "CONCLUIDO"})

        if sit_analise == "PENDENTE_DOC":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "DOC_001", "SEVERIDADE": "MEDIO", "REGRA": "Documentação Faltante", "MENSAGEM_DESCRITIVA": "A análise está suspensa por falta de documentação.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_ANALISE", "VALOR_OBSERVADO": sit_analise, "LIMITE_ESPERADO": "VIGENTE"})

        if status_contratual == "CONTRATO_VIGENTE" and sit_analise == "VENCIDA":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "ANA_001", "SEVERIDADE": "ALTO", "REGRA": "Análise Vencida com Contrato Vigente", "MENSAGEM_DESCRITIVA": "Contraparte com contrato ativo e análise expirada.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_ANALISE", "VALOR_OBSERVADO": sit_analise, "LIMITE_ESPERADO": "VIGENTE"})
            
        if status_contratual == "CONTRATO_VIGENTE" and metodologia == "DF_DETALHADA" and sit_analise != "VIGENTE":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "VOL_001", "SEVERIDADE": "CRITICO", "REGRA": ">= 5MWm sem DF Vigente", "MENSAGEM_DESCRITIVA": "Volume exige DF (>= 5 MWm), mas análise não vigente.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "METODOLOGIA_EXIGIDA", "VALOR_OBSERVADO": f"Volume: {vol_mwm:.2f}", "LIMITE_ESPERADO": "DF Vigente"})
            
        if metodologia == "DF_DETALHADA" and (pd.isna(data_df) or str(data_df).strip() in ("", "None", "nan", "NaT")):
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "DF_001", "SEVERIDADE": "CRITICO", "REGRA": "DF Ausente", "MENSAGEM_DESCRITIVA": "Balanço contábil não recebido para segmento elegível.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "DATA_DEMONSTRACAO_FINANCEIRA", "VALOR_OBSERVADO": "Nulo", "LIMITE_ESPERADO": "Data Preenchida"})

        if status_calculo_pd == "CONCLUIDO_COM_PD_SUB":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "RAT_001", "SEVERIDADE": "ALTO", "REGRA": "Uso de PD Substituta (Dados Antigos)", "MENSAGEM_DESCRITIVA": "O Rating foi penalizado pelo acionamento de PD Substituta (DF Vencida).", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_CALCULO_PD", "VALOR_OBSERVADO": "CONCLUIDO_COM_PD_SUB", "LIMITE_ESPERADO": "CONCLUIDO"})
            
        if rating_final == "E":
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "RAT_002", "SEVERIDADE": "ALTO", "REGRA": "Rating Deteriorado (E)", "MENSAGEM_DESCRITIVA": "Contraparte atingiu rating E (Alerta de Default ou Rejeição).", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "RATING_FINAL", "VALOR_OBSERVADO": rating_final, "LIMITE_ESPERADO": "A, B, C, D"})

        sit_cad = str(rfb_situacao.get(cnpj, c_dim.get("SITUACAO_CADASTRAL", ""))).upper()
        if sit_cad and sit_cad not in ("ATIVA", "ATIVO", "NAO_INFORMADO"):
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "CAD_001", "SEVERIDADE": "CRITICO", "REGRA": "Situação Cadastral Irregular", "MENSAGEM_DESCRITIVA": "Situação na Receita Federal não é ATIVA.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "SITUACAO_CADASTRAL", "VALOR_OBSERVADO": sit_cad, "LIMITE_ESPERADO": "ATIVA"})
                    
        mtm_info = mtm_dados.get(cnpj)
        if mtm_info:
            try:
                perc_uso = float(mtm_info.get("PERCENTUAL_USO_LIMITE", 0.0))
                if perc_uso > 100.0:
                    alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "EXP_001", "SEVERIDADE": "CRITICO", "REGRA": "Estouro de Limite (MtM)", "MENSAGEM_DESCRITIVA": "Uso de limite ultrapassou 100% da exposição aprovada.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "PERCENTUAL_USO_LIMITE", "VALOR_OBSERVADO": f"{perc_uso}%", "LIMITE_ESPERADO": "<= 100%"})
            except Exception:
                pass

            status_rec = str(mtm_info.get("STATUS_RECONCILIACAO", "")).upper()
            if status_rec == "DIVERGENTE":
                alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "CTR_001", "SEVERIDADE": "MEDIO", "REGRA": "Divergência Contratual", "MENSAGEM_DESCRITIVA": "O contrato Denodo diverge da carga MtM.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_RECONCILIACAO", "VALOR_OBSERVADO": status_rec, "LIMITE_ESPERADO": "CONVERGENTE"})

        if cnpj in gar_vencidas_por_cnpj:
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "GAR_001", "SEVERIDADE": "MEDIO", "REGRA": "Garantia Vencida", "MENSAGEM_DESCRITIVA": "Existe garantia atrelada ao CNPJ que está vencida.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "STATUS_GARANTIA", "VALOR_OBSERVADO": "VENCIDA", "LIMITE_ESPERADO": "VIGENTE"})

        holding_cnpj = c_dim.get("CNPJ_CONTROLADORA")
        if seg_metodologico == "CGRUPO" and (pd.isna(holding_cnpj) or not str(holding_cnpj).strip()):
            alertas.append({"CNPJ": cnpj, "CODIGO_ALERTA": "GRP_001", "SEVERIDADE": "MEDIO", "REGRA": "CGRUPO sem Holding", "MENSAGEM_DESCRITIVA": "Classificado como CGRUPO mas sem holding declarada.", "DATA_DETECCAO": agora, "CAMPO_AFETADO": "HOLDING_CNPJ", "VALOR_OBSERVADO": "Nulo", "LIMITE_ESPERADO": "CNPJ Válido"})

    return alertas


def main():
    print("=" * 70)
    print("VALIDAÇÃO DE IMPACTO: FATO_ALERTAS ATUAL VS REFATORADA")
    print("=" * 70)

    context = carregar_contexto(ROOT / "ENTRADAS" / "configs")

    print("\n[1] Executando lógica atual (via Camada Gold)...")
    alertas_leg = gerar_alertas_logica_legada(context)
    df_leg = pd.DataFrame(alertas_leg)
    print(f"-> Total alertas gerados pela lógica legada: {len(df_leg)}")

    print("\n[2] Executando lógica refatorada (via Camadas Relacional + Silver)...")
    alertas_ref = gerar_alertas_logica_refatorada(context)
    df_ref = pd.DataFrame(alertas_ref)
    print(f"-> Total alertas gerados pela lógica refatorada: {len(df_ref)}")

    print("\n[3] Comparação por Código de Alerta:")
    cont_leg = df_leg["CODIGO_ALERTA"].value_counts().to_dict() if not df_leg.empty else {}
    cont_ref = df_ref["CODIGO_ALERTA"].value_counts().to_dict() if not df_ref.empty else {}
    todos_codigos = sorted(set(cont_leg.keys()) | set(cont_ref.keys()))

    print(f"{'Código':<12} | {'Legado (Gold)':<15} | {'Refatorado (Rel)':<18} | {'Diff':<8}")
    print("-" * 60)
    for cod in todos_codigos:
        q_leg = cont_leg.get(cod, 0)
        q_ref = cont_ref.get(cod, 0)
        diff = q_ref - q_leg
        status_diff = "OK" if diff == 0 else f"{diff:+d}"
        print(f"{cod:<12} | {q_leg:<15} | {q_ref:<18} | {status_diff:<8}")

    print("\n[4] Comparação de Schema:")
    print(f"Colunas padrão Fato Alerta: {COLUNAS_FATO_ALERTA}")
    
    # Validação de pares (CNPJ, CODIGO_ALERTA)
    if not df_leg.empty and not df_ref.empty:
        pares_leg = set(zip(df_leg["CNPJ"], df_leg["CODIGO_ALERTA"]))
        pares_ref = set(zip(df_ref["CNPJ"], df_ref["CODIGO_ALERTA"]))
        
        apenas_leg = pares_leg - pares_ref
        apenas_ref = pares_ref - pares_leg
        
        print(f"\nPares (CNPJ, Alerta) em comum: {len(pares_leg & pares_ref)}")
        if apenas_leg:
            print(f"⚠️ Presentes apenas no legado: {len(apenas_leg)} (Exemplos: {list(apenas_leg)[:3]})")
        if apenas_ref:
            print(f"ℹ️ Presentes apenas no refatorado: {len(apenas_ref)} (Exemplos: {list(apenas_ref)[:3]})")
        if not apenas_leg and not apenas_ref:
            print("✅ 100% DE PARIDADE: Nenhuma discrepância entre Legado e Refatorado!")

    print("\n" + "=" * 70)
    print("FIM DO TESTE DE IMPACTO")
    print("=" * 70)

if __name__ == "__main__":
    main()
