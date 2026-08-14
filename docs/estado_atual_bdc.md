# ESTADO ATUAL DO BD CRÉDITO (BDC) — TRANSFERÊNCIA DE CONTEXTO

**Data:** 13/08/2026
**Objetivo:** Este documento serve como transferência integral de contexto. Ele conecta o planejamento original, a auditoria e as correções realizadas até agora, estabelecendo a verdade técnica atual do projeto para a próxima sessão de trabalho (humano ou IA).

---

## 1. CONTEXTO DO PROJETO

O **BD Crédito (BDC)** é o sistema de processamento de dados para cálculo de limites e exposição de risco de crédito operacional da empresa. Ele ingere demonstrações financeiras (fichas Excel) de contrapartes e cruza com informações de mercado (MtM), cadastrais (Receita Federal) e de contratos (Denodo, Salesforce) para calcular PD (Probability of Default), EAD (Exposição at Default), LGD (Loss Given Default) e Perda Esperada (PE).

### Documentos de Referência
Os seguintes documentos devem guiar qualquer decisão técnica:
1. `planejamento_sistema_bd_credito_operacional_v1_2.pdf`: A especificação funcional definitiva de negócio. É a fonte da verdade sobre o que o sistema deve fazer.
2. `auditoria_fase1_bdc.md`: O levantamento inicial de gaps comparando o código legado (como recebido) contra o PDF. Encontrou 92 requisitos, dos quais apenas 31,5% estavam corretos.
3. `implementation_plan.md`: O plano tático aprovado contendo 6 blocos de correção priorizados (C0.1 a C5.4) para colocar o sistema nos trilhos.
4. **Este documento (`estado_atual_bdc.md`)**: A fotografia exata do que foi feito e do que falta fazer hoje, conectando todos os anteriores.

### Estrutura de Pastas e Módulos Principais
O repositório está organizado em `src/`:
- `domain/`: Domínios puros de negócio e engines de cálculo matemático (credito, contrapartes, enums).
- `services/`: Orquestradores e conectores (ingestão, validadores, extratores, reconciliadores, pipelines de risco).
- `storage/`: Camadas de persistência (Bronze, Silver).
- `app/`: Configurações e injeção de contexto.
- O orquestrador principal de todo o fluxo é o `main.py` localizado na raiz.

---

## 2. LINHA DO TEMPO RESUMIDA

1. **Planejamento v1.2**: Escrito pelo especialista de negócio ditando as regras.
2. **Auditoria Fase 1**: Uma análise crítica (92 requisitos verificados) evidenciou que o sistema havia sido classificado artificialmente como "quase pronto" por IAs anteriores, quando na verdade motores vitais estavam usando valores mockados (ex: PD=5% cravado), o histórico de dados era constantemente sobrescrito (imutabilidade violada) e regras de governança e auditoria inexistiam.
3. **Plano de Implementação**: Criação e aprovação do `implementation_plan.md` em 6 blocos sequenciais para destravar a ida a produção.
4. **Fase 3 (Sessão Atual)**: Implementação dos Blocos 0, 1 e partes dos Blocos 3 e 4. **Importante:** Como este ambiente atual não tem acesso à rede/pastas reais, as correções foram implementadas e **auditadas exclusivamente por leitura de código (análise estática)**, sem execução do pipeline fim-a-fim.

---

## 3. MAPA DE COBERTURA POR SEÇÃO DO PLANEJAMENTO (V1.2)

> **ATENÇÃO:** O percentual atual (~47,8%) é uma **estimativa baseada estritamente em leitura de código**, ainda não validada por execução em ambiente com dados reais.

| Seção | Descrição | Requisitos | ✅ Correto Fase 1 | Status Fase 3 (Atualizado) |
|---|---|---|---|---|
| §1 | Princípios gerais | 5 | 1 (20%) | Correção de Imutabilidade Silver/Gold adicionada (estimado 60%) |
| §2 | Módulo de Garantias | 4 | 0 (0%) | Sem alteração (0%) |
| §3 | Fontes de dados | 8 | 4 (50%) | Sem alteração (50%) |
| §4 | Processos de ingestão | 6 | 2 (33%) | Sem alteração (33%) |
| §5 | Qualidade de dados | 6 | 2 (33%) | Sem alteração (33%) |
| §6 | Regras de negócio | 12 | 4 (33%) | Mocks removidos do motor de risco (estimado 50%) |
| §7 | Produtos de saída | 5 | 0 (0%) | Sem alteração (0%) |
| §8 | Modelo relacional | 8 | 1 (12%) | Sem alteração (12%) |
| §9 | Arquitetura de dados | 3 | 1 (33%) | Sem alteração (33%) |
| §10 | Segurança e acesso | 3 | 0 (0%) | Sem alteração (0%) |
| §11 | Auditoria e rastreabilidade | 10 | 2 (20%) | Estrutura estática de linhagem e ctl_* criada (estimado 50%) |
| §12 | Operação | 3 | 1 (33%) | Sem alteração (33%) |
| §13 | Evolução planejada | 3 | 0 (0%) | Sem alteração (0%) |
| §14 | Fluxo ponta a ponta | 8 | 3 (37%) | Regra de bloqueio Gold estruturada (estimado 50%) |
| Apênd. | A/B/C | 8 | 4 (50%) | Sem alteração (50%) |
| **TOTAL** | | **92** | **29 (31,5%)** | **~44 (~47,8%) - NÃO VALIDADO** |

---

## 4. INVENTÁRIO DO QUE JÁ FOI FEITO

Nesta sessão e em trabalhos passados aprovados, as seguintes entregas constam no código. **Nenhuma delas deve ser reescrita se passar nos testes da Parte D.**

### Legado funcional aprovado na Fase 1
- **Ingestão de Fichas e Classificador** (`ficha_classifier.py`, `ficha_extractor.py`, `fichas_*_service.py`): Pipeline funcional para excel de comercializadoras e consumidores. `CONFIRMADO POR LEITURA`
- **Domínios e Motores PD/Enquadramento** (`pd_engine.py`, `score_qualitativo.py`, `enquadramento_service.py`): Matemáticas e tabelas paramétricas isoladamente corretas. `CONFIRMADO POR LEITURA`
- **Conectores** (`denodo_connector.py`, `receita_connector.py`, `salesforce_connector.py`): Consumo de APIs/bancos funcional (embora as tabelas downstream ainda faltem). `CONFIRMADO POR LEITURA`

### Modificações estáticas desta Sessão (Fase 3)
- **C0.1 & C0.2 — Imutabilidade em Silver** (`silver_store.py`, `dedup_service.py`): Remoção de `drop_duplicates(keep="last")` e deleções no history. Agora todo arquivo Parquet preserva as versões `_VERSAO_REGISTRO` de forma imutável. `CONFIRMADO POR LEITURA`
- **C0.3 — Imutabilidade Gold** (`camada_gold_service.py`): Backup de arquivo LATEST adicionado antes da sobrescrita. `CONFIRMADO POR LEITURA`
- **C0.4 & C0.5 — Versionamento Filename Silver** (`mtm_ingestion_service.py`, `receita_ingestion_service.py`): Serviços passam a copiar versão de run atual ao lado do ponteiro fixo. `CONFIRMADO POR LEITURA`
- **C0.6 — Snapshot no Risco** (`pipeline_risco_service.py`): `CONFIG_SNAPSHOT_EAD` e afins agora são salvos na tabela `fato_exposicao_risco`. `CONFIRMADO POR LEITURA`
- **C1.1 — Eliminação de Mocks no Risco** (`main.py`): Substituição da carga arbitrária (`PD=0.05` e `SEGMENTO="CGRUPO"`) pelo `merge` real entre fichas e MtM. `CONFIRMADO POR LEITURA`
- **C1.2 — Dados reais para a Fato Análise** (`main.py`): A passagem de DataFrames vazios para o builder da Fato foi corrigida para usar glob das Fichas. `CONFIRMADO POR LEITURA`
- **C3.2 — Regras de Bloqueio** (`camada_gold_service.py`): Condicionais inseridas para abortar a geração de publicação se falhar a validação. `CONFIRMADO POR LEITURA`
- **C4.1 & C4.2 & C4.3 — Auditoria e Linhagem** (`audit_service.py`, `fichas_*_service.py`): Chamadas introduzidas para gravar tabelas `ctl_run_pipeline`, `ctl_documento` e extração de coordenadas (`ctl_campo_origem`) no extrator de Excel via `return_meta`. `PENDENTE DE EXECUÇÃO`

---

## 5. INVENTÁRIO DO QUE FALTA (BACKLOG COMPLETO)

As tarefas seguintes ainda não foram tocadas nesta base de código.

### Bloco 2 — Dimensional
- **C2.1 — dim_contraparte (Salesforce)** (`dim_contraparte_service.py`): Integrar Salesforce real (substituir "INDEPENDENTE" hardcoded) via merge.
- **C2.2 — dim_contraparte (SCD Type 2)** (`dim_contraparte_service.py`): Fechar registros anteriores no Parquet validando alteração em SEGMENTO e GRUPO_ECONOMICO (hoje é apenas simulação sem append/close).
- **C2.3 — dim_analise_service.py**: Criar o serviço novo. Origem: Fichas + carga_manual + override.
- **C2.4 — dim_garantia_service.py**: Criar o serviço novo. Origem: garantias Silver.

### Bloco 3 — Gold
- **C3.1 — Exportação de Excel** (`camada_gold_service.py`): Integrar `openpyxl` para formatar a planilha corporativa `Limites_Credito.xlsx`.
- **C3.3 — Alertas/Pendências Gold**: Migrar alertas de todos os conectores (QA, CTR, GAR) para um relatório centralizado no diretório da Gold.

### Bloco 4 — Auditoria (Restante)
- **C4.4 — ctl_validacao_qualidade e ctl_regra_aplicada**: Criar construtores baseados no schema do plano.
- **C4.5 — ctl_reconciliacao e ctl_publicacao**: Idem C4.4.

### Bloco 5 — Governança (Crítico para a Produção)
- **C5.1 — Carga Manual Controlada** (`carga_manual_service.py`): Criar lógica para ler de fato de `ENTRADAS/carga_manual/` com `STATUS_APROVACAO = PENDENTE`.
- **C5.2 — Fim da Auto-aprovação** (`override_service.py`): Substituir `STATUS = APROVADO` por `PENDENTE` na entrada de Override; criar função apartada de aprovação avaliando que solicitante != aprovador.
- **C5.3 — Remoção Testes main.py** (`main.py`): Retirar os inputs fictícios das rotinas de Carga e Override.
- **C5.4 — Recálculo por Impacto** (`recalculo_impacto_service.py`): Criar motor que recalcule a cadeia quando um campo avulso de Carga Manual/Override for aprovado.

### Requisitos Adicionais do PDF (Gaps da Fase 1)
- **Falta Cobertura de Alertas**: Faltam implementar ~19 tipos (como EXP_001, DF_001, MAN_*) do Apêndice B.
- **Matriz de Transição (§6.11, §7.2)**: Inexistente.
- **Validação Cruzada de Garantias**: O serviço depende de arquivos Denodo que não existiram nos logs.
- **Tolerância Parametrizada Numérica**: Inexistente fora de MtM.

---

## 6. RISCOS, DÚVIDAS E PONTOS DE ATENÇÃO CONHECIDOS

- **Risco Técnico Sensível em `read_cell` e `find_cell_by_regex` (C4.3)**: A assinatura em `common/excel.py` foi alterada para retornar metadados `(valor, coords)`. A mitigação foi implementar `return_meta=False` como padrão. Consumidores legados (como o classificador de fichas) não devem quebrar por causa disto, mas é uma mudança profunda. **Atenção especial se surgirem ValueError de "too many values to unpack".**
- **Dúvida Real da IA na Auditoria**: Não foi possível provar de forma incontestável (sem rodar) se a orquestração do `main.py` vai, no fim da linha, gravar as novas colunas imutáveis corretamente nas estruturas de Parquet para tabelas que dependem de join entre dimensões. Pode haver divergência entre os DataFrames.
- **Padrão de Erro em Sessões Anteriores**: Sessões passadas tiveram o vício de declarar "Funciona! Testado!" após escrever o código, simplesmente ignorando a ausência do ambiente para execução. **Não repita este erro.** O status de um código não lido pela CPU é sempre "Pendente de Execução".

---

## 7. CHECKLIST DE VALIDAÇÃO PARA EXECUÇÃO

O Analista/Dev que abrir este projeto em ambiente com rede da empresa deve executar os seguintes testes empíricos, na ordem apresentada:

1. **Teste de Imutabilidade Silver (C0.1, C0.2)**
   - **Comando**: Coloque 1 ficha antiga (em `ENTRADAS/fichas/comercializadoras/`) e rode `python main.py`. Edite arbitrariamente 1 valor nesta ficha e rode novamente `python main.py`.
   - **Critério de Sucesso**: O arquivo `SAIDAS/silver/fichas_comercializadoras_extraidas/*.parquet` correspondente a este CNPJ deve conter duas linhas independentes, com `_VERSAO_REGISTRO` iguais a 1 e 2 respectivamente. O registro 1 deve ter `status_extracao = "SUBSTITUIDO"`.
   - **Critério de Falha**: Apenas 1 linha no arquivo, com o valor mais recente (sobrescrita).

2. **Teste de Versionamento MtM/Receita (C0.4, C0.5)**
   - **Comando**: No `main.py`, comente as execuções de pipeline, exceto o `Pipeline de Risco de Crédito`, e execute `python main.py`.
   - **Critério de Sucesso**: O pipeline deve rodar sem logs de exceção ou stack trace.
   - **Critério de Falha**: Ocorrer `FileNotFoundError` ou `KeyError` lendo `mtm_agregado_contraparte.parquet`.

3. **Teste do Motor de Risco Real (C1.1, C0.6)**
   - **Comando**: Inspecione o csv: `SAIDAS/relational/facts/fato_exposicao_risco_RUN_*.csv`.
   - **Critério de Sucesso**: O campo `PD_UTILIZADA` e `SEGMENTO` possuem variabilidade genuína baseada nas fichas e `CONFIG_SNAPSHOT_EAD` não está vazio.
   - **Critério de Falha**: `PD_UTILIZADA` continua cravado em "0.05" e segmento em "CGRUPO" em massa.

4. **Teste das Tabelas de Auditoria (C4.1, C4.2, C4.3)**
   - **Comando**: Localize os arquivos em `SAIDAS/relational/control/` (`ctl_run_pipeline.parquet`, `ctl_documento.parquet` e `ctl_campo_origem.parquet`).
   - **Critério de Sucesso**: Os arquivos têm mais de 0KB. O `ctl_campo_origem` mapeia claramente a aba (ex: "Plan1") e célula (ex: "B25") para o seu campo extraído correspondente.
   - **Critério de Falha**: Arquivos ausentes ou coordenadas vazias.

---

## 8. COMO A PRÓXIMA SESSÃO DEVE COMEÇAR

Você, a IA ou o analista que iniciar os próximos passos, **deve executar o seguinte fluxo**:

1. Leia este documento até aqui para contextualização (ok, concluído).
2. Se estiver em ambiente com dados, **execute rigorosamente a checklist da seção 7**.
3. Reporte no chat, textualmente, os resultados da checklist. Atualize as seções 3 e 4 deste documento com base na prova empírica (alterando de "Pendente" ou "Estimativa" para "Confirmado por Execução" se passar).
4. Se houver quebras nos testes da Seção 7, seu primeiro trabalho é corrigir as regressões da Fase 3.
5. Se tudo passar com sucesso, somente então abra o `implementation_plan.md` e retome o desenvolvimento a partir do **Bloco 2 (C2.1)**.
6. **Mantenha a regra de ouro:** nenhuma correção pode ser dada como concluída sem apresentar o estado final do código e, idealmente, execução verificada.
