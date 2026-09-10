# RESUMO TÉCNICO


---

## `gerar_contexto_ia.py`

- Linhas: 877
- Bytes: 30174
- Codificação: `utf-8`
- SHA-256: `76d881e95595f097fc4a0b9ba8c427c94df791382813838c890f54e3010f1c05`

### Imports

- `__future__`
- `argparse`
- `ast`
- `collections`
- `dataclasses`
- `datetime`
- `hashlib`
- `json`
- `pathlib`
- `re`
- `shutil`
- `textwrap`
- `typing`

### Classes

- `SymbolInfo` (class, linhas 63-68) | decorators: dataclass
- `FileAnalysis` (class, linhas 72-84) | decorators: dataclass
- `Alert` (class, linhas 88-93) | decorators: dataclass

### Funções e métodos

- `parse_args` (function, linhas 96-129)
- `is_ignored` (function, linhas 132-141)
- `is_sensitive_file` (function, linhas 144-146)
- `read_text_safe` (function, linhas 149-166)
- `sanitize_text` (function, linhas 169-189)
- `sha256_file` (function, linhas 192-197)
- `dotted_name` (function, linhas 200-208)
- `decorator_names` (function, linhas 211-212)
- `analyze_python` (function, linhas 215-274)
- `scan_alerts` (function, linhas 277-336)
- `build_tree` (function, linhas 339-362)
- `discover_files` (function, linhas 365-387)
- `module_group` (function, linhas 390-406)
- `distribute_semantically` (function, linhas 409-446)
- `detect_internal_dependencies` (function, linhas 449-474)
- `write_readme` (function, linhas 477-510)
- `write_context` (function, linhas 513-552)
- `write_structure` (function, linhas 555-558)
- `code_fence_language` (function, linhas 561-570)
- `write_configurations` (function, linhas 573-611)
- `format_symbol` (function, linhas 614-619)
- `write_technical_summary` (function, linhas 622-658)
- `write_dependencies` (function, linhas 661-682)
- `write_alerts` (function, linhas 685-712)
- `write_code_parts` (function, linhas 715-764)
- `write_manifest` (function, linhas 767-802)
- `main` (function, linhas 805-873)


---

## `main.py`

- Linhas: 219
- Bytes: 11356
- Codificação: `utf-8`
- SHA-256: `7d979b101a6b23e5e874cfb1e5213caa2ebe1cbd47fc362497858f1e0cc55c24`

### Imports

- `app.bootstrap`
- `argparse`
- `cli`
- `control.logger`
- `datetime`
- `domain.auditoria.servico_auditoria`
- `domain.cadastro.servico_bureau`
- `domain.cadastro.servico_receita`
- `domain.carga_manual.servico_carga_manual`
- `domain.contrapartes.servico_enquadramento`
- `domain.contratos.servico_contratos_denodo`
- `domain.credito.servico_override`
- `domain.garantias.servico_garantia`
- `domain.mtm.servico_mtm`
- `domain.salesforce.servico_salesforce`
- `gold.servico_gold`
- `inspect`
- `pandas`
- `pathlib`
- `relational.dimensions.dim_contraparte`
- `relational.facts.fato_alertas`
- `relational.facts.fato_alertas_manuais`
- `relational.facts.fato_analise_credito`
- `relational.facts.fato_exposicao_risco`
- `relational.facts.fato_garantia`
- `relational.facts.fato_reconciliacao_contrato_mtm`
- `relational.facts.fato_reconciliacao_fichas_salesforce`
- `subprocess`
- `sys`
- `typing`

### Classes

- `PipelineStep` (class, linhas 123-125)

### Funções e métodos

- `rodar_interface_streamlit` (function, linhas 42-46)
- `preparar_e_rodar_risco` (function, linhas 48-78)
- `preparar_dim_contraparte` (function, linhas 80-105)
- `preparar_fato_analise` (function, linhas 107-121)
- `main` (function, linhas 157-216)


---

## `reset.py`

- Linhas: 141
- Bytes: 4755
- Codificação: `utf-8`
- SHA-256: `c979c3cab322361465cecb7e954be33d61f95a326d8c33956228c2396028aa1e`

### Imports

- `__future__`
- `pathlib`
- `shutil`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `clear_directory_contents` (function, linhas 12-28)
- `clear_jsonl_files` (function, linhas 31-43)
- `move_files_back_to_pending` (function, linhas 46-74)
- `move_generic_back_to_pending` (function, linhas 76-102)
- `main` (function, linhas 104-137)


---

## `scripts/auditoria_fase3_alertas.py`

- Linhas: 43
- Bytes: 1709
- Codificação: `utf-8`
- SHA-256: `93d6c67465ef4f2de5144e2f4aaa614af81078b6c74a50dbf840a191b772e16a`

### Imports

- `pandas`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `auditar_alertas` (function, linhas 4-40)


---

## `scripts/busca_lucro_liquido.py`

- Linhas: 62
- Bytes: 3040
- Codificação: `utf-8`
- SHA-256: `491ab1f038b79aaac0771b6ba5104ccbb5df66f8bcdee6d04ec52486464ea741`

### Imports

- `openpyxl`
- `pandas`
- `pathlib`
- `re`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `main` (function, linhas 6-59)


---

## `scripts/busca_profunda.py`

- Linhas: 95
- Bytes: 4809
- Codificação: `utf-8`
- SHA-256: `bf4f026551a0fd742f8bc04d614e476056d850f6a51cbeb6d5edd27db0bf4146`

### Imports

- `openpyxl`
- `pandas`
- `pathlib`
- `re`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `main` (function, linhas 6-92)


---

## `scripts/buscar_coordenadas_amostra.py`

- Linhas: 85
- Bytes: 4237
- Codificação: `utf-8`
- SHA-256: `1b8e9b09130566372f9c7877fa3725bb38b3275715d92fe03bdaf9ced01b70f0`

### Imports

- `openpyxl`
- `pandas`
- `pathlib`
- `re`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `buscar_amostras` (function, linhas 6-82)


---

## `scripts/captura_evidencias.py`

- Linhas: 62
- Bytes: 2306
- Codificação: `utf-8`
- SHA-256: `0ae7fc9653fb04e479f579ad73ce14f93f09857d62967701984feb561bdd0bb9`

### Imports

- `json`
- `pandas`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `scripts/check_fase2.py`

- Linhas: 64
- Bytes: 2949
- Codificação: `utf-8`
- SHA-256: `834dd41d6dc36a0e82a08b7be4d700144c4704392a93941ea4a863b2df0dd4de`

### Imports

- `pandas`
- `pathlib`
- `warnings`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `rodar_auditoria` (function, linhas 6-60)


---

## `scripts/comparar_bases.py`

- Linhas: 55
- Bytes: 2198
- Codificação: `utf-8`
- SHA-256: `ba550c1b2c4d6f98133bbb4ba5a883bdce8e6af47dad0403b126220a383a18a1`

### Imports

- `pandas`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `main` (function, linhas 4-52)


---

## `scripts/debug_silver_comercializadoras.py`

- Linhas: 107
- Bytes: 4348
- Codificação: `utf-8`
- SHA-256: `985409c0fcba2a568ae044e2eae9847c7d5f7ef8022a6c1c9298ec7c8a41e68c`

### Imports

- `json`
- `pandas`
- `pathlib`
- `warnings`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `generate_audit_report` (function, linhas 6-104)


---

## `scripts/debug_zero_consumidores.py`

- Linhas: 29
- Bytes: 1045
- Codificação: `utf-8`
- SHA-256: `1a846352f329d647a27c60d4726e8ccaf965f30e61e77c795f31cf68663f8955`

### Imports

- `pandas`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `debug_zeros` (function, linhas 4-26)


---

## `scripts/find_coords.py`

- Linhas: 55
- Bytes: 2360
- Codificação: `utf-8`
- SHA-256: `1207be0ba570b69c3e0e4cdc6309b83b1bb936ac69c2b5a6309688e4571fc04a`

### Imports

- `openpyxl`
- `os`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `scripts/find_labels.py`

- Linhas: 44
- Bytes: 1927
- Codificação: `utf-8`
- SHA-256: `4b89a26ed1cd27dd4b64cf993eee4fdc190155c985a5399ef3b506ae58d372bf`

### Imports

- `openpyxl`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `scripts/restore_data_calculo.py`

- Linhas: 73
- Bytes: 2564
- Codificação: `utf-8`
- SHA-256: `1057b02ef6fbd3035ace4f78bf30806590616c4210b5aa56846b3951ea0e5147`

### Imports

- `json`
- `os`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `restore_data_calculo` (function, linhas 10-69)


---

## `scripts/sync_metadata.py`

- Linhas: 93
- Bytes: 4229
- Codificação: `utf-8`
- SHA-256: `83bdea4a37b7cb20d51023c63bfdf51695076bcd638fa2452012ad56ae057bd1`

### Imports

- `copy`
- `json`
- `os`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `clean_and_inject` (function, linhas 36-89)


---

## `scripts/teste_antes_depois_semantica.py`

- Linhas: 61
- Bytes: 2394
- Codificação: `utf-8`
- SHA-256: `f743e9d51cb03a6e082a55a074b08edcd9391f3fa850eae464bc7bf32279ead9`

### Imports

- `domain.fichas.extrator`
- `json`
- `logging`
- `openpyxl`
- `pathlib`
- `sys`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `main` (function, linhas 13-58)


---

## `scripts/teste_hipotese_cluster.py`

- Linhas: 76
- Bytes: 2859
- Codificação: `utf-8`
- SHA-256: `cc16aea5f47e8977656ae4c9f275d938259d2e1f363ca50a5e31f27ec6c35c7f`

### Imports

- `pandas`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `testar_hipotese_cluster` (function, linhas 4-73)


---

## `scripts/valida_ajustes.py`

- Linhas: 56
- Bytes: 2597
- Codificação: `utf-8`
- SHA-256: `d23d73d58b9bc22bde351f3c8fbd47566e4f5936cb3220285090ab546d272174`

### Imports

- `pandas`
- `pathlib`
- `warnings`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `validar_ajustes` (function, linhas 6-53)


---

## `src/app/__init__.py`

- Linhas: 1
- Bytes: 57
- Codificação: `utf-8`
- SHA-256: `92314c9144f52e90a5125c383d7d421654581ab3784a0291d94fccf621e3888e`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.

### Docstring do módulo

Pacote de bootstrap e contexto da aplicação BDC.


---

## `src/app/bootstrap.py`

- Linhas: 59
- Bytes: 2074
- Codificação: `utf-8`
- SHA-256: `76f6381dce428c77b2528d3e667a6a261f21242409583b3201c1ac460d2ed28c`

### Imports

- `dotenv`
- `os`
- `pathlib`
- `src.app.context`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `resolve_configs_dir` (function, linhas 13-45)
- `aplicativo_bootstrap` (function, linhas 48-59)


---

## `src/app/comercializadoras/orquestrador_comercializadoras.py`

- Linhas: 417
- Bytes: 19017
- Codificação: `utf-8`
- SHA-256: `9be95c2ed0327d4631edd4157776b8c206f1f5f1654f7984cdd65255a67a74bd`

### Imports

- `__future__`
- `app.context`
- `common.datas`
- `common.excel`
- `common.hashing`
- `common.identificadores`
- `common.json`
- `common.servico_desduplicacao`
- `common.utils_orquestracao`
- `control.carregador_de_mapeamento`
- `control.layout_catalog`
- `control.logger`
- `datetime`
- `domain.auditoria.servico_auditoria`
- `domain.fichas.derivador_financeiro`
- `domain.fichas.extrator`
- `domain.fichas.validador`
- `pandas`
- `pathlib`
- `relational.facts.fato_alerta_util`
- `silver.documentos_classificados`
- `silver.formatador_silver`
- `silver.mapeador_dominio`
- `staging.staging_arquivo`
- `storage.armazenamento_manifest`
- `storage.bronze_arquivo`
- `storage.escrever_dados`
- `storage.estado_armazenamento`
- `traceback`
- `typing`
- `uuid`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `carregar_overrides_manuais` (function, linhas 50-105)
- `aplicar_overrides_manuais` (function, linhas 107-160)
- `processar_arquivo_individual` (function, linhas 162-357)
- `processar_fichas_comercializadoras` (function, linhas 359-417)

### Docstring do módulo

Serviço principal refatorado do pipeline de fichas de comercializadoras.


---

## `src/app/config_builder.py`

- Linhas: 17
- Bytes: 677
- Codificação: `utf-8`
- SHA-256: `70e131ff82912665892e62669e54027f97661d38dd66ee0053e48de072666dda`

### Imports

- `pathlib`
- `typing`

### Classes

- `AppConfigBuilder` (class, linhas 6-17)

### Funções e métodos

- `__init__` (function, linhas 9-10)
- `resolve_dict` (function, linhas 12-17)

### Docstring do módulo

Builder programático para resolução de caminhos do sistema.


---

## `src/app/consumidores/orquestrador_consumidores.py`

- Linhas: 605
- Bytes: 23380
- Codificação: `utf-8`
- SHA-256: `d51417a7dcc8e13ff7f485303e4b7c149a0d86b8a2d48b94c2a1dc8ccc24f4fd`

### Imports

- `__future__`
- `app.context`
- `common.datas`
- `common.excel`
- `common.hashing`
- `common.identificadores`
- `common.json`
- `common.nulos`
- `common.servico_desduplicacao`
- `common.utils_orquestracao`
- `control.carregador_de_mapeamento`
- `control.layout_catalog`
- `control.logger`
- `control.quality_loader`
- `datetime`
- `domain.auditoria.servico_auditoria`
- `domain.consumidores.classificacao`
- `domain.fichas.derivador_financeiro`
- `domain.fichas.extrator`
- `domain.fichas.validador`
- `pandas`
- `pathlib`
- `relational.facts.fato_alerta_util`
- `silver.documentos_classificados`
- `silver.formatador_silver`
- `silver.mapeador_dominio`
- `staging.staging_arquivo`
- `storage.armazenamento_manifest`
- `storage.bronze_arquivo`
- `storage.escrever_dados`
- `storage.estado_armazenamento`
- `typing`
- `uuid`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `carregar_overrides_manuais` (function, linhas 55-110)
- `aplicar_overrides_manuais` (function, linhas 112-165)
- `processar_arquivo_individual` (function, linhas 167-513)
- `processar_fichas_consumidores` (function, linhas 516-605)

### Docstring do módulo

Serviço principal refatorado do pipeline de fichas de consumidores.


---

## `src/app/context.py`

- Linhas: 92
- Bytes: 2833
- Codificação: `utf-8`
- SHA-256: `7c4799b8ae896eeea3a23f651ee80d0647a05f078b670e1f6e9ecb89180963ae`

### Imports

- `__future__`
- `app.config_builder`
- `common.json`
- `dataclasses`
- `dotenv`
- `logging`
- `os`
- `pathlib`
- `sys`
- `typing`

### Classes

- `AppContext` (class, linhas 22-33) | decorators: dataclass

### Funções e métodos

- `path` (function, linhas 29-30)
- `control_file` (function, linhas 32-33)
- `carregar_contexto` (function, linhas 36-92)

### Docstring do módulo

Carregamento do contexto de execução do sistema BDC.


---

## `src/cli/__init__.py`

- Linhas: 1
- Bytes: 40
- Codificação: `utf-8`
- SHA-256: `c0fea4204125e107b4e18bdffe64ae25285e656a10e210754100fdc2aefb7fb2`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.

### Docstring do módulo

Comandos de linha do sistema BDC.


---

## `src/cli/rodar_fichas_comercializadoras.py`

- Linhas: 52
- Bytes: 1667
- Codificação: `utf-8`
- SHA-256: `ded76cf9e310e90db17e2687075b5f5cfae24710f870c4a2982f55e6b4621fdf`

### Imports

- `app.comercializadoras.orquestrador_comercializadoras`
- `argparse`
- `control.logger`
- `pathlib`
- `pyautogui`
- `src.app.bootstrap`
- `sys`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `criar_analisador` (function, linhas 12-29)
- `main` (function, linhas 32-48)


---

## `src/cli/rodar_fichas_consumidores.py`

- Linhas: 50
- Bytes: 1601
- Codificação: `utf-8`
- SHA-256: `6a9b37827affadef589ce932dc4e381272e4dabcb55ac41cb14025e6feda1d4f`

### Imports

- `app.consumidores.orquestrador_consumidores`
- `argparse`
- `control.logger`
- `pathlib`
- `src.app.bootstrap`
- `sys`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `criar_analisador` (function, linhas 10-27)
- `main` (function, linhas 30-46)


---

## `src/common/__init__.py`

- Linhas: 1
- Bytes: 40
- Codificação: `utf-8`
- SHA-256: `8da5e1c3376bdb71a74c9cda926c3fb1b5a4999da8a293dae8fafb8c948c96d2`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/common/dados.py`

- Linhas: 128
- Bytes: 3581
- Codificação: `utf-8`
- SHA-256: `f4c9349c58834c93dc1f08dd1274e052f122883e1b38d76d06aefee76fb6a22a`

### Imports

- `__future__`
- `collections.abc`
- `common.dominio`
- `common.identificadores`
- `common.numeros`
- `pandas`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `normalizar_coluna_cnpj` (function, linhas 12-54)
- `normalizar_coluna_auditor` (function, linhas 56-73)
- `normalizar_coluna_percentual` (function, linhas 75-98)
- `validar_coluna_cnpj_canonica` (function, linhas 100-117)
- `aplicar_schema_dataframe` (function, linhas 119-121)
- `validar_schema_dataframe` (function, linhas 123-128)


---

## `src/common/datas.py`

- Linhas: 83
- Bytes: 2217
- Codificação: `utf-8`
- SHA-256: `0b71d83bb9293f2fc593edea1f89cb319da85f46f4f877c0ef7f2053124b078f`

### Imports

- `__future__`
- `common.nulos`
- `datetime`
- `pandas`
- `re`
- `typing`
- `warnings`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `normalizar_data` (function, linhas 9-41)
- `normalizar_competencia` (function, linhas 43-49)
- `normalizar_data_demonstracao_financeira` (function, linhas 53-83)


---

## `src/common/dominio.py`

- Linhas: 90
- Bytes: 2156
- Codificação: `utf-8`
- SHA-256: `f237ada9872212a26da1d58acc30d0c46a519c325f0b9737895e18668f70b6fc`

### Imports

- `__future__`
- `collections.abc`
- `common.texto`
- `re`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_criar_indice_aliases` (function, linhas 10-27)
- `normalizar_valor_dominio` (function, linhas 29-60)
- `normalizar_auditor` (function, linhas 62-70)
- `normalizar_agencia` (function, linhas 72-80)
- `normalizar_rating` (function, linhas 82-90)


---

## `src/common/excel.py`

- Linhas: 85
- Bytes: 2851
- Codificação: `utf-8`
- SHA-256: `0c9d939cd7a0c68d6b6db7d493267614da3e29aa0ba7836e68df6bf2d4a8b914`

### Imports

- `__future__`
- `openpyxl`
- `openpyxl.utils`
- `openpyxl.worksheet.worksheet`
- `pathlib`
- `re`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `abrir_pasta` (function, linhas 14-21)
- `fechar_pasta` (function, linhas 23-30)
- `ler_celula` (function, linhas 32-39)
- `localizar_celula_por_regex` (function, linhas 41-85)

### Docstring do módulo

Operações de leitura e fechamento seguro de workbooks Excel.


---

## `src/common/hashing.py`

- Linhas: 21
- Bytes: 534
- Codificação: `utf-8`
- SHA-256: `e3985a2e5d4874fdbe5c302a1ce1dd121710ad8a040bf548e8538115ed8bbea3`

### Imports

- `__future__`
- `hashlib`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `arquivo_hash` (function, linhas 9-21)

### Docstring do módulo

Geração de hash para arquivos do sistema BDC.


---

## `src/common/identificadores.py`

- Linhas: 127
- Bytes: 3308
- Codificação: `utf-8`
- SHA-256: `068b1c7f37064585dcb52c7800100ec97a00a197af4a893e0e47bf411329b3b5`

### Imports

- `__future__`
- `common.nulos`
- `dataclasses`
- `enum`
- `math`
- `re`
- `typing`

### Classes

- `StatusCNPJ` (class, linhas 10-14)
- `ResultadoCNPJ` (class, linhas 18-27) | decorators: dataclass

### Funções e métodos

- `valido` (function, linhas 26-27) | decorators: property
- `_valor_nulo` (function, linhas 31-32)
- `_extrair_digitos_identificador` (function, linhas 34-44)
- `validar_digitos_cnpj` (function, linhas 46-68)
- `calcular_digito` (function, linhas 53-56)
- `normalizar_cnpj_raiz` (function, linhas 70-72)
- `normalizar_cnpj` (function, linhas 74-127)


---

## `src/common/json.py`

- Linhas: 33
- Bytes: 1017
- Codificação: `utf-8`
- SHA-256: `1acf34a81e04873760dcab6f32c7625153b5f3d1834283908746ddff42696521`

### Imports

- `__future__`
- `json`
- `jsonschema`
- `jsonschema.exceptions`
- `logging`
- `pathlib`
- `sys`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `ler_json` (function, linhas 17-21)
- `validar_esquema_json` (function, linhas 24-33)

### Docstring do módulo

Leitura, escrita e validação estrutural de arquivos JSON do sistema BDC.


---

## `src/common/nulos.py`

- Linhas: 31
- Bytes: 862
- Codificação: `utf-8`
- SHA-256: `d6ae48a8d014187b5026a05b97a72150441fbfc77a737e0e9b9594291d295f0b`

### Imports

- `pandas`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `is_nulo_textual` (function, linhas 26-31)

### Docstring do módulo

Definição canônica de valores textuais que devem ser tratados como nulos (vazios).
Centraliza as verificações que antes estavam espalhadas pelo código.


---

## `src/common/numeros.py`

- Linhas: 84
- Bytes: 2424
- Codificação: `utf-8`
- SHA-256: `c4fb6437c9b64aa6cd796f627b6cd828a1e0581fcbef9a10930a66a609a9e895`

### Imports

- `__future__`
- `common.nulos`
- `decimal`
- `math`
- `re`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_texto_numerico` (function, linhas 9-22)
- `to_decimal_br` (function, linhas 24-52)
- `to_float_br` (function, linhas 54-57)
- `to_int_br` (function, linhas 59-64)
- `to_percentual_br` (function, linhas 66-84)


---

## `src/common/paths.py`

- Linhas: 16
- Bytes: 443
- Codificação: `utf-8`
- SHA-256: `2d930628cb2adfb30703b443281259e35098998b05d084d14ffed9f3a88cd7fa`

### Imports

- `__future__`
- `re`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `sanitizar_nome_da_pasta` (function, linhas 11-16)

### Docstring do módulo

Funções utilitárias para nomes de paths e diretórios.


---

## `src/common/servico_desduplicacao.py`

- Linhas: 67
- Bytes: 2085
- Codificação: `utf-8`
- SHA-256: `96c06dbb862b44008d9868c8a2d93253189a1ef9b781c8f0148203d8526e6c90`

### Imports

- `__future__`
- `datetime`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `tem_hash_duplicado` (function, linhas 8-16)
- `tem_chave_de_negocio_duplicada` (function, linhas 18-42)
- `virar_chave_de_negocio_no_historico` (function, linhas 44-67)

### Docstring do módulo

Regras de deduplicação e atualização incremental do sistema.


---

## `src/common/texto.py`

- Linhas: 99
- Bytes: 2017
- Codificação: `utf-8`
- SHA-256: `15c98e40b30aae443db8f0b035afc7d07d1c7ef48cf86fce66ce524443aec382`

### Imports

- `__future__`
- `re`
- `typing`
- `unicodedata`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `texto_ou_none` (function, linhas 20-32)
- `remover_acentos` (function, linhas 35-50)
- `normalizar_texto` (function, linhas 53-75)
- `normalizar_chave_textual` (function, linhas 78-99)


---

## `src/common/utils_orquestracao.py`

- Linhas: 199
- Bytes: 7346
- Codificação: `utf-8`
- SHA-256: `24ef2835bfd06370f87bad1282d66a94dae1714c366335288157b98b755d71bf`

### Imports

- `__future__`
- `app.context`
- `common.paths`
- `datetime`
- `domain.auditoria.servico_auditoria`
- `json`
- `logging`
- `pathlib`
- `staging.descoberta`
- `storage.armazenamento_manifest`
- `storage.estado_armazenamento`
- `storage.operacao_arquivo`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `registrar_rejeicao_json` (function, linhas 22-41)
- `disco_cheio_erro` (function, linhas 44-56)
- `criar_run_id` (function, linhas 59-63)
- `criar_nome_arquivo_padronizado` (function, linhas 65-94)
- `resolver_subpasta_bronze` (function, linhas 97-106)
- `criar_fila_processamento` (function, linhas 108-135)
- `mover_para_rejeitados` (function, linhas 138-168)
- `mover_para_processados` (function, linhas 171-199)

### Docstring do módulo

Funções utilitárias compartilhadas entre os orquestradores do BDC.


---

## `src/control/__init__.py`

- Linhas: 1
- Bytes: 59
- Codificação: `utf-8`
- SHA-256: `d3ca3f3a650cfe2dba096307c2555bde1882db0a709abfc618fe728324844a25`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.

### Docstring do módulo

Carregadores de arquivos de controle do sistema BDC.


---

## `src/control/carregador_de_mapeamento.py`

- Linhas: 73
- Bytes: 2381
- Codificação: `utf-8`
- SHA-256: `623f9ff6574ace3c82363e7948de33e0d031dec66fb84c9729840e74c754dffd`

### Imports

- `__future__`
- `app.context`
- `common.json`
- `logging`
- `pathlib`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `carregar_e_validar_mapeamento` (function, linhas 13-47)
- `mapeamento_de_carga_fichas_comercializadoras` (function, linhas 50-60)
- `mapeamento_de_carga_fichas_consumidores` (function, linhas 63-73)

### Docstring do módulo

Carregamento e validação estrita dos mappings das fichas.


---

## `src/control/layout_catalog.py`

- Linhas: 123
- Bytes: 3850
- Codificação: `utf-8`
- SHA-256: `89ed7f9d677d522a831f5cd944071b45eca1efbe266b05cf6fc3ff99129476eb`

### Imports

- `__future__`
- `app.context`
- `common.json`
- `sys`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `validar_estrutura_do_layout` (function, linhas 12-29)
- `carregar_catalogo_de_layouts` (function, linhas 32-51)
- `carregar_layouts_comercializadoras` (function, linhas 54-87)
- `carregar_layouts_consumidores` (function, linhas 90-123)

### Docstring do módulo

Carregamento e validação dos layouts de fichas.


---

## `src/control/logger.py`

- Linhas: 44
- Bytes: 1294
- Codificação: `utf-8`
- SHA-256: `a7cc9461c938145db6ff54a50b1ed369a6575ebb00c1dd0387ce94971fc184e0`

### Imports

- `__future__`
- `datetime`
- `logging`
- `pathlib`
- `sys`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `obter_logger` (function, linhas 10-44)

### Docstring do módulo

Configuração padronizada de loggers do sistema BDC.


---

## `src/control/quality_loader.py`

- Linhas: 71
- Bytes: 2432
- Codificação: `utf-8`
- SHA-256: `4a3636b5650dfcea38005004b36cb5cf4b1ef1b7db0079d87f5ef41e02cae20e`

### Imports

- `__future__`
- `app.context`
- `common.json`
- `pathlib`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_carregar_e_validar_regras_de_qualidade` (function, linhas 17-47)
- `carregar_regras_de_qualidade_de_dados_comercializadoras` (function, linhas 50-59)
- `carregar_regras_de_qualidade_de_dados_consumidores` (function, linhas 62-71)

### Docstring do módulo

Carregamento e validação estrita das regras de qualidade da entidade.

feat(T1.1.2): Integra validação contra JSON Schema (mesmo padrão de mapping_loader.py).
Regras malformadas geram erro descritivo antes do processamento de qualquer ficha.
Ref: §5.2, §5.3 do Planejamento Funcional.


---

## `src/domain/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/auditoria/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/auditoria/servico_auditoria.py`

- Linhas: 149
- Bytes: 4952
- Codificação: `utf-8`
- SHA-256: `80d1095625535368c2212deeb935572661819c75ac28489e70e8c6ad38194fff`

### Imports

- `__future__`
- `datetime`
- `logging`
- `pandas`
- `pathlib`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `registrar_inicio_pipeline` (function, linhas 21-38)
- `registrar_fim_pipeline` (function, linhas 41-73)
- `registrar_documento` (function, linhas 75-112)
- `registrar_linhagem_campos` (function, linhas 114-149)

### Docstring do módulo

Serviços de Auditoria do Pipeline (§11.5 — Tabelas de Controle).

Registra cada execução do pipeline (ctl_run_pipeline) e cada documento
processado (ctl_documento) em tabelas persistentes.


---

## `src/domain/cadastro/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/cadastro/servico_bureau.py`

- Linhas: 103
- Bytes: 4777
- Codificação: `utf-8`
- SHA-256: `123331af3355a15dbed554e4025d48bc236a6c78504a019f3f03390dd1a899e0`

### Imports

- `__future__`
- `app.context`
- `control.logger`
- `datetime`
- `pandas`
- `pathlib`
- `services.connectors.risk3_connector`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `inserir_dados_bureau` (function, linhas 14-92)
- `_gravar_silver_vazia` (function, linhas 95-103)

### Docstring do módulo

Serviço de Ingestão e Persistência do Bureau RISK3.


---

## `src/domain/cadastro/servico_receita.py`

- Linhas: 144
- Bytes: 6043
- Codificação: `utf-8`
- SHA-256: `0b33c549ce3a8b95dd077f6cf077b724822d494bfce09c99e23b514b5a745b35`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `control.logger`
- `datetime`
- `domain.enums`
- `json`
- `logging`
- `pandas`
- `pathlib`
- `re`
- `relational.facts.fato_alerta_util`
- `services.connectors.receita_connector`
- `shutil`
- `storage.escrever_dados`
- `typing`

### Classes

- `ReceitaIngestionError` (class, linhas 23-24)

### Funções e métodos

- `_listar_cnpjs_de_entrada` (function, linhas 26-51)
- `_salvar_instantaneo_bruto` (function, linhas 53-59)
- `inserir_dados_receita` (function, linhas 63-144)

### Docstring do módulo

Serviço de ingestão e validação cadastral da Receita Federal.


---

## `src/domain/carga_manual/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/carga_manual/servico_carga_manual.py`

- Linhas: 127
- Bytes: 5596
- Codificação: `utf-8`
- SHA-256: `2623b4d64bd402257afa4ef3733a078a15d77d1ed14dd958e50d8657b314ef6b`

### Imports

- `__future__`
- `app.context`
- `common.datas`
- `common.identificadores`
- `common.json`
- `common.numeros`
- `control.logger`
- `datetime`
- `domain.carga_manual.servico_repescagem`
- `logging`
- `pandas`
- `pathlib`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `inserir_dados_carga_manual` (function, linhas 20-127)

### Docstring do módulo

Serviço de Carga Manual e Eventos de Negócio.


---

## `src/domain/carga_manual/servico_repescagem.py`

- Linhas: 73
- Bytes: 4308
- Codificação: `utf-8`
- SHA-256: `e376fcca61814724ac5a172bdc7765a8f95fb3dd67b804d44ce0e9079f5be7e8`

### Imports

- `app.context`
- `common.identificadores`
- `logging`
- `pandas`
- `pathlib`
- `shutil`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `repescar_fichas_alteradas` (function, linhas 7-73)


---

## `src/domain/consumidores/classificacao.py`

- Linhas: 176
- Bytes: 5711
- Codificação: `utf-8`
- SHA-256: `c71546c294a4ce832954903d31105a3788db0b80246891f6afeff72769c2be5c`

### Imports

- `__future__`
- `dataclasses`
- `typing`

### Classes

- `ClassificacaoDocumental` (class, linhas 18-28) | decorators: dataclass

### Funções e métodos

- `_esta_vazio` (function, linhas 52-58)
- `_tem_demonstracoes_financeiras` (function, linhas 61-69)
- `_avaliar_confianca` (function, linhas 72-94)
- `classificar_consumidor` (function, linhas 97-160)
- `criar_classificacao_registro` (function, linhas 163-176)

### Docstring do módulo

Serviço de classificação documental de consumidores.

Determina o tipo de análise exigida (detalhada ou simplificada)
com base no volume contratado, conforme planejamento v1.2.


---

## `src/domain/contrapartes/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/contrapartes/segmentacao.py`

- Linhas: 41
- Bytes: 1245
- Codificação: `utf-8`
- SHA-256: `1a724984a8ba995e174389248435c0c5bef29697b6982010fccf0e198ffc6ed1`

### Imports

- `__future__`
- `common.numeros`
- `common.texto`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `definir_segmento_metodologico` (function, linhas 10-41)

### Docstring do módulo

Segmentação metodológica da contraparte para cálculo de PD.


---

## `src/domain/contrapartes/servico_enquadramento.py`

- Linhas: 130
- Bytes: 4672
- Codificação: `utf-8`
- SHA-256: `eea54a1d6968964310e90eb4bb0103175d901ea983de7e88de71071845c2ad42`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `pandas`
- `pathlib`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `calcular_enquadramento_consumidor` (function, linhas 12-124)
- `_salvar_enquadramento` (function, linhas 126-130)

### Docstring do módulo

Serviço de cálculo do volume de enquadramento (≥ 5 MWm) para consumidores.


---

## `src/domain/contratos/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/contratos/servico_contratos_denodo.py`

- Linhas: 159
- Bytes: 8337
- Codificação: `utf-8`
- SHA-256: `b0d3d6bde2570301062e6e93991187e21967226b13fd91ba60a0b337a1e6d3e3`

### Imports

- `__future__`
- `app.context`
- `calendar`
- `common.dados`
- `datetime`
- `logging`
- `pandas`
- `pathlib`
- `services.connectors.denodo_connector`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `aplicar_regras_negocio_pandas` (function, linhas 20-73)
- `calcular_horas` (function, linhas 39-47)
- `processar_contratos_denodo` (function, linhas 75-159)

### Docstring do módulo

Serviço oficial de ingestão de Contratos Correntes do Denodo.


---

## `src/domain/credito/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/credito/motor_ead.py`

- Linhas: 63
- Bytes: 2075
- Codificação: `utf-8`
- SHA-256: `3fafde1e29cb1c83fce6479d0daa58776e004503f1522a33b3c9131da1919e70`

### Imports

- `__future__`
- `datetime`
- `hashlib`
- `json`
- `typing`
- `uuid`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `calcular_ead` (function, linhas 17-63)

### Docstring do módulo

Motor de Exposure at Default (EAD).

feat(T3.2.1): Adicionados fator de conversão parametrizado e rastreabilidade
com calculo_id e config_snapshot_id.
Ref: §6.7 (Exposição), §7.1, §11.2 (Identificadores) do Planejamento Funcional.


---

## `src/domain/credito/motor_lgd.py`

- Linhas: 85
- Bytes: 2858
- Codificação: `utf-8`
- SHA-256: `15023c941174eb1f923709b8e4bbe9912f34636a5616f5f6f24c088462f4f355`

### Imports

- `__future__`
- `datetime`
- `hashlib`
- `json`
- `typing`
- `uuid`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `calcular_lgd` (function, linhas 28-85)

### Docstring do módulo

Motor de Loss Given Default (LGD).

feat(T3.3.1): Adicionados lookup de LGD bruta por segmento via config e
rastreabilidade com calculo_id.
Ref: §6.8, §7.1, Apêndice C do Planejamento Funcional.

Nota: A redução por garantias é recebida como parâmetro (cobertura_garantias).
A integração com a base real de garantias é um TODO — quando disponível,
o percentual será calculado automaticamente a partir de garantias_service.


---

## `src/domain/credito/motor_pe.py`

- Linhas: 73
- Bytes: 2080
- Codificação: `utf-8`
- SHA-256: `ea0ddfd09b81ec73a5a8fe129f874d06425243267a8cfeb986e39f590ed2d99c`

### Imports

- `__future__`
- `datetime`
- `math`
- `uuid`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_is_missing` (function, linhas 15-22)
- `calcular_perda_esperada` (function, linhas 25-73)

### Docstring do módulo

Motor de Perda Esperada (PE).

feat(T3.4.1): Retorno dual (pe_reais + pe_percentual) e rastreabilidade
com calculo_id.
Ref: §6.7, §11.2, §11.6 (Reconciliação PE) do Planejamento Funcional.


---

## `src/domain/credito/motor_taxa_risco.py`

- Linhas: 88
- Bytes: 2625
- Codificação: `utf-8`
- SHA-256: `f80ca8d72a85b0f51a6f4543c13c80da233477480e58dbdee5b59908d6ff28db`

### Imports

- `__future__`
- `datetime`
- `logging`
- `math`
- `relational.facts.fato_alerta_util`
- `typing`
- `uuid`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_is_missing` (function, linhas 11-18)
- `calcular_taxa_risco` (function, linhas 23-88)


---

## `src/domain/credito/notas_quantitativas_cpura.py`

- Linhas: 167
- Bytes: 5031
- Codificação: `utf-8`
- SHA-256: `fa60b717134a1f87977aea13a7c1a11f925ceedbdc657891c934328db6d3f2af`

### Imports

- `__future__`
- `common.numeros`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_obter_valor_numerico` (function, linhas 14-26)
- `_normalizar_pd` (function, linhas 29-44)
- `_obter_faixas_notas` (function, linhas 47-66)
- `_atribuir_nota_por_faixa` (function, linhas 69-99)
- `calcular_notas_quantitativas_cpura` (function, linhas 102-167)

### Docstring do módulo

Cálculo das notas quantitativas de CPURA.


---

## `src/domain/credito/pd_base.py`

- Linhas: 42
- Bytes: 1055
- Codificação: `utf-8`
- SHA-256: `98cd207f945d3a03d84f52e0abeee3e219fc813191ff6fcc2047dfeee81143e1`

### Imports

- `__future__`
- `common.numeros`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `calcular_pd_base` (function, linhas 11-42)

### Docstring do módulo

Cálculo ou leitura da PD base.


---

## `src/domain/credito/pd_cgrupo.py`

- Linhas: 140
- Bytes: 3983
- Codificação: `utf-8`
- SHA-256: `0adc7252c968f4f5bc24bd862fa8d5510752bd54a9c4f0de2826c6bb98f0efdb`

### Imports

- `__future__`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_norm` (function, linhas 11-12)
- `_norm_agencia` (function, linhas 15-20)
- `_norm_rating` (function, linhas 23-24)
- `_mapear_rating_externo` (function, linhas 27-48)
- `_resolver_rating_cgrupo` (function, linhas 51-75)
- `_pior_rating` (function, linhas 78-84)
- `_percentil_empirico` (function, linhas 87-96)
- `_interpolar_pd` (function, linhas 99-100)
- `calcular_pd_final_cgrupo` (function, linhas 103-140)


---

## `src/domain/credito/pd_consumidor_gt5.py`

- Linhas: 121
- Bytes: 3518
- Codificação: `utf-8`
- SHA-256: `c74acd6e73bbf80bd86f899bb92c65489888d3c779da1a853a941d22f08629a1`

### Imports

- `__future__`
- `domain.credito.pd_exceptions`
- `math`
- `statistics`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_inv_t_aproximado` (function, linhas 15-28)
- `_normalize_pd_input` (function, linhas 31-38)
- `calcular_pd_final_consumidor_gt5` (function, linhas 41-121)

### Docstring do módulo

Transformação da PD para consumidores acima de 5 MWm.


---

## `src/domain/credito/pd_consumidor_le5.py`

- Linhas: 73
- Bytes: 2616
- Codificação: `utf-8`
- SHA-256: `52f0c6d1e1e6a7b437809e4d7dcc5ebc983fe807a4c5f8263fdd03767eb0f968`

### Imports

- `__future__`
- `common.numeros`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `calcular_pd_final_consumidor_le5` (function, linhas 9-73)

### Docstring do módulo

Transformação da PD para consumidores abaixo de 5 MWm (Bureau).


---

## `src/domain/credito/pd_cpura.py`

- Linhas: 282
- Bytes: 8644
- Codificação: `utf-8`
- SHA-256: `f19899024250bcd12ddd9c50c62e0720809bf01e03ff03edf20583bdb354da39`

### Imports

- `__future__`
- `domain.credito.pd_exceptions`
- `math`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_clamp` (function, linhas 14-16)
- `_obter_score_total` (function, linhas 19-40)
- `_obter_faixa_score_rating` (function, linhas 43-78)
- `_obter_estabilizacao` (function, linhas 81-115)
- `_calcular_score_truncado` (function, linhas 118-124)
- `_calcular_posicao_relativa` (function, linhas 127-137)
- `_calcular_pd_bruta` (function, linhas 140-147)
- `_estabilizar_pd` (function, linhas 150-161)
- `calcular_pd_final_cpura` (function, linhas 164-282)

### Docstring do módulo

Transformação de PD para comercializadoras puras.


---

## `src/domain/credito/pd_exceptions.py`

- Linhas: 15
- Bytes: 393
- Codificação: `utf-8`
- SHA-256: `40d069ee1f05d3978202b180a5d4ca89927e99faae914be4c37110c116abda73`

### Imports

- `__future__`

### Classes

- `PdCalculationError` (class, linhas 6-7)
- `PdInputValidationError` (class, linhas 10-11)
- `PdConfigurationError` (class, linhas 14-15)

### Funções e métodos

- Nenhuma função detectada.

### Docstring do módulo

Exceções do motor de probabilidade de default.


---

## `src/domain/credito/pd_motor.py`

- Linhas: 174
- Bytes: 6466
- Codificação: `utf-8`
- SHA-256: `f5d08b23f0649fb8f1bf1442804307aa439484e5be824620503c495681bf9e11`

### Imports

- `__future__`
- `common.texto`
- `domain.credito.notas_quantitativas_cpura`
- `domain.credito.pd_base`
- `domain.credito.pd_exceptions`
- `domain.credito.pd_transform`
- `domain.credito.pd_validator`
- `domain.credito.rating`
- `domain.credito.score_qualitativo`
- `domain.credito.score_quantitativo`
- `domain.credito.score_total`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `calcular_pd_ajustada` (function, linhas 22-174)


---

## `src/domain/credito/pd_transform.py`

- Linhas: 173
- Bytes: 5375
- Codificação: `utf-8`
- SHA-256: `9805676fef28778e94d04caf92ab4b46fa43712db52b32a01ce3825d07ce2f5a`

### Imports

- `__future__`
- `domain.credito.pd_cgrupo`
- `domain.credito.pd_consumidor_gt5`
- `domain.credito.pd_consumidor_le5`
- `domain.credito.pd_cpura`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_obter_faixa_pd` (function, linhas 14-50)
- `transformar_pd_por_segmento` (function, linhas 53-173)

### Docstring do módulo

Despacho da transformação de PD por segmento.


---

## `src/domain/credito/pd_validator.py`

- Linhas: 112
- Bytes: 3932
- Codificação: `utf-8`
- SHA-256: `40c639c2d4b0bba831cd01bbe2c9a3f05fff180d39a8b6ca287b6e0ab180ff76`

### Imports

- `__future__`
- `common.numeros`
- `common.texto`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `validar_probabilidade` (function, linhas 12-19)
- `_is_blank` (function, linhas 22-26)
- `validar_insumos_pd` (function, linhas 29-112)

### Docstring do módulo

Validação dos insumos do cálculo de PD ajustada.


---

## `src/domain/credito/rating.py`

- Linhas: 112
- Bytes: 3339
- Codificação: `utf-8`
- SHA-256: `db149ac548706330ff1be83d0db7801945334f4acbc14c2f1f812ba1f5f79772`

### Imports

- `__future__`
- `common.texto`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_calcular_rating_final_cpura` (function, linhas 14-56)
- `_obter_rating_pronto` (function, linhas 59-86)
- `calcular_rating_final` (function, linhas 89-112)

### Docstring do módulo

Determinação do rating final para o cálculo de PD ajustada.


---

## `src/domain/credito/score_qualitativo.py`

- Linhas: 161
- Bytes: 4798
- Codificação: `utf-8`
- SHA-256: `aad08bf27861e45ce5fc0e918916dc2256b5469dc30670d106ae310fc55bbbbe`

### Imports

- `__future__`
- `common.texto`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_obter_nota_auditoria` (function, linhas 14-31)
- `_obter_peso_nota` (function, linhas 34-57)
- `calcular_score_qualitativo_cpura` (function, linhas 60-161)

### Docstring do módulo

Cálculo do score qualitativo para CPURA.


---

## `src/domain/credito/score_quantitativo.py`

- Linhas: 126
- Bytes: 3938
- Codificação: `utf-8`
- SHA-256: `bd6033eeb004b4a1344f831f57d3a22934ff9682b0bfd048094cd72ba778e1cf`

### Imports

- `__future__`
- `common.texto`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_obter_peso_nota` (function, linhas 14-37)
- `calcular_score_quantitativo_cpura` (function, linhas 40-126)

### Docstring do módulo

Cálculo do score quantitativo para CPURA.


---

## `src/domain/credito/score_total.py`

- Linhas: 49
- Bytes: 1329
- Codificação: `utf-8`
- SHA-256: `e7afb903f278a5c07d4502a4c3b0b138edd5bbe3a89d50b1fce66d1138bc3553`

### Imports

- `__future__`
- `domain.credito.pd_exceptions`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `calcular_score_total_cpura` (function, linhas 10-49)

### Docstring do módulo

Cálculo do score total de CPURA.


---

## `src/domain/credito/servico_override.py`

- Linhas: 96
- Bytes: 4095
- Codificação: `utf-8`
- SHA-256: `ff968f5b595bcd3f3a1042cf3a0b70ef0f24aac6946f0e068fe9321c61ab110f`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `datetime`
- `domain.enums`
- `logging`
- `pandas`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `processar_solicitacao_override` (function, linhas 14-96)

### Docstring do módulo

Serviço de Gestão de Overrides e Exceções (Módulo de Governança).


---

## `src/domain/diagnostico/servico_diagnostico.py`

- Linhas: 129
- Bytes: 6134
- Codificação: `utf-8`
- SHA-256: `93b0879564616de96223e741dd6ec77cd2f62eaeb804ddac28b98a72482fb458`

### Imports

- `common.identificadores`
- `control.logger`
- `datetime`
- `domain.diagnostico.servico_recuperacao`
- `json`
- `os`
- `pandas`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_carregar_catalogo` (function, linhas 10-25)
- `gerar_diagnostico` (function, linhas 27-129)


---

## `src/domain/diagnostico/servico_exportacao.py`

- Linhas: 68
- Bytes: 2884
- Codificação: `utf-8`
- SHA-256: `9f7a16a9a8a441887fb2a3361c78a7fded397f13137d129830e25ad7b25eea81`

### Imports

- `common.identificadores`
- `control.logger`
- `datetime`
- `pandas`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `exportar_carga_manual` (function, linhas 7-68)


---

## `src/domain/diagnostico/servico_recuperacao.py`

- Linhas: 118
- Bytes: 4820
- Codificação: `utf-8`
- SHA-256: `6efce87fd19448128d2fffe3974b4d8e69d80691df35db6fb32bb6327f084ec4`

### Imports

- `common.excel`
- `common.json`
- `control.logger`
- `datetime`
- `domain.fichas.extrator`
- `glob`
- `os`
- `pandas`
- `pathlib`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_encontrar_ficha_bronze` (function, linhas 11-38)
- `_carregar_layouts_dinamico` (function, linhas 40-53)
- `recuperar_pendencias_automaticamente` (function, linhas 55-118)


---

## `src/domain/enums.py`

- Linhas: 126
- Bytes: 3530
- Codificação: `utf-8`
- SHA-256: `a8353187a79b4c8a87f890023a0204025f5c4beb7feae8be5c96b9c2b5f3b253`

### Imports

- `enum`

### Classes

- `TipoFicha` (class, linhas 7-10) | decorators: unique
- `LoadMode` (class, linhas 14-17) | decorators: unique
- `StatusIngestao` (class, linhas 21-26) | decorators: unique
- `StatusClassificacao` (class, linhas 30-34) | decorators: unique
- `StatusExtracao` (class, linhas 38-49) | decorators: unique
- `SegmentoMetodologico` (class, linhas 53-58) | decorators: unique
- `TipoAnalise` (class, linhas 62-66) | decorators: unique
- `SeveridadeAlerta` (class, linhas 70-75) | decorators: unique
- `StatusGarantia` (class, linhas 78-84) | decorators: unique
- `StatusAnalise` (class, linhas 88-94) | decorators: unique
- `StatusDocumento` (class, linhas 98-108) | decorators: unique
- `StatusAlerta` (class, linhas 112-117) | decorators: unique
- `StatusAprovacao` (class, linhas 121-126) | decorators: unique

### Funções e métodos

- Nenhuma função detectada.

### Docstring do módulo

Domínios controlados e enumeradores do sistema BDC.


---

## `src/domain/fichas/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/fichas/derivador_financeiro.py`

- Linhas: 62
- Bytes: 2227
- Codificação: `utf-8`
- SHA-256: `d6750482cec091cee71487d8df95cae7e5c32c50603e8639a1e9dfa732f710ad`

### Imports

- `logging`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `divisao_segura` (function, linhas 5-15)
- `calcular_indicadores_derivados` (function, linhas 17-62)


---

## `src/domain/fichas/extrator.py`

- Linhas: 469
- Bytes: 19872
- Codificação: `utf-8`
- SHA-256: `626ac496779a5f0fc2f8f9d371d2bb858e56b36aa1be9efba6a1df9069d8a088`

### Imports

- `__future__`
- `common.nulos`
- `common.texto`
- `datetime`
- `logging`
- `math`
- `openpyxl.utils`
- `openpyxl.utils.cell`
- `openpyxl.utils.datetime`
- `re`
- `time`
- `typing`
- `warnings`

### Classes

- `LeitorPlanilha` (class, linhas 20-46)

### Funções e métodos

- `__init__` (function, linhas 22-25)
- `do_workbook` (function, linhas 28-34) | decorators: classmethod
- `ler_celula` (function, linhas 36-46)
- `analisar_data_com_seguranca` (function, linhas 48-64)
- `valor_extraido_limpo` (function, linhas 66-127)
- `_tipo_extraido_valido` (function, linhas 129-193)
- `busca_omnidirecional` (function, linhas 195-238)
- `extrair_registro` (function, linhas 240-399)
- `avaliar_vencedor_por_grid` (function, linhas 401-463)
- `norm_tab` (function, linhas 419-421)
- `extrair_registro_do_vencedor` (function, linhas 466-469)


---

## `src/domain/fichas/validador.py`

- Linhas: 275
- Bytes: 10913
- Codificação: `utf-8`
- SHA-256: `a9916ffc8f3333679050702c721bf34a81d5242f27efde2d54d50db6b1282792`

### Imports

- `__future__`
- `common.nulos`
- `json`
- `jsonschema`
- `pandas`
- `pathlib`
- `typing`

### Classes

- `DomainRuleEngine` (class, linhas 14-75)

### Funções e métodos

- `_is_empty` (function, linhas 6-12)
- `__init__` (function, linhas 17-19)
- `validate` (function, linhas 21-75)
- `validar_schema` (function, linhas 82-127)
- `validar_registro` (function, linhas 130-191)
- `validar_registro_consumidor` (function, linhas 194-275)

### Docstring do módulo

Validação técnica e de domínio unificada dos registros extraídos.


---

## `src/domain/garantias/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/garantias/servico_garantia.py`

- Linhas: 105
- Bytes: 4289
- Codificação: `utf-8`
- SHA-256: `a0da57abfefaea7d53f1fc9d133ab22606fe68580773a2170a4bc9b837d45cef`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `control.logger`
- `datetime`
- `pandas`
- `pathlib`
- `shutil`
- `storage.escrever_dados`
- `typing`

### Classes

- `GarantiaIngestionError` (class, linhas 21-22)

### Funções e métodos

- `inserir_dados_garantias` (function, linhas 26-105)

### Docstring do módulo

Serviço de ingestão, validação e alertas de Garantias.

Lê o CSV extraído da query customizada do Denodo, salva na Bronze,
valida regras de vigência e cobertura, gera alertas e publica na Silver.
Ref: §2 (Módulo Garantias), §6.8 do Planejamento Funcional.


---

## `src/domain/mtm/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/mtm/servico_mtm.py`

- Linhas: 131
- Bytes: 5459
- Codificação: `utf-8`
- SHA-256: `9b22bf1e4d3295aa31dcd91a0221b969970dd2663cec267b2b19f76bda06fe8f`

### Imports

- `__future__`
- `app.context`
- `control.logger`
- `datetime`
- `pandas`
- `pathlib`
- `services.connectors.mtm_connector`
- `shutil`
- `storage.escrever_dados`
- `typing`

### Classes

- `MtmReconciliationError` (class, linhas 23-24)

### Funções e métodos

- `inserir_dados_mtm` (function, linhas 27-131)

### Docstring do módulo

Serviço de ingestão e agregação da base de MtM para as camadas Bronze e Silver.

fix(T2.2.2): Removida lógica duplicada (leitura antiga via MTM_NETWORK_PATH
que salvava Bronze duas vezes). Mantido apenas o fluxo via mtm_connector.
Ref: §3.5, §11.6 do Planejamento Funcional.


---

## `src/domain/salesforce/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/domain/salesforce/servico_salesforce.py`

- Linhas: 126
- Bytes: 5342
- Codificação: `utf-8`
- SHA-256: `0774a68a31bbfe1d709e98c12041ebaf92376ab31fd93e7e663eece8220651c3`

### Imports

- `__future__`
- `app.context`
- `control.logger`
- `datetime`
- `pandas`
- `pathlib`
- `services.connectors.salesforce_connector`
- `shutil`
- `storage.escrever_dados`
- `typing`

### Classes

- `SalesforceIngestionError` (class, linhas 18-19)

### Funções e métodos

- `inserir_dados_salesforce` (function, linhas 22-126)
- `enriquecer_com_cnpj` (function, linhas 68-83)

### Docstring do módulo

Serviço de ingestão e normalização da base do Salesforce.


---

## `src/gold/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/gold/regras_gold.py`

- Linhas: 142
- Bytes: 4821
- Codificação: `utf-8`
- SHA-256: `c9518fc3cb8e674aebba2a09020df4a8dbc9fe03c8f184029137f1bbeea158cd`

### Imports

- `__future__`
- `app.context`
- `common.nulos`
- `json`
- `pandas`
- `pathlib`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_load_status_domains` (function, linhas 11-29)
- `_safe_str` (function, linhas 33-37)
- `checar_contrato_obrigatorio` (function, linhas 39-48)
- `resolver_situacao_df` (function, linhas 50-70)
- `resolver_situacao_analise` (function, linhas 72-101)
- `classificar_exigencia` (function, linhas 103-123)
- `status_metodologia` (function, linhas 125-142)

### Docstring do módulo

Regras de Negócio e Classificação da Visão Consolidada Gold.


---

## `src/gold/servico_gold.py`

- Linhas: 509
- Bytes: 26639
- Codificação: `utf-8`
- SHA-256: `9953e3f1e7831d1e6d5fcab2fe6798c1baae5a5acebcd78b30bc0f9dca28ae12`

### Imports

- `common.dados`
- `common.identificadores`
- `common.nulos`
- `control.logger`
- `datetime`
- `gold.regras_gold`
- `logging`
- `pandas`
- `pathlib`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `carregar_entradas_gold` (function, linhas 17-83)
- `salvar_visao_gold` (function, linhas 85-99)
- `construir_visao_consolidada` (function, linhas 101-474)
- `extrair_rating_valido` (function, linhas 145-151)
- `extrair_pd_valido` (function, linhas 153-159)
- `exportar_visao_consolidada_gold` (function, linhas 476-509)


---

## `src/relational/dimensions/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/relational/dimensions/dim_contraparte.py`

- Linhas: 89
- Bytes: 4632
- Codificação: `utf-8`
- SHA-256: `73d2734e2e5fe0bf781bda66192ef275d9ba65b5752ee6923d65048fb1c17347`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `datetime`
- `logging`
- `pandas`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `criar_dim_contraparte` (function, linhas 11-89)

### Docstring do módulo

Serviço de consolidação da Dimensão de Contraparte.


---

## `src/relational/facts/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/relational/facts/fato_alerta_util.py`

- Linhas: 134
- Bytes: 5831
- Codificação: `utf-8`
- SHA-256: `560e0a1056c94affa33d93150d8c15785cf13b4094863dd6597e952b89931a34`

### Imports

- `datetime`
- `pandas`
- `pathlib`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `registrar_alerta` (function, linhas 7-74)
- `registrar_alertas_em_lote` (function, linhas 76-134)

### Docstring do módulo

Serviço de registro unificado de alertas no modelo Star Schema (Fato Alerta).


---

## `src/relational/facts/fato_alertas.py`

- Linhas: 136
- Bytes: 6121
- Codificação: `utf-8`
- SHA-256: `9f7395b590bcb6a02f8faf0de518b3b75c94e85d336c9d61039fb4c3c5d613d4`

### Imports

- `control.logger`
- `datetime`
- `pandas`
- `pathlib`
- `relational.facts.fato_alerta_util`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `gerar_fato_alertas_credito` (function, linhas 10-135)

### Docstring do módulo

Serviço de geração de alertas de crédito no padrão Star Schema (Fato Alerta).


---

## `src/relational/facts/fato_alertas_manuais.py`

- Linhas: 142
- Bytes: 6481
- Codificação: `utf-8`
- SHA-256: `6bbba55379f649acda1edb70691d0829563751556acc2dc78b6844b06e2e49d5`

### Imports

- `control.logger`
- `datetime`
- `pandas`
- `pathlib`
- `relational.facts.fato_alerta_util`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `gerar_fato_alertas_manuais` (function, linhas 10-142)

### Docstring do módulo

Serviço de geração de alertas da esteira de Carga Manual e Exceções (MAN_* e EXC_*).


---

## `src/relational/facts/fato_analise_credito.py`

- Linhas: 156
- Bytes: 7683
- Codificação: `utf-8`
- SHA-256: `8c1594e1fe254940444a131e3a5b6767c545aeaf74a6d6bedcf732d2afac6659`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `common.json`
- `control.logger`
- `datetime`
- `domain.contrapartes.segmentacao`
- `domain.credito.pd_exceptions`
- `domain.credito.pd_motor`
- `logging`
- `pandas`
- `pathlib`
- `relational.facts.fato_alerta_util`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `construir_fato_analise_credito` (function, linhas 17-156)

### Docstring do módulo

Construção da tabela Fato de Análise de Crédito e Execução do Motor de Risco.


---

## `src/relational/facts/fato_exposicao_risco.py`

- Linhas: 122
- Bytes: 6206
- Codificação: `utf-8`
- SHA-256: `a930e59730131b3f69f470f2c38782d365b6c922a104f396d5ec79b295ad863c`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `control.logger`
- `datetime`
- `domain.credito.motor_ead`
- `domain.credito.motor_lgd`
- `domain.credito.motor_pe`
- `domain.credito.motor_taxa_risco`
- `logging`
- `math`
- `pandas`
- `pathlib`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `construir_fato_exposicao_risco` (function, linhas 19-122)

### Docstring do módulo

Serviço de construção da tabela Fato Exposição de Risco.


---

## `src/relational/facts/fato_garantia.py`

- Linhas: 151
- Bytes: 5976
- Codificação: `utf-8`
- SHA-256: `848f5a631f5d935a5bcb33a4687500ef270ffc4f0be26666069873cf71f1e8ce`

### Imports

- `__future__`
- `app.context`
- `control.logger`
- `datetime`
- `domain.enums`
- `logging`
- `pandas`
- `pathlib`
- `relational.facts.fato_alerta_util`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `gerar_fato_garantia` (function, linhas 17-151)

### Docstring do módulo

Serviço de construção da tabela Fato Garantia (Star Schema).


---

## `src/relational/facts/fato_reconciliacao_contrato_mtm.py`

- Linhas: 174
- Bytes: 7574
- Codificação: `utf-8`
- SHA-256: `3cf48f5936a9e1de78c2e57a5746ee32fb86f13ac5c040125b884819a56cf92b`

### Imports

- `__future__`
- `app.context`
- `control.logger`
- `datetime`
- `domain.enums`
- `numpy`
- `pandas`
- `pathlib`
- `relational.facts.fato_alerta_util`
- `storage.escrever_dados`
- `typing`

### Classes

- `ReconciliacaoDataError` (class, linhas 19-20)

### Funções e métodos

- `executar_reconciliacao_denodo_mtm` (function, linhas 22-174)

### Docstring do módulo

Serviço de reconciliação entre contratos do Denodo e posições consolidadas de MtM.


---

## `src/relational/facts/fato_reconciliacao_fichas_salesforce.py`

- Linhas: 127
- Bytes: 5443
- Codificação: `utf-8`
- SHA-256: `009ac40145dde5e412a4a5538392d8829f043ed2271eb631cb995727e13e78c6`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `control.logger`
- `datetime`
- `pandas`
- `pathlib`
- `relational.facts.fato_alerta_util`
- `storage.escrever_dados`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `executar_reconciliacao_fichas_salesforce` (function, linhas 20-127)

### Docstring do módulo

Serviço de Reconciliação: Fichas de Crédito vs Salesforce.
Verifica se todas as contrapartes com ficha de crédito estão devidamente cadastradas no CRM.


---

## `src/services/__init__.py`

- Linhas: 1
- Bytes: 49
- Codificação: `utf-8`
- SHA-256: `5f0bf3cdfde1cd820db7f9f9600ef1bd072706c5ad66c8346056f5a892d97968`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.

### Docstring do módulo

Serviços de processamento do sistema BDC.


---

## `src/services/connectors/__init__.py`

- Linhas: 0
- Bytes: 0
- Codificação: `utf-8`
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.


---

## `src/services/connectors/denodo_connector.py`

- Linhas: 133
- Bytes: 4385
- Codificação: `utf-8`
- SHA-256: `9f222d90009ffadcb8f8c6017ac200b58115e1169a8f125a9c638269515b2e19`

### Imports

- `__future__`
- `logging`
- `os`
- `pandas`
- `pathlib`
- `requests`
- `requests.auth`
- `time`
- `typing`
- `urllib3`

### Classes

- `DenodoConnectionError` (class, linhas 29-30)

### Funções e métodos

- `_solicitacao_com_tentativa` (function, linhas 33-58)
- `_encontrar_arquivo_bronze_recente` (function, linhas 61-71)
- `buscar_denodo` (function, linhas 74-133)

### Docstring do módulo

Conector central para o virtualizador Denodo via API RESTful.

feat(T2.1.1): Adicionados retry com backoff exponencial e fallback para
último snapshot Bronze em caso de indisponibilidade.
Ref: §3.4 do Planejamento Funcional.


---

## `src/services/connectors/mtm_connector.py`

- Linhas: 78
- Bytes: 3977
- Codificação: `utf-8`
- SHA-256: `6451c86efac9d455f89c226d7764f7a11e0e01269d462e4025fba38265b06f00`

### Imports

- `__future__`
- `common.dados`
- `datetime`
- `pandas`
- `pathlib`
- `typing`

### Classes

- `MtmConnectionError` (class, linhas 11-12)

### Funções e métodos

- `_encontrar_arquivo_mtm_recente` (function, linhas 14-17)
- `buscar_mtm_consolidado` (function, linhas 19-78)

### Docstring do módulo

Conector de integração com a base de MtM (Risco de Mercado).


---

## `src/services/connectors/receita_connector.py`

- Linhas: 177
- Bytes: 7315
- Codificação: `utf-8`
- SHA-256: `876316b9086c26db78c4b1f5c4a5157da736742100b45b7b77935da308e883de`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `datetime`
- `json`
- `logging`
- `pandas`
- `pathlib`
- `requests`
- `time`
- `typing`
- `urllib3`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_cache_path` (function, linhas 21-22)
- `_load_cache` (function, linhas 24-38)
- `_save_cache` (function, linhas 40-43)
- `_is_cache_valido` (function, linhas 45-52)
- `_consultar_cnpj_brasilapi` (function, linhas 54-118)
- `buscar_receita_dados_lote` (function, linhas 120-177)


---

## `src/services/connectors/risk3_connector.py`

- Linhas: 186
- Bytes: 9295
- Codificação: `utf-8`
- SHA-256: `ee62e86a2bdb06f884937c76824b13702295b328e40a6914f89b8f7f969bfec8`

### Imports

- `__future__`
- `app.context`
- `common.identificadores`
- `control.logger`
- `datetime`
- `dateutil.relativedelta`
- `json`
- `logging`
- `math`
- `os`
- `pandas`
- `pathlib`
- `requests`
- `time`
- `typing`
- `urllib3`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_obter_token_auth` (function, linhas 21-49)
- `buscar_bureau_risk3` (function, linhas 51-186)

### Docstring do módulo

Conector oficial para a API Expresso RISK3 (Bureau de Crédito).


---

## `src/services/connectors/salesforce_connector.py`

- Linhas: 66
- Bytes: 2341
- Codificação: `utf-8`
- SHA-256: `29db84cdaf229231e2ef7fc7e80efacb44517cd25ac830903382cbe6636ba3c5`

### Imports

- `__future__`
- `common.identificadores`
- `pandas`
- `pathlib`
- `typing`

### Classes

- `SalesforceConnectionError` (class, linhas 10-11)

### Funções e métodos

- `buscar_salesforce_dados` (function, linhas 14-66)

### Docstring do módulo

Conector de integração de arquivos extraídos do Salesforce (via Power Query).


---

## `src/silver/__init__.py`

- Linhas: 1
- Bytes: 36
- Codificação: `utf-8`
- SHA-256: `156ba1160b561672f49fccf03aeff8141ef1478dbcff7690ffbe35416138e6fb`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.

### Docstring do módulo

Camada silver do sistema BDC.


---

## `src/silver/documentos_classificados.py`

- Linhas: 21
- Bytes: 562
- Codificação: `utf-8`
- SHA-256: `ab95651cdadd95007d7e85dfe1c7167c1c6087ecab0fa6b20d35d761ff5edf6c`

### Imports

- `__future__`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `criar_documento_classificado` (function, linhas 3-21)


---

## `src/silver/formatador_silver.py`

- Linhas: 98
- Bytes: 4302
- Codificação: `utf-8`
- SHA-256: `d9ec3686987b5f0cb9cc67a843e4f611a5a3ecc7f7fe3141c8b0f7442fc39778`

### Imports

- `__future__`
- `app.context`
- `common.datas`
- `common.identificadores`
- `common.numeros`
- `common.texto`
- `datetime`
- `pathlib`
- `re`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `normalizar_registro` (function, linhas 18-98)

### Docstring do módulo

Normalização técnica das fichas.


---

## `src/silver/mapeador_dominio.py`

- Linhas: 91
- Bytes: 2967
- Codificação: `utf-8`
- SHA-256: `b6147a259b175dae408fb259469a06772274241983d191f7e03961928d12459d`

### Imports

- `__future__`
- `app.context`
- `common.dominio`
- `json`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `aplicar_normalizacao_de_dominio` (function, linhas 14-91)


---

## `src/staging/__init__.py`

- Linhas: 1
- Bytes: 40
- Codificação: `utf-8`
- SHA-256: `34854bdbb0e8e62d0877ff38c278a527e5ac5689874b5603d03524371a15f570`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.

### Docstring do módulo

Camada de staging do sistema BDC.


---

## `src/staging/descoberta.py`

- Linhas: 47
- Bytes: 1797
- Codificação: `utf-8`
- SHA-256: `d81d5a9242d289958b6988696bed36d490e4656ef086ecba651c708f8758b860`

### Imports

- `__future__`
- `dataclasses`
- `hashlib`
- `pathlib`

### Classes

- `ArquivoDescoberto` (class, linhas 10-15) | decorators: dataclass

### Funções e métodos

- `descobrir_arquivos_excel` (function, linhas 17-42)
- `detectar_arquivos_excel_pendentes` (function, linhas 44-47)

### Docstring do módulo

Descoberta de arquivos pendentes para processamento.


---

## `src/staging/staging_arquivo.py`

- Linhas: 19
- Bytes: 485
- Codificação: `utf-8`
- SHA-256: `ff5e2a70d416e7f7abe70b473d764875c63709c5ce0436b9cb745210d82ffda0`

### Imports

- `__future__`
- `pathlib`
- `shutil`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `copiar_para_staging` (function, linhas 7-19)


---

## `src/storage/__init__.py`

- Linhas: 1
- Bytes: 54
- Codificação: `utf-8`
- SHA-256: `39ab5aea815e70a328edec6d01393b78a687554950e5a2a04d1ba6ab1f1ca850`

### Imports

- Nenhum import detectado.

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- Nenhuma função detectada.

### Docstring do módulo

Camada de persistência física do sistema BDC.


---

## `src/storage/armazenamento_manifest.py`

- Linhas: 26
- Bytes: 943
- Codificação: `utf-8`
- SHA-256: `7903c1418dd5327885c9f4361a306217038d71e127cdcd532a34f79e1790c827`

### Imports

- `json`
- `pathlib`
- `typing`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `anexar_registro_de_manifesto` (function, linhas 5-11)
- `historico_de_ingestao_de_carga` (function, linhas 13-26)


---

## `src/storage/bronze_arquivo.py`

- Linhas: 18
- Bytes: 465
- Codificação: `utf-8`
- SHA-256: `56460ec5cc7fee217b72f5b7c561d9de659c17592dbcce3f9d044590ad740b05`

### Imports

- `__future__`
- `pathlib`
- `shutil`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `publicar_arquivo_bruto` (function, linhas 7-18)


---

## `src/storage/escrever_dados.py`

- Linhas: 186
- Bytes: 7647
- Codificação: `utf-8`
- SHA-256: `6fb92b1ecbbe800def74870db084fa1c6ea562d361ff0376d9ab3ccd5f03bf34`

### Imports

- `json`
- `logging`
- `pandas`
- `pathlib`
- `typing`
- `warnings`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `_normalize_filename` (function, linhas 9-16)
- `escrever_conjunto_de_dados_silver` (function, linhas 18-67)
- `mesclar_conjunto_de_dados_prata_por_chave_de_negocio` (function, linhas 69-186)


---

## `src/storage/estado_armazenamento.py`

- Linhas: 72
- Bytes: 2959
- Codificação: `utf-8`
- SHA-256: `958582422f8d2ee2991a2354696370f48233e4048f3f8549523d98dc43666b08`

### Imports

- `__future__`
- `dataclasses`
- `domain.enums`
- `typing`

### Classes

- `DocumentManifest` (class, linhas 16-72) | decorators: dataclass

### Funções e métodos

- `__post_init__` (function, linhas 40-64)
- `to_dict` (function, linhas 66-72)

### Docstring do módulo

Estruturas de estado e manifesto do processamento.


---

## `src/storage/operacao_arquivo.py`

- Linhas: 32
- Bytes: 795
- Codificação: `utf-8`
- SHA-256: `b3e837da233860aa1d3049268a1d8f39e23a1adb1aff8b13a73b920e4e3f5a6a`

### Imports

- `__future__`
- `pathlib`
- `shutil`
- `time`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `mover_arquivo_com_tentativa_adicional` (function, linhas 8-32)


---

## `src/ui/app.py`

- Linhas: 45
- Bytes: 1145
- Codificação: `utf-8`
- SHA-256: `1b927dd2eb4066e85524c45e73c40b2a6a71c555fae482a68ea8255c9ad5d906`

### Imports

- `pathlib`
- `streamlit`
- `sys`
- `ui.views.visao_carga_manual`
- `ui.views.visao_carteira`
- `ui.views.visao_orquestrador`
- `ui.views.visao_silver`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `main` (function, linhas 18-42)


---

## `src/ui/views/visao_carga_manual.py`

- Linhas: 308
- Bytes: 15581
- Codificação: `utf-8`
- SHA-256: `676ed06dc31a745fb12a655c6073f894425a0ac3d61539ce09c24c07a2606adc`

### Imports

- `common.datas`
- `common.identificadores`
- `domain.diagnostico.servico_diagnostico`
- `domain.diagnostico.servico_exportacao`
- `json`
- `os`
- `pandas`
- `pathlib`
- `streamlit`
- `sys`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `formatar_cnpj_canonico` (function, linhas 32-34)
- `formatar_data_canonica` (function, linhas 36-38)
- `montar_chave_pendencia` (function, linhas 40-44)
- `carregar_dados` (function, linhas 46-63)
- `salvar_form_rascunho` (function, linhas 65-102)
- `limpar_rascunho` (function, linhas 104-106)
- `render_visao_carga_manual` (function, linhas 108-308)


---

## `src/ui/views/visao_carteira.py`

- Linhas: 278
- Bytes: 12613
- Codificação: `utf-8`
- SHA-256: `ca35059c92d4e51ad08291aaae3fe58b49f5342ad4a101f22a5c1feb376a5505`

### Imports

- `os`
- `pandas`
- `pathlib`
- `streamlit`
- `sys`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `ler_parquet_ou_csv` (function, linhas 12-37)
- `carregar_dados_carteira` (function, linhas 39-125)
- `render_visao_carteira` (function, linhas 127-278)


---

## `src/ui/views/visao_orquestrador.py`

- Linhas: 111
- Bytes: 4308
- Codificação: `utf-8`
- SHA-256: `87fdc451ce9d1906806db88a7e17d01ed1eb7fc69e2644ef68e440579550a410`

### Imports

- `datetime`
- `os`
- `pathlib`
- `streamlit`
- `subprocess`
- `sys`
- `time`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `obter_ultimo_log_runner` (function, linhas 11-32)
- `render_visao_orquestrador` (function, linhas 34-111)


---

## `src/ui/views/visao_silver.py`

- Linhas: 208
- Bytes: 9375
- Codificação: `utf-8`
- SHA-256: `ce48c46304579ee762f5caddff1f83079cfb245ca3d5b535adc22236c4679a01`

### Imports

- `common.datas`
- `common.identificadores`
- `json`
- `os`
- `pandas`
- `pathlib`
- `streamlit`
- `sys`

### Classes

- Nenhuma classe detectada.

### Funções e métodos

- `ler_arquivo_silver` (function, linhas 28-44)
- `registrar_correcao_rascunho` (function, linhas 46-80)
- `render_visao_silver` (function, linhas 82-208)
- `aplicar_filtro` (function, linhas 143-163)
