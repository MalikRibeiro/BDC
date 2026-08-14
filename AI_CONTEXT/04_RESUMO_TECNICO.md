# RESUMO TÉCNICO


## gerar_contexto_ia.py
Linhas: 146

Imports:
- ast
- pathlib
- shutil
- textwrap

Classes:

Funções:
- tree
- analyze


## main.py
Linhas: 198

Imports:
- app.bootstrap
- argparse
- cli
- datetime
- inspect
- pandas
- pathlib
- services.audit_service
- services.camada_gold_service
- services.carga_manual_service
- services.contratos_denodo_service
- services.dim_contraparte_service
- services.enquadramento_service
- services.fato_analise_credito_service
- services.garantias_service
- services.mtm_ingestion_service
- services.override_service
- services.pipeline_risco_service
- services.receita_ingestion_service
- services.reconciliacao_denodo_mtm_service
- services.reconciliacao_fichas_salesforce_service
- services.salesforce_ingestion_service
- sys
- traceback
- typing

Classes:
- PipelineStep

Funções:
- preparar_e_rodar_risco
- preparar_dim_contraparte
- preparar_fato_analise
- main

Docstring:
main.py

Orquestrador principal para executar os pipelines do projeto BDC em sequência.


## reset.py
Linhas: 126

Imports:
- __future__
- pathlib
- shutil

Classes:

Funções:
- clear_directory_contents
- clear_jsonl_files
- move_files_back_to_pending
- main

Docstring:
Utilitário simples para reiniciar o pipeline BDC e reprocessar as fichas.


## src\app\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Pacote de bootstrap e contexto da aplicação BDC.


## src\app\bootstrap.py
Linhas: 60

Imports:
- dotenv
- os
- pathlib
- src.app.context
- typing

Classes:

Funções:
- resolve_configs_dir
- bootstrap_application


## src\app\config_builder.py
Linhas: 17

Imports:
- pathlib
- typing

Classes:
- AppConfigBuilder

Funções:
- __init__
- resolve_dict

Docstring:
Builder programático para resolução de caminhos do sistema.


## src\app\context.py
Linhas: 96

Imports:
- __future__
- app.config_builder
- common.io_json
- common.validation
- dataclasses
- dotenv
- logging
- os
- pathlib
- sys
- typing

Classes:
- AppContext

Funções:
- load_context
- path
- control_file

Docstring:
Carregamento do contexto de execução do sistema BDC.


## src\cli\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Comandos de linha do sistema BDC.


## src\cli\run_discovery.py
Linhas: 57

Imports:
- app.bootstrap
- argparse
- pathlib
- services.network_discovery_service
- sys
- traceback

Classes:

Funções:
- build_parser
- main

Docstring:
CLI para disparar a varredura e triagem de fichas na rede corporativa.


## src\cli\run_fichas_comercializadoras.py
Linhas: 47

Imports:
- argparse
- pathlib
- src.app.bootstrap
- src.services.fichas_comercializadoras_service
- sys

Classes:

Funções:
- build_parser
- main


## src\cli\run_fichas_consumidores.py
Linhas: 47

Imports:
- argparse
- pathlib
- src.app.bootstrap
- src.services.fichas_consumidores_service
- sys

Classes:

Funções:
- build_parser
- main


## src\common\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Utilitários compartilhados do sistema BDC.


## src\common\dates.py
Linhas: 34

Imports:
- __future__
- datetime
- typing

Classes:

Funções:
- normalize_date

Docstring:
Normalização de datas no sistema BDC.


## src\common\excel.py
Linhas: 94

Imports:
- __future__
- openpyxl
- openpyxl.utils
- openpyxl.worksheet.worksheet
- pathlib
- re
- typing

Classes:

Funções:
- open_workbook
- close_workbook_safely
- read_cell
- normalize_label_text
- find_cell_by_regex

Docstring:
Operações de leitura e fechamento seguro de workbooks Excel.


## src\common\hashing.py
Linhas: 21

Imports:
- __future__
- hashlib
- pathlib

Classes:

Funções:
- hash_file

Docstring:
Geração de hash para arquivos do sistema BDC.


## src\common\io_json.py
Linhas: 14

Imports:
- __future__
- json
- pathlib
- typing

Classes:

Funções:
- read_json

Docstring:
Leitura e escrita de arquivos JSON do sistema BDC.


## src\common\logging_utils.py
Linhas: 34

Imports:
- __future__
- logging
- pathlib

Classes:

Funções:
- get_logger

Docstring:
Configuração padronizada de loggers do sistema BDC.


## src\common\paths.py
Linhas: 16

Imports:
- __future__
- re

Classes:

Funções:
- sanitize_folder_name

Docstring:
Funções utilitárias para nomes de paths e diretórios.


## src\common\strings.py
Linhas: 31

Imports:
- __future__
- re
- typing

Classes:

Funções:
- normalize_string
- normalize_cnpj

Docstring:
Normalização de textos e documentos no sistema BDC.


## src\common\types.py
Linhas: 20

Imports:
- __future__
- typing

Classes:

Funções:
- normalize_float

Docstring:
Conversões tipadas para valores numéricos do sistema BDC.


## src\common\validation.py
Linhas: 18

Imports:
- jsonschema
- jsonschema.exceptions
- logging
- sys
- typing

Classes:

Funções:
- validate_json_schema


## src\control\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Carregadores de arquivos de controle do sistema BDC.


## src\control\field_types.py
Linhas: 75

Imports:
- dataclasses
- typing

Classes:
- FieldTypeConfig

Funções:
- get_field_type_config

Docstring:
Definição programática e tipada dos domínios de campos (Substitui os JSONs legados).


## src\control\layout_catalog.py
Linhas: 128

Imports:
- __future__
- app.context
- common.io_json
- sys
- typing

Classes:

Funções:
- _validate_layout_structure
- load_layout_catalog
- load_layouts_comercializadoras
- load_layouts_consumidores

Docstring:
Carregamento e validação dos layouts de fichas.


## src\control\mapping_loader.py
Linhas: 75

Imports:
- __future__
- app.context
- common.io_json
- common.validation
- logging
- pathlib
- typing

Classes:

Funções:
- _load_and_validate_mapping
- load_mapping_fichas_comercializadoras
- load_mapping_fichas_consumidores

Docstring:
Carregamento e validação estrita dos mappings das fichas.


## src\control\quality_loader.py
Linhas: 73

Imports:
- __future__
- app.context
- common.io_json
- common.validation
- typing

Classes:

Funções:
- _load_and_validate_quality_rules
- load_data_quality_rules_comercializadoras
- load_data_quality_rules_consumidores

Docstring:
Carregamento e validação estrita das regras de qualidade da entidade.

feat(T1.1.2): Integra validação contra JSON Schema (mesmo padrão de mapping_loader.py).
Regras malformadas geram erro descritivo antes do processamento de qualquer ficha.
Ref: §5.2, §5.3 do Planejamento Funcional.


## src\domain\contrapartes\segmentacao.py
Linhas: 51

Imports:
- __future__
- common.strings
- common.types
- typing

Classes:

Funções:
- definir_segmento_metodologico

Docstring:
Segmentação metodológica da contraparte para cálculo de PD.


## src\domain\credito\ead_engine.py
Linhas: 64

Imports:
- __future__
- datetime
- hashlib
- json
- typing
- uuid

Classes:

Funções:
- calcular_ead

Docstring:
Motor de Exposure at Default (EAD).

feat(T3.2.1): Adicionados fator de conversão parametrizado e rastreabilidade
com calculo_id e config_snapshot_id.
Ref: §6.7 (Exposição), §7.1, §11.2 (Identificadores) do Planejamento Funcional.


## src\domain\credito\lgd_engine.py
Linhas: 90

Imports:
- __future__
- datetime
- hashlib
- json
- typing
- uuid

Classes:

Funções:
- calcular_lgd

Docstring:
Motor de Loss Given Default (LGD).

feat(T3.3.1): Adicionados lookup de LGD bruta por segmento via config e
rastreabilidade com calculo_id.
Ref: §6.8, §7.1, Apêndice C do Planejamento Funcional.

Nota: A redução por garantias é recebida como parâmetro (cobertura_garantias).
A integração com a base real de garantias é um TODO — quando disponível,
o percentual será calculado automaticamente a partir de garantias_service.


## src\domain\credito\notas_quantitativas_cpura.py
Linhas: 172

Imports:
- __future__
- common.types
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- _obter_valor_numerico
- _normalizar_pd
- _obter_faixas_notas
- _atribuir_nota_por_faixa
- calcular_notas_quantitativas_cpura

Docstring:
Cálculo das notas quantitativas de CPURA.


## src\domain\credito\pd_base.py
Linhas: 43

Imports:
- __future__
- common.types
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- calcular_pd_base

Docstring:
Cálculo ou leitura da PD base.


## src\domain\credito\pd_cgrupo.py
Linhas: 151

Imports:
- __future__
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- _norm
- _norm_agencia
- _norm_rating
- _mapear_rating_externo
- _resolver_rating_cgrupo
- _pior_rating
- _percentil_empirico
- _interpolar_pd
- calcular_pd_final_cgrupo


## src\domain\credito\pd_consumidor_gt5.py
Linhas: 121

Imports:
- __future__
- domain.credito.pd_exceptions
- math
- statistics
- typing

Classes:

Funções:
- _inv_t_approx
- _normalize_pd_input
- calcular_pd_final_consumidor_gt5

Docstring:
Transformação da PD para consumidores acima de 5 MWm.


## src\domain\credito\pd_consumidor_le5.py
Linhas: 75

Imports:
- __future__
- common.types
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- calcular_pd_final_consumidor_le5

Docstring:
Transformação da PD para consumidores abaixo de 5 MWm (Bureau).


## src\domain\credito\pd_cpura.py
Linhas: 282

Imports:
- __future__
- domain.credito.pd_exceptions
- math
- typing

Classes:

Funções:
- _clamp
- _obter_score_total
- _obter_faixa_score_rating
- _obter_estabilizacao
- _calcular_score_truncado
- _calcular_posicao_relativa
- _calcular_pd_bruta
- _estabilizar_pd
- calcular_pd_final_cpura

Docstring:
Transformação de PD para comercializadoras puras.


## src\domain\credito\pd_engine.py
Linhas: 164

Imports:
- __future__
- domain.credito.notas_quantitativas_cpura
- domain.credito.pd_base
- domain.credito.pd_exceptions
- domain.credito.pd_transform
- domain.credito.pd_validator
- domain.credito.rating
- domain.credito.score_qualitativo
- domain.credito.score_quantitativo
- domain.credito.score_total
- typing

Classes:

Funções:
- calcular_pd_ajustada

Docstring:
Orquestração do cálculo de PD ajustada.


## src\domain\credito\pd_exceptions.py
Linhas: 15

Imports:
- __future__

Classes:
- PdCalculationError
- PdInputValidationError
- PdConfigurationError

Funções:

Docstring:
Exceções do motor de probabilidade de default.


## src\domain\credito\pd_transform.py
Linhas: 173

Imports:
- __future__
- domain.credito.pd_cgrupo
- domain.credito.pd_consumidor_gt5
- domain.credito.pd_consumidor_le5
- domain.credito.pd_cpura
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- _obter_faixa_pd
- transformar_pd_por_segmento

Docstring:
Despacho da transformação de PD por segmento.


## src\domain\credito\pd_validator.py
Linhas: 105

Imports:
- __future__
- common.strings
- common.types
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- _is_blank
- validar_insumos_pd

Docstring:
Validação dos insumos do cálculo de PD ajustada.


## src\domain\credito\pe_engine.py
Linhas: 63

Imports:
- __future__
- datetime
- uuid

Classes:

Funções:
- calcular_perda_esperada

Docstring:
Motor de Perda Esperada (PE).

feat(T3.4.1): Retorno dual (pe_reais + pe_percentual) e rastreabilidade
com calculo_id.
Ref: §6.7, §11.2, §11.6 (Reconciliação PE) do Planejamento Funcional.


## src\domain\credito\rating.py
Linhas: 112

Imports:
- __future__
- common.strings
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- _calcular_rating_final_cpura
- _obter_rating_pronto
- calcular_rating_final

Docstring:
Determinação do rating final para o cálculo de PD ajustada.


## src\domain\credito\score_qualitativo.py
Linhas: 161

Imports:
- __future__
- common.strings
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- _obter_nota_auditoria
- _obter_peso_nota
- calcular_score_qualitativo_cpura

Docstring:
Cálculo do score qualitativo para CPURA.


## src\domain\credito\score_quantitativo.py
Linhas: 127

Imports:
- __future__
- common.strings
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- _obter_peso_nota
- calcular_score_quantitativo_cpura

Docstring:
Cálculo do score quantitativo para CPURA.


## src\domain\credito\score_total.py
Linhas: 50

Imports:
- __future__
- domain.credito.pd_exceptions
- typing

Classes:

Funções:
- calcular_score_total_cpura

Docstring:
Cálculo do score total de CPURA.


## src\domain\credito\taxa_risco_engine.py
Linhas: 79

Imports:
- __future__
- datetime
- logging
- typing
- uuid

Classes:

Funções:
- calcular_taxa_risco

Docstring:
Motor de Taxa de Risco de Crédito.

feat(T3.4.2): Cálculo de Taxa_Risco = PE_total / Notional_total.
Trata divisão por zero gerando alerta QLT_002.
Ref: §7.1, §8.3 (QLT_002), §11.6 do Planejamento Funcional.


## src\domain\enums.py
Linhas: 126

Imports:
- enum

Classes:
- TipoFicha
- LoadMode
- StatusIngestao
- StatusClassificacao
- StatusExtracao
- SegmentoMetodologico
- TipoAnalise
- SeveridadeAlerta
- StatusGarantia
- StatusAnalise
- StatusDocumento
- StatusAlerta
- StatusAprovacao

Funções:

Docstring:
Domínios controlados e enumeradores do sistema BDC.


## src\domain\garantias\garantia_model.py
Linhas: 27

Imports:
- dataclasses
- typing

Classes:
- GarantiaModel

Funções:

Docstring:
Modelo de dados formal para o domínio de Garantias.


## src\services\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Serviços de processamento do sistema BDC.


## src\services\audit_service.py
Linhas: 162

Imports:
- __future__
- datetime
- logging
- pandas
- pathlib
- storage.silver_store
- typing

Classes:

Funções:
- registrar_inicio_pipeline
- registrar_fim_pipeline
- registrar_documento
- registrar_linhagem_campos

Docstring:
Serviços de Auditoria do Pipeline (§11.5 — Tabelas de Controle).

Registra cada execução do pipeline (ctl_run_pipeline) e cada documento
processado (ctl_documento) em tabelas persistentes.


## src\services\camada_gold_service.py
Linhas: 145

Imports:
- __future__
- app.context
- datetime
- logging
- pandas
- pydot
- storage.silver_store

Classes:

Funções:
- _classificar_matriz_operacional
- exportar_visao_consolidada_gold

Docstring:
Construtor da Visão Operacional Consolidada (Camada Gold).


## src\services\carga_manual_service.py
Linhas: 85

Imports:
- __future__
- app.context
- common.io_json
- common.validation
- datetime
- logging
- pandas
- storage.silver_store
- typing

Classes:

Funções:
- ingest_carga_manual

Docstring:
Serviço de Carga Manual e Eventos de Negócio.

feat(T4.1.2): Serviço de ingestão de eventos de carga manual com garantia
de imutabilidade (append-only) e dupla temporalidade.
Ref: §4.3, §4.5 do Planejamento Funcional.


## src\services\contratos_denodo_service.py
Linhas: 131

Imports:
- __future__
- app.context
- datetime
- logging
- pandas
- pathlib
- services.denodo_connector
- storage.silver_store
- typing

Classes:

Funções:
- aplicar_regras_negocio_pandas
- ingest_contratos_denodo

Docstring:
Serviço oficial de ingestão de Contratos Correntes do Denodo.


## src\services\dedup_service.py
Linhas: 70

Imports:
- __future__
- datetime
- typing

Classes:

Funções:
- has_duplicate_hash
- has_duplicate_business_key
- upsert_business_key_in_history

Docstring:
Regras de deduplicação e atualização incremental do sistema.


## src\services\denodo_connector.py
Linhas: 144

Imports:
- __future__
- logging
- os
- pandas
- pathlib
- requests
- requests.auth
- time
- typing
- urllib3

Classes:
- DenodoConnectionError

Funções:
- _request_with_retry
- _find_latest_bronze_snapshot
- fetch_denodo_rest

Docstring:
Conector central para o virtualizador Denodo via API RESTful.

feat(T2.1.1): Adicionados retry com backoff exponencial e fallback para
último snapshot Bronze em caso de indisponibilidade.
Ref: §3.4 do Planejamento Funcional.


## src\services\dim_contraparte_service.py
Linhas: 42

Imports:
- __future__
- app.context
- datetime
- logging
- pandas
- storage.silver_store
- typing

Classes:

Funções:
- build_dim_contraparte

Docstring:
Construção da dimensão de Contrapartes (dim_contraparte).


## src\services\enquadramento_service.py
Linhas: 72

Imports:
- __future__
- app.context
- pandas
- pathlib
- typing

Classes:

Funções:
- calcular_enquadramento_consumidor

Docstring:
Serviço de cálculo do volume de enquadramento (≥ 5 MWm) para consumidores.


## src\services\fato_analise_credito_service.py
Linhas: 47

Imports:
- __future__
- app.context
- datetime
- logging
- pandas
- storage.silver_store
- typing

Classes:

Funções:
- build_fato_analise_credito

Docstring:
Construção da tabela Fato de Análise de Crédito (fato_analise_credito).


## src\services\ficha_classifier.py
Linhas: 200

Imports:
- __future__
- common.excel
- common.strings
- dataclasses
- openpyxl.worksheet.worksheet
- re
- typing

Classes:
- ClassificationResult

Funções:
- _normalize_label
- _find_label_by_regex
- _verify_field
- classify_workbook

Docstring:
Classificação de fichas conforme os layouts conhecidos.


## src\services\ficha_extractor.py
Linhas: 140

Imports:
- common.excel
- datetime
- openpyxl
- openpyxl.utils.datetime
- typing

Classes:

Funções:
- parse_date_safely
- extract_field_value
- extract_record

Docstring:
Serviço de extração de dados das fichas Excel.


## src\services\ficha_validator.py
Linhas: 123

Imports:
- __future__
- typing

Classes:
- DomainRuleEngine

Funções:
- _is_empty
- validate_record
- __init__
- validate

Docstring:
Validação técnica e de domínio unificada dos registros extraídos.


## src\services\fichas_comercializadoras_service.py
Linhas: 736

Imports:
- __future__
- app.context
- common.excel
- common.hashing
- common.io_json
- common.logging_utils
- common.paths
- common.strings
- control.layout_catalog
- control.mapping_loader
- control.quality_loader
- datetime
- domain.contrapartes.segmentacao
- domain.credito.pd_engine
- pathlib
- services.audit_service
- services.dedup_service
- services.ficha_classifier
- services.ficha_extractor
- services.ficha_validator
- silver.documentos_classificados
- silver.field_type_normalizer
- staging.discovery
- staging.staging_writer
- storage.bronze_store
- storage.file_ops
- storage.manifest_store
- storage.silver_store
- storage.state_store
- typing
- uuid

Classes:

Funções:
- is_valid_cnpj
- _is_disk_full_error
- _build_run_id
- _build_target_name
- _resolve_bronze_subfolder
- _move_to_rejected
- _move_to_processed
- _build_pd_info
- _build_processing_queue
- _process_single_file
- process_fichas_comercializadoras
- calc_digit

Docstring:
Serviço principal refatorado do pipeline de fichas de comercializadoras.


## src\services\fichas_consumidores_service.py
Linhas: 689

Imports:
- __future__
- app.context
- common.excel
- common.hashing
- common.io_json
- common.logging_utils
- common.paths
- common.strings
- control.layout_catalog
- control.mapping_loader
- control.quality_loader
- datetime
- domain.contrapartes.segmentacao
- domain.credito.pd_engine
- pathlib
- services.audit_service
- services.dedup_service
- services.ficha_classifier
- services.ficha_extractor
- services.ficha_validator
- silver.documentos_classificados
- silver.field_type_normalizer
- staging.discovery
- staging.staging_writer
- storage.bronze_store
- storage.file_ops
- storage.manifest_store
- storage.silver_store
- storage.state_store
- typing
- uuid

Classes:

Funções:
- is_valid_cnpj
- _is_disk_full_error
- _build_run_id
- _build_target_name
- _resolve_bronze_subfolder
- _move_to_rejected
- _move_to_processed
- _build_pd_info
- _build_processing_queue
- _process_single_file
- process_fichas_consumidores
- calc_digit

Docstring:
Serviço principal refatorado do pipeline de fichas de consumidores.


## src\services\garantias_service.py
Linhas: 178

Imports:
- __future__
- app.context
- common.logging_utils
- datetime
- domain.enums
- pandas
- pathlib
- shutil
- storage.silver_store
- typing

Classes:
- GarantiaIngestionError

Funções:
- ingest_garantias_data

Docstring:
Serviço de ingestão, validação e alertas de Garantias.

Lê o CSV extraído da query customizada do Denodo, salva na Bronze,
valida regras de vigência e cobertura, gera alertas e publica na Silver.
Ref: §2 (Módulo Garantias), §6.8 do Planejamento Funcional.


## src\services\mtm_connector.py
Linhas: 70

Imports:
- __future__
- datetime
- pandas
- pathlib
- typing

Classes:
- MtmConnectionError

Funções:
- _encontrar_arquivo_mtm_recente
- fetch_mtm_consolidado

Docstring:
Conector de integração com a base de MtM (Risco de Mercado).


## src\services\mtm_ingestion_service.py
Linhas: 130

Imports:
- __future__
- app.context
- common.logging_utils
- datetime
- pandas
- services.mtm_connector
- shutil
- storage.silver_store
- typing

Classes:
- MtmReconciliationError

Funções:
- ingest_mtm_data

Docstring:
Serviço de ingestão e agregação da base de MtM para as camadas Bronze e Silver.

fix(T2.2.2): Removida lógica duplicada (leitura antiga via MTM_NETWORK_PATH
que salvava Bronze duas vezes). Mantido apenas o fluxo via mtm_connector.
Ref: §3.5, §11.6 do Planejamento Funcional.


## src\services\network_discovery_service.py
Linhas: 188

Imports:
- __future__
- app.context
- common.excel
- common.logging_utils
- control.layout_catalog
- datetime
- logging
- pandas
- pathlib
- services.ficha_classifier
- shutil
- typing

Classes:
- NetworkDiscoveryError

Funções:
- _obter_assinaturas_locais
- run_network_discovery

Docstring:
Serviço de Coleta na Rede e Triagem Automática de Fichas de Crédito.


## src\services\override_service.py
Linhas: 79

Imports:
- __future__
- app.context
- datetime
- domain.enums
- logging
- pandas
- storage.silver_store
- typing

Classes:

Funções:
- processar_solicitacao_override

Docstring:
Serviço de Gestão de Overrides e Exceções (Módulo de Governança).

feat(T4.2.1): Serviço para aplicar, aprovar e monitorar vigência de Overrides.
Ref: §11.7 do Planejamento Funcional.


## src\services\pipeline_risco_service.py
Linhas: 108

Imports:
- __future__
- app.context
- common.logging_utils
- datetime
- domain.credito.ead_engine
- domain.credito.lgd_engine
- domain.credito.pe_engine
- domain.credito.taxa_risco_engine
- logging
- pandas
- storage.silver_store
- typing

Classes:

Funções:
- run_pipeline_risco

Docstring:
Orquestrador do Pipeline de Risco de Crédito.


## src\services\receita_connector.py
Linhas: 117

Imports:
- __future__
- app.context
- datetime
- json
- logging
- pandas
- pathlib
- requests
- time
- typing
- urllib3

Classes:

Funções:
- normalizar_cnpj
- _cache_path
- _load_cache
- _save_cache
- _is_same_day_cache
- fetch_receita_data_batch

Docstring:
Conector e cache da BrasilAPI para consulta cadastral de Receita Federal.


## src\services\receita_ingestion_service.py
Linhas: 130

Imports:
- __future__
- app.context
- datetime
- domain.enums
- json
- logging
- pandas
- pathlib
- re
- services.receita_connector
- shutil
- storage.silver_store
- typing

Classes:
- ReceitaIngestionError

Funções:
- _listar_cnpjs_de_entrada
- _save_raw_snapshot
- ingest_receita_data

Docstring:
Serviço de ingestão e validação cadastral da Receita Federal.


## src\services\reconciliacao_denodo_mtm_service.py
Linhas: 144

Imports:
- __future__
- app.context
- common.logging_utils
- datetime
- domain.enums
- numpy
- pandas
- storage.silver_store
- typing

Classes:
- ReconciliacaoDataError

Funções:
- executar_reconciliacao_denodo_mtm

Docstring:
Serviço de reconciliação entre contratos do Denodo e posições consolidadas de MtM.


## src\services\reconciliacao_fichas_salesforce_service.py
Linhas: 124

Imports:
- __future__
- app.context
- datetime
- logging
- pandas
- storage.silver_store
- typing

Classes:

Funções:
- executar_reconciliacao_fichas_salesforce

Docstring:
Serviço de Reconciliação: Fichas de Crédito vs Salesforce.
Verifica se todas as contrapartes com ficha de crédito estão devidamente cadastradas no CRM.


## src\services\salesforce_connector.py
Linhas: 74

Imports:
- __future__
- pandas
- pathlib
- typing

Classes:
- SalesforceConnectionError

Funções:
- fetch_salesforce_data

Docstring:
Conector de integração de arquivos extraídos do Salesforce (via Power Query).


## src\services\salesforce_ingestion_service.py
Linhas: 134

Imports:
- __future__
- app.context
- common.logging_utils
- datetime
- pandas
- services.salesforce_connector
- shutil
- storage.silver_store
- typing

Classes:
- SalesforceIngestionError

Funções:
- ingest_salesforce_data
- enriquecer_com_cnpj

Docstring:
Serviço de ingestão e normalização da base do Salesforce.


## src\silver\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Camada silver do sistema BDC.


## src\silver\documentos_classificados.py
Linhas: 24

Imports:
- __future__

Classes:

Funções:
- build_classified_document

Docstring:
Builders da camada silver para documentos classificados.


## src\silver\field_type_normalizer.py
Linhas: 136

Imports:
- __future__
- app.context
- common.dates
- common.io_json
- common.strings
- common.types
- control.field_types
- datetime
- re
- typing

Classes:

Funções:
- _get_fields
- normalize_data_demonstracao_financeira
- normalize_record

Docstring:
Normalização técnica das fichas.


## src\staging\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Camada de staging do sistema BDC.


## src\staging\discovery.py
Linhas: 18

Imports:
- __future__
- pathlib

Classes:

Funções:
- discover_pending_excels

Docstring:
Descoberta de arquivos pendentes para processamento.


## src\staging\staging_writer.py
Linhas: 21

Imports:
- __future__
- pathlib
- shutil

Classes:

Funções:
- copy_to_staging

Docstring:
Cópia de arquivos para a área de staging do sistema.


## src\storage\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Camada de persistência física do sistema BDC.


## src\storage\bronze_store.py
Linhas: 20

Imports:
- __future__
- pathlib
- shutil

Classes:

Funções:
- publish_raw_file

Docstring:
Publicação de arquivos válidos na camada bronze.


## src\storage\file_ops.py
Linhas: 34

Imports:
- __future__
- pathlib
- shutil
- time

Classes:

Funções:
- move_file_with_retry

Docstring:
Operações robustas de arquivo para ambiente Windows.


## src\storage\manifest_store.py
Linhas: 39

Imports:
- __future__
- json
- pathlib
- typing

Classes:

Funções:
- append_manifest_record
- load_ingestion_history

Docstring:
Persistência do manifest de ingestão em formato JSONL.


## src\storage\silver_store.py
Linhas: 136

Imports:
- pandas
- pathlib
- typing

Classes:

Funções:
- _normalize_filename
- write_silver_dataset
- merge_silver_dataset_by_business_key

Docstring:
Persistência de datasets padronizados da camada silver.


## src\storage\state_store.py
Linhas: 72

Imports:
- __future__
- dataclasses
- domain.enums
- typing

Classes:
- DocumentManifest

Funções:
- __post_init__
- to_dict

Docstring:
Estruturas de estado e manifesto do processamento.


## src\tests\test_context.py
Linhas: 131

Imports:
- app.context
- json
- pathlib
- pytest
- sys

Classes:

Funções:
- setup_env
- test_cenario_1_sucesso
- test_cenario_2_diretorio_inexistente
- test_cenario_3_arquivo_config_ausente
- test_cenario_4_control_files_ausente
- test_cenario_5_schema_nao_encontrado_no_disco
- test_cenario_6_schema_invalido_campo_ausente
- test_cenario_7_schema_invalido_tipo_errado


## src\tests\test_denodo_connector.py
Linhas: 27

Imports:
- pandas
- pathlib
- pytest
- services.denodo_connector
- sys

Classes:

Funções:
- test_t211_leitura_denodo_local


## src\tests\test_domain_rule_engine.py
Linhas: 43

Imports:
- logging
- pathlib
- pytest
- services.ficha_validator
- sys

Classes:

Funções:
- test_t132_engine_com_regras_dinamicas
- test_t132_engine_fallback_nativo


## src\tests\test_dynamic_paths.py
Linhas: 26

Imports:
- app.config_builder
- pathlib
- pytest
- sys

Classes:

Funções:
- test_config_builder_sem_json_t122


## src\tests\test_enquadramento.py
Linhas: 42

Imports:
- pandas
- pathlib
- pytest
- services.enquadramento_service
- sys

Classes:
- MockContext

Funções:
- test_t213_calculo_volume_enquadramento
- path


## src\tests\test_enums.py
Linhas: 36

Imports:
- pathlib
- pytest
- storage.state_store
- sys

Classes:

Funções:
- test_t133_rejeicao_valor_fora_do_dominio
- test_t133_conversao_string_valida_para_enum


## src\tests\test_field_type_normalizer.py
Linhas: 71

Imports:
- json
- logging
- pathlib
- pytest
- silver.field_type_normalizer
- sys

Classes:
- MockContext

Funções:
- mock_context
- test_t131_normalizer_using_python_class
- test_t131_normalizer_fallback_json
- control_file


## src\tests\test_layout_catalog.py
Linhas: 46

Imports:
- control.layout_catalog
- logging
- pathlib
- pytest
- sys

Classes:

Funções:
- test_cenario_1_layout_valido
- test_cenario_2_layout_sem_field_map
- test_cenario_3_layout_com_campo_vazio


## src\tests\test_mtm_connector.py
Linhas: 46

Imports:
- pandas
- pathlib
- pytest
- services.mtm_connector
- sys

Classes:

Funções:
- test_t221_leitura_mtm_local


## src\tests\test_mtm_ingestion.py
Linhas: 135

Imports:
- pandas
- pathlib
- pytest
- services.mtm_ingestion_service
- sys

Classes:
- MockContext

Funções:
- mock_context_factory
- test_t222_ingestao_e_reconciliacao_mtm_sucesso
- test_t222_falha_reconciliacao_mtm
- _create_mock_context
- __init__
- path


## src\tests\test_pd_consumidor_le5.py
Linhas: 33

Imports:
- domain.credito.pd_consumidor_le5
- pathlib
- pytest
- sys

Classes:

Funções:
- test_t142_calculo_pd_bureau_sem_restritivo
- test_t142_calculo_pd_bureau_com_restritivo


## src\tests\test_receita_ingestion.py
Linhas: 133

Imports:
- json
- pandas
- pathlib
- pytest
- services.receita_connector
- services.receita_ingestion_service
- sys

Classes:
- MockContext
- DummyResponse

Funções:
- _write_cnpj_list_file
- test_consulta_brasilapi_sucesso
- test_cache_local_receita
- test_geracao_alerta_cad001
- __init__
- path
- fake_get
- fake_get
- __init__
- json


## src\tests\test_reconciliacao_denodo_mtm.py
Linhas: 97

Imports:
- pandas
- pathlib
- pytest
- services.reconciliacao_denodo_mtm_service
- sys

Classes:
- MockContext

Funções:
- test_t223_reconciliacao_denodo_mtm_cenarios_completos
- path


## src\tests\test_reconciliacao_fichas_salesforce.py
Linhas: 78

Imports:
- pandas
- pathlib
- pytest
- services.reconciliacao_fichas_salesforce_service
- sys

Classes:
- MockContext

Funções:
- test_t232_reconciliacao_fichas_salesforce_cenarios
- path


## src\tests\test_salesforce_ingestion.py
Linhas: 107

Imports:
- pandas
- pathlib
- pytest
- services.salesforce_ingestion_service
- sys

Classes:
- MockContext

Funções:
- mock_context
- criar_mock_excel_salesforce
- test_t232_ingestao_salesforce_sucesso
- test_t232_ingestao_salesforce_arquivo_inexistente
- path
