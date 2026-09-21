# Auditoria Consolidada — BD Crédito
**Data:** 21/09/2026  
**Documentos normativos:** Planejamento Funcional v1.2 · Nota Técnica PD/TRC v7  
**Escopo:** Código-fonte atual (`src/`), configurações (`ENTRADAS/control/`), pipeline (`main.py`)

---

## Sumário Executivo

O projeto possui **arquitetura sólida e motor de crédito funcional** para os quatro segmentos. Os motores de EAD, LGD, PE e TRC estão implementados e integrados. A separação de camadas (Silver → Relational → Gold) está preservada. Configurações estão externalizadas em JSON.

Há **1 achado crítico de fórmula** (coeficiente do Score na fórmula Risk3 de Consumidor ≤5MWm), **2 achados de governança estrutural** (tabelas de controle e trilha de auditoria incompletas), e **diversas lacunas de média prioridade** (tabelas fato de histórico, controles automáticos da Seção 12, saídas previstas).

---

## EIXO A — Estrutura, Camadas e Orquestração

### A.1 — Árvore de diretórios vs. Seção 10

| Pacote Planejado (§10) | Existe? | Nome Real | Obs |
|---|---|---|---|
| `app/` | ✅ | `src/app/` | Bootstrap e contexto |
| `cli/` | ✅ | `src/cli/` | Orquestradores de fichas |
| `common/` | ✅ | `src/common/` | Utilitários |
| `control/` | ✅ | `src/control/` | Logger |
| `staging/` | ✅ | `src/staging/` | Existe, mas pouco populado |
| `storage/` | ✅ | `src/storage/` | Escritores de dados |
| `silver/` | ✅ | `src/silver/` | Camada silver |
| `domain/` | ✅ | `src/domain/` | Motor de crédito + sub-domínios |
| `relational/` | ✅ | `src/relational/` | Facts + Dimensions |
| `gold/` | ✅ | `src/gold/` | Visão consolidada |
| `services/` | ✅ | `src/services/` | Conectores (Denodo, Risk3, etc.) |
| `tests/` | ❌ | **Ausente** | Não existe diretório `tests/` no `src/` |
| `ui/` | ⚠️ | `src/ui/` | Fora do escopo Planejamento (Eixo H) |

### A.2 — PIPELINE_STEPS ativo ([main.py](file:///c:/Users/C807951/Desktop/BDC/main.py#L58-L89))

```
BLOCO 1 — INGESTÃO:
  1. Fichas Comercializadoras
  2. Fichas Consumidores

BLOCO 2 — APIS/CONECTORES:
  3. Contratos (Denodo) [CRITICO]
  4. Enquadramento Consumidores
  5. MtM
  6. Salesforce
  7. Receita Federal
  8. Bureau (RISK3)
  9. Controladoras [DEGRADADO]
  10. Garantias
  11. Solicitações de Override
  12. Carga Manual

BLOCO 3 — MOTOR + RELACIONAL + GOLD:
  13. Dimensão Contraparte
  14. Fato Análise de Crédito (Motor de PD)
  15. Fato Garantia
  16. Fato Exposição de Risco (EAD/LGD/PE/TRC)
  17. Reconciliação Denodo × MtM [CRITICO]
  18. Reconciliação Fichas × Salesforce
  19. Alertas Manuais
  20. Visão Gold Consolidada
  21. Alertas de Crédito
  22. Exportação de Limites

BLOCO 4 — INTERFACE:
  23. Streamlit
```

### A.3 — Separação de camadas

**Conforme.** O motor de crédito (PD, EAD, LGD, PE, TRC) executa na camada Relacional (`fato_analise_credito.py`, `fato_exposicao_risco.py`). A Silver contém apenas dados extraídos/normalizados. Não há vazamento de cálculo de risco para a Silver.

### A.4 — Arquivos de configuração JSON

| Config | Caminho | Consumido por | Externalizado? |
|---|---|---|---|
| `pd_zscore_config.json` | `ENTRADAS/control/configs/` | [pd_base.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_base.py#L53-L57) | ✅ Mas há fallback hardcoded nos `.get()` |
| `pd_faixas.json` | `ENTRADAS/control/configs/` | [pd_transform.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_transform.py) | ✅ |
| `pd_cpura_config.json` | `ENTRADAS/control/configs/` | [pd_cpura.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_cpura.py) | ✅ |
| `pd_transform_rules.json` | `ENTRADAS/control/configs/` | [pd_cgrupo.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_cgrupo.py), [pd_consumidor_gt5.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_consumidor_gt5.py) | ✅ |
| `score_cpura_config.json` | `ENTRADAS/control/configs/` | score_quantitativo, score_qualitativo | ✅ |
| `garantias_config.json` | `ENTRADAS/control/configs/` | [motor_garantias.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_garantias.py) | ✅ |
| `master_catalog_comercializadoras.json` | `ENTRADAS/control/quality/` | Extrator/Validador de fichas | ✅ |
| `master_catalog_consumidores.json` | `ENTRADAS/control/quality/` | Extrator/Validador de fichas | ✅ |
| `domain_dictionaries.json` | `ENTRADAS/control/quality/` | Normalização Silver | ✅ |
| `mapping_fichas_*.json` | `ENTRADAS/control/mappings/` | Orquestrador de fichas | ✅ |

> [!WARNING]
> **Fallback hardcoded em `pd_base.py` L53-57:** Os coeficientes do Z-score são lidos do JSON mas possuem valores default idênticos nos `.get()`. Isso funciona, mas viola o princípio de "sem constante duplicada" da Seção 1.5.

---

## EIXO B — Silver: Comercializadoras e Consumidores

> Avaliação diferencial vs. rodada anterior (não repete levantamento).

**(a) Corrigido desde a última rodada:**
- Busca na Visão Silver agora inclui `CONTRAPARTE_APELIDO` em `colunas_alvo` — verificado em [visao_silver.py L158](file:///c:/Users/C807951/Desktop/BDC/src/ui/views/visao_silver.py#L158).
- Contagem "Total de Contratos" na aba Denodo agora usa `nunique()` em `NUMERO_REFERENCIA_CONTRATO`.

**(b) Continua pendente:**
- Coluna `LUCRO_LIQUIDO`, `FCO` e `AT_PT` duplicadas (calculadas no `derivador_financeiro.py` E extraídas via layout JSON). Você identificou isso hoje e optou por resolver manualmente.

**(c) Novidades:**
- Nenhuma alteração estrutural no extrator Silver desde a última rodada.

---

## EIXO C — Motor de Crédito

### C.1 — Recuperação Judicial

| Aspecto | Status | Evidência |
|---|---|---|
| Curto-circuito PD=1.0 | ✅ Conforme | [pd_motor.py L56-66](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_motor.py#L56-L66) |
| Rating_final=E | ✅ Conforme | L64 |
| EAD/LGD/PE/TRC continuam | ✅ Conforme | `fato_exposicao_risco.py` processa normalmente após PD=1.0 |
| Garantidor em RJ | ✅ Conforme | [motor_garantias.py L74](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_garantias.py#L74): `GARANTIDOR_EM_RJ` → rejeição |

### C.2 — PD substituta e validade

| Segmento | Piso | Evidência | 4 campos auditoria |
|---|---|---|---|
| CPURA (DF>18m) | max(PD_Risk3, 10%) | ✅ [pd_motor.py L91](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_motor.py#L91) | ✅ L116-119 |
| CGRUPO (DF/rating>18m) | max(última, 15%) | ✅ [pd_motor.py L99](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_motor.py#L99) | ✅ |
| CONS>5 (DF>18m) | max(PD_Risk3, 50%) | ✅ [pd_motor.py L103](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_motor.py#L103) | ✅ |
| CONS≤5 | N/A (sem PD_sub) | ✅ Correto | N/A |

> [!IMPORTANT]
> Os 4 campos (`MOTIVO_PD_SUB`, `DATA_ACIONAMENTO_PD_SUB`, `FONTE_PD_SUB`, `VALOR_PD_SUB`) são retornados no dict do motor (L116-119), mas **não estão no rename_map de `fato_analise_credito.py`** (L182-191). Portanto **são persistidos no CSV/Parquet intermediário, mas NÃO chegam à tabela fato renomeada final**. São efetivamente **perdidos na persistência relacional**.

### C.3 — LGD

| Aspecto | Status | Evidência |
|---|---|---|
| Fórmula `LGD = 1 - cobertura` | ✅ | [motor_lgd.py L56](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_lgd.py#L56): `lgd_bruta * (1 - cobertura)` |
| Default cobertura=0.0 | ✅ | L25: `cobertura_garantias: float = 0.0` |
| Motor de garantias | ✅ | [motor_garantias.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_garantias.py) existe e está integrado em `fato_exposicao_risco.py` L104-112 |
| Haircuts marcados como propostos | ⚠️ | [garantias_config.json L2](file:///c:/Users/C807951/Desktop/BDC/ENTRADAS/control/configs/garantias_config.json#L2): `"status": "HOMOLOGADO"` — mas sem evidência de aprovação formal documentada |
| Garantidor em RJ | ✅ | L74: `rj_garantidor == "SIM"` → rejeição |
| Rating deteriorado do garantidor | ❌ Ausente | O filtro verifica `rating_garantidor_tier_1` para definir haircut de fiança, mas **não rejeita garantias de garantidor com rating deteriorado (ex: E)**. Apenas diferencia haircut tier 1 vs. inferior. |

### C.4 — CGRUPO (21 combinações)

A tabela `pd_tabela` em [pd_transform_rules.json](file:///c:/Users/C807951/Desktop/BDC/ENTRADAS/control/configs/pd_transform_rules.json#L37-L51) contém **50 entradas** (cobrindo Fitch, S&P e Moody's com notações específicas + Moody's com aliases). Comparando com a Nota Técnica §7.1 (21 linhas):

| Notch NT | Config | PD NT | PD Config | Match? |
|---|---|---|---|---|
| AAA | ✅ | 0.05% | 0.0005 | ✅ |
| AA+ | ✅ | 0.08% | 0.0008 | ✅ |
| ... (todos os 21) | ✅ | — | — | ✅ |
| DDD/D | ✅ | 100% | 1.0000 | ✅ |

**21/21 combinações conferem.** O lookup é por notch exato (não por banda).

### C.5 — Consumidor ≤5MWm

> [!CAUTION]
> **DIVERGÊNCIA CRÍTICA DE FÓRMULA**
>
> Nota Técnica §8.1: `PD_Risk3 = min{1,9·exp[-0,5·(0,11·Score - Alerta/3 + 1)], 0,9999}`
>
> Código [pd_consumidor_le5.py L26](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_consumidor_le5.py#L26): `expoente = -0.5 * (0.011 * score - (alerta / 3.0) + 1.0)`
>
> **O coeficiente do Score é `0.011` no código vs. `0.11` na Nota Técnica.** Diferença de ordem de magnitude (fator 10). Isso produz PDs sistematicamente menores do que o especificado.
>
> **Impacto:** Todas as PDs de consumidores ≤5MWm calculadas até agora estão potencialmente subestimadas.

**Rating Copel:** Corretamente não atribuído. `RATING_FINAL: "NAO_APLICAVEL"` em L34.

### C.6 — Z-Score (PD_base contábil)

| Aspecto | Status | Evidência |
|---|---|---|
| X12 = (LA + RL) / AT | ✅ | [pd_base.py L48](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_base.py#L48): `(la + rl) / at` onde `la=LUCROS_ACUMULADOS`, `rl=RESERVA_DE_LUCROS` |
| Coefs em JSON | ✅ | [pd_zscore_config.json](file:///c:/Users/C807951/Desktop/BDC/ENTRADAS/control/configs/pd_zscore_config.json): intercept=-4.03, x12=-3.70, x16=11.66, x19=-7.86, x22=-11.33 |
| Fail-safe sem raise | ⚠️ | L70-73: `except Exception` retorna `None` + log warning. Sem raise. Conforme. Mas o caller em `fato_analise_credito.py` trata `None` como erro silencioso, não gera alerta PD_002. |

### C.7 — Consumidor >5MWm (Item 9)

| Aspecto | Status | Evidência |
|---|---|---|
| Transformação t-Student 6gl, escala 1.2 | ✅ | [pd_consumidor_gt5.py L60-76](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_consumidor_gt5.py#L60-L76) + [pd_transform_rules.json L54-61](file:///c:/Users/C807951/Desktop/BDC/ENTRADAS/control/configs/pd_transform_rules.json#L54-L61) |
| Faixas calibradas (§9.1) | ✅ | [pd_faixas.json L14-19](file:///c:/Users/C807951/Desktop/BDC/ENTRADAS/control/configs/pd_faixas.json#L14-L19) |
| Régua indicador→nota distinta de CPURA (PD) | ✅ | [score_cpura_config.json L62-87](file:///c:/Users/C807951/Desktop/BDC/ENTRADAS/control/configs/score_cpura_config.json#L62-L87): bloco `PD_CONSUMIDOR_GT_5` com faixas próprias |
| Auditor→Nota reutilizado | ✅ | Mesmo `auditor_para_nota` do config, sem duplicação |

> [!NOTE]
> O bloco quantitativo para >5MWm deveria ter pesos globais de 32%/24%/7%/7% (§9 da NT). Atualmente o config usa pesos idênticos aos de CPURA (PD=0.322, FCO=0.238 etc.). Se os pesos de >5MWm forem de fato iguais aos de CPURA quando pré-multiplicados, está correto. Mas a NT lista valores levemente diferentes: 32% vs 0.46×0.70=32.2%, 24% vs 0.34×0.70=23.8%. **Diferença de arredondamento, não de substância** — mas merece verificação contra a planilha original.

### C.8 — EAD / EL / TRC

| Aspecto | Status | Evidência |
|---|---|---|
| EAD = max(MtM, 0) | ✅ | [motor_ead.py L53](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_ead.py#L53) |
| EL = EAD × PD × LGD | ✅ | [motor_pe.py L57](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_pe.py#L57) |
| TRC = ΣEL / ΣNotional (agregado) | ✅ | [motor_taxa_risco.py L78](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_taxa_risco.py#L78) + [fato_exposicao_risco.py L122-126,142](file:///c:/Users/C807951/Desktop/BDC/src/relational/facts/fato_exposicao_risco.py#L122-L142) (acumula soma) |
| PD/LGD/EAD persistidas no registro | ✅ | [fato_exposicao_risco.py L128-139](file:///c:/Users/C807951/Desktop/BDC/src/relational/facts/fato_exposicao_risco.py#L128-L139): `PD_UTILIZADA`, `EAD_VALOR`, `LGD_LIQUIDA` gravados por linha |

### C.9 — Golden Tests

**Status: Ausente.** Não existe diretório `tests/` em `src/`. Não há testes unitários ou de integração automatizados para o motor de crédito. Não tenho como executar nenhum teste, pois eles simplesmente não existem no repositório.

---

## EIXO D — Alertas (Apêndice B)

| Código | Implementado? | Evidência |
|---|---|---|
| ANA_001 | ✅ | [fato_alertas.py L63](file:///c:/Users/C807951/Desktop/BDC/src/relational/facts/fato_alertas.py#L63) |
| SEG_001 | ✅ | L79 |
| SEG_002 | ✅ | L95 |
| PD_002 | ✅ | L47 |
| PD_ERR_001 | ✅ | [fato_analise_credito.py L110](file:///c:/Users/C807951/Desktop/BDC/src/relational/facts/fato_analise_credito.py#L110) |
| QLT_002 | ✅ | [motor_taxa_risco.py L50](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_taxa_risco.py#L50) |
| CAD, RAT, EXP, GAR, DOC, CTR, VOL, GRP, DF, MAN, EXC | ❌ | **Não implementados** |

> [!WARNING]
> Dos 15 prefixos do Apêndice B, apenas **4 prefixos** estão cobertos (ANA, SEG, PD, QLT). Os demais **11 prefixos** (CAD, RAT, EXP, GAR, DOC, CTR, VOL, GRP, DF, MAN, EXC) não possuem alertas implementados.

**Alerta de PD_sub acionada:** Não existe como alerta autônomo em `cfg_regras_alerta`. O campo `MOTIVO_PD_SUB` é gravado no dict do motor, mas conforme C.2 acima, **não chega à fato final**.

---

## EIXO E — Carga Manual e Overrides

### E.1 — Tipos de evento

Na UI (`visao_carga_manual.py` L92) há referência a `COMPLEMENTACAO`. Em `visao_silver.py` L73 há `CORRECAO`. Os outros 3 tipos (`ATUALIZACAO_HISTORICA`, `REGISTRO_SEM_DF`, `OVERRIDE`) **não foram encontrados como opções na UI** nem como validação no backend. Existem apenas como conceito no Planejamento.

### E.2 — Regras automáticas vs. override

A RJ e PD_sub são **regras automáticas normativas** implementadas diretamente no motor (`pd_motor.py`). Não passam pelo fluxo de override. Isso é correto conforme o Planejamento §4.5: são regras do motor, não decisões humanas.

### E.3 — Herança de risco (Controladoras)

- **Plugado no pipeline:** ✅ [main.py L70](file:///c:/Users/C807951/Desktop/BDC/main.py#L70) + [fato_analise_credito.py L154-176](file:///c:/Users/C807951/Desktop/BDC/src/relational/facts/fato_analise_credito.py#L154-L176)
- **Decisão herança automática vs. override:** Resolvida como **automática** — `herdar_risco_controladoras()` executa direto no pipeline sem intervenção humana.
- **Documentação formal:** ❌ Não documentada como extensão (ver Eixo H).

---

## EIXO F — Saídas e Relatórios

### F.1 — Saídas previstas (§7.2 do Planejamento, 14 itens)

| Saída | Status |
|---|---|
| Visão Gold Consolidada | ✅ Existe |
| Arquivo de Limites | ✅ `servico_limites.py` |
| Fato Análise de Crédito | ✅ |
| Fato Exposição de Risco | ✅ |
| Fato Garantia | ✅ |
| Fato Alertas | ✅ |
| Fato Reconciliação Denodo × MtM | ✅ |
| Fato Reconciliação Fichas × SF | ✅ |
| Dim Contraparte | ✅ |
| ctl_run_pipeline | ✅ |
| ctl_documento | ✅ |
| ctl_campo_origem | ✅ |
| fato_score_rating_pd (histórico) | ❌ **Ausente** |
| fato_migracao_rating | ❌ **Ausente** |

### F.2 — Pedidos de negócio pendentes

- **Migração de rating ao longo do tempo:** `fato_score_rating_pd` e `fato_migracao_rating` **não existem** no repositório. Sem dados históricos de série temporal de rating por contraparte.
- **Lista de pendência por faixa de vencimento:** Não implementada como relatório autônomo.

### F.3 — visao_carteira.py

Itens anteriores corrigidos nesta sessão:
- ✅ PD formatada como percentual (×100)
- ✅ Filtro dinâmico "Sem Contrato"
- ✅ Análise Não Encontrada → exibição no "Tipo de Análise"
- ✅ Análise Herdada → label dedicado
- ✅ Filtros multiselect com `key=` estáveis
- ✅ Busca por Contraparte/CNPJ adicionada
- ✅ `CONTRAPARTE_APELIDO` preservado na Gold

---

## EIXO G — Governança, Auditoria e Reprodutibilidade

### G.1 — Tabelas de controle (§11.5)

| Tabela | Implementada? | Evidência |
|---|---|---|
| `ctl_run_pipeline` | ✅ | [servico_auditoria.py L56](file:///c:/Users/C807951/Desktop/BDC/src/domain/auditoria/servico_auditoria.py#L56) |
| `ctl_documento` | ✅ | L99 |
| `ctl_campo_origem` | ✅ | L139 |
| `ctl_evento_processamento` | ❌ | |
| `ctl_validacao_qualidade` | ⚠️ | Parcial (`ctl_validacao_qualidade_credito` em fato_analise_credito.py L203) |
| `ctl_regra_aplicada` | ❌ | |
| `ctl_reconciliacao` | ❌ | (Existe fato de reconciliação, não tabela de controle) |
| `ctl_override` | ❌ | |
| `ctl_publicacao` | ❌ | |
| `ctl_mudanca_config` | ❌ | |
| `ctl_aprovacao_manual` | ❌ | |

**3 de 11 implementadas.** As 8 restantes são lacunas de governança.

### G.2 — Registro mínimo (§12 da Nota Técnica)

| Item §12 | Persistido na fato? |
|---|---|
| Segmento e regra aplicada | ✅ `SEGMENTO_METODOLOGICO_FICHA`, `PD_METODO` |
| Datas de validade DF/bureau/rating | ⚠️ Apenas calculadas em memória (`_is_expired`), não persistidas na fato |
| PD_base ou PD_Risk3 + dados entrada | ⚠️ `PD_BASE` está no dict mas não no rename_map da fato |
| Scores e Score_total | ✅ `SCORE` (renomeado de `SCORE_TOTAL`) |
| [PD_min, PD_max] e interpolação | ⚠️ Calculados mas não persistidos na fato final |
| Motivo/data/fonte/valor PD_sub | ❌ **Perdidos no rename_map** (ver C.2) |
| Status RJ | ✅ `STATUS_CALCULO_PD = RECUPERACAO_JUDICIAL` |
| EAD/LGD/EL/Notional/TRC | ✅ Na `fato_exposicao_risco` |
| Versão tabelas | ⚠️ `config_snapshot_id` existe em EAD/LGD, mas não cobre PD/Score |

### G.3 — config_snapshot_id

Presente em EAD ([motor_ead.py L39](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_ead.py#L39)) e LGD ([motor_lgd.py L64](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_lgd.py#L64)). **Não existe** para `pd_zscore_config`, `pd_transform_rules`, `score_cpura_config`, `pd_faixas` ou `garantias_config`. Reprodutibilidade parcial.

### G.4 — Controles automáticos (§12 da NT)

| Controle | Implementado? |
|---|---|
| PD em [0,1] | ⚠️ Implícito pela lógica do motor (clamp), não validado explicitamente pós-cálculo |
| Rating no domínio (só com Rating Copel) | ⚠️ Implícito |
| Coerência PD_final/Rating_final | ❌ Sem validação cruzada explícita |
| PD_final = PD_Risk3 para ≤5MWm | ⚠️ Garantido pela estrutura do código, não por teste |
| Piso 50% para Rating E em >5MWm | ❌ Não validado explicitamente |
| Verificação validades DF/bureau | ✅ `_is_expired()` no motor |
| Regras PD_sub | ✅ Implementadas no motor |

**Nenhum dos controles existe como validação automatizada pós-cálculo.** São garantidos "por construção" do código, sem checagem independente.

---

## EIXO H — Itens Fora do Escopo Original

### H.1 — Herança de risco por controladora/subsidiária

- **Arquivos:** `controlador_connector.py`, `servico_controlador.py`
- **Classificação:** **(ii) Decisão pendente de formalização.** Funciona, está plugado, mas não consta em nenhum dos dois documentos normativos. A decisão "herança automática" foi implementada sem trilha de aprovação formal.

### H.2 — Motor de Elegibilidade e Haircut de Garantias

- **Arquivo:** [motor_garantias.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/motor_garantias.py)
- **Config:** [garantias_config.json](file:///c:/Users/C807951/Desktop/BDC/ENTRADAS/control/configs/garantias_config.json) — campo `"status": "HOMOLOGADO"` sem evidência de aprovação formal.
- **Classificação:** **(ii) Decisão pendente de formalização.** A NT explicitamente delega garantias "fora do escopo". Os haircuts precisam de documento de aprovação separado.

### H.3 — Interface Streamlit (visao_carteira, visao_silver, etc.)

- **Classificação:** **(i) Extensão legítima e necessária.** O Planejamento prevê saídas mas não especifica a interface. A tela é ferramenta operacional do analista.

### H.4 — Domínios e status extras

| Item | Onde | Classificação |
|---|---|---|
| `STATUS_CALCULO_PD` (enum) | [fato_analise_credito.py](file:///c:/Users/C807951/Desktop/BDC/src/relational/facts/fato_analise_credito.py) | (i) Necessário — decorre da NT |
| `RECUPERACAO_JUDICIAL` como condição | [pd_motor.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/credito/pd_motor.py) | (i) Necessário — §10.1 da NT |
| `ANALISE_HERDADA` / `TIPO_ANALISE` | [servico_controlador.py](file:///c:/Users/C807951/Desktop/BDC/src/domain/controlador/servico_controlador.py) | (ii) Depende de H.1 |
| `visao_carga_manual` como tela | [visao_carga_manual.py](file:///c:/Users/C807951/Desktop/BDC/src/ui/views/visao_carga_manual.py) | (i) Necessário |
| `servico_limites.py` | [servico_limites.py](file:///c:/Users/C807951/Desktop/BDC/src/gold/servico_limites.py) | (i) Necessário |

### H.5 — Integrações não previstas nos §3.1-3.6

| Fonte | Planejamento? | Classificação |
|---|---|---|
| Salesforce (Account) | ❌ Não listada | (i) Extensão legítima (reconciliação) |
| Receita Federal | ❌ Não listada | (i) Extensão legítima (cadastro) |
| Controladoras (planilha) | ❌ Não listada | (ii) Pendente formalização |

---

## Lista Final Priorizada

### 🔴 Crítico

| # | Item | Tipo | Eixo |
|---|---|---|---|
| 1 | **Coeficiente Score Risk3: 0.011 vs 0.11** — todas PDs de ≤5MWm potencialmente subestimadas em 1 ordem de magnitude | Gap implementação | C.5 |
| 2 | **Campos PD_sub perdidos no rename_map** — `MOTIVO_PD_SUB`, `DATA_ACIONAMENTO_PD_SUB`, `FONTE_PD_SUB`, `VALOR_PD_SUB` nunca chegam à fato final | Gap implementação | C.2 / G.2 |

### 🟠 Alto

| # | Item | Tipo | Eixo |
|---|---|---|---|
| 3 | 8/11 tabelas de controle ausentes | Gap implementação | G.1 |
| 4 | `fato_score_rating_pd` e `fato_migracao_rating` inexistentes — sem histórico de série temporal | Gap implementação | F.2 |
| 5 | 11/15 prefixos de alertas do Apêndice B não implementados | Gap implementação | D |
| 6 | Controles automáticos §12 da NT inexistentes como validação pós-cálculo | Gap implementação | G.4 |
| 7 | `config_snapshot_id` não cobre configs de PD/Score — reprodutibilidade parcial | Gap implementação | G.3 |
| 8 | Haircuts marcados "HOMOLOGADO" sem evidência de aprovação | Decisão pendente Malik | H.2 |

### 🟡 Médio

| # | Item | Tipo | Eixo |
|---|---|---|---|
| 9 | PD_base, PD_min, PD_max não persistidos na fato final (rename_map) | Gap implementação | G.2 |
| 10 | Datas de validade (DF, bureau, rating) calculadas em memória, não gravadas | Gap implementação | G.2 |
| 11 | Diretório `tests/` ausente — zero testes automatizados | Gap implementação | C.9 |
| 12 | Herança controladora sem documentação formal | Decisão pendente Malik | H.1 |
| 13 | Fallback hardcoded nos coeficientes Z-score (`pd_base.py .get()`) | Divergência método | A.4 |
| 14 | Garantidor com rating deteriorado não rejeitado (só ajusta haircut) | Divergência método | C.3 |

### 🟢 Baixo

| # | Item | Tipo | Eixo |
|---|---|---|---|
| 15 | `LUCRO_LIQUIDO`/`FCO`/`AT_PT` duplicados (derivador + layout) | Gap menor | B |
| 16 | Pesos quantitativos >5MWm arredondamento (32% vs 32.2%) | Verificação pendente | C.7 |
| 17 | 3 tipos de evento Carga Manual não implementados na UI | Gap menor | E.1 |
| 18 | Salesforce/Receita Federal não listados no Planejamento §3 | Formalização | H.5 |

---

> Relatório da **Fase 1** concluído. Nenhuma alteração de código foi feita. Posso prosseguir para a **Fase 2** (documentos de apresentação profissional) após sua revisão deste relatório?
