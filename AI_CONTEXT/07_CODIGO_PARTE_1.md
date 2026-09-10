# CÓDIGO PARTE 1

Arquivos consolidados por afinidade de domínio, mantendo arquivos pequenos relacionados juntos.


# GRUPO: domain_services


---

## `src/domain/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/auditoria/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/auditoria/servico_auditoria.py`

- Linhas: 149
- SHA-256: `80d1095625535368c2212deeb935572661819c75ac28489e70e8c6ad38194fff`
- Classes: -
- Funções: registrar_inicio_pipeline, registrar_fim_pipeline, registrar_documento, registrar_linhagem_campos

```python
"""Serviços de Auditoria do Pipeline (§11.5 — Tabelas de Controle).

Registra cada execução do pipeline (ctl_run_pipeline) e cada documento
processado (ctl_documento) em tabelas persistentes.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from storage.escrever_dados import escrever_conjunto_de_dados_silver


LOGGER = logging.getLogger("bdc.auditoria")

def registrar_inicio_pipeline(
    run_id: str,
    etapas_planejadas: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o início de uma execução do pipeline."""
    registro = {
        "RUN_ID": run_id,
        "DT_INICIO": datetime.now().isoformat(timespec="seconds"),
        "DT_FIM": None,
        "STATUS_GERAL": "EM_EXECUCAO",
        "TOTAL_ETAPAS": etapas_planejadas,
        "ETAPAS_OK": 0,
        "ETAPAS_FALHA": 0,
        "VERSAO_SISTEMA": "BDC_v06",
    }
    LOGGER.info("Pipeline iniciado (run_id=%s).", run_id)
    return registro


def registrar_fim_pipeline(
    registro_inicio: dict[str, Any],
    etapas_ok: int,
    etapas_falha: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o fim de uma execução do pipeline e persiste em ctl_run_pipeline."""
    registro = registro_inicio.copy()
    registro["DT_FIM"] = datetime.now().isoformat(timespec="seconds")
    registro["STATUS_GERAL"] = "SUCESSO" if etapas_falha == 0 else "PARCIAL"
    registro["ETAPAS_OK"] = etapas_ok
    registro["ETAPAS_FALHA"] = etapas_falha

    control_dir.mkdir(parents=True, exist_ok=True)

    ctl_path = control_dir / "ctl_run_pipeline.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    csv_path = control_dir / "ctl_run_pipeline.csv"
    df_combined.to_csv(csv_path, index=False, encoding="utf-8-sig", sep=";")

    LOGGER.info(
        "Pipeline finalizado (run_id=%s). Status=%s. OK=%d, Falha=%d.",
        registro["RUN_ID"], registro["STATUS_GERAL"],
        etapas_ok, etapas_falha,
    )
    return registro

def registrar_documento(
    documento_id: str,
    run_id: str,
    arquivo_origem: str,
    hash_arquivo: str | None,
    tipo_ficha: str,
    status_classificacao: str,
    status_extracao: str,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra um documento processado na tabela ctl_documento (append-only)."""
    registro = {
        "DOCUMENTO_ID": documento_id,
        "RUN_ID": run_id,
        "ARQUIVO_ORIGEM": arquivo_origem,
        "HASH_ARQUIVO": hash_arquivo,
        "TIPO_FICHA": tipo_ficha,
        "STATUS_CLASSIFICACAO": status_classificacao,
        "STATUS_EXTRACAO": status_extracao,
        "DT_PROCESSAMENTO": datetime.now().isoformat(timespec="seconds"),
    }

    control_dir.mkdir(parents=True, exist_ok=True)

    ctl_path = control_dir / "ctl_documento.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    LOGGER.info(
        "Documento registrado: %s (tipo=%s, status=%s).",
        documento_id, tipo_ficha, status_extracao,
    )
    return registro

def registrar_linhagem_campos(
    documento_id: str,
    run_id: str,
    campos_metadata: list[dict[str, Any]],
    control_dir: Path,
) -> None:
    """Registra a linhagem (aba, célula, método) de cada campo extraído."""
    if not campos_metadata:
        return

    registros = []
    dt_proc = datetime.now().isoformat(timespec="seconds")
    for cm in campos_metadata:
        registros.append({
            "DOCUMENTO_ID": documento_id,
            "RUN_ID": run_id,
            "CAMPO": cm.get("campo"),
            "ABA_ORIGEM": cm.get("aba_origem"),
            "CELULA_ORIGEM": cm.get("celula_origem"),
            "METODO_EXTRACAO": cm.get("metodo"),
            "VALOR_EXTRAIDO": str(cm.get("valor"))[:255] if cm.get("valor") is not None else None,
            "DT_PROCESSAMENTO": dt_proc,
        })

    control_dir.mkdir(parents=True, exist_ok=True)
    ctl_path = control_dir / "ctl_campo_origem.parquet"
    
    df_new = pd.DataFrame(registros)
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_parquet(ctl_path, index=False)
    LOGGER.debug("Registrada linhagem de %d campos para documento %s.", len(registros), documento_id)
```


---

## `src/domain/cadastro/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/cadastro/servico_bureau.py`

- Linhas: 103
- SHA-256: `123331af3355a15dbed554e4025d48bc236a6c78504a019f3f03390dd1a899e0`
- Classes: -
- Funções: inserir_dados_bureau, _gravar_silver_vazia

```python
"""Serviço de Ingestão e Persistência do Bureau RISK3."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from pathlib import Path
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def inserir_dados_bureau(context: AppContext) -> dict[str, Any]:
    run_id = f"BUR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.bureau", Path("LOGS/ingestao") / f"{run_id}__ingestao_bureau.log")

    path_enq = context.path("relational_configs")
    arquivos = list(path_enq.glob("enquadramento_consumidores_*.csv"))
    if not arquivos:
        logger.warning("Nenhum enquadramento encontrado para guiar o Bureau.")
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "SEM_DADOS_ENQUADRAMENTO"}
        
    try:
        df_enq = pd.read_csv(max(arquivos, key=lambda f: f.stat().st_mtime), sep=",", dtype={"CNPJ": str})
    except Exception as e:
        logger.critical("Falha ao ler arquivo de enquadramento: %s. Prosseguindo com DataFrame vazio.", e)
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "FALHA_LEITURA_ENQUADRAMENTO"}
    
    cnpjs_enquadrados = df_enq["CNPJ"].dropna().unique().tolist()
    
    path_contratos = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_contratos.exists():
        path_contratos = context.path("silver") / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
        
    if path_contratos.exists():
        df_contratos = pd.read_parquet(path_contratos)
        status_excluidos = ["CANCELADO", "DISTRATADO", "ENCERRADO", "REJEITADO", "INATIVO"]
        if "STATUS" in df_contratos.columns:
            df_ativos = df_contratos[~df_contratos["STATUS"].astype(str).str.upper().isin(status_excluidos)]
        else:
            df_ativos = df_contratos
        cnpjs_ativos = set(df_ativos["CNPJ"].dropna().unique())
        cnpjs_alvo = [c for c in cnpjs_enquadrados if c in cnpjs_ativos]
    else:
        logger.warning("Base de contratos correntes não encontrada. Prosseguindo sem filtro de atividade.")
        cnpjs_alvo = cnpjs_enquadrados

    logger.info("Total de CNPJs elegíveis para consulta RISK3 (Enquadrados e Ativos): %d", len(cnpjs_alvo))
    
    if not cnpjs_alvo:
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "NENHUM_CLIENTE_ELEGIVEL"}

    try:
        from services.connectors.risk3_connector import buscar_bureau_risk3
        df_bureau = buscar_bureau_risk3(cnpjs_alvo, context)
    except Exception as e:
        logger.critical("API RISK3 indisponível ou falha de conexão: %s. Prosseguindo com Silver vazia.", e)
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "FALHA_API_RISK3"}

    if df_bureau.empty:
        logger.warning("Consulta RISK3 retornou DataFrame vazio.")
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "SEM_RETORNO_API"}

    bronze_dir = context.path("bronze") / "snapshots_fontes" / "bureau"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    df_bureau.to_parquet(bronze_dir / f"raw_bureau_{run_id}.parquet", index=False)

    df_silver = df_bureau[df_bureau["STATUS"] == "SUCESSO"].copy()
    
    if df_silver.empty:
        logger.warning("Nenhum registro com STATUS=SUCESSO retornado pelo Bureau.")
        _gravar_silver_vazia(context, run_id)
        return {"run_id": run_id, "status": "FALHA_OU_BLOQUEIO_DE_REDE"}
        
    df_silver["RUN_ID"] = run_id
    df_silver["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
    
    silver_dir = context.path("silver") / "fato_bureau_silver"
    escrever_conjunto_de_dados_silver(
        records=df_silver.to_dict(orient="records"), 
        output_dir=silver_dir, 
        filename="fato_bureau_silver"
    )

    logger.info("Ingestão do Bureau concluída. %d registros na Silver.", len(df_silver))
    return {"run_id": run_id, "status": "SUCESSO", "linhas": len(df_silver)}


def _gravar_silver_vazia(context: AppContext, run_id: str) -> None:
    silver_dir = context.path("silver") / "fato_bureau_silver"
    silver_dir.mkdir(parents=True, exist_ok=True)
    df_vazio = pd.DataFrame(columns=[
        "CNPJ", "SCORE_BUREAU", "RATING_BUREAU", "PD_BUREAU",
        "RESTRITIVOS", "DATA_CONSULTA", "DATA_VALIDADE",
        "STATUS", "RAW_DATA", "RUN_ID", "DT_PROCESSAMENTO"
    ])
    df_vazio.to_parquet(silver_dir / "fato_bureau_silver.parquet", index=False)
```


---

## `src/domain/cadastro/servico_receita.py`

- Linhas: 144
- SHA-256: `0b33c549ce3a8b95dd077f6cf077b724822d494bfce09c99e23b514b5a745b35`
- Classes: ReceitaIngestionError
- Funções: _listar_cnpjs_de_entrada, _salvar_instantaneo_bruto, inserir_dados_receita

```python
"""Serviço de ingestão e validação cadastral da Receita Federal."""

from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from domain.enums import StatusAlerta
from relational.facts.fato_alerta_util import registrar_alerta
from services.connectors.receita_connector import buscar_receita_dados_lote
from storage.escrever_dados import escrever_conjunto_de_dados_silver

LOGGER = logging.getLogger(__name__)

class ReceitaIngestionError(Exception):
    """Exceção para falhas na ingestão da base da Receita Federal."""

def _listar_cnpjs_de_entrada(context: AppContext) -> list[str]:
    """Lê TODOS os CNPJs das Fichas e dos Contratos para garantir cobertura total."""
    cnpjs = set()
    silver_dir = context.path("silver")

    for segmento in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        path = silver_dir / segmento / f"{segmento}.parquet"
        if path.exists():
            df = pd.read_parquet(path)
            if "CNPJ" in df.columns:
                cnpjs.update(df["CNPJ"].dropna().astype(str).str.strip().tolist())

    path_contratos = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if path_contratos.exists():
        df_contratos = pd.read_parquet(path_contratos)
        if "CNPJ" in df_contratos.columns:
            cnpjs.update(df_contratos["CNPJ"].dropna().astype(str).str.strip().tolist())

    from common.identificadores import normalizar_cnpj
    cnpjs_limpos = []
    for c in cnpjs:
        resultado = normalizar_cnpj(c)
        if resultado.valido:
            cnpjs_limpos.append(resultado.cnpj)

    return list(set(cnpjs_limpos))

def _salvar_instantaneo_bruto(context: AppContext, payload: list[dict[str, Any]]) -> Path:
    bronze_dir = context.path("bronze") / "snapshots_fontes" / "receita"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    filename = f"raw_receita_{date.today().strftime('%Y%m%d')}.json"
    target = bronze_dir / filename
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target

from control.logger import obter_logger

def inserir_dados_receita(context: AppContext) -> dict[str, Any]:
    run_id = f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.receita", Path("LOGS/ingestao") / f"{run_id}__ingestao_receita.log")

    cnpjs = _listar_cnpjs_de_entrada(context)
    if not cnpjs:
        logger.warning("Nenhum CNPJ encontrado nas bases da Silver para consulta na Receita.")
        return {"run_id": run_id, "linhas_processadas": 0, "alertas_gerados_cad001": 0, "status": "SEM_DADOS"}

    logger.info("Iniciando consulta na BrasilAPI para %d CNPJ(s). Pode levar alguns minutos (Cache ativo)...", len(cnpjs))
    df_receita = buscar_receita_dados_lote(cnpjs, context, logger)
    
    if df_receita.empty:
        logger.warning("Consulta da Receita retornou DataFrame vazio.")
        return {"run_id": run_id, "linhas_processadas": 0, "alertas_gerados_cad001": 0, "status": "SEM_DADOS"}

    payload = df_receita.to_dict(orient="records")
    _salvar_instantaneo_bruto(context, payload)

    df_receita = df_receita.drop_duplicates(subset=["CNPJ"], keep="last").reset_index(drop=True)
    df_receita["RUN_ID"] = run_id
    df_receita["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

    alertas: list[dict[str, Any]] = []
    for _, row in df_receita.iterrows():
        situacao = str(row.get("SITUACAO_CADASTRAL") or "").strip().upper()
        if situacao and situacao != "ATIVA" and situacao != "NONE":
            alertas.append({
                "CODIGO": "CAD_001",
                "CNPJ": row.get("CNPJ"),
                "MENSAGEM": f"CNPJ com situação cadastral irregular: {situacao}.",
                "SEVERIDADE": "ALTA",
                "RUN_ID": run_id,
                "DT_DETECCAO": datetime.now().isoformat(timespec="seconds"),
                "STATUS_ALERTA": StatusAlerta.ABERTO.value,
            })
            
            registrar_alerta(
                codigo="CAD_001",
                severidade="ALTO",
                regra="Situação Cadastral Irregular",
                mensagem=f"CNPJ com situação cadastral irregular: {situacao}.",
                campo_afetado="SITUACAO_CADASTRAL",
                valor_observado=situacao,
                limite_esperado="ATIVA",
                contraparte_id=row.get("CNPJ"),
                run_id=run_id,
                context=context
            )

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        escrever_conjunto_de_dados_silver(
            records=df_alertas.to_dict(orient="records"),
            output_dir=context.path("silver") / "alertas_credito",
            filename=f"alertas_cadastrais_receita_{run_id}",
        )

    silver_dir = context.path("silver") / "receita_silver"
    escrever_conjunto_de_dados_silver(
        records=df_receita.to_dict(orient="records"),
        output_dir=silver_dir,
        filename=f"receita_cadastral_silver_{run_id}",
    )

    import shutil
    latest_path = silver_dir / "receita_cadastral_silver.parquet"
    versioned_path = silver_dir / f"receita_cadastral_silver_{run_id}.parquet"
    if latest_path.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(latest_path, silver_dir / f"receita_cadastral_silver_HIST_{ts}.parquet")
    if versioned_path.exists():
        shutil.copy2(versioned_path, latest_path)

    resumo = {
        "run_id": run_id,
        "linhas_processadas": int(len(df_receita)),
        "alertas_gerados_cad001": len(alertas),
        "status": "SUCESSO",
    }
    logger.info("Ingestão da Receita concluída: %s", resumo)
    return resumo
```


---

## `src/domain/carga_manual/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/carga_manual/servico_carga_manual.py`

- Linhas: 127
- SHA-256: `2623b4d64bd402257afa4ef3733a078a15d77d1ed14dd958e50d8657b314ef6b`
- Classes: -
- Funções: inserir_dados_carga_manual

```python
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
```


---

## `src/domain/carga_manual/servico_repescagem.py`

- Linhas: 73
- SHA-256: `e376fcca61814724ac5a172bdc7765a8f95fb3dd67b804d44ce0e9079f5be7e8`
- Classes: -
- Funções: repescar_fichas_alteradas

```python
import pandas as pd
import shutil
import logging
from pathlib import Path
from app.context import AppContext

def repescar_fichas_alteradas(context: AppContext, cnpjs_alterados: set[str], logger: logging.Logger | None = None) -> None:
    """Busca o arquivo original na pasta de processados e devolve para pendentes."""
    if not cnpjs_alterados:
        return
        
    if logger is None:
        logger = logging.getLogger("bdc.governanca.repescagem")
    
    silver_path_com = context.path("silver") / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    silver_path_cons = context.path("silver") / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet"
    
    df_silver_com = pd.read_parquet(silver_path_com) if silver_path_com.exists() else pd.DataFrame()
    df_silver_cons = pd.read_parquet(silver_path_cons) if silver_path_cons.exists() else pd.DataFrame()
    
    from common.identificadores import normalizar_cnpj
    if not df_silver_com.empty and "CNPJ" in df_silver_com.columns:
        df_silver_com["CNPJ"] = df_silver_com["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    if not df_silver_cons.empty and "CNPJ" in df_silver_cons.columns:
        df_silver_cons["CNPJ"] = df_silver_cons["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    
    repescados = 0
    for cnpj_raw in cnpjs_alterados:
        resultado = normalizar_cnpj(cnpj_raw)
        if not resultado.valido:
            continue
        cnpj = resultado.cnpj
        match_com = df_silver_com[df_silver_com["CNPJ"] == cnpj] if not df_silver_com.empty else pd.DataFrame()
        match_cons = df_silver_cons[df_silver_cons["CNPJ"] == cnpj] if not df_silver_cons.empty else pd.DataFrame()
        
        if not match_com.empty:
            nome_arquivo = match_com.iloc[-1].get("arquivo_nome")
            if nome_arquivo:
                proc_dir = context.path("input_fichas_comercializadoras_processadas")
                pend_dir = context.path("input_reprocessamento_comercializadoras_pendentes")
                pend_dir.mkdir(parents=True, exist_ok=True)
                arq_proc = proc_dir / nome_arquivo
                arq_pend = pend_dir / nome_arquivo
                
                if not arq_pend.exists() and arq_proc.exists():
                    shutil.copy2(arq_proc, arq_pend)
                    logger.info("[REPESCAGEM] Ficha comercializadora '%s' devolvida para a fila (CNPJ: %s).", nome_arquivo, cnpj)
                    repescados += 1
                elif arq_pend.exists():
                    logger.info("[REPESCAGEM] Ficha comercializadora '%s' já estava na fila de pendentes (CNPJ: %s).", nome_arquivo, cnpj)
                elif not arq_proc.exists():
                    logger.warning("[REPESCAGEM] Arquivo original '%s' não encontrado em processados (CNPJ: %s).", nome_arquivo, cnpj)
                    
        elif not match_cons.empty:
            nome_arquivo = match_cons.iloc[-1].get("arquivo_nome")
            if nome_arquivo:
                proc_dir = context.path("input_fichas_consumidores_processadas")
                pend_dir = context.path("input_reprocessamento_consumidores_pendentes")
                pend_dir.mkdir(parents=True, exist_ok=True)
                arq_proc = proc_dir / nome_arquivo
                arq_pend = pend_dir / nome_arquivo
                
                if not arq_pend.exists() and arq_proc.exists():
                    shutil.copy2(arq_proc, arq_pend)
                    logger.info("[REPESCAGEM] Ficha consumidor '%s' devolvida para a fila (CNPJ: %s).", nome_arquivo, cnpj)
                    repescados += 1
                elif arq_pend.exists():
                    logger.info("[REPESCAGEM] Ficha consumidor '%s' já estava na fila de pendentes (CNPJ: %s).", nome_arquivo, cnpj)
                elif not arq_proc.exists():
                    logger.warning("[REPESCAGEM] Arquivo original '%s' não encontrado em processados (CNPJ: %s).", nome_arquivo, cnpj)
                    
    if repescados > 0:
        logger.info("[REPESCAGEM] Sucesso! %d fichas enfileiradas para reprocessamento imediato.", repescados)
```


---

## `src/domain/consumidores/classificacao.py`

- Linhas: 176
- SHA-256: `c71546c294a4ce832954903d31105a3788db0b80246891f6afeff72769c2be5c`
- Classes: ClassificacaoDocumental
- Funções: _esta_vazio, _tem_demonstracoes_financeiras, _avaliar_confianca, classificar_consumidor, criar_classificacao_registro

```python
"""Serviço de classificação documental de consumidores.

Determina o tipo de análise exigida (detalhada ou simplificada)
com base no volume contratado, conforme planejamento v1.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


LIMIAR_MWM_DETALHADO = 5.0
VERSAO_REGRA_ATUAL = "v1.2"


@dataclass
class ClassificacaoDocumental:
    """Resultado da classificação documental de um consumidor."""

    tipo_consumidor: str
    presenca_df: bool
    tipo_analise_exigida: str
    versao_layout: str    
    campos_obrigatorios: list[str]   
    confianca_classificacao: str
    compatibilidade_ficha_segmento: bool
    campos_df_nao_aplicavel: list[str]


CAMPOS_DF_COMPLETA = [
    "ATIVO_CIRCULANTE", "ATIVO_CIRCULANTE_FINANCEIRO", "ATIVO_TOTAL",
    "PASSIVO_CIRCULANTE", "PASSIVO_CIRCULANTE_FINANCEIRO",
    "PASSIVO_NAO_CIRCULANTE_FINANCEIRO", "PATRIMONIO_LIQUIDO",
    "LUCROS_ACUMULADOS", "RESERVA_DE_LUCROS", "VENDAS_LIQUIDAS",
    "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
]

CAMPOS_OBRIGATORIOS_DETALHADA = [
    "CNPJ", "EMPRESA", "DATA_DEMONSTRACAO_FINANCEIRA",
    "PATRIMONIO_LIQUIDO", "ATIVO_CIRCULANTE", "ATIVO_TOTAL",
    "PASSIVO_CIRCULANTE", "LUCRO_LIQUIDO",
    "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
    "FCO", "ROA", "ROE", "PROBABILIDADE_DEFAULT",
]

CAMPOS_OBRIGATORIOS_SIMPLIFICADA = [
    "CNPJ", "EMPRESA", "SCORE_BUREAU",
]


def _esta_vazio(value: Any) -> bool:
    """Indica se o valor deve ser tratado como vazio."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _tem_demonstracoes_financeiras(record: dict[str, Any]) -> bool:
    """Verifica se a ficha possui demonstrações financeiras preenchidas."""
    campos_presentes = 0
    for campo in CAMPOS_DF_COMPLETA:
        val = record.get(campo)
        if not _esta_vazio(val) and str(val).upper() != "NAO_APLICAVEL":
            campos_presentes += 1

    return campos_presentes >= len(CAMPOS_DF_COMPLETA) * 0.5


def _avaliar_confianca(
    record: dict[str, Any],
    tipo_consumidor: str,
    presenca_df: bool,
) -> str:
    """Avalia a confiança da classificação com base na consistência dos dados."""
    problemas = 0

    if tipo_consumidor == ">=5MWm" and not presenca_df:
        problemas += 2

    if _esta_vazio(record.get("CNPJ")):
        problemas += 1

    if _esta_vazio(record.get("EMPRESA")):
        problemas += 1

    if problemas == 0:
        return "alta"
    elif problemas == 1:
        return "media"
    else:
        return "baixa"


def classificar_consumidor(
    record: dict[str, Any],
    versao_layout: str,
    volume_mwm: float | None = None,
) -> ClassificacaoDocumental:
    """Classifica um consumidor conforme a metodologia aplicável.

    Args:
        record: Registro normalizado extraído da ficha.
        versao_layout: Versão do layout utilizado (e.g. "v3").
        volume_mwm: Volume contratado em MWm. Se None, tenta obter do record.

    Returns:
        ClassificacaoDocumental com todos os campos preenchidos.
    """
    if volume_mwm is None:
        volume_mwm = record.get("VOLUME_CONTRATADO")
        if volume_mwm is not None:
            try:
                volume_mwm = float(volume_mwm)
            except (ValueError, TypeError):
                volume_mwm = None

    if volume_mwm is not None and volume_mwm >= LIMIAR_MWM_DETALHADO:
        tipo_consumidor = ">=5MWm"
    elif volume_mwm is not None and volume_mwm < LIMIAR_MWM_DETALHADO:
        tipo_consumidor = "<5MWm"
    else:
        presenca_df = _tem_demonstracoes_financeiras(record)
        tipo_consumidor = ">=5MWm" if presenca_df else "<5MWm"

    presenca_df = _tem_demonstracoes_financeiras(record)

    if tipo_consumidor == ">=5MWm":
        tipo_analise = "detalhada"
        campos_obrigatorios = list(CAMPOS_OBRIGATORIOS_DETALHADA)
    else:
        tipo_analise = "simplificada"
        campos_obrigatorios = list(CAMPOS_OBRIGATORIOS_SIMPLIFICADA)

    campos_nao_aplicavel: list[str] = []
    if tipo_consumidor == "<5MWm":
        for campo in CAMPOS_DF_COMPLETA:
            val = record.get(campo)
            if _esta_vazio(val) or str(val).upper() == "NAO_APLICAVEL":
                campos_nao_aplicavel.append(campo)

    if tipo_consumidor == ">=5MWm":
        compativel = presenca_df
    else:
        compativel = not _esta_vazio(record.get("SCORE_BUREAU"))

    confianca = _avaliar_confianca(record, tipo_consumidor, presenca_df)

    return ClassificacaoDocumental(
        tipo_consumidor=tipo_consumidor,
        presenca_df=presenca_df,
        tipo_analise_exigida=tipo_analise,
        versao_layout=versao_layout,
        campos_obrigatorios=campos_obrigatorios,
        confianca_classificacao=confianca,
        compatibilidade_ficha_segmento=compativel,
        campos_df_nao_aplicavel=campos_nao_aplicavel,
    )


def criar_classificacao_registro(
    classificacao: ClassificacaoDocumental,
) -> dict[str, Any]:
    """Converte a classificação documental em dict para o silver_record."""
    return {
        "tipo_consumidor": classificacao.tipo_consumidor,
        "presenca_df": classificacao.presenca_df,
        "tipo_analise_exigida": classificacao.tipo_analise_exigida,
        "versao_layout": classificacao.versao_layout,
        "campos_obrigatorios": ",".join(classificacao.campos_obrigatorios),
        "confianca_classificacao": classificacao.confianca_classificacao,
        "compatibilidade_ficha_segmento": classificacao.compatibilidade_ficha_segmento,
        "campos_df_nao_aplicavel": ",".join(classificacao.campos_df_nao_aplicavel),
    }
```


---

## `src/domain/contrapartes/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/contrapartes/segmentacao.py`

- Linhas: 41
- SHA-256: `1a724984a8ba995e174389248435c0c5bef29697b6982010fccf0e198ffc6ed1`
- Classes: -
- Funções: definir_segmento_metodologico

```python
"""Segmentação metodológica da contraparte para cálculo de PD."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from common.numeros import to_float_br

def definir_segmento_metodologico(
    registro: dict[str, Any],
) -> str:
    """Define o segmento metodológico da contraparte."""
    tipo_ficha = normalizar_texto(registro.get("TIPO_FICHA"))
    
    if tipo_ficha == "COMERCIALIZADORA":
        tipo_comercializadora = normalizar_texto(registro.get("TIPO_COMERCIALIZADORA"))
        if tipo_comercializadora == "CPURA":
            return "CPURA"

        if tipo_comercializadora == "CGRUPO":
            return "CGRUPO"

        raise ValueError(
            "Comercializadora sem TIPO_COMERCIALIZADORA válido."
        )

    if tipo_ficha == "CONSUMIDOR":
        volume_mwm = to_float_br(registro.get("VOLUME_ENQUADRAMENTO_MWM"))
        
        if volume_mwm is None:
            return "NAO_ENQUADRADO"
            
        if volume_mwm >= 5.0:
            return "CONSUMIDOR_GT_5"
        else:
            return "CONSUMIDOR_LE_5"

    raise ValueError(
        f"TIPO_FICHA inválido para segmentação: {tipo_ficha!r}"
    )
```


---

## `src/domain/contrapartes/servico_enquadramento.py`

- Linhas: 130
- SHA-256: `eea54a1d6968964310e90eb4bb0103175d901ea983de7e88de71071845c2ad42`
- Classes: -
- Funções: calcular_enquadramento_consumidor, _salvar_enquadramento

```python
"""Serviço de cálculo do volume de enquadramento (≥ 5 MWm) para consumidores."""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Any

from app.context import AppContext


def calcular_enquadramento_consumidor(
    competencia_base: str,
    context: AppContext,
) -> pd.DataFrame:
    """
    Lê os contratos normalizados da Silver do Denodo, calcula o maior volume mensal
    simultâneo por raiz de CNPJ (Matriz + Filiais) e retorna a base consolidada
    de enquadramento propagada para todos os CNPJs completos.
    """
    silver_dir = context.path("silver") / "denodo_contratos_padronizados"
    parquet_path = silver_dir / f"contratos_correntes_{competencia_base}.parquet"

    if not parquet_path.exists():
        df_vazio = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"])
        _salvar_enquadramento(context, competencia_base, df_vazio)
        return df_vazio

    df_contratos = pd.read_parquet(parquet_path)

    if df_contratos.empty:
        df_enquadramento = pd.DataFrame(
            columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"]
        )
        _salvar_enquadramento(context, competencia_base, df_enquadramento)
        return df_enquadramento

    status_excluidos = ["CANCELADO", "DISTRATADO", "ENCERRADO", "REJEITADO", "INATIVO"]
    if "STATUS" in df_contratos.columns:
        df_contratos["STATUS_UP"] = (
            df_contratos["STATUS"]
            .astype(str)
            .str.upper()
        )

        df_ativos = df_contratos[
            ~df_contratos["STATUS_UP"].isin(status_excluidos)
        ].copy()
    else:
        df_ativos = df_contratos.copy()

    if df_ativos.empty:
        df_enquadramento = pd.DataFrame(
            columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"]
        )
        _salvar_enquadramento(context, competencia_base, df_enquadramento)
        return df_enquadramento

    if "CNPJ_RAIZ" not in df_ativos.columns:
        from common.identificadores import normalizar_cnpj
        df_ativos["CNPJ_RAIZ"] = df_ativos["CNPJ"].apply(lambda x: normalizar_cnpj(x).raiz if normalizar_cnpj(x).valido else None)

    col_ano = next((c for c in df_ativos.columns if c.upper() == "ANO"), None)
    col_mes = next((c for c in df_ativos.columns if c.upper() == "MES"), None)

    col_vol = next(
        (c for c in df_ativos.columns if c.upper() in {"VOLUME_CONTRATADO_MENSAL_MWM", "VOLUME_MWM"}),
        None,
    )
    if col_vol is None:
        raise KeyError(
            "Coluna de volume (VOLUME_CONTRATADO_MENSAL_MWM ou VOLUME_MWM) "
            "não encontrada na base de contratos."
        )
    if col_vol != "VOLUME_CONTRATADO_MENSAL_MWM":
        df_ativos = df_ativos.rename(columns={col_vol: "VOLUME_CONTRATADO_MENSAL_MWM"})

    if "COMPETENCIA" not in df_ativos.columns and col_ano and col_mes:
        df_ativos["COMPETENCIA"] = (
            df_ativos[col_ano].astype(str).str.replace(r"\.0$", "", regex=True)
            + df_ativos[col_mes].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(2)
        )

    df_mensal = (
        df_ativos.groupby(
            ["CNPJ_RAIZ", "COMPETENCIA"],
            as_index=False,
        )["VOLUME_CONTRATADO_MENSAL_MWM"]
        .sum()
        .rename(
            columns={
                "VOLUME_CONTRATADO_MENSAL_MWM": "VOLUME_CONSOLIDADO_MENSAL"
            }
        )
    )

    df_enq_raiz = (
        df_mensal.groupby(
            "CNPJ_RAIZ",
            as_index=False,
        )["VOLUME_CONSOLIDADO_MENSAL"]
        .max()
        .rename(
            columns={
                "VOLUME_CONSOLIDADO_MENSAL": "VOLUME_ENQUADRAMENTO_MWM"
            }
        )
    )

    LIMIAR_MWM = 5.0

    df_enq_raiz["POSSUI_PELO_MENOS_5_MWM"] = (
        df_enq_raiz["VOLUME_ENQUADRAMENTO_MWM"] >= LIMIAR_MWM
    )

    df_enquadramento = pd.merge(
        df_ativos[["CNPJ", "CNPJ_RAIZ"]].drop_duplicates(),
        df_enq_raiz,
        on="CNPJ_RAIZ",
        how="left",
    ).drop(columns=["CNPJ_RAIZ"])

    _salvar_enquadramento(context, competencia_base, df_enquadramento)
    return df_enquadramento

def _salvar_enquadramento(context: AppContext, competencia_base: str, df: pd.DataFrame) -> None:
    relational_dir = context.path("relational_configs")
    relational_dir.mkdir(parents=True, exist_ok=True)
    output_path = relational_dir / f"enquadramento_consumidores_{competencia_base}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
```


---

## `src/domain/contratos/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/contratos/servico_contratos_denodo.py`

- Linhas: 159
- SHA-256: `b0d3d6bde2570301062e6e93991187e21967226b13fd91ba60a0b337a1e6d3e3`
- Classes: -
- Funções: aplicar_regras_negocio_pandas, calcular_horas, processar_contratos_denodo

```python
"""Serviço oficial de ingestão de Contratos Correntes do Denodo."""

from __future__ import annotations

import logging
import calendar
import pandas as pd

from datetime import datetime
from pathlib import Path
from typing import Any

from app.context import AppContext
from common.dados import normalizar_coluna_cnpj
from services.connectors.denodo_connector import buscar_denodo
from storage.escrever_dados import escrever_conjunto_de_dados_silver

LOGGER = logging.getLogger(__name__)

def aplicar_regras_negocio_pandas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    col_cnpj = "contraparte_cnpj" if "contraparte_cnpj" in df.columns else "cnpj"
    if col_cnpj in df.columns:
        df = normalizar_coluna_cnpj(df, coluna_origem=col_cnpj)
        if "STATUS_CNPJ" not in df.columns and "CNPJ_STATUS" in df.columns:
            df["STATUS_CNPJ"] = df["CNPJ_STATUS"]
    else:
        df["CNPJ"]       = None
        df["CNPJ_RAIZ"]  = None
        df["STATUS_CNPJ"] = "CNPJ_AUSENTE"
        
    colunas_numericas = ["ano", "mes", "id_parte", "id_tipo_contrato", "id_contraparte", "id_status", "quant_contratada"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    def calcular_horas(row):
        try:
            ano = int(row.get("ano", 0))
            mes = int(row.get("mes", 0))
            if 2000 <= ano <= 2100 and 1 <= mes <= 12:
                return calendar.monthrange(ano, mes)[1] * 24
        except:
            pass
        return 730

    df["HORAS_MES"] = df.apply(calcular_horas, axis=1)
    df["VOLUME_MWH"] = df["quant_contratada"]
    df["VOLUME_MWM"] = df["quant_contratada"] / df["HORAS_MES"]

    col_in = "suprimento_inicio" if "suprimento_inicio" in df.columns else ("vigencia_inicio" if "vigencia_inicio" in df.columns else "inicio_suprimento")
    df["DT_IN_TEMP"] = pd.to_datetime(df.get(col_in), errors="coerce")
    hoje = pd.Timestamp("today").normalize()
    filtro_futuros = (df["DT_IN_TEMP"] > hoje)

    filtro = (
        (df.get("ano", 0) >= 2020) & 
        (df.get("parte_apelido", "") == "COPEL COM") &
        (df.get("contraparte_apelido", "") != "COPEL COM - Transferência de energia") &
        (df.get("id_parte", 0) == 297) &
        (df.get("id_tipo_contrato", 0).isin([1, 3, 33, 90])) & 
        (df.get("contrato_vinculado", "").isna() | (df.get("contrato_vinculado", "") == "")) &
        ((~df.get("id_status", 0).isin([0, 1, 4, 5, 6, 9, 10, 11])) | filtro_futuros) & 
        (df.get("quant_contratada", 0) > 0)
    )
    
    if "ncdempresaproprietaria" in df.columns: filtro = filtro & (df["ncdempresaproprietaria"] == 297)
    if "id_contraparte" in df.columns: filtro = filtro & (df["id_contraparte"] != 9057)
    filtro = filtro & (df["STATUS_CNPJ"] == "CNPJ_VALIDO")

    return df.loc[filtro].drop(columns=["DT_IN_TEMP"]).copy()

def processar_contratos_denodo(context: AppContext) -> dict[str, Any]:
    run_id = f"CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.contratos")

    try:
        input_dir = context.path("entradas") / "contratos_denodo"
        arquivos_locais = list(input_dir.glob("*.csv"))
        
        df_raw = pd.DataFrame()
        if arquivos_locais:
            arquivo = max(arquivos_locais, key=lambda f: f.stat().st_mtime)
            logger.info("Lendo contratos de arquivo local: %s (Ignorando API para evitar timeout da rede)", arquivo.name)
            try:
                df_raw = pd.read_csv(arquivo, sep=",", dtype=str)
                if len(df_raw.columns) < 5:
                    df_raw = pd.read_csv(arquivo, sep=";", dtype=str)
            except Exception:
                df_raw = pd.read_csv(arquivo, sep=";", dtype=str)
        else:
            logger.info("Iniciando extração da view vwi_exportar_contrato via REST.")
            colunas_necessarias = "ano,mes,ncdempresaproprietaria,id_parte,id_tipo_contrato,id_contraparte,contrato_vinculado,id_status,quant_contratada,quant_sazonalizada,parte_apelido,contraparte_apelido,contraparte_cnpj,nome_contrato,suprimento_inicio,suprimento_termino,status"
            parametros_api = {
                "$select": colunas_necessarias, 
                "$filter": "ano >= 2024 AND parte_apelido = 'COPEL COM' AND id_parte = 297 AND ncdempresaproprietaria = 297"
            }
            df_raw = buscar_denodo("vwi_exportar_contrato", params=parametros_api)
        
        if df_raw.empty: return {"run_id": run_id, "status": "SEM_DADOS", "linhas": 0}

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "denodo"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        df_raw.to_parquet(bronze_dir / f"raw_contratos_{run_id}.parquet", index=False)

        df_silver = aplicar_regras_negocio_pandas(df_raw)
        df_silver.columns = [str(c).strip().upper() for c in df_silver.columns]
        
        rename_map = {
            "NOME_CONTRATO": "CONTRATO", 
            "SUPRIMENTO_INICIO": "VIGENCIA_INICIO", 
            "SUPRIMENTO_TERMINO": "VIGENCIA_FIM"
        }
        df_silver = df_silver.rename(columns=rename_map)
        
        df_silver["QUANT_CONTRATADA"] = df_silver["QUANT_CONTRATADA"]
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = df_silver["VOLUME_MWM"]
        df_silver["VOLUME_MWH_ORIGINAL"] = df_silver["VOLUME_MWH"]
        df_silver["COMPETENCIA"] = df_silver["ANO"].astype(str).str.replace(r"\.0", "", regex=True) + df_silver["MES"].astype(str).str.replace(r"\.0", "", regex=True).str.zfill(2)
        
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = pd.to_numeric(df_silver["VOLUME_CONTRATADO_MENSAL_MWM"], errors="coerce").fillna(0.0)
        if "STATUS" not in df_silver.columns: df_silver["STATUS"] = "ATIVO"

        for col in ["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]:
            if col not in df_silver.columns: df_silver[col] = "NAO_INFORMADO"

        group_cols = ["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]
        for extra_col in ["NUMERO_REFERENCIA_CONTRATO", "CONTRAPARTE_APELIDO", "CONTRAPARTE_NOME_FANTASIA"]:
            if extra_col in df_silver.columns and extra_col not in group_cols:
                group_cols.append(extra_col)

        df_silver_final = df_silver.groupby(group_cols, as_index=False).agg({"VOLUME_CONTRATADO_MENSAL_MWM": "sum"})

        cols_identidade = ["CNPJ", "CNPJ_RAIZ", "STATUS_CNPJ"]
        cols_identidade_presentes = [c for c in cols_identidade if c in df_silver.columns]
        df_identidade = df_silver[cols_identidade_presentes].drop_duplicates(subset=["CNPJ"])
        df_silver_final = pd.merge(df_silver_final, df_identidade, on="CNPJ", how="left")
        
        df_silver_final["RUN_ID"] = run_id
        df_silver_final["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        silver_dir = context.path("silver") / "denodo_contratos_padronizados"
        silver_dir.mkdir(parents=True, exist_ok=True)
        
        for comp in df_silver_final["COMPETENCIA"].unique():
            if str(comp) in ["000", "NAO_INFORMADONAO_INFORMADO", "00", "nan00"]: continue
            df_comp = df_silver_final[df_silver_final["COMPETENCIA"] == comp]
            escrever_conjunto_de_dados_silver(records=df_comp.to_dict(orient="records"), output_dir=silver_dir, filename=f"contratos_correntes_{comp}")

        dir_reconciliacao = context.path("silver") / "denodo_contratos_silver"
        escrever_conjunto_de_dados_silver(records=df_silver_final.to_dict(orient="records"), output_dir=dir_reconciliacao, filename="contratos_correntes")
        
        logger.info("Contratos agregados e sem duplicidades salvos. %d registros limpos", len(df_silver_final))
        return {"run_id": run_id, "linhas_processadas": len(df_silver_final), "status": "SUCESSO"}
    except Exception as exc:
        logger.exception("Falha crítica na ingestão de contratos do Denodo.")
        raise Exception(f"Erro na ingestão Denodo: {exc}") from exc
```


---

## `src/domain/credito/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/credito/motor_ead.py`

- Linhas: 63
- SHA-256: `3fafde1e29cb1c83fce6479d0daa58776e004503f1522a33b3c9131da1919e70`
- Classes: -
- Funções: calcular_ead

```python
"""Motor de Exposure at Default (EAD).

feat(T3.2.1): Adicionados fator de conversão parametrizado e rastreabilidade
com calculo_id e config_snapshot_id.
Ref: §6.7 (Exposição), §7.1, §11.2 (Identificadores) do Planejamento Funcional.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import uuid4


def calcular_ead(
    mtm_positivo_total: float | None,
    fator_conversao: float = 1.0,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Cálculo de EAD baseado na exposição positiva de MtM.

    Regra: EAD = max(MtM favorável à Copel, 0) × fator_conversao (§6.7).

    Args:
        mtm_positivo_total: MtM positivo consolidado por contraparte.
        fator_conversao: Fator de conversão de crédito (CCF), default 1.0.
            Deve ser lido de config (ex: config["ead"]["fator_conversao"]).
        config: Dicionário de configuração para snapshot de rastreabilidade (§11.2).

    Returns:
        Dict com calculo_id, ead_valor, config_snapshot_id e metadados.
    """
    calculo_id = f"EAD_{uuid4().hex[:12]}"

    config_usada = {"fator_conversao": fator_conversao}
    config_snapshot_id = hashlib.sha256(
        json.dumps(config_usada, sort_keys=True).encode()
    ).hexdigest()[:16]

    if mtm_positivo_total is None:
        return {
            "calculo_id": calculo_id,
            "ead_valor": None,
            "fator_conversao": fator_conversao,
            "config_snapshot_id": config_snapshot_id,
            "dt_calculo": datetime.now().isoformat(timespec="seconds"),
            "status": "SEM_DADOS_MTM",
        }

    ead_valor = max(float(mtm_positivo_total), 0.0) * fator_conversao

    return {
        "calculo_id": calculo_id,
        "ead_valor": ead_valor,
        "mtm_positivo_input": float(mtm_positivo_total),
        "fator_conversao": fator_conversao,
        "config_snapshot_id": config_snapshot_id,
        "dt_calculo": datetime.now().isoformat(timespec="seconds"),
        "status": "CALCULADO",
    }
```


---

## `src/domain/credito/motor_lgd.py`

- Linhas: 85
- SHA-256: `15023c941174eb1f923709b8e4bbe9912f34636a5616f5f6f24c088462f4f355`
- Classes: -
- Funções: calcular_lgd

```python
"""Motor de Loss Given Default (LGD).

feat(T3.3.1): Adicionados lookup de LGD bruta por segmento via config e
rastreabilidade com calculo_id.
Ref: §6.8, §7.1, Apêndice C do Planejamento Funcional.

Nota: A redução por garantias é recebida como parâmetro (cobertura_garantias).
A integração com a base real de garantias é um TODO — quando disponível,
o percentual será calculado automaticamente a partir de garantias_service.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import uuid4

LGD_BRUTA_POR_SEGMENTO: dict[str, float] = {
    "CPURA": 0.45,
    "CGRUPO": 0.45,
    "CONSUMIDOR_GT_5": 0.45,
    "CONSUMIDOR_LE_5": 0.75,
}


def calcular_lgd(
    segmento: str,
    cobertura_garantias: float = 0.0,
    lgd_bruta_override: float | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Cálculo da LGD líquida após mitigação por garantias.

    Fórmula: LGD_liquida = LGD_bruta × (1 - cobertura_garantias) (§6.8).

    Args:
        segmento: Segmento metodológico (CPURA, CGRUPO, etc.).
        cobertura_garantias: Percentual de cobertura de garantias elegíveis [0, 1].
            Default 0.0 — TODO: será alimentado automaticamente pela base de garantias.
        lgd_bruta_override: Se informado, sobrescreve o lookup por segmento.
        config: Dict de configuração para lookup customizado.

    Returns:
        Dict rastreável com calculo_id, lgd_bruta, lgd_liquida e metadados.
    """
    calculo_id = f"LGD_{uuid4().hex[:12]}"

    if lgd_bruta_override is not None:
        lgd_bruta = lgd_bruta_override
        fonte_lgd_bruta = "OVERRIDE"
    elif config and "lgd_bruta_por_segmento" in config:
        lgd_bruta = config["lgd_bruta_por_segmento"].get(segmento, LGD_BRUTA_POR_SEGMENTO.get(segmento, 0.45))
        fonte_lgd_bruta = "CONFIG"
    else:
        lgd_bruta = LGD_BRUTA_POR_SEGMENTO.get(segmento, 0.45)
        fonte_lgd_bruta = "PADRAO_SISTEMA"

    cobertura_efetiva = max(0.0, min(float(cobertura_garantias), 1.0))

    lgd_liquida = lgd_bruta * (1.0 - cobertura_efetiva)

    config_usada = {
        "segmento": segmento,
        "lgd_bruta": lgd_bruta,
        "fonte_lgd_bruta": fonte_lgd_bruta,
        "cobertura_garantias": cobertura_efetiva,
    }
    config_snapshot_id = hashlib.sha256(
        json.dumps(config_usada, sort_keys=True).encode()
    ).hexdigest()[:16]

    return {
        "calculo_id": calculo_id,
        "segmento": segmento,
        "lgd_bruta": lgd_bruta,
        "fonte_lgd_bruta": fonte_lgd_bruta,
        "cobertura_garantias": cobertura_efetiva,
        "lgd_liquida": lgd_liquida,
        "config_snapshot_id": config_snapshot_id,
        "dt_calculo": datetime.now().isoformat(timespec="seconds"),
        "status": "CALCULADO",
    }
```


---

## `src/domain/credito/motor_pe.py`

- Linhas: 73
- SHA-256: `ea0ddfd09b81ec73a5a8fe129f874d06425243267a8cfeb986e39f590ed2d99c`
- Classes: -
- Funções: _is_missing, calcular_perda_esperada

```python
"""Motor de Perda Esperada (PE).

feat(T3.4.1): Retorno dual (pe_reais + pe_percentual) e rastreabilidade
com calculo_id.
Ref: §6.7, §11.2, §11.6 (Reconciliação PE) do Planejamento Funcional.
"""

from __future__ import annotations

import math
from datetime import datetime
from uuid import uuid4


def _is_missing(val) -> bool:
    """Retorna True se val for None ou NaN."""
    if val is None:
        return True
    try:
        return math.isnan(float(val))
    except (TypeError, ValueError):
        return False


def calcular_perda_esperada(
    ead: float | None,
    lgd_liquida: float | None,
    pd_final: float | None,
    notional: float | None = None,
) -> dict[str, object]:
    """
    Cálculo da Perda Esperada.

    Fórmula: PE = EAD × LGD × PD (§6.7).

    Args:
        ead: Exposure at Default em R$.
        lgd_liquida: Loss Given Default líquida [0, 1].
        pd_final: Probability of Default [0, 1].
        notional: Notional total para cálculo do percentual (PE / Notional).

    Returns:
        Dict com pe_reais, pe_percentual, calculo_id e metadados.
    """
    calculo_id = f"PE_{uuid4().hex[:12]}"
    dt_calculo = datetime.now().isoformat(timespec="seconds")

    if _is_missing(ead) or _is_missing(lgd_liquida) or _is_missing(pd_final):
        return {
            "calculo_id": calculo_id,
            "pe_reais": None,
            "pe_percentual": None,
            "dt_calculo": dt_calculo,
            "status": "DADOS_INSUFICIENTES",
        }

    pe_reais = float(ead) * float(lgd_liquida) * float(pd_final)

    pe_percentual = None
    if not _is_missing(notional) and float(notional) > 0:
        pe_percentual = pe_reais / float(notional)

    return {
        "calculo_id": calculo_id,
        "pe_reais": pe_reais,
        "pe_percentual": pe_percentual,
        "ead_input": float(ead),
        "lgd_input": float(lgd_liquida),
        "pd_input": float(pd_final),
        "notional_input": float(notional) if notional is not None else None,
        "dt_calculo": dt_calculo,
        "status": "CALCULADO",
    }
```


---

## `src/domain/credito/motor_taxa_risco.py`

- Linhas: 88
- SHA-256: `f80ca8d72a85b0f51a6f4543c13c80da233477480e58dbdee5b59908d6ff28db`
- Classes: -
- Funções: _is_missing, calcular_taxa_risco

```python
from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any
from uuid import uuid4
from relational.facts.fato_alerta_util import registrar_alerta


def _is_missing(val) -> bool:
    """Retorna True se val for None ou NaN."""
    if val is None:
        return True
    try:
        return math.isnan(float(val))
    except (TypeError, ValueError):
        return False

LOGGER = logging.getLogger(__name__)


def calcular_taxa_risco(
    pe_total: float | None,
    notional_total: float | None,
    run_id: str | None = None,
    context: Any | None = None
) -> dict[str, Any]:
    calculo_id = f"TAXA_{uuid4().hex[:12]}"
    dt_calculo = datetime.now().isoformat(timespec="seconds")

    if _is_missing(pe_total) or _is_missing(notional_total):
        return {
            "calculo_id": calculo_id,
            "taxa_risco": None,
            "dt_calculo": dt_calculo,
            "status": "DADOS_INSUFICIENTES",
            "alertas": []
        }

    alertas = []
    
    if _is_missing(notional_total) or float(notional_total) <= 0:
        LOGGER.warning(
            "Cálculo de Taxa de Risco não executado: Notional Total inválido ou zero (%.2f).", 
            notional_total
        )
        msg = f"Divisão por zero: Notional total ({notional_total}) <= 0 durante cálculo da Taxa de Risco."
        alertas.append({
            "CODIGO": "QLT_002",
            "SEVERIDADE": "ALTO",
            "MENSAGEM": msg
        })
        
        if run_id and context:
            registrar_alerta(
                codigo="QLT_002",
                severidade="ALTO",
                regra="Notional Total Zerado",
                mensagem=msg,
                campo_afetado="NOTIONAL_TOTAL",
                valor_observado=notional_total,
                limite_esperado="> 0",
                contraparte_id="N/A (Carteira)",
                run_id=run_id,
                context=context
            )
        return {
            "calculo_id": calculo_id,
            "taxa_risco": None,
            "pe_total_input": float(pe_total),
            "notional_total_input": float(notional_total),
            "dt_calculo": dt_calculo,
            "status": "ERRO_MATEMATICO",
            "alertas": alertas
        }

    taxa_risco = float(pe_total) / float(notional_total)

    return {
        "calculo_id": calculo_id,
        "taxa_risco": taxa_risco,
        "pe_total_input": float(pe_total),
        "notional_total_input": float(notional_total),
        "dt_calculo": dt_calculo,
        "status": "CALCULADO",
        "alertas": alertas
    }
```


---

## `src/domain/credito/notas_quantitativas_cpura.py`

- Linhas: 167
- SHA-256: `fa60b717134a1f87977aea13a7c1a11f925ceedbdc657891c934328db6d3f2af`
- Classes: -
- Funções: _obter_valor_numerico, _normalizar_pd, _obter_faixas_notas, _atribuir_nota_por_faixa, calcular_notas_quantitativas_cpura

```python
"""Cálculo das notas quantitativas de CPURA."""

from __future__ import annotations

from typing import Any

from common.numeros import to_float_br
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_valor_numerico(
    registro: dict[str, Any],
    campo: str,
) -> float:
    """Obtém e valida um valor numérico do registro."""
    valor = to_float_br(registro.get(campo))

    if valor is None:
        raise PdInputValidationError(
            f"{campo} não informado."
        )

    return float(valor)


def _normalizar_pd(valor: float) -> float:
    """Normaliza PD para escala decimal [0, 1]."""
    if valor < 0:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT negativa: {valor}"
        )

    if valor > 1:
        valor = valor / 100.0

    if valor > 1:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT fora do intervalo após normalização: {valor}"
        )

    return valor


def _obter_faixas_notas(
    score_cpura_config: dict[str, Any],
    indicador: str,
) -> list[dict[str, Any]]:
    """Obtém as faixas de notas de um indicador."""
    faixas_root = score_cpura_config.get("faixas_notas_quantitativas")

    if not isinstance(faixas_root, dict):
        raise PdConfigurationError(
            "Bloco 'faixas_notas_quantitativas' ausente ou inválido."
        )

    faixas = faixas_root.get(indicador)

    if not isinstance(faixas, list) or not faixas:
        raise PdConfigurationError(
            f"Faixas quantitativas ausentes ou inválidas para {indicador}."
        )

    return faixas


def _atribuir_nota_por_faixa(
    valor: float,
    faixas: list[dict[str, Any]],
    indicador: str,
) -> str:
    """Atribui nota A-E conforme a faixa parametrizada."""
    for faixa in faixas:
        try:
            nota = str(faixa["nota"]).strip().upper()
            minimo = float(faixa["min"])
            maximo = float(faixa["max"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Faixa incompleta em {indicador}: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                f"Faixa inválida em {indicador}."
            ) from exc

        if minimo > maximo:
            raise PdConfigurationError(
                f"Faixa inválida em {indicador}: min > max."
            )

        if minimo <= valor <= maximo:
            return nota

    raise PdInputValidationError(
        f"Valor sem faixa configurada para {indicador}: {valor}"
    )


def calcular_notas_quantitativas_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula as notas quantitativas de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo das notas quantitativas CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )

        pd_valor = _obter_valor_numerico(registro, "PROBABILIDADE_DEFAULT")
        fco_rol_valor = _obter_valor_numerico(registro, "FCO")
        roe_valor = _obter_valor_numerico(registro, "ROE")
        roa_valor = _obter_valor_numerico(registro, "ROA")

        pd_valor = _normalizar_pd(pd_valor)

        nota_pd = _atribuir_nota_por_faixa(
            valor=pd_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "PD"),
            indicador="PD",
        )
        nota_fco_rol = _atribuir_nota_por_faixa(
            valor=fco_rol_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "FCO_ROL"),
            indicador="FCO_ROL",
        )
        nota_roe = _atribuir_nota_por_faixa(
            valor=roe_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "ROE"),
            indicador="ROE",
        )
        nota_roa = _atribuir_nota_por_faixa(
            valor=roa_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "ROA"),
            indicador="ROA",
        )

        resultado = {
            "NOTA_PD": nota_pd,
            "NOTA_FCO_ROL": nota_fco_rol,
            "NOTA_ROE": nota_roe,
            "NOTA_ROA": nota_roa,
        }

        if logger is not None:
            logger.info(
                "Notas quantitativas CPURA calculadas. "
                "CNPJ=%s NOTA_PD=%s NOTA_FCO_ROL=%s NOTA_ROE=%s NOTA_ROA=%s",
                registro.get("CNPJ"),
                resultado["NOTA_PD"],
                resultado["NOTA_FCO_ROL"],
                resultado["NOTA_ROE"],
                resultado["NOTA_ROA"],
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception("Falha no cálculo das notas quantitativas CPURA. CNPJ=%s", registro.get('CNPJ'))
        raise
```


---

## `src/domain/credito/pd_base.py`

- Linhas: 42
- SHA-256: `98cd207f945d3a03d84f52e0abeee3e219fc813191ff6fcc2047dfeee81143e1`
- Classes: -
- Funções: calcular_pd_base

```python
"""Cálculo ou leitura da PD base."""

from __future__ import annotations

from typing import Any

from common.numeros import to_float_br
from domain.credito.pd_exceptions import PdInputValidationError


def calcular_pd_base(
    registro: dict[str, Any],
    segmento_pd: str,
) -> float:
    """Calcula ou lê a PD base do registro."""
    valor = registro.get("PROBABILIDADE_DEFAULT")
    pd_base = to_float_br(valor)
    
    if segmento_pd == "CONSUMIDOR_LE_5":
        return 0.0
    
    valor = registro.get("PROBABILIDADE_DEFAULT")

    if pd_base is None:
        raise PdInputValidationError(
            f"Registro sem PROBABILIDADE_DEFAULT para {segmento_pd}."
        )

    if pd_base < 0:
        raise PdInputValidationError(
            f"PD base negativa: {pd_base}"
        )

    if pd_base > 1:
        pd_base = pd_base / 100.0

    if pd_base > 1:
        raise PdInputValidationError(
            f"PD base fora do intervalo após normalização: {pd_base}"
        )

    return pd_base
```


---

## `src/domain/credito/pd_cgrupo.py`

- Linhas: 140
- SHA-256: `0adc7252c968f4f5bc24bd862fa8d5510752bd54a9c4f0de2826c6bb98f0efdb`
- Classes: -
- Funções: _norm, _norm_agencia, _norm_rating, _mapear_rating_externo, _resolver_rating_cgrupo, _pior_rating, _percentil_empirico, _interpolar_pd, calcular_pd_final_cgrupo

```python
from __future__ import annotations

from typing import Any

from domain.credito.pd_exceptions import PdCalculationError


RATING_ORDER = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


def _norm(value: Any) -> str:
    return str(value or "").strip().upper()


def _norm_agencia(value: Any) -> str:
    agencia = _norm(value)

    # A normalização de aliases já ocorreu na camada Silver via domain_dictionaries.json.
    # Aqui, garantimos apenas a consistência básica.
    return agencia


def _norm_rating(value: Any) -> str:
    return _norm(value)


def _mapear_rating_externo(
    agencia: str,
    rating_externo: str,
    regras_rating: dict[str, Any],
) -> str:
    ag = _norm_agencia(agencia)
    rt = _norm(rating_externo)

    short_default = {_norm(x)
                     for x in regras_rating["short_term_or_default_markers"]}
    if rt in short_default:
        return regras_rating["default_class"]

    agencias = regras_rating["agencias"]
    if ag not in agencias:
        return regras_rating["default_class"]

    for rating_copel, lista_externa in agencias[ag].items():
        if rt in {_norm(x) for x in lista_externa}:
            return rating_copel

    return regras_rating["default_class"]


def _resolver_rating_cgrupo(
    registro: dict[str, Any],
    regras_segmento: dict[str, Any],
) -> tuple[str, str]:
    regras_rating = regras_segmento["rating_externo"]

    agencia = registro.get("AGENCIA")
    rating = registro.get("NOTA_CREDITO")

    if agencia and rating:
        rating_convertido = _mapear_rating_externo(
            agencia=agencia,
            rating_externo=rating,
            regras_rating=regras_rating,
        )
        return rating_convertido, "RATING_PUBLICO"

    rating_interno = _norm(registro.get("RATING_FINAL")
                           or registro.get("RATING_COPEL"))
    if rating_interno not in {"A", "B", "E"}:
        raise PdCalculationError(
            f"Rating interno inválido para CGRUPO: {rating_interno!r}"
        )

    return rating_interno, "RATING_INTERNO"


def _pior_rating(ratings: list[str]) -> str:
    validos = [r for r in ratings if r in RATING_ORDER]
    if not validos:
        raise PdCalculationError(
            "Nenhum rating válido encontrado para CGRUPO."
        )
    return max(validos, key=lambda x: RATING_ORDER[x])


def _percentil_empirico(pd_base, peer_group):
    n = len(peer_group)

    if n <= 1:
        return 0.5

    menores = sum(1 for x in peer_group if x < pd_base)
    iguais = sum(1 for x in peer_group if x == pd_base)

    return (menores + 0.5 * iguais) / n


def _interpolar_pd(pd_min: float, pd_max: float, u: float) -> float:
    return pd_min + u * (pd_max - pd_min)


def calcular_pd_final_cgrupo(
    registro: dict[str, Any],
    regras_segmento: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    pd_base = float(registro["PD_BASE"])
    rating, fonte_rating = _resolver_rating_cgrupo(registro, regras_segmento)

    regras_pd = regras_segmento["pd_final_rules"]
    fixed_pd = regras_pd.get("fixed_pd_by_rating", {})

    if rating in fixed_pd:
        pd_final = float(fixed_pd[rating])
        return {
            "RATING_FINAL": rating,
            "FONTE_RATING": fonte_rating,
            "PD_MIN_FAIXA": 0.0,
            "PD_MAX_FAIXA": pd_final,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": pd_final,
            "PD_METODO": "FIXED_PD",
        }

    faixa = regras_pd["faixas_pd"][rating]
    pd_min = float(faixa["min"])
    pd_max = float(faixa["max"])

    pd_final = min(max(pd_base, pd_min), pd_max)

    return {
        "RATING_FINAL": rating,
        "FONTE_RATING": fonte_rating,
        "PD_MIN_FAIXA": pd_min,
        "PD_MAX_FAIXA": pd_max,
        "PERCENTIL_PD_BASE": None,
        "PD_FINAL": pd_final,
        "PD_METODO": "CLAMP",
    }
```


---

## `src/domain/credito/pd_consumidor_gt5.py`

- Linhas: 121
- SHA-256: `c74acd6e73bbf80bd86f899bb92c65489888d3c779da1a853a941d22f08629a1`
- Classes: -
- Funções: _inv_t_aproximado, _normalize_pd_input, calcular_pd_final_consumidor_gt5

```python
"""Transformação da PD para consumidores acima de 5 MWm."""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

from domain.credito.pd_exceptions import (
    PdCalculationError,
    PdConfigurationError,
)


def _inv_t_aproximado(prob: float, df: float) -> float:
    """Aproxima o quantil da t de Student a partir do quantil normal."""
    if not 0 < prob < 1:
        raise PdCalculationError(
            f"Probabilidade inválida para inversa t: {prob!r}"
        )

    z = NormalDist().inv_cdf(prob)

    g1 = (z**3 + z) / (4 * df)
    g2 = (5 * z**5 + 16 * z**3 + 3 * z) / (96 * (df**2))
    g3 = (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * (df**3))

    return z + g1 + g2 + g3


def _normalize_pd_input(
    value: float,
    normalize_percent_if_gt_1: bool,
) -> float:
    q = float(value)
    if normalize_percent_if_gt_1 and q > 1:
        q = q / 100.0
    return q


def calcular_pd_final_consumidor_gt5(
    registro: dict[str, Any],
    pd_base: float,
    rating_final: str,
    pd_min: float,
    pd_max: float,
    regras_segmento: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada para consumidor acima de 5 MWm."""
    try:
        regras_pd = regras_segmento["pd_final_rules"]
        metodo = str(regras_pd.get("method", "")).strip().lower()

        if metodo != "t_dist_logistic":
            raise PdConfigurationError(
                f"Método inválido para CONSUMIDOR_GT_5: {metodo!r}"
            )

        df = float(regras_pd["df"])
        scale = float(regras_pd["scale"])
        eps = float(regras_pd["eps"])
        normalize_percent_if_gt_1 = bool(
            regras_pd.get("normalize_input_percent_if_gt_1", True)
        )

        q = _normalize_pd_input(
            value=float(pd_base),
            normalize_percent_if_gt_1=normalize_percent_if_gt_1,
        )

        q_cap = min(1 - eps, max(eps, q))

        z_t = _inv_t_aproximado(q_cap, df)
        z = scale * z_t
        u = 1.0 / (1.0 + math.exp(-z))

        pd_final = pd_min + u * (pd_max - pd_min)

        resultado = {
            "RATING_FINAL": rating_final,
            "PD_BASE": pd_base,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": pd_final,
            "PD_METODO": "T_DIST_LOGISTIC",
            "PD_Q_NORMALIZADA": q,
            "PD_Q_CAP": q_cap,
            "PD_Z_T": z_t,
            "PD_Z_ESCALADO": z,
            "PD_U_INTERPOLACAO": u,
        }

        if logger is not None:
            logger.info(
                "PD ajustada CONSUMIDOR_GT_5 calculada. "
                "CNPJ=%s RATING=%s PD_BASE=%s Q=%s Q_CAP=%s "
                "PD_MIN=%s PD_MAX=%s Z_T=%s Z=%s U=%s PD_FINAL=%s",
                registro.get("CNPJ"),
                rating_final,
                pd_base,
                q,
                q_cap,
                pd_min,
                pd_max,
                z_t,
                z,
                u,
                pd_final,
            )

        return resultado

    except Exception as exc:
        if isinstance(exc, (PdCalculationError, PdConfigurationError)):
            raise
        raise PdCalculationError(
            "Falha no cálculo da PD ajustada de CONSUMIDOR_GT_5: "
            f"{exc}"
        ) from exc
```


---

## `src/domain/credito/pd_consumidor_le5.py`

- Linhas: 73
- SHA-256: `52f0c6d1e1e6a7b437809e4d7dcc5ebc983fe807a4c5f8263fdd03767eb0f968`
- Classes: -
- Funções: calcular_pd_final_consumidor_le5

```python
"""Transformação da PD para consumidores abaixo de 5 MWm (Bureau)."""

from __future__ import annotations
from typing import Any

from common.numeros import to_float_br
from domain.credito.pd_exceptions import PdCalculationError, PdInputValidationError

def calcular_pd_final_consumidor_le5(
    registro: dict[str, Any],
    pd_faixas: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula PD via score de bureau e restritivos (Sem DFs)."""
    try:
        score = to_float_br(registro.get("SCORE_BUREAU"))
        
        _r = to_float_br(registro.get("QUANTIDADE_RESTRITIVOS"))
        restritivos = _r if _r is not None else 0.0

        if score is None:
            raise PdInputValidationError("SCORE_BUREAU não informado para consumidor < 5 MWm.")

        if score >= 800:
            rating = "A"
        elif score >= 600:
            rating = "B"
        elif score >= 400:
            rating = "C"
        elif score >= 200:
            rating = "D"
        else:
            rating = "E"

        if restritivos > 0:
            rating = "E"

        faixas = pd_faixas.get("CONSUMIDOR_LE_5", {})
        if rating not in faixas:
            raise PdCalculationError(f"Faixa de PD não encontrada para o rating {rating}.")

        pd_min = float(faixas[rating]["min"])
        pd_max = float(faixas[rating]["max"])

        limites = {"A": (800, 1000), "B": (600, 800), "C": (400, 600), "D": (200, 400), "E": (0, 200)}
        s_min, s_max = limites[rating]

        score_truncado = max(s_min, min(score, s_max))
        fator = 0.5 if s_max == s_min else 1.0 - ((score_truncado - s_min) / (s_max - s_min))
        pd_final = pd_min + (fator * (pd_max - pd_min))

        resultado = {
            "RATING_FINAL": rating,
            "PD_FINAL": pd_final,
            "PD_METODO": "SCORE_BUREAU",
            "SCORE_BUREAU_UTILIZADO": score,
            "QUANTIDADE_RESTRITIVOS": restritivos,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            "PATRIMONIO_LIQUIDO": "NAO_APLICAVEL",
            "LUCRO_LIQUIDO": "NAO_APLICAVEL",
            "ATIVO_TOTAL": "NAO_APLICAVEL",
            "PASSIVO_CIRCULANTE": "NAO_APLICAVEL"
        }

        if logger:
            logger.info("PD LE_5 calculada. CNPJ=%s SCORE=%s RATING=%s PD=%s", registro.get("CNPJ"), score, rating, pd_final)

        return resultado

    except Exception as exc:
        if logger: logger.exception("Falha no cálculo LE_5.")
        raise PdCalculationError(f"Falha LE_5: {exc}") from exc
```


---

## `src/domain/credito/pd_cpura.py`

- Linhas: 282
- SHA-256: `f19899024250bcd12ddd9c50c62e0720809bf01e03ff03edf20583bdb354da39`
- Classes: -
- Funções: _clamp, _obter_score_total, _obter_faixa_score_rating, _obter_estabilizacao, _calcular_score_truncado, _calcular_posicao_relativa, _calcular_pd_bruta, _estabilizar_pd, calcular_pd_final_cpura

```python
"""Transformação de PD para comercializadoras puras."""

from __future__ import annotations

import math
from typing import Any

from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _clamp(valor: float, minimo: float, maximo: float) -> float:
    """Restringe valor ao intervalo informado."""
    return max(min(valor, maximo), minimo)


def _obter_score_total(registro: dict[str, Any]) -> float:
    """Obtém o score total S do registro."""
    score_total = registro.get("SCORE_TOTAL")

    if score_total is None:
        raise PdInputValidationError(
            "Registro sem SCORE_TOTAL para cálculo de PD de CPURA."
        )

    try:
        score_total = float(score_total)
    except (TypeError, ValueError) as exc:
        raise PdInputValidationError(
            f"SCORE_TOTAL inválido: {score_total!r}"
        ) from exc

    if score_total < 0 or score_total > 10:
        raise PdInputValidationError(
            f"SCORE_TOTAL fora do intervalo esperado [0, 10]: {score_total}"
        )

    return score_total


def _obter_faixa_score_rating(
    rating_final: str,
    score_faixas: dict[str, dict[str, float]],
) -> tuple[float, float]:
    """Obtém a faixa de score do rating."""
    if not score_faixas:
        raise PdConfigurationError(
            "Configuração 'score_faixas' não informada para CPURA."
        )

    if rating_final not in score_faixas:
        raise PdConfigurationError(
            f"Rating inválido para CPURA: {rating_final}"
        )

    faixa = score_faixas[rating_final]

    if "min" not in faixa or "max" not in faixa:
        raise PdConfigurationError(
            f"Faixa de score inválida para rating {rating_final}."
        )

    try:
        score_min = float(faixa["min"])
        score_max = float(faixa["max"])
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            f"Faixa de score não numérica para rating {rating_final}."
        ) from exc

    if score_min > score_max:
        raise PdConfigurationError(
            f"Faixa de score inválida para rating {rating_final}: min > max."
        )

    return score_min, score_max


def _obter_estabilizacao(
    cpura_config: dict[str, Any],
) -> tuple[float, float, float]:
    """Obtém os parâmetros de estabilização numérica."""
    estabilizacao = cpura_config.get("estabilizacao")

    if not isinstance(estabilizacao, dict):
        raise PdConfigurationError(
            "Bloco 'estabilizacao' ausente ou inválido em cpura_config."
        )

    try:
        epsilon = float(estabilizacao["epsilon"])
        z_min = float(estabilizacao["z_min"])
        z_max = float(estabilizacao["z_max"])
    except KeyError as exc:
        raise PdConfigurationError(
            f"Parâmetro de estabilização ausente: {exc}"
        ) from exc
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            "Parâmetros de estabilização inválidos."
        ) from exc

    if epsilon <= 0 or epsilon >= 0.5:
        raise PdConfigurationError(
            f"Epsilon inválido para estabilização: {epsilon}"
        )

    if z_min > z_max:
        raise PdConfigurationError(
            f"Intervalo de logit inválido: z_min={z_min}, z_max={z_max}"
        )

    return epsilon, z_min, z_max


def _calcular_score_truncado(
    score_total: float,
    score_min: float,
    score_max: float,
) -> float:
    """Aplica truncamento do score dentro da faixa do rating."""
    return _clamp(score_total, score_min, score_max)


def _calcular_posicao_relativa(
    score_truncado: float,
    score_min: float,
    score_max: float,
) -> float:
    """Calcula a posição relativa intra-rating."""
    if score_max == score_min:
        return 0.0

    u = (score_max - score_truncado) / (score_max - score_min)
    return _clamp(u, 0.0, 1.0)


def _calcular_pd_bruta(
    pd_min: float,
    pd_max: float,
    posicao_relativa: float,
) -> float:
    """Interpola a PD bruta dentro da faixa do rating."""
    pd_bruta = pd_min + posicao_relativa * (pd_max - pd_min)
    return _clamp(pd_bruta, 0.0, 1.0)


def _estabilizar_pd(
    pd_bruta: float,
    epsilon: float,
    z_min: float,
    z_max: float,
) -> tuple[float, float, float]:
    """Aplica estabilização numérica via logit."""
    p = _clamp(pd_bruta, epsilon, 1.0 - epsilon)
    z = math.log(p / (1.0 - p))
    z_truncado = _clamp(z, z_min, z_max)
    pd_final = 1.0 / (1.0 + math.exp(-z_truncado))
    return p, z_truncado, pd_final


def calcular_pd_final_cpura(
    registro: dict[str, Any],
    pd_base: float,
    rating_final: str,
    pd_min: float,
    pd_max: float,
    cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD final de CPURA por interpolação intra-rating."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo de PD final CPURA. "
                "CNPJ=%s rating=%s pd_min=%s pd_max=%s",
                registro.get("CNPJ"),
                rating_final,
                pd_min,
                pd_max,
            )

        if not cpura_config:
            raise PdConfigurationError(
                "Configuração de CPURA não informada."
            )

        if pd_min < 0 or pd_max < 0 or pd_min > 1 or pd_max > 1:
            raise PdInputValidationError(
                f"Faixa de PD inválida: pd_min={pd_min}, pd_max={pd_max}"
            )

        if pd_min > pd_max:
            raise PdInputValidationError(
                f"Faixa de PD inválida: pd_min > pd_max "
                f"({pd_min} > {pd_max})"
            )

        score_total = _obter_score_total(registro)
        score_faixas = cpura_config.get("score_faixas", {})
        score_min, score_max = _obter_faixa_score_rating(
            rating_final=rating_final,
            score_faixas=score_faixas,
        )
        epsilon, z_min, z_max = _obter_estabilizacao(cpura_config)

        score_truncado = _calcular_score_truncado(
            score_total=score_total,
            score_min=score_min,
            score_max=score_max,
        )

        posicao_relativa = _calcular_posicao_relativa(
            score_truncado=score_truncado,
            score_min=score_min,
            score_max=score_max,
        )

        pd_bruta = _calcular_pd_bruta(
            pd_min=pd_min,
            pd_max=pd_max,
            posicao_relativa=posicao_relativa,
        )

        p_estabilizado, z_truncado, pd_final = _estabilizar_pd(
            pd_bruta=pd_bruta,
            epsilon=epsilon,
            z_min=z_min,
            z_max=z_max,
        )

        resultado = {
            "SCORE_TOTAL": score_total,
            "SCORE_MIN_RATING": score_min,
            "SCORE_MAX_RATING": score_max,
            "SCORE_TRUNCADO": score_truncado,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            "PD_PERCENTIL_INTERNO": posicao_relativa,
            "PD_BRUTA": pd_bruta,
            "PD_ESTABILIZADA": p_estabilizado,
            "PD_FINAL": pd_final,
            "PD_METODO": "INTERPOLACAO_INTRA_RATING_CPURA",
            "LOGIT_TRUNCADO": z_truncado,
        }

        if logger is not None:
            logger.info(
                "PD final CPURA calculada com sucesso. "
                "CNPJ=%s score_total=%s score_truncado=%s "
                "u=%s pd_bruta=%s pd_final=%s",
                registro.get("CNPJ"),
                resultado["SCORE_TOTAL"],
                resultado["SCORE_TRUNCADO"],
                resultado["PD_PERCENTIL_INTERNO"],
                resultado["PD_BRUTA"],
                resultado["PD_FINAL"],
            )

        return resultado

    except (PdInputValidationError, PdConfigurationError):
        if logger is not None:
            logger.exception(
                "Erro controlado no cálculo de PD final CPURA. "
                "CNPJ=%s rating=%s",
                registro.get("CNPJ"),
                rating_final,
            )
        raise

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha inesperada no cálculo de PD final CPURA. "
                "CNPJ=%s rating=%s",
                registro.get("CNPJ"),
                rating_final,
            )
        raise
```


---

## `src/domain/credito/pd_exceptions.py`

- Linhas: 15
- SHA-256: `40d069ee1f05d3978202b180a5d4ca89927e99faae914be4c37110c116abda73`
- Classes: PdCalculationError, PdInputValidationError, PdConfigurationError
- Funções: -

```python
"""Exceções do motor de probabilidade de default."""

from __future__ import annotations


class PdCalculationError(Exception):
    """Erro base do cálculo de PD ajustada."""


class PdInputValidationError(PdCalculationError):
    """Erro de validação dos insumos de PD."""


class PdConfigurationError(PdCalculationError):
    """Erro de configuração do motor de PD."""
```


---

## `src/domain/credito/pd_motor.py`

- Linhas: 174
- SHA-256: `f5d08b23f0649fb8f1bf1442804307aa439484e5be824620503c495681bf9e11`
- Classes: -
- Funções: calcular_pd_ajustada

```python
from __future__ import annotations

from typing import Any

from domain.credito.notas_quantitativas_cpura import (
    calcular_notas_quantitativas_cpura,
)
from domain.credito.pd_base import calcular_pd_base
from domain.credito.pd_exceptions import (
    PdCalculationError,
    PdConfigurationError,
)
from domain.credito.pd_transform import transformar_pd_por_segmento
from domain.credito.pd_validator import validar_insumos_pd, _is_blank
from domain.credito.rating import calcular_rating_final
from domain.credito.score_qualitativo import calcular_score_qualitativo_cpura
from domain.credito.score_quantitativo import calcular_score_quantitativo_cpura
from domain.credito.score_total import calcular_score_total_cpura
from common.texto import normalizar_texto


def calcular_pd_ajustada(
    registro: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any] | None = None,
    pd_cpura_config: dict[str, Any] | None = None,
    score_cpura_config: dict[str, Any] | None = None,
    peer_group: list[float] | None = None,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada/final da contraparte."""
    segmento_pd = str(registro.get("SEGMENTO_PD", "")).strip().upper()

    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo de PD ajustada. "
                "CNPJ=%s SEGMENTO_PD=%s",
                registro.get("CNPJ"),
                segmento_pd,
            )

        validar_insumos_pd(registro, segmento_pd)

        pd_base = calcular_pd_base(registro, segmento_pd)

        registro_calculo = dict(registro)
        registro_calculo["PD_BASE"] = pd_base

        resultado_scores: dict[str, Any] = {}

        if segmento_pd == "CPURA":
            if not score_cpura_config:
                raise PdConfigurationError(
                    "score_cpura_config não informado para CPURA."
                )

            if not pd_cpura_config:
                raise PdConfigurationError(
                    "pd_cpura_config não informado para CPURA."
                )

            # --- FAIL-SAFE PARA RATING NULO ---
            rating_raw = registro_calculo.get("RATING_FINAL") or registro_calculo.get("RATING_COPEL") or registro_calculo.get("NOTA_CREDITO")
            rating_norm = normalizar_texto(str(rating_raw)) if not _is_blank(rating_raw) else None
            
            if rating_norm is None:
                if logger is not None:
                    logger.warning("Cálculo CPURA suspenso por Falha Segura. Rating nulo. CNPJ=%s", registro.get("CNPJ"))
                resultado_fail = dict(registro_calculo)
                resultado_fail["STATUS_CALCULO_PD"] = "PENDENTE"
                resultado_fail["PD_FINAL"] = None
                resultado_fail["RATING_FINAL"] = None
                return resultado_fail

            notas_quant_info = calcular_notas_quantitativas_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(notas_quant_info)

            score_qual_info = calcular_score_qualitativo_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(score_qual_info)

            score_quant_info = calcular_score_quantitativo_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(score_quant_info)

            score_total_info = calcular_score_total_cpura(
                score_quant_info=score_quant_info,
                score_qual_info=score_qual_info,
                logger=logger,
            )
            registro_calculo.update(score_total_info)

            rating_final = calcular_rating_final(
                registro=registro_calculo,
                segmento_pd=segmento_pd,
                pd_cpura_config=pd_cpura_config,
            )
            registro_calculo["RATING_FINAL"] = rating_final

            resultado_scores.update(notas_quant_info)
            resultado_scores.update(score_qual_info)
            resultado_scores.update(score_quant_info)
            resultado_scores.update(score_total_info)

        if segmento_pd in {"CGRUPO", "CONSUMIDOR_GT_5"} and not pd_transform_rules:
            raise PdConfigurationError(
                f"pd_transform_rules não informado para {segmento_pd}."
            )
        
        # Só transformamos se não tivermos abortado lá em cima
        resultado_transformacao = transformar_pd_por_segmento(
            registro=registro_calculo,
            segmento_pd=segmento_pd,
            pd_base=pd_base,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=pd_cpura_config,
            peer_group=peer_group,
            logger=logger,
            rating_final=(
                registro_calculo.get("RATING_FINAL")
                or registro_calculo.get("RATING_COPEL")
            ),
        )

        resultado = {
            "SEGMENTO_PD": segmento_pd,
            "PD_BASE": pd_base,
            "STATUS_CALCULO_PD": "CONCLUIDO",
            **resultado_scores,
            **resultado_transformacao,
        }

        if logger is not None:
            logger.info(
                "PD ajustada calculada com sucesso. "
                "CNPJ=%s SEGMENTO_PD=%s PD_BASE=%s "
                "RATING_FINAL=%s SCORE_TOTAL=%s PD_FINAL=%s METODO=%s",
                registro.get("CNPJ"),
                segmento_pd,
                resultado.get("PD_BASE"),
                resultado.get("RATING_FINAL"),
                resultado.get("SCORE_TOTAL"),
                resultado.get("PD_FINAL"),
                resultado.get("PD_METODO"),
            )

        return resultado

    except PdCalculationError:
        if logger is not None:
            logger.exception("Erro controlado no cálculo de PD ajustada. CNPJ=%s SEGMENTO_PD=%s", registro.get('CNPJ'), segmento_pd)
        raise

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha crítica no cálculo de PD ajustada. "
                "CNPJ=%s SEGMENTO_PD=%s",
                registro.get("CNPJ"),
                segmento_pd,
            )
        raise
```


---

## `src/domain/credito/pd_transform.py`

- Linhas: 173
- SHA-256: `9805676fef28778e94d04caf92ab4b46fa43712db52b32a01ce3825d07ce2f5a`
- Classes: -
- Funções: _obter_faixa_pd, transformar_pd_por_segmento

```python
"""Despacho da transformação de PD por segmento."""

from __future__ import annotations

from typing import Any

from domain.credito.pd_cgrupo import calcular_pd_final_cgrupo
from domain.credito.pd_consumidor_gt5 import calcular_pd_final_consumidor_gt5
from domain.credito.pd_consumidor_le5 import calcular_pd_final_consumidor_le5
from domain.credito.pd_cpura import calcular_pd_final_cpura
from domain.credito.pd_exceptions import PdCalculationError, PdConfigurationError


def _obter_faixa_pd(
    pd_faixas: dict[str, Any],
    segmento_pd: str,
    rating_final: str,
) -> tuple[float, float]:
    """Obtém a faixa de PD parametrizada para segmento e rating."""
    if not pd_faixas:
        raise PdConfigurationError("Faixas de PD não informadas.")

    if segmento_pd not in pd_faixas:
        raise PdConfigurationError(
            f"Segmento não encontrado nas faixas de PD: {segmento_pd}"
        )

    faixas_segmento = pd_faixas[segmento_pd]

    if rating_final not in faixas_segmento:
        raise PdConfigurationError(
            f"Rating {rating_final} não encontrado para {segmento_pd}"
        )

    faixa = faixas_segmento[rating_final]

    if "min" not in faixa or "max" not in faixa:
        raise PdConfigurationError(
            f"Faixa inválida para {segmento_pd}/{rating_final}."
        )

    pd_min = float(faixa["min"])
    pd_max = float(faixa["max"])

    if pd_min > pd_max:
        raise PdConfigurationError(
            f"Faixa inválida: min > max para {segmento_pd}/{rating_final}."
        )

    return pd_min, pd_max


def transformar_pd_por_segmento(
    registro: dict[str, Any],
    segmento_pd: str,
    pd_base: float,
    pd_faixas: dict[str, Any],
    pd_cpura_config: dict[str, Any] | None = None,
    logger: Any | None = None,
    peer_group: list[float] | None = None,
    pd_transform_rules: dict[str, Any] | None = None,
    rating_final: str | None = None,
) -> dict[str, Any]:
    """Transforma a PD base conforme a metodologia do segmento."""
    segmento = str(segmento_pd or "").strip().upper()

    if segmento == "CPURA":
        rating = str(
            registro.get("RATING_FINAL") or rating_final or ""
        ).strip().upper()

        if not rating:
            raise PdConfigurationError(
                "RATING_FINAL não informado para CPURA.")

        pd_min, pd_max = _obter_faixa_pd(
            pd_faixas=pd_faixas,
            segmento_pd=segmento,
            rating_final=rating,
        )

        return calcular_pd_final_cpura(
            registro=registro,
            pd_base=pd_base,
            rating_final=rating,
            pd_min=pd_min,
            pd_max=pd_max,
            cpura_config=pd_cpura_config or {},
            logger=logger,
        )

    if segmento == "CGRUPO":
        if not pd_transform_rules:
            raise PdConfigurationError(
                "pd_transform_rules não informado para CGRUPO."
            )

        registro_calculo = dict(registro)
        registro_calculo["PD_BASE"] = pd_base

        return calcular_pd_final_cgrupo(
            registro=registro_calculo,
            regras_segmento=pd_transform_rules["CGRUPO"],
            logger=logger,
        )

    if segmento == "CONSUMIDOR_GT_5":
        rating = str(
            registro.get("RATING_FINAL")
            or registro.get("RATING_COPEL")
            or rating_final
            or ""
        ).strip().upper()

        if not rating:
            raise PdConfigurationError(
                "RATING_FINAL não informado para CONSUMIDOR_GT_5."
            )

        pd_min, pd_max = _obter_faixa_pd(
            pd_faixas=pd_faixas,
            segmento_pd=segmento,
            rating_final=rating,
        )

        if not pd_transform_rules or segmento not in pd_transform_rules:
            raise PdConfigurationError(
                "pd_transform_rules não informado para CONSUMIDOR_GT_5."
            )

        return calcular_pd_final_consumidor_gt5(
            registro=registro,
            pd_base=pd_base,
            rating_final=rating,
            pd_min=pd_min,
            pd_max=pd_max,
            regras_segmento=pd_transform_rules[segmento],
            logger=logger,
        )
        
    if segmento == "CONSUMIDOR_LE_5":
        rating = str(
            registro.get("RATING_FINAL")
            or registro.get("RATING_COPEL")
            or rating_final
            or ""
        ).strip().upper()

        if not rating:
            raise PdConfigurationError(
                "RATING_FINAL não informado para CONSUMIDOR_LE_5."
            )

        pd_min, pd_max = _obter_faixa_pd(
            pd_faixas=pd_faixas,
            segmento_pd=segmento,
            rating_final=rating,
        )

        if not pd_transform_rules or segmento not in pd_transform_rules:
            raise PdConfigurationError(
                "pd_transform_rules não informado para CONSUMIDOR_LE_5."
            )

        return calcular_pd_final_consumidor_le5(
            registro=registro,
            pd_faixas=pd_faixas,
            logger=logger,
        )

    raise PdCalculationError(
        f"Segmento PD não suportado para transformação: {segmento}"
    )
```


---

## `src/domain/credito/pd_validator.py`

- Linhas: 112
- SHA-256: `40c639c2d4b0bba831cd01bbe2c9a3f05fff180d39a8b6ca287b6e0ab180ff76`
- Classes: -
- Funções: validar_probabilidade, _is_blank, validar_insumos_pd

```python
"""Validação dos insumos do cálculo de PD ajustada."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from common.numeros import to_percentual_br
from domain.credito.pd_exceptions import PdInputValidationError, PdCalculationError


def validar_probabilidade(valor: Any) -> float | None:
    """Aplica regra de negócio: normaliza e garante range de [0, 1]."""
    perc = to_percentual_br(valor)
    if perc is None:
        return None
    if perc > 1.0:
        return None
    return perc


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    texto = str(value).strip().upper()
    return texto in {"", "N/A", "NA", "N.D.", "ND", "NONE", "NULL"}


def validar_insumos_pd(
    registro: dict[str, Any],
    segmento_pd: str,
) -> None:
    """Valida os insumos mínimos para cálculo de PD ajustada."""
    if not segmento_pd:
        raise PdInputValidationError("SEGMENTO_PD não informado.")
    
    if segmento_pd == "CONSUMIDOR_LE_5":
        if registro.get("SCORE_BUREAU") is None:
            raise PdInputValidationError("SCORE_BUREAU não informado para CONSUMIDOR_LE_5.")
        return

    pd_base_raw = registro.get("PROBABILIDADE_DEFAULT")
    pd_base = validar_probabilidade(pd_base_raw)

    if pd_base is None:
        raise PdInputValidationError("PROBABILIDADE_DEFAULT não informada.")

    if pd_base < 0:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT negativa: {pd_base_raw!r}"
        )

    if segmento_pd == "CGRUPO":
        agencia = registro.get("AGENCIA")
        nota_credito = registro.get("NOTA_CREDITO")
        rating_interno = registro.get(
            "RATING_FINAL") or registro.get("RATING_COPEL")

        tem_rating_publico = not _is_blank(
            agencia) and not _is_blank(nota_credito)
        tem_rating_interno = not _is_blank(rating_interno)

        if not tem_rating_publico and not tem_rating_interno:
            raise PdInputValidationError(
                "CGRUPO sem rating público (AGENCIA/NOTA_CREDITO) "
                "e sem rating interno (RATING_FINAL/RATING_COPEL)."
            )

    else:
        rating = (
            registro.get("RATING_COPEL")
            or registro.get("NOTA_CREDITO")
            or registro.get("RATING_FINAL")
        )

        if not _is_blank(rating):
            rating_normalizado = normalizar_texto(str(rating))
            ratings_validos = {"A", "B", "C", "D", "E"}

            if rating_normalizado is not None and rating_normalizado not in ratings_validos:
                raise PdInputValidationError(
                    f"Rating inválido para {segmento_pd}: {rating_normalizado!r}"
                )

    if segmento_pd in {"CPURA", "CGRUPO"}:
        tipo_comercializadora = normalizar_texto(
            str(registro.get("TIPO_COMERCIALIZADORA", ""))
        )
        if tipo_comercializadora not in {"CPURA", "CGRUPO"}:
            raise PdInputValidationError(
                "TIPO_COMERCIALIZADORA inválido ou ausente."
            )
    if segmento_pd == "CONSUMIDOR_GT_5":
        pd_base = registro.get("PROBABILIDADE_DEFAULT")
        rating = registro.get("RATING_FINAL") or registro.get("RATING_COPEL")

        if _is_blank(pd_base):
            raise PdCalculationError(
                "PROBABILIDADE_DEFAULT não informada para CONSUMIDOR_GT_5."
            )

        if _is_blank(rating):
            raise PdCalculationError(
                "RATING_FINAL/RATING_COPEL não informado para CONSUMIDOR_GT_5."
            )

        rating_norm = normalizar_texto(rating)
        if rating_norm not in {"A", "B", "C", "D", "E"}:
            raise PdCalculationError(
                f"Rating inválido para CONSUMIDOR_GT_5: {rating_norm!r}"
            )
        return
```


---

## `src/domain/credito/rating.py`

- Linhas: 112
- SHA-256: `db149ac548706330ff1be83d0db7801945334f4acbc14c2f1f812ba1f5f79772`
- Classes: -
- Funções: _calcular_rating_final_cpura, _obter_rating_pronto, calcular_rating_final

```python
"""Determinação do rating final para o cálculo de PD ajustada."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _calcular_rating_final_cpura(
    registro: dict[str, Any],
    cpura_score_faixas: dict[str, Any],
) -> str:
    """Calcula o rating final de CPURA a partir do SCORE_TOTAL."""
    score_total = registro.get("SCORE_TOTAL")

    if score_total is None:
        raise PdInputValidationError(
            "SCORE_TOTAL não informado para cálculo do rating de CPURA."
        )

    try:
        score_total = float(score_total)
    except (TypeError, ValueError) as exc:
        raise PdInputValidationError(
            f"SCORE_TOTAL inválido: {score_total!r}"
        ) from exc

    if not isinstance(cpura_score_faixas, dict) or not cpura_score_faixas:
        raise PdConfigurationError(
            "Configuração de score_faixas de CPURA ausente ou inválida."
        )

    for rating, faixa in cpura_score_faixas.items():
        try:
            score_min = float(faixa["min"])
            score_max = float(faixa["max"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Faixa de score incompleta para rating {rating}."
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                f"Faixa de score inválida para rating {rating}."
            ) from exc

        if score_min <= score_total <= score_max:
            return rating

    raise PdInputValidationError(
        f"SCORE_TOTAL fora das faixas esperadas para CPURA: {score_total}"
    )


def _obter_rating_pronto(
    registro: dict[str, Any],
    segmento_pd: str,
) -> str:
    """Obtém rating já existente no registro."""
    rating = (
        registro.get("RATING_COPEL")
        or registro.get("NOTA_CREDITO")
        or registro.get("RATING_FINAL")
    )

    if rating is None:
        raise PdInputValidationError(
            f"Registro sem rating para {segmento_pd}."
        )

    rating_final = normalizar_texto(rating)

    validos = {"A", "B","C", "D", "E"} if segmento_pd == "CGRUPO" else {
        "A", "B", "C", "D", "E", "F"
    }

    if rating_final not in validos:
        raise PdInputValidationError(
            f"Rating inválido para {segmento_pd}: {rating_final}"
        )

    return rating_final


def calcular_rating_final(
    registro: dict[str, Any],
    segmento_pd: str,
    pd_cpura_config: dict[str, Any] | None = None,
) -> str:
    """Determina o rating final conforme o segmento."""
    segmento_pd = str(segmento_pd).strip().upper()

    if segmento_pd == "CPURA":
        if not pd_cpura_config:
            raise PdConfigurationError(
                "pd_cpura_config não informado para cálculo do rating de CPURA."
            )

        score_faixas = pd_cpura_config.get("score_faixas")
        return _calcular_rating_final_cpura(
            registro=registro,
            cpura_score_faixas=score_faixas,
        )

    return _obter_rating_pronto(
        registro=registro,
        segmento_pd=segmento_pd,
    )
```


---

## `src/domain/credito/score_qualitativo.py`

- Linhas: 161
- SHA-256: `aad08bf27861e45ce5fc0e918916dc2256b5469dc30670d106ae310fc55bbbbe`
- Classes: -
- Funções: _obter_nota_auditoria, _obter_peso_nota, calcular_score_qualitativo_cpura

```python
"""Cálculo do score qualitativo para CPURA."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_nota_auditoria(
    auditor: Any,
    auditor_para_nota: dict[str, str],
) -> str:
    """Converte o auditor em nota qualitativa."""
    auditor_normalizado = normalizar_texto(auditor)

    if not auditor_normalizado:
        raise PdInputValidationError("AUDITOR não informado.")

    nota = auditor_para_nota.get(auditor_normalizado)

    if nota is None:
        raise PdInputValidationError(
            f"AUDITOR sem mapeamento qualitativo: {auditor!r}"
        )

    return nota


def _obter_peso_nota(
    nota: Any,
    nota_para_peso: dict[str, Any],
    nome_campo: str,
) -> float:
    """Obtém o peso numérico da nota qualitativa."""
    nota_normalizada = normalizar_texto(nota)

    if not nota_normalizada:
        raise PdInputValidationError(
            f"{nome_campo} não informada."
        )

    if nota_normalizada not in nota_para_peso:
        raise PdInputValidationError(
            f"{nome_campo} inválida: {nota!r}"
        )

    try:
        return float(nota_para_peso[nota_normalizada])
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            f"Peso inválido para nota {nota_normalizada}."
        ) from exc


def calcular_score_qualitativo_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score qualitativo de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando score qualitativo CPURA. CNPJ=%s",
                registro.get("CNPJ"),
            )

        nota_para_peso = score_cpura_config.get("nota_para_peso")
        pesos_qualitativos = score_cpura_config.get("pesos_qualitativos")
        auditor_para_nota = score_cpura_config.get("auditor_para_nota")

        if not isinstance(nota_para_peso, dict):
            raise PdConfigurationError(
                "Bloco 'nota_para_peso' ausente ou inválido."
            )

        if not isinstance(pesos_qualitativos, dict):
            raise PdConfigurationError(
                "Bloco 'pesos_qualitativos' ausente ou inválido."
            )

        if not isinstance(auditor_para_nota, dict):
            raise PdConfigurationError(
                "Bloco 'auditor_para_nota' ausente ou inválido."
            )

        nota_board = registro.get("NOTA_BOARD")
        nota_bureau = registro.get("NOTA_BUREAU")
        auditor = registro.get("AUDITOR")

        nota_auditoria = _obter_nota_auditoria(
            auditor,
            auditor_para_nota,
        )

        peso_board = _obter_peso_nota(
            nota_board,
            nota_para_peso,
            "NOTA_BOARD",
        )
        peso_bureau = _obter_peso_nota(
            nota_bureau,
            nota_para_peso,
            "NOTA_BUREAU",
        )
        peso_auditoria = _obter_peso_nota(
            nota_auditoria,
            nota_para_peso,
            "NOTA_AUDITORIA",
        )

        try:
            w_board = float(pesos_qualitativos["BOARD"])
            w_auditoria = float(pesos_qualitativos["AUDITORIA"])
            w_bureau = float(pesos_qualitativos["BUREAU"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Peso qualitativo ausente: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                "Pesos qualitativos inválidos."
            ) from exc

        score_qualitativo = (
            w_board * peso_board
            + w_auditoria * peso_auditoria
            + w_bureau * peso_bureau
        )

        resultado = {
            "NOTA_AUDITORIA": nota_auditoria,
            "PESO_BOARD": peso_board,
            "PESO_AUDITORIA": peso_auditoria,
            "PESO_BUREAU": peso_bureau,
            "SCORE_QUALITATIVO": score_qualitativo,
        }

        if logger is not None:
            logger.info(
                "Score qualitativo CPURA calculado. "
                "CNPJ=%s SCORE_QUALITATIVO=%s",
                registro.get("CNPJ"),
                score_qualitativo,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score qualitativo CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )
        raise
```


---

## `src/domain/credito/score_quantitativo.py`

- Linhas: 126
- SHA-256: `bd6033eeb004b4a1344f831f57d3a22934ff9682b0bfd048094cd72ba778e1cf`
- Classes: -
- Funções: _obter_peso_nota, calcular_score_quantitativo_cpura

```python
"""Cálculo do score quantitativo para CPURA."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_peso_nota(
    nota: Any,
    nota_para_peso: dict[str, Any],
    nome_campo: str,
) -> float:
    """Obtém o peso numérico da nota."""
    nota_normalizada = normalizar_texto(nota)

    if not nota_normalizada:
        raise PdInputValidationError(
            f"{nome_campo} não informada."
        )

    if nota_normalizada not in nota_para_peso:
        raise PdInputValidationError(
            f"{nome_campo} inválida: {nota!r}"
        )

    try:
        return float(nota_para_peso[nota_normalizada])
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            f"Peso inválido para nota {nota_normalizada}."
        ) from exc


def calcular_score_quantitativo_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score quantitativo de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando score quantitativo CPURA. CNPJ=%s",
                registro.get("CNPJ"),
            )

        nota_para_peso = score_cpura_config.get("nota_para_peso")
        pesos_quantitativos = score_cpura_config.get("pesos_quantitativos")

        if not isinstance(nota_para_peso, dict):
            raise PdConfigurationError(
                "Bloco 'nota_para_peso' ausente ou inválido."
            )

        if not isinstance(pesos_quantitativos, dict):
            raise PdConfigurationError(
                "Bloco 'pesos_quantitativos' ausente ou inválido."
            )

        nota_pd = registro.get("NOTA_PD")
        nota_fco_rol = registro.get("NOTA_FCO_ROL")
        nota_roe = registro.get("NOTA_ROE")
        nota_roa = registro.get("NOTA_ROA")

        peso_pd = _obter_peso_nota(nota_pd, nota_para_peso, "NOTA_PD")
        peso_fco_rol = _obter_peso_nota(
            nota_fco_rol,
            nota_para_peso,
            "NOTA_FCO_ROL",
        )
        peso_roe = _obter_peso_nota(nota_roe, nota_para_peso, "NOTA_ROE")
        peso_roa = _obter_peso_nota(nota_roa, nota_para_peso, "NOTA_ROA")

        try:
            w_pd = float(pesos_quantitativos["PD"])
            w_fco_rol = float(pesos_quantitativos["FCO_ROL"])
            w_roe = float(pesos_quantitativos["ROE"])
            w_roa = float(pesos_quantitativos["ROA"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Peso quantitativo ausente: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                "Pesos quantitativos inválidos."
            ) from exc

        score_quantitativo = (
            w_pd * peso_pd
            + w_fco_rol * peso_fco_rol
            + w_roe * peso_roe
            + w_roa * peso_roa
        )

        resultado = {
            "PESO_PD": peso_pd,
            "PESO_FCO_ROL": peso_fco_rol,
            "PESO_ROE": peso_roe,
            "PESO_ROA": peso_roa,
            "SCORE_QUANTITATIVO": score_quantitativo,
        }

        if logger is not None:
            logger.info(
                "Score quantitativo CPURA calculado. "
                "CNPJ=%s SCORE_QUANTITATIVO=%s",
                registro.get("CNPJ"),
                score_quantitativo,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score quantitativo CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )
        raise
```


---

## `src/domain/credito/score_total.py`

- Linhas: 49
- SHA-256: `e7afb903f278a5c07d4502a4c3b0b138edd5bbe3a89d50b1fce66d1138bc3553`
- Classes: -
- Funções: calcular_score_total_cpura

```python
"""Cálculo do score total de CPURA."""

from __future__ import annotations

from typing import Any

from domain.credito.pd_exceptions import PdInputValidationError


def calcular_score_total_cpura(
    score_quant_info: dict[str, Any],
    score_qual_info: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score total de CPURA."""
    try:
        score_quant = score_quant_info.get("SCORE_QUANTITATIVO")
        score_qual = score_qual_info.get("SCORE_QUALITATIVO")

        if score_quant is None:
            raise PdInputValidationError(
                "SCORE_QUANTITATIVO não informado."
            )

        if score_qual is None:
            raise PdInputValidationError(
                "SCORE_QUALITATIVO não informado."
            )

        score_total = float(score_quant) + float(score_qual)

        resultado = {
            "SCORE_TOTAL": score_total,
        }

        if logger is not None:
            logger.info(
                "Score total CPURA calculado. SCORE_TOTAL=%s",
                score_total,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score total CPURA."
            )
        raise
```


---

## `src/domain/credito/servico_override.py`

- Linhas: 96
- SHA-256: `ff968f5b595bcd3f3a1042cf3a0b70ef0f24aac6946f0e068fe9321c61ab110f`
- Classes: -
- Funções: processar_solicitacao_override

```python
"""Serviço de Gestão de Overrides e Exceções (Módulo de Governança)."""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from domain.enums import StatusAprovacao
from common.identificadores import normalizar_cnpj
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def processar_solicitacao_override(context: AppContext) -> dict[str, Any]:
    run_id = f"OVR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.governanca.override")

    input_dir = context.path("entradas") / "overrides" / "pendentes"
    input_dir.mkdir(parents=True, exist_ok=True)

    arquivos = list(input_dir.glob("*.csv")) + list(input_dir.glob("*.xlsx"))
    if not arquivos:
        return {"run_id": run_id, "processados": 0, "status": "SEM_DADOS"}

    campos_obrigatorios = [
        "CNPJ", "TIPO_OVERRIDE", "VALOR_ANTES", "VALOR_DEPOIS",
        "JUSTIFICATIVA", "EVIDENCIA", "SOLICITANTE", "APROVADOR", "DATA_EXPIRACAO"
    ]

    processados = []
    hoje = datetime.now()

    for arquivo in arquivos:
        try:
            if arquivo.suffix == ".csv":
                df = pd.read_csv(arquivo, sep=";", dtype=str)
            else:
                df = pd.read_excel(arquivo, dtype=str)

            registros = df.to_dict(orient="records")

            for idx, solicitacao in enumerate(registros):
                valido = True
                for campo in campos_obrigatorios:
                    if campo not in solicitacao or pd.isna(solicitacao[campo]) or str(solicitacao[campo]).strip() == "":
                        logger.warning("Campo '%s' ausente na linha %d. Rejeitado.", campo, idx)
                        valido = False
                        break
                if not valido:
                    continue

                res_cnpj = normalizar_cnpj(str(solicitacao["CNPJ"]))
                if not res_cnpj.valido:
                    logger.warning("CNPJ inválido no override: %s", solicitacao["CNPJ"])
                    continue
                
                solicitacao["CNPJ"] = res_cnpj.cnpj

                solicitante = str(solicitacao["SOLICITANTE"]).strip().upper()
                aprovador = str(solicitacao["APROVADOR"]).strip().upper()

                if solicitante == aprovador:
                    logger.warning("Conflito de Segregação (CNPJ %s): Solicitante = Aprovador.", solicitacao['CNPJ'])
                    continue

                expiracao = pd.to_datetime(solicitacao["DATA_EXPIRACAO"], errors="coerce")
                if pd.isna(expiracao) or expiracao < hoje:
                    logger.warning("Data de expiração inválida/passada (CNPJ %s).", solicitacao['CNPJ'])
                    continue

                registro = solicitacao.copy()
                registro["STATUS"] = StatusAprovacao.APROVADO.value
                registro["DATA_APROVACAO"] = hoje.isoformat(timespec="seconds")
                registro["RUN_ID"] = run_id
                processados.append(registro)

            target_dir = context.path("entradas") / "overrides" / "processadas"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.replace(target_dir / arquivo.name)
            
        except Exception:
            logger.exception("Erro no arquivo %s", arquivo.name)
            target_dir = context.path("entradas") / "overrides" / "rejeitadas"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.replace(target_dir / arquivo.name)

    if processados:
        silver_dir = context.path("silver") / "governanca_overrides"
        escrever_conjunto_de_dados_silver(
            records=processados,
            output_dir=silver_dir,
            filename=f"solicitacao_override_{run_id}"
        )

    logger.info("Overrides processados: %d.", len(processados))
    return {"run_id": run_id, "processados": len(processados), "status": "SUCESSO"}
```


---

## `src/domain/diagnostico/servico_diagnostico.py`

- Linhas: 129
- SHA-256: `93b0879564616de96223e741dd6ec77cd2f62eaeb804ddac28b98a72482fb458`
- Classes: -
- Funções: _carregar_catalogo, gerar_diagnostico

```python
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import os
from control.logger import obter_logger
from common.identificadores import normalizar_cnpj
from domain.diagnostico.servico_recuperacao import _encontrar_ficha_bronze

def _carregar_catalogo(catalog_path: Path) -> list[str]:
    """Retorna a lista de campos obrigatórios do catálogo JSON."""
    if not catalog_path.exists():
        return []
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    
    campos_obrigatorios = []
    fields = catalog.get("fields", {})
    for field_name, config in fields.items():
        if config.get("nature") == "DERIVED":
            continue
        if config.get("criticality") in ["GATE_ENGINE", "REQUIRED_FOR_CALCULATION"]:
            campos_obrigatorios.append(field_name)
            
    return campos_obrigatorios

def gerar_diagnostico(base_dir: str = ".") -> None:
    """Lê a Silver e gera a fila de pendências CSV."""
    base_path = Path(base_dir)
    data_atual = datetime.now().strftime("%Y%m%d")
    log_path = base_path / "LOGS" / "atualizacoes_manuais" / f"UI_MANUAL_{data_atual}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = obter_logger("bdc.ui.carga_manual.diagnostico", log_path)
    
    logger.info("Iniciando varredura da Silver para detecção de pendências...")
    
    saidas_dir = base_path / "SAIDAS"
    entradas_dir = base_path / "ENTRADAS"
    
    diagnostico_dir = base_path / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico"
    diagnostico_dir.mkdir(parents=True, exist_ok=True)
    
    fila_pendencias_path = diagnostico_dir / "fila_pendencias.csv"
    
    # Catálogos
    catalog_comercializadoras = entradas_dir / "control" / "quality" / "master_catalog_comercializadoras.json"
    catalog_consumidores = entradas_dir / "control" / "quality" / "master_catalog_consumidores.json"
    
    campos_com = _carregar_catalogo(catalog_comercializadoras)
    campos_cons = _carregar_catalogo(catalog_consumidores)
    
    pendencias = []
    
    # Comercializadoras
    silver_com_path = saidas_dir / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    if not silver_com_path.exists():
        silver_com_path = saidas_dir / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.csv"
        
    if silver_com_path.exists():
        if silver_com_path.suffix == '.csv':
            df_com = pd.read_csv(silver_com_path, sep=';', encoding='utf-8-sig')
        else:
            df_com = pd.read_parquet(silver_com_path)
            
        # Remove eventuais caracteres de BOM (Byte Order Mark) que corrompem o nome da primeira coluna (ex: \ufeffCNPJ)
        df_com.columns = [str(col).replace('\ufeff', '').strip() for col in df_com.columns]
            
        for _, row in df_com.iterrows():
            res_cnpj = normalizar_cnpj(row.get("CNPJ", ""))
            cnpj = res_cnpj.cnpj if res_cnpj.cnpj else str(row.get("CNPJ", ""))
            data_df = str(row.get("DATA_DEMONSTRACAO_FINANCEIRA", ""))
            empresa = str(row.get("SIGLA", row.get("EMPRESA", "")))
            ficha_path = _encontrar_ficha_bronze(cnpj, base_path)
            arquivo_str = str(ficha_path) if ficha_path else "Arquivo não localizado na Bronze"
            
            for campo in campos_com:
                val = row.get(campo)
                if pd.isna(val) or val is None or str(val).strip() == "":
                    pendencias.append({
                        "CNPJ": cnpj,
                        "DATA_DEMONSTRACAO_FINANCEIRA": data_df,
                        "EMPRESA": empresa,
                        "CAMPO_FALTANTE": campo,
                        "STATUS": "PENDENTE",
                        "ARQUIVO_ORIGEM": arquivo_str
                    })
                    
    # Consumidores
    silver_cons_path = saidas_dir / "silver" / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet"
    if not silver_cons_path.exists():
        silver_cons_path = saidas_dir / "silver" / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.csv"
        
    if silver_cons_path.exists():
        if silver_cons_path.suffix == '.csv':
            df_cons = pd.read_csv(silver_cons_path, sep=';', encoding='utf-8-sig')
        else:
            df_cons = pd.read_parquet(silver_cons_path)
            
        df_cons.columns = [str(col).replace('\ufeff', '').strip() for col in df_cons.columns]
            
        for _, row in df_cons.iterrows():
            res_cnpj = normalizar_cnpj(row.get("CNPJ", ""))
            cnpj = res_cnpj.cnpj if res_cnpj.cnpj else str(row.get("CNPJ", ""))
            data_df = str(row.get("DATA_DEMONSTRACAO_FINANCEIRA", ""))
            empresa = str(row.get("EMPRESA", ""))
            ficha_path = _encontrar_ficha_bronze(cnpj, base_path)
            arquivo_str = str(ficha_path) if ficha_path else "Arquivo não localizado na Bronze"
            
            for campo in campos_cons:
                val = row.get(campo)
                if pd.isna(val) or val is None or str(val).strip() == "":
                    pendencias.append({
                        "CNPJ": cnpj,
                        "DATA_DEMONSTRACAO_FINANCEIRA": data_df,
                        "EMPRESA": empresa,
                        "CAMPO_FALTANTE": campo,
                        "STATUS": "PENDENTE",
                        "ARQUIVO_ORIGEM": arquivo_str
                    })

    df_pendencias = pd.DataFrame(pendencias)
    if not df_pendencias.empty:
        # Remover duplicadas caso haja o mesmo CNPJ+DATA+CAMPO
        df_pendencias = df_pendencias.drop_duplicates(subset=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "CAMPO_FALTANTE"])
    else:
        df_pendencias = pd.DataFrame(columns=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA", "CAMPO_FALTANTE", "STATUS", "ARQUIVO_ORIGEM"])

    df_pendencias.to_csv(fila_pendencias_path, index=False, sep=";")
    logger.info("Diagnóstico concluído. %d pendências identificadas.", len(df_pendencias))
```


---

## `src/domain/diagnostico/servico_exportacao.py`

- Linhas: 68
- SHA-256: `9f7a16a9a8a441887fb2a3361c78a7fded397f13137d129830e25ad7b25eea81`
- Classes: -
- Funções: exportar_carga_manual

```python
import pandas as pd
from pathlib import Path
from datetime import datetime
from control.logger import obter_logger
from common.identificadores import normalizar_cnpj

def exportar_carga_manual(base_dir: str = ".") -> bool:
    """Exporta o rascunho para a pasta de atualizações manuais no formato oficial."""
    base_path = Path(base_dir)
    data_atual = datetime.now().strftime("%Y%m%d")
    log_path = base_path / "LOGS" / "atualizacoes_manuais" / f"UI_MANUAL_{data_atual}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = obter_logger("bdc.ui.carga_manual.exportacao", log_path)
    
    rascunho_path = base_path / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico" / "rascunho_carga_manual.csv"
    
    if not rascunho_path.exists():
        logger.warning("Rascunho não encontrado. Abortando exportação.")
        return False
        
    df = pd.read_csv(rascunho_path, sep=";")
    if df.empty:
        logger.warning("Rascunho vazio. Abortando exportação.")
        return False
        
    logger.info("Iniciando exportação de %d pendências do rascunho...", len(df))
        
    registros_carga = []
    
    for _, row in df.iterrows():
        # Converte para o Schema de Carga Manual
        # schema_carga_manual.json keys: CNPJ, DATA_DEMONSTRACAO_FINANCEIRA, CAMPO_AFETADO, 
        # VALOR_NOVO, MOTIVO, SOLICITANTE, TIPO_EVENTO, EVIDENCIA
        res_cnpj = normalizar_cnpj(row.get("CNPJ"))
        cnpj_norm = res_cnpj.cnpj if res_cnpj.cnpj else row.get("CNPJ")
        
        reg = {
            "CNPJ": cnpj_norm,
            "DATA_DEMONSTRACAO_FINANCEIRA": row.get("DATA_DEMONSTRACAO_FINANCEIRA"),
            "CAMPO_AFETADO": row.get("CAMPO_FALTANTE"),
            "VALOR_NOVO": row.get("VALOR_NOVO"),
            "MOTIVO": row.get("MOTIVO", "Complementação Assistida"),
            "SOLICITANTE": row.get("SOLICITANTE", "Operador de Qualidade"),
            "TIPO_EVENTO": row.get("TIPO_EVENTO", "COMPLEMENTACAO"),
            "EVIDENCIA": row.get("FONTE", "Desconhecida")
        }
        registros_carga.append(reg)
        
    df_export = pd.DataFrame(registros_carga)
    
    data_hoje = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = base_path / "ENTRADAS" / "atualizacoes_manuais" / "pendentes"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    export_path = export_dir / f"carga_manual_assistida_{data_hoje}.xlsx"
    
    # Força CNPJ como texto para evitar notação científica no Excel
    df_export["CNPJ"] = df_export["CNPJ"].astype(str)
    
    # Grava final
    df_export.to_excel(export_path, index=False, engine="openpyxl")
    logger.info("Carga manual gerada com sucesso: %s", export_path)
    
    # Limpa o rascunho após gerar
    rascunho_path.unlink()
    logger.info("Contrato Efêmero cumprido: Rascunho temporário excluído permanentemente.")
    
    return True
```


---

## `src/domain/diagnostico/servico_recuperacao.py`

- Linhas: 118
- SHA-256: `6efce87fd19448128d2fffe3974b4d8e69d80691df35db6fb32bb6327f084ec4`
- Classes: -
- Funções: _encontrar_ficha_bronze, _carregar_layouts_dinamico, recuperar_pendencias_automaticamente

```python
import pandas as pd
from pathlib import Path
from common.excel import abrir_pasta, fechar_pasta
from common.json import ler_json
from domain.fichas.extrator import extrair_registro_do_vencedor
import glob
import os
from control.logger import obter_logger
from datetime import datetime

def _encontrar_ficha_bronze(cnpj: str, base_dir: Path) -> Path | None:
    """Busca o arquivo mais recente da ficha na camada Bronze para um CNPJ."""
    # A estrutura bronze geralmente tem o CNPJ na pasta ou no nome do arquivo
    # Vamos buscar iterativamente (sem assumir a estrutura profunda de pastas)
    bronze_dir = base_dir / "SAIDAS" / "bronze"
    if not bronze_dir.exists():
        return None
        
    cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
    if not cnpj_limpo:
        return None
        
    candidatos = []
    # Busca recursiva rápida apenas nas pastas raw
    for raw_dir in ["fichas_comercializadoras_raw", "fichas_consumidores_raw"]:
        search_path = bronze_dir / raw_dir
        if search_path.exists():
            for root, _, files in os.walk(search_path):
                for file in files:
                    if cnpj_limpo in file.replace(".", "").replace("-", "").replace("/", ""):
                        candidatos.append(Path(root) / file)
                        
    if not candidatos:
        return None
        
    # Ordena pelo tempo de modificação para pegar a mais recente
    candidatos.sort(key=os.path.getmtime, reverse=True)
    return candidatos[0]

def _carregar_layouts_dinamico(base_dir: Path, is_comercializadora: bool) -> dict:
    """Carrega os layouts sem precisar do AppContext completo."""
    layouts = {}
    control_dir = base_dir / "ENTRADAS" / "control" / "layouts"
    prefix = "layout_ficha_comercializadora" if is_comercializadora else "layout_ficha_consumidor"
    max_ver = 7 if is_comercializadora else 3
    
    for v in range(1, max_ver + 1):
        file_path = control_dir / f"{prefix}_v{v}.json"
        if file_path.exists():
            k = f"padrao_{v}" if is_comercializadora else f"v{v}"
            layouts[k] = ler_json(file_path)
            
    return layouts

def recuperar_pendencias_automaticamente(base_dir: str = ".") -> None:
    """Tenta recuperar dados ausentes re-executando a extração nas fichas Bronze."""
    base_path = Path(base_dir)
    data_atual = datetime.now().strftime("%Y%m%d")
    log_path = base_path / "LOGS" / "atualizacoes_manuais" / f"UI_MANUAL_{data_atual}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = obter_logger("bdc.ui.carga_manual.recuperacao", log_path)
    
    fila_path = base_path / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico" / "fila_pendencias.csv"
    
    if not fila_path.exists():
        logger.warning("Fila de pendências não encontrada.")
        return
        
    df = pd.read_csv(fila_path, sep=";")
    if df.empty:
        logger.info("Fila vazia. Nada a recuperar.")
        return
        
    logger.info("Iniciando tentativa de recuperação automática de %d pendências possíveis...", len(df))
        
    # Carrega catálogos
    cat_com = ler_json(base_path / "ENTRADAS" / "control" / "quality" / "master_catalog_comercializadoras.json")
    cat_cons = ler_json(base_path / "ENTRADAS" / "control" / "quality" / "master_catalog_consumidores.json")
    
    layouts_com = _carregar_layouts_dinamico(base_path, True)
    layouts_cons = _carregar_layouts_dinamico(base_path, False)
    
    recuperados = 0

    for idx, row in df.iterrows():
        if row["STATUS"] != "PENDENTE":
            continue
            
        cnpj = str(row["CNPJ"])
        campo = str(row["CAMPO_FALTANTE"])
        
        ficha_path = _encontrar_ficha_bronze(cnpj, base_path)
        if not ficha_path:
            continue
            
        is_comercializadora = "comercializadoras" in str(ficha_path)
        layouts = layouts_com if is_comercializadora else layouts_cons
        master_catalog = cat_com if is_comercializadora else cat_cons
        
        workbook = None
        try:
            workbook = abrir_pasta(ficha_path)
            raw_record, _, _ = extrair_registro_do_vencedor(workbook, layouts, master_catalog)
            
            valor_extraido = raw_record.get(campo)
            if valor_extraido is not None and str(valor_extraido).strip() != "":
                df.at[idx, "STATUS"] = "RECUPERADO_AUTOMATICAMENTE"
                df.at[idx, "VALOR_RECUPERADO"] = valor_extraido
                recuperados += 1
                
        except Exception:
            pass
        finally:
            if workbook:
                fechar_pasta(workbook)

    df.to_csv(fila_path, index=False, sep=";")
    logger.info("Recuperação automática concluída. %d valores resgatados da Bronze.", recuperados)
```


---

## `src/domain/enums.py`

- Linhas: 126
- SHA-256: `a8353187a79b4c8a87f890023a0204025f5c4beb7feae8be5c96b9c2b5f3b253`
- Classes: TipoFicha, LoadMode, StatusIngestao, StatusClassificacao, StatusExtracao, SegmentoMetodologico, TipoAnalise, SeveridadeAlerta, StatusGarantia, StatusAnalise, StatusDocumento, StatusAlerta, StatusAprovacao
- Funções: -

```python
"""Domínios controlados e enumeradores do sistema BDC."""

from enum import Enum, unique


@unique
class TipoFicha(str, Enum):
    """Domínio para os tipos de fichas processadas."""
    COMERCIALIZADORA = "COMERCIALIZADORA"
    CONSUMIDOR = "CONSUMIDOR"


@unique
class LoadMode(str, Enum):
    """Domínio para os modos de carga do orquestrador."""
    INCREMENTAL = "incremental"
    REPROCESS = "reprocess"


@unique
class StatusIngestao(str, Enum):
    """Domínio para o status de movimentação dos arquivos na camada Bronze."""
    INICIADO = "INICIADO"
    SUCESSO = "SUCESSO"
    ERRO = "ERRO"
    REJEITADO = "REJEITADO"


@unique
class StatusClassificacao(str, Enum):
    """Domínio para os resultados do motor de classificação de layouts."""
    CLASSIFICADO = "CLASSIFICADO"
    REJEITADO = "REJEITADO"
    NAO_CLASSIFICADO = "NAO_CLASSIFICADO"


@unique
class StatusExtracao(str, Enum):
    """Domínio detalhado para os estados de extração e validação técnica."""
    NAO_EXECUTADO = "NAO_EXECUTADO"
    SUCESSO = "SUCESSO"
    ERRO = "ERRO"
    ERRO_VALIDACAO = "ERRO_VALIDACAO"
    ERRO_DUPLICIDADE_HASH = "ERRO_DUPLICIDADE_HASH"
    ERRO_DUPLICIDADE_NEGOCIO = "ERRO_DUPLICIDADE_NEGOCIO"
    ERRO_PROCESSAMENTO = "ERRO_PROCESSAMENTO"
    ERRO_LAYOUT = "ERRO_LAYOUT"
    ERRO_SEM_CNPJ = "ERRO_SEM_CNPJ"
    ERRO_CNPJ_INVALIDO = "ERRO_CNPJ_INVALIDO"


@unique
class SegmentoMetodologico(str, Enum):
    """Domínio das segmentações metodológicas de crédito."""
    CPURA = "CPURA"
    CGRUPO = "CGRUPO"
    CONSUMIDOR_GT_5 = "CONSUMIDOR_GT_5"
    CONSUMIDOR_LE_5 = "CONSUMIDOR_LE_5"


@unique
class TipoAnalise(str, Enum):
    """Domínio para a origem ou tipo de análise gerada."""
    AUTOMATICA = "AUTOMATICA"
    MANUAL = "MANUAL"
    MANUAL_AJUSTADA = "MANUAL_AJUSTADA"


@unique
class SeveridadeAlerta(str, Enum):
    """Domínio para a classificação de alertas do sistema."""
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"
    
@unique
class StatusGarantia(str, Enum):
    """Domínio para os estados de vigência de garantias (§6.8)."""
    VIGENTE = "VIGENTE"
    PROXIMA_VENCIMENTO = "PROXIMA_VENCIMENTO"
    VENCIDA = "VENCIDA"
    CANCELADA = "CANCELADA"
    NAO_ELEGIVEL = "NAO_ELEGIVEL"


@unique
class StatusAnalise(str, Enum):
    """Domínio para o ciclo de vida de uma análise de crédito (§4.2, Apêndice A)."""
    VIGENTE = "VIGENTE"
    PROXIMA_VENCIMENTO = "PROXIMA_VENCIMENTO"
    VENCIDA = "VENCIDA"
    EM_RENOVACAO = "EM_RENOVACAO"
    SUSPENSA = "SUSPENSA"


@unique
class StatusDocumento(str, Enum):
    """Domínio para o estado de processamento de um documento/ficha (§4.2, Apêndice A)."""
    DESCOBERTO = "DESCOBERTO"
    EM_STAGING = "EM_STAGING"
    INGERIDO = "INGERIDO"
    CLASSIFICADO = "CLASSIFICADO"
    EXTRAIDO = "EXTRAIDO"
    VALIDADO = "VALIDADO"
    PUBLICADO = "PUBLICADO"
    PENDENTE = "PENDENTE"
    REJEITADO = "REJEITADO"


@unique
class StatusAlerta(str, Enum):
    """Domínio para os estados de resolução de alertas (§6.10)."""
    ABERTO = "ABERTO"
    EM_TRATAMENTO = "EM_TRATAMENTO"
    RESOLVIDO = "RESOLVIDO"
    IGNORADO = "IGNORADO"


@unique
class StatusAprovacao(str, Enum):
    """Domínio para o fluxo de aprovação de carga manual e overrides (§11.7)."""
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"
    EXPIRADO = "EXPIRADO"
```


---

## `src/domain/fichas/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/fichas/derivador_financeiro.py`

- Linhas: 62
- SHA-256: `d6750482cec091cee71487d8df95cae7e5c32c50603e8639a1e9dfa732f710ad`
- Classes: -
- Funções: divisao_segura, calcular_indicadores_derivados

```python
import logging

logger = logging.getLogger(__name__)

def divisao_segura(num, den):
    if num is None or den is None:
        return None
    try:
        f_num = float(num)
        f_den = float(den)
        if f_den == 0.0:
            return None
        return f_num / f_den
    except (ValueError, TypeError):
        return None

def calcular_indicadores_derivados(record: dict) -> dict:
    ativo_circulante = record.get("ATIVO_CIRCULANTE_AJUSTADO")
    passivo_circulante = record.get("PASSIVO_CIRCULANTE_AJUSTADO")
    ativo_total = record.get("ATIVO_TOTAL_AJUSTADO")
    passivo_nao_circulante = record.get("PASSIVO_NAO_CIRCULANTE_FINANCEIRO_AJUSTADO")
    lucro_liquido = record.get("LUCRO_LIQUIDO")
    patrimonio_liquido = record.get("PATRIMONIO_LIQUIDO")
    fluxo_caixa = record.get("FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS")
    
    rol = record.get("ROL")
    vendas = record.get("VENDAS_LIQUIDAS")
    receita_base = rol if rol is not None else vendas

    if record.get("AC_PC") is None:
        val = divisao_segura(ativo_circulante, passivo_circulante)
        if val is not None:
            record["AC_PC"] = val
            
    if record.get("AT_PT") is None:
        if passivo_circulante is not None and passivo_nao_circulante is not None:
            passivo_total = float(passivo_circulante) + float(passivo_nao_circulante)
            val = divisao_segura(ativo_total, passivo_total)
            if val is not None:
                record["AT_PT"] = val
                
    if record.get("ROA") is None:
        val = divisao_segura(lucro_liquido, ativo_total)
        if val is not None:
            record["ROA"] = val
            
    if record.get("ROE") is None:
        val = divisao_segura(lucro_liquido, patrimonio_liquido)
        if val is not None:
            record["ROE"] = val
            
    if record.get("FCO") is None:
        val = divisao_segura(fluxo_caixa, receita_base)
        if val is not None:
            record["FCO"] = val
            
    if record.get("LUCRO_LIQUIDO_SOBRE_ROL") is None:
        val = divisao_segura(lucro_liquido, receita_base)
        if val is not None:
            record["LUCRO_LIQUIDO_SOBRE_ROL"] = val
            
    return record
```


---

## `src/domain/fichas/extrator.py`

- Linhas: 469
- SHA-256: `626ac496779a5f0fc2f8f9d371d2bb858e56b36aa1be9efba6a1df9069d8a088`
- Classes: LeitorPlanilha
- Funções: __init__, do_workbook, ler_celula, analisar_data_com_seguranca, valor_extraido_limpo, _tipo_extraido_valido, busca_omnidirecional, extrair_registro, avaliar_vencedor_por_grid, norm_tab, extrair_registro_do_vencedor

```python
from __future__ import annotations

import re
import math
import time
import logging
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from openpyxl.utils.datetime import from_excel
from openpyxl.utils import get_column_letter
from openpyxl.utils.cell import coordinate_to_tuple
from common.nulos import is_nulo_textual
from common.texto import normalizar_texto

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

logger = logging.getLogger(__name__)

class LeitorPlanilha:
    """Representação intermediária de uma planilha, para leitura independente de I/O."""
    def __init__(self, abas_grid: dict[str, list[tuple]], aba_ativa: str = None):
        self.abas_grid = abas_grid
        self.abas_nomes = list(abas_grid.keys())
        self.aba_ativa = aba_ativa if aba_ativa else (self.abas_nomes[0] if self.abas_nomes else "")

    @classmethod
    def do_workbook(cls, workbook) -> LeitorPlanilha:
        grid = {}
        aba_ativa = workbook.active.title if workbook.active else None
        for sheet_name in workbook.sheetnames:
            ws = workbook[sheet_name]
            grid[sheet_name] = list(ws.iter_rows(min_row=1, max_row=150, min_col=1, max_col=30, values_only=True))
        return cls(grid, aba_ativa)

    def ler_celula(self, aba: str, cell_ref: str) -> Any:
        if aba not in self.abas_grid:
            return None
        try:
            row, col = coordinate_to_tuple(cell_ref)
            grid = self.abas_grid[aba]
            if 0 <= row - 1 < len(grid) and 0 <= col - 1 < len(grid[row - 1]):
                return grid[row - 1][col - 1]
            return None
        except Exception:
            return None

def analisar_data_com_seguranca(date_val: Any) -> Optional[datetime]:
    if isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, (int, float)):
        if 1990 <= date_val <= 2100:
            return datetime(int(date_val), 12, 31)
        try:
            return from_excel(date_val)
        except Exception:
            return None
    if isinstance(date_val, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_val.strip(), fmt)
            except ValueError:
                pass
    return None

def valor_extraido_limpo(val: Any, data_type: Optional[str] = None) -> Any:
    """Normalização puramente de extração."""
    if val is None:
        return None
    
    dt_str = str(data_type).lower() if data_type else ""
    
    if isinstance(val, str):
        s_upper = val.strip().upper()
        
        if not s_upper or s_upper.startswith("#") or is_nulo_textual(val) or s_upper == "-":
            return None

    if any(t in dt_str for t in ("float", "num", "dec", "int", "moeda", "percent", "taxa", "valor", "score")):
        if isinstance(val, (int, float)):
            if math.isnan(val) or math.isinf(val):
                return None
            return float(val)
        
        clean = str(val).strip()
        is_percent = "%" in clean
        
        if clean.startswith("(") and clean.endswith(")"):
            clean = "-" + clean[1:-1].strip()
        
        clean = re.sub(r"[^\d\,\.\-eE+]", "", clean)
        
        if not clean:
            return None
            
        last_comma = clean.rfind(",")
        last_dot = clean.rfind(".")
        
        try:
            if last_comma > last_dot:
                clean = clean.replace(".", "").replace(",", ".")
            elif last_dot > last_comma:
                if "," in clean:
                    clean = clean.replace(",", "")
                else:
                    if clean.count(".") > 1:
                        clean = clean.replace(".", "")
                    else:
                        parts = clean.split(".")
                        if len(parts) > 1 and len(parts[1]) == 3 and not any(t in dt_str for t in ("percent", "taxa")) and not is_percent:
                            clean = clean.replace(".", "")
            
            val_float = float(clean)

            if is_percent:
                val_float = val_float / 100.0
                
            return val_float
        except ValueError:
            return None

    if any(t in dt_str for t in ("date", "data")):
        return analisar_data_com_seguranca(val)

    if isinstance(val, float) and val.is_integer():
        val = int(val) 
    return str(val).strip()

def _tipo_extraido_valido(val: Any, data_type: str, field_name: str = "") -> bool:
    if val is None:
        return False
        
    dt_str = str(data_type).lower() if data_type else ""
    fn_lower = field_name.lower()
    
    if any(t in dt_str for t in ("float", "num", "dec", "int", "moeda", "percent", "taxa", "valor", "score", "pd")):
        if not isinstance(val, (int, float)):
            return False
            
        if val > 10000000 and str(int(val)).startswith(("20", "31", "30", "01")):
            return False

        campos_nao_zeraveis = (
            "ativo_total", "passivo_circulante", "vendas_liquidas", 
            "probabilidade_default", "pd", "patrimonio_liquido", "rol"
        )
        if val == 0.0 and any(k in fn_lower for k in campos_nao_zeraveis):
            return False
            
        campos_indicadores = ("roa", "roe", "fco", "fco_rol", "margem")
        if val == -10.0 and any(k in fn_lower for k in campos_indicadores):
            return False

        if any(k in fn_lower for k in ("probabilidade", "pd")):
            if val < 0.0 or val > 1.0:
                return False

        campos_de_balanco = ("ativo", "passivo", "patrimonio", "receita", "rol", "lucro", "fluxo", "fco")
        if any(k in fn_lower for k in campos_de_balanco):
            if val > 50000000000.0 or val < -50000000000.0:
                return False
                
        return True

    if any(t in dt_str for t in ("date", "data")):
        if isinstance(val, datetime):
            if 1990 <= val.year <= datetime.now().year + 10:
                return True
        return False
        
    if isinstance(val, str):
        v = val.lower().strip()
        if not v or v in ("tipo", "valor", "data", "descrição", "ajustado", "-", "0"):
            return False
            
        if len(v) > 60 and "endereco" not in fn_lower and "endereço" not in fn_lower:
            return False
            
        if fn_lower in ("auditor", "empresa", "sigla") and v.replace(".", "").replace(",", "").isdigit():
            return False
            
        if "agencia" in fn_lower or "agência" in fn_lower:
            if not any(k in v for k in ("fitch", "mood", "s&p", "sp", "standard")): 
                return False
                
        if "nota" in fn_lower or "rating" in fn_lower:
            if len(v) > 5 or any(k in v for k in ("menor", "qualidade", "classificação", "agência", "risco")): 
                return False
                
        if "auditor" in fn_lower:
            if len(v) > 40: return False
            
    return True

def busca_omnidirecional(leitor: LeitorPlanilha, search_pattern: str, data_type: str, sheet_hint: str = None, field_name: str = "", offset_col: int = None, offset_row: int = None) -> Tuple[Any, dict]:
    try:
        regex = re.compile(search_pattern, re.IGNORECASE)
    except re.error:
        return None, {}

    sheet_names = leitor.abas_nomes
    if sheet_hint:
        hint_clean = str(sheet_hint).replace(" ", "").lower()
        sheet_names = sorted(sheet_names, key=lambda x: 0 if hint_clean in x.replace(" ", "").lower() else 1)

    for sheet_name in sheet_names:
        grid = leitor.abas_grid.get(sheet_name, [])
        for r_idx, row_tuple in enumerate(grid):
            for c_idx, cell_value in enumerate(row_tuple):
                if cell_value and isinstance(cell_value, str):
                    if regex.search(cell_value.strip()):
                        targets = []
                        if offset_col is not None or offset_row is not None:
                            o_col = int(offset_col) if offset_col is not None else 0
                            o_row = int(offset_row) if offset_row is not None else 0
                            targets.append((r_idx + o_row, c_idx + o_col))
                            
                        default_targets = [(r_idx, c_idx + offset) for offset in range(1, 7)]
                        default_targets.extend([(r_idx + offset, c_idx) for offset in range(1, 3)])
                        
                        for dt in default_targets:
                            if dt not in targets:
                                targets.append(dt)
                        
                        for tr, tc in targets:
                            if 0 <= tr < len(grid) and 0 <= tc < len(grid[tr]):
                                raw_val = grid[tr][tc]
                                cleaned_val = valor_extraido_limpo(raw_val, data_type)
                                
                                if cleaned_val is not None and _tipo_extraido_valido(cleaned_val, data_type, field_name):
                                    col_letter = get_column_letter(tc + 1)
                                    coord = f"{col_letter}{tr + 1}"
                                    return cleaned_val, {
                                        "celula_origem": coord,
                                        "aba_origem": sheet_name,
                                        "metodo": "omnidirectional_regex"
                                    }
    return None, {}

def extrair_registro(leitor: LeitorPlanilha, layout_schema: Dict[str, Any], master_catalog: Dict[str, Any] = None, allow_semantic: bool = True) -> Tuple[Dict[str, Any], List[dict[str, Any]]]:
    extracted_data = {}
    metadata_list = []
    
    fields_to_extract = {}
    max_score = 0.0
    gates_to_check = []
    
    if not master_catalog or "fields" not in master_catalog:
        raise ValueError("O master_catalog é obrigatório e deve conter 'fields'.")

    for mc_field, mc_config in master_catalog["fields"].items():
        if mc_config.get("nature") == "OBSERVED":
            fields_to_extract[mc_field] = dict(mc_config)
            max_score += float(mc_config.get("weight", 0))
            if mc_config.get("criticality") == "GATE_ENGINE":
                gates_to_check.append(mc_field)
        
    score_obtido = 0.0

    for field_name, field_config in fields_to_extract.items():
        data_type = field_config.get("data_type") or field_config.get("type")
        if not data_type:
            fn_lower = field_name.lower()
            if any(t in fn_lower for t in ("ativo", "passivo", "lucro", "patrimonio", "capital", "venda", "receita", "lair", "lajir", "fco", "fluxo", "probabilidade", "pd", "rol", "reserva", "imposto", "resultado", "score", "ac_pc", "at_pt", "mtm", "dividendos")):
                data_type = "float"
            elif any(t in fn_lower for t in ("data", "dt")):
                data_type = "date"
            else:
                data_type = "string"
                
        LEGADO_MAPEAMENTO = {
            "FCO": ["SCORE_FCO_ROL", "FCO_ROL", "MARGEM_FLUXO_CAIXA"],
            "ROA": ["SCORE_ROA"],
            "ROE": ["SCORE_ROE"],
            "PATRIMONIO_LIQUIDO": ["PL", "TOTAL_PATRIMONIO_LIQUIDO"],
            "ATIVO_TOTAL_AJUSTADO": ["ATIVO_TOTAL", "TOTAL_ATIVOS"],
            "ATIVO_CIRCULANTE_AJUSTADO": ["ATIVO_CIRCULANTE"],
            "PASSIVO_CIRCULANTE_AJUSTADO": ["PASSIVO_CIRCULANTE"],
            "PASSIVO_NAO_CIRCULANTE_FINANCEIRO_AJUSTADO": ["PASSIVO_NAO_CIRCULANTE", "PASSIVO_N_CIRCULANTE"],
            "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS": ["FCO", "FLUXO_DE_CAIXA_OPERACIONAL"],
            "LUCRO_LIQUIDO": ["RESULTADO_LIQUIDO", "LUCRO_PREJUIZO"],
            "ROL": ["RECEITA_OPERACIONAL_LIQUIDA", "RECEITA_LIQUIDA"]
        }

        layout_field_config = layout_schema.get("field_map", {}).get(field_name)
        
        if not layout_field_config and field_name in LEGADO_MAPEAMENTO:
            for alias in LEGADO_MAPEAMENTO[field_name]:
                layout_field_config = layout_schema.get("field_map", {}).get(alias)
                if layout_field_config:
                    break
                    
        layout_field_config = layout_field_config or {}
        
        sheet_hint = layout_field_config.get("sheet") or field_config.get("sheet")
        offset_col = layout_field_config.get("offset_col")
        offset_row = layout_field_config.get("offset_row")
        
        celula_estatica = layout_field_config.get("value_cell") or layout_field_config.get("cell") or field_config.get("value_cell") or field_config.get("cell")
        
        val = None
        meta = {
            "campo": field_name,
            "aba_origem": None,
            "celula_origem": None,
            "metodo": "falha_extracao",
            "valor": None
        }
        if celula_estatica and str(celula_estatica).strip() not in ("0", ""):
            try:
                aba_estatica = leitor.aba_ativa
                if sheet_hint:
                    hint_clean = str(sheet_hint).replace(" ", "").lower()
                    for aba_real in leitor.abas_nomes:
                        if hint_clean in aba_real.replace(" ", "").lower():
                            aba_estatica = aba_real
                            break

                raw_val = leitor.ler_celula(aba_estatica, celula_estatica)
                clean_val = valor_extraido_limpo(raw_val, data_type)
                if clean_val is not None and _tipo_extraido_valido(clean_val, data_type, field_name):
                    val = clean_val
                    meta.update({
                        "aba_origem": aba_estatica,
                        "celula_origem": celula_estatica,
                        "metodo": "estatico_layout",
                        "valor": val
                    })
            except Exception:
                pass
                
        field_allow_semantic = field_config.get("allow_semantic", True)

        if val is None and allow_semantic and field_allow_semantic:
            patterns = field_config.get("search_patterns")
            if patterns and isinstance(patterns, list) and len(patterns) > 0:
                search_pattern = "|".join(patterns)
            else:
                search_pattern = field_name.replace("_", r"\s*")
                    
            val_dinamico, meta_inf = busca_omnidirecional(
                leitor, 
                search_pattern, 
                data_type, 
                sheet_hint, 
                field_name, 
                offset_col=offset_col,
                offset_row=offset_row
            )
            if val_dinamico is not None:
                val = val_dinamico
                meta.update({
                    "aba_origem": meta_inf.get("aba_origem"),
                    "celula_origem": meta_inf.get("celula_origem"),
                    "metodo": meta_inf.get("metodo", "omnidirectional_regex"),
                    "valor": val
                })

        value_mapping = field_config.get("value_mapping")
        if val is not None and value_mapping:
            val_upper = str(val).strip().upper()
            val = value_mapping.get(val_upper, val)
            
        field_enum = field_config.get("enum")
        if val is not None and field_enum and isinstance(field_enum, list):
            if str(val).strip().upper() not in [str(e).strip().upper() for e in field_enum if e is not None]:
                val = None
                meta["metodo"] = "rejeitado_por_enum"

        extracted_data[field_name] = val
        if meta["metodo"] != "falha_extracao":
            meta["valor"] = val
            metadata_list.append(meta)
            
        if val is not None:
            score_obtido += float(field_config.get("weight", 0))

    score = (score_obtido / max_score) * 100 if max_score > 0 else 0
    extracted_data["INTEGRIDADE_EXTRAIDA_PERCENTUAL"] = round(score, 2)
    
    falha_gate = False
    for gate in gates_to_check:
        if extracted_data.get(gate) is None:
            falha_gate = True
            logger.debug("[GATE_ENGINE] Layout candidato descartado. Campo %s (GATE) ausente.", gate)
            break
            
    extracted_data["_FALHA_GATE_CRITICO"] = falha_gate
    
    if falha_gate:
        score = 0.0
        extracted_data["INTEGRIDADE_EXTRAIDA_PERCENTUAL"] = 0.0
        logger.debug("[INTEGRIDADE] Layout candidato recusado: Falha no GATE Crítico.")
    elif score >= 40.0:
        logger.debug("[INTEGRIDADE] Layout candidato atingiu %.2f%% de integridade.", score)
    else:
        logger.debug("[INTEGRIDADE] Layout candidato recusado: baixa integridade (%.2f%%).", score)

    return extracted_data, metadata_list

def avaliar_vencedor_por_grid(leitor: LeitorPlanilha, layouts: Dict[str, Any], master_catalog: Dict[str, Any] = None) -> Tuple[Dict[str, Any], List[dict[str, Any]], str]:
    

    if not master_catalog or "fields" not in master_catalog:
        raise ValueError("master_catalog é obrigatório.")

    expected_tabs_raw = set()
    for _, l_schema in layouts.items():
        if "expected_tabs" in l_schema:
            expected_tabs_raw.update(l_schema["expected_tabs"])
            
    if not expected_tabs_raw:
        expected_tabs_raw = {
            "V0", "Para_Limite_Comercializadoras", "Premissas", 
            "FichaIndividual", "Memória de Cálculo", "Conf. Puras_DRE", 
            "Dados Gerais e Qualitativos", "DRE", "Dem.Fin."
        }
    
    def norm_tab(t: str) -> str:
        s = normalizar_texto(t, caixa_alta=True, remover_acentuacao=True)
        return s.replace(" ", "") if s else ""
        
    expected_tabs_norm = {norm_tab(t) for t in expected_tabs_raw}
    workbook_tabs_norm = {norm_tab(t) for t in leitor.abas_nomes}
    
    if not expected_tabs_norm.intersection(workbook_tabs_norm):
        logger.warning(f"[VETO] Documento rejeitado. Nenhuma aba bate com as abas de layout: {leitor.abas_nomes}")
        return {}, [], "DOC_001_ESTRUTURA_INCOMPATIVEL"

    aba_ativa = leitor.aba_ativa
    linhas_lidas = len(leitor.abas_grid.get(aba_ativa, []))
    colunas_lidas = len(leitor.abas_grid.get(aba_ativa, [])[0]) if linhas_lidas else 0
    
    logger.info("Extração (Schema): Arquivo lido. %s colunas, %s linhas identificadas na aba '%s'.", colunas_lidas, linhas_lidas, aba_ativa)

    layouts_to_test = list(layouts.items())
    allow_semantic = True

    melhor_score = -1.0
    vencedor_dados = {}
    vencedor_meta = []
    vencedor_nome = "NENHUM"

    inicio_extracao = time.perf_counter()
    
    for layout_name, layout_schema in layouts_to_test:
        extracted, metadata = extrair_registro(leitor, layout_schema, master_catalog, allow_semantic=allow_semantic)
        score = extracted.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        
        if score > melhor_score:
            melhor_score = score
            vencedor_dados = extracted
            vencedor_meta = metadata
            vencedor_nome = layout_name

    duracao_forca_bruta_ms = (time.perf_counter() - inicio_extracao) * 1000

    logger.info(
        "[CHAMPION] Torneio Força Bruta finalizado em %.1f ms. Vencedor: '%s' com score de %.2f%%.", 
        duracao_forca_bruta_ms, vencedor_nome, melhor_score
    )

    return vencedor_dados, vencedor_meta, vencedor_nome


def extrair_registro_do_vencedor(workbook: Any, layouts: Dict[str, Any], master_catalog: Dict[str, Any] = None) -> Tuple[Dict[str, Any], List[dict[str, Any]], str]:
    """Wrapper legado para manter compatibilidade com consumidores antigos."""
    leitor = LeitorPlanilha.do_workbook(workbook)
    return avaliar_vencedor_por_grid(leitor, layouts, master_catalog)
```


---

## `src/domain/fichas/validador.py`

- Linhas: 275
- SHA-256: `a9916ffc8f3333679050702c721bf34a81d5242f27efde2d54d50db6b1282792`
- Classes: DomainRuleEngine
- Funções: _is_empty, __init__, validate, validar_schema, validar_registro, validar_registro_consumidor

```python
"""Validação técnica e de domínio unificada dos registros extraídos."""

from __future__ import annotations
from typing import Any

def _is_empty(value: Any) -> bool:
    """Indica se o valor deve ser tratado como vazio."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False

class DomainRuleEngine:
    """Motor unificado que aplica validações nativas e regras do JSON em um único passo."""

    def __init__(self, quality_rules: dict[str, Any] | None = None):
        self.quality_rules = quality_rules or {}
        self.dynamic_rules = self.quality_rules.get("rules", [])

    def validate(
        self, record: dict[str, Any], required_fields: list[str]
    ) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        for field in required_fields:
            if _is_empty(record.get(field)):
                errors.append(f"Campo obrigatório ausente: {field}")

        pl = record.get("PATRIMONIO_LIQUIDO")
        if _is_empty(pl):
            warnings.append("PATRIMONIO_LIQUIDO não informado.")
        elif str(pl).upper() != "NAO_APLICAVEL" and not isinstance(pl, (int, float)):
            errors.append("PATRIMONIO_LIQUIDO inválido: valor não numérico.")


        has_pd_rule = any(r.get("field") == "PROBABILIDADE_DEFAULT" for r in self.dynamic_rules)
        if not has_pd_rule and "PROBABILIDADE_DEFAULT" in record:
            pd_val = record.get("PROBABILIDADE_DEFAULT")
            if _is_empty(pd_val):
                warnings.append("PROBABILIDADE_DEFAULT não informada.")
            elif str(pd_val).upper() != "NAO_APLICAVEL" and not isinstance(pd_val, (int, float)):
                errors.append("PROBABILIDADE_DEFAULT inválida: valor não numérico.")
            elif isinstance(pd_val, (int, float)) and (pd_val < 0 or pd_val > 100):
                errors.append("PROBABILIDADE_DEFAULT inválida: fora do intervalo [0, 100].")

        for rule in self.dynamic_rules:
            field = rule.get("field")
            val = record.get(field)

            if _is_empty(val):
                continue

            if not isinstance(val, (int, float)):
                errors.append(f"{field} inválido: valor não numérico.")
                continue

            rule_type = rule.get("type")
            if rule_type == "range":
                r_min, r_max = rule.get("min"), rule.get("max")
                if r_min is not None and val < r_min:
                    errors.append(f"{field} inválido: valor {val} menor que o limite ({r_min}).")
                if r_max is not None and val > r_max:
                    errors.append(f"{field} inválido: valor {val} maior que o limite ({r_max}).")
            elif rule_type == "min":
                r_val = rule.get("value")
                if r_val is not None and val < r_val:
                    errors.append(f"{field} inválido: valor {val} menor que o limite ({r_val}).")
            elif rule_type == "max":
                r_val = rule.get("value")
                if r_val is not None and val > r_val:
                    errors.append(f"{field} inválido: valor {val} maior que o limite ({r_val}).")

        return errors, warnings


import jsonschema
import json
from pathlib import Path

def validar_schema(record: dict[str, Any], logger: Any | None = None) -> list[str]:
    tipo_ficha = record.get("TIPO_FICHA")
    if tipo_ficha == "CONSUMIDOR":
        schema_path = Path("ENTRADAS/control/schemas/schema_ficha_consumidor_extraida.json")
    elif tipo_ficha == "COMERCIALIZADORA":
        schema_path = Path("ENTRADAS/control/schemas/schema_ficha_comercializadora_extraida.json")
    else:
        return []

    if not schema_path.exists():
        return []

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        
        # Chaves temporárias de runtime que NÃO pertencem ao contrato da Silver.
        # São subprodutos do extrator/classificador e devem ser descartadas
        # antes da validação de schema (Fail-Safe estrito).
        _RUNTIME_KEYS = {
            "DATA_DF_EPOCH_ORIGINAL",
            "FLAG_DATA_DF_CORRIGIDA",
            "STATUS_CNPJ",
            "_FALHA_GATE_CRITICO",
        }

        clean_record = {}
        from common.nulos import is_nulo_textual
        import pandas as pd
        for k, v in record.items():
            if k in _RUNTIME_KEYS:
                continue
            if is_nulo_textual(v):
                clean_record[k] = None
            elif isinstance(v, pd.Timestamp):
                clean_record[k] = v.strftime("%Y-%m-%d")
            else:
                clean_record[k] = v

        jsonschema.validate(instance=clean_record, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        return [f"Violação de contrato (Schema): {e.message}"]
    except Exception as e:
        if logger:
            logger.warning("Falha na validação de schema: %s", e)
    return []


def validar_registro(
    record: dict[str, Any],
    master_catalog: dict[str, Any] | None = None,
    logger: Any | None = None,
    required_fields: list[str] | None = None,
    quality_rules: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """Valida o registro normalizado da ficha usando o Master Catalog ou fallback para legados."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando validação unificada do registro. CNPJ=%s",
                record.get("CNPJ"),
            )

        errors: list[str] = []
        warnings: list[str] = []

        if master_catalog and "fields" in master_catalog:
            for field, config in master_catalog["fields"].items():
                if config.get("criticality") == "GATE_ENGINE":
                    if _is_empty(record.get(field)):
                        errors.append(f"GATE_ENGINE ausente: {field}")

            ativo_total = record.get("ATIVO_TOTAL_AJUSTADO")
            pl = record.get("PATRIMONIO_LIQUIDO")
            passivo_circulante = record.get("PASSIVO_CIRCULANTE_AJUSTADO")
            passivo_nao_circulante = record.get("PASSIVO_NAO_CIRCULANTE_FINANCEIRO_AJUSTADO")
            
            if ativo_total is not None and pl is not None:
                pc = float(passivo_circulante) if passivo_circulante is not None else 0.0
                pnc = float(passivo_nao_circulante) if passivo_nao_circulante is not None else 0.0
                
                passivo_exigivel = pc + pnc
                ativo_t = float(ativo_total)
                patrimonio = float(pl)
                
                diferenca = abs(ativo_t - (passivo_exigivel + patrimonio))
                if diferenca > (0.05 * ativo_t):
                    warnings.append(f"ALERTA_CONTABIL: Balanço não fecha. Ativo difere de Passivo+PL. (Diferença: {diferenca:.2f})")
        else:
            engine = DomainRuleEngine(quality_rules)
            err, warn = engine.validate(record, required_fields or [])
            errors.extend(err)
            warnings.extend(warn)

        if logger is not None:
            logger.info(
                "Validação concluída. CNPJ=%s ERROS=%s AVISOS=%s",
                record.get("CNPJ"),
                len(errors),
                len(warnings),
            )
            if errors:
                logger.warning("Erros de validação para CNPJ=%s: %s", record.get("CNPJ"), errors)

        return errors, warnings

    except Exception:
        if logger is not None:
            logger.exception("Falha inesperada na validação do registro. CNPJ=%s", record.get("CNPJ"))
        raise


def validar_registro_consumidor(
    record: dict[str, Any],
    master_catalog: dict[str, Any] | None = None,
    classificacao: Any | None = None,
    logger: Any | None = None,
) -> tuple[list[str], list[str]]:
    """Valida o registro de consumidor com regras condicionais por tipo de análise.

    Estende a validação padrão com regras específicas de consumidores:
    - ≥5 MWm (detalhada): valida presença obrigatória dos campos financeiros.
    - <5 MWm (simplificada): valida que campos financeiros são NAO_APLICAVEL,
      e exige score de bureau.
    """
    errors, warnings = validar_registro(
        record=record,
        master_catalog=master_catalog,
        logger=logger,
    )

    if classificacao is None:
        return errors, warnings

    tipo_analise = getattr(classificacao, "tipo_analise_exigida", None)

    if tipo_analise == "detalhada":
        campos_financeiros_obrigatorios = [
            "PATRIMONIO_LIQUIDO", "ATIVO_CIRCULANTE", "ATIVO_TOTAL",
            "PASSIVO_CIRCULANTE", "LUCRO_LIQUIDO",
            "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        ]
        for campo in campos_financeiros_obrigatorios:
            val = record.get(campo)
            if _is_empty(val):
                errors.append(
                    f"Campo financeiro obrigatório ausente para consumidor ≥5 MWm: {campo}"
                )

        if _is_empty(record.get("AUDITOR")):
            warnings.append("AUDITOR não informado para consumidor ≥5 MWm.")

    elif tipo_analise == "simplificada":
        if _is_empty(record.get("DATA_DEMONSTRACAO_FINANCEIRA")):
            record["DATA_DEMONSTRACAO_FINANCEIRA"] = "NAO_APLICAVEL"
            if "DATA_DEMONSTRACAO_FINANCEIRA não informada." in warnings:
                warnings.remove("DATA_DEMONSTRACAO_FINANCEIRA não informada.")

        if _is_empty(record.get("SCORE_BUREAU")):
            errors.append(
                "SCORE_BUREAU obrigatório para consumidor <5 MWm não informado."
            )

        campos_df = [
            "ATIVO_CIRCULANTE", "ATIVO_TOTAL", "PASSIVO_CIRCULANTE",
            "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        ]
        for campo in campos_df:
            val = record.get(campo)
            if not _is_empty(val) and str(val).upper() != "NAO_APLICAVEL":
                warnings.append(
                    f"Campo {campo} preenchido em ficha simplificada (<5 MWm). "
                    f"Valor: {val}"
                )

    if hasattr(classificacao, "compatibilidade_ficha_segmento"):
        if not classificacao.compatibilidade_ficha_segmento:
            warnings.append(
                f"Incompatibilidade detectada: ficha para tipo "
                f"'{classificacao.tipo_consumidor}' não contém os dados esperados. "
                f"Confiança: {classificacao.confianca_classificacao}."
            )

    if logger is not None:
        logger.info(
            "Validação condicional concluída para %s. "
            "Tipo=%s ERROS=%s AVISOS=%s",
            record.get("CNPJ"),
            tipo_analise,
            len(errors),
            len(warnings),
        )

    return errors, warnings
```


---

## `src/domain/garantias/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/garantias/servico_garantia.py`

- Linhas: 105
- SHA-256: `a0da57abfefaea7d53f1fc9d133ab22606fe68580773a2170a4bc9b837d45cef`
- Classes: GarantiaIngestionError
- Funções: inserir_dados_garantias

```python
"""Serviço de ingestão, validação e alertas de Garantias.

Lê o CSV extraído da query customizada do Denodo, salva na Bronze,
valida regras de vigência e cobertura, gera alertas e publica na Silver.
Ref: §2 (Módulo Garantias), §6.8 do Planejamento Funcional.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

class GarantiaIngestionError(Exception):
    """Exceção levantada para falhas na ingestão de garantias."""

COBERTURA_MINIMA = 0.5

def inserir_dados_garantias(
    context: AppContext,
    df_garantias_externo: pd.DataFrame | None = None,
) -> dict[str, Any]:
    run_id = f"GAR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/ingestao") / f"{run_id}__ingestao_garantias.log"
    logger = obter_logger("bdc.garantias", log_file)

    try:
        logger.info("Iniciando ingestão de Garantias (Modo CSV Local).")

        if df_garantias_externo is not None:
            df_raw = df_garantias_externo.copy()
            logger.info("Usando DataFrame externo fornecido.")
        else:
            input_dir = context.path("entradas") / "garantias"
            input_dir.mkdir(parents=True, exist_ok=True)

            arquivos = [
                f for f in input_dir.iterdir()
                if f.is_file() and f.suffix.lower() in {".xlsx", ".xls", ".csv"}
                and not f.name.startswith("~$")
            ]

            if not arquivos:
                logger.warning("Nenhum arquivo de garantias encontrado em %s.", input_dir)
                return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

            arquivo_fonte = max(arquivos, key=lambda f: f.stat().st_mtime)
            logger.info("Lendo garantias do arquivo local: %s", arquivo_fonte.name)

            if arquivo_fonte.suffix.lower() == ".csv":
                df_raw = pd.read_csv(arquivo_fonte, dtype=str, sep=";", encoding="utf-8-sig")
            else:
                df_raw = pd.read_excel(arquivo_fonte, dtype=str)

        if df_raw.empty:
            return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "garantias"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        caminho_bronze = bronze_dir / f"raw_garantias_{datetime.now().strftime('%Y%m%d')}.parquet"
        
        df_raw.to_parquet(caminho_bronze, index=False)

        df_garantias = df_raw.copy()
        df_garantias.columns = [str(c).strip().upper() for c in df_garantias.columns]

        from common.identificadores import normalizar_cnpj
        df_garantias["CNPJ_CONTRAPARTE"] = df_garantias["CNPJ_CONTRAPARTE"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
        df_garantias["VENCIMENTO"] = pd.to_datetime(df_garantias["VENCIMENTO"], errors="coerce")

        if "PERCENTUAL_COBERTURA" not in df_garantias.columns:
            df_garantias["PERCENTUAL_COBERTURA"] = 1.0
        else:
            df_garantias["PERCENTUAL_COBERTURA"] = pd.to_numeric(
                df_garantias["PERCENTUAL_COBERTURA"], errors="coerce"
            ).fillna(1.0)

        df_garantias["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
        df_garantias["RUN_ID"] = run_id

        silver_dir = context.path("silver") / "garantias_silver"
        escrever_conjunto_de_dados_silver(
            records=df_garantias.to_dict(orient="records"),
            output_dir=silver_dir,
            filename="garantia_silver"
        )

        logger.info("Ingestão de garantias na Silver concluída. Registros salvos: %s", len(df_garantias))

        return {
            "run_id": run_id,
            "linhas_processadas": len(df_garantias),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão de garantias.")
        raise GarantiaIngestionError(f"Erro ao ingerir base de garantias: {exc}") from exc
```


---

## `src/domain/mtm/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/mtm/servico_mtm.py`

- Linhas: 131
- SHA-256: `9b22bf1e4d3295aa31dcd91a0221b969970dd2663cec267b2b19f76bda06fe8f`
- Classes: MtmReconciliationError
- Funções: inserir_dados_mtm

```python
"""Serviço de ingestão e agregação da base de MtM para as camadas Bronze e Silver.

fix(T2.2.2): Removida lógica duplicada (leitura antiga via MTM_NETWORK_PATH
que salvava Bronze duas vezes). Mantido apenas o fluxo via mtm_connector.
Ref: §3.5, §11.6 do Planejamento Funcional.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from services.connectors.mtm_connector import buscar_mtm_consolidado, _encontrar_arquivo_mtm_recente
from storage.escrever_dados import escrever_conjunto_de_dados_silver


class MtmReconciliationError(Exception):
    """Exceção para falhas na reconciliação de totais entre Bronze e Silver."""


def inserir_dados_mtm(context: AppContext) -> dict[str, Any]:
    """Orquestra a ingestão MtM: Bronze snapshot → Conector → Agregação → Reconciliação → Silver."""
    run_id = f"MTM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/ingestao") / f"{run_id}__ingestao_mtm.log"
    logger = obter_logger("bdc.mtm", log_file)

    try:
        logger.info("Iniciando processo de ingestão e agregação da base de MtM.")

        input_dir = context.path("entradas") / "mtm"
        arquivo_bruto = _encontrar_arquivo_mtm_recente(input_dir)

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "mtm"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_mtm_{datetime.now().strftime('%Y%m%d')}_{arquivo_bruto.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(arquivo_bruto, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze)

        df_mtm = buscar_mtm_consolidado(input_dir=input_dir, logger=logger)

        if df_mtm.empty:
            logger.warning("Nenhum registro encontrado na base de MtM.")
            return {"run_id": run_id, "contrapartes_consolidadas": 0, "status": "SEM_DADOS"}

        soma_mtm_orig = float(df_mtm["MTM_TOTAL"].sum())
        soma_not_orig = float(df_mtm["NOTIONAL"].sum())

        if "DATA_BASE" not in df_mtm.columns:
            df_mtm["DATA_BASE"] = datetime.now().strftime("%Y-%m-%d")

        df_agregado = (
            df_mtm.groupby(["CNPJ", "CNPJ_RAIZ", "DATA_BASE"], as_index=False)
            .agg({
                "MTM_TOTAL": "sum",
                "NOTIONAL": "sum"
            })
            .rename(columns={
                "MTM_TOTAL": "MTM_TOTAL_NETTED",
                "NOTIONAL": "NOTIONAL_TOTAL"
            })
        )

        df_agregado["MTM_POSITIVO_TOTAL"] = df_agregado["MTM_TOTAL_NETTED"].apply(
            lambda x: x if x > 0 else 0.0
        )
        df_agregado["MTM_NEGATIVO_TOTAL"] = df_agregado["MTM_TOTAL_NETTED"].apply(
            lambda x: abs(x) if x < 0 else 0.0
        )

        if "STATUS_CNPJ" in df_mtm.columns:
            status_map = df_mtm[["CNPJ", "STATUS_CNPJ"]].drop_duplicates(subset=["CNPJ"])
            df_agregado = pd.merge(df_agregado, status_map, on="CNPJ", how="left")

        reconciliation_config = context.config.get("reconciliacao_mtm", {})
        tolerancia = reconciliation_config.get("tolerancia_absoluta", 0.01)

        soma_mtm_silver = float(df_agregado["MTM_TOTAL_NETTED"].sum())
        soma_not_silver = float(df_agregado["NOTIONAL_TOTAL"].sum())

        checks = [
            ("MTM Total", soma_mtm_orig, soma_mtm_silver),
            ("Notional Total", soma_not_orig, soma_not_silver),
        ]
        for label, original, silver in checks:
            diff = abs(original - silver)
            if diff > tolerancia:
                raise MtmReconciliationError(
                    f"Divergência de reconciliação no {label}! "
                    f"Original: {original} vs Silver: {silver} (Diff: {diff} > Tolerância: {tolerancia})"
                )

        df_agregado["RUN_ID"] = run_id
        df_agregado["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        records = df_agregado.to_dict(orient="records")

        silver_output_dir = context.path("silver") / "mtm_consolidado_silver"
        csv_path, parquet_path = escrever_conjunto_de_dados_silver(
            records=records,
            output_dir=silver_output_dir,
            filename=f"mtm_agregado_contraparte_{run_id}"
        )

        latest_path = silver_output_dir / "mtm_agregado_contraparte.parquet"
        if latest_path.exists():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(latest_path, silver_output_dir / f"mtm_agregado_contraparte_HIST_{ts}.parquet")
        shutil.copy2(parquet_path, latest_path)

        return {
            "run_id": run_id,
            "linhas_processadas": len(df_mtm),
            "contrapartes_consolidadas": len(records),
            "soma_mtm_total_netted": soma_mtm_silver,
            "soma_mtm_positivo_total": float(df_agregado["MTM_POSITIVO_TOTAL"].sum()),
            "soma_mtm_negativo_total": float(df_agregado["MTM_NEGATIVO_TOTAL"].sum()),
            "soma_notional_total": soma_not_silver,
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão/reconciliação do MtM.")
        raise
```


---

## `src/domain/salesforce/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/domain/salesforce/servico_salesforce.py`

- Linhas: 126
- SHA-256: `0774a68a31bbfe1d709e98c12041ebaf92376ab31fd93e7e663eece8220651c3`
- Classes: SalesforceIngestionError
- Funções: inserir_dados_salesforce, enriquecer_com_cnpj

```python
"""Serviço de ingestão e normalização da base do Salesforce."""

from __future__ import annotations

import shutil
from pathlib import Path
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from services.connectors.salesforce_connector import buscar_salesforce_dados
from storage.escrever_dados import escrever_conjunto_de_dados_silver


class SalesforceIngestionError(Exception):
    """Exceção para falhas na ingestão da base do Salesforce."""


def inserir_dados_salesforce(context: AppContext) -> dict[str, Any]:
    """
    Lê o arquivo do Salesforce (via conector), salva o snapshot na Bronze,
    deduplica os registros, enriquece as tabelas filhas com o CNPJ da Conta
    e persiste na camada Silver.
    """
    run_id = f"SF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/ingestao") / f"{run_id}__ingestao_salesforce.log"
    logger = obter_logger("bdc.salesforce", log_file)

    try:
        logger.info("Iniciando processo de ingestão da base do Salesforce.")

        input_dir = context.path("entradas") / "salesforce"
        arquivo_bruto = input_dir / "salesforce.xlsx"

        if not arquivo_bruto.exists():
            logger.warning("Arquivo salesforce.xlsx não encontrado na entrada.")
            return {"run_id": run_id, "status": "SEM_DADOS"}

        bronze_dir = context.path("bronze") / "snapshots_fontes" / "salesforce"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_salesforce_{datetime.now().strftime('%Y%m%d')}_{arquivo_bruto.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(arquivo_bruto, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze.name)

        dfs_sf = buscar_salesforce_dados(input_dir=input_dir, logger=logger)
        
        df_account = dfs_sf.get("Account", pd.DataFrame())
        df_cotacao = dfs_sf.get("Cotacao", pd.DataFrame())
        df_chamado = dfs_sf.get("Chamado", pd.DataFrame())
        df_contrato = dfs_sf.get("Contrato", pd.DataFrame())

        df_account = df_account.drop_duplicates(subset=["Id"], keep="last") if not df_account.empty else df_account
        df_cotacao = df_cotacao.drop_duplicates(subset=["Id"], keep="last") if not df_cotacao.empty else df_cotacao
        df_chamado = df_chamado.drop_duplicates(subset=["Id"], keep="last") if not df_chamado.empty else df_chamado
        df_contrato = df_contrato.drop_duplicates(subset=["Id"], keep="last") if not df_contrato.empty else df_contrato

        if "CNPJ__c" in df_account.columns:
            df_account = df_account.rename(columns={"CNPJ__c": "CNPJ"})

        if not df_account.empty and "CNPJ" in df_account.columns:
            account_map = df_account[["Id", "CNPJ"]].rename(columns={"Id": "AccountId_Join"})
            
            def enriquecer_com_cnpj(df_filho: pd.DataFrame) -> pd.DataFrame:
                if df_filho.empty or "AccountId" not in df_filho.columns:
                    return df_filho
                
                df_merged = pd.merge(
                    df_filho, 
                    account_map, 
                    left_on="AccountId", 
                    right_on="AccountId_Join", 
                    how="left"
                )
                df_merged = df_merged.drop(columns=["AccountId_Join"])
                
                if "CNPJ" in df_merged.columns:
                    df_merged["CNPJ"] = df_merged["CNPJ"].fillna("00000000000000")
                return df_merged

            df_cotacao = enriquecer_com_cnpj(df_cotacao)
            df_chamado = enriquecer_com_cnpj(df_chamado)
            df_contrato = enriquecer_com_cnpj(df_contrato)

        for df in [df_account, df_cotacao, df_chamado, df_contrato]:
            if not df.empty:
                df["RUN_ID"] = run_id
                df["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        silver_dir = context.path("silver") / "salesforce_silver"
        
        datasets = {
            "account": df_account,
            "cotacao": df_cotacao,
            "chamado": df_chamado,
            "contrato": df_contrato
        }

        arquivos_salvos = []
        for nome, df in datasets.items():
            if not df.empty:
                csv_p, pqt_p = escrever_conjunto_de_dados_silver(
                    records=df.to_dict(orient="records"),
                    output_dir=silver_dir / nome,
                    filename=f"salesforce_{nome}"
                )
                arquivos_salvos.append(nome)

        logger.info("Ingestão do Salesforce concluída. Objetos salvos: %s", ", ".join(arquivos_salvos))

        return {
            "run_id": run_id,
            "linhas_account": len(df_account),
            "linhas_cotacao": len(df_cotacao),
            "linhas_chamado": len(df_chamado),
            "linhas_contrato": len(df_contrato),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão do Salesforce.")
        raise SalesforceIngestionError(f"Erro ao ingerir base do Salesforce: {exc}") from exc
```


---

## `src/services/__init__.py`

- Linhas: 1
- SHA-256: `5f0bf3cdfde1cd820db7f9f9600ef1bd072706c5ad66c8346056f5a892d97968`
- Classes: -
- Funções: -

```python
"""Serviços de processamento do sistema BDC."""
```


---

## `src/services/connectors/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/services/connectors/denodo_connector.py`

- Linhas: 133
- SHA-256: `9f222d90009ffadcb8f8c6017ac200b58115e1169a8f125a9c638269515b2e19`
- Classes: DenodoConnectionError
- Funções: _solicitacao_com_tentativa, _encontrar_arquivo_bronze_recente, buscar_denodo

```python
"""Conector central para o virtualizador Denodo via API RESTful.

feat(T2.1.1): Adicionados retry com backoff exponencial e fallback para
último snapshot Bronze em caso de indisponibilidade.
Ref: §3.4 do Planejamento Funcional.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 2.0


class DenodoConnectionError(Exception):
    """Exceção levantada para falhas de conexão na API do Denodo."""


def _solicitacao_com_tentativa(url: str, params, auth, max_retries: int = MAX_RETRIES) -> requests.Response:
    """Executa GET com retry e backoff exponencial."""
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                auth=auth,
                verify=False,
                timeout=300,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            if attempt < max_retries:
                wait = BACKOFF_BASE_SECONDS ** attempt
                LOGGER.warning(
                    "Tentativa %s/%s falhou para '%s'. Retry em %.1fs. Erro: %s",
                    attempt, max_retries, url, wait, exc,
                )
                time.sleep(wait)
            else:
                LOGGER.error("Todas as %s tentativas falharam para '%s'.", max_retries, url)
    raise last_exc


def _encontrar_arquivo_bronze_recente(bronze_dir: Path, prefix: str = "raw_contratos") -> Path | None:
    """Localiza o snapshot Bronze mais recente para fallback."""
    if not bronze_dir.exists():
        return None
    snapshots = [
        f for f in bronze_dir.iterdir()
        if f.is_file() and f.name.startswith(prefix) and f.suffix == ".parquet"
    ]
    if not snapshots:
        return None
    return max(snapshots, key=lambda f: f.stat().st_mtime)


def buscar_denodo(
    view_name: str,
    params: dict[str, Any] | None = None,
    bronze_fallback_dir: Path | None = None,
) -> pd.DataFrame:
    base_url = os.getenv("DENODO_REST_BASE_URL", "https://vidgcpprd.copel.nt:9443/denodo-restfulws/com/views")
    url = f"{base_url}/{view_name}"

    user = os.getenv("DENODO_USER")
    pwd = <REDACTED>

    if not all([user, pwd]):
        raise ValueError("Credenciais DENODO_USER ou DENODO_PWD não encontradas no arquivo .env.")

    req_params: dict[str, Any] | None = {"$format": "json"}
    if params:
        req_params.update(params)

    auth = HTTPBasicAuth(user, pwd)
    all_elements: list[dict[str, Any]] = []

    try:
        LOGGER.info("Iniciando extração da view '%s' via REST API...", view_name)

        while url:
            response = _solicitacao_com_tentativa(url, params=req_params, auth=auth)

            data = response.json()
            elements = data.get("elements", [])

            if not elements:
                break

            all_elements.extend(elements)

            links = data.get("links", [])
            next_link = next((link["href"] for link in links if link.get("rel") == "next"), None)

            if next_link:
                url = next_link
                req_params = None
            else:
                url = None

        LOGGER.info("Extração via REST finalizada. %s registros carregados.", len(all_elements))
        return pd.DataFrame(all_elements)

    except (requests.exceptions.RequestException, DenodoConnectionError) as exc:
        LOGGER.exception("Falha na comunicação com a API REST do Denodo.")

        if bronze_fallback_dir:
            snapshot = _encontrar_arquivo_bronze_recente(bronze_fallback_dir)
            if snapshot:
                LOGGER.warning(
                    "Usando fallback: lendo último snapshot Bronze '%s'.", snapshot.name
                )
                return pd.read_parquet(snapshot)
            LOGGER.error("Nenhum snapshot Bronze encontrado para fallback em '%s'.", bronze_fallback_dir)

        raise DenodoConnectionError(f"Erro ao acessar endpoint '{view_name}': {exc}") from exc
```


---

## `src/services/connectors/mtm_connector.py`

- Linhas: 78
- SHA-256: `6451c86efac9d455f89c226d7764f7a11e0e01269d462e4025fba38265b06f00`
- Classes: MtmConnectionError
- Funções: _encontrar_arquivo_mtm_recente, buscar_mtm_consolidado

```python
"""Conector de integração com a base de MtM (Risco de Mercado)."""

from __future__ import annotations
from pathlib import Path
from typing import Any
from datetime import datetime
import pandas as pd

from common.dados import normalizar_coluna_cnpj

class MtmConnectionError(Exception):
    """Exceção levantada quando a base de MtM não pode ser obtida."""

def _encontrar_arquivo_mtm_recente(diretorio: Path) -> Path:
    arquivos = [f for f in diretorio.iterdir() if f.is_file() and f.suffix.lower() in {".xlsx", ".xls", ".csv"} and not f.name.startswith("~$")]
    if not arquivos: raise FileNotFoundError(f"Nenhum arquivo de MtM encontrado na pasta: {diretorio}")
    return max(arquivos, key=lambda f: f.stat().st_mtime)

def buscar_mtm_consolidado(input_dir: Path | str, logger: Any | None = None) -> pd.DataFrame:
    diretorio = Path(input_dir)
    diretorio.mkdir(parents=True, exist_ok=True)
    
    try:
        arquivo_fonte = _encontrar_arquivo_mtm_recente(diretorio)
        if logger: logger.info("Lendo base de MtM a partir do arquivo local: %s", arquivo_fonte.name)
        
        if arquivo_fonte.suffix.lower() == ".csv":
            df_bruto = pd.read_csv(arquivo_fonte, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)
        else:
            df_bruto = pd.read_excel(arquivo_fonte, dtype=str)

        df_bruto.columns = [str(c).strip().upper() for c in df_bruto.columns]

        col_cnpj = next((c for c in df_bruto.columns if "CNPJ" in c and "CONTROLADOR" not in c), None)
        if col_cnpj:
            df_bruto = normalizar_coluna_cnpj(df_bruto, coluna_origem=col_cnpj)
            cnpj_series  = df_bruto["CNPJ"]
            raiz_series  = df_bruto["CNPJ_RAIZ"]
            status_series = df_bruto["CNPJ_STATUS"]
        else:
            cnpj_series   = pd.Series(["00000000000000"] * len(df_bruto), name="CNPJ")
            raiz_series   = pd.Series(["00000000"] * len(df_bruto), name="CNPJ_RAIZ")
            status_series = pd.Series(["CNPJ_AUSENTE"] * len(df_bruto), name="STATUS_CNPJ")

        if "MTM_TOTAL" in df_bruto.columns:
            raw_mtm = df_bruto["MTM_TOTAL"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            valores_mtm = pd.to_numeric(raw_mtm, errors="coerce").fillna(0.0)
        else:
            valores_mtm = pd.Series([0.0] * len(df_bruto), name="MTM_TOTAL")

        if "ENERGIA_MWH" in df_bruto.columns and "PRECO_REAJUSTADO" in df_bruto.columns:
            vol = df_bruto["ENERGIA_MWH"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            px = df_bruto["PRECO_REAJUSTADO"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            valores_notional = pd.to_numeric(vol, errors="coerce").fillna(0.0) * pd.to_numeric(px, errors="coerce").fillna(0.0)
        else:
            valores_notional = pd.Series([0.0] * len(df_bruto), name="NOTIONAL")

        contrato_series = df_bruto.get("COD_CONTRATO", pd.Series([None] * len(df_bruto)))
        data_base_series = df_bruto.get("DATA_AVALIACAO", pd.Series([datetime.now().strftime("%Y-%m-%d")] * len(df_bruto)))

        df_resultado = pd.DataFrame({
            "CNPJ":        cnpj_series,
            "CNPJ_RAIZ":   raiz_series,
            "STATUS_CNPJ": status_series,
            "CONTRATO":    contrato_series,
            "DATA_BASE":   data_base_series,
            "MTM_TOTAL":   valores_mtm,
            "NOTIONAL":    valores_notional
        })

        df_resultado = df_resultado[df_resultado["STATUS_CNPJ"] == "CNPJ_VALIDO"].copy()

        if logger: logger.info("MtM lido. Notional convertido para Financeiro (R$).")
        return df_resultado

    except Exception as exc:
        if logger: logger.exception("Falha ao processar o arquivo local de MtM.")
        raise MtmConnectionError(f"Erro ao ler base de MtM: {exc}") from exc
```


---

## `src/services/connectors/receita_connector.py`

- Linhas: 177
- SHA-256: `876316b9086c26db78c4b1f5c4a5157da736742100b45b7b77935da308e883de`
- Classes: -
- Funções: _cache_path, _load_cache, _save_cache, _is_cache_valido, _consultar_cnpj_brasilapi, buscar_receita_dados_lote

```python
from __future__ import annotations
from common.identificadores import normalizar_cnpj

import json
import logging
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from app.context import AppContext

LOGGER = logging.getLogger(__name__)
BRASIL_API_BASE_URL = "https://brasilapi.com.br/api/cnpj/v1"

def _cache_path(context: AppContext) -> Path:
    return context.path("entradas") / "receita" / "cache" / "receita_cache.json"

def _load_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists(): return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError): return {}
    if not isinstance(payload, dict): return {}
    
    cache: dict[str, dict[str, Any]] = {}
    for cnpj, record in payload.items():
        if record.get("STATUS") == "OK_BYPASS" or "Simulacao" in str(record.get("NATUREZA_JURIDICA", "")):
            continue
        resultado = normalizar_cnpj(cnpj)
        if resultado.valido and isinstance(record, dict):
            cache[resultado.cnpj] = record
    return cache

def _save_cache(path: Path, cache: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = {cnpj: cache[cnpj] for cnpj in sorted(cache)}
    path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")

def _is_cache_valido(record: dict[str, Any], dias_validade: int = 30) -> bool:
    """Retorna True se o registro de cache foi consultado dentro do período de validade."""
    quando = record.get("DATA_CONSULTA")
    if not quando: return False
    try:
        dt_consulta = datetime.fromisoformat(str(quando)[:19])
        return (datetime.now() - dt_consulta).days < dias_validade
    except Exception: return False

def _consultar_cnpj_brasilapi(cnpj: str, session: requests.Session) -> dict[str, Any]:
    url = f"{BRASIL_API_BASE_URL}/{cnpj}"
    resultado = {
        "CNPJ": cnpj, "SITUACAO_CADASTRAL": "ERRO_API", "DATA_ABERTURA": "N/D",
        "CNAE_PRINCIPAL": "N/D", "NATUREZA_JURIDICA": "N/D",
        "DATA_CONSULTA": datetime.now().isoformat(timespec="seconds"),
        "STATUS": "FALHA", "MENSAGEM": ""
    }
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BDC_Pipeline/1.0",
    }
    
    tentativas_maximas = 4
    espera_base = 3.0

    for tentativa in range(1, tentativas_maximas + 1):
        try:
            resp = session.get(url, headers=headers, timeout=15, verify=False)
            
            if resp.status_code == 200:
                data = resp.json()
                resultado["SITUACAO_CADASTRAL"] = str(data.get("descricao_situacao_cadastral", "N/D")).strip().upper()
                resultado["DATA_ABERTURA"] = str(data.get("data_inicio_atividade", "N/D")).strip()
                resultado["CNAE_PRINCIPAL"] = str(data.get("cnae_fiscal", "N/D")).strip()
                resultado["NATUREZA_JURIDICA"] = str(data.get("natureza_juridica", "N/D")).strip()
                resultado["STATUS"] = "SUCESSO"
                resultado["MENSAGEM"] = "Consulta via BrasilAPI com sucesso"
                return resultado
                
            if resp.status_code in (404, 400):
                resultado["SITUACAO_CADASTRAL"] = "NAO_ENCONTRADO"
                resultado["MENSAGEM"] = f"CNPJ inexistente (HTTP {resp.status_code})"
                return resultado
                
            if resp.status_code == 429 or resp.status_code >= 500:
                if tentativa < tentativas_maximas:
                    tempo_espera = espera_base * (2 ** (tentativa - 1))
                    LOGGER.warning("API bloqueou - HTTP %s. Pausando %ss...", resp.status_code, tempo_espera)
                    time.sleep(tempo_espera)
                    continue
                else:
                    resultado["SITUACAO_CADASTRAL"] = "RATE_LIMIT"
                    resultado["MENSAGEM"] = "Bloqueio persistente após múltiplas tentativas."
                    return resultado

            resultado["SITUACAO_CADASTRAL"] = f"ERRO_HTTP_{resp.status_code}"
            return resultado

        except requests.exceptions.Timeout:
            if tentativa < tentativas_maximas:
                time.sleep(espera_base * tentativa)
                continue
            resultado["SITUACAO_CADASTRAL"] = "TIMEOUT"
            return resultado
            
        except requests.exceptions.RequestException as e:
            if tentativa < tentativas_maximas:
                time.sleep(espera_base * tentativa)
                continue
            resultado["SITUACAO_CADASTRAL"] = "ERRO_CONEXAO"
            return resultado

    return resultado

def buscar_receita_dados_lote(cnpjs: list[str], context: AppContext, logger: logging.Logger = LOGGER) -> pd.DataFrame:
    cache_path = _cache_path(context)
    cache = _load_cache(cache_path)
    
    list_normalizada = []
    seen = set()
    for cnpj in cnpjs or []:
        resultado = normalizar_cnpj(cnpj)
        if resultado.valido and resultado.cnpj not in seen:
            seen.add(resultado.cnpj)
            list_normalizada.append(resultado.cnpj)

    results = []
    total = len(list_normalizada)
    qtd_cache = 0
    qtd_api = 0
    qtd_erro = 0
    
    logger.info("[RECEITA FEDERAL] Processando %d CNPJs...", total)
    logger.info("--- INICIANDO CONSULTA RECEITA FEDERAL (%d CNPJs) ---", total)

    with requests.Session() as sessao:
        for index, cnpj in enumerate(list_normalizada):
            cached = cache.get(cnpj)
            
            if cached and _is_cache_valido(cached):
                if cached.get("SITUACAO_CADASTRAL") not in ["TIMEOUT", "RATE_LIMIT", "ERRO_CONEXAO", "ERRO_API"]:
                    logger.info("[%d/%d] CNPJ %s -> CACHE (%s)", index + 1, total, cnpj, cached.get('SITUACAO_CADASTRAL'))
                    results.append(cached)
                    qtd_cache += 1
                    continue

            logger.info("[%d/%d] CNPJ %s -> Consultando API...", index + 1, total, cnpj)
            api_result = _consultar_cnpj_brasilapi(cnpj, sessao)
            status_obtido = api_result.get("SITUACAO_CADASTRAL")
            logger.info("Resultado: %s", status_obtido)
            
            qtd_api += 1
            if api_result.get("STATUS") == "FALHA":
                qtd_erro += 1
                
            if status_obtido not in ["TIMEOUT", "RATE_LIMIT", "ERRO_CONEXAO"]:
                cache[cnpj] = api_result
                
            results.append(api_result)
            
            time.sleep(0.8)

            if qtd_api > 0 and qtd_api % 50 == 0:
                _save_cache(cache_path, cache)

    if qtd_api > 0:
        _save_cache(cache_path, cache)

    logger.info("--- RESUMO RECEITA: %d Cache | %d API | %d Erros ---", qtd_cache, qtd_api, qtd_erro)

    df = pd.DataFrame(results)
    return df.drop_duplicates(subset=["CNPJ"], keep="last").reset_index(drop=True)
```


---

## `src/services/connectors/risk3_connector.py`

- Linhas: 186
- SHA-256: `ee62e86a2bdb06f884937c76824b13702295b328e40a6914f89b8f7f969bfec8`
- Classes: -
- Funções: _obter_token_auth, buscar_bureau_risk3

```python
"""Conector oficial para a API Expresso RISK3 (Bureau de Crédito)."""
from __future__ import annotations
import json
import logging
import math
import os
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import Any
import pandas as pd
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from app.context import AppContext
from common.identificadores import normalizar_cnpj
from control.logger import obter_logger
logger = obter_logger(__name__)

def _obter_token_auth() -> str | None:
    """Autentica na API da RISK3 e obtém um token de sessão via POST."""
    base_url = os.getenv("RISK3_API_URL")
    user = os.getenv("RISK3_USER")
    pwd = <REDACTED>

    if not all([base_url, user, pwd]):
        logger.warning("Credenciais RISK3_API_URL, RISK3_USER ou RISK3_PWD ausentes no .env")
        return None
    proxies = {"http": None, "https": None}

    try:
        url = f"{base_url.rstrip('/')}/api/v0/login"
        resp = requests.post(url, json={"username": user, "password": pwd}, timeout=15, verify=False, proxies=proxies)
        
        if "Acesso Bloqueado" in resp.text or "Netskope" in resp.text:
            logger.error("Conexão interceptada pelo Netskope/Firewall da Copel.")
            return None

        if resp.status_code == 200:
            data = resp.json().get("data")
            if isinstance(data, dict):
                return data.get("token")
            return data
        logger.error("Falha na autenticação RISK3. HTTP %s", resp.status_code)
        return None
    except Exception as e:
        logger.error("Falha de conexão na RISK3: %s", e)
        return None

def buscar_bureau_risk3(cnpjs: list[str], context: AppContext) -> pd.DataFrame:
    """Orquestra a consulta em lote na RISK3 utilizando cache local."""
    cache_path = context.path("entradas") / "bureau" / "cache" / "risk3_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache = {}

    if cache_path.exists():

        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    token = <REDACTED>
    if not token:
        logger.warning("Sem token da RISK3. Abortando consulta de Bureau.")
        return pd.DataFrame()
    api_url = os.getenv("RISK3_API_URL", "").rstrip('/')
    proxies = {"http": None, "https": None}
    cnpjs_unicos = sorted(list(set(normalizar_cnpj(c).cnpj for c in cnpjs if normalizar_cnpj(c).valido)))
    results = []
    
    logger.info("--- INICIANDO CONSULTA RISK3 BUREAU (%d CNPJs) ---", len(cnpjs_unicos))
    
    for i, cnpj in enumerate(cnpjs_unicos):
        cached = cache.get(cnpj)
        if cached:
            status_cache = cached.get("STATUS")
            data_cons = cached.get("DATA_CONSULTA")
            if data_cons and status_cache in ("SUCESSO", "NAO_ENCONTRADO"):
                dias_cache = (datetime.now() - datetime.fromisoformat(data_cons)).days
                ttl = 365 if status_cache == "SUCESSO" else 30
                if dias_cache < ttl:
                    logger.info("[%d/%d] CNPJ %s -> CACHE (%s, %dd/%dd)", i + 1, len(cnpjs_unicos), cnpj, status_cache, dias_cache, ttl)
                    results.append(cached)
                    continue

        logger.info("[%d/%d] CNPJ %s -> Consultando API (Endpoint detalhado por CNPJ)...", i + 1, len(cnpjs_unicos), cnpj)
        
        auth_value = json.dumps(token) if isinstance(token, dict) else str(token)
        headers = {"Venidera-AuthToken": auth_value}
        
        resultado = {
            "CNPJ": cnpj,
            "DATA_CONSULTA": datetime.now().isoformat(timespec="seconds"),
            "STATUS": "FALHA"
        }

        try:
            # Pelo Swagger oficial, o endpoint correto de consulta por CNPJ é:
            url_busca = f"{api_url}/api/v0/analises/cnpj/{cnpj}"
            resp_busca = requests.get(url_busca, headers=headers, timeout=20, verify=False, proxies=proxies)
            
            if "Netskope" in resp_busca.text or "Acesso Bloqueado" in resp_busca.text:
                resultado["STATUS"] = "BLOQUEIO_FIREWALL"
                logger.warning("BLOQUEIO_FIREWALL")
            elif resp_busca.status_code == 200:
                body_busca = resp_busca.json()
                data_obj = body_busca.get("data")
                
                if not data_obj:
                    resultado["STATUS"] = "NAO_ENCONTRADO"
                    logger.info("NAO_ENCONTRADO (Data vazio)")
                else:
                    # A resposta detalhada pode vir como uma lista de análises para aquele CNPJ ou um dicionário
                    analises = data_obj if isinstance(data_obj, list) else data_obj.get("analises", [])
                    if isinstance(data_obj, dict) and not analises:
                        analises = [data_obj]
                    
                    if not analises:
                        resultado["STATUS"] = "NAO_ENCONTRADO"
                        logger.warning("NAO_ENCONTRADO (Lista de análises vazia no retorno detalhado)")
                    else:
                        analise_item = analises[0]
                        bloco_analise = analise_item.get("analise", {}) if "analise" in analise_item else analise_item
                        bloco_calculos = bloco_analise.get("calculos", {})
                        bloco_custom = bloco_analise.get("custom_ratings", {}).get("rating", {})
                        
                        score_val = bloco_calculos.get("score_final")
                        restritivos_val = bloco_calculos.get("fator_de_alerta")
                        
                        resultado["SCORE_BUREAU"] = float(score_val) if score_val is not None else None
                        resultado["RATING_BUREAU"] = bloco_custom.get("grade") if bloco_custom.get("grade") is not None else None
                        resultado["RESTRITIVOS"] = float(restritivos_val) if restritivos_val is not None else None
                        
                        data_req = analise_item.get("data_da_solicitacao")
                        if data_req:
                            try:
                                dt_consulta = pd.to_datetime(data_req)
                                resultado["DATA_CONSULTA"] = dt_consulta.strftime("%Y-%m-%d")
                                resultado["DATA_VALIDADE"] = (dt_consulta + relativedelta(months=18)).strftime("%Y-%m-%d")
                            except Exception:
                                resultado["DATA_CONSULTA"] = data_req
                                resultado["DATA_VALIDADE"] = None
                        else:
                            resultado["DATA_CONSULTA"] = None
                            resultado["DATA_VALIDADE"] = None
                            
                        if resultado["SCORE_BUREAU"] is not None and resultado["RESTRITIVOS"] is not None:
                            try:
                                s = resultado["SCORE_BUREAU"]
                                r = resultado["RESTRITIVOS"]
                                pd_calc = 1.9 * math.exp(-0.5 * (0.11 * s - r / 3.0 + 1))
                                resultado["PD_BUREAU"] = min(pd_calc, 0.9999)
                            except Exception:
                                resultado["PD_BUREAU"] = None
                        else:
                            resultado["PD_BUREAU"] = None

                        resultado["RAW_DATA"] = json.dumps(data_obj, ensure_ascii=False)
                        resultado["STATUS"] = "SUCESSO"
                        logger.info("SUCESSO na extração dos detalhes!")
                        
                        # Salvar raw json na pasta risk3 (Auditoria/Física)
                        pasta_raw = context.path("bronze") / "risk3_raw"
                        pasta_raw.mkdir(parents=True, exist_ok=True)
                        arquivo_raw = pasta_raw / f"risk3_{cnpj}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        arquivo_raw.write_text(resultado["RAW_DATA"], encoding="utf-8")
                        
            elif resp_busca.status_code in (404, 422):
                resultado["STATUS"] = "NAO_ENCONTRADO"
                logger.info("NAO_ENCONTRADO (HTTP %s - A análise pode não existir ainda no Bureau)", resp_busca.status_code)
            else:
                resultado["STATUS"] = f"ERRO_HTTP_{resp_busca.status_code}"
                logger.warning("ERRO_HTTP_%s ao consultar CNPJ", resp_busca.status_code)
        except Exception as e:
            resultado["STATUS"] = "ERRO_CONEXAO"
            logger.exception("ERRO_CONEXAO: %s", e)
        if resultado["STATUS"] in ["SUCESSO", "NAO_ENCONTRADO"]:
            cache[cnpj] = resultado
        results.append(resultado)
        time.sleep(0.5)

    if results:
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return pd.DataFrame(results)
```


---

## `src/services/connectors/salesforce_connector.py`

- Linhas: 66
- SHA-256: `29db84cdaf229231e2ef7fc7e80efacb44517cd25ac830903382cbe6636ba3c5`
- Classes: SalesforceConnectionError
- Funções: buscar_salesforce_dados

```python
"""Conector de integração de arquivos extraídos do Salesforce (via Power Query)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

class SalesforceConnectionError(Exception):
    """Exceção levantada quando a base do Salesforce não pode ser obtida."""


def buscar_salesforce_dados(
    input_dir: Path | str,
    logger: Any | None = None,
) -> Dict[str, pd.DataFrame]:
    """
    Lê o arquivo salesforce.xlsx atualizado via Power Query contendo as abas:
    Conta, Cotação, Chamado e Contrato. Retorna um dicionário de DataFrames.
    """
    diretorio = Path(input_dir)
    arquivo_sf = diretorio / "salesforce.xlsx"
    
    if logger:
        logger.info("Iniciando leitura da base local do Salesforce: %s", arquivo_sf)
        
    if not arquivo_sf.exists():
        if logger:
            logger.error("Arquivo %s não encontrado.", arquivo_sf)
        raise FileNotFoundError(f"Arquivo Salesforce não encontrado na pasta: {arquivo_sf}")

    resultados_df = {}
    
    mapa_abas = {
        "Conta": "Account",
        "Cotação": "Cotacao",
        "Chamado": "Chamado",
        "Contrato": "Contrato"
    }

    try:
        for aba_excel, chave_dict in mapa_abas.items():
            if logger:
                logger.info("Lendo aba '%s' do Salesforce...", aba_excel)
            
            df = pd.read_excel(arquivo_sf, sheet_name=aba_excel, dtype=str)
            
            df = df.fillna("")
            df = df.replace("nan", "")
            
            if chave_dict == "Account" and "CNPJ__c" in df.columns:
                from common.identificadores import normalizar_cnpj
                df["CNPJ__c"] = df["CNPJ__c"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
            
            resultados_df[chave_dict] = df
            
            if logger:
                logger.info("Aba '%s' carregada com sucesso. %s registros processados.", aba_excel, len(df))

        return resultados_df

    except Exception as exc:
        if logger:
            logger.exception("Falha crítica ao ler o arquivo local do Salesforce.")
        raise SalesforceConnectionError(f"Erro ao processar as planilhas do Salesforce: {exc}") from exc
```
