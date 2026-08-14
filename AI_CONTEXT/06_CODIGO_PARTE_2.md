# CÓDIGO PARTE 2


---
## main.py
Linhas: 198
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

# 1. PRIMEIRO ADICIONA O 'src' AO PATH DO PYTHON
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.bootstrap import load_context 

# --- IMPORTS DOS SERVIÇOS ---
from cli import run_fichas_comercializadoras
from cli import run_fichas_consumidores
from services.contratos_denodo_service import ingest_contratos_denodo
from services.enquadramento_service import calcular_enquadramento_consumidor
from services.mtm_ingestion_service import ingest_mtm_data
from services.reconciliacao_denodo_mtm_service import executar_reconciliacao_denodo_mtm
from services.salesforce_ingestion_service import ingest_salesforce_data
from services.reconciliacao_fichas_salesforce_service import executar_reconciliacao_fichas_salesforce
from services.receita_ingestion_service import ingest_receita_data
from services.garantias_service import ingest_garantias_data
from services.pipeline_risco_service import run_pipeline_risco
from services.dim_contraparte_service import build_dim_contraparte
from services.fato_analise_credito_service import build_fato_analise_credito
from services.carga_manual_service import ingest_carga_manual
from services.override_service import processar_solicitacao_override
from services.camada_gold_service import exportar_visao_consolidada_gold
from services.audit_service import registrar_inicio_pipeline, registrar_fim_pipeline

# ==============================================================================
# WRAPPERS PREPARADORES (Alimentam os motores com os dados da Silver)
# ==============================================================================
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
    return run_pipeline_risco(context, df_exposicoes=df_exposicoes)

def preparar_dim_contraparte(context):
    receita_path = context.path("silver") / "receita_silver" / "receita_cadastral_silver.parquet"
    enquadra_path = context.path("relational_configs") / f"enquadramento_consumidores_{datetime.now().strftime('%Y%m')}.csv"
    df_receita = pd.read_parquet(receita_path) if receita_path.exists() else pd.DataFrame()
    df_seg = pd.read_csv(enquadra_path) if enquadra_path.exists() else pd.DataFrame()
    return build_dim_contraparte(context, df_silver_receita=df_receita, df_silver_segmentacao=df_seg)

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
    return build_fato_analise_credito(context, df_silver_analises=df_fichas, df_dim_contraparte=df_dim)

# ==============================================================================
# PIPELINE OFICIAL
# ==============================================================================
class PipelineStep(NamedTuple):
    name: str
    func: Callable[[Any], Any]

PIPELINE_STEPS = [
    PipelineStep(name="Fichas Comercializadoras", func=lambda ctx: run_fichas_comercializadoras.main()),
    PipelineStep(name="Fichas Consumidores", func=lambda ctx: run_fichas_consumidores.main()),
    PipelineStep(name="Ingestão de Contratos (Denodo)", func=ingest_contratos_denodo),
    PipelineStep(name="Enquadramento de Consumidores", func=lambda ctx: calcular_enquadramento_consumidor(datetime.now().strftime("%Y%m"), ctx)),
    PipelineStep(name="Ingestão de MtM", func=ingest_mtm_data),
    PipelineStep(name="Reconciliação Denodo x MtM", func=executar_reconciliacao_denodo_mtm),
    PipelineStep(name="Ingestão do Salesforce", func=ingest_salesforce_data),
    PipelineStep(name="Reconciliação Fichas x Salesforce", func=executar_reconciliacao_fichas_salesforce),
    
    # ATENÇÃO: Etapa da Receita Reativada!
    PipelineStep(name="Ingestão da Receita Federal", func=ingest_receita_data),
    
    PipelineStep(name="Ingestão de Garantias", func=ingest_garantias_data),
    PipelineStep(name="Pipeline de Risco de Crédito", func=preparar_e_rodar_risco),
    PipelineStep(name="Dimensão Contraparte", func=preparar_dim_contraparte),
    PipelineStep(name="Fato Análise de Crédito", func=preparar_fato_analise),
    PipelineStep(name="Carga Manual (Log Eventos)", func=lambda ctx: ingest_carga_manual(ctx, registros=[])),
    PipelineStep(name="Solicitações de Override", func=lambda ctx: processar_solicitacao_override(ctx, solicitacao={"CNPJ": "00000000000000", "TIPO_OVERRIDE": "TESTE", "VALOR_ANTES": 0, "VALOR_DEPOIS": 0, "JUSTIFICATIVA": "Teste Segurança", "EVIDENCIA": "N/A", "SOLICITANTE": "SISTEMA", "APROVADOR": "ADMIN", "DATA_EXPIRACAO": "2099-12-31"})),
    PipelineStep(name="Visão Consolidada Gold", func=exportar_visao_consolidada_gold),
]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs-dir", default=str(Path("ENTRADAS") / "configs"))
    args = parser.parse_args()

    try:
        context = load_context(Path(args.configs_dir))
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
        print(f"5. Contrato Vigente SEM Análise Vigente:   {metricas_operacionais.get('contrato_vig_sem_analise_vig', 0)} ⚠️  (Exposição Descoberta: R$ {metricas_operacionais.get('ead_descoberto', 0.0):,.2f})")
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
## src\common\logging_utils.py
Linhas: 34
Classes: -
Funções: get_logger
```python
"""Configuração padronizada de loggers do sistema BDC."""

from __future__ import annotations

import logging
from pathlib import Path


def get_logger(name: str, file_path: str | Path) -> logging.Logger:
    """Cria ou devolve um logger com saída em arquivo e console."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    target = Path(file_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(target, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger

```


---
## src\common\types.py
Linhas: 20
Classes: -
Funções: normalize_float
```python
"""Conversões tipadas para valores numéricos do sistema BDC."""

from __future__ import annotations

from typing import Any


def normalize_float(value: Any) -> float | None:
    """Converte um valor textual ou numérico em ``float``."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None

```


---
## src\common\validation.py
Linhas: 18
Classes: -
Funções: validate_json_schema
```python
import sys
import logging
from typing import Any
import jsonschema
from jsonschema.exceptions import ValidationError

logger = logging.getLogger(__name__)

def validate_json_schema(instance: dict[str, Any], schema: dict[str, Any], label: str) -> None:
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
## src\control\layout_catalog.py
Linhas: 128
Classes: -
Funções: _validate_layout_structure, load_layout_catalog, load_layouts_comercializadoras, load_layouts_consumidores
```python
"""Carregamento e validação dos layouts de fichas."""

from __future__ import annotations

import sys
from typing import Any

from app.context import AppContext
from common.io_json import read_json


def _validate_layout_structure(layout: dict[str, Any], versao: str, logger: Any) -> None:
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


def load_layout_catalog(
    catalog_path: str,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Carrega o catálogo consolidado de layouts."""
    try:
        if logger is not None:
            logger.info("Carregando catálogo de layouts: %s", catalog_path)

        catalog = read_json(catalog_path)

        if logger is not None:
            logger.info("Catálogo de layouts carregado com sucesso.")

        return catalog

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar catálogo de layouts: %s", catalog_path)
        raise


def load_layouts_comercializadoras(
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

            layout_data = read_json(layout_path)
            
            # Validação adaptada para não quebrar layouts antigos
            if logger is not None:
                _validate_layout_structure(layout_data, key, logger)

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


def load_layouts_consumidores(
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

            layout_data = read_json(layout_path)
            
            # Validação adaptada para não quebrar layouts antigos
            if logger is not None:
                _validate_layout_structure(layout_data, key, logger)

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
## src\domain\credito\ead_engine.py
Linhas: 64
Classes: -
Funções: calcular_ead
```python
"""Motor de Exposure at Default (EAD).

feat(T3.2.1): Adicionados fator de conversão parametrizado e rastreabilidade
com calculo_id e config_snapshot_id.
Ref: §6.7 (Exposição), §7.1, §11.2 (Identificadores) do Planejamento Funcional.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import uuid4


def calcular_ead(
    mtm_positivo_total: float | None,
    fator_conversao: float = 1.0,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Cálculo de EAD baseado na exposição positiva de MtM.

    Regra: EAD = max(MtM favorável à Copel, 0) × fator_conversao (§6.7).

    Args:
        mtm_positivo_total: MtM positivo consolidado por contraparte.
        fator_conversao: Fator de conversão de crédito (CCF), default 1.0.
            Deve ser lido de config (ex: config["ead"]["fator_conversao"]).
        config: Dicionário de configuração para snapshot de rastreabilidade (§11.2).

    Returns:
        Dict com calculo_id, ead_valor, config_snapshot_id e metadados.
    """
    calculo_id = f"EAD_{uuid4().hex[:12]}"

    # Snapshot da configuração usada no cálculo (§11.2)
    config_usada = {"fator_conversao": fator_conversao}
    config_snapshot_id = hashlib.sha256(
        json.dumps(config_usada, sort_keys=True).encode()
    ).hexdigest()[:16]

    if mtm_positivo_total is None:
        return {
            "calculo_id": calculo_id,
            "ead_valor": None,
            "fator_conversao": fator_conversao,
            "config_snapshot_id": config_snapshot_id,
            "dt_calculo": datetime.now().isoformat(timespec="seconds"),
            "status": "SEM_DADOS_MTM",
        }

    ead_valor = max(float(mtm_positivo_total), 0.0) * fator_conversao

    return {
        "calculo_id": calculo_id,
        "ead_valor": ead_valor,
        "mtm_positivo_input": float(mtm_positivo_total),
        "fator_conversao": fator_conversao,
        "config_snapshot_id": config_snapshot_id,
        "dt_calculo": datetime.now().isoformat(timespec="seconds"),
        "status": "CALCULADO",
    }
```


---
## src\domain\credito\pd_base.py
Linhas: 43
Classes: -
Funções: calcular_pd_base
```python
"""Cálculo ou leitura da PD base."""

from __future__ import annotations

from typing import Any

from common.types import normalize_float
from domain.credito.pd_exceptions import PdInputValidationError


def calcular_pd_base(
    registro: dict[str, Any],
    segmento_pd: str,
) -> float:
    """Calcula ou lê a PD base do registro."""
    valor = registro.get("PROBABILIDADE_DEFAULT")
    pd_base = normalize_float(valor)
    
    if segmento_pd == "CONSUMIDOR_LE_5":
        # Para consumidores abaixo de 5 MWm, a PD base não é utilizada
        return 0.0
    
    valor = registro.get("PROBABILIDADE_DEFAULT")

    if pd_base is None:
        raise PdInputValidationError(
            f"Registro sem PROBABILIDADE_DEFAULT para {segmento_pd}."
        )

    if pd_base < 0:
        raise PdInputValidationError(
            f"PD base negativa: {pd_base}"
        )

    if pd_base > 1:
        pd_base = pd_base / 100.0

    if pd_base > 1:
        raise PdInputValidationError(
            f"PD base fora do intervalo após normalização: {pd_base}"
        )

    return pd_base

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


RATING_ORDER = {"A": 1, "B": 2, "E": 3}


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
## src\domain\credito\pd_engine.py
Linhas: 164
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

    except PdCalculationError:
        if logger is not None:
            logger.exception(
                "Erro controlado no cálculo de PD ajustada. "
                "CNPJ=%s SEGMENTO_PD=%s",
                registro.get("CNPJ"),
                segmento_pd,
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
## src\domain\credito\pd_validator.py
Linhas: 105
Classes: -
Funções: _is_blank, validar_insumos_pd
```python
"""Validação dos insumos do cálculo de PD ajustada."""

from __future__ import annotations

from typing import Any

from common.types import normalize_float
from common.strings import normalize_string
from domain.credito.pd_exceptions import PdInputValidationError, PdCalculationError


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    texto = str(value).strip().upper()
    return texto in {"", "N/A", "NA", "N.D.", "ND", "NONE", "NULL"}


def validar_insumos_pd(
    registro: dict[str, Any],
    segmento_pd: str,
) -> None:
    """Valida os insumos mínimos para cálculo de PD ajustada."""
    if not segmento_pd:
        raise PdInputValidationError("SEGMENTO_PD não informado.")
    
    if segmento_pd == "CONSUMIDOR_LE_5":
        if registro.get("SCORE_BUREAU") is None:
            raise PdInputValidationError("SCORE_BUREAU não informado para CONSUMIDOR_LE_5.")
        return

    pd_base_raw = registro.get("PROBABILIDADE_DEFAULT")
    pd_base = normalize_float(pd_base_raw)

    if pd_base is None:
        raise PdInputValidationError("PROBABILIDADE_DEFAULT não informada.")

    if pd_base < 0:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT negativa: {pd_base_raw!r}"
        )

    if segmento_pd == "CGRUPO":
        agencia = registro.get("AGENCIA")
        nota_credito = registro.get("NOTA_CREDITO")
        rating_interno = registro.get(
            "RATING_FINAL") or registro.get("RATING_COPEL")

        tem_rating_publico = not _is_blank(
            agencia) and not _is_blank(nota_credito)
        tem_rating_interno = not _is_blank(rating_interno)

        if not tem_rating_publico and not tem_rating_interno:
            raise PdInputValidationError(
                "CGRUPO sem rating público (AGENCIA/NOTA_CREDITO) "
                "e sem rating interno (RATING_FINAL/RATING_COPEL)."
            )

    else:
        rating = (
            registro.get("RATING_COPEL")
            or registro.get("NOTA_CREDITO")
            or registro.get("RATING_FINAL")
        )

        if _is_blank(rating):
            raise PdInputValidationError("Rating final não informado.")

        rating_normalizado = normalize_string(str(rating), upper=True)
        ratings_validos = {"A", "B", "C", "D", "E"}

        if rating_normalizado not in ratings_validos:
            raise PdInputValidationError(
                f"Rating inválido para {segmento_pd}: {rating_normalizado!r}"
            )

    if segmento_pd in {"CPURA", "CGRUPO"}:
        tipo_comercializadora = normalize_string(
            str(registro.get("TIPO_COMERCIALIZADORA", "")),
            upper=True,
        )
        if tipo_comercializadora not in {"CPURA", "CGRUPO"}:
            raise PdInputValidationError(
                "TIPO_COMERCIALIZADORA inválido ou ausente."
            )
    if segmento_pd == "CONSUMIDOR_GT_5":
        pd_base = registro.get("PROBABILIDADE_DEFAULT")
        rating = registro.get("RATING_FINAL") or registro.get("RATING_COPEL")

        if _is_blank(pd_base):
            raise PdCalculationError(
                "PROBABILIDADE_DEFAULT não informada para CONSUMIDOR_GT_5."
            )

        if _is_blank(rating):
            raise PdCalculationError(
                "RATING_FINAL/RATING_COPEL não informado para CONSUMIDOR_GT_5."
            )

        rating_norm = normalize_string(rating, upper=True)
        if rating_norm not in {"A", "B", "C", "D", "E"}:
            raise PdCalculationError(
                f"Rating inválido para CONSUMIDOR_GT_5: {rating_norm!r}"
            )
        return

```


---
## src\domain\credito\score_quantitativo.py
Linhas: 127
Classes: -
Funções: _obter_peso_nota, calcular_score_quantitativo_cpura
```python
# -*- coding: utf-8 -*-
"""Cálculo do score quantitativo para CPURA."""

from __future__ import annotations

from typing import Any

from common.strings import normalize_string
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_peso_nota(
    nota: Any,
    nota_para_peso: dict[str, Any],
    nome_campo: str,
) -> float:
    """Obtém o peso numérico da nota."""
    nota_normalizada = normalize_string(nota, upper=True)

    if not nota_normalizada:
        raise PdInputValidationError(
            f"{nome_campo} não informada."
        )

    if nota_normalizada not in nota_para_peso:
        raise PdInputValidationError(
            f"{nome_campo} inválida: {nota!r}"
        )

    try:
        return float(nota_para_peso[nota_normalizada])
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            f"Peso inválido para nota {nota_normalizada}."
        ) from exc


def calcular_score_quantitativo_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score quantitativo de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando score quantitativo CPURA. CNPJ=%s",
                registro.get("CNPJ"),
            )

        nota_para_peso = score_cpura_config.get("nota_para_peso")
        pesos_quantitativos = score_cpura_config.get("pesos_quantitativos")

        if not isinstance(nota_para_peso, dict):
            raise PdConfigurationError(
                "Bloco 'nota_para_peso' ausente ou inválido."
            )

        if not isinstance(pesos_quantitativos, dict):
            raise PdConfigurationError(
                "Bloco 'pesos_quantitativos' ausente ou inválido."
            )

        nota_pd = registro.get("NOTA_PD")
        nota_fco_rol = registro.get("NOTA_FCO_ROL")
        nota_roe = registro.get("NOTA_ROE")
        nota_roa = registro.get("NOTA_ROA")

        peso_pd = _obter_peso_nota(nota_pd, nota_para_peso, "NOTA_PD")
        peso_fco_rol = _obter_peso_nota(
            nota_fco_rol,
            nota_para_peso,
            "NOTA_FCO_ROL",
        )
        peso_roe = _obter_peso_nota(nota_roe, nota_para_peso, "NOTA_ROE")
        peso_roa = _obter_peso_nota(nota_roa, nota_para_peso, "NOTA_ROA")

        try:
            w_pd = float(pesos_quantitativos["PD"])
            w_fco_rol = float(pesos_quantitativos["FCO_ROL"])
            w_roe = float(pesos_quantitativos["ROE"])
            w_roa = float(pesos_quantitativos["ROA"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Peso quantitativo ausente: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                "Pesos quantitativos inválidos."
            ) from exc

        score_quantitativo = (
            w_pd * peso_pd
            + w_fco_rol * peso_fco_rol
            + w_roe * peso_roe
            + w_roa * peso_roa
        )

        resultado = {
            "PESO_PD": peso_pd,
            "PESO_FCO_ROL": peso_fco_rol,
            "PESO_ROE": peso_roe,
            "PESO_ROA": peso_roa,
            "SCORE_QUANTITATIVO": score_quantitativo,
        }

        if logger is not None:
            logger.info(
                "Score quantitativo CPURA calculado. "
                "CNPJ=%s SCORE_QUANTITATIVO=%s",
                registro.get("CNPJ"),
                score_quantitativo,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score quantitativo CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )
        raise

```


---
## src\domain\enums.py
Linhas: 126
Classes: TipoFicha, LoadMode, StatusIngestao, StatusClassificacao, StatusExtracao, SegmentoMetodologico, TipoAnalise, SeveridadeAlerta, StatusGarantia, StatusAnalise, StatusDocumento, StatusAlerta, StatusAprovacao
Funções: -
```python
"""Domínios controlados e enumeradores do sistema BDC."""

from enum import Enum, unique


@unique
class TipoFicha(str, Enum):
    """Domínio para os tipos de fichas processadas."""
    COMERCIALIZADORA = "comercializadora"
    CONSUMIDOR = "consumidor"


@unique
class LoadMode(str, Enum):
    """Domínio para os modos de carga do orquestrador."""
    INCREMENTAL = "incremental"
    REPROCESS = "reprocess"


@unique
class StatusIngestao(str, Enum):
    """Domínio para o status de movimentação dos arquivos na camada Bronze."""
    INICIADO = "INICIADO"
    SUCESSO = "SUCESSO"
    ERRO = "ERRO"
    REJEITADO = "REJEITADO"


@unique
class StatusClassificacao(str, Enum):
    """Domínio para os resultados do motor de classificação de layouts."""
    CLASSIFICADO = "CLASSIFICADO"
    REJEITADO = "REJEITADO"
    NAO_CLASSIFICADO = "NAO_CLASSIFICADO"


@unique
class StatusExtracao(str, Enum):
    """Domínio detalhado para os estados de extração e validação técnica."""
    NAO_EXECUTADO = "NAO_EXECUTADO"
    SUCESSO = "SUCESSO"
    ERRO = "ERRO"
    ERRO_VALIDACAO = "ERRO_VALIDACAO"
    ERRO_DUPLICIDADE_HASH = "ERRO_DUPLICIDADE_HASH"
    ERRO_DUPLICIDADE_NEGOCIO = "ERRO_DUPLICIDADE_NEGOCIO"
    ERRO_PROCESSAMENTO = "ERRO_PROCESSAMENTO"
    ERRO_LAYOUT = "ERRO_LAYOUT"
    ERRO_SEM_CNPJ = "ERRO_SEM_CNPJ"
    ERRO_CNPJ_INVALIDO = "ERRO_CNPJ_INVALIDO"


@unique
class SegmentoMetodologico(str, Enum):
    """Domínio das segmentações metodológicas de crédito."""
    CPURA = "CPURA"
    CGRUPO = "CGRUPO"
    CONSUMIDOR_GT_5 = "CONSUMIDOR_GT_5"
    CONSUMIDOR_LE_5 = "CONSUMIDOR_LE_5"


@unique
class TipoAnalise(str, Enum):
    """Domínio para a origem ou tipo de análise gerada."""
    AUTOMATICA = "AUTOMATICA"
    MANUAL = "MANUAL"
    MANUAL_AJUSTADA = "MANUAL_AJUSTADA"


@unique
class SeveridadeAlerta(str, Enum):
    """Domínio para a classificação de alertas do sistema."""
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"
    
@unique
class StatusGarantia(str, Enum):
    """Domínio para os estados de vigência de garantias (§6.8)."""
    VIGENTE = "VIGENTE"
    PROXIMA_VENCIMENTO = "PROXIMA_VENCIMENTO"
    VENCIDA = "VENCIDA"
    CANCELADA = "CANCELADA"
    NAO_ELEGIVEL = "NAO_ELEGIVEL"


@unique
class StatusAnalise(str, Enum):
    """Domínio para o ciclo de vida de uma análise de crédito (§4.2, Apêndice A)."""
    VIGENTE = "VIGENTE"
    PROXIMA_VENCIMENTO = "PROXIMA_VENCIMENTO"
    VENCIDA = "VENCIDA"
    EM_RENOVACAO = "EM_RENOVACAO"
    SUSPENSA = "SUSPENSA"


@unique
class StatusDocumento(str, Enum):
    """Domínio para o estado de processamento de um documento/ficha (§4.2, Apêndice A)."""
    DESCOBERTO = "DESCOBERTO"
    EM_STAGING = "EM_STAGING"
    INGERIDO = "INGERIDO"
    CLASSIFICADO = "CLASSIFICADO"
    EXTRAIDO = "EXTRAIDO"
    VALIDADO = "VALIDADO"
    PUBLICADO = "PUBLICADO"
    PENDENTE = "PENDENTE"
    REJEITADO = "REJEITADO"


@unique
class StatusAlerta(str, Enum):
    """Domínio para os estados de resolução de alertas (§6.10)."""
    ABERTO = "ABERTO"
    EM_TRATAMENTO = "EM_TRATAMENTO"
    RESOLVIDO = "RESOLVIDO"
    IGNORADO = "IGNORADO"


@unique
class StatusAprovacao(str, Enum):
    """Domínio para o fluxo de aprovação de carga manual e overrides (§11.7)."""
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"
    EXPIRADO = "EXPIRADO"
```


---
## src\services\carga_manual_service.py
Linhas: 85
Classes: -
Funções: ingest_carga_manual
```python
"""Serviço de Carga Manual e Eventos de Negócio.

feat(T4.1.2): Serviço de ingestão de eventos de carga manual com garantia
de imutabilidade (append-only) e dupla temporalidade.
Ref: §4.3, §4.5 do Planejamento Funcional.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from common.validation import validate_json_schema
from common.io_json import read_json
from storage.silver_store import write_silver_dataset


def ingest_carga_manual(
    context: AppContext,
    registros: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Recebe registros de carga manual, os valida contra o schema e 
    salva em um log imutável de eventos na camada Silver.
    """
    run_id = f"MAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.governanca.carga_manual")
    
    logger.info("Iniciando processamento de carga manual (run_id=%s).", run_id)

    if not registros:
        return {"run_id": run_id, "processados": 0, "status": "SEM_DADOS"}

    # Carrega Schema de validação
    schema_path = context.path("control_schemas") / "schema_carga_manual.json"
    if not schema_path.exists():
        logger.error("Schema schema_carga_manual.json não encontrado.")
        raise FileNotFoundError("Schema de Carga Manual ausente.")
    
    schema = read_json(schema_path)

    processados = []
    agora = datetime.now().isoformat(timespec="seconds")

    for idx, reg in enumerate(registros):
        # Valida estrutura via JSON Schema (Fail-Fast)
        try:
            validate_json_schema(reg, schema, f"Registro Carga Manual [{idx}]")
        except SystemExit as exc:
            logger.warning(f"Registro {idx} inválido: falhou na validação de schema. Erro: {exc}. Ignorando este registro.")
            # Continua para o próximo registro sem abortar o pipeline
            continue
    

        # Dupla temporalidade (§4.5): data_referencia_negocio vs data_registro_sistema
        novo_reg = reg.copy()
        novo_reg["DATA_REGISTRO_SISTEMA"] = agora
        novo_reg["RUN_ID"] = run_id
        
        # O histórico é append-only: nunca atualizamos, apenas inserimos o novo evento
        processados.append(novo_reg)

    df_manual = pd.DataFrame(processados)
    
    # Salva na Silver (tabela log_eventos_manuais)
    silver_dir = context.path("silver") / "governanca_carga_manual"
    if not silver_dir.exists():
        silver_dir.mkdir(parents=True, exist_ok=True)
        
    write_silver_dataset(
        records=df_manual.to_dict(orient="records"),
        output_dir=silver_dir,
        filename=f"eventos_manuais_{run_id}"
    )

    logger.info("Carga manual processada com sucesso. %d eventos registrados.", len(processados))

    return {
        "run_id": run_id,
        "eventos_processados": len(processados),
        "status": "SUCESSO"
    }

```


---
## src\services\contratos_denodo_service.py
Linhas: 131
Classes: -
Funções: aplicar_regras_negocio_pandas, ingest_contratos_denodo
```python
"""Serviço oficial de ingestão de Contratos Correntes do Denodo."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from services.denodo_connector import fetch_denodo_rest
from storage.silver_store import write_silver_dataset

LOGGER = logging.getLogger(__name__)

def aplicar_regras_negocio_pandas(df: pd.DataFrame) -> pd.DataFrame:
    # Garante que todas as colunas estão em minúsculo para a filtragem não quebrar (CSV vs API)
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    colunas_numericas = ["ano", "ncdempresaproprietaria", "id_parte", "id_tipo_contrato", "id_contraparte", "id_status", "quant_contratada", "quant_sazonalizada"]
    for col in colunas_numericas:
        if col in df.columns:
            # Troca vírgula por ponto caso venha formato brasileiro do CSV
            df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Filtro operacional seguro
    filtro = (
        (df.get("ano", 0) >= 2020) & 
        (df.get("parte_apelido", "") == "COPEL COM") &
        (df.get("contraparte_apelido", "") != "COPEL COM - Transferência de energia") &
        (df.get("ncdempresaproprietaria", 0) == 297) & 
        (df.get("id_parte", 0) == 297) &
        (df.get("id_tipo_contrato", 0).isin([1, 3, 33, 90])) & 
        (df.get("id_contraparte", 0) != 9057) &
        (df.get("contrato_vinculado", "").isna() | (df.get("contrato_vinculado", "") == "")) &
        (~df.get("id_status", 0).isin([0, 1, 4, 5, 6, 9, 10, 11])) &
        ((df.get("quant_contratada", 0) > 0) | (df.get("quant_sazonalizada", 0) > 0))
    )
    return df[filtro].copy()

def ingest_contratos_denodo(context: AppContext) -> dict[str, Any]:
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
            df_raw = fetch_denodo_rest("vwi_exportar_contrato", params=parametros_api)
        
        if df_raw.empty: return {"run_id": run_id, "status": "SEM_DADOS", "linhas": 0}

        # Backup Bronze
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "denodo"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        df_raw.to_parquet(bronze_dir / f"raw_contratos_{run_id}.parquet", index=False)

        # Processamento e Limpeza
        df_silver = aplicar_regras_negocio_pandas(df_raw)
        df_silver.columns = [str(c).strip().upper() for c in df_silver.columns]
        
        # Mapeamento robusto para diferenças entre CSV e API
        rename_map = {
            "CONTRAPARTE_CNPJ": "CNPJ", 
            "NOME_CONTRATO": "CONTRATO", 
            "SUPRIMENTO_INICIO": "VIGENCIA_INICIO", 
            "SUPRIMENTO_TERMINO": "VIGENCIA_FIM"
        }
        df_silver = df_silver.rename(columns=rename_map)
        
        if "CNPJ" not in df_silver.columns and "CONTRAPARTE_CNPJ" in df_silver.columns:
            df_silver = df_silver.rename(columns={"CONTRAPARTE_CNPJ": "CNPJ"})
        
        # Volumes e Competências
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = df_silver["QUANT_SAZONALIZADA"].where(df_silver["QUANT_SAZONALIZADA"] > 0, df_silver["QUANT_CONTRATADA"])
        df_silver["COMPETENCIA"] = df_silver["ANO"].astype(str).str.replace(r"\.0", "", regex=True) + df_silver["MES"].astype(str).str.replace(r"\.0", "", regex=True).str.zfill(2)
        
        # NORMALIZAÇÃO DO CNPJ ESTREITA (Regex limpa pontuação)
        df_silver["CNPJ"] = df_silver["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
        df_silver["VOLUME_CONTRATADO_MENSAL_MWM"] = pd.to_numeric(df_silver["VOLUME_CONTRATADO_MENSAL_MWM"], errors="coerce").fillna(0.0)
        if "STATUS" not in df_silver.columns: df_silver["STATUS"] = "ATIVO"

        # Garantia de colunas para o groupby
        for col in ["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]:
            if col not in df_silver.columns: df_silver[col] = "NAO_INFORMADO"

        # RESOLUÇÃO DA EXPLOSÃO CARTESIANA: Agrupando o volume por Contrato Único
        df_silver_final = df_silver.groupby(["CNPJ", "CONTRATO", "COMPETENCIA", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"], as_index=False).agg({"VOLUME_CONTRATADO_MENSAL_MWM": "sum"})
        
        df_silver_final["RUN_ID"] = run_id
        df_silver_final["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        # Persistência Silver
        silver_dir = context.path("silver") / "denodo_contratos_padronizados"
        silver_dir.mkdir(parents=True, exist_ok=True)
        
        for comp in df_silver_final["COMPETENCIA"].unique():
            if str(comp) in ["000", "NAO_INFORMADONAO_INFORMADO", "00", "nan00"]: continue
            df_comp = df_silver_final[df_silver_final["COMPETENCIA"] == comp]
            write_silver_dataset(records=df_comp.to_dict(orient="records"), output_dir=silver_dir, filename=f"contratos_correntes_{comp}")

        dir_reconciliacao = context.path("silver") / "denodo_contratos_silver"
        write_silver_dataset(records=df_silver_final.to_dict(orient="records"), output_dir=dir_reconciliacao, filename="contratos_correntes")
        
        logger.info("Contratos agregados e sem duplicidades salvos. %d registros limpos", len(df_silver_final))
        return {"run_id": run_id, "linhas_processadas": len(df_silver_final), "status": "SUCESSO"}
    except Exception as exc:
        logger.exception("Falha crítica na ingestão de contratos do Denodo.")
        raise Exception(f"Erro na ingestão Denodo: {exc}") from exc
```


---
## src\services\ficha_classifier.py
Linhas: 200
Classes: ClassificationResult
Funções: _normalize_label, _find_label_by_regex, _verify_field, classify_workbook
```python
"""Classificação de fichas conforme os layouts conhecidos."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from common.excel import read_cell
from openpyxl.worksheet.worksheet import Worksheet
from common.strings import normalize_string


@dataclass
class ClassificationResult:
    """Representa o resultado da classificação de layout."""

    versao_ficha: str
    matched_fields: list[str]
    missing_fields: list[str]


def _normalize_label(value: Any) -> str:
    """Normaliza texto de label para comparação."""
    if value is None:
        return ""

    return normalize_string(str(value), upper=True)


def _find_label_by_regex(
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


def _verify_field(
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
            raise ValueError(f"Campo '{field_name}' tem 'label_cell' mas falta 'expected_label'.")

        actual_label = read_cell(ws, label_cell)
        expected_normalized = _normalize_label(expected_label)
        actual_normalized = _normalize_label(actual_label)

        # Lógica de exceção para o layout "padrao_3"
        if expected_normalized == "CNPJ" and versao_ficha == "padrao_3":
            categoria_label = read_cell(ws, "A19")
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
        matched = _find_label_by_regex(ws, search_pattern)
        logger.info(
            "Verificação (dinâmica) '%s': pattern='%s', matched=%s",
            field_name, search_pattern, matched
        )
        return matched

    raise ValueError(
        f"Campo de verificação '{field_name}' no layout '{versao_ficha}' "
        "não possui 'label_cell' nem 'search_pattern' para classificação."
    )


def classify_workbook(
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

                if _verify_field(workbook, field_name, meta, logger, versao_ficha):
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
## src\services\fichas_comercializadoras_service.py
Linhas: 736
Classes: -
Funções: is_valid_cnpj, _is_disk_full_error, _build_run_id, _build_target_name, _resolve_bronze_subfolder, _move_to_rejected, _move_to_processed, _build_pd_info, _build_processing_queue, _process_single_file, process_fichas_comercializadoras, calc_digit
```python
"""Serviço principal refatorado do pipeline de fichas de comercializadoras."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.context import AppContext
from common.excel import close_workbook_safely, open_workbook
from common.hashing import hash_file
from common.io_json import read_json
from common.logging_utils import get_logger
from common.paths import sanitize_folder_name
from common.strings import normalize_cnpj
from control.layout_catalog import load_layouts_comercializadoras
from control.mapping_loader import load_mapping_fichas_comercializadoras
from control.quality_loader import load_data_quality_rules_comercializadoras
from domain.contrapartes.segmentacao import definir_segmento_metodologico
from domain.credito.pd_engine import calcular_pd_ajustada
from services.audit_service import registrar_documento, registrar_linhagem_campos
from services.dedup_service import (
    has_duplicate_business_key,
    has_duplicate_hash,
    upsert_business_key_in_history,
)
from services.ficha_classifier import classify_workbook
from services.ficha_extractor import extract_record
from services.ficha_validator import validate_record
from silver.documentos_classificados import build_classified_document
from silver.field_type_normalizer import normalize_record
from staging.discovery import discover_pending_excels
from staging.staging_writer import copy_to_staging
from storage.bronze_store import publish_raw_file
from storage.file_ops import move_file_with_retry
from storage.manifest_store import (
    append_manifest_record,
    load_ingestion_history,
)
from storage.silver_store import (
    merge_silver_dataset_by_business_key,
    write_silver_dataset,
)
from storage.state_store import DocumentManifest


def is_valid_cnpj(digits: str | None) -> bool:
    """Valida se o valor é um CNPJ válido."""
    if digits is None:
        return False

    if digits == digits[0] * 14:
        return False

    def calc_digit(base: str, weights: list[int]) -> str:
        total = sum(int(num) * weight for num, weight in zip(base, weights))
        remainder = total % 11
        return "0" if remainder < 2 else str(11 - remainder)

    first_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    second_weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    first_digit = calc_digit(digits[:12], first_weights)
    second_digit = calc_digit(digits[:12] + first_digit, second_weights)

    return digits[-2:] == first_digit + second_digit


def _is_disk_full_error(exc: Exception) -> bool:
    """Indica se a exceção representa falta de espaço em disco."""
    if not isinstance(exc, OSError):
        return False

    text = str(exc).lower()

    return (
        getattr(exc, "winerror", None) == 112
        or getattr(exc, "errno", None) == 28
        or "no space left on device" in text
        or "espaço insuficiente no disco" in text
    )


def _build_run_id(context: AppContext) -> str:
    """Monta o identificador textual da execução."""
    prefix = context.naming.get("run_id_prefix", "BDC")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"


def _build_target_name(
    original_name: str,
    versao_ficha: str | None,
    cnpj: str | None,
    data_df: str | None,
    hash_value: str | None,
) -> str:
    """Monta o nome técnico do arquivo processado."""
    source = Path(original_name)
    stem = source.stem[:40]

    parts: list[str] = [stem]

    if versao_ficha:
        parts.append(versao_ficha)

    if cnpj:
        safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
        parts.append(safe_cnpj)

    if data_df:
        safe_data_df = "".join(ch for ch in str(data_df) if ch.isdigit())
        parts.append(safe_data_df[:8])

    if hash_value:
        parts.append(hash_value[:8])

    return "__".join(parts) + source.suffix.lower()


def _resolve_bronze_subfolder(
    cnpj: str | None,
    sigla: str | None,
) -> str:
    """Resolve a subpasta da bronze organizada por CNPJ e sigla."""
    if not cnpj:
        raise ValueError("Não é possível publicar em bronze sem CNPJ válido.")
    safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
    safe_sigla = sanitize_folder_name(sigla or "")
    if safe_sigla:
        return f"{safe_cnpj}__{safe_sigla}"

    return safe_cnpj


def _move_to_rejected(
    source_file: Path,
    rejected_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
    control_dir: Path | None = None,
) -> None:
    """Move o arquivo para rejeitados e grava o manifest."""
    target = rejected_dir / source_file.name

    try:
        if source_file.exists():
            move_file_with_retry(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para rejeitados: {exc}")
        logger.exception("Falha ao mover %s para rejeitados.", source_file.name)

    try:
        append_manifest_record(str(ingestion_log_path), manifest.to_dict())
        if control_dir:
            registrar_documento(
                manifest.documento_id,
                manifest.run_id,
                manifest.arquivo_nome,
                manifest.hash_arquivo,
                manifest.tipo_ficha,
                manifest.status_classificacao or "N/A",
                manifest.status_extracao or "N/A",
                control_dir
            )
    except Exception as exc:
        logger.exception(
            "Falha ao gravar manifest de rejeição para %s.", source_file.name
        )
        raise


def _move_to_processed(
    source_file: Path,
    processed_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
    control_dir: Path | None = None,
) -> None:
    """Move o arquivo para processadas e grava o manifest."""
    target = processed_dir / source_file.name

    try:
        if source_file.exists():
            move_file_with_retry(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para processadas: {exc}")
        logger.exception("Falha ao mover %s para processadas.", source_file.name)

    try:
        append_manifest_record(str(ingestion_log_path), manifest.to_dict())
        if control_dir:
            registrar_documento(
                manifest.documento_id,
                manifest.run_id,
                manifest.arquivo_nome,
                manifest.hash_arquivo,
                manifest.tipo_ficha,
                manifest.status_classificacao or "N/A",
                manifest.status_extracao or "N/A",
                control_dir
            )
    except Exception as exc:
        logger.exception(
            "Falha ao gravar manifest de processamento para %s.", source_file.name
        )
        raise


def _build_pd_info(
    normalized: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    pd_cpura_config: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any,
    source_file: Path,
    manifest: DocumentManifest,
    peer_group: list[float] | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada para o registro normalizado de comercializadora."""
    segmento_pd: str | None = None

    try:
        registro_pd = dict(normalized)
        registro_pd["TIPO_FICHA"] = "COMERCIALIZADORA"

        segmento_pd = definir_segmento_metodologico(registro_pd)
        registro_pd["SEGMENTO_PD"] = segmento_pd

        pd_info = calcular_pd_ajustada(
            registro=registro_pd,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=pd_cpura_config,
            score_cpura_config=score_cpura_config,
            peer_group=peer_group,
            logger=logger,
        )

        logger.info(
            "PD ajustada calculada para %s. "
            "Segmento=%s SCORE_TOTAL=%s RATING_FINAL=%s PD_FINAL=%s",
            source_file.name,
            pd_info.get("SEGMENTO_PD"),
            pd_info.get("SCORE_TOTAL"),
            pd_info.get("RATING_FINAL"),
            pd_info.get("PD_FINAL"),
        )
        return pd_info

    except Exception as exc:
        logger.warning(
            "PD ajustada não calculada para %s. Motivo: %s",
            source_file.name,
            exc,
        )
        manifest.avisos.append(f"PD ajustada não calculada: {exc}")

        return {
            "SEGMENTO_PD": segmento_pd,
            "NOTA_AUDITORIA": None,
            "PESO_BOARD": None,
            "PESO_AUDITORIA": None,
            "PESO_BUREAU": None,
            "SCORE_QUALITATIVO": None,
            "PESO_PD": None,
            "PESO_FCO_ROL": None,
            "PESO_ROE": None,
            "PESO_ROA": None,
            "SCORE_QUANTITATIVO": None,
            "SCORE_TOTAL": None,
            "SCORE_MIN_RATING": None,
            "SCORE_MAX_RATING": None,
            "SCORE_TRUNCADO": None,
            "PD_BASE": None,
            "RATING_FINAL": None,
            "FONTE_RATING": None,
            "PD_MIN_FAIXA": None,
            "PD_MAX_FAIXA": None,
            "PERCENTIL_PD_BASE": None,
            "PD_BRUTA": None,
            "PD_ESTABILIZADA": None,
            "PD_FINAL": None,
            "PD_METODO": None,
            "LOGIT_TRUNCADO": None,
        }


def _build_processing_queue(
    context: AppContext,
) -> list[tuple[Path, str, Path, Path]]:
    """Monta a fila de processamento normal e reprocessamento."""
    normal_files = discover_pending_excels(
        context.path("input_fichas_comercializadoras_pendentes")
    )
    reprocess_files = discover_pending_excels(
        context.path("input_reprocessamento_comercializadoras_pendentes")
    )

    queue: list[tuple[Path, str, Path, Path]] = []

    for file_path in normal_files:
        queue.append(
            (
                file_path,
                "incremental",
                context.path("input_fichas_comercializadoras_processadas"),
                context.path("input_fichas_comercializadoras_rejeitadas"),
            )
        )

    for file_path in reprocess_files:
        queue.append(
            (
                file_path,
                "reprocess",
                context.path("input_reprocessamento_comercializadoras_processados"),
                context.path("input_reprocessamento_comercializadoras_rejeitados"),
            )
        )

    return queue


def _process_single_file(
    source_file: Path,
    load_mode: str,
    processed_dir: Path,
    rejected_dir: Path,
    context: AppContext,
    layouts: dict[str, Any],
    required_fields: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_cpura_config: dict[str, Any],
    score_cpura_config: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    quality_rules: dict[str, Any],
    control_dir: Path | None = None,
) -> Optional[dict[str, Any]]:
    """Processa de ponta a ponta um único arquivo de ficha de comercializadora."""
    workbook = None
    manifest = DocumentManifest(
        documento_id=str(uuid.uuid4()),
        run_id=run_id,
        ambiente=context.app_config["env"],
        tipo_ficha="comercializadora",
        arquivo_nome=source_file.name,
        caminho_origem=str(source_file),
        load_mode=load_mode,
    )

    try:
        logger.info(
            "Iniciando processamento do arquivo %s em modo %s.",
            source_file.name,
            load_mode,
        )

        manifest.hash_arquivo = hash_file(source_file)

        # 1. Checagem de Hash em Carga Incremental
        if load_mode == "incremental" and has_duplicate_hash(
            history, manifest.hash_arquivo
        ):
            manifest.status_extracao = "ERRO_DUPLICIDADE_HASH"
            manifest.erros.append("Hash já processado anteriormente.")
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        # 2. Copia para Staging
        staging_dir = context.path("staging_fichas_comercializadoras")
        staging_name = _build_target_name(
            original_name=source_file.name,
            versao_ficha=None,
            cnpj=None,
            data_df=None,
            hash_value=manifest.hash_arquivo,
        )
        staging_file = copy_to_staging(source_file, staging_dir, staging_name)
        manifest.caminho_staging = str(staging_file)

        # 3. Abertura e Classificação do Layout
        workbook = open_workbook(staging_file)
        classification = classify_workbook(workbook, layouts, logger)

        if classification is None:
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("Layout não identificado.")
            close_workbook_safely(workbook)
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        manifest.versao_ficha = classification.versao_ficha
        manifest.status_classificacao = "CLASSIFICADO"

        logger.info(
            "Layout %s identificado para %s.",
            classification.versao_ficha,
            source_file.name,
        )

        # 4. Extração e Normalização
        layout = layouts[classification.versao_ficha]
        raw_record, metadata_list = extract_record(workbook, layout)
        
        if control_dir and metadata_list:
            registrar_linhagem_campos(
                manifest.documento_id,
                manifest.run_id,
                metadata_list,
                control_dir
            )
            
        slug = "field_types_fichas_comercializadoras"
        normalized = normalize_record(raw_record, context, slug, logger)

        manifest.cnpj_extraido = normalize_cnpj(normalized.get("CNPJ"))
        normalized["CNPJ"] = manifest.cnpj_extraido

        manifest.data_demonstracao_financeira = normalized.get(
            "DATA_DEMONSTRACAO_FINANCEIRA"
        )
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        # 5. Validação Técnica e CNPJ
        validate_fields = required_fields[classification.versao_ficha]
        errors, warnings = validate_record(
            normalized, validate_fields, logger=logger, quality_rules=quality_rules
        )
        manifest.erros.extend(errors)
        manifest.avisos.extend(warnings)

        if not manifest.cnpj_extraido:
            manifest.status_extracao = "ERRO_SEM_CNPJ"
            manifest.erros.append("Ficha sem CNPJ válido.")
            close_workbook_safely(workbook)
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if not is_valid_cnpj(manifest.cnpj_extraido):
            manifest.status_extracao = "ERRO_CNPJ_INVALIDO"
            manifest.erros.append(f"CNPJ inválido: {manifest.cnpj_extraido}")
            close_workbook_safely(workbook)
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO"
            close_workbook_safely(workbook)
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        # 6. Checagem de Duplicidade de Negócio e Versionamento
        duplicate_business = has_duplicate_business_key(
            history,
            manifest.cnpj_extraido,
            manifest.data_demonstracao_financeira,
        )

        # C0.1 - CORREÇÃO: Se o hash é novo (passou na etapa 1), mas a chave de negócio existe,
        # trata-se de uma nova versão factual da ficha. O sistema não rejeita, ele versiona.
        if duplicate_business:
            manifest.reprocessed = True
            manifest.previous_record_found = True
            logger.info("Nova versão identificada para CNPJ %s e DF %s. O registro será versionado na Silver.", manifest.cnpj_extraido, manifest.data_demonstracao_financeira)
        else:
            manifest.reprocessed = False
            manifest.previous_record_found = False

        close_workbook_safely(workbook)
        workbook = None

        # 7. Regras de Negócio de Crédito (PD / Scoring)
        pd_info = _build_pd_info(
            normalized=normalized,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=pd_cpura_config,
            score_cpura_config=score_cpura_config,
            logger=logger,
            source_file=source_file,
            manifest=manifest,
            peer_group=None,
        )

        # 8. Verificação de Caminhos e Publicação Bronze
        bronze_root_dir = context.path("bronze_fichas_comercializadoras_raw")
        bronze_name = _build_target_name(
            original_name=source_file.name,
            versao_ficha=manifest.versao_ficha,
            cnpj=manifest.cnpj_extraido,
            data_df=manifest.data_demonstracao_financeira,
            hash_value=manifest.hash_arquivo,
        )

        bronze_subfolder = _resolve_bronze_subfolder(
            manifest.cnpj_extraido,
            normalized.get("SIGLA"),
        )
        bronze_staging_target = staging_dir / bronze_name

        logger.info("Fonte bronze_staging: %s", staging_file)
        logger.info("Destino bronze_staging: %s", bronze_staging_target)
        logger.info(
            "Tamanho do caminho destino: %s", len(str(bronze_staging_target))
        )

        target_path = staging_dir / bronze_name
        if len(str(target_path)) > 240:
            raise ValueError(f"Caminho de destino muito longo: {target_path}")

        bronze_staging = copy_to_staging(staging_file, staging_dir, bronze_name)
        bronze_file = publish_raw_file(
            source_file=bronze_staging,
            bronze_root_dir=bronze_root_dir / bronze_subfolder,
        )
        manifest.caminho_bronze = str(bronze_file)
        manifest.status_extracao = "SUCESSO"

        _move_to_processed(
            source_file, processed_dir, manifest, ingestion_log_path, logger, control_dir
        )
        upsert_business_key_in_history(history, manifest.to_dict())

        logger.info("Ficha processada com sucesso: %s.", source_file.name)

        # 9. Retorno Estruturado
        silver_record = {
            **normalized,
            **pd_info,
            "documento_id": manifest.documento_id,
            "run_id": run_id,
            "ambiente": manifest.ambiente,
            "tipo_ficha": manifest.tipo_ficha,
            "versao_ficha": manifest.versao_ficha,
            "arquivo_nome": manifest.arquivo_nome,
            "hash_arquivo": manifest.hash_arquivo,
            "load_mode": load_mode,
            "dt_processamento": datetime.now().isoformat(timespec="seconds"),
        }

        classified_document = build_classified_document(
            documento_id=manifest.documento_id,
            run_id=run_id,
            ambiente=manifest.ambiente,
            arquivo_nome=manifest.arquivo_nome or "",
            versao_ficha=manifest.versao_ficha or "",
            tipo_ficha=manifest.tipo_ficha,
            hash_arquivo=manifest.hash_arquivo or "",
        )

        return {
            "silver_record": silver_record,
            "classified_document": classified_document,
        }

    except Exception as exc:
        if workbook:
            close_workbook_safely(workbook)
        manifest.status_extracao = "ERRO_PROCESSAMENTO"
        manifest.erros.append(str(exc))

        if _is_disk_full_error(exc):
            logger.exception(
                "Execução interrompida por falta de espaço em disco ao processar %s.",
                source_file.name,
            )
            raise

        try:
            _move_to_rejected(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
        except Exception as move_exc:
            if _is_disk_full_error(move_exc):
                logger.exception(
                    "Execução interrompida por falta de espaço em disco ao registrar rejeição do arquivo %s.",
                    source_file.name,
                )
                raise

            logger.exception(
                "Falha adicional ao mover/gravar rejeição do arquivo %s.",
                source_file.name,
            )
            raise

        logger.exception("Falha inesperada ao processar %s.", source_file.name)
        return None


def process_fichas_comercializadoras(
    context: AppContext,
) -> dict[str, Any]:
    """Executa o pipeline completo das fichas de comercializadoras."""
    run_id = _build_run_id(context)

    log_file = (
        context.path("log_runner") / f"{run_id}__fichas_comercializadoras.log"
    )
    logger = get_logger("bdc.comercializadoras", log_file)

    _ = load_mapping_fichas_comercializadoras(context, logger)

    layouts = load_layouts_comercializadoras(context, logger)
    quality_rules = load_data_quality_rules_comercializadoras(context, logger)

    try:
        pd_faixas = read_json(context.control_file("pd_faixas"))
        logger.info("Faixas de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_faixas.")
        raise

    try:
        pd_cpura_config = read_json(context.control_file("pd_cpura_config"))
        logger.info("Configuração de CPURA carregada com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_cpura_config.")
        raise

    try:
        score_cpura_config = read_json(
            context.control_file("score_cpura_config")
        )
        logger.info("Configuração de score de CPURA carregada com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar score_cpura_config.")
        raise

    try:
        pd_transform_rules = read_json(
            context.control_file("pd_transform_rules")
        )
        logger.info("Regras de transformação de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_transform_rules.")
        raise

    required_fields = quality_rules.get("required_fields_by_version")

    ingestion_log_path = (
        context.path("bronze_ingestion_log")
        / "fichas_comercializadoras_ingestion.jsonl"
    )
    history = load_ingestion_history(ingestion_log_path)

    silver_records: list[dict[str, Any]] = []
    classified_documents: list[dict[str, Any]] = []

    queue = _build_processing_queue(context)

    normal_count = sum(1 for _, mode, _, _ in queue if mode == "incremental")
    reprocess_count = sum(1 for _, mode, _, _ in queue if mode == "reprocess")

    logger.info(
        "Iniciando processamento de %s fichas (%s normais, %s reprocessamento).",
        len(queue),
        normal_count,
        reprocess_count,
    )

    # Processa cada item da fila isoladamente
    for source_file, load_mode, processed_dir, rejected_dir in queue:
        result = _process_single_file(
            source_file=source_file,
            load_mode=load_mode,
            processed_dir=processed_dir,
            rejected_dir=rejected_dir,
            context=context,
            layouts=layouts,
            required_fields=required_fields,
            pd_faixas=pd_faixas,
            pd_cpura_config=pd_cpura_config,
            score_cpura_config=score_cpura_config,
            pd_transform_rules=pd_transform_rules,
            history=history,
            ingestion_log_path=ingestion_log_path,
            logger=logger,
            run_id=run_id,
            quality_rules=quality_rules,
            control_dir=context.path("relational_control") if hasattr(context, "path") and context.path("relational_control") else Path("SAIDAS/relational/control"),
        )

        if result:
            silver_records.append(result["silver_record"])
            classified_documents.append(result["classified_document"])

    silver_output_dir = context.path("silver_fichas_comercializadoras_extraidas")
    docs_output_dir = context.path("silver_documentos_classificados")

    if silver_records:
        merge_silver_dataset_by_business_key(
            records=silver_records,
            output_dir=silver_output_dir,
            filename="fichas_comercializadoras_extraidas.csv",
            business_keys=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA"],
        )

    if classified_documents:
        write_silver_dataset(
            records=classified_documents,
            output_dir=docs_output_dir,
            filename=f"documentos_classificados__{run_id}",
        )

    summary = {
        "run_id": run_id,
        "arquivos_recebidos": len(queue),
        "arquivos_normais": normal_count,
        "arquivos_reprocessamento": reprocess_count,
        "registros_silver": len(silver_records),
        "documentos_classificados": len(classified_documents),
    }

    logger.info("Resumo do processamento: %s", summary)
    return summary
```


---
## src\services\pipeline_risco_service.py
Linhas: 108
Classes: -
Funções: run_pipeline_risco
```python
"""Orquestrador do Pipeline de Risco de Crédito."""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from common.logging_utils import get_logger
from domain.credito.ead_engine import calcular_ead
from domain.credito.lgd_engine import calcular_lgd
from domain.credito.pe_engine import calcular_perda_esperada
from domain.credito.taxa_risco_engine import calcular_taxa_risco
from storage.silver_store import write_silver_dataset

def run_pipeline_risco(
    context: AppContext,
    df_exposicoes: pd.DataFrame,
    fator_conversao_ead: float = 1.0,
    config_lgd: dict[str, Any] | None = None
) -> dict[str, Any]:
    run_id = f"RSK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = get_logger("bdc.risco", context.path("log_runner") / f"{run_id}__pipeline_risco.log")
    logger.info("Iniciando Pipeline de Risco de Crédito (run_id=%s)", run_id)
    
    garantias_path = context.path("silver") / "garantias_silver" / "fato_garantia.parquet"
    df_garantias = pd.read_parquet(garantias_path) if garantias_path.exists() else pd.DataFrame()

    resultados_fatos = []
    pe_total_carteira = 0.0
    notional_total_carteira = 0.0
    alertas = []

    df_exposicoes["MTM_POSITIVO_TOTAL"] = pd.to_numeric(df_exposicoes.get("MTM_POSITIVO_TOTAL", 0), errors="coerce").fillna(0.0)
    df_exposicoes["NOTIONAL_TOTAL"] = pd.to_numeric(df_exposicoes.get("NOTIONAL_TOTAL", 0), errors="coerce").fillna(0.0)
    df_exposicoes["PD_FINAL"] = pd.to_numeric(df_exposicoes.get("PD_FINAL", 0), errors="coerce").fillna(0.0)

    for idx, row in df_exposicoes.iterrows():
        cnpj = row.get("CNPJ")
        mtm_positivo = row.get("MTM_POSITIVO_TOTAL")
        notional = row.get("NOTIONAL_TOTAL")
        segmento = row.get("SEGMENTO_METODOLOGICO", "CGRUPO")
        pd_final = row.get("PD_FINAL")

        cobertura_aplicada = 0.0
        # CORREÇÃO: Aplica a garantia se ela estiver VIGENTE
        if not df_garantias.empty and "CNPJ_CONTRAPARTE" in df_garantias.columns:
            filtro = (df_garantias["CNPJ_CONTRAPARTE"] == cnpj) & (df_garantias.get("STATUS", "") == "VIGENTE")
            if filtro.any():
                cobertura_calculada = df_garantias.loc[filtro, "PERCENTUAL_COBERTURA"].sum()
                cobertura_aplicada = min(float(cobertura_calculada), 1.0)

        res_ead = calcular_ead(mtm_positivo_total=mtm_positivo, fator_conversao=fator_conversao_ead)
        res_lgd = calcular_lgd(segmento=segmento, cobertura_garantias=cobertura_aplicada, config=config_lgd)
        res_pe = calcular_perda_esperada(
            ead=res_ead.get("ead_valor"), 
            lgd_liquida=res_lgd.get("lgd_liquida"), 
            pd_final=pd_final, 
            notional=notional
        )

        pe_val = res_pe.get("pe_reais", 0.0)
        if pe_val is not None: pe_total_carteira += float(pe_val)
        if notional is not None: notional_total_carteira += float(notional)

        fato = {
            "RUN_ID": run_id, "CNPJ": cnpj, "SEGMENTO": segmento,
            "DT_CALCULO": res_pe.get("dt_calculo"),
            "CALCULO_ID_EAD": res_ead.get("calculo_id"), "EAD_VALOR": res_ead.get("ead_valor", 0.0),
            "FATOR_CONVERSAO_EAD": res_ead.get("fator_conversao"), "CONFIG_SNAPSHOT_EAD": res_ead.get("config_snapshot_id"),
            "CALCULO_ID_LGD": res_lgd.get("calculo_id"), "LGD_BRUTA": res_lgd.get("lgd_bruta"),
            "LGD_LIQUIDA": res_lgd.get("lgd_liquida", 0.0), "COBERTURA_GARANTIAS": res_lgd.get("cobertura_garantias"),
            "CONFIG_SNAPSHOT_LGD": res_lgd.get("config_snapshot_id"),
            "PD_UTILIZADA": pd_final,
            "CALCULO_ID_PE": res_pe.get("calculo_id"), "PE_REAIS": res_pe.get("pe_reais", 0.0),
            "PE_PERCENTUAL": res_pe.get("pe_percentual", 0.0),
        }
        resultados_fatos.append(fato)

    res_taxa = calcular_taxa_risco(pe_total=pe_total_carteira, notional_total=notional_total_carteira)
    taxa_val = res_taxa.get("taxa_risco")
    taxa_print = f"{taxa_val*100:.4f}%" if taxa_val is not None else "0.00% (Notional Zerado na Origem)"
    
    if res_taxa.get("alertas"): alertas.extend(res_taxa["alertas"])

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        df_alertas["RUN_ID"] = run_id
        df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
        df_alertas["STATUS_ALERTA"] = "ABERTO"
        write_silver_dataset(records=df_alertas.to_dict(orient="records"), output_dir=context.path("silver") / "alertas_credito", filename=f"alertas_risco_{run_id}")

    if resultados_fatos:
        df_fatos = pd.DataFrame(resultados_fatos)
        relational_dir = context.path("relational_facts")
        relational_dir.mkdir(parents=True, exist_ok=True)
        
        write_silver_dataset(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename=f"fato_exposicao_risco_{run_id}")
        write_silver_dataset(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename="fato_exposicao_risco_LATEST")
        
    logger.info("Pipeline de Risco concluído. Taxa Carteira: %s", taxa_print)

    return {
        "run_id": run_id, "linhas_processadas": len(resultados_fatos),
        "taxa_risco_carteira": taxa_val, "pe_total_carteira": pe_total_carteira,
        "notional_total_carteira": notional_total_carteira, "calculo_id_taxa": res_taxa.get("calculo_id")
    }
```


---
## src\services\reconciliacao_fichas_salesforce_service.py
Linhas: 124
Classes: -
Funções: executar_reconciliacao_fichas_salesforce
```python
"""
Serviço de Reconciliação: Fichas de Crédito vs Salesforce.
Verifica se todas as contrapartes com ficha de crédito estão devidamente cadastradas no CRM.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from storage.silver_store import write_silver_dataset

LOGGER = logging.getLogger(__name__)

def executar_reconciliacao_fichas_salesforce(context: AppContext) -> dict[str, Any]:
    run_id = f"REC_SF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.reconciliacao_sf")
    
    silver_dir = context.path("silver")

    # 1. Carregar Fichas (Busca ampla nas pastas conhecidas)
    df_fichas = pd.DataFrame()
    for segmento in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        path_seg = silver_dir / segmento
        if path_seg.exists():
            parquets = list(path_seg.glob("*.parquet"))
            if parquets:
                df_seg = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg], ignore_index=True)

    # 2. Carregar Contas do Salesforce (Busca dinâmica e recursiva)
    df_sf = pd.DataFrame()
    
    # Varre a camada Silver inteira atrás de qualquer arquivo Parquet de Account do Salesforce
    arquivos_sf = list(silver_dir.rglob("account*.parquet"))
    if not arquivos_sf:
        # Tenta outro padrão comum de nomenclatura
        arquivos_sf = list(silver_dir.rglob("*salesforce*account*.parquet"))
        
    if arquivos_sf:
        arquivo_sf_mais_recente = max(arquivos_sf, key=lambda f: f.stat().st_mtime)
        df_sf = pd.read_parquet(arquivo_sf_mais_recente)

    # Validação Robusta
    if df_fichas.empty:
        print("\n[AVISO] Base de Fichas está vazia. Abortando reconciliação.")
        return {"run_id": run_id, "status": "SEM_DADOS_FICHAS"}
        
    if df_sf.empty:
        print("\n[AVISO] Base do Salesforce (Account) não foi encontrada na Silver. Abortando.")
        return {"run_id": run_id, "status": "SEM_DADOS_SF"}

    # 3. Normalização de CNPJs (Chave de Negócio)
    df_fichas["CNPJ_FICHAS"] = df_fichas["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
    df_fichas_unique = df_fichas.drop_duplicates(subset=["CNPJ_FICHAS"]).copy()

    # Caça a coluna que guarda o CNPJ dentro do CRM
    col_cnpj_sf = "CNPJ" if "CNPJ" in df_sf.columns else next((c for c in df_sf.columns if "CNPJ" in str(c).upper() or "DOCUMENTO" in str(c).upper()), None)
    
    if not col_cnpj_sf:
        print("\n[AVISO] Coluna de CNPJ não encontrada na base do Salesforce.")
        return {"run_id": run_id, "status": "FALHA_MAPEAMENTO_SF"}

    df_sf["CNPJ_SF"] = df_sf[col_cnpj_sf].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
    df_sf_unique = df_sf.drop_duplicates(subset=["CNPJ_SF"]).copy()

    # 4. Cruzamento Direcional (Left Join a partir das Fichas)
    df_merge = pd.merge(df_fichas_unique, df_sf_unique, left_on="CNPJ_FICHAS", right_on="CNPJ_SF", how="left", indicator=True)
    
    # 5. Geração de Alertas (Fichas sem CRM)
    alertas = []
    df_missing_in_sf = df_merge[df_merge["_merge"] == "left_only"]
    
    for _, row in df_missing_in_sf.iterrows():
        cnpj = row["CNPJ_FICHAS"]
        if cnpj == "00000000000000": continue
        
        alertas.append({
            "CODIGO": "SF_001",
            "CNPJ": cnpj,
            "MENSAGEM": "Contraparte possui Ficha de Crédito, mas NÃO foi encontrada na base de Contas do CRM (Salesforce).",
            "SEVERIDADE": "MÉDIA",
            "RUN_ID": run_id,
            "DT_DETECCAO": datetime.now().isoformat(timespec="seconds"),
            "STATUS_ALERTA": "ABERTO"
        })

    # 6. Salvar Tabela Fato de Reconciliação
    relational_dir = context.path("relational_facts")
    relational_dir.mkdir(parents=True, exist_ok=True)
    
    df_resultado = df_merge[["CNPJ_FICHAS", "CNPJ_SF", "_merge"]].copy()
    df_resultado.columns = ["CNPJ", "CNPJ_SALESFORCE", "STATUS_RECONCILIACAO"]
    df_resultado["STATUS_RECONCILIACAO"] = df_resultado["STATUS_RECONCILIACAO"].map({
        "both": "SINCRONIZADO", 
        "left_only": "PENDENTE_NO_SALESFORCE", 
        "right_only": "SOMENTE_SALESFORCE"
    })

    df_resultado.to_csv(relational_dir / "fato_reconciliacao_fichas_salesforce.csv", index=False, sep=";", decimal=",")
    df_resultado.to_parquet(relational_dir / "fato_reconciliacao_fichas_salesforce.parquet", index=False)

    # 7. Disparo dos Alertas
    if alertas:
        df_alertas = pd.DataFrame(alertas)
        write_silver_dataset(
            records=df_alertas.to_dict(orient="records"), 
            output_dir=silver_dir / "alertas_credito", 
            filename=f"alertas_reconciliacao_sf_{run_id}"
        )

    # Imprime direto no console para você ver sem precisar abrir logs
    print(f"\n[RECONCILIAÇÃO CRM] Concluída! {len(alertas)} Fichas aprovadas não possuem cadastro correspondente no Salesforce.")
    
    return {
        "run_id": run_id, 
        "status": "SUCESSO", 
        "fichas_cruzadas": len(df_fichas_unique),
        "alertas_gerados": len(alertas)
    }
```


---
## src\silver\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Camada silver do sistema BDC."""

```


---
## src\silver\documentos_classificados.py
Linhas: 24
Classes: -
Funções: build_classified_document
```python
"""Builders da camada silver para documentos classificados."""

from __future__ import annotations


def build_classified_document(
    documento_id: str,
    run_id: str,
    ambiente: str,
    arquivo_nome: str,
    versao_ficha: str,
    tipo_ficha: str,
    hash_arquivo: str,
) -> dict[str, str]:
    """Monta o registro silver de documento classificado."""
    return {
        "documento_id": documento_id,
        "run_id": run_id,
        "ambiente": ambiente,
        "arquivo_nome": arquivo_nome,
        "versao_ficha": versao_ficha,
        "tipo_ficha": tipo_ficha,
        "hash_arquivo": hash_arquivo,
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
## src\staging\discovery.py
Linhas: 18
Classes: -
Funções: discover_pending_excels
```python
"""Descoberta de arquivos pendentes para processamento."""

from __future__ import annotations

from pathlib import Path


def discover_pending_excels(input_dir: str | Path) -> list[Path]:
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
## src\staging\staging_writer.py
Linhas: 21
Classes: -
Funções: copy_to_staging
```python
"""Cópia de arquivos para a área de staging do sistema."""

from __future__ import annotations

import shutil
from pathlib import Path


def copy_to_staging(
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
## src\storage\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Camada de persistência física do sistema BDC."""

```


---
## src\storage\bronze_store.py
Linhas: 20
Classes: -
Funções: publish_raw_file
```python
"""Publicação de arquivos válidos na camada bronze."""

from __future__ import annotations

import shutil
from pathlib import Path


def publish_raw_file(
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
## src\storage\file_ops.py
Linhas: 34
Classes: -
Funções: move_file_with_retry
```python
"""Operações robustas de arquivo para ambiente Windows."""

from __future__ import annotations

import shutil
import time
from pathlib import Path


def move_file_with_retry(
    source: str | Path,
    target: str | Path,
    attempts: int = 5,
    wait_seconds: float = 0.5,
) -> Path:
    """Move um arquivo com novas tentativas em caso de bloqueio."""
    source_path = Path(source)
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None

    for _ in range(attempts):
        try:
            shutil.move(str(source_path), str(target_path))
            return target_path
        except PermissionError as exc:
            last_error = exc
            time.sleep(wait_seconds)

    if last_error is not None:
        raise last_error

    return target_path

```


---
## src\storage\manifest_store.py
Linhas: 39
Classes: -
Funções: append_manifest_record, load_ingestion_history
```python
"""Persistência do manifest de ingestão em formato JSONL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_manifest_record(
    output_file: str | Path,
    record: dict[str, Any],
) -> None:
    """Acrescenta um registro no arquivo JSONL de ingestão."""
    target = Path(output_file)
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_ingestion_history(
    input_file: str | Path,
) -> list[dict[str, Any]]:
    """Carrega o histórico de ingestão a partir do arquivo JSONL."""
    source = Path(input_file)
    if not source.exists():
        return []

    history: list[dict[str, Any]] = []

    with source.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            line = line.strip()
            if not line:
                continue
            history.append(json.loads(line))

    return history

```


---
## src\storage\silver_store.py
Linhas: 136
Classes: -
Funções: _normalize_filename, write_silver_dataset, merge_silver_dataset_by_business_key
```python
"""Persistência de datasets padronizados da camada silver."""

from pathlib import Path
import pandas as pd
from typing import Any, Dict, List, Union


_KNOWN_EXTENSIONS = (".parquet", ".csv")


def _normalize_filename(filename: str) -> str:
    """
    Remove extensões conhecidas (.csv, .parquet) do filename recebido,
    evitando duplicação como 'arquivo.csv.csv' quando quem chama já
    passa o nome com extensão.
    """
    stem = filename.strip()
    for ext in _KNOWN_EXTENSIONS:
        if stem.lower().endswith(ext):
            stem = stem[: -len(ext)]
            break
    return stem


def write_silver_dataset(
    records: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    filename: str,
    sep: str = ";",
    decimal: str = ",",
    encoding: str = "utf-8-sig",
) -> tuple[Path, Path]:
    """
    Persiste a lista de registros normalizados nos formatos CSV e Parquet,
    garantindo compatibilidade com o padrão regional brasileiro (ponto e vírgula).
    """
    filename = _normalize_filename(filename)

    if not records:
        csv_path = Path(output_dir) / f"{filename}.csv"
        parquet_path = Path(output_dir) / f"{filename}.parquet"
        return csv_path, parquet_path

    df = pd.DataFrame(records)

    # Conversão segura de tipos para garantir que o Parquet e o Risco não quebrem
    for col in df.columns:
        if "data" in col.lower() or "date" in col.lower() or col.lower().startswith("dt_"):
            df[col] = pd.to_datetime(df[col], errors="coerce")
        elif not (pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col])):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    csv_path = target_dir / f"{filename}.csv"
    parquet_path = target_dir / f"{filename}.parquet"

    # Restabelecido o padrão regional brasileiro
    df.to_csv(csv_path, index=False, sep=sep, decimal=decimal, encoding=encoding)
    
    # Compressão Snappy do Parquet (Essencial para o motor de Risco e Power BI)
    df.to_parquet(parquet_path, index=False, engine="pyarrow", compression="snappy")

    return csv_path, parquet_path


def merge_silver_dataset_by_business_key(
    records: List[Dict[str, Any]],
    output_dir: Union[str, Path],
    filename: str,
    business_keys: List[str],
    sep: str = ";",
    decimal: str = ",",
    encoding: str = "utf-8-sig",
) -> tuple[Path, Path]:
    """
    Realiza o merge incremental preservando histórico completo (§1.5 — imutabilidade).

    Todas as versões são mantidas. A mais recente recebe _STATUS_REGISTRO = 'VIGENTE'
    e as anteriores recebem 'SUBSTITUIDO'.
    """
    filename = _normalize_filename(filename)

    target_dir = Path(output_dir)
    parquet_path = target_dir / f"{filename}.parquet"

    if not records:
        return parquet_path, parquet_path

    df_new = pd.DataFrame(records)
    dt_carga = pd.Timestamp.now()
    df_new["_DT_CARGA"] = dt_carga
    df_new["_STATUS_REGISTRO"] = "VIGENTE" # Nova versão entra como vigente

    if parquet_path.exists():
        df_existing = pd.read_parquet(parquet_path)

        # Garante colunas de controle no histórico legado
        if "_VERSAO_REGISTRO" not in df_existing.columns:
            df_existing["_VERSAO_REGISTRO"] = 1
        if "_DT_CARGA" not in df_existing.columns:
            df_existing["_DT_CARGA"] = pd.NaT
        if "_STATUS_REGISTRO" not in df_existing.columns:
            df_existing["_STATUS_REGISTRO"] = "VIGENTE"

        # Identifica chaves de negócio que estão sendo atualizadas e rebaixa o status das antigas
        cond_atualizacao = df_existing.set_index(business_keys).index.isin(df_new.set_index(business_keys).index)
        df_existing.loc[cond_atualizacao, "_STATUS_REGISTRO"] = "SUBSTITUIDO"

        # Calcula a próxima versão para cada business_key
        max_versoes = (
            df_existing.groupby(business_keys, dropna=False)["_VERSAO_REGISTRO"]
            .max()
            .reset_index()
            .rename(columns={"_VERSAO_REGISTRO": "_MAX_VERSAO"})
        )

        df_new = pd.merge(df_new, max_versoes, on=business_keys, how="left")
        df_new["_MAX_VERSAO"] = df_new["_MAX_VERSAO"].fillna(0).astype(int)
        df_new["_VERSAO_REGISTRO"] = df_new["_MAX_VERSAO"] + 1
        df_new = df_new.drop(columns=["_MAX_VERSAO"])

        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_new["_VERSAO_REGISTRO"] = 1
        df_combined = df_new

    return write_silver_dataset(
        records=df_combined.to_dict(orient="records"),
        output_dir=output_dir,
        filename=filename,
        sep=sep,
        decimal=decimal,
        encoding=encoding
    )
```


---
## src\tests\test_domain_rule_engine.py
Linhas: 43
Classes: -
Funções: test_t132_engine_com_regras_dinamicas, test_t132_engine_fallback_nativo
```python
import sys
import pytest
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.ficha_validator import validate_record

logger = logging.getLogger("test_logger")

def test_t132_engine_com_regras_dinamicas():
    """Cenário 1: Engine consome regras parametrizadas diretamente do JSON."""
    quality_rules = {
        "rules": [
            {"field": "PROBABILIDADE_DEFAULT", "type": "range", "min": 0, "max": 100},
            {"field": "SCORE_BUREAU", "type": "min", "value": 0}
        ]
    }
    
    # Injetando um registro falho para testar a captura unificada
    record_invalido = {
        "CNPJ": "123", "EMPRESA": "TESTE",
        "PROBABILIDADE_DEFAULT": 105, # Viola max=100
        "SCORE_BUREAU": -5 # Viola min=0
    }
    
    erros, avisos = validate_record(record_invalido, ["CNPJ"], logger, quality_rules)
    
    assert any("PROBABILIDADE_DEFAULT" in e and "maior que o limite (100)" in e for e in erros)
    assert any("SCORE_BUREAU" in e and "menor que o limite (0)" in e for e in erros)

def test_t132_engine_fallback_nativo():
    """Cenário 2: Engine aplica regras nativas (fallback) se a comercializadora não possuir a chave rules."""
    quality_rules = None 
    
    record_invalido = {
        "CNPJ": "123", "EMPRESA": "TESTE",
        "PROBABILIDADE_DEFAULT": -10 # Regra nativa deve capturar o erro menor que zero
    }
    
    erros, avisos = validate_record(record_invalido, ["CNPJ"], logger, quality_rules)
    assert any("PROBABILIDADE_DEFAULT" in e and "fora do intervalo" in e for e in erros)
```


---
## src\tests\test_field_type_normalizer.py
Linhas: 71
Classes: MockContext
Funções: mock_context, test_t131_normalizer_using_python_class, test_t131_normalizer_fallback_json, control_file
```python
import sys
import json
import logging
import pytest
from pathlib import Path

# Ajuste do path para a raiz do código fonte
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from silver.field_type_normalizer import normalize_record

logger = logging.getLogger("test_logger")

@pytest.fixture
def mock_context(tmp_path):
    """Cria um contexto falso simulando a presença de um JSON de fallback."""
    control_dir = tmp_path / "control" / "quality"
    control_dir.mkdir(parents=True)
    
    fallback_json = control_dir / "field_types_teste.json"
    fallback_data = {
        "date_fields": ["DATA_TESTE"],
        "float_fields": ["VALOR_TESTE"],
        "text_fields": ["NOME_TESTE"],
        "cnpj_fields": ["CNPJ_TESTE"]
    }
    fallback_json.write_text(json.dumps(fallback_data))
    
    class MockContext:
        def control_file(self, key):
            if key == "field_types_teste":
                return fallback_json
            return fallback_json
            
    return MockContext()

def test_t131_normalizer_using_python_class(mock_context):
    """Cenário 1: Usa o slug mapeado e consome a tipagem via Classe Python."""
    slug = "field_types_fichas_comercializadoras"
    
    raw_record = {
        "CNPJ": "12.345.678/0001-90",
        "DATA_DEMONSTRACAO_FINANCEIRA": "2024",
        "PATRIMONIO_LIQUIDO": "1500.5",
        "SIGLA": "  EMPRESA X  "
    }
    
    normalized = normalize_record(raw_record, mock_context, slug, logger)
    
    assert normalized["CNPJ"] == "12345678000190"
    assert normalized["DATA_DEMONSTRACAO_FINANCEIRA"] == "31/12/2024"
    assert normalized["PATRIMONIO_LIQUIDO"] == 1500.5
    assert normalized["SIGLA"] == "EMPRESA X"

def test_t131_normalizer_fallback_json(mock_context):
    """Cenário 2: Usa um slug inexistente na classe e força a leitura do JSON."""
    slug = "field_types_teste"
    
    raw_record = {
        "CNPJ_TESTE": "98.765.432/0001-10",
        "DATA_TESTE": "15/10/2023",
        "VALOR_TESTE": " 300.0 ",
        "NOME_TESTE": "  TESTE  "
    }
    
    normalized = normalize_record(raw_record, mock_context, slug, logger)
    
    assert normalized["CNPJ_TESTE"] == "98765432000110"
    assert normalized["DATA_TESTE"] == "2023-10-15"
    assert normalized["VALOR_TESTE"] == 300.0
    assert normalized["NOME_TESTE"] == "TESTE"
```


---
## src\tests\test_mtm_ingestion.py
Linhas: 135
Classes: MockContext
Funções: mock_context_factory, test_t222_ingestao_e_reconciliacao_mtm_sucesso, test_t222_falha_reconciliacao_mtm, _create_mock_context, __init__, path
```python
import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.mtm_ingestion_service import ingest_mtm_data, MtmReconciliationError


@pytest.fixture
def mock_context_factory(tmp_path):
    """Factory para criar um MockContext com configurações de tolerância customizáveis."""
    def _create_mock_context(tolerancia=0.01):
        class MockContext:
            def __init__(self):
                self.config = {
                    "reconciliacao_mtm": {
                        "tolerancia_absoluta": tolerancia
                    }
                }

            def path(self, key):
                if key == "entradas":
                    return tmp_path / "ENTRADAS"
                if key == "bronze":
                    return tmp_path / "SAIDAS" / "bronze"
                if key == "silver":
                    return tmp_path / "SAIDAS" / "silver"
                if key == "log_runner":
                    p = tmp_path / "LOGS"
                    p.mkdir(parents=True, exist_ok=True)
                    return p
                return tmp_path
        return MockContext()
    return _create_mock_context


@pytest.mark.parametrize("tolerancia_teste", [0.01, 0.0])
def test_t222_ingestao_e_reconciliacao_mtm_sucesso(tmp_path, mock_context_factory, tolerancia_teste):
    """Garante que a ingestão cria a cópia na Bronze e agrega na Silver com reconciliação."""
    
    # 1. Estrutura mock de diretórios
    entradas_mtm = tmp_path / "ENTRADAS" / "mtm"
    entradas_mtm.mkdir(parents=True)
    
    # 2. CSV mock com MTM positivo, negativo e Notional (via ENERGIA_MWM)
    csv_content = (
        "COD_CONTRATO;CNPJ;MTM_TOTAL;DATA_AVALIACAO;ENERGIA_MWM\n"
        "C1;12345678000199;1000,50;2026-08-10;10\n"
        "C2;12345678000199;2000,50;2026-08-10;20\n"
        "C3;98765432000188;500,00;2026-08-10;5\n"
        "C4;12345678000199;-300,25;2026-08-10;3"  # Linha com MTM negativo
    )
    (entradas_mtm / "mtm_amostra.csv").write_text(csv_content, encoding="utf-8")
    
    # 3. Executa a ingestão com a tolerância parametrizada
    mock_context = mock_context_factory(tolerancia=tolerancia_teste)
    res = ingest_mtm_data(mock_context)
    
    # 4. Validações do resultado
    assert res["status"] == "SUCESSO"
    assert res["linhas_processadas"] == 4
    assert res["contrapartes_consolidadas"] == 2
    
    # Valida presença do snapshot na Bronze
    bronze_dir = tmp_path / "SAIDAS" / "bronze" / "snapshots_fontes" / "mtm"
    bronze_files = list(bronze_dir.glob("*.csv"))
    assert len(bronze_files) == 1, "Snapshot bruto deveria estar salvo na Bronze."
    
    # Valida arquivo de saída Silver
    silver_file = tmp_path / "SAIDAS" / "silver" / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
    assert silver_file.exists(), "Arquivo Parquet Silver deveria ter sido gerado."
    
    df_silver = pd.read_parquet(silver_file)
    assert not df_silver.empty
    
    # Valida agregação da EMPRESA A (CNPJ 12345678000199)
    empresa_a = df_silver[df_silver["CNPJ"] == "12345678000199"].iloc[0]
    # MTM Positivo: C1 (1000.50) + C2 (2000.50) = 3001.00
    assert empresa_a["MTM_POSITIVO_TOTAL"] == pytest.approx(3001.00)
    # MTM Negativo: C4 (-300.25)
    assert empresa_a["MTM_NEGATIVO_TOTAL"] == pytest.approx(300.25)
    # Notional: C1 (10) + C2 (20) + C4 (3) = 33
    assert empresa_a["NOTIONAL_TOTAL"] == pytest.approx(33.0)

    # Valida agregação da EMPRESA B (CNPJ 98765432000188)
    empresa_b = df_silver[df_silver["CNPJ"] == "98765432000188"].iloc[0]
    assert empresa_b["MTM_POSITIVO_TOTAL"] == pytest.approx(500.00)
    assert empresa_b["MTM_NEGATIVO_TOTAL"] == pytest.approx(0.0)
    assert empresa_b["NOTIONAL_TOTAL"] == pytest.approx(5.0)


@pytest.mark.parametrize(
    "campo_divergente, valor_mock_divergente, mensagem_erro_esperada",
    [
        ("MTM_POSITIVO_TOTAL", 1000.00, "Divergência de reconciliação no MTM Positivo Total"),
        ("MTM_NEGATIVO_TOTAL", 200.00, "Divergência de reconciliação no MTM Negativo Total"),
        ("NOTIONAL_TOTAL", 49.0, "Divergência de reconciliação no Notional Total"),
    ],
)
def test_t222_falha_reconciliacao_mtm(
    tmp_path, mock_context_factory, monkeypatch, campo_divergente, valor_mock_divergente, mensagem_erro_esperada
):
    """Valida se MtmReconciliationError é levantada quando a reconciliação falha."""
    # 1. Prepara o ambiente como no teste de sucesso
    entradas_mtm = tmp_path / "ENTRADAS" / "mtm"
    entradas_mtm.mkdir(parents=True)
    # CSV com valores para MTM positivo, negativo e notional
    csv_content = "COD_CONTRATO;CNPJ;MTM_TOTAL;ENERGIA_MWM\nC1;12345678000199;1000,50;50\nC2;12345678000199;-200,25;0"
    (entradas_mtm / "mtm_amostra.csv").write_text(csv_content, encoding="utf-8")

    mock_context = mock_context_factory(tolerancia=0.01)

    # 2. Usa monkeypatch para simular uma falha na agregação
    # O conector lê os valores originais, mas forçamos a agregação a produzir um valor diferente
    # para o campo parametrizado.
    mock_record = {
        "CNPJ": "12345678000199",
        "DATA_BASE": "2026-08-10",
        "MTM_POSITIVO_TOTAL": 1000.50,
        "MTM_NEGATIVO_TOTAL": 200.25,
        "NOTIONAL_TOTAL": 50.0,
    }
    mock_record[campo_divergente] = valor_mock_divergente
    df_agregado_mock = pd.DataFrame([mock_record])

    # Mocka o método 'agg' do GroupBy para retornar nosso DataFrame com divergência
    monkeypatch.setattr(pd.core.groupby.generic.DataFrameGroupBy, "agg", lambda *args, **kwargs: df_agregado_mock)

    # 3. Executa e valida se a exceção correta é levantada
    with pytest.raises(MtmReconciliationError) as excinfo:
        ingest_mtm_data(mock_context)

    assert mensagem_erro_esperada in str(excinfo.value)
```
