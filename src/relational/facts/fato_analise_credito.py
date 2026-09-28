"""Construção da tabela Fato de Análise de Crédito e Execução do Motor de Risco."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from storage.escrever_dados import escrever_conjunto_de_dados_silver
from common.json import ler_json
from pathlib import Path
from control.logger import obter_logger
from domain.contrapartes.segmentacao import definir_segmento_metodologico
from domain.credito.pd_motor import calcular_pd_ajustada
from domain.credito.pd_exceptions import PdInputValidationError, PdCalculationError

def processar_fato_analise_credito(context: AppContext) -> dict[str, Any]:
    """Orquestra a leitura de dependências e construção da Fato de Análise de Crédito."""
    from common.dados import carregar_fichas_silver_consolidadas
    from common.identificadores import normalizar_cnpj_coluna
    df_fichas = carregar_fichas_silver_consolidadas(context.path("silver"))
    if not df_fichas.empty and "CNPJ" in df_fichas.columns:
        df_fichas["CNPJ"] = df_fichas["CNPJ"].apply(normalizar_cnpj_coluna)
        
    dim_path = context.path("relational_dimensions") / "dim_contraparte.parquet"
    if not dim_path.exists():
        dim_path = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"
    df_dim = pd.read_parquet(dim_path) if dim_path.exists() else pd.DataFrame()
    if not df_dim.empty and "CNPJ" in df_dim.columns:
        df_dim["CNPJ"] = df_dim["CNPJ"].apply(normalizar_cnpj_coluna)
        if not df_fichas.empty and "VOLUME_ENQUADRAMENTO_MWM" not in df_fichas.columns and "VOLUME_ENQUADRAMENTO_MWM" in df_dim.columns:
            df_fichas = pd.merge(df_fichas, df_dim[["CNPJ", "VOLUME_ENQUADRAMENTO_MWM"]].drop_duplicates("CNPJ"), on="CNPJ", how="left")
    
    bureau_path = context.path("silver") / "fato_bureau_silver" / "fato_bureau_silver.parquet"
    if bureau_path.exists():
        df_bureau = pd.read_parquet(bureau_path)
        if not df_bureau.empty:
            df_bureau["CNPJ"] = df_bureau["CNPJ"].apply(normalizar_cnpj_coluna)
            if "DATA_CONSULTA" in df_bureau.columns and "DATA_BUREAU" not in df_bureau.columns:
                df_bureau["DATA_BUREAU"] = df_bureau["DATA_CONSULTA"]
            if "SCORE_BUREAU" in df_bureau.columns:
                df_bureau["SCORE_BUREAU"] = pd.to_numeric(df_bureau["SCORE_BUREAU"], errors="coerce")
            if "RESTRITIVOS" in df_bureau.columns:
                df_bureau["RESTRITIVOS"] = pd.to_numeric(df_bureau["RESTRITIVOS"], errors="coerce")
            if "PD_BUREAU" in df_bureau.columns:
                df_bureau["PD_BUREAU"] = pd.to_numeric(df_bureau["PD_BUREAU"], errors="coerce")
            col_data_bureau = "DATA_CONSULTA" if "DATA_CONSULTA" in df_bureau.columns else "CNPJ"
            df_bureau = df_bureau.sort_values(col_data_bureau).drop_duplicates(subset=["CNPJ"], keep="last")
            
            cols_bureau_uteis = ["CNPJ", "SCORE_BUREAU", "RESTRITIVOS", "DATA_BUREAU", "PD_BUREAU", "RATING_BUREAU"]
            df_bureau_sub = df_bureau[[c for c in cols_bureau_uteis if c in df_bureau.columns]].copy()
            
            if df_fichas.empty:
                df_fichas = df_bureau_sub.copy()
                df_fichas["TIPO_FICHA"] = "CONSUMIDOR"
                df_fichas["VOLUME_ENQUADRAMENTO_MWM"] = 1.0
                df_fichas["DATA_ANALISE"] = df_fichas.get("DATA_BUREAU", pd.NaT)
            else:
                cnpjs_bureau = set(df_bureau_sub["CNPJ"].dropna().unique())
                cnpjs_fichas = set(df_fichas["CNPJ"].dropna().unique())
                
                # Cruzamento: priorizar colunas reais da Risk3 para o segmento de Bureau
                df_fichas = pd.merge(df_fichas, df_bureau_sub, on="CNPJ", how="left", suffixes=("", "_BUR"))
                vol_enq = pd.to_numeric(df_fichas["VOLUME_ENQUADRAMENTO_MWM"], errors="coerce").fillna(0.0) if "VOLUME_ENQUADRAMENTO_MWM" in df_fichas.columns else pd.Series(0.0, index=df_fichas.index)
                tipo_ficha_ser = df_fichas["TIPO_FICHA"] if "TIPO_FICHA" in df_fichas.columns else pd.Series("", index=df_fichas.index)
                is_bureau_seg = (tipo_ficha_ser == "CONSUMIDOR") & (vol_enq < 5.0)

                # SEGREGAÇÃO ESTRITA:
                # 1. SCORE_BUREAU e RESTRITIVOS: Sempre provenientes da API RISK3 para QUALQUER contraparte com consulta
                # 2. RATING_BUREAU, PD_BUREAU e DATA_BUREAU: Associados EXCLUSIVAMENTE ao segmento de Bureau (CONSUMIDOR <= 5MWm)
                for col in ["SCORE_BUREAU", "RESTRITIVOS", "DATA_BUREAU", "PD_BUREAU", "RATING_BUREAU"]:
                    col_bur = f"{col}_BUR"
                    if col_bur in df_fichas.columns:
                        if col not in df_fichas.columns:
                            df_fichas[col] = pd.NA
                        if col in ["SCORE_BUREAU", "RESTRITIVOS"]:
                            df_fichas[col] = df_fichas[col_bur]
                        else:
                            df_fichas.loc[is_bureau_seg, col] = df_fichas.loc[is_bureau_seg, col_bur]
                            df_fichas.loc[~is_bureau_seg, col] = pd.NA
                        df_fichas.drop(columns=[col_bur], inplace=True)
                    elif col in df_fichas.columns and col not in ["SCORE_BUREAU", "RESTRITIVOS"]:
                        df_fichas.loc[~is_bureau_seg, col] = pd.NA
                
                df_fichas["ORIGEM_FONTE"] = "DF"
                df_fichas.loc[is_bureau_seg, "ORIGEM_FONTE"] = "BUREAU"

                # Adicionar CNPJs exclusivos do Bureau (clientes sem ficha cadastrada)
                cnpjs_somente_bureau = cnpjs_bureau - cnpjs_fichas
                if cnpjs_somente_bureau:
                    df_so_bureau = df_bureau_sub[df_bureau_sub["CNPJ"].isin(cnpjs_somente_bureau)].copy()
                    df_so_bureau["TIPO_FICHA"] = "CONSUMIDOR"
                    df_so_bureau["VOLUME_ENQUADRAMENTO_MWM"] = 1.0
                    df_so_bureau["DATA_ANALISE"] = df_so_bureau.get("DATA_BUREAU", pd.NaT)
                    df_so_bureau["ORIGEM_FONTE"] = "BUREAU"
                    df_fichas = pd.concat([df_fichas, df_so_bureau], ignore_index=True)
    
    return construir_fato_analise_credito(context, df_silver_analises=df_fichas, df_dim_contraparte=df_dim)


def construir_fato_analise_credito(
    context: AppContext,
    df_silver_analises: pd.DataFrame,
    df_dim_contraparte: pd.DataFrame,
) -> dict[str, Any]:
    run_id = f"FATO_ANL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold.fato_analise_credito", Path("LOGS/relational") / f"{run_id}__fato_analise_credito.log")
    logger.info("Iniciando carga de fato_analise_credito e execução do Motor de Crédito (run_id=%s).", run_id)

    if df_silver_analises.empty:
        return {"run_id": run_id, "linhas": 0, "status": "SEM_DADOS"}

    df_fato = df_silver_analises.copy()
    from common.identificadores import normalizar_cnpj_coluna
    df_fato["CNPJ"] = df_fato["CNPJ"].apply(normalizar_cnpj_coluna)
    df_fato["CNPJ_RAIZ"] = df_fato["CNPJ"].str[:8]

    try:
        pd_faixas = ler_json(context.control_file("pd_faixas"))
        pd_cpura_config = ler_json(context.control_file("pd_cpura_config"))
        score_cpura_config = ler_json(context.control_file("score_cpura_config"))
        pd_transform_rules = ler_json(context.control_file("pd_transform_rules"))
        try:
            pd_zscore_config = ler_json(context.control_file("pd_zscore_config"))
        except Exception:
            # Fallback se não mapeado no context
            pd_zscore_config = ler_json(context.path("control") / "configs" / "pd_zscore_config.json")
    except Exception:
        logger.exception("Falha ao carregar configurações do motor de crédito")
        raise

    resultados = []
    erros_qualidade = []
    alertas_db = []
    
    for _, row in df_fato.iterrows():
        registro = row.to_dict()
        cnpj = registro.get("CNPJ")
        
        # Tratar enquadramento de contrapartes de Bureau
        if pd.isna(registro.get("TIPO_FICHA")) or str(registro.get("TIPO_FICHA")).strip() == "":
            if registro.get("SCORE_BUREAU") is not None and not pd.isna(registro.get("SCORE_BUREAU")):
                registro["TIPO_FICHA"] = "CONSUMIDOR"
                if pd.isna(registro.get("VOLUME_ENQUADRAMENTO_MWM")):
                    registro["VOLUME_ENQUADRAMENTO_MWM"] = 1.0
            elif "DATA_BUREAU" in registro or "DATA_CONSULTA" in registro or registro.get("STATUS") in ["NAO_ENCONTRADO", "SUCESSO"]:
                registro["TIPO_FICHA"] = "CONSUMIDOR"
                if pd.isna(registro.get("VOLUME_ENQUADRAMENTO_MWM")):
                    registro["VOLUME_ENQUADRAMENTO_MWM"] = 1.0
            else:
                registro["TIPO_FICHA"] = "COMERCIALIZADORA"
        elif registro.get("TIPO_FICHA") == "CONSUMIDOR" and pd.isna(registro.get("VOLUME_ENQUADRAMENTO_MWM")):
            registro["VOLUME_ENQUADRAMENTO_MWM"] = 1.0

        try:
            segmento = definir_segmento_metodologico(registro)
            registro["SEGMENTO_PD"] = segmento
            
            if segmento == "NAO_ENQUADRADO":
                erros_qualidade.append({
                    "CNPJ": cnpj,
                    "RUN_ID": run_id,
                    "REGRA_QUALIDADE": "Enquadramento Metodológico",
                    "VALOR_OBSERVADO": "NAO_ENQUADRADO",
                    "MENSAGEM_ERRO": "Segmento NAO_ENQUADRADO, regras de crédito suspensas."
                })
                registro["RATING_FINAL"] = pd.NA
                registro["PD_FINAL"] = pd.NA
                registro["SCORE_TOTAL"] = pd.NA
                if registro.get("TIPO_FICHA") == "CONSUMIDOR":
                    registro["TIPO_ANALISE"] = "Análise Bureau"
                else:
                    registro["TIPO_ANALISE"] = "Análise DF"
                resultados.append(registro)
                continue
                
            pd_info = calcular_pd_ajustada(
                registro=registro,
                pd_faixas=pd_faixas,
                pd_transform_rules=pd_transform_rules,
                pd_cpura_config=pd_cpura_config,
                score_cpura_config=score_cpura_config,
                pd_zscore_config=pd_zscore_config,
                logger=logger
            )
            registro.update(pd_info)
            
            # Enriquecimento com Score e Restritivos da Risk3 (quando disponíveis)
            if registro.get("SCORE_BUREAU") is not None and not pd.isna(registro.get("SCORE_BUREAU")):
                registro["SCORE_TOTAL"] = float(registro["SCORE_BUREAU"])
            elif registro.get("SCORE_BUREAU_UTILIZADO") is not None:
                registro["SCORE_TOTAL"] = float(registro["SCORE_BUREAU_UTILIZADO"])
            
            if registro.get("RESTRITIVOS") is not None and not pd.isna(registro.get("RESTRITIVOS")):
                registro["RESTRITIVOS"] = float(registro.get("RESTRITIVOS"))
            elif registro.get("FATOR_ALERTA_UTILIZADO") is not None:
                registro["RESTRITIVOS"] = float(registro.get("FATOR_ALERTA_UTILIZADO"))

            # Definição estrita da metodologia de análise
            seg_pd = str(registro.get("SEGMENTO_PD", "")).strip().upper()
            if seg_pd == "CONSUMIDOR_LE_5":
                tem_score = (
                    registro.get("SCORE_BUREAU") is not None and not pd.isna(registro.get("SCORE_BUREAU"))
                ) or (
                    registro.get("SCORE_BUREAU_UTILIZADO") is not None and not pd.isna(registro.get("SCORE_BUREAU_UTILIZADO"))
                )
                if tem_score:
                    if registro.get("RATING_BUREAU") and (registro.get("RATING_FINAL") in ["NAO_APLICAVEL", None, ""]):
                        registro["RATING_FINAL"] = registro.get("RATING_BUREAU")
                    registro["TIPO_ANALISE"] = "Análise Bureau"
                else:
                    registro["TIPO_ANALISE"] = "Análise Bureau (N/A)"
                    registro["STATUS_CALCULO_PD"] = "PENDENTE"
                    registro["RATING_FINAL"] = pd.NA
                    registro["PD_FINAL"] = pd.NA
                    registro["SCORE_TOTAL"] = pd.NA
            elif registro.get("ANALISE_HERDADA") is True or registro.get("ORIGEM_ANALISE") == "HERDADA":
                registro["TIPO_ANALISE"] = "Análise Herdada"
            else:
                registro["TIPO_ANALISE"] = "Análise DF"
            
        except (PdInputValidationError, PdCalculationError, ValueError) as e:
            logger.warning("[CNPJ: %s] Falha no cálculo (Insumo Inválido/Pendente): %s", cnpj, e)
            valor_obs = str(registro.get("RATING_COPEL") or registro.get("NOTA_CREDITO") or registro.get("RATING") or registro.get("RATING_FINAL") or "None")
            alertas_db.append({
                "codigo": "PD_ERR_001",
                "severidade": "MEDIO",
                "regra": "Validação de Domínio Motor PD",
                "mensagem": str(e),
                "campo_afetado": "RATING/PD",
                "valor_observado": valor_obs,
                "limite_esperado": "VÁLIDO",
                "contraparte_id": cnpj
            })
            # Preservar o rating documental da ficha (RATING_COPEL, NOTA_CREDITO ou RATING)
            rating_doc = registro.get("RATING_COPEL") or registro.get("NOTA_CREDITO") or registro.get("RATING")
            registro["RATING_FINAL"] = str(rating_doc).strip() if pd.notna(rating_doc) and str(rating_doc).strip() not in ("", "None", "nan", "<NA>") else pd.NA
            registro["PD_FINAL"] = pd.NA
            registro["STATUS_CALCULO_PD"] = "PENDENTE"
            
            # Preservar SCORE_TOTAL e RESTRITIVOS da RISK3 se existirem
            if registro.get("SCORE_BUREAU") is not None and not pd.isna(registro.get("SCORE_BUREAU")):
                registro["SCORE_TOTAL"] = float(registro["SCORE_BUREAU"])
            elif registro.get("SCORE_TOTAL") is None:
                registro["SCORE_TOTAL"] = pd.NA

            if registro.get("RESTRITIVOS") is not None and not pd.isna(registro.get("RESTRITIVOS")):
                registro["RESTRITIVOS"] = float(registro.get("RESTRITIVOS"))
                
            if "TIPO_ANALISE" not in registro or not registro.get("TIPO_ANALISE"):
                if registro.get("TIPO_FICHA") == "CONSUMIDOR":
                    registro["TIPO_ANALISE"] = "Análise Bureau (N/A)" if pd.isna(registro.get("SCORE_TOTAL")) else "Análise Bureau"
                else:
                    registro["TIPO_ANALISE"] = "Análise DF" if pd.notna(registro["RATING_FINAL"]) else "Análise DF (N/A)"
            
        except Exception as e:
            logger.exception("Falha sistêmica no cálculo de crédito para CNPJ %s: %s", cnpj, e)
            alertas_db.append({
                "codigo": "PD_SYS_001",
                "severidade": "CRITICO",
                "regra": "Execução Motor PD",
                "mensagem": f"Erro sistêmico: {str(e)}",
                "campo_afetado": "MOTOR_PD",
                "valor_observado": "ERRO",
                "limite_esperado": "SUCESSO",
                "contraparte_id": cnpj
            })
            rating_doc = registro.get("RATING_COPEL") or registro.get("NOTA_CREDITO") or registro.get("RATING")
            registro["RATING_FINAL"] = str(rating_doc).strip() if pd.notna(rating_doc) and str(rating_doc).strip() not in ("", "None", "nan", "<NA>") else pd.NA
            registro["PD_FINAL"] = pd.NA
            registro["STATUS_CALCULO_PD"] = "ERRO_SISTEMICO"
            if registro.get("SCORE_BUREAU") is not None and not pd.isna(registro.get("SCORE_BUREAU")):
                registro["SCORE_TOTAL"] = float(registro["SCORE_BUREAU"])
            elif registro.get("SCORE_TOTAL") is None:
                registro["SCORE_TOTAL"] = pd.NA
            if registro.get("RESTRITIVOS") is not None and not pd.isna(registro.get("RESTRITIVOS")):
                registro["RESTRITIVOS"] = float(registro.get("RESTRITIVOS"))
            if "TIPO_ANALISE" not in registro or not registro.get("TIPO_ANALISE"):
                registro["TIPO_ANALISE"] = "Análise Bureau" if registro.get("TIPO_FICHA") == "CONSUMIDOR" else "Análise DF"

        resultados.append(registro)

    if alertas_db:
        from relational.facts.fato_alerta_util import registrar_alertas_em_lote
        registrar_alertas_em_lote(alertas_db, run_id, context)

    df_processado = pd.DataFrame(resultados)
    
    # Regra Estrita para DATA_ANALISE por metodologia:
    # 1. Se for Análise Bureau: DATA_ANALISE = DATA_BUREAU (ou DATA_CONSULTA)
    # 2. Se for Análise DF: DATA_ANALISE = DATA_CALCULO (ou DATA_DEMONSTRACAO_FINANCEIRA).
    #    Se a data vier nula da Silver, PERMANECE NaT! Nunca preencher com Risk3.
    df_processado["DATA_ANALISE"] = pd.NaT
    mask_bureau = df_processado["TIPO_ANALISE"] == "Análise Bureau"
    
    if "DATA_BUREAU" in df_processado.columns:
        df_processado.loc[mask_bureau, "DATA_ANALISE"] = pd.to_datetime(df_processado.loc[mask_bureau, "DATA_BUREAU"], errors="coerce")
    if "DATA_CONSULTA" in df_processado.columns:
        df_processado.loc[mask_bureau, "DATA_ANALISE"] = df_processado.loc[mask_bureau, "DATA_ANALISE"].fillna(pd.to_datetime(df_processado.loc[mask_bureau, "DATA_CONSULTA"], errors="coerce"))
        
    mask_df = ~mask_bureau
    if "DATA_CALCULO" in df_processado.columns:
        df_processado.loc[mask_df, "DATA_ANALISE"] = pd.to_datetime(df_processado.loc[mask_df, "DATA_CALCULO"], errors="coerce")
    if "DATA_DEMONSTRACAO_FINANCEIRA" in df_processado.columns:
        df_processado.loc[mask_df, "DATA_ANALISE"] = df_processado.loc[mask_df, "DATA_ANALISE"].fillna(pd.to_datetime(df_processado.loc[mask_df, "DATA_DEMONSTRACAO_FINANCEIRA"], errors="coerce"))
        
    # Converter para datetime64[ns]
    if "RATING_COPEL" in df_processado.columns:
        if "RATING_FINAL" not in df_processado.columns:
            df_processado["RATING_FINAL"] = df_processado["RATING_COPEL"]
        else:
            mask_na_rating = df_processado["RATING_FINAL"].isna() | df_processado["RATING_FINAL"].astype(str).str.strip().isin(["", "None", "nan", "<NA>"])
            df_processado.loc[mask_na_rating, "RATING_FINAL"] = df_processado.loc[mask_na_rating, "RATING_COPEL"]
    if "MODELO_METODOLOGICO" not in df_processado.columns and "versao_ficha" in df_processado.columns:
        df_processado["MODELO_METODOLOGICO"] = df_processado["versao_ficha"]

    # --- HERANÇA DE RISCO DE CONTROLADORAS ---
    try:
        from domain.controlador.servico_controlador import herdar_risco_controladoras
        
        ctrl_path = context.path("silver") / "mapeamento_controladoras" / "mapeamento_controladoras.parquet"
        df_controladoras = pd.read_parquet(ctrl_path) if ctrl_path.exists() else pd.DataFrame()
        
        if not df_controladoras.empty:
            if "_STATUS_REGISTRO" in df_controladoras.columns:
                df_controladoras = df_controladoras[df_controladoras["_STATUS_REGISTRO"] == "VIGENTE"]
            df_processado = herdar_risco_controladoras(df_processado, df_controladoras, col_cnpj="CNPJ")
            
        from domain.controlador.servico_controlador import herdar_risco_filiais
        
        path_contratos = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
        if not path_contratos.exists():
            path_contratos = context.path("silver") / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
            
        df_contratos = pd.read_parquet(path_contratos) if path_contratos.exists() else pd.DataFrame()
        df_processado = herdar_risco_filiais(df_processado, df_contratos)
    except Exception as e:
        logger.warning(f"Bypass Herança de Risco: Não foi possível aplicar herança de controladoras/filiais ({e})")
    # -----------------------------------------

    # Garantir FIM_VIGENCIA_ANALISE canônica
    if "FIM_VIGENCIA_ANALISE" not in df_processado.columns:
        df_processado["FIM_VIGENCIA_ANALISE"] = None
    mask_fim_na = df_processado["FIM_VIGENCIA_ANALISE"].isna() & df_processado["DATA_ANALISE"].notna()
    if mask_fim_na.any():
        mask_bur_na = mask_fim_na & (df_processado["TIPO_ANALISE"].astype(str).str.contains("Bureau"))
        mask_df_na = mask_fim_na & (~mask_bur_na)
        df_processado.loc[mask_bur_na, "FIM_VIGENCIA_ANALISE"] = (
            pd.to_datetime(df_processado.loc[mask_bur_na, "DATA_ANALISE"], errors="coerce") + pd.DateOffset(months=12)
        ).dt.strftime("%Y-%m-%d")
        df_processado.loc[mask_df_na, "FIM_VIGENCIA_ANALISE"] = (
            pd.to_datetime(df_processado.loc[mask_df_na, "DATA_ANALISE"], errors="coerce") + pd.DateOffset(months=18)
        ).dt.strftime("%Y-%m-%d")

    for col in ["ANALISE_ID", "DATA_ANALISE", "RATING_FINAL", "PD_FINAL", "SCORE_TOTAL", "CLASSE_RISCO", "MODELO_METODOLOGICO", "DATA_DEMONSTRACAO_FINANCEIRA", "SEGMENTO_PD", "TIPO_FICHA", "PATRIMONIO_LIQUIDO", "SITUACAO_DF", "SITUACAO_ANALISE", "CNPJ_RAIZ", "STATUS_CALCULO_PD", "RESTRITIVOS", "TIPO_ANALISE", "MOTIVO_PD_SUB", "DATA_ACIONAMENTO_PD_SUB", "FONTE_PD_SUB", "VALOR_PD_SUB", "PD_BASE", "PD_MIN_FAIXA", "PD_MAX_FAIXA", "CONFIG_SNAPSHOT_PD", "VALIDADE_DF", "VALIDADE_BUREAU", "VALIDADE_RATING_PUBLICO", "FIM_VIGENCIA_ANALISE", "ORIGEM_FONTE"]:
        if col not in df_processado.columns:
            df_processado[col] = None

    rename_map = {
        "ANALISE_ID": "ANALISE_ID",
        "CNPJ": "CNPJ", "CNPJ_RAIZ": "CNPJ_RAIZ", "DATA_ANALISE": "DATA_ANALISE", "RATING_FINAL": "RATING",
        "PD_FINAL": "PD_PERCENTUAL", "SCORE_TOTAL": "SCORE", "CLASSE_RISCO": "CLASSE",
        "MODELO_METODOLOGICO": "MODELO", "DATA_DEMONSTRACAO_FINANCEIRA": "DATA_BALANCO_USADO",
        "SEGMENTO_PD": "SEGMENTO_METODOLOGICO_FICHA", "TIPO_FICHA": "TIPO_FICHA",
        "PATRIMONIO_LIQUIDO": "PATRIMONIO_LIQUIDO", "SITUACAO_DF": "SITUACAO_DF",
        "SITUACAO_ANALISE": "SITUACAO_ANALISE", "STATUS_CALCULO_PD": "STATUS_CALCULO_PD",
        "ANALISE_HERDADA": "ANALISE_HERDADA", "ORIGEM_ANALISE": "ORIGEM_ANALISE",
        "TIPO_ANALISE": "TIPO_ANALISE", "RESTRITIVOS": "RESTRITIVOS",
        "MOTIVO_PD_SUB": "MOTIVO_PD_SUB", "DATA_ACIONAMENTO_PD_SUB": "DATA_ACIONAMENTO_PD_SUB",
        "FONTE_PD_SUB": "FONTE_PD_SUB", "VALOR_PD_SUB": "VALOR_PD_SUB",
        "PD_BASE": "PD_BASE", "PD_MIN_FAIXA": "PD_MIN", "PD_MAX_FAIXA": "PD_MAX",
        "CONFIG_SNAPSHOT_PD": "CONFIG_SNAPSHOT_PD",
        "VALIDADE_DF": "VALIDADE_DF", "VALIDADE_BUREAU": "VALIDADE_BUREAU", "VALIDADE_RATING_PUBLICO": "VALIDADE_RATING_PUBLICO",
        "FIM_VIGENCIA_ANALISE": "FIM_VIGENCIA_ANALISE", "ORIGEM_FONTE": "ORIGEM_FONTE"
    }

    df_final = df_processado[[c for c in rename_map.keys() if c in df_processado.columns]].rename(columns=rename_map).copy()
    df_final["ETL_RUN_ID"] = run_id

    relational_dir = context.path("relational_facts") / "credito"
    relational_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = relational_dir / "fato_analise_credito.parquet"
    
    if "DATA_ANALISE" in df_final.columns:
        df_final["DATA_ANALISE"] = pd.to_datetime(df_final["DATA_ANALISE"], errors="coerce")
    for num_col in ["SCORE", "PD_PERCENTUAL", "RESTRITIVOS", "PATRIMONIO_LIQUIDO"]:
        if num_col in df_final.columns:
            df_final[num_col] = pd.to_numeric(df_final[num_col], errors="coerce")

    if parquet_path.exists():
        df_existente = pd.read_parquet(parquet_path)
        if "DATA_ANALISE" in df_existente.columns:
            df_existente["DATA_ANALISE"] = pd.to_datetime(df_existente["DATA_ANALISE"], errors="coerce")
        for num_col in ["SCORE", "PD_PERCENTUAL", "RESTRITIVOS", "PATRIMONIO_LIQUIDO"]:
            if num_col in df_existente.columns:
                df_existente[num_col] = pd.to_numeric(df_existente[num_col], errors="coerce")
        df_historico = pd.concat([df_existente, df_final], ignore_index=True)
        # SCD2: dedup based on CNPJ and Date, keeping latest
        # fillna to avoid dropping NaT
        df_historico["_TEMP_DATE"] = df_historico["DATA_ANALISE"].fillna(pd.Timestamp("1900-01-01"))
        df_historico_dedup = df_historico.drop_duplicates(subset=["CNPJ", "_TEMP_DATE"], keep="last")
        df_historico_dedup = df_historico_dedup.sort_values(["CNPJ", "_TEMP_DATE"]).reset_index(drop=True)
        df_historico_dedup.drop(columns=["_TEMP_DATE"], inplace=True)
        
        df_historico_dedup["_VERSAO_REGISTRO"] = df_historico_dedup.groupby("CNPJ").cumcount() + 1
        df_historico_dedup["_STATUS_REGISTRO"] = "HISTORICO"
        idx_last = df_historico_dedup.groupby("CNPJ").tail(1).index
        df_historico_dedup.loc[idx_last, "_STATUS_REGISTRO"] = "VIGENTE"
        df_final = df_historico_dedup
    else:
        df_final["_VERSAO_REGISTRO"] = df_final.groupby("CNPJ").cumcount() + 1
        df_final["_STATUS_REGISTRO"] = "VIGENTE"

    # Garantir datetime64[ns] unificado antes de gravar em Parquet
    if "DATA_ANALISE" in df_final.columns:
        df_final["DATA_ANALISE"] = pd.to_datetime(df_final["DATA_ANALISE"], errors="coerce").astype("datetime64[ns]")
        
    escrever_conjunto_de_dados_silver(records=df_final.to_dict(orient="records"), output_dir=relational_dir, filename="fato_analise_credito")
    df_final.to_parquet(parquet_path, index=False)
    
    if erros_qualidade:
        df_erros = pd.DataFrame(erros_qualidade)
        erros_dir = context.path("silver") / "ctl_validacao_qualidade_credito"
        erros_dir.mkdir(parents=True, exist_ok=True)
        escrever_conjunto_de_dados_silver(records=df_erros.to_dict(orient="records"), output_dir=erros_dir, filename=f"pendencias_{run_id}")
        logger.info("Foram registradas %d pendências em ctl_validacao_qualidade_credito", len(erros_qualidade))

    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}


if __name__ == "__main__":
    from app.bootstrap import carregar_contexto
    ctx = carregar_contexto(Path("ENTRADAS/configs"))
    processar_fato_analise_credito(ctx)