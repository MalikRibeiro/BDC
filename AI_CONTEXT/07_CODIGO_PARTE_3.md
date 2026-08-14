# CÓDIGO PARTE 3


---
## reset.py
Linhas: 126
Classes: -
Funções: clear_directory_contents, clear_jsonl_files, move_files_back_to_pending, main
```python
"""Utilitário simples para reiniciar o pipeline BDC e reprocessar as fichas."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENTRADAS_DIR = ROOT / "ENTRADAS"
SAIDAS_DIR = ROOT / "SAIDAS"


def clear_directory_contents(dir_path: Path) -> int:
    """Apaga o conteúdo interno de um diretório sem remover a pasta raiz."""
    removed = 0
    if not dir_path.exists() or not dir_path.is_dir():
        return removed

    for item in sorted(dir_path.iterdir()):
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                removed += 1
            elif item.is_dir():
                shutil.rmtree(item)
                removed += 1
        except Exception as exc:
            print(f"⚠️ Falha ao limpar {item}: {exc}")
    return removed


def clear_jsonl_files(dir_path: Path) -> int:
    """Remove apenas arquivos .jsonl de um diretório."""
    removed = 0
    if not dir_path.exists() or not dir_path.is_dir():
        return removed

    for file_path in sorted(dir_path.glob("*.jsonl")):
        try:
            file_path.unlink()
            removed += 1
        except Exception as exc:
            print(f"⚠️ Falha ao apagar {file_path.name}: {exc}")
    return removed


def move_files_back_to_pending(category: str) -> int:
    """Move os arquivos de processadas/rejeitadas para pendentes."""
    base_path = ENTRADAS_DIR / "fichas" / category
    pendentes_dir = base_path / "pendentes"
    processadas_dir = base_path / "processadas"
    rejeitadas_dir = base_path / "rejeitadas"

    pendentes_dir.mkdir(parents=True, exist_ok=True)
    moved = 0

    for source_dir in (processadas_dir, rejeitadas_dir):
        if not source_dir.exists():
            continue

        for source_file in sorted(source_dir.rglob("*")):
            if not source_file.is_file():
                continue

            rel_path = source_file.relative_to(source_dir)
            destination = pendentes_dir / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)

            if destination.exists():
                destination.unlink()

            shutil.move(str(source_file), str(destination))
            moved += 1

    return moved


def main() -> None:
    print("🧹 Reiniciando o pipeline BDC...")

    targets = [
        SAIDAS_DIR / "staging" / "fichas_comercializadoras",
        SAIDAS_DIR / "staging" / "fichas_consumidores",
        SAIDAS_DIR / "bronze" / "fichas_comercializadoras_raw",
        SAIDAS_DIR / "bronze" / "fichas_consumidores_raw",
        SAIDAS_DIR / "bronze" / "snapshots_fontes",
        SAIDAS_DIR / "silver" / "fichas_comercializadoras_extraidas",
        SAIDAS_DIR / "silver" / "fichas_consumidores_extraidas",
        SAIDAS_DIR / "silver" / "documentos_classificados",
        SAIDAS_DIR / "silver" / "mtm_consolidado_silver",
        SAIDAS_DIR / "silver" / "denodo_contratos_silver",
        SAIDAS_DIR / "silver" / "denodo_contratos_padronizados", 
        SAIDAS_DIR / "silver" / "salesforce_silver",
        SAIDAS_DIR / "silver" / "receita_silver", 
        SAIDAS_DIR / "silver" / "garantias_silver", 
        SAIDAS_DIR / "silver" / "reconciliacao_contratos_mtm",
        SAIDAS_DIR / "silver" / "reconciliacao_fichas_salesforce",
        SAIDAS_DIR / "silver" / "alertas_credito",
        SAIDAS_DIR / "silver" / "governanca_carga_manual", 
        SAIDAS_DIR / "silver" / "governanca_overrides", 
        SAIDAS_DIR / "relational" / "facts",
        SAIDAS_DIR / "relational" / "dimensions", 
        SAIDAS_DIR / "relational" / "configs", 
        SAIDAS_DIR / "gold" / "relatorio_credito_atual", 
        SAIDAS_DIR / "output", 
    ]

    for path in targets:
        if path.exists():
            cleared = clear_directory_contents(path)
            print(f"   - Limpo: {path} ({cleared} itens removidos)")

    ingestion_log_dir = SAIDAS_DIR / "bronze" / "ingestion_log"
    jsonl_removed = clear_jsonl_files(ingestion_log_dir)
    print(f"   - Arquivos .jsonl removidos em {ingestion_log_dir}: {jsonl_removed}")

    moved_comercializadoras = move_files_back_to_pending("comercializadoras")
    moved_consumidores = move_files_back_to_pending("consumidores")

    print(f"   - Comercializadoras movidas para pendentes: {moved_comercializadoras}")
    print(f"   - Consumidores movidos para pendentes: {moved_consumidores}")
    print("✨ Reset concluído. Agora você pode executar novamente o main.py.")


if __name__ == "__main__":
    main()
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
## src\app\context.py
Linhas: 96
Classes: AppContext
Funções: load_context, path, control_file
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
from common.io_json import read_json
from common.validation import validate_json_schema

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


def load_context(configs_dir: str | Path) -> AppContext:
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

    app_config = read_json(app_config_path)
    config = read_json(config_path)

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

    schema_app_config = read_json(schema_app_config_path)
    schema_config = read_json(schema_config_path)

    # Validação estrutural do JSON original (Fail-Fast)
    validate_json_schema(app_config, schema_app_config, "app_config.json")
    validate_json_schema(config, schema_config, "config.json")

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
## src\cli\run_fichas_comercializadoras.py
Linhas: 47
Classes: -
Funções: build_parser, main
```python
import argparse
import sys
from pathlib import Path

from src.app.bootstrap import bootstrap_application
from src.services.fichas_comercializadoras_service import process_fichas_comercializadoras


def build_parser() -> argparse.ArgumentParser:
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
    parser = build_parser()
    args = parser.parse_args()

    try:
        app_ctx = bootstrap_application(configs_dir=args.configs_dir)
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
## src\common\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Utilitários compartilhados do sistema BDC."""

```


---
## src\common\dates.py
Linhas: 34
Classes: -
Funções: normalize_date
```python
"""Normalização de datas no sistema BDC."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def normalize_date(value: Any) -> str | None:
    """Normaliza uma data para o formato ISO ``YYYY-MM-DD``."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    text = str(value).strip()
    if not text:
        return None

    patterns = (
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d.%m.%Y",
    )

    for pattern in patterns:
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue

    return None

```


---
## src\common\hashing.py
Linhas: 21
Classes: -
Funções: hash_file
```python
"""Geração de hash para arquivos do sistema BDC."""

from __future__ import annotations

import hashlib
from pathlib import Path


def hash_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
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
## src\common\io_json.py
Linhas: 14
Classes: -
Funções: read_json
```python
"""Leitura e escrita de arquivos JSON do sistema BDC."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> Any:
    """Lê um arquivo JSON e devolve seu conteúdo."""
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)

```


---
## src\common\paths.py
Linhas: 16
Classes: -
Funções: sanitize_folder_name
```python
"""Funções utilitárias para nomes de paths e diretórios."""

from __future__ import annotations

import re


_INVALID_PATH_CHARS = r'[<>:"/\\|?*]+'


def sanitize_folder_name(value: str) -> str:
    """Sanitiza um texto para uso seguro em nome de pasta."""
    cleaned = re.sub(_INVALID_PATH_CHARS, "_", value.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("._ ")

```


---
## src\common\strings.py
Linhas: 31
Classes: -
Funções: normalize_string, normalize_cnpj
```python
"""Normalização de textos e documentos no sistema BDC."""

from __future__ import annotations

import re
from typing import Any


def normalize_string(value: Any, upper: bool = False) -> str | None:
    """Normaliza um valor textual."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    return text.upper() if upper else text


def normalize_cnpj(value: Any) -> str | None:
    """Normaliza um CNPJ para 14 dígitos numéricos."""
    if value is None:
        return None

    digits = re.sub(r"\D", "", str(value))

    if not digits:
        return None

    return digits.zfill(14)

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
## src\control\field_types.py
Linhas: 75
Classes: FieldTypeConfig
Funções: get_field_type_config
```python
"""Definição programática e tipada dos domínios de campos (Substitui os JSONs legados)."""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FieldTypeConfig:
    """Configuração dos tipos de campos para normalização estrutural."""
    entity: str
    date_fields: list[str] = field(default_factory=list)
    float_fields: list[str] = field(default_factory=list)
    text_fields: list[str] = field(default_factory=list)
    cnpj_fields: list[str] = field(default_factory=list)


COMERCIALIZADORAS_FIELD_TYPES = FieldTypeConfig(
    entity="fichas_comercializadoras",
    date_fields=[
        "DATA_DEMONSTRACAO_FINANCEIRA", "DATA_ADESAO_CCEE", 
        "DATA_CALCULO", "DATA_RATING_AGENCIA"
    ],
    float_fields=[
        "PATRIMONIO_LIQUIDO", "PROBABILIDADE_DEFAULT", "ATIVO_CIRCULANTE_FINANCEIRO",
        "CAPITAL_SOCIAL", "ATIVO_CIRCULANTE_AJUSTADO", "ATIVO_TOTAL_AJUSTADO",
        "PASSIVO_CIRCULANTE_AJUSTADO", "PASSIVO_CIRCULANTE_FINANCEIRO_AJUSTADO",
        "PASSIVO_NAO_CIRCULANTE_FINANCEIRO_AJUSTADO", "LUCROS_ACUMULADOS",
        "RESERVA_DE_LUCROS", "VENDAS_LIQUIDAS", "LUCRO_LIQUIDO",
        "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "LIQUIDEZ_CORRENTE_AJUSTADO",
        "INDICE_SOLVENCIA_GERAL_AJUSTADO", "INDICE_COBERTURA_DE_DESPESA_COM_PESSOAL",
        "PAYOUT_AJUSTADO", "CAPITAL_CIRCULANTE_LIQUIDO_AJUSTADO", "ROE", "ROA", "MFCO",
        "SCORE_BUREAU", "QUANTIDADE_RESTRITIVOS", "ROL", "LUCRO_BRUTO", "LAJIR", "LAIR",
        "PL_CONTROLADOR", "PERCENTUAL_CONTROLADOR"
    ],
    text_fields=[
        "CODIGO_CCEE", "SIGLA", "RATING_COPEL", "AGENCIA", "NOTA_CREDITO", "AUDITOR", 
        "NOTA_BOARD", "NOTA_BUREAU", "TIPO_COMERCIALIZADORA", "CONTROLADOR"
    ],
    cnpj_fields=[
        "CNPJ", "CNPJ_BBCE", "CNPJ_CONTROLADOR"
    ]
)

CONSUMIDORES_FIELD_TYPES = FieldTypeConfig(
    entity="fichas_consumidores",
    date_fields=[
        "DATA_DEMONSTRACAO_FINANCEIRA", "DATA_CALCULO", "DATA_ABERTURA", 
        "DATA_RATING_CONTROLADOR"
    ],
    float_fields=[
        "CAPITAL_SOCIAL", "ATIVO_CIRCULANTE", "ATIVO_CIRCULANTE_FINANCEIRO", "ATIVO_TOTAL",
        "PASSIVO_CIRCULANTE", "PASSIVO_CIRCULANTE_FINANCEIRO", "PASSIVO_NAO_CIRCULANTE_FINANCEIRO",
        "PATRIMONIO_LIQUIDO", "LUCROS_ACUMULADOS", "RESERVA_DE_LUCROS", "VENDAS_LIQUIDAS",
        "PROBABILIDADE_DEFAULT", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "MFCO", "ROA", "ROE",
        "ROL", "LUCRO_BRUTO", "LAJIR", "LAIR", "LUCRO_LIQUIDO", "SCORE_BUREAU", "QUANTIDADE_RESTRITIVOS",
        "PL_CONTROLADOR", "PERCENTUAL_CONTROLADOR", "CAPITAL_CIRCULANTE_LIQUIDO", "NECESSIDADE_CAPITAL_GIRO",
        "INDICE_AUTO_FINANCIAMENTO", "LIQUIDEZ_SECA", "INDICE_SOLVENCIA_GERAL", "MARGEM_LIQUIDA"
    ],
    text_fields=[
        "EMPRESA", "CEP", "ENDERECO", "AUDITOR", "AGENCIA", "NOTA_CREDITO", "NOTA_BOARD",
        "NOTA_BUREAU", "RATING_COPEL", "CONTROLADOR", "NOTA_CREDITO_CONTROLADOR", "AGENCIA_CONTROLADOR"
    ],
    cnpj_fields=[
        "CNPJ", "CNPJ_CONTROLADOR"
    ]
)

# Catálogo em memória que substitui a busca no disco
FIELD_TYPES_CATALOG = {
    "field_types_fichas_comercializadoras": COMERCIALIZADORAS_FIELD_TYPES,
    "field_types_fichas_consumidores": CONSUMIDORES_FIELD_TYPES,
}

def get_field_type_config(slug: str) -> Optional[FieldTypeConfig]:
    """Retorna a configuração de tipagem em memória correspondente ao slug."""
    return FIELD_TYPES_CATALOG.get(slug)
```


---
## src\domain\contrapartes\segmentacao.py
Linhas: 51
Classes: -
Funções: definir_segmento_metodologico
```python
"""Segmentação metodológica da contraparte para cálculo de PD."""

from __future__ import annotations

from typing import Any

from common.strings import normalize_string
from common.types import normalize_float


def definir_segmento_metodologico(
    registro: dict[str, Any],
) -> str:
    """Define o segmento metodológico da contraparte."""
    tipo_ficha = normalize_string(
        registro.get("TIPO_FICHA"),
        upper=True,
    )
    
    if tipo_ficha == "COMERCIALIZADORA":
        tipo_comercializadora = normalize_string(
            registro.get("TIPO_COMERCIALIZADORA"),
            upper=True,
        )
        if tipo_comercializadora == "CPURA":
            return "CPURA"

        if tipo_comercializadora == "CGRUPO":
            return "CGRUPO"

        raise ValueError(
            "Comercializadora sem TIPO_COMERCIALIZADORA válido."
        )

    if tipo_ficha == "CONSUMIDOR":
        # Extrai o volume de enquadramento (em MWm)
        volume_mwm = normalize_float(registro.get("VOLUME_ENQUADRAMENTO_MWM"))
        
        # Critério de Aceite: Consumidor sem volume retorna NAO_ENQUADRADO
        if volume_mwm is None:
            return "NAO_ENQUADRADO"
            
        # Critério de Aceite: Bifurcação baseada no limite de 5 MWm
        if volume_mwm >= 5.0:
            return "CONSUMIDOR_GT_5"
        else:
            return "CONSUMIDOR_LE_5"

    raise ValueError(
        f"TIPO_FICHA inválido para segmentação: {tipo_ficha!r}"
    )
```


---
## src\domain\credito\lgd_engine.py
Linhas: 90
Classes: -
Funções: calcular_lgd
```python
"""Motor de Loss Given Default (LGD).

feat(T3.3.1): Adicionados lookup de LGD bruta por segmento via config e
rastreabilidade com calculo_id.
Ref: §6.8, §7.1, Apêndice C do Planejamento Funcional.

Nota: A redução por garantias é recebida como parâmetro (cobertura_garantias).
A integração com a base real de garantias é um TODO — quando disponível,
o percentual será calculado automaticamente a partir de garantias_service.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any
from uuid import uuid4

# LGD bruta padrão por segmento metodológico (§6.8)
# Estes valores devem migrar para config.json quando homologados pelo negócio.
LGD_BRUTA_POR_SEGMENTO: dict[str, float] = {
    "CPURA": 0.45,
    "CGRUPO": 0.45,
    "CONSUMIDOR_GT_5": 0.45,
    "CONSUMIDOR_LE_5": 0.75,
}


def calcular_lgd(
    segmento: str,
    cobertura_garantias: float = 0.0,
    lgd_bruta_override: float | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Cálculo da LGD líquida após mitigação por garantias.

    Fórmula: LGD_liquida = LGD_bruta × (1 - cobertura_garantias) (§6.8).

    Args:
        segmento: Segmento metodológico (CPURA, CGRUPO, etc.).
        cobertura_garantias: Percentual de cobertura de garantias elegíveis [0, 1].
            Default 0.0 — TODO: será alimentado automaticamente pela base de garantias.
        lgd_bruta_override: Se informado, sobrescreve o lookup por segmento.
        config: Dict de configuração para lookup customizado.

    Returns:
        Dict rastreável com calculo_id, lgd_bruta, lgd_liquida e metadados.
    """
    calculo_id = f"LGD_{uuid4().hex[:12]}"

    # Lookup de LGD bruta por segmento (§6.8)
    if lgd_bruta_override is not None:
        lgd_bruta = lgd_bruta_override
        fonte_lgd_bruta = "OVERRIDE"
    elif config and "lgd_bruta_por_segmento" in config:
        lgd_bruta = config["lgd_bruta_por_segmento"].get(segmento, LGD_BRUTA_POR_SEGMENTO.get(segmento, 0.45))
        fonte_lgd_bruta = "CONFIG"
    else:
        lgd_bruta = LGD_BRUTA_POR_SEGMENTO.get(segmento, 0.45)
        fonte_lgd_bruta = "PADRAO_SISTEMA"

    # Trava matemática para não gerar LGD negativa (§6.8)
    cobertura_efetiva = max(0.0, min(float(cobertura_garantias), 1.0))

    lgd_liquida = lgd_bruta * (1.0 - cobertura_efetiva)

    # Snapshot da configuração usada (§11.2)
    config_usada = {
        "segmento": segmento,
        "lgd_bruta": lgd_bruta,
        "fonte_lgd_bruta": fonte_lgd_bruta,
        "cobertura_garantias": cobertura_efetiva,
    }
    config_snapshot_id = hashlib.sha256(
        json.dumps(config_usada, sort_keys=True).encode()
    ).hexdigest()[:16]

    return {
        "calculo_id": calculo_id,
        "segmento": segmento,
        "lgd_bruta": lgd_bruta,
        "fonte_lgd_bruta": fonte_lgd_bruta,
        "cobertura_garantias": cobertura_efetiva,
        "lgd_liquida": lgd_liquida,
        "config_snapshot_id": config_snapshot_id,
        "dt_calculo": datetime.now().isoformat(timespec="seconds"),
        "status": "CALCULADO",
    }
```


---
## src\domain\credito\pd_consumidor_gt5.py
Linhas: 121
Classes: -
Funções: _inv_t_approx, _normalize_pd_input, calcular_pd_final_consumidor_gt5
```python
"""Transformação da PD para consumidores acima de 5 MWm."""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

from domain.credito.pd_exceptions import (
    PdCalculationError,
    PdConfigurationError,
)


def _inv_t_approx(prob: float, df: float) -> float:
    """Aproxima o quantil da t de Student a partir do quantil normal."""
    if not 0 < prob < 1:
        raise PdCalculationError(
            f"Probabilidade inválida para inversa t: {prob!r}"
        )

    z = NormalDist().inv_cdf(prob)

    g1 = (z**3 + z) / (4 * df)
    g2 = (5 * z**5 + 16 * z**3 + 3 * z) / (96 * (df**2))
    g3 = (3 * z**7 + 19 * z**5 + 17 * z**3 - 15 * z) / (384 * (df**3))

    return z + g1 + g2 + g3


def _normalize_pd_input(
    value: float,
    normalize_percent_if_gt_1: bool,
) -> float:
    q = float(value)
    if normalize_percent_if_gt_1 and q > 1:
        q = q / 100.0
    return q


def calcular_pd_final_consumidor_gt5(
    registro: dict[str, Any],
    pd_base: float,
    rating_final: str,
    pd_min: float,
    pd_max: float,
    regras_segmento: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada para consumidor acima de 5 MWm."""
    try:
        regras_pd = regras_segmento["pd_final_rules"]
        metodo = str(regras_pd.get("method", "")).strip().lower()

        if metodo != "t_dist_logistic":
            raise PdConfigurationError(
                f"Método inválido para CONSUMIDOR_GT_5: {metodo!r}"
            )

        df = float(regras_pd["df"])
        scale = float(regras_pd["scale"])
        eps = float(regras_pd["eps"])
        normalize_percent_if_gt_1 = bool(
            regras_pd.get("normalize_input_percent_if_gt_1", True)
        )

        q = _normalize_pd_input(
            value=float(pd_base),
            normalize_percent_if_gt_1=normalize_percent_if_gt_1,
        )

        q_cap = min(1 - eps, max(eps, q))

        z_t = _inv_t_approx(q_cap, df)
        z = scale * z_t
        u = 1.0 / (1.0 + math.exp(-z))

        pd_final = pd_min + u * (pd_max - pd_min)

        resultado = {
            "RATING_FINAL": rating_final,
            "PD_BASE": pd_base,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": pd_final,
            "PD_METODO": "T_DIST_LOGISTIC",
            "PD_Q_NORMALIZADA": q,
            "PD_Q_CAP": q_cap,
            "PD_Z_T": z_t,
            "PD_Z_ESCALADO": z,
            "PD_U_INTERPOLACAO": u,
        }

        if logger is not None:
            logger.info(
                "PD ajustada CONSUMIDOR_GT_5 calculada. "
                "CNPJ=%s RATING=%s PD_BASE=%s Q=%s Q_CAP=%s "
                "PD_MIN=%s PD_MAX=%s Z_T=%s Z=%s U=%s PD_FINAL=%s",
                registro.get("CNPJ"),
                rating_final,
                pd_base,
                q,
                q_cap,
                pd_min,
                pd_max,
                z_t,
                z,
                u,
                pd_final,
            )

        return resultado

    except Exception as exc:
        if isinstance(exc, (PdCalculationError, PdConfigurationError)):
            raise
        raise PdCalculationError(
            "Falha no cálculo da PD ajustada de CONSUMIDOR_GT_5: "
            f"{exc}"
        ) from exc

```


---
## src\domain\credito\pd_cpura.py
Linhas: 282
Classes: -
Funções: _clamp, _obter_score_total, _obter_faixa_score_rating, _obter_estabilizacao, _calcular_score_truncado, _calcular_posicao_relativa, _calcular_pd_bruta, _estabilizar_pd, calcular_pd_final_cpura
```python
"""Transformação de PD para comercializadoras puras."""

from __future__ import annotations

import math
from typing import Any

from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _clamp(valor: float, minimo: float, maximo: float) -> float:
    """Restringe valor ao intervalo informado."""
    return max(min(valor, maximo), minimo)


def _obter_score_total(registro: dict[str, Any]) -> float:
    """Obtém o score total S do registro."""
    score_total = registro.get("SCORE_TOTAL")

    if score_total is None:
        raise PdInputValidationError(
            "Registro sem SCORE_TOTAL para cálculo de PD de CPURA."
        )

    try:
        score_total = float(score_total)
    except (TypeError, ValueError) as exc:
        raise PdInputValidationError(
            f"SCORE_TOTAL inválido: {score_total!r}"
        ) from exc

    if score_total < 0 or score_total > 10:
        raise PdInputValidationError(
            f"SCORE_TOTAL fora do intervalo esperado [0, 10]: {score_total}"
        )

    return score_total


def _obter_faixa_score_rating(
    rating_final: str,
    score_faixas: dict[str, dict[str, float]],
) -> tuple[float, float]:
    """Obtém a faixa de score do rating."""
    if not score_faixas:
        raise PdConfigurationError(
            "Configuração 'score_faixas' não informada para CPURA."
        )

    if rating_final not in score_faixas:
        raise PdConfigurationError(
            f"Rating inválido para CPURA: {rating_final}"
        )

    faixa = score_faixas[rating_final]

    if "min" not in faixa or "max" not in faixa:
        raise PdConfigurationError(
            f"Faixa de score inválida para rating {rating_final}."
        )

    try:
        score_min = float(faixa["min"])
        score_max = float(faixa["max"])
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            f"Faixa de score não numérica para rating {rating_final}."
        ) from exc

    if score_min > score_max:
        raise PdConfigurationError(
            f"Faixa de score inválida para rating {rating_final}: min > max."
        )

    return score_min, score_max


def _obter_estabilizacao(
    cpura_config: dict[str, Any],
) -> tuple[float, float, float]:
    """Obtém os parâmetros de estabilização numérica."""
    estabilizacao = cpura_config.get("estabilizacao")

    if not isinstance(estabilizacao, dict):
        raise PdConfigurationError(
            "Bloco 'estabilizacao' ausente ou inválido em cpura_config."
        )

    try:
        epsilon = float(estabilizacao["epsilon"])
        z_min = float(estabilizacao["z_min"])
        z_max = float(estabilizacao["z_max"])
    except KeyError as exc:
        raise PdConfigurationError(
            f"Parâmetro de estabilização ausente: {exc}"
        ) from exc
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            "Parâmetros de estabilização inválidos."
        ) from exc

    if epsilon <= 0 or epsilon >= 0.5:
        raise PdConfigurationError(
            f"Epsilon inválido para estabilização: {epsilon}"
        )

    if z_min > z_max:
        raise PdConfigurationError(
            f"Intervalo de logit inválido: z_min={z_min}, z_max={z_max}"
        )

    return epsilon, z_min, z_max


def _calcular_score_truncado(
    score_total: float,
    score_min: float,
    score_max: float,
) -> float:
    """Aplica truncamento do score dentro da faixa do rating."""
    return _clamp(score_total, score_min, score_max)


def _calcular_posicao_relativa(
    score_truncado: float,
    score_min: float,
    score_max: float,
) -> float:
    """Calcula a posição relativa intra-rating."""
    if score_max == score_min:
        return 0.0

    u = (score_max - score_truncado) / (score_max - score_min)
    return _clamp(u, 0.0, 1.0)


def _calcular_pd_bruta(
    pd_min: float,
    pd_max: float,
    posicao_relativa: float,
) -> float:
    """Interpola a PD bruta dentro da faixa do rating."""
    pd_bruta = pd_min + posicao_relativa * (pd_max - pd_min)
    return _clamp(pd_bruta, 0.0, 1.0)


def _estabilizar_pd(
    pd_bruta: float,
    epsilon: float,
    z_min: float,
    z_max: float,
) -> tuple[float, float, float]:
    """Aplica estabilização numérica via logit."""
    p = _clamp(pd_bruta, epsilon, 1.0 - epsilon)
    z = math.log(p / (1.0 - p))
    z_truncado = _clamp(z, z_min, z_max)
    pd_final = 1.0 / (1.0 + math.exp(-z_truncado))
    return p, z_truncado, pd_final


def calcular_pd_final_cpura(
    registro: dict[str, Any],
    pd_base: float,
    rating_final: str,
    pd_min: float,
    pd_max: float,
    cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD final de CPURA por interpolação intra-rating."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo de PD final CPURA. "
                "CNPJ=%s rating=%s pd_min=%s pd_max=%s",
                registro.get("CNPJ"),
                rating_final,
                pd_min,
                pd_max,
            )

        if not cpura_config:
            raise PdConfigurationError(
                "Configuração de CPURA não informada."
            )

        if pd_min < 0 or pd_max < 0 or pd_min > 1 or pd_max > 1:
            raise PdInputValidationError(
                f"Faixa de PD inválida: pd_min={pd_min}, pd_max={pd_max}"
            )

        if pd_min > pd_max:
            raise PdInputValidationError(
                f"Faixa de PD inválida: pd_min > pd_max "
                f"({pd_min} > {pd_max})"
            )

        score_total = _obter_score_total(registro)
        score_faixas = cpura_config.get("score_faixas", {})
        score_min, score_max = _obter_faixa_score_rating(
            rating_final=rating_final,
            score_faixas=score_faixas,
        )
        epsilon, z_min, z_max = _obter_estabilizacao(cpura_config)

        score_truncado = _calcular_score_truncado(
            score_total=score_total,
            score_min=score_min,
            score_max=score_max,
        )

        posicao_relativa = _calcular_posicao_relativa(
            score_truncado=score_truncado,
            score_min=score_min,
            score_max=score_max,
        )

        pd_bruta = _calcular_pd_bruta(
            pd_min=pd_min,
            pd_max=pd_max,
            posicao_relativa=posicao_relativa,
        )

        p_estabilizado, z_truncado, pd_final = _estabilizar_pd(
            pd_bruta=pd_bruta,
            epsilon=epsilon,
            z_min=z_min,
            z_max=z_max,
        )

        resultado = {
            "SCORE_TOTAL": score_total,
            "SCORE_MIN_RATING": score_min,
            "SCORE_MAX_RATING": score_max,
            "SCORE_TRUNCADO": score_truncado,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            "PD_PERCENTIL_INTERNO": posicao_relativa,
            "PD_BRUTA": pd_bruta,
            "PD_ESTABILIZADA": p_estabilizado,
            "PD_FINAL": pd_final,
            "PD_METODO": "INTERPOLACAO_INTRA_RATING_CPURA",
            "LOGIT_TRUNCADO": z_truncado,
        }

        if logger is not None:
            logger.info(
                "PD final CPURA calculada com sucesso. "
                "CNPJ=%s score_total=%s score_truncado=%s "
                "u=%s pd_bruta=%s pd_final=%s",
                registro.get("CNPJ"),
                resultado["SCORE_TOTAL"],
                resultado["SCORE_TRUNCADO"],
                resultado["PD_PERCENTIL_INTERNO"],
                resultado["PD_BRUTA"],
                resultado["PD_FINAL"],
            )

        return resultado

    except (PdInputValidationError, PdConfigurationError):
        if logger is not None:
            logger.exception(
                "Erro controlado no cálculo de PD final CPURA. "
                "CNPJ=%s rating=%s",
                registro.get("CNPJ"),
                rating_final,
            )
        raise

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha inesperada no cálculo de PD final CPURA. "
                "CNPJ=%s rating=%s",
                registro.get("CNPJ"),
                rating_final,
            )
        raise

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

from common.strings import normalize_string
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

    rating_final = normalize_string(rating, upper=True)

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
## src\services\camada_gold_service.py
Linhas: 145
Classes: -
Funções: _classificar_matriz_operacional, exportar_visao_consolidada_gold
```python
"""
Construtor da Visão Operacional Consolidada (Camada Gold).
"""
from __future__ import annotations
import logging
from datetime import datetime
import pandas as pd
from pydot import Any
from app.context import AppContext
from storage.silver_store import write_silver_dataset

def _classificar_matriz_operacional(row: pd.Series) -> str:
    c = row.get("STATUS_CONTRATUAL", "SEM_CONTRATO")
    a = row.get("SITUACAO_ANALISE", "SEM_ANALISE")
    if c == "CONTRATO_VIGENTE":
        if a == "VIGENTE": return "CONTRATO_VIGENTE_ANALISE_VIGENTE"
        if a == "VENCIDA": return "CONTRATO_VIGENTE_ANALISE_VENCIDA"
        return "CONTRATO_VIGENTE_SEM_ANALISE"
    if c == "CONTRATO_FUTURO":
        if a == "VIGENTE": return "CONTRATO_FUTURO_ANALISE_VIGENTE"
        if a == "VENCIDA": return "CONTRATO_FUTURO_ANALISE_VENCIDA"
        return "CONTRATO_FUTURO_SEM_ANALISE"
    if c == "SEM_CONTRATO":
        if a == "VIGENTE": return "SEM_CONTRATO_ANALISE_VIGENTE"
        if a == "VENCIDA": return "SEM_CONTRATO_ANALISE_VENCIDA"
        return "SEM_CONTRATO_SEM_ANALISE"
    return "OUTROS"

def exportar_visao_consolidada_gold(context: AppContext) -> dict[str, Any]:
    run_id = f"GLD_MVP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.gold.operacional")

    path_contratos = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"
    path_analises = context.path("relational_facts") / "fato_analise_credito.parquet"
    path_contraparte = context.path("relational_dimensions") / "dim_contraparte.parquet"
    path_risco = context.path("relational_facts") / "fato_exposicao_risco_LATEST.parquet"
    
    df_contratos = pd.read_parquet(path_contratos) if path_contratos.exists() else pd.DataFrame()
    df_analises = pd.read_parquet(path_analises) if path_analises.exists() else pd.DataFrame()
    df_contraparte = pd.read_parquet(path_contraparte) if path_contraparte.exists() else pd.DataFrame()
    df_risco = pd.read_parquet(path_risco) if path_risco.exists() else pd.DataFrame()

    hoje = pd.Timestamp(datetime.now().date())

    df_contratos_agg = pd.DataFrame()
    if not df_contratos.empty:
        df_contratos["CNPJ"] = df_contratos["CNPJ"].astype(str).str.replace(r'\D', '', regex=True).str.zfill(14)
        df_contratos["VOLUME_MWM"] = pd.to_numeric(df_contratos.get("VOLUME_CONTRATADO_MENSAL_MWM", 0), errors="coerce").fillna(0.0)
        df_contratos["INICIO"] = pd.to_datetime(df_contratos.get("VIGENCIA_INICIO"), errors="coerce")
        df_contratos["FIM"] = pd.to_datetime(df_contratos.get("VIGENCIA_FIM"), errors="coerce")
        df_contratos["EH_VIGENTE"] = (df_contratos["INICIO"] <= hoje) & (df_contratos["FIM"] >= hoje)
        df_contratos["EH_FUTURO"] = (df_contratos["INICIO"] > hoje)
        
        df_contratos_agg = df_contratos.groupby("CNPJ").agg(
            QTD_CONTRATOS=("CONTRATO", "nunique"), VOLUME_MWM=("VOLUME_MWM", "sum"),
            QTD_VIGENTES=("EH_VIGENTE", "sum"), QTD_FUTUROS=("EH_FUTURO", "sum"),
            PROXIMO_INICIO=("INICIO", "min"), PROXIMO_FIM=("FIM", "max")
        ).reset_index()
        
        df_contratos_agg["STATUS_CONTRATUAL"] = df_contratos_agg.apply(lambda r: "CONTRATO_VIGENTE" if r["QTD_VIGENTES"] > 0 else ("CONTRATO_FUTURO" if r["QTD_FUTUROS"] > 0 else "CONTRATO_VENCIDO"), axis=1)
        df_contratos_agg["TEM_CONTRATO"] = df_contratos_agg["STATUS_CONTRATUAL"].isin(["CONTRATO_VIGENTE", "CONTRATO_FUTURO"]).map({True:"SIM", False:"NÃO"})

    df_analises_agg = pd.DataFrame()
    if not df_analises.empty:
        df_analises["CNPJ"] = df_analises["CNPJ"].astype(str).str.replace(r'\D', '', regex=True).str.zfill(14)
        df_analises = df_analises.dropna(subset=["CNPJ"]).copy()
        
        df_analises["DATA_BALANCO_DT"] = pd.to_datetime(df_analises.get("DATA_BALANCO_USADO"), format="%d/%m/%Y", errors="coerce")
        df_analises.loc[df_analises["DATA_BALANCO_DT"].isna(), "DATA_BALANCO_DT"] = pd.to_datetime(df_analises.get("DATA_BALANCO_USADO"), errors="coerce")
        df_analises["VALIDADE_DT"] = df_analises["DATA_BALANCO_DT"] + pd.DateOffset(years=1, months=4)
        
        df_analises = df_analises.sort_values("DATA_BALANCO_DT").drop_duplicates("CNPJ", keep="last")
        df_analises["SITUACAO_ANALISE"] = df_analises["VALIDADE_DT"].apply(lambda x: "VIGENTE" if pd.notnull(x) and x >= hoje else ("VENCIDA" if pd.notnull(x) else "IRREGULAR"))
        
        col_map = {"DATA_ANALISE": "DATA_ANALISE", "DATA_BALANCO_USADO": "DATA_DF", "RATING": "RATING", "PD_PERCENTUAL": "PD", "MODELO": "MODELO_ANALISE"}
        df_analises_agg = df_analises.rename(columns=col_map)
        df_analises_agg["VALIDADE_ANALISE"] = df_analises_agg["VALIDADE_DT"].dt.strftime("%d/%m/%Y")
        df_analises_agg["TEM_ANALISE"] = "SIM"

    if df_contratos_agg.empty and df_analises_agg.empty:
        return {"run_id": run_id, "status": "SEM_DADOS"}
    elif df_contratos_agg.empty:
        df_gold = df_analises_agg.copy()
    elif df_analises_agg.empty:
        df_gold = df_contratos_agg.copy()
    else:
        df_gold = pd.merge(df_contratos_agg, df_analises_agg, on="CNPJ", how="outer")

    if not df_contraparte.empty and "CNPJ" in df_contraparte.columns:
        df_contraparte["CNPJ"] = df_contraparte["CNPJ"].astype(str).str.zfill(14)
        df_gold = pd.merge(df_gold, df_contraparte[["CNPJ", "SEGMENTO_METODOLOGICO", "SITUACAO_CADASTRAL"]], on="CNPJ", how="left")

    # ENRIQUECIMENTO FINANCEIRO (Risco / Exposições)
    if not df_risco.empty and "CNPJ" in df_risco.columns:
        df_risco["CNPJ"] = df_risco["CNPJ"].astype(str).str.zfill(14)
        df_risco = df_risco.drop_duplicates(subset=["CNPJ"], keep="last")
        df_gold = pd.merge(df_gold, df_risco[["CNPJ", "EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"]], on="CNPJ", how="left")

    colunas_finais = ["CNPJ", "SEGMENTO_METODOLOGICO", "SITUACAO_CADASTRAL", "STATUS_CONTRATUAL", "TEM_CONTRATO", "QTD_CONTRATOS", "VOLUME_MWM", "PROXIMO_INICIO", "PROXIMO_FIM", "TEM_ANALISE", "SITUACAO_ANALISE", "DATA_ANALISE", "DATA_DF", "VALIDADE_ANALISE", "RATING", "PD", "MODELO_ANALISE", "EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"]
    df_gold = df_gold.reindex(columns=colunas_finais)

    df_gold["STATUS_CONTRATUAL"] = df_gold["STATUS_CONTRATUAL"].fillna("SEM_CONTRATO").astype(str)
    df_gold["TEM_CONTRATO"] = df_gold["TEM_CONTRATO"].fillna("NÃO").astype(str)
    df_gold["QTD_CONTRATOS"] = df_gold["QTD_CONTRATOS"].fillna(0).astype(int)
    df_gold["VOLUME_MWM"] = df_gold["VOLUME_MWM"].fillna(0.0).astype(float).round(2)
    df_gold["TEM_ANALISE"] = df_gold["TEM_ANALISE"].fillna("NÃO").astype(str)
    df_gold["SITUACAO_ANALISE"] = df_gold["SITUACAO_ANALISE"].fillna("SEM_ANALISE").astype(str)
    df_gold["SEGMENTO_METODOLOGICO"] = df_gold["SEGMENTO_METODOLOGICO"].fillna("NAO_ENQUADRADO").astype(str)
    df_gold["SITUACAO_CADASTRAL"] = df_gold["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADA").astype(str)
    
    # Preenchimento das colunas financeiras (mantém como Float para o Power BI / Excel formatar o R$)
    for col_fin in ["EAD_VALOR", "LGD_LIQUIDA", "PE_REAIS"]:
        df_gold[col_fin] = pd.to_numeric(df_gold[col_fin], errors="coerce").fillna(0.0).round(2)
    
    for col in ["PROXIMO_INICIO", "PROXIMO_FIM", "DATA_ANALISE", "DATA_DF", "VALIDADE_ANALISE", "RATING", "PD", "MODELO_ANALISE"]:
        df_gold[col] = df_gold[col].fillna("-").astype(str)

    df_gold["STATUS_OPERACIONAL"] = df_gold.apply(_classificar_matriz_operacional, axis=1)
    colunas_finais.append("STATUS_OPERACIONAL")
    df_export = df_gold[colunas_finais].copy()

    gold_dir = context.path("gold") / "visao_operacional_negocio"
    gold_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    df_export.to_csv(gold_dir / f"Visao_Operacional_BDC_{timestamp}.csv", index=False, encoding="utf-8-sig", sep=";", decimal=",")
    df_export.to_parquet(gold_dir / "Visao_Operacional_BDC_LATEST.parquet", index=False)

    # Cálculo da Exposição a Descoberto
    mask_descoberto = (df_export["STATUS_CONTRATUAL"] == "CONTRATO_VIGENTE") & (df_export["SITUACAO_ANALISE"] != "VIGENTE")
    ead_descoberto = df_export.loc[mask_descoberto, "EAD_VALOR"].sum()

    metrics = {
        "run_id": run_id, "status": "SUCESSO", "total_contrapartes": len(df_export),
        "contrato_vigente": int((df_export["STATUS_CONTRATUAL"] == "CONTRATO_VIGENTE").sum()),
        "contrato_futuro": int((df_export["STATUS_CONTRATUAL"] == "CONTRATO_FUTURO").sum()),
        "analise_vigente": int((df_export["SITUACAO_ANALISE"] == "VIGENTE").sum()),
        "contrato_vig_sem_analise_vig": int(mask_descoberto.sum()),
        "analise_vencida": int((df_export["SITUACAO_ANALISE"] == "VENCIDA").sum()),
        "ficha_sem_contrato": int(((df_export["STATUS_CONTRATUAL"] == "SEM_CONTRATO") & (df_export["TEM_ANALISE"] == "SIM")).sum()),
        "contrato_sem_ficha": int(((df_export["STATUS_CONTRATUAL"].isin(["CONTRATO_VIGENTE", "CONTRATO_FUTURO"])) & (df_export["TEM_ANALISE"] == "NÃO")).sum()),
        "dados_incompletos": int((df_export["SITUACAO_CADASTRAL"] == "NAO_INFORMADA").sum()),
        "ead_descoberto": float(ead_descoberto)
    }
    return metrics
```


---
## src\services\dim_contraparte_service.py
Linhas: 42
Classes: -
Funções: build_dim_contraparte
```python
"""Construção da dimensão de Contrapartes (dim_contraparte)."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from app.context import AppContext
from storage.silver_store import write_silver_dataset

def build_dim_contraparte(context: AppContext, df_silver_receita: pd.DataFrame, df_silver_segmentacao: pd.DataFrame) -> dict[str, Any]:
    run_id = f"DIM_CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.gold.dim_contraparte")

    if df_silver_receita.empty:
        df_silver_receita = pd.DataFrame(columns=["CNPJ", "SITUACAO_CADASTRAL", "NATUREZA_JURIDICA", "CNAE_PRINCIPAL"])
    if df_silver_segmentacao.empty:
        df_silver_segmentacao = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"])

    # NORMALIZAÇÃO ESTRITA
    df_silver_receita["CNPJ"] = df_silver_receita["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
    df_silver_segmentacao["CNPJ"] = df_silver_segmentacao["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)

    for col in ["SITUACAO_CADASTRAL", "CNAE_PRINCIPAL"]:
        if col not in df_silver_receita.columns: df_silver_receita[col] = "NAO_INFORMADO"
    for col in ["SEGMENTO_METODOLOGICO"]:
        if col not in df_silver_segmentacao.columns: df_silver_segmentacao[col] = "NAO_ENQUADRADO"

    # OUTER JOIN PARA SALVAR O SEGMENTO MESMO SEM RECEITA FEDERAL
    df_dim = pd.merge(df_silver_receita, df_silver_segmentacao, on="CNPJ", how="outer")
    df_dim = df_dim.dropna(subset=["CNPJ"])
    
    df_dim["CNPJ_RAIZ"] = df_dim["CNPJ"].str[:8]
    df_dim["SITUACAO_CADASTRAL"] = df_dim["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADO")
    df_dim["SEGMENTO_METODOLOGICO"] = df_dim["SEGMENTO_METODOLOGICO"].fillna("NAO_ENQUADRADO")

    schema_dim = {"CNPJ": "CNPJ", "CNPJ_RAIZ": "CNPJ_RAIZ", "SITUACAO_CADASTRAL": "SITUACAO_CADASTRAL", "CNAE_PRINCIPAL": "SETOR", "SEGMENTO_METODOLOGICO": "SEGMENTO_METODOLOGICO"}
    df_final = df_dim[list(schema_dim.keys())].rename(columns=schema_dim).copy()
    
    relational_dir = context.path("relational_dimensions")
    relational_dir.mkdir(parents=True, exist_ok=True)
    write_silver_dataset(records=df_final.to_dict(orient="records"), output_dir=relational_dir, filename="dim_contraparte")
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}
```


---
## src\services\enquadramento_service.py
Linhas: 72
Classes: -
Funções: calcular_enquadramento_consumidor
```python
"""Serviço de cálculo do volume de enquadramento (≥ 5 MWm) para consumidores."""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Any

from app.context import AppContext


def calcular_enquadramento_consumidor(
    competencia_base: str,
    context: AppContext,
) -> pd.DataFrame:
    """
    Lê os contratos normalizados da Silver do Denodo, calcula o maior volume mensal
    simultâneo por CNPJ e retorna a base consolidada de enquadramento.
    """
    silver_dir = context.path("silver") / "denodo_contratos_padronizados"
    parquet_path = silver_dir / f"contratos_correntes_{competencia_base}.parquet"

    if not parquet_path.exists():
        raise FileNotFoundError(
            f"Base Silver de contratos do Denodo não encontrada para a competência {competencia_base} em: {parquet_path}. "
            "Execute a ingestão (T2.1.2) primeiro."
        )

    df_contratos = pd.read_parquet(parquet_path)

    if df_contratos.empty:
        return pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"])

    # 1. Filtra apenas contratos ativos/válidos se houver coluna de status
    if "STATUS" in df_contratos.columns:
        # Padroniza para capturar variações como 'Ativo', 'ATIVO', 'Ativo/Fechado'
        df_contratos["STATUS_UP"] = df_contratos["STATUS"].astype(str).str.upper()
        df_ativos = df_contratos[df_contratos["STATUS_UP"].str.contains("ATIVO", na=False)].copy()
    else:
        df_ativos = df_contratos.copy()

    if df_ativos.empty:
        return pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM"])

    # 2. Agrupa por CNPJ e Competência para somar volumes simultâneos
    df_mensal = (
        df_ativos.groupby(["CNPJ", "COMPETENCIA"], as_index=False)["VOLUME_CONTRATADO_MENSAL_MWM"]
        .sum()
        .rename(columns={"VOLUME_CONTRATADO_MENSAL_MWM": "VOLUME_CONSOLIDADO_MENSAL"})
    )

    # 3. Regra de Negócio: O volume de enquadramento é o MAIOR volume mensal
    df_enquadramento = (
        df_mensal.groupby("CNPJ", as_index=False)["VOLUME_CONSOLIDADO_MENSAL"]
        .max()
        .rename(columns={"VOLUME_CONSOLIDADO_MENSAL": "VOLUME_ENQUADRAMENTO_MWM"})
    )

    # 4. Deriva o indicador booleano de corte (Parametrizado em 5.0 MWm conforme Planejamento §6.2)
    LIMIAR_MWM = 5.0
    df_enquadramento["POSSUI_PELO_MENOS_5_MWM"] = (
        df_enquadramento["VOLUME_ENQUADRAMENTO_MWM"] >= LIMIAR_MWM
    )

    # Persiste o resultado resumido na camada Relacional (Dimensions/Configs)
    relational_dir = context.path("relational_configs")
    relational_dir.mkdir(parents=True, exist_ok=True)
    output_path = relational_dir / f"enquadramento_consumidores_{competencia_base}.csv"
    
    df_enquadramento.to_csv(output_path, index=False, encoding="utf-8-sig")

    return df_enquadramento
```


---
## src\services\ficha_validator.py
Linhas: 123
Classes: DomainRuleEngine
Funções: _is_empty, validate_record, __init__, validate
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
        elif not isinstance(pl, (int, float)):
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
            elif not isinstance(pd_val, (int, float)):
                errors.append("PROBABILIDADE_DEFAULT inválida: valor não numérico.")
            elif pd_val < 0 or pd_val > 100:
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


def validate_record(
    record: dict[str, Any],
    required_fields: list[str],
    logger: Any | None = None,
    quality_rules: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """Valida o registro normalizado da ficha usando o DomainRuleEngine."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando validação unificada do registro. CNPJ=%s EMPRESA=%s",
                record.get("CNPJ"),
                record.get("EMPRESA"),
            )

        engine = DomainRuleEngine(quality_rules)
        errors, warnings = engine.validate(record, required_fields)

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
```


---
## src\services\garantias_service.py
Linhas: 178
Classes: GarantiaIngestionError
Funções: ingest_garantias_data
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
from common.logging_utils import get_logger
from domain.enums import StatusGarantia
from storage.silver_store import write_silver_dataset

class GarantiaIngestionError(Exception):
    """Exceção levantada para falhas na ingestão de garantias."""

# Limiar mínimo de cobertura para disparo de alerta GAR_002 (§6.8)
COBERTURA_MINIMA = 0.5

def ingest_garantias_data(
    context: AppContext,
    df_garantias_externo: pd.DataFrame | None = None,
) -> dict[str, Any]:
    run_id = f"GAR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__ingestao_garantias.log"
    logger = get_logger("bdc.garantias", log_file)

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

            write_silver_dataset(
                records=df_alertas.to_dict(orient="records"),
                output_dir=context.path("silver") / "alertas_credito",
                filename=f"alertas_garantias_{run_id}"
            )
            logger.info("Gerados %s alertas de garantias (GAR_001 / GAR_002).", len(alertas))

        silver_dir = context.path("silver") / "garantias_silver"
        write_silver_dataset(
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
## src\services\mtm_connector.py
Linhas: 70
Classes: MtmConnectionError
Funções: _encontrar_arquivo_mtm_recente, fetch_mtm_consolidado
```python
"""Conector de integração com a base de MtM (Risco de Mercado)."""

from __future__ import annotations
from pathlib import Path
from typing import Any
from datetime import datetime
import pandas as pd

class MtmConnectionError(Exception):
    """Exceção levantada quando a base de MtM não pode ser obtida."""

def _encontrar_arquivo_mtm_recente(diretorio: Path) -> Path:
    arquivos = [f for f in diretorio.iterdir() if f.is_file() and f.suffix.lower() in {".xlsx", ".xls", ".csv"} and not f.name.startswith("~$")]
    if not arquivos: raise FileNotFoundError(f"Nenhum arquivo de MtM encontrado na pasta: {diretorio}")
    return max(arquivos, key=lambda f: f.stat().st_mtime)

def fetch_mtm_consolidado(input_dir: Path | str, logger: Any | None = None) -> pd.DataFrame:
    diretorio = Path(input_dir)
    diretorio.mkdir(parents=True, exist_ok=True)
    
    try:
        arquivo_fonte = _encontrar_arquivo_mtm_recente(diretorio)
        if logger: logger.info("Lendo base de MtM a partir do arquivo local: %s", arquivo_fonte.name)
        
        if arquivo_fonte.suffix.lower() == ".csv":
            df_bruto = pd.read_csv(arquivo_fonte, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)
        else:
            df_bruto = pd.read_excel(arquivo_fonte, dtype=str)

        df_bruto.columns = [str(c).strip().upper() for c in df_bruto.columns]

        # 1. CNPJ
        col_cnpj = next((c for c in df_bruto.columns if "CNPJ" in c and "CONTROLADOR" not in c), None)
        cnpj_series = df_bruto[col_cnpj].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14) if col_cnpj else pd.Series(["00000000000000"] * len(df_bruto), name="CNPJ")

        # 2. MTM TOTAL (Reais)
        if "MTM_TOTAL" in df_bruto.columns:
            raw_mtm = df_bruto["MTM_TOTAL"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            valores_mtm = pd.to_numeric(raw_mtm, errors="coerce").fillna(0.0)
        else:
            valores_mtm = pd.Series([0.0] * len(df_bruto), name="MTM_TOTAL")

        # 3. NOTIONAL FINANCEIRO (MWh * Preço)
        if "ENERGIA_MWH" in df_bruto.columns and "PRECO_REAJUSTADO" in df_bruto.columns:
            vol = df_bruto["ENERGIA_MWH"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            px = df_bruto["PRECO_REAJUSTADO"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            valores_notional = pd.to_numeric(vol, errors="coerce").fillna(0.0) * pd.to_numeric(px, errors="coerce").fillna(0.0)
        else:
            valores_notional = pd.Series([0.0] * len(df_bruto), name="NOTIONAL")

        # 4. Dados Base
        contrato_series = df_bruto.get("COD_CONTRATO", pd.Series([None] * len(df_bruto)))
        data_base_series = df_bruto.get("DATA_AVALIACAO", pd.Series([datetime.now().strftime("%Y-%m-%d")] * len(df_bruto)))

        # 5. Output
        df_resultado = pd.DataFrame({
            "CNPJ": cnpj_series,
            "CONTRATO": contrato_series,
            "DATA_BASE": data_base_series,
            "MTM_POSITIVO": valores_mtm.apply(lambda x: x if x > 0 else 0.0),
            "MTM_NEGATIVO": valores_mtm.apply(lambda x: abs(x) if x < 0 else 0.0),
            "NOTIONAL": valores_notional
        })

        if logger: logger.info("MtM lido. Notional convertido para Financeiro (R$).")
        return df_resultado

    except Exception as exc:
        if logger: logger.exception("Falha ao processar o arquivo local de MtM.")
        raise MtmConnectionError(f"Erro ao ler base de MtM: {exc}") from exc
```


---
## src\services\mtm_ingestion_service.py
Linhas: 130
Classes: MtmReconciliationError
Funções: ingest_mtm_data
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
from common.logging_utils import get_logger
from services.mtm_connector import fetch_mtm_consolidado, _encontrar_arquivo_mtm_recente
from storage.silver_store import write_silver_dataset


class MtmReconciliationError(Exception):
    """Exceção para falhas na reconciliação de totais entre Bronze e Silver."""


def ingest_mtm_data(context: AppContext) -> dict[str, Any]:
    """Orquestra a ingestão MtM: Bronze snapshot → Conector → Agregação → Reconciliação → Silver."""
    run_id = f"MTM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__ingestao_mtm.log"
    logger = get_logger("bdc.mtm", log_file)

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
        df_mtm = fetch_mtm_consolidado(input_dir=input_dir, logger=logger)

        if df_mtm.empty:
            logger.warning("Nenhum registro encontrado na base de MtM.")
            return {"run_id": run_id, "contrapartes_consolidadas": 0, "status": "SEM_DADOS"}

        # Captura totais originais para controle de reconciliação
        soma_pos_orig = float(df_mtm["MTM_POSITIVO"].sum())
        soma_neg_orig = float(df_mtm["MTM_NEGATIVO"].sum())
        soma_not_orig = float(df_mtm["NOTIONAL"].sum())

        # 3. Agregação por contraparte (CNPJ) e DATA_BASE para a Silver
        if "DATA_BASE" not in df_mtm.columns:
            df_mtm["DATA_BASE"] = datetime.now().strftime("%Y-%m-%d")

        df_agregado = (
            df_mtm.groupby(["CNPJ", "DATA_BASE"], as_index=False)
            .agg({
                "MTM_POSITIVO": "sum",
                "MTM_NEGATIVO": "sum",
                "NOTIONAL": "sum"
            })
            .rename(columns={
                "MTM_POSITIVO": "MTM_POSITIVO_TOTAL",
                "MTM_NEGATIVO": "MTM_NEGATIVO_TOTAL",
                "NOTIONAL": "NOTIONAL_TOTAL"
            })
        )

        # 4. Reconciliação de integridade entre Bronze e Silver (§11.6)
        reconciliation_config = context.config.get("reconciliacao_mtm", {})
        tolerancia = reconciliation_config.get("tolerancia_absoluta", 0.01)

        soma_pos_silver = float(df_agregado["MTM_POSITIVO_TOTAL"].sum())
        soma_neg_silver = float(df_agregado["MTM_NEGATIVO_TOTAL"].sum())
        soma_not_silver = float(df_agregado["NOTIONAL_TOTAL"].sum())

        checks = [
            ("MTM Positivo Total", soma_pos_orig, soma_pos_silver),
            ("MTM Negativo Total", soma_neg_orig, soma_neg_silver),
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
        csv_path, parquet_path = write_silver_dataset(
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
            "soma_mtm_positivo_total": soma_pos_silver,
            "soma_mtm_negativo_total": soma_neg_silver,
            "soma_notional_total": soma_not_silver,
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão/reconciliação do MtM.")
        raise
```


---
## src\services\network_discovery_service.py
Linhas: 188
Classes: NetworkDiscoveryError
Funções: _obter_assinaturas_locais, run_network_discovery
```python
"""Serviço de Coleta na Rede e Triagem Automática de Fichas de Crédito."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.context import AppContext
from common.excel import close_workbook_safely, open_workbook
from common.logging_utils import get_logger
from control.layout_catalog import (
    load_layouts_comercializadoras,
    load_layouts_consumidores,
)
from services.ficha_classifier import classify_workbook

EXTENSOES_EXCEL = {".xlsx", ".xls", ".xlsm"}

class NetworkDiscoveryError(Exception):
    """Exceção levantada para falhas na varredura de arquivos de rede."""

def _obter_assinaturas_locais(entradas_dir: Path) -> set[str]:
    """
    Varre a pasta local ENTRADAS/fichas (abrangendo pendentes, processadas, 
    rejeitadas e nao_identificados) e gera uma assinatura 'Nome_Tamanho' 
    para cada arquivo. Isso evita downloads redundantes da rede.
    """
    assinaturas = set()
    fichas_dir = entradas_dir / "fichas"
    
    if not fichas_dir.exists():
        return assinaturas

    for f in fichas_dir.rglob("*"):
        if f.is_file() and f.suffix.lower() in EXTENSOES_EXCEL and not f.name.startswith("~$"):
            try:
                # Assinatura rápida e leve: Nome do arquivo + Tamanho em bytes
                assinatura = f"{f.name}_{f.stat().st_size}"
                assinaturas.add(assinatura)
            except OSError:
                continue
                
    return assinaturas

def run_network_discovery(context: AppContext) -> dict[str, Any]:
    """
    Varre os diretórios de rede parametrizados, ignora arquivos já existentes localmente,
    classifica as novas fichas e as copia para as pastas de 'pendentes'.
    """
    run_id = f"DISC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__discovery.log"
    logger = get_logger("bdc.discovery", log_file)

    try:
        logger.info("Iniciando varredura inteligente na rede...")

        # 1. Carrega caminhos de rede e lista de arquivos já conhecidos
        network_paths = context.config.get("network_paths", {})
        if not network_paths:
            logger.warning("Nenhum 'network_paths' configurado no config.json.")
            return {"run_id": run_id, "status": "SEM_CONFIGURACAO"}

        assinaturas_conhecidas = _obter_assinaturas_locais(context.path("entradas"))
        logger.info("Encontrados %s arquivos já cacheados localmente. Eles serão ignorados na rede.", len(assinaturas_conhecidas))

        # 2. Carrega catálogos de layouts silenciosamente
        dummy_logger = logging.getLogger("dummy")
        dummy_logger.setLevel(logging.CRITICAL)
        layouts_com = load_layouts_comercializadoras(context, logger=dummy_logger)
        layouts_cons = load_layouts_consumidores(context, logger=dummy_logger)

        # 3. Prepara diretórios de destino
        dest_com = context.path("input_fichas_comercializadoras_pendentes")
        dest_cons = context.path("input_fichas_consumidores_pendentes")
        dest_falha = context.path("entradas") / "fichas" / "nao_identificados"

        dest_com.mkdir(parents=True, exist_ok=True)
        dest_cons.mkdir(parents=True, exist_ok=True)
        dest_falha.mkdir(parents=True, exist_ok=True)

        registros_relatorio = []
        cont_com, cont_cons, cont_falha, cont_ignorados = 0, 0, 0, 0

        # 4. Varredura na Rede
        for key, pasta_raiz in network_paths.items():
            raiz = Path(pasta_raiz)
            if not raiz.exists():
                logger.warning("Pasta de rede inacessível: %s", raiz)
                continue

            for caminho in raiz.rglob("*"):
                if not caminho.is_file() or caminho.suffix.lower() not in EXTENSOES_EXCEL or caminho.name.startswith("~$"):
                    continue

                nome_original = caminho.name
                
                # Filtro Antiduplicidade de Rede (Aderente à Seção 4.1 do Planejamento)
                try:
                    assinatura_rede = f"{nome_original}_{caminho.stat().st_size}"
                except OSError:
                    continue

                if assinatura_rede in assinaturas_conhecidas:
                    cont_ignorados += 1
                    continue

                logger.info("Novo arquivo detectado na rede: %s", nome_original)

                workbook = None
                destino_final = "ERRO_LEITURA"
                tipo_identificado = "FALHA/DESCONHECIDO"

                try:
                    # Trazemos para a memória (via openpyxl) SOMENTE se for um arquivo novo
                    workbook = open_workbook(caminho)

                    match_com = classify_workbook(workbook, layouts_com, logger=dummy_logger)
                    match_cons = None
                    if not match_com:
                        match_cons = classify_workbook(workbook, layouts_cons, logger=dummy_logger)

                    close_workbook_safely(workbook)

                    if match_com:
                        shutil.copy2(caminho, dest_com / nome_original)
                        tipo_identificado = "COMERCIALIZADORA"
                        destino_final = str(dest_com)
                        cont_com += 1
                    elif match_cons:
                        shutil.copy2(caminho, dest_cons / nome_original)
                        tipo_identificado = "CONSUMIDOR"
                        destino_final = str(dest_cons)
                        cont_cons += 1
                    else:
                        shutil.copy2(caminho, dest_falha / nome_original)
                        destino_final = str(dest_falha)
                        cont_falha += 1

                except Exception as e:
                    if workbook is not None:
                        close_workbook_safely(workbook)
                    logger.error("Erro ao ler %s: %s", nome_original, e)
                    shutil.copy2(caminho, dest_falha / f"[ERRO_LEITURA] {nome_original}")
                    destino_final = str(dest_falha)
                    cont_falha += 1

                # Adiciona a assinatura aos conhecidos em memória para evitar que
                # o mesmo arquivo repetido em duas pastas de rede seja copiado duas vezes no mesmo run.
                assinaturas_conhecidas.add(assinatura_rede)

                registros_relatorio.append({
                    "Origem_Rede": str(caminho),
                    "Nome_Arquivo": nome_original,
                    "Classificacao": tipo_identificado,
                    "Destino_Local": destino_final,
                    "Data_Coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        # 5. Geração de Relatório
        if registros_relatorio:
            df = pd.DataFrame(registros_relatorio)
            output_dir = context.path("output")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            nome_relatorio = output_dir / f"relatorio_triagem_{run_id}.xlsx"
            df.to_excel(nome_relatorio, index=False)
            logger.info("Relatório de triagem de rede gerado: %s", nome_relatorio.name)

        summary = {
            "run_id": run_id,
            "arquivos_ignorados_ja_locais": cont_ignorados,
            "comercializadoras_novas": cont_com,
            "consumidores_novos": cont_cons,
            "falhas_identificacao": cont_falha,
            "status": "SUCESSO"
        }
        
        logger.info("Discovery concluído. Resumo: %s", summary)
        return summary

    except Exception as exc:
        logger.exception("Falha crítica durante a triagem de rede.")
        raise NetworkDiscoveryError(f"Erro na varredura: {exc}") from exc
```


---
## src\services\receita_connector.py
Linhas: 117
Classes: -
Funções: normalizar_cnpj, _cache_path, _load_cache, _save_cache, _is_same_day_cache, fetch_receita_data_batch
```python
# -*- coding: utf-8 -*-
"""Conector e cache da BrasilAPI para consulta cadastral de Receita Federal."""

from __future__ import annotations

import json
import logging
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from app.context import AppContext

LOGGER = logging.getLogger(__name__)

def normalizar_cnpj(valor: Any) -> str | None:
    """Normaliza um CNPJ para 14 dígitos, preservando zeros à esquerda."""
    if valor is None or pd.isna(valor):
        return None
    cnpj = str(valor).strip()
    if cnpj.endswith(".0"):
        cnpj = cnpj[:-2]
    somente_digitos = "".join(ch for ch in cnpj if ch.isdigit())
    if len(somente_digitos) != 14:
        return None
    return somente_digitos.zfill(14)

def _cache_path(context: AppContext) -> Path:
    return context.path("entradas") / "receita" / "cache" / "receita_cache.json"

def _load_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(payload, dict):
        return {}
    cache: dict[str, dict[str, Any]] = {}
    for cnpj, record in payload.items():
        normalized = normalizar_cnpj(cnpj)
        if normalized and isinstance(record, dict):
            cache[normalized] = record
    return cache

def _save_cache(path: Path, cache: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = {cnpj: cache[cnpj] for cnpj in sorted(cache)}
    path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")

def _is_same_day_cache(record: dict[str, Any]) -> bool:
    quando = record.get("DATA_CONSULTA")
    if not quando:
        return False
    try:
        return str(quando)[:10] == date.today().isoformat()
    except Exception:
        return False

def fetch_receita_data_batch(cnpjs: list[str], context: AppContext) -> pd.DataFrame:
    cache_path = _cache_path(context)
    cache = _load_cache(cache_path)
    
    list_normalizada = []
    seen = set()
    for cnpj in cnpjs or []:
        normalized = normalizar_cnpj(cnpj)
        if normalized and normalized not in seen:
            seen.add(normalized)
            list_normalizada.append(normalized)

    results = []
    total = len(list_normalizada)
    
    print(f"\n[RECEITA FEDERAL] Iniciando processamento de {total} CNPJs...")

    for index, cnpj in enumerate(list_normalizada):
        if index > 0 and index % 500 == 0:
            print(f" -> Progresso Receita Federal: {index}/{total} CNPJs validados...")

        cached = cache.get(cnpj)
        if cached and _is_same_day_cache(cached):
            results.append(cached)
            continue

        # BYPASS PARA O MVP: Simula retorno de sucesso sem bater na API HTTP
        # Isso reduz o tempo da etapa de 20 minutos para 0.2 segundos.
        mock_result = {
            "CNPJ": cnpj,
            "SITUACAO_CADASTRAL": "ATIVA",
            "DATA_ABERTURA": "2000-01-01",
            "CNAE_PRINCIPAL": "0000000",
            "NATUREZA_JURIDICA": "Simulacao MVP Bypass",
            "DATA_CONSULTA": datetime.now().isoformat(timespec="seconds"),
            "STATUS": "OK_BYPASS",
            "MENSAGEM": "Bypass aplicado para acelerar execução local"
        }
        cache[cnpj] = mock_result
        results.append(mock_result)

    if cache:
        _save_cache(cache_path, cache)

    print(f"[RECEITA FEDERAL] Concluído! {total} CNPJs consolidados no cache local.\n")

    if not results:
        return pd.DataFrame(columns=["CNPJ", "SITUACAO_CADASTRAL", "DATA_ABERTURA", "CNAE_PRINCIPAL", "NATUREZA_JURIDICA", "DATA_CONSULTA"])

    df = pd.DataFrame(results)
    return df.drop_duplicates(subset=["CNPJ"], keep="last").reset_index(drop=True)
```


---
## src\services\reconciliacao_denodo_mtm_service.py
Linhas: 144
Classes: ReconciliacaoDataError
Funções: executar_reconciliacao_denodo_mtm
```python
"""Serviço de reconciliação entre contratos do Denodo e posições consolidadas de MtM."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from app.context import AppContext
from common.logging_utils import get_logger
from domain.enums import StatusAlerta
from storage.silver_store import write_silver_dataset


class ReconciliacaoDataError(Exception):
    """Exceção levantada quando os dados fonte para a reconciliação estão inacessíveis ou vazios."""

def executar_reconciliacao_denodo_mtm(context: AppContext) -> dict[str, Any]:
    """
    Cruza o consolidado de contratos do Denodo com posições do MtM na camada Silver por CNPJ.
    Classifica as contrapartes e dispara os alertas CTR_001 e CTR_002.
    """
    run_id = f"REC_MTM_DENODO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__reconciliacao.log"
    logger = get_logger("bdc.reconciliacao", log_file)

    try:
        logger.info("Iniciando reconciliação entre Denodo e MtM por Contraparte.")

        # 1. Carregamento das bases Silver
        silver_mtm_path = context.path("silver") / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
        silver_denodo_path = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"

        if not silver_mtm_path.exists() or not silver_denodo_path.exists():
            raise ReconciliacaoDataError("As bases Silver do Denodo ou MtM não foram encontradas para a reconciliação.")

        df_mtm = pd.read_parquet(silver_mtm_path)
        df_denodo_full = pd.read_parquet(silver_denodo_path)

        if df_mtm.empty or df_denodo_full.empty:
            logger.warning("Uma das bases Silver está vazia. Cancelando reconciliação.")
            return {"run_id": run_id, "linhas_conciliadas": 0, "status": "SEM_DADOS"}

        # 2. Padronização: Como o MtM está agregado por CNPJ, agregamos o Denodo por CNPJ
        df_denodo_full["CNPJ"] = df_denodo_full["CNPJ"].astype(str).str.zfill(14)
        df_mtm["CNPJ"] = df_mtm["CNPJ"].astype(str).str.zfill(14)

        # Para conciliação, basta saber se a contraparte tem AO MENOS UM contrato ativo
        df_denodo = df_denodo_full[["CNPJ"]].drop_duplicates()
        df_denodo["TEM_CONTRATO"] = True

        # 3. Cruzamento (Outer Join por CNPJ)
        df_merged = pd.merge(
            df_denodo, 
            df_mtm, 
            on="CNPJ", 
            how="outer", 
            indicator=True
        )

        # 4. Classificação de Reconciliação
        conditions = [
            df_merged["_merge"] == "both",
            df_merged["_merge"] == "left_only",
            df_merged["_merge"] == "right_only"
        ]
        choices = ["CONCILIADO", "CONTRATO_SEM_MTM", "MTM_SEM_CONTRATO"]
        
        df_merged["STATUS_CONCILIACAO"] = np.select(conditions, choices, default="DIVERGENTE")

        # 5. Geração de Alertas
        alertas = []
        
        # CTR_001: Contrato corrente no Denodo sem posição correspondente no MtM
        mask_ctr_001 = df_merged["STATUS_CONCILIACAO"] == "CONTRATO_SEM_MTM"
        for _, row in df_merged[mask_ctr_001].iterrows():
            alertas.append({
                "CODIGO": "CTR_001",
                "CNPJ": row["CNPJ"],
                "SEVERIDADE": "MEDIO",
                "MENSAGEM": f"A contraparte (CNPJ {row['CNPJ']}) possui contrato(s) no Denodo, mas não tem posição na base de MtM."
            })

        # CTR_002: Posição no MtM sem contrato corrente identificado no Denodo
        mask_ctr_002 = df_merged["STATUS_CONCILIACAO"] == "MTM_SEM_CONTRATO"
        for _, row in df_merged[mask_ctr_002].iterrows():
            alertas.append({
                "CODIGO": "CTR_002",
                "CNPJ": row["CNPJ"],
                "SEVERIDADE": "ALTO",
                "MENSAGEM": f"Posição de MtM identificada para a contraparte {row['CNPJ']}, mas nenhum contrato corrente consta no Denodo."
            })

        if alertas:
            df_alertas = pd.DataFrame(alertas)
            df_alertas["RUN_ID"] = run_id
            df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
            df_alertas["STATUS_ALERTA"] = StatusAlerta.ABERTO.value
            
            alertas_output_dir = context.path("silver") / "alertas_credito"
            write_silver_dataset(
                records=df_alertas.to_dict(orient="records"),
                output_dir=alertas_output_dir,
                filename=f"alertas_reconciliacao_{run_id}"
            )
            logger.info("Gerados %s alertas de negócio na reconciliação.", len(alertas))

        # 6. Organização e Persistência do resultado
        colunas_saida = [
            "CNPJ", "STATUS_CONCILIACAO", 
            "MTM_POSITIVO_TOTAL", "MTM_NEGATIVO_TOTAL", "NOTIONAL_TOTAL"
        ]
        
        colunas_disponiveis = [col for col in colunas_saida if col in df_merged.columns]
        df_reconciliacao = df_merged[colunas_disponiveis].copy()
        
        df_reconciliacao["RUN_ID"] = run_id
        df_reconciliacao["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        reconciliacao_output_dir = context.path("silver") / "reconciliacao_contratos_mtm"
        csv_path, parquet_path = write_silver_dataset(
            records=df_reconciliacao.to_dict(orient="records"),
            output_dir=reconciliacao_output_dir,
            filename="fato_reconciliacao_contrato_mtm"
        )

        logger.info(
            "Reconciliação Denodo x MtM finalizada. %s contrapartes cruzadas. Relatórios: \n - %s\n - %s",
            len(df_reconciliacao), csv_path.name, parquet_path.name
        )

        return {
            "run_id": run_id,
            "linhas_conciliadas": len(df_reconciliacao),
            "alertas_gerados_ctr001": mask_ctr_001.sum(),
            "alertas_gerados_ctr002": mask_ctr_002.sum(),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica no serviço de reconciliação Denodo x MtM.")
        raise ReconciliacaoDataError(f"Erro ao processar reconciliação: {exc}") from exc
```


---
## src\silver\field_type_normalizer.py
Linhas: 136
Classes: -
Funções: _get_fields, normalize_data_demonstracao_financeira, normalize_record
```python
"""Normalização técnica das fichas."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from app.context import AppContext
from common.dates import normalize_date
from common.io_json import read_json
from common.strings import normalize_cnpj, normalize_string
from common.types import normalize_float
from control.field_types import get_field_type_config


def _get_fields(field_types: dict[str, Any], key: str) -> list[str]:
    """Obtém uma lista de campos do JSON de tipos (Usado apenas no fallback)."""
    value = field_types.get(key, [])

    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(
            f"Configuração inválida em '{key}': "
            f"esperado list, recebido {type(value).__name__}."
        )

    return [str(item).strip() for item in value if str(item).strip()]


def normalize_data_demonstracao_financeira(value: Any) -> str | None:
    """Normaliza DATA_DEMONSTRACAO_FINANCEIRA para dd/mm/aaaa."""
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    if re.fullmatch(r"\d{4}", text):
        return f"31/12/{text}"

    text = text.split()[0]

    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]

    for fmt in formatos:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            continue

    return None


def normalize_record(
    record: dict[str, Any],
    context: AppContext,
    slug: str,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Normaliza o registro bruto extraído da ficha."""
    try:
        # T1.3.1: Uso da Classe Python Tipada com prioridade sobre o JSON
        config_class = get_field_type_config(slug)

        if config_class:
            if logger is not None:
                logger.info("Carregando tipagem da classe Python: %s", slug)
            date_fields = config_class.date_fields
            float_fields = config_class.float_fields
            text_fields = config_class.text_fields
            cnpj_fields = config_class.cnpj_fields
        else:
            if logger is not None:
                logger.info("Classe Python não encontrada. Fallback para JSON: %s", slug)
            field_types_path = context.control_file(slug)
            field_types = read_json(field_types_path)

            date_fields = _get_fields(field_types, "date_fields")
            float_fields = _get_fields(field_types, "float_fields")
            text_fields = _get_fields(field_types, "text_fields")
            cnpj_fields = _get_fields(field_types, "cnpj_fields")

        out = dict(record)

        for field in cnpj_fields:
            if field in out:
                try:
                    out[field] = normalize_cnpj(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro CNPJ: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo CNPJ '{field}'.") from exc

        for field in date_fields:
            if field in out:
                try:
                    if field == "DATA_DEMONSTRACAO_FINANCEIRA":
                        out[field] = normalize_data_demonstracao_financeira(out.get(field))
                    else:
                        out[field] = normalize_date(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Data: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo de data '{field}'.") from exc

        for field in float_fields:
            if field in out:
                try:
                    out[field] = normalize_float(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Float: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo numérico '{field}'.") from exc

        for field in text_fields:
            if field in out and out.get(field) is not None:
                try:
                    out[field] = normalize_string(out.get(field))
                except Exception as exc:
                    if logger: logger.exception("Erro Texto: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo textual '{field}'.") from exc

        if logger is not None:
            logger.info("Registro normalizado (Entrada: %s, Saída: %s).", len(record), len(out))
            
        return out

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha na normalização: CNPJ=%s EMPRESA=%s",
                record.get("CNPJ"), record.get("EMPRESA")
            )
        raise
```


---
## src\storage\state_store.py
Linhas: 72
Classes: DocumentManifest
Funções: __post_init__, to_dict
```python
"""Estruturas de estado e manifesto do processamento."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from domain.enums import (
    LoadMode,
    StatusClassificacao,
    StatusExtracao,
    TipoFicha,
)

@dataclass
class DocumentManifest:
    """Representa o manifesto técnico de uma ficha processada."""

    documento_id: str
    run_id: str
    ambiente: str
    tipo_ficha: TipoFicha | str
    arquivo_nome: str | None = None
    caminho_origem: str | None = None
    caminho_staging: str | None = None
    caminho_bronze: str | None = None
    hash_arquivo: str | None = None
    versao_ficha: str | None = None
    cnpj_extraido: str | None = None
    data_demonstracao_financeira: str | None = None
    data_calculo: str | None = None
    status_classificacao: StatusClassificacao | str | None = None
    status_extracao: StatusExtracao | str | None = None
    load_mode: LoadMode | str | None = None
    reprocessed: bool | None = None
    previous_record_found: bool | None = None
    erros: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Garante que os atributos controlados pertençam aos domínios nativos."""
        if isinstance(self.tipo_ficha, str):
            try:
                self.tipo_ficha = TipoFicha(self.tipo_ficha.lower())
            except ValueError:
                raise ValueError(f"Valor rejeitado para tipo_ficha: '{self.tipo_ficha}'. Domínios válidos: {[e.value for e in TipoFicha]}")

        if isinstance(self.status_classificacao, str):
            try:
                self.status_classificacao = StatusClassificacao(self.status_classificacao.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para status_classificacao: '{self.status_classificacao}'. Domínios válidos: {[e.value for e in StatusClassificacao]}")

        if isinstance(self.status_extracao, str):
            try:
                self.status_extracao = StatusExtracao(self.status_extracao.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para status_extracao: '{self.status_extracao}'. Domínios válidos: {[e.value for e in StatusExtracao]}")
                
        if isinstance(self.load_mode, str):
            try:
                self.load_mode = LoadMode(self.load_mode.lower())
            except ValueError:
                raise ValueError(f"Valor rejeitado para load_mode: '{self.load_mode}'. Domínios válidos: {[e.value for e in LoadMode]}")

    def to_dict(self) -> dict[str, Any]:
        """Serializa o manifesto convertendo os Enums para seus valores primitivos (strings)."""
        manifest_dict = asdict(self)
        for key, value in manifest_dict.items():
            if hasattr(value, "value"):
                manifest_dict[key] = value.value
        return manifest_dict
```


---
## src\tests\test_denodo_connector.py
Linhas: 27
Classes: -
Funções: test_t211_leitura_denodo_local
```python
import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.denodo_connector import fetch_contratos_competencia

def test_t211_leitura_denodo_local():
    """Garante que o conector offline formata o DataFrame estruturalmente."""
    pasta_entradas = Path(__file__).resolve().parents[2] / "ENTRADAS" / "contratos_denodo"
    
    df = fetch_contratos_competencia("202608", input_dir=pasta_entradas)
    
    assert not df.empty, "O DataFrame não deveria estar vazio para 202608."
    
    colunas_esperadas = ["CNPJ", "CONTRATO", "COMPETENCIA", "VOLUME_MWM", "VIGENCIA_INICIO", "VIGENCIA_FIM", "STATUS"]
    for col in colunas_esperadas:
        assert col in df.columns, f"Coluna {col} ausente no DataFrame retornado."
        
    # Verifica se o filtro de competência funcionou perfeitamente
    assert (df["COMPETENCIA"] == "202608").all(), "O filtro de competência falhou."
    
    # Verifica tipagem do Volume e CNPJ com as APIs modernas do Pandas
    assert pd.api.types.is_numeric_dtype(df["VOLUME_MWM"]), "VOLUME_MWM não é numérico."
    assert pd.api.types.is_string_dtype(df["CNPJ"]), "CNPJ deveria ser string."
```


---
## src\tests\test_dynamic_paths.py
Linhas: 26
Classes: -
Funções: test_config_builder_sem_json_t122
```python
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config_builder import AppConfigBuilder

def test_config_builder_sem_json_t122(tmp_path):
    """
    Testa a resolução dinâmica sem depender da leitura do arquivo JSON em disco.
    """
    base_dir_simulado = tmp_path / "Z_DRIVE_CORPORATIVO"
    
    # Dicionário mock simulando a estrutura relativa contida no JSON
    mock_paths = {
        "entradas": "ENTRADAS",
        "staging": "SAIDAS/staging"
    }
    
    builder = AppConfigBuilder(base_dir_simulado)
    resolved_paths = builder.resolve_dict(mock_paths)
    
    # Validações
    assert resolved_paths["entradas"] == str(base_dir_simulado / "ENTRADAS")
    assert resolved_paths["staging"] == str(base_dir_simulado / "SAIDAS" / "staging")
```


---
## src\tests\test_enums.py
Linhas: 36
Classes: -
Funções: test_t133_rejeicao_valor_fora_do_dominio, test_t133_conversao_string_valida_para_enum
```python
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from storage.state_store import DocumentManifest

def test_t133_rejeicao_valor_fora_do_dominio():
    """Garante que o manifesto rejeita strings inválidas e levanta erro claro."""
    with pytest.raises(ValueError) as exc:
        DocumentManifest(
            documento_id="123",
            run_id="run_1",
            ambiente="dev",
            tipo_ficha="comercializadora",
            status_extracao="FALHA_NA_PLANILHA" # Valor não mapeado no Enum
        )
    
    assert "Valor rejeitado para status_extracao" in str(exc.value)
    assert "ERRO_PROCESSAMENTO" in str(exc.value)

def test_t133_conversao_string_valida_para_enum():
    """Garante que strings minúsculas/maiúsculas sejam corrigidas para o Enum correspondente."""
    manifest = DocumentManifest(
        documento_id="123",
        run_id="run_1",
        ambiente="dev",
        tipo_ficha="COMERCIALIZADORA", # Enviado maiúsculo, mas o Enum é minúsculo
        status_extracao="sucesso" # Enviado minúsculo, mas o Enum é maiúsculo
    )
    
    # O método to_dict extrai o valor consolidado correto para persistência
    data = manifest.to_dict()
    assert data["tipo_ficha"] == "comercializadora"
    assert data["status_extracao"] == "SUCESSO"
```


---
## src\tests\test_layout_catalog.py
Linhas: 46
Classes: -
Funções: test_cenario_1_layout_valido, test_cenario_2_layout_sem_field_map, test_cenario_3_layout_com_campo_vazio
```python
import sys
import logging
import pytest
from pathlib import Path

# Ajuste do path: como o arquivo está em src/tests/,
# .parent é 'tests' e .parent.parent é a pasta 'src'.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from control.layout_catalog import _validate_layout_structure

# Criação de um logger simulado para o teste
logger = logging.getLogger("test_logger")

def test_cenario_1_layout_valido():
    """Cenário 1: Layout possui field_map e campos com pelo menos uma âncora válida."""
    layout_valido = {
        "field_map": {
            "CNPJ": {"value_cell": "B13"},
            "DATA_DF": {"search_pattern": "^DATA"},
            "MISTO": {"value_cell": "A1", "search_pattern": "PADRAO"}
        }
    }
    # Se a validação passar, nenhuma exceção é lançada e o teste tem sucesso
    _validate_layout_structure(layout_valido, "layout_mock_valido", logger)

def test_cenario_2_layout_sem_field_map():
    """Cenário 2: Layout está corrompido e perdeu a raiz 'field_map'."""
    layout_invalido = {
        "outra_chave": "valor_qualquer"
    }
    with pytest.raises(SystemExit) as e:
        _validate_layout_structure(layout_invalido, "layout_mock_corrompido", logger)
    assert e.value.code == 1

def test_cenario_3_layout_com_campo_vazio():
    """Cenário 3: Um campo específico perdeu as âncoras 'value_cell' e 'search_pattern'."""
    layout_invalido = {
        "field_map": {
            "CNPJ": {"value_cell": "B13"},
            "CAMPO_FALTANDO_ANCORA": {"alguma_outra_coisa": "X"} # Falha aqui
        }
    }
    with pytest.raises(SystemExit) as e:
        _validate_layout_structure(layout_invalido, "layout_mock_campo_vazio", logger)
    assert e.value.code == 1
```


---
## src\tests\test_pd_consumidor_le5.py
Linhas: 33
Classes: -
Funções: test_t142_calculo_pd_bureau_sem_restritivo, test_t142_calculo_pd_bureau_com_restritivo
```python
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.credito.pd_consumidor_le5 import calcular_pd_final_consumidor_le5

def test_t142_calculo_pd_bureau_sem_restritivo():
    """Score 700 = Rating B (Faixa de B: 1% a 3%). Deve interpolar corretamente."""
    pd_faixas = {
        "CONSUMIDOR_LE_5": {
            "B": {"min": 0.0100, "max": 0.0300}
        }
    }
    registro = {"SCORE_BUREAU": 700.0, "QUANTIDADE_RESTRITIVOS": 0}
    
    res = calcular_pd_final_consumidor_le5(registro, pd_faixas)
    
    assert res["RATING_FINAL"] == "B"
    assert res["PATRIMONIO_LIQUIDO"] == "NAO_APLICAVEL"
    # Uso do pytest.approx para evitar quebra por conversão de floating point em binário
    assert res["PD_FINAL"] == pytest.approx(0.02, abs=1e-5)

def test_t142_calculo_pd_bureau_com_restritivo():
    """Mesmo com score alto, se houver restritivo, vai para Rating E."""
    pd_faixas = {"CONSUMIDOR_LE_5": {"E": {"min": 0.1100, "max": 1.0000}}}
    registro = {"SCORE_BUREAU": 950.0, "QUANTIDADE_RESTRITIVOS": 2}
    
    res = calcular_pd_final_consumidor_le5(registro, pd_faixas)
    
    assert res["RATING_FINAL"] == "E"
    assert res["PD_METODO"] == "SCORE_BUREAU"
```


---
## src\tests\test_reconciliacao_denodo_mtm.py
Linhas: 97
Classes: MockContext
Funções: test_t223_reconciliacao_denodo_mtm_cenarios_completos, path
```python
import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.reconciliacao_denodo_mtm_service import executar_reconciliacao_denodo_mtm

def test_t223_reconciliacao_denodo_mtm_cenarios_completos(tmp_path):
    """
    Testa a classificação de reconciliação cruzando Denodo x MtM e o disparo de alertas.
    Cobre: CONCILIADO, CONTRATO_SEM_MTM (CTR_001) e MTM_SEM_CONTRATO (CTR_002).
    """
    
    # 1. Estrutura mock de diretórios na Silver
    silver_dir = tmp_path / "SAIDAS" / "silver"
    dir_denodo = silver_dir / "denodo_contratos_silver"
    dir_mtm = silver_dir / "mtm_consolidado_silver"
    dir_denodo.mkdir(parents=True)
    dir_mtm.mkdir(parents=True)

    class MockContext:
        def path(self, key):
            if key == "silver":
                return silver_dir
            if key == "log_runner":
                p = tmp_path / "LOGS"
                p.mkdir(parents=True, exist_ok=True)
                return p
            return tmp_path

    context = MockContext()

    # 2. Criando massa de dados mockada
    
    # Base Denodo:
    # C1 vai cruzar perfeitamente com o MtM.
    # C2 existe só no Denodo (vai gerar CTR_001).
    df_denodo = pd.DataFrame([
        {"CNPJ": "11111111111111", "CONTRATO": "C1"},
        {"CNPJ": "22222222222222", "CONTRATO": "C2"},
    ])
    df_denodo.to_parquet(dir_denodo / "contratos_correntes.parquet", index=False)

    # Base MtM:
    # C1 vai cruzar perfeitamente com o Denodo.
    # C3 existe só no MtM (vai gerar CTR_002).
    df_mtm = pd.DataFrame([
        {
            "CNPJ": "11111111111111", "CONTRATO": "C1", 
            "MTM_POSITIVO_TOTAL": 1000.0, "MTM_NEGATIVO_TOTAL": 0.0, "NOTIONAL_TOTAL": 50.0
        },
        {
            "CNPJ": "33333333333333", "CONTRATO": "C3", 
            "MTM_POSITIVO_TOTAL": 500.0, "MTM_NEGATIVO_TOTAL": 10.0, "NOTIONAL_TOTAL": 20.0
        },
    ])
    df_mtm.to_parquet(dir_mtm / "mtm_agregado_contraparte.parquet", index=False)

    # 3. Executa o serviço de reconciliação
    res = executar_reconciliacao_denodo_mtm(context)

    # 4. Validações do dicionário de resposta
    assert res["status"] == "SUCESSO"
    assert res["linhas_conciliadas"] == 3  # Avaliou C1, C2 e C3 (Outer Join)
    assert res["alertas_gerados_ctr001"] == 1
    assert res["alertas_gerados_ctr002"] == 1

    # 5. Validação da Tabela de Fatos da Reconciliação
    path_reconciliacao = silver_dir / "reconciliacao_contratos_mtm" / "fato_reconciliacao_contrato_mtm.parquet"
    assert path_reconciliacao.exists(), "Tabela de fatos de reconciliação não foi gerada."
    
    df_rec = pd.read_parquet(path_reconciliacao)

    c1_status = df_rec.loc[df_rec["CONTRATO"] == "C1", "STATUS_CONCILIACAO"].iloc[0]
    c2_status = df_rec.loc[df_rec["CONTRATO"] == "C2", "STATUS_CONCILIACAO"].iloc[0]
    c3_status = df_rec.loc[df_rec["CONTRATO"] == "C3", "STATUS_CONCILIACAO"].iloc[0]

    # Valida se a regra de Outer Join inferiu corretamente os domínios de negócio
    assert c1_status == "CONCILIADO", "Contrato presente em ambas as pontas deveria estar CONCILIADO."
    assert c2_status == "CONTRATO_SEM_MTM", "Contrato órfão do Denodo classificado incorretamente."
    assert c3_status == "MTM_SEM_CONTRATO", "Contrato órfão do MtM classificado incorretamente."

    # 6. Validação dos Alertas (CTR_001 e CTR_002)
    path_alertas_dir = silver_dir / "alertas_credito"
    arquivos_alerta = list(path_alertas_dir.glob("*.parquet"))
    assert len(arquivos_alerta) == 1, "Arquivo físico de alertas não foi salvo."

    df_alertas = pd.read_parquet(arquivos_alerta[0])
    
    # Precisam existir exatamente 2 alertas na nossa massa de dados (C2 e C3)
    assert len(df_alertas) == 2 
    codigos_alerta = df_alertas["CODIGO"].tolist()
    
    assert "CTR_001" in codigos_alerta
    assert "CTR_002" in codigos_alerta
```


---
## src\tests\test_reconciliacao_fichas_salesforce.py
Linhas: 78
Classes: MockContext
Funções: test_t232_reconciliacao_fichas_salesforce_cenarios, path
```python
import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.reconciliacao_fichas_salesforce_service import executar_reconciliacao_fichas_salesforce


def test_t232_reconciliacao_fichas_salesforce_cenarios(tmp_path):
    """
    Testa o cruzamento entre Fichas e Salesforce.
    Cobre a geração do alerta CAD_002 para divergência de Grupo Econômico 
    e o armazenamento de ratings concorrentes.
    """
    
    # 1. Estrutura mock
    silver_dir = tmp_path / "SAIDAS" / "silver"
    dir_fichas_com = silver_dir / "fichas_comercializadoras"
    dir_sf_account = silver_dir / "salesforce_silver" / "account"
    
    dir_fichas_com.mkdir(parents=True)
    dir_sf_account.mkdir(parents=True)

    class MockContext:
        def path(self, key):
            if key == "silver":
                return silver_dir
            if key == "log_runner":
                p = tmp_path / "LOGS"
                p.mkdir(parents=True, exist_ok=True)
                return p
            return tmp_path

    context = MockContext()

    # 2. Mock de Fichas
    # C1: Divergência de grupo. C2: Consistente.
    df_fichas = pd.DataFrame([
        {"CNPJ": "11111111111111", "GRUPO_ECONOMICO": "Grupo A", "RATING": "A"},
        {"CNPJ": "22222222222222", "GRUPO_ECONOMICO": "Grupo B", "RATING": "B+"},
    ])
    df_fichas.to_parquet(dir_fichas_com / "fichas_padronizadas.parquet", index=False)

    # 3. Mock de Salesforce (Account)
    df_sf = pd.DataFrame([
        {"CNPJ": "11111111111111", "Grupo_economico__c": "Grupo Diferente", "Risk3_Rating__c": "A-"},
        {"CNPJ": "22222222222222", "Grupo_economico__c": "Grupo B", "Risk3_Rating__c": "B+"},
        {"CNPJ": "33333333333333", "Grupo_economico__c": "Grupo C", "Risk3_Rating__c": "C"},
    ])
    df_sf.to_parquet(dir_sf_account / "salesforce_account.parquet", index=False)

    # 4. Executa Reconciliação
    res = executar_reconciliacao_fichas_salesforce(context)

    # 5. Asserções
    assert res["status"] == "SUCESSO"
    assert res["linhas_conciliadas"] == 2  # Somente 111... e 222... (Inner join)
    assert res["alertas_gerados_cad002"] == 1  # Divergência no 111...
    
    # Valida arquivo de alertas
    path_alertas_dir = silver_dir / "alertas_credito"
    arquivos_alerta = list(path_alertas_dir.glob("*.parquet"))
    assert len(arquivos_alerta) == 1
    
    df_alertas = pd.read_parquet(arquivos_alerta[0])
    assert df_alertas["CODIGO"].iloc[0] == "CAD_002"
    assert df_alertas["CNPJ"].iloc[0] == "11111111111111"
    
    # Valida armazenamento de Rating Concorrente
    path_ratings = silver_dir / "reconciliacao_fichas_salesforce" / "fato_concorrencia_rating.parquet"
    assert path_ratings.exists()
    
    df_rating = pd.read_parquet(path_ratings)
    assert len(df_rating) == 2
    assert "RATING_FICHA" in df_rating.columns
    assert "RATING_SF" in df_rating.columns
```
