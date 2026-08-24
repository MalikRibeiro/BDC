# CÓDIGO PARTE 2


---
## app_dashboard.py
Linhas: 75
Classes: -
Funções: -
```python
import streamlit as st
import pandas as pd
from pathlib import Path

# ==================================================
# CONFIGURAÇÕES
# ==================================================
st.set_page_config(page_title="BDC | Dashboard de Extração", layout="wide", page_icon="📄")

st.title("BD CRÉDITO | Dashboard de Extração de Fichas")

# Definição de caminhos
BASE_DIR = Path(r"C:\Users\C807951\Desktop\BDC")
BRONZE_DIR = BASE_DIR / "SAIDAS" / "bronze" / "fichas_comercializadoras_raw"
SILVER_DIR = BASE_DIR / "SAIDAS" / "silver" / "fichas_comercializadoras_extraidas"

# ==================================================
# 1. CAMADA BRONZE (Quantidade de Fichas Lidas)
# ==================================================
st.header("🗂️ Camada Bronze")
st.caption(f"Caminho: `{BRONZE_DIR}`")

qtd_fichas_bronze = 0
if BRONZE_DIR.exists():
    qtd_fichas_bronze = len([f for f in BRONZE_DIR.rglob("*") if f.is_file()])

st.metric(label="Quantidade de Fichas Lidas (Raw)", value=f"{qtd_fichas_bronze} arquivos")

st.divider()

# ==================================================
# 2. CAMADA SILVER (Tabela Extraída e Dados por Campo)
# ==================================================
st.header("⚙️ Camada Silver")
st.caption(f"Caminho: `{SILVER_DIR}`")

df_silver = pd.DataFrame()

if SILVER_DIR.exists():
    csv_files = list(SILVER_DIR.glob("*.csv"))
    if csv_files:
        df_list = []
        for p in csv_files:
            try:
                df = pd.read_csv(p, sep=';', on_bad_lines='skip', low_memory=False)
                df_list.append(df)
            except Exception as e:
                st.error(f"Erro ao ler {p.name}: {e}")
        
        if df_list:
            df_silver = pd.concat(df_list, ignore_index=True)

if not df_silver.empty:
    st.success(f"Foram extraídos {len(df_silver)} registros no total.")
    
    # 2.1 Tabela Completa (Fichas Extraídas)
    st.subheader("1. Tabela de Fichas Extraídas (fichas_comercializadoras_extraidas)")
    st.dataframe(df_silver, use_container_width=True)

    # 2.2 Dados Lidos para Cada Campo (Estatísticas de Preenchimento)
    st.subheader("2. Resumo de Dados Lidos para Cada Campo")
    
    # Montando a tabela de estatísticas dos campos
    resumo_campos = pd.DataFrame({
        "Campo Extraído": df_silver.columns,
        "Tipo de Dado": df_silver.dtypes.astype(str),
        "Total de Registros": len(df_silver),
        "Valores Preenchidos": df_silver.notna().sum().values,
        "% de Preenchimento": (df_silver.notna().mean().values * 100).round(2).astype(str) + "%"
    })
    
    st.dataframe(resumo_campos.reset_index(drop=True), use_container_width=True)

else:
    st.warning(f"Nenhum arquivo .csv encontrado no diretório Silver ({SILVER_DIR}).")
```


---
## main.py
Linhas: 220
Classes: PipelineStep
Funções: preparar_e_rodar_risco, preparar_dim_contraparte, preparar_fato_analise, main
```python
"""
main.py

Orquestrador principal para executar os pipelines do projeto BDC em sequência.
"""

import argparse
import sys
from pathlib import Path
from typing import Callable, NamedTuple, Any
from datetime import datetime
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.bootstrap import carregar_contexto 

# --- IMPORTS DOS SERVIÇOS ---
from cli import rodar_fichas_comercializadoras
from cli import rodar_fichas_consumidores

from domain.contratos.servico_contratos_denodo import processar_contratos_denodo
from domain.credito.servico_risco import rodar_pipeline_risco
from domain.credito.servico_fato_analise_credito import construir_fato_analise_credito
from domain.auditoria.servico_auditoria import registrar_inicio_pipeline, registrar_fim_pipeline
from domain.contrapartes.servico_enquadramento import calcular_enquadramento_consumidor
from domain.mtm.servico_mtm import inserir_dados_mtm
from domain.mtm.servico_denodo_mtm_reconciliacao import executar_reconciliacao_denodo_mtm
from domain.salesforce.servico_salesforce import inserir_dados_salesforce
from domain.salesforce.servico_salesforce_reconciliacao import executar_reconciliacao_fichas_salesforce
from domain.cadastro.servico_receita import inserir_dados_receita
from domain.garantias.servico_garantia import inserir_dados_garantias
from domain.carga_manual.servico_carga_manual import inserir_dados_carga_manual
from domain.credito.servico_override import processar_solicitacao_override
from gold.service_gold import exportar_visao_consolidada_gold
from domain.contrapartes.servico_dim_contraparte import criar_dim_contraparte
from domain.cadastro.servico_bureau import inserir_dados_bureau

def preparar_e_rodar_risco(context):
    mtm_path = context.path("silver") / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
    df_mtm = pd.read_parquet(mtm_path) if mtm_path.exists() else pd.DataFrame()
    if df_mtm.empty: return
        
    df_fichas = pd.DataFrame()
    for segmento_dir in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        seg_path = context.path("silver") / segmento_dir
        if seg_path.exists():
            parquets = list(seg_path.glob("*.parquet"))
            if parquets:
                df_seg = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg], ignore_index=True)
                
    df_mtm["CNPJ"] = df_mtm["CNPJ"].astype(str).str.zfill(14)
    df_exposicoes = df_mtm.copy()
    
    if not df_fichas.empty and "CNPJ" in df_fichas.columns:
        df_fichas["CNPJ"] = df_fichas["CNPJ"].astype(str).str.zfill(14)
        if "_VERSAO_REGISTRO" in df_fichas.columns:
            df_fichas = df_fichas.sort_values("_VERSAO_REGISTRO").drop_duplicates("CNPJ", keep="last")
        elif "DT_PROCESSAMENTO" in df_fichas.columns:
            df_fichas = df_fichas.sort_values("DT_PROCESSAMENTO").drop_duplicates("CNPJ", keep="last")
            
        cols_ficha = ["CNPJ"]
        if "PD_FINAL" in df_fichas.columns: cols_ficha.append("PD_FINAL")
        if "SEGMENTO_PD" in df_fichas.columns: cols_ficha.append("SEGMENTO_PD")
        df_exposicoes = pd.merge(df_exposicoes, df_fichas[cols_ficha], on="CNPJ", how="left")
        if "SEGMENTO_PD" in df_exposicoes.columns:
            df_exposicoes["SEGMENTO_METODOLOGICO"] = df_exposicoes["SEGMENTO_PD"]
            
    if "PD_FINAL" not in df_exposicoes.columns: df_exposicoes["PD_FINAL"] = None
    if "SEGMENTO_METODOLOGICO" not in df_exposicoes.columns: df_exposicoes["SEGMENTO_METODOLOGICO"] = "NAO_ENQUADRADO"
    return rodar_pipeline_risco(context, df_exposicoes=df_exposicoes)

def preparar_dim_contraparte(context):
    receita_path = context.path("silver") / "receita_silver" / "receita_cadastral_silver.parquet"
    enquadra_path = context.path("relational_configs") / f"enquadramento_consumidores_{datetime.now().strftime('%Y%m')}.csv"
    salesforce_path = context.path("silver") / "salesforce_silver" / "account" / "salesforce_account.parquet"
    
    df_receita = pd.read_parquet(receita_path) if receita_path.exists() else pd.DataFrame()
    df_seg = pd.read_csv(enquadra_path) if enquadra_path.exists() else pd.DataFrame()
    df_sf_account = pd.read_parquet(salesforce_path) if salesforce_path.exists() else pd.DataFrame()
    
    df_fichas = pd.DataFrame()
    for segmento_dir in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        seg_path = context.path("silver") / segmento_dir
        if seg_path.exists():
            parquets = list(seg_path.glob("*.parquet"))
            if parquets:
                df_seg_fichas = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg_fichas], ignore_index=True)

    from domain.contrapartes.servico_dim_contraparte import criar_dim_contraparte
    return criar_dim_contraparte(
        context, 
        df_silver_receita=df_receita, 
        df_silver_segmentacao=df_seg,
        df_silver_salesforce_account=df_sf_account,
        df_silver_fichas=df_fichas
    )
    
def preparar_fato_analise(context):
    df_fichas = pd.DataFrame()
    for segmento_dir in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        seg_path = context.path("silver") / segmento_dir
        if seg_path.exists():
            parquets = list(seg_path.glob("*.parquet"))
            if parquets:
                df_seg = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg], ignore_index=True)
                
    dim_path = context.path("relational_dimensions") / "dim_contraparte.parquet"
    if not dim_path.exists():
        dim_path = context.path("saidas") / "relational" / "dimensions" / "dim_contraparte.parquet"
    df_dim = pd.read_parquet(dim_path) if dim_path.exists() else pd.DataFrame()
    return construir_fato_analise_credito(context, df_silver_analises=df_fichas, df_dim_contraparte=df_dim)

# ==============================================================================
# PIPELINE OFICIAL
# ==============================================================================
class PipelineStep(NamedTuple):
    name: str
    func: Callable[[Any], Any]

PIPELINE_STEPS = [
    PipelineStep(name="Fichas Comercializadoras", func=lambda ctx: rodar_fichas_comercializadoras.main()),
    # PipelineStep(name="Fichas Consumidores", func=lambda ctx: run_fichas_consumidores.main()),
    # PipelineStep(name="Ingestão de Contratos (Denodo)", func=ingest_contratos_denodo),
    # PipelineStep(name="Enquadramento de Consumidores", func=lambda ctx: calcular_enquadramento_consumidor(datetime.now().strftime("%Y%m"), ctx)),
    # PipelineStep(name="Ingestão de MtM", func=ingest_mtm_data),
    # PipelineStep(name="Reconciliação Denodo x MtM", func=executar_reconciliacao_denodo_mtm),
    # PipelineStep(name="Ingestão do Salesforce", func=ingest_salesforce_data),
    # PipelineStep(name="Reconciliação Fichas x Salesforce", func=executar_reconciliacao_fichas_salesforce),
    # PipelineStep(name="Ingestão da Receita Federal", func=ingest_receita_data), 
    # PipelineStep(name="Ingestão de Bureau (RISK3)", func=ingest_bureau_data),
    # PipelineStep(name="Ingestão de Garantias", func=ingest_garantias_data),
    # PipelineStep(name="Pipeline de Risco de Crédito", func=preparar_e_rodar_risco),
    # PipelineStep(name="Dimensão Contraparte", func=preparar_dim_contraparte),
    # PipelineStep(name="Fato Análise de Crédito", func=preparar_fato_analise),
    # PipelineStep(name="Carga Manual (Log Eventos)", func=ingest_carga_manual),
    # PipelineStep(name="Solicitações de Override", func=processar_solicitacao_override),
    # PipelineStep(name="Visão Consolidada Gold", func=exportar_visao_consolidada_gold),
]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs-dir", default=str(Path("ENTRADAS") / "configs"))
    args = parser.parse_args()

    try:
        context = carregar_contexto(Path(args.configs_dir))
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao inicializar: {e}")
        return 1

    run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    control_dir = context.path("saidas") / "relational" / "control" if hasattr(context, "path") else Path("SAIDAS/relational/control")
    registro_inicio = registrar_inicio_pipeline(run_id, len(PIPELINE_STEPS), control_dir)

    exit_codes = []
    metricas_operacionais = {}
    
    for step in PIPELINE_STEPS:
        try:
            print(f"\n{'=' * 60}\nExecutando Etapa: {step.name}\n{'=' * 60}")
            import inspect
            sig = inspect.signature(step.func)
            if len(sig.parameters) > 0:
                result = step.func(context)
            else:
                result = step.func()
                
            if step.name == "Visão Consolidada Gold" and isinstance(result, dict):
                metricas_operacionais = result
                
            print(f"[OK] '{step.name}' concluído com sucesso.")
            exit_codes.append(0)
        except Exception as e:
            print(f"[ERRO] '{step.name}' falhou com a exceção: {e}")
            import traceback
            traceback.print_exc()
            exit_codes.append(1)
            
            if step.name in ["Ingestão de Contratos (Denodo)", "Reconciliação Denodo x MtM"]:
                print(f"[ERRO FATAL] Interrompendo pipeline devido à falha crítica em '{step.name}'.")
                return 1

    etapas_ok = sum(1 for code in exit_codes if code == 0)
    etapas_falha = sum(1 for code in exit_codes if code != 0)
    registrar_fim_pipeline(registro_inicio, etapas_ok, etapas_falha, control_dir)

    print(f"\n{'=' * 60}\nResumo Final da Execução do Pipeline:")
    for step, code in zip(PIPELINE_STEPS, exit_codes):
        print(f"  - {step.name}: {'OK' if code == 0 else f'FALHOU (código {code})'}")
        
    if metricas_operacionais:
        print(f"\n{'=' * 60}\nRESUMO DA VISÃO OPERACIONAL (MVP DO NEGÓCIO):\n{'=' * 60}")
        print(f"1. Total de Contrapartes detectadas:       {metricas_operacionais.get('total_contrapartes', 0)}")
        print(f"2. Possuem Contrato Vigente:               {metricas_operacionais.get('contrato_vigente', 0)}")
        print(f"3. Possuem Contrato Futuro:                {metricas_operacionais.get('contrato_futuro', 0)}")
        print(f"4. Possuem Análise de Crédito Vigente:     {metricas_operacionais.get('analise_vigente', 0)}")
        print(f"5. Contrato Vigente SEM Análise Vigente (Total): {metricas_operacionais.get('contrato_vig_sem_analise_vig', 0)} ⚠️")
        print(f"   ├─ Irregulares (>= 5 MWm sem DF): {metricas_operacionais.get('contrato_irregular_sem_df', 0)} 🚨 (Exposição Descoberta: R$ {metricas_operacionais.get('ead_descoberto', 0.0):,.2f})")
        print(f"   └─ Pendentes de Bureau (< 5 MWm): {metricas_operacionais.get('contrato_pendente_bureau', 0)} ⏳")
        print(f"6. Possuem Análise Vencida:                {metricas_operacionais.get('analise_vencida', 0)} ⏰ (Requer Revisão)")
        print(f"7. Possuem Ficha mas SEM Contrato:         {metricas_operacionais.get('ficha_sem_contrato', 0)}")
        print(f"8. Possuem Contrato mas NUNCA tiveram Ficha: {metricas_operacionais.get('contrato_sem_ficha', 0)} ⚠️")
        print(f"9. Cadastro Incompleto (Sem Receita Fed.): {metricas_operacionais.get('dados_incompletos', 0)}")
        
        pe_global = pd.read_parquet(context.path("relational_facts") / "fato_exposicao_risco_LATEST.parquet")["PE_REAIS"].sum()
        print(f"10. Perda Esperada (PE) Total da Carteira: R$ {pe_global:,.2f}")

    print(f"{'=' * 60}")

    return 1 if any(code != 0 for code in exit_codes) else 0

if __name__ == "__main__":
    sys.exit(main())
```


---
## src\app\config_builder.py
Linhas: 17
Classes: AppConfigBuilder
Funções: __init__, resolve_dict
```python
"""Builder programático para resolução de caminhos do sistema."""

from pathlib import Path
from typing import Any

class AppConfigBuilder:
    """Construtor responsável por aplicar o diretório base à topologia relativa."""
    
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir).resolve()

    def resolve_dict(self, paths_dict: dict[str, Any]) -> dict[str, str]:
        """Resolve todos os caminhos relativos de um dicionário contra o diretório base."""
        resolved = {}
        for key, relative_path in paths_dict.items():
            resolved[key] = str(self.base_dir / relative_path)
        return resolved
```


---
## src\app\consumidores\classificacao.py
Linhas: 188
Classes: ClassificacaoDocumental
Funções: _esta_vazio, _tem_demonstracoes_financeiras, _avaliar_confianca, classificar_consumidor, criar_classificacao_registro
```python
"""Serviço de classificação documental de consumidores.

Determina o tipo de análise exigida (detalhada ou simplificada)
com base no volume contratado, conforme planejamento v1.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


LIMIAR_MWM_DETALHADO = 5.0
VERSAO_REGRA_ATUAL = "v1.2"


@dataclass
class ClassificacaoDocumental:
    """Resultado da classificação documental de um consumidor."""

    tipo_consumidor: str                  # ">=5MWm" ou "<5MWm"
    presenca_df: bool                     # Se há demonstrações financeiras
    tipo_analise_exigida: str             # "detalhada" ou "simplificada"
    versao_layout: str                    # Versão do layout usado
    campos_obrigatorios: list[str]        # Lista dos campos obrigatórios
    confianca_classificacao: str          # "alta", "media", "baixa"
    compatibilidade_ficha_segmento: bool  # Se a ficha é compatível
    campos_df_nao_aplicavel: list[str]    # Campos marcados como NAO_APLICAVEL


# Campos financeiros que devem ser NAO_APLICAVEL em fichas simplificadas (<5 MWm)
CAMPOS_DF_COMPLETA = [
    "ATIVO_CIRCULANTE", "ATIVO_CIRCULANTE_FINANCEIRO", "ATIVO_TOTAL",
    "PASSIVO_CIRCULANTE", "PASSIVO_CIRCULANTE_FINANCEIRO",
    "PASSIVO_NAO_CIRCULANTE_FINANCEIRO", "PATRIMONIO_LIQUIDO",
    "LUCROS_ACUMULADOS", "RESERVA_DE_LUCROS", "VENDAS_LIQUIDAS",
    "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
]

CAMPOS_OBRIGATORIOS_DETALHADA = [
    "CNPJ", "EMPRESA", "DATA_DEMONSTRACAO_FINANCEIRA",
    "PATRIMONIO_LIQUIDO", "ATIVO_CIRCULANTE", "ATIVO_TOTAL",
    "PASSIVO_CIRCULANTE", "LUCRO_LIQUIDO",
    "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
    "FCO", "ROA", "ROE", "PROBABILIDADE_DEFAULT",
]

CAMPOS_OBRIGATORIOS_SIMPLIFICADA = [
    "CNPJ", "EMPRESA", "SCORE_BUREAU",
]


def _esta_vazio(value: Any) -> bool:
    """Indica se o valor deve ser tratado como vazio."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _tem_demonstracoes_financeiras(record: dict[str, Any]) -> bool:
    """Verifica se a ficha possui demonstrações financeiras preenchidas."""
    campos_presentes = 0
    for campo in CAMPOS_DF_COMPLETA:
        val = record.get(campo)
        if not _esta_vazio(val) and str(val).upper() != "NAO_APLICAVEL":
            campos_presentes += 1

    # Considera presente se pelo menos 50% dos campos DF estão preenchidos
    return campos_presentes >= len(CAMPOS_DF_COMPLETA) * 0.5


def _avaliar_confianca(
    record: dict[str, Any],
    tipo_consumidor: str,
    presenca_df: bool,
) -> str:
    """Avalia a confiança da classificação com base na consistência dos dados."""
    problemas = 0

    # Consumidor >=5 MWm sem DF é inconsistente
    if tipo_consumidor == ">=5MWm" and not presenca_df:
        problemas += 2

    # CNPJ ausente reduz confiança
    if _esta_vazio(record.get("CNPJ")):
        problemas += 1

    # Empresa ausente reduz confiança
    if _esta_vazio(record.get("EMPRESA")):
        problemas += 1

    if problemas == 0:
        return "alta"
    elif problemas == 1:
        return "media"
    else:
        return "baixa"


def classificar_consumidor(
    record: dict[str, Any],
    versao_layout: str,
    volume_mwm: float | None = None,
) -> ClassificacaoDocumental:
    """Classifica um consumidor conforme a metodologia aplicável.

    Args:
        record: Registro normalizado extraído da ficha.
        versao_layout: Versão do layout utilizado (e.g. "v3").
        volume_mwm: Volume contratado em MWm. Se None, tenta obter do record.

    Returns:
        ClassificacaoDocumental com todos os campos preenchidos.
    """
    # Determinar volume contratado
    if volume_mwm is None:
        volume_mwm = record.get("VOLUME_CONTRATADO")
        if volume_mwm is not None:
            try:
                volume_mwm = float(volume_mwm)
            except (ValueError, TypeError):
                volume_mwm = None

    # Classificar tipo de consumidor
    if volume_mwm is not None and volume_mwm >= LIMIAR_MWM_DETALHADO:
        tipo_consumidor = ">=5MWm"
    elif volume_mwm is not None and volume_mwm < LIMIAR_MWM_DETALHADO:
        tipo_consumidor = "<5MWm"
    else:
        # Sem volume informado: inferir pela presença de DF
        presenca_df = _tem_demonstracoes_financeiras(record)
        tipo_consumidor = ">=5MWm" if presenca_df else "<5MWm"

    presenca_df = _tem_demonstracoes_financeiras(record)

    # Tipo de análise exigida
    if tipo_consumidor == ">=5MWm":
        tipo_analise = "detalhada"
        campos_obrigatorios = list(CAMPOS_OBRIGATORIOS_DETALHADA)
    else:
        tipo_analise = "simplificada"
        campos_obrigatorios = list(CAMPOS_OBRIGATORIOS_SIMPLIFICADA)

    # Identificar campos que devem ser NAO_APLICAVEL em simplificada
    campos_nao_aplicavel: list[str] = []
    if tipo_consumidor == "<5MWm":
        for campo in CAMPOS_DF_COMPLETA:
            val = record.get(campo)
            if _esta_vazio(val) or str(val).upper() == "NAO_APLICAVEL":
                campos_nao_aplicavel.append(campo)

    # Compatibilidade entre ficha e segmento
    if tipo_consumidor == ">=5MWm":
        compativel = presenca_df
    else:
        # Para <5 MWm, basta ter score de bureau
        compativel = not _esta_vazio(record.get("SCORE_BUREAU"))

    confianca = _avaliar_confianca(record, tipo_consumidor, presenca_df)

    return ClassificacaoDocumental(
        tipo_consumidor=tipo_consumidor,
        presenca_df=presenca_df,
        tipo_analise_exigida=tipo_analise,
        versao_layout=versao_layout,
        campos_obrigatorios=campos_obrigatorios,
        confianca_classificacao=confianca,
        compatibilidade_ficha_segmento=compativel,
        campos_df_nao_aplicavel=campos_nao_aplicavel,
    )


def criar_classificacao_registro(
    classificacao: ClassificacaoDocumental,
) -> dict[str, Any]:
    """Converte a classificação documental em dict para o silver_record."""
    return {
        "tipo_consumidor": classificacao.tipo_consumidor,
        "presenca_df": classificacao.presenca_df,
        "tipo_analise_exigida": classificacao.tipo_analise_exigida,
        "versao_layout": classificacao.versao_layout,
        "campos_obrigatorios": ",".join(classificacao.campos_obrigatorios),
        "confianca_classificacao": classificacao.confianca_classificacao,
        "compatibilidade_ficha_segmento": classificacao.compatibilidade_ficha_segmento,
        "campos_df_nao_aplicavel": ",".join(classificacao.campos_df_nao_aplicavel),
    }
```


---
## src\app\context.py
Linhas: 96
Classes: AppContext
Funções: carregar_contexto, path, control_file
```python
"""Carregamento do contexto de execução do sistema BDC."""

from __future__ import annotations

import os
import sys
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app.config_builder import AppConfigBuilder
from common.json import ler_json
from common.validador import validar_esquema_json

logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class AppContext:
    app_config: dict[str, Any]
    config: dict[str, Any]
    paths: dict[str, Any]
    control_files: dict[str, Any]
    naming: dict[str, Any]

    def path(self, key: str) -> Path:
        return Path(self.paths[key])

    def control_file(self, key: str) -> Path:
        return Path(self.control_files[key])


def carregar_contexto(configs_dir: str | Path) -> AppContext:
    configs_path = Path(configs_dir)

    base_dir_env = os.getenv("BDC_BASE_DIR")
    if not base_dir_env:
        logger.critical("Variavel BDC_BASE_DIR nao encontrada no arquivo .env!")
        sys.exit(1)

    if not configs_path.exists():
        logger.critical("Diretório de configs não encontrado: %s", configs_path)
        sys.exit(1)

    app_config_path = configs_path / "app_config.json"
    config_path = configs_path / "config.json"

    if not app_config_path.exists() or not config_path.exists():
        logger.critical("Arquivos de configuração base não encontrados.")
        sys.exit(1)

    app_config = ler_json(app_config_path)
    config = ler_json(config_path)

    try:
        raw_paths = app_config["paths"]
        raw_control_files = app_config["control_files"]
    except KeyError as e:
        logger.critical("app_config.json malformado. Chave ausente: %s", e)
        sys.exit(1)

    # Resolve os caminhos usando o Builder
    builder = AppConfigBuilder(base_dir_env)
    resolved_paths = builder.resolve_dict(raw_paths)
    resolved_control_files = builder.resolve_dict(raw_control_files)

    schema_app_config_path = Path(resolved_control_files["schema_app_config"])
    schema_config_path = Path(resolved_control_files["schema_config"])

    if not schema_app_config_path.exists() or not schema_config_path.exists():
        logger.critical("Arquivos de schema de configuração não encontrados.")
        sys.exit(1)

    schema_app_config = ler_json(schema_app_config_path)
    schema_config = ler_json(schema_config_path)

    # Validação estrutural do JSON original (Fail-Fast)
    validar_esquema_json(app_config, schema_app_config, "app_config.json")
    validar_esquema_json(config, schema_config, "config.json")

    # Injeta valores resolvidos para manter coerência nos serviços
    app_config["base_dir"] = str(builder.base_dir)
    app_config["paths"] = resolved_paths
    app_config["control_files"] = resolved_control_files

    return AppContext(
        app_config=app_config,
        config=config,
        paths=resolved_paths,
        control_files=resolved_control_files,
        naming=app_config.get("naming", {}),
    )
```


---
## src\cli\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Comandos de linha do sistema BDC."""

```


---
## src\cli\rodar_fichas_comercializadoras.py
Linhas: 47
Classes: -
Funções: criar_analisador, main
```python
import argparse
import sys
from pathlib import Path

from src.app.bootstrap import aplicativo_bootstrap
from src.app.comercializadoras.orquestrador import process_fichas_comercializadoras


def criar_analisador() -> argparse.ArgumentParser:
    """
    Constrói o parser de argumentos de linha de comando para o script de comercializadoras.
    """
    parser = argparse.ArgumentParser(
        description="Processamento e geração de fichas de comercializadoras."
    )
    parser.add_argument(
        "--configs-dir",
        type=str,
        default=None,
        help=(
            "Caminho para o diretório de configurações (opcional). "
            "Se omitido, busca a variável de ambiente 'BDC_CONFIGS_DIR' "
            "ou utiliza o caminho relativo da raiz do projeto ('ENTRADAS/configs')."
        ),
    )
    return parser


def main() -> None:
    parser = criar_analisador()
    args = parser.parse_args()

    try:
        app_ctx = aplicativo_bootstrap(configs_dir=args.configs_dir)
        print(f"[INFO] Contexto da aplicacao inicializado a partir de: {app_ctx.path('configs')}")
        
        # Inicia o processamento real da fila
        summary = process_fichas_comercializadoras(app_ctx)
        print(f"[INFO] Resumo do processamento: {summary}")

    except Exception as exc:
        print(f"[ERRO] Falha na execucao: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```


---
## src\cli\rodar_fichas_consumidores.py
Linhas: 47
Classes: -
Funções: criar_analisador, main
```python
import argparse
import sys
from pathlib import Path

from src.app.bootstrap import aplicativo_bootstrap
from src.app.consumidores.orquestrador import processar_fichas_consumidores


def criar_analisador() -> argparse.ArgumentParser:
    """
    Constrói o parser de argumentos de linha de comando para o script de consumidores.
    """
    parser = argparse.ArgumentParser(
        description="Processamento e geração de fichas de consumidores."
    )
    parser.add_argument(
        "--configs-dir",
        type=str,
        default=None,
        help=(
            "Caminho para o diretório de configurações (opcional). "
            "Se omitido, busca a variável de ambiente 'BDC_CONFIGS_DIR' "
            "ou utiliza o caminho relativo da raiz do projeto ('ENTRADAS/configs')."
        ),
    )
    return parser


def main() -> None:
    parser = criar_analisador()
    args = parser.parse_args()

    try:
        app_ctx = aplicativo_bootstrap(configs_dir=args.configs_dir)
        print(f"[INFO] Contexto da aplicacao inicializado a partir de: {app_ctx.path('configs')}")
        
        # Inicia o processamento real da fila
        summary = processar_fichas_consumidores(app_ctx)
        print(f"[INFO] Resumo do processamento: {summary}")

    except Exception as exc:
        print(f"[ERRO] Falha na execucao: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```


---
## src\common\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
# Init para o pacote comum de domínios

```


---
## src\common\domain_normalizer.py
Linhas: 84
Classes: -
Funções: carregar_dicionarios_de_dominio, _normalizar_string_por_dicionario, aplicar_normalizacao_de_dominio
```python
"""Normalizador Semântico de Domínio.

Aplica padronização de valores baseado em dicionários de negócios unificados,
garantindo que strings equivalentes (ex: 'FITCH RATINGS' e 'FITCH') convirjam 
para a mesma chave primária definida pela área de risco.
"""
from __future__ import annotations

import logging
from typing import Any

from app.context import AppContext
from common.json import ler_json

logger = logging.getLogger(__name__)

def carregar_dicionarios_de_dominio(context: AppContext) -> dict[str, Any]:
    """Carrega o dicionário unificado de domínio."""
    # Como app_config.json pode não ter o caminho mapeado ainda, usamos um caminho fixo seguro
    dict_path = context.path("control_quality") / "domain_dictionaries.json"
    if not dict_path.exists():
        logger.warning("Dicionário de domínio não encontrado em %s", dict_path)
        return {}
    return ler_json(dict_path)

def _normalizar_string_por_dicionario(value: str, mapping: dict[str, list[str]]) -> str:
    """Procura a string bruta nas listas de apelidos do dicionário e retorna a chave oficial."""
    if not value or not isinstance(value, str):
        return value
        
    val_upper = value.strip().upper()
    
    # 1. Busca exata ou por substring segura
    for canonical_key, aliases in mapping.items():
        # Verifica se o próprio canonical key foi passado
        if val_upper == canonical_key.upper():
            return canonical_key
            
        for alias in aliases:
            if alias.upper() in val_upper or val_upper in alias.upper():
                return canonical_key
                
    return value

def aplicar_normalizacao_de_dominio(record: dict[str, Any], context: AppContext, log: logging.Logger = logger) -> dict[str, Any]:
    """
    Recebe o dicionário já com tipos primitivos (float, str, date) tratados pelo 
    field_type_normalizer e aplica as regras semânticas de negócio.
    """
    dictionaries = carregar_dicionarios_de_dominio(context)
    if not dictionaries:
        return record

    out = dict(record)

    # 1. Normalização de Agência
    if "AGENCIA" in out and out["AGENCIA"]:
        old_val = out["AGENCIA"]
        new_val = _normalizar_string_por_dicionario(old_val, dictionaries.get("AGENCIA", {}))
        out["AGENCIA"] = new_val
        if old_val != new_val:
            log.info("Semântica: AGENCIA normalizada de '%s' para '%s'", old_val, new_val)

    # 2. Normalização de Nota de Crédito (Rating)
    if "NOTA_CREDITO" in out and out["NOTA_CREDITO"]:
        old_val = out["NOTA_CREDITO"]
        new_val = _normalizar_string_por_dicionario(old_val, dictionaries.get("NOTA_CREDITO", {}))
        out["NOTA_CREDITO"] = new_val
        if old_val != new_val:
            log.info("Semântica: NOTA_CREDITO normalizada de '%s' para '%s'", old_val, new_val)

    # 3. Normalização de Auditor (Para extrair o peso da nota caso precise)
    # Se quiser que AUDITOR vire 'KPMG', mas também traga o PESO 'A':
    # Como o dicionário AUDITOR_PARA_NOTA é Key=Nota, Values=[Auditores]
    if "AUDITOR" in out and out["AUDITOR"]:
        old_val = out["AUDITOR"]
        nota_auditor = _normalizar_string_por_dicionario(old_val, dictionaries.get("AUDITOR_PARA_NOTA", {}))
        # O retorno será 'A', 'C', etc. 
        # Podemos criar um novo campo NOTA_AUDITORIA automaticamente!
        if nota_auditor in dictionaries.get("AUDITOR_PARA_NOTA", {}):
            out["NOTA_AUDITORIA"] = nota_auditor
            log.info("Semântica: Auditor '%s' gerou NOTA_AUDITORIA = '%s'", old_val, nota_auditor)

    return out

```


---
## src\common\excel.py
Linhas: 87
Classes: -
Funções: abrir_pasta, fechar_pasta, ler_celula, localizar_celula_por_regex
```python
"""Operações de leitura e fechamento seguro de workbooks Excel."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter


def abrir_pasta(path: str | Path) -> Any:
    """Abre um workbook Excel em modo somente leitura."""
    return load_workbook(
        filename=Path(path),
        data_only=True,
        read_only=True,
        keep_links=False,
    )

def fechar_pasta(workbook: Any) -> None:
    """Fecha um workbook ignorando falhas de liberação."""
    if workbook is None:
        return
    try:
        workbook.close()
    except Exception:
        return

def ler_celula(worksheet: Worksheet, cell_ref: str, return_meta: bool = False) -> Any:
    """Lê o valor de uma célula a partir de uma referência A1 (ex: 'A19')."""
    if not cell_ref or cell_ref == "0":
        return (None, None) if return_meta else None
    val = worksheet[cell_ref].value
    if return_meta:
        return val, {"aba": worksheet.title, "celula": cell_ref}
    return val

def localizar_celula_por_regex(
    worksheet: Worksheet,
    search_pattern: str,
    offset_col: int = 1,
    offset_row: int = 0,
    max_search_rows: int = 150,
    max_search_cols: int = 30,
    return_meta: bool = False
) -> Optional[Any]:
    """
    Varre a aba procurando uma expressão e retorna a célula adjacente.
    """
    if not search_pattern:
        return (None, None) if return_meta else None

    try:
        regex = re.compile(search_pattern, re.IGNORECASE)
    except re.error:
        return (None, None) if return_meta else None

    # OTIMIZAÇÃO CRÍTICA: Extrai o bloco de dados de uma vez só 
    # para evitar travamentos de O(N^2) no modo read_only=True.
    max_r = max_search_rows + max(0, offset_row)
    max_c = max_search_cols + max(0, offset_col)
    
    grid = []
    for row_vals in worksheet.iter_rows(min_row=1, max_row=max_r, min_col=1, max_col=max_c, values_only=True):
        grid.append(row_vals)

    for r_idx in range(min(max_search_rows, len(grid))):
        row_data = grid[r_idx]
        for c_idx in range(min(max_search_cols, len(row_data))):
            cell_value = row_data[c_idx]
            
            if cell_value and isinstance(cell_value, str):
                if regex.search(cell_value.strip()):
                    target_r = r_idx + offset_row
                    target_c = c_idx + offset_col
                    
                    if target_r < len(grid) and target_c < len(grid[target_r]):
                        val = grid[target_r][target_c]
                        if return_meta:
                            celula_ref = f"{get_column_letter(target_c + 1)}{target_r + 1}"
                            return val, {"aba": worksheet.title, "celula": celula_ref}
                        return val

    return (None, None) if return_meta else None
```


---
## src\common\hashing.py
Linhas: 21
Classes: -
Funções: arquivo_hash
```python
"""Geração de hash para arquivos do sistema BDC."""

from __future__ import annotations

import hashlib
from pathlib import Path


def arquivo_hash(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Calcula o hash SHA-256 de um arquivo."""
    file_path = Path(path)
    hasher = hashlib.sha256()

    with file_path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()

```


---
## src\common\json.py
Linhas: 14
Classes: -
Funções: ler_json
```python
"""Leitura e escrita de arquivos JSON do sistema BDC."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ler_json(path: str | Path) -> Any:
    """Lê um arquivo JSON e devolve seu conteúdo."""
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)

```


---
## src\common\paths.py
Linhas: 16
Classes: -
Funções: sanitizar_nome_da_pasta
```python
"""Funções utilitárias para nomes de paths e diretórios."""

from __future__ import annotations

import re


_INVALID_PATH_CHARS = r'[<>:"/\\|?*]+'


def sanitizar_nome_da_pasta(value: str) -> str:
    """Sanitiza um texto para uso seguro em nome de pasta."""
    cleaned = re.sub(_INVALID_PATH_CHARS, "_", value.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("._ ")

```


---
## src\common\servico_desduplicacao.py
Linhas: 70
Classes: -
Funções: tem_hash_duplicado, tem_chave_de_negocio_duplicada, virar_chave_de_negocio_no_historico
```python
"""Regras de deduplicação e atualização incremental do sistema."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def tem_hash_duplicado(
    history: list[dict[str, Any]],
    hash_value: str | None,
) -> bool:
    """Indica se o hash já foi processado anteriormente."""
    if not hash_value:
        return False

    return any(item.get("hash_arquivo") == hash_value for item in history)


def tem_chave_de_negocio_duplicada(
    history: list[dict[str, Any]],
    cnpj: str | None,
    data_demonstracao_financeira: str | None,
) -> bool:
    """Indica se a chave de negócio já existe com sucesso."""
    if not cnpj or not data_demonstracao_financeira:
        return False

    for item in history:
        if item.get("status_extracao") != "SUCESSO":
            continue

        if item.get("cnpj_extraido") != cnpj:
            continue

        if (
            item.get("data_demonstracao_financeira")
            != data_demonstracao_financeira
        ):
            continue

        return True

    return False


def virar_chave_de_negocio_no_historico(
    history: list[dict[str, Any]],
    manifest_record: dict[str, Any],
) -> None:
    """Atualiza o histórico em memória com a chave de negócio corrente.

    Em modo reprocess, MARCA registros anteriores como SUBSTITUIDO
    em vez de removê-los, preservando o histórico completo (§1.5 — imutabilidade).
    """
    load_mode = manifest_record.get("load_mode")
    cnpj = manifest_record.get("cnpj_extraido")
    data_df = manifest_record.get("data_demonstracao_financeira")

    if load_mode == "reprocess" and cnpj and data_df:
        for item in history:
            if (
                item.get("status_extracao") == "SUCESSO"
                and item.get("cnpj_extraido") == cnpj
                and item.get("data_demonstracao_financeira") == data_df
            ):
                item["status_extracao"] = "SUBSTITUIDO"
                item["dt_substituicao"] = datetime.now().isoformat(timespec="seconds")

    history.append(manifest_record)
```


---
## src\common\validador.py
Linhas: 18
Classes: -
Funções: validar_esquema_json
```python
import sys
import logging
from typing import Any
import jsonschema
from jsonschema.exceptions import ValidationError

logger = logging.getLogger(__name__)

def validar_esquema_json(instance: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    """Valida um dicionário contra um JSON Schema e aborta a execução em caso de falha."""
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except ValidationError as e:
        logger.critical(
            "Falha de validação estrutural no arquivo %s. Caminho do erro: %s. Motivo: %s",
            label, e.json_path, e.message,
        )
        sys.exit(1)
```


---
## src\control\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Carregadores de arquivos de controle do sistema BDC."""

```


---
## src\control\carregador_de_mapeamento.py
Linhas: 75
Classes: -
Funções: carregar_e_validar_mapeamento, mapeamento_de_carga_fichas_comercializadoras, mapeamento_de_carga_fichas_consumidores
```python
"""Carregamento e validação estrita dos mappings das fichas."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.context import AppContext
from common.json import ler_json
from common.validador import validar_esquema_json

def carregar_e_validar_mapeamento(
    mapping_path: Path,
    schema_path: Path,
    descricao: str,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega um mapping de fichas e valida estritamente contra seu JSON Schema."""
    try:
        logger.info("Carregando %s: %s", descricao, mapping_path)

        if not mapping_path.exists():
            raise FileNotFoundError(f"Arquivo de mapping não encontrado: {mapping_path}")
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_path}")

        # Leitura dos arquivos
        content = ler_json(mapping_path)
        schema = ler_json(schema_path)

        # Validação Estrita (Fail-Fast)
        validar_esquema_json(instance=content, schema=schema, label=descricao)

        if not isinstance(content, list):
            raise ValueError(f"O {descricao} deve ser uma lista.")

        logger.info(
            "%s carregado e validado com sucesso. Quantidade de registros: %s",
            descricao,
            len(content),
        )

        return content

    except Exception:
        logger.exception("Falha crítica ao carregar e validar %s", descricao)
        raise


def mapeamento_de_carga_fichas_comercializadoras(
    context: AppContext,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega e valida o mapping de fichas de comercializadoras."""
    return carregar_e_validar_mapeamento(
        mapping_path=context.control_file("mapping_fichas_comercializadoras"),
        schema_path=context.control_file("schema_mapping_fichas_comercializadoras"),
        descricao="Mapping de Comercializadoras",
        logger=logger,
    )


def mapeamento_de_carga_fichas_consumidores(
    context: AppContext,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega e valida o mapping de fichas de consumidores."""
    return carregar_e_validar_mapeamento(
        mapping_path=context.control_file("mapping_fichas_consumidores"),
        schema_path=context.control_file("schema_mapping_fichas_consumidores"),
        descricao="Mapping de Consumidores",
        logger=logger,
    )
```


---
## src\control\layout_catalog.py
Linhas: 128
Classes: -
Funções: validar_estrutura_do_layout, carregar_catalogo_de_layouts, carregar_layouts_comercializadoras, carregar_layouts_consumidores
```python
"""Carregamento e validação dos layouts de fichas."""

from __future__ import annotations

import sys
from typing import Any

from app.context import AppContext
from common.json import ler_json


def validar_estrutura_do_layout(layout: dict[str, Any], versao: str, logger: Any) -> None:
    """Valida se o layout possui a estrutura mínima para não quebrar o extrator."""
    if "field_map" not in layout:
        logger.critical("Layout '%s' inválido: chave 'field_map' ausente.", versao)
        sys.exit(1)
        
    for field_name, config in layout["field_map"].items():
        # Ignora campos que explicitamente não estão implementados nos layouts antigos (v1 ao v6)
        if not config.get("implemented", True):
            continue
            
        has_static = "value_cell" in config and config["value_cell"] not in [None, "0", 0]
        has_dynamic = "search_pattern" in config and config["search_pattern"] not in [None, ""]
        
        # Removemos o sys.exit(1) que estava quebrando os layouts antigos.
        # O extrator já está preparado para retornar None quando a âncora não existe.
        if not has_static and not has_dynamic:
            logger.debug(
                "Layout '%s' - Campo '%s': sem âncora estática ou dinâmica. Retornará vazio.", 
                versao, field_name
            )


def carregar_catalogo_de_layouts(
    catalog_path: str,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Carrega o catálogo consolidado de layouts."""
    try:
        if logger is not None:
            logger.info("Carregando catálogo de layouts: %s", catalog_path)

        catalog = ler_json(catalog_path)

        if logger is not None:
            logger.info("Catálogo de layouts carregado com sucesso.")

        return catalog

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar catálogo de layouts: %s", catalog_path)
        raise


def carregar_layouts_comercializadoras(
    context: AppContext,
    logger: Any | None = None,
) -> dict[str, dict[str, Any]]:
    """Carrega e valida os layouts de fichas de comercializadoras."""
    layouts: dict[str, dict[str, Any]] = {}

    try:
        if logger is not None:
            logger.info("Iniciando carga dos layouts de comercializadoras.")

        for version in range(1, 8):
            key = f"layout_ficha_comercializadora_v{version}"
            layout_path = context.control_file(key)

            layout_data = ler_json(layout_path)
            
            # Validação adaptada para não quebrar layouts antigos
            if logger is not None:
                validar_estrutura_do_layout(layout_data, key, logger)

            layouts[f"padrao_{version}"] = layout_data

        if logger is not None:
            logger.info(
                "Layouts de comercializadoras carregados com sucesso. Quantidade: %s",
                len(layouts),
            )

        return layouts

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar layouts de comercializadoras.")
        raise


def carregar_layouts_consumidores(
    context: AppContext,
    logger: Any | None = None,
) -> dict[str, dict[str, Any]]:
    """Carrega e valida os layouts de fichas de consumidores."""
    layouts: dict[str, dict[str, Any]] = {}

    try:
        if logger is not None:
            logger.info("Iniciando carga dos layouts de consumidores.")

        for version in range(1, 4):
            key = f"layout_ficha_consumidor_v{version}"
            layout_path = context.control_file(key)

            layout_data = ler_json(layout_path)
            
            # Validação adaptada para não quebrar layouts antigos
            if logger is not None:
                validar_estrutura_do_layout(layout_data, key, logger)

            layouts[f"v{version}"] = layout_data

        if logger is not None:
            logger.info(
                "Layouts de consumidores carregados com sucesso. Quantidade: %s",
                len(layouts),
            )

        return layouts

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar layouts de consumidores.")
        raise
```


---
## src\domain\cadastro\servico_receita.py
Linhas: 130
Classes: ReceitaIngestionError
Funções: _listar_cnpjs_de_entrada, _salvar_instantaneo_bruto, inserir_dados_receita
```python
"""Serviço de ingestão e validação cadastral da Receita Federal."""

from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from domain.enums import StatusAlerta
from services.connectors.receita_connector import buscar_receita_dados_lote
from storage.escrever_dados import escrever_conjunto_de_dados_silver

LOGGER = logging.getLogger(__name__)

class ReceitaIngestionError(Exception):
    """Exceção para falhas na ingestão da base da Receita Federal."""

def _listar_cnpjs_de_entrada(context: AppContext) -> list[str]:
    """Lê TODOS os CNPJs das Fichas e dos Contratos para garantir cobertura total."""
    cnpjs = set()
    silver_dir = context.path("silver")

    # 1. CNPJs das Fichas
    for segmento in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        path = silver_dir / segmento / f"{segmento}.parquet"
        if path.exists():
            df = pd.read_parquet(path)
            if "CNPJ" in df.columns:
                cnpjs.update(df["CNPJ"].dropna().astype(str).str.strip().tolist())

    # 2. CNPJs dos Contratos (Base completa do MVP)
    path_contratos = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if path_contratos.exists():
        df_contratos = pd.read_parquet(path_contratos)
        if "CNPJ" in df_contratos.columns:
            cnpjs.update(df_contratos["CNPJ"].dropna().astype(str).str.strip().tolist())

    # Limpeza e validação estrita dos 14 dígitos
    cnpjs_limpos = []
    for c in cnpjs:
        c_limpo = re.sub(r"\D", "", str(c)).zfill(14)
        if len(c_limpo) == 14 and c_limpo != "00000000000000":
            cnpjs_limpos.append(c_limpo)

    return list(set(cnpjs_limpos))

def _salvar_instantaneo_bruto(context: AppContext, payload: list[dict[str, Any]]) -> Path:
    bronze_dir = context.path("bronze") / "snapshots_fontes" / "receita"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    filename = f"raw_receita_{date.today().strftime('%Y%m%d')}.json"
    target = bronze_dir / filename
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target

def inserir_dados_receita(context: AppContext) -> dict[str, Any]:
    run_id = f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.receita")

    cnpjs = _listar_cnpjs_de_entrada(context)
    if not cnpjs:
        logger.warning("Nenhum CNPJ encontrado nas bases da Silver para consulta na Receita.")
        return {"run_id": run_id, "linhas_processadas": 0, "alertas_gerados_cad001": 0, "status": "SEM_DADOS"}

    logger.info("Iniciando consulta na BrasilAPI para %d CNPJ(s). Pode levar alguns minutos (Cache ativo)...", len(cnpjs))
    df_receita = buscar_receita_dados_lote(cnpjs, context)
    
    if df_receita.empty:
        logger.warning("Consulta da Receita retornou DataFrame vazio.")
        return {"run_id": run_id, "linhas_processadas": 0, "alertas_gerados_cad001": 0, "status": "SEM_DADOS"}

    payload = df_receita.to_dict(orient="records")
    _salvar_instantaneo_bruto(context, payload)

    df_receita = df_receita.drop_duplicates(subset=["CNPJ"], keep="last").reset_index(drop=True)
    df_receita["RUN_ID"] = run_id
    df_receita["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

    alertas: list[dict[str, Any]] = []
    for _, row in df_receita.iterrows():
        situacao = str(row.get("SITUACAO_CADASTRAL") or "").strip().upper()
        if situacao and situacao != "ATIVA" and situacao != "NONE":
            alertas.append({
                "CODIGO": "CAD_001",
                "CNPJ": row.get("CNPJ"),
                "MENSAGEM": f"CNPJ com situação cadastral irregular: {situacao}.",
                "SEVERIDADE": "ALTA",
                "RUN_ID": run_id,
                "DT_DETECCAO": datetime.now().isoformat(timespec="seconds"),
                "STATUS_ALERTA": StatusAlerta.ABERTO.value,
            })

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        escrever_conjunto_de_dados_silver(
            records=df_alertas.to_dict(orient="records"),
            output_dir=context.path("silver") / "alertas_credito",
            filename=f"alertas_cadastrais_receita_{run_id}",
        )

    silver_dir = context.path("silver") / "receita_silver"
    escrever_conjunto_de_dados_silver(
        records=df_receita.to_dict(orient="records"),
        output_dir=silver_dir,
        filename=f"receita_cadastral_silver_{run_id}",
    )

    # Ponteiro LATEST
    import shutil
    latest_path = silver_dir / "receita_cadastral_silver.parquet"
    versioned_path = silver_dir / f"receita_cadastral_silver_{run_id}.parquet"
    if latest_path.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(latest_path, silver_dir / f"receita_cadastral_silver_HIST_{ts}.parquet")
    if versioned_path.exists():
        shutil.copy2(versioned_path, latest_path)

    resumo = {
        "run_id": run_id,
        "linhas_processadas": int(len(df_receita)),
        "alertas_gerados_cad001": len(alertas),
        "status": "SUCESSO",
    }
    logger.info("Ingestão da Receita concluída: %s", resumo)
    return resumo
```


---
## src\domain\contratos\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\contratos\servico_contratos_denodo.py
Linhas: 171
Classes: -
Funções: aplicar_regras_negocio_pandas, processar_contratos_denodo, calcular_horas
```python
"""Serviço oficial de ingestão de Contratos Correntes do Denodo."""

from __future__ import annotations

import logging
import calendar
import pandas as pd

from datetime import datetime
from pathlib import Path
from typing import Any

from app.context import AppContext
from silver.normalizadores import padronizar_cnpj
from services.connectors.denodo_connector import buscar_denodo
from storage.escrever_dados import escrever_conjunto_de_dados_silver

LOGGER = logging.getLogger(__name__)

def aplicar_regras_negocio_pandas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # 1. TRATAMENTO DE CNPJ — via validador centralizado
    col_cnpj = "contraparte_cnpj" if "contraparte_cnpj" in df.columns else "cnpj"
    if col_cnpj in df.columns:
        parsed = df[col_cnpj].map(padronizar_cnpj)
        df["CNPJ"]       = parsed.map(lambda t: t[0])
        df["CNPJ_RAIZ"]  = parsed.map(lambda t: t[1])
        df["STATUS_CNPJ"] = parsed.map(lambda t: t[2])
    else:
        df["CNPJ"]       = None
        df["CNPJ_RAIZ"]  = None
        df["STATUS_CNPJ"] = "CNPJ_AUSENTE"
        
    # 2. TIPAGEM E NORMALIZAÇÃO
    colunas_numericas = ["ano", "mes", "id_parte", "id_tipo_contrato", "id_contraparte", "id_status", "quant_contratada"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 3. CÁLCULO DE MWh PARA MWm (Unidade Exclusiva: quant_contratada)
    def calcular_horas(row):
        try:
            ano = int(row.get("ano", 0))
            mes = int(row.get("mes", 0))
            if 2000 <= ano <= 2100 and 1 <= mes <= 12:
                return calendar.monthrange(ano, mes)[1] * 24
        except:
            pass
        return 730 # Fallback

    df["HORAS_MES"] = df.apply(calcular_horas, axis=1)
    df["VOLUME_MWH"] = df["quant_contratada"] # Preserva a origem auditável
    df["VOLUME_MWM"] = df["quant_contratada"] / df["HORAS_MES"] # Conversão Real

    # 4. IDENTIFICAÇÃO DE FUTUROS E GRANULARIDADE
    col_in = "suprimento_inicio" if "suprimento_inicio" in df.columns else ("vigencia_inicio" if "vigencia_inicio" in df.columns else "inicio_suprimento")
    df["DT_IN_TEMP"] = pd.to_datetime(df.get(col_in), errors="coerce")
    hoje = pd.Timestamp("today").normalize()
    filtro_futuros = (df["DT_IN_TEMP"] > hoje)

    filtro = (
        (df.get("ano", 0) >= 2020) & 
        (df.get("parte_apelido", "") == "COPEL COM") &
        (df.get("contraparte_apelido", "") != "COPEL COM - Transferência de energia") &
        (df.get("id_parte", 0) == 297) &
        (df.get("id_tipo_contrato", 0).isin([1, 3, 33, 90])) & 
        (df.get("contrato_vinculado", "").isna() | (df.get("contrato_vinculado", "") == "")) &
        ((~df.get("id_status", 0).isin([0, 1, 4, 5, 6, 9, 10, 11])) | filtro_futuros) & 
        (df.get("quant_contratada", 0) > 0) # Removido uso de quant_sazonalizada
    )
    
    if "ncdempresaproprietaria" in df.columns: filtro = filtro & (df["ncdempresaproprietaria"] == 297)
    if "id_contraparte" in df.columns: filtro = filtro & (df["id_contraparte"] != 9057)
    filtro = filtro & (df["STATUS_CNPJ"] == "CNPJ_VALIDO")

    return df.loc[filtro].drop(columns=["DT_IN_TEMP"]).copy()

def processar_contratos_denodo(context: AppContext) -> dict[str, Any]:
    run_id = f"CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.contratos")

    try:
        # ESTRATÉGIA OFFLINE/LOCAL: Lê o CSV se existir para evitar Timeout na API da rede
        input_dir = context.path("entradas") / "contratos_denodo"
        arquivos_locais = list(input_dir.glob("*.csv"))
        
        df_raw = pd.DataFrame()
        if arquivos_locais:
            arquivo = max(arquivos_locais, key=lambda f: f.stat().st_mtime)
            logger.info("Lendo contratos de arquivo local: %s (Ignorando API para evitar timeout da rede)", arquivo.name)
            # Tenta ler separado por vírgula, se não der, tenta ponto e vírgula
            try:
                df_raw = pd.read_csv(arquivo, sep=",", dtype=str)
                if len(df_raw.columns) < 5:
                    df_raw = pd.read_csv(arquivo, sep=";", dtype=str)
            except Exception:
                df_raw = pd.read_csv(arquivo, sep=";", dtype=str)
        else:
            logger.info("Iniciando extração da view vwi_exportar_contrato via REST.")
            colunas_necessarias = "ano,mes,ncdempresaproprietaria,id_parte,id_tipo_contrato,id_contraparte,contrato_vinculado,id_status,quant_contratada,quant_sazonalizada,parte_apelido,contraparte_apelido,contraparte_cnpj,nome_contrato,suprimento_inicio,suprimento_termino,status"
            parametros_api = {
                "$select": colunas_necessarias, 
                "$filter": "ano >= 2024 AND parte_apelido = 'COPEL COM' AND id_parte = 297 AND ncdempresaproprietaria = 297"
            }
            df_raw = buscar_denodo("vwi_exportar_contrato", params=parametros_api)
        
        if df_raw.empty: return {"run_id": run_id, "status": "SEM_DADOS", "linhas": 0}

        # Backup Bronze
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "denodo"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        df_raw.to_parquet(bronze_dir / f"raw_contratos_{run_id}.parquet", index=False)

        # Processamento e Limpeza
        df_silver = aplicar_regras_negocio_pandas(df_raw)
        df_silver.columns = [str(c).strip().upper() for c in df_silver.columns]
        
        # O CNPJ já foi limpo e criado na função aplicar_regras_negocio_pandas!
        # Removida a conversão duplicada "CONTRAPARTE_CNPJ": "CNPJ"
        rename_map = {
            "NOME_CONTRATO": "CONTRATO", 
            "SUPRIMENTO_INICIO": "VIGENCIA_INICIO", 
            "SUPRIMENTO_TERMINO": "VIGENCIA_FIM"
        }
        df_silver = df_silver.rename(columns=rename_map)
        
        # Volumes e Competências
        df_silver["QUANT_CONTRATADA"] = df_silver["QUANT_CONTRATADA"]
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = df_silver["VOLUME_MWM"] # O valor já dividido e convertido em MWm
        df_silver["VOLUME_MWH_ORIGINAL"] = df_silver["VOLUME_MWH"] # Preserva a origem auditável
        df_silver["COMPETENCIA"] = df_silver["ANO"].astype(str).str.replace(r"\.0", "", regex=True) + df_silver["MES"].astype(str).str.replace(r"\.0", "", regex=True).str.zfill(2)
        
        # A normalização de regex do CNPJ foi removida daqui, pois já foi feita na origem.
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = pd.to_numeric(df_silver["VOLUME_CONTRATADO_MENSAL_MWM"], errors="coerce").fillna(0.0)
        if "STATUS" not in df_silver.columns: df_silver["STATUS"] = "ATIVO"

        # Garantia de colunas para o groupby
        for col in ["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]:
            if col not in df_silver.columns: df_silver[col] = "NAO_INFORMADO"

        # RESOLUÇÃO DA EXPLOSÃO CARTESIANA: Agrupando o volume por Contrato Único
        df_silver_final = df_silver.groupby(["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"], as_index=False).agg({"VOLUME_CONTRATADO_MENSAL_MWM": "sum"})

        # Preserva CNPJ_RAIZ e STATUS_CNPJ (descartadas pelo groupby) reinserindo via merge
        cols_identidade = ["CNPJ", "CNPJ_RAIZ", "STATUS_CNPJ"]
        cols_identidade_presentes = [c for c in cols_identidade if c in df_silver.columns]
        df_identidade = df_silver[cols_identidade_presentes].drop_duplicates(subset=["CNPJ"])
        df_silver_final = pd.merge(df_silver_final, df_identidade, on="CNPJ", how="left")
        
        df_silver_final["RUN_ID"] = run_id
        df_silver_final["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        # Persistência Silver
        silver_dir = context.path("silver") / "denodo_contratos_padronizados"
        silver_dir.mkdir(parents=True, exist_ok=True)
        
        for comp in df_silver_final["COMPETENCIA"].unique():
            if str(comp) in ["000", "NAO_INFORMADONAO_INFORMADO", "00", "nan00"]: continue
            df_comp = df_silver_final[df_silver_final["COMPETENCIA"] == comp]
            escrever_conjunto_de_dados_silver(records=df_comp.to_dict(orient="records"), output_dir=silver_dir, filename=f"contratos_correntes_{comp}")

        dir_reconciliacao = context.path("silver") / "denodo_contratos_silver"
        escrever_conjunto_de_dados_silver(records=df_silver_final.to_dict(orient="records"), output_dir=dir_reconciliacao, filename="contratos_correntes")
        
        logger.info("Contratos agregados e sem duplicidades salvos. %d registros limpos", len(df_silver_final))
        return {"run_id": run_id, "linhas_processadas": len(df_silver_final), "status": "SUCESSO"}
    except Exception as exc:
        logger.exception("Falha crítica na ingestão de contratos do Denodo.")
        raise Exception(f"Erro na ingestão Denodo: {exc}") from exc
```


---
## src\domain\credito\pd_cgrupo.py
Linhas: 151
Classes: -
Funções: _norm, _norm_agencia, _norm_rating, _mapear_rating_externo, _resolver_rating_cgrupo, _pior_rating, _percentil_empirico, _interpolar_pd, calcular_pd_final_cgrupo
```python
from __future__ import annotations

from typing import Any

from domain.credito.pd_exceptions import PdCalculationError


RATING_ORDER = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}


def _norm(value: Any) -> str:
    return str(value or "").strip().upper()


def _norm_agencia(value: Any) -> str:
    agencia = _norm(value)

    mapa = {
        "FITCH": "FITCH",
        "FITCH RATINGS": "FITCH",
        "MOODYS": "MOODYS",
        "MOODY'S": "MOODYS",
        "MOODY S": "MOODYS",
        "SP": "SP",
        "S&P": "SP",
        "STANDARD & POOR'S": "SP",
        "STANDARD & POORS": "SP",
        "STANDARD AND POOR'S": "SP",
        "STANDARD AND POORS": "SP",
    }
    return mapa.get(agencia, agencia)


def _norm_rating(value: Any) -> str:
    return _norm(value)


def _mapear_rating_externo(
    agencia: str,
    rating_externo: str,
    regras_rating: dict[str, Any],
) -> str:
    ag = _norm_agencia(agencia)
    rt = _norm(rating_externo)

    short_default = {_norm(x)
                     for x in regras_rating["short_term_or_default_markers"]}
    if rt in short_default:
        return regras_rating["default_class"]

    agencias = regras_rating["agencias"]
    if ag not in agencias:
        return regras_rating["default_class"]

    for rating_copel, lista_externa in agencias[ag].items():
        if rt in {_norm(x) for x in lista_externa}:
            return rating_copel

    return regras_rating["default_class"]


def _resolver_rating_cgrupo(
    registro: dict[str, Any],
    regras_segmento: dict[str, Any],
) -> tuple[str, str]:
    regras_rating = regras_segmento["rating_externo"]

    agencia = registro.get("AGENCIA")
    rating = registro.get("NOTA_CREDITO")

    if agencia and rating:
        rating_convertido = _mapear_rating_externo(
            agencia=agencia,
            rating_externo=rating,
            regras_rating=regras_rating,
        )
        return rating_convertido, "RATING_PUBLICO"

    rating_interno = _norm(registro.get("RATING_FINAL")
                           or registro.get("RATING_COPEL"))
    if rating_interno not in {"A", "B", "E"}:
        raise PdCalculationError(
            f"Rating interno inválido para CGRUPO: {rating_interno!r}"
        )

    return rating_interno, "RATING_INTERNO"


def _pior_rating(ratings: list[str]) -> str:
    validos = [r for r in ratings if r in RATING_ORDER]
    if not validos:
        raise PdCalculationError(
            "Nenhum rating válido encontrado para CGRUPO."
        )
    return max(validos, key=lambda x: RATING_ORDER[x])


def _percentil_empirico(pd_base, peer_group):
    n = len(peer_group)

    if n <= 1:
        return 0.5

    menores = sum(1 for x in peer_group if x < pd_base)
    iguais = sum(1 for x in peer_group if x == pd_base)

    return (menores + 0.5 * iguais) / n


def _interpolar_pd(pd_min: float, pd_max: float, u: float) -> float:
    return pd_min + u * (pd_max - pd_min)


def calcular_pd_final_cgrupo(
    registro: dict[str, Any],
    regras_segmento: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    pd_base = float(registro["PD_BASE"])
    rating, fonte_rating = _resolver_rating_cgrupo(registro, regras_segmento)

    regras_pd = regras_segmento["pd_final_rules"]
    fixed_pd = regras_pd.get("fixed_pd_by_rating", {})

    if rating in fixed_pd:
        pd_final = float(fixed_pd[rating])
        return {
            "RATING_FINAL": rating,
            "FONTE_RATING": fonte_rating,
            "PD_MIN_FAIXA": 0.0,
            "PD_MAX_FAIXA": pd_final,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": pd_final,
            "PD_METODO": "FIXED_PD",
        }

    faixa = regras_pd["faixas_pd"][rating]
    pd_min = float(faixa["min"])
    pd_max = float(faixa["max"])

    pd_final = min(max(pd_base, pd_min), pd_max)

    return {
        "RATING_FINAL": rating,
        "FONTE_RATING": fonte_rating,
        "PD_MIN_FAIXA": pd_min,
        "PD_MAX_FAIXA": pd_max,
        "PERCENTIL_PD_BASE": None,
        "PD_FINAL": pd_final,
        "PD_METODO": "CLAMP",
    }

```


---
## src\domain\credito\pd_motor.py
Linhas: 161
Classes: -
Funções: calcular_pd_ajustada
```python
"""Orquestração do cálculo de PD ajustada."""

from __future__ import annotations

from typing import Any

from domain.credito.notas_quantitativas_cpura import (
    calcular_notas_quantitativas_cpura,
)
from domain.credito.pd_base import calcular_pd_base
from domain.credito.pd_exceptions import (
    PdCalculationError,
    PdConfigurationError,
)
from domain.credito.pd_transform import transformar_pd_por_segmento
from domain.credito.pd_validator import validar_insumos_pd
from domain.credito.rating import calcular_rating_final
from domain.credito.score_qualitativo import calcular_score_qualitativo_cpura
from domain.credito.score_quantitativo import calcular_score_quantitativo_cpura
from domain.credito.score_total import calcular_score_total_cpura


def calcular_pd_ajustada(
    registro: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any] | None = None,
    pd_cpura_config: dict[str, Any] | None = None,
    score_cpura_config: dict[str, Any] | None = None,
    peer_group: list[float] | None = None,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada/final da contraparte."""
    segmento_pd = str(registro.get("SEGMENTO_PD", "")).strip().upper()

    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo de PD ajustada. "
                "CNPJ=%s SEGMENTO_PD=%s",
                registro.get("CNPJ"),
                segmento_pd,
            )

        validar_insumos_pd(registro, segmento_pd)

        pd_base = calcular_pd_base(registro, segmento_pd)

        registro_calculo = dict(registro)
        registro_calculo["PD_BASE"] = pd_base

        resultado_scores: dict[str, Any] = {}

        if segmento_pd == "CPURA":
            if not score_cpura_config:
                raise PdConfigurationError(
                    "score_cpura_config não informado para CPURA."
                )

            if not pd_cpura_config:
                raise PdConfigurationError(
                    "pd_cpura_config não informado para CPURA."
                )

            notas_quant_info = calcular_notas_quantitativas_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(notas_quant_info)

            score_qual_info = calcular_score_qualitativo_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(score_qual_info)

            score_quant_info = calcular_score_quantitativo_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(score_quant_info)

            score_total_info = calcular_score_total_cpura(
                score_quant_info=score_quant_info,
                score_qual_info=score_qual_info,
                logger=logger,
            )
            registro_calculo.update(score_total_info)

            rating_final = calcular_rating_final(
                registro=registro_calculo,
                segmento_pd=segmento_pd,
                pd_cpura_config=pd_cpura_config,
            )
            registro_calculo["RATING_FINAL"] = rating_final

            resultado_scores.update(notas_quant_info)
            resultado_scores.update(score_qual_info)
            resultado_scores.update(score_quant_info)
            resultado_scores.update(score_total_info)

        if segmento_pd in {"CGRUPO", "CONSUMIDOR_GT_5"} and not pd_transform_rules:
            raise PdConfigurationError(
                f"pd_transform_rules não informado para {segmento_pd}."
            )
        resultado_transformacao = transformar_pd_por_segmento(
            registro=registro_calculo,
            segmento_pd=segmento_pd,
            pd_base=pd_base,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=pd_cpura_config,
            peer_group=peer_group,
            logger=logger,
            rating_final=(
                registro_calculo.get("RATING_FINAL")
                or registro_calculo.get("RATING_COPEL")
            ),
        )

        resultado = {
            "SEGMENTO_PD": segmento_pd,
            "PD_BASE": pd_base,
            **resultado_scores,
            **resultado_transformacao,
        }

        if logger is not None:
            logger.info(
                "PD ajustada calculada com sucesso. "
                "CNPJ=%s SEGMENTO_PD=%s PD_BASE=%s "
                "RATING_FINAL=%s SCORE_TOTAL=%s PD_FINAL=%s METODO=%s",
                registro.get("CNPJ"),
                segmento_pd,
                resultado.get("PD_BASE"),
                resultado.get("RATING_FINAL"),
                resultado.get("SCORE_TOTAL"),
                resultado.get("PD_FINAL"),
                resultado.get("PD_METODO"),
            )

        return resultado

    except PdCalculationError as e:
        if logger is not None:
            logger.error(
                f"Erro controlado no cálculo de PD ajustada. CNPJ={registro.get('CNPJ')} SEGMENTO_PD={segmento_pd} - Motivo: {str(e)}"
            )
        raise

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha inesperada no cálculo de PD ajustada. "
                "CNPJ=%s SEGMENTO_PD=%s",
                registro.get("CNPJ"),
                segmento_pd,
            )
        raise

```


---
## src\domain\credito\pe_engine.py
Linhas: 63
Classes: -
Funções: calcular_perda_esperada
```python
"""Motor de Perda Esperada (PE).

feat(T3.4.1): Retorno dual (pe_reais + pe_percentual) e rastreabilidade
com calculo_id.
Ref: §6.7, §11.2, §11.6 (Reconciliação PE) do Planejamento Funcional.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4


def calcular_perda_esperada(
    ead: float | None,
    lgd_liquida: float | None,
    pd_final: float | None,
    notional: float | None = None,
) -> dict[str, object]:
    """
    Cálculo da Perda Esperada.

    Fórmula: PE = EAD × LGD × PD (§6.7).

    Args:
        ead: Exposure at Default em R$.
        lgd_liquida: Loss Given Default líquida [0, 1].
        pd_final: Probability of Default [0, 1].
        notional: Notional total para cálculo do percentual (PE / Notional).

    Returns:
        Dict com pe_reais, pe_percentual, calculo_id e metadados.
    """
    calculo_id = f"PE_{uuid4().hex[:12]}"
    dt_calculo = datetime.now().isoformat(timespec="seconds")

    if ead is None or lgd_liquida is None or pd_final is None:
        return {
            "calculo_id": calculo_id,
            "pe_reais": None,
            "pe_percentual": None,
            "dt_calculo": dt_calculo,
            "status": "DADOS_INSUFICIENTES",
        }

    pe_reais = float(ead) * float(lgd_liquida) * float(pd_final)

    # PE percentual = PE / Notional (§11.6 — reconciliação)
    pe_percentual = None
    if notional is not None and float(notional) > 0:
        pe_percentual = pe_reais / float(notional)

    return {
        "calculo_id": calculo_id,
        "pe_reais": pe_reais,
        "pe_percentual": pe_percentual,
        "ead_input": float(ead),
        "lgd_input": float(lgd_liquida),
        "pd_input": float(pd_final),
        "notional_input": float(notional) if notional is not None else None,
        "dt_calculo": dt_calculo,
        "status": "CALCULADO",
    }
```


---
## src\domain\credito\rating.py
Linhas: 112
Classes: -
Funções: _calcular_rating_final_cpura, _obter_rating_pronto, calcular_rating_final
```python
"""Determinação do rating final para o cálculo de PD ajustada."""

from __future__ import annotations

from typing import Any

from silver.normalizadores import normalizar_string
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _calcular_rating_final_cpura(
    registro: dict[str, Any],
    cpura_score_faixas: dict[str, Any],
) -> str:
    """Calcula o rating final de CPURA a partir do SCORE_TOTAL."""
    score_total = registro.get("SCORE_TOTAL")

    if score_total is None:
        raise PdInputValidationError(
            "SCORE_TOTAL não informado para cálculo do rating de CPURA."
        )

    try:
        score_total = float(score_total)
    except (TypeError, ValueError) as exc:
        raise PdInputValidationError(
            f"SCORE_TOTAL inválido: {score_total!r}"
        ) from exc

    if not isinstance(cpura_score_faixas, dict) or not cpura_score_faixas:
        raise PdConfigurationError(
            "Configuração de score_faixas de CPURA ausente ou inválida."
        )

    for rating, faixa in cpura_score_faixas.items():
        try:
            score_min = float(faixa["min"])
            score_max = float(faixa["max"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Faixa de score incompleta para rating {rating}."
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                f"Faixa de score inválida para rating {rating}."
            ) from exc

        if score_min <= score_total <= score_max:
            return rating

    raise PdInputValidationError(
        f"SCORE_TOTAL fora das faixas esperadas para CPURA: {score_total}"
    )


def _obter_rating_pronto(
    registro: dict[str, Any],
    segmento_pd: str,
) -> str:
    """Obtém rating já existente no registro."""
    rating = (
        registro.get("RATING_COPEL")
        or registro.get("NOTA_CREDITO")
        or registro.get("RATING_FINAL")
    )

    if rating is None:
        raise PdInputValidationError(
            f"Registro sem rating para {segmento_pd}."
        )

    rating_final = normalizar_string(rating, upper=True)

    validos = {"A", "B", "E"} if segmento_pd == "CGRUPO" else {
        "A", "B", "C", "D", "E"
    }

    if rating_final not in validos:
        raise PdInputValidationError(
            f"Rating inválido para {segmento_pd}: {rating_final}"
        )

    return rating_final


def calcular_rating_final(
    registro: dict[str, Any],
    segmento_pd: str,
    pd_cpura_config: dict[str, Any] | None = None,
) -> str:
    """Determina o rating final conforme o segmento."""
    segmento_pd = str(segmento_pd).strip().upper()

    if segmento_pd == "CPURA":
        if not pd_cpura_config:
            raise PdConfigurationError(
                "pd_cpura_config não informado para cálculo do rating de CPURA."
            )

        score_faixas = pd_cpura_config.get("score_faixas")
        return _calcular_rating_final_cpura(
            registro=registro,
            cpura_score_faixas=score_faixas,
        )

    return _obter_rating_pronto(
        registro=registro,
        segmento_pd=segmento_pd,
    )

```


---
## src\domain\credito\score_total.py
Linhas: 50
Classes: -
Funções: calcular_score_total_cpura
```python
# -*- coding: utf-8 -*-
"""Cálculo do score total de CPURA."""

from __future__ import annotations

from typing import Any

from domain.credito.pd_exceptions import PdInputValidationError


def calcular_score_total_cpura(
    score_quant_info: dict[str, Any],
    score_qual_info: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score total de CPURA."""
    try:
        score_quant = score_quant_info.get("SCORE_QUANTITATIVO")
        score_qual = score_qual_info.get("SCORE_QUALITATIVO")

        if score_quant is None:
            raise PdInputValidationError(
                "SCORE_QUANTITATIVO não informado."
            )

        if score_qual is None:
            raise PdInputValidationError(
                "SCORE_QUALITATIVO não informado."
            )

        score_total = float(score_quant) + float(score_qual)

        resultado = {
            "SCORE_TOTAL": score_total,
        }

        if logger is not None:
            logger.info(
                "Score total CPURA calculado. SCORE_TOTAL=%s",
                score_total,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score total CPURA."
            )
        raise

```


---
## src\domain\credito\servico_fato_analise_credito.py
Linhas: 53
Classes: -
Funções: construir_fato_analise_credito
```python
"""Construção da tabela Fato de Análise de Crédito (fato_analise_credito)."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from app.context import AppContext
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def construir_fato_analise_credito(
    context: AppContext,
    df_silver_analises: pd.DataFrame,
    df_dim_contraparte: pd.DataFrame,
) -> dict[str, Any]:
    run_id = f"FATO_ANL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.gold.fato_analise_credito")
    logger.info("Iniciando carga de fato_analise_credito (run_id=%s).", run_id)

    if df_silver_analises.empty:
        return {"run_id": run_id, "linhas": 0, "status": "SEM_DADOS"}

    df_fato = df_silver_analises.copy()
    df_fato["CNPJ"] = df_fato["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)

    # CORREÇÃO DOS MAPEAMENTOS DA FONTE
    if "DATA_CALCULO" in df_fato.columns and "DATA_ANALISE" not in df_fato.columns:
        df_fato["DATA_ANALISE"] = df_fato["DATA_CALCULO"]
    if "RATING_FINAL" not in df_fato.columns and "RATING_COPEL" in df_fato.columns:
        df_fato["RATING_FINAL"] = df_fato["RATING_COPEL"]
    if "MODELO_METODOLOGICO" not in df_fato.columns and "versao_ficha" in df_fato.columns:
        df_fato["MODELO_METODOLOGICO"] = df_fato["versao_ficha"]
        
    # Adicionando PATRIMONIO_LIQUIDO, SITUACAO_DF e SITUACAO_ANALISE na lista de colunas esperadas
    for col in ["ANALISE_ID", "DATA_ANALISE", "RATING_FINAL", "PD_FINAL", "SCORE_CALCULADO", "CLASSE_RISCO", "MODELO_METODOLOGICO", "DATA_DEMONSTRACAO_FINANCEIRA", "SEGMENTO_PD", "TIPO_FICHA", "PATRIMONIO_LIQUIDO", "SITUACAO_DF", "SITUACAO_ANALISE"]:
        if col not in df_fato.columns: df_fato[col] = None

    rename_map = {
        "CNPJ": "CNPJ", "DATA_ANALISE": "DATA_ANALISE", "RATING_FINAL": "RATING",
        "PD_FINAL": "PD_PERCENTUAL", "SCORE_CALCULADO": "SCORE", "CLASSE_RISCO": "CLASSE",
        "MODELO_METODOLOGICO": "MODELO", "DATA_DEMONSTRACAO_FINANCEIRA": "DATA_BALANCO_USADO",
        "SEGMENTO_PD": "SEGMENTO_METODOLOGICO_FICHA", "TIPO_FICHA": "TIPO_FICHA",
        "PATRIMONIO_LIQUIDO": "PATRIMONIO_LIQUIDO", "SITUACAO_DF": "SITUACAO_DF",
        "SITUACAO_ANALISE": "SITUACAO_ANALISE"
    }
    
    # Previne KeyError garantindo que só renomeia o que existe
    df_final = df_fato[[c for c in rename_map.keys() if c in df_fato.columns]].rename(columns=rename_map).copy()
    
    df_final["ETL_RUN_ID"] = run_id
    relational_dir = context.path("relational_facts")
    relational_dir.mkdir(parents=True, exist_ok=True)
    escrever_conjunto_de_dados_silver(records=df_final.to_dict(orient="records"), output_dir=relational_dir, filename="fato_analise_credito")
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}
```


---
## src\domain\credito\taxa_risco_engine.py
Linhas: 79
Classes: -
Funções: calcular_taxa_risco
```python
"""Motor de Taxa de Risco de Crédito.

feat(T3.4.2): Cálculo de Taxa_Risco = PE_total / Notional_total.
Trata divisão por zero gerando alerta QLT_002.
Ref: §7.1, §8.3 (QLT_002), §11.6 do Planejamento Funcional.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

LOGGER = logging.getLogger(__name__)


def calcular_taxa_risco(
    pe_total: float | None,
    notional_total: float | None,
) -> dict[str, Any]:
    """
    Cálculo da Taxa de Risco de Crédito da carteira.

    Fórmula: Taxa_Risco = PE_total / Notional_total (§7.1).

    Args:
        pe_total: Somatório da Perda Esperada em Reais.
        notional_total: Somatório do Notional (Exposição Bruta).

    Returns:
        Dict com taxa_risco, calculo_id e potenciais alertas.
    """
    calculo_id = f"TAXA_{uuid4().hex[:12]}"
    dt_calculo = datetime.now().isoformat(timespec="seconds")

    if pe_total is None or notional_total is None:
        return {
            "calculo_id": calculo_id,
            "taxa_risco": None,
            "dt_calculo": dt_calculo,
            "status": "DADOS_INSUFICIENTES",
            "alertas": []
        }

    alertas = []
    
    # Tratamento de divisão por zero / Notional inválido (§8.3 — QLT_002)
    if float(notional_total) <= 0:
        LOGGER.warning(
            "Cálculo de Taxa de Risco não executado: Notional Total inválido ou zero (%.2f).", 
            notional_total
        )
        alertas.append({
            "CODIGO": "QLT_002",
            "SEVERIDADE": "ALTO",
            "MENSAGEM": f"Divisão por zero: Notional total ({notional_total}) <= 0 durante cálculo da Taxa de Risco."
        })
        return {
            "calculo_id": calculo_id,
            "taxa_risco": None,
            "pe_total_input": float(pe_total),
            "notional_total_input": float(notional_total),
            "dt_calculo": dt_calculo,
            "status": "ERRO_MATEMATICO",
            "alertas": alertas
        }

    taxa_risco = float(pe_total) / float(notional_total)

    return {
        "calculo_id": calculo_id,
        "taxa_risco": taxa_risco,
        "pe_total_input": float(pe_total),
        "notional_total_input": float(notional_total),
        "dt_calculo": dt_calculo,
        "status": "CALCULADO",
        "alertas": alertas
    }

```


---
## src\domain\fichas\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\fichas\classificador.py
Linhas: 196
Classes: ClassificationResult
Funções: normalizar_rotulo, localizar_celula_por_regex, verificar_label, classificar_pasta_de_trabalho
```python
"""Classificação de fichas conforme os layouts conhecidos."""

from __future__ import annotations

import re
from typing import Any
from openpyxl.worksheet.worksheet import Worksheet

from dataclasses import dataclass
from common.excel import ler_celula
from silver.normalizadores import normalizar_string


@dataclass
class ClassificationResult:
    """Representa o resultado da classificação de layout."""

    versao_ficha: str
    matched_fields: list[str]
    missing_fields: list[str]

def normalizar_rotulo(value: Any) -> str:
    """Normaliza texto de label para comparação."""
    if value is None:
        return ""

    return normalizar_string(str(value), upper=True)

def localizar_celula_por_regex(
    worksheet: Worksheet,
    search_pattern: str,
    max_rows: int = 150,
    max_cols: int = 30,
) -> bool:
    """
    Verifica se um label correspondente ao padrão regex existe na planilha.

    Args:
        worksheet: Aba do openpyxl.
        search_pattern: Expressão regular para buscar o rótulo.
        max_rows: Limite de linhas para a busca.
        max_cols: Limite de colunas para a busca.

    Returns:
        True se o padrão for encontrado, False caso contrário.
    """
    if not search_pattern:
        return False

    try:
        regex = re.compile(search_pattern, re.IGNORECASE)
    except re.error:
        # Se o padrão for inválido, não pode haver match.
        return False

    # Itera nas células dentro do limite de busca
    for row in worksheet.iter_rows(
        min_row=1, max_row=max_rows, min_col=1, max_col=max_cols
    ):
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                if regex.search(cell.value.strip()):
                    # Encontrou o label, a verificação é bem-sucedida.
                    return True

    return False

def verificar_label(
    workbook: Any,
    field_name: str,
    meta: dict[str, Any],
    logger: Any,
    versao_ficha: str,
) -> bool:
    """Verifica se o label do campo coincide com o esperado."""
    sheet_name = meta.get("sheet_name", workbook.active.title)
    ws = workbook[sheet_name] if sheet_name in workbook.sheetnames else workbook.active

    label_cell = meta.get("label_cell")
    search_pattern = meta.get("search_pattern")
    expected_label = meta.get("expected_label")

    # Estratégia 1: Verificação por coordenada fixa (label_cell)
    if label_cell:
        if expected_label is None:
            expected_label = field_name

        actual_label = ler_celula(ws, label_cell)
        expected_normalized = normalizar_rotulo(expected_label)
        actual_normalized = normalizar_rotulo(actual_label)

        # Lógica de exceção para o layout "padrao_3"
        if expected_normalized == "CNPJ" and versao_ficha == "padrao_3":
            categoria_label = ler_celula(ws, "A19")
            if expected_normalized == actual_normalized and categoria_label == "Categoria":
                return False

        matched = expected_normalized in actual_normalized
        logger.info(
            "Verificação (estática) '%s': label_cell=%s, expected='%s', actual='%s', matched=%s",
            field_name, label_cell, expected_normalized, actual_normalized, matched
        )
        return matched

    # Estratégia 2: Verificação por busca de padrão (search_pattern)
    if search_pattern:
        matched = localizar_celula_por_regex(ws, search_pattern) is not None
        logger.info(
            "Verificação (dinâmica) '%s': pattern='%s', matched=%s",
            field_name, search_pattern, matched
        )
        return matched

    raise ValueError(
        f"Campo de verificação '{field_name}' no layout '{versao_ficha}' "
        "não possui 'label_cell' nem 'search_pattern' para classificação."
    )

def classificar_pasta_de_trabalho(
    workbook: Any,
    layouts: dict[str, dict[str, Any]],
    logger: Any,
) -> ClassificationResult | None:
    """Classifica um workbook pelos verify_fields.

    Um layout só é aceito se todos os campos em verify_fields
    coincidirem no label_cell com o expected_label.
    """
    try:
        logger.info(
            "Iniciando classificação do workbook com %s layouts.",
            len(layouts),
        )

        for versao_ficha, layout in layouts.items():
            verify_fields = layout.get("verify_fields", [])

            logger.info(
                "Testando layout '%s' com %s verify_fields.",
                versao_ficha,
                len(verify_fields),
            )

            if not verify_fields:
                raise ValueError(
                    f"Layout '{versao_ficha}' sem verify_fields."
                )

            matched_fields: list[str] = []
            missing_fields: list[str] = []

            all_match = True

            for field_name in verify_fields:
                if field_name not in layout.get("field_map", {}):
                    raise ValueError(
                        f"Campo '{field_name}' está em verify_fields, "
                        f"mas não existe em 'field_map' no layout "
                        f"'{versao_ficha}'."
                    )

                meta = layout["field_map"][field_name]

                if verificar_label(workbook, field_name, meta, logger, versao_ficha):
                    matched_fields.append(field_name)
                else:
                    missing_fields.append(field_name)
                    all_match = False

                    logger.info(
                        "Layout '%s' rejeitado. Campo de verificação "
                        "'%s' não coincidiu.",
                        versao_ficha,
                        field_name,
                    )
                    break

            if all_match:
                logger.info(
                    "Layout '%s' classificado com sucesso. "
                    "Campos verificados: %s",
                    versao_ficha,
                    matched_fields,
                )
                return ClassificationResult(
                    versao_ficha=versao_ficha,
                    matched_fields=matched_fields,
                    missing_fields=missing_fields,
                )

        logger.warning("Nenhum layout compatível foi identificado.")
        return None

    except Exception:
        logger.exception("Falha durante a classificação do workbook.")
        raise
```


---
## src\domain\fichas\validador.py
Linhas: 242
Classes: DomainRuleEngine
Funções: _is_empty, validar_registro, validar_registro_consumidor, __init__, validate
```python
"""Validação técnica e de domínio unificada dos registros extraídos."""

from __future__ import annotations
from typing import Any

def _is_empty(value: Any) -> bool:
    """Indica se o valor deve ser tratado como vazio."""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False

class DomainRuleEngine:
    """Motor unificado que aplica validações nativas e regras do JSON em um único passo."""

    def __init__(self, quality_rules: dict[str, Any] | None = None):
        self.quality_rules = quality_rules or {}
        self.dynamic_rules = self.quality_rules.get("rules", [])

    def validate(
        self, record: dict[str, Any], required_fields: list[str]
    ) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        # 1. Validação de Campos Obrigatórios (Estática)
        for field in required_fields:
            if _is_empty(record.get(field)):
                errors.append(f"Campo obrigatório ausente: {field}")

        # 2. Validações de Domínio Universais (Fallback / Plausibilidade Básica)
        pl = record.get("PATRIMONIO_LIQUIDO")
        if _is_empty(pl):
            warnings.append("PATRIMONIO_LIQUIDO não informado.")
        elif str(pl).upper() != "NAO_APLICAVEL" and not isinstance(pl, (int, float)):
            errors.append("PATRIMONIO_LIQUIDO inválido: valor não numérico.")

        data_df = record.get("DATA_DEMONSTRACAO_FINANCEIRA")
        data_calculo = record.get("DATA_CALCULO")
        if _is_empty(data_df):
            warnings.append("DATA_DEMONSTRACAO_FINANCEIRA não informada.")
        if _is_empty(data_calculo):
            warnings.append("DATA_CALCULO não informada.")

        # Trata a PD se não houver regra dinâmica explícita (para não quebrar comercializadoras)
        has_pd_rule = any(r.get("field") == "PROBABILIDADE_DEFAULT" for r in self.dynamic_rules)
        if not has_pd_rule and "PROBABILIDADE_DEFAULT" in record:
            pd_val = record.get("PROBABILIDADE_DEFAULT")
            if _is_empty(pd_val):
                warnings.append("PROBABILIDADE_DEFAULT não informada.")
            elif str(pd_val).upper() != "NAO_APLICAVEL" and not isinstance(pd_val, (int, float)):
                errors.append("PROBABILIDADE_DEFAULT inválida: valor não numérico.")
            elif isinstance(pd_val, (int, float)) and (pd_val < 0 or pd_val > 100):
                errors.append("PROBABILIDADE_DEFAULT inválida: fora do intervalo [0, 100].")

        # 3. Validações Dinâmicas (Data Quality Rules JSON)
        for rule in self.dynamic_rules:
            field = rule.get("field")
            val = record.get(field)

            if _is_empty(val):
                continue

            if not isinstance(val, (int, float)):
                errors.append(f"{field} inválido: valor não numérico.")
                continue

            rule_type = rule.get("type")
            if rule_type == "range":
                r_min, r_max = rule.get("min"), rule.get("max")
                if r_min is not None and val < r_min:
                    errors.append(f"{field} inválido: valor {val} menor que o limite ({r_min}).")
                if r_max is not None and val > r_max:
                    errors.append(f"{field} inválido: valor {val} maior que o limite ({r_max}).")
            elif rule_type == "min":
                r_val = rule.get("value")
                if r_val is not None and val < r_val:
                    errors.append(f"{field} inválido: valor {val} menor que o limite ({r_val}).")
            elif rule_type == "max":
                r_val = rule.get("value")
                if r_val is not None and val > r_val:
                    errors.append(f"{field} inválido: valor {val} maior que o limite ({r_val}).")

        return errors, warnings


def validar_registro(
    record: dict[str, Any],
    master_catalog: dict[str, Any] | None = None,
    logger: Any | None = None,
    # Parâmetros Legados para Consumidores:
    required_fields: list[str] | None = None,
    quality_rules: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """Valida o registro normalizado da ficha usando o Master Catalog ou fallback para legados."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando validação unificada do registro. CNPJ=%s",
                record.get("CNPJ"),
            )

        errors: list[str] = []
        warnings: list[str] = []

        if master_catalog and "fields" in master_catalog:
            # 1. LÓGICA DE GATES (Master Catalog)
            for field, config in master_catalog["fields"].items():
                if config.get("criticality") == "GATE_ENGINE":
                    if _is_empty(record.get(field)):
                        errors.append(f"GATE_ENGINE ausente: {field}")

            # 2. SANITY CHECK CONTÁBIL (Consistência)
            ativo_total = record.get("ATIVO_TOTAL_AJUSTADO")
            pl = record.get("PATRIMONIO_LIQUIDO")
            passivo_circulante = record.get("PASSIVO_CIRCULANTE_AJUSTADO")
            passivo_nao_circulante = record.get("PASSIVO_NAO_CIRCULANTE_FINANCEIRO_AJUSTADO")
            
            if ativo_total is not None and pl is not None:
                pc = float(passivo_circulante) if passivo_circulante is not None else 0.0
                pnc = float(passivo_nao_circulante) if passivo_nao_circulante is not None else 0.0
                
                passivo_exigivel = pc + pnc
                ativo_t = float(ativo_total)
                patrimonio = float(pl)
                
                diferenca = abs(ativo_t - (passivo_exigivel + patrimonio))
                if diferenca > (0.05 * ativo_t):
                    warnings.append(f"ALERTA_CONTABIL: Balanço não fecha. Ativo difere de Passivo+PL. (Diferença: {diferenca:.2f})")
        else:
            # Fallback Legacy (Consumidores)
            engine = DomainRuleEngine(quality_rules)
            err, warn = engine.validate(record, required_fields or [])
            errors.extend(err)
            warnings.extend(warn)

        if logger is not None:
            logger.info(
                "Validação concluída. CNPJ=%s ERROS=%s AVISOS=%s",
                record.get("CNPJ"),
                len(errors),
                len(warnings),
            )
            if errors:
                logger.warning("Erros de validação para CNPJ=%s: %s", record.get("CNPJ"), errors)
            if warnings:
                logger.warning("Avisos de validação para CNPJ=%s: %s", record.get("CNPJ"), warnings)

        return errors, warnings

    except Exception:
        if logger is not None:
            logger.exception("Falha inesperada na validação do registro. CNPJ=%s", record.get("CNPJ"))
        raise


def validar_registro_consumidor(
    record: dict[str, Any],
    required_fields: list[str],
    classificacao: Any | None = None,
    logger: Any | None = None,
    quality_rules: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """Valida o registro de consumidor com regras condicionais por tipo de análise.

    Estende a validação padrão com regras específicas de consumidores:
    - ≥5 MWm (detalhada): valida presença obrigatória dos campos financeiros.
    - <5 MWm (simplificada): valida que campos financeiros são NAO_APLICAVEL,
      e exige score de bureau.
    """
    # Validação base (universal)
    errors, warnings = validar_registro(
        record=record,
        required_fields=required_fields,
        logger=logger,
        quality_rules=quality_rules,
    )

    if classificacao is None:
        return errors, warnings

    tipo_analise = getattr(classificacao, "tipo_analise_exigida", None)

    if tipo_analise == "detalhada":
        # Validar presença de campos financeiros obrigatórios para ≥5 MWm
        campos_financeiros_obrigatorios = [
            "PATRIMONIO_LIQUIDO", "ATIVO_CIRCULANTE", "ATIVO_TOTAL",
            "PASSIVO_CIRCULANTE", "LUCRO_LIQUIDO",
            "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        ]
        for campo in campos_financeiros_obrigatorios:
            val = record.get(campo)
            if _is_empty(val):
                errors.append(
                    f"Campo financeiro obrigatório ausente para consumidor ≥5 MWm: {campo}"
                )

        # Auditor deve estar presente em análise detalhada
        if _is_empty(record.get("AUDITOR")):
            warnings.append("AUDITOR não informado para consumidor ≥5 MWm.")

    elif tipo_analise == "simplificada":
        # Score de bureau é obrigatório para <5 MWm
        if _is_empty(record.get("SCORE_BUREAU")):
            errors.append(
                "SCORE_BUREAU obrigatório para consumidor <5 MWm não informado."
            )

        # Campos financeiros devem ser NAO_APLICAVEL ou vazios
        campos_df = [
            "ATIVO_CIRCULANTE", "ATIVO_TOTAL", "PASSIVO_CIRCULANTE",
            "LUCRO_LIQUIDO", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS",
        ]
        for campo in campos_df:
            val = record.get(campo)
            if not _is_empty(val) and str(val).upper() != "NAO_APLICAVEL":
                warnings.append(
                    f"Campo {campo} preenchido em ficha simplificada (<5 MWm). "
                    f"Valor: {val}"
                )

    # Verificar compatibilidade ficha-segmento
    if hasattr(classificacao, "compatibilidade_ficha_segmento"):
        if not classificacao.compatibilidade_ficha_segmento:
            warnings.append(
                f"Incompatibilidade detectada: ficha para tipo "
                f"'{classificacao.tipo_consumidor}' não contém os dados esperados. "
                f"Confiança: {classificacao.confianca_classificacao}."
            )

    if logger is not None:
        logger.info(
            "Validação condicional concluída para %s. "
            "Tipo=%s ERROS=%s AVISOS=%s",
            record.get("CNPJ"),
            tipo_analise,
            len(errors),
            len(warnings),
        )

    return errors, warnings
```


---
## src\domain\garantias\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\garantias\garantia_model.py
Linhas: 27
Classes: GarantiaModel
Funções: -
```python
"""Modelo de dados formal para o domínio de Garantias."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class GarantiaModel:
    garantia_id: str
    cnpj_contraparte: str
    grupo_economico: Optional[str]
    contrato_vinculado: Optional[str]
    tipo: Optional[str]
    modalidade: Optional[str]
    garantidor_emissor: Optional[str]
    cnpj_garantidor: Optional[str]
    instituicao_financeira: Optional[str]
    beneficiario: Optional[str]
    valor_nominal: Optional[float]
    valor_atualizado: Optional[float]
    moeda: Optional[str]
    data_avaliacao: Optional[str]
    percentual_cobertura: Optional[float]
    data_inicio: Optional[str]
    vencimento: Optional[str]
    status: str
    elegibilidade: str
    data_ultima_validacao: Optional[str]
```


---
## src\domain\garantias\servico_garantia.py
Linhas: 178
Classes: GarantiaIngestionError
Funções: inserir_dados_garantias
```python
"""Serviço de ingestão, validação e alertas de Garantias.

Lê o CSV extraído da query customizada do Denodo, salva na Bronze,
valida regras de vigência e cobertura, gera alertas e publica na Silver.
Ref: §2 (Módulo Garantias), §6.8 do Planejamento Funcional.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from domain.enums import StatusGarantia
from storage.escrever_dados import escrever_conjunto_de_dados_silver

class GarantiaIngestionError(Exception):
    """Exceção levantada para falhas na ingestão de garantias."""

# Limiar mínimo de cobertura para disparo de alerta GAR_002 (§6.8)
COBERTURA_MINIMA = 0.5

def inserir_dados_garantias(
    context: AppContext,
    df_garantias_externo: pd.DataFrame | None = None,
) -> dict[str, Any]:
    run_id = f"GAR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__ingestao_garantias.log"
    logger = obter_logger("bdc.garantias", log_file)

    try:
        logger.info("Iniciando ingestão de Garantias (Modo CSV Local).")

        # --- Obtenção dos dados ---
        if df_garantias_externo is not None:
            df_raw = df_garantias_externo.copy()
            logger.info("Usando DataFrame externo fornecido.")
        else:
            input_dir = context.path("entradas") / "garantias"
            input_dir.mkdir(parents=True, exist_ok=True)

            arquivos = [
                f for f in input_dir.iterdir()
                if f.is_file() and f.suffix.lower() in {".xlsx", ".xls", ".csv"}
                and not f.name.startswith("~$")
            ]

            if not arquivos:
                logger.warning("Nenhum arquivo de garantias encontrado em %s.", input_dir)
                return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

            arquivo_fonte = max(arquivos, key=lambda f: f.stat().st_mtime)
            logger.info("Lendo garantias do arquivo local: %s", arquivo_fonte.name)

            if arquivo_fonte.suffix.lower() == ".csv":
                df_raw = pd.read_csv(arquivo_fonte, dtype=str, sep=";", encoding="utf-8-sig")
            else:
                df_raw = pd.read_excel(arquivo_fonte, dtype=str)

        if df_raw.empty:
            return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

        # 1. Snapshot na Bronze (Imutabilidade — §11.5)
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "garantias"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        caminho_bronze = bronze_dir / f"raw_garantias_{datetime.now().strftime('%Y%m%d')}.parquet"
        
        # Salva o Parquet cru na Bronze
        df_raw.to_parquet(caminho_bronze, index=False)

        # Padroniza as colunas em maiúsculo (pois o CSV veio em minúsculo da query)
        df_garantias = df_raw.copy()
        df_garantias.columns = [str(c).strip().upper() for c in df_garantias.columns]

        # Limpa CNPJ, converte Datas e Valores Numéricos
        df_garantias["CNPJ_CONTRAPARTE"] = (
            df_garantias["CNPJ_CONTRAPARTE"]
            .astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
        )
        # O CSV usa VENCIMENTO, não VIGENCIA_FIM
        df_garantias["VENCIMENTO"] = pd.to_datetime(df_garantias["VENCIMENTO"], errors="coerce")

        if "PERCENTUAL_COBERTURA" not in df_garantias.columns:
            df_garantias["PERCENTUAL_COBERTURA"] = 1.0
        else:
            df_garantias["PERCENTUAL_COBERTURA"] = pd.to_numeric(
                df_garantias["PERCENTUAL_COBERTURA"], errors="coerce"
            ).fillna(1.0)

        hoje = pd.Timestamp(datetime.now().date())
        alertas = []
        status_list = []

        # 2. Validação de Regras de Negócio e Geração de Alertas
        for _, row in df_garantias.iterrows():
            garantia_id = row.get("GARANTIA_ID")
            cnpj = row.get("CNPJ_CONTRAPARTE")
            data_fim = row.get("VENCIMENTO")
            cobertura = float(row.get("PERCENTUAL_COBERTURA", 1.0))

            # Regra: GAR_001 (Vencida ou Próxima do Vencimento — §6.8)
            dias_para_vencimento = (data_fim - hoje).days if pd.notnull(data_fim) else -1

            if dias_para_vencimento < 0:
                status_garantia = StatusGarantia.VENCIDA.value
                data_fmt = data_fim.strftime('%Y-%m-%d') if pd.notnull(data_fim) else "N/A"
                alertas.append({
                    "CODIGO": "GAR_001",
                    "CNPJ": cnpj,
                    "SEVERIDADE": "ALTO",
                    "MENSAGEM": f"Garantia {garantia_id} está vencida desde {data_fmt}."
                })
            elif 0 <= dias_para_vencimento <= 30:
                status_garantia = StatusGarantia.PROXIMA_VENCIMENTO.value
                alertas.append({
                    "CODIGO": "GAR_001",
                    "CNPJ": cnpj,
                    "SEVERIDADE": "MEDIO",
                    "MENSAGEM": f"Garantia {garantia_id} próxima do vencimento ({dias_para_vencimento} dias)."
                })
            else:
                status_garantia = StatusGarantia.VIGENTE.value

            # Regra: GAR_002 (Cobertura abaixo do mínimo — §6.8)
            if cobertura < COBERTURA_MINIMA:
                alertas.append({
                    "CODIGO": "GAR_002",
                    "CNPJ": cnpj,
                    "SEVERIDADE": "MEDIO",
                    "MENSAGEM": f"Garantia {garantia_id} com cobertura insuficiente ({cobertura*100:.1f}%)."
                })

            status_list.append(status_garantia)

        # Sobrescrevemos o status da query SQL caso o Python perceba que venceu hoje
        df_garantias["STATUS"] = status_list
        df_garantias["VENCIMENTO"] = df_garantias["VENCIMENTO"].dt.strftime("%Y-%m-%d")
        df_garantias["RUN_ID"] = run_id
        df_garantias["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        # 3. Gravação de Alertas e Fatos
        if alertas:
            df_alertas = pd.DataFrame(alertas)
            df_alertas["RUN_ID"] = run_id
            df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
            df_alertas["STATUS_ALERTA"] = "ABERTO"

            escrever_conjunto_de_dados_silver(
                records=df_alertas.to_dict(orient="records"),
                output_dir=context.path("silver") / "alertas_credito",
                filename=f"alertas_garantias_{run_id}"
            )
            logger.info("Gerados %s alertas de garantias (GAR_001 / GAR_002).", len(alertas))

        silver_dir = context.path("silver") / "garantias_silver"
        escrever_conjunto_de_dados_silver(
            records=df_garantias.to_dict(orient="records"),
            output_dir=silver_dir,
            filename="fato_garantia"
        )

        logger.info("Ingestão de garantias concluída. Registros salvos: %s", len(df_garantias))

        return {
            "run_id": run_id,
            "linhas_processadas": len(df_garantias),
            "alertas_gerados": len(alertas),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão de garantias.")
        raise GarantiaIngestionError(f"Erro ao ingerir base de garantias: {exc}") from exc
```


---
## src\domain\mtm\servico_mtm.py
Linhas: 142
Classes: MtmReconciliationError
Funções: inserir_dados_mtm
```python
"""Serviço de ingestão e agregação da base de MtM para as camadas Bronze e Silver.

fix(T2.2.2): Removida lógica duplicada (leitura antiga via MTM_NETWORK_PATH
que salvava Bronze duas vezes). Mantido apenas o fluxo via mtm_connector.
Ref: §3.5, §11.6 do Planejamento Funcional.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from services.connectors.mtm_connector import buscar_mtm_consolidado, _encontrar_arquivo_mtm_recente
from storage.escrever_dados import escrever_conjunto_de_dados_silver


class MtmReconciliationError(Exception):
    """Exceção para falhas na reconciliação de totais entre Bronze e Silver."""


def inserir_dados_mtm(context: AppContext) -> dict[str, Any]:
    """Orquestra a ingestão MtM: Bronze snapshot → Conector → Agregação → Reconciliação → Silver."""
    run_id = f"MTM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__ingestao_mtm.log"
    logger = obter_logger("bdc.mtm", log_file)

    try:
        logger.info("Iniciando processo de ingestão e agregação da base de MtM.")

        input_dir = context.path("entradas") / "mtm"
        arquivo_bruto = _encontrar_arquivo_mtm_recente(input_dir)

        # 1. Copia o snapshot bruto intacto para a Bronze (DoD T2.2.2 — §11.5)
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "mtm"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_mtm_{datetime.now().strftime('%Y%m%d')}_{arquivo_bruto.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(arquivo_bruto, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze)

        # 2. Leitura via Conector (T2.2.1)
        df_mtm = buscar_mtm_consolidado(input_dir=input_dir, logger=logger)

        if df_mtm.empty:
            logger.warning("Nenhum registro encontrado na base de MtM.")
            return {"run_id": run_id, "contrapartes_consolidadas": 0, "status": "SEM_DADOS"}

        # Captura totais originais para controle de reconciliação
        soma_mtm_orig = float(df_mtm["MTM_TOTAL"].sum())
        soma_not_orig = float(df_mtm["NOTIONAL"].sum())

        # 3. Agregação por contraparte (CNPJ) e DATA_BASE para a Silver
        if "DATA_BASE" not in df_mtm.columns:
            df_mtm["DATA_BASE"] = datetime.now().strftime("%Y-%m-%d")

        df_agregado = (
            df_mtm.groupby(["CNPJ", "CNPJ_RAIZ", "DATA_BASE"], as_index=False)
            .agg({
                "MTM_TOTAL": "sum",
                "NOTIONAL": "sum"
            })
            .rename(columns={
                "MTM_TOTAL": "MTM_TOTAL_NETTED",
                "NOTIONAL": "NOTIONAL_TOTAL"
            })
        )

        # Netting aplicado: derivar colunas positivo/negativo APÓS a soma por contraparte
        df_agregado["MTM_POSITIVO_TOTAL"] = df_agregado["MTM_TOTAL_NETTED"].apply(
            lambda x: x if x > 0 else 0.0
        )
        df_agregado["MTM_NEGATIVO_TOTAL"] = df_agregado["MTM_TOTAL_NETTED"].apply(
            lambda x: abs(x) if x < 0 else 0.0
        )

        # Preserva STATUS_CNPJ (descartado pelo groupby) reinserindo via merge
        if "STATUS_CNPJ" in df_mtm.columns:
            status_map = df_mtm[["CNPJ", "STATUS_CNPJ"]].drop_duplicates(subset=["CNPJ"])
            df_agregado = pd.merge(df_agregado, status_map, on="CNPJ", how="left")

        # 4. Reconciliação de integridade entre Bronze e Silver (§11.6)
        # Compara apenas MTM_TOTAL e NOTIONAL brutos (soma algébrica), pois
        # as colunas positivo/negativo pós-netting não têm equivalência linear
        # com os valores linha a linha da origem.
        reconciliation_config = context.config.get("reconciliacao_mtm", {})
        tolerancia = reconciliation_config.get("tolerancia_absoluta", 0.01)

        soma_mtm_silver = float(df_agregado["MTM_TOTAL_NETTED"].sum())
        soma_not_silver = float(df_agregado["NOTIONAL_TOTAL"].sum())

        checks = [
            ("MTM Total", soma_mtm_orig, soma_mtm_silver),
            ("Notional Total", soma_not_orig, soma_not_silver),
        ]
        for label, original, silver in checks:
            diff = abs(original - silver)
            if diff > tolerancia:
                raise MtmReconciliationError(
                    f"Divergência de reconciliação no {label}! "
                    f"Original: {original} vs Silver: {silver} (Diff: {diff} > Tolerância: {tolerancia})"
                )

        df_agregado["RUN_ID"] = run_id
        df_agregado["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        records = df_agregado.to_dict(orient="records")

        # 5. Persistência na Silver (CSV + Parquet) — versionado por run_id (§1.5)
        silver_output_dir = context.path("silver") / "mtm_consolidado_silver"
        csv_path, parquet_path = escrever_conjunto_de_dados_silver(
            records=records,
            output_dir=silver_output_dir,
            filename=f"mtm_agregado_contraparte_{run_id}"
        )

        # Ponteiro LATEST para consumo downstream (preserva versão anterior)
        latest_path = silver_output_dir / "mtm_agregado_contraparte.parquet"
        if latest_path.exists():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(latest_path, silver_output_dir / f"mtm_agregado_contraparte_HIST_{ts}.parquet")
        shutil.copy2(parquet_path, latest_path)

        return {
            "run_id": run_id,
            "linhas_processadas": len(df_mtm),
            "contrapartes_consolidadas": len(records),
            "soma_mtm_total_netted": soma_mtm_silver,
            "soma_mtm_positivo_total": float(df_agregado["MTM_POSITIVO_TOTAL"].sum()),
            "soma_mtm_negativo_total": float(df_agregado["MTM_NEGATIVO_TOTAL"].sum()),
            "soma_notional_total": soma_not_silver,
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão/reconciliação do MtM.")
        raise
```


---
## src\gold\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\gold\service_gold.py
Linhas: 347
Classes: -
Funções: exportar_visao_consolidada_gold, resolver_situacao_df, resolver_situacao_analise, classificar_exigencia, status_metodologia
```python
# -*- coding: utf-8 -*-
"""
Serviço da Camada Gold.
Responsável por realizar o Master Join entre Contratos (Denodo), Fichas (Análise), Risco (MtM), e Cadastro.
Aplica as agregações mensais de volume e regras de negócio temporais para criar a Tabela Analítica Oficial.
"""

import logging
from pathlib import Path
from typing import Any
import pandas as pd
from datetime import datetime

from silver.normalizadores import padronizar_cnpj

LOGGER = logging.getLogger(__name__)

def exportar_visao_consolidada_gold(context: Any) -> dict[str, Any]:
    logger = logging.getLogger("bdc.gold")
    logger.info("Construindo Visão Consolidada Gold (Master Join)...")
    hoje = pd.Timestamp("today").normalize()

    # 1. Resolução de Caminhos (Paths)
    silver_dir = Path("SAIDAS/silver")
    rel_dim_dir = Path("SAIDAS/relational/dimensions")
    rel_fact_dir = Path("SAIDAS/relational/facts")
    gold_dir = Path("SAIDAS/gold/visao_operacional_negocio")
    gold_dir.mkdir(parents=True, exist_ok=True)

    path_contraparte = rel_dim_dir / "dim_contraparte.parquet"
    path_contratos = silver_dir / "denodo_contratos_silver" / "contratos_correntes.parquet"
    if not path_contratos.exists():
        path_contratos = silver_dir / "denodo_contratos_padronizados" / "contratos_correntes.parquet"
        
    path_risco = rel_fact_dir / "fato_exposicao_risco_LATEST.parquet"
    if not path_risco.exists():
        path_risco = silver_dir / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"

    path_analises = rel_fact_dir / "fato_analise_credito.parquet"
    
    # Bloqueio de Falha Segura
    if not path_contratos.exists():
        logger.critical("Bloqueio de Falha Segura: Base Silver de contratos não encontrada (%s).", path_contratos)
        raise FileNotFoundError(f"Base crítica de contratos inexistente na Silver: {path_contratos}")

    # 2. Carregamento dos Datasets
    df_contraparte = pd.read_parquet(path_contraparte) if path_contraparte.exists() else pd.DataFrame()
    df_contratos = pd.read_parquet(path_contratos) if path_contratos.exists() else pd.DataFrame()
    df_analises = pd.read_parquet(path_analises) if path_analises.exists() else pd.DataFrame()
    df_risco = pd.read_parquet(path_risco) if path_risco.exists() else pd.DataFrame()

    # 3. Master Join (Âncora na Dimensão Contraparte para garantir volumetria total)
    if not df_contraparte.empty:
        parsed_ct = df_contraparte["CNPJ"].map(padronizar_cnpj)
        df_contraparte["CNPJ"]      = parsed_ct.map(lambda t: t[0])
        df_contraparte["CNPJ_RAIZ"] = parsed_ct.map(lambda t: t[1])
        df_contraparte = df_contraparte[parsed_ct.map(lambda t: t[2]) == "CNPJ_VALIDO"]
        cols_contra = [c for c in ["CNPJ", "CNPJ_RAIZ", "SIGLA", "NOME", "SEGMENTO_METODOLOGICO", "SITUACAO_CADASTRAL"] if c in df_contraparte.columns]
        df_gold = df_contraparte[cols_contra].copy()
    else:
        df_gold = pd.DataFrame(columns=["CNPJ", "CNPJ_RAIZ", "SEGMENTO_METODOLOGICO"])

    # 4. Agregação das Análises (Fichas) com Cascata CNPJ 14 dígitos -> CNPJ Raiz 8 dígitos (Matriz/Filial)
    if not df_analises.empty:
        parsed_an = df_analises["CNPJ"].map(padronizar_cnpj)
        df_analises["CNPJ"]      = parsed_an.map(lambda t: t[0])
        df_analises["CNPJ_RAIZ"] = parsed_an.map(lambda t: t[1])
        
        # Mapeamento e normalização flexível de nomes de colunas (Silver / Fato)
        if "DATA_CALCULO" in df_analises.columns and "DATA_ANALISE" not in df_analises.columns:
            df_analises["DATA_ANALISE"] = df_analises["DATA_CALCULO"]
        if "DATA_DEMONSTRACAO_FINANCEIRA" in df_analises.columns and "DATA_BALANCO_USADO" not in df_analises.columns:
            df_analises["DATA_BALANCO_USADO"] = df_analises["DATA_DEMONSTRACAO_FINANCEIRA"]
        if "DATA_DF" in df_analises.columns and "DATA_BALANCO_USADO" not in df_analises.columns:
            df_analises["DATA_BALANCO_USADO"] = df_analises["DATA_DF"]
            
        if "RATING" in df_analises.columns and "RATING_FINAL" not in df_analises.columns:
            df_analises["RATING_FINAL"] = df_analises["RATING"]
        if "RATING_COPEL" in df_analises.columns and "RATING_FINAL" not in df_analises.columns:
            df_analises["RATING_FINAL"] = df_analises["RATING_COPEL"]
            
        if "PD_PERCENTUAL" in df_analises.columns and "PD_FINAL" not in df_analises.columns:
            df_analises["PD_FINAL"] = df_analises["PD_PERCENTUAL"]
        if "PD" in df_analises.columns and "PD_FINAL" not in df_analises.columns:
            df_analises["PD_FINAL"] = df_analises["PD"]
            
        if "MODELO" in df_analises.columns and "MODELO_METODOLOGICO" not in df_analises.columns:
            df_analises["MODELO_METODOLOGICO"] = df_analises["MODELO"]
        if "versao_ficha" in df_analises.columns and "MODELO_METODOLOGICO" not in df_analises.columns:
            df_analises["MODELO_METODOLOGICO"] = df_analises["versao_ficha"]

        # Ordena para pegar a análise mais recente por CNPJ
        col_sort = "DATA_ANALISE" if "DATA_ANALISE" in df_analises.columns else ("DATA_BALANCO_USADO" if "DATA_BALANCO_USADO" in df_analises.columns else "CNPJ")
        if col_sort in df_analises.columns and col_sort != "CNPJ":
            df_analises["_DT_SORT"] = pd.to_datetime(df_analises[col_sort], errors="coerce")
            df_analises = df_analises.sort_values("_DT_SORT", na_position="first").drop_duplicates("CNPJ", keep="last")
        else:
            df_analises = df_analises.drop_duplicates("CNPJ", keep="last")

        # Cálculo da validade temporal da Ficha de Crédito (Metodologia BDC / Copel)
        # Regra: DF + 16 meses (1 ano e 4 meses) ou Data da Análise + 12 meses (1 ano)
        dt_balanco = pd.to_datetime(df_analises.get("DATA_BALANCO_USADO"), errors="coerce")
        dt_analise = pd.to_datetime(df_analises.get("DATA_ANALISE"), errors="coerce")
        
        mask_balanco = (dt_balanco.dt.year > 1900) & (dt_balanco.notna())
        mask_analise = (dt_analise.dt.year > 1900) & (dt_analise.notna())
        
        df_analises["VALIDADE_DT"] = pd.NaT
        df_analises.loc[mask_balanco, "VALIDADE_DT"] = dt_balanco.loc[mask_balanco] + pd.DateOffset(years=1, months=4)
        df_analises.loc[~mask_balanco & mask_analise, "VALIDADE_DT"] = dt_analise.loc[~mask_balanco & mask_analise] + pd.DateOffset(years=1)

        # Determinação da SITUACAO_ANALISE para as fichas existentes
        if "SITUACAO_ANALISE" not in df_analises.columns:
            df_analises["SITUACAO_ANALISE"] = df_analises["VALIDADE_DT"].apply(
                lambda dt: "VIGENTE" if pd.notnull(dt) and dt >= hoje else ("VENCIDA" if pd.notnull(dt) else "VENCIDA")
            )
        else:
            mask_null = df_analises["SITUACAO_ANALISE"].isna() | (df_analises["SITUACAO_ANALISE"].astype(str).str.strip().isin(["", "None", "nan", "<NA>"]))
            df_analises.loc[mask_null, "SITUACAO_ANALISE"] = df_analises.loc[mask_null, "VALIDADE_DT"].apply(
                lambda dt: "VIGENTE" if pd.notnull(dt) and dt >= hoje else ("VENCIDA" if pd.notnull(dt) else "VENCIDA")
            )

        # Determinação da SITUACAO_DF para as fichas existentes
        if "SITUACAO_DF" not in df_analises.columns:
            df_analises["SITUACAO_DF"] = "RECEBIDA"
        else:
            df_analises["SITUACAO_DF"] = df_analises["SITUACAO_DF"].fillna("RECEBIDA")

        # Garante flag TEM_ANALISE
        df_analises["TEM_ANALISE"] = "SIM"
            
        cols_analise_payload = [
            c for c in [
                "SITUACAO_ANALISE", "SITUACAO_DF", "RATING_FINAL", "PD_FINAL", 
                "MODELO_METODOLOGICO", "PATRIMONIO_LIQUIDO", "DATA_ANALISE", "DATA_BALANCO_USADO", "TEM_ANALISE"
            ] if c in df_analises.columns
        ]

        # 4.1. MATCHING PRIMÁRIO: Cruzamento exato pelo CNPJ de 14 dígitos
        df_gold = pd.merge(
            df_gold, 
            df_analises[["CNPJ"] + cols_analise_payload], 
            on="CNPJ", 
            how="left"
        )

        # 4.2. MATCHING SECUNDÁRIO (FALLBACK): Herança de Análise da Matriz para Filiais por CNPJ_RAIZ
        # Identifica e prioriza a Ficha da Matriz (final 0001) e/ou a ficha mais recente da mesma raiz
        df_analises["_EH_MATRIZ"] = df_analises["CNPJ"].str[8:12] == "0001"
        sort_raiz = ["_EH_MATRIZ"]
        if "_DT_SORT" in df_analises.columns:
            sort_raiz.append("_DT_SORT")
            
        df_analises_raiz = (
            df_analises.sort_values(sort_raiz, ascending=[True] * len(sort_raiz))
            .drop_duplicates(subset=["CNPJ_RAIZ"], keep="last")
        )
        
        df_fallback = df_analises_raiz[["CNPJ_RAIZ"] + cols_analise_payload].copy()
        df_fallback.columns = ["CNPJ_RAIZ"] + [f"{c}_RAIZ" for c in cols_analise_payload]

        df_gold = pd.merge(df_gold, df_fallback, on="CNPJ_RAIZ", how="left")

        # 4.3. COMBINAÇÃO E HERANÇA: Preenche filiais sem análise com os dados consolidados da Matriz
        for col in cols_analise_payload:
            col_raiz = f"{col}_RAIZ"
            if col_raiz in df_gold.columns:
                df_gold[col] = df_gold[col].combine_first(df_gold[col_raiz])
                df_gold = df_gold.drop(columns=[col_raiz])
    
    if "TEM_ANALISE" not in df_gold.columns:
        df_gold["TEM_ANALISE"] = "NÃO"
    df_gold["TEM_ANALISE"] = df_gold["TEM_ANALISE"].fillna("NÃO")

    # 5. Matemática de Contratos e Agregação de Volume (Enquadramento MWm)
    if not df_contratos.empty:
        parsed_ctr = df_contratos["CNPJ"].map(padronizar_cnpj)
        df_contratos["CNPJ"]      = parsed_ctr.map(lambda t: t[0])
        df_contratos["CNPJ_RAIZ"] = parsed_ctr.map(lambda t: t[1])
        df_contratos = df_contratos[parsed_ctr.map(lambda t: t[2]) == "CNPJ_VALIDO"].copy()

        col_vol = "VOLUME_CONTRATADO_MENSAL_MWM" if "VOLUME_CONTRATADO_MENSAL_MWM" in df_contratos.columns else "VOLUME_MWM"
        if col_vol in df_contratos.columns:
            df_contratos["VOLUME_MWM"] = pd.to_numeric(df_contratos[col_vol], errors="coerce").fillna(0.0)
        else:
            df_contratos["VOLUME_MWM"] = 0.0
        
        # AGREGAÇÃO REGRA DE NEGÓCIO: Soma as competências (Ano/Mês) de contratos paralelos, depois acha o MÁXIMO daquele CNPJ
        if "ano" in df_contratos.columns and "mes" in df_contratos.columns:
            df_mensal = df_contratos.groupby(["CNPJ_RAIZ", "ano", "mes"], as_index=False)["VOLUME_MWM"].sum()
            df_vol_enquadramento = df_mensal.groupby("CNPJ_RAIZ", as_index=False)["VOLUME_MWM"].max()
        else:
            df_vol_enquadramento = df_contratos.groupby("CNPJ_RAIZ", as_index=False)["VOLUME_MWM"].max()

        # Busca das colunas de temporalidade
        col_id = "CONTRATO" if "CONTRATO" in df_contratos.columns else "CONTRATO_ID"
        col_in = "SUPRIMENTO_INICIO"
        if col_in not in df_contratos.columns:
            col_in = "VIGENCIA_INICIO" if "VIGENCIA_INICIO" in df_contratos.columns else "inicio_suprimento"
            
        col_out = "SUPRIMENTO_TERMINO"
        if col_out not in df_contratos.columns:
            col_out = "VIGENCIA_FIM" if "VIGENCIA_FIM" in df_contratos.columns else "fim_suprimento"

        df_contratos["DT_INICIO"] = pd.to_datetime(df_contratos.get(col_in), errors="coerce")
        df_contratos["DT_FIM"] = pd.to_datetime(df_contratos.get(col_out), errors="coerce")
        
        # Avalia se a janela de datas do contrato envolve o dia de Hoje
        df_contratos["EH_VIGENTE"] = (
            (df_contratos.get("STATUS", df_contratos.get("id_status", "")).astype(str).str.upper().str.contains("ATIVO|EM SUPRIMENTO|2")) &
            (df_contratos["DT_INICIO"] <= hoje) &
            (df_contratos["DT_FIM"] >= hoje)
        )
        df_contratos["EH_FUTURO"] = (df_contratos["DT_INICIO"] > hoje)

        resumo_contratos = df_contratos.groupby("CNPJ").agg(
            QTD_CONTRATOS=(col_id, "nunique") if col_id in df_contratos.columns else ("CNPJ", "count"),
            STATUS_CONTRATUAL=("EH_VIGENTE", lambda x: "CONTRATO_VIGENTE" if x.any() else ("CONTRATO_FUTURO" if df_contratos.loc[x.index, "EH_FUTURO"].any() else "SEM_CONTRATO")),
            PROXIMO_INICIO=("DT_INICIO", "min"),
            PROXIMO_FIM=("DT_FIM", "max")
        ).reset_index()

        resumo_contratos["CNPJ_RAIZ"] = resumo_contratos["CNPJ"].str[:8]
        df_contratos_gold = pd.merge(resumo_contratos, df_vol_enquadramento[["CNPJ_RAIZ", "VOLUME_MWM"]], on="CNPJ_RAIZ", how="left")
        df_gold = pd.merge(df_gold, df_contratos_gold, on="CNPJ", how="left")
    else:
        df_gold["STATUS_CONTRATUAL"] = "SEM_CONTRATO"
        df_gold["VOLUME_MWM"] = 0.0
        
    df_gold["TEM_CONTRATO"] = df_gold["STATUS_CONTRATUAL"].apply(lambda x: "SIM" if x in ["CONTRATO_VIGENTE", "CONTRATO_FUTURO"] else "NÃO")

    # 6. Agregação de Risco / Exposição (MtM)
    if not df_risco.empty:
        parsed_risco = df_risco["CNPJ"].map(padronizar_cnpj)
        df_risco["CNPJ"] = parsed_risco.map(lambda t: t[0])
        df_risco = df_risco[parsed_risco.map(lambda t: t[2]) == "CNPJ_VALIDO"]
        df_risco = df_risco.drop_duplicates(subset=["CNPJ"], keep="last")
        
        if "PE_REAIS" in df_risco.columns:
            cols_risco = [c for c in ["CNPJ", "EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"] if c in df_risco.columns]
            df_gold = pd.merge(df_gold, df_risco[cols_risco], on="CNPJ", how="left")
        else:
            # Fallback direto da silver mtm
            col_mtm = "FINANCEIRO_MTM" if "FINANCEIRO_MTM" in df_risco.columns else ("MTM" if "MTM" in df_risco.columns else None)
            if col_mtm:
                df_gold = pd.merge(df_gold, df_risco[["CNPJ", col_mtm]].rename(columns={col_mtm: "EAD_VALOR"}), on="CNPJ", how="left")
                df_gold["PE_REAIS"] = 0.0

    # 7. Tratamento Final e Enquadramento Metodológico
    # Em vez de preencher com zero ou N/A, garantimos a integridade de NULOS VERDADEIROS e Governança
    colunas_esperadas = [
        "VOLUME_MWM", "EAD_VALOR", "PE_REAIS", "PATRIMONIO_LIQUIDO", "QTD_CONTRATOS", 
        "STATUS_CONTRATUAL", "SITUACAO_ANALISE", "SITUACAO_DF", "SITUACAO_CADASTRAL"
    ]
    for col in colunas_esperadas:
        if col not in df_gold.columns:
            df_gold[col] = pd.NA  # Nulo verdadeiro

    # Preenche STATUS_CONTRATUAL e SITUACAO_CADASTRAL onde realmente ausente
    df_gold["STATUS_CONTRATUAL"] = df_gold["STATUS_CONTRATUAL"].fillna("SEM_CONTRATO")
    df_gold["SITUACAO_CADASTRAL"] = df_gold["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADA")

    # Tratamento de governança para contrapartes SEM FICHA (TEM_ANALISE == "NÃO")
    def resolver_situacao_df(row):
        sit = row.get("SITUACAO_DF")
        if pd.notna(sit) and str(sit).strip() not in ["", "None", "nan", "<NA>"]:
            return sit
        
        status_ct = row.get("STATUS_CONTRATUAL")
        if status_ct in ["CONTRATO_VIGENTE", "CONTRATO_FUTURO"]:
            vol = pd.to_numeric(row.get("VOLUME_MWM"), errors='coerce')
            if pd.isna(vol): vol = 0.0
            if vol >= 5.0:
                return "NAO_RECEBIDA"
            else:
                return "NAO_APLICAVEL"
        return pd.NA

    def resolver_situacao_analise(row):
        sit = row.get("SITUACAO_ANALISE")
        if pd.notna(sit) and str(sit).strip() not in ["", "None", "nan", "<NA>"]:
            return sit
            
        status_ct = row.get("STATUS_CONTRATUAL")
        if status_ct in ["CONTRATO_VIGENTE", "CONTRATO_FUTURO"]:
            vol = pd.to_numeric(row.get("VOLUME_MWM"), errors='coerce')
            if pd.isna(vol): vol = 0.0
            if vol >= 5.0:
                return "IRREGULAR"  # Exigência de DF >= 5MWm sem ficha processada
        return pd.NA  # Nulo verdadeiro para demais casos sem ficha

    df_gold["SITUACAO_DF"] = df_gold.apply(resolver_situacao_df, axis=1)
    df_gold["SITUACAO_ANALISE"] = df_gold.apply(resolver_situacao_analise, axis=1)

    def classificar_exigencia(row):
        if row.get("STATUS_CONTRATUAL") == "SEM_CONTRATO": return "NAO_APLICAVEL"
        vol = pd.to_numeric(row.get("VOLUME_MWM"), errors='coerce')
        if pd.isna(vol): vol = 0.0
        return "DF_DETALHADA" if vol >= 5 else "BUREAU"
        
    df_gold["METODOLOGIA_EXIGIDA"] = df_gold.apply(classificar_exigencia, axis=1)
    
    def status_metodologia(row):
        if row.get("METODOLOGIA_EXIGIDA") == "NAO_APLICAVEL": return "NAO_APLICAVEL"
        sit_analise = str(row.get("SITUACAO_ANALISE") or "").upper()
        if sit_analise == "VIGENTE": return "COMPLIANT"
        if sit_analise == "VENCIDA": return "VENCIDA (ALERTA)"
        return "PENDENTE"

    df_gold["STATUS_METODOLOGIA"] = df_gold.apply(status_metodologia, axis=1)

    # 8. Exportação dos Arquivos da Visão
    out_parquet = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.parquet"
    out_latest = gold_dir / "Visao_Operacional_BDC_LATEST.parquet"
    out_csv = gold_dir / f"Visao_Operacional_BDC_{hoje.strftime('%Y%m%d')}.csv"
    
    df_gold.to_parquet(out_parquet, index=False)
    df_gold.to_parquet(out_latest, index=False)
    # Formatação especial do CSV para abrir no Excel do Brasil perfeitamente
    df_gold.to_csv(out_csv, index=False, sep=";", decimal=",", encoding="utf-8-sig")

    logger.info("Visão Gold gerada. Total Contrapartes consolidadas: %d", len(df_gold))

    # 9. Retorno do Dicionário Matemático de KPIs para Orquestrador
    sit_analise = df_gold["SITUACAO_ANALISE"].fillna("").astype(str)
    met_exigida  = df_gold["METODOLOGIA_EXIGIDA"].fillna("").astype(str)
    stat_ctr     = df_gold["STATUS_CONTRATUAL"].fillna("").astype(str)

    mask_descoberto     = (stat_ctr == "CONTRATO_VIGENTE") & (sit_analise != "VIGENTE")
    mask_irregular      = (stat_ctr == "CONTRATO_VIGENTE") & (met_exigida == "DF_DETALHADA") & (sit_analise != "VIGENTE")
    mask_pendente_bureau = (stat_ctr == "CONTRATO_VIGENTE") & (met_exigida == "BUREAU")      & (sit_analise != "VIGENTE")

    return {
        "status": "SUCESSO",
        "total_contrapartes": len(df_gold),
        "contrato_vigente": int((df_gold["STATUS_CONTRATUAL"] == "CONTRATO_VIGENTE").sum()),
        "contrato_futuro": int((df_gold["STATUS_CONTRATUAL"] == "CONTRATO_FUTURO").sum()),
        "analise_vigente": int((df_gold["SITUACAO_ANALISE"].fillna("").astype(str) == "VIGENTE").sum()),
        "analise_vencida": int((df_gold["SITUACAO_ANALISE"].fillna("").astype(str) == "VENCIDA").sum()),
        "contrato_vig_sem_analise_vig": int(mask_descoberto.sum()),
        "contrato_irregular_sem_df": int(mask_irregular.sum()),
        "contrato_pendente_bureau": int(mask_pendente_bureau.sum()),
        "ficha_sem_contrato": int(((df_gold["TEM_ANALISE"] == "SIM") & (df_gold["STATUS_CONTRATUAL"] == "SEM_CONTRATO")).sum()),
        "contrato_sem_ficha": int(((df_gold["STATUS_CONTRATUAL"].isin(["CONTRATO_VIGENTE", "CONTRATO_FUTURO"])) & (df_gold["TEM_ANALISE"] == "NÃO")).sum()),
        "dados_incompletos": int((df_gold["SITUACAO_CADASTRAL"].isin(["NAO_INFORMADA", "PENDENTE"])).sum()),
        "ead_descoberto": float(df_gold.loc[mask_irregular, "EAD_VALOR"].sum(skipna=True)),
    }
```


---
## src\staging\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Camada de staging do sistema BDC."""

```


---
## src\staging\descoberta.py
Linhas: 18
Classes: -
Funções: detectar_arquivos_excel_pendentes
```python
"""Descoberta de arquivos pendentes para processamento."""

from __future__ import annotations

from pathlib import Path


def detectar_arquivos_excel_pendentes(input_dir: str | Path) -> list[Path]:
    """Lista arquivos Excel pendentes em um diretório."""
    base_dir = Path(input_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    return sorted(
        file_path
        for file_path in base_dir.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower() in {".xlsx", ".xlsm", ".xls"}
    )

```


---
## src\staging\staging_arquivo.py
Linhas: 21
Classes: -
Funções: copiar_para_staging
```python
"""Cópia de arquivos para a área de staging do sistema."""

from __future__ import annotations

import shutil
from pathlib import Path


def copiar_para_staging(
    source_file: str | Path,
    staging_dir: str | Path,
    target_name: str,
) -> Path:
    """Copia um arquivo para o staging com nome técnico."""
    source_path = Path(source_file)
    target_dir = Path(staging_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / target_name
    shutil.copy2(source_path, target_path)
    return target_path

```


---
## src\storage\bronze_arquivo.py
Linhas: 20
Classes: -
Funções: publicar_arquivo_bruto
```python
"""Publicação de arquivos válidos na camada bronze."""

from __future__ import annotations

import shutil
from pathlib import Path


def publicar_arquivo_bruto(
    source_file: str | Path,
    bronze_root_dir: str | Path,
) -> Path:
    """Publica um arquivo na camada bronze."""
    source_path = Path(source_file)
    target_dir = Path(bronze_root_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / source_path.name
    shutil.copy2(source_path, target_path)
    return target_path

```


---
## src\storage\escrever_dados.py
Linhas: 159
Classes: -
Funções: _normalize_filename, escrever_conjunto_de_dados_silver, mesclar_conjunto_de_dados_prata_por_chave_de_negocio
```python
"""Persistência de datasets padronizados da camada silver."""

from pathlib import Path
import pandas as pd
from typing import Any, Dict, List, Union

_KNOWN_EXTENSIONS = (".parquet", ".csv")

def _normalize_filename(filename: str) -> str:
    """
    Remove extensões conhecidas (.csv, .parquet) do filename recebido,
    evitando duplicação como 'arquivo.csv.csv'.
    """
    stem = filename.strip()
    for ext in _KNOWN_EXTENSIONS:
        if stem.lower().endswith(ext):
            stem = stem[: -len(ext)]
            break
    return stem

def escrever_conjunto_de_dados_silver(
    records: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    filename: str,
    sep: str = ";",
    decimal: str = ",",
    encoding: str = "utf-8-sig",
) -> tuple[Path, Path]:
    """Persiste a lista de registros normalizados em CSV e Parquet."""
    filename = _normalize_filename(filename)

    if not records:
        csv_path = Path(output_dir) / f"{filename}.csv"
        parquet_path = Path(output_dir) / f"{filename}.parquet"
        return csv_path, parquet_path

    df = pd.DataFrame(records)

    # Conversão segura de tipos blindada para o PyArrow não quebrar
    for col in df.columns:
        if "data" in col.lower() or "date" in col.lower() or col.lower().startswith("dt_") or col.startswith("_DT_"):
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif not (pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col])):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    csv_path = target_dir / f"{filename}.csv"
    parquet_path = target_dir / f"{filename}.parquet"

    df.to_csv(csv_path, index=False, sep=sep, decimal=decimal, encoding=encoding)
    df.to_parquet(parquet_path, index=False, engine="pyarrow", compression="snappy")

    return csv_path, parquet_path

def mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
    records: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    filename: str,
    business_keys: List[str],
    sep: str = ";",
    decimal: str = ",",
    encoding: str = "utf-8-sig",
) -> tuple[Path, Path]:
    """
    Realiza o merge incremental preservando histórico completo (SCD Tipo 2).
    Garante o versionamento sequencial de chaves de negócio duplicadas.
    """
    filename = _normalize_filename(filename)
    target_dir = Path(output_dir)
    parquet_path = target_dir / f"{filename}.parquet"

    if not records:
        return parquet_path, parquet_path

    df_new = pd.DataFrame(records)
    df_new["_DT_CARGA"] = pd.Timestamp.now()

    # PRÉ-PROCESSAMENTO: Aplica as coerções de datas do sistema
    for col in df_new.columns:
        if "data" in col.lower() or "date" in col.lower() or col.lower().startswith("dt_"):
            df_new[col] = pd.to_datetime(df_new[col], errors="coerce")

    if parquet_path.exists():
        df_existing = pd.read_parquet(parquet_path)

        # Garante colunas de controle no histórico legado
        if "_VERSAO_REGISTRO" not in df_existing.columns:
            df_existing["_VERSAO_REGISTRO"] = 1
            
        if "_DT_CARGA" not in df_existing.columns:
            df_existing["_DT_CARGA"] = pd.NaT
        else:
            df_existing["_DT_CARGA"] = pd.to_datetime(df_existing["_DT_CARGA"], errors="coerce")
            
        if "_STATUS_REGISTRO" not in df_existing.columns:
            df_existing["_STATUS_REGISTRO"] = "VIGENTE"

        # BLINDAGEM DE TIPOS NA CHAVE DE NEGÓCIO
        for b_key in business_keys:
            if b_key in df_existing.columns and b_key in df_new.columns:
                if pd.api.types.is_datetime64_any_dtype(df_existing[b_key]) and not pd.api.types.is_datetime64_any_dtype(df_new[b_key]):
                    df_new[b_key] = pd.to_datetime(df_new[b_key], errors="coerce")
                elif not pd.api.types.is_datetime64_any_dtype(df_existing[b_key]) and pd.api.types.is_datetime64_any_dtype(df_new[b_key]):
                    df_existing[b_key] = pd.to_datetime(df_existing[b_key], errors="coerce")
                else:
                    df_new[b_key] = df_new[b_key].astype(df_existing[b_key].dtype)

        df_existing_keys = df_existing[business_keys].drop_duplicates()
        df_new_keys = df_new[business_keys].drop_duplicates()
        
        # Rebaixa o status das chaves de negócio que sofrerão atualização
        keys_to_replace = pd.merge(df_existing_keys, df_new_keys, on=business_keys, how='inner')
        if not keys_to_replace.empty:
            cond_atualizacao = df_existing.set_index(business_keys).index.isin(keys_to_replace.set_index(business_keys).index)
            df_existing.loc[cond_atualizacao, "_STATUS_REGISTRO"] = "SUBSTITUIDO"

        max_versoes = (
            df_existing.groupby(business_keys, dropna=False)["_VERSAO_REGISTRO"]
            .max()
            .reset_index()
            .rename(columns={"_VERSAO_REGISTRO": "_MAX_VERSAO"})
        )

        df_new = pd.merge(df_new, max_versoes, on=business_keys, how="left")
        df_new["_MAX_VERSAO"] = df_new["_MAX_VERSAO"].fillna(0).astype(int)
    else:
        df_existing = pd.DataFrame()
        df_new["_MAX_VERSAO"] = 0

    # ORDENAÇÃO CRONOLÓGICA PARA GARANTIR SEQUÊNCIA EXATA
    if "dt_processamento" in df_new.columns:
        df_new = df_new.sort_values(by=business_keys + ["dt_processamento"])

    # VERSIONAMENTO ATÔMICO DA SILVER: Resolve o BUG AMBAR
    df_new["rank_interno"] = df_new.groupby(business_keys).cumcount() + 1
    df_new["_VERSAO_REGISTRO"] = df_new["_MAX_VERSAO"] + df_new["rank_interno"]
    df_new = df_new.drop(columns=["_MAX_VERSAO", "rank_interno"])

    # STATUS
    df_new["_STATUS_REGISTRO"] = "SUBSTITUIDO"
    idx_vigentes = df_new.groupby(business_keys)["_VERSAO_REGISTRO"].idxmax()
    df_new.loc[idx_vigentes, "_STATUS_REGISTRO"] = "VIGENTE"

    if not df_existing.empty:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    # Exportamos direto pro to_dict nativo; o write_silver cuidará das tipagens de volta.
    return escrever_conjunto_de_dados_silver(
        records=df_combined.to_dict(orient="records"),
        output_dir=output_dir,
        filename=filename,
        sep=sep,
        decimal=decimal,
        encoding=encoding
    )
```
