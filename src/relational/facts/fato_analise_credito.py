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
from domain.credito.pd_exceptions import PdInputValidationError

def construir_fato_analise_credito(
    context: AppContext,
    df_silver_analises: pd.DataFrame,
    df_dim_contraparte: pd.DataFrame,
) -> dict[str, Any]:
    run_id = f"FATO_ANL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold.fato_analise_credito", Path("LOGS/relacional") / f"{run_id}__fato_analise_credito.log")
    logger.info("Iniciando carga de fato_analise_credito e execução do Motor de Crédito (run_id=%s).", run_id)

    if df_silver_analises.empty:
        return {"run_id": run_id, "linhas": 0, "status": "SEM_DADOS"}

    df_fato = df_silver_analises.copy()
    from common.identificadores import normalizar_cnpj
    df_fato["CNPJ"] = df_fato["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    df_fato["CNPJ_RAIZ"] = df_fato["CNPJ"].str[:8]

    try:
        pd_faixas = ler_json(context.control_file("pd_faixas"))
        pd_cpura_config = ler_json(context.control_file("pd_cpura_config"))
        score_cpura_config = ler_json(context.control_file("score_cpura_config"))
        pd_transform_rules = ler_json(context.control_file("pd_transform_rules"))
    except Exception:
        logger.exception("Falha ao carregar configurações do motor de crédito")
        raise

    resultados = []
    erros_qualidade = []
    alertas_db = []
    
    for _, row in df_fato.iterrows():
        registro = row.to_dict()
        registro["TIPO_FICHA"] = registro.get("TIPO_FICHA", "COMERCIALIZADORA")
        cnpj = registro.get("CNPJ")

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
                resultados.append(registro)
                continue
                
            pd_info = calcular_pd_ajustada(
                registro=registro,
                pd_faixas=pd_faixas,
                pd_transform_rules=pd_transform_rules,
                pd_cpura_config=pd_cpura_config,
                score_cpura_config=score_cpura_config,
                logger=logger
            )
            registro.update(pd_info)
            
        except (PdInputValidationError, ValueError) as e:
            logger.warning("[CNPJ: %s] Falha no cálculo (Insumo Inválido): %s", cnpj, e)
            valor_obs = str(registro.get("RATING_COPEL") or registro.get("NOTA_CREDITO") or registro.get("RATING") or registro.get("RATING_FINAL") or "None")
            alertas_db.append({
                "codigo": "PD_ERR_001",
                "severidade": "ALTO",
                "regra": "Validação de Domínio Motor PD",
                "mensagem": str(e),
                "campo_afetado": "RATING/PD",
                "valor_observado": valor_obs,
                "limite_esperado": "VÁLIDO",
                "contraparte_id": cnpj
            })
            registro["RATING_FINAL"] = pd.NA
            registro["PD_FINAL"] = pd.NA
            registro["SCORE_TOTAL"] = pd.NA
            
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
            registro["RATING_FINAL"] = pd.NA
            registro["PD_FINAL"] = pd.NA
            registro["SCORE_TOTAL"] = pd.NA

        resultados.append(registro)

    if alertas_db:
        from relational.facts.fato_alerta_util import registrar_alertas_em_lote
        registrar_alertas_em_lote(alertas_db, run_id, context)

    df_processado = pd.DataFrame(resultados)

    if "DATA_CALCULO" in df_processado.columns and "DATA_ANALISE" not in df_processado.columns:
        df_processado["DATA_ANALISE"] = df_processado["DATA_CALCULO"]
    if "RATING_FINAL" not in df_processado.columns and "RATING_COPEL" in df_processado.columns:
        df_processado["RATING_FINAL"] = df_processado["RATING_COPEL"]
    if "MODELO_METODOLOGICO" not in df_processado.columns and "versao_ficha" in df_processado.columns:
        df_processado["MODELO_METODOLOGICO"] = df_processado["versao_ficha"]

    for col in ["ANALISE_ID", "DATA_ANALISE", "RATING_FINAL", "PD_FINAL", "SCORE_TOTAL", "CLASSE_RISCO", "MODELO_METODOLOGICO", "DATA_DEMONSTRACAO_FINANCEIRA", "SEGMENTO_PD", "TIPO_FICHA", "PATRIMONIO_LIQUIDO", "SITUACAO_DF", "SITUACAO_ANALISE", "CNPJ_RAIZ", "STATUS_CALCULO_PD"]:
        if col not in df_processado.columns:
            df_processado[col] = None

    rename_map = {
        "CNPJ": "CNPJ", "CNPJ_RAIZ": "CNPJ_RAIZ", "DATA_ANALISE": "DATA_ANALISE", "RATING_FINAL": "RATING",
        "PD_FINAL": "PD_PERCENTUAL", "SCORE_TOTAL": "SCORE", "CLASSE_RISCO": "CLASSE",
        "MODELO_METODOLOGICO": "MODELO", "DATA_DEMONSTRACAO_FINANCEIRA": "DATA_BALANCO_USADO",
        "SEGMENTO_PD": "SEGMENTO_METODOLOGICO_FICHA", "TIPO_FICHA": "TIPO_FICHA",
        "PATRIMONIO_LIQUIDO": "PATRIMONIO_LIQUIDO", "SITUACAO_DF": "SITUACAO_DF",
        "SITUACAO_ANALISE": "SITUACAO_ANALISE", "STATUS_CALCULO_PD": "STATUS_CALCULO_PD"
    }

    df_final = df_processado[[c for c in rename_map.keys() if c in df_processado.columns]].rename(columns=rename_map).copy()
    df_final["ETL_RUN_ID"] = run_id

    relational_dir = context.path("relational_facts") / "credito"
    relational_dir.mkdir(parents=True, exist_ok=True)
    escrever_conjunto_de_dados_silver(records=df_final.to_dict(orient="records"), output_dir=relational_dir, filename="fato_analise_credito")
    df_final.to_parquet(relational_dir / "fato_analise_credito.parquet", index=False)
    
    if erros_qualidade:
        df_erros = pd.DataFrame(erros_qualidade)
        erros_dir = context.path("silver") / "ctl_validacao_qualidade_credito"
        erros_dir.mkdir(parents=True, exist_ok=True)
        escrever_conjunto_de_dados_silver(records=df_erros.to_dict(orient="records"), output_dir=erros_dir, filename=f"pendencias_{run_id}")
        logger.info("Foram registradas %d pendências em ctl_validacao_qualidade_credito", len(erros_qualidade))

    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}