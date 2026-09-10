# DEPENDÊNCIAS INTERNAS

Mapa aproximado baseado em imports estáticos analisáveis por AST.

## `gerar_contexto_ia.py`

- Nenhuma dependência interna resolvida.

## `main.py`

- importa `src/app/bootstrap.py`
- importa `src/cli/__init__.py`
- importa `src/control/logger.py`
- importa `src/domain/auditoria/servico_auditoria.py`
- importa `src/domain/cadastro/servico_bureau.py`
- importa `src/domain/cadastro/servico_receita.py`
- importa `src/domain/carga_manual/servico_carga_manual.py`
- importa `src/domain/contrapartes/servico_enquadramento.py`
- importa `src/domain/contratos/servico_contratos_denodo.py`
- importa `src/domain/credito/servico_override.py`
- importa `src/domain/garantias/servico_garantia.py`
- importa `src/domain/mtm/servico_mtm.py`
- importa `src/domain/salesforce/servico_salesforce.py`
- importa `src/gold/servico_gold.py`
- importa `src/relational/dimensions/dim_contraparte.py`
- importa `src/relational/facts/fato_alertas.py`
- importa `src/relational/facts/fato_alertas_manuais.py`
- importa `src/relational/facts/fato_analise_credito.py`
- importa `src/relational/facts/fato_exposicao_risco.py`
- importa `src/relational/facts/fato_garantia.py`
- importa `src/relational/facts/fato_reconciliacao_contrato_mtm.py`
- importa `src/relational/facts/fato_reconciliacao_fichas_salesforce.py`

## `reset.py`

- Nenhuma dependência interna resolvida.

## `scripts/auditoria_fase3_alertas.py`

- Nenhuma dependência interna resolvida.

## `scripts/busca_lucro_liquido.py`

- Nenhuma dependência interna resolvida.

## `scripts/busca_profunda.py`

- Nenhuma dependência interna resolvida.

## `scripts/buscar_coordenadas_amostra.py`

- Nenhuma dependência interna resolvida.

## `scripts/captura_evidencias.py`

- Nenhuma dependência interna resolvida.

## `scripts/check_fase2.py`

- Nenhuma dependência interna resolvida.

## `scripts/comparar_bases.py`

- Nenhuma dependência interna resolvida.

## `scripts/debug_silver_comercializadoras.py`

- Nenhuma dependência interna resolvida.

## `scripts/debug_zero_consumidores.py`

- Nenhuma dependência interna resolvida.

## `scripts/find_coords.py`

- Nenhuma dependência interna resolvida.

## `scripts/find_labels.py`

- Nenhuma dependência interna resolvida.

## `scripts/restore_data_calculo.py`

- Nenhuma dependência interna resolvida.

## `scripts/sync_metadata.py`

- Nenhuma dependência interna resolvida.

## `scripts/teste_antes_depois_semantica.py`

- importa `src/domain/fichas/extrator.py`

## `scripts/teste_hipotese_cluster.py`

- Nenhuma dependência interna resolvida.

## `scripts/valida_ajustes.py`

- Nenhuma dependência interna resolvida.

## `src/app/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/app/bootstrap.py`

- importa `src/app/context.py`

## `src/app/comercializadoras/orquestrador_comercializadoras.py`

- importa `src/app/context.py`
- importa `src/common/datas.py`
- importa `src/common/excel.py`
- importa `src/common/hashing.py`
- importa `src/common/identificadores.py`
- importa `src/common/json.py`
- importa `src/common/servico_desduplicacao.py`
- importa `src/common/utils_orquestracao.py`
- importa `src/control/carregador_de_mapeamento.py`
- importa `src/control/layout_catalog.py`
- importa `src/control/logger.py`
- importa `src/domain/auditoria/servico_auditoria.py`
- importa `src/domain/fichas/derivador_financeiro.py`
- importa `src/domain/fichas/extrator.py`
- importa `src/domain/fichas/validador.py`
- importa `src/relational/facts/fato_alerta_util.py`
- importa `src/silver/documentos_classificados.py`
- importa `src/silver/formatador_silver.py`
- importa `src/silver/mapeador_dominio.py`
- importa `src/staging/staging_arquivo.py`
- importa `src/storage/armazenamento_manifest.py`
- importa `src/storage/bronze_arquivo.py`
- importa `src/storage/escrever_dados.py`
- importa `src/storage/estado_armazenamento.py`

## `src/app/config_builder.py`

- Nenhuma dependência interna resolvida.

## `src/app/consumidores/orquestrador_consumidores.py`

- importa `src/app/context.py`
- importa `src/common/datas.py`
- importa `src/common/excel.py`
- importa `src/common/hashing.py`
- importa `src/common/identificadores.py`
- importa `src/common/json.py`
- importa `src/common/nulos.py`
- importa `src/common/servico_desduplicacao.py`
- importa `src/common/utils_orquestracao.py`
- importa `src/control/carregador_de_mapeamento.py`
- importa `src/control/layout_catalog.py`
- importa `src/control/logger.py`
- importa `src/control/quality_loader.py`
- importa `src/domain/auditoria/servico_auditoria.py`
- importa `src/domain/consumidores/classificacao.py`
- importa `src/domain/fichas/derivador_financeiro.py`
- importa `src/domain/fichas/extrator.py`
- importa `src/domain/fichas/validador.py`
- importa `src/relational/facts/fato_alerta_util.py`
- importa `src/silver/documentos_classificados.py`
- importa `src/silver/formatador_silver.py`
- importa `src/silver/mapeador_dominio.py`
- importa `src/staging/staging_arquivo.py`
- importa `src/storage/armazenamento_manifest.py`
- importa `src/storage/bronze_arquivo.py`
- importa `src/storage/escrever_dados.py`
- importa `src/storage/estado_armazenamento.py`

## `src/app/context.py`

- importa `src/app/config_builder.py`
- importa `src/common/json.py`

## `src/cli/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/cli/rodar_fichas_comercializadoras.py`

- importa `src/app/bootstrap.py`
- importa `src/app/comercializadoras/orquestrador_comercializadoras.py`
- importa `src/control/logger.py`

## `src/cli/rodar_fichas_consumidores.py`

- importa `src/app/bootstrap.py`
- importa `src/app/consumidores/orquestrador_consumidores.py`
- importa `src/control/logger.py`

## `src/common/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/common/dados.py`

- importa `src/common/dominio.py`
- importa `src/common/identificadores.py`
- importa `src/common/numeros.py`

## `src/common/datas.py`

- importa `src/common/nulos.py`

## `src/common/dominio.py`

- importa `src/common/texto.py`

## `src/common/excel.py`

- Nenhuma dependência interna resolvida.

## `src/common/hashing.py`

- Nenhuma dependência interna resolvida.

## `src/common/identificadores.py`

- importa `src/common/nulos.py`

## `src/common/json.py`

- Nenhuma dependência interna resolvida.

## `src/common/nulos.py`

- Nenhuma dependência interna resolvida.

## `src/common/numeros.py`

- importa `src/common/nulos.py`

## `src/common/paths.py`

- Nenhuma dependência interna resolvida.

## `src/common/servico_desduplicacao.py`

- Nenhuma dependência interna resolvida.

## `src/common/texto.py`

- Nenhuma dependência interna resolvida.

## `src/common/utils_orquestracao.py`

- importa `src/app/context.py`
- importa `src/common/paths.py`
- importa `src/domain/auditoria/servico_auditoria.py`
- importa `src/staging/descoberta.py`
- importa `src/storage/armazenamento_manifest.py`
- importa `src/storage/estado_armazenamento.py`
- importa `src/storage/operacao_arquivo.py`

## `src/control/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/control/carregador_de_mapeamento.py`

- importa `src/app/context.py`
- importa `src/common/json.py`

## `src/control/layout_catalog.py`

- importa `src/app/context.py`
- importa `src/common/json.py`

## `src/control/logger.py`

- Nenhuma dependência interna resolvida.

## `src/control/quality_loader.py`

- importa `src/app/context.py`
- importa `src/common/json.py`

## `src/domain/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/auditoria/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/auditoria/servico_auditoria.py`

- importa `src/storage/escrever_dados.py`

## `src/domain/cadastro/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/cadastro/servico_bureau.py`

- importa `src/app/context.py`
- importa `src/control/logger.py`
- importa `src/services/connectors/risk3_connector.py`
- importa `src/storage/escrever_dados.py`

## `src/domain/cadastro/servico_receita.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`
- importa `src/control/logger.py`
- importa `src/domain/enums.py`
- importa `src/relational/facts/fato_alerta_util.py`
- importa `src/services/connectors/receita_connector.py`
- importa `src/storage/escrever_dados.py`

## `src/domain/carga_manual/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/carga_manual/servico_carga_manual.py`

- importa `src/app/context.py`
- importa `src/common/datas.py`
- importa `src/common/identificadores.py`
- importa `src/common/json.py`
- importa `src/common/numeros.py`
- importa `src/control/logger.py`
- importa `src/domain/carga_manual/servico_repescagem.py`
- importa `src/storage/escrever_dados.py`

## `src/domain/carga_manual/servico_repescagem.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`

## `src/domain/consumidores/classificacao.py`

- Nenhuma dependência interna resolvida.

## `src/domain/contrapartes/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/contrapartes/segmentacao.py`

- importa `src/common/numeros.py`
- importa `src/common/texto.py`

## `src/domain/contrapartes/servico_enquadramento.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`

## `src/domain/contratos/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/contratos/servico_contratos_denodo.py`

- importa `src/app/context.py`
- importa `src/common/dados.py`
- importa `src/services/connectors/denodo_connector.py`
- importa `src/storage/escrever_dados.py`

## `src/domain/credito/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/credito/motor_ead.py`

- Nenhuma dependência interna resolvida.

## `src/domain/credito/motor_lgd.py`

- Nenhuma dependência interna resolvida.

## `src/domain/credito/motor_pe.py`

- Nenhuma dependência interna resolvida.

## `src/domain/credito/motor_taxa_risco.py`

- importa `src/relational/facts/fato_alerta_util.py`

## `src/domain/credito/notas_quantitativas_cpura.py`

- importa `src/common/numeros.py`
- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/pd_base.py`

- importa `src/common/numeros.py`
- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/pd_cgrupo.py`

- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/pd_consumidor_gt5.py`

- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/pd_consumidor_le5.py`

- importa `src/common/numeros.py`
- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/pd_cpura.py`

- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/pd_exceptions.py`

- Nenhuma dependência interna resolvida.

## `src/domain/credito/pd_motor.py`

- importa `src/common/texto.py`
- importa `src/domain/credito/notas_quantitativas_cpura.py`
- importa `src/domain/credito/pd_base.py`
- importa `src/domain/credito/pd_exceptions.py`
- importa `src/domain/credito/pd_transform.py`
- importa `src/domain/credito/pd_validator.py`
- importa `src/domain/credito/rating.py`
- importa `src/domain/credito/score_qualitativo.py`
- importa `src/domain/credito/score_quantitativo.py`
- importa `src/domain/credito/score_total.py`

## `src/domain/credito/pd_transform.py`

- importa `src/domain/credito/pd_cgrupo.py`
- importa `src/domain/credito/pd_consumidor_gt5.py`
- importa `src/domain/credito/pd_consumidor_le5.py`
- importa `src/domain/credito/pd_cpura.py`
- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/pd_validator.py`

- importa `src/common/numeros.py`
- importa `src/common/texto.py`
- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/rating.py`

- importa `src/common/texto.py`
- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/score_qualitativo.py`

- importa `src/common/texto.py`
- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/score_quantitativo.py`

- importa `src/common/texto.py`
- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/score_total.py`

- importa `src/domain/credito/pd_exceptions.py`

## `src/domain/credito/servico_override.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`
- importa `src/domain/enums.py`
- importa `src/storage/escrever_dados.py`

## `src/domain/diagnostico/servico_diagnostico.py`

- importa `src/common/identificadores.py`
- importa `src/control/logger.py`
- importa `src/domain/diagnostico/servico_recuperacao.py`

## `src/domain/diagnostico/servico_exportacao.py`

- importa `src/common/identificadores.py`
- importa `src/control/logger.py`

## `src/domain/diagnostico/servico_recuperacao.py`

- importa `src/common/excel.py`
- importa `src/common/json.py`
- importa `src/control/logger.py`
- importa `src/domain/fichas/extrator.py`

## `src/domain/enums.py`

- Nenhuma dependência interna resolvida.

## `src/domain/fichas/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/fichas/derivador_financeiro.py`

- Nenhuma dependência interna resolvida.

## `src/domain/fichas/extrator.py`

- importa `src/common/nulos.py`
- importa `src/common/texto.py`

## `src/domain/fichas/validador.py`

- importa `src/common/nulos.py`

## `src/domain/garantias/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/garantias/servico_garantia.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`
- importa `src/control/logger.py`
- importa `src/storage/escrever_dados.py`

## `src/domain/mtm/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/mtm/servico_mtm.py`

- importa `src/app/context.py`
- importa `src/control/logger.py`
- importa `src/services/connectors/mtm_connector.py`
- importa `src/storage/escrever_dados.py`

## `src/domain/salesforce/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/domain/salesforce/servico_salesforce.py`

- importa `src/app/context.py`
- importa `src/control/logger.py`
- importa `src/services/connectors/salesforce_connector.py`
- importa `src/storage/escrever_dados.py`

## `src/gold/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/gold/regras_gold.py`

- importa `src/app/context.py`
- importa `src/common/nulos.py`

## `src/gold/servico_gold.py`

- importa `src/common/dados.py`
- importa `src/common/identificadores.py`
- importa `src/common/nulos.py`
- importa `src/control/logger.py`
- importa `src/gold/regras_gold.py`

## `src/relational/dimensions/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/relational/dimensions/dim_contraparte.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`
- importa `src/storage/escrever_dados.py`

## `src/relational/facts/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/relational/facts/fato_alerta_util.py`

- Nenhuma dependência interna resolvida.

## `src/relational/facts/fato_alertas.py`

- importa `src/control/logger.py`
- importa `src/relational/facts/fato_alerta_util.py`
- importa `src/storage/escrever_dados.py`

## `src/relational/facts/fato_alertas_manuais.py`

- importa `src/control/logger.py`
- importa `src/relational/facts/fato_alerta_util.py`

## `src/relational/facts/fato_analise_credito.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`
- importa `src/common/json.py`
- importa `src/control/logger.py`
- importa `src/domain/contrapartes/segmentacao.py`
- importa `src/domain/credito/pd_exceptions.py`
- importa `src/domain/credito/pd_motor.py`
- importa `src/relational/facts/fato_alerta_util.py`
- importa `src/storage/escrever_dados.py`

## `src/relational/facts/fato_exposicao_risco.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`
- importa `src/control/logger.py`
- importa `src/domain/credito/motor_ead.py`
- importa `src/domain/credito/motor_lgd.py`
- importa `src/domain/credito/motor_pe.py`
- importa `src/domain/credito/motor_taxa_risco.py`
- importa `src/storage/escrever_dados.py`

## `src/relational/facts/fato_garantia.py`

- importa `src/app/context.py`
- importa `src/control/logger.py`
- importa `src/domain/enums.py`
- importa `src/relational/facts/fato_alerta_util.py`
- importa `src/storage/escrever_dados.py`

## `src/relational/facts/fato_reconciliacao_contrato_mtm.py`

- importa `src/app/context.py`
- importa `src/control/logger.py`
- importa `src/domain/enums.py`
- importa `src/relational/facts/fato_alerta_util.py`
- importa `src/storage/escrever_dados.py`

## `src/relational/facts/fato_reconciliacao_fichas_salesforce.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`
- importa `src/control/logger.py`
- importa `src/relational/facts/fato_alerta_util.py`
- importa `src/storage/escrever_dados.py`

## `src/services/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/services/connectors/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/services/connectors/denodo_connector.py`

- Nenhuma dependência interna resolvida.

## `src/services/connectors/mtm_connector.py`

- importa `src/common/dados.py`

## `src/services/connectors/receita_connector.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`

## `src/services/connectors/risk3_connector.py`

- importa `src/app/context.py`
- importa `src/common/identificadores.py`
- importa `src/control/logger.py`

## `src/services/connectors/salesforce_connector.py`

- importa `src/common/identificadores.py`

## `src/silver/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/silver/documentos_classificados.py`

- Nenhuma dependência interna resolvida.

## `src/silver/formatador_silver.py`

- importa `src/app/context.py`
- importa `src/common/datas.py`
- importa `src/common/identificadores.py`
- importa `src/common/numeros.py`
- importa `src/common/texto.py`

## `src/silver/mapeador_dominio.py`

- importa `src/app/context.py`
- importa `src/common/dominio.py`

## `src/staging/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/staging/descoberta.py`

- Nenhuma dependência interna resolvida.

## `src/staging/staging_arquivo.py`

- Nenhuma dependência interna resolvida.

## `src/storage/__init__.py`

- Nenhuma dependência interna resolvida.

## `src/storage/armazenamento_manifest.py`

- Nenhuma dependência interna resolvida.

## `src/storage/bronze_arquivo.py`

- Nenhuma dependência interna resolvida.

## `src/storage/escrever_dados.py`

- Nenhuma dependência interna resolvida.

## `src/storage/estado_armazenamento.py`

- importa `src/domain/enums.py`

## `src/storage/operacao_arquivo.py`

- Nenhuma dependência interna resolvida.

## `src/ui/app.py`

- importa `src/ui/views/visao_carga_manual.py`
- importa `src/ui/views/visao_carteira.py`
- importa `src/ui/views/visao_orquestrador.py`
- importa `src/ui/views/visao_silver.py`

## `src/ui/views/visao_carga_manual.py`

- importa `src/common/datas.py`
- importa `src/common/identificadores.py`
- importa `src/domain/diagnostico/servico_diagnostico.py`
- importa `src/domain/diagnostico/servico_exportacao.py`

## `src/ui/views/visao_carteira.py`

- Nenhuma dependência interna resolvida.

## `src/ui/views/visao_orquestrador.py`

- Nenhuma dependência interna resolvida.

## `src/ui/views/visao_silver.py`

- importa `src/common/datas.py`
- importa `src/common/identificadores.py`

# MÓDULOS INTERNOS MAIS REFERENCIADOS

- `src/app/context.py`: 28 consumidor(es)
- `src/control/logger.py`: 23 consumidor(es)
- `src/common/identificadores.py`: 22 consumidor(es)
- `src/storage/escrever_dados.py`: 18 consumidor(es)
- `src/domain/credito/pd_exceptions.py`: 14 consumidor(es)
- `src/relational/facts/fato_alerta_util.py`: 10 consumidor(es)
- `src/common/json.py`: 9 consumidor(es)
- `src/common/texto.py`: 9 consumidor(es)
- `src/common/nulos.py`: 8 consumidor(es)
- `src/common/numeros.py`: 8 consumidor(es)
- `src/common/datas.py`: 6 consumidor(es)
- `src/domain/enums.py`: 5 consumidor(es)
- `src/domain/auditoria/servico_auditoria.py`: 4 consumidor(es)
- `src/domain/fichas/extrator.py`: 4 consumidor(es)
- `src/app/bootstrap.py`: 3 consumidor(es)
- `src/common/excel.py`: 3 consumidor(es)
- `src/storage/armazenamento_manifest.py`: 3 consumidor(es)
- `src/storage/estado_armazenamento.py`: 3 consumidor(es)
- `src/common/dados.py`: 3 consumidor(es)
- `src/common/hashing.py`: 2 consumidor(es)
- `src/common/servico_desduplicacao.py`: 2 consumidor(es)
- `src/common/utils_orquestracao.py`: 2 consumidor(es)
- `src/control/carregador_de_mapeamento.py`: 2 consumidor(es)
- `src/control/layout_catalog.py`: 2 consumidor(es)
- `src/domain/fichas/derivador_financeiro.py`: 2 consumidor(es)
- `src/domain/fichas/validador.py`: 2 consumidor(es)
- `src/silver/documentos_classificados.py`: 2 consumidor(es)
- `src/silver/formatador_silver.py`: 2 consumidor(es)
- `src/silver/mapeador_dominio.py`: 2 consumidor(es)
- `src/staging/staging_arquivo.py`: 2 consumidor(es)
- `src/storage/bronze_arquivo.py`: 2 consumidor(es)
- `src/common/dominio.py`: 2 consumidor(es)
- `src/cli/__init__.py`: 1 consumidor(es)
- `src/domain/cadastro/servico_bureau.py`: 1 consumidor(es)
- `src/domain/cadastro/servico_receita.py`: 1 consumidor(es)
- `src/domain/carga_manual/servico_carga_manual.py`: 1 consumidor(es)
- `src/domain/contrapartes/servico_enquadramento.py`: 1 consumidor(es)
- `src/domain/contratos/servico_contratos_denodo.py`: 1 consumidor(es)
- `src/domain/credito/servico_override.py`: 1 consumidor(es)
- `src/domain/garantias/servico_garantia.py`: 1 consumidor(es)
- `src/domain/mtm/servico_mtm.py`: 1 consumidor(es)
- `src/domain/salesforce/servico_salesforce.py`: 1 consumidor(es)
- `src/gold/servico_gold.py`: 1 consumidor(es)
- `src/relational/dimensions/dim_contraparte.py`: 1 consumidor(es)
- `src/relational/facts/fato_alertas.py`: 1 consumidor(es)
- `src/relational/facts/fato_alertas_manuais.py`: 1 consumidor(es)
- `src/relational/facts/fato_analise_credito.py`: 1 consumidor(es)
- `src/relational/facts/fato_exposicao_risco.py`: 1 consumidor(es)
- `src/relational/facts/fato_garantia.py`: 1 consumidor(es)
- `src/relational/facts/fato_reconciliacao_contrato_mtm.py`: 1 consumidor(es)
- `src/relational/facts/fato_reconciliacao_fichas_salesforce.py`: 1 consumidor(es)
- `src/control/quality_loader.py`: 1 consumidor(es)
- `src/domain/consumidores/classificacao.py`: 1 consumidor(es)
- `src/app/config_builder.py`: 1 consumidor(es)
- `src/app/comercializadoras/orquestrador_comercializadoras.py`: 1 consumidor(es)
- `src/app/consumidores/orquestrador_consumidores.py`: 1 consumidor(es)
- `src/common/paths.py`: 1 consumidor(es)
- `src/staging/descoberta.py`: 1 consumidor(es)
- `src/storage/operacao_arquivo.py`: 1 consumidor(es)
- `src/services/connectors/risk3_connector.py`: 1 consumidor(es)
- `src/services/connectors/receita_connector.py`: 1 consumidor(es)
- `src/domain/carga_manual/servico_repescagem.py`: 1 consumidor(es)
- `src/services/connectors/denodo_connector.py`: 1 consumidor(es)
- `src/domain/credito/notas_quantitativas_cpura.py`: 1 consumidor(es)
- `src/domain/credito/pd_base.py`: 1 consumidor(es)
- `src/domain/credito/pd_transform.py`: 1 consumidor(es)
- `src/domain/credito/pd_validator.py`: 1 consumidor(es)
- `src/domain/credito/rating.py`: 1 consumidor(es)
- `src/domain/credito/score_qualitativo.py`: 1 consumidor(es)
- `src/domain/credito/score_quantitativo.py`: 1 consumidor(es)
- `src/domain/credito/score_total.py`: 1 consumidor(es)
- `src/domain/credito/pd_cgrupo.py`: 1 consumidor(es)
- `src/domain/credito/pd_consumidor_gt5.py`: 1 consumidor(es)
- `src/domain/credito/pd_consumidor_le5.py`: 1 consumidor(es)
- `src/domain/credito/pd_cpura.py`: 1 consumidor(es)
- `src/domain/diagnostico/servico_recuperacao.py`: 1 consumidor(es)
- `src/services/connectors/mtm_connector.py`: 1 consumidor(es)
- `src/services/connectors/salesforce_connector.py`: 1 consumidor(es)
- `src/gold/regras_gold.py`: 1 consumidor(es)
- `src/domain/contrapartes/segmentacao.py`: 1 consumidor(es)
- `src/domain/credito/pd_motor.py`: 1 consumidor(es)
- `src/domain/credito/motor_ead.py`: 1 consumidor(es)
- `src/domain/credito/motor_lgd.py`: 1 consumidor(es)
- `src/domain/credito/motor_pe.py`: 1 consumidor(es)
- `src/domain/credito/motor_taxa_risco.py`: 1 consumidor(es)
- `src/ui/views/visao_carga_manual.py`: 1 consumidor(es)
- `src/ui/views/visao_carteira.py`: 1 consumidor(es)
- `src/ui/views/visao_orquestrador.py`: 1 consumidor(es)
- `src/ui/views/visao_silver.py`: 1 consumidor(es)
- `src/domain/diagnostico/servico_diagnostico.py`: 1 consumidor(es)
- `src/domain/diagnostico/servico_exportacao.py`: 1 consumidor(es)
