---
title: "Nota Técnica - Probabilidade de Default (PD) e Taxa de Risco de Crédito (TRC)"
version: "v7"
date: "2026-09-10"
language: "pt-BR"
horizon_months: 12
document_type: "nota-tecnica"
keywords:
  - probabilidade de default
  - PD
  - taxa de risco de credito
  - TRC
  - mercado livre de energia
  - ACL
---

# Metodologia de estimativa da Probabilidade de Default (PD) e apuração da Taxa de Risco de Crédito (TRC) no Mercado Livre de Energia (ACL)

**Horizonte de risco:** 12 meses  
**Versão:** revisada v7  
**Data:** 10/09/2026

| **Finalidade** | **Consolidar a metodologia de PD por tipo de contraparte e sua aplicação na Taxa de Risco de Crédito.** |
|----|----|
| **Públicos** | Comercializadoras Puras; Comercializadoras de Grupo; Consumidores até 5 MWm; Consumidores acima de 5 MWm. |
| **Referências normativas** | NCE 4.03 – Limites Operacionais e Garantias Financeiras; NCE 4.04 – Análise de Crédito e Garantias Financeiras para Consumidores. |
| **Escopo de garantias** | A Nota não define modalidade, elegibilidade ou estrutura de garantias; eventual mitigação é recebida como parâmetro de entrada para LGD. |

## 1 Objetivo e princípios da metodologia

Esta Nota Técnica consolida a metodologia aplicada para estimar e atribuir a Probabilidade de Default (PD) anual das contrapartes do Mercado Livre de Energia (ACL) e para transformar essa informação em Taxa de Risco de Crédito (TRC). A metodologia busca combinar aderência às Normas de Comercialização de Energia, comparabilidade entre públicos, rastreabilidade das decisões e coerência entre risco quantitativo, classificação de rating e decisão de crédito.

A arquitetura preserva a fonte de risco própria de cada segmento. A PD não é forçada a nascer de um único modelo: para Comercializadoras Puras e Consumidores acima de 5 MWm pode haver PD contábil; para Consumidores até 5 MWm a fonte é a Risk 3; e para Comercializadoras de Grupo a PD é aquela associada ao rating público na NCE 4.03, enquanto as informações que sustentam o enquadramento estiverem válidas.

| Princípio de coerência: nos segmentos em que existe Rating_final interno, o componente qualitativo não é somado diretamente à fórmula estatística de PD. Ele atua sobre o Rating_final. Se a avaliação qualitativa melhora ou piora o rating, a PD_final deve ser reposicionada para a faixa compatível com o novo rating. Para consumidores até 5 MWm, não há Rating Copel: a PD utilizada é diretamente a PD_Risk3. Eventos de política que impedem operação, como Recuperação Judicial, prevalecem sobre essas regras. |
|----|

## 2 Escopo, fontes de dados e validade

| **Público** | **Fonte principal da PD** | **Validade relevante** | **Tratamento central** |
|----|----|----|----|
| Comercializadoras Puras (CPURA) | Modelo contábil + score quantitativo/qualitativo | DF: 18 meses; bureau: 120 dias | PD_base contábil; Rating_final pelo score; interpolação intrafaixa; PD_sub conforme item 6.4. |
| Comercializadoras de Grupo (CGRUPO) | Rating público nacional e tabela de PD da NCE 4.03 | DF e rating público: 18 meses | PD da NCE enquanto válida; PD substituta quando DF/rating perde validade. |
| Consumidores até 5 MWm | Risk 3: score + fator de alerta | Bureau: 365 dias | PD_Risk3 utilizada diretamente; não há Rating Copel nem reenquadramento em faixa interna. |
| Consumidores acima de 5 MWm | Modelo contábil + análise quantitativa/qualitativa | DF: 18 meses; bureau: 365 dias | PD_base + Rating_final; interpolação t-Student; PD_sub conforme item 9.4. |

Os prazos acima reproduzem as regras atualmente previstas nas NCEs 4.03 e 4.04. Informação vencida não sustenta nova decisão de crédito. As regras específicas de validade e PD_sub constam dos itens 6.4, 7.2, 8.2 e 9.4.

## 3 Definições e hierarquia de aplicação

| **Termo** | **Definição** |
|----|----|
| **PD_base** | Probabilidade proveniente do modelo quantitativo antes da transformação final. Para consumidores até 5 MWm, utiliza-se a denominação específica PD_Risk3. |
| **Rating_final** | Classificação interna de risco utilizada na decisão de crédito, após aplicação dos componentes quantitativos, qualitativos e regras da política, quando aplicável. Não existe Rating Copel para consumidores até 5 MWm. |
| **PD_final** | Probabilidade efetivamente utilizada na mensuração de risco: coerente com o Rating_final nos segmentos com rating interno; igual à PD_Risk3 para consumidores até 5 MWm; e igual à PD da NCE para CGRUPO enquanto válida. |
| **PD_sub** | PD substituta utilizada quando a fonte primária que sustentava a PD deixa de ser válida, segundo a regra específica de cada segmento (CPURA, CGRUPO e consumidores acima de 5 MWm). |
| **EAD** | Exposição no momento do default, mensurada no horizonte de 12 meses. |
| **LGD** | Severidade de perda após mitigadores reconhecidos, calculada como a parcela não coberta da EAD. A metodologia de aceitação e qualidade da garantia não é definida nesta Nota. |
| **EL** | Perda esperada: EAD × PD_final × LGD. |
| **TRC** | Taxa de Risco de Crédito: perda esperada em proporção ao notional de referência. |

## 4 Modelo contábil de PD_base

Quando o segmento exige análise contábil, a PD_base é obtida por regressão logística com os indicadores econômico-financeiros previstos na metodologia de Assaf Neto (2008) utilizada nas NCEs. Primeiro calcula-se o escore linear z:

z = -4,03 - 3,70·X₁₂ + 11,66·X₁₆ - 7,86·X₁₉ - 11,33·X₂₂

| **Variável** | **Definição**     | **Interpretação econômica**       |
|--------------|-------------------|-----------------------------------|
| X₁₂          | (LA + RL) / AT    | Lucros retidos sobre o ativo.     |
| X₁₆          | (PCF + PNCF) / AT | Endividamento financeiro.         |
| X₁₉          | (AC - PC) / AT    | Capital de giro líquido.          |
| X₂₂          | (ACF - PCF) / VL  | Saldo de tesouraria sobre vendas. |

A probabilidade é a transformação logística do escore linear:

PD_base = 1 / (1 + exp(-z))

De forma equivalente, o logit da probabilidade satisfaz z = ln[PD_base/(1-PD_base)]. Essa distinção é importante para a implementação: z é o escore do modelo e PD_base é a probabilidade anual resultante.

## 5 Regra geral de coerência entre rating e PD

Nos segmentos em que o rating decorre de combinação quantitativa e qualitativa (CPURA e consumidores acima de 5 MWm), a PD_base representa o sinal quantitativo de insolvência, mas a PD_final deve refletir a classificação efetivamente atribuída pela política. Assim, a análise qualitativa atua como overlay de crédito: ela pode alterar o Rating_final e, consequentemente, o intervalo no qual a PD_final deve permanecer.

PD_min(Rating_final) ≤ PD_final ≤ PD_max(Rating_final)

A transformação da PD dentro da faixa não é discricionária. Para CPURA, utiliza-se a interpolação linear decrescente em função do Score_total, conforme o item 6.3. Para consumidores acima de 5 MWm, utiliza-se a transformação t-Student e interpolação intrafaixa descritas no item 9.2. Consumidores até 5 MWm não passam por esse processo, pois a PD_Risk3 é utilizada diretamente.

| Melhora qualitativa de rating implica redução da PD percebida para a faixa do novo rating; piora qualitativa implica aumento da PD percebida para a faixa correspondente. A exceção são eventos impeditivos da política, nos quais não há possibilidade de compensação qualitativa. |
|----|

## 6 Comercializadoras Puras (CPURA)

### 6.1 Formação do score

Para CPURA, o Rating_final deriva de score em escala de 0 a 10. Cada indicador é classificado em A, B, C, D ou E e convertido na escala numérica A=10, B=8, C=6, D=3 e E=0.

O bloco quantitativo, que representa 70% do score total, é:

Score_quant = 0,46·S_PD + 0,34·S_FCO/ROL + 0,10·S_ROE + 0,10·S_ROA

O bloco qualitativo, que representa 30% do score total, é composto por Board, Auditoria e Bureau:

Score_qual = (2/3)·S_Board + (1/6)·S_Auditoria + (1/6)·S_Bureau

Score_total = 0,70·Score_quant + 0,30·Score_qual

### 6.2 Réguas dos indicadores quantitativos

| **Indicador** | **A** | **B** | **C** | **D** | **E** |
|----|----|----|----|----|----|
| **PD_base** | ≤ 0,50% | >0,50% a 1,00% | >1,00% a 3,00% | >3,00% a 10,00% | >10,00% |
| **FCO/ROL** | >17,84% | 6,76% a 17,84% | 0% a 6,76% | -4,12% a 0% | ≤ -4,12% |
| **ROA** | >20,81% | 11,72% a 20,81% | 0% a 11,72% | -5,95% a 0% | ≤ -5,95% |
| **ROE** | >25,05% | 14,10% a 25,05% | 0% a 14,10% | -6,38% a 0% | ≤ -6,38% |

Se a PD_base da comercializadora pura for superior a 10%, aplica-se o enquadramento automático em Rating E, em linha com a NCE 4.03.

### 6.3 Score_total, Rating_final e determinação da PD_final

O Rating_final é determinado pelo Score_total, respeitados os gatilhos mandatórios previstos na NCE 4.03. Para o Rating A, a PD_final é fixada em 0,50%. Para os Ratings B, C, D e E, a PD_final não corresponde simplesmente ao limite da classe e não é escolhida discricionariamente: a metodologia utiliza interpolação linear obrigatória em função do Score_total, preservando granularidade intraclasse.

| **Rating** | **Faixa de Score_total** | **Parâmetros operacionais de PD_final** |
|----|----|----|
| A | 8,00 a 10,00 | 0,50% (fixa) |
| B | 7,00 a <8,00 | 0,51% a 0,76% |
| C | 6,00 a <7,00 | 0,76% a 4,17% |
| D | 5,00 a <6,00 | 4,17% a 10,00% |
| E | 0,00 a <5,00 | 10,00% a 100,00% |

Para cada rating r, definem-se S_min(r) e S_max(r) como os limites inferior e superior do score da classe e PD_min(r) e PD_max(r) como os limites inferior e superior de probabilidade utilizados na fórmula operacional. O Score_total é inicialmente limitado aos extremos da classe:

Score_cap = min{S_max(r), max[S_min(r), Score_total]}

Em seguida, determina-se a posição relativa da contraparte dentro da faixa. A orientação é decrescente: quanto maior o Score_total dentro da classe, menor a PD atribuída.

u = [S_max(r) - Score_cap] / [S_max(r) - S_min(r)]

PD_bruta = PD_min(r) + u·[PD_max(r) - PD_min(r)]

De forma equivalente, a planilha operacional calcula PD_bruta = PD_max(r) - [PD_max(r) - PD_min(r)]·[Score_cap - S_min(r)]/[S_max(r) - S_min(r)]. As duas expressões são algebricamente equivalentes e produzem a mesma ordenação intraclasse.

Após a interpolação, aplica-se exclusivamente um tratamento de estabilidade numérica. Se 0 < PD_bruta < 1, define-se ε = 10⁻¹², limita-se p = max{ε, min[1-ε, PD_bruta]} e calcula-se o logit z = ln[p/(1-p)]. O valor z é limitado ao intervalo [-13, 13] e retorna-se à escala de probabilidade pela transformação logística. Se PD_bruta ≤ 0, utiliza-se 0; se PD_bruta ≥ 1, utiliza-se 1.

z_cap = max{-13, min[13, ln(p/(1-p))]}

PD_final = 1 / [1 + exp(-z_cap)]

Esse tratamento não cria liberdade de escolha para o analista: a granularização da PD é parte integrante da metodologia e deve reproduzir os parâmetros versionados da planilha Com Puras.xlsx. Assim, o Rating_final define a faixa admissível e o Score_total determina objetivamente a posição da contraparte dentro dessa faixa.

### 6.4 Validade das informações e PD substituta

As demonstrações financeiras utilizadas na avaliação das Comercializadoras Puras possuem validade de 18 meses, enquanto a consulta de bureau possui validade de 120 dias, conforme a NCE 4.03. Enquanto as demonstrações financeiras permanecerem válidas, aplica-se a metodologia ordinária descrita nos itens 6.1 a 6.3.

Caso as demonstrações financeiras ultrapassem o prazo de 18 meses sem disponibilização de novas informações contábeis válidas, a PD_base proveniente do modelo contábil deixa de ser considerada vigente. Até a realização de nova análise com demonstrações financeiras atualizadas, utiliza-se como PD substituta a PD_Risk3 vigente, sujeita ao piso conservador de 10%:

PD_sub,CPURA = max(PD_Risk3, 10,00%)

O piso de 10% corresponde ao limiar de entrada da classe E na régua quantitativa de PD das Comercializadoras Puras. A regra impede que a perda de validade da informação contábil produza uma melhora artificial da percepção de risco. Se a PD_Risk3 vigente for superior a 10%, prevalece o maior valor.

A utilização da PD_Risk3 como fonte substituta pressupõe consulta vigente. Na ausência de PD_Risk3 válida, deverá ser realizada nova consulta antes de nova decisão de crédito; informação vencida não deve ser tratada como evidência corrente.

O vencimento isolado da consulta de bureau não substitui automaticamente uma PD contábil ainda válida. Nessa situação, a consulta qualitativa deve ser atualizada antes de nova análise ou revisão do Rating_final, observando-se a validade de 120 dias prevista na NCE 4.03.

Uma vez restabelecidas demonstrações financeiras válidas, a contraparte retorna à metodologia ordinária dos itens 6.1 a 6.3, não havendo restauração automática de PD anterior sem novo cálculo.

## 7 Comercializadoras de Grupo (CGRUPO)

Para Comercializadoras de Grupo não se cria uma régua paralela de PD. Enquanto a demonstração financeira e o rating público nacional aplicável estiverem válidos, a PD_final é exatamente a probabilidade associada ao rating público no Anexo 1 da NCE 4.03.

PD_final = PD_NCE 4.03(Rating público válido)

### 7.1 Tabela de equivalência e PD

| **Rating Copel** | **Fitch / S&P** | **Moody's** | **PD anual** |
|------------------|-----------------|-------------|--------------|
| A                | AAA             | Aaa         | 0,05%        |
| A                | AA+             | Aa1         | 0,08%        |
| A                | AA              | Aa2         | 0,10%        |
| A                | AA-             | Aa3         | 0,14%        |
| A                | A+              | A1          | 0,19%        |
| A                | A               | A2          | 0,25%        |
| A                | A-              | A3          | 0,38%        |
| B                | BBB+            | Baa1        | 0,58%        |
| B                | BBB             | Baa2        | 0,80%        |
| B                | BBB-            | Baa3        | 1,41%        |
| C                | BB+             | Ba1         | 1,99%        |
| C                | BB              | Ba2         | 2,50%        |
| C                | BB-             | Ba3         | 3,88%        |
| D                | B+              | B1          | 5,02%        |
| D                | B               | B2          | 6,00%        |
| D                | B-              | B3          | 9,49%        |
| E                | CCC+            | Caa1        | 15,00%       |
| E                | CCC             | Caa2        | 18,00%       |
| E                | CCC-/CC-        | Caa3        | 22,00%       |
| E                | CC              | Ca          | 30,00%       |
| E                | C               | —           | 45,00%       |
| E                | DDD/D           | C           | 100,00%      |

### 7.2 Validade e PD substituta

A NCE 4.03 estabelece validade de 18 meses tanto para as demonstrações financeiras quanto para a informação de rating público nacional das Comercializadoras de Grupo. A PD da tabela acima somente é tratada como vigente enquanto essas duas condições estiverem atendidas.

Se a demonstração financeira ultrapassar 18 meses, ou se o rating público ultrapassar 18 meses, for retirado, suspenso ou deixar de ser válido, a PD associada ao rating anterior deixa de ser utilizada como PD corrente. Até a atualização das informações, aplica-se uma PD substituta conservadora equivalente, no mínimo, ao primeiro nível da classe E da NCE 4.03:

PD_sub,CGRUPO = max(PD_última_válida, 15,00%)

Na ausência de PD válida anterior, adota-se 15,00%. A regra evita que o simples vencimento da informação produza melhora artificial de risco: se a última PD válida já era superior a 15%, permanece o maior valor. Uma vez restabelecidas DF e rating público válidos, a PD volta a ser aquela correspondente ao rating vigente na NCE 4.03.

## 8 Consumidores até 5 MWm

### 8.1 PD de origem Risk 3

Para consumidores com demanda agregada até 5 MWm, a Probabilidade de Default utilizada na metodologia é proveniente diretamente da Risk 3 e depende do Score e do Fator de Alerta. Não há Rating Copel para esse segmento e, portanto, não existe etapa de transposição, reenquadramento ou calibração da PD em faixas internas de rating.

PD_Risk3 = min{1,9·exp[-0,5·(0,11·Score - Alerta/3 + 1)], 0,9999}

PD_final = PD_Risk3

O eventual rating disponibilizado pela Risk 3 é mantido exclusivamente como informação de origem e evidência da consulta, sem conversão para Rating Copel e sem interferência adicional sobre a PD utilizada na mensuração de risco.

### 8.2 Validade da consulta

A consulta de bureau para consumidores possui validade de 365 dias, conforme a NCE 4.04. Durante esse período, utiliza-se diretamente a PD_Risk3 vigente. Após o vencimento, a informação deixa de sustentar nova decisão de crédito e deve ser realizada nova consulta Risk 3, observadas as regras operacionais da NCE. Não se atribui rating interno apenas para substituir uma consulta vencida.

## 9 Consumidores acima de 5 MWm

Para consumidores com demanda agregada superior a 5 MWm, a análise de crédito combina componentes quantitativos e qualitativos conforme a NCE 4.04. O bloco quantitativo representa 70% da avaliação, com pesos globais de 32% para PD, 24% para FCO/ROL, 7% para ROE e 7% para ROA. O bloco qualitativo representa 30%, composto por Nota Board (20%), Auditoria (5%) e Bureau (5%).

A PD_base é calculada pelo modelo contábil do item 4 e constitui o sinal quantitativo utilizado na granularização. O Rating_final resulta da metodologia interna e pode ser melhor ou pior que a indicação isolada da PD_base. Uma vez determinado o Rating_final, a PD_final deve ser calculada obrigatoriamente dentro da faixa correspondente, segundo a transformação definida no item 9.2.

### 9.1 Faixas calibradas de PD

| **Rating** | **Faixa anual de PD_final**       |
|------------|-----------------------------------|
| A          | 0,50% a 1,8280%                   |
| B          | >1,8280% a 6,6337%               |
| C          | >6,6337% a 14,1236%              |
| D          | >14,1236% a 50,00%               |
| E          | >50,00% a 99,9958% (aprox. 100%) |

Os limites acima correspondem aos parâmetros correntes do estudo. Os valores exibidos estão arredondados; a implementação utiliza os parâmetros completos versionados na planilha Consumidores maior que 5MWm.xlsx. O valor de 50% constitui a fronteira D/E.

### 9.2 Transformação da PD_base e interpolação intrafaixa

A posição da contraparte dentro da faixa do Rating_final não é escolhida pelo usuário e não decorre de simples truncamento da PD_base. A planilha define uma transformação monotônica objetiva. Seja r o Rating_final, q a PD_base expressa entre 0 e 1, L = PD_min(r) e K = PD_max(r). Quando a entrada estiver expressa em percentual maior que 1, ela é previamente dividida por 100.

q = PD_base; L = PD_min(r); K = PD_max(r)

Para estabilidade numérica, limita-se a entrada probabilística com ε = 10⁻⁹:

q_cap = min{1-ε, max[ε, q]}

Em seguida, aplica-se a função quantil da distribuição t-Student com 6 graus de liberdade, multiplicada pelo fator de escala 1,2:

z = 1,2 · T₆⁻¹(q_cap)

O valor transformado é convertido em uma posição relativa u, necessariamente entre zero e um, pela função logística:

u = 1 / [1 + exp(-z)]

Por fim, a PD_final é obtida por interpolação linear entre os limites da faixa correspondente ao Rating_final:

PD_final = L + u·(K - L)

A transformação é monotônica: dentro de um mesmo Rating_final, maior PD_base implica maior u e, consequentemente, maior PD_final. Dessa forma, duas contrapartes com o mesmo rating podem manter probabilidades distintas sem ultrapassar os limites definidos para a classe.

### 9.3 Efeito do componente qualitativo

Como o Rating_final incorpora componentes quantitativos e qualitativos, uma melhora qualitativa desloca a contraparte para a faixa de menor risco correspondente ao novo rating, enquanto um rebaixamento desloca a PD_final para a faixa de maior risco. Em ambos os casos, a PD_base permanece como referência para determinar a posição relativa dentro da nova faixa por meio da transformação do item 9.2.

Assim, o Rating_final determina a faixa admissível de PD e a PD_base determina objetivamente a posição da contraparte dentro dessa faixa. A interpolação t-Student é parte integrante da metodologia e não constitui opção de implementação.

### 9.4 Validade das informações e PD substituta

As demonstrações financeiras utilizadas na avaliação dos consumidores com demanda agregada superior a 5 MWm possuem validade de 18 meses, enquanto a consulta de bureau possui validade de 365 dias, conforme a NCE 4.04. Enquanto as demonstrações financeiras permanecerem válidas, aplica-se a metodologia ordinária descrita nos itens 9.1 a 9.3.

Caso as demonstrações financeiras ultrapassem o prazo de 18 meses sem disponibilização de novas informações contábeis válidas, a PD_base proveniente do modelo contábil deixa de ser considerada vigente. Até a realização de nova análise com demonstrações financeiras atualizadas, utiliza-se como PD substituta a PD_Risk3 vigente, sujeita ao piso conservador de 50%:

PD_sub,Cons>5 = max(PD_Risk3, 50,00%)

O piso de 50% corresponde à fronteira definida para o critério de maior risco dos consumidores na metodologia vigente. A regra assegura tratamento conservador durante o período em que a fonte contábil primária deixou de ser válida. Se a PD_Risk3 vigente for superior a 50%, prevalece o maior valor.

A utilização da PD_Risk3 como fonte substituta pressupõe consulta vigente. Na ausência de PD_Risk3 válida, deverá ser realizada nova consulta antes de nova decisão de crédito; informação vencida não deve ser tratada como evidência corrente.

O vencimento isolado da consulta de bureau não implica substituição automática de uma PD contábil ainda válida. Nessa situação, a informação qualitativa deve ser atualizada antes de nova análise de crédito ou revisão do Rating_final, observando-se a validade de 365 dias prevista na NCE 4.04.

Uma vez restabelecidas demonstrações financeiras válidas, a contraparte retorna à metodologia ordinária dos itens 9.1 a 9.3, com novo cálculo da PD_base, do Rating_final e da PD_final.

## 10 Eventos especiais e regras de impedimento

### 10.1 Recuperação Judicial

A Recuperação Judicial é tratada como evento de crédito impeditivo para novas operações, pois a política da companhia não permite realização de negócio com contraparte em RJ. Consequentemente, a avaliação qualitativa não pode elevar o rating ou reduzir a PD enquanto a contraparte estiver nessa condição.

RJ = Sim ⇒ PD_final = 100% e novas operações = não permitidas

A PD de 100% é utilizada para mensuração conservadora do risco das exposições existentes durante a RJ. O retorno à metodologia ordinária somente ocorre após o encerramento formal da condição e realização de nova análise de crédito com informações válidas; não há restauração automática do rating anterior.

Para consumidores, essa regra também é coerente com a NCE 4.04, que exclui contrapartes em Recuperação Judicial da possibilidade de elevação de rating por histórico de 12 meses de adimplência.

### 10.2 Monitoramento e demais restrições operacionais

Regras de suspensão de limites por monitoramento na CCEE ou por decisão interna permanecem regidas pela NCE 4.03. O status de monitoramento deve ser registrado separadamente da PD para que a decisão operacional não seja confundida com a estimativa estatística de default.

## 11 Perda Esperada e Taxa de Risco de Crédito

A PD_final anual é utilizada em conjunto com a exposição e a severidade de perda para apurar a perda esperada. Para esta Nota, a exposição no momento do default é definida como a marcação a mercado positiva da carteira frente à contraparte no horizonte de 12 meses:

EAD₁₂ₘ = max(MtM₁₂ₘ, 0)

A LGD corresponde à parcela da EAD não coberta por garantia ou outro mitigador reconhecido para fins de risco. Esta Nota não define modalidade, estrutura, elegibilidade, haircut ou validade jurídica da garantia; esses elementos pertencem à metodologia específica de garantias. O valor da garantia reconhecida é recebido como parâmetro de entrada e a LGD é calculada pela parcela não mitigada da exposição:

LGD = min{1, max[(EAD₁₂ₘ - Garantia_reconhecida) / EAD₁₂ₘ, 0]}, para EAD₁₂ₘ > 0

Quando não houver garantia ou mitigador reconhecido, Garantia_reconhecida = 0 e, portanto, LGD = 100%. Se EAD₁₂ₘ = 0, não há exposição ao default e a perda esperada é nula; para fins operacionais, adota-se LGD = 0.

EL = EAD₁₂ₘ · PD_final · LGD

TRC = EL / Notional

Para a carteira, utiliza-se a razão entre a soma das perdas esperadas e a soma dos notionals:

TRC_carteira = Σ ELᵢ / Σ Notionalᵢ

| A separação entre PD e garantias evita dupla contagem. A PD mede o risco de ocorrência do default da contraparte; a LGD mede a parcela da exposição efetivamente perdida após mitigadores. |
|----|

## 12 Controles, evidências e governança

A aplicação da metodologia deve manter trilha de auditoria suficiente para reproduzir o resultado de cada contraparte. O registro mínimo inclui:

> **•** segmento da contraparte e regra metodológica aplicada;
>
> **•** data e validade das demonstrações financeiras, do bureau e do rating público, quando aplicável;
>
> **•** PD_base ou PD_Risk3 e respectivos dados de entrada;
>
> **•** scores quantitativos e qualitativos, Score_total e Rating_final, quando aplicável;
>
> **•** faixa [PD_min, PD_max], parâmetros e regra de interpolação intrafaixa, quando aplicável, e PD_final;
>
> **• motivo, data de acionamento, fonte substituta e valor da PD_sub, quando utilizada para CPURA, CGRUPO ou consumidores acima de 5 MWm;**
>
> **•** status de Recuperação Judicial e demais impedimentos operacionais;
>
> **•** EAD_12m, LGD utilizada, EL, Notional e TRC;
>
> **•** versão das tabelas, parâmetros, bases de calibração e fórmulas de granularização utilizadas.

Devem existir controles automáticos para assegurar PD no intervalo [0,1]; rating no domínio permitido apenas nos segmentos em que existe Rating Copel; coerência da PD_final com o Rating_final para CPURA e consumidores acima de 5 MWm; igualdade PD_final = PD_Risk3 para consumidores até 5 MWm; respeito à fronteira de 50% para Rating E nos consumidores acima de 5 MWm; reprodução dos parâmetros de interpolação versionados; verificação das validades de DF e bureau por segmento; e aplicação das regras de PD substituta previstas nos itens 6.4, 7.2 e 9.4.

## 13 Quadro-resumo de decisão

| **Público** | **PD em condição normal** | **Informação vencida / evento** | **Resultado** |
|----|----|----|----|
| CPURA | PD contábil + Rating_final + interpolação linear pelo Score_total | DF >18 meses ou bureau vencido | DF vencida: PD_sub = max(PD_Risk3 vigente, 10%). Bureau vencido isoladamente: atualizar consulta antes de nova análise. |
| CGRUPO | PD exata da NCE 4.03 | DF ou rating >18 meses, retirado/suspenso | PD_sub = max(PD_última_válida, 15%). |
| Consumidor ≤5 MWm | PD_Risk3 utilizada diretamente | Bureau vencido | Nova consulta Risk 3; não há Rating Copel nem reenquadramento da PD. |
| Consumidor >5 MWm | PD_base + Rating_final + interpolação t-Student intrafaixa | DF >18 meses ou bureau vencido | DF vencida: PD_sub = max(PD_Risk3 vigente, 50%). Bureau vencido isoladamente: atualizar consulta antes de nova análise. |
| Qualquer público | Regra do segmento | Recuperação Judicial | PD=100% e novas operações vedadas. |

## 14 Referências internas

> **•** NCE 4.03 – Limites Operacionais e Garantias Financeiras Comercializadoras e Geradores, versão 08, 07/07/2026.
>
> **•** NCE 4.04 – Análise de Crédito e Garantias Financeiras para Consumidores, versão 05, 07/07/2026.
