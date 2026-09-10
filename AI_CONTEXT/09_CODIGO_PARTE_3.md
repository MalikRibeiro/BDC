# CÓDIGO PARTE 3

Arquivos consolidados por afinidade de domínio, mantendo arquivos pequenos relacionados juntos.


# GRUPO: application


---

## `src/app/__init__.py`

- Linhas: 1
- SHA-256: `92314c9144f52e90a5125c383d7d421654581ab3784a0291d94fccf621e3888e`
- Classes: -
- Funções: -

```python
"""Pacote de bootstrap e contexto da aplicação BDC."""
```


---

## `src/app/bootstrap.py`

- Linhas: 59
- SHA-256: `76f6381dce428c77b2528d3e667a6a261f21242409583b3201c1ac460d2ed28c`
- Classes: -
- Funções: resolve_configs_dir, aplicativo_bootstrap

```python
import os
from pathlib import Path
from typing import Optional, Union

from src.app.context import AppContext, carregar_contexto
from dotenv import load_dotenv

load_dotenv()

CONFIGS_DIR_ENV_VAR = "BDC_CONFIGS_DIR"


def resolve_configs_dir(explicit_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Resolve o diretório de configurações utilizando a seguinte hierarquia:
    1. Caminho explícito fornecido (ex.: via flag CLI --configs-dir).
    2. Variável de ambiente `BDC_CONFIGS_DIR`.
    3. Diretório relativo à raiz do projeto (`<project_root>/ENTRADAS/configs`).

    Args:
        explicit_path: Caminho explícito opcional (string ou Path).

    Returns:
        Path: Objeto Path do diretório de configurações validado.

    Raises:
        FileNotFoundError: Caso o diretório de configurações não exista.
    """
    if explicit_path:
        configs_dir = Path(explicit_path).resolve()
    elif os.environ.get(CONFIGS_DIR_ENV_VAR):
        configs_dir = Path(os.environ[CONFIGS_DIR_ENV_VAR]).resolve()
    else:
        project_root = Path(__file__).resolve().parents[2]
        configs_dir = project_root / "ENTRADAS" / "configs"

    if not configs_dir.exists() or not configs_dir.is_dir():
        raise FileNotFoundError(
            f"Diretório de configurações não encontrado em: '{configs_dir}'.\n"
            f"Por favor, verifique se o caminho existe ou especifique o caminho correto via:\n"
            f"  - Flag CLI: --configs-dir /caminho/para/configs\n"
            f"  - Variável de ambiente: export {CONFIGS_DIR_ENV_VAR}=/caminho/para/configs"
        )

    return configs_dir


def aplicativo_bootstrap(configs_dir: Optional[Union[str, Path]] = None) -> AppContext:
    """
    Realiza o bootstrap da aplicação e carrega o AppContext.

    Args:
        configs_dir: Caminho explícito ou opcional para o diretório de configurações.

    Returns:
        AppContext: Contexto inicializado da aplicação.
    """
    resolved_dir = resolve_configs_dir(configs_dir)
    return carregar_contexto(resolved_dir)
```


---

## `src/app/comercializadoras/orquestrador_comercializadoras.py`

- Linhas: 417
- SHA-256: `9be95c2ed0327d4631edd4157776b8c206f1f5f1654f7984cdd65255a67a74bd`
- Classes: -
- Funções: carregar_overrides_manuais, aplicar_overrides_manuais, processar_arquivo_individual, processar_fichas_comercializadoras

```python
"""Serviço principal refatorado do pipeline de fichas de comercializadoras."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.context import AppContext
from common.excel import abrir_pasta, fechar_pasta
from common.hashing import arquivo_hash
from common.identificadores import normalizar_cnpj
from common.json import ler_json
from control.logger import obter_logger

from control.layout_catalog import carregar_layouts_comercializadoras
from control.carregador_de_mapeamento import mapeamento_de_carga_fichas_comercializadoras
from domain.auditoria.servico_auditoria import registrar_linhagem_campos
from relational.facts.fato_alerta_util import registrar_alerta
from common.servico_desduplicacao import (
    tem_chave_de_negocio_duplicada,
    tem_hash_duplicado,
    virar_chave_de_negocio_no_historico,
)
from domain.fichas.validador import validar_registro
from silver.documentos_classificados import criar_documento_classificado
from silver.formatador_silver import normalizar_registro
from staging.staging_arquivo import copiar_para_staging
from storage.bronze_arquivo import publicar_arquivo_bruto
from storage.armazenamento_manifest import (
    historico_de_ingestao_de_carga,
)
from storage.escrever_dados import (
    mesclar_conjunto_de_dados_prata_por_chave_de_negocio,
    escrever_conjunto_de_dados_silver,
)
from storage.estado_armazenamento import DocumentManifest
from common.utils_orquestracao import (
    disco_cheio_erro,
    criar_run_id,
    criar_nome_arquivo_padronizado,
    resolver_subpasta_bronze,
    criar_fila_processamento,
    mover_para_rejeitados,
    mover_para_processados
)


def carregar_overrides_manuais(eventos_manuais_path: Path, logger: Any) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """Carrega de forma segura os dados de overrides manuais armazenados em formato Parquet."""
    overrides_dict = {}
    if not eventos_manuais_path.exists():
        logger.info("Nenhuma base de Carga Manual encontrada em %s", eventos_manuais_path)
        return overrides_dict
        
    try:
        import pandas as pd
        df_overrides = pd.read_parquet(eventos_manuais_path)
        
        if df_overrides.empty:
            return overrides_dict
            
        if "_STATUS_REGISTRO" in df_overrides.columns:
            df_overrides = df_overrides[df_overrides["_STATUS_REGISTRO"] == "VIGENTE"]
            
        df_overrides = df_overrides.dropna(subset=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "CAMPO_AFETADO"])
        
        from common.identificadores import normalizar_cnpj
        from common.datas import normalizar_data
        
        for row in df_overrides.to_dict(orient="records"):
            res_cnpj = normalizar_cnpj(row.get("CNPJ"))
            cnpj_over = res_cnpj.cnpj if res_cnpj.valido else None
            data_over = normalizar_data(row.get("DATA_DEMONSTRACAO_FINANCEIRA"))
            
            if not cnpj_over or not data_over:
                continue
                
            chave = (cnpj_over, data_over)
            
            if chave not in overrides_dict:
                overrides_dict[chave] = []
                
            valor_salvo = row.get("VALOR_NOVO")
            valor_tratado = valor_salvo
            
            if isinstance(valor_salvo, str):
                try:
                    valor_tratado = float(valor_salvo)
                except ValueError:
                    pass
                
            campo_afetado = str(row.get("CAMPO_AFETADO", "")).strip().upper().replace(" ", "_")
            
            overrides_dict[chave].append({
                "campo": campo_afetado if campo_afetado and campo_afetado != "NONE" else row.get("CAMPO_AFETADO"),
                "valor": valor_tratado
            })
            
        logger.info("Base de Overrides carregada: %d chaves vigentes.", len(overrides_dict))
    except Exception:
        logger.exception("Falha ao carregar overrides Parquet. Ignorando carga manual.")
        
    return overrides_dict

def aplicar_overrides_manuais(
    registro: dict[str, Any], 
    overrides_dict: dict[tuple[str, str], list[dict[str, Any]]], 
    logger: Any
) -> None:
    """Aplica as atualizações manuais injetando os valores na ficha normalizada."""
    from common.identificadores import normalizar_cnpj
    from common.datas import normalizar_data
    
    cnpj_atual = registro.get("CNPJ")
    data_bruta = registro.get("DATA_DEMONSTRACAO_FINANCEIRA")
    
    if not cnpj_atual:
        return
        
    res_cnpj = normalizar_cnpj(cnpj_atual)
    cnpj_normalizado = res_cnpj.cnpj if res_cnpj.valido else None
    
    if not cnpj_normalizado:
        return
    
    data_normalizada = normalizar_data(data_bruta) if data_bruta else None
    
    if data_normalizada:
        chave_atual = (cnpj_normalizado, data_normalizada)
        if chave_atual in overrides_dict:
            for override in overrides_dict[chave_atual]:
                campo = override["campo"]
                novo_valor = override["valor"]
                if campo:
                    valor_antigo = registro.get(campo)
                    registro[campo] = novo_valor
                    registro[f"_INDICADOR_DADO_MANUAL_{campo}"] = True
                    logger.warning(
                        "[OVERRIDE MANUAL] CNPJ %s | %s alterado de '%s' para '%s'.", 
                        cnpj_normalizado, campo, valor_antigo, novo_valor
                    )
            return
    
    cnpjs_no_override = {k[0] for k in overrides_dict.keys()}
    if cnpj_normalizado in cnpjs_no_override:
        chaves_deste_cnpj = [k for k in overrides_dict.keys() if k[0] == cnpj_normalizado]
        for chave_override in chaves_deste_cnpj:
            data_override = chave_override[1]
            if data_normalizada is None:
                logger.warning(
                    "[OVERRIDE IGNORADO] CNPJ encontrado (%s), mas DATA_DEMONSTRACAO_FINANCEIRA da ficha é nula. Override esperava data: %s.",
                    cnpj_normalizado, data_override
                )
            else:
                logger.warning(
                    "[OVERRIDE IGNORADO] CNPJ encontrado (%s), mas divergência de data. Ficha: %s | Override: %s.",
                    cnpj_normalizado, data_normalizada, data_override
                )

def processar_arquivo_individual(
    source_file: Path,
    load_mode: str,
    processed_dir: Path,
    rejected_dir: Path,
    context: AppContext,
    layouts: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    master_catalog: dict[str, Any],
    overrides_dict: dict[tuple[str, str], list[dict[str, Any]]],
    control_dir: Path | None = None,
) -> Optional[dict[str, Any]]:
    """Processa de ponta a ponta um único arquivo de ficha de comercializadora."""
    workbook = None
    manifest = DocumentManifest(
        documento_id=str(uuid.uuid4()),
        run_id=run_id,
        ambiente=context.app_config["env"],
        tipo_ficha="COMERCIALIZADORA",
        arquivo_nome=source_file.name,
        caminho_origem=str(source_file),
        load_mode=load_mode,
    )

    try:
        logger.info("Iniciando processamento do arquivo %s em modo %s.", source_file.name, load_mode)
        manifest.hash_arquivo = arquivo_hash(source_file)

        if load_mode == "incremental" and tem_hash_duplicado(history, manifest.hash_arquivo):
            manifest.status_extracao = "ERRO_DUPLICIDADE_HASH"
            manifest.erros.append("Hash já processado anteriormente.")
            mover_para_rejeitados(source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir)
            return None

        staging_dir = context.path("staging_fichas_comercializadoras")
        staging_name = criar_nome_arquivo_padronizado(
            original_name=source_file.name, versao_ficha=None, cnpj=None, data_df=None, hash_value=manifest.hash_arquivo
        )
        staging_file = copiar_para_staging(source_file, staging_dir, staging_name)
        manifest.caminho_staging = str(staging_file)

        workbook = abrir_pasta(staging_file)
        from domain.fichas.extrator import extrair_registro_do_vencedor
        raw_record, metadata_list, winner_layout = extrair_registro_do_vencedor(workbook, layouts, master_catalog)
        
        if winner_layout == "DOC_001_ESTRUTURA_INCOMPATIVEL":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            msg = "DOC_001_ESTRUTURA_INCOMPATIVEL: Nenhuma aba compativel com o layout esperada foi encontrada."
            manifest.erros.append(msg)
            registrar_alerta(
                codigo="DOC_001",
                severidade="ALTO",
                regra="Estrutura de Ficha Incompatível",
                mensagem=msg,
                campo_afetado="CLASSIFICACAO_DOCUMENTO",
                valor_observado="Desconhecido",
                limite_esperado="Layout mapeado",
                contraparte_id=None,
                run_id=run_id,
                context=context
            )
            fechar_pasta(workbook)
            mover_para_rejeitados(source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir)
            return None
            
        score_campeao = raw_record.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        
        if raw_record.get("_FALHA_GATE_CRITICO"):
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_DADOS_CRITICOS_AUSENTES"
            manifest.erros.append("Ficha falhou nos GATES de segurança (Campos obrigatórios ausentes).")
            fechar_pasta(workbook)
            mover_para_rejeitados(source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir)
            return None
            
        if not winner_layout or winner_layout == "NENHUM" or score_campeao < 40.0:
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_INTEGRIDADE"
            manifest.erros.append(f"Score insuficiente: {score_campeao}%. Minimo exigido: 40.0%.")
            fechar_pasta(workbook)
            mover_para_rejeitados(source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir)
            return None

        manifest.versao_ficha = winner_layout
        manifest.status_classificacao = "CLASSIFICADO"
        
        if control_dir and metadata_list:
            registrar_linhagem_campos(manifest.documento_id, manifest.run_id, metadata_list, control_dir)
            
        normalized = normalizar_registro(raw_record, master_catalog, logger)
        normalized["TIPO_FICHA"] = "COMERCIALIZADORA"
        
        from silver.mapeador_dominio import aplicar_normalizacao_de_dominio
        normalized = aplicar_normalizacao_de_dominio(normalized, context, logger)
        
        from domain.fichas.derivador_financeiro import calcular_indicadores_derivados
        normalized = calcular_indicadores_derivados(normalized)

        aplicar_overrides_manuais(normalized, overrides_dict, logger)

        manifest.cnpj_extraido = normalized.get("CNPJ")
        manifest.data_demonstracao_financeira = normalized.get("DATA_DEMONSTRACAO_FINANCEIRA")
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        errors, warnings = validar_registro(record=normalized, master_catalog=master_catalog, logger=logger)
        integridade = normalized.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        
        manifest.erros.extend(errors)
        manifest.avisos.extend(warnings)
        
        if errors or integridade < 40.0 or not manifest.cnpj_extraido:
            manifest.status_extracao = "ERRO_VALIDACAO_GATES" if errors else ("ERRO_INTEGRIDADE" if integridade < 40.0 else "ERRO_SEM_CNPJ")
            fechar_pasta(workbook)
            mover_para_rejeitados(source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir)
            return None

        resultado_cnpj = normalizar_cnpj(manifest.cnpj_extraido)
        if not resultado_cnpj.valido:
            manifest.status_extracao = "ERRO_CNPJ_INVALIDO"
            fechar_pasta(workbook)
            mover_para_rejeitados(source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir)
            return None
        
        manifest.cnpj_extraido = resultado_cnpj.cnpj
        normalized["CNPJ"] = resultado_cnpj.cnpj
        normalized["CNPJ_RAIZ"] = resultado_cnpj.raiz

        if tem_chave_de_negocio_duplicada(history, manifest.cnpj_extraido, manifest.data_demonstracao_financeira):
            manifest.reprocessed = True
            manifest.previous_record_found = True
        else:
            manifest.reprocessed = False
            manifest.previous_record_found = False

        fechar_pasta(workbook)
        workbook = None

        bronze_root_dir = context.path("bronze_fichas_comercializadoras_raw")
        bronze_name = criar_nome_arquivo_padronizado(
            original_name=source_file.name, versao_ficha=manifest.versao_ficha, cnpj=manifest.cnpj_extraido,
            data_df=manifest.data_demonstracao_financeira, hash_value=manifest.hash_arquivo,
        )

        bronze_subfolder = resolver_subpasta_bronze(manifest.cnpj_extraido, normalized.get("SIGLA"))
        bronze_staging = copiar_para_staging(staging_file, staging_dir, bronze_name)
        bronze_file = publicar_arquivo_bruto(source_file=bronze_staging, bronze_root_dir=bronze_root_dir / bronze_subfolder)
        
        manifest.caminho_bronze = str(bronze_file)
        manifest.status_extracao = "SUCESSO"

        mover_para_processados(source_file, processed_dir, manifest, ingestion_log_path, logger, control_dir)
        virar_chave_de_negocio_no_historico(history, manifest.to_dict())

        silver_record = {
            **normalized,
            "documento_id": manifest.documento_id,
            "run_id": run_id,
            "ambiente": manifest.ambiente,
            "versao_ficha": manifest.versao_ficha,
            "arquivo_nome": manifest.arquivo_nome,
            "hash_arquivo": manifest.hash_arquivo,
            "load_mode": load_mode,
            "dt_processamento": datetime.now().isoformat(timespec="seconds"),
        }

        from domain.fichas.validador import validar_schema
        schema_errors = validar_schema(silver_record, logger)
        if schema_errors:
            manifest.status_extracao = "ERRO_CONTRATO_SILVER"
            manifest.erros.extend(schema_errors)
            logger.warning("Violação de contrato Silver para CNPJ=%s: %s", manifest.cnpj_extraido, schema_errors)

        classified_document = criar_documento_classificado(
            documento_id=manifest.documento_id, run_id=run_id, ambiente=manifest.ambiente,
            arquivo_nome=manifest.arquivo_nome or "", versao_ficha=manifest.versao_ficha or "",
            TIPO_FICHA=manifest.tipo_ficha, hash_arquivo=manifest.hash_arquivo or ""
        )

        return {"silver_record": silver_record, "classified_document": classified_document}

    except Exception as exc:
        if workbook: fechar_pasta(workbook)
        manifest.status_extracao = "ERRO_PROCESSAMENTO"
        manifest.erros.append(str(exc))
        logger.error(f"Erro processando arquivo {source_file.name}: {exc}")
        import traceback
        logger.error(traceback.format_exc())
        try:
            mover_para_rejeitados(source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir)
        except Exception:
            pass
        return None

def processar_fichas_comercializadoras(context: AppContext) -> dict[str, Any]:
    """Executa o pipeline de ingestão purificado das fichas de comercializadoras."""
    run_id = criar_run_id(context)
    log_file = Path("LOGS/execucao") / f"{run_id}__fichas_comercializadoras.log"
    logger = obter_logger("bdc.comercializadoras", log_file)

    _ = mapeamento_de_carga_fichas_comercializadoras(context, logger)
    layouts = carregar_layouts_comercializadoras(context, logger)
    
    catalog_path = context.path("control_quality") / "master_catalog_comercializadoras.json"
    master_catalog = ler_json(catalog_path)

    ingestion_log_path = context.path("bronze_ingestion_log") / "fichas_comercializadoras_ingestion.jsonl"
    history = historico_de_ingestao_de_carga(ingestion_log_path)

    silver_records: list[dict[str, Any]] = []
    classified_documents: list[dict[str, Any]] = []

    eventos_manuais_path = context.path("silver") / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"
    overrides_dict = carregar_overrides_manuais(eventos_manuais_path, logger)

    queue = criar_fila_processamento(context, "comercializadoras")
    logger.info("Iniciando processamento: %s fichas detectadas.", len(queue))

    for source_file, load_mode, processed_dir, rejected_dir in queue:
        result = processar_arquivo_individual(
            source_file=source_file, load_mode=load_mode, processed_dir=processed_dir,
            rejected_dir=rejected_dir, context=context, layouts=layouts,
            history=history, ingestion_log_path=ingestion_log_path, logger=logger,
            run_id=run_id, master_catalog=master_catalog, overrides_dict=overrides_dict,
            control_dir=context.path("relational_control"),
        )

        if result:
            silver_records.append(result["silver_record"])
            classified_documents.append(result["classified_document"])

    silver_output_dir = context.path("silver_fichas_comercializadoras_extraidas")
    docs_output_dir = context.path("silver_documentos_classificados")

    if silver_records:
        mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
            records=silver_records, output_dir=silver_output_dir,
            filename="fichas_comercializadoras_extraidas.csv", business_keys=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA"],
        )

    if classified_documents:
        escrever_conjunto_de_dados_silver(
            records=classified_documents, output_dir=docs_output_dir, filename=f"documentos_classificados__{run_id}",
        )

    summary = {
        "run_id": run_id, "arquivos_recebidos": len(queue), "registros_silver": len(silver_records),
        "metricas_qualidade": {
            "cobertura_fco": f"{(sum(1 for r in silver_records if r.get('FCO') is not None) / len(silver_records) * 100):.1f}%" if silver_records else "0%"
        }
    }
    logger.info("Resumo do processamento: %s", summary)
    return summary
```


---

## `src/app/config_builder.py`

- Linhas: 17
- SHA-256: `70e131ff82912665892e62669e54027f97661d38dd66ee0053e48de072666dda`
- Classes: AppConfigBuilder
- Funções: __init__, resolve_dict

```python
"""Builder programático para resolução de caminhos do sistema."""

from pathlib import Path
from typing import Any

class AppConfigBuilder:
    """Construtor responsável por aplicar o diretório base à topologia relativa."""
    
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir).resolve()

    def resolve_dict(self, paths_dict: dict[str, Any]) -> dict[str, str]:
        """Resolve todos os caminhos relativos de um dicionário contra o diretório base."""
        resolved = {}
        for key, relative_path in paths_dict.items():
            resolved[key] = str(self.base_dir / relative_path)
        return resolved
```


---

## `src/app/consumidores/orquestrador_consumidores.py`

- Linhas: 605
- SHA-256: `d51417a7dcc8e13ff7f485303e4b7c149a0d86b8a2d48b94c2a1dc8ccc24f4fd`
- Classes: -
- Funções: carregar_overrides_manuais, aplicar_overrides_manuais, processar_arquivo_individual, processar_fichas_consumidores

```python
"""Serviço principal refatorado do pipeline de fichas de consumidores."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.context import AppContext
from relational.facts.fato_alerta_util import registrar_alerta
from common.excel import fechar_pasta, abrir_pasta
from common.hashing import arquivo_hash
from common.json import ler_json
from control.logger import obter_logger
from common.identificadores import normalizar_cnpj
from common.nulos import is_nulo_textual

from control.layout_catalog import carregar_layouts_consumidores
from control.carregador_de_mapeamento import mapeamento_de_carga_fichas_consumidores
from control.quality_loader import carregar_regras_de_qualidade_de_dados_consumidores
from common.servico_desduplicacao import (
    tem_chave_de_negocio_duplicada,
    tem_hash_duplicado,
    virar_chave_de_negocio_no_historico,
)
from domain.fichas.validador import validar_registro_consumidor
from domain.consumidores.classificacao import (
    classificar_consumidor,
    criar_classificacao_registro,
    VERSAO_REGRA_ATUAL,
)
from silver.documentos_classificados import criar_documento_classificado
from silver.formatador_silver import normalizar_registro
from staging.staging_arquivo import copiar_para_staging
from storage.bronze_arquivo import publicar_arquivo_bruto
from storage.armazenamento_manifest import (
    historico_de_ingestao_de_carga,
)
from storage.escrever_dados import (
    mesclar_conjunto_de_dados_prata_por_chave_de_negocio,
    escrever_conjunto_de_dados_silver,
)
from storage.estado_armazenamento import DocumentManifest
from common.utils_orquestracao import (
    disco_cheio_erro,
    criar_run_id,
    criar_nome_arquivo_padronizado,
    resolver_subpasta_bronze,
    criar_fila_processamento,
    mover_para_rejeitados,
    mover_para_processados
)

def carregar_overrides_manuais(eventos_manuais_path: Path, logger: Any) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """Carrega de forma segura os dados de overrides manuais armazenados em formato Parquet."""
    overrides_dict: dict[tuple[str, str], list[dict[str, Any]]] = {}
    if not eventos_manuais_path.exists():
        logger.info("Nenhuma base de Carga Manual encontrada em %s", eventos_manuais_path)
        return overrides_dict
        
    try:
        import pandas as pd
        df_overrides = pd.read_parquet(eventos_manuais_path)
        
        if df_overrides.empty:
            return overrides_dict
            
        if "_STATUS_REGISTRO" in df_overrides.columns:
            df_overrides = df_overrides[df_overrides["_STATUS_REGISTRO"] == "VIGENTE"]
            
        df_overrides = df_overrides.dropna(subset=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "CAMPO_AFETADO"])
        
        from common.identificadores import normalizar_cnpj as _normalizar_cnpj
        from common.datas import normalizar_data
        
        for row in df_overrides.to_dict(orient="records"):
            res_cnpj = _normalizar_cnpj(row.get("CNPJ"))
            cnpj_over = res_cnpj.cnpj if res_cnpj.valido else None
            data_over = normalizar_data(row.get("DATA_DEMONSTRACAO_FINANCEIRA"))
            
            if not cnpj_over or not data_over:
                continue
                
            chave = (cnpj_over, data_over)
            
            if chave not in overrides_dict:
                overrides_dict[chave] = []
                
            valor_salvo = row.get("VALOR_NOVO")
            valor_tratado = valor_salvo
            
            if isinstance(valor_salvo, str):
                try:
                    valor_tratado = float(valor_salvo)
                except ValueError:
                    pass
                
            campo_afetado = str(row.get("CAMPO_AFETADO", "")).strip().upper().replace(" ", "_")
            
            overrides_dict[chave].append({
                "campo": campo_afetado if campo_afetado and campo_afetado != "NONE" else row.get("CAMPO_AFETADO"),
                "valor": valor_tratado
            })
            
        logger.info("Base de Overrides carregada: %d chaves vigentes.", len(overrides_dict))
    except Exception:
        logger.exception("Falha ao carregar overrides Parquet. Ignorando carga manual.")
        
    return overrides_dict

def aplicar_overrides_manuais(
    registro: dict[str, Any], 
    overrides_dict: dict[tuple[str, str], list[dict[str, Any]]], 
    logger: Any
) -> None:
    """Aplica as atualizações manuais injetando os valores na ficha normalizada."""
    from common.identificadores import normalizar_cnpj as _normalizar_cnpj
    from common.datas import normalizar_data
    
    cnpj_atual = registro.get("CNPJ")
    data_bruta = registro.get("DATA_DEMONSTRACAO_FINANCEIRA")
    
    if not cnpj_atual:
        return
        
    res_cnpj = _normalizar_cnpj(cnpj_atual)
    cnpj_normalizado = res_cnpj.cnpj if res_cnpj.valido else None
    
    if not cnpj_normalizado:
        return
    
    data_normalizada = normalizar_data(data_bruta) if data_bruta else None
    
    if data_normalizada:
        chave_atual = (cnpj_normalizado, data_normalizada)
        if chave_atual in overrides_dict:
            for override in overrides_dict[chave_atual]:
                campo = override["campo"]
                novo_valor = override["valor"]
                if campo:
                    valor_antigo = registro.get(campo)
                    registro[campo] = novo_valor
                    registro[f"_INDICADOR_DADO_MANUAL_{campo}"] = True
                    logger.warning(
                        "[OVERRIDE MANUAL] CNPJ %s | %s alterado de '%s' para '%s'.", 
                        cnpj_normalizado, campo, valor_antigo, novo_valor
                    )
            return
    
    cnpjs_no_override = {k[0] for k in overrides_dict.keys()}
    if cnpj_normalizado in cnpjs_no_override:
        chaves_deste_cnpj = [k for k in overrides_dict.keys() if k[0] == cnpj_normalizado]
        for chave_override in chaves_deste_cnpj:
            data_override = chave_override[1]
            if data_normalizada is None:
                logger.warning(
                    "[OVERRIDE IGNORADO] CNPJ encontrado (%s), mas DATA_DEMONSTRACAO_FINANCEIRA da ficha é nula. Override esperava data: %s.",
                    cnpj_normalizado, data_override
                )
            else:
                logger.warning(
                    "[OVERRIDE IGNORADO] CNPJ encontrado (%s), mas divergência de data. Ficha: %s | Override: %s.",
                    cnpj_normalizado, data_normalizada, data_override
                )

def processar_arquivo_individual(
    source_file: Path,
    load_mode: str,
    processed_dir: Path,
    rejected_dir: Path,
    context: AppContext,
    layouts: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    master_catalog: dict[str, Any],
    overrides_dict: dict[tuple[str, str], list[dict[str, Any]]],
    control_dir: Path | None = None,
) -> Optional[dict[str, Any]]:
    """Processa isoladamente um único arquivo de ficha de consumidor."""
    workbook = None
    manifest = DocumentManifest(
        documento_id=str(uuid.uuid4()),
        run_id=run_id,
        ambiente=context.app_config["env"],
        tipo_ficha="CONSUMIDOR",
        arquivo_nome=source_file.name,
        caminho_origem=str(source_file),
        load_mode=load_mode,
    )

    try:
        logger.info(
            "Iniciando processamento do arquivo %s em modo %s.",
            source_file.name,
            load_mode,
        )

        manifest.hash_arquivo = arquivo_hash(source_file)

        if load_mode == "incremental" and tem_hash_duplicado(
            history, manifest.hash_arquivo
        ):
            manifest.status_extracao = "ERRO_DUPLICIDADE_HASH"
            manifest.erros.append("Hash já processado anteriormente.")
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        staging_dir = context.path("staging_fichas_consumidores")
        staging_name = criar_nome_arquivo_padronizado(
            original_name=source_file.name,
            versao_ficha=None,
            cnpj=None,
            data_df=None,
            hash_value=manifest.hash_arquivo,
        )
        staging_file = copiar_para_staging(source_file, staging_dir, staging_name)
        manifest.caminho_staging = str(staging_file)

        workbook = abrir_pasta(staging_file)
        from domain.fichas.extrator import extrair_registro_do_vencedor

        raw_record, metadata_list, winner_layout = extrair_registro_do_vencedor(workbook, layouts, master_catalog)

        if winner_layout == "DOC_001_ESTRUTURA_INCOMPATIVEL":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            msg = "DOC_001_ESTRUTURA_INCOMPATIVEL: Nenhuma aba compativel com o layout esperada foi encontrada."
            manifest.erros.append(msg)
            registrar_alerta(
                codigo="DOC_001",
                severidade="ALTO",
                regra="Estrutura de Ficha Incompatível",
                mensagem=msg,
                campo_afetado="CLASSIFICACAO_DOCUMENTO",
                valor_observado="Desconhecido",
                limite_esperado="Layout mapeado",
                contraparte_id=None,
                run_id=run_id,
                context=context
            )
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if not winner_layout or winner_layout == "NENHUM":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("Nenhum layout obteve score suficiente.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        manifest.versao_ficha = winner_layout
        manifest.status_classificacao = "CLASSIFICADO"

        logger.info(
            "Extração competitiva: Vencedor %s identificado para %s.",
            winner_layout,
            source_file.name,
        )

        classification = type("MockClassification", (), {"versao_ficha": winner_layout})()
        
        if control_dir and metadata_list:
            from domain.auditoria.servico_auditoria import registrar_linhagem_campos
            registrar_linhagem_campos(manifest.documento_id, manifest.run_id, metadata_list, control_dir)
        
        normalized = normalizar_registro(raw_record, master_catalog, logger)
        normalized.pop("DADOS_CADASTRAIS", None)
        normalized["TIPO_FICHA"] = "CONSUMIDOR"
        
        from silver.mapeador_dominio import aplicar_normalizacao_de_dominio
        normalized = aplicar_normalizacao_de_dominio(normalized, context, logger)

        from domain.fichas.derivador_financeiro import calcular_indicadores_derivados
        normalized = calcular_indicadores_derivados(normalized)

        aplicar_overrides_manuais(normalized, overrides_dict, logger)

        manifest.cnpj_extraido = normalized.get("CNPJ")
        manifest.data_demonstracao_financeira = normalized.get(
            "DATA_DEMONSTRACAO_FINANCEIRA"
        )
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        classificacao = classificar_consumidor(
            record=normalized,
            versao_layout=classification.versao_ficha,
        )

        logger.info(
            "Classificação documental para %s: tipo=%s analise=%s confianca=%s",
            source_file.name,
            classificacao.tipo_consumidor,
            classificacao.tipo_analise_exigida,
            classificacao.confianca_classificacao,
        )

        campos_financeiros_globais = [
            "ATIVO_CIRCULANTE", "ATIVO_TOTAL", "PASSIVO_CIRCULANTE", "PATRIMONIO_LIQUIDO",
            "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "ROA", "ROE", "FCO_ROL", "FCO"
        ]

        if getattr(classificacao, "tipo_analise_exigida", "") == "simplificada":
            for campo in campos_financeiros_globais:
                normalized[campo] = None
                
        # Regra 14.8 (Global para qualquer consumidor, detalhada ou não): 
        # Se DF for nula ou não aplicável, garante que 0.0 vire nulo para não mascarar score.
        dt_df = normalized.get("DATA_DEMONSTRACAO_FINANCEIRA")
        if not dt_df or str(dt_df).upper() == "NAO_APLICAVEL" or is_nulo_textual(dt_df):
            for campo in campos_financeiros_globais:
                if normalized.get(campo) == 0.0 or normalized.get(campo) == 0:
                    normalized[campo] = None

        errors, warnings = validar_registro_consumidor(
            record=normalized,
            master_catalog=master_catalog,
            classificacao=classificacao,
            logger=logger,
        )
        
        integridade = normalized.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        if integridade >= 40.0:
            critical_errors = []
            for e in errors:
                if "ausente" in e.lower() or "não informado" in e.lower() or "não informada" in e.lower():
                    warnings.append(f"Ignorado por Integridade >= 40%: {e}")
                else:
                    critical_errors.append(e)
            errors = critical_errors

        manifest.erros.extend(errors)
        manifest.avisos.extend(warnings)

        if integridade < 40.0:
            manifest.status_extracao = "ERRO_INTEGRIDADE"
            manifest.erros.append(f"Integridade baixa: {integridade}% (mínimo 40%). Ficha rejeitada.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if not manifest.cnpj_extraido:
            manifest.status_extracao = "ERRO_SEM_CNPJ"
            manifest.erros.append("Ficha sem CNPJ válido.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        resultado_cnpj = normalizar_cnpj(manifest.cnpj_extraido)
        if not resultado_cnpj.valido:
            manifest.status_extracao = "ERRO_CNPJ_INVALIDO"
            manifest.erros.append(f"CNPJ inválido: {manifest.cnpj_extraido}")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        manifest.cnpj_extraido = resultado_cnpj.cnpj
        normalized["CNPJ"] = resultado_cnpj.cnpj
        normalized["CNPJ_RAIZ"] = resultado_cnpj.raiz

        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO"
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        duplicate_business = tem_chave_de_negocio_duplicada(
            history,
            manifest.cnpj_extraido,
            manifest.data_demonstracao_financeira,
        )

        if duplicate_business and load_mode == "incremental":
            manifest.status_extracao = "ERRO_DUPLICIDADE_NEGOCIO"
            manifest.erros.append(
                "Já existe documento com mesmo CNPJ e data da DF."
            )
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if duplicate_business and load_mode == "reprocess":
            manifest.reprocessed = True
            manifest.previous_record_found = True
        elif load_mode == "reprocess":
            manifest.reprocessed = False
            manifest.previous_record_found = False

        fechar_pasta(workbook)
        workbook = None

        bronze_root_dir = context.path("bronze_fichas_consumidores_raw")
        bronze_name = criar_nome_arquivo_padronizado(
            original_name=source_file.name,
            versao_ficha=manifest.versao_ficha,
            cnpj=manifest.cnpj_extraido,
            data_df=manifest.data_demonstracao_financeira,
            hash_value=manifest.hash_arquivo,
        )

        bronze_subfolder = resolver_subpasta_bronze(
            manifest.cnpj_extraido,
            normalized.get("EMPRESA"),
        )

        bronze_staging = copiar_para_staging(
            staging_file, staging_dir, bronze_name
        )
        bronze_file = publicar_arquivo_bruto(
            source_file=bronze_staging,
            bronze_root_dir=bronze_root_dir / bronze_subfolder,
        )
        manifest.caminho_bronze = str(bronze_file)
        manifest.status_extracao = "SUCESSO"

        mover_para_processados(
            source_file, processed_dir, manifest, ingestion_log_path, logger, control_dir
        )
        virar_chave_de_negocio_no_historico(history, manifest.to_dict())

        logger.info("Ficha processada com sucesso: %s.", source_file.name)

        classificacao_record = criar_classificacao_registro(classificacao)

        silver_record = {
            **normalized,
            **classificacao_record,
            "documento_id": manifest.documento_id,
            "run_id": run_id,
            "ambiente": manifest.ambiente,
            "versao_ficha": manifest.versao_ficha,
            "arquivo_nome": manifest.arquivo_nome,
            "hash_arquivo": manifest.hash_arquivo,
            "load_mode": load_mode,
            "dt_processamento": datetime.now().isoformat(timespec="seconds"),
        }

        from domain.fichas.validador import validar_schema
        schema_errors = validar_schema(silver_record, logger)
        if schema_errors:
            manifest.status_extracao = "ERRO_CONTRATO_SILVER"
            manifest.erros.extend(schema_errors)
            logger.warning("Violação de contrato Silver para CNPJ=%s: %s", manifest.cnpj_extraido, schema_errors)

        classified_document = criar_documento_classificado(
            documento_id=manifest.documento_id,
            run_id=run_id,
            ambiente=manifest.ambiente,
            arquivo_nome=manifest.arquivo_nome or "",
            versao_ficha=manifest.versao_ficha or "",
            TIPO_FICHA=manifest.tipo_ficha,
            hash_arquivo=manifest.hash_arquivo or "",
        )

        return {
            "silver_record": silver_record,
            "classified_document": classified_document,
        }

    except Exception as exc:
        if workbook:
            fechar_pasta(workbook)

        manifest.status_extracao = "ERRO_PROCESSAMENTO"
        manifest.erros.append(str(exc))

        if disco_cheio_erro(exc):
            logger.exception(
                "Execução interrompida por falta de espaço em disco ao processar %s.",
                source_file.name,
            )
            raise

        try:
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
        except Exception as move_exc:
            if disco_cheio_erro(move_exc):
                logger.exception(
                    "Execução interrompida por falta de espaço em disco ao registrar rejeição do arquivo %s.",
                    source_file.name,
                )
                raise

            logger.exception(
                "Falha adicional ao mover/gravar rejeição do arquivo %s.",
                source_file.name,
            )
            raise

        logger.exception("Falha inesperada ao processar %s.", source_file.name)
        return None


def processar_fichas_consumidores(
    context: AppContext,
) -> dict[str, Any]:
    """Executa o pipeline completo das fichas de consumidores."""
    run_id = criar_run_id(context)

    log_file = (
        Path("LOGS/execucao") / f"{run_id}__fichas_consumidores.log"
    )
    logger = obter_logger("bdc.consumidores", log_file)

    _ = mapeamento_de_carga_fichas_consumidores(context, logger)

    layouts = carregar_layouts_consumidores(context, logger)
    master_catalog = carregar_regras_de_qualidade_de_dados_consumidores(context, logger)

    ingestion_log_path = (
        context.path("bronze_ingestion_log")
        / "fichas_consumidores_ingestion.jsonl"
    )
    history = historico_de_ingestao_de_carga(ingestion_log_path)

    silver_records: list[dict[str, Any]] = []
    classified_documents: list[dict[str, Any]] = []

    eventos_manuais_path = context.path("silver") / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"
    overrides_dict = carregar_overrides_manuais(eventos_manuais_path, logger)

    queue = criar_fila_processamento(context, "consumidores")

    normal_count = sum(1 for _, mode, _, _ in queue if mode == "incremental")
    reprocess_count = sum(1 for _, mode, _, _ in queue if mode == "reprocess")

    logger.info(
        "Iniciando processamento de %s fichas (%s normais, %s reprocessamento).",
        len(queue),
        normal_count,
        reprocess_count,
    )

    for source_file, load_mode, processed_dir, rejected_dir in queue:
        result = processar_arquivo_individual(
            source_file=source_file,
            load_mode=load_mode,
            processed_dir=processed_dir,
            rejected_dir=rejected_dir,
            context=context,
            layouts=layouts,
            history=history,
            ingestion_log_path=ingestion_log_path,
            logger=logger,
            run_id=run_id,
            master_catalog=master_catalog,
            overrides_dict=overrides_dict,
            control_dir=context.path("relational_control"),
        )

        if result:
            silver_records.append(result["silver_record"])
            classified_documents.append(result["classified_document"])

    silver_output_dir = context.path("silver_fichas_consumidores_extraidas")
    docs_output_dir = context.path("silver_documentos_classificados")

    if silver_records:
        mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
            records=silver_records,
            output_dir=silver_output_dir,
            filename="fichas_consumidores_extraidas.csv",
            business_keys=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA"],
        )

    if classified_documents:
        escrever_conjunto_de_dados_silver(
            records=classified_documents,
            output_dir=docs_output_dir,
            filename=f"documentos_classificados__{run_id}",
        )

    summary = {
        "run_id": run_id,
        "arquivos_recebidos": len(queue),
        "arquivos_normais": normal_count,
        "arquivos_reprocessamento": reprocess_count,
        "registros_silver": len(silver_records),
        "documentos_classificados": len(classified_documents),
    }

    logger.info("Resumo do processamento: %s", summary)
    return summary
```


---

## `src/app/context.py`

- Linhas: 92
- SHA-256: `7c4799b8ae896eeea3a23f651ee80d0647a05f078b670e1f6e9ecb89180963ae`
- Classes: AppContext
- Funções: path, control_file, carregar_contexto

```python
"""Carregamento do contexto de execução do sistema BDC."""

from __future__ import annotations

import os
import sys
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app.config_builder import AppConfigBuilder
from common.json import ler_json, validar_esquema_json

logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class AppContext:
    app_config: dict[str, Any]
    config: dict[str, Any]
    paths: dict[str, Any]
    control_files: dict[str, Any]
    naming: dict[str, Any]

    def path(self, key: str) -> Path:
        return Path(self.paths[key])

    def control_file(self, key: str) -> Path:
        return Path(self.control_files[key])


def carregar_contexto(configs_dir: str | Path) -> AppContext:
    configs_path = Path(configs_dir)

    base_dir_env = os.getenv("BDC_BASE_DIR")
    if not base_dir_env:
        logger.critical("Variavel BDC_BASE_DIR nao encontrada no arquivo .env!")
        sys.exit(1)

    if not configs_path.exists():
        logger.critical("Diretório de configs não encontrado: %s", configs_path)
        sys.exit(1)

    app_config_path = configs_path / "app_config.json"
    config_path = configs_path / "config.json"

    if not app_config_path.exists() or not config_path.exists():
        logger.critical("Arquivos de configuração base não encontrados.")
        sys.exit(1)

    app_config = ler_json(app_config_path)
    config = ler_json(config_path)

    try:
        raw_paths = app_config["paths"]
        raw_control_files = app_config["control_files"]
    except KeyError as e:
        logger.critical("app_config.json malformado. Chave ausente: %s", e)
        sys.exit(1)

    builder = AppConfigBuilder(base_dir_env)
    resolved_paths = builder.resolve_dict(raw_paths)
    resolved_control_files = builder.resolve_dict(raw_control_files)

    schema_app_config_path = Path(resolved_control_files["schema_app_config"])
    schema_config_path = Path(resolved_control_files["schema_config"])

    if not schema_app_config_path.exists() or not schema_config_path.exists():
        logger.critical("Arquivos de schema de configuração não encontrados.")
        sys.exit(1)

    schema_app_config = ler_json(schema_app_config_path)
    schema_config = ler_json(schema_config_path)

    validar_esquema_json(app_config, schema_app_config, "app_config.json")
    validar_esquema_json(config, schema_config, "config.json")

    app_config["base_dir"] = str(builder.base_dir)
    app_config["paths"] = resolved_paths
    app_config["control_files"] = resolved_control_files

    return AppContext(
        app_config=app_config,
        config=config,
        paths=resolved_paths,
        control_files=resolved_control_files,
        naming=app_config.get("naming", {}),
    )
```


---

## `src/cli/__init__.py`

- Linhas: 1
- SHA-256: `c0fea4204125e107b4e18bdffe64ae25285e656a10e210754100fdc2aefb7fb2`
- Classes: -
- Funções: -

```python
"""Comandos de linha do sistema BDC."""
```


---

## `src/cli/rodar_fichas_comercializadoras.py`

- Linhas: 52
- SHA-256: `ded76cf9e310e90db17e2687075b5f5cfae24710f870c4a2982f55e6b4621fdf`
- Classes: -
- Funções: criar_analisador, main

```python
import argparse
import sys
from pathlib import Path

from pyautogui import click

from src.app.bootstrap import aplicativo_bootstrap
from app.comercializadoras.orquestrador_comercializadoras import processar_fichas_comercializadoras
from control.logger import obter_logger


def criar_analisador() -> argparse.ArgumentParser:
    """
    Constrói o parser de argumentos de linha de comando para o script de comercializadoras.
    """
    parser = argparse.ArgumentParser(
        description="Processamento e geração de fichas de comercializadoras."
    )
    parser.add_argument(
        "--configs-dir",
        type=str,
        default=None,
        help=(
            "Caminho para o diretório de configurações (opcional). "
            "Se omitido, busca a variável de ambiente 'BDC_CONFIGS_DIR' "
            "ou utiliza o caminho relativo da raiz do projeto ('ENTRADAS/configs')."
        ),
    )
    return parser


def main() -> None:
    parser = criar_analisador()
    args, _ = parser.parse_known_args()

    try:
        app_ctx = aplicativo_bootstrap(configs_dir=args.configs_dir)
        logger = obter_logger("bdc.cli", Path("LOGS/execucao") / "cli_comercializadoras.log")
        logger.info("Contexto da aplicacao inicializado a partir de: %s", app_ctx.path('configs'))
        
        processar_fichas_comercializadoras(app_ctx)

    except Exception as exc:
        if 'logger' in locals():
            logger.error("Falha na execucao: %s", exc)
        else:
            sys.stderr.write(f"[ERRO] Falha na execucao: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
```


---

## `src/cli/rodar_fichas_consumidores.py`

- Linhas: 50
- SHA-256: `6a9b37827affadef589ce932dc4e381272e4dabcb55ac41cb14025e6feda1d4f`
- Classes: -
- Funções: criar_analisador, main

```python
import argparse
import sys
from pathlib import Path

from src.app.bootstrap import aplicativo_bootstrap
from app.consumidores.orquestrador_consumidores import processar_fichas_consumidores
from control.logger import obter_logger


def criar_analisador() -> argparse.ArgumentParser:
    """
    Constrói o parser de argumentos de linha de comando para o script de consumidores.
    """
    parser = argparse.ArgumentParser(
        description="Processamento e geração de fichas de consumidores."
    )
    parser.add_argument(
        "--configs-dir",
        type=str,
        default=None,
        help=(
            "Caminho para o diretório de configurações (opcional). "
            "Se omitido, busca a variável de ambiente 'BDC_CONFIGS_DIR' "
            "ou utiliza o caminho relativo da raiz do projeto ('ENTRADAS/configs')."
        ),
    )
    return parser


def main() -> None:
    parser = criar_analisador()
    args, _ = parser.parse_known_args()

    try:
        app_ctx = aplicativo_bootstrap(configs_dir=args.configs_dir)
        logger = obter_logger("bdc.cli", Path("LOGS/execucao") / "cli_consumidores.log")
        logger.info("Contexto da aplicacao inicializado a partir de: %s", app_ctx.path('configs'))
        
        processar_fichas_consumidores(app_ctx)

    except Exception as exc:
        if 'logger' in locals():
            logger.error("Falha na execucao: %s", exc)
        else:
            sys.stderr.write(f"[ERRO] Falha na execucao: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
```


# GRUPO: data_infrastructure


---

## `src/gold/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/gold/regras_gold.py`

- Linhas: 142
- SHA-256: `c9518fc3cb8e674aebba2a09020df4a8dbc9fe03c8f184029137f1bbeea158cd`
- Classes: -
- Funções: _load_status_domains, _safe_str, checar_contrato_obrigatorio, resolver_situacao_df, resolver_situacao_analise, classificar_exigencia, status_metodologia

```python
"""Regras de Negócio e Classificação da Visão Consolidada Gold."""

from __future__ import annotations
from typing import Any
import pandas as pd

import json
from pathlib import Path
from app.context import AppContext

def _load_status_domains() -> dict[str, list[str]]:
    try:
        # Pega do path padrao
        path = Path("ENTRADAS/control/quality/domain_dictionaries.json")
        if path.exists():
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
                return {
                    "SITUACAO_DF": list(d.get("SITUACAO_DF", {}).keys()),
                    "SITUACAO_ANALISE": list(d.get("SITUACAO_ANALISE", {}).keys()),
                    "STATUS_CONTRATUAL": list(d.get("STATUS_CONTRATUAL", {}).keys())
                }
    except Exception:
        pass
    return {
        "SITUACAO_DF": ["RECEBIDA", "NAO_RECEBIDA", "DISPENSADA"],
        "SITUACAO_ANALISE": ["VIGENTE", "VENCIDA", "NAO_POSSUI"],
        "STATUS_CONTRATUAL": ["CONTRATO_VIGENTE", "CONTRATO_FUTURO", "SEM_CONTRATO"]
    }

_STATUS_DOMAINS = _load_status_domains()

def _safe_str(val: Any) -> str:
    """Extrai string segura lidando com pd.NA."""
    if pd.isna(val):
        return ""
    return str(val).strip().upper()

def checar_contrato_obrigatorio(df: pd.DataFrame, colunas_obrigatorias: list[str], nome_dataset: str) -> None:
    """Valida se as colunas obrigatórias estão presentes no DataFrame."""
    if df is None or df.empty:
        return
    colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
    if colunas_faltantes:
        raise ValueError(
            f"Dataset '{nome_dataset}' viola o contrato de dados da Gold. "
            f"Colunas obrigatórias faltantes: {', '.join(colunas_faltantes)}"
        )

def resolver_situacao_df(row: Any) -> str:
    """Determina a situação da Demonstração Financeira (RECEBIDA, NAO_RECEBIDA, DISPENSADA)."""
    sit_atual = _safe_str(row.get("SITUACAO_DF"))
    if sit_atual in _STATUS_DOMAINS["SITUACAO_DF"]:
        return sit_atual
        
    data_df = row.get("DATA_BALANCO_USADO")
    if pd.isna(data_df):
        data_df = row.get("DATA_DEMONSTRACAO_FINANCEIRA")
    if pd.isna(data_df):
        data_df = row.get("DATA_DF")
        
    from common.nulos import is_nulo_textual
    if pd.notna(data_df) and not is_nulo_textual(data_df):
        return "RECEBIDA"
        
    tem_analise = _safe_str(row.get("TEM_ANALISE"))
    if tem_analise == "SIM":
        return "RECEBIDA"
        
    return "NAO_RECEBIDA"

def resolver_situacao_analise(row: Any) -> str:
    """Determina se a análise de crédito é VIGENTE, VENCIDA ou NAO_POSSUI."""
    sit_atual = _safe_str(row.get("SITUACAO_ANALISE"))
    if sit_atual in _STATUS_DOMAINS["SITUACAO_ANALISE"]:
        return sit_atual

    tem_analise = _safe_str(row.get("TEM_ANALISE"))
    if tem_analise != "SIM":
        return "NAO_POSSUI"

    data_anl = row.get("DATA_ANALISE")
    if pd.isna(data_anl):
        data_anl = row.get("DATA_CALCULO")
        
    from common.nulos import is_nulo_textual
    if is_nulo_textual(data_anl) or pd.isna(data_anl):
        return "VIGENTE"

    try:
        dt = pd.to_datetime(data_anl, errors="coerce")
        if pd.isna(dt):
            return "VIGENTE"
        hoje = pd.Timestamp.now().normalize()
        # Validade de 365 dias para análise de crédito
        if (hoje - dt).days <= 365:
            return "VIGENTE"
        else:
            return "VENCIDA"
    except Exception:
        return "VIGENTE"

def classificar_exigencia(row: Any) -> str:
    """Classifica a exigência metodológica de crédito (DF_DETALHADA, BUREAU, DISPENSADA)."""
    seg = _safe_str(row.get("SEGMENTO_METODOLOGICO"))
    if not seg:
        seg = _safe_str(row.get("TIPO_FICHA"))
        
    vol = row.get("VOLUME_MWM")
    try:
        vol_float = float(vol) if pd.notna(vol) else 0.0
    except (ValueError, TypeError):
        vol_float = 0.0

    if "COMERCIALIZADORA" in seg:
        return "DF_DETALHADA"

    if vol_float >= 5.0:
        return "DF_DETALHADA"
    elif vol_float > 0.0:
        return "BUREAU"
    else:
        return "DISPENSADA"

def status_metodologia(row: Any) -> str:
    """Calcula o status de conformidade metodológica (COMPLIANT, PENDENTE, IRREGULAR)."""
    exigencia = classificar_exigencia(row)
    sit_analise = resolver_situacao_analise(row)
    status_ctr = _safe_str(row.get("STATUS_CONTRATUAL"))

    if status_ctr not in _STATUS_DOMAINS["STATUS_CONTRATUAL"][:2]: # CONTRATO_VIGENTE, CONTRATO_FUTURO
        return "COMPLIANT"

    if exigencia == "DISPENSADA":
        return "COMPLIANT"

    if sit_analise == "VIGENTE":
        return "COMPLIANT"
    elif exigencia == "DF_DETALHADA":
        return "IRREGULAR"
    else:
        return "PENDENTE"
```


---

## `src/gold/servico_gold.py`

- Linhas: 509
- SHA-256: `9953e3f1e7831d1e6d5fcab2fe6798c1baae5a5acebcd78b30bc0f9dca28ae12`
- Classes: -
- Funções: carregar_entradas_gold, salvar_visao_gold, construir_visao_consolidada, extrair_rating_valido, extrair_pd_valido, exportar_visao_consolidada_gold

```python
import logging
from pathlib import Path
from typing import Any
import pandas as pd
from datetime import datetime

from common.dados import validar_coluna_cnpj_canonica
from control.logger import obter_logger
from gold.regras_gold import (
    resolver_situacao_df,
    resolver_situacao_analise,
    classificar_exigencia,
    status_metodologia,
    checar_contrato_obrigatorio
)

def carregar_entradas_gold(context: Any, logger: logging.Logger) -> dict[str, pd.DataFrame]:
    silver_dir = context.path("silver")
    rel_dim_dir = context.path("relational_dimensions")
    rel_fact_dir = context.path("relational_facts")
    
    path_contraparte = rel_dim_dir / "contrapartes" / "dim_contraparte.parquet"
    path_contratos = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_contratos.exists():
        path_contratos = silver_dir / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
        
    path_risco = rel_fact_dir / "risco" / "fato_exposicao_risco_LATEST.parquet"
    if not path_risco.exists():
        path_risco = silver_dir / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"

    path_analises = rel_fact_dir / "credito" / "fato_analise_credito.parquet"
    path_eventos_manuais = silver_dir / "governanca_carga_manual" / "eventos_manuais_consolidados.parquet"

    if not path_contraparte.exists():
        logger.error(f"Fonte obrigatória ausente: {path_contraparte}")
        raise FileNotFoundError(f"Fonte obrigatória ausente: {path_contraparte}. A dimensão de contraparte deve existir.")
    df_contraparte = pd.read_parquet(path_contraparte)

    if path_contratos.exists():
        df_contratos = pd.read_parquet(path_contratos)
    else:
        logger.warning(f"Base opcional de contratos ausente: {path_contratos}. Prosseguindo sem contratos.")
        df_contratos = pd.DataFrame()

    if path_analises.exists():
        df_analises = pd.read_parquet(path_analises)
    else:
        logger.warning(f"Base opcional de análises ausente: {path_analises}. Prosseguindo sem análises.")
        df_analises = pd.DataFrame()

    if path_risco.exists():
        df_risco = pd.read_parquet(path_risco)
    else:
        logger.warning(f"Base opcional de risco ausente: {path_risco}. Prosseguindo sem risco.")
        df_risco = pd.DataFrame()

    path_reconciliacao = rel_fact_dir / "reconciliacao" / "fato_reconciliacao_contrato_mtm.parquet"
    if path_reconciliacao.exists():
        df_reconciliacao = pd.read_parquet(path_reconciliacao)
    else:
        logger.warning(f"Base de reconciliação ausente: {path_reconciliacao}. Prosseguindo sem reconciliação.")
        df_reconciliacao = pd.DataFrame()

    if path_eventos_manuais.exists():
        df_eventos = pd.read_parquet(path_eventos_manuais)
    else:
        df_eventos = pd.DataFrame()

    path_bureau = silver_dir / "fato_bureau_silver" / "fato_bureau_silver.parquet"
    if path_bureau.exists():
        df_bureau = pd.read_parquet(path_bureau)
    else:
        df_bureau = pd.DataFrame()

    return {
        "contraparte": df_contraparte,
        "contratos": df_contratos,
        "analises": df_analises,
        "risco": df_risco,
        "eventos": df_eventos,
        "bureau": df_bureau,
        "reconciliacao": df_reconciliacao
    }

def salvar_visao_gold(context: Any, df_gold: pd.DataFrame, hoje: datetime, run_id: str, logger: logging.Logger):
    gold_dir = context.path("saidas") / "gold" / "visao_operacional_negocio"
    gold_dir.mkdir(parents=True, exist_ok=True)
    
    out_parquet = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.parquet"
    out_latest = gold_dir / "Visao_Operacional_BDC_LATEST.parquet"
    out_csv = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.csv"
    out_latest_csv = gold_dir / "Visao_Operacional_BDC_LATEST.csv"
    
    df_gold.to_parquet(out_parquet, index=False)
    df_gold.to_parquet(out_latest, index=False)
    df_gold.to_csv(out_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    df_gold.to_csv(out_latest_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

    logger.info("Visão Gold gerada. Total Contrapartes consolidadas: %d", len(df_gold))

def construir_visao_consolidada(dfs: dict[str, pd.DataFrame], run_id: str, hoje: datetime) -> pd.DataFrame:
    df_contraparte = dfs["contraparte"]
    df_contratos = dfs["contratos"]
    df_analises = dfs["analises"]
    df_risco = dfs["risco"]
    df_eventos = dfs.get("eventos", pd.DataFrame())
    df_bureau = dfs.get("bureau", pd.DataFrame())
    df_reconciliacao = dfs.get("reconciliacao", pd.DataFrame())

    if df_contraparte.empty:
        raise ValueError("O DataFrame obrigatório 'contraparte' não pode estar vazio.")

    erros = validar_coluna_cnpj_canonica(df_contraparte)
    if erros:
        raise ValueError("Dataset Silver fora do contrato (contraparte): " + "; ".join(erros))
    
    checar_contrato_obrigatorio(df_contraparte, ["CNPJ"], "contraparte")
    
    cols_contra = [c for c in ["CNPJ", "CNPJ_RAIZ", "SIGLA", "NOME", "SEGMENTO_METODOLOGICO", "SITUACAO_CADASTRAL"] if c in df_contraparte.columns]
    df_gold = df_contraparte[cols_contra].copy()

    # Garante que todo CNPJ com contrato sobreviva na Gold (mesmo sem contraparte mapeada)
    if not df_contratos.empty:
        cnpjs_contratos = set(df_contratos["CNPJ"].dropna().unique())
        cnpjs_gold = set(df_gold["CNPJ"].dropna().unique())
        cnpjs_faltantes = cnpjs_contratos - cnpjs_gold
        if cnpjs_faltantes:
            df_missing = pd.DataFrame({"CNPJ": list(cnpjs_faltantes)})
            df_missing["CNPJ_RAIZ"] = df_missing["CNPJ"].str[:8]
            df_gold = pd.concat([df_gold, df_missing], ignore_index=True)

    if not df_analises.empty:
        erros = validar_coluna_cnpj_canonica(df_analises)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (analises): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_analises, ["CNPJ"], "analises")
        
        if "DATA_CALCULO" in df_analises.columns and "DATA_ANALISE" not in df_analises.columns:
            df_analises["DATA_ANALISE"] = df_analises["DATA_CALCULO"]
        if "DATA_DEMONSTRACAO_FINANCEIRA" in df_analises.columns and "DATA_BALANCO_USADO" not in df_analises.columns:
            df_analises["DATA_BALANCO_USADO"] = df_analises["DATA_DEMONSTRACAO_FINANCEIRA"]
        if "DATA_DF" in df_analises.columns and "DATA_BALANCO_USADO" not in df_analises.columns:
            df_analises["DATA_BALANCO_USADO"] = df_analises["DATA_DF"]
            
        def extrair_rating_valido(row):
            from common.nulos import is_nulo_textual
            for col in ["RATING_COPEL", "NOTA_CREDITO", "NOTA_BOARD", "RATING"]:
                val = row.get(col)
                if pd.notna(val) and not is_nulo_textual(val):
                    return str(val).strip().upper()
            return pd.NA

        def extrair_pd_valido(row):
            from common.nulos import is_nulo_textual
            for col in ["PROBABILIDADE_DEFAULT", "PD_PERCENTUAL", "PD"]:
                val = row.get(col)
                if pd.notna(val) and not is_nulo_textual(val):
                    return val
            return pd.NA

        if "RATING_FINAL" not in df_analises.columns:
            df_analises["RATING_FINAL"] = df_analises.apply(extrair_rating_valido, axis=1)
            
        if "PD_FINAL" not in df_analises.columns:
            df_analises["PD_FINAL"] = df_analises.apply(extrair_pd_valido, axis=1)
            
        if "MODELO" in df_analises.columns and "MODELO_METODOLOGICO" not in df_analises.columns:
            df_analises["MODELO_METODOLOGICO"] = df_analises["MODELO"]
        if "versao_ficha" in df_analises.columns and "MODELO_METODOLOGICO" not in df_analises.columns:
            df_analises["MODELO_METODOLOGICO"] = df_analises["versao_ficha"]

        col_sort = "DATA_ANALISE" if "DATA_ANALISE" in df_analises.columns else ("DATA_BALANCO_USADO" if "DATA_BALANCO_USADO" in df_analises.columns else "CNPJ")
        if col_sort in df_analises.columns and col_sort != "CNPJ":
            df_analises["_DT_SORT"] = pd.to_datetime(df_analises[col_sort], errors="coerce")
            df_analises = df_analises.sort_values("_DT_SORT", na_position="first").drop_duplicates("CNPJ", keep="last")
        else:
            df_analises = df_analises.drop_duplicates("CNPJ", keep="last")

        dt_balanco = pd.to_datetime(df_analises.get("DATA_BALANCO_USADO"), errors="coerce")
        dt_analise = pd.to_datetime(df_analises.get("DATA_ANALISE"), errors="coerce")
        
        mask_balanco = (dt_balanco.dt.year > 1900) & (dt_balanco.notna())
        mask_analise = (dt_analise.dt.year > 1900) & (dt_analise.notna())
        
        df_analises["VALIDADE_DT"] = pd.NaT
        df_analises.loc[mask_balanco, "VALIDADE_DT"] = dt_balanco.loc[mask_balanco] + pd.DateOffset(years=1, months=4)
        df_analises.loc[~mask_balanco & mask_analise, "VALIDADE_DT"] = dt_analise.loc[~mask_balanco & mask_analise] + pd.DateOffset(years=1)

        if "SITUACAO_ANALISE" not in df_analises.columns:
            df_analises["SITUACAO_ANALISE"] = df_analises["VALIDADE_DT"].apply(
                lambda dt: "VIGENTE" if pd.notnull(dt) and dt >= hoje else ("VENCIDA" if pd.notnull(dt) else "VENCIDA")
            )
        else:
            mask_null = df_analises["SITUACAO_ANALISE"].isna() | (df_analises["SITUACAO_ANALISE"].astype(str).str.strip().isin(["", "None", "nan", "<NA>"]))
            df_analises.loc[mask_null, "SITUACAO_ANALISE"] = df_analises.loc[mask_null, "VALIDADE_DT"].apply(
                lambda dt: "VIGENTE" if pd.notnull(dt) and dt >= hoje else ("VENCIDA" if pd.notnull(dt) else "VENCIDA")
            )

        if "SITUACAO_DF" not in df_analises.columns:
            df_analises["SITUACAO_DF"] = "RECEBIDA"
        else:
            df_analises["SITUACAO_DF"] = df_analises["SITUACAO_DF"].fillna("RECEBIDA")


        df_analises["TEM_ANALISE"] = "SIM"
            
        cols_analise_payload = [
            c for c in [
                "SITUACAO_ANALISE", "SITUACAO_DF", "RATING_FINAL", "PD_FINAL", 
                "MODELO_METODOLOGICO", "PATRIMONIO_LIQUIDO", "DATA_ANALISE", "DATA_BALANCO_USADO", "TEM_ANALISE",
                "MOTIVO_AUSENCIA_DF", "TIPO_EVENTO_MANUAL", "ORIGEM_REGISTRO", "VALIDADE_EXCECAO", "STATUS_CALCULO_PD"
            ] if c in df_analises.columns
        ]

        df_gold = pd.merge(
            df_gold, 
            df_analises[["CNPJ"] + cols_analise_payload], 
            on="CNPJ", 
            how="left"
        )

        df_analises["_EH_MATRIZ"] = df_analises["CNPJ"].str[8:12] == "0001"
        sort_raiz = ["_EH_MATRIZ"]
        if "_DT_SORT" in df_analises.columns:
            sort_raiz.append("_DT_SORT")
            
        df_analises_raiz = (
            df_analises.sort_values(sort_raiz, ascending=[True] * len(sort_raiz))
            .drop_duplicates(subset=["CNPJ_RAIZ"], keep="last")
        )
        
        df_fallback = df_analises_raiz[["CNPJ_RAIZ"] + cols_analise_payload].copy()
        df_fallback.columns = ["CNPJ_RAIZ"] + [f"{c}_RAIZ" for c in cols_analise_payload]

        if "CNPJ_RAIZ" in df_gold.columns:
            df_gold = pd.merge(df_gold, df_fallback, on="CNPJ_RAIZ", how="left")
            for col in cols_analise_payload:
                col_raiz = f"{col}_RAIZ"
                if col_raiz in df_gold.columns:
                    df_gold[col] = df_gold[col].combine_first(df_gold[col_raiz])
                    df_gold = df_gold.drop(columns=[col_raiz])
    
    if "TEM_ANALISE" not in df_gold.columns:
        df_gold["TEM_ANALISE"] = "NÃO"
    df_gold["TEM_ANALISE"] = df_gold["TEM_ANALISE"].fillna("NÃO")

    if not df_contratos.empty:
        erros = validar_coluna_cnpj_canonica(df_contratos)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (contratos): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_contratos, ["CNPJ_RAIZ"], "contratos")

        col_vol = "VOLUME_CONTRATADO_MENSAL_MWM" if "VOLUME_CONTRATADO_MENSAL_MWM" in df_contratos.columns else "VOLUME_MWM"
        if col_vol in df_contratos.columns:
            df_contratos["VOLUME_MWM"] = pd.to_numeric(df_contratos[col_vol], errors="coerce").fillna(0.0)
        else:
            df_contratos["VOLUME_MWM"] = 0.0
        
        if "ano" in df_contratos.columns and "mes" in df_contratos.columns:
            df_mensal = df_contratos.groupby(["CNPJ_RAIZ", "ano", "mes"], as_index=False)["VOLUME_MWM"].sum()
            df_vol_enquadramento = df_mensal.groupby("CNPJ_RAIZ", as_index=False)["VOLUME_MWM"].max()
        else:
            df_vol_enquadramento = df_contratos.groupby("CNPJ_RAIZ", as_index=False)["VOLUME_MWM"].max()

        col_id = "NUMERO_REFERENCIA_CONTRATO"
        col_in = "SUPRIMENTO_INICIO"
        if col_in not in df_contratos.columns:
            col_in = "VIGENCIA_INICIO" if "VIGENCIA_INICIO" in df_contratos.columns else "inicio_suprimento"
            
        col_out = "SUPRIMENTO_TERMINO"
        if col_out not in df_contratos.columns:
            col_out = "VIGENCIA_FIM" if "VIGENCIA_FIM" in df_contratos.columns else "fim_suprimento"

        df_contratos["DT_INICIO"] = pd.to_datetime(df_contratos.get(col_in), errors="coerce")
        df_contratos["DT_FIM"] = pd.to_datetime(df_contratos.get(col_out), errors="coerce")
        
        df_contratos["EH_VIGENTE"] = (
            (df_contratos.get("STATUS", df_contratos.get("id_status", "")).astype(str).str.upper().str.contains("ATIVO|EM SUPRIMENTO|2")) &
            (df_contratos["DT_INICIO"] <= hoje) &
            (df_contratos["DT_FIM"] >= hoje)
        )
        df_contratos["EH_FUTURO"] = (df_contratos["DT_INICIO"] > hoje)

        resumo_contratos = df_contratos.groupby("CNPJ").agg(
            QUANTIDADE_CONTRATOS=(col_id, "nunique") if col_id in df_contratos.columns else ("CNPJ", "count"),
            NUMERACAO_CONTRATOS=(col_id, lambda x: ", ".join(x.dropna().astype(str).unique())) if col_id in df_contratos.columns else ("CNPJ", lambda x: ""),
            STATUS_CONTRATUAL=("EH_VIGENTE", lambda x: "CONTRATO_VIGENTE" if x.any() else ("CONTRATO_FUTURO" if df_contratos.loc[x.index, "EH_FUTURO"].any() else "SEM_CONTRATO")),
            PROXIMO_INICIO=("DT_INICIO", "min"),
            PROXIMO_FIM=("DT_FIM", "max")
        ).reset_index()

        resumo_contratos["ANO_INICIO_CONTRATO"] = resumo_contratos["PROXIMO_INICIO"].dt.year.fillna(0).astype(int)

        resumo_contratos["CNPJ_RAIZ"] = resumo_contratos["CNPJ"].str[:8]
        df_contratos_gold = pd.merge(resumo_contratos, df_vol_enquadramento[["CNPJ_RAIZ", "VOLUME_MWM"]], on="CNPJ_RAIZ", how="left")
        df_gold = pd.merge(df_gold, df_contratos_gold, on="CNPJ", how="left")
    else:
        df_gold["STATUS_CONTRATUAL"] = "SEM_CONTRATO"
        df_gold["VOLUME_MWM"] = 0.0
        df_gold["NUMERACAO_CONTRATOS"] = ""
        df_gold["QUANTIDADE_CONTRATOS"] = 0
        df_gold["ANO_INICIO_CONTRATO"] = 0
        df_gold["PROXIMO_INICIO"] = pd.NaT
        df_gold["PROXIMO_FIM"] = pd.NaT
        
    df_gold["TEM_CONTRATO"] = df_gold["STATUS_CONTRATUAL"].apply(lambda x: "SIM" if x in ["CONTRATO_VIGENTE", "CONTRATO_FUTURO"] else "NÃO")

    if not df_risco.empty:
        erros = validar_coluna_cnpj_canonica(df_risco)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (risco): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_risco, ["CNPJ"], "risco")
        df_risco = df_risco.drop_duplicates(subset=["CNPJ"], keep="last")
        
        if "PE_REAIS" in df_risco.columns:
            cols_risco = [c for c in ["CNPJ", "EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"] if c in df_risco.columns]
            df_gold = pd.merge(df_gold, df_risco[cols_risco], on="CNPJ", how="left")
        else:
            col_mtm = "FINANCEIRO_MTM" if "FINANCEIRO_MTM" in df_risco.columns else ("MTM" if "MTM" in df_risco.columns else None)
            if col_mtm:
                df_gold = pd.merge(df_gold, df_risco[["CNPJ", col_mtm]].rename(columns={col_mtm: "EAD_VALOR"}), on="CNPJ", how="left")
                df_gold["PE_REAIS"] = 0.0

    if not df_reconciliacao.empty:
        erros = validar_coluna_cnpj_canonica(df_reconciliacao)
        if erros:
            raise ValueError("Dataset Silver fora do contrato (reconciliacao): " + "; ".join(erros))
        checar_contrato_obrigatorio(df_reconciliacao, ["CNPJ"], "reconciliacao")
        df_reconciliacao = df_reconciliacao.drop_duplicates(subset=["CNPJ"], keep="last")
        
        cols_recon = [c for c in ["CNPJ", "STATUS_CONCILIACAO", "MTM_POSITIVO_TOTAL"] if c in df_reconciliacao.columns]
        df_gold = pd.merge(df_gold, df_reconciliacao[cols_recon], on="CNPJ", how="left")
        
        if "MTM_POSITIVO_TOTAL" in df_gold.columns:
            df_gold["POSICAO_MTM_MW"] = pd.to_numeric(df_gold["MTM_POSITIVO_TOTAL"], errors="coerce").fillna(0.0)
            df_gold = df_gold.drop(columns=["MTM_POSITIVO_TOTAL"])
        else:
            df_gold["POSICAO_MTM_MW"] = 0.0
            
        if "STATUS_CONCILIACAO" not in df_gold.columns:
            df_gold["STATUS_CONCILIACAO"] = "DIVERGENTE"
    else:
        df_gold["POSICAO_MTM_MW"] = 0.0
        df_gold["STATUS_CONCILIACAO"] = "DIVERGENTE"

    colunas_esperadas = [
        "VOLUME_MWM", "EAD_VALOR", "PE_REAIS", "PATRIMONIO_LIQUIDO", "QUANTIDADE_CONTRATOS", 
        "STATUS_CONTRATUAL", "SITUACAO_ANALISE", "SITUACAO_DF", "SITUACAO_CADASTRAL"
    ]
    for col in colunas_esperadas:
        if col not in df_gold.columns:
            logging.warning("Coluna esperada '%s' ausente no DataFrame Gold. Preenchida com fallback pd.NA.", col)
            df_gold[col] = pd.NA

    df_gold["STATUS_CONTRATUAL"] = df_gold["STATUS_CONTRATUAL"].fillna("SEM_CONTRATO")
    df_gold["SITUACAO_CADASTRAL"] = df_gold["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADA")

    df_gold["SITUACAO_DF"] = df_gold.apply(resolver_situacao_df, axis=1)
    df_gold["SITUACAO_ANALISE"] = df_gold.apply(resolver_situacao_analise, axis=1)
    df_gold["METODOLOGIA_EXIGIDA"] = df_gold.apply(classificar_exigencia, axis=1)
    df_gold["STATUS_METODOLOGIA"] = df_gold.apply(status_metodologia, axis=1)

    df_gold["CONTRAPARTE_ID"] = df_gold["CNPJ"].apply(lambda x: f"CPT_{x}")
    df_gold["ANALISE_ID"] = df_gold.apply(
        lambda row: f"ANA_{row['CNPJ']}_{str(row.get('DATA_ANALISE', '')).replace('-','')}" if row.get("TEM_ANALISE") == "SIM" and pd.notna(row.get("DATA_ANALISE")) else pd.NA, axis=1
    )
    df_gold["RUN_ID"] = run_id
    df_gold["REVISAO_LIMITE"] = (df_gold["STATUS_METODOLOGIA"] != "COMPLIANT")
    df_gold["DATA_GERACAO"] = hoje
    df_gold["VERSAO_LAYOUT_LIMITE"] = "v1.2"
    df_gold["FONTE_VOLUME"] = "DENODO_CONTRATOS"
    df_gold["DATA_REFERENCIA_VOLUME"] = hoje

    if "MOTIVO_AUSENCIA_DF" not in df_gold.columns:
        df_gold["MOTIVO_AUSENCIA_DF"] = df_gold["SITUACAO_DF"].apply(lambda x: "NAO_ENVIADA_PELA_CONTRAPARTE" if x == "NAO_RECEBIDA" else pd.NA)

    if not df_eventos.empty and "CNPJ" in df_eventos.columns:
        from common.identificadores import normalizar_cnpj
        
        df_ev_vigentes = df_eventos[df_eventos["STATUS_EVENTO"] == "VIGENTE"].copy() if "STATUS_EVENTO" in df_eventos.columns else df_eventos.copy()
        df_ev_vigentes["CNPJ"] = df_ev_vigentes["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
        df_ev_vigentes = df_ev_vigentes.dropna(subset=["CNPJ"])
        
        cnpjs_manuais = set(df_ev_vigentes["CNPJ"].unique())
        df_gold["INDICADOR_DADO_MANUAL"] = df_gold["CNPJ"].apply(lambda x: "SIM" if x in cnpjs_manuais else "NÃO")
        
        if not df_ev_vigentes.empty and "CAMPO_AFETADO" in df_ev_vigentes.columns and "VALOR_NOVO" in df_ev_vigentes.columns:
            df_ev_vigentes["CAMPO_AFETADO"] = df_ev_vigentes["CAMPO_AFETADO"].replace({
                "NOTA_CREDITO": "RATING_FINAL",
                "RATING": "RATING_FINAL",
                "NOTA_BOARD": "RATING_FINAL",
                "NOTA_BUREAU": "RATING_FINAL",
                "PD": "PD_FINAL",
                "PROBABILIDADE_DEFAULT": "PD_FINAL"
            })
            
            df_ev_dedup = df_ev_vigentes.drop_duplicates(subset=["CNPJ", "CAMPO_AFETADO"], keep="last")
            df_ev_pivot = df_ev_dedup.pivot(index="CNPJ", columns="CAMPO_AFETADO", values="VALOR_NOVO").reset_index()
            
            for col in df_ev_pivot.columns:
                if col != "CNPJ" and col in df_gold.columns:
                    df_gold = pd.merge(df_gold, df_ev_pivot[["CNPJ", col]], on="CNPJ", how="left", suffixes=("", "_MANUAL"))
                    
                    col_manual = f"{col}_MANUAL"
                    if col_manual in df_gold.columns:
                        mask_manual = df_gold[col_manual].notna() & (df_gold[col_manual].astype(str).str.strip().str.upper() != "NONE")
                        mask_none = df_gold[col_manual].astype(str).str.strip().str.upper() == "NONE"
                        
                        if mask_manual.any():
                            if pd.api.types.is_numeric_dtype(df_gold[col]):
                                valores_convertidos = pd.to_numeric(df_gold.loc[mask_manual, col_manual], errors="coerce")
                                df_gold.loc[mask_manual, col] = valores_convertidos.astype(df_gold[col].dtype)
                            else:
                                df_gold.loc[mask_manual, col] = df_gold.loc[mask_manual, col_manual]
                        if mask_none.any():
                            df_gold.loc[mask_none, col] = pd.NA
                            
                        df_gold = df_gold.drop(columns=[col_manual])
    else:
        df_gold["INDICADOR_DADO_MANUAL"] = "NÃO"

    if "ORIGEM_REGISTRO" in df_gold.columns:
        df_gold["ORIGEM_ANALISE"] = df_gold["ORIGEM_REGISTRO"].fillna("FICHA")
    else:
        df_gold["ORIGEM_ANALISE"] = "FICHA"

    if "VALIDADE_EXCECAO" not in df_gold.columns:
        df_gold["VALIDADE_EXCECAO"] = pd.NaT

    if "PATRIMONIO_LIQUIDO" in df_gold.columns:
        df_gold["PATRIMONIO_LIQUIDO_AJUSTADO"] = df_gold["PATRIMONIO_LIQUIDO"]
    else:
        df_gold["PATRIMONIO_LIQUIDO_AJUSTADO"] = pd.NA

    if not df_bureau.empty and "CNPJ" in df_bureau.columns:
        df_b_unique = df_bureau.drop_duplicates("CNPJ", keep="last").copy()
        
        colunas_bureau = ["CNPJ"]
        for col in ["RATING_BUREAU", "PD_BUREAU", "SCORE_BUREAU", "RESTRITIVOS", "DATA_CONSULTA"]:
            if col in df_b_unique.columns:
                colunas_bureau.append(col)
                
        df_gold = pd.merge(df_gold, df_b_unique[colunas_bureau], on="CNPJ", how="left")
        
        if "METODOLOGIA_EXIGIDA" in df_gold.columns:
            mask_bureau = df_gold["METODOLOGIA_EXIGIDA"] == "BUREAU"
            
            if "RATING_BUREAU" in df_gold.columns:
                if "RATING_FINAL" not in df_gold.columns:
                    df_gold["RATING_FINAL"] = pd.NA
                df_gold.loc[mask_bureau, "RATING_FINAL"] = df_gold.loc[mask_bureau, "RATING_BUREAU"]
                    
            if "PD_BUREAU" in df_gold.columns:
                df_gold["PD_BUREAU"] = pd.to_numeric(df_gold["PD_BUREAU"], errors="coerce")
                if "PD_FINAL" not in df_gold.columns:
                    df_gold["PD_FINAL"] = pd.NA
                df_gold["PD_FINAL"] = pd.to_numeric(df_gold["PD_FINAL"], errors="coerce")
                df_gold.loc[mask_bureau, "PD_FINAL"] = df_gold.loc[mask_bureau, "PD_BUREAU"]

        if "SCORE_BUREAU" not in df_gold.columns: df_gold["SCORE_BUREAU"] = pd.NA
        if "RESTRITIVOS" not in df_gold.columns: df_gold["RESTRITIVOS"] = pd.NA
    else:
        df_gold["SCORE_BUREAU"] = pd.NA
        df_gold["RESTRITIVOS"] = pd.NA
        
    df_gold["DATA_DA_ANALISE"] = pd.NA
    if "DATA_BALANCO_USADO" in df_gold.columns:
        df_gold["DATA_DA_ANALISE"] = df_gold["DATA_BALANCO_USADO"]
        
    if "METODOLOGIA_EXIGIDA" in df_gold.columns and "DATA_CONSULTA" in df_gold.columns:
        mask_bureau = df_gold["METODOLOGIA_EXIGIDA"] == "BUREAU"
        df_gold.loc[mask_bureau, "DATA_DA_ANALISE"] = df_gold.loc[mask_bureau, "DATA_CONSULTA"]

    return df_gold

def exportar_visao_consolidada_gold(context: Any) -> dict[str, Any]:
    run_id = f"GOLD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold", Path("LOGS/gold") / f"{run_id}__service_gold.log")
    logger.info("Construindo Visão Consolidada Gold (Master Join)...")
    hoje = pd.Timestamp("today").normalize()

    dfs = carregar_entradas_gold(context, logger)
    df_gold = construir_visao_consolidada(dfs, run_id, hoje)
    
    salvar_visao_gold(context, df_gold, hoje, run_id, logger)

    sit_analise = df_gold["SITUACAO_ANALISE"].fillna("").astype(str)
    met_exigida  = df_gold["METODOLOGIA_EXIGIDA"].fillna("").astype(str)
    stat_ctr     = df_gold["STATUS_CONTRATUAL"].fillna("").astype(str)

    mask_descoberto     = (stat_ctr == "CONTRATO_VIGENTE") & (sit_analise != "VIGENTE")
    mask_irregular      = (stat_ctr == "CONTRATO_VIGENTE") & (met_exigida == "DF_DETALHADA") & (sit_analise != "VIGENTE")
    mask_pendente_bureau = (stat_ctr == "CONTRATO_VIGENTE") & (met_exigida == "BUREAU")      & (sit_analise != "VIGENTE")

    return {
        "status": "SUCESSO",
        "total_contrapartes": len(df_gold),
        "contrato_vigente": int((df_gold["STATUS_CONTRATUAL"] == "CONTRATO_VIGENTE").sum()),
        "contrato_futuro": int((df_gold["STATUS_CONTRATUAL"] == "CONTRATO_FUTURO").sum()),
        "analise_vigente": int((df_gold["SITUACAO_ANALISE"].fillna("").astype(str) == "VIGENTE").sum()),
        "analise_vencida": int((df_gold["SITUACAO_ANALISE"].fillna("").astype(str) == "VENCIDA").sum()),
        "contrato_vig_sem_analise_vig": int(mask_descoberto.sum()),
        "contrato_irregular_sem_df": int(mask_irregular.sum()),
        "contrato_pendente_bureau": int(mask_pendente_bureau.sum()),
        "ficha_sem_contrato": int(((df_gold["TEM_ANALISE"] == "SIM") & (df_gold["STATUS_CONTRATUAL"] == "SEM_CONTRATO")).sum()),
        "contrato_sem_ficha": int(((df_gold["STATUS_CONTRATUAL"].isin(["CONTRATO_VIGENTE", "CONTRATO_FUTURO"])) & (df_gold["TEM_ANALISE"] == "NÃO")).sum()),
        "dados_incompletos": int((df_gold["SITUACAO_CADASTRAL"].isin(["NAO_INFORMADA", "PENDENTE"])).sum()),
        "ead_descoberto": float(df_gold.loc[mask_irregular, "EAD_VALOR"].sum(skipna=True)) if "EAD_VALOR" in df_gold.columns else 0.0,
    }
```


---

## `src/silver/__init__.py`

- Linhas: 1
- SHA-256: `156ba1160b561672f49fccf03aeff8141ef1478dbcff7690ffbe35416138e6fb`
- Classes: -
- Funções: -

```python
"""Camada silver do sistema BDC."""
```


---

## `src/silver/documentos_classificados.py`

- Linhas: 21
- SHA-256: `ab95651cdadd95007d7e85dfe1c7167c1c6087ecab0fa6b20d35d761ff5edf6c`
- Classes: -
- Funções: criar_documento_classificado

```python
from __future__ import annotations

def criar_documento_classificado(
    documento_id: str,
    run_id: str,
    ambiente: str,
    arquivo_nome: str,
    versao_ficha: str,
    TIPO_FICHA: str,
    hash_arquivo: str,
) -> dict[str, str]:
    """Monta o registro silver de documento classificado."""
    return {
        "documento_id": documento_id,
        "run_id": run_id,
        "ambiente": ambiente,
        "arquivo_nome": arquivo_nome,
        "versao_ficha": versao_ficha,
        "TIPO_FICHA": TIPO_FICHA,
        "hash_arquivo": hash_arquivo,
    }
```


---

## `src/silver/formatador_silver.py`

- Linhas: 98
- SHA-256: `d9ec3686987b5f0cb9cc67a843e4f611a5a3ecc7f7fe3141c8b0f7442fc39778`
- Classes: -
- Funções: normalizar_registro

```python
"""Normalização técnica das fichas."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from pathlib import Path

from app.context import AppContext
from common.datas import normalizar_data, normalizar_data_demonstracao_financeira
from common.numeros import to_percentual_br, to_float_br
from common.texto import normalizar_texto
from common.identificadores import normalizar_cnpj



def normalizar_registro(
    record: dict[str, Any],
    catalog: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Normaliza o registro bruto extraído da ficha."""
    try:
        fields = catalog.get("fields", {})
        if not fields:
            raise ValueError("O catálogo fornecido não contém a chave 'fields' ou está vazio. Sem configuração de tipos, a normalização é impossível.")

        date_fields = [k for k, v in fields.items() if v.get("type") == "date"]
        float_fields = [k for k, v in fields.items() if v.get("type") == "float"]
        text_fields = [k for k, v in fields.items() if v.get("type") in ("string", "text")]
        cnpj_fields = [k for k, v in fields.items() if v.get("type") == "cnpj"]

        out = dict(record)
        
        for field in cnpj_fields:
            if field in out:
                try:
                    resultado_cnpj = normalizar_cnpj(out.get(field))
                    if resultado_cnpj.valido:
                        out[field] = resultado_cnpj.cnpj
                        if field == "CNPJ":
                            out["CNPJ_RAIZ"] = resultado_cnpj.raiz
                            out["STATUS_CNPJ"] = resultado_cnpj.status.value
                    else:
                        out[field] = None
                        if field == "CNPJ":
                            out["CNPJ_RAIZ"] = None
                            out["STATUS_CNPJ"] = resultado_cnpj.status.value
                except Exception as exc:
                    if logger: logger.exception("Erro CNPJ: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo CNPJ '{field}'.") from exc

        for field in date_fields:
            if field in out:
                try:
                    if field == "DATA_DEMONSTRACAO_FINANCEIRA":
                        val_norm, epoch_orig, was_corrected = normalizar_data_demonstracao_financeira(out.get(field))
                        out[field] = val_norm
                        out["FLAG_DATA_DF_CORRIGIDA"] = was_corrected
                        out["DATA_DF_EPOCH_ORIGINAL"] = epoch_orig
                    else:
                        out[field] = normalizar_data(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Data: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo de data '{field}'.") from exc

        for field in float_fields:
            if field in out:
                try:
                    if field in ("PROBABILIDADE_DEFAULT", "PD", "SCORE_PD"):
                        out[field] = to_percentual_br(out.get(field))
                    else:
                        out[field] = to_float_br(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Float: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo numérico '{field}'.") from exc

        for field in text_fields:
            if field in out and out.get(field) is not None:
                try:
                    out[field] = normalizar_texto(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Texto: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo textual '{field}'.") from exc

        if logger is not None:
            logger.info("Registro normalizado (Entrada: %s, Saída: %s).", len(record), len(out))
        
        return out

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha na normalização: CNPJ=%s EMPRESA=%s",
                record.get("CNPJ"), record.get("EMPRESA")
            )
        raise
```


---

## `src/silver/mapeador_dominio.py`

- Linhas: 91
- SHA-256: `b6147a259b175dae408fb259469a06772274241983d191f7e03961928d12459d`
- Classes: -
- Funções: aplicar_normalizacao_de_dominio

```python
from __future__ import annotations

import json
from typing import Any

from app.context import AppContext
from common.dominio import (
    normalizar_agencia,
    normalizar_auditor,
    normalizar_rating,
)


def aplicar_normalizacao_de_dominio(
    registro: dict[str, Any],
    context: AppContext,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Aplica regras semânticas de domínio (auditor, agência, etc.) sobre o registro."""
    out = dict(registro)

    try:
        dict_path = context.control_file("domain_dictionaries")
        with open(dict_path, encoding="utf-8") as f:
            dicionarios = json.load(f)
    except Exception as exc:
        if logger:
            logger.warning("Não foi possível carregar dicionários de domínio: %s", exc)
        return out

    if "AUDITOR" in out and out["AUDITOR"] is not None:
        try:
            out["AUDITOR"] = normalizar_auditor(
                out["AUDITOR"],
                dicionarios.get("AUDITOR", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar AUDITOR: %s", exc)

    if "AGENCIA" in out and out["AGENCIA"] is not None:
        try:
            out["AGENCIA"] = normalizar_agencia(
                out["AGENCIA"],
                dicionarios.get("AGENCIA", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar AGENCIA: %s", exc)

    if "NOTA_CREDITO" in out and out["NOTA_CREDITO"] is not None:
        try:
            out["NOTA_CREDITO"] = normalizar_rating(
                out["NOTA_CREDITO"],
                dicionarios.get("NOTA_CREDITO", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar NOTA_CREDITO: %s", exc)
                
    if "RATING_COPEL" in out and out["RATING_COPEL"] is not None:
        try:
            out["RATING_COPEL"] = normalizar_rating(
                out["RATING_COPEL"],
                dicionarios.get("RATING_COPEL", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar RATING_COPEL: %s", exc)

    if "NOTA_BOARD" in out and out["NOTA_BOARD"] is not None:
        try:
            out["NOTA_BOARD"] = normalizar_rating(
                out["NOTA_BOARD"],
                dicionarios.get("NOTA_BOARD", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar NOTA_BOARD: %s", exc)

    if "NOTA_BUREAU" in out and out["NOTA_BUREAU"] is not None:
        try:
            out["NOTA_BUREAU"] = normalizar_rating(
                out["NOTA_BUREAU"],
                dicionarios.get("NOTA_BUREAU", {}),
            )
        except Exception as exc:
            if logger:
                logger.warning("Falha ao normalizar NOTA_BUREAU: %s", exc)

    return out
```


---

## `src/staging/__init__.py`

- Linhas: 1
- SHA-256: `34854bdbb0e8e62d0877ff38c278a527e5ac5689874b5603d03524371a15f570`
- Classes: -
- Funções: -

```python
"""Camada de staging do sistema BDC."""
```


---

## `src/staging/descoberta.py`

- Linhas: 47
- SHA-256: `d81d5a9242d289958b6988696bed36d490e4656ef086ecba651c708f8758b860`
- Classes: ArquivoDescoberto
- Funções: descobrir_arquivos_excel, detectar_arquivos_excel_pendentes

```python
"""Descoberta de arquivos pendentes para processamento."""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
import hashlib

@dataclass(frozen=True)
class ArquivoDescoberto:
    caminho_original: Path
    nome_arquivo: str
    extensao: str
    tamanho_bytes: int
    hash_sha256: str | None = None

def descobrir_arquivos_excel(input_dir: str | Path, calcular_hash: bool = False) -> list[ArquivoDescoberto]:
    """Lista arquivos Excel encapsulando os metadados de infraestrutura para evitar I/O repetitivo."""
    base_dir = Path(input_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    arquivos = []
    for file_path in base_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in {".xlsx", ".xlsm", ".xls"}:
            
            file_hash = None
            if calcular_hash:
                hasher = hashlib.sha256()
                with file_path.open("rb") as f:
                    for chunk in iter(lambda: f.read(1024 * 1024), b""):
                        hasher.update(chunk)
                file_hash = hasher.hexdigest()
                
            arquivos.append(ArquivoDescoberto(
                caminho_original=file_path,
                nome_arquivo=file_path.name,
                extensao=file_path.suffix.lower(),
                tamanho_bytes=file_path.stat().st_size,
                hash_sha256=file_hash
            ))
            
    return sorted(arquivos, key=lambda x: x.nome_arquivo)

def detectar_arquivos_excel_pendentes(input_dir: str | Path) -> list[Path]:
    """Adaptador legado: Lista arquivos Excel pendentes retornando lista de Paths."""
    descobertos = descobrir_arquivos_excel(input_dir, calcular_hash=False)
    return [arq.caminho_original for arq in descobertos]
```


---

## `src/staging/staging_arquivo.py`

- Linhas: 19
- SHA-256: `ff5e2a70d416e7f7abe70b473d764875c63709c5ce0436b9cb745210d82ffda0`
- Classes: -
- Funções: copiar_para_staging

```python
from __future__ import annotations

import shutil
from pathlib import Path


def copiar_para_staging(
    source_file: str | Path,
    staging_dir: str | Path,
    target_name: str,
) -> Path:
    """Copia um arquivo para o staging com nome técnico."""
    source_path = Path(source_file)
    target_dir = Path(staging_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / target_name
    shutil.copy2(source_path, target_path)
    return target_path
```


---

## `src/storage/__init__.py`

- Linhas: 1
- SHA-256: `39ab5aea815e70a328edec6d01393b78a687554950e5a2a04d1ba6ab1f1ca850`
- Classes: -
- Funções: -

```python
"""Camada de persistência física do sistema BDC."""
```


---

## `src/storage/armazenamento_manifest.py`

- Linhas: 26
- SHA-256: `7903c1418dd5327885c9f4361a306217038d71e127cdcd532a34f79e1790c827`
- Classes: -
- Funções: anexar_registro_de_manifesto, historico_de_ingestao_de_carga

```python
import json
from pathlib import Path
from typing import Any

def anexar_registro_de_manifesto(file_path: str, record: dict[str, Any]) -> None:
    """Anexa um novo manifesto em formato JSON Lines ao histórico."""
    target = Path(file_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    
    with target.open("a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

def historico_de_ingestao_de_carga(file_path: Path) -> list[dict[str, Any]]:
    """Lê o histórico completo de ingestão em formato JSONL."""
    history = []
    if not file_path.exists():
        return history
    
    with file_path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if line.strip():
                try:
                    history.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return history
```


---

## `src/storage/bronze_arquivo.py`

- Linhas: 18
- SHA-256: `56460ec5cc7fee217b72f5b7c561d9de659c17592dbcce3f9d044590ad740b05`
- Classes: -
- Funções: publicar_arquivo_bruto

```python
from __future__ import annotations

import shutil
from pathlib import Path


def publicar_arquivo_bruto(
    source_file: str | Path,
    bronze_root_dir: str | Path,
) -> Path:
    """Publica um arquivo na camada bronze."""
    source_path = Path(source_file)
    target_dir = Path(bronze_root_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / source_path.name
    shutil.copy2(source_path, target_path)
    return target_path
```


---

## `src/storage/escrever_dados.py`

- Linhas: 186
- SHA-256: `6fb92b1ecbbe800def74870db084fa1c6ea562d361ff0376d9ab3ccd5f03bf34`
- Classes: -
- Funções: _normalize_filename, escrever_conjunto_de_dados_silver, mesclar_conjunto_de_dados_prata_por_chave_de_negocio

```python
import json
import warnings
from pathlib import Path
import pandas as pd
from typing import Any, Dict, List, Union

_KNOWN_EXTENSIONS = (".parquet", ".csv")

def _normalize_filename(filename: str) -> str:
    """Remove extensões conhecidas (.csv, .parquet) do filename recebido."""
    stem = filename.strip()
    for ext in _KNOWN_EXTENSIONS:
        if stem.lower().endswith(ext):
            stem = stem[: -len(ext)]
            break
    return stem

def escrever_conjunto_de_dados_silver(
    records: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    filename: str,
    sep: str = ";",
    decimal: str = ",",
    encoding: str = "utf-8-sig",
) -> tuple[Path, Path]:
    """Persiste a lista de registros normalizados em CSV e Parquet."""
    filename = _normalize_filename(filename)

    if not records:
        csv_path = Path(output_dir) / f"{filename}.csv"
        parquet_path = Path(output_dir) / f"{filename}.parquet"
        return csv_path, parquet_path

    df = pd.DataFrame(records)

    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False, default=str) if isinstance(x, (list, dict)) else x)
            
        elif pd.api.types.is_datetime64_any_dtype(df[col]) or "data" in col.lower() or "date" in col.lower() or col.lower().startswith("dt_") or col.startswith("_DT_") or "vencimento" in col.lower():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
            
        elif not (pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col])):
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
        elif pd.api.types.is_object_dtype(df[col]):
            df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else None)

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    csv_path = target_dir / f"{filename}.csv"
    parquet_path = target_dir / f"{filename}.parquet"

    df.to_csv(
        csv_path, 
        index=False, 
        sep=sep, 
        decimal=decimal, 
        encoding=encoding, 
        date_format="%d/%m/%Y"
    )
    df.to_parquet(parquet_path, index=False, engine="pyarrow", compression="snappy")

    return csv_path, parquet_path

def mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
    records: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    filename: str,
    business_keys: List[str],
    sep: str = ";",
    decimal: str = ",",
    encoding: str = "utf-8-sig",
) -> tuple[Path, Path]:
    """Realiza o merge incremental preservando histórico completo (SCD Tipo 2)."""
    filename = _normalize_filename(filename)
    target_dir = Path(output_dir)
    parquet_path = target_dir / f"{filename}.parquet"

    if not records:
        return parquet_path, parquet_path

    df_new = pd.DataFrame(records)
    df_new["_DT_CARGA"] = pd.Timestamp.now()

    for col in df_new.columns:
        if df_new[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df_new[col] = df_new[col].apply(lambda x: json.dumps(x, ensure_ascii=False, default=str) if isinstance(x, (list, dict)) else x)
        
        if "data" in col.lower() or "date" in col.lower() or col.lower().startswith("dt_"):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                df_new[col] = pd.to_datetime(df_new[col], errors="coerce", dayfirst=True)

    if parquet_path.exists():
        df_existing = pd.read_parquet(parquet_path)

        if "_VERSAO_REGISTRO" not in df_existing.columns:
            df_existing["_VERSAO_REGISTRO"] = 1
        
        if "_DT_CARGA" not in df_existing.columns:
            df_existing["_DT_CARGA"] = pd.NaT
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                df_existing["_DT_CARGA"] = pd.to_datetime(df_existing["_DT_CARGA"], errors="coerce", dayfirst=True)
            
        if "_STATUS_REGISTRO" not in df_existing.columns:
            df_existing["_STATUS_REGISTRO"] = "VIGENTE"

        for b_key in business_keys:
            if b_key in df_existing.columns and b_key in df_new.columns:
                if pd.api.types.is_datetime64_any_dtype(df_existing[b_key]) and not pd.api.types.is_datetime64_any_dtype(df_new[b_key]):
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        df_new[b_key] = pd.to_datetime(df_new[b_key], errors="coerce", dayfirst=True)
                elif not pd.api.types.is_datetime64_any_dtype(df_existing[b_key]) and pd.api.types.is_datetime64_any_dtype(df_new[b_key]):
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        df_existing[b_key] = pd.to_datetime(df_existing[b_key], errors="coerce", dayfirst=True)
                else:
                    df_new[b_key] = df_new[b_key].astype(df_existing[b_key].dtype)

        df_existing_keys = df_existing[business_keys].drop_duplicates()
        df_new_keys = df_new[business_keys].drop_duplicates()
        
        keys_to_replace = pd.merge(df_existing_keys, df_new_keys, on=business_keys, how='inner')
        if not keys_to_replace.empty:
            cond_atualizacao = df_existing.set_index(business_keys).index.isin(keys_to_replace.set_index(business_keys).index)
            df_existing.loc[cond_atualizacao, "_STATUS_REGISTRO"] = "SUBSTITUIDO"

        max_versoes = (
            df_existing.groupby(business_keys, dropna=False)["_VERSAO_REGISTRO"]
            .max()
            .reset_index()
            .rename(columns={"_VERSAO_REGISTRO": "_MAX_VERSAO"})
        )

        df_new = pd.merge(df_new, max_versoes, on=business_keys, how="left")
        df_new["_MAX_VERSAO"] = df_new["_MAX_VERSAO"].fillna(0).astype(int)
    else:
        df_existing = pd.DataFrame()
        df_new["_MAX_VERSAO"] = 0

    if "dt_processamento" in df_new.columns:
        df_new = df_new.sort_values(by=business_keys + ["dt_processamento"])

    df_new["rank_interno"] = df_new.groupby(business_keys).cumcount() + 1
    df_new["_VERSAO_REGISTRO"] = df_new["_MAX_VERSAO"] + df_new["rank_interno"]
    df_new = df_new.drop(columns=["_MAX_VERSAO", "rank_interno"])

    df_new["_STATUS_REGISTRO"] = "SUBSTITUIDO"
    idx_vigentes = df_new.groupby(business_keys)["_VERSAO_REGISTRO"].idxmax()
    df_new.loc[idx_vigentes, "_STATUS_REGISTRO"] = "VIGENTE"

    if not df_existing.empty:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
        
    df_new["_STATUS_REGISTRO"] = "SUBSTITUIDO"
    idx_vigentes = df_new.groupby(business_keys)["_VERSAO_REGISTRO"].idxmax()
    df_new.loc[idx_vigentes, "_STATUS_REGISTRO"] = "VIGENTE"

    if not df_existing.empty:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    qtd_inseridos = len(df_new)
    qtd_atualizados = len(keys_to_replace) if 'keys_to_replace' in locals() and not keys_to_replace.empty else 0
    
    import logging
    temp_logger = logging.getLogger("bdc.comercializadoras")

    return escrever_conjunto_de_dados_silver(
        records=df_combined.to_dict(orient="records"),
        output_dir=output_dir,
        filename=filename,
        sep=sep,
        decimal=decimal,
        encoding=encoding
    )
```


---

## `src/storage/estado_armazenamento.py`

- Linhas: 72
- SHA-256: `958582422f8d2ee2991a2354696370f48233e4048f3f8549523d98dc43666b08`
- Classes: DocumentManifest
- Funções: __post_init__, to_dict

```python
"""Estruturas de estado e manifesto do processamento."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from domain.enums import (
    LoadMode,
    StatusClassificacao,
    StatusExtracao,
    TipoFicha,
)

@dataclass
class DocumentManifest:
    """Representa o manifesto técnico de uma ficha processada."""

    documento_id: str
    run_id: str
    ambiente: str
    tipo_ficha: TipoFicha | str
    arquivo_nome: str | None = None
    caminho_origem: str | None = None
    caminho_staging: str | None = None
    caminho_bronze: str | None = None
    hash_arquivo: str | None = None
    versao_ficha: str | None = None
    cnpj_extraido: str | None = None
    data_demonstracao_financeira: str | None = None
    data_calculo: str | None = None
    status_classificacao: StatusClassificacao | str | None = None
    status_extracao: StatusExtracao | str | None = None
    load_mode: LoadMode | str | None = None
    reprocessed: bool | None = None
    previous_record_found: bool | None = None
    erros: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Garante que os atributos controlados pertençam aos domínios nativos."""
        if isinstance(self.tipo_ficha, str):
            try:
                self.tipo_ficha = TipoFicha(self.tipo_ficha.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para tipo_ficha: '{self.tipo_ficha}'. Domínios válidos: {[e.value for e in TipoFicha]}")

        if isinstance(self.status_classificacao, str):
            try:
                self.status_classificacao = StatusClassificacao(self.status_classificacao.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para status_classificacao: '{self.status_classificacao}'. Domínios válidos: {[e.value for e in StatusClassificacao]}")

        if isinstance(self.status_extracao, str):
            try:
                self.status_extracao = StatusExtracao(self.status_extracao.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para status_extracao: '{self.status_extracao}'. Domínios válidos: {[e.value for e in StatusExtracao]}")
                
        if isinstance(self.load_mode, str):
            try:
                self.load_mode = LoadMode(self.load_mode.lower())
            except ValueError:
                raise ValueError(f"Valor rejeitado para load_mode: '{self.load_mode}'. Domínios válidos: {[e.value for e in LoadMode]}")

    def to_dict(self) -> dict[str, Any]:
        """Serializa o manifesto convertendo os Enums para seus valores primitivos (strings)."""
        manifest_dict = asdict(self)
        for key, value in manifest_dict.items():
            if hasattr(value, "value"):
                manifest_dict[key] = value.value
        return manifest_dict
```


---

## `src/storage/operacao_arquivo.py`

- Linhas: 32
- SHA-256: `b3e837da233860aa1d3049268a1d8f39e23a1adb1aff8b13a73b920e4e3f5a6a`
- Classes: -
- Funções: mover_arquivo_com_tentativa_adicional

```python
from __future__ import annotations

import shutil
import time
from pathlib import Path


def mover_arquivo_com_tentativa_adicional(
    source: str | Path,
    target: str | Path,
    attempts: int = 5,
    wait_seconds: float = 0.5,
) -> Path:
    """Move um arquivo com novas tentativas em caso de bloqueio."""
    source_path = Path(source)
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None

    for _ in range(attempts):
        try:
            shutil.move(str(source_path), str(target_path))
            return target_path
        except PermissionError as exc:
            last_error = exc
            time.sleep(wait_seconds)

    if last_error is not None:
        raise last_error

    return target_path
```


# GRUPO: main.py


---

## `main.py`

- Linhas: 219
- SHA-256: `7d979b101a6b23e5e874cfb1e5213caa2ebe1cbd47fc362497858f1e0cc55c24`
- Classes: PipelineStep
- Funções: rodar_interface_streamlit, preparar_e_rodar_risco, preparar_dim_contraparte, preparar_fato_analise, main

```python
import argparse
import sys
import pandas as pd
import subprocess

from pathlib import Path
from typing import Callable, NamedTuple, Any
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.bootstrap import carregar_contexto 
from control.logger import obter_logger

from cli import rodar_fichas_comercializadoras
from cli import rodar_fichas_consumidores

from domain.auditoria.servico_auditoria import registrar_inicio_pipeline, registrar_fim_pipeline
from domain.contratos.servico_contratos_denodo import processar_contratos_denodo
from domain.contrapartes.servico_enquadramento import calcular_enquadramento_consumidor
from domain.mtm.servico_mtm import inserir_dados_mtm
from domain.salesforce.servico_salesforce import inserir_dados_salesforce
from domain.cadastro.servico_receita import inserir_dados_receita
from domain.garantias.servico_garantia import inserir_dados_garantias
from domain.carga_manual.servico_carga_manual import inserir_dados_carga_manual
from domain.credito.servico_override import processar_solicitacao_override
from domain.cadastro.servico_bureau import inserir_dados_bureau
from gold.servico_gold import exportar_visao_consolidada_gold
from relational.facts.fato_exposicao_risco import construir_fato_exposicao_risco
from relational.facts.fato_analise_credito import construir_fato_analise_credito
from relational.facts.fato_reconciliacao_fichas_salesforce import executar_reconciliacao_fichas_salesforce
from relational.dimensions.dim_contraparte import criar_dim_contraparte
from relational.facts.fato_reconciliacao_contrato_mtm import executar_reconciliacao_denodo_mtm
from relational.facts.fato_alertas import gerar_fato_alertas_credito
from relational.facts.fato_alertas_manuais import gerar_fato_alertas_manuais
from relational.facts.fato_garantia import gerar_fato_garantia


def rodar_interface_streamlit():
    app_path = PROJECT_ROOT / "src" / "ui" / "app.py"
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", str(app_path)
    ])

def preparar_e_rodar_risco(context):
    mtm_path = context.path("silver") / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
    df_mtm = pd.read_parquet(mtm_path) if mtm_path.exists() else pd.DataFrame()
    if df_mtm.empty: return
        
    fato_path = context.path("relational_facts") / "fato_analise_credito.parquet"
    df_fichas = pd.read_parquet(fato_path) if fato_path.exists() else pd.DataFrame()

    df_mtm["CNPJ"] = df_mtm["CNPJ"].astype(str).str.zfill(14)
    df_exposicoes = df_mtm.copy()
    
    if not df_fichas.empty and "CNPJ" in df_fichas.columns:
        df_fichas["CNPJ"] = df_fichas["CNPJ"].astype(str).str.zfill(14)
        if "DATA_ANALISE" in df_fichas.columns:
            df_fichas = df_fichas.sort_values("DATA_ANALISE").drop_duplicates("CNPJ", keep="last")
            
        cols_ficha = ["CNPJ"]
        if "PD_PERCENTUAL" in df_fichas.columns: cols_ficha.append("PD_PERCENTUAL")
        if "SEGMENTO_METODOLOGICO_FICHA" in df_fichas.columns: cols_ficha.append("SEGMENTO_METODOLOGICO_FICHA")
        
        df_exposicoes = pd.merge(df_exposicoes, df_fichas[cols_ficha], on="CNPJ", how="left")
        
        if "PD_PERCENTUAL" in df_exposicoes.columns:
            df_exposicoes["PD_FINAL"] = df_exposicoes["PD_PERCENTUAL"]
        if "SEGMENTO_METODOLOGICO_FICHA" in df_exposicoes.columns:
            df_exposicoes["SEGMENTO_METODOLOGICO"] = df_exposicoes["SEGMENTO_METODOLOGICO_FICHA"]
            
    if "PD_FINAL" not in df_exposicoes.columns: df_exposicoes["PD_FINAL"] = None
    if "SEGMENTO_METODOLOGICO" not in df_exposicoes.columns: df_exposicoes["SEGMENTO_METODOLOGICO"] = "NAO_ENQUADRADO"
    
    return construir_fato_exposicao_risco(context, df_exposicoes=df_exposicoes)

def preparar_dim_contraparte(context):
    receita_path = context.path("silver") / "receita_silver" / "receita_cadastral_silver.parquet"
    enquadra_path = context.path("relational_configs") / f"enquadramento_consumidores_{datetime.now().strftime('%Y%m')}.csv"
    salesforce_path = context.path("silver") / "salesforce_silver" / "account" / "salesforce_account.parquet"
    
    df_receita = pd.read_parquet(receita_path) if receita_path.exists() else pd.DataFrame()
    df_seg = pd.read_csv(enquadra_path) if enquadra_path.exists() else pd.DataFrame()
    df_sf_account = pd.read_parquet(salesforce_path) if salesforce_path.exists() else pd.DataFrame()
    
    df_fichas = pd.DataFrame()
    for segmento_dir in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        seg_path = context.path("silver") / segmento_dir
        if seg_path.exists():
            parquets = list(seg_path.glob("*.parquet"))
            if parquets:
                df_seg_fichas = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg_fichas], ignore_index=True)

    from relational.dimensions.dim_contraparte import criar_dim_contraparte
    return criar_dim_contraparte(
        context, 
        df_silver_receita=df_receita, 
        df_silver_segmentacao=df_seg,
        df_silver_salesforce_account=df_sf_account,
        df_silver_fichas=df_fichas
    )
    
def preparar_fato_analise(context):
    df_fichas = pd.DataFrame()
    for segmento_dir in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        seg_path = context.path("silver") / segmento_dir
        if seg_path.exists():
            parquets = list(seg_path.glob("*.parquet"))
            if parquets:
                df_seg = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg], ignore_index=True)
                
    dim_path = context.path("relational_dimensions") / "dim_contraparte.parquet"
    if not dim_path.exists():
        dim_path = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"
    df_dim = pd.read_parquet(dim_path) if dim_path.exists() else pd.DataFrame()
    return construir_fato_analise_credito(context, df_silver_analises=df_fichas, df_dim_contraparte=df_dim)

class PipelineStep(NamedTuple):
    name: str
    func: Callable[[Any], Any]

PIPELINE_STEPS = [
    # BLOCO 1: INGESTaO CORE E OVERRIDES (ATIVO)
    PipelineStep(name="Fichas Comercializadoras", func=lambda ctx: rodar_fichas_comercializadoras.main()),
    PipelineStep(name="Fichas Consumidores", func=lambda ctx: rodar_fichas_consumidores.main()),
    
    # BLOCO 2: APIS EXTERNAS E CONECTORES
    PipelineStep(name="Ingestao de Contratos (Denodo)", func=processar_contratos_denodo),
    PipelineStep(name="Enquadramento de Consumidores", func=lambda ctx: calcular_enquadramento_consumidor(datetime.now().strftime("%Y%m"), ctx)),
    PipelineStep(name="Ingestao de MtM", func=inserir_dados_mtm),
    PipelineStep(name="Ingestao do Salesforce", func=inserir_dados_salesforce),
    PipelineStep(name="Ingestao da Receita Federal", func=inserir_dados_receita), 
    PipelineStep(name="Ingestao de Bureau (RISK3)", func=inserir_dados_bureau),
    PipelineStep(name="Ingestao de Garantias", func=inserir_dados_garantias),
    PipelineStep(name="Solicitacoes de Override", func=processar_solicitacao_override),
    PipelineStep(name="Carga Manual (Eventos e Overrides)", func=lambda ctx: inserir_dados_carga_manual(ctx)),

    # BLOCO 3: MOTOR DE CRÉDITO E CAMADAS RELACIONAIS
    PipelineStep(name="Dimensao Contraparte", func=preparar_dim_contraparte),
    PipelineStep(name="Fato Analise de Credito", func=preparar_fato_analise),
    PipelineStep(name="Fato Garantia", func=gerar_fato_garantia),
    PipelineStep(name="Fato Exposicao de Risco", func=preparar_e_rodar_risco),
    PipelineStep(name="Fato Reconciliacao Denodo x MtM", func=executar_reconciliacao_denodo_mtm),
    PipelineStep(name="Fato Reconciliacao Fichas x Salesforce", func=executar_reconciliacao_fichas_salesforce),
    PipelineStep(name="Alertas de Carga Manual e Exceções", func=gerar_fato_alertas_manuais),
    PipelineStep(name="Visao Consolidada Gold", func=exportar_visao_consolidada_gold),
    PipelineStep(name="Fato Alertas de Credito", func=gerar_fato_alertas_credito),

    # BLOCO 4: INTERFACE
    PipelineStep(name="Interface Streamlit", func=lambda ctx: rodar_interface_streamlit()),
]
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs-dir", default=str(Path("ENTRADAS") / "configs"))
    parser.add_argument("--ui", action="store_true", help="Abre apenas a interface, sem rodar o pipeline")
    parser.add_argument("--no-ui", action="store_true", help="Roda apenas o pipeline, sem abrir a interface no final")
    args = parser.parse_args()

    if args.ui:
        rodar_interface_streamlit()
        return 0

    try:
        context = carregar_contexto(Path(args.configs_dir))
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao inicializar: {e}")
        return 1

    run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger_runner = obter_logger("bdc.runner", context.path("log_runner") / f"{run_id}__orquestrador_principal.log")

    control_dir = context.path("saidas") / "relational" / "control" if hasattr(context, "path") else Path("SAIDAS/relational/control")
    registro_inicio = registrar_inicio_pipeline(run_id, len(PIPELINE_STEPS), control_dir)

    exit_codes = []
    metricas_operacionais = {}
    
    for step in PIPELINE_STEPS:
        try:
            logger_runner.info(f"\n{'=' * 60}\nExecutando Etapa: {step.name}\n{'=' * 60}")
            import inspect
            sig = inspect.signature(step.func)
            if len(sig.parameters) > 0:
                result = step.func(context)
            else:
                result = step.func()
                
            if step.name == "Visao Consolidada Gold" and isinstance(result, dict):
                metricas_operacionais = result
                
            logger_runner.info(f"[OK] '{step.name}' concluido com sucesso.")
            exit_codes.append(0)
        except Exception as e:
            logger_runner.error(f"[ERRO] '{step.name}' falhou com a excecao: {e}", exc_info=True)
            exit_codes.append(1)
            
            if step.name in ["Ingestao de Contratos (Denodo)", "Reconciliacao Denodo x MtM"]:
                logger_runner.error(f"[ERRO FATAL] Interrompendo pipeline devido a falha critica em '{step.name}'.")
                return 1

    etapas_ok = sum(1 for code in exit_codes if code == 0)
    etapas_falha = sum(1 for code in exit_codes if code != 0)
    registrar_fim_pipeline(registro_inicio, etapas_ok, etapas_falha, control_dir)

    logger_runner.info(f"\n{'=' * 60}\nResumo Final da Execucao do Pipeline:")
    for step, code in zip(PIPELINE_STEPS, exit_codes):
        logger_runner.info(f"  - {step.name}: {'OK' if code == 0 else f'FALHOU (codigo {code})'}")
        
    logger_runner.info(f"{'=' * 60}")

    return 1 if any(code != 0 for code in exit_codes) else 0

if __name__ == "__main__":
    sys.exit(main())
```


# GRUPO: reset.py


---

## `reset.py`

- Linhas: 141
- SHA-256: `c979c3cab322361465cecb7e954be33d61f95a326d8c33956228c2396028aa1e`
- Classes: -
- Funções: clear_directory_contents, clear_jsonl_files, move_files_back_to_pending, move_generic_back_to_pending, main

```python
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENTRADAS_DIR = ROOT / "ENTRADAS"
SAIDAS_DIR = ROOT / "SAIDAS"
LOGS_DIR = ROOT / "LOGS"


def clear_directory_contents(dir_path: Path) -> int:
    """Apaga o conteúdo interno de um diretório sem remover a pasta raiz."""
    removed = 0
    if not dir_path.exists() or not dir_path.is_dir():
        return removed

    for item in sorted(dir_path.iterdir()):
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                removed += 1
            elif item.is_dir():
                shutil.rmtree(item)
                removed += 1
        except Exception as exc:
            print(f"⚠️ Falha ao limpar {item}: {exc}")
    return removed


def clear_jsonl_files(dir_path: Path) -> int:
    """Remove apenas arquivos .jsonl de um diretório."""
    removed = 0
    if not dir_path.exists() or not dir_path.is_dir():
        return removed

    for file_path in sorted(dir_path.glob("*.jsonl")):
        try:
            file_path.unlink()
            removed += 1
        except Exception as exc:
            print(f"⚠️ Falha ao apagar {file_path.name}: {exc}")
    return removed


def move_files_back_to_pending(category: str) -> int:
    """Move os arquivos de processadas/rejeitadas para pendentes."""
    base_path = ENTRADAS_DIR / "fichas" / category
    pendentes_dir = base_path / "pendentes"
    processadas_dir = base_path / "processadas"
    rejeitadas_dir = base_path / "rejeitadas"

    pendentes_dir.mkdir(parents=True, exist_ok=True)
    moved = 0

    for source_dir in (processadas_dir, rejeitadas_dir):
        if not source_dir.exists():
            continue

        for source_file in sorted(source_dir.rglob("*")):
            if not source_file.is_file():
                continue

            rel_path = source_file.relative_to(source_dir)
            destination = pendentes_dir / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)

            if destination.exists():
                destination.unlink()

            shutil.move(str(source_file), str(destination))
            moved += 1

    return moved

def move_generic_back_to_pending(base_path: Path) -> int:
    pendentes_dir = base_path / "pendentes"
    processadas_dir = base_path / "processadas"
    rejeitadas_dir = base_path / "rejeitadas"

    pendentes_dir.mkdir(parents=True, exist_ok=True)
    moved = 0

    for source_dir in (processadas_dir, rejeitadas_dir):
        if not source_dir.exists():
            continue

        for source_file in sorted(source_dir.rglob("*")):
            if not source_file.is_file():
                continue

            rel_path = source_file.relative_to(source_dir)
            destination = pendentes_dir / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)

            if destination.exists():
                destination.unlink()

            shutil.move(str(source_file), str(destination))
            moved += 1

    return moved

def main() -> None:
    print("Reiniciando o pipeline BDC...")

    targets = [
        SAIDAS_DIR / "staging",
        SAIDAS_DIR / "bronze" / "fichas_comercializadoras_raw",
        SAIDAS_DIR / "bronze" / "fichas_consumidores_raw",
        SAIDAS_DIR / "bronze" / "snapshots_fontes",
        SAIDAS_DIR / "silver",
        SAIDAS_DIR / "relational",
        SAIDAS_DIR / "gold",
        SAIDAS_DIR / "output",
        LOGS_DIR
    ]

    for path in targets:
        if path.exists():
            cleared = clear_directory_contents(path)
            print(f"Limpo: {path} ({cleared} itens removidos)")

    ingestion_log_dir = SAIDAS_DIR / "bronze" / "ingestion_log"
    jsonl_removed = clear_jsonl_files(ingestion_log_dir)
    print(f"Arquivos .jsonl removidos em {ingestion_log_dir}: {jsonl_removed}")

    moved_comercializadoras = move_files_back_to_pending("comercializadoras")
    moved_consumidores = move_files_back_to_pending("consumidores")
    moved_overrides = move_generic_back_to_pending(ENTRADAS_DIR / "overrides")
    moved_manual = move_generic_back_to_pending(ENTRADAS_DIR / "atualizacoes_manuais")

    print(f"Comercializadoras movidas para pendentes: {moved_comercializadoras}")
    print(f"Consumidores movidos para pendentes: {moved_consumidores}")
    print(f"Overrides movidos para pendentes: {moved_overrides}")
    print(f"Carga Manual movidas para pendentes: {moved_manual}")
    print("Reset concluído. Agora você pode executar novamente o main.py.")


if __name__ == "__main__":
    main()
```


# GRUPO: scripts


---

## `scripts/auditoria_fase3_alertas.py`

- Linhas: 43
- SHA-256: `93d6c67465ef4f2de5144e2f4aaa614af81078b6c74a50dbf840a191b772e16a`
- Classes: -
- Funções: auditar_alertas

```python
import pandas as pd
from pathlib import Path

def auditar_alertas():
    path = Path(r"SAIDAS/relational/facts/alertas/fato_alerta_credito.parquet")
    if not path.exists():
        print(f"Base de alertas não encontrada: {path}")
        return
        
    df = pd.read_parquet(path)
    
    print("="*80)
    print(f"AUDITORIA DE ALERTAS DE NEGÓCIO - FASE 3")
    print(f"Total de alertas disparados: {len(df)}")
    print("="*80)
    
    print("\n[A] DISTRIBUIÇÃO DE ALERTAS IMPLEMENTADOS:")
    if 'CODIGO_ALERTA' in df.columns:
        print(df['CODIGO_ALERTA'].value_counts(dropna=False))
    else:
        print("Coluna CODIGO_ALERTA ausente!")
        
    print("\n[B] STATUS DOS ALERTAS CRÍTICOS PARA CARGA MANUAL:")
    alertas_criticos = ['DF_001', 'MAN_001', 'MAN_002', 'MAN_003', 'MAN_004', 'EXC_001']
    encontrados = df[df['CODIGO_ALERTA'].isin(alertas_criticos)]
    if encontrados.empty:
        print(">>> Nenhum alerta da esteira de Carga Manual/Exceção foi disparado. CONFIRMADO: GAP FUNCIONAL.")
    else:
        print(encontrados['CODIGO_ALERTA'].value_counts())
        
    print("\n[C] AMOSTRAGEM PARA VALIDAÇÃO DE FALSOS POSITIVOS:")
    if not df.empty:
        amostra = df.sample(min(15, len(df)))
        colunas_exibicao = ['CODIGO_ALERTA', 'CNPJ', 'MENSAGEM_DESCRITIVA', 'CAMPO_AFETADO', 'VALOR_OBSERVADO']
        colunas_presentes = [c for c in colunas_exibicao if c in df.columns]
        
        for _, row in amostra[colunas_presentes].iterrows():
            print("-" * 50)
            for col in colunas_presentes:
                print(f"{col}: {row[col]}")

if __name__ == "__main__":
    auditar_alertas()
```


---

## `scripts/busca_lucro_liquido.py`

- Linhas: 62
- SHA-256: `491ab1f038b79aaac0771b6ba5104ccbb5df66f8bcdee6d04ec52486464ea741`
- Classes: -
- Funções: main

```python
import re
import openpyxl
import pandas as pd
from pathlib import Path

def main():
    print("="*80)
    print("BUSCA PROFUNDA: LUCRO LÍQUIDO EM TODAS AS ABAS (PADRAO 2 E 4)")
    print("="*80)
    
    base_dir = Path(r"<USER_HOME>\Desktop\BDC")
    processadas_dir = base_dir / "ENTRADAS" / "fichas" / "comercializadoras" / "processadas"
    
    # Carrega base Silver para pegar amostras
    silver_path = base_dir / "SAIDAS" / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    if not silver_path.exists():
        print("Base Silver não encontrada.")
        return
        
    df = pd.read_parquet(silver_path)
    
    regex_lucro = re.compile(r'lucro\s*l[ií]quido|resultado\s*l[ií]quido|lucro.*preju[ií]zo.*exerc[ií]cio', re.IGNORECASE)
    
    for versao in ["padrao_2", "padrao_4"]:
        amostras = df[df["versao_ficha"] == versao]["arquivo_nome"].dropna().unique()
        # Pega as 3 primeiras amostras físicas
        amostras_fisicas = [a for a in amostras if (processadas_dir / a).exists()][:3]
        
        print(f"\n[{versao}] Buscando em {len(amostras_fisicas)} amostras:")
        for arquivo in amostras_fisicas:
            caminho_arquivo = processadas_dir / arquivo
            print(f"\n  -> Arquivo: {arquivo}")
            try:
                wb = openpyxl.load_workbook(caminho_arquivo, data_only=True)
                encontrou = False
                for aba_nome in wb.sheetnames:
                    ws = wb[aba_nome]
                    for r in range(1, min(ws.max_row, 300) + 1):
                        for c in range(1, min(ws.max_column, 30) + 1):
                            cell = ws.cell(row=r, column=c)
                            if cell.value and isinstance(cell.value, str):
                                if regex_lucro.search(cell.value):
                                    encontrou = True
                                    # Pega o valor da vizinhança
                                    vizinhos = []
                                    if c < ws.max_column:
                                        v_dir = ws.cell(row=r, column=c+1).value
                                        if v_dir is not None: vizinhos.append(f"Dir:{v_dir}")
                                    if r < ws.max_row:
                                        v_baixo = ws.cell(row=r+1, column=c).value
                                        if v_baixo is not None: vizinhos.append(f"Abaixo:{v_baixo}")
                                        
                                    print(f"      [Encontrado na aba '{aba_nome}'] Célula {cell.coordinate}: '{cell.value}'")
                                    if vizinhos:
                                        print(f"         Vizinhos: {' | '.join(vizinhos)}")
                if not encontrou:
                    print("      NÃO ENCONTRADO em nenhuma aba!")
            except Exception as e:
                print(f"      Erro ao ler arquivo: {e}")

if __name__ == "__main__":
    main()
```


---

## `scripts/busca_profunda.py`

- Linhas: 95
- SHA-256: `bf4f026551a0fd742f8bc04d614e476056d850f6a51cbeb6d5edd27db0bf4146`
- Classes: -
- Funções: main

```python
import pandas as pd
from pathlib import Path
import openpyxl
import re

def main():
    silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.parquet")
    if silver_path.exists():
        df = pd.read_parquet(silver_path)
    else:
        df = pd.read_csv(str(silver_path).replace(".parquet", ".csv"), sep=";")
        
    pastas_raw = Path("ENTRADAS/fichas/comercializadoras/processadas")
    
    print("="*60)
    print("FRENTE 2: VERIFICAÇÃO DE DATA LIMITE (30/04/2025)")
    print("="*60)
    
    df["DATA_DF_DT"] = pd.to_datetime(df["DATA_DEMONSTRACAO_FINANCEIRA"], errors="coerce")
    limite = pd.Timestamp('2025-04-30')
    
    for versao in ["padrao_2", "padrao_4"]:
        df_v = df[df["versao_ficha"] == versao].dropna(subset=["DATA_DF_DT"])
        total = len(df_v)
        antes = (df_v["DATA_DF_DT"] < limite).sum()
        depois = (df_v["DATA_DF_DT"] >= limite).sum()
        print(f"[{versao}] Total de registros com data válida: {total}")
        print(f"  -> Antes de 30/04/2025 (Sem allow_semantic): {antes}")
        print(f"  -> Depois de 30/04/2025 (Com allow_semantic): {depois}\n")

    print("="*60)
    print("FRENTE 3: BUSCA PROFUNDA (GAP REAL E WD AGROINDUSTRIAL)")
    print("="*60)
    
    regex_a = re.compile(r'\b(FCO|ROA|ROE)\b|NOTA\s+BOARD|BOARD|NOTA\s+BUREAU|SCORE\s+BUREAU|\bBUREAU\b', re.IGNORECASE)
    
    for versao in ["padrao_2", "padrao_3", "padrao_4", "padrao_5"]:
        amostras = df[df["versao_ficha"] == versao]["arquivo_nome"].dropna().unique()
        amostras_fisicas = [a for a in amostras if (pastas_raw / a).exists()][:2]
        
        for arquivo in amostras_fisicas:
            caminho_arquivo = pastas_raw / arquivo
            print(f"\nBuscando 5 indicadores (gap real) em [{versao}] {arquivo}...")
            try:
                wb = openpyxl.load_workbook(caminho_arquivo, data_only=True)
                # Foca nas abas de Memória de Cálculo / Conf. Puras DRE e DFC, ou todas
                abas_alvo = [a for a in wb.sheetnames if "memória" in a.lower() or "calculo" in a.lower() or "cálculo" in a.lower() or "dre" in a.lower() or "dfc" in a.lower()]
                if not abas_alvo: abas_alvo = wb.sheetnames
                    
                encontrou_algo = False
                for aba_nome in abas_alvo:
                    ws = wb[aba_nome]
                    for r in range(1, min(ws.max_row, 300) + 1):
                        for c in range(1, min(ws.max_column, 25) + 1):
                            cell = ws.cell(row=r, column=c)
                            if cell.value and isinstance(cell.value, str):
                                if regex_a.search(cell.value):
                                    encontrou_algo = True
                                    val = str(cell.value).strip().replace('\n', ' ')
                                    if len(val) > 40: val = val[:37] + "..."
                                    print(f"  ENCONTRADO [{aba_nome}] {cell.coordinate}: '{val}'")
                if not encontrou_algo:
                    print("  -> CONFIRMADO: Nenhum dos 5 indicadores foi encontrado nas abas matemáticas.")
                wb.close()
            except Exception as e:
                print(f"Erro: {e}")

    print("\nBuscando TIPO_COMERCIALIZADORA em TODAS AS ABAS do arquivo WD AGROINDUSTRIAL (padrao_7)...")
    wd_files = [f for f in df[df["versao_ficha"] == "padrao_7"]["arquivo_nome"].unique() if "WD" in str(f).upper()]
    if wd_files and (pastas_raw / wd_files[0]).exists():
        arquivo_wd = wd_files[0]
        caminho_wd = pastas_raw / arquivo_wd
        regex_b = re.compile(r'TIPO\s+DE\s+COMERCIALIZADORA|CPURA|CGRUPO|\bPURA\b|\bGRUPO\b', re.IGNORECASE)
        try:
            wb = openpyxl.load_workbook(caminho_wd, data_only=True)
            encontrou = False
            for aba_nome in wb.sheetnames:
                ws = wb[aba_nome]
                for r in range(1, min(ws.max_row, 300) + 1):
                    for c in range(1, min(ws.max_column, 30) + 1):
                        cell = ws.cell(row=r, column=c)
                        if cell.value and isinstance(cell.value, str):
                            if regex_b.search(cell.value):
                                if "grupo econ" in str(cell.value).lower(): continue
                                encontrou = True
                                val = str(cell.value).strip().replace('\n', ' ')
                                print(f"  ENCONTRADO [{aba_nome}] {cell.coordinate}: '{val}'")
            if not encontrou:
                print("  -> CONFIRMADO: Campo totalmente OMITIDO da ficha física.")
            wb.close()
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
```


---

## `scripts/buscar_coordenadas_amostra.py`

- Linhas: 85
- SHA-256: `1b8e9b09130566372f9c7877fa3725bb38b3275715d92fe03bdaf9ced01b70f0`
- Classes: -
- Funções: buscar_amostras

```python
import pandas as pd
from pathlib import Path
import openpyxl
import re

def buscar_amostras():
    silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.parquet")
    if silver_path.exists():
        df = pd.read_parquet(silver_path)
    else:
        df = pd.read_csv(str(silver_path).replace(".parquet", ".csv"), sep=";")

    pastas_raw = Path("ENTRADAS/fichas/comercializadoras/processadas")
    
    regex_a = re.compile(r'\b(FCO|ROA|ROE)\b|LUCRO\s+L[IÍ]QUIDO|LUCRO/PREJU[IÍ]ZO|RESULTADO\s+L[IÍ]QUIDO|FLUXO\s+DE\s+CAIXA\s+OPERACIONAL|FLUXO\s+DE\s+CAIXA\s+DAS\s+ATIVIDADES|CAIXA\s+L[IÍ]QUIDO\s+GERADO|NOTA\s+BOARD|BOARD|NOTA\s+BUREAU|SCORE\s+BUREAU|\bBUREAU\b', re.IGNORECASE)
    regex_b = re.compile(r'TIPO\s+DE\s+COMERCIALIZADORA|CPURA|CGRUPO|\bPURA\b|\bGRUPO\b', re.IGNORECASE)
    
    versoes = {
        "padrao_2": regex_a,
        "padrao_3": regex_a,
        "padrao_4": regex_a,
        "padrao_5": regex_a,
        "padrao_6": regex_b,
        "padrao_7": regex_b
    }
    
    for versao, regex_comp in versoes.items():
        print("="*90)
        print(f"ANALISANDO VERSÃO: {versao}")
        print("="*90)
        
        amostras = df[df["versao_ficha"] == versao]["arquivo_nome"].dropna().unique()
        amostras_fisicas = [a for a in amostras if (pastas_raw / a).exists()][:2]
        
        if not amostras_fisicas:
            print("Nenhuma amostra física encontrada.")
            continue
            
        for arquivo in amostras_fisicas:
            caminho_arquivo = pastas_raw / arquivo
            print(f"\n>>> ARQUIVO: {arquivo}")
            try:
                wb = openpyxl.load_workbook(caminho_arquivo, data_only=True)
                for aba_nome in wb.sheetnames:
                    ws = wb[aba_nome]
                    max_row = min(ws.max_row, 150)
                    max_col = min(ws.max_column, 25)
                    
                    for r in range(1, max_row + 1):
                        for c in range(1, max_col + 1):
                            cell = ws.cell(row=r, column=c)
                            if cell.value and isinstance(cell.value, str):
                                if regex_comp.search(cell.value):
                                    if "grupo econ" in cell.value.lower(): continue
                                    
                                    coord = cell.coordinate
                                    val = str(cell.value).strip().replace('\n', ' ')
                                    if len(val) > 40: val = val[:37] + "..."
                                    
                                    # Vizinhos Dir, Dir2, Baixo, BaixoDir
                                    vizinhos = []
                                    if c + 1 <= max_col:
                                        v = ws.cell(row=r, column=c+1).value
                                        if v is not None: vizinhos.append(f"Dir:{str(v)[:20]}")
                                    if c + 2 <= max_col:
                                        v = ws.cell(row=r, column=c+2).value
                                        if v is not None: vizinhos.append(f"Dir2:{str(v)[:20]}")
                                    if r + 1 <= max_row:
                                        v = ws.cell(row=r+1, column=c).value
                                        if v is not None: vizinhos.append(f"Abaixo:{str(v)[:20]}")
                                    if r + 1 <= max_row and c + 1 <= max_col:
                                        v = ws.cell(row=r+1, column=c+1).value
                                        if v is not None: vizinhos.append(f"AbaixoDir:{str(v)[:20]}")
                                        
                                    viz_str = " | ".join(vizinhos).replace('\n', ' ')
                                    if not viz_str: viz_str = "Vazio"
                                    
                                    print(f"  [{aba_nome}] {coord}: '{val}' --> VIZINHOS: {viz_str}")
                                    
                wb.close()
            except Exception as e:
                print(f"Erro lendo arquivo: {e}")

if __name__ == "__main__":
    buscar_amostras()
```


---

## `scripts/captura_evidencias.py`

- Linhas: 62
- SHA-256: `0ae7fc9653fb04e479f579ad73ce14f93f09857d62967701984feb561bdd0bb9`
- Classes: -
- Funções: -

```python
import pandas as pd
from pathlib import Path
import json

base = Path(r"<USER_HOME>\Desktop\BDC")

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
```


---

## `scripts/check_fase2.py`

- Linhas: 64
- SHA-256: `834dd41d6dc36a0e82a08b7be4d700144c4704392a93941ea4a863b2df0dd4de`
- Classes: -
- Funções: rodar_auditoria

```python
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

def rodar_auditoria(caminho, segmento):
    pasta = Path(caminho)
    if not pasta.exists():
        return
    
    arquivos = list(pasta.glob("*.parquet"))
    if not arquivos:
        return
        
    df = pd.concat([pd.read_parquet(f) for f in arquivos], ignore_index=True)
    print(f"\n{'='*60}\nAUDITORIA SILVER: {segmento} | Total: {len(df)} registros\n{'='*60}")
    
    col_v = None
    for c in ["VERSAO_FICHA", "LAYOUT", "NOME_LAYOUT", "LAYOUT_NAME", "VERSAO", "TIPO_LAYOUT", "LAYOUT_UTILIZADO", "PADRAO_LAYOUT"]:
        if c in df.columns:
            col_v = c
            break
    
    if col_v:
        for v in df[col_v].unique():
            df_v = df[df[col_v] == v]
            print(f"\n--- Layout/Versão: {v} ({len(df_v)} registros) ---")
            nulos = (df_v.isnull().sum() / len(df_v)) * 100
            for campo, pct in nulos[nulos > 0].sort_values(ascending=False).head(10).items():
                print(f"  {campo}: {pct:.1f}% nulo")
    else:
        print("\n[AVISO] Coluna de versão não encontrada. Colunas disponíveis no arquivo:")
        print(df.columns.tolist())
        # Imprime os nulos globais como fallback
        print("\n--- % Nulos Geral ---")
        nulos = (df.isnull().sum() / len(df)) * 100
        for campo, pct in nulos[nulos > 0].sort_values(ascending=False).head(10).items():
            print(f"  {campo}: {pct:.1f}% nulo")
        
    # --- TESTE DA REGRA CRÍTICA: AUSÊNCIA DE DF NÃO VIRA ZERO ---
    print(f"\n--- Validação: Regra de Ouro (DF ausente != Zero) ---")
    campos_fin = ["ATIVO_TOTAL", "LUCRO_LIQUIDO", "PATRIMONIO_LIQUIDO", "PASSIVO_CIRCULANTE"]
    campos_fin = [c for c in campos_fin if c in df.columns]
    
    if "DATA_DEMONSTRACAO_FINANCEIRA" in df.columns:
        mask_df_ausente = df["DATA_DEMONSTRACAO_FINANCEIRA"].isnull() | (df["DATA_DEMONSTRACAO_FINANCEIRA"].astype(str).str.upper() == "NAO_APLICAVEL")
        df_ausentes = df[mask_df_ausente]
        
        violacoes = 0
        if not df_ausentes.empty:
            for c in campos_fin:
                zeros = df_ausentes[df_ausentes[c] == 0.0]
                if not zeros.empty:
                    print(f"[FALHA CRÍTICA] Campo {c} virou '0.0' indevidamente em {len(zeros)} fichas sem DF! Ex: CNPJs {zeros['CNPJ'].head(3).tolist()}")
                    violacoes += len(zeros)
                    
        if violacoes == 0:
            print("[OK] Nenhum indicador financeiro avaliado foi convertido para zero incorretamente.")
    else:
        print("[AVISO] DATA_DEMONSTRACAO_FINANCEIRA ausente no parquet.")

if __name__ == "__main__":
    rodar_auditoria(r"SAIDAS\silver\fichas_comercializadoras_extraidas", "Comercializadoras")
    rodar_auditoria(r"SAIDAS\silver\fichas_consumidores_extraidas", "Consumidores")
```


---

## `scripts/comparar_bases.py`

- Linhas: 55
- SHA-256: `ba550c1b2c4d6f98133bbb4ba5a883bdce8e6af47dad0403b126220a383a18a1`
- Classes: -
- Funções: main

```python
import pandas as pd
from pathlib import Path

def main():
    print("="*100)
    print("COMPARAÇÃO DE BASES TRILATERAL: REGRA ANTIGA vs OMNI-LAYOUT vs MODELO HÍBRIDO")
    print("="*100)

    base_dir = Path(r"<USER_HOME>\Desktop\BDC")
    
    path_antiga = base_dir / "tests" / "fichas_comercializadoras_extraidas_versao_7layouts.csv"
    path_omni = base_dir / "tests" / "fichas_comercializadoras_extraidas_versao_omni_layout.csv"
    path_hibrida = base_dir / "SAIDAS" / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.csv"

    dfs = {}
    for nome, path in [("Antiga (7 s/ Semântica)", path_antiga), ("Omni (Só Padrão 7)", path_omni), ("Híbrida (7 c/ Semântica)", path_hibrida)]:
        if not path.exists():
            print(f"ERRO: Base {nome} não encontrada em {path}")
            return
        try:
            dfs[nome] = pd.read_csv(path, sep=";")
        except:
            dfs[nome] = pd.read_csv(path)
            
    print("\n--- TOTAL DE REGISTROS EXTRAÍDOS ---")
    for nome, df in dfs.items():
        print(f"  - {nome}: {len(df)} registros")

    print("\n--- COMPARATIVO DE NULOS (Menos nulos = Melhor) ---")
    
    campos_criticos = [
        "TIPO_COMERCIALIZADORA", "FCO", "ROA", "ROE",
        "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        "NOTA_BOARD", "NOTA_BUREAU", "PATRIMONIO_LIQUIDO"
    ]
    
    resultados = []
    
    for col in campos_criticos:
        nulos_antiga = dfs["Antiga (7 s/ Semântica)"][col].isna().sum() if col in dfs["Antiga (7 s/ Semântica)"].columns else "N/A"
        nulos_omni = dfs["Omni (Só Padrão 7)"][col].isna().sum() if col in dfs["Omni (Só Padrão 7)"].columns else "N/A"
        nulos_hibrida = dfs["Híbrida (7 c/ Semântica)"][col].isna().sum() if col in dfs["Híbrida (7 c/ Semântica)"].columns else "N/A"
        
        resultados.append({
            "Campo": col,
            "Nulos Antiga": nulos_antiga,
            "Nulos Omni": nulos_omni,
            "Nulos Híbrida": nulos_hibrida
        })
            
    df_res = pd.DataFrame(resultados)
    print(df_res.to_string(index=False))

if __name__ == "__main__":
    main()
```


---

## `scripts/debug_silver_comercializadoras.py`

- Linhas: 107
- SHA-256: `985409c0fcba2a568ae044e2eae9847c7d5f7ef8022a6c1c9298ec7c8a41e68c`
- Classes: -
- Funções: generate_audit_report

```python
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
```


---

## `scripts/debug_zero_consumidores.py`

- Linhas: 29
- SHA-256: `1a846352f329d647a27c60d4726e8ccaf965f30e61e77c795f31cf68663f8955`
- Classes: -
- Funções: debug_zeros

```python
import pandas as pd
from pathlib import Path

def debug_zeros():
    caminho = Path(r"SAIDAS\silver\fichas_consumidores_extraidas")
    arquivos = list(caminho.glob("*.parquet"))
    
    if not arquivos:
        print("Arquivos parquet não encontrados.")
        return
        
    df = pd.concat([pd.read_parquet(f) for f in arquivos], ignore_index=True)
    cnpjs_problema = ['00529188000160', '38246958000130', '41501877000143']
    alvos = df[df["CNPJ"].isin(cnpjs_problema)]
    
    colunas = [
        "CNPJ", "arquivo_nome", "tipo_analise_exigida", "DATA_DEMONSTRACAO_FINANCEIRA", 
        "LUCRO_LIQUIDO", "PATRIMONIO_LIQUIDO", "ATIVO_TOTAL"
    ]
    cols = [c for c in colunas if c in alvos.columns]
    
    print("\n" + "="*80 + "\nDIAGNÓSTICO DOS 'FALSOS ZEROS'\n" + "="*80)
    for _, row in alvos[cols].iterrows():
        print("\n--------------------------------------------------")
        for col in cols:
            print(f"{col}: {row[col]}")

if __name__ == "__main__":
    debug_zeros()
```


---

## `scripts/find_coords.py`

- Linhas: 55
- SHA-256: `1207be0ba570b69c3e0e4cdc6309b83b1bb936ac69c2b5a6309688e4571fc04a`
- Classes: -
- Funções: -

```python
import openpyxl
from pathlib import Path
import os

files_to_check = {
    "padrao_4": "ATVOS SANTA LUZIA 31072026.xlsx",
    "padrao_2": "SAFIRA COM_05_03_2021.xlsx",
    "padrao_6": "POLLARIX 03062026.xlsx",
    "padrao_7": "ENGIE 12052026.xlsx"
}

base_dir = Path(r"<USER_HOME>\Desktop\BDC\ENTRADAS\fichas\comercializadoras")

for padrao, filename in files_to_check.items():
    paths = list(base_dir.rglob(filename))
    if not paths:
        print(f"File not found recursively: {filename}")
        continue
    
    path = paths[0]
    print(f"\n--- Checking {filename} ({padrao}) ---")
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as e:
        print(f"Failed to load: {e}")
        continue
    
    # Check TIPO_COMERCIALIZADORA in FichaIndividual
    if "FichaIndividual" in wb.sheetnames:
        sheet = wb["FichaIndividual"]
        print("TIPO_COMERCIALIZADORA candidates:")
        for row in range(1, 30):
            for col in range(1, 10):
                val = str(sheet.cell(row=row, column=col).value).strip().upper()
                if val and ("PURA" in val or "GRUPO" in val or "COMERCIALIZADORA" in val):
                    coord = sheet.cell(row=row, column=col).coordinate
                    print(f"  FichaIndividual!{coord}: {val}")
                    
        print("\nCONTROLADOR candidates:")
        for row in range(1, 30):
            for col in range(1, 15):
                val = str(sheet.cell(row=row, column=col).value).strip().upper()
                if val and ("POLLARIX" in val or "ENGIE" in val or "SAFIRA" in val or "ATVOS" in val):
                    coord = sheet.cell(row=row, column=col).coordinate
                    print(f"  FichaIndividual!{coord}: {val}")
    
    if padrao == "padrao_2" and "Para_Limite_Comercializadoras" in wb.sheetnames:
        sheet = wb["Para_Limite_Comercializadoras"]
        print("\nPara_Limite_Comercializadoras TIPO candidates:")
        for row in range(1, 10):
            for col in range(1, 15):
                val = str(sheet.cell(row=row, column=col).value).strip().upper()
                if val and ("PURA" in val or "GRUPO" in val or "COMERCIALIZADORA" in val):
                    coord = sheet.cell(row=row, column=col).coordinate
                    print(f"  Para_Limite_Comercializadoras!{coord}: {val}")
```


---

## `scripts/find_labels.py`

- Linhas: 44
- SHA-256: `4b89a26ed1cd27dd4b64cf993eee4fdc190155c985a5399ef3b506ae58d372bf`
- Classes: -
- Funções: -

```python
import openpyxl
from pathlib import Path

files_to_check = {
    "padrao_6": "POLLARIX 03062026.xlsx",
    "padrao_7": "ENGIE 12052026.xlsx",
    "padrao_4": "ATVOS SANTA LUZIA 31072026.xlsx",
    "padrao_2": "SAFIRA COM_05_03_2021.xlsx"
}

base_dir = Path(r"<USER_HOME>\Desktop\BDC\ENTRADAS\fichas\comercializadoras")

for padrao, filename in files_to_check.items():
    paths = list(base_dir.rglob(filename))
    if not paths: continue
    
    print(f"\n--- {padrao}: {filename} ---")
    wb = openpyxl.load_workbook(paths[0], data_only=True)
    
    for sheet_name in ["FichaIndividual", "Para_Limite_Comercializadoras"]:
        if sheet_name not in wb.sheetnames: continue
        sheet = wb[sheet_name]
        
        for row in range(1, 100):
            for col in range(1, 20):
                val = str(sheet.cell(row=row, column=col).value).strip().upper()
                if not val or val == 'NONE': continue
                
                # Check for CONTROLADOR
                if "CONTROLADOR" in val:
                    neighbor = str(sheet.cell(row=row, column=col+1).value).strip()
                    neighbor_below = str(sheet.cell(row=row+1, column=col).value).strip()
                    print(f"[{sheet_name}] Found '{val}' at row {row}, col {col}")
                    print(f"  -> Right neighbor: {neighbor}")
                    print(f"  -> Below neighbor: {neighbor_below}")
                
                # Check for TIPO / PURA / GRUPO
                if "TIPO" in val and "COMER" in val:
                    neighbor = str(sheet.cell(row=row, column=col+1).value).strip()
                    print(f"[{sheet_name}] Found '{val}' at row {row}, col {col}")
                    print(f"  -> Right neighbor: {neighbor}")
                    
                if "PURA" in val or "GRUPO" in val:
                    print(f"[{sheet_name}] Cell contains '{val}' at row {row}, col {col}")
```


---

## `scripts/restore_data_calculo.py`

- Linhas: 73
- SHA-256: `1057b02ef6fbd3035ace4f78bf30806590616c4210b5aa56846b3951ea0e5147`
- Classes: -
- Funções: restore_data_calculo

```python
import json
import os

BASE_DIR = r"<USER_HOME>\Desktop\BDC\ENTRADAS\control"

f_master = os.path.join(BASE_DIR, "quality", "master_catalog_comercializadoras.json")
f_schema = os.path.join(BASE_DIR, "schemas", "schema_ficha_comercializadora_extraida.json")
f_mapping = os.path.join(BASE_DIR, "mappings", "mapping_fichas_comercializadoras.json")

def restore_data_calculo():
    # 1. Master Catalog
    with open(f_master, "r", encoding="utf-8") as f:
        master = json.load(f)
        
    master["fields"]["DATA_CALCULO"] = {
        "nature": "OBSERVED",
        "type": "date",
        "criticality": "OPTIONAL",
        "weight": 10,
        "search_patterns": ["DATA\\s*DA\\s*FICHA"]
    }
        
    with open(f_master, "w", encoding="utf-8") as f:
        json.dump(master, f, indent=4, ensure_ascii=False)
        
    # 2. Schema
    with open(f_schema, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    schema["properties"]["DATA_CALCULO"] = {
        "type": ["string", "null"]
    }
        
    with open(f_schema, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4, ensure_ascii=False)
        
    # 3. Mapping
    with open(f_mapping, "r", encoding="utf-8") as f:
        mapping = json.load(f)
        
    if not any(m.get("RUBRICAS") == "DATA_CALCULO" for m in mapping):
        novo_map = {
            "RUBRICAS": "DATA_CALCULO",
            "ABA_PADRAO_1": "V0",
            "CELULA_RUBRICA_PADRAO_1": "B5",
            "CELULA_PADRAO_1": "E5",
            "ABA_PADRAO_2": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_2": "A1",
            "CELULA_PADRAO_2": "E1",
            "ABA_PADRAO_3": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_3": "C7",
            "CELULA_PADRAO_3": "D7",
            "ABA_PADRAO_4": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_4": "C9",
            "CELULA_PADRAO_4": "D9",
            "ABA_PADRAO_5": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_5": "C8",
            "CELULA_PADRAO_5": "D8",
            "ABA_PADRAO_6": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_6": "C7",
            "CELULA_PADRAO_6": "D7",
            "ABA_PADRAO_7": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_7": "C7",
            "CELULA_PADRAO_7": "D7"
        }
        mapping.append(novo_map)
            
    with open(f_mapping, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    restore_data_calculo()
    print("DATA_CALCULO RESTAURADA COM SUCESSO!")
```


---

## `scripts/sync_metadata.py`

- Linhas: 93
- SHA-256: `83bdea4a37b7cb20d51023c63bfdf51695076bcd638fa2452012ad56ae057bd1`
- Classes: -
- Funções: clean_and_inject

```python
import json
import os
import copy

BASE_DIR = r"<USER_HOME>\Desktop\BDC\ENTRADAS\control"

f_master = os.path.join(BASE_DIR, "quality", "master_catalog_comercializadoras.json")
f_schema = os.path.join(BASE_DIR, "schemas", "schema_ficha_comercializadora_extraida.json")
f_mapping = os.path.join(BASE_DIR, "mappings", "mapping_fichas_comercializadoras.json")

campos_remover = [
    "DATA_CALCULO", "DATA_ABERTURA", "CEP", "ENDERECO", "AGENCIA", "DATA_RATING_AGENCIA", 
    "LUCRO_BRUTO", "LAJIR", "LAIR", "CONTROLADOR", "CNPJ_CONTROLADOR", "PL_CONTROLADOR", "PERCENTUAL_CONTROLADOR"
]

campos_injetar = {
    "CNPJ_BBCE": {"type": "string", "regex": ["CNPJ\\s*BBCE", "BBCE"]},
    "CODIGO_CCEE": {"type": "string", "regex": ["C[OÓ]DIGO\\s*CCEE", "CCEE"]},
    "DATA_ADESAO_CCEE": {"type": "date", "regex": ["DATA\\s*ADES[AÃ]O", "ADES[AÃ]O\\s*CCEE"]},
    "MATURIDADE_CALCULADA": {"type": "float", "regex": ["MATURIDADE", "MATURIDADE\\s*CALCULADA"]},
    "CATEGORIA": {"type": "string", "regex": ["CATEGORIA"]},
    "RATING_PUBLICO": {"type": "string", "regex": ["RATING\\s*P[UÚ]BLICO", "RATING\\s*AG[EÊ]NCIA"]},
    "SCORES_INDIVIDUAIS": {"type": "string", "regex": ["SCORES\\s*INDIVIDUAIS"]},
    "SCORE_QUANTITATIVO": {"type": "float", "regex": ["SCORE\\s*QUANTITATIVO", "SCORE\\s*QUANT"]},
    "DEMONSTRACOES_FINANCEIRAS_AUDITADAS": {"type": "string", "regex": ["DEMONSTRA[CÇ][OÕ]ES.*AUDITADAS", "DF.*AUDITADA"]},
    "RATING_SCORE_DE_AUDITORIA": {"type": "string", "regex": ["RATING.*AUDITORIA", "SCORE.*AUDITORIA"]},
    "RATING_SCORE_DE_BUREAU": {"type": "string", "regex": ["RATING.*BUREAU", "SCORE.*BUREAU"]},
    "RESTRITIVOS": {"type": "string", "regex": ["RESTRITIVOS", "APONTA.*RESTRITIVOS"]},
    "SCORE_QUALITATIVO": {"type": "float", "regex": ["SCORE\\s*QUALITATIVO", "SCORE\\s*QUAL"]},
    "MARGEM_DESPESA_PESSOAL": {"type": "float", "regex": ["MARGEM\\s*DESPESA", "RECEITA.*CUSTO.*PESSOAL"]},
    "MTM_TOTAL_PL": {"type": "float", "regex": ["MTM.*PL", "MTM.*PATRIM[OÔ]NIO"]},
    "DIVIDENDOS_LUCRO_LIQUIDO": {"type": "float", "regex": ["DIVIDENDOS.*LUCRO", "JCP.*LUCRO"]},
    "CAPITAL_CIRCULANTE_LIQUIDO": {"type": "float", "regex": ["CAPITAL\\s*CIRCULANTE\\s*L[IÍ]QUIDO", "CCL\\b"]}
}

def clean_and_inject():
    # 1. Master Catalog
    with open(f_master, "r", encoding="utf-8") as f:
        master = json.load(f)
        
    for c in campos_remover:
        if c in master["fields"]:
            del master["fields"][c]
            
    for c, meta in campos_injetar.items():
        master["fields"][c] = {
            "nature": "OBSERVED",
            "type": meta["type"],
            "criticality": "OPTIONAL",
            "weight": 10,
            "allow_semantic": True,
            "search_patterns": meta["regex"]
        }
        
    with open(f_master, "w", encoding="utf-8") as f:
        json.dump(master, f, indent=4, ensure_ascii=False)
        
    # 2. Schema
    with open(f_schema, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    for c in campos_remover:
        if c in schema["properties"]:
            del schema["properties"][c]
            
    for c, meta in campos_injetar.items():
        json_type = "number" if meta["type"] == "float" else "string"
        schema["properties"][c] = {"type": [json_type, "null"]}
        
    with open(f_schema, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4, ensure_ascii=False)
        
    # 3. Mapping
    with open(f_mapping, "r", encoding="utf-8") as f:
        mapping = json.load(f)
        
    mapping = [m for m in mapping if m.get("RUBRICAS") not in campos_remover]
    
    for c in campos_injetar.keys():
        if not any(m.get("RUBRICAS") == c for m in mapping):
            novo_map = {"RUBRICAS": c}
            for i in range(1, 8):
                novo_map[f"ABA_PADRAO_{i}"] = "0"
                novo_map[f"CELULA_RUBRICA_PADRAO_{i}"] = "0"
                novo_map[f"CELULA_PADRAO_{i}"] = "0"
            mapping.append(novo_map)
            
    with open(f_mapping, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    clean_and_inject()
    print("ARQUIVOS JSON ATUALIZADOS COM SUCESSO!")
```


---

## `scripts/teste_antes_depois_semantica.py`

- Linhas: 61
- SHA-256: `f743e9d51cb03a6e082a55a074b08edcd9391f3fa850eae464bc7bf32279ead9`
- Classes: -
- Funções: main

```python
import json
import logging
import openpyxl
from pathlib import Path
import sys
base_dir = Path(r"<USER_HOME>\Desktop\BDC")
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))
from domain.fichas.extrator import LeitorPlanilha, extrair_registro

logging.basicConfig(level=logging.ERROR)

def main():
    processadas_dir = base_dir / "ENTRADAS" / "fichas" / "comercializadoras" / "processadas"
    
    # Carrega master catalog
    catalog_path = base_dir / "ENTRADAS" / "control" / "quality" / "master_catalog_comercializadoras.json"
    with open(catalog_path, "r", encoding="utf-8") as f:
        master_catalog = json.load(f)
        
    # Amostras para testar
    amostras = {
        "padrao_2": "TRADENER 29_08_2022.xlsx",
        "padrao_4": "BOENERGY_08052023.xlsx"
    }
    
    print("="*80)
    print("TESTE A/B: EXTRAÇÃO COM VS SEM SEMÂNTICA (REGEX)")
    print("="*80)
    
    for padrao, arquivo in amostras.items():
        print(f"\n[{padrao}] Arquivo: {arquivo}")
        
        # Carrega o layout correspondente
        layout_path = base_dir / "ENTRADAS" / "control" / "layouts" / f"layout_ficha_comercializadora_v{padrao[-1]}.json"
        with open(layout_path, "r", encoding="utf-8") as f:
            layout_schema = json.load(f)
            
        caminho_arquivo = processadas_dir / arquivo
        if not caminho_arquivo.exists():
            print(f"  -> Arquivo {arquivo} não encontrado na pasta processadas.")
            continue
            
        # Carrega a planilha na memória
        wb = openpyxl.load_workbook(caminho_arquivo, data_only=True)
        leitor = LeitorPlanilha.do_workbook(wb)
        
        # TESTE 1: REGRA ANTIGA (Sem Semântica)
        dados_antigo, _ = extrair_registro(leitor, layout_schema, master_catalog, allow_semantic=False)
        lucro_antigo = dados_antigo.get("LUCRO_LIQUIDO")
        
        # TESTE 2: REGRA NOVA (Com Semântica Forçada)
        # Atenção: Precisamos garantir que o campo tem search_pattern no layout!
        dados_novo, _ = extrair_registro(leitor, layout_schema, master_catalog, allow_semantic=True)
        lucro_novo = dados_novo.get("LUCRO_LIQUIDO")
        
        print(f"  -> ANTES  (Semântica OFF): LUCRO_LIQUIDO = {lucro_antigo}")
        print(f"  -> DEPOIS (Semântica ON) : LUCRO_LIQUIDO = {lucro_novo}")

if __name__ == "__main__":
    main()
```


---

## `scripts/teste_hipotese_cluster.py`

- Linhas: 76
- SHA-256: `cc16aea5f47e8977656ae4c9f275d938259d2e1f363ca50a5e31f27ec6c35c7f`
- Classes: -
- Funções: testar_hipotese_cluster

```python
import pandas as pd
from pathlib import Path

def testar_hipotese_cluster():
    silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.parquet")
    if not silver_path.exists():
        silver_path = Path("SAIDAS/silver/fichas_comercializadoras_extraidas/fichas_comercializadoras_extraidas.csv")
        if not silver_path.exists():
            print("Base Silver não encontrada.")
            return
            
    if silver_path.suffix == ".parquet":
        df = pd.read_parquet(silver_path)
    else:
        df = pd.read_csv(silver_path, sep=";")
        
    print("="*60)
    print("1. TESTE DA HIPÓTESE DO CLUSTER (Agrupamento por versao_ficha)")
    print("="*60)
    
    campos_alvo = [
        "TIPO_COMERCIALIZADORA", "FCO", "ROA", "ROE",
        "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        "NOTA_BOARD", "NOTA_BUREAU"
    ]
    
    total_por_versao = df["versao_ficha"].value_counts().to_dict()
    print("Total de registros por versao_ficha na base:")
    for v, t in total_por_versao.items():
        print(f"  - {v}: {t} registros")
    print("-" * 40)
    
    for campo in campos_alvo:
        if campo not in df.columns:
            print(f"Campo {campo} não existe na base.")
            continue
            
        nulos_mask = df[campo].isna()
        total_nulos = nulos_mask.sum()
        
        if total_nulos == 0:
            print(f"Campo {campo}: 0 nulos.")
            continue
            
        df_nulos = df[nulos_mask]
        contagem = df_nulos["versao_ficha"].value_counts()
        
        print(f"\nCampo: {campo} ({total_nulos} nulos no total)")
        for versao, qtd in contagem.items():
            pct_do_campo = (qtd / total_nulos) * 100
            pct_da_versao = (qtd / total_por_versao.get(versao, 1)) * 100
            print(f"  -> {versao}: {qtd} nulos ({pct_do_campo:.1f}% dos nulos, afeta {pct_da_versao:.1f}% desta versão)")
            
    print("\n" + "="*60)
    print("2. SANITY CHECK GLOBAL DE DATA (Impacto Atual na Silver)")
    print("="*60)
    
    campos_data = ["DATA_DEMONSTRACAO_FINANCEIRA", "DATA_ADESAO_CCEE", "DATA_CALCULO", "DATA_RATING_AGENCIA"]
    
    for campo in campos_data:
        if campo not in df.columns: continue
        
        s = pd.to_datetime(df[campo], errors="coerce")
        
        fora_da_faixa = s.dropna()[~s.dropna().dt.year.between(1990, 2035)]
        qtd = len(fora_da_faixa)
        
        print(f"Campo: {campo}")
        print(f"  - Registros fora da faixa (serão barrados pela nova regra): {qtd}")
        if qtd > 0:
            print("  - Amostra das datas absurdas encontradas:")
            print(fora_da_faixa.head(5).dt.strftime("%Y-%m-%d").to_string(index=False))
        print("-" * 20)

if __name__ == "__main__":
    testar_hipotese_cluster()
```


---

## `scripts/valida_ajustes.py`

- Linhas: 56
- SHA-256: `d23d73d58b9bc22bde351f3c8fbd47566e4f5936cb3220285090ab546d272174`
- Classes: -
- Funções: validar_ajustes

```python
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

def validar_ajustes():
    caminho = Path(r"SAIDAS\silver\fichas_consumidores_extraidas")
    arquivos = list(caminho.glob("*.parquet"))
    
    if not arquivos:
        print("Arquivos parquet não encontrados em SAIDAS\\silver\\fichas_consumidores_extraidas.")
        return
        
    df = pd.concat([pd.read_parquet(f) for f in arquivos], ignore_index=True)
    
    print("\n" + "="*80)
    print(f"VALIDAÇÃO DE AJUSTES - CONSUMIDORES (Total: {len(df)} registros)")
    print("="*80)
    
    # 1. Validação do Padrão de Versão
    print("\n1. Distribuição da versão do layout:")
    col_v = "versao_ficha" if "versao_ficha" in df.columns else "versao_layout" if "versao_layout" in df.columns else None
    if col_v:
        print(df[col_v].value_counts(dropna=False))
    else:
        print(" [AVISO] Coluna de versão não encontrada.")

    # 2. Validação do Volume de Datas Extraídas
    if 'DATA_DEMONSTRACAO_FINANCEIRA' in df.columns:
        # Conta as datas válidas (excluindo nulos e 'NAO_APLICAVEL')
        mask_valida = df['DATA_DEMONSTRACAO_FINANCEIRA'].notnull() & (df['DATA_DEMONSTRACAO_FINANCEIRA'].astype(str).str.upper() != 'NAO_APLICAVEL')
        qtd_com_df = mask_valida.sum()
        print(f"\n2. Datas de DF Extraídas com Sucesso: {qtd_com_df} (Antes do ajuste era ~294)")
    else:
        print("\n2. [ERRO] Coluna DATA_DEMONSTRACAO_FINANCEIRA não encontrada!")

    # 3. Validação dos Falsos Zeros (Regra 14.8)
    print("\n3. Checagem de Falsos Zeros (Regra 14.8):")
    if 'DATA_DEMONSTRACAO_FINANCEIRA' in df.columns and 'LUCRO_LIQUIDO' in df.columns:
        sem_df = df[df['DATA_DEMONSTRACAO_FINANCEIRA'].isnull() | (df['DATA_DEMONSTRACAO_FINANCEIRA'].astype(str).str.upper() == 'NAO_APLICAVEL')]
        
        if sem_df.empty:
            print("  Nenhuma ficha sem DF encontrada para validar.")
        else:
            zeros_falsos = sem_df[sem_df['LUCRO_LIQUIDO'] == 0.0]
            if zeros_falsos.empty:
                print(f"  [SUCESSO] ZERO vazamentos encontrados. Todos os 0.0 falsos entre as {len(sem_df)} fichas sem DF foram anulados corretamente.")
            else:
                print(f"  [FALHA] Ainda vazaram {len(zeros_falsos)} falsos zeros! Ex CNPJs: {zeros_falsos['CNPJ'].head(3).tolist()}")
    else:
        print("  Colunas necessárias ausentes para validação da Regra 14.8.")

    print("\n" + "="*80)

if __name__ == "__main__":
    validar_ajustes()
```
