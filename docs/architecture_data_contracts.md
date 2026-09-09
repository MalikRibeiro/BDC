# Arquitetura e Contratos de Dados (BD Crédito)

## 1. Princípios e Limites Arquiteturais

1. **Unidade Central:** A contraparte é a entidade central (CNPJ padronizado).
2. **Histórico Imutável:** Avaliações geram novas linhas (versões), não sobresscrevem o histórico.
3. **Falha Segura:** Erros críticos em campos sensíveis (como CNPJ ausente ou falha de conversão numérica) bloqueiam a publicação do dado na camada Gold.
4. **Carga Manual Controlada:** Inserções manuais, overrides e substituições de DF devem estar desassociadas dos dados de origem, possuindo entidade própria e dupla temporalidade (data de registro x competência do negócio).

## 2. Mapa de Diretórios e Camadas

- **`ENTRADAS/control/`**: Ponto único de parametrização do negócio (configs, mappings, schemas, rules, quality).
- **`src/staging/` e `src/storage/`**: Isolamento de movimentação, bloqueio concorrente (staging) e gravação de arquivos raw imutáveis (Bronze).
- **`src/silver/`**: Regras estritas de validação técnica, padronização (CNPJ, Datas) e integração com catálogos (sem aplicação de lógica de crédito).
- **`src/domain/`**: Lógica central por nicho. Fichas (extração), Contrapartes (matching), Crédito (Motores de PD, Rating, LGD) e Auditoria.
- **`src/relational/` e `src/gold/`**: Camadas de consumo estruturadas em modelo estrela/relacional, tabelas materializadas finais.

## 3. Fonte Canônica de JSONs

- **`domain_dictionaries.json`**: Guarda os domínios aceitos e listas de conversão nominal (Aliases de Agências, Auditorias, Enums de Status de Contrato e Analise).
- **`schema_ficha_*.json`**: Fonte estrita para tipos de variáveis, obrigatoriedade de campos e Regex das chaves extraídas da Bronze para a Silver.
- **`master_catalog_*.json`**: Mapeamento físico para as origens dos dados. Substitui *hardcodes* de aba/célula no extrator e define os blocos funcionais do dado.
- **`score_cpura_config.json`**: Contém **pesos matemáticos, faixas numéricas de indicadores e faixas de score qualitativo** da metodologia do Scorecard (Comercializadoras Puras).
- **`pd_faixas.json`**: Mantém as faixas globais de probabilidade de default para limites de Clamp (C-PURA, C-GRUPO, Consumidores).
- **`pd_transform_rules.json`**: Define regras diretas de de-para para metodologias que não passam por scorecards (C-Grupo e rating externo de Consumidores).

## 4. Política de Precedência e Conflitos

- **Tipagem:** A tipagem declarada no Schema JSON (`schema_ficha_*`) prevalece sobre conversões em código (o código deve apenas garantir compatibilidade com o schema).
- **Domínios e Aliases:** O dado sempre passa por normalização de chave usando o `domain_dictionaries.json`. Hardcodes de dicionários em módulos como `pd_cgrupo.py` são expressamente proibidos. O fluxo de normalização ocorre na passagem para a **Silver**.
- **Nulidade:** Entradas como "N/A", "-", "#" e texto nulo são tratadas de forma centralizada pelo módulo comum de nulos. Ausência de demonstração financeira nunca é convertida para 0 de forma automática.
- **Regras de Negócio e Cálculos:** Devem estar contidos na camada Relacional (construção da Fato/Dimensões). A camada Silver reflete puramente o que estava na origem (a verdade dos dados extraídos).

## 5. Estratégia de Compartilhamento e Diferenças Legítimas

### Consumidores x Comercializadoras
- Compartilham os módulos de extração de dados `extrator.py` e validação de schema `validador.py`.
- Compartilham o motor unificado de conversões financeiras em `domain/fichas/`.
- **Diferenças legítimas:** 
  - Comercializadoras Puras dependem de `score_cpura_config.json` e cálculo complexo de rating via PD Motor.
  - Consumidores e Comercializadoras de Grupo (C-Grupo) têm fluxo direto com `pd_transform_rules.json`, sem cálculo de scorecard qualitativo, pois confiam no Rating Externo ou Score de Bureau.
  
## 6. Fluxo de Execução Simplificado
`Ingestão Bronze` -> `Extrator Ficha` -> `Normalização de Domínio (Silver)` -> `Validação JSON Schema e Regras Qualidade` -> `Classificação / Orquestrador` -> `Motor de Crédito (PD, Rating)` -> `Modelo Relacional` -> `Visões Gold`.
