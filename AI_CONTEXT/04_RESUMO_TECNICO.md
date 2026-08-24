# RESUMO TÉCNICO


## 0_obter_e_triar.py
Linhas: 516

Imports:
- __future__
- app.context
- common
- control.layout_catalog
- datetime
- domain.fichas.classificador
- logging
- pandas
- pathlib
- shutil
- sys
- warnings

Classes:

Funções:
- criar_pastas
- gerar_assinatura
- obter_assinaturas_locais
- copiar_sem_sobrescrever
- main

Docstring:
RPA Unificado: Coleta na Rede e Triagem Automática de Fichas de Crédito.


## app_dashboard.py
Linhas: 75

Imports:
- pandas
- pathlib
- streamlit

Classes:

Funções:


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
Linhas: 220

Imports:
- app.bootstrap
- argparse
- cli
- datetime
- domain.auditoria.servico_auditoria
- domain.cadastro.servico_bureau
- domain.cadastro.servico_receita
- domain.carga_manual.servico_carga_manual
- domain.contrapartes.servico_dim_contraparte
- domain.contrapartes.servico_enquadramento
- domain.contratos.servico_contratos_denodo
- domain.credito.servico_fato_analise_credito
- domain.credito.servico_override
- domain.credito.servico_risco
- domain.garantias.servico_garantia
- domain.mtm.servico_denodo_mtm_reconciliacao
- domain.mtm.servico_mtm
- domain.salesforce.servico_salesforce
- domain.salesforce.servico_salesforce_reconciliacao
- gold.service_gold
- inspect
- pandas
- pathlib
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
- aplicativo_bootstrap


## src\app\comercializadoras\orquestrador.py
Linhas: 768

Imports:
- __future__
- app.context
- common.domain_normalizer
- common.excel
- common.hashing
- common.json
- common.paths
- common.servico_desduplicacao
- control.carregador_de_mapeamento
- control.layout_catalog
- control.logger
- datetime
- domain.auditoria.servico_auditoria
- domain.contrapartes.segmentacao
- domain.credito.pd_motor
- domain.fichas.derivador_financeiro
- domain.fichas.extrator
- domain.fichas.validador
- pathlib
- silver.documentos_classificados
- silver.normalizador_de_tipo_de_campo
- silver.normalizadores
- staging.descoberta
- staging.staging_arquivo
- storage.armazenamento_manifest
- storage.bronze_arquivo
- storage.escrever_dados
- storage.estado_armazenamento
- storage.operacao_arquivo
- typing
- uuid

Classes:

Funções:
- disco_cheio_erro
- criar_run_id
- criar_nome_arquivo
- resolver_subpasta_bronze
- mover_para_rejeitados
- mover_para_processados
- criar_info_pd
- criar_fila_processamento
- processar_arquivo_individual
- process_fichas_comercializadoras

Docstring:
Serviço principal refatorado do pipeline de fichas de comercializadoras.


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


## src\app\consumidores\classificacao.py
Linhas: 188

Imports:
- __future__
- dataclasses
- typing

Classes:
- ClassificacaoDocumental

Funções:
- _esta_vazio
- _tem_demonstracoes_financeiras
- _avaliar_confianca
- classificar_consumidor
- criar_classificacao_registro

Docstring:
Serviço de classificação documental de consumidores.

Determina o tipo de análise exigida (detalhada ou simplificada)
com base no volume contratado, conforme planejamento v1.2.


## src\app\consumidores\orquestrador.py
Linhas: 709

Imports:
- __future__
- app.consumidores.classificacao
- app.context
- common.domain_normalizer
- common.excel
- common.hashing
- common.json
- common.paths
- common.servico_desduplicacao
- control.carregador_de_mapeamento
- control.layout_catalog
- control.logger
- control.quality_loader
- datetime
- domain.contrapartes.segmentacao
- domain.credito.pd_motor
- domain.fichas.extrator
- domain.fichas.validador
- pathlib
- silver.documentos_classificados
- silver.normalizador_de_tipo_de_campo
- silver.normalizadores
- staging.descoberta
- staging.staging_arquivo
- storage.armazenamento_manifest
- storage.bronze_arquivo
- storage.escrever_dados
- storage.estado_armazenamento
- storage.operacao_arquivo
- typing
- uuid

Classes:

Funções:
- disco_cheio_erro
- criar_run_id
- criar_alvo_nome
- resolver_subpasta_bronze
- mover_para_rejeitados
- mover_para_processados
- criar_info_pd
- criar_fila_processamento
- processar_arquivo_individual
- processar_fichas_consumidores

Docstring:
Serviço principal refatorado do pipeline de fichas de consumidores.


## src\app\context.py
Linhas: 96

Imports:
- __future__
- app.config_builder
- common.json
- common.validador
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
- carregar_contexto
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


## src\cli\rodar_fichas_comercializadoras.py
Linhas: 47

Imports:
- argparse
- pathlib
- src.app.bootstrap
- src.app.comercializadoras.orquestrador
- sys

Classes:

Funções:
- criar_analisador
- main


## src\cli\rodar_fichas_consumidores.py
Linhas: 47

Imports:
- argparse
- pathlib
- src.app.bootstrap
- src.app.consumidores.orquestrador
- sys

Classes:

Funções:
- criar_analisador
- main


## src\common\__init__.py
Linhas: 1

Imports:

Classes:

Funções:


## src\common\domain_normalizer.py
Linhas: 84

Imports:
- __future__
- app.context
- common.json
- logging
- typing

Classes:

Funções:
- carregar_dicionarios_de_dominio
- _normalizar_string_por_dicionario
- aplicar_normalizacao_de_dominio

Docstring:
Normalizador Semântico de Domínio.

Aplica padronização de valores baseado em dicionários de negócios unificados,
garantindo que strings equivalentes (ex: 'FITCH RATINGS' e 'FITCH') convirjam 
para a mesma chave primária definida pela área de risco.


## src\common\excel.py
Linhas: 87

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
- abrir_pasta
- fechar_pasta
- ler_celula
- localizar_celula_por_regex

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
- arquivo_hash

Docstring:
Geração de hash para arquivos do sistema BDC.


## src\common\json.py
Linhas: 14

Imports:
- __future__
- json
- pathlib
- typing

Classes:

Funções:
- ler_json

Docstring:
Leitura e escrita de arquivos JSON do sistema BDC.


## src\common\paths.py
Linhas: 16

Imports:
- __future__
- re

Classes:

Funções:
- sanitizar_nome_da_pasta

Docstring:
Funções utilitárias para nomes de paths e diretórios.


## src\common\servico_desduplicacao.py
Linhas: 70

Imports:
- __future__
- datetime
- typing

Classes:

Funções:
- tem_hash_duplicado
- tem_chave_de_negocio_duplicada
- virar_chave_de_negocio_no_historico

Docstring:
Regras de deduplicação e atualização incremental do sistema.


## src\common\validador.py
Linhas: 18

Imports:
- jsonschema
- jsonschema.exceptions
- logging
- sys
- typing

Classes:

Funções:
- validar_esquema_json


## src\control\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Carregadores de arquivos de controle do sistema BDC.


## src\control\carregador_de_mapeamento.py
Linhas: 75

Imports:
- __future__
- app.context
- common.json
- common.validador
- logging
- pathlib
- typing

Classes:

Funções:
- carregar_e_validar_mapeamento
- mapeamento_de_carga_fichas_comercializadoras
- mapeamento_de_carga_fichas_consumidores

Docstring:
Carregamento e validação estrita dos mappings das fichas.


## src\control\field_types.py
Linhas: 50

Imports:
- dataclasses
- typing

Classes:
- FieldTypeConfig

Funções:
- obter_config_tipo_campo

Docstring:
Definição programática e tipada dos domínios de campos (Substitui os JSONs legados).


## src\control\layout_catalog.py
Linhas: 128

Imports:
- __future__
- app.context
- common.json
- sys
- typing

Classes:

Funções:
- validar_estrutura_do_layout
- carregar_catalogo_de_layouts
- carregar_layouts_comercializadoras
- carregar_layouts_consumidores

Docstring:
Carregamento e validação dos layouts de fichas.


## src\control\logger.py
Linhas: 34

Imports:
- __future__
- logging
- pathlib

Classes:

Funções:
- obter_logger

Docstring:
Configuração padronizada de loggers do sistema BDC.


## src\control\quality_loader.py
Linhas: 71

Imports:
- __future__
- app.context
- common.json
- common.validador
- pathlib
- typing

Classes:

Funções:
- _carregar_e_validar_regras_de_qualidade
- carregar_regras_de_qualidade_de_dados_comercializadoras
- carregar_regras_de_qualidade_de_dados_consumidores

Docstring:
Carregamento e validação estrita das regras de qualidade da entidade.

feat(T1.1.2): Integra validação contra JSON Schema (mesmo padrão de mapping_loader.py).
Regras malformadas geram erro descritivo antes do processamento de qualquer ficha.
Ref: §5.2, §5.3 do Planejamento Funcional.


## src\domain\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\domain\auditoria\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\domain\auditoria\servico_auditoria.py
Linhas: 162

Imports:
- __future__
- datetime
- logging
- pandas
- pathlib
- storage.escrever_dados
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


## src\domain\cadastro\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\domain\cadastro\servico_bureau.py
Linhas: 69

Imports:
- __future__
- app.context
- datetime
- logging
- pandas
- services.connectors.risk3_connector
- storage.escrever_dados
- typing

Classes:

Funções:
- inserir_dados_bureau

Docstring:
Serviço de Ingestão e Persistência do Bureau RISK3.


## src\domain\cadastro\servico_receita.py
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
- services.connectors.receita_connector
- shutil
- storage.escrever_dados
- typing

Classes:
- ReceitaIngestionError

Funções:
- _listar_cnpjs_de_entrada
- _salvar_instantaneo_bruto
- inserir_dados_receita

Docstring:
Serviço de ingestão e validação cadastral da Receita Federal.


## src\domain\carga_manual\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\domain\carga_manual\servico_carga_manual.py
Linhas: 75

Imports:
- __future__
- app.context
- common.json
- common.validador
- datetime
- logging
- pandas
- pathlib
- storage.escrever_dados
- typing

Classes:

Funções:
- inserir_dados_carga_manual

Docstring:
Serviço de Carga Manual e Eventos de Negócio.


## src\domain\contrapartes\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\domain\contrapartes\segmentacao.py
Linhas: 50

Imports:
- __future__
- silver.normalizadores
- typing

Classes:

Funções:
- definir_segmento_metodologico

Docstring:
Segmentação metodológica da contraparte para cálculo de PD.


## src\domain\contrapartes\servico_dim_contraparte.py
Linhas: 87

Imports:
- __future__
- app.context
- datetime
- logging
- pandas
- storage.escrever_dados
- typing

Classes:

Funções:
- criar_dim_contraparte

Docstring:
Serviço de consolidação da Dimensão de Contraparte.


## src\domain\contrapartes\servico_enquadramento.py
Linhas: 173

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


## src\domain\contratos\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\domain\contratos\servico_contratos_denodo.py
Linhas: 171

Imports:
- __future__
- app.context
- calendar
- datetime
- logging
- pandas
- pathlib
- services.connectors.denodo_connector
- silver.normalizadores
- storage.escrever_dados
- typing

Classes:

Funções:
- aplicar_regras_negocio_pandas
- processar_contratos_denodo
- calcular_horas

Docstring:
Serviço oficial de ingestão de Contratos Correntes do Denodo.


## src\domain\credito\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


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
Linhas: 170

Imports:
- __future__
- domain.credito.pd_exceptions
- silver.normalizadores
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
- domain.credito.pd_exceptions
- silver.normalizadores
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
- _inv_t_aproximado
- _normalize_pd_input
- calcular_pd_final_consumidor_gt5

Docstring:
Transformação da PD para consumidores acima de 5 MWm.


## src\domain\credito\pd_consumidor_le5.py
Linhas: 75

Imports:
- __future__
- domain.credito.pd_exceptions
- silver.normalizadores
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


## src\domain\credito\pd_motor.py
Linhas: 161

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
Linhas: 104

Imports:
- __future__
- domain.credito.pd_exceptions
- silver.normalizadores
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
- domain.credito.pd_exceptions
- silver.normalizadores
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
- domain.credito.pd_exceptions
- silver.normalizadores
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
- domain.credito.pd_exceptions
- silver.normalizadores
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


## src\domain\credito\servico_fato_analise_credito.py
Linhas: 53

Imports:
- __future__
- app.context
- datetime
- logging
- pandas
- storage.escrever_dados
- typing

Classes:

Funções:
- construir_fato_analise_credito

Docstring:
Construção da tabela Fato de Análise de Crédito (fato_analise_credito).


## src\domain\credito\servico_override.py
Linhas: 88

Imports:
- __future__
- app.context
- datetime
- domain.enums
- logging
- pandas
- storage.escrever_dados
- typing

Classes:

Funções:
- processar_solicitacao_override

Docstring:
Serviço de Gestão de Overrides e Exceções (Módulo de Governança).


## src\domain\credito\servico_risco.py
Linhas: 124

Imports:
- __future__
- app.context
- control.logger
- datetime
- domain.credito.ead_engine
- domain.credito.lgd_engine
- domain.credito.pe_engine
- domain.credito.taxa_risco_engine
- logging
- pandas
- storage.escrever_dados
- typing

Classes:

Funções:
- rodar_pipeline_risco

Docstring:
Orquestrador do Pipeline de Risco de Crédito.


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


## src\domain\fichas\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\domain\fichas\classificador.py
Linhas: 196

Imports:
- __future__
- common.excel
- dataclasses
- openpyxl.worksheet.worksheet
- re
- silver.normalizadores
- typing

Classes:
- ClassificationResult

Funções:
- normalizar_rotulo
- localizar_celula_por_regex
- verificar_label
- classificar_pasta_de_trabalho

Docstring:
Classificação de fichas conforme os layouts conhecidos.


## src\domain\fichas\derivador_financeiro.py
Linhas: 74

Imports:
- logging

Classes:

Funções:
- divisao_segura
- calcular_indicadores_derivados


## src\domain\fichas\extrator.py
Linhas: 505

Imports:
- __future__
- common.excel
- datetime
- logging
- math
- openpyxl
- openpyxl.utils
- openpyxl.utils.datetime
- openpyxl.worksheet.worksheet
- re
- silver.normalizadores
- typing
- warnings

Classes:

Funções:
- analisar_data_com_seguranca
- valor_extraido_limpo
- _tipo_extraido_valido
- busca_omnidirecional
- extrair_registro
- extrair_registro_do_vencedor
- norm_tab

Docstring:
Serviço de extração de dados dinâmico e omnidirecional das fichas Excel.


## src\domain\fichas\ficha_extractor.py
Linhas: 424

Imports:
- __future__
- common.excel
- datetime
- logging
- math
- openpyxl
- openpyxl.utils
- openpyxl.utils.datetime
- openpyxl.worksheet.worksheet
- re
- silver.normalizadores
- typing

Classes:

Funções:
- analisar_data_com_seguranca
- valor_extraido_limpo
- _tipo_extraido_valido
- busca_omnidirecional
- extrair_registro
- extrair_registro_do_vencedor
- norm_tab

Docstring:
Serviço de extração de dados dinâmico e omnidirecional das fichas Excel.


## src\domain\fichas\validador.py
Linhas: 242

Imports:
- __future__
- typing

Classes:
- DomainRuleEngine

Funções:
- _is_empty
- validar_registro
- validar_registro_consumidor
- __init__
- validate

Docstring:
Validação técnica e de domínio unificada dos registros extraídos.


## src\domain\garantias\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


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


## src\domain\garantias\servico_garantia.py
Linhas: 178

Imports:
- __future__
- app.context
- control.logger
- datetime
- domain.enums
- pandas
- pathlib
- shutil
- storage.escrever_dados
- typing

Classes:
- GarantiaIngestionError

Funções:
- inserir_dados_garantias

Docstring:
Serviço de ingestão, validação e alertas de Garantias.

Lê o CSV extraído da query customizada do Denodo, salva na Bronze,
valida regras de vigência e cobertura, gera alertas e publica na Silver.
Ref: §2 (Módulo Garantias), §6.8 do Planejamento Funcional.


## src\domain\mtm\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\domain\mtm\servico_denodo_mtm_reconciliacao.py
Linhas: 144

Imports:
- __future__
- app.context
- control.logger
- datetime
- domain.enums
- numpy
- pandas
- storage.escrever_dados
- typing

Classes:
- ReconciliacaoDataError

Funções:
- executar_reconciliacao_denodo_mtm

Docstring:
Serviço de reconciliação entre contratos do Denodo e posições consolidadas de MtM.


## src\domain\mtm\servico_mtm.py
Linhas: 142

Imports:
- __future__
- app.context
- control.logger
- datetime
- pandas
- services.connectors.mtm_connector
- shutil
- storage.escrever_dados
- typing

Classes:
- MtmReconciliationError

Funções:
- inserir_dados_mtm

Docstring:
Serviço de ingestão e agregação da base de MtM para as camadas Bronze e Silver.

fix(T2.2.2): Removida lógica duplicada (leitura antiga via MTM_NETWORK_PATH
que salvava Bronze duas vezes). Mantido apenas o fluxo via mtm_connector.
Ref: §3.5, §11.6 do Planejamento Funcional.


## src\domain\salesforce\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\domain\salesforce\servico_salesforce.py
Linhas: 134

Imports:
- __future__
- app.context
- control.logger
- datetime
- pandas
- services.connectors.salesforce_connector
- shutil
- storage.escrever_dados
- typing

Classes:
- SalesforceIngestionError

Funções:
- inserir_dados_salesforce
- enriquecer_com_cnpj

Docstring:
Serviço de ingestão e normalização da base do Salesforce.


## src\domain\salesforce\servico_salesforce_reconciliacao.py
Linhas: 124

Imports:
- __future__
- app.context
- datetime
- logging
- pandas
- storage.escrever_dados
- typing

Classes:

Funções:
- executar_reconciliacao_fichas_salesforce

Docstring:
Serviço de Reconciliação: Fichas de Crédito vs Salesforce.
Verifica se todas as contrapartes com ficha de crédito estão devidamente cadastradas no CRM.


## src\gold\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\gold\service_gold.py
Linhas: 347

Imports:
- datetime
- logging
- pandas
- pathlib
- silver.normalizadores
- typing

Classes:

Funções:
- exportar_visao_consolidada_gold
- resolver_situacao_df
- resolver_situacao_analise
- classificar_exigencia
- status_metodologia

Docstring:
Serviço da Camada Gold.
Responsável por realizar o Master Join entre Contratos (Denodo), Fichas (Análise), Risco (MtM), e Cadastro.
Aplica as agregações mensais de volume e regras de negócio temporais para criar a Tabela Analítica Oficial.


## src\relational\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\services\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Serviços de processamento do sistema BDC.


## src\services\connectors\__init__.py
Linhas: 0

Imports:

Classes:

Funções:


## src\services\connectors\denodo_connector.py
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
- _solicitacao_com_tentativa
- _encontrar_arquivo_bronze_recente
- buscar_denodo

Docstring:
Conector central para o virtualizador Denodo via API RESTful.

feat(T2.1.1): Adicionados retry com backoff exponencial e fallback para
último snapshot Bronze em caso de indisponibilidade.
Ref: §3.4 do Planejamento Funcional.


## src\services\connectors\mtm_connector.py
Linhas: 84

Imports:
- __future__
- datetime
- pandas
- pathlib
- silver.normalizadores
- typing

Classes:
- MtmConnectionError

Funções:
- _encontrar_arquivo_mtm_recente
- buscar_mtm_consolidado

Docstring:
Conector de integração com a base de MtM (Risco de Mercado).


## src\services\connectors\receita_connector.py
Linhas: 181

Imports:
- __future__
- app.context
- datetime
- json
- logging
- pandas
- pathlib
- requests
- silver.normalizadores
- time
- typing
- urllib3

Classes:

Funções:
- _cache_path
- _load_cache
- _save_cache
- _is_same_day_cache
- _consultar_cnpj_brasilapi
- buscar_receita_dados_lote

Docstring:
Conector e cache da BrasilAPI para consulta cadastral de Receita Federal.


## src\services\connectors\risk3_connector.py
Linhas: 130

Imports:
- __future__
- app.context
- datetime
- json
- logging
- os
- pandas
- pathlib
- requests
- silver.normalizadores
- time
- typing
- urllib3

Classes:

Funções:
- _obter_token_auth
- buscar_bureau_risk3

Docstring:
Conector oficial para a API Expresso RISK3 (Bureau de Crédito).


## src\services\connectors\salesforce_connector.py
Linhas: 74

Imports:
- __future__
- pandas
- pathlib
- typing

Classes:
- SalesforceConnectionError

Funções:
- buscar_salesforce_dados

Docstring:
Conector de integração de arquivos extraídos do Salesforce (via Power Query).


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
- criar_documento_classificado

Docstring:
Builders da camada silver para documentos classificados.


## src\silver\normalizador_de_tipo_de_campo.py
Linhas: 140

Imports:
- __future__
- anyio
- app.context
- common.json
- control.field_types
- datetime
- re
- silver.normalizadores
- typing

Classes:

Funções:
- _obter_campos
- normalizar_registro

Docstring:
Normalização técnica das fichas.


## src\silver\normalizadores.py
Linhas: 182

Imports:
- __future__
- datetime
- math
- re
- typing

Classes:

Funções:
- normalizar_string
- normalizar_float
- normalize_date
- normalize_data_demonstracao_financeira
- padronizar_cnpj
- calc_digit

Docstring:
Orquestrador Central de Normalizadores do Projeto BDC.


## src\staging\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Camada de staging do sistema BDC.


## src\staging\descoberta.py
Linhas: 18

Imports:
- __future__
- pathlib

Classes:

Funções:
- detectar_arquivos_excel_pendentes

Docstring:
Descoberta de arquivos pendentes para processamento.


## src\staging\staging_arquivo.py
Linhas: 21

Imports:
- __future__
- pathlib
- shutil

Classes:

Funções:
- copiar_para_staging

Docstring:
Cópia de arquivos para a área de staging do sistema.


## src\storage\__init__.py
Linhas: 1

Imports:

Classes:

Funções:

Docstring:
Camada de persistência física do sistema BDC.


## src\storage\armazenamento_manifest.py
Linhas: 39

Imports:
- __future__
- json
- pathlib
- typing

Classes:

Funções:
- anexar_registro_de_manifesto
- historico_de_ingestao_de_carga

Docstring:
Persistência do manifest de ingestão em formato JSONL.


## src\storage\bronze_arquivo.py
Linhas: 20

Imports:
- __future__
- pathlib
- shutil

Classes:

Funções:
- publicar_arquivo_bruto

Docstring:
Publicação de arquivos válidos na camada bronze.


## src\storage\escrever_dados.py
Linhas: 159

Imports:
- pandas
- pathlib
- typing

Classes:

Funções:
- _normalize_filename
- escrever_conjunto_de_dados_silver
- mesclar_conjunto_de_dados_prata_por_chave_de_negocio

Docstring:
Persistência de datasets padronizados da camada silver.


## src\storage\estado_armazenamento.py
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


## src\storage\operacao_arquivo.py
Linhas: 34

Imports:
- __future__
- pathlib
- shutil
- time

Classes:

Funções:
- mover_arquivo_com_tentativa_adicional

Docstring:
Operações robustas de arquivo para ambiente Windows.
