# ALERTAS ESTATÍSTICOS

Alertas heurísticos para orientar revisão humana. Eles não provam que o código está incorreto.

## Resumo

- ALTA: 10
- MÉDIA: 45
- BAIXA: 160

## Ocorrências

- **ALTA** | `BARE_EXCEPT` | `scripts/comparar_bases.py:22` | Bloco except sem tipo de exceção.

- **ALTA** | `SILENT_EXCEPTION` | `src/app/comercializadoras/orquestrador_comercializadoras.py:355` | except Exception com pass oculta falhas.

- **ALTA** | `BARE_EXCEPT` | `src/domain/contratos/servico_contratos_denodo.py:45` | Bloco except sem tipo de exceção.

- **ALTA** | `SILENT_EXCEPTION` | `src/domain/diagnostico/servico_recuperacao.py:111` | except Exception com pass oculta falhas.

- **ALTA** | `SILENT_EXCEPTION` | `src/domain/fichas/extrator.py:329` | except Exception com pass oculta falhas.

- **ALTA** | `SILENT_EXCEPTION` | `src/gold/regras_gold.py:23` | except Exception com pass oculta falhas.

- **ALTA** | `SILENT_EXCEPTION` | `src/ui/views/visao_carteira.py:20` | except Exception com pass oculta falhas.

- **ALTA** | `SILENT_EXCEPTION` | `src/ui/views/visao_carteira.py:29` | except Exception com pass oculta falhas.

- **ALTA** | `SILENT_EXCEPTION` | `src/ui/views/visao_silver.py:35` | except Exception com pass oculta falhas.

- **ALTA** | `SILENT_EXCEPTION` | `src/ui/views/visao_silver.py:41` | except Exception com pass oculta falhas.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `gerar_contexto_ia.py:182` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `gerar_contexto_ia.py:183` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `SYS_EXIT` | `main.py:219` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `scripts/busca_lucro_liquido.py:11` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `scripts/captura_evidencias.py:5` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `scripts/comparar_bases.py:9` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `scripts/find_coords.py:12` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `scripts/find_labels.py:11` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `scripts/restore_data_calculo.py:4` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `scripts/sync_metadata.py:5` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `ABSOLUTE_USER_PATH` | `scripts/teste_antes_depois_semantica.py:6` | Caminho absoluto de usuário encontrado.

- **MÉDIA** | `LONG_FUNCTION` | `src/app/comercializadoras/orquestrador_comercializadoras.py:162` | Função processar_arquivo_individual possui 196 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/app/consumidores/orquestrador_consumidores.py:167` | Função processar_arquivo_individual possui 347 linhas.

- **MÉDIA** | `SYS_EXIT` | `src/app/context.py:42` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `SYS_EXIT` | `src/app/context.py:46` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `SYS_EXIT` | `src/app/context.py:53` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `SYS_EXIT` | `src/app/context.py:63` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `SYS_EXIT` | `src/app/context.py:74` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `SYS_EXIT` | `src/cli/rodar_fichas_comercializadoras.py:48` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `SYS_EXIT` | `src/cli/rodar_fichas_consumidores.py:46` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `SYS_EXIT` | `src/common/json.py:33` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `SYS_EXIT` | `src/control/layout_catalog.py:16` | sys.exit fora da camada de interface deve ser revisado.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/carga_manual/servico_carga_manual.py:20` | Função inserir_dados_carga_manual possui 108 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/contrapartes/servico_enquadramento.py:12` | Função calcular_enquadramento_consumidor possui 113 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/credito/pd_cpura.py:164` | Função calcular_pd_final_cpura possui 119 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/credito/pd_motor.py:22` | Função calcular_pd_ajustada possui 153 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/credito/pd_transform.py:53` | Função transformar_pd_por_segmento possui 121 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/credito/score_qualitativo.py:60` | Função calcular_score_qualitativo_cpura possui 102 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/diagnostico/servico_diagnostico.py:27` | Função gerar_diagnostico possui 103 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/fichas/extrator.py:240` | Função extrair_registro possui 160 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/mtm/servico_mtm.py:27` | Função inserir_dados_mtm possui 105 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/domain/salesforce/servico_salesforce.py:22` | Função inserir_dados_salesforce possui 105 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/gold/servico_gold.py:101` | Função construir_visao_consolidada possui 374 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/relational/facts/fato_alertas.py:10` | Função gerar_fato_alertas_credito possui 126 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/relational/facts/fato_alertas_manuais.py:10` | Função gerar_fato_alertas_manuais possui 133 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/relational/facts/fato_analise_credito.py:17` | Função construir_fato_analise_credito possui 140 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/relational/facts/fato_exposicao_risco.py:19` | Função construir_fato_exposicao_risco possui 104 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/relational/facts/fato_garantia.py:17` | Função gerar_fato_garantia possui 135 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/relational/facts/fato_reconciliacao_contrato_mtm.py:22` | Função executar_reconciliacao_denodo_mtm possui 153 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/relational/facts/fato_reconciliacao_fichas_salesforce.py:20` | Função executar_reconciliacao_fichas_salesforce possui 108 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/services/connectors/risk3_connector.py:51` | Função buscar_bureau_risk3 possui 136 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/storage/escrever_dados.py:69` | Função mesclar_conjunto_de_dados_prata_por_chave_de_negocio possui 118 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/ui/views/visao_carga_manual.py:108` | Função render_visao_carga_manual possui 201 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/ui/views/visao_carteira.py:127` | Função render_visao_carteira possui 152 linhas.

- **MÉDIA** | `LONG_FUNCTION` | `src/ui/views/visao_silver.py:82` | Função render_visao_silver possui 127 linhas.

- **BAIXA** | `PRINT` | `gerar_contexto_ia.py:864` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `gerar_contexto_ia.py:865` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `gerar_contexto_ia.py:866` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `gerar_contexto_ia.py:867` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `gerar_contexto_ia.py:868` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `gerar_contexto_ia.py:869` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `gerar_contexto_ia.py:870` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `gerar_contexto_ia.py:871` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `main.py:171` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:27` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:42` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:105` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:122` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:126` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:133` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:134` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:135` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:136` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `reset.py:137` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:7` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:12` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:13` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:14` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:15` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:17` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:19` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:21` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:23` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:27` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:29` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:31` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:38` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/auditoria_fase3_alertas.py:40` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:7` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:8` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:9` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:17` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:29` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:32` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:53` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:55` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:57` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_lucro_liquido.py:59` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:15` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:16` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:17` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:27` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:28` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:29` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:31` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:32` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:33` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:43` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:61` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:63` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:66` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:68` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:87` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:89` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/busca_profunda.py:92` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/buscar_coordenadas_amostra.py:28` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/buscar_coordenadas_amostra.py:29` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/buscar_coordenadas_amostra.py:30` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/buscar_coordenadas_amostra.py:36` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/buscar_coordenadas_amostra.py:41` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/buscar_coordenadas_amostra.py:78` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/buscar_coordenadas_amostra.py:82` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/captura_evidencias.py:54` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/captura_evidencias.py:55` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/captura_evidencias.py:56` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/captura_evidencias.py:58` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/captura_evidencias.py:60` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/captura_evidencias.py:62` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:16` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:27` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:30` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:32` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:33` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:35` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:38` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:41` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:54` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:58` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/check_fase2.py:60` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/comparar_bases.py:5` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/comparar_bases.py:6` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/comparar_bases.py:7` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/comparar_bases.py:18` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/comparar_bases.py:25` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/comparar_bases.py:27` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/comparar_bases.py:29` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/comparar_bases.py:52` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/debug_silver_comercializadoras.py:23` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/debug_silver_comercializadoras.py:101` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/debug_silver_comercializadoras.py:102` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/debug_silver_comercializadoras.py:103` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/debug_silver_comercializadoras.py:104` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/debug_zero_consumidores.py:9` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/debug_zero_consumidores.py:22` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/debug_zero_consumidores.py:24` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/debug_zero_consumidores.py:26` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_coords.py:17` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_coords.py:21` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_coords.py:25` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_coords.py:31` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_coords.py:37` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_coords.py:39` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_coords.py:45` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_coords.py:49` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_coords.py:55` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_labels.py:17` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_labels.py:33` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_labels.py:34` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_labels.py:35` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_labels.py:40` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_labels.py:41` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/find_labels.py:44` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/restore_data_calculo.py:73` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/sync_metadata.py:93` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_antes_depois_semantica.py:27` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_antes_depois_semantica.py:28` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_antes_depois_semantica.py:29` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_antes_depois_semantica.py:32` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_antes_depois_semantica.py:41` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_antes_depois_semantica.py:57` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_antes_depois_semantica.py:58` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:9` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:17` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:18` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:19` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:28` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:30` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:31` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:35` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:42` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:48` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:52` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:54` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:55` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:56` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:68` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:69` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:71` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:72` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/teste_hipotese_cluster.py:73` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:11` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:16` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:17` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:18` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:21` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:24` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:26` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:33` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:35` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:38` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:43` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:47` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:49` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:51` | Uso de print; avaliar logging estruturado.

- **BAIXA** | `PRINT` | `scripts/valida_ajustes.py:53` | Uso de print; avaliar logging estruturado.
