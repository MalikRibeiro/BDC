# REGRAS E BORDAS EXTRAÍDAS DAS FICHAS CADASTRAIS (FASE 0.6)

**Data de Geração:** 2026-10-05 09:14:21
**Fonte:** Fórmulas reais inspecionadas em amostras físicas de `padrao_6` e `padrao_7`.

## 1. Fórmulas de Classificação (C26:C29)

| Arquivo | Layout | Célula | Rótulo | Texto Real da Fórmula | Valor em Cache |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ELERA COMERCIALIZADORA 28082026.xlsx | padrao_7 | C26 | Probabilidade de Default  - PD (%) | `=INDEX('Calculo Rating'!D6:D10,MATCH(FichaIndividual!B26,'Calculo Rating'!B6:B10))` | E |
| ELERA COMERCIALIZADORA 28082026.xlsx | padrao_7 | C27 | Fluxo de Caixa Operacional/Receita Operacional Líquida | `=INDEX('Calculo Rating'!H6:H10,MATCH(FichaIndividual!B27,'Calculo Rating'!F6:F10))` | D |
| ELERA COMERCIALIZADORA 28082026.xlsx | padrao_7 | C28 | Retorno sobre Ativos | `=INDEX('Calculo Rating'!D16:D20,MATCH(FichaIndividual!B28,'Calculo Rating'!B16:B20))` | E |
| ELERA COMERCIALIZADORA 28082026.xlsx | padrao_7 | C29 | Retorno Sobre Patrimônio Líquido | `=INDEX('Calculo Rating'!H16:H20,MATCH(FichaIndividual!B29,'Calculo Rating'!F16:F20))` | E |
| MARFRIG 27082026.xlsx | padrao_7 | C26 | Probabilidade de Default  - PD (%) | `=INDEX('Calculo Rating'!D6:D10,MATCH(FichaIndividual!B26,'Calculo Rating'!B6:B10))` | C |
| MARFRIG 27082026.xlsx | padrao_7 | C27 | Fluxo de Caixa Operacional/Receita Operacional Líquida | `=INDEX('Calculo Rating'!H6:H10,MATCH(FichaIndividual!B27,'Calculo Rating'!F6:F10))` | D |
| MARFRIG 27082026.xlsx | padrao_7 | C28 | Retorno sobre Ativos | `=INDEX('Calculo Rating'!D16:D20,MATCH(FichaIndividual!B28,'Calculo Rating'!B16:B20))` | C |
| MARFRIG 27082026.xlsx | padrao_7 | C29 | Retorno Sobre Patrimônio Líquido | `=INDEX('Calculo Rating'!H16:H20,MATCH(FichaIndividual!B29,'Calculo Rating'!F16:F20))` | B |
| KROMA 09092026.xlsx | padrao_7 | C26 | Probabilidade de Default  - PD (%) | `=INDEX('Calculo Rating'!D6:D10,MATCH(FichaIndividual!B26,'Calculo Rating'!B6:B10))` | E |
| KROMA 09092026.xlsx | padrao_7 | C27 | Fluxo de Caixa Operacional/Receita Operacional Líquida | `=INDEX('Calculo Rating'!H6:H10,MATCH(FichaIndividual!B27,'Calculo Rating'!F6:F10))` | D |
| KROMA 09092026.xlsx | padrao_7 | C28 | Retorno sobre Ativos | `=INDEX('Calculo Rating'!D16:D20,MATCH(FichaIndividual!B28,'Calculo Rating'!B16:B20))` | C |
| KROMA 09092026.xlsx | padrao_7 | C29 | Retorno Sobre Patrimônio Líquido | `=INDEX('Calculo Rating'!H16:H20,MATCH(FichaIndividual!B29,'Calculo Rating'!F16:F20))` | C |
| NOVA ENERGIA 26082026.xlsx | padrao_7 | C26 | Probabilidade de Default  - PD (%) | `=INDEX('Calculo Rating'!D6:D10,MATCH(FichaIndividual!B26,'Calculo Rating'!B6:B10))` | C |
| NOVA ENERGIA 26082026.xlsx | padrao_7 | C27 | Fluxo de Caixa Operacional/Receita Operacional Líquida | `=INDEX('Calculo Rating'!H6:H10,MATCH(FichaIndividual!B27,'Calculo Rating'!F6:F10))` | C |
| NOVA ENERGIA 26082026.xlsx | padrao_7 | C28 | Retorno sobre Ativos | `=INDEX('Calculo Rating'!D16:D20,MATCH(FichaIndividual!B28,'Calculo Rating'!B16:B20))` | D |
| NOVA ENERGIA 26082026.xlsx | padrao_7 | C29 | Retorno Sobre Patrimônio Líquido | `=INDEX('Calculo Rating'!H16:H20,MATCH(FichaIndividual!B29,'Calculo Rating'!F16:F20))` | D |
| POLLARIX 03062026.xlsx | padrao_6 | C26 | Probabilidade de Default  - PD (%) | `=INDEX('Calculo Rating'!D6:D10,MATCH(FichaIndividual!B26,'Calculo Rating'!B6:B10))` | A |
| POLLARIX 03062026.xlsx | padrao_6 | C27 | Fluxo de Caixa Operacional/Receita Operacional Líquida | `=INDEX('Calculo Rating'!H6:H10,MATCH(FichaIndividual!B27,'Calculo Rating'!F6:F10))` | E |
| POLLARIX 03062026.xlsx | padrao_6 | C28 | Retorno sobre Ativos | `=INDEX('Calculo Rating'!D16:D20,MATCH(FichaIndividual!B28,'Calculo Rating'!B16:B20))` | A |
| POLLARIX 03062026.xlsx | padrao_6 | C29 | Retorno Sobre Patrimônio Líquido | `=INDEX('Calculo Rating'!H16:H20,MATCH(FichaIndividual!B29,'Calculo Rating'!F16:F20))` | A |
| J&F 20082026.xlsx | padrao_6 | C26 | Probabilidade de Default  - PD (%) | `=IF(H12='Rating Grupo'!A2,
    _xlfn.XLOOKUP(FichaIndividual!H13,'Rating Grupo'!A8:A27,'Rating Grupo'!G8:G27),
    IF(H12='Rating Grupo'!A3,
       _xlfn.XLOOKUP(FichaIndividual!H13,'Rating Grupo'!A28:A48,'Rating Grupo'!G28:G48),
       IF(H12='Rating Grupo'!A4,
          _xlfn.XLOOKUP(FichaIndividual!H13,'Rating Grupo'!A49:A70,'Rating Grupo'!G49:G70),
          "E")))` | A |
| J&F 20082026.xlsx | padrao_6 | C27 | Fluxo de Caixa Operacional/Receita Operacional Líquida | `=INDEX('Calculo Rating'!H6:H10,MATCH(FichaIndividual!B27,'Calculo Rating'!F6:F10))` | C |
| J&F 20082026.xlsx | padrao_6 | C28 | Retorno sobre Ativos | `=INDEX('Calculo Rating'!D16:D20,MATCH(FichaIndividual!B28,'Calculo Rating'!B16:B20))` | C |
| J&F 20082026.xlsx | padrao_6 | C29 | Retorno Sobre Patrimônio Líquido | `=INDEX('Calculo Rating'!H16:H20,MATCH(FichaIndividual!B29,'Calculo Rating'!F16:F20))` | A |

## 2. Fórmulas de Conversão em Score (N67 e N72:N76)

| Arquivo | Layout | Célula | Rótulo | Texto Real da Fórmula | Valor em Cache |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| POLLARIX 03062026.xlsx | padrao_6 | N67 | Board Copel | `=VLOOKUP(M67,'Calculo Rating'!$J$5:$K$9,2)*C37` | 1.1999999999999997 |
| POLLARIX 03062026.xlsx | padrao_6 | N72 | Probabilidade de Default | `=VLOOKUP(M72,'Calculo Rating'!$J$5:$K$9,2)*C42` | 3.22 |
| POLLARIX 03062026.xlsx | padrao_6 | N73 | FCO/ROL | `=IFERROR(VLOOKUP(M73,'Calculo Rating'!$J$5:$K$9,2)*C45,0)` | 0 |
| POLLARIX 03062026.xlsx | padrao_6 | N74 | ROA | `=IFERROR(VLOOKUP(M74,'Calculo Rating'!$J$5:$K$9,2)*C44,0)` | 0.7 |
| POLLARIX 03062026.xlsx | padrao_6 | N75 | ROE | `=IFERROR(VLOOKUP(M75,'Calculo Rating'!$J$5:$K$9,2)*C43,0)` | 0.7 |
| J&F 20082026.xlsx | padrao_6 | N67 | Board Copel | `=VLOOKUP(M67,'Calculo Rating'!$J$5:$K$9,2)*C37` | 1.9999999999999996 |
| J&F 20082026.xlsx | padrao_6 | N72 | Probabilidade de Default | `=VLOOKUP(M72,'Calculo Rating'!$J$5:$K$9,2)*C42` | 3.22 |
| J&F 20082026.xlsx | padrao_6 | N73 | FCO/ROL | `=IFERROR(VLOOKUP(M73,'Calculo Rating'!$J$5:$K$9,2)*C45,0)` | 1.428 |
| J&F 20082026.xlsx | padrao_6 | N74 | ROA | `=IFERROR(VLOOKUP(M74,'Calculo Rating'!$J$5:$K$9,2)*C44,0)` | 0.41999999999999993 |
| J&F 20082026.xlsx | padrao_6 | N75 | ROE | `=IFERROR(VLOOKUP(M75,'Calculo Rating'!$J$5:$K$9,2)*C43,0)` | 0.7 |

## 3. Síntese das Bordas de Decisão Observadas

*(As bordas são derivadas exclusivamente das cláusulas `SE(...)` acima)*:

- **PD Base (C26):**
  - Se $PD \le 2,00\% \implies A$
  - Se $2,00\% < PD \le 5,00\% \implies B$
  - Se $5,00\% < PD \le 10,00\% \implies C$
  - Se $10,00\% < PD \le 15,00\% \implies D$
  - Se $PD > 15,00\% \implies E$

