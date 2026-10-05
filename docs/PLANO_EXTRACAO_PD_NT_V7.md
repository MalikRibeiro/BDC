# PLANO DE IMPLEMENTAÇÃO: EXTRAÇÃO DE FICHAS E CÁLCULO DE PD (NT v7) — VERSÃO 2.2

**Documento:** Plano de Arquitetura, Extração, Validação Paralela e Auditoria da Probabilidade de Default e Ratings  
**Versão:** 2.2 (Consolidação da Auditoria Física da Fase 0.7 e Decisões Homologadas do /grill-me)  
**Data de Referência:** 05/10/2026  
**Status de Autorização:**
* **Fase 0 (Inventário Quantitativo e Auditoria Física 0.7):** **CONCLUÍDA** com 100% de evidências físicas apuradas.
* **Fase 1A (Arquitetura de Layouts v7/v6, Correção de `pd_base.py` e Validação Paralela):** **SUBMETIDA PARA AUTORIZAÇÃO FORMAL**.
* **Fases 1B a 4:** **NÃO AUTORIZADAS** (aguardando entregas e homologação da Fase 1A).

---

## CHANGELOG: HISTÓRICO DE MUDANÇAS (v2.0 $\rightarrow$ v2.2)

| Item | Origem | Descrição da Alteração na Versão 2.2 |
| :--- | :--- | :--- |
| **D5** | Negócio / Metodologia | **Tratamento de Insumos Inválidos em `pd_base.py`:** Se houver divisão por zero ou falta de insumos essenciais (ex.: $AT = 0$ ou $VL = 0$), o motor retorna estritamente `None` com status `INSUMO_CONTABIL_INVALIDO` e warning de log, sem imputar zeros ou valores arbitrários (Regra V e X do BDC). |
| **D6** | Governança / SCD2 | **Persistência na Silver via Versionamento SCD2:** A atualização da extração das 40 fichas de CPURA e 34 Geradoras do `padrao_7` será feita via SCD2 padrão: gera nova versão com `_VERSAO_REGISTRO = 2` e `_STATUS_REGISTRO = 'VIGENTE'`, arquivando a versão anterior como `'SUBSTITUIDO'` sem perda de histórico. |
| **D7** | Arquitetura | **Especialização de Layouts no Catálogo Declarativo:** Separação estrita dos layouts em arquivos dedicados: `layout_ficha_comercializadora_v7_cpura.json` (balanço em $G14:G26$, scores em $G67:H79$, campos de origem em $B26..B29$) e `layout_ficha_comercializadora_v7_cgrupo.json` (scores em $M67:N79$, rating em $C32$). Extrator 100% declarativo sem regras procedurais no Python. |
| **D8** | Governança / Cadastro | **Resgate e Enquadramento das 34 Fichas Geradoras:** As 34 fichas vigentes em `padrao_7` com $B18 = \text{"Geradora"}$ ou $\text{"Produtor Independente"}$ deixam o status `INDEFINIDO` e são enquadradas no pipeline contábil de CPURA (`v7_cpura`), preservando `SUBSEGMENTO = 'GERADORA'` para relatórios de negócio. |
| **D9** | Linhagem / Silver | **Extração dos Indicadores da Origem com Sufixo `_FICHA`:** Células $B26..B29$ da planilha são extraídas na Silver como `PD_BASE_FICHA`, `FCO_ROL_FICHA`, `ROA_FICHA` e `ROE_FICHA` para servirem de contraprova da origem na Validação Paralela, sem violar a regra de que a Silver guarda a verdade observada. |
| **D10**| Negócio / Governança | **Soberania da Ficha Excel na Validação Paralela:** O valor extraído da ficha Excel é a **autoridade soberana oficial** para a concessão de crédito em caso de divergência contra o recálculo do Python. A divergência é auditada com status `DIVERGENCIA_ORIGEM` e log de observabilidade sem interromper o pipeline. |
| **F0.7**| Auditoria Física | **Comprovação Factual das Fórmulas da NT v7:** A auditoria da Fase 0.7 comprovou que a fórmula $\text{PD} = \frac{1}{1 + e^{-z}}$ da NT v7 reproduz exatamente 83 de 83 (100%) fichas vigentes de `padrao_6` contra a PD declarada (tolerância $< 10^{-6}$). Provou também que $B26$ no `padrao_7` contém fórmula contábil nativa `=IF(B18="CGRUPO", 0.5%, G46)` com escore linear em $H44$. |

---

## 1. CONTEXTO, HIERARQUIA NORMATIVA E OBJETIVOS

### 1.1 Contexto do Projeto
O BD Crédito (BDC) da Copel Comercializadora é a base corporativa de gestão de risco de contrapartes. Opera atualmente em ambiente de homologação local no PC do analista, mas sua arquitetura deve ser estritamente desacoplada de caminhos locais e do Excel, preparando a solução para a migração corporativa da TI para GCP / Oracle / Denodo.

### 1.2 Hierarquia Normativa
1. **Nota Técnica de PD e TRC v7 (10/09/2026):** Autoridade normativa máxima para as fórmulas de risco, transformações intrafaixa, modelo logístico contábil e réguas de corte.
2. **Planejamento do Sistema BD Crédito v1.2 (21/07/2026):** Autoridade máxima para a arquitetura de dados, divisão de camadas (Silver vs Relacional vs Gold), trilha de auditoria e governança de overrides/carga manual.

### 1.3 Objetivos da Versão 2.2
1. Corrigir o motor de risco contábil (`pd_base.py`) para aplicar a fórmula exata da NT v7 §4 ($\text{PD} = \frac{1}{1 + e^{-z}}$).
2. Curar a extração contábil do `padrao_7` (mapear Vendas, Lucro e FCO em $G24:G26$).
3. Estruturar os catálogos declarativos especializados para CPURA e CGRUPO nos layouts v7 e v6.
4. Enquadrar as 34 geradoras vigentes com preservação de subsegmento.
5. Implementar a Validação Paralela na camada Relacional, populando `fato_analise_credito` e `fato_score_rating_pd`.

---

## 2. DECISÕES DE NEGÓCIO E ARQUITETURA CONSOLIDADAS

### 2.1 Limiar de 5 MWm para Consumidores (Decisão D1)
* Volume Contratado $\ge 5,00\text{ MWm} \implies \text{CONSUMIDOR\_GE\_5}$ (Análise Detalhada com DF).
* Volume Contratado $< 5,00\text{ MWm} \implies \text{CONSUMIDOR\_LT\_5}$ (Análise Simplificada por Bureau).
* Parametrizado em `ENTRADAS/control/rules/enquadramento_config.json`.

### 2.2 Nomenclatura Canônica e Equivalência (Decisão D2)
* Siglas técnicas internas: `CPURA`, `CGRUPO`, `CONSUMIDOR_GE_5`, `CONSUMIDOR_LT_5`.
* Mapeamento único preservado em `ENTRADAS/control/quality/domain_dictionaries.json`.

### 2.3 Cálculo de ROA, ROE e FCO/ROL (Decisão D3)
* Cálculos pontuais oficiais: $ROA = \frac{\text{Lucro Líquido}}{\text{Ativo Total}}$, $ROE = \frac{\text{Lucro Líquido}}{\text{Patrimônio Líquido}}$, $FCO/ROL = \frac{\text{FCO}}{\text{Vendas Líquidas}}$.
* Se o denominador for nulo ou zero, o resultado é estritamente `None` (nulo), nunca zero.

### 2.4 Soberania da Origem e Validação Paralela (Decisões D4 e D10)
* **Princípio da Soberania da Origem:** O valor oficial para fins de limites e exposição é o valor aprovado e extraído da ficha cadastral.
* **Validação Paralela:** O motor Python recalcula os valores como "auditoria sombra".
* **Conflito:** Se houver divergência, o valor da ficha permanece oficial na Gold e o registro é marcado como `DIVERGENCIA_ORIGEM` na auditoria. Substituições formais exigem o fluxo de Carga Manual / Overrides com aprovação da área (Planejamento §4.5 e §11.7).

### 2.5 Especialização Declarativa dos Layouts (Decisão D7)
* Proibição de regras procedurais com `if/else` por categoria no código do extrator.
* Criação de arquivos de layout JSON dedicados:
  * `layout_ficha_comercializadora_v7_cpura.json`
  * `layout_ficha_comercializadora_v7_cgrupo.json`
  * `layout_ficha_comercializadora_v6_cpura.json`
  * `layout_ficha_comercializadora_v6_cgrupo.json`

### 2.6 Enquadramento de Geradoras (Decisão D8)
* Fichas com categoria "Geradora" ou "Produtor Independente" são processadas com o layout `v7_cpura`.
* A Silver e Relacional registram `SEGMENTO = 'CPURA'` e `SUBSEGMENTO = 'GERADORA'`.

---

## 3. AUDITORIA FÍSICA E MAPEAMENTO CÉLULA A CÉLULA POR LAYOUT

### 3.1 Mapeamento Comparativo: `padrao_7` (CPURA vs CGRUPO)

| Conceito de Negócio | Campo Canônico Silver | `padrao_7_cpura` (e Geradoras) | `padrao_7_cgrupo` | Tipo de Dado |
| :--- | :--- | :---: | :---: | :---: |
| **CNPJ** | `CNPJ` | `B13` (ou `B10`) | `B13` (ou `B10`) | String (14 dígitos) |
| **Categoria Declarada** | `CATEGORIA` | `B18` ("CPURA" / "Geradora") | `B18` ("CGRUPO") | String |
| **Data da Demonstração** | `DATA_DEMONSTRACAO_FINANCEIRA` | `B9` | `B9` | Date (YYYY-MM-DD) |
| **Ativo Total** | `ATIVO_TOTAL` | `G16` (ou `K16`) | `G16` (ou `K16`) | Float |
| **Ativo Circulante** | `ATIVO_CIRCULANTE` | `G14` (ou `K14`) | `G14` (ou `K14`) | Float |
| **Ativo Circ. Financeiro**| `ATIVO_CIRCULANTE_FINANCEIRO` | `G15` (ou `K15`) | `G15` (ou `K15`) | Float |
| **Passivo Circulante** | `PASSIVO_CIRCULANTE` | `G17` (ou `K17`) | `G17` (ou `K17`) | Float |
| **Passivo Circ. Financ.** | `PASSIVO_CIRCULANTE_FINANCEIRO` | `G18` (ou `K18`) | `G18` (ou `K18`) | Float |
| **Passivo Não Circ. Fin.**| `PASSIVO_NAO_CIRCULANTE_FINANCEIRO`| `G19` (ou `K19`) | `G19` (ou `K19`) | Float |
| **Patrimônio Líquido** | `PATRIMONIO_LIQUIDO` | `G20` (ou `K20`) | `G20` (ou `K20`) | Float |
| **Vendas Líquidas (ROL)** | `VENDAS_LIQUIDAS` | **`G24`** (ou `K24`) | **`G24`** (ou `K24`) | Float |
| **Lucro Líquido** | `LUCRO_LIQUIDO` | **`G25`** (ou `K25`) | **`G25`** (ou `K25`) | Float |
| **Fluxo Caixa Operacional**| `FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS`| **`G26`** (ou `K26`) | **`G26`** (ou `K26`) | Float |
| **PD Base da Planilha** | `PD_BASE_FICHA` | `B26` (Fórmula `IF(B18="CGRUPO",0.5%,G46)`) | `B26` (Valor 0.5%) | Float |
| **FCO/ROL da Planilha** | `FCO_ROL_FICHA` | `B27` | `B27` | Float |
| **ROA da Planilha** | `ROA_FICHA` | `B28` | `B28` | Float |
| **ROE da Planilha** | `ROE_FICHA` | `B29` | `B29` | Float |
| **Rating Board Copel** | `RATING_BOARD_COPEL` | `C32` | `C32` | String (A–E) |
| **Scores Individuais** | `SCORE_PD`, `SCORE_FCO`, etc. | **`H67:H79`** | **`N67:N79`** | Float |
| **Notas Individuais** | `NOTA_PD`, `NOTA_FCO`, etc. | **`G67:G79`** | **`M67:M79`** | String / Float |
| **Rating Copel Declarado**| `RATING_COPEL` | `B49` | `B49` | String (A–E) |

### 3.2 Mapeamento `padrao_6` (CPURA e CGRUPO)
* **Balanço e DRE:** Preenchidos no bloco `Q14:Q26` (Ativo Total `Q16`, Vendas Líquidas `Q24`, Lucro Líquido `Q25`, FCO `Q26`).
* **Scores e Notas:** Em CPURA localizados nas colunas `G/H`; em CGRUPO nas colunas `M/N`.
* **Rating Copel:** Célula `B49` (ou `C32` para Board Copel).
* **Aderência NT v7 Comprovada:** 83 de 83 fichas vigentes reproduzem $1 / (1 + e^{-z})$ com tolerância $< 10^{-6}$.

### 3.3 Layouts Legados `padrao_1` a `padrao_5`
* Fichas históricas sem réguas completas de scores ou rating Copel.
* **Diretriz do Planejamento v1.2 §6.4:** Manter os dados observados da época como cadastrados. Não tentar forçar ou recalcular retroativamente ratings de fichas que não possuíam o modelo implementado no Excel.

### 3.4 Fichas de Consumidores (`v1`, `v2`, `v3`)
* **Consumidor $\ge 5$ MWm:** Extrai demonstrações financeiras completas da ficha e aplica o recálculo contábil com distribuição t-Student ($df=6$, escala 1.2) conforme NT v7 §9.
* **Consumidor $< 5$ MWm:** Extrai dados de Bureau (Score Risk 3, Restritivos, PD declarada). Campos de DF são classificados como `NAO_APLICAVEL` (e não como pendência ou erro), conforme Planejamento v1.2 §3.2.

---

## 4. ESPECIFICAÇÃO TÉCNICA DA CAMADA SILVER

### 4.1 Contrato da Tabela Silver `fichas_comercializadoras_extraidas`
A tabela Silver é enriquecida com os novos campos de linhagem e auditoria, sem quebrar contratos downstream:

1. **Campos Contábeis Padronizados:** `ATIVO_TOTAL`, `ATIVO_CIRCULANTE`, `PASSIVO_CIRCULANTE`, `PATRIMONIO_LIQUIDO`, `VENDAS_LIQUIDAS`, `LUCRO_LIQUIDO`, `FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS`.
2. **Campos de Controle da Origem (`_FICHA`):** `PD_BASE_FICHA`, `FCO_ROL_FICHA`, `ROA_FICHA`, `ROE_FICHA`.
3. **Classificação e Subsegmento:** `SEGMENTO` (`CPURA` / `CGRUPO`), `SUBSEGMENTO` (`COMERCIALIZADORA` / `GERADORA`).
4. **Metadados de Linhagem Técnica:** `versao_layout`, `hash_arquivo`, `_DATA_PROCESSAMENTO`, `_VERSAO_REGISTRO`, `_STATUS_REGISTRO`.

### 4.2 Idempotência e Reprocessamento SCD2
* Reprocessamento de arquivos não apaga versões anteriores.
* Ao reprocessar as 74 fichas vigentes de `padrao_7` com os novos layouts:
  * Versão anterior: `_STATUS_REGISTRO = 'SUBSTITUIDO'`.
  * Nova versão: `_VERSAO_REGISTRO = 2`, `_STATUS_REGISTRO = 'VIGENTE'`.
  * Hash do arquivo atualizado e trilha mantida.

---

## 5. CAMADA RELACIONAL: MOTOR DE CRÉDITO E VALIDAÇÃO PARALELA

### 5.1 Correção Matemática de `src/domain/credito/pd_base.py`
A função real `calcular_pd_base` será corrigida e modularizada:
* **Fórmula Oficial (NT v7 §4):**
  $$z = -4,03 - 3,70 \cdot X_{12} + 11,66 \cdot X_{16} - 7,86 \cdot X_{19} - 11,33 \cdot X_{22}$$
  $$\text{PD}_{\text{calc}} = \frac{1}{1 + e^{-z}}$$
* **Tratamento de Insumos Inválidos (Decisão D5):**
  ```python
  if ativo_total is None or ativo_total <= 0:
      logger.warning(f"Insumo inválido para CNPJ={cnpj}: ATIVO_TOTAL nulo ou zero.")
      return None, "INSUMO_CONTABIL_INVALIDO"
  if vendas_liquidas is None or vendas_liquidas <= 0:
      logger.warning(f"Insumo inválido para CNPJ={cnpj}: VENDAS_LIQUIDAS nulo ou zero.")
      return None, "INSUMO_CONTABIL_INVALIDO"
  ```

### 5.2 Validação Paralela (Gate de Auditoria na Camada Relacional)
O módulo `validador_paralelo.py` realiza a confrontação:
* Compara $\text{PD}_{\text{calc}}$ vs $\text{PD}_{\text{ficha}}$ (tolerância $10^{-6}$).
* Compara Rating Recalculado vs Rating Declarado na ficha.
* **Geração de Status de Conciliação:**
  * `CONCILIADO`: recálculo Python idêntico ao cache da planilha.
  * `DIVERGENCIA_ARREDONDAMENTO`: diferença numérica dentro da máscara de formatação (`number_format`).
  * `DIVERGENCIA_ORIGEM`: diferença material decorrente de preenchimento manual ou divergência na ficha.
* Em conformidade com a Decisão D10, o valor oficial exibido nas consultas de crédito permanece o valor da ficha (`RATING_COPEL`), acompanhado da flag de auditoria.

### 5.3 População da `fato_analise_credito` e `fato_score_rating_pd`
* Eliminar os registros com `PD_BASE = NULO` gerando a linhagem completa:
  * Insumos $X_{12}, X_{16}, X_{19}, X_{22}$ persistidos.
  * Escore linear $z$ persistido.
  * $\text{PD}_{\text{base}}$ calculada persistida.
  * Scores individuais e Score Total persistidos.
  * Status da validação paralela registrado.

---

## 6. CRONOGRAMA DETALHADO DE IMPLEMENTAÇÃO

### FASE 0: Inventário e Auditoria Física (100% CONCLUÍDA)
- [x] Inventário quantitativo de 797 registros em `docs/inventario_fichas.csv`.
- [x] Rastreamento de precedentes e fórmulas em `docs/amostras/p7_rastreio_precedentes.csv`.
- [x] Prova matemática do recálculo da NT v7 em 83 fichas de `padrao_6`.
- [x] Leitura física de $B18$ nas 34 fichas de geradoras.
- [x] Relatório analítico emitido: `docs/investigacao_fase_07.md`.

### FASE 1A: Layouts v7/v6, Motor `pd_base.py` e Validação Paralela (EM APROVAÇÃO)
1. **Catálogos e Schemas:**
   - Criar `ENTRADAS/control/layouts/layout_ficha_comercializadora_v7_cpura.json`.
   - Criar `ENTRADAS/control/layouts/layout_ficha_comercializadora_v7_cgrupo.json`.
   - Ajustar `catalogo_layouts_ficha_comercializadora.json` para despachar `padrao_7_cpura` e `padrao_7_cgrupo`.
   - Atualizar `master_catalog_comercializadoras.json` com campos `_FICHA` e subsegmento.
2. **Extrator Silver:**
   - Ajustar o classificador e o extrator para aplicar os layouts dedicados e registrar `SUBSEGMENTO = 'GERADORA'`.
   - Testar reprocessamento das 74 fichas de `padrao_7` via SCD2.
3. **Motor Relacional de Risco:**
   - Corrigir a função `calcular_pd_base` em `src/domain/credito/pd_base.py` para $1 / (1 + e^{-z})$.
   - Implementar `validador_paralelo.py` com classificação `CONCILIADO` / `DIVERGENCIA_ORIGEM`.
   - Atualizar a pipeline de cálculo da `fato_analise_credito` e `fato_score_rating_pd`.
4. **Validação de Saída:**
   - Script de teste de regressão validando 100% das 83 fichas de `padrao_6` e 40 de `padrao_7`.

### FASE 1B: Módulo de Carga Manual e Overrides (BACKLOG)
- Implementar fluxo de carga manual com chave exata (`CNPJ + DATA_DF + CAMPO_AFETADO`) conforme Planejamento v1.2 §4.5.

### FASE 2: Fichas de Consumidores (BACKLOG)
- Atualizar layouts de consumidores ($\ge 5$ MWm com DF e $< 5$ MWm com Bureau Risk 3).

---

## 7. CRITÉRIO DE ACEITE E VERIFICAÇÃO

A Fase 1A será considerada homologada quando:
1. **Zero Nulos no `padrao_7`:** Vendas Líquidas, Lucro Líquido e FCO extraídos com sucesso nas 40 fichas vigentes de CPURA.
2. **Zero Fichas INDEFINIDO no `padrao_7`:** As 34 fichas de Geradoras classificadas com sucesso como CPURA (`SUBSEGMENTO = 'GERADORA'`).
3. **Acurácia Matemática de 100%:** A função corrigida de `pd_base.py` reproduzir as 83 fichas de `padrao_6` com precisão $< 10^{-6}$.
4. **Idempotência SCD2 Preservada:** Nenhuma linha do histórico da Silver apagada; novas extrações versionadas como `_VERSAO_REGISTRO = 2`.
5. **Zero Fórmulas Excel Alteradas:** Fichas originais em `ENTRADAS/` permanecem estritamente intactas e imutáveis.
