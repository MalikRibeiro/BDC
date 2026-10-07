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
            if "DATA_BUREAU" not in df_bureau.columns:
                df_bureau["DATA_BUREAU"] = df_bureau.get("DATA_CONSULTA", pd.NaT)
            if "DATA_VALIDADE" in df_bureau.columns:
                mask_sem_dt = df_bureau["DATA_BUREAU"].isna() | df_bureau["DATA_BUREAU"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "NaT"])
                df_bureau.loc[mask_sem_dt, "DATA_BUREAU"] = (
                    pd.to_datetime(df_bureau.loc[mask_sem_dt, "DATA_VALIDADE"], errors="coerce") - pd.DateOffset(months=12)
                ).dt.strftime("%Y-%m-%d")

            if "SCORE_BUREAU" in df_bureau.columns:
                df_bureau["SCORE_BUREAU"] = pd.to_numeric(df_bureau["SCORE_BUREAU"], errors="coerce")
            if "RESTRITIVOS" in df_bureau.columns:
                df_bureau["RESTRITIVOS"] = pd.to_numeric(df_bureau["RESTRITIVOS"], errors="coerce")
            if "PD_BUREAU" in df_bureau.columns:
                df_bureau["PD_BUREAU"] = pd.to_numeric(df_bureau["PD_BUREAU"], errors="coerce")
            col_data_bureau = "DATA_CONSULTA" if "DATA_CONSULTA" in df_bureau.columns else "CNPJ"
            df_bureau = df_bureau.sort_values(col_data_bureau).drop_duplicates(subset=["CNPJ"], keep="last")
            
            cols_bureau_uteis = ["CNPJ", "SCORE_BUREAU", "RESTRITIVOS", "DATA_BUREAU", "PD_BUREAU", "RATING_BUREAU", "DATA_VALIDADE"]
            df_bureau_sub = df_bureau[[c for c in cols_bureau_uteis if c in df_bureau.columns]].copy()
            
            if df_fichas.empty:
                df_fichas = df_bureau_sub.copy()
                df_fichas["TIPO_FICHA"] = "CONSUMIDOR"
                df_fichas["VOLUME_ENQUADRAMENTO_MWM"] = 1.0
                df_fichas["DATA_ANALISE"] = df_fichas.get("DATA_BUREAU", pd.NaT)
                df_fichas["ORIGEM_FONTE"] = "BUREAU"
            else:
                cnpjs_bureau = set(df_bureau_sub["CNPJ"].dropna().unique())
                cnpjs_fichas = set(df_fichas["CNPJ"].dropna().unique())
                
                # Cruzamento: enriquecer com colunas da Risk3
                df_fichas = pd.merge(df_fichas, df_bureau_sub, on="CNPJ", how="left", suffixes=("", "_BUR"))
                
                # Preservar e integrar colunas do Bureau
                for col in ["SCORE_BUREAU", "RESTRITIVOS", "DATA_BUREAU", "PD_BUREAU", "RATING_BUREAU", "DATA_VALIDADE"]:
                    col_bur = f"{col}_BUR"
                    if col_bur in df_fichas.columns:
                        if col not in df_fichas.columns:
                            df_fichas[col] = df_fichas[col_bur]
                        else:
                            df_fichas[col] = df_fichas[col].combine_first(df_fichas[col_bur])
                        df_fichas.drop(columns=[col_bur], inplace=True)
                
                # Identificar quem possui Demonstração Financeira preenchida na ficha
                tem_df_mask = pd.Series(False, index=df_fichas.index)
                for c_df in ["DATA_DEMONSTRACAO_FINANCEIRA", "DATA_CALCULO", "ATIVO_TOTAL", "PATRIMONIO_LIQUIDO", "RATING_COPEL", "NOTA_CREDITO"]:
                    if c_df in df_fichas.columns:
                        s_val = df_fichas[c_df]
                        tem_df_mask = tem_df_mask | (s_val.notna() & (~s_val.astype(str).str.strip().isin(["", "None", "nan", "<NA>", "NaT", "-"])))

                df_fichas["ORIGEM_FONTE"] = "DF"
                # Apenas consumidores pequenos (< 5 MWm) sem DF podem ter ORIGEM_FONTE = "BUREAU"
                # Comercializadoras, Geradoras e Grandes Consumidores exigem obrigatoriamente DF e permanecem ORIGEM_FONTE = "DF"
                mask_pode_ser_bureau = ~tem_df_mask
                if "TIPO_FICHA" in df_fichas.columns:
                    mask_pode_ser_bureau = mask_pode_ser_bureau & (df_fichas["TIPO_FICHA"] == "CONSUMIDOR")
                if "VOLUME_ENQUADRAMENTO_MWM" in df_fichas.columns:
                    mask_pode_ser_bureau = mask_pode_ser_bureau & (df_fichas["VOLUME_ENQUADRAMENTO_MWM"].fillna(0) < 5.0)

                df_fichas.loc[mask_pode_ser_bureau, "ORIGEM_FONTE"] = "BUREAU"

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
        
        # Identificar se o registro possui Demonstração Financeira preenchida (Ficha Cadastral DF)
        tem_df_contabil = (
            (pd.notna(registro.get("DATA_DEMONSTRACAO_FINANCEIRA")) and str(registro.get("DATA_DEMONSTRACAO_FINANCEIRA")).strip() not in ("", "None", "nan", "<NA>", "NaT")) or 
            (pd.notna(registro.get("DATA_CALCULO")) and str(registro.get("DATA_CALCULO")).strip() not in ("", "None", "nan", "<NA>", "NaT")) or
            (pd.notna(registro.get("ATIVO_TOTAL")) and str(registro.get("ATIVO_TOTAL")).strip() not in ("", "None", "nan", "<NA>")) or
            (pd.notna(registro.get("PATRIMONIO_LIQUIDO")) and str(registro.get("PATRIMONIO_LIQUIDO")).strip() not in ("", "None", "nan", "<NA>")) or
            (pd.notna(registro.get("RATING_COPEL")) and str(registro.get("RATING_COPEL")).strip() not in ("", "None", "nan", "<NA>")) or
            (pd.notna(registro.get("NOTA_CREDITO")) and str(registro.get("NOTA_CREDITO")).strip() not in ("", "None", "nan", "<NA>"))
        )

        if pd.isna(registro.get("TIPO_FICHA")) or str(registro.get("TIPO_FICHA")).strip() == "":
            if not tem_df_contabil and (registro.get("SCORE_BUREAU") is not None and not pd.isna(registro.get("SCORE_BUREAU"))):
                registro["TIPO_FICHA"] = "CONSUMIDOR"
                if pd.isna(registro.get("VOLUME_ENQUADRAMENTO_MWM")):
                    registro["VOLUME_ENQUADRAMENTO_MWM"] = 1.0
            elif not tem_df_contabil and ("DATA_BUREAU" in registro or "DATA_CONSULTA" in registro or registro.get("STATUS") in ["NAO_ENCONTRADO", "SUCESSO"]):
                registro["TIPO_FICHA"] = "CONSUMIDOR"
                if pd.isna(registro.get("VOLUME_ENQUADRAMENTO_MWM")):
                    registro["VOLUME_ENQUADRAMENTO_MWM"] = 1.0
            else:
                registro["TIPO_FICHA"] = "COMERCIALIZADORA"
        elif registro.get("TIPO_FICHA") == "CONSUMIDOR":
            if tem_df_contabil:
                # Consumidor com Demonstração Financeira: assegurar capacidade contábil (>= 5 MWm) para preservar motor contábil
                if pd.isna(registro.get("VOLUME_ENQUADRAMENTO_MWM")):
                    registro["VOLUME_ENQUADRAMENTO_MWM"] = 5.0
            elif pd.isna(registro.get("VOLUME_ENQUADRAMENTO_MWM")):
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
                registro["STATUS_AUDITORIA_PD"] = "NAO_VALIDAVEL"
                registro["STATUS_AUDITORIA_RATING"] = "NAO_VALIDAVEL"
                registro["PD_OFICIAL_FICHA"] = None
                registro["PD_RECALCULADA_PYTHON"] = None
                registro["DELTA_PD"] = None
                vol_mwm = float(registro.get("VOLUME_ENQUADRAMENTO_MWM") or 0)
                if registro.get("TIPO_FICHA") == "CONSUMIDOR" and not tem_df_contabil and vol_mwm < 5.0:
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
            
            # Validação Paralela (Auditoria Sombra): Soberania da Ficha vs Recálculo Python
            try:
                from domain.credito.validador_paralelo import validar_paralelamente_pd_e_rating
                from common.numeros import to_float_br, to_percentual_br

                # Soberania da Origem (Regra III): A ficha é soberana para relatórios oficiais
                pd_ficha_raw = registro.get("PROBABILIDADE_DEFAULT") if registro.get("PROBABILIDADE_DEFAULT") is not None else registro.get("PD_BASE_FICHA")
                pd_ficha_num = to_percentual_br(pd_ficha_raw) if pd_ficha_raw is not None else None
                pd_calc_num = to_float_br(registro.get("PD_BASE")) if registro.get("PD_BASE") is not None else to_float_br(registro.get("PD_FINAL"))
                rating_ficha = str(registro.get("RATING_COPEL") or registro.get("NOTA_CREDITO") or "").strip() or None
                rating_calc = registro.get("RATING_FINAL")

                res_val = validar_paralelamente_pd_e_rating(
                    pd_calculada=pd_calc_num,
                    pd_declarada=pd_ficha_num,
                    rating_calculado=rating_calc,
                    rating_declarado=rating_ficha,
                    logger=logger,
                    cnpj=cnpj
                )
                registro["PD_OFICIAL_FICHA"] = res_val["PD_OFICIAL"]
                registro["PD_RECALCULADA_PYTHON"] = res_val["PD_CALCULADA"]
                registro["STATUS_AUDITORIA_PD"] = res_val["STATUS_CONCILIACAO_PD"]
                registro["STATUS_AUDITORIA_RATING"] = res_val["STATUS_CONCILIACAO_RATING"]
                registro["DELTA_PD"] = res_val["DELTA_PD"]

                # O valor oficial soberano prevalece para concessão se presente
                if pd_ficha_num is not None:
                    registro["PD_FINAL"] = pd_ficha_num
                if rating_ficha is not None:
                    registro["RATING_FINAL"] = rating_ficha
            except Exception as e_val:
                logger.warning("[AUDITORIA_SOMBRA] Falha ao executar conciliação para CNPJ %s: %s", cnpj, e_val)

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
            if seg_pd == "CONSUMIDOR_LE_5" and not tem_df_contabil:
                tem_score = (
                    registro.get("SCORE_BUREAU") is not None and not pd.isna(registro.get("SCORE_BUREAU"))
                ) or (
                    registro.get("SCORE_BUREAU_UTILIZADO") is not None and not pd.isna(registro.get("SCORE_BUREAU_UTILIZADO"))
                )
                if tem_score:
                    rb = registro.get("RATING_BUREAU")
                    rf = registro.get("RATING_FINAL")
                    if pd.notna(rb) and str(rb).strip() not in ("", "None", "nan", "<NA>"):
                        if pd.isna(rf) or str(rf).strip() in ("", "None", "nan", "<NA>", "NAO_APLICAVEL"):
                            registro["RATING_FINAL"] = str(rb).strip()
                    
                    pb = registro.get("PD_BUREAU")
                    pf = registro.get("PD_FINAL")
                    if pd.notna(pb) and (pd.isna(pf) or str(pf).strip() in ("", "None", "nan", "<NA>")):
                        registro["PD_FINAL"] = pb
                    registro["TIPO_ANALISE"] = "Análise Bureau"
                else:
                    registro["TIPO_ANALISE"] = "Análise Bureau (N/A)"
                    registro["STATUS_CALCULO_PD"] = "PENDENTE"
                    registro["RATING_FINAL"] = pd.NA
                    registro["PD_FINAL"] = pd.NA
                    registro["SCORE_TOTAL"] = pd.NA
            elif registro.get("ANALISE_HERDADA") is True or registro.get("ORIGEM_ANALISE") == "HERDADA":
                registro["TIPO_ANALISE"] = "Análise Herdada"
            elif registro.get("ORIGEM_FONTE") == "BUREAU" and not tem_df_contabil and registro.get("TIPO_FICHA") == "CONSUMIDOR" and float(registro.get("VOLUME_ENQUADRAMENTO_MWM") or 0) < 5.0:
                rb = registro.get("RATING_BUREAU")
                rf = registro.get("RATING_FINAL")
                if pd.notna(rb) and str(rb).strip() not in ("", "None", "nan", "<NA>"):
                    if pd.isna(rf) or str(rf).strip() in ("", "None", "nan", "<NA>", "NAO_APLICAVEL"):
                        registro["RATING_FINAL"] = str(rb).strip()
                
                pb = registro.get("PD_BUREAU")
                pf = registro.get("PD_FINAL")
                if pd.notna(pb) and (pd.isna(pf) or str(pf).strip() in ("", "None", "nan", "<NA>")):
                    registro["PD_FINAL"] = pb
                registro["TIPO_ANALISE"] = "Análise Bureau"
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
            rating_oficial = str(rating_doc).strip() if pd.notna(rating_doc) and str(rating_doc).strip() not in ("", "None", "nan", "<NA>") else None
            registro["RATING_FINAL"] = rating_oficial if rating_oficial is not None else pd.NA
            
            # SOBERANIA DA ORIGEM (Regra III): Preservar PD oficial da ficha se existir
            from domain.credito.validador_paralelo import validar_paralelamente_pd_e_rating
            from common.numeros import to_float_br, to_percentual_br

            pd_ficha_raw = registro.get("PROBABILIDADE_DEFAULT") if registro.get("PROBABILIDADE_DEFAULT") is not None else registro.get("PD_BASE_FICHA")
            pd_ficha_num = to_percentual_br(pd_ficha_raw) if pd_ficha_raw is not None else None
            registro["PD_FINAL"] = pd_ficha_num if pd_ficha_num is not None else pd.NA
            registro["STATUS_CALCULO_PD"] = "PENDENTE"

            # Contingência 1: Se houver PD contábil da ficha mas faltar Rating alfabético (ex: Axia/Eletrobras)
            if (registro["RATING_FINAL"] is pd.NA or pd.isna(registro["RATING_FINAL"])) and pd_ficha_num is not None:
                from domain.credito.rating import derivar_rating_por_pd
                r_der = derivar_rating_por_pd(pd_ficha_num, registro.get("SEGMENTO_PD") or registro.get("TIPO_FICHA"), pd_faixas)
                if r_der:
                    registro["RATING_FINAL"] = r_der

            # Segmentos com DF pendente/ausente: manter estritamente como pendência contábil (sem mascaramento por Bureau)
            registro["SITUACAO_DF"] = "PENDENTE_DF"

            try:
                res_val = validar_paralelamente_pd_e_rating(
                    pd_calculada=None,
                    pd_declarada=pd_ficha_num,
                    rating_calculado=None,
                    rating_declarado=rating_oficial,
                    logger=logger,
                    cnpj=cnpj
                )
                registro["PD_OFICIAL_FICHA"] = res_val["PD_OFICIAL"]
                registro["PD_RECALCULADA_PYTHON"] = res_val["PD_CALCULADA"]
                registro["STATUS_AUDITORIA_PD"] = res_val["STATUS_CONCILIACAO_PD"]
                registro["STATUS_AUDITORIA_RATING"] = res_val["STATUS_CONCILIACAO_RATING"]
                registro["DELTA_PD"] = res_val["DELTA_PD"]
            except Exception as e_val:
                logger.warning("[AUDITORIA_SOMBRA] Falha ao executar conciliação em contingência para CNPJ %s: %s", cnpj, e_val)
            
            # Preservar SCORE_TOTAL e RESTRITIVOS da RISK3 se existirem
            if registro.get("SCORE_BUREAU") is not None and not pd.isna(registro.get("SCORE_BUREAU")):
                registro["SCORE_TOTAL"] = float(registro["SCORE_BUREAU"])
            elif registro.get("SCORE_TOTAL") is None:
                registro["SCORE_TOTAL"] = pd.NA

            if registro.get("RESTRITIVOS") is not None and not pd.isna(registro.get("RESTRITIVOS")):
                registro["RESTRITIVOS"] = float(registro.get("RESTRITIVOS"))
                
            tipo_anl = registro.get("TIPO_ANALISE")
            if pd.isna(tipo_anl) or str(tipo_anl).strip() in ("", "None", "nan", "<NA>"):
                vol_mwm = float(registro.get("VOLUME_ENQUADRAMENTO_MWM") or 0)
                if registro.get("TIPO_FICHA") == "CONSUMIDOR" and vol_mwm < 5.0:
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
            rating_oficial = str(rating_doc).strip() if pd.notna(rating_doc) and str(rating_doc).strip() not in ("", "None", "nan", "<NA>") else None
            registro["RATING_FINAL"] = rating_oficial if rating_oficial is not None else pd.NA

            from domain.credito.validador_paralelo import validar_paralelamente_pd_e_rating
            from common.numeros import to_float_br, to_percentual_br

            pd_ficha_raw = registro.get("PROBABILIDADE_DEFAULT") if registro.get("PROBABILIDADE_DEFAULT") is not None else registro.get("PD_BASE_FICHA")
            pd_ficha_num = to_percentual_br(pd_ficha_raw) if pd_ficha_raw is not None else None
            registro["PD_FINAL"] = pd_ficha_num if pd_ficha_num is not None else pd.NA
            registro["STATUS_CALCULO_PD"] = "ERRO_SISTEMICO"

            try:
                res_val = validar_paralelamente_pd_e_rating(
                    pd_calculada=None,
                    pd_declarada=pd_ficha_num,
                    rating_calculado=None,
                    rating_declarado=rating_oficial,
                    logger=logger,
                    cnpj=cnpj
                )
                registro["PD_OFICIAL_FICHA"] = res_val["PD_OFICIAL"]
                registro["PD_RECALCULADA_PYTHON"] = res_val["PD_CALCULADA"]
                registro["STATUS_AUDITORIA_PD"] = res_val["STATUS_CONCILIACAO_PD"]
                registro["STATUS_AUDITORIA_RATING"] = res_val["STATUS_CONCILIACAO_RATING"]
                registro["DELTA_PD"] = res_val["DELTA_PD"]
            except Exception as e_val:
                logger.warning("[AUDITORIA_SOMBRA] Falha ao executar conciliação em erro sistêmico para CNPJ %s: %s", cnpj, e_val)
            if registro.get("SCORE_BUREAU") is not None and not pd.isna(registro.get("SCORE_BUREAU")):
                registro["SCORE_TOTAL"] = float(registro["SCORE_BUREAU"])
            elif registro.get("SCORE_TOTAL") is None:
                registro["SCORE_TOTAL"] = pd.NA
            if registro.get("RESTRITIVOS") is not None and not pd.isna(registro.get("RESTRITIVOS")):
                registro["RESTRITIVOS"] = float(registro.get("RESTRITIVOS"))
            tipo_anl_err = registro.get("TIPO_ANALISE")
            if pd.isna(tipo_anl_err) or str(tipo_anl_err).strip() in ("", "None", "nan", "<NA>"):
                vol_mwm = float(registro.get("VOLUME_ENQUADRAMENTO_MWM") or 0)
                registro["TIPO_ANALISE"] = "Análise Bureau" if (registro.get("TIPO_FICHA") == "CONSUMIDOR" and vol_mwm < 5.0) else "Análise DF"

        resultados.append(registro)

    if alertas_db:
        from relational.facts.fato_alerta_util import registrar_alertas_em_lote
        registrar_alertas_em_lote(alertas_db, run_id, context)

    df_processado = pd.DataFrame(resultados)
    
    # Regra Estrita para DATA_ANALISE por metodologia:
    # 1. Se for Análise Bureau: DATA_ANALISE = DATA_BUREAU (ou DATA_CONSULTA ou DATA_VALIDADE - 12 meses)
    # 2. Se for Análise DF: DATA_ANALISE = DATA_CALCULO (ou DATA_DEMONSTRACAO_FINANCEIRA).
    df_processado["DATA_ANALISE"] = pd.NaT
    mask_bureau = df_processado["TIPO_ANALISE"].astype(str).str.contains("Bureau", na=False)
    
    if "DATA_BUREAU" in df_processado.columns:
        df_processado.loc[mask_bureau, "DATA_ANALISE"] = pd.to_datetime(df_processado.loc[mask_bureau, "DATA_BUREAU"], errors="coerce")
    if "DATA_CONSULTA" in df_processado.columns:
        df_processado.loc[mask_bureau, "DATA_ANALISE"] = df_processado.loc[mask_bureau, "DATA_ANALISE"].fillna(pd.to_datetime(df_processado.loc[mask_bureau, "DATA_CONSULTA"], errors="coerce"))
    if "DATA_VALIDADE" in df_processado.columns:
        df_processado.loc[mask_bureau, "DATA_ANALISE"] = df_processado.loc[mask_bureau, "DATA_ANALISE"].fillna(
            pd.to_datetime(df_processado.loc[mask_bureau, "DATA_VALIDADE"], errors="coerce") - pd.DateOffset(months=12)
        )
    if "FIM_VIGENCIA_ANALISE" in df_processado.columns:
        df_processado.loc[mask_bureau, "DATA_ANALISE"] = df_processado.loc[mask_bureau, "DATA_ANALISE"].fillna(
            pd.to_datetime(df_processado.loc[mask_bureau, "FIM_VIGENCIA_ANALISE"], errors="coerce") - pd.DateOffset(months=12)
        )
        
    mask_df = ~mask_bureau
    if "DATA_CALCULO" in df_processado.columns:
        df_processado.loc[mask_df, "DATA_ANALISE"] = pd.to_datetime(df_processado.loc[mask_df, "DATA_CALCULO"], errors="coerce")
    if "DATA_DEMONSTRACAO_FINANCEIRA" in df_processado.columns:
        df_processado.loc[mask_df, "DATA_ANALISE"] = df_processado.loc[mask_df, "DATA_ANALISE"].fillna(pd.to_datetime(df_processado.loc[mask_df, "DATA_DEMONSTRACAO_FINANCEIRA"], errors="coerce"))
        
    # Assegurar FIM_VIGENCIA_ANALISE para Bureau
    if "DATA_VALIDADE" in df_processado.columns:
        if "FIM_VIGENCIA_ANALISE" not in df_processado.columns:
            df_processado["FIM_VIGENCIA_ANALISE"] = pd.NA
        mask_sem_fim_bur = mask_bureau & (df_processado["FIM_VIGENCIA_ANALISE"].isna() | df_processado["FIM_VIGENCIA_ANALISE"].astype(str).str.strip().isin(["", "None", "nan", "<NA>"]))
        df_processado.loc[mask_sem_fim_bur, "FIM_VIGENCIA_ANALISE"] = df_processado.loc[mask_sem_fim_bur, "DATA_VALIDADE"]
        
    # Converter para datetime64[ns]
    if "RATING_COPEL" in df_processado.columns:
        if "RATING_FINAL" not in df_processado.columns:
            df_processado["RATING_FINAL"] = df_processado["RATING_COPEL"]
        else:
            mask_na_rating = df_processado["RATING_FINAL"].isna() | df_processado["RATING_FINAL"].astype(str).str.strip().isin(["", "None", "nan", "<NA>"])
            df_processado.loc[mask_na_rating, "RATING_FINAL"] = df_processado.loc[mask_na_rating, "RATING_COPEL"]
    if "MODELO_METODOLOGICO" not in df_processado.columns and "versao_ficha" in df_processado.columns:
        df_processado["MODELO_METODOLOGICO"] = df_processado["versao_ficha"]

    # --- HERANÇA DE RISCO DIMENSIONAL (PARTE 2 APROVADA) ---
    # A clonagem física de linhas sintéticas na Fato foi eliminada. A herança de risco
    # agora é resolvida de forma relacional via dim_estabelecimento (FK/Join),
    # preservando a integridade da fato_analise_credito estritamente para análises reais.
    logger.info("Herança de Risco: resolvida relacionalmente via dim_estabelecimento (sem clonagem sintética na fato).")

    # --- FALLBACK 3: ANÁLISE DE CRÉDITO VIA SALESFORCE (CHAMADO / CONTA) ---
    try:
        RATINGS_VALIDOS_COPEL = {"A", "B", "C", "D", "E", "F"}
        from common.identificadores import normalizar_cnpj_coluna
        from common.numeros import to_float_br

        # 1. Carregar chamados de crédito do Salesforce
        sf_chamado_path = context.path("silver") / "salesforce_silver" / "chamado" / "salesforce_chamado.parquet"
        df_sf_chamados_val = pd.DataFrame()
        if sf_chamado_path.exists():
            df_ch = pd.read_parquet(sf_chamado_path)
            if not df_ch.empty and "CNPJ" in df_ch.columns:
                df_ch["CNPJ"] = df_ch["CNPJ"].apply(normalizar_cnpj_coluna)
                if "Status_Analise_de_Credito__c" in df_ch.columns:
                    mask_aprov = df_ch["Status_Analise_de_Credito__c"].astype(str).str.strip().str.upper() == "APROVADO"
                    df_ch = df_ch[mask_aprov]
                
                col_dt_ch = "Data_AvaliacaoCredito__c" if "Data_AvaliacaoCredito__c" in df_ch.columns else "DT_PROCESSAMENTO"
                if col_dt_ch in df_ch.columns:
                    df_ch = df_ch.sort_values(col_dt_ch, na_position="first").drop_duplicates(subset=["CNPJ"], keep="last")
                df_sf_chamados_val = df_ch

        # 2. Carregar contas do Salesforce
        sf_acc_path = context.path("silver") / "salesforce_silver" / "account" / "salesforce_account.parquet"
        df_sf_acc_val = pd.DataFrame()
        if sf_acc_path.exists():
            df_acc = pd.read_parquet(sf_acc_path)
            if not df_acc.empty and "CNPJ" in df_acc.columns:
                df_acc["CNPJ"] = df_acc["CNPJ"].apply(normalizar_cnpj_coluna)
                df_sf_acc_val = df_acc.drop_duplicates(subset=["CNPJ"], keep="last")

        # 3. Aplicar fallback nos registros órfãos de df_processado
        mask_sem_rating = (
            df_processado["RATING_FINAL"].isna() | 
            df_processado["RATING_FINAL"].astype(str).str.strip().isin(["", "None", "nan", "<NA>", "PENDENTE", "NAO_ENQUADRADO", "NAO_APLICAVEL"])
        )

        for idx in df_processado[mask_sem_rating].index:
            cnpj_target = str(df_processado.at[idx, "CNPJ"]).strip()
            aplicou_sf = False

            # Prioridade A: Chamado Aprovado mais recente
            if not df_sf_chamados_val.empty and cnpj_target in df_sf_chamados_val["CNPJ"].values:
                ch_row = df_sf_chamados_val[df_sf_chamados_val["CNPJ"] == cnpj_target].iloc[0]
                rating_cand = str(ch_row.get("Rating_final__c") or ch_row.get("Risk3_Rating__c") or "").strip().upper()
                if rating_cand in RATINGS_VALIDOS_COPEL:
                    df_processado.at[idx, "RATING_FINAL"] = rating_cand
                    pd_raw = ch_row.get("Probabilidade_de_default__c")
                    df_processado.at[idx, "PD_FINAL"] = to_float_br(pd_raw) if pd_raw is not None else pd.NA
                    dt_aval = ch_row.get("Data_AvaliacaoCredito__c")
                    if dt_aval and pd.notna(dt_aval):
                        df_processado.at[idx, "DATA_ANALISE"] = pd.to_datetime(dt_aval, errors="coerce")
                    seg_alvo = str(df_processado.at[idx, "SEGMENTO_PD"] or "").strip().upper()
                    df_processado.at[idx, "TIPO_ANALISE"] = "Análise Bureau" if seg_alvo == "CONSUMIDOR_LE_5" else "Análise DF"
                    df_processado.at[idx, "ANALISE_HERDADA"] = False
                    df_processado.at[idx, "ORIGEM_ANALISE"] = "SALESFORCE_CHAMADO"
                    df_processado.at[idx, "ORIGEM_FONTE"] = "SALESFORCE"
                    df_processado.at[idx, "STATUS_CALCULO_PD"] = "CONCLUIDO"
                    aplicou_sf = True

            # Prioridade B: Conta Salesforce (se Chamado não contiver rating alfabético válido)
            if not aplicou_sf and not df_sf_acc_val.empty and cnpj_target in df_sf_acc_val["CNPJ"].values:
                acc_row = df_sf_acc_val[df_sf_acc_val["CNPJ"] == cnpj_target].iloc[0]
                rating_cand = str(acc_row.get("Risk3_Rating__c") or acc_row.get("RatingCreditoMiddle__c") or "").strip().upper()
                if rating_cand in RATINGS_VALIDOS_COPEL:
                    df_processado.at[idx, "RATING_FINAL"] = rating_cand
                    df_processado.at[idx, "PD_FINAL"] = pd.NA
                    dt_aval = acc_row.get("DataAvaliacao__c") or acc_row.get("Risk3_DataAvaliacao__c")
                    if dt_aval and pd.notna(dt_aval):
                        df_processado.at[idx, "DATA_ANALISE"] = pd.to_datetime(dt_aval, errors="coerce")
                    validade_sf = acc_row.get("CreditAnalysisValidity__c") or acc_row.get("Risk3_ValidadeAvaliacao__c")
                    if validade_sf and pd.notna(validade_sf):
                        dt_v = pd.to_datetime(validade_sf, errors="coerce")
                        if not pd.isna(dt_v):
                            df_processado.at[idx, "FIM_VIGENCIA_ANALISE"] = dt_v.strftime("%Y-%m-%d")
                    seg_alvo = str(df_processado.at[idx, "SEGMENTO_PD"] or "").strip().upper()
                    df_processado.at[idx, "TIPO_ANALISE"] = "Análise Bureau" if seg_alvo == "CONSUMIDOR_LE_5" else "Análise DF"
                    df_processado.at[idx, "ANALISE_HERDADA"] = False
                    df_processado.at[idx, "ORIGEM_ANALISE"] = "SALESFORCE_CONTA"
                    df_processado.at[idx, "ORIGEM_FONTE"] = "SALESFORCE"
                    df_processado.at[idx, "STATUS_CALCULO_PD"] = "CONCLUIDO"
                    aplicou_sf = True

            # Prioridade C: Bureau Risk3 (aplicável EXCLUSIVAMENTE a Consumidores LE_5 onde a metodologia oficial é o Bureau)
            if not aplicou_sf:
                seg_alvo = str(df_processado.at[idx, "SEGMENTO_PD"] or "").strip().upper()
                tipo_f = str(df_processado.at[idx, "TIPO_FICHA"] or "").strip().upper()
                exige_df = ("CPURA" in seg_alvo) or ("CGRUPO" in seg_alvo) or (tipo_f == "COMERCIALIZADORA") or ("GT_5" in seg_alvo)
                if not exige_df and seg_alvo == "CONSUMIDOR_LE_5":
                    rb_cand = str(df_processado.at[idx, "RATING_BUREAU"] or "").strip().upper()
                    if rb_cand in RATINGS_VALIDOS_COPEL:
                        df_processado.at[idx, "RATING_FINAL"] = rb_cand
                        pb_val = df_processado.at[idx, "PD_BUREAU"]
                        if pd.notna(pb_val):
                            df_processado.at[idx, "PD_FINAL"] = to_float_br(pb_val)
                        dt_b = df_processado.at[idx, "DATA_BUREAU"] or df_processado.at[idx, "DATA_VALIDADE"]
                        if dt_b and pd.notna(dt_b):
                            df_processado.at[idx, "DATA_ANALISE"] = pd.to_datetime(dt_b, errors="coerce")
                        val_b = df_processado.at[idx, "DATA_VALIDADE"]
                        if val_b and pd.notna(val_b):
                            df_processado.at[idx, "FIM_VIGENCIA_ANALISE"] = str(val_b)
                        df_processado.at[idx, "TIPO_ANALISE"] = "Análise Bureau"
                        df_processado.at[idx, "ANALISE_HERDADA"] = False
                        df_processado.at[idx, "ORIGEM_ANALISE"] = "BUREAU_RISK3"
                        df_processado.at[idx, "ORIGEM_FONTE"] = "BUREAU"
                        df_processado.at[idx, "FONTE_ANALISE"] = "Bureau (Risk3)"
                        df_processado.at[idx, "STATUS_CALCULO_PD"] = "CONCLUIDO"
                        aplicou_sf = True

            # Prioridade D: Derivação de Rating por PD se PD estiver calculada (ex: Axia/Eletrobras)
            if not aplicou_sf:
                pd_cand = df_processado.at[idx, "PD_FINAL"]
                if pd_cand is not None and pd.notna(pd_cand):
                    from domain.credito.rating import derivar_rating_por_pd
                    r_der = derivar_rating_por_pd(pd_cand, df_processado.at[idx, "SEGMENTO_PD"] or df_processado.at[idx, "TIPO_FICHA"], pd_faixas)
                    if r_der in RATINGS_VALIDOS_COPEL:
                        df_processado.at[idx, "RATING_FINAL"] = r_der
                        df_processado.at[idx, "STATUS_CALCULO_PD"] = "CONCLUIDO"
                        aplicou_sf = True

        # 4. Inserir contrapartes ativas de contratos que NÃO estavam na Fato e possuem análise no Salesforce
        cnpjs_na_fato = set(df_processado["CNPJ"].unique())
        if not df_contratos.empty and "CNPJ" in df_contratos.columns:
            cnpjs_contratos_ativos = set(df_contratos["CNPJ"].dropna().unique())
            cnpjs_orfaos_contrato = cnpjs_contratos_ativos - cnpjs_na_fato

            novos_registros_sf = []
            for cnpj_orfao in cnpjs_orfaos_contrato:
                c_str = str(cnpj_orfao).strip()
                novo_reg = None

                if not df_sf_chamados_val.empty and c_str in df_sf_chamados_val["CNPJ"].values:
                    ch_row = df_sf_chamados_val[df_sf_chamados_val["CNPJ"] == c_str].iloc[0]
                    rating_cand = str(ch_row.get("Rating_final__c") or ch_row.get("Risk3_Rating__c") or "").strip().upper()
                    if rating_cand in RATINGS_VALIDOS_COPEL:
                        pd_raw = ch_row.get("Probabilidade_de_default__c")
                        dt_aval = ch_row.get("Data_AvaliacaoCredito__c")
                        novo_reg = {
                            "CNPJ": c_str,
                            "CNPJ_RAIZ": c_str[:8],
                            "RATING_FINAL": rating_cand,
                            "PD_FINAL": to_float_br(pd_raw) if pd_raw is not None else pd.NA,
                            "DATA_ANALISE": pd.to_datetime(dt_aval, errors="coerce") if dt_aval else pd.NaT,
                            "ANALISE_HERDADA": False,
                            "TIPO_ANALISE": "Análise DF",
                            "ORIGEM_ANALISE": "SALESFORCE_CHAMADO",
                            "ORIGEM_FONTE": "SALESFORCE",
                            "STATUS_CALCULO_PD": "CONCLUIDO"
                        }
                elif not df_sf_acc_val.empty and c_str in df_sf_acc_val["CNPJ"].values:
                    acc_row = df_sf_acc_val[df_sf_acc_val["CNPJ"] == c_str].iloc[0]
                    rating_cand = str(acc_row.get("Risk3_Rating__c") or acc_row.get("RatingCreditoMiddle__c") or "").strip().upper()
                    if rating_cand in RATINGS_VALIDOS_COPEL:
                        dt_aval = acc_row.get("DataAvaliacao__c") or acc_row.get("Risk3_DataAvaliacao__c")
                        validade_sf = acc_row.get("CreditAnalysisValidity__c") or acc_row.get("Risk3_ValidadeAvaliacao__c")
                        fim_vig = None
                        if validade_sf and pd.notna(validade_sf):
                            dt_v = pd.to_datetime(validade_sf, errors="coerce")
                            if not pd.isna(dt_v):
                                fim_vig = dt_v.strftime("%Y-%m-%d")
                        novo_reg = {
                            "CNPJ": c_str,
                            "CNPJ_RAIZ": c_str[:8],
                            "RATING_FINAL": rating_cand,
                            "PD_FINAL": pd.NA,
                            "DATA_ANALISE": pd.to_datetime(dt_aval, errors="coerce") if dt_aval else pd.NaT,
                            "FIM_VIGENCIA_ANALISE": fim_vig,
                            "ANALISE_HERDADA": False,
                            "TIPO_ANALISE": "Análise DF",
                            "ORIGEM_ANALISE": "SALESFORCE_CONTA",
                            "ORIGEM_FONTE": "SALESFORCE",
                            "STATUS_CALCULO_PD": "CONCLUIDO"
                        }
                if novo_reg:
                    novos_registros_sf.append(novo_reg)
            if novos_registros_sf:
                df_novos_sf = pd.DataFrame(novos_registros_sf)
                df_processado = pd.concat([df_processado, df_novos_sf], ignore_index=True)
    except Exception as e:
        logger.warning(f"Bypass Fallback Salesforce Risco: {e}")
    # ----------------------------------------------------------------------

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

    # BUG 3 FIX: Gerar ANALISE_ID como hash determinístico (CNPJ + DATA_ANALISE)
    import hashlib
    def _gerar_analise_id(row):
        cnpj = str(row.get("CNPJ", "")).strip()
        data = str(row.get("DATA_ANALISE", "")).strip().replace("-", "").replace(" ", "")[:8]
        if not cnpj or cnpj in ("None", "nan", "<NA>"):
            return None
        chave = f"{cnpj}_{data}"
        return f"ANA_{hashlib.md5(chave.encode()).hexdigest()[:12].upper()}"
    df_processado["ANALISE_ID"] = df_processado.apply(_gerar_analise_id, axis=1)

    # PADRONIZAÇÃO: Derivar FONTE_ANALISE canônica a partir de ORIGEM_FONTE e ORIGEM_ANALISE
    _mapa_fonte = {
        "DF": "Ficha Interna",
        "BUREAU": "Bureau (Risk3)",
        "SALESFORCE": "Salesforce",
    }
    if "ORIGEM_FONTE" not in df_processado.columns:
        df_processado["ORIGEM_FONTE"] = None
    of = df_processado["ORIGEM_FONTE"].astype(str).str.strip().str.upper()
    df_processado["FONTE_ANALISE"] = of.map(_mapa_fonte).fillna("Ficha Interna")
    # Heranças (TIPO_ANALISE contém "Herdada")
    mask_herdada = df_processado["TIPO_ANALISE"].astype(str).str.contains("Herdada", case=False, na=False)
    df_processado.loc[mask_herdada, "FONTE_ANALISE"] = "Herança Societária"
    # Salesforce: prevalece sobre a label genérica quando a origem é explícita
    mask_sf = of.isin(["SALESFORCE"])
    df_processado.loc[mask_sf, "FONTE_ANALISE"] = "Salesforce"

    # Identificação Declarativa de Intercompany (Grupo Próprio Isento de Risco de Crédito)
    try:
        cfg_intercompany_path = Path("ENTRADAS/control/configs/contrapartes_grupo_proprio.json")
        if cfg_intercompany_path.exists():
            import json
            with open(cfg_intercompany_path, "r", encoding="utf-8") as f_ic:
                cfg_ic = json.load(f_ic)
            raizes_ic = tuple(cfg_ic.get("raizes_cnpj_isentas", []))
            cnpjs_exatos_ic = set(cfg_ic.get("cnpjs_isentos", []))
            termos_nome_ic = cfg_ic.get("termos_razao_social", [])

            s_cnpj_fat = df_processado["CNPJ"].astype(str).str.zfill(14)
            cond_rz = s_cnpj_fat.str.startswith(raizes_ic) if raizes_ic else pd.Series(False, index=df_processado.index)
            cond_cp = s_cnpj_fat.isin(cnpjs_exatos_ic) if cnpjs_exatos_ic else pd.Series(False, index=df_processado.index)
            
            col_nm = "RAZAO_SOCIAL" if "RAZAO_SOCIAL" in df_processado.columns else ("NOME" if "NOME" in df_processado.columns else None)
            s_nm = df_processado[col_nm].astype(str).str.upper() if col_nm and col_nm in df_processado.columns else pd.Series("", index=df_processado.index)
            cond_nm = s_nm.apply(lambda x: any(t in x for t in termos_nome_ic)) if termos_nome_ic else pd.Series(False, index=df_processado.index)

            mask_ic = cond_rz | cond_cp | cond_nm
            if mask_ic.any():
                df_processado.loc[mask_ic, "RATING_FINAL"] = "ISENTO_INTERCOMPANY"
                df_processado.loc[mask_ic, "PD_FINAL"] = 0.0
                df_processado.loc[mask_ic, "SITUACAO_ANALISE"] = "ISENTO_INTERCOMPANY"
                df_processado.loc[mask_ic, "TIPO_ANALISE"] = "Intercompany"
                df_processado.loc[mask_ic, "ORIGEM_ANALISE"] = "INTERCOMPANY"
                df_processado.loc[mask_ic, "FONTE_ANALISE"] = "Intercompany"
                df_processado.loc[mask_ic, "STATUS_CALCULO_PD"] = "ISENTO"
                df_processado.loc[mask_ic, "STATUS_AUDITORIA_PD"] = "NAO_APLICAVEL"
                df_processado.loc[mask_ic, "STATUS_AUDITORIA_RATING"] = "NAO_APLICAVEL"
    except Exception as e_ic:
        logger.warning("Falha ao identificar intercompany em fato_analise_credito: %s", e_ic)

    for col in ["ANALISE_ID", "DATA_ANALISE", "RATING_FINAL", "PD_FINAL", "SCORE_TOTAL", "CLASSE_RISCO", "MODELO_METODOLOGICO", "DATA_DEMONSTRACAO_FINANCEIRA", "SEGMENTO_PD", "TIPO_FICHA", "PATRIMONIO_LIQUIDO", "SITUACAO_DF", "SITUACAO_ANALISE", "CNPJ_RAIZ", "STATUS_CALCULO_PD", "RESTRITIVOS", "TIPO_ANALISE", "MOTIVO_PD_SUB", "DATA_ACIONAMENTO_PD_SUB", "FONTE_PD_SUB", "VALOR_PD_SUB", "PD_BASE", "PD_MIN_FAIXA", "PD_MAX_FAIXA", "CONFIG_SNAPSHOT_PD", "VALIDADE_DF", "VALIDADE_BUREAU", "VALIDADE_RATING_PUBLICO", "FIM_VIGENCIA_ANALISE", "ORIGEM_FONTE", "FONTE_ANALISE"]:
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
        "FIM_VIGENCIA_ANALISE": "FIM_VIGENCIA_ANALISE", "ORIGEM_FONTE": "ORIGEM_FONTE",
        "FONTE_ANALISE": "FONTE_ANALISE",
        "PD_OFICIAL_FICHA": "PD_OFICIAL_FICHA",
        "PD_RECALCULADA_PYTHON": "PD_RECALCULADA_PYTHON",
        "STATUS_AUDITORIA_PD": "STATUS_AUDITORIA_PD",
        "STATUS_AUDITORIA_RATING": "STATUS_AUDITORIA_RATING",
        "DELTA_PD": "DELTA_PD",
        "VENDAS_LIQUIDAS": "VENDAS_LIQUIDAS",
        "LUCRO_LIQUIDO": "LUCRO_LIQUIDO",
        "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS": "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        "SCORE_BOARD_COPEL": "SCORE_BOARD_COPEL",
        "RATING_BOARD_COPEL": "RATING_BOARD_COPEL"
    }

    df_final = df_processado[[c for c in rename_map.keys() if c in df_processado.columns]].rename(columns=rename_map).copy()
    df_final["ETL_RUN_ID"] = run_id

    relational_dir = context.path("relational_facts") / "credito"
    relational_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = relational_dir / "fato_analise_credito.parquet"
    
    if "DATA_ANALISE" in df_final.columns:
        df_final["DATA_ANALISE"] = pd.to_datetime(df_final["DATA_ANALISE"], errors="coerce")
    colunas_numericas = [
        "SCORE", "PD_PERCENTUAL", "RESTRITIVOS", "PATRIMONIO_LIQUIDO",
        "VENDAS_LIQUIDAS", "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        "SCORE_BOARD_COPEL", "PD_OFICIAL_FICHA", "PD_RECALCULADA_PYTHON", "DELTA_PD",
        "PD_BASE", "PD_MIN", "PD_MAX", "VALOR_PD_SUB"
    ]
    for num_col in colunas_numericas:
        if num_col in df_final.columns:
            df_final[num_col] = pd.to_numeric(df_final[num_col], errors="coerce")

    if parquet_path.exists():
        df_existente = pd.read_parquet(parquet_path)
        # Expurgo estrito da clonagem sintética legada do histórico físico da fato
        if "ANALISE_HERDADA" in df_existente.columns:
            df_existente = df_existente[df_existente["ANALISE_HERDADA"] != True]
        if "ORIGEM_ANALISE" in df_existente.columns:
            df_existente = df_existente[~df_existente["ORIGEM_ANALISE"].astype(str).str.contains("HERDADA", case=False, na=False)]
        if "DATA_ANALISE" in df_existente.columns:
            df_existente["DATA_ANALISE"] = pd.to_datetime(df_existente["DATA_ANALISE"], errors="coerce")
        for num_col in colunas_numericas:
            if num_col in df_existente.columns:
                df_existente[num_col] = pd.to_numeric(df_existente[num_col], errors="coerce")
        df_historico = pd.concat([df_existente, df_final], ignore_index=True)
        # SCD2: dedup based on CNPJ and Date, keeping latest
        col_r_chk = "RATING_FINAL" if "RATING_FINAL" in df_historico.columns else "RATING"
        has_r = df_historico[col_r_chk].notna() & (~df_historico[col_r_chk].astype(str).str.strip().isin(["", "None", "nan", "<NA>"]))
        df_historico["_HAS_RATING"] = has_r.astype(int)
        df_historico["_TEMP_DATE"] = pd.to_datetime(df_historico["DATA_ANALISE"], errors="coerce").fillna(pd.Timestamp("1900-01-01"))
        
        # Registros com Rating e data mais recente prevalecem
        df_historico_dedup = df_historico.sort_values(["CNPJ", "_TEMP_DATE", "_HAS_RATING"]).reset_index(drop=True)
        df_historico_dedup = df_historico_dedup.drop_duplicates(subset=["CNPJ", "_TEMP_DATE"], keep="last")
        df_historico_dedup = df_historico_dedup.sort_values(["CNPJ", "_TEMP_DATE", "_HAS_RATING"]).reset_index(drop=True)
        df_historico_dedup.drop(columns=["_TEMP_DATE", "_HAS_RATING"], inplace=True)
        
        df_historico_dedup["_VERSAO_REGISTRO"] = df_historico_dedup.groupby("CNPJ").cumcount() + 1
        df_historico_dedup["_STATUS_REGISTRO"] = "HISTORICO"
        idx_last = df_historico_dedup.groupby("CNPJ").tail(1).index
        df_historico_dedup.loc[idx_last, "_STATUS_REGISTRO"] = "VIGENTE"
        df_final = df_historico_dedup
    else:
        col_r_chk = "RATING_FINAL" if "RATING_FINAL" in df_final.columns else "RATING"
        has_r = df_final[col_r_chk].notna() & (~df_final[col_r_chk].astype(str).str.strip().isin(["", "None", "nan", "<NA>"]))
        df_final["_HAS_RATING"] = has_r.astype(int)
        df_final["_TEMP_DATE"] = pd.to_datetime(df_final["DATA_ANALISE"], errors="coerce").fillna(pd.Timestamp("1900-01-01"))
        df_final = df_final.sort_values(["CNPJ", "_TEMP_DATE", "_HAS_RATING"]).reset_index(drop=True)
        df_final.drop(columns=["_TEMP_DATE", "_HAS_RATING"], inplace=True)
        df_final["_VERSAO_REGISTRO"] = df_final.groupby("CNPJ").cumcount() + 1
        df_final["_STATUS_REGISTRO"] = "HISTORICO"
        idx_last = df_final.groupby("CNPJ").tail(1).index
        df_final.loc[idx_last, "_STATUS_REGISTRO"] = "VIGENTE"

    # Garantir datetime64[ns] unificado antes de gravar em Parquet
    if "DATA_ANALISE" in df_final.columns:
        df_final["DATA_ANALISE"] = pd.to_datetime(df_final["DATA_ANALISE"], errors="coerce").astype("datetime64[ns]")

    # Garantir tipagem limpa para evitar falha no pyarrow com valores tipo 'NAO_APLICAVEL'
    for num_col in colunas_numericas:
        if num_col in df_final.columns:
            df_final[num_col] = pd.to_numeric(df_final[num_col], errors="coerce")

    colunas_texto = [
        "STATUS_AUDITORIA_PD", "STATUS_AUDITORIA_RATING", "RATING", 
        "RATING_BOARD_COPEL", "MODELO", "CLASSE", "SITUACAO_DF", 
        "SITUACAO_ANALISE", "TIPO_ANALISE", "FONTE_ANALISE", "ORIGEM_FONTE"
    ]
    for str_col in colunas_texto:
        if str_col in df_final.columns:
            df_final[str_col] = df_final[str_col].astype("string")
        
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