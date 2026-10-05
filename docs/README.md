# BDC — Sistema de Gestão de Risco de Crédito

Bem-vindo ao repositório do **BDC**, o sistema central de ingestão, transformação, governança e armazenamento de dados de risco de crédito (focados em Contrapartes, Comercializadoras e Consumidores Livres).

Este sistema adota uma arquitetura orientada a metadados (Config-Driven) e baseada nos preceitos de um **Data Lakehouse** (Bronze, Silver, Gold), focado na extração automatizada de dados financeiros a partir de planilhas Excel heterogêneas ("Fichas"), e processamento limpo 100% *in-memory* com validação tipificada e trilha de auditoria completa (proveniência).

---

## 🏛️ Arquitetura e Lógica do Projeto

### 1. Separação de Camadas (Lakehouse)
- **ENTRADAS:** Recebe os arquivos Excel originais (fichas, garantias) e abriga os arquivos de **controle** em JSON.
- **SAIDAS/BRONZE:** Armazena os registros brutos extraídos exatamente como vieram das fichas, sem tipagem ou sanitização. A prioridade é imutabilidade e extração semântica baseada em layouts dinâmicos.
- **SAIDAS/SILVER:** Aplica transformações (datas, números, CNPJ, normalização de strings) guiadas estritamente pelo catálogo oficial (`master_catalog`). Não roda regras de negócio ou cálculos de risco (estes ficam confinados aos relatórios e Gold), e possui validação estrita (GATES) para rejeitar registros corrompidos.
- **SAIDAS/GOLD / RELACIONAL:** Tabelas dimensionais e visões master para o consumo final e aplicação dos motores matemáticos de crédito.

### 2. Orientação a Metadados (Config-Driven)
O BDC **não possui configurações de layout ou tipagem hardcoded em Python**. Todo o comportamento do pipeline é ditado por dicionários, catálogos e schemas JSON centralizados na pasta `ENTRADAS/control/`:
- `quality/master_catalog_*.json`: Define a tipagem (`float`, `date`, `cnpj`), se o campo é obrigatório (`criticality`) e os padrões de busca semântica em planilhas (`search_patterns`).
- `layouts/catalogo_layouts_*.json`: Dita o comportamento do extrator para diferentes padrões/versões de planilhas recebidas (por exemplo, quais abas ler, em que coordenada inicia).

### 3. Governança e Carga Manual (Overrides)
O sistema aceita overrides pontuais para dados financeiros que falharam na extração automatizada ou não vieram nas Fichas. Esse processo é formal e estruturado (`schema_carga_manual`), mantendo rastreabilidade rigorosa. As intervenções geram CSVs que são processados e injetados de volta no pipeline da Silver durante a orquestração.

---

## 🚀 Ordem de Execução e Orquestração

O pipeline de dados processa os fluxos em domínios isolados, permitindo que a ingestão de **Comercializadoras** seja operada de modo independente de **Consumidores**.

### 1. Ingestão e Processamento (ETL Base)
Estes são os motores principais do pipeline. Devem ser rodados para carregar novas Fichas que foram depositadas nas pastas de `ENTRADAS/fichas/...` e promover os dados até a camada Silver.

Para executar o pipeline de **Comercializadoras**:
```bash
python -m src.app.comercializadoras.orquestrador_comercializadoras
```

Para executar o pipeline de **Consumidores**:
```bash
python -m src.app.consumidores.orquestrador_consumidores
```

*(Nota: Estes orquestradores cuidarão automaticamente de ler as Fichas, processar na Bronze, normalizar, validar o catálogo JSON, aplicar as cargas manuais e gravar em Parquet/CSV na Silver).*

### 2. Torre de Controle de Dados (Streamlit)
O sistema dispõe de uma interface **Streamlit** operacional completa ("Torre de Controle") com navegação modular:

- **🚀 Orquestrador (ETL):** Permite disparar o pipeline completo (`main.py`) em segundo plano e acompanhar o log de execução em tempo real (`LOGS/runner/`).
- **🔍 Diagnóstico e Carga Manual:** Escaneia a camada Silver, identifica lacunas obrigatórias, pagina pendências e gera automaticamente os CSVs de Carga Manual (`COMPLEMENTACAO`).
- **📊 Visão Silver:** Permite consultar os datasets normalizados da Silver (Comercializadoras, Consumidores, Denodo, Salesforce e Receita) e criar eventos formais de `CORRECAO` (Override).
- **⚖️ Reconciliações:** Apresenta relatórios e cruzamentos relacionais de integridade cruzada (Contratos x MtM e Fichas x Salesforce) com identificação de divergências.

**Para iniciar a Torre de Controle:**
```bash
python -m streamlit run src/ui/app.py
```
*(O aplicativo abrirá no seu navegador local em `http://localhost:8501`. Nenhum dado sensível é trafegado para fora da sua máquina).*

---

## 🛠️ Manutenção e Boas Práticas (Developer Guide)

- **Nunca chumbem tipos ou layouts no Python:** Se um tipo precisar ser alterado de `float` para `string`, ou uma nova regra de busca de string surgir para o `LUCRO_LIQUIDO`, modifique o `master_catalog_comercializadoras.json` ou `master_catalog_consumidores.json`. 
- **Nunca edite os Parquets ou CSVs da Silver diretamente:** A Silver é o reflexo da Bronze + Metadados + Carga Manual formal. Se um número estiver incorreto na Silver, utilize a UI de Carga Assistida ou registre um evento de `CORRECAO` para que o pipeline incorpore a mudança de forma auditada.
- **Fail-Safe e Logs:** O projeto registra eventos operacionais, falhas em parsing de planilhas e auditoria nos diretórios `LOGS/runner/` e `LOGS/ingestion/`. Consulte-os primeiro ao investigar uma queda no pipeline.