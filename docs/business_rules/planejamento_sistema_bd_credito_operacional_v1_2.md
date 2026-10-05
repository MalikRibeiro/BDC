<!-- Página 1 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## BD CRÉDITO

# Planejamento do Sistema de Gestão

# de Dados de Crédito

Definição funcional, arquitetura de dados, saídas analíticas, controles e trilha de

auditoria

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Versão operacional proposta: 1.2

Data de referência: 21/07/2026

Área de Gestão de Risco de Mercado e Crédito


Uso interno — documento de planejamento

Página 1 de 37


---

<!-- Página 2 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## Controle do documento

Item
Definição

Documento
Planejamento do Sistema de Gestão de Dados de Crédito — BD Crédito

Objetivo
Consolidar o escopo funcional, técnico e operacional do sistema, incluindo entradas automáticas
e manuais, processamentos, saídas, auditoria, rastreabilidade e regras de enquadramento por
contrato e volume.

Versão
1.2 — versão operacional com carga manual histórica controlada e tratamento de ausência de
DF

Data
21/07/2026

Situação
Proposta para revisão e homologação da área de negócio

Escopo principal
Gestão documental, cadastro de contrapartes, contratos correntes, segmentação, análises de
crédito, atualização manual controlada do histórico, rating/PD, perda esperada, garantias, taxa
de risco, relatórios e interface de dados para cálculo externo de limites.


Uso interno — documento de planejamento

Página 2 de 37


---

<!-- Página 3 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## Sumário executivo

O BD Crédito será a base corporativa para receber, identificar, classificar, organizar, extrair, consolidar e
acompanhar historicamente informações de crédito de contrapartes. A solução deverá integrar fichas de
comercializadoras e consumidores, Salesforce, dados cadastrais externos, arquivos de parametrização e a
base de MtM do sistema de risco de mercado.

A unidade central do sistema será a contraparte, identificada por chave interna e CNPJ padronizado. A
solução deverá preservar tanto a evidência documental original quanto os dados extraídos, as regras
aplicadas, os cálculos realizados e as versões publicadas, permitindo reconstruir qualquer resultado
apresentado nos relatórios.

O sistema será responsável pela consolidação de rating, probabilidade de default, exposição, LGD, perda
esperada, garantias, taxa de risco de crédito e situação da análise. O cálculo do limite de crédito
permanecerá fora do escopo: o BD Crédito gerará um arquivo de entrada padronizado para o sistema
responsável pelo cálculo de limites.

Princípio central de governança
Nenhum dado final deverá existir sem vínculo com a fonte, a data de referência, a versão da
metodologia, os parâmetros utilizados e o processamento que o produziu. A trilha de auditoria deverá
permitir navegar do relatório Gold até o arquivo, registro ou célula de origem.


A segmentação metodológica será determinada pela natureza da contraparte e, no caso de consumidores,
pelo volume contratado. Comercializadoras serão classificadas como puras ou pertencentes a grupo
econômico, mantendo análise individual por CNPJ. Consumidores com pelo menos 5 MWm contratados
serão submetidos à análise detalhada de demonstrações financeiras; consumidores abaixo de 5 MWm
serão avaliados por score de bureau. O relatório de contratos do Denodo será a fonte preferencial para
vínculo contratual e volume, enquanto o MtM será a fonte oficial de exposição e uma fonte de reconciliação.

O sistema também deverá aceitar atualizações históricas inseridas manualmente quando uma informação
não estiver disponível nas fontes automáticas — por exemplo, quando a contraparte não encaminhar as
demonstrações financeiras. A carga manual será tratada como uma fonte controlada, com competência do
fato, data de registro, motivo, evidência, responsável, aprovação e vigência. Ela não poderá apagar ou
reescrever registros anteriores nem transformar ausência de DF em demonstração financeira disponível.

Uso interno — documento de planejamento

Página 3 de 37


---

<!-- Página 4 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## Estrutura do documento

- 
1. Objetivo, escopo e princípios
- 
2. Arquitetura funcional do sistema
- 
3. Fontes de dados e conteúdo informacional
- 
4. Fluxo operacional e processamento documental
- 
5. Padronização, qualidade e regras de integração
- 
6. Regras de negócio de crédito
- 
7. Saídas, relatórios e interfaces
- 
8. Modelo relacional de dados
- 
9. Arquitetura de dados, ambientes e repositórios
- 
10. Arquitetura modular do código
- 
11. Auditoria, rastreabilidade e controles
- 
12. Operação, monitoramento e segurança
- 
13. Roadmap e critérios de aceite
- 
14. Especificação operacional: entradas, processamentos e saídas
- 
Apêndices: domínios, alertas e dicionário mínimo de saídas.

Uso interno — documento de planejamento

Página 4 de 37


---

<!-- Página 5 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 1. Objetivo, escopo e princípios

### 1.1 Objetivo do sistema

Desenvolver um sistema para receber, identificar, classificar, organizar, extrair, consolidar e acompanhar
historicamente informações de crédito de contrapartes, a partir de fichas individuais e de fontes
complementares, gerando uma visão padronizada, rastreável e atualizada para suporte à gestão de crédito.

O sistema deverá manter um repositório documental organizado das fichas processadas, identificar
automaticamente o tipo, subtipo e versão de cada ficha, aplicar o extrator adequado, integrar as informações
às demais fontes, executar regras parametrizadas e publicar relatórios atuais e históricos.

### 1.2 Valor esperado

- 
Criar uma visão única da contraparte, conciliando cadastro, análise, rating, PD, exposição, garantias e
histórico.
- 
Reduzir tarefas manuais de organização de fichas, consolidação de planilhas e acompanhamento de
vencimentos.
- 
Preservar histórico sem sobrescrever avaliações anteriores.
- 
Padronizar cálculos, domínios, alertas, datas, CNPJ e versões metodológicas.
- 
Disponibilizar evidências suficientes para auditoria, reconciliação e reprodução dos resultados.
- 
Fornecer dados estruturados para Power BI e para o sistema externo de cálculo de limites.

### 1.3 Escopo incluído

- 
Gestão do ciclo documental das fichas de comercializadoras e consumidores.
- 
Classificação de tipo, subtipo e versão/layout por campos-chave.
- 
Extração e padronização dos dados das fichas.
- 
Integração com Salesforce, base de MtM, Receita/Gov.br e arquivos de configuração.
- 
Cadastro e identificação consolidada de contrapartes e grupos econômicos.
- 
Controle de vigência, vencimento e renovação das análises de crédito.
- 
Armazenamento e histórico de rating, scores, PD e componentes do cálculo.
- 
Cálculo e histórico de EAD, LGD, perda esperada e taxa de risco de crédito.
- 
Cadastro e acompanhamento de garantias.
- 
Geração de relatórios atuais, históricos, analíticos, de vencimento, pendências e auditoria.
- 
Exportação do arquivo de dados para o sistema responsável pelo cálculo de limites.

### 1.4 Fora do escopo atual

- 
Cálculo do limite de crédito, do limite disponível ou do consumo de limite: essas funções pertencem a outro
sistema.
- 
Consumo separado das tabelas de contratos e de price adjustment do sistema de risco de mercado; a
integração de risco utilizará a base de MtM consolidada.
- 
Alteração dos arquivos-fonte originais; o sistema deverá preservá-los como evidência.
- 
Decisão automática de aprovação ou reprovação de crédito sem validação da alçada competente.
- 
Substituição dos processos formais de aprovação e governança existentes no Salesforce ou em outros
sistemas corporativos.

Uso interno — documento de planejamento

Página 5 de 37


---

<!-- Página 6 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

### 1.5 Premissas e princípios

Princípio
Aplicação no sistema

Unidade central
A contraparte é a entidade central. O CNPJ padronizado será a principal chave
de integração, complementado por identificador interno e vínculos de grupo
econômico.

Histórico imutável
Novas avaliações e novos cálculos geram novas linhas; registros anteriores não
são sobrescritos.

Fonte identificada
Todo campo deve possuir fonte, data de referência e, quando aplicável,
localização de origem no documento.

Parametrização
Prazos, domínios, regras de alerta, modelos e tabelas de conversão devem ser
externos ao código sempre que possível.

Reprodutibilidade
Resultados devem ser reproduzíveis a partir do snapshot da fonte, versão do
código, configuração e metodologia.

Segregação
DEV, TEST e PRD devem ser fisicamente separados e operar com versões
controladas.

Falha segura
Erros críticos bloqueiam a publicação do dado afetado; o sistema não deve
substituir uma saída válida por uma saída incompleta.

Carga manual controlada
Inclusões tardias e correções entram como novos eventos versionados, com
evidência, alçada e separação entre data do fato e data de registro.

Uso interno — documento de planejamento

Página 6 de 37


---

<!-- Página 7 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 2. Arquitetura funcional do sistema

A solução deverá ser organizada em módulos funcionais independentes, porém integrados por chaves e
identificadores comuns. Essa divisão evita concentração de regras em um único processo e facilita testes,
manutenção e auditoria.

Módulo
Responsabilidade principal

Gestão documental
Receber, identificar, copiar, nomear, classificar, versionar, rejeitar ou promover
fichas e demais arquivos.

Cadastro de contrapartes
Consolidar identidade, CNPJ, CNPJ raiz, matriz/filial, grupo econômico,
controladora, dados cadastrais e status.

Análises de crédito
Controlar data da análise, DF, aprovação, validade, próxima análise,
responsável, parecer, tipo e versão.

Rating e PD
Armazenar scores, componentes quantitativos e qualitativos, rating final, PD
calculada/ajustada e histórico de migração.

Exposição e perda esperada
Consolidar MtM positivo, EAD, LGD, garantias, perda esperada e taxa de risco de
crédito.

Garantias
Cadastrar garantias, valores, emissores, vigência, cobertura e vínculo com
contraparte/contrato.

Relatórios e alertas
Publicar visão atual, histórico, vencimentos, pendências, inconsistências e alertas
de negócio.

Interface de limites
Exportar arquivo Excel padronizado com os dados necessários ao sistema
externo de cálculo de limites.

Auditoria e controle
Registrar processamento, origem, regras, exceções, aprovações, reconciliações,
alterações e publicações.

Atualizações manuais
Receber, validar, aprovar e historizar complementações, correções, ausência de
DF e demais dados tardios sem edição direta da base.

Uso interno — documento de planejamento

Página 7 de 37


---

<!-- Página 8 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 3. Fontes de dados e conteúdo informacional

### 3.1 Fichas de comercializadoras

Bloco
Campos mínimos

Dados gerais
Sigla; CNPJ BBCE; CNPJ; data da DF; código CCEE; data de adesão à CCEE; maturidade
calculada; tipo da comercializadora; categoria; patrimônio líquido; rating público; rating Copel.

Análise quantitativa
PD; FCO/ROL; ROA; ROE; scores individuais e score quantitativo.

Análise qualitativa
Nota Board Copel; demonstrações financeiras auditadas; bureau; rating/score de auditoria;
rating/score de bureau; restritivos; score qualitativo.

Indicadores financeiros
AC/PC; AT/PT; lucro líquido/ROL; (receita de energia - custo de energia)/despesa com pessoal;
MtM total/PL; (dividendos + JCP)/lucro líquido; capital circulante líquido.

Demonstrações financeiras
Ativo circulante; ativo circulante financeiro; ativo total; passivo circulante; passivo circulante
financeiro; passivo não circulante financeiro; patrimônio líquido; capital social; lucros
acumulados; reserva de lucros; vendas líquidas; lucro líquido; FCO.


### 3.2 Fichas de consumidores

As fichas de consumidores deverão ser classificadas conforme a metodologia aplicável. Consumidores com
pelo menos 5 MWm contratados deverão possuir ficha com demonstrações financeiras e análise detalhada.
Consumidores abaixo de 5 MWm deverão possuir análise simplificada baseada em score de bureau, sem
transformar a ausência de demonstrações financeiras em erro. O sistema deverá registrar o volume, a data
de referência, a fonte e a versão da regra utilizada no enquadramento.

Bloco
Campos mínimos

Cadastro comum

CNPJ; razão social; data de abertura; situação cadastral; endereço;
capital social; natureza jurídica; CNAE; grupo econômico; contrato
corrente; volume contratado e fonte do enquadramento.

Consumidor com pelo menos 5 MWm

Ficha com DF; data da DF; ativo, passivo, patrimônio líquido, resultado e
fluxo de caixa; FCO/ROL; ROA; ROE; PD; scores quantitativos;
qualificação da DF; rating resultante.

Consumidor abaixo de 5 MWm

Score de bureau; restritivos; resultado da consulta; rating ou classe
decorrente do bureau; PD associada; data e validade da consulta.
Campos de DF devem ser NÃO_APLICÁVEL, e não pendentes.

Classificação documental

Tipo de consumidor; presença de DF; tipo de análise exigida; versão do
layout; campos obrigatórios; confiança da classificação; compatibilidade
entre ficha e segmento.

Rastreabilidade do enquadramento

volume_enquadramento_mwm; competência; contratos considerados;
fonte_volume; regra_enquadramento; versão_regra;
segmento_metodológico utilizado na análise.

Regra de composição dos campos financeiros
Ativo circulante financeiro compreende, no mínimo, caixa, equivalentes de caixa e aplicações
financeiras. Passivos financeiros compreendem empréstimos e financiamentos, debêntures,
derivativos, duplicatas descontadas, receita diferida, adiantamentos de clientes e partes relacionadas.
Partes relacionadas devem ser consideradas pelo valor líquido, conforme regra definida pela área.




Uso interno — documento de planejamento

Página 8 de 37


---

<!-- Página 9 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

### 3.3 Salesforce

Objeto
Informações de interesse

Cotação
Identificador, AccountId, aprovação, datas de preço e emissão, pagamento, garantia financeira,
modalidade, operação, ponto de entrega, reajuste anual, semanas operativas, maior volume em
MWm, rating vinculado e modalidade de contratação.

Account
Identificador, razão social, cidade, estado, telefone, CNPJ, related party, natureza legal, rating,
score, classificação, resultado, restrição, datas de avaliação e validade, ratings legados, grupo
econômico e perfil de produto.

Chamado
Score, resultado, restrição, rating, classificação, PD, datas de avaliação, rating final, rating de
crédito, status da análise e nota de bureau.

Contrato
Identificação do contrato, vínculo com a conta, código contratual, modalidade e status.


### 3.4 Relatório de contratos do Denodo

O relatório de contratos do Denodo será a fonte preferencial para identificar vínculo contratual corrente com
a Copel e para apurar o volume contratado utilizado no enquadramento metodológico dos consumidores. A
informação será consolidada por CNPJ, contrato, competência e operação, preservando o snapshot da
fonte.

Bloco
Campos mínimos e utilização
Identificação
CNPJ; AccountId quando disponível; contrato_id; código contratual; contraparte; grupo econômico.

Vigência
Status contratual; data de assinatura; início e fim de suprimento; cancelamento ou rescisão; data
de referência.
Características
Modalidade; operação; ponto de entrega; produto; submercado; período; moeda.

Volume
Volume em MWm por competência; unidade; sazonalização quando disponível; maior volume
mensal simultâneo por contraparte.

Derivações
possui_contrato_corrente_copel; quantidade_contratos_correntes; volume_enquadramento_mwm;
possui_pelo_menos_5_mwm.

Auditoria
source_snapshot_id; data de extração; run_id; quantidade de registros; reconciliação com
Salesforce e MtM.

### 3.5 Sistema de risco de mercado

A entrada de risco de mercado será a base de MtM por contraparte, considerada a fonte oficial para
mensuração da exposição de crédito e para obtenção do notional quando a granularidade necessária estiver
disponível. A base deverá preservar contraparte, contrato, operação, período, competência, data-base,
notional, MtM e identificadores do processamento de risco.

O MtM poderá apoiar a identificação de contratos e volumes, mas não será utilizado isoladamente para
concluir que não existe contrato corrente. A ausência de posição no MtM não implica ausência de vínculo
contratual. O Denodo será a fonte preferencial para o status contratual, e a divergência Denodo × MtM
deverá ser reconciliada.

### 3.6 Fontes externas, manuais e parametrizações

- 
API Gov.br/Receita: dados cadastrais, situação cadastral, CNAE principal e secundários, natureza jurídica e
datas de atualização.
- 
Blacklist: contrapartes, grupos, CNPJ, motivo, vigência, responsável e aprovação.
- 
Configurações: prazos por tipo de contraparte, domínios, escalas de rating, regras de alerta, parâmetros de
LGD, mapeamentos, tolerâncias e versões metodológicas.
- 
Catálogo de layouts: campos-chave, campos obrigatórios, localização esperada, pesos, regras de
classificação e versão do extrator.

Uso interno — documento de planejamento

Página 9 de 37


---

<!-- Página 10 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 4. Fluxo operacional e processamento documental

### 4.1 Fluxo ponta a ponta

1. Recebimento: os analistas depositam as fichas e demais arquivos nas pastas de entrada do ambiente.
2. Descoberta: o sistema identifica arquivos ainda não processados por hash, nome, tamanho, data de

modificação e metadados.
3. Staging: o arquivo é copiado para área temporária e bloqueado para processamento concorrente.
4. Ingestão Bronze: o arquivo original é preservado, recebe documento_id, hash e registro de origem.
5. Classificação: o sistema identifica tipo, subtipo e versão/layout por campos-chave e calcula a confiança da

classificação.
6. Extração: o extrator correspondente lê os campos e registra, sempre que possível, aba, célula, intervalo ou

caminho de origem.
7. Validação Silver: CNPJ, datas, tipos, domínios e consistência mínima são verificados e padronizados.
8. Integração: os dados são conciliados com Salesforce, relatório de contratos do Denodo, MtM, Receita,

blacklist, garantias e configurações.
9. Aplicação de regras: são apurados contrato corrente, volume por competência, segmento metodológico,

vencimento, rating/PD, exposição, LGD, perda esperada, taxa de risco e alertas.
10. Publicação: são geradas tabelas relacionais, visões Gold, relatórios, arquivos de interface e evidências de

auditoria.
11. Encerramento: o run recebe status final, totais, exceções, reconciliações e referência às versões

publicadas.

### 4.2 Estados do documento

Status
Significado

DESCOBERTO
Arquivo localizado na entrada, ainda não copiado para staging.

EM_STAGING
Cópia temporária criada e hash calculado.

INGERIDO
Original preservado na Bronze e metadados registrados.

CLASSIFICADO
Tipo, subtipo e layout identificados acima do limite de confiança.

EXTRAÍDO
Campos lidos pelo extrator correspondente.

VALIDADO
Regras mínimas de qualidade e consistência atendidas.

PUBLICADO
Dados promovidos à camada relacional/Gold.

PENDENTE
Processamento incompleto por campo, regra ou vínculo ainda não resolvido.

REJEITADO
Arquivo inválido, corrompido, duplicado indevido ou sem layout reconhecido.


### 4.3 Repositório documental e nomenclatura

A pasta de entrada é operacional e não representa o repositório definitivo. O original deverá ser copiado
para a camada Bronze antes da classificação e jamais deverá ser alterado pelo sistema.

<tipo_ficha>__<subtipo>__<versao>__<cnpj>__<data_analise>__<hash_curto>.<ext>
Exemplo:
comercializadora__com_df__v2__12345678000199__2025-08-31__a81f2c.xlsx


O nome padronizado é um facilitador operacional, mas a identidade definitiva do documento será o
documento_id associado ao hash integral do arquivo.

Uso interno — documento de planejamento

Página 10 de 37


---

<!-- Página 11 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

### 4.4 Metadados documentais mínimos

Grupo
Campos

Identificação
documento_id; hash_arquivo; hash_curto; nome_original; extensão; tamanho_bytes.

Origem
caminho_origem; ambiente; fonte; usuário_depositante quando disponível; data_hora_descoberta.

Destino
caminho_staging; caminho_bronze; caminho_repositório_organizado.

Classificação
tipo_ficha; subtipo_ficha; versão_layout; confiança; campos-chave encontrados;
classificador_versão.

Extração
cnpj_extraído; data_análise_extraída; extrator_versão; status; quantidade_campos;
quantidade_erros.

Processamento
run_id; data_hora_início; data_hora_fim; status_final; mensagem_erro; reprocessamento_de.


### 4.5 Carga manual controlada e atualização histórica

A atualização manual deverá utilizar um template Excel/CSV padronizado na primeira fase ou formulário
controlado em evolução futura. O usuário não poderá editar diretamente arquivos Silver, tabelas relacionais,
saídas Gold ou registros históricos já publicados.

Tipo de evento manual
Uso permitido
Tratamento

COMPLEMENTACAO
Adicionar informação ausente obtida posteriormente, com
fonte comprovável.

Criar nova versão ou evento, mantendo o valor
anterior.

CORRECAO
Corrigir erro de digitação, classificação ou vínculo.
Registrar valor anterior, valor novo, motivo,
evidência e aprovação.

ATUALIZACAO_HISTORICA
Inserir informação referente a competência passada que
não estava estruturada.

Separar data de referência do fato e data de
registro no sistema.

REGISTRO_SEM_DF
Registrar que a empresa não enviou a DF e incluir
informações alternativas permitidas.

Marcar situação da DF e gerar alerta; não
preencher valores financeiros inexistentes.

OVERRIDE
Alterar resultado calculado ou decisão metodológica.
Aplicar fluxo de alçada, vigência, justificativa e
reversibilidade.
A carga deverá preservar dois tempos: a data de referência ou vigência do fato de negócio e a data em que
a informação foi registrada no sistema. Assim, uma informação histórica inserida hoje poderá produzir uma
nova versão válida para uma competência passada sem simular que o dado já estava disponível naquela
época.

Regra para ausência de demonstrações financeiras
A ausência de DF deve ser registrada como situação e motivo, nunca como valores iguais a zero. Para segmentos que exigem
análise detalhada, o registro manual não substitui a DF. Caso a informação manual seja utilizada para manter rating, PD, validade
ou elegibilidade de crédito, deverá existir exceção/override aprovado, com prazo de expiração e alerta específico.

Uso interno — documento de planejamento

Página 11 de 37


---

<!-- Página 12 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 5. Padronização, qualidade e regras de integração

### 5.1 Padrões de dados

Elemento
Padrão

CNPJ
String com 14 dígitos, sem máscara, com validação de dígitos verificadores e preservação
de zeros à esquerda.

CNPJ raiz
Oito primeiros dígitos do CNPJ, armazenados como string.

Datas
ISO YYYY-MM-DD; timestamps em ISO 8601 com fuso do ambiente.

Valores monetários
Decimal, moeda identificada e data-base definida; evitar float binário para persistência
final.

Percentuais
Decimal entre 0 e 1 internamente; apresentação em percentual apenas na camada de
relatório.

Ratings
Domínio controlado com ordem ordinal, classe, PD de referência e vigência da escala.

Status e motivos
Códigos padronizados em configuração, acompanhados de descrição legível.

Ausência de dado
Nulo verdadeiro; não utilizar zero ou texto vazio para representar indisponibilidade.


### 5.2 Dimensões de qualidade

Dimensão
Exemplo de controle

Completude
Percentual de campos obrigatórios preenchidos por tipo de ficha e versão.

Validade
CNPJ válido, datas plausíveis, rating pertencente ao domínio e percentuais na faixa esperada.

Unicidade
Uma identidade documental por hash e uma contraparte vigente por CNPJ/identificador.

Consistência
Ativo total compatível com componentes; datas em ordem lógica; rating e PD coerentes com a escala
vigente.

Rastreabilidade
Campo final ligado à fonte, localização, transformação e versão da regra.


### 5.3 Regras mínimas de validação

- 
Bloquear publicação de ficha sem CNPJ válido, data de análise ou layout reconhecido, salvo exceção
formalmente aprovada.
- 
Sinalizar divergência de CNPJ entre nome do arquivo, conteúdo da ficha, Salesforce e Receita.
- 
Sinalizar rating fora do domínio, PD fora de [0,1], valores monetários não numéricos e datas futuras
indevidas.
- 
Sinalizar duplicidade por hash e possível duplicidade semântica por CNPJ + data da análise + versão.
- 
Registrar campos ausentes, campos adicionais e mudança de localização em relação ao layout esperado.
- 
Não publicar saída Gold quando reconciliações críticas falharem acima da tolerância configurada.
- 
Bloquear análise detalhada de consumidor sem demonstrações financeiras quando o volume de
enquadramento for igual ou superior a 5 MWm.
- 
Bloquear análise simplificada de consumidor abaixo de 5 MWm quando não houver bureau válido e vigente.
- 
Sinalizar volume não identificado, mudança de faixa desde a análise anterior e divergência de volume entre
Denodo, Salesforce e MtM.
- 
Sinalizar comercializadora de grupo sem grupo econômico identificado ou sem análise individual vinculada
ao CNPJ.
- 
Validar CNPJ, competência, campo, tipo de dado, domínio, motivo, evidência, solicitante e aprovador de
toda carga manual.

Uso interno — documento de planejamento

Página 12 de 37


---

<!-- Página 13 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

- 
Impedir que carga manual sobrescreva fisicamente uma análise, DF, rating, PD ou cálculo já publicado; a
correção deverá gerar nova versão.
- 
Não converter campo financeiro ausente em zero. Utilizar situacao_df, motivo_ausencia_df e indicador de
não aplicabilidade.
- 
Bloquear publicação de campos sensíveis inseridos manualmente enquanto a aprovação estiver pendente
ou a evidência estiver ausente.
- 
Recalcular somente os resultados impactados pela atualização manual, preservando a publicação anterior
e a justificativa do reprocessamento.

### 5.4 Regras de matching e precedência de fontes

A integração deverá priorizar chaves determinísticas. O CNPJ completo é a primeira chave; CNPJ raiz,
código CCEE, AccountId e identificadores internos podem complementar o vínculo. Matching aproximado
por nome deverá ser utilizado apenas como sugestão de pendência, nunca como vínculo automático
definitivo sem regra e evidência.

Informação
Fonte preferencial sugerida
Regra de conflito

Situação cadastral e CNAE
Receita/Gov.br
Manter o valor mais recente e preservar o histórico das
consultas.

Identidade comercial e grupo econômico
Salesforce, validado pela área
Divergência gera pendência; não sobrescrever
silenciosamente.

Rating e PD aprovados
Ficha/análise homologada ou Chamado
aprovado

Priorizar registro aprovado e vigente; armazenar valores
concorrentes por fonte.

Exposição
Base de MtM
Conciliar total por data-base e contraparte com a fonte.

Dados financeiros
Ficha e demonstração financeira vinculada
Conservar data da DF e versão da ficha.

Contrato corrente com a Copel
Relatório de contratos do Denodo
MtM e Salesforce funcionam como reconciliação;
ausência no MtM não encerra o vínculo contratual.
Volume para enquadramento do
consumidor

Denodo por competência; Salesforce
aprovado como alternativa

Utilizar o maior volume mensal simultâneo; exceção
manual exige aprovação, evidência e vigência.

Posição e exposição de risco
Base de MtM
Conciliar contrato, CNPJ e competência com Denodo;
divergência gera pendência.

Informação inserida manualmente
Template/formulário controlado e
aprovado

Não sobrescrever fonte oficial; registrar competência,
data da inserção, evidência, responsável, aprovador e
impacto.

Uso interno — documento de planejamento

Página 13 de 37


---

<!-- Página 14 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 6. Regras de negócio de crédito

### 6.1 Cadastro e identificação da contraparte

- 
Identificador interno único da contraparte.
- 
CNPJ completo e CNPJ raiz.
- 
CNPJ BBCE, código CCEE e data de adesão à CCEE, quando aplicáveis.
- 
Maturidade em anos, calculada a partir da data de adesão ou da data de abertura conforme regra do
segmento.
- 
Tipo da comercializadora, categoria, matriz/filial e contraparte individual ou grupo consolidado.
- 
Grupo econômico, controladora final e tipo de vínculo com o grupo.
- 
Situação cadastral, data da atualização, setor econômico padronizado e CNAEs.
- 
Indicador de contrato corrente com a Copel, quantidade de contratos vigentes, datas extremas de vigência
e data de referência contratual.
- 
Volume contratado por competência, maior volume mensal simultâneo, indicador de pelo menos 5 MWm,
fonte e data de extração.
- 
Indicador de posição existente no MtM e status de conciliação entre contrato Denodo e posição de risco.
- 
Segmento atual da contraparte e segmento metodológico utilizado em cada análise histórica.

### 6.2 Segmentação metodológica e vínculo contratual

A segmentação deverá ocorrer antes da execução da metodologia de crédito. O cadastro atual poderá ser
atualizado a cada carga, mas cada análise deverá preservar o segmento, o volume, a fonte e a regra
utilizados na data da avaliação.

Tipo / segmento
Critério operacional
Análise exigida

Comercializadora pura
Comercializadora sem enquadramento em grupo
econômico para fins da metodologia.

Análise individual da comercializadora, com DF
e metodologia aplicável ao segmento.

Comercializadora de grupo
Comercializadora vinculada a grupo econômico e
controladora final identificados.

Análise individual por CNPJ; informações do
grupo podem complementar, mas não
substituir a avaliação da entidade.
Consumidor com pelo menos 5
MWm

Maior volume mensal simultâneo contratado maior
ou igual ao limiar parametrizado de 5 MWm.

Análise detalhada com demonstrações
financeiras.

Consumidor abaixo de 5 MWm
Maior volume mensal simultâneo contratado abaixo
de 5 MWm.

Análise simplificada baseada em score de
bureau.
Para o status contratual, um contrato será corrente quando possuir status ativo parametrizado, início de
vigência menor ou igual à data de referência e fim de vigência maior ou igual à data de referência, sem
cancelamento ou rescisão vigente. O indicador possui_contrato_corrente_copel será derivado do Denodo.

O volume de enquadramento será calculado por competência, somando contratos simultaneamente
vigentes e obtendo o maior total mensal dentro do horizonte definido. Não deverão ser somados volumes
pertencentes a competências distintas.

### 6.3 Controle da análise de crédito

Grupo
Campos e regras

Datas
Data da análise; data da DF; data de aprovação; data de validade; data prevista da
próxima análise.

Contadores
Dias até o vencimento; dias desde o vencimento; calculados diariamente com base na
data de referência.

Situação
VIGENTE; PRÓXIMA_DO_VENCIMENTO; VENCIDA; EM_RENOVAÇÃO; SUSPENSA.

Tipo
DF_COMPLETA; BUREAU; EXTRAORDINÁRIA; REVISÃO_BUREAU;
ATUALIZAÇÃO_MANUAL; EXTRAORDINÁRIA_SEM_DF; outros tipos parametrizados.

Responsabilidade
Responsável pela análise; aprovador; área; parecer conclusivo; versão da análise.

Histórico
Cada aprovação, revisão, correção ou carga manual cria nova análise_id/versão ou
evento vinculado, preservando a anterior.

Disponibilidade da DF
RECEBIDA; EM_VALIDACAO; INCOMPLETA; NAO_RECEBIDA; NAO_APLICAVEL;
motivo, data da solicitação e evidência de cobrança.

Uso interno — documento de planejamento

Página 14 de 37


---

<!-- Página 15 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

Faixa de vencimento
Critério

Vencida
data_prevista_proxima_analise < data_referencia

Vence em até 15 dias
0 a 15 dias restantes

Entre 16 e 30 dias
16 a 30 dias restantes

Entre 31 e 60 dias
31 a 60 dias restantes

Entre 61 e 90 dias
61 a 90 dias restantes

Acima de 90 dias
mais de 90 dias restantes


### 6.4 Rating, scores e probabilidade de default

Não deverá ser armazenada apenas a PD final. O sistema deverá preservar os componentes do cálculo, os
dados de entrada, a escala de rating, a versão do modelo e eventuais ajustes aprovados.

Bloco
Campos mínimos

PD
PD calculada; PD ajustada; horizonte; data de cálculo; validade; metodologia; versão do modelo.

Quantitativo
Score bruto; score PD; score FCO/ROL; score ROA; score ROE; score quantitativo.

Qualitativo
Nota Board; rating/score auditoria; rating/score bureau; restritivos; score qualitativo.

Resultado
Score Copel; classe de risco; rating resultante; PD associada ao rating; rating público; rating Copel.

Governança
Fonte, análise_id, aprovador, justificativa de ajuste, validade e versão da escala.


### 6.5 Histórico e matriz de transição

Deverá existir uma linha por avaliação. A matriz de transição será calculada a partir desse histórico, sem
sobrescrever avaliações anteriores.

Campo
Definição

rating_atual / rating_anterior
Ratings de duas avaliações consecutivas da mesma contraparte e metodologia compatível.

variação_em_graus
Diferença entre as posições ordinais da escala. O sinal deve seguir convenção única: positivo
para melhora ou piora, conforme parametrização explícita.

pd_atual / pd_anterior
PDs associadas às duas avaliações.

delta_pd
PD atual menos PD anterior; pode ser apresentado em pontos percentuais e variação relativa.

direção_migração
MELHORA; ESTÁVEL; PIORA; DEFAULT; SEM_COMPARAÇÃO.

data_alteração
Data da nova avaliação ou da aprovação da mudança.


#### 6.5.1 Atualização manual do histórico e dados tardios

O histórico poderá receber informações inseridas posteriormente à competência a que se referem. O
registro deverá ser anexado à contraparte e, quando aplicável, à análise original, sem alteração destrutiva
da linha anterior. A visão atual será reconstruída por regras de vigência e status, e não pela simples
substituição do arquivo histórico.

Campo de controle
Finalidade
registro_manual_id
Identificador único da solicitação ou evento manual.
contraparte_id / analise_id
Entidade e análise afetadas; analise_id pode ser nulo em eventos cadastrais.
data_referencia_negocio
Competência, data-base ou período ao qual a informação pertence.
data_registro_sistema
Data e hora em que o dado foi efetivamente inserido.
tipo_evento / campo_afetado
Complementação, correção, atualização histórica, registro sem DF ou override.
valor_anterior / valor_novo
Valores preservados para reconstrução e comparação.

Uso interno — documento de planejamento

Página 15 de 37


---

<!-- Página 16 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

Campo de controle
Finalidade
motivo / evidência
Justificativa, documento de suporte, comunicação da contraparte ou fonte alternativa.
responsável / aprovador
Segregação entre inclusão e aprovação, conforme alçada.
vigência / status
Início, fim, expiração, APROVADO, REJEITADO, PENDENTE ou REVOGADO.
impacta_calculo
Indica se rating, PD, PE, vencimento, segmentação ou relatório deve ser recalculado.

### 6.6 Exposição, LGD e perda esperada

No escopo atual, a EAD será derivada da exposição positiva da Copel na base de MtM. A regra deverá ser
versionada para permitir futura inclusão de exposição potencial futura ou outros componentes.

EAD atual: EAD = max(MtM favorável à Copel, 0)

A data-base, o horizonte e o nível de agregação devem ser registrados em cada cálculo.


A LGD deverá ser armazenada antes e depois da consideração das garantias. A redução por garantia
deverá considerar elegibilidade, vigência, valor atualizado, alocação, haircut e limite de cobertura conforme
a metodologia aprovada.

Perda Esperada: PE = EAD × LGD × PD

PD, LGD e EAD utilizadas devem ser persistidas no próprio registro do cálculo, evitando dependência apenas de
tabelas vigentes.


Resultado
Campos mínimos

Componentes
PD utilizada; LGD bruta; LGD após garantias; EAD utilizada.

Valor
Perda esperada em reais; perda esperada percentual sobre EAD.

Referência
Competência; horizonte; data-base; data e hora do cálculo.

Metodologia
Versão da metodologia; parâmetros; regra de agregação; identificador do processamento.

Histórico
Uma linha por contraparte, competência, horizonte e versão do cálculo.


### 6.7 Garantias

Grupo
Campos mínimos

Identificação
garantia_id; CNPJ da contraparte; grupo econômico; contrato vinculado; tipo; modalidade.

Partes
Garantidor/emissor; CNPJ do garantidor; instituição financeira; beneficiário.

Valores
Valor nominal; valor atualizado; moeda; data da avaliação; percentual de cobertura.

Vigência
Data de início; vencimento; status; elegibilidade; data da última validação.






Uso interno — documento de planejamento

Página 16 de 37


---

<!-- Página 17 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

### 6.8 Taxa de risco de crédito

Taxa de Risco de Crédito: Taxa de Risco = Perda Esperada ÷ Notional Total
O notional deve ser apurado para o mesmo conjunto de operações, competência e horizonte utilizados na perda
esperada. Divisão por zero deve resultar em nulo e alerta de qualidade.


- 
EAD: exposição positiva no horizonte definido.
- 
LGD: percentual de perda após garantias elegíveis.
- 
PD ajustada: probabilidade de default utilizada no cálculo.
- 
Notional total: volume financeiro consolidado da carteira ou contraparte no mesmo recorte.
- 
Resultado: taxa em percentual, com data-base, versão e nível de agregação registrados.

### 6.9 Indicadores financeiros

Indicador
Fórmula / observação

Liquidez corrente
Ativo Circulante ÷ Passivo Circulante.

Cobertura patrimonial
Ativo Total ÷ Passivo Total.

Margem líquida
Lucro Líquido ÷ Receita Operacional Líquida.

Cobertura de pessoal
(Receita de Energia - Custo de Energia) ÷ Despesa com Pessoal.

MtM sobre PL
MtM Total ÷ Patrimônio Líquido.

Distribuição de resultados
(Dividendos + JCP) ÷ Lucro Líquido.

Capital circulante líquido
Ativo Circulante - Passivo Circulante.

FCO/ROL
Fluxo de Caixa Operacional ÷ Receita Operacional Líquida.

ROA
Lucro Líquido ÷ Ativo Total médio, conforme metodologia.

ROE
Lucro Líquido ÷ Patrimônio Líquido médio, conforme metodologia.


### 6.10 Alertas de negócio

Cada alerta deverá possuir código, severidade, regra, mensagem, data de detecção, campo afetado, valor
observado, limite esperado, status de tratamento, responsável e evidência de encerramento.

- 
Análise vencida ou próxima do vencimento.
- 
Contraparte em blacklist ou com situação cadastral irregular.
- 
Rating deteriorado acima do número de graus definido.
- 
Aumento relevante da PD ou da perda esperada.
- 
MtM positivo sem análise vigente.
- 
CNPJ ou grupo econômico divergente entre fontes.
- 
Campo obrigatório ausente ou falha de reconciliação.
- 
Metodologia, configuração ou fonte desatualizada.
- 
Contrato vigente no Denodo sem posição correspondente no MtM.
- 
Posição no MtM sem contrato corrente identificado no Denodo.
- 
Consumidor com pelo menos 5 MWm sem análise detalhada de DF vigente.
- 
Consumidor abaixo de 5 MWm sem consulta de bureau válida.
- 
Mudança de faixa de volume que exija revisão da metodologia de análise.
- 
Volume de enquadramento não identificado ou divergente entre fontes.
- 
Demonstração financeira não recebida para segmento que exige análise detalhada.
- 
Carga manual pendente de aprovação ou sem evidência obrigatória.
- 
Exceção/override por ausência de DF próxima do vencimento ou expirada.
- 
Informação manual divergente da fonte oficial posteriormente recebida.

Uso interno — documento de planejamento

Página 17 de 37


---

<!-- Página 18 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

- 
Atualização retroativa com impacto em cálculos ou publicações anteriores.

Uso interno — documento de planejamento

Página 18 de 37


---

<!-- Página 19 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 7. Saídas, relatórios e interfaces

### 7.1 Visão consolidada atual por contraparte

A visão atual deverá conter uma linha por contraparte no nível definido para consumo — individual ou
consolidado — e referências para as tabelas históricas. Ela não substituirá os fatos históricos.

- 
Cadastro e identificação: contraparte_id, CNPJ, CNPJ raiz, CNPJ BBCE, código CCEE, grupo,
controladora, situação cadastral e CNAE.
- 
Análise: data, validade, próxima análise, dias para vencimento, faixa, situação, tipo, responsável e parecer.
- 
Risco: rating, PD, classe, score, EAD, LGD, perda esperada, taxa de risco e data-base.
- 
Garantias: valor vigente, valor elegível, cobertura e vencimento mais próximo.
- 
Alertas: quantidade, maior severidade, código principal e status de tratamento.
- 
Rastreabilidade: análise_id, cálculo_id, run_id e data da última atualização.
- 
Contrato: possui_contrato_corrente_copel, quantidade de contratos, datas de vigência e fonte oficial.
- 
Segmentação: tipo de contraparte, comercializadora pura/de grupo, volume de enquadramento, faixa de 5
MWm, metodologia exigida e fonte.
- 
Conciliação: possui_posicao_mtm e status_conciliacao_contrato_mtm.
- 
Origem da análise, situação da DF, motivo da ausência, indicador de dado manual, status da aprovação e
validade da exceção.

### 7.2 Relatórios previstos

Saída
Grão e finalidade

Relatório de crédito atual
Uma linha por contraparte, com a situação vigente e principais indicadores.

Relatório analítico
Detalhamento por contraparte, incluindo histórico, DF, scores, garantias, exposição
e alertas.

Relatório de vencimentos
Contrapartes por faixa de vencimento, responsável, status e prioridade.

Histórico de análises
Uma linha por análise e versão, preservando toda a evolução.

Matriz de transição
Contagem e percentual de migrações entre ratings por período e segmento.

Histórico de perda esperada
Uma linha por contraparte, competência, horizonte e versão metodológica.

Relatório de garantias
Garantias vigentes, vencidas, elegíveis, alocadas e cobertura da exposição.

Pendências e inconsistências
Erros de classificação, extração, integração, qualidade e reconciliação.

Relatório de auditoria
Runs, arquivos processados, regras aplicadas, exceções, aprovações e
publicações.

Relatório de contratos correntes
Uma linha por contrato e competência, com vigência, volume, status e vínculo com
a contraparte.

Relatório de enquadramento de consumidores
Uma linha por consumidor, volume de referência, faixa, metodologia exigida, fonte e
pendências.

Reconciliação Denodo × MtM
Contratos e posições conciliados, contrato sem MtM, MtM sem contrato e
divergências de chave.

Histórico de atualizações manuais
Uma linha por solicitação/evento e detalhe de campo, com competência, evidência,
aprovação, vigência e impacto.





Uso interno — documento de planejamento

Página 19 de 37


---

<!-- Página 20 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

### 7.3 Arquivo de entrada para cálculo de limites

Delimitação de responsabilidade
O BD Crédito não calculará o limite. Sua responsabilidade será gerar e versionar um arquivo Excel de
entrada, com dados consistentes e rastreáveis, para o sistema externo de cálculo de limites.


Campo mínimo
Origem / observação

Nome do agente
Cadastro consolidado da contraparte.

CNPJ
CNPJ padronizado com 14 dígitos.

Tipo
Tipo/segmento metodológico da contraparte.

Patrimônio líquido
Última DF válida vinculada à análise.

Patrimônio líquido ajustado
Valor informado ou calculado conforme metodologia externa; regra e fonte devem
ser identificadas.

Rating
Rating vigente aprovado.

Data da DF
Data-base da demonstração financeira utilizada.

Identificadores de controle
contraparte_id, análise_id, data de geração, versão do layout e run_id.

possui_contrato_corrente_copel
Derivado do Denodo na data de referência.
volume_enquadramento_mwm
Maior volume mensal simultâneo utilizado na segmentação.
segmento_metodologico
Comercializadora pura/de grupo ou consumidor por faixa de volume.
fonte_volume / data_referencia_volume
Rastreabilidade da classificação utilizada.
situacao_df / motivo_ausencia_df
Indica se a DF foi recebida e, em caso negativo, a justificativa formal.
origem_analise / indicador_dado_manual
Permite identificar uso de carga manual ou exceção nos dados exportados.
validade_excecao
Data de expiração de eventual decisão provisória por ausência de DF.

### 7.4 Requisitos das saídas

- 
Publicação atual e histórica separadas.
- 
Arquivos com timestamp, versão de layout e hash quando aplicável.
- 
Controle de latest somente como ponteiro; a versão histórica não pode ser sobrescrita.
- 
Metadados de geração e totalizadores em arquivo de manifesto.
- 
Power BI deve consumir preferencialmente a camada relacional, não arquivos-fonte.

Uso interno — documento de planejamento

Página 20 de 37


---

<!-- Página 21 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 8. Modelo relacional de dados

A camada relacional deverá utilizar dimensões, fatos, configurações e tabelas de controle. Cada fato deve
possuir grão explícito e chaves para reconstrução do resultado.

### 8.1 Dimensões principais

Objeto
Grão / conteúdo

dim_contraparte
Uma linha por contraparte lógica, com chaves cadastrais e atributos de identidade.

dim_estabelecimento
Uma linha por CNPJ completo, permitindo matriz e filiais.

dim_grupo_economico
Uma linha por grupo econômico e controladora final.

dim_layout_ficha
Uma linha por tipo, subtipo e versão de layout.

dim_rating
Uma linha por rating, escala, ordem, classe e PD de referência.

dim_classificacao
Domínios de classificação, status e severidade.

dim_tempo
Calendário para análises, competências, vencimentos e snapshots.

dim_metodologia
Versões de modelos de PD, LGD, perda esperada e taxa de risco.

dim_segmento_metodologico
Domínio e vigência das categorias de comercializadoras e consumidores.
dim_status_contrato
Status contratuais padronizados e indicador de contrato ativo.

### 8.2 Fatos principais

Objeto
Grão / conteúdo

fato_documento_credito
Uma linha por documento processado e versão.

fato_campo_extraido
Uma linha por documento, campo e ocorrência, com valor e localização de origem.

fato_analise_credito
Uma linha por análise de contraparte.

fato_score_rating_pd
Uma linha por análise e versão do modelo.

fato_demonstracao_financeira
Uma linha por contraparte, data da DF e versão da ficha.

fato_indicador_financeiro
Uma linha por análise, indicador e metodologia.

fato_exposicao_mtm
Uma linha por contraparte, contrato/operação, período e data-base.

fato_garantia
Uma linha por garantia e avaliação/vigência.

fato_perda_esperada
Uma linha por contraparte, competência, horizonte e versão de cálculo.

fato_migracao_rating
Uma linha por par de avaliações consecutivas.

fato_alerta_credito
Uma linha por ocorrência de alerta.

fato_exportacao_limites
Uma linha por contraparte e versão do arquivo exportado.

fato_contrato_corrente
Uma linha por contrato, contraparte, competência, versão da fonte e data de referência.
fato_volume_contratado_mensal
Volume simultâneo consolidado por contraparte e competência.
fato_enquadramento_metodologico
Uma linha por contraparte e data de avaliação, com volume, fonte, regra e segmento.
fato_reconciliacao_contrato_mtm
Uma linha por contrato/posição reconciliada ou divergência identificada.

fato_evento_manual_credito
Uma linha por solicitação manual, contraparte, tipo de evento, competência, aprovação
e vigência.

fato_campo_manual_credito
Uma linha por evento e campo alterado ou complementado, com valor anterior, novo,
evidência e impacto.

Uso interno — documento de planejamento

Página 21 de 37


---

<!-- Página 22 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

### 8.3 Configurações e tabelas de controle

Objeto
Finalidade

cfg_prazo_analise
Prazo de validade e próxima análise por tipo/segmento.

cfg_layout_campos
Campos esperados, obrigatórios, localização e pesos de classificação.

cfg_mapeamento_campos
Mapeamentos origem-destino e conversões de domínio.

cfg_escala_rating
Ordem, classe, PD e vigência da escala.

cfg_regras_alerta
Condições, severidade, mensagem e vigência dos alertas.

cfg_parametros_lgd
Haircuts, elegibilidade e regras de redução por garantia.

ctl_run_pipeline
Execuções do pipeline, versão do código, ambiente e status.

cfg_status_contrato_ativo
Define quais status do Denodo representam vínculo contratual corrente.
cfg_regra_enquadramento_volume
Define limiar, operador, horizonte e critério de agregação dos 5 MWm.
cfg_campos_carga_manual
Define campos permitidos, tipo, obrigatoriedade, impacto e alçada de aprovação.
cfg_motivos_ausencia_df
Domínio de motivos, evidências requeridas e tratamento por segmento.
cfg_validade_excecao_sem_df
Prazo máximo, alertas e regra de expiração de exceções sem DF.
ctl_aprovacao_manual
Solicitação, responsável, aprovador, decisão, timestamp, comentário e evidência.

Uso interno — documento de planejamento

Página 22 de 37


---

<!-- Página 23 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 9. Arquitetura de dados, ambientes e repositórios

### 9.1 Ambientes

Ambiente
Uso

DEV
Construção, testes exploratórios, novos layouts, novas regras e dados simulados/amostrais.

TEST
Homologação integrada com amostras representativas, reconciliações e evidências de aceite.

PRD
Processamento oficial, repositório definitivo, relatórios e arquivos consumidos pela área.


### 9.2 Estrutura física sugerida

C:\Users\c050777\RepositorioGit\BDC\Script\arquivos_python\
S:\COM_CPR\00_BI\
├── BDC_HML\
│   ├── dev\
│   │   ├── ENTRADAS\
│   │   ├── SAIDAS\
│   │   └── LOGS\
│   └── test\
│       ├── ENTRADAS\
│       ├── SAIDAS\
│       └── LOGS\
└── BDC\
    ├── ENTRADAS\
    ├── SAIDAS\
    └── LOGS


O código-fonte permanecerá exclusivamente no repositório Git. DEV, TEST e PRD manterão apenas dados,
configurações, controles, saídas e logs.

### 9.3 Estrutura das entradas

ENTRADAS\
├── configs\
├── control\
│   ├── schemas\
│   ├── layouts\
│   ├── mappings\
│   ├── rules\
│   └── quality\
├── fichas\
│   ├── comercializadoras\pendentes|processadas|rejeitadas\
│   └── consumidores\pendentes|processadas|rejeitadas\
├── atualizacoes_manuais\
│   ├── pendentes\
│   ├── aprovadas\
│   └── rejeitadas\
├── salesforce\
├── contratos_denodo\
├── mtm\
├── garantias\
├── blacklist\
└── receita


Uso interno — documento de planejamento

Página 23 de 37


---

<!-- Página 24 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

### 9.4 Camadas de dados

Camada
Responsabilidade

Staging
Cópia temporária e controle de concorrência antes da ingestão.

Bronze
Evidência bruta imutável, snapshots e metadados de ingestão.

Silver
Classificação, extração, padronização, validação e integração técnica.

Relational
Dimensions, facts, configs e control em formato estruturado para consumo.

Gold
Visões de negócio, históricos, alertas, relatórios e arquivos de interface.

Output
Arquivos finais distribuídos, manifestos e versões publicadas.


### 9.5 Estrutura das saídas e logs

SAIDAS\
├── staging\
├── bronze\
│   ├── documentos_raw\
│   ├── atualizacoes_manuais_raw\
│   └── snapshots_fontes\
├── silver\
│   ├── fichas_padronizadas\
│   ├── atualizacoes_manuais_padronizadas\
│   └── fontes_integradas\
├── relational\
│   ├── dimensions\
│   ├── facts\
│   ├── configs\
│   └── control\
├── gold\
└── output\
LOGS\
├── runner\
├── ingestion\
├── classification\
├── extraction\
├── manual_updates\
├── quality\
├── relational\
├── gold\
└── audit


Uso interno — documento de planejamento

Página 24 de 37


---

<!-- Página 25 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 10. Arquitetura modular do código

A organização do código deverá refletir os domínios funcionais e as camadas de dados, evitando módulos
genéricos excessivamente grandes.

app\
cli\
common\
control\
staging\
storage\
silver\
domain\
├── fichas\
├── contrapartes\
├── credito\
├── salesforce\
├── mtm\
├── cadastro\
├── carga_manual\
└── auditoria\
relational\
gold\
services\
tests


Pacote
Responsabilidade

app / cli
Bootstrap, contexto de execução, comandos e orquestração.

common / control
Configurações, caminhos, hashing, schemas, domínios, logging e utilitários.

staging / storage
Movimentação segura, persistência Bronze e controle de arquivos.

silver
Padronização técnica, validações e qualidade.

domain.fichas
Classificação, extração, validação por layout e reprocessamento.

domain.contrapartes
Identidade, matching, grupos e visão única.

domain.credito
Análise, rating, PD, exposição, LGD, perda esperada, taxa e alertas.

domain.auditoria
Eventos, reconciliações, evidências, overrides, publicações e relatórios de controle.

relational / gold
Construção de tabelas relacionais e saídas finais.

tests
Testes unitários, integração, regressão de layouts e reconciliação.

domain.carga_manual
Validação do template/formulário, dupla data, aprovação, complementação histórica,
correção, ausência de DF e recálculo impactado.

Uso interno — documento de planejamento

Página 25 de 37


---

<!-- Página 26 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 11. Auditoria, rastreabilidade e controles

A auditoria deverá ser tratada como requisito estrutural, e não como um relatório acrescentado ao final. O
sistema deve registrar evidências suficientes para responder: qual foi a fonte, quem ou o que alterou o dado,
qual regra foi aplicada, quais parâmetros estavam vigentes, quando o resultado foi publicado e se houve
exceção ou aprovação manual.

### 11.1 Objetivos de auditoria

- 
Comprovar a integridade e a origem dos documentos e dados processados.
- 
Reproduzir cálculos históricos mesmo após alteração de regras ou configurações.
- 
Identificar todas as transformações entre fonte, Silver, relacional e Gold.
- 
Demonstrar a completude e a conciliação das cargas.
- 
Controlar intervenções manuais, exceções, aprovações e reprocessamentos.
- 
Evidenciar segregação de ambientes, acessos e mudanças promovidas para produção.
- 
Permitir análise de causa-raiz em erros e divergências.

### 11.2 Identificadores de rastreabilidade

Identificador
Finalidade

run_id
Identifica uma execução ponta a ponta ou uma etapa do pipeline.

documento_id
Identifica de forma permanente o arquivo original ingerido.

source_snapshot_id
Identifica a versão/snapshot de uma fonte externa ou tabela.

contraparte_id
Identifica a contraparte lógica consolidada.

analise_id
Identifica uma avaliação de crédito específica.

calculo_id
Identifica uma execução de PD, LGD, perda esperada ou taxa de risco.

regra_id / regra_versao
Identifica a regra aplicada e seu período de vigência.

config_snapshot_id
Identifica o conjunto exato de parâmetros utilizados.

publicacao_id
Identifica um conjunto de saídas oficialmente publicado.

override_id
Identifica uma intervenção manual controlada.


### 11.3 Linhagem no nível do campo

Para os campos extraídos de fichas, a trilha ideal deverá registrar documento_id, aba, célula ou intervalo,
rótulo encontrado, valor bruto, valor padronizado, transformação aplicada, confiança e versão do extrator.
Para APIs e tabelas, deverá registrar objeto, chave do registro, campo de origem, data de consulta e
snapshot.

Campo de auditoria
Exemplo

origem_tipo
EXCEL; SALESFORCE; DENODO_CONTRATOS; API_RECEITA; MTM; GARANTIA; CONFIG;
CARGA_MANUAL.

origem_localizacao
Aba “Rating”, célula F18; objeto Account, campo Rating__c.

valor_bruto
“12,5%”; “A-”; “31/12/2025”.

valor_padronizado
0,125; A_MINUS; 2025-12-31.

transformação
Remoção de máscara; conversão percentual; mapeamento de domínio.

qualidade
VALIDO; ALERTA; BLOQUEADO; PENDENTE.

versões
extrator 2.1; mapping 4; schema 3; config snapshot 20260721_01.

Uso interno — documento de planejamento

Página 26 de 37


---

<!-- Página 27 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA


### 11.4 Eventos que devem ser auditados

- 
Descoberta, cópia, ingestão, classificação, extração, validação, integração e publicação de arquivos.
- 
Mudança de status de documento, contraparte, análise, alerta e garantia.
- 
Alteração de vínculo entre CNPJ, contraparte e grupo econômico.
- 
Cálculo ou recálculo de rating, PD, EAD, LGD, perda esperada e taxa de risco.
- 
Aplicação de nova versão de layout, regra, escala de rating ou parâmetro.
- 
Criação, aprovação, alteração, expiração ou revogação de override.
- 
Publicação e substituição do ponteiro latest.
- 
Falhas, reprocessamentos, cancelamentos e retomadas.
- 
Registro de indisponibilidade de DF, motivo, evidência de solicitação e exceção concedida.

### 11.5 Tabelas de controle e auditoria

Tabela
Conteúdo mínimo

ctl_run_pipeline
run_id, ambiente, comando, início/fim, usuário/serviço, versão Git, status e totais.

ctl_documento
documento_id, hashes, caminhos, fonte, status, datas e run_id.

ctl_evento_processamento
evento, entidade, status anterior/novo, timestamp, responsável e mensagem.

ctl_campo_origem
Campo destino, localização, valor bruto, valor padronizado, transformação e
confiança.

ctl_validacao_qualidade
Regra de qualidade, severidade, valor, resultado, tolerância e ação.

ctl_regra_aplicada
regra_id, versão, entradas, parâmetros, saída e cálculo_id.

ctl_reconciliacao
Origem/destino, métrica, valor esperado, observado, diferença, tolerância e status.

ctl_override
Campo/resultado alterado, valor anterior/novo, motivo, evidência, solicitante,
aprovador e vigência.

ctl_publicacao
publicacao_id, arquivos/tabelas, hashes, quantidade de linhas, data, aprovador e
status.

ctl_mudanca_config
Configuração alterada, antes/depois, solicitante, aprovação, ambiente e vigência.

ctl_aprovacao_manual
registro_manual_id, solicitante, aprovador, decisão, data/hora, comentário, alçada,
evidência e vigência.

### 11.6 Reconciliações obrigatórias

Controle
Comparação / critério

Arquivos
Quantidade descoberta = processados + pendentes + rejeitados; hashes únicos.

Extração
Campos obrigatórios esperados versus extraídos por layout.

Contrapartes
Cobertura de CNPJ entre fichas, Salesforce, Receita e MtM; divergências identificadas.

MtM
Soma por data-base e contraparte na Silver/Gold igual à fonte, dentro da tolerância.

Garantias
Valor nominal, atualizado, elegível e alocado; nenhuma alocação acima do valor
disponível.

Perda esperada
Recalcular amostras e verificar PE = EAD × LGD × PD.

Taxa de risco
Verificar mesma competência/horizonte entre PE e notional.

Histórico
Nenhuma análise anterior removida; contagem de versões e datas coerentes.

Publicação
Quantidade de linhas, soma de métricas-chave e hash do arquivo publicado.

Contratos
Contratos vigentes e volumes na Silver/Gold iguais ao snapshot Denodo, dentro da
tolerância.

Denodo × MtM
Classificar cada vínculo como CONCILIADO, CONTRATO_SEM_MTM,
MTM_SEM_CONTRATO ou DIVERGENTE.
Enquadramento
Recalcular o maior volume mensal e validar segmento e metodologia da análise.

Uso interno — documento de planejamento

Página 27 de 37


---

<!-- Página 28 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

Controle
Comparação / critério

Carga manual
Quantidade de solicitações = aprovadas + rejeitadas + pendentes; campos publicados
devem possuir evidência e aprovação válidas.

### 11.7 Overrides e ajustes manuais

Override é uma alteração controlada de um resultado calculado ou de uma classificação automática,
realizada por autoridade competente. O sistema não deverá permitir edição direta silenciosa de campos
calculados.

Requisito
Definição

Justificativa
Motivo padronizado e descrição obrigatória.

Evidência
Parecer, ata, aprovação, e-mail, documento ou chamado vinculado.

Alçada
Solicitante e aprovador distintos quando exigido pela política.

Vigência
Data de início, fim e condição de expiração.

Valores
Valor calculado original e valor final aprovado.

Escopo
Contraparte, análise, campo, metodologia e período afetados.

Reversibilidade
Possibilidade de revogação sem apagar o histórico.

Apresentação
Relatórios devem indicar que o valor possui override vigente.


#### 11.7.1 Distinção entre carga manual e override

Carga manual é a inclusão, complementação ou correção controlada de um dado de origem. Override é a
alteração de um resultado calculado, classificação ou decisão metodológica. Uma carga manual poderá
existir sem override; porém, quando for utilizada para alterar rating, PD, validade, segmentação ou
elegibilidade contrariando a regra padrão, também deverá gerar um override vinculado.

Requisito da carga manual
Definição
Dupla temporalidade
data_referencia_negocio e data_registro_sistema devem ser mantidas separadamente.
Evidência
Documento, e-mail, ata, consulta externa ou justificativa formal que suporte a informação.
Segregação
Quem inclui não deve aprovar campos sensíveis ou exceções, conforme alçada.
Imutabilidade
Correções geram nova versão; o registro anterior permanece consultável.
Expiração
Dados provisórios e exceções sem DF devem possuir vigência e alerta de vencimento.

Conflito posterior
Quando a fonte oficial chegar, comparar, reconciliar e encerrar ou substituir a informação manual por
novo evento.

### 11.8 Gestão de mudanças

- 
Código versionado em Git com commit identificado no run de produção.
- 
Layouts, mappings, schemas, regras e configurações com número de versão e vigência.

### 11.10 Retenção e imutabilidade

- 
Preservar documentos Bronze, metadados, análises, cálculos, configurações e publicações.
- 
Não apagar registros de negócio para corrigir erro; gerar nova versão ou evento de estorno/correção.
- 
Registrar hash de documentos e arquivos publicados para comprovação de integridade.
- 
Separar backups operacionais de evidências de auditoria.


Uso interno — documento de planejamento

Página 28 de 37


---

<!-- Página 29 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 12. Operação, monitoramento e segurança

### 12.1 Monitoramento operacional

- 
Painel de execução com último run por fonte, status, duração e volume processado.
- 
Alertas para ausência de arquivo esperado, falha de API, mudança de layout e atraso de atualização.
- 
Indicadores de documentos pendentes/rejeitados e tempo de resolução.
- 
Monitoramento de crescimento do repositório, espaço em disco e retenção.
- 
Registro de SLA por etapa e tempo total de processamento.

### 12.2 Segurança e privacidade

- 
Acesso por menor privilégio às pastas, configurações e relatórios.
- 
Credenciais e tokens fora do código e dos arquivos versionados.
- 
Mascaramento ou restrição de dados pessoais quando não necessários ao uso analítico.
- 
Logs sem exposição indevida de segredos, tokens ou conteúdo sensível.
- 
Criptografia e controles de rede conforme padrões corporativos disponíveis.
- 
Registro e revisão periódica de acessos privilegiados.

### 12.3 Estratégia de falha e reprocessamento

- 
Processamento idempotente: executar novamente não deve duplicar fatos válidos.
- 
Reprocessamento vinculado ao run e documento originais.
- 
Publicação atômica: somente trocar o latest após conclusão e reconciliação bem-sucedidas.
- 
Quarentena para arquivos problemáticos, sem interromper fontes independentes quando permitido.
- 
Mensagens de erro com etapa, entidade, código e ação recomendada.

Uso interno — documento de planejamento

Página 29 de 37


---

<!-- Página 30 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 13. Roadmap e critérios de aceite

### 13.1 Roadmap recomendado

Fase
Entregas

Fase 1 — Fundação documental
Repositórios, ambientes, ingestão, hash, classificação, extratores de fichas, metadados, logs e pendências.

Fase 2 — Visão de contraparte
Cadastro consolidado, Receita, Salesforce inicial, contratos Denodo, volume, histórico de análises, carga
manual controlada e relatório de vencimentos.

Fase 3 — Motor de crédito
Scores, rating, PD, MtM/EAD, garantias, LGD, perda esperada, taxa de risco e histórico.

Fase 4 — Auditoria e publicação
Reconciliações, carga manual/overrides, linhagem, camada relacional, Gold, Power BI e arquivo para limites.

Fase 5 — Evoluções
Matriz de transição avançada, integrações adicionais, automações de workflow e eventual migração para
GCP.


### 13.2 Critérios de aceite funcional

- 
Classificar corretamente os layouts homologados e encaminhar desconhecidos para pendência.
- 
Preservar o arquivo original e registrar hash e metadados.
- 
Extrair os campos obrigatórios com rastreabilidade de origem.
- 
Consolidar uma contraparte sem duplicidade indevida e preservar conflitos entre fontes.
- 
Calcular corretamente datas de próxima análise e faixas de vencimento.
- 
Preservar histórico de análises, rating, PD e perda esperada.
- 
Gerar PE e taxa de risco com componentes persistidos e fórmula reproduzível.
- 
Publicar relatórios e arquivo de limites com totais conciliados.
- 
Registrar overrides, versões, aprovações e mudanças em produção.
- 
Impedir publicação quando controles críticos falharem.

### 13.3 Decisões pendentes para detalhamento

Tema
Decisão necessária

Escala de rating
Ordem oficial, sinal da variação em graus, classes e PDs associadas.

PD
Metodologia por segmento, horizonte, ajuste e regra de validade.

LGD
Valores brutos, elegibilidade de garantias, haircuts e alocação.

EAD
Confirmação do uso exclusivo de MtM positivo e futuras parcelas de exposição.

Notional
Fonte, granularidade e recorte para taxa de risco.

Prazos
Prazo de próxima análise por tipo de contraparte e fonte analítica.

Precedência
Fonte oficial de grupo econômico, rating aprovado e dados cadastrais.

Retenção
Prazo corporativo para documentos, logs e cálculos históricos.

Alçadas
Quem pode aprovar análises, exceções, overrides e publicações.

Power BI
Modelo semântico, frequência de atualização e requisitos de acesso.

Regra dos 5 MWm
Confirmar se o critério oficial é maior ou igual a 5 MWm, o horizonte observado e o
tratamento de contratos futuros.
Volume contratual
Confirmar campo, unidade, sazonalização e forma de agregação no relatório Denodo.
Contrato corrente
Homologar os status ativos, regras de rescisão e datas que definem vigência.

Fallback de fonte
Definir quando Salesforce, MtM ou exceção manual podem substituir temporariamente o
Denodo.

Carga manual histórica
Definir template/formulário, campos permitidos, alçadas, evidências obrigatórias e prazo de
aprovação.

Ausência de DF
Definir quais informações podem ser registradas sem DF, se podem sustentar decisão
vigente e qual a validade máxima da exceção.

Retroatividade
Definir quando uma inclusão tardia recalcula histórico, perda esperada e relatórios já
publicados.

Uso interno — documento de planejamento

Página 30 de 37


---

<!-- Página 31 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## 14. Especificação operacional: entradas, processamentos e saídas

Esta seção traduz o planejamento funcional em rotinas executáveis. Cada fonte deverá possuir contrato de
dados, snapshot, validações, regra de atualização, tabela de destino e evidência de processamento. A
sequência padrão será: entrada, Bronze, padronização Silver, integração, regra de negócio, controles,
camada relacional, Gold e publicação.

### 14.1 Matriz operacional das entradas

Entrada
Fonte / frequência
Conteúdo principal
Destino inicial

Fichas de comercializadoras
Pasta de entrada; por evento
Identidade, DF, indicadores, scores, rating, PD e parecer.
Bronze documental e Silver de
fichas.
Fichas de consumidores ≥ 5
MWm
Pasta de entrada; por evento
DF detalhada, indicadores quantitativos, rating e PD.
Bronze documental e Silver
consumidores com DF.
Bureau de consumidores < 5
MWm
Arquivo/API ou ficha; por evento
Score, restritivos, resultado, rating/classe, PD e validade.
Bronze/Silver bureau.

Relatório de contratos Denodo
Consulta/arquivo; diária
Contrato, vigência, status, competência, operação e
volume em MWm.

Bronze contratos e Silver
contratos padronizados.
Salesforce
API/arquivo; diária
Account, Chamado, Cotação e Contrato.
Bronze/Silver Salesforce.

MtM do risco de mercado
Arquivo/tabela; diária após
pipeline de risco

MtM, notional, contrato, operação, competência e data-
base.
Bronze/Silver MtM.

Receita/Gov.br
API; novo CNPJ e atualização
periódica
Situação cadastral, CNAE, natureza jurídica e endereço.
Bronze/Silver cadastro externo.

Garantias e blacklist
Arquivo/sistema; diária ou por
evento
Vigência, valor, elegibilidade, motivo e aprovação.
Bronze/Silver de controles de
crédito.

Configurações
Arquivos homologados; por
mudança

Domínios, regras, limiares, layouts, PD, LGD, alertas e
tolerâncias.
Snapshot de configuração.

Atualizações manuais
Template/formulário; por evento

Bronze manual e Silver de
eventos/campos manuais.

Complementação histórica, correção, ausência de DF,
valor anterior/novo, competência, motivo, evidência,
solicitante e aprovação.

### 14.2 Carga manual histórica e ausência de DF

12. Receber o arquivo-padrão ou submissão do formulário e gerar registro_manual_id.
13. Preservar o arquivo ou submissão original na Bronze, com hash, solicitante e data de recebimento.
14. Validar CNPJ, competência, tipo de evento, campos, domínios, motivo e evidência.
15. Classificar a solicitação como complementação, correção, atualização histórica, registro sem DF ou

override.
16. Submeter à alçada exigida e impedir publicação enquanto o status estiver pendente.
17. Criar novo evento e detalhes de campo na camada relacional, sem alterar fisicamente o histórico anterior.
18. Recalcular apenas os objetos impactados e gerar nova publicação quando necessário.
19. Quando a fonte oficial for recebida, reconciliar, encerrar a vigência provisória e preservar o histórico das

duas informações.

Cenário
Tratamento operacional

Empresa não envia DF
Registrar situacao_df = NAO_RECEBIDA, motivo, data da solicitação ou cobrança e evidência. Não
preencher saldos ou indicadores com zero.
Informação alternativa disponível
Inserir somente campos permitidos, identificando a fonte alternativa e o grau de confiabilidade.

Necessidade de manter decisão vigente
Criar exceção/override com alçada, validade máxima e alerta; o registro manual isolado não substitui a
DF.

DF recebida posteriormente
Ingerir a DF normalmente, comparar com a informação provisória e criar nova versão da análise ou
cálculo.

Correção de histórico
Usar competência passada e data atual de registro; nunca retroceder artificialmente a data de
conhecimento do sistema.

### 14.3 Derivação contratual e enquadramento

20. Carregar e preservar o snapshot do relatório de contratos do Denodo.
21. Padronizar CNPJ, contrato, status, datas, operação, competência, unidade e volume.
22. Aplicar o domínio homologado de contratos ativos e identificar contratos correntes na data de referência.
23. Expandir ou consolidar contratos por competência mensal, sem somar períodos diferentes.
24. Somar volumes simultâneos por contraparte e competência e calcular o maior volume mensal no horizonte.
25. Classificar consumidores pelo limiar parametrizado e selecionar a metodologia exigida.
26. Conciliar contratos com Salesforce e posições do MtM, gerando status e alertas.
27. Preservar o volume, a fonte, a data e a versão da regra em cada análise de crédito.

Indicador derivado
Regra

possui_contrato_corrente_copel
Verdadeiro quando existir ao menos um contrato com status ativo, início ≤ data de referência
e fim ≥ data de referência, sem cancelamento/rescisão vigente.
volume_contratado_mensal_mwm
Soma dos volumes dos contratos simultaneamente válidos na mesma competência.
volume_enquadramento_mwm
Maior volume contratado mensal no horizonte definido pela política.
possui_pelo_menos_5_mwm
volume_enquadramento_mwm ≥ limiar configurado, atualmente proposto em 5 MWm.
segmento_metodologico
Determinado pelo tipo da contraparte e, para consumidores, pela faixa de volume.

Uso interno — documento de planejamento

Página 31 de 37


---

<!-- Página 32 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

Indicador derivado
Regra
status_conciliacao_contrato_mtm
Resultado da comparação entre contratos correntes e posições existentes na base de MtM.

### 14.4 Fluxo diário integrado

28. Abrir run_id e carregar as versões homologadas de código, schemas, mappings e configurações.
29. Processar novas fichas, consultas de bureau e solicitações de atualização manual, preservando

documentos e submissões na Bronze.
30. Carregar Salesforce, contratos Denodo, Receita, blacklist, garantias e MtM.
31. Executar padronização técnica e controles de completude, validade e unicidade.
32. Consolidar a identidade da contraparte, grupo econômico e vínculos entre CNPJ, AccountId, código CCEE

e contratos.
33. Calcular contrato corrente, volume mensal, maior volume e segmento metodológico.
34. Validar compatibilidade entre o segmento e a análise recebida: DF detalhada ou bureau.
35. Atualizar análise, rating, PD, histórico, situação da DF, eventos manuais aprovados e vencimentos.
36. Calcular EAD a partir do MtM, aplicar a metodologia de garantias/LGD e calcular perda esperada e taxa de

risco.
37. Executar reconciliações Denodo × MtM, cargas manuais × fontes oficiais, fontes × Silver e Silver × Gold.
38. Publicar camada relacional, relatórios Gold, arquivo para limites, manifesto e evidências de auditoria.
39. Encerrar o run com status, totais, erros, alertas, publicacao_id e hashes dos artefatos.

### 14.5 Matriz de processamentos e persistência

Processamento
Entradas
Saída persistida / grão
Classificação de documento
Arquivo, catálogo de layouts e campos-chave
fato_documento: uma linha por documento e versão.
Extração de ficha
Documento classificado e mapping
fato_campo_extraido e fatos de análise/DF.
Contrato corrente
Denodo e cfg_status_contrato_ativo
fato_contrato_corrente por contrato e competência.

Volume contratado
Contratos correntes por competência
fato_volume_contratado_mensal por contraparte e
competência.
Enquadramento
Tipo de contraparte, volume e cfg_regra_enquadramento
fato_enquadramento_metodologico por análise/data.
Conciliação contratual
Denodo, Salesforce e MtM
fato_reconciliacao_contrato_mtm por chave comparada.
Rating e PD
Ficha/bureau, scores, modelo e overrides
fato_rating_pd por análise e versão.

Exposição e PE
MtM, PD, LGD e garantias
fato_exposicao_mtm e fato_perda_esperada por
competência/horizonte.
Publicação
Tabelas validadas e controles aprovados
ctl_publicacao, snapshots relacionais e Gold.

Carga manual histórica
Template/formulário, evidência, alçada e regras de campos

fato_evento_manual_credito e
fato_campo_manual_credito; uma nova versão ou evento
por aprovação.

### 14.6 Saídas operacionais

Saída
Grão
Finalidade

Cadastro atual de contrapartes
Uma linha por CNPJ
Identidade, grupo, situação cadastral, contrato corrente, volume,
segmento e análise vigente.
Base de contratos correntes
Contrato × competência
Evidenciar vigência, volume, operação e fonte.
Base de enquadramento
Contraparte × data de referência
Demonstrar por que a análise exigida é DF detalhada ou bureau.
Relatório de vencimentos
Contraparte × análise
Priorizar renovações e controlar validade.

Relatório analítico
Contraparte com histórico
Apresentar cadastro, DF/bureau, rating, PD, exposição, garantias, PE e
auditoria.
Reconciliação Denodo × MtM
Contrato/posição × data-base
Identificar ausência, divergência e inconsistência de chave.
Matriz de transição
Rating origem × destino × período
Acompanhar migração de risco.

Arquivo para sistema de limites
Contraparte × data de referência
Fornecer PL, rating, PD, data da DF, contrato, volume e segmento; não
calcular limite.

Pendências e qualidade
Ocorrência
Direcionar correção de documento, fonte, vínculo, volume ou
metodologia.
Auditoria
Run, campo, cálculo e publicação
Permitir reconstrução ponta a ponta de qualquer resultado.

Base de atualizações manuais
Evento × campo × competência
Evidenciar dados tardios, correções, ausência de DF, aprovações,
vigência e impacto nos resultados.

### 14.7 Frequência e dependências

Rotina
Frequência sugerida
Dependência / observação

Fichas e bureau
Por evento ou várias vezes ao dia
Não depende da carga diária completa; publicação pode
aguardar validações.
Contratos Denodo
Diária
Deve ocorrer antes do enquadramento de consumidores.

Salesforce
Diária
Utilizado em cadastro, workflow e fonte alternativa de
volume/cotação.

MtM
Diária após risco de mercado
Deve ocorrer antes de EAD, perda esperada e reconciliação
contratual.
Receita
Novo CNPJ e atualização mensal/trimestral
Respeitar limites e disponibilidade da API.
Garantias e blacklist
Diária ou por evento
Mudanças relevantes devem disparar recálculo.
Gold e arquivo para limites
Diária e sob demanda
Somente após controles críticos aprovados.
Matriz de transição
Mensal
Usa histórico imutável de avaliações.

Atualizações manuais
Por evento
Publicação depende de validação, evidência e aprovação;
campos impactados podem exigir recálculo.

Uso interno — documento de planejamento

Página 32 de 37


---

<!-- Página 33 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

### 14.8 Critérios de bloqueio operacional

- 
Contrato ou volume sem CNPJ válido não poderá ser utilizado para enquadramento automático.
- 
Consumidor com volume igual ou superior ao limiar não poderá receber análise apenas de bureau, salvo
override aprovado e vigente.
- 
Consumidor abaixo do limiar não poderá ser publicado sem bureau válido, quando essa for a metodologia
exigida.
- 
Comercializadora de grupo não poderá ser publicada sem análise individual; a informação consolidada do
grupo não a substitui.
- 
Divergência crítica entre Denodo e MtM deverá bloquear os cálculos afetados, mas não necessariamente
toda a carteira.
- 
Na indisponibilidade de uma fonte, o uso de snapshot anterior ou fonte alternativa deverá seguir regra
parametrizada, com alerta e data de expiração.
- 
Atualização manual pendente, rejeitada ou sem evidência não poderá compor a visão oficial.
- 
Registro manual de ausência de DF não satisfaz a exigência de análise detalhada; eventual manutenção de
decisão requer override aprovado e vigente.
- 
Campos financeiros não recebidos deverão permanecer nulos com status apropriado, nunca preenchidos
com zero por conveniência.
- 
Correção retroativa que altere rating, PD, perda esperada ou arquivo de limites deverá gerar nova versão
de cálculo ou publicação e manter a anterior.

Uso interno — documento de planejamento

Página 33 de 37


---

<!-- Página 34 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## Apêndice A — Domínios mínimos

Domínio
Valores iniciais sugeridos

status_analise
VIGENTE; PROXIMA_VENCIMENTO; VENCIDA; EM_RENOVACAO; SUSPENSA.

tipo_analise
DF_COMPLETA; BUREAU; EXTRAORDINARIA; REVISAO_BUREAU.

status_documento
DESCOBERTO; EM_STAGING; INGERIDO; CLASSIFICADO; EXTRAIDO; VALIDADO;
PUBLICADO; PENDENTE; REJEITADO.

direcao_migracao
MELHORA; ESTAVEL; PIORA; DEFAULT; SEM_COMPARACAO.

severidade_alerta
INFORMATIVO; BAIXO; MEDIO; ALTO; CRITICO.

status_alerta
ABERTO; EM_TRATAMENTO; RESOLVIDO; ACEITO; CANCELADO.

status_garantia
VIGENTE; PROXIMA_VENCIMENTO; VENCIDA; CANCELADA; NAO_ELEGIVEL.

Contrato
possui_contrato_corrente_copel; quantidade_contratos; primeira_vigencia;
ultima_vigencia; data_referencia_contrato; fonte_contrato.

Segmentação
tipo_contraparte; subtipo_comercializadora; volume_enquadramento_mwm;
possui_pelo_menos_5_mwm; segmento_metodologico; fonte_volume.
Conciliação contratual
possui_posicao_mtm; status_conciliacao_contrato_mtm; data_ultima_reconciliacao.
tipo_contraparte
COMERCIALIZADORA; CONSUMIDOR.

segmento_metodologico

COMERCIALIZADORA_PURA; COMERCIALIZADORA_GRUPO;
CONSUMIDOR_GE_5_MWM_DF; CONSUMIDOR_LT_5_MWM_BUREAU;
NAO_ENQUADRADO.

status_conciliacao_contrato_mtm
CONCILIADO; CONTRATO_SEM_MTM; MTM_SEM_CONTRATO;
DIVERGENCIA_CNPJ; DIVERGENCIA_CONTRATO; SEM_DADOS.
fonte_volume
DENODO_CONTRATOS; SALESFORCE_COTACAO; MTM; EXCECAO_MANUAL.

tipo_evento_manual
COMPLEMENTACAO; CORRECAO; ATUALIZACAO_HISTORICA;
REGISTRO_SEM_DF; OVERRIDE.
status_aprovacao_manual
PENDENTE; APROVADO; REJEITADO; REVOGADO; EXPIRADO.
situacao_df
RECEBIDA; EM_VALIDACAO; INCOMPLETA; NAO_RECEBIDA; NAO_APLICAVEL.

motivo_ausencia_df
NAO_ENVIADA_PELA_CONTRAPARTE; NAO_DISPONIVEL; ATRASO_PUBLICACAO;
DISPENSA_APROVADA; OUTRO.

origem_registro
FICHA; BUREAU; SALESFORCE; DENODO; MTM; RECEITA; CARGA_MANUAL;
CALCULADO.

Uso interno — documento de planejamento

Página 34 de 37


---

<!-- Página 35 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## Apêndice B — Códigos iniciais de alerta

Código
Descrição

ANA_001
Análise vencida.

ANA_002
Análise vence dentro da faixa crítica configurada.

CAD_001
CNPJ com situação cadastral irregular.

CAD_002
Divergência de CNPJ ou grupo econômico entre fontes.

RAT_001
Deterioração de rating acima do limite configurado.

PD_001
Aumento relevante da PD.

EXP_001
Exposição positiva sem análise vigente.

GAR_001
Garantia vencida ou próxima do vencimento.

GAR_002
Cobertura abaixo do mínimo definido.

QLT_001
Campo obrigatório ausente.

QLT_002
Reconciliação fora da tolerância.

DOC_001
Layout não reconhecido ou confiança insuficiente.

CTR_001
Contrato corrente no Denodo sem posição correspondente no MtM.
CTR_002
Posição no MtM sem contrato corrente identificado no Denodo.
VOL_001
Volume de enquadramento não identificado.
VOL_002
Divergência relevante de volume entre fontes.
SEG_001
Consumidor com pelo menos 5 MWm sem análise detalhada de DF.
SEG_002
Consumidor abaixo de 5 MWm sem bureau válido.
SEG_003
Mudança de faixa de volume exige revisão da metodologia.
GRP_001
Comercializadora de grupo sem grupo econômico ou controladora final identificados.
DF_001
Demonstração financeira não recebida para segmento que exige análise detalhada.
MAN_001
Carga manual pendente de aprovação.
MAN_002
Carga manual sem evidência obrigatória ou com campo não permitido.
MAN_003
Informação manual divergente da fonte oficial.
MAN_004
Atualização retroativa exige recálculo ou republicação.
EXC_001
Exceção ou override por ausência de DF próxima do vencimento ou expirada.

Uso interno — documento de planejamento

Página 35 de 37


---

<!-- Página 36 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## Apêndice C — Dicionário mínimo da visão atual

Grupo
Campos principais

Identidade
contraparte_id; CNPJ; CNPJ raiz; nome; tipo; grupo; controladora; código CCEE; CNPJ BBCE.

Cadastro
situação Receita; data atualização; CNAE; setor; matriz/filial.

Análise
analise_id; data análise; data DF; aprovação; validade; próxima análise; dias; faixa; situação;
responsável.

Rating/PD
rating público; rating Copel; classe; scores; PD calculada; PD ajustada; modelo e validade.

Exposição
data-base; MtM positivo; EAD; notional.

Garantias/LGD
valor nominal; valor elegível; cobertura; LGD bruta; LGD após garantia.

Perda esperada
PE em reais; PE percentual; taxa de risco; competência; horizonte; cálculo_id.

Alertas
quantidade; severidade máxima; código principal; status.

Auditoria
documento_id; run_id; config_snapshot_id; publicacao_id; data atualização.

Atualização manual/DF
situacao_df; motivo_ausencia_df; origem_analise; indicador_dado_manual;
registro_manual_id; status_aprovacao; validade_excecao.

Uso interno — documento de planejamento

Página 36 de 37


---

<!-- Página 37 de 37 -->
BD CRÉDITO  |  PLANEJAMENTO FUNCIONAL E DE AUDITORIA

## Encerramento

Este planejamento consolida o escopo atual do BD Crédito e estabelece a auditoria como componente
transversal da solução. O detalhamento técnico seguinte deverá transformar os objetos, campos, regras e
controles aqui definidos em schemas, contratos de dados, catálogo de layouts, testes e backlog de
implementação.

Próximo artefato recomendado
Elaborar o modelo de dados detalhado e o catálogo operacional de interfaces, incluindo o template de atualização
manual histórica. Cada campo deverá possuir chave, tipo, obrigatoriedade, origem, regra de transformação,
frequência, regra de qualidade, alçada, evidência, dupla temporalidade e impacto em cálculos ou publicações.


Uso interno — documento de planejamento

Página 37 de 37


---
