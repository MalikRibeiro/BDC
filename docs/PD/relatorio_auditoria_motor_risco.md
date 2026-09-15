# Relatório de Auditoria de Compliance: Motor de Risco de Crédito

> **Base Normativa:** NOTA_TECNICA_PROB_DEFAULT_FINAL.md (v7)
> **Escopo:** Diretórios `src/domain/credito/`, `src/relational/` e `src/gold/`
> **Objetivo:** Mapeamento Read-Only das lógicas de probabilidade e política.

---

### EIXO 1: Cálculos Matemáticos e Interpolações

* **Modelo Contábil (Z-Score e Logit)** 
  * **[STATUS: AUSENTE]**
  * **Onde deveria residir:** `src/domain/credito/pd_base.py`
  * **Análise:** O arquivo se limita a ler a chave extraída (`PROBABILIDADE_DEFAULT` - Linha 16). Ele não calcula nativamente o escore linear $z$ a partir dos pesos financeiros ($X_{12}, X_{16}, X_{19}, X_{22}$) tampouco operacionaliza a fórmula logística $PD = 1 / (1 + \exp(-z))$. A dependência matemática foi totalmente terceirizada para o arquivo Excel, criando uma caixa-preta externa à engenharia.

* **Interpolação Intrafaixa (CPURA e Consumidores > 5 MWm)** 
  * **[STATUS: IMPLEMENTADO]**
  * **Onde reside:** `src/domain/credito/pd_cpura.py` e `src/domain/credito/pd_consumidor_gt5.py`
  * **Análise:** O cálculo de posição relativa (Linear) para Comercializadoras Puras está perfeitamente refletido em `pd_cpura.py` (linhas 132-147). O escalonamento via Transformação t-Student (6 graus de liberdade, escala 1,2) para grandes consumidores está fielmente transcrito em `pd_consumidor_gt5.py` (linhas 15-28, função `_inv_t_aproximado`, e linhas 74-78).

* **Perda Esperada (EL)**
  * **[STATUS: IMPLEMENTADO]**
  * **Onde reside:** `src/domain/credito/motor_pe.py`
  * **Análise:** A fórmula $EL = EAD_{12m} \cdot PD_{final} \cdot LGD$ está aplicada adequadamente na função `calcular_perda_esperada` (linha 57: `pe_reais = float(ead) * float(lgd_liquida) * float(pd_final)`).

---

### EIXO 2: Fallbacks e PD Substituta ($PD_{sub}$)

* **Trava de Validade (> 18 meses) e Pisos Matemáticos ($10\%$, $15\%$, $50\%$)**
  * **[STATUS: AUSENTE]**
  * **Onde deveria residir:** `src/domain/credito/pd_motor.py` ou `src/domain/credito/pd_validator.py`
  * **Análise:** Não há qualquer controle de obsolescência comparando a data da demonstração financeira e a data base. Consequentemente, o código não impõe as sobreposições de salvaguarda $PD_{sub}$ citadas (ex: `max(PD_Risk3, 10%)` para CPURA). Isso expõe a arquitetura ao risco sistêmico de manter ratings artificialmente bons com informações caducadas.

---

### EIXO 3: Segregação Metodológica (Bureau)

* **Consumidores $\le$ 5 MWm (Adoção direta da $PD_{Risk3}$)**
  * **[STATUS: AUSENTE]** (Possui implementação falha/paralela)
  * **Onde reside:** `src/domain/credito/pd_consumidor_le5.py`
  * **Análise:** Há uma quebra metodológica grave. O normativo estabelece que consumidores deste segmento não possuem Rating Copel e adotam diretamente a $PD_{Risk3}$. Contudo, no código (linhas 24-34), o sistema forja artificialmente um Rating Copel partindo do Score do Bureau (`if score >= 800: rating = 'A'`) e pior: submete essa nota fabricada a um novo processo de interpolação nas faixas (linha 50). 

---

### EIXO 4: Eventos Impeditivos

* **Recuperação Judicial (RJ)**
  * **[STATUS: AUSENTE]**
  * **Onde deveria residir:** `src/domain/credito/pd_motor.py` ou um módulo raiz (ex: `pd_exceptions.py` / orchestrator de regras impeditivas).
  * **Análise:** O motor de cálculo flui organicamente para todas as contrapartes sem travas de short-circuit (curto-circuito) verificando a tag de Recuperação Judicial. O código não trava a $PD_{final} = 100\%$ nos casos confirmados, podendo gerar cálculos falsamente saudáveis se o rating e a DF passarem.
