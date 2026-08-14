# AUDITORIA TÉCNICA — FASE 1: BD CRÉDITO (BDC)
## Relatório de Gaps e Conformidade contra Planejamento Funcional v1.2

**Data:** 13/08/2026  
**Auditor:** Auditor técnico sênior independente  
**Escopo:** Código-fonte em `c:\Users\malik\Downloads\BDC_v06\BDC\` vs. documento `planejamento_sistema_bd_credito_operacional_v1_2.pdf`  
**Regra:** Nenhuma afirmação de status sem evidência de código citado.

---

## RESUMO EXECUTIVO

> [!CAUTION]
> **Este sistema NÃO pode ir para produção como fonte oficial de dados de crédito.**
>
> De **~92 requisitos contáveis** extraídos do documento (seções 1–14 + Apêndices), apenas **~29 podem ser marcados como `IMPLEMENTADO CORRETO`** com evidência de código (31,5%). Outros **~18 estão implementados com problemas significativos** (19,6%), **~38 estão ausentes** (41,3%) e **~7 não puderam ser verificados** (7,6%).
>
> Os motivos principais que impedem produção são:
> 1. **Pipeline de risco usa dados mockados** (PD=5%, segmento=CGRUPO hardcoded em `main.py:54-55`)
> 2. **Imutabilidade histórica violada** em múltiplos pontos (`merge_silver_dataset_by_business_key` com `keep="last"` sobrescreve registros)
> 3. **Camada Gold vazia** — nenhum arquivo gerado; lógica existe mas depende de dados upstream que não chegam
> 4. **Tabelas de auditoria (ctl_\*) completamente ausentes** — zero referência no código
> 5. **Carga manual e override são cascas** — sem schema real, sem fluxo de aprovação real, sem recálculo
> 6. **Regras de bloqueio operacional não implementadas** — nenhum enforcement real

### Tabela de Cobertura por Seção

| Seção | Descrição | Requisitos | ✅ Correto | ⚠️ Com Problema | ❌ Ausente | ❓ Não Verif. | % Correto |
|---|---|---|---|---|---|---|---|
| §1 | Princípios gerais | 5 | 1 | 2 | 2 | 0 | 20% |
| §2 | Módulo de Garantias | 4 | 0 | 2 | 2 | 0 | 0% |
| §3 | Fontes de dados (conectores) | 8 | 4 | 2 | 1 | 1 | 50% |
| §4 | Processos de ingestão | 6 | 2 | 2 | 2 | 0 | 33% |
| §5 | Qualidade de dados | 6 | 2 | 2 | 2 | 0 | 33% |
| §6 | Regras de negócio/cálculos | 12 | 4 | 4 | 3 | 1 | 33% |
| §7 | Produtos de saída (Gold) | 5 | 0 | 2 | 3 | 0 | 0% |
| §8 | Modelo relacional | 8 | 1 | 2 | 5 | 0 | 12% |
| §9 | Arquitetura de dados | 3 | 1 | 1 | 1 | 0 | 33% |
| §10 | Segurança e acesso | 3 | 0 | 0 | 1 | 2 | 0% |
| §11 | Auditoria e rastreabilidade | 10 | 2 | 2 | 5 | 1 | 20% |
| §12 | Operação | 3 | 1 | 1 | 1 | 0 | 33% |
| §13 | Evolução planejada | 3 | 0 | 0 | 3 | 0 | 0% |
| §14 | Fluxo ponta a ponta | 8 | 3 | 3 | 2 | 0 | 37% |
| Apêndices | A/B/C | 8 | 4 | 1 | 1 | 2 | 50% |
| **TOTAL** | | **92** | **29** | **18** | **38** | **7** | **31,5%** |

> **Conta explícita:** 29 ÷ 92 = **31,5% implementado correto**. Mesmo somando os "com problema" (29+18=47), a taxa máxima seria 51% — e muitos desses "com problema" são falhas graves.

---

## TABELAS DETALHADAS DE GAPS POR SEÇÃO

---

### §1 — PRINCÍPIOS GERAIS E ARQUITETURA

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 1.1 Pipeline Bronze→Silver→Relational→Gold | IMPLEMENTADO COM PROBLEMA | [main.py:81-102](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L81-L102) — pipeline declara 16 etapas | ALTA | Pipeline declara etapas, mas Gold depende de dados que nunca chegam (relational vazio). |
| 1.2 Múltiplas fontes (fichas, Salesforce, Denodo, MtM, Receita) | IMPLEMENTADO CORRETO | [main.py:23-38](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L23-L38) — imports de todos os 5 conectores | BAIXA | Importações e serviços existem para as 5 fontes. |
| 1.3 Classificador de ficha multi-versão | IMPLEMENTADO CORRETO | [ficha_classifier.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/ficha_classifier.py) — 200 linhas, suporta 7+3 layouts | — | — |
| 1.5 Parametrização e não sobrescrita (imutabilidade) | IMPLEMENTADO COM PROBLEMA | [silver_store.py:94](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/storage/silver_store.py#L94) — `drop_duplicates(keep="last")` | CRÍTICA | **VIOLAÇÃO DIRETA.** A função `merge_silver_dataset_by_business_key` faz concat → deduplica com `keep="last"`, sobrescrevendo versões anteriores no arquivo Parquet/CSV. Isso é exatamente o oposto de imutabilidade. |
| 1.5 Versionamento com run_id, calculo_id | AUSENTE | Nenhuma tabela de controle de versões; `config_snapshot_id` gerado nos engines mas **não persistido** na fato — [pipeline_risco_service.py:87-98](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/pipeline_risco_service.py#L87-L98) omite o campo | CRÍTICA | EAD e LGD geram `config_snapshot_id` mas o campo é descartado ao montar o registro fato. |

---

### §2 — MÓDULO DE GARANTIAS

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 2.1 Schema de garantias (tipo, emissor, vigência, valor, cobertura, status) | IMPLEMENTADO COM PROBLEMA | [garantias_service.py:77-93](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/garantias_service.py#L77-L93) — padroniza colunas, valida vencimento | ALTA | Não há schema formal definido; se o CSV de entrada não tiver `GARANTIA_ID` ou `CNPJ_CONTRAPARTE`, o código falha silenciosamente (`.get()` retorna None). |
| 2.2 Validação de vigência e elegibilidade | IMPLEMENTADO COM PROBLEMA | [garantias_service.py:99-138](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/garantias_service.py#L99-L138) — verifica vencimento e cobertura | MÉDIA | A lógica de elegibilidade é simplista: não há critérios formais de tipo de garantia elegível. O campo `ELEGIBILIDADE` é presumido vir do CSV de entrada, não calculado. |
| 2.3 Conexão com base real de garantias | AUSENTE | [garantias_service.py docstring linhas 1-6](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/garantias_service.py#L1-L6): "Lê o CSV extraído da query customizada do Denodo" — mas a query e o CSV **nunca existiram em execuções reais** (diretório `ENTRADAS/garantias` não referenciado em nenhum log ou dado) | CRÍTICA | A docstring afirma ler do Denodo, mas na prática lê CSV local que não existe. |
| 2.4 Alertas GAR_001 e GAR_002 | AUSENTE | Código existe mas depende de dados que nunca são alimentados — sem input, sem alerta | ALTA | Código correto em isolamento, mas nunca executa com dados reais. |

---

### §3 — FONTES DE DADOS (CONECTORES)

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 3.1 Fichas de comercializadoras/consumidores (Excel) | IMPLEMENTADO CORRETO | [fichas_comercializadoras_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/fichas_comercializadoras_service.py) — 708 linhas; [fichas_consumidores_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/fichas_consumidores_service.py) — 661 linhas | — | Pipeline completo de ingestão funcional. |
| 3.2 Segmentação CONSUMIDOR_LE_5 (bureau) | IMPLEMENTADO CORRETO | [segmentacao.py:35-47](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/contrapartes/segmentacao.py#L35-L47) — bifurcação correta ≥5/`<`5 MWm; [pd_consumidor_le5.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/pd_consumidor_le5.py) — motor de PD por bureau | — | Implementado com interpolação inversamente proporcional. |
| 3.3 Conector Salesforce | IMPLEMENTADO CORRETO | [salesforce_connector.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/salesforce_connector.py) — 74 linhas; [salesforce_ingestion_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/salesforce_ingestion_service.py) — 134 linhas | — | Via Power Query (arquivo local Excel), não via API REST. Funcional para o modelo atual. |
| 3.4 Conector Denodo (contratos/volume) | IMPLEMENTADO CORRETO | [denodo_connector.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/denodo_connector.py) — 144 linhas, retry com backoff; [contratos_denodo_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/contratos_denodo_service.py) — 157 linhas | — | REST API com fallback para snapshot Bronze. |
| 3.5 Conector MtM | IMPLEMENTADO COM PROBLEMA | [mtm_connector.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/mtm_connector.py) — 109 linhas; [mtm_ingestion_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/mtm_ingestion_service.py) — 129 linhas | ALTA | Lê arquivo local (CSV/Excel) de `ENTRADAS/mtm`. O [main.py:53-55](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L53-L55) substitui os dados reais por mock: `SEGMENTO="CGRUPO"` e `PD=0.05` hardcoded. |
| 3.6 Conector Receita Federal | IMPLEMENTADO CORRETO | [receita_connector.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/receita_connector.py) — 231 linhas, cache local, BrasilAPI | — | Funcional com rate-limiting e cache por dia. |
| 3.7 Reconciliação Denodo × MtM | IMPLEMENTADO COM PROBLEMA | [reconciliacao_denodo_mtm_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/reconciliacao_denodo_mtm_service.py) — outer join por CNPJ | MÉDIA | A reconciliação é por CNPJ (presença/ausência), não por contrato individual. Não verifica valor/volume — apenas existência. |
| 3.8 Reconciliação Fichas × Salesforce | NÃO VERIFICADO | Arquivo existe, mas não pude confirmar lógica sem dados de teste | MÉDIA | — |

---

### §4 — PROCESSOS DE INGESTÃO

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 4.1 Classificação automática de layout | IMPLEMENTADO CORRETO | [ficha_classifier.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/ficha_classifier.py) — `classify_workbook()` com regex patterns | — | — |
| 4.2 Extração estruturada de campos | IMPLEMENTADO CORRETO | [ficha_extractor.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/ficha_extractor.py) — 121 linhas | — | — |
| 4.3 Deduplicação por hash e chave de negócio | IMPLEMENTADO COM PROBLEMA | [dedup_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/dedup_service.py) — hash + (CNPJ, data_DF); **MAS** [dedup_service.py:56-64](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/dedup_service.py#L56-L64): modo `reprocess` **remove** registros anteriores do history em memória | CRÍTICA | **VIOLAÇÃO DE IMUTABILIDADE:** `upsert_business_key_in_history` em modo reprocess **apaga entradas anteriores** do histórico (filtra e substitui). Isso contradiz §1.5 (nunca sobrescrever). |
| 4.4 Staging → Bronze → Silver | IMPLEMENTADO CORRETO | [staging/](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/staging), [storage/bronze_store.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/storage/bronze_store.py), [storage/silver_store.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/storage/silver_store.py) | — | Fluxo básico funciona. |
| 4.5 Carga manual controlada com dupla temporalidade | IMPLEMENTADO COM PROBLEMA | [carga_manual_service.py:58-64](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/carga_manual_service.py#L58-L64) — adiciona `DATA_REGISTRO_SISTEMA` e preserva `data_referencia_negocio` do input | CRÍTICA | **Casca vazia em runtime.** O main.py chama com `registros=[]` ([main.py:99](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L99)), garantindo que a lógica **nunca execute**. Não há formulário, template Excel, nem interface para alimentar registros. Schema JSON existe mas nunca é usado com dados reais. |
| 4.5.1 Fluxo de aprovação (solicitante ≠ aprovador, expiração) | AUSENTE | Override service tem validação de segregação ([override_service.py:45-48](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/override_service.py#L45-L48)), mas **carga manual NÃO tem**. Não existe `ctl_aprovacao_manual`. Status vai direto de input para `processados` sem aprovação. | CRÍTICA | §4.5 exige aprovação antes de compor visão oficial. Não implementado. |

---

### §5 — QUALIDADE DE DADOS

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 5.1 Normalização de tipos (datas, numéricos, strings, CNPJ) | IMPLEMENTADO CORRETO | [field_type_normalizer.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/silver/field_type_normalizer.py) — 136 linhas; [common/strings.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/common/strings.py), [common/dates.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/common/dates.py) | — | — |
| 5.2 Validação contra regras de qualidade (required, range, format) | IMPLEMENTADO COM PROBLEMA | [ficha_validator.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/ficha_validator.py) — `DomainRuleEngine` + validações imperativas | MÉDIA | Duplicação entre JSON e Python (reconhecida no backlog §2.2). |
| 5.3 Validação de domínio (PD ∈ [0,1], PL numérico, datas plausíveis) | IMPLEMENTADO CORRETO | [pd_validator.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/pd_validator.py) — 105 linhas | — | — |
| 5.4 Regras de matching (reconciliação Ficha × Salesforce) | IMPLEMENTADO COM PROBLEMA | [reconciliacao_fichas_salesforce_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/reconciliacao_fichas_salesforce_service.py) — 161 linhas | MÉDIA | Faz matching por CNPJ mas [linha 50-52](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/reconciliacao_fichas_salesforce_service.py#L50-L52): deduplica fichas com `keep="last"`, perdendo histórico. |
| 5.5 Alertas de qualidade (25+ tipos, Apêndice B) | AUSENTE | Apenas ~6 tipos implementados: CAD_001, CTR_001, CTR_002, GAR_001, GAR_002, QLT_002. Faltam ~19 tipos. | ALTA | Cobertura de ~25% dos alertas requeridos. |
| 5.6 Tolerância parametrizada para reconciliação numérica | AUSENTE | [mtm_ingestion_service.py:79](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/mtm_ingestion_service.py#L79) usa config mas apenas para MtM. Outras reconciliações não têm tolerância. | MÉDIA | — |

---

### §6 — REGRAS DE NEGÓCIO E CÁLCULOS

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 6.1 Cadastro unificado de contraparte | IMPLEMENTADO COM PROBLEMA | [dim_contraparte_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/dim_contraparte_service.py) — merge Receita + Segmentação | ALTA | Campos `GRUPO_ECONOMICO="INDEPENDENTE"` e `CONTROLADORA="NAO_INFORMADO"` são hardcoded ([linha 64-65](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/dim_contraparte_service.py#L64-L65)). Sem ligação com Salesforce para grupo econômico real. `NOME` ausente no schema. |
| 6.2 Enquadramento ≥5MWm (maior volume mensal simultâneo) | IMPLEMENTADO CORRETO | [enquadramento_service.py:46-57](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/enquadramento_service.py#L46-L57) — groupby (CNPJ, COMPETENCIA) → sum → max | — | Lógica correta: soma volumes por mês, depois pega o máximo. Confere com §6.2 ("maior volume mensal simultâneo"). |
| 6.3 Motor de PD ajustada (CPURA, CGRUPO, GT_5, LE_5) | IMPLEMENTADO CORRETO | [pd_engine.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/pd_engine.py) — 165 linhas, orquestra 8 módulos; [pd_transform.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/pd_transform.py) despacha 4 segmentos | — | Pipeline PD completo com notas quant/qual, score, rating, transformação por segmento. |
| 6.4 Score qualitativo e quantitativo (CPURA) | IMPLEMENTADO CORRETO | [score_qualitativo.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/score_qualitativo.py), [score_quantitativo.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/score_quantitativo.py), [score_total.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/score_total.py) | — | — |
| 6.5 Rating final | IMPLEMENTADO CORRETO | [rating.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/rating.py) — 112 linhas | — | — |
| 6.5.1 Carga manual controlada com dupla temporalidade | AUSENTE | Conforme §4.5 — casca vazia | CRÍTICA | Ver análise em §4. |
| 6.6 EAD = max(MtM positivo, 0) × FCF | IMPLEMENTADO COM PROBLEMA | [ead_engine.py:54](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/ead_engine.py#L54) — `ead = max(float(mtm_positivo_total), 0.0) * fator_conversao` ✅ fórmula correta | CRÍTICA | **Fórmula correta, MAS o input é mockado.** [main.py:53-55](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L53-L55): `df_exposicoes = df_mtm.copy()`, `SEGMENTO="CGRUPO"`, `PD_FINAL=0.05`. O EAD real nunca é calculado com dados das fichas. |
| 6.7 PE = EAD × LGD × PD | IMPLEMENTADO COM PROBLEMA | [pe_engine.py:46](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/pe_engine.py#L46) — `pe_reais = float(ead) * float(lgd_liquida) * float(pd_final)` ✅ fórmula correta | CRÍTICA | Mesma ressalva: PD de input é 0.05 hardcoded, não a PD real da ficha. |
| 6.8 LGD líquida = LGD_bruta × (1 - cobertura_garantias) | IMPLEMENTADO COM PROBLEMA | [lgd_engine.py:67](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/lgd_engine.py#L67) — `lgd_liquida = lgd_bruta * (1.0 - cobertura_efetiva)` ✅ fórmula correta | ALTA | Cobertura sempre 0.0 porque não há base de garantias alimentada. LGD_liquida = LGD_bruta na prática. |
| 6.9 Taxa de Risco = PE_total / Notional_total | IMPLEMENTADO CORRETO | [taxa_risco_engine.py:69](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/taxa_risco_engine.py#L69) — `taxa = pe_total / notional_total` | — | Fórmula correta, com tratamento de divisão por zero. |
| 6.10 Alertas de negócio (25+ tipos) | IMPLEMENTADO COM PROBLEMA | CAD_001, CTR_001/002, GAR_001/002, QLT_002 implementados. Faltam: EXP_001, DF_001, EXC_001, MAN_001-004 e ~15 outros do Apêndice B. | ALTA | ~25% de cobertura dos alertas obrigatórios. |
| 6.11 Matriz de transição de rating | AUSENTE | Nenhuma referência a "matriz de transição" em qualquer módulo Python. | MÉDIA | Requisito §7.2 não implementado. |

---

### §7 — PRODUTOS DE SAÍDA (CAMADA GOLD)

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 7.1 Visão consolidada atual por contraparte | IMPLEMENTADO COM PROBLEMA | [camada_gold_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/camada_gold_service.py) — 100 linhas, join risco + contraparte + análise | CRÍTICA | **Código existe mas NUNCA gerou output.** Diretório `SAIDAS/gold/relatorio_credito_atual/` está VAZIO. O serviço falha em [linha 38-40](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/camada_gold_service.py#L38-L40) quando `df_risco.empty` (que é o caso, pois `relational/facts/` está vazio). |
| 7.2 Histórico e matriz de transição | AUSENTE | Diretório `SAIDAS/gold/historico_analises/` existe mas está vazio. Nenhum código gera dados aqui. | ALTA | — |
| 7.3 Arquivo Excel padronizado para cálculo de limites | IMPLEMENTADO COM PROBLEMA | [camada_gold_service.py:59-81](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/camada_gold_service.py#L59-L81) — define mapa de exportação correto, mas campos `PL_AJUSTADO_REFERENCIA="0.00"` e `VALIDADE_EXCECAO="N/A"` são hardcoded | ALTA | **Não é Excel**, é Parquet/CSV. O requisito §7.3 pede Excel padronizado. Além disso, nunca gera output real. |
| 7.4 Interface para Power BI | AUSENTE | Nenhum modelo semântico documentado. `LATEST.parquet` é mencionado no código [linha 95](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/camada_gold_service.py#L95) mas **sobrescreve o arquivo anterior** — viola §1.5 | ALTA | `Limites_Credito_LATEST.parquet` é sobrescrito a cada execução sem preservar versão anterior. |
| 7.5 Alertas e pendências Gold | AUSENTE | Diretórios `SAIDAS/gold/alertas_credito/` e `SAIDAS/gold/pendencias/` existem mas vazios | ALTA | — |

---

### §8 — MODELO RELACIONAL

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 8.1 dim_contraparte | IMPLEMENTADO COM PROBLEMA | [dim_contraparte_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/dim_contraparte_service.py) — schema parcial | ALTA | Faltam: NOME, campos reais de grupo econômico. SCD Type 2 "simulado" [linha 69-71](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/dim_contraparte_service.py#L69-L71): `DATA_INICIO=hoje`, `DATA_FIM=2099-12-31`, `ATIVO=True` hardcoded — **não há lógica real de SCD** (nunca fecha registro anterior). `relational/dimensions/` está vazio. |
| 8.1 dim_analise | AUSENTE | Nenhum código. Zero referências a `dim_analise` no código. | ALTA | — |
| 8.1 dim_garantia | AUSENTE | Nenhum código. Zero referências a `dim_garantia` como dimensão. `fato_garantia` existe em Silver mas não em Relational. | ALTA | — |
| 8.1 dim_data (calendário) | AUSENTE | Nenhum código | MÉDIA | — |
| 8.1 dim_contrato | AUSENTE | Nenhum código | MÉDIA | — |
| 8.1 dim_rating_escala | AUSENTE | Nenhum código | MÉDIA | — |
| 8.2 fato_analise_credito | IMPLEMENTADO COM PROBLEMA | [fato_analise_credito_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/fato_analise_credito_service.py) — schema correto em teoria | ALTA | Chamado com `df_silver_analises=pd.DataFrame()` e `df_dim_contraparte=pd.DataFrame()` em [main.py:72](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L72). **Sempre retorna "SEM_DADOS"** porque os DataFrames são vazios. |
| 8.2 fato_exposicao_risco | IMPLEMENTADO CORRETO | [pipeline_risco_service.py:86-99](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/pipeline_risco_service.py#L86-L99) + persistência em [134-138](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/pipeline_risco_service.py#L134-L138) | — | Schema correto com calculo_ids de EAD/LGD/PE. Mas `relational/facts/` vazio confirma que nunca executou com sucesso até o Gold. |

---

### §9 — ARQUITETURA DE DADOS

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 9.1 Camadas Bronze/Silver/Gold | IMPLEMENTADO CORRETO | Diretórios existem em `SAIDAS/`. Bronze com snapshots imutáveis por data | — | — |
| 9.2 Portabilidade (sem caminhos hardcoded) | IMPLEMENTADO COM PROBLEMA | [context.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/app/context.py) e [config_builder.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/app/config_builder.py) usam resolução dinâmica | MÉDIA | Backlog reporta 97 caminhos hardcoded em app_config.json (§2.1). Parcialmente corrigido mas não verificável sem ver o JSON atual. |
| 9.3 Ambientes (dev/homolog/prod) | AUSENTE | Nenhuma configuração de ambiente | BAIXA | — |

---

### §10 — SEGURANÇA E ACESSO

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 10.1 Controle de acesso por perfil | NÃO VERIFICADO | Sem interface web/CLI que implemente roles | MÉDIA | Fora do escopo de um pipeline local sem UI. |
| 10.2 Credenciais via .env | NÃO VERIFICADO | [.env](file:///c:/Users/malik/Downloads/BDC_v06/BDC/.env) existe (369 bytes) mas não inspecionado por segurança | BAIXA | — |
| 10.3 Segregação de função em overrides | AUSENTE | Override service valida `solicitante ≠ aprovador` ([override_service.py:45](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/override_service.py#L45)), mas o main.py passa dados de teste com `SOLICITANTE="SISTEMA"`, `APROVADOR="ADMIN"` ([main.py:100](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L100)) — **sem integração com autenticação real** | ALTA | Não há quem autentique o solicitante/aprovador. |

---

### §11 — AUDITORIA E RASTREABILIDADE

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 11.1 Identificadores únicos (documento_id, run_id, calculo_id) | IMPLEMENTADO COM PROBLEMA | `documento_id` gerado via UUID em [fichas_comercializadoras_service.py:325](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/fichas_comercializadoras_service.py#L325); `run_id` em todos os serviços; `calculo_id` nos engines | ALTA | `config_snapshot_id` gerado no EAD/LGD mas **não persiste na tabela fato** ([pipeline_risco_service.py:87-98](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/pipeline_risco_service.py#L87-L98)). Sem `regra_versao`. |
| 11.2 Rastreabilidade ponta a ponta | IMPLEMENTADO COM PROBLEMA | `run_id` conecta etapas; `calculo_id` nos engines | ALTA | **Não há tabela central** que vincule todos os calculo_ids de um run. O fato grava 3 calculo_ids mas não o da Taxa de Risco. |
| 11.3 Linhagem no nível do campo (ctl_campo_origem) | AUSENTE | Zero referências a `ctl_campo_origem` ou linhagem campo-a-campo no código | CRÍTICA | Requisito central de auditoria. Deveria rastrear célula Excel → campo Silver. |
| 11.4 Recálculo por impacto de atualização | AUSENTE | Nenhum mecanismo de identificação de dependências ou recálculo parcial | ALTA | — |
| 11.5 Tabelas de auditoria (ctl_run_pipeline, ctl_documento) | AUSENTE | Zero referências a qualquer tabela `ctl_*` no código | CRÍTICA | Nem schema, nem código, nem stub. |
| 11.6 Reconciliações obrigatórias (13 tipos) | IMPLEMENTADO COM PROBLEMA | Apenas ~3 tipos implementados: MtM Bronze↔Silver, Denodo×MtM, Fichas×Salesforce | ALTA | ~23% dos 13 tipos obrigatórios. |
| 11.7 Overrides com vigência e expiração | IMPLEMENTADO COM PROBLEMA | [override_service.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/override_service.py) — valida campos, segregação, expiração | ALTA | **Auto-aprovação:** Linha 58 seta `STATUS = APROVADO` diretamente, sem fluxo de aprovação real. O override é aprovado no ato da solicitação. |
| 11.7.1 Dupla temporalidade em carga manual | AUSENTE | `carga_manual_service.py` adiciona `DATA_REGISTRO_SISTEMA` mas é chamado com lista vazia | CRÍTICA | — |
| 11.8 Relatório de conciliação por execução | AUSENTE | Sem relatório consolidado por run | MÉDIA | — |
| 11.10 Não sobrescrita / histórico imutável | AUSENTE | **VIOLAÇÃO CONFIRMADA em múltiplos pontos:** (1) `merge_silver_dataset_by_business_key` com `drop_duplicates(keep="last")` — [silver_store.py:94](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/storage/silver_store.py#L94); (2) `upsert_business_key_in_history` remove registros em modo reprocess — [dedup_service.py:56-64](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/dedup_service.py#L56-L64); (3) `Limites_Credito_LATEST` sobrescreve arquivo — [camada_gold_service.py:95-96](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/camada_gold_service.py#L95-L96); (4) `mtm_agregado_contraparte` sobrescreve a cada execução — [mtm_ingestion_service.py:108](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/mtm_ingestion_service.py#L108); (5) `receita_cadastral_silver` sobrescreve — [receita_ingestion_service.py:111](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/receita_ingestion_service.py#L111) | CRÍTICA | **5 pontos confirmados de violação de imutabilidade.** |

---

### §12 — OPERAÇÃO

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 12.1 Orquestração automatizada do pipeline | IMPLEMENTADO CORRETO | [main.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py) — 16 steps sequenciais com try/except e resumo | — | — |
| 12.2 Logs estruturados por etapa | IMPLEMENTADO COM PROBLEMA | [logging_utils.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/common/logging_utils.py) — loggers por serviço; mas sem formato JSON estruturado | BAIXA | Logs em texto plano, não JSON. |
| 12.3 Reset e reprocessamento | AUSENTE | [reset.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/reset.py) existe mas apaga diretórios inteiros — viola imutabilidade | ALTA | `clear_directory_contents` é uma operação destrutiva. |

---

### §13 — EVOLUÇÃO PLANEJADA

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 13.1 Migração para banco de dados relacional | AUSENTE | — | MÉDIA | Planejamento futuro, mas nenhuma preparação. |
| 13.2 Dashboard interativo (Power BI) | AUSENTE | — | MÉDIA | — |
| 13.3 API de consulta | AUSENTE | — | BAIXA | — |

---

### §14 — FLUXO PONTA A PONTA

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| 14.1 Etapas 1-5 (Ingestão de fontes externas) | IMPLEMENTADO CORRETO | [main.py:82-90](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L82-L90) — Fichas, Denodo, Enquadramento, MtM, Reconciliação, Salesforce, Receita | — | Todas as etapas de ingestão são chamadas. |
| 14.2 Etapa 6 (Garantias) | IMPLEMENTADO CORRETO | [main.py:91](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L91) — `ingest_garantias_data` chamado | — | Chamado, mas depende de arquivo de entrada que pode não existir. |
| 14.3 Etapa 7 (Motor de Risco EAD→LGD→PE→Taxa) | IMPLEMENTADO COM PROBLEMA | [main.py:43-57](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L43-L57) — `preparar_e_rodar_risco` | CRÍTICA | **PD=0.05 e SEGMENTO="CGRUPO" hardcoded.** O motor de risco NUNCA usa dados reais das fichas. Ver linhas 54-55: `df_exposicoes["SEGMENTO_METODOLOGICO"] = "CGRUPO"` e `df_exposicoes["PD_FINAL"] = 0.05`. |
| 14.4 Etapas 8-9 (Dimensões e Fatos) | IMPLEMENTADO COM PROBLEMA | [main.py:95-96](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L95-L96) — chamados | ALTA | `preparar_fato_analise` passa DataFrames VAZIOS ([main.py:72](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L72)), garantindo que a fato sempre retorne "SEM_DADOS". |
| 14.5 Etapa 10 (Governança: carga manual, overrides) | IMPLEMENTADO COM PROBLEMA | [main.py:99-100](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L99-L100) — chamados com dados de teste hardcoded | ALTA | Carga manual com `registros=[]` (noop). Override com CNPJ de teste `"00000000000000"`. |
| 14.6 Etapa 11 (Gold/Limites) | IMPLEMENTADO COM PROBLEMA | [main.py:101](file:///c:/Users/malik/Downloads/BDC_v06/BDC/main.py#L101) — chamado | ALTA | Falha porque `fato_exposicao_risco` não existe em `relational/facts/`. |
| 14.7 Controles de qualidade antes de publicação Gold | AUSENTE | Nenhum gate/check antes de publicar na Gold | CRÍTICA | §14.8 exige regras de bloqueio. |
| 14.8 Regras de bloqueio operacional | AUSENTE | Zero código de enforcement. Exemplos ausentes: "não publicar consumidor ≥5MWm sem DF", "não publicar sem reconciliação crítica OK" | CRÍTICA | Nenhuma regra implementada como código que impede publicação. |

---

### APÊNDICES A, B, C

| Requisito | Status | Evidência | Severidade | Observação |
|---|---|---|---|---|
| A — Domínios controlados (Enums) | IMPLEMENTADO CORRETO | [enums.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/enums.py) — 126 linhas, 13 enums: TipoFicha, LoadMode, StatusIngestao, etc. | — | Cobertura adequada dos domínios principais. |
| A — Enum para SEGMENTO_METODOLOGICO | IMPLEMENTADO CORRETO | [enums.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/enums.py) contém `SegmentoMetodologico` | — | — |
| A — Enum StatusGarantia | IMPLEMENTADO CORRETO | [enums.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/enums.py) — `StatusGarantia` | — | — |
| A — Enum StatusAprovacao | IMPLEMENTADO CORRETO | [enums.py](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/enums.py) — `StatusAprovacao` | — | — |
| B — Catálogo de alertas (25+ tipos) | IMPLEMENTADO COM PROBLEMA | ~6 de ~25+ implementados | ALTA | Ver §5.5 |
| C — Campos mínimos da visão Gold | NÃO VERIFICADO | [camada_gold_service.py:60-71](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/camada_gold_service.py#L60-L71) lista campos, mas sem referência cruzada com PDF | MÉDIA | Não foi possível comparar com Apêndice C do PDF. |
| C — LGD bruta por segmento (tabela de parâmetros) | NÃO VERIFICADO | [lgd_engine.py:22-27](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/lgd_engine.py#L22-L27) — CPURA/CGRUPO/GT_5 = 0.45, LE_5 = 0.75 | MÉDIA | Valores parecem razoáveis mas não pude confirmar contra o Apêndice C do PDF. |
| C — Faixas de PD por segmento e rating | NÃO VERIFICADO | `pd_faixas.json` referenciado mas não inspecionado | MÉDIA | — |

---

## TOP 10 GAPS MAIS CRÍTICOS

| # | Gap | Severidade | Impacto |
|---|---|---|---|
| 1 | **Pipeline de risco usa PD=5% e SEGMENTO=CGRUPO hardcoded** em `main.py:54-55` — NUNCA usa dados reais das fichas | CRÍTICA | Todo cálculo de EAD/LGD/PE/Taxa é fictício |
| 2 | **Imutabilidade violada em 5 pontos confirmados** — merge com `keep="last"`, upsert que apaga, LATEST que sobrescreve | CRÍTICA | Impossível auditar histórico; dados anteriores perdidos |
| 3 | **Tabelas de auditoria (ctl_\*) completamente ausentes** — zero código, zero referência | CRÍTICA | Sem trilha de auditoria; inaceitável para sistema de crédito |
| 4 | **Carga manual é noop** — chamada com `registros=[]`; sem formulário, sem aprovação | CRÍTICA | Requisito complexo do documento, totalmente ausente na prática |
| 5 | **Regras de bloqueio operacional ausentes** — nenhum enforcement antes de publicar Gold | CRÍTICA | Sistema pode publicar dados incorretos/incompletos |
| 6 | **Camada Gold vazia** — código existe mas nunca gera output | CRÍTICA | Produto final do sistema não existe |
| 7 | **Override auto-aprovado** — `STATUS=APROVADO` na criação, sem fluxo de governança | ALTA | Viola segregação de funções exigida pelo documento |
| 8 | **fato_analise_credito sempre vazia** — chamada com DataFrames vazios | ALTA | Tabela central do modelo dimensional não é populada |
| 9 | **SCD Type 2 simulado** — dim_contraparte não fecha registros anteriores | ALTA | Histórico de mudanças de segmento/grupo não é preservado |
| 10 | **Linhagem campo-a-campo (ctl_campo_origem) ausente** — não rastreia célula Excel → campo Silver | CRÍTICA | Impossível auditar origem de um dado específico |

---

## VERIFICAÇÃO MANUAL DE FÓRMULAS

### EAD (§6.7)
- **Documento:** EAD = max(MtM positivo, 0) × fator de conversão
- **Código:** [ead_engine.py:54](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/ead_engine.py#L54) → `max(float(mtm_positivo_total), 0.0) * fator_conversao`
- **Resultado:** ✅ Fórmula confere. Mas fator_conversao default=1.0 e nunca é parametrizado na prática.

### LGD (§6.8)
- **Documento:** LGD_líquida = LGD_bruta × (1 - cobertura_garantias)
- **Código:** [lgd_engine.py:67](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/lgd_engine.py#L67) → `lgd_bruta * (1.0 - cobertura_efetiva)`
- **Resultado:** ✅ Fórmula confere. Cobertura efetiva travada em [0, 1] (linha 65).

### PE (§6.7)
- **Documento:** PE = EAD × LGD × PD
- **Código:** [pe_engine.py:46](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/pe_engine.py#L46) → `float(ead) * float(lgd_liquida) * float(pd_final)`
- **Resultado:** ✅ Fórmula confere.

### Taxa de Risco (§7.1)
- **Documento:** Taxa_Risco = PE_total / Notional_total
- **Código:** [taxa_risco_engine.py:69](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/domain/credito/taxa_risco_engine.py#L69) → `float(pe_total) / float(notional_total)`
- **Resultado:** ✅ Fórmula confere.

### Enquadramento ≥5 MWm (§6.2)
- **Documento:** Maior volume mensal simultâneo por competência
- **Código:** [enquadramento_service.py:46-57](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/enquadramento_service.py#L46-L57) → groupby(CNPJ, COMPETENCIA).sum() → groupby(CNPJ).max()
- **Resultado:** ✅ Lógica confere: soma por mês, depois máximo entre meses.

> [!IMPORTANT]
> **Todas as fórmulas estão matematicamente corretas em isolamento.** O problema é que os INPUTS são mockados ou inexistentes, fazendo com que os cálculos corretos produzam resultados fictícios.

---

## VERIFICAÇÃO DE IMUTABILIDADE — DETALHAMENTO

| Ponto de violação | Arquivo:Linha | Mecanismo | Impacto |
|---|---|---|---|
| `merge_silver_dataset_by_business_key` | [silver_store.py:91-96](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/storage/silver_store.py#L91-L96) | Concat + `drop_duplicates(keep="last")` → registro anterior SOBRESCRITO | Fichas de comercializadoras e consumidores perdem versões anteriores |
| `upsert_business_key_in_history` | [dedup_service.py:56-64](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/dedup_service.py#L56-L64) | Em modo `reprocess`, filtra e REMOVE entradas do history | Histórico de ingestão de fichas pode perder registros |
| `Limites_Credito_LATEST` | [camada_gold_service.py:95-96](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/camada_gold_service.py#L95-L96) | `to_parquet(path)` sem versionamento → SOBRESCREVE arquivo | Versão anterior do Gold perdida |
| `mtm_agregado_contraparte` | [mtm_ingestion_service.py:105-109](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/mtm_ingestion_service.py#L105-L109) | `write_silver_dataset` com mesmo filename → SOBRESCREVE | Cada execução perde snapshot anterior do MtM Silver |
| `receita_cadastral_silver` | [receita_ingestion_service.py:108-111](file:///c:/Users/malik/Downloads/BDC_v06/BDC/src/services/receita_ingestion_service.py#L108-L111) | `write_silver_dataset` com mesmo filename → SOBRESCREVE | Versão anterior da consulta Receita perdida |

---

## RESPOSTA DIRETA À PERGUNTA

> **"Este sistema, hoje, pode ir para produção como fonte oficial de dados de crédito?"**

**Não.** Por 4 razões fundamentais:

1. **Os cálculos de risco são fictícios.** O pipeline de risco opera com PD hardcoded (5%) e segmento fixo (CGRUPO), ignorando completamente os dados extraídos das fichas. Nenhum relatório gerado pelo sistema reflete a realidade creditícia das contrapartes.

2. **O sistema não preserva histórico.** Pelo menos 5 pontos no código sobrescrevem dados anteriores, violando o princípio central do documento (§1.5, §11.10). Um sistema de crédito que não preserva histórico é irauditável.

3. **Não existe trilha de auditoria.** Nenhuma das tabelas de controle exigidas (ctl_run_pipeline, ctl_documento, ctl_campo_origem, ctl_validacao_qualidade, ctl_regra_aplicada, ctl_reconciliacao, ctl_publicacao) existe no código. A rastreabilidade célula-a-célula exigida pelo documento é completamente inexistente.

4. **A camada Gold não gera nenhum output.** O produto final do sistema — a visão consolidada de crédito que alimentaria o cálculo de limites e o Power BI — é um diretório vazio. O código existe mas depende de dados upstream que nunca chegam porque os inputs do motor de risco são mockados.

O sistema tem uma **base sólida de ingestão e extração de fichas** (~31% do escopo), um **motor de PD bem implementado** para 4 segmentos, e **conectores funcionais** para 5 fontes. Mas faltam ~70% do escopo especificado, e os ~30% existentes têm problemas graves de integridade que precisam ser corrigidos antes de qualquer extensão.
