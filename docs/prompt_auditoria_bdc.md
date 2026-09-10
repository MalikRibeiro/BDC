# PROMPT — Auditoria Técnica e Funcional do Projeto BD Crédito

> Cole este prompt no Antigravity (Gemini 3.1 Pro High). Ele está dividido em
> FASES. Rode a FASE 0 e a FASE 1 primeiro e revise o relatório antes de
> autorizar qualquer coisa além de leitura. As fases 2 a 5 também são
> read-only. Não existe fase de correção automática neste prompt — correções
> são um prompt separado, feito depois que você aprovar os achados.

---

## PAPEL

Você é um Engenheiro de Dados Sênior fazendo uma auditoria de terceira parte
independente no projeto **BD Crédito**. Você não escreveu este código e não
tem interesse em parecer que o projeto está mais pronto do que está. Seu
único objetivo é produzir um relatório verdadeiro, verificável e específico.

## REGRAS INEGOCIÁVEIS (leia antes de começar)

1. **MODO SOMENTE LEITURA.** Você não deve criar, editar, renomear, mover ou
   apagar nenhum arquivo, nem executar `reset.py` ou qualquer script que
   altere Staging/Bronze/Silver/Relational/Gold. Se precisar rodar algo para
   inspecionar (ex.: `pandas.read_parquet` num script temporário só seu, fora
   da pasta do projeto), diga explicitamente que fez isso e onde.
2. **NADA DE HARDCODE NA SUA ANÁLISE.** Ao verificar regras, schemas,
   domínios ou nomes de campo, leia do catálogo/config real do projeto
   (`master_catalog`, `mapping_fichas_*.json`, `cfg_*`), nunca do que está
   descrito de memória no documento de planejamento. O documento é a
   especificação; o catálogo/JSON é a implementação. Aponte toda divergência
   entre os dois.
3. **TODA AFIRMAÇÃO PRECISA DE EVIDÊNCIA.** Nada de "está implementado" ou
   "está ok" sem citar arquivo + linha (ou célula/coluna, no caso de
   planilha) que comprove. Se não conseguir confirmar algo, escreva
   explicitamente "não verificado" ou "não encontrado" — nunca assuma
   sucesso por ausência de erro.
4. **NÃO INFLE O PERCENTUAL DE CONCLUSÃO.** Já tive relatórios anteriores
   (de outra IA) que classificaram o pipeline como "pronto para a próxima
   fase" e estavam errados. Se um módulo existe mas está com dado mockado,
   parcial ou com nulos suspeitos, classifique como "parcial" ou "não
   confiável", não como "concluído".
5. **SEPARE FATO DE HIPÓTESE.** Quando não tiver certeza da causa-raiz de um
   problema, apresente a hipótese como hipótese e liste o que falta
   verificar para confirmá-la — não apresente como diagnóstico fechado.
6. Se, durante a leitura, você perceber que teria que editar algo para
   "testar direito", **pare e me pergunte antes** em vez de editar.

## CONTEXTO DO PROJETO (resumo — valide contra a realidade, não confie cegamente)

- Projeto: **BD Crédito (BDC)** — sistema para consolidar dados de crédito de
  contrapartes (comercializadoras e consumidores) da Copel a partir de ~2.000
  fichas em Excel, hoje espalhadas em pastas de rede historicamente
  desorganizadas.
- Documento de referência normativo: **"BD Crédito — Planejamento Funcional
  e de Auditoria", versão 1.2, datado de 21/07/2026** (anexo/fornecido
  separadamente). Esse documento é a fonte da verdade sobre o que o sistema
  *deveria* fazer — arquitetura em camadas (Staging → Bronze → Silver →
  Relational → Gold → Output), modelo relacional (dimensões/fatos/config),
  regras de negócio (segmentação por volume ≥/< 5 MWm, EAD/LGD/PE/taxa de
  risco), regras de carga manual controlada (seção 4.5, 6.5.1, 11.7.1) e
  catálogo de alertas (Apêndice B).
- Repositório: https://github.com/MalikRibeiro/BDC (acesse se tiver
  ferramenta de leitura de repositório; senão, trabalhe sobre os arquivos
  locais do workspace atual do Antigravity, que devem ser os mesmos).
- Stack: Python, pandas/pyarrow, Streamlit (dashboards), openpyxl,
  arquitetura modular em `src/domain/*` (fichas, contrapartes, credito,
  salesforce, mtm, cadastro, carga_manual, auditoria), `src/silver`,
  `src/relational`, `src/gold`, `src/services`.
- Estado conhecido pelo dono do projeto (para você confirmar ou refutar, não
  para aceitar como verdade): pipeline roda ponta a ponta localmente;
  Comercializadoras e Consumidores já têm extração Silver rodando; há
  múltiplas versões de layout mapeadas por tipo de ficha; existe suspeita de
  campos com mapeamento de célula incompleto em versões antigas de layout;
  nem todos os ~11+ códigos de alerta do Apêndice B chegam de fato à camada
  relacional; a carga manual controlada (dupla temporalidade, evidência,
  alçada) é uma frente ainda em desenvolvimento.

---

## FASE 0 — Inventário real (não pule esta etapa)

Antes de comparar qualquer coisa com o planejamento, mapeie o que **de fato
existe** no repositório agora:

1. Liste a árvore de diretórios de `src/` até 3 níveis, e a árvore de
   `SAIDAS/` (ou `ENTRADAS/SAIDAS/LOGS` conforme a estrutura real) até 2
   níveis.
2. Liste todos os arquivos de configuração/catálogo JSON usados pelo motor
   (`master_catalog`, `mapping_fichas_comercializadoras.json`,
   `mapping_fichas_consumidores.json`, `cfg_*`), com o número de campos/
   versões de layout mapeados em cada um.
3. Identifique qual script orquestra o pipeline hoje (`main.py` ou
   equivalente) e liste **exatamente** quais etapas ele chama, na ordem —
   não presuma que todas as etapas descritas no planejamento estão
   orquestradas.
4. Rode (ou leia o resultado mais recente de) qualquer contagem de arquivos
   processados/rejeitados por tipo de ficha (comercializadoras/consumidores)
   que já exista em log/CSV, e reporte os números crus, com data do
   arquivo/log de onde tirou o número.

Produza uma tabela: **Módulo do planejamento (Seção X)** → **Existe no
código? (sim/parcial/não)** → **Arquivo(s) evidência** → **Observação**.

---

## FASE 1 — Estrutura do projeto vs Planejamento v1.2

Usando a tabela da Fase 0, aprofunde item a item das seções abaixo do
documento de planejamento, e para cada uma diga se está implementada,
parcialmente implementada (e o que falta) ou ausente:

- Seção 2 (módulos funcionais) — confirme se cada módulo listado
  (Gestão documental, Cadastro de contrapartes, Análises de crédito,
  Rating e PD, Exposição e perda esperada, Garantias, Relatórios e alertas,
  Interface de limites, Auditoria e controle, Atualizações manuais) tem um
  correspondente real em `src/domain/*` ou em algum serviço, e não apenas
  um nome de pasta vazio.
- Seção 4.2 (estados do documento: DESCOBERTO → ... → PUBLICADO/PENDENTE/
  REJEITADO) — confirme se esses estados são de fato usados como valores
  de campo em algum log/tabela de controle, e não apenas conceituais.
- Seção 8 (modelo relacional — dimensões e fatos) — para cada
  `dim_*`/`fato_*` listado no documento (8.1 e 8.2), diga se existe um
  arquivo/tabela real com esse nome ou equivalente, quantas linhas tem
  atualmente, e se o grão bate com o descrito no documento.
- Seção 9 (camadas: Staging/Bronze/Silver/Relational/Gold/Output) —
  confirme se a separação física de pastas existe e se **nenhuma regra de
  negócio/cálculo de risco está vazando para a camada Silver** (isso é uma
  regra arquitetural crítica do projeto: cálculos de PD/rating/LGD/EAD só
  podem existir na camada Relacional, nunca na Silver). Cite qualquer
  violação encontrada com arquivo e linha.
- Seção 10 (arquitetura modular do código) — compare a árvore real de
  `src/` com a estrutura de pacotes proposta na seção 10 e liste divergências.

---

## FASE 2 — Validação Bronze → Silver (Comercializadoras e Consumidores)

Este é o foco principal desta rodada de auditoria.

Para **Comercializadoras** (seção 3.1 do planejamento) e para **Consumidores** (seção 3.2, incluindo a distinção ≥5 MWm com DF vs <5 MWm com bureau):

1. Pegue a lista de "campos mínimos" descrita no planejamento para cada bloco (dados gerais, análise quantitativa, análise qualitativa, indicadores financeiros, demonstrações financeiras — e para consumidores, também cadastro comum, classificação documental e rastreabilidade do enquadramento).
2. Para cada campo, verifique no catálogo/mapping real se ele: 
- existe mapeado para **todas** as versões de layout atualmente suportadas, ou só para algumas (liste quais faltam);
- tem `allow_semantic` coerente com o tipo de campo (não aceite a resposta "está mapeado" sem checar isso);
- aparece de fato na saída Silver (arquivo/parquet/csv real), com um comando de verificação (ex.: `% de nulos por campo`, agrupado por `versao_ficha`/layout).
3. Rode (ou peça para eu rodar e colar o output, se você estiver bloqueado de terminal) uma checagem de nulos por campo × versão de layout, igual ao padrão já usado no projeto (cluster de nulos concentrados numa versão específica = mapeamento incompleto daquele layout; nulo espalhado e baixo percentual = provavelmente dado esparso legítimo na fonte). Reporte os dois tipos separadamente — não misture.
4. Verifique especificamente os campos historicamente problemáticos deste projeto, se ainda existirem no catálogo: `CONTROLADOR`, `TIPO_COMERCIALIZADORA`, `DATA_RATING_AGENCIA`, e qualquer campo do bloco FCO/ROA/ROE/LUCRO_LIQUIDO/FLUXO_DE_CAIXA/NOTA_BOARD/NOTA_BUREAU — confirme se os mapeamentos de célula aplicados anteriormente continuam presentes e não foram sobrescritos.
5. Compare o valor bruto de uma amostra pequena (mínimo 3 arquivos por versão de layout ativa) entre o arquivo original em `Bronze` e o registro correspondente na `Silver`, célula a célula para os campos críticos (CNPJ, data da análise, PD, rating, indicadores financeiros usados em EAD/LGD/PE). Não aceite "os totais batem" como prova — mostre a comparação campo a campo.
6. Verifique explicitamente a regra "ausência de DF nunca vira zero" (seção 4.5, "Regra para ausência de demonstrações financeiras" e critério de bloqueio da seção 14.8): procure por qualquer valor `0` em campo financeiro que deveria estar nulo com `situacao_df` = `NAO_RECEBIDA` ou `NAO_APLICAVEL`. Isso é um dos critérios de bloqueio mais importantes do documento — trate qualquer violação como achado crítico.

Entregue uma tabela por segmento (Comercializadoras / Consumidores ≥5MWm /
Consumidores <5MWm):

| Campo | Coberto em quais versões de layout | % nulo (cluster vs esparso) | Bronze↔Silver bate na amostra? | Severidade do gap |

---

## FASE 3 — Coerência dos alertas de negócio

O objetivo aqui é responder: **os alertas que o sistema gera hoje são
confiáveis o suficiente para eu decidir, com base neles, o que precisa de
carga manual?**

1. Liste todos os códigos de alerta do Apêndice B do planejamento (ANA_001,
   ANA_002, CAD_001, CAD_002, RAT_001, PD_001, EXP_001, GAR_001, GAR_002,
   QLT_001, QLT_002, DOC_001, CTR_001, CTR_002, VOL_001, VOL_002, SEG_001,
   SEG_002, SEG_003, GRP_001, DF_001, MAN_001, MAN_002, MAN_003, MAN_004,
   EXC_001).
2. Para cada um, diga: implementado / não implementado / implementado com
   nome diferente do documento (se achar drift de nomenclatura tipo o
   `SF_001` encontrado anteriormente, reporte).
3. Para os alertas implementados, verifique se eles de fato chegam até
   `fato_alerta_credito` (camada relacional/Gold) ou se ficam presos em
   log/memória/Silver sem virar um registro consultável. Um alerta que só
   existe em log não serve para o analista decidir carga manual — trate
   isso como gap funcional, não como "implementado".
4. Pegue uma amostra de 10 a 15 alertas realmente disparados na última
   execução (de qualquer tipo) e valide manualmente contra os dados
   fonte se o alerta está **correto** (não é falso positivo) e se a
   **mensagem/campo afetado é específico o suficiente** para eu saber o
   que corrigir sem precisar investigar do zero. Reporte quantos dos
   validados são falsos positivos.
5. Verifique especialmente os alertas ligados a dados que exigem ação
   manual: `DF_001` (DF não recebida em segmento que exige análise
   detalhada), `MAN_001`/`MAN_002`/`MAN_003` (carga manual pendente/sem
   evidência/campo não permitido) e `EXC_001` (exceção sem DF vencida).
   Esses são os que orientam diretamente o meu trabalho de carga manual —
   se estiverem incompletos ou incorretos, marque como prioridade alta.

---

## FASE 4 — Carga manual controlada

Valide a implementação da carga manual controlada contra as seções 4.5,
6.5.1 e 11.7.1 do planejamento:

1. Confirme se existe um mecanismo real (não só conceitual) para os 5 tipos
   de evento manual (`COMPLEMENTACAO`, `CORRECAO`, `ATUALIZACAO_HISTORICA`,
   `REGISTRO_SEM_DF`, `OVERRIDE`), e se cada um segue o tratamento correto
   descrito na tabela da seção 4.5.
2. Confirme a **dupla temporalidade** (`data_referencia_negocio` separada
   de `data_registro_sistema`) está de fato persistida em algum lugar, e
   não é só um campo previsto no schema mas nunca preenchido.
3. Confirme que a carga manual **nunca sobrescreve fisicamente** um
   registro já publicado — verifique se toda alteração gera nova versão/
   evento (procure por qualquer `UPDATE`/sobrescrita in-place em vez de
   append/nova linha).
4. Confirme a segregação de alçada (quem insere ≠ quem aprova, quando a
   política exigir) e se existe status `PENDENTE/APROVADO/REJEITADO/
   REVOGADO/EXPIRADO` sendo de fato respeitado antes de um dado manual virar
   parte da "visão oficial" (regra de bloqueio da seção 14.8: "Atualização
   manual pendente, rejeitada ou sem evidência não poderá compor a visão
   oficial").
5. Confirme que a regra de ausência de DF nunca vira zero (repetido
   deliberadamente aqui, porque cruza Silver + carga manual) está sendo
   respeitada também no fluxo manual, e que qualquer override que sustente
   rating/PD/validade sem DF tem `validade_excecao` (prazo de expiração) e
   gera o alerta `EXC_001` quando vencer.

Se qualquer um dos 5 pontos acima não existir de fato, diga isso
claramente — "carga manual controlada" sem essas garantias é apenas edição
de planilha com passos extras, e é importante eu saber se é esse o caso
hoje.

---

## FASE 5 — Tela `visao_carteira.py` (fora do planejamento formal, mas real)

Esta tela **não está descrita no documento de planejamento** — foi
construída à parte para dar visibilidade da carteira. Regra: **não alterar
nenhuma regra de negócio existente no código anexo** (mapeamento de
`STATUS_CONTRATUAL`, cálculo de `Tipo de analise` a partir de
`METODOLOGIA_EXIGIDA`, formatação de PD, etc.) — o objetivo desta fase é
validar e sugerir, não reescrever a regra.

1. Confirme que todo campo exibido na tela (`Contraparte`, `CNPJ`,
   `Quantidade de contratos`, `Numero do contrato`, `Rating`,
   `Probabilidade de default`, `Score`, `Restritivos`, `Data da Analise`,
   `Tipo de analise`, `Status_Fornecimento`, `Vigencia_Inicio`,
   `Vigencia_Fim`) tem, de fato, origem na camada **Gold** (arquivo
   `Visao_Operacional_BDC_LATEST`) e não está lendo Silver/Bronze
   diretamente — isso violaria a regra "Power BI/dashboards devem consumir
   preferencialmente a camada relacional/Gold, não arquivos-fonte" (seção
   7.4).
2. Verifique se as colunas que a tela espera (`STATUS_CONTRATUAL`,
   `RATING_FINAL`, `PD_FINAL`, `SCORE_BUREAU`, `RESTRITIVOS`,
   `DATA_DA_ANALISE`, `METODOLOGIA_EXIGIDA`, `QUANTIDADE_CONTRATOS`,
   `NUMERACAO_CONTRATOS`, `ANO_INICIO_CONTRATO`, `PROXIMO_INICIO`,
   `PROXIMO_FIM`) realmente existem com esse nome exato no builder da Gold
   (`servico_gold.py` ou equivalente) — se algum nome mudou, a tela vai
   falhar silenciosamente (ex.: `row.get()` retornando `None` sem erro) e
   isso é um risco real de "carteira aparentemente vazia sem alerta".
3. Aponte qualquer lugar onde a tela está **mascarando dado ausente como
   string vazia/"nan" em vez de deixar nulo** de forma que o usuário não
   perceba que falta rating/PD/score — isso vai contra o princípio geral do
   projeto de "ausência de dado = nulo verdadeiro, nunca zero/vazio
   disfarçado" (seção 5.1). Sugestão, sem mudar a regra de negócio: indicar
   visualmente (ex. badge "Sem análise") em vez de célula em branco
   indistinguível de erro.
4. Verifique performance/robustez básica sem mudar lógica: tratamento de
   erro ao ler arquivo Gold ausente (já existe), tratamento de tipo em
   `int(row.get("QUANTIDADE_CONTRATOS", 0))` quando o valor vier como
   string ou NaN, e se o filtro por `STATUS_CONTRATUAL` está de fato restrito
   aos dois valores esperados ou se está descartando silenciosamente
   outros status válidos (ex.: contratos encerrados que talvez devessem
   aparecer em outra aba).
5. Liste, sem implementar, sugestões de melhoria de UX/dados que sejam
   estritamente aditivas (não mudam nenhuma regra de cálculo já existente):
   por exemplo, exibir `origem_analise`/`situacao_df` como coluna auxiliar
   para o usuário já ver direto na tela por que um `Tipo de analise` está
   como "Sem Análise", ou exportação para Excel da visão filtrada.

---

## FORMATO DE ENTREGA

Entregue um único relatório Markdown com esta estrutura:

1. **Resumo executivo** (máx. 15 linhas, sem eufemismo — se algo está
   quebrado, diga que está quebrado).
2. **Fase 0 — Inventário real** (tabela).
3. **Fase 1 — Estrutura vs Planejamento** (tabela por seção).
4. **Fase 2 — Bronze→Silver** (tabelas por segmento + lista de achados
   críticos).
5. **Fase 3 — Alertas** (tabela de cobertura + taxa de falso positivo da
   amostra).
6. **Fase 4 — Carga manual** (checklist dos 5 pontos, cada um com
   evidência).
7. **Fase 5 — visao_carteira.py** (checklist + lista de sugestões
   aditivas, claramente separada de "achados de bug").
8. **Lista final priorizada de gaps**, ordenada por severidade
   (Crítico / Alto / Médio / Baixo), cada item com: descrição, evidência
   (arquivo:linha), e o que precisaria ser verificado/feito a seguir —
   **sem implementar nada ainda**.

Não gere código de correção nesta rodada. Ao final do relatório, pergunte
se deve prosseguir para um prompt de implementação separado, com escopo
travado item a item da lista priorizada.
