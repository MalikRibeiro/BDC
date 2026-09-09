"""Serviço de Carga Manual e Eventos de Negócio."""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from pathlib import Path

from app.context import AppContext
from common.json import validar_esquema_json
from common.json import ler_json
from common.identificadores import normalizar_cnpj
from common.datas import normalizar_data
from common.numeros import to_decimal_br
from domain.carga_manual.servico_repescagem import repescar_fichas_alteradas
from control.logger import obter_logger
from storage.escrever_dados import mesclar_conjunto_de_dados_prata_por_chave_de_negocio

def inserir_dados_carga_manual(context: AppContext) -> dict[str, Any]:
    run_id = f"MAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.governanca.carga_manual", Path("LOGS/atualizacoes_manuais") / f"{run_id}__carga_manual.log")
    
    input_dir = context.path("entradas") / "atualizacoes_manuais" / "pendentes"
    input_dir.mkdir(parents=True, exist_ok=True)

    arquivos = list(input_dir.glob("*.csv")) + list(input_dir.glob("*.xlsx"))
    if not arquivos:
        return {"run_id": run_id, "processados": 0, "status": "SEM_DADOS"}

    schema_path = context.path("control_schemas") / "schema_carga_manual.json"
    schema = ler_json(schema_path) if schema_path.exists() else None

    processados = []
    agora = datetime.now().isoformat(timespec="seconds")

    for arquivo in arquivos:
        try:
            if arquivo.suffix == ".csv":
                df = pd.read_csv(arquivo, sep=";", dtype=str).fillna("")
            else:
                df = pd.read_excel(arquivo, dtype=str).fillna("")

            df.columns = [str(c).strip() for c in df.columns]

            if "CNPJ" in df.columns:
                df["CNPJ"] = df["CNPJ"].astype(str).str.replace(r"[\t\'\"]", "", regex=True).str.strip()

            for col in df.columns:
                df[col] = df[col].astype(str).str.strip()
            
            df = df.replace('nan', '')
            
            df["CNPJ"] = df["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
            df = df.dropna(subset=["CNPJ"])

            registros = df.to_dict(orient="records")

            for idx, reg in enumerate(registros):
                
                if "VALOR_NOVO" in reg and pd.notna(reg["VALOR_NOVO"]):
                    try:
                        reg["VALOR_NOVO"] = float(str(reg["VALOR_NOVO"]).replace(",", "."))
                    except ValueError:
                        pass

                if schema:
                    try:
                        validar_esquema_json(reg, schema, f"Registro [{idx}] do arquivo {arquivo.name}")
                    except Exception as exc:
                        logger.warning("Registro %s inválido: %s. Ignorando.", idx, exc)
                        continue

                cnpj_14 = reg.get("CNPJ")
                    
                data_iso = normalizar_data(reg.get("DATA_DEMONSTRACAO_FINANCEIRA"))
                if data_iso is None:
                    logger.warning("Registro [%s] ignorado: Data da DF inválida.", idx)
                    continue

                valor_bruto = reg.get("VALOR_NOVO")
                numero = to_decimal_br(valor_bruto)
                valor_float = float(numero) if numero is not None else None

                novo_reg = reg.copy()
                novo_reg["CNPJ"] = cnpj_14
                novo_reg["DATA_DEMONSTRACAO_FINANCEIRA"] = data_iso
                
                campo_bruto = str(reg.get("CAMPO_AFETADO", "")).strip().upper()
                novo_reg["CAMPO_AFETADO"] = campo_bruto.replace(" ", "_")
                
                if valor_float is not None:
                    novo_reg["VALOR_NOVO"] = str(valor_float)
                elif pd.notna(valor_bruto):
                    novo_reg["VALOR_NOVO"] = str(valor_bruto).strip()
                else:
                    novo_reg["VALOR_NOVO"] = None
                    
                novo_reg["DATA_REGISTRO_SISTEMA"] = agora
                novo_reg["RUN_ID"] = run_id
                processados.append(novo_reg)

            target_dir = context.path("entradas") / "atualizacoes_manuais" / "processadas"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.replace(target_dir / arquivo.name)
            
        except Exception:
            logger.exception("Erro ao processar arquivo %s", arquivo.name)
            target_dir = context.path("entradas") / "atualizacoes_manuais" / "rejeitadas"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.replace(target_dir / arquivo.name)

    if processados:
            silver_dir = context.path("silver") / "governanca_carga_manual"
            
            mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
                records=processados,
                output_dir=silver_dir,
                filename="eventos_manuais_consolidados",
                business_keys=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "CAMPO_AFETADO"]
            )

            cnpjs_afetados = {reg["CNPJ"] for reg in processados if "CNPJ" in reg}
            repescar_fichas_alteradas(context, cnpjs_afetados, logger)

    logger.info("Carga manual concluída. %d eventos registrados.", len(processados))
    return {"run_id": run_id, "eventos_processados": len(processados), "status": "SUCESSO"}