# RELATÓRIO DE AUDITORIA TÉCNICA — SISTEMA BDC

**Data da Auditoria:** 24/09/2026  
**Auditor(a):** Auditoria Técnica Sênior de Engenharia de Dados  
**Repositório:** `C:\Users\C807951\Desktop\BDC`  
**Documentos Base (Fontes da Verdade):**

1. *Planejamento do Sistema de Gestão de Dados de Crédito — BD Crédito* (v1.2, 21/07/2026) — Seções 7.2, 8, 9 e 10.
2. *Nota Técnica — PD e Taxa de Risco de Crédito (TRC)* (v7, 10/09/2026) — Seções 4 a 11.

---

### A. Inventário da Árvore de Código

O levantamento detalhado das pastas de código-fonte (`src/`, scripts auxiliares em raiz e diretório `tests/`) apresenta a seguinte distribuição física de responsabilidades em comparação à arquitetura modular planejada (Seção 10 do Planejamento):

| Pasta / Pacote | Nº Arqs | Responsabilidade Real Observada | Responsabilidade Planejada (Doc Lucas §10) | Aderente? |
|---|:---:|---|---|:---:|
| `src/app/` | 1 | Ponto de entrada do pipeline unificado (`main.py` de orquestração interna). | `app/`: Aplicação principal, CLI, Streamlit, orquestrador de execução. | **Sim** |
| `src/cli/` | 2 | Subcomandos de linha de comando (`cli_execucao.py`, `cli_overrides.py`). | `cli/`: Comandos e interfaces de linha de comando. | **Sim** |
| `src/common/` | 4 | Constantes do sistema, classes de erro (`erros.py`), tipos base e utilitários gerais. | `common/`: Utilitários compartilhados, logging, configuração, exceções. | **Sim** |
| `src/control/` | 6 | Logs estruturados, manifestos de execução, rastreadores e orquestrador de pipeline (`pipeline_orquestrador.py`). | `control/`: Controle de execução, manifests, logs, rastreabilidade, orquestrador. | **Sim** |
| `src/staging/` | 12 | Ingestão e triagem de arquivos brutos (Salesforce, Denodo, MtM, Fichas, Overrides, Blacklist). | `staging/`: Triagem de arquivos, ingestão de dados brutos, integridade física. | **Sim** |
| `src/storage/` | 4 | Leitores e gravadores de repositório Parquet/CSV particionado e versionado. | `storage/`: Persistência física, parquet writer, versionamento, SCD2. | **Sim** |
| `src/silver/` | 6 | Padronização técnica, deduplicação, normalização e aplicação de gates de qualidade técnica. | `silver/`: Deduplicação, normalização, enriquecimento estrutural, aplicação de gates. | **Sim** |
| `src/domain/fichas/` | 9 | Motores de extração e parsing de planilhas de fichas cadastrais (v1, v2, v3, migração). | `domain.fichas`: Extração de fichas cadastrais por versão de layout. | **Sim** |
| `src/domain/contrapartes/` | 4 | Normalização de contrapartes, cruzamento CNPJ/grupo econômico e segmentação. | `domain.contrapartes`: Unificação de cadastros, hierarquia de grupos econômicos. | **Sim** |
| `src/domain/consumidores/` | 2 | Classificação e tratamento específico de consumidores livres (≤5MWm vs >5MWm). | `domain.consumidores` (subdomínio previsto nas regras de enquadramento). | **Parcial** *(sobrepõe `contrapartes/segmentacao.py`)* |
| `src/domain/credito/` | 9 | Motores de cálculo de PD (CPURA, CGRUPO, Consumidores), Motor de PE e Taxa de Risco. | `domain.credito`: Motores de cálculo de rating, PD, PE, EAD, LGD, TRC. | **Sim** *(Centralização estrita)* |
| `src/domain/salesforce/` | 3 | Processamento de regras de negócio de propostas e aprovações do Salesforce. | `domain.salesforce`: Ingestão e regras de negócio de propostas/aprovações. | **Sim** |
| `src/domain/denodo/` | 1 | Ingestão e normalização de contratos vigentes e operações do Denodo. | `domain.denodo` / `domain.mtm`: Ingestão de operações correntes e MtM. | **Sim** |
| `src/domain/mtm/` | 2 | Curva MtM de contratos e exposição de mercado. | `domain.mtm`: Processamento de curvas e marcação a mercado. | **Sim** |
| `src/domain/risco/` | 2 | **CÓDIGO MORTO / DUPLICADO:** Contém cópia idêntica de `servico_mtm.py`. | Não previsto no planejamento (redundante com `domain/mtm/` e `domain/credito/`). | **Não** |
| `src/domain/garantias/` | 1 | Processamento de garantias vinculadas a contratos e operações. | `domain.garantias`: Ingestão e validação de garantias vinculadas. | **Sim** |
| `src/domain/carga_manual/` | 5 | Ingestão, governança de overrides, dupla custódia e validação de eventos manuais. | `domain.carga_manual`: Governança de ajustes manuais, aprovação, audit trail. | **Sim** |
| `src/domain/auditoria/` | 1 | Rastreabilidade e verificação de regras de conformidade. | `domain.auditoria`: Validação de regras e integridade do processo. | **Sim** |
| `src/domain/bureau/` | 2 | Ingestão e cliente de cache do bureau de crédito RISK3. | Previsto no ecossistema de dados cadastrais/externos. | **Sim** |
| `src/relational/` | 20 | Modelagem dimensional: 7 Dimensões (`dimensions/`), 10 Fatos (`facts/`), `servico_relational.py`. | `relational/`: Fatos e dimensões (Apêndice 8 do planejamento). | **Parcial** *(Violação de camada em `fato_alertas`)* |
| `src/gold/` | 6 | Construção das visões consolidadas de negócio e relatórios analíticos. | `gold/`: Visões consolidadas e relatórios analíticos (§7.2 do doc Lucas). | **Parcial** *(Falta de cobertura dos 14 relatórios)* |
| `src/services/` | 1 | `servico_limites.py`: Geração da planilha Excel para o modelo de limites. | `services/`: Serviços de exportação e integrações downstream. | **Sim** |
| `src/ui/` | 6 | Frontend em Streamlit: `app.py`, componentes e 4 visões analíticas. | Previsto em `app/` (Visualizações / Streamlit). | **Sim** |
| `tests/` | 27 | Suíte de testes unitários e de integração (`unitarios/`, `integracao/`). | `tests/`: Testes automatizados por módulo. | **Sim** |
| Raiz (`./`) | 5 | `main.py`, `reset.py`, `0_obter_e_triar.py`, `scratch_auditoria_carteira.py`, `scratch_executar_e_auditar.py`. | Scripts raiz (Pipeline operacional principal vs scripts de debug descartáveis). | **Parcial** *(Clutter de scripts de dev na raiz)* |

---

### B. Matriz de Redundância e Oportunidades de Consolidação

A avaliação foi conduzida sob a **Escada das 7 Perguntas**:

1. *Isso precisa existir?* (YAGNI / Escopo)
2. *Já existe algo parecido?* (Reuso / Consolidação)
3. *A stdlib do Python resolve?*
4. *Algum recurso nativo da plataforma resolve?* (Pandas / PyArrow / Parquet)
5. *Uma dependência já instalada resolve?*
6. *O código cabe em uma linha / solução mínima?*
7. *Qual é o mínimo absoluto que funciona?*

| Arquivo / Função A | Arquivo / Função B | Tipo de Problema | Pergunta da Escada que Resolve | Recomendação | Risco de Consolidar |
|---|---|---|---|---|:---:|
| `src/domain/risco/servico_mtm.py` | `src/domain/mtm/servico_mtm.py` | **Duplicação Exata / Código Morto** | **Pergunta 1 (YAGNI)** e **Pergunta 2 (Reuso):** O módulo `domain/risco/` é uma réplica abandonada de `domain/mtm/`. Nenhuma linha do pipeline oficial importa `domain.risco`. | **Remover** pasta `domain/risco/` integralmente. | **Baixo** (Zero imports no codebase ativo). |
| `src/domain/consumidores/classificacao.py` | `src/domain/contrapartes/segmentacao.py` e `servico_enquadramento.py` | **Duplicação Lógica / Fragmentação de Domínio** | **Pergunta 2 (Reuso):** Ambos os arquivos definem regras para separar Consumidor Livre ≤5MWm e >5MWm. Em `contrapartes/segmentacao.py` a lógica é feita por colunas de volume, enquanto em `consumidores/classificacao.py` reimplementa checagem idêntica. | **Consolidar** regras de enquadramento de contrapartes e consumidores em `domain/contrapartes/segmentacao.py`. | **Médio** (Requer conferir mapeamentos no orquestrador e nos testes unitários). |
| `src/relational/facts/fato_alertas.py` (Linha 15) | `src/gold/servico_gold.py` | **Violação Grave de Camada (Inversão Medalhão)** | **Pergunta 1 (Arquitetura) / Pergunta 7 (Mínimo):** `fato_alertas.py` lê diretamente de `SAIDAS/gold/visao_operacional_negocio/Visao_Operacional_BDC_LATEST.parquet` em vez de ler as tabelas Silver ou Fatos relacionais base (`fato_analise_credito`, `fato_exposicao_risco`). Isso quebra a idempotência e inverte o fluxo Medalhão (Silver → Relational → Gold). | **Refatorar** `fato_alertas.py` para consumir dimensões e fatos da camada Relational, permitindo que a camada Gold seja a última a ser gerada. | **Médio** (Corrige a ordem de execução do pipeline em `main.py`). |
| `src/gold/servico_contratos.py`, `servico_analises.py`, `servico_risco.py`, `servico_eventos_manuais.py` | `src/gold/servico_gold.py` | **Fragmentação Excessiva de Módulos Helper** | **Pergunta 6 (Mínimo):** Nenhum desses 4 submódulos gera tabelas Gold independentes. Eles são apenas joins intermediários chamados em sequência estrita por `servico_gold.py` para formar a tabela única `Visao_Operacional_BDC`. | **Consolidar** ou agrupar os builders dentro de `servico_gold.py` (ou pacote interno privado `gold/builders/`), tornando evidente que há apenas uma saída de negócio. | **Baixo** (Trata-se de reorganização interna sem alterar schema final). |
| Scripts da raiz: `scratch_auditoria_carteira.py`, `scratch_executar_e_auditar.py`, `0_obter_e_triar.py` | Diretório `scratch/` e `src/staging/` | **Clutter / Scripts Descartáveis de Dev em Produção** | **Pergunta 1 (YAGNI):** `0_obter_e_triar.py` foi o protótipo inicial do staging. Os arquivos `scratch_*.py` na raiz foram criados para depuração pontual e não fazem parte do pipeline oficial `main.py`. | **Mover** para `scratch/` ou arquivar em pasta de tooling/dev fora do pacote de produção. | **Baixo** (Não afeta a esteira produtiva). |

---

### C. Camadas Gold — Mapa de Consumo

O documento funcional de Planejamento (Seção 7.2) prevê a entrega de **14 relatórios e visões analíticas**. A auditoria comparou as saídas físicas e endpoints de escrita do código atual contra essa especificação e contra os reais consumidores no repositório:

| Saída Prevista (Planejamento §7.2) | Tabela / Arquivo Físico Gerado | Gerado por | Consumidor Identificado no Código | Status Atual |
|---|---|---|---|:---:|
| **1. Relatório de Crédito Atual** | `SAIDAS/gold/visao_operacional_negocio/Visao_Operacional_BDC_LATEST.parquet` | `src/gold/servico_gold.py` | `src/ui/views/visao_governanca.py`, `src/services/servico_limites.py` e `fato_alertas.py`. | **Ativa** (Saída Master) |
| **2. Relatório Analítico** | Não gerado como tabela Gold separada. | — | Incorporado visualmente nas agregações do Streamlit (`src/ui/views/visao_carteira.py`). | **Parcial / Embutido** |
| **3. Relatório de Vencimentos** | Não gerado como tabela Gold separada. | — | Exibido via filtro de vigência/validade em `src/ui/views/visao_carteira.py`. | **Órfã de Arquivo** (Existe só em UI) |
| **4. Histórico de Análises** | Gerado na Relational: `fato_analise_credito.parquet`. | `src/relational/facts/fato_analise_credito.py` | Lido por `servico_gold.py` e tela Streamlit. Não tem export Gold dedicado. | **Ativa na Relational** |
| **5. Matriz de Transição de Rating** | Gerado na Relational: `fato_migracao_rating.parquet`. | `src/relational/facts/fato_migracao_rating.py` | **Nenhum consumidor direto em Gold ou UI.** | **Órfã** (Fato relacional sem visão Gold de consumo) |
| **6. Histórico de Perda Esperada** | Gerado na Relational: `fato_exposicao_risco.parquet`. | `src/relational/facts/fato_exposicao_risco.py` | Consumido por `servico_gold.py`. | **Ativa na Relational** |
| **7. Relatório de Garantias** | Gerado na Relational: `fato_garantia.parquet`. | `src/relational/facts/fato_garantia.py` | Não consumido em Gold consolidado. | **Órfã** (Fato relacional sem visão Gold de consumo) |
| **8. Pendências e Inconsistências** | Gerado na Relational: `fato_divergencia_contratual.parquet` e `fato_alertas.parquet`. | `src/relational/facts/fato_divergencia_contratual.py` | Consumido por `src/ui/views/visao_governanca.py`. | **Ativa** |
| **9. Relatório de Auditoria** | `SAIDAS/controles/` (`manifesto_execucao_*.json`). | `src/control/manifesto.py` | Consumido pelo painel de controle e governança. | **Ativa** |
| **10. Relatório de Contratos Correntes** | `SAIDAS/gold/visao_carteira/Visao_Carteira_Contratos.parquet` | `src/gold/servico_gold.py` | Consumido por `src/ui/views/visao_carteira.py`. | **Ativa** |
| **11. Relatório de Enquadramento** | `dim_contraparte.parquet` (campo `SEGMENTO_CREDITO`). | `src/relational/dimensions/dim_contraparte.py` | Integrado nas visões Gold gerais. | **Ativa na Relational** |
| **12. Reconciliação Denodo × MtM** | Gerado em `fato_divergencia_contratual.parquet`. | `src/relational/facts/fato_divergencia_contratual.py` | Consumido em governança. | **Ativa na Relational** |
| **13. Histórico de Atualizações Manuais** | Gerado em `fato_eventos_manuais.parquet`. | `src/relational/facts/fato_eventos_manuais.py` | Consumido por `src/gold/servico_eventos_manuais.py`. | **Ativa** |
| **14. Arquivo Modelo de Limites** | `SAIDAS/output/entrada_limites_credito_LATEST.xlsx` | `src/services/servico_limites.py` | Consumidor Externo (Planilha de Limites Downstream). | **Ativa** |

**Diagnóstico Factual da Camada Gold:**

- O projeto físico **não gera 14 arquivos Gold diferentes**. Ele gera apenas **2 Parquets Gold master** (`Visao_Operacional_BDC_LATEST.parquet` e `Visao_Carteira_Contratos.parquet`) mais **1 export em Excel** (`entrada_limites_credito_LATEST.xlsx`).
- As demais saídas funcionais previstas no Planejamento foram modeladas como **Fatos Relacionais** e consumidas diretamente pelo Streamlit (`visao_governanca.py`, `visao_carteira.py`), o que atende ao consumo analítico sem a necessidade de duplicar espaço em disco criando dezenas de tabelas Gold redundantes.

---

### D. Achados sobre a Fórmula de PD/TRC

A auditoria inspecionou os arquivos sob `src/` em busca de divergências, duplicações de fórmulas ou vazamentos de cálculo de risco para camadas indevidas (Silver/Gold):

1. **Centralização e Unicidade (FATO):**
   - Os cálculos de Probabilidade de Default (PD), Perda Esperada (PE) e Taxa de Risco de Crédito (TRC) estão **100% centralizados no pacote `src/domain/credito/`**.
   - Não foi encontrada **nenhuma reimplementação paralela** ou fórmula solta em scripts de Silver, Gold ou Staging.

2. **Aderência à Nota Técnica v7 por Segmento:**
   - **Comercializadoras Puras (CPURA):**
     - Arquivo: `src/domain/credito/pd_cpura.py`
     - Implementa o modelo de regressão logística de Assaf Neto baseado nos 6 índices contábeis ($X_1$ a $X_6$), calculando o Score de Solvência ($Z$) e interpolando linearmente a PD em conformidade estrita com a Tabela da Nota Técnica.
   - **Comercializadoras Ligadas a Grupos (CGRUPO):**
     - Arquivo: `src/domain/credito/pd_cgrupo.py`
     - Mapeia o Rating de Agência Externa (S&P, Moody's, Fitch) para a Escala Padronizada e atribui a PD de tabela NCE 4.03.
   - **Consumidores Livres ≤ 5 MWm (Sem DF obrigatória):**
     - Arquivo: `src/domain/credito/pd_consumidor_le5.py`
     - Consome diretamente o Score do bureau de crédito (RISK3) e aplica o mapeamento de PD previsto na Seção 6 da Nota Técnica. Quando o bureau não está disponível ou a validade expirou, aplica a regra de PD Substituta / Penalização.
   - **Consumidores Livres > 5 MWm (Com DF):**
     - Arquivo: `src/domain/credito/pd_consumidor_gt5.py`
     - Implementa a regressão multivariada com calibração pela distribuição t-Student conforme prescrito na Nota Técnica v7.
   - **Motor de Risco e Perda Esperada:**
     - Arquivos: `src/domain/credito/motor_pe.py` e `src/domain/credito/motor_taxa_risco.py`
     - Fórmulas de Perda Esperada ($PE = EAD \times LGD \times PD$) e Taxa de Risco de Crédito ($TRC$) implementadas de forma unificada e consumidas exclusivamente pelo fato relacional `fato_exposicao_risco.py`.

3. **Validação das Camadas Silver e Gold:**
   - **FATO:** Nenhuma coluna de PD, Rating ou Score é calculada dentro de `src/silver/`. A camada Silver limita-se a extrair os campos declarados nas fichas de origem (DF) e validar a consistência cadastral.
   - **FATO:** As visões Gold (`servico_gold.py`) apenas realizam agregações e projeções de fatos já calculados na camada Relacional (`fato_score_rating_pd`, `fato_exposicao_risco`), respeitando a governança de engenharia de dados.

---

### E. Plano de Consolidação Sugerido (Não Executado)

Recomendações técnicas priorizadas por impacto e esforço, visando simplificar a manutenção do sistema por um único desenvolvedor:

#### Prioridade 1: Alto Impacto / Baixo Esforço (Higienização e Correção Arquitetural)

1. **Remoção de Código Morto em `src/domain/risco/`:**
   - *Ref. Matriz:* Item 1.
   - *Ação:* Apagar a pasta `src/domain/risco/` (`servico_mtm.py` idêntico e sem uso).
   - *Impacto:* Reduz a confusão conceitual entre `domain/mtm` e `domain/risco`. Zero risco de regressão.

2. **Correção do Vazamento de Camada em `fato_alertas.py`:**
   - *Ref. Matriz:* Item 3.
   - *Ação:* Ajustar `src/relational/facts/fato_alertas.py` para construir suas regras a partir dos Fatos e Dimensões relacionais (`fato_analise_credito`, `dim_contraparte`, `fato_exposicao_risco`), eliminando a leitura circular da Gold (`Visao_Operacional_BDC_LATEST.parquet`).
   - *Impacto:* Restaura a linhagem limpa do pipeline medalhão (Silver → Relational → Gold).

3. **Limpeza da Raiz do Projeto:**
   - *Ref. Matriz:* Item 5.
   - *Ação:* Mover os scripts auxiliares de teste/debug (`scratch_auditoria_carteira.py`, `scratch_executar_e_auditar.py`, `0_obter_e_triar.py`) para a pasta `scratch/` ou pasta `tools/`.
   - *Impacto:* Deixa a raiz do repositório profissional e limpa, contendo apenas `main.py` e `reset.py`.

#### Prioridade 2: Médio Impacto / Médio Esforço (Consolidação de Módulos Helper)

4. **Unificação dos Módulos Helper da Camada Gold:**
   - *Ref. Matriz:* Item 4.
   - *Ação:* Agrupar os 4 arquivos satélites (`servico_contratos.py`, `servico_analises.py`, `servico_risco.py`, `servico_eventos_manuais.py`) dentro de um módulo estruturado ou consolidá-los em classes de transformação coesas chamadas por `servico_gold.py`.
   - *Impacto:* Torna a camada Gold mais legível para apresentação, evidenciando que ela gera uma visão unificada e não 5 subsistemas dispersos.

5. **Consolidação de Enquadramento (`domain/consumidores` vs `domain/contrapartes`):**
   - *Ref. Matriz:* Item 2.
   - *Ação:* Centralizar toda a lógica de enquadramento de porte e tipo de contraparte (Consumidor ≤5MWm, >5MWm, Comercializadora) em `src/domain/contrapartes/segmentacao.py`.
   - *Impacto:* Evita que regras de limite de volume (5MWm) fiquem declaradas em mais de um arquivo.

---

### F. Itens Pendentes de Validação Manual

Os seguintes pontos foram identificados na leitura estática do código, mas sua validação funcional e volumétrica depende de execução controlada e testes de ponta a ponta:

1. **Comportamento de `fato_migracao_rating.py` e `fato_garantia.py`:**
   - *Incerteza:* O pipeline gera fisicamente essas tabelas relacionais em `SAIDAS/relational/facts/`, porém não há nenhum componente do frontend Streamlit (`src/ui/`) ou relatório Gold que as consuma atualmente.
   - *Validação Manual Necessária:* Confirmar com o gestor se esses fatos devem ser exibidos em uma nova aba do Streamlit (ex.: aba dedicada a Garantias e Matriz de Transição) ou se o cálculo pode ser mantido apenas para fins de auditoria em banco.

2. **Impacto do Ajuste de Linhagem de `fato_alertas.py`:**
   - *Incerteza:* Ao desacoplar `fato_alertas.py` da tabela Gold, é necessário checar se todas as colunas derivadas de joins (ex.: junção de contratos Salesforce + Denodo + Rating) estão disponíveis de forma idêntica diretamente nos fatos relacionais.
   - *Validação Manual Necessária:* Executar o pipeline gerando o `fato_alertas` a partir dos fatos relacionais e rodar um teste de comparação de schemas e valores antes e depois da refatoração.

3. **Persistência de Cache do RISK3 (`ENTRADAS/bureau/cache/risk3_cache.json`):**
   - *Incerteza:* O cliente de bureau utiliza um arquivo JSON local como cache offline. É necessário validar em ambiente real se requisições para novos CNPJs que retornam status de não encontrado (`N/A`) persistem adequadamente a marcação de carência/penalização na Silver sem reexecutar chamadas desnecessárias à API.

---

*Relatório de Auditoria concluído com estrita observância à regra de SOMENTE LEITURA. Nenhuma linha de código ou arquivo de produção foi alterado.*
