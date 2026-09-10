# Relatório de Auditoria Arquitetural - BD Crédito

## 1. Resumo Executivo
A esteira de Engenharia de Dados atingiu maturidade estrutural. A separação estrita entre as camadas Bronze, Silver e Gold está operacional e governada por *Schemas JSON* restritos, garantindo que a ingestão bloqueie esquemas anômalos. O grave vazamento de falsos positivos na `fato_garantia` (o "Bug de 1970") foi erradicado, limpando mais de 17.000 alertas indevidos. A infraestrutura base para *Human-in-the-Loop* (Fase 4) foi implantada com sucesso, provada pela captura inédita de anomalias `MAN_004`. No entanto, restam GAPs técnicos pontuais de negócio: falhas de insumo (Rating *None*) estão derrubando o Motor CPURA para CNPJs específicos e a interface de visualização (Fase 5) oculta valores nulos, além de carecer de atualização técnica (warnings de depreciação do Streamlit). O pipeline é resiliente, mas o motor matemático ainda é frágil a dados ausentes.

---

## 2. Fase 0 — Inventário Real

| Módulo do Planejamento | Existe no código? | Arquivo(s) evidência | Observação |
| :--- | :--- | :--- | :--- |
| **Extrator (Silver)** | Sim | `src/app/comercializadoras/`, `src/app/consumidores/` | Lendo planilhas Excel em `SAIDAS/staging`. |
| **Contratos (Schemas)** | Sim | `ENTRADAS/control/schemas/` | Ativos e rigorosamente validados. Sincronizador criado (`sync_metadata.py`). |
| **Motor de Risco** | Parcial | `src/domain/credito/pd_motor.py` | Operacional, mas falhando sem *fail-safe* para insumos nulos (ex: `PdInputValidationError`). |
| **Alertas de Negócio** | Sim | `src/relational/facts/fato_alertas.py` | Cobertura parcial (ANA, SEG, GAR, CTR). Falsos positivos do 1970 contidos. |
| **Carga Manual** | Sim | `src/relational/facts/fato_alertas_manuais.py` | Implantado e atrelado no `main.py` antes da consolidação Gold. |
| **Orquestrador** | Sim | `main.py` | Orquestra de blocos 1 a 4. |

*(Nota: Volumes processados — ~1.300 Fichas Comercializadoras e ~600 Consumidores extraídos com sucesso na última run verificada, Gold consolidando ~21.000 registros)*

---

## 3. Fase 1 — Estrutura vs Planejamento

| Camada Data Lakehouse | Planejado | Implementado Real | Aderência |
| :--- | :--- | :--- | :--- |
| **Bronze** | Arquivos Imutáveis | Cópias em formato binário Excel (`SAIDAS/bronze/`). | 100% |
| **Silver** | Normalização sem Regras | Schemas aplicam casting; `fato_analise_credito` isolado do extrator. | 100% |
| **Relational** | Star Schema | Fatos e Dimensões geradas em parquet na pasta `SAIDAS/relational/facts`. | 100% |
| **Gold** | Visão Master | Master Join construído em `Visao_Operacional_BDC_LATEST.parquet`. | 100% |

---

## 4. Fase 2 — Bronze→Silver

**Mapeamento de Conformidade:**
*   **Comercializadoras:** Sucesso absoluto após a sincronização do `master_catalog_comercializadoras.json` que incorporou as colunas de metadados (`INTEGRIDADE_EXTRAIDA_PERCENTUAL`, `load_mode`, etc).
*   **Consumidores:** Sucesso atingido. Colunas de linhagem exclusivas (`campos_obrigatorios`, `confianca_classificacao`, etc) foram adicionadas na *whitelist* do validador.

**Achados Críticos:** Nenhum estrutural. O pipeline ingere arquivos, converte tipos e persiste em Parquet obedecendo rigidamente os Schemas.

---

## 5. Fase 3 — Alertas

| Alerta | Descrição | Status de Disparo (Última Run) | Taxa de Falsos Positivos |
| :--- | :--- | :--- | :--- |
| **GAR_001** | Garantia Vencida | 19.221 alertas. | **0%** (Bug 1970 resolvido; datas refletem vencimentos genuínos anteriores ao ano-base do sistema de 2026). |
| **CTR_001** | Denodo vs MtM | 1.079 alertas. | Baixa. Conciliação flagrando ausências físicas. |
| **PD_ERR_001**| Erro no Motor PD | 442 alertas. | Preciso. Captura falhas de cálculo (ex: Rating None). |

**Conclusão Fase 3:** O volume de 19.221 alertas `GAR_001` faz sentido para uma base consolidadora de 21 mil registros históricos.

---

## 6. Fase 4 — Carga Manual

Checklist de Validação:
- [x] Lógica implementada em `fato_alertas_manuais.py` e isolada das regras de cálculo de crédito.
- [x] O script varre as Fichas Extraídas diretamente na Silver, e não na Gold.
- [x] Orquestrador `main.py` chama o serviço de Carga Manual antes do Master Join.
- [x] Alertas mapeados: `MAN_001`, `MAN_002`, `MAN_003`, `MAN_004`, `DF_001`.
- [x] **Evidência de Disparo:** 4 ocorrências do alerta `MAN_004` registradas no Terminal comprovam que o validador humano é acionado quando dados vitais (como PL) estão em branco.

*(Nota: Nenhum MAN_001/MAN_002 disparou porque a base simulada atual possui CNPJ e Datas preenchidos ou pre-mockados. O validador está funcionando corretamente e flagrou apenas os Patrimônios nulos).*

---

## 7. Fase 5 — visao_carteira.py (Frontend UX)

**Checklist:**
- [x] Todo campo exibido tem origem na Gold? **Sim**. (Verificado em `visao_carteira.py`, linha 41: `gold_dir = BASE_DIR / "SAIDAS" / "gold" / ...`).
- [ ] O frontend não mascara nulos? **Não**. (Achado de BUG: Linhas 58 e 61 convertem Ratings e Score nulos para string vazia `""`, escondendo a falha do usuário).
- [ ] Tratamento de tipos? **Parcial**. Ocorre filtragem estrita em `STATUS_CONTRATUAL` (apenas VIGENTE e FUTURO), ocultando silenciosamente qualquer contrato ENCERRADO.

**Achados/Sugestões Aditivas (Não são bugs impeditivos, exceto o mascaramento de nulos):**
1. O Streamlit emitiu Warning: ``Please replace `use_container_width` with `width`... `` (Depreciação prevista para 2025-12-31).
2. Adicionar badge/alerta visual na tabela quando houver "Sem análise", em vez de deixar células vazias enganosas.
3. Expor os alertas MAN_* numa aba própria de "Pendências de Carga Manual".

---

## 8. Lista Final Priorizada de Gaps (AÇÃO FUTURA)

| Severidade | Descrição do Gap | Evidência (Arquivo:Linha) | Próximo Passo Sugerido |
| :--- | :--- | :--- | :--- |
| **CRÍTICA** | **Quebra do Motor PD por Insumos Nulos (CPURA)**<br>O Motor está recebendo `Rating = None` para algumas contrapartes e falhando de forma ruidosa em vez de gerenciar o nulo no cálculo. | `main.py`:189<br> `src/domain/credito/pd_motor.py`:44 (`PdInputValidationError: Rating inválido para CPURA: None`) | Implementar cláusula de *fail-safe* ou conversão neutra no Motor CPURA para suportar ratings vazios em vez de `raise Exception`. |
| **ALTA** | **Mascaramento Visual de Dados Nulos**<br>A interface `visao_carteira.py` converte falhas de cálculo (None) em strings vazias, passando a falsa impressão de que a tabela está limpa, desobedecendo a seção 5.1. | `src/ui/views/visao_carteira.py`:58 e 61 | Remover `.strip()` cego sobre campos nulos; manter representação explícita de `Nulo` ou `Sem Dado`. |
| **MÉDIA** | **Streamlit deprecation warning**<br>O framework UX emitiu alertas vermelhos no terminal. | Log Terminal de Orquestração do `main.py` | Atualizar os parâmetros `use_container_width` nas views da interface. |
| **BAIXA** | **Ocultação de Contratos Encerrados**<br>O filtro principal da interface exclui agressivamente contratos que não sejam VIGENTES ou FUTUROS. | `src/ui/views/visao_carteira.py`:49 | Criar aba de "Histórico" ou filtro toggle no UI para contratos inativos. |

> **PERGUNTA FINAL DO AUDITOR:** 
> Devemos prosseguir para um **prompt de implementação separado**, com o escopo travado em atacar o item Crítico do Motor PD (Item 1 da Lista de Gaps)?
