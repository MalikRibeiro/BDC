# CÓDIGO PARTE 1


---
## gerar_contexto_ia.py
Linhas: 146
Classes: -
Funções: tree, analyze
```python

from pathlib import Path
import shutil
import ast
from textwrap import dedent


ROOT = Path(".").resolve()
OUT = ROOT / "AI_CONTEXT"

IGNORE = {
    ".git",".venv","venv","__pycache__",".idea",".vscode",
    "node_modules","dist","build",".pytest_cache",".mypy_cache","AI_CONTEXT"
}

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

py_files=[]
json_files=[]

for p in ROOT.rglob("*"):
    if any(x in p.parts for x in IGNORE):
        continue
    if p.is_file():
        if p.suffix.lower()==".py":
            py_files.append(p)
        elif p.suffix.lower()==".json":
            json_files.append(p)

py_files.sort()
json_files.sort()

def tree(folder,prefix=""):
    lines=[]
    items=[i for i in sorted(folder.iterdir(), key=lambda x:(x.is_file(),x.name.lower()))
           if i.name not in IGNORE]
    for idx,item in enumerate(items):
        last=idx==len(items)-1
        c="└── " if last else "├── "
        lines.append(prefix+c+item.name)
        if item.is_dir():
            lines.extend(tree(item,prefix+("    " if last else "│   ")))
    return lines

def analyze(path):
    try:
        txt=path.read_text(encoding="utf-8")
    except:
        return {"lines":0,"imports":[],"classes":[],"functions":[],"doc":""}
    info={"lines":len(txt.splitlines()),"imports":[],"classes":[],"functions":[],"doc":""}
    try:
        t=ast.parse(txt)
        info["doc"]=ast.get_docstring(t) or ""
        for n in ast.walk(t):
            if isinstance(n,ast.Import):
                info["imports"] += [a.name for a in n.names]
            elif isinstance(n,ast.ImportFrom):
                info["imports"].append(n.module or "")
            elif isinstance(n,ast.ClassDef):
                info["classes"].append(n.name)
            elif isinstance(n,ast.FunctionDef):
                info["functions"].append(n.name)
    except:
        pass
    return info

(OUT/"00_README.md").write_text(dedent("""\
# AI_CONTEXT

Arquivos gerados automaticamente para análise por IA.

Ordem sugerida:
1. Planejamento.pdf
2. 01_CONTEXTO.md
3. 02_ESTRUTURA.md
4. 03_CONFIGURACOES.md
5. 04_RESUMO_TECNICO.md
6. 05_CODIGO_PARTE_1.md
7. 06_CODIGO_PARTE_2.md
8. 07_CODIGO_PARTE_3.md
"""),encoding="utf-8")

with open(OUT/"01_CONTEXTO.md","w",encoding="utf-8") as f:
    f.write("# CONTEXTO\n\n")
    f.write(f"Python: {len(py_files)}\n\nJSON: {len(json_files)}\n\n")

with open(OUT/"02_ESTRUTURA.md","w",encoding="utf-8") as f:
    f.write("# ESTRUTURA\n\n")
    f.write(ROOT.name+"\n")
    f.write("\n".join(tree(ROOT)))

with open(OUT/"03_CONFIGURACOES.md","w",encoding="utf-8") as f:
    f.write("# CONFIGURAÇÕES\n")
    for j in json_files:
        f.write(f"\n\n---\n# {j.relative_to(ROOT)}\n```json\n")
        try:
            f.write(j.read_text(encoding="utf-8"))
        except:
            f.write("[Erro ao ler]")
        f.write("\n```\n")

with open(OUT/"04_RESUMO_TECNICO.md","w",encoding="utf-8") as f:
    f.write("# RESUMO TÉCNICO\n")
    for p in py_files:
        i=analyze(p)
        f.write(f"\n\n## {p.relative_to(ROOT)}\n")
        f.write(f"Linhas: {i['lines']}\n\n")
        f.write("Imports:\n")
        for x in sorted(set(i["imports"])):
            f.write(f"- {x}\n")
        f.write("\nClasses:\n")
        for x in i["classes"]:
            f.write(f"- {x}\n")
        f.write("\nFunções:\n")
        for x in i["functions"]:
            f.write(f"- {x}\n")
        if i["doc"]:
            f.write("\nDocstring:\n"+i["doc"]+"\n")

parts=[[],[],[]]
sizes=[0,0,0]
for p in py_files:
    s=p.stat().st_size
    idx=sizes.index(min(sizes))
    parts[idx].append(p)
    sizes[idx]+=s

for n,plist in enumerate(parts,5):
    with open(OUT/f"{n:02d}_CODIGO_PARTE_{n-4}.md","w",encoding="utf-8") as f:
        f.write(f"# CÓDIGO PARTE {n-4}\n")
        for p in plist:
            info=analyze(p)
            f.write(f"\n\n---\n## {p.relative_to(ROOT)}\n")
            f.write(f"Linhas: {info['lines']}\n")
            f.write(f"Classes: {', '.join(info['classes']) or '-'}\n")
            f.write(f"Funções: {', '.join(info['functions']) or '-'}\n")
            f.write("```python\n")
            try:
                f.write(p.read_text(encoding="utf-8"))
            except:
                f.write("[Erro ao ler]")
            f.write("\n```\n")

print("Concluído.")

```


---
## src\app\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Pacote de bootstrap e contexto da aplicação BDC."""

```


---
## src\app\bootstrap.py
Linhas: 60
Classes: -
Funções: resolve_configs_dir, bootstrap_application
```python
import os
from pathlib import Path
from typing import Optional, Union

from src.app.context import AppContext, load_context
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do arquivo .env para o os.environ automaticamente

CONFIGS_DIR_ENV_VAR = "BDC_CONFIGS_DIR"


def resolve_configs_dir(explicit_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Resolve o diretório de configurações utilizando a seguinte hierarquia:
    1. Caminho explícito fornecido (ex.: via flag CLI --configs-dir).
    2. Variável de ambiente `BDC_CONFIGS_DIR`.
    3. Diretório relativo à raiz do projeto (`<project_root>/ENTRADAS/configs`).

    Args:
        explicit_path: Caminho explícito opcional (string ou Path).

    Returns:
        Path: Objeto Path do diretório de configurações validado.

    Raises:
        FileNotFoundError: Caso o diretório de configurações não exista.
    """
    if explicit_path:
        configs_dir = Path(explicit_path).resolve()
    elif os.environ.get(CONFIGS_DIR_ENV_VAR):
        configs_dir = Path(os.environ[CONFIGS_DIR_ENV_VAR]).resolve()
    else:
        # Calcula a raiz do projeto (src/app/bootstrap.py -> src/app -> src -> project_root)
        project_root = Path(__file__).resolve().parents[2]
        configs_dir = project_root / "ENTRADAS" / "configs"

    if not configs_dir.exists() or not configs_dir.is_dir():
        raise FileNotFoundError(
            f"Diretório de configurações não encontrado em: '{configs_dir}'.\n"
            f"Por favor, verifique se o caminho existe ou especifique o caminho correto via:\n"
            f"  - Flag CLI: --configs-dir /caminho/para/configs\n"
            f"  - Variável de ambiente: export {CONFIGS_DIR_ENV_VAR}=/caminho/para/configs"
        )

    return configs_dir


def bootstrap_application(configs_dir: Optional[Union[str, Path]] = None) -> AppContext:
    """
    Realiza o bootstrap da aplicação e carrega o AppContext.

    Args:
        configs_dir: Caminho explícito ou opcional para o diretório de configurações.

    Returns:
        AppContext: Contexto inicializado da aplicação.
    """
    resolved_dir = resolve_configs_dir(configs_dir)
    return load_context(resolved_dir)
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
## src\cli\run_discovery.py
Linhas: 57
Classes: -
Funções: build_parser, main
```python
"""CLI para disparar a varredura e triagem de fichas na rede corporativa."""

import argparse
import sys
from pathlib import Path

from app.bootstrap import bootstrap_application
from services.network_discovery_service import run_network_discovery


def build_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos para o script de discovery."""
    parser = argparse.ArgumentParser(
        description="Varre pastas de rede, classifica fichas e as copia para processamento."
    )
    parser.add_argument(
        "--configs-dir",
        type=str,
        default=None,
        help="Caminho para o diretório de configurações (opcional).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        app_ctx = bootstrap_application(configs_dir=args.configs_dir)
        print(f"[INFO] Contexto inicializado a partir de: {app_ctx.path('configs')}")
        
        print("\n" + "="*60)
        print("INICIANDO VARREDURA E TRIAGEM NA REDE")
        print("="*60)

        # Inicia a varredura real
        summary = run_network_discovery(app_ctx)
        
        print("\n" + "="*60)
        print("RESUMO DA TRIAGEM")
        print("="*60)
        print(f"✅ Comercializadoras (Movidas para pendentes): {summary.get('comercializadoras_encontradas', 0)}")
        print(f"✅ Consumidores (Movidas para pendentes)   : {summary.get('consumidores_encontrados', 0)}")
        print(f"❌ Não Identificados / Erros             : {summary.get('falhas_identificacao', 0)}")
        print(f"📄 Status Final                          : {summary.get('status')}")
        print("="*60)

    except Exception as exc:
        print(f"\n[ERRO CRÍTICO] Falha na execução do Discovery: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
```


---
## src\cli\run_fichas_consumidores.py
Linhas: 47
Classes: -
Funções: build_parser, main
```python
import argparse
import sys
from pathlib import Path

from src.app.bootstrap import bootstrap_application
from src.services.fichas_consumidores_service import process_fichas_consumidores


def build_parser() -> argparse.ArgumentParser:
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
    parser = build_parser()
    args = parser.parse_args()

    try:
        app_ctx = bootstrap_application(configs_dir=args.configs_dir)
        print(f"[INFO] Contexto da aplicacao inicializado a partir de: {app_ctx.path('configs')}")
        
        # Inicia o processamento real da fila
        summary = process_fichas_consumidores(app_ctx)
        print(f"[INFO] Resumo do processamento: {summary}")

    except Exception as exc:
        print(f"[ERRO] Falha na execucao: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```


---
## src\common\excel.py
Linhas: 94
Classes: -
Funções: open_workbook, close_workbook_safely, read_cell, normalize_label_text, find_cell_by_regex
```python
"""Operações de leitura e fechamento seguro de workbooks Excel."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter


def open_workbook(path: str | Path) -> Any:
    """Abre um workbook Excel em modo somente leitura."""
    return load_workbook(
        filename=Path(path),
        data_only=True,
        read_only=True,
        keep_links=False,
    )

def close_workbook_safely(workbook: Any) -> None:
    """Fecha um workbook ignorando falhas de liberação."""
    if workbook is None:
        return
    try:
        workbook.close()
    except Exception:
        return

def read_cell(worksheet: Worksheet, cell_ref: str, return_meta: bool = False) -> Any:
    """Lê o valor de uma célula a partir de uma referência A1 (ex: 'A19')."""
    if not cell_ref or cell_ref == "0":
        return (None, None) if return_meta else None
    val = worksheet[cell_ref].value
    if return_meta:
        return val, {"aba": worksheet.title, "celula": cell_ref}
    return val

def normalize_label_text(text: Any) -> str:
    """Normaliza o texto removendo espaços extras, acentos e marcadores."""
    if text is None:
        return ""
    text_str = str(text).strip().lower()
    return re.sub(r"\s+", " ", text_str)

def find_cell_by_regex(
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
## src\control\mapping_loader.py
Linhas: 75
Classes: -
Funções: _load_and_validate_mapping, load_mapping_fichas_comercializadoras, load_mapping_fichas_consumidores
```python
"""Carregamento e validação estrita dos mappings das fichas."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.context import AppContext
from common.io_json import read_json
from common.validation import validate_json_schema

def _load_and_validate_mapping(
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
        content = read_json(mapping_path)
        schema = read_json(schema_path)

        # Validação Estrita (Fail-Fast)
        validate_json_schema(instance=content, schema=schema, label=descricao)

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


def load_mapping_fichas_comercializadoras(
    context: AppContext,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega e valida o mapping de fichas de comercializadoras."""
    return _load_and_validate_mapping(
        mapping_path=context.control_file("mapping_fichas_comercializadoras"),
        schema_path=context.control_file("schema_mapping_fichas_comercializadoras"),
        descricao="Mapping de Comercializadoras",
        logger=logger,
    )


def load_mapping_fichas_consumidores(
    context: AppContext,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega e valida o mapping de fichas de consumidores."""
    return _load_and_validate_mapping(
        mapping_path=context.control_file("mapping_fichas_consumidores"),
        schema_path=context.control_file("schema_mapping_fichas_consumidores"),
        descricao="Mapping de Consumidores",
        logger=logger,
    )
```


---
## src\control\quality_loader.py
Linhas: 73
Classes: -
Funções: _load_and_validate_quality_rules, load_data_quality_rules_comercializadoras, load_data_quality_rules_consumidores
```python
"""Carregamento e validação estrita das regras de qualidade da entidade.

feat(T1.1.2): Integra validação contra JSON Schema (mesmo padrão de mapping_loader.py).
Regras malformadas geram erro descritivo antes do processamento de qualquer ficha.
Ref: §5.2, §5.3 do Planejamento Funcional.
"""
from __future__ import annotations

from typing import Any

from app.context import AppContext
from common.io_json import read_json
from common.validation import validate_json_schema


def _load_and_validate_quality_rules(
    rules_path,
    schema_path,
    descricao: str,
    logger: Any,
) -> dict[str, Any]:
    """Carrega um arquivo de quality rules e valida contra seu JSON Schema."""
    try:
        logger.info("Carregando %s: %s", descricao, rules_path)

        if not rules_path.exists():
            raise FileNotFoundError(f"Arquivo de quality rules não encontrado: {rules_path}")

        if not schema_path.exists():
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_path}")

        content = read_json(rules_path)
        schema = read_json(schema_path)

        # Validação Estrita (Fail-Fast)
        validate_json_schema(instance=content, schema=schema, label=descricao)

        if not isinstance(content, dict):
            raise ValueError(f"O {descricao} deve ser um objeto JSON.")

        logger.info("%s carregado e validado com sucesso.", descricao)

        return content

    except Exception:
        logger.exception("Falha crítica ao carregar e validar %s", descricao)
        raise


def load_data_quality_rules_comercializadoras(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega e valida as regras de qualidade das fichas de comercializadoras."""
    return _load_and_validate_quality_rules(
        rules_path=context.control_file("data_quality_rules_fichas_comercializadoras"),
        schema_path=context.control_file("schema_data_quality_rules"),
        descricao="Regras de Qualidade de Comercializadoras",
        logger=logger,
    )


def load_data_quality_rules_consumidores(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega e valida as regras de qualidade das fichas de consumidores."""
    return _load_and_validate_quality_rules(
        rules_path=context.control_file("data_quality_rules_fichas_consumidores"),
        schema_path=context.control_file("schema_data_quality_rules"),
        descricao="Regras de Qualidade de Consumidores",
        logger=logger,
    )

```


---
## src\domain\credito\notas_quantitativas_cpura.py
Linhas: 172
Classes: -
Funções: _obter_valor_numerico, _normalizar_pd, _obter_faixas_notas, _atribuir_nota_por_faixa, calcular_notas_quantitativas_cpura
```python
# -*- coding: utf-8 -*-
"""Cálculo das notas quantitativas de CPURA."""

from __future__ import annotations

from typing import Any

from common.types import normalize_float
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_valor_numerico(
    registro: dict[str, Any],
    campo: str,
) -> float:
    """Obtém e valida um valor numérico do registro."""
    valor = normalize_float(registro.get(campo))

    if valor is None:
        raise PdInputValidationError(
            f"{campo} não informado."
        )

    return float(valor)


def _normalizar_pd(valor: float) -> float:
    """Normaliza PD para escala decimal [0, 1]."""
    if valor < 0:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT negativa: {valor}"
        )

    if valor > 1:
        valor = valor / 100.0

    if valor > 1:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT fora do intervalo após normalização: {valor}"
        )

    return valor


def _obter_faixas_notas(
    score_cpura_config: dict[str, Any],
    indicador: str,
) -> list[dict[str, Any]]:
    """Obtém as faixas de notas de um indicador."""
    faixas_root = score_cpura_config.get("faixas_notas_quantitativas")

    if not isinstance(faixas_root, dict):
        raise PdConfigurationError(
            "Bloco 'faixas_notas_quantitativas' ausente ou inválido."
        )

    faixas = faixas_root.get(indicador)

    if not isinstance(faixas, list) or not faixas:
        raise PdConfigurationError(
            f"Faixas quantitativas ausentes ou inválidas para {indicador}."
        )

    return faixas


def _atribuir_nota_por_faixa(
    valor: float,
    faixas: list[dict[str, Any]],
    indicador: str,
) -> str:
    """Atribui nota A-E conforme a faixa parametrizada."""
    for faixa in faixas:
        try:
            nota = str(faixa["nota"]).strip().upper()
            minimo = float(faixa["min"])
            maximo = float(faixa["max"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Faixa incompleta em {indicador}: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                f"Faixa inválida em {indicador}."
            ) from exc

        if minimo > maximo:
            raise PdConfigurationError(
                f"Faixa inválida em {indicador}: min > max."
            )

        if minimo <= valor <= maximo:
            return nota

    raise PdInputValidationError(
        f"Valor sem faixa configurada para {indicador}: {valor}"
    )


def calcular_notas_quantitativas_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula as notas quantitativas de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo das notas quantitativas CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )

        pd_valor = _obter_valor_numerico(registro, "PROBABILIDADE_DEFAULT")
        fco_rol_valor = _obter_valor_numerico(registro, "MFCO")
        roe_valor = _obter_valor_numerico(registro, "ROE")
        roa_valor = _obter_valor_numerico(registro, "ROA")

        pd_valor = _normalizar_pd(pd_valor)

        nota_pd = _atribuir_nota_por_faixa(
            valor=pd_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "PD"),
            indicador="PD",
        )
        nota_fco_rol = _atribuir_nota_por_faixa(
            valor=fco_rol_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "FCO_ROL"),
            indicador="FCO_ROL",
        )
        nota_roe = _atribuir_nota_por_faixa(
            valor=roe_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "ROE"),
            indicador="ROE",
        )
        nota_roa = _atribuir_nota_por_faixa(
            valor=roa_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "ROA"),
            indicador="ROA",
        )

        resultado = {
            "NOTA_PD": nota_pd,
            "NOTA_FCO_ROL": nota_fco_rol,
            "NOTA_ROE": nota_roe,
            "NOTA_ROA": nota_roa,
        }

        if logger is not None:
            logger.info(
                "Notas quantitativas CPURA calculadas. "
                "CNPJ=%s NOTA_PD=%s NOTA_FCO_ROL=%s NOTA_ROE=%s NOTA_ROA=%s",
                registro.get("CNPJ"),
                resultado["NOTA_PD"],
                resultado["NOTA_FCO_ROL"],
                resultado["NOTA_ROE"],
                resultado["NOTA_ROA"],
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo das notas quantitativas CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )
        raise

```


---
## src\domain\credito\pd_consumidor_le5.py
Linhas: 75
Classes: -
Funções: calcular_pd_final_consumidor_le5
```python
"""Transformação da PD para consumidores abaixo de 5 MWm (Bureau)."""

from __future__ import annotations
from typing import Any

from common.types import normalize_float
from domain.credito.pd_exceptions import PdCalculationError, PdInputValidationError

def calcular_pd_final_consumidor_le5(
    registro: dict[str, Any],
    pd_faixas: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula PD via score de bureau e restritivos (Sem DFs)."""
    try:
        score = normalize_float(registro.get("SCORE_BUREAU"))
        restritivos = normalize_float(registro.get("QUANTIDADE_RESTRITIVOS")) or 0.0

        if score is None:
            raise PdInputValidationError("SCORE_BUREAU não informado para consumidor < 5 MWm.")

        # 1. Mapeamento Direto: Score -> Rating (Escala 0 a 1000)
        if score >= 800:
            rating = "A"
        elif score >= 600:
            rating = "B"
        elif score >= 400:
            rating = "C"
        elif score >= 200:
            rating = "D"
        else:
            rating = "E"

        # 2. Regra de Política de Crédito: Restritivos derrubam a nota
        if restritivos > 0:
            rating = "E"

        faixas = pd_faixas.get("CONSUMIDOR_LE_5", {})
        if rating not in faixas:
            raise PdCalculationError(f"Faixa de PD não encontrada para o rating {rating}.")

        pd_min = float(faixas[rating]["min"])
        pd_max = float(faixas[rating]["max"])

        # 3. Interpolação: Inversamente proporcional (Maior Score = Menor PD)
        limites = {"A": (800, 1000), "B": (600, 800), "C": (400, 600), "D": (200, 400), "E": (0, 200)}
        s_min, s_max = limites[rating]

        score_truncado = max(s_min, min(score, s_max))
        fator = 0.5 if s_max == s_min else 1.0 - ((score_truncado - s_min) / (s_max - s_min))
        pd_final = pd_min + (fator * (pd_max - pd_min))

        resultado = {
            "RATING_FINAL": rating,
            "PD_FINAL": pd_final,
            "PD_METODO": "SCORE_BUREAU",
            "SCORE_BUREAU_UTILIZADO": score,
            "QUANTIDADE_RESTRITIVOS": restritivos,
            "PD_MIN_FAIXA": pd_min,
            "PD_MAX_FAIXA": pd_max,
            # T1.4.2: Mascarar campos ausentes como NAO_APLICAVEL para tabelas relacionais
            "PATRIMONIO_LIQUIDO": "NAO_APLICAVEL",
            "LUCRO_LIQUIDO": "NAO_APLICAVEL",
            "ATIVO_TOTAL": "NAO_APLICAVEL",
            "PASSIVO_CIRCULANTE": "NAO_APLICAVEL"
        }

        if logger:
            logger.info("PD LE_5 calculada. CNPJ=%s SCORE=%s RATING=%s PD=%s", registro.get("CNPJ"), score, rating, pd_final)

        return resultado

    except Exception as exc:
        if logger: logger.exception("Falha no cálculo LE_5.")
        raise PdCalculationError(f"Falha LE_5: {exc}") from exc
```


---
## src\domain\credito\pd_exceptions.py
Linhas: 15
Classes: PdCalculationError, PdInputValidationError, PdConfigurationError
Funções: -
```python
"""Exceções do motor de probabilidade de default."""

from __future__ import annotations


class PdCalculationError(Exception):
    """Erro base do cálculo de PD ajustada."""


class PdInputValidationError(PdCalculationError):
    """Erro de validação dos insumos de PD."""


class PdConfigurationError(PdCalculationError):
    """Erro de configuração do motor de PD."""

```


---
## src\domain\credito\pd_transform.py
Linhas: 173
Classes: -
Funções: _obter_faixa_pd, transformar_pd_por_segmento
```python
"""Despacho da transformação de PD por segmento."""

from __future__ import annotations

from typing import Any

from domain.credito.pd_cgrupo import calcular_pd_final_cgrupo
from domain.credito.pd_consumidor_gt5 import calcular_pd_final_consumidor_gt5
from domain.credito.pd_consumidor_le5 import calcular_pd_final_consumidor_le5
from domain.credito.pd_cpura import calcular_pd_final_cpura
from domain.credito.pd_exceptions import PdCalculationError, PdConfigurationError


def _obter_faixa_pd(
    pd_faixas: dict[str, Any],
    segmento_pd: str,
    rating_final: str,
) -> tuple[float, float]:
    """Obtém a faixa de PD parametrizada para segmento e rating."""
    if not pd_faixas:
        raise PdConfigurationError("Faixas de PD não informadas.")

    if segmento_pd not in pd_faixas:
        raise PdConfigurationError(
            f"Segmento não encontrado nas faixas de PD: {segmento_pd}"
        )

    faixas_segmento = pd_faixas[segmento_pd]

    if rating_final not in faixas_segmento:
        raise PdConfigurationError(
            f"Rating {rating_final} não encontrado para {segmento_pd}"
        )

    faixa = faixas_segmento[rating_final]

    if "min" not in faixa or "max" not in faixa:
        raise PdConfigurationError(
            f"Faixa inválida para {segmento_pd}/{rating_final}."
        )

    pd_min = float(faixa["min"])
    pd_max = float(faixa["max"])

    if pd_min > pd_max:
        raise PdConfigurationError(
            f"Faixa inválida: min > max para {segmento_pd}/{rating_final}."
        )

    return pd_min, pd_max


def transformar_pd_por_segmento(
    registro: dict[str, Any],
    segmento_pd: str,
    pd_base: float,
    pd_faixas: dict[str, Any],
    pd_cpura_config: dict[str, Any] | None = None,
    logger: Any | None = None,
    peer_group: list[float] | None = None,
    pd_transform_rules: dict[str, Any] | None = None,
    rating_final: str | None = None,
) -> dict[str, Any]:
    """Transforma a PD base conforme a metodologia do segmento."""
    segmento = str(segmento_pd or "").strip().upper()

    if segmento == "CPURA":
        rating = str(
            registro.get("RATING_FINAL") or rating_final or ""
        ).strip().upper()

        if not rating:
            raise PdConfigurationError(
                "RATING_FINAL não informado para CPURA.")

        pd_min, pd_max = _obter_faixa_pd(
            pd_faixas=pd_faixas,
            segmento_pd=segmento,
            rating_final=rating,
        )

        return calcular_pd_final_cpura(
            registro=registro,
            pd_base=pd_base,
            rating_final=rating,
            pd_min=pd_min,
            pd_max=pd_max,
            cpura_config=pd_cpura_config or {},
            logger=logger,
        )

    if segmento == "CGRUPO":
        if not pd_transform_rules:
            raise PdConfigurationError(
                "pd_transform_rules não informado para CGRUPO."
            )

        registro_calculo = dict(registro)
        registro_calculo["PD_BASE"] = pd_base

        return calcular_pd_final_cgrupo(
            registro=registro_calculo,
            regras_segmento=pd_transform_rules["CGRUPO"],
            logger=logger,
        )

    if segmento == "CONSUMIDOR_GT_5":
        rating = str(
            registro.get("RATING_FINAL")
            or registro.get("RATING_COPEL")
            or rating_final
            or ""
        ).strip().upper()

        if not rating:
            raise PdConfigurationError(
                "RATING_FINAL não informado para CONSUMIDOR_GT_5."
            )

        pd_min, pd_max = _obter_faixa_pd(
            pd_faixas=pd_faixas,
            segmento_pd=segmento,
            rating_final=rating,
        )

        if not pd_transform_rules or segmento not in pd_transform_rules:
            raise PdConfigurationError(
                "pd_transform_rules não informado para CONSUMIDOR_GT_5."
            )

        return calcular_pd_final_consumidor_gt5(
            registro=registro,
            pd_base=pd_base,
            rating_final=rating,
            pd_min=pd_min,
            pd_max=pd_max,
            regras_segmento=pd_transform_rules[segmento],
            logger=logger,
        )
        
    if segmento == "CONSUMIDOR_LE_5":
        rating = str(
            registro.get("RATING_FINAL")
            or registro.get("RATING_COPEL")
            or rating_final
            or ""
        ).strip().upper()

        if not rating:
            raise PdConfigurationError(
                "RATING_FINAL não informado para CONSUMIDOR_LE_5."
            )

        pd_min, pd_max = _obter_faixa_pd(
            pd_faixas=pd_faixas,
            segmento_pd=segmento,
            rating_final=rating,
        )

        if not pd_transform_rules or segmento not in pd_transform_rules:
            raise PdConfigurationError(
                "pd_transform_rules não informado para CONSUMIDOR_LE_5."
            )

        return calcular_pd_final_consumidor_le5(
            registro=registro,
            pd_faixas=pd_faixas,
            logger=logger,
        )

    raise PdCalculationError(
        f"Segmento PD não suportado para transformação: {segmento}"
    )

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
## src\domain\credito\score_qualitativo.py
Linhas: 161
Classes: -
Funções: _obter_nota_auditoria, _obter_peso_nota, calcular_score_qualitativo_cpura
```python
"""Cálculo do score qualitativo para CPURA."""

from __future__ import annotations

from typing import Any

from common.strings import normalize_string
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_nota_auditoria(
    auditor: Any,
    auditor_para_nota: dict[str, str],
) -> str:
    """Converte o auditor em nota qualitativa."""
    auditor_normalizado = normalize_string(auditor, upper=True)

    if not auditor_normalizado:
        raise PdInputValidationError("AUDITOR não informado.")

    nota = auditor_para_nota.get(auditor_normalizado)

    if nota is None:
        raise PdInputValidationError(
            f"AUDITOR sem mapeamento qualitativo: {auditor!r}"
        )

    return nota


def _obter_peso_nota(
    nota: Any,
    nota_para_peso: dict[str, Any],
    nome_campo: str,
) -> float:
    """Obtém o peso numérico da nota qualitativa."""
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


def calcular_score_qualitativo_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score qualitativo de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando score qualitativo CPURA. CNPJ=%s",
                registro.get("CNPJ"),
            )

        nota_para_peso = score_cpura_config.get("nota_para_peso")
        pesos_qualitativos = score_cpura_config.get("pesos_qualitativos")
        auditor_para_nota = score_cpura_config.get("auditor_para_nota")

        if not isinstance(nota_para_peso, dict):
            raise PdConfigurationError(
                "Bloco 'nota_para_peso' ausente ou inválido."
            )

        if not isinstance(pesos_qualitativos, dict):
            raise PdConfigurationError(
                "Bloco 'pesos_qualitativos' ausente ou inválido."
            )

        if not isinstance(auditor_para_nota, dict):
            raise PdConfigurationError(
                "Bloco 'auditor_para_nota' ausente ou inválido."
            )

        nota_board = registro.get("NOTA_BOARD")
        nota_bureau = registro.get("NOTA_BUREAU")
        auditor = registro.get("AUDITOR")

        nota_auditoria = _obter_nota_auditoria(
            auditor,
            auditor_para_nota,
        )

        peso_board = _obter_peso_nota(
            nota_board,
            nota_para_peso,
            "NOTA_BOARD",
        )
        peso_bureau = _obter_peso_nota(
            nota_bureau,
            nota_para_peso,
            "NOTA_BUREAU",
        )
        peso_auditoria = _obter_peso_nota(
            nota_auditoria,
            nota_para_peso,
            "NOTA_AUDITORIA",
        )

        try:
            w_board = float(pesos_qualitativos["BOARD"])
            w_auditoria = float(pesos_qualitativos["AUDITORIA"])
            w_bureau = float(pesos_qualitativos["BUREAU"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Peso qualitativo ausente: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                "Pesos qualitativos inválidos."
            ) from exc

        score_qualitativo = (
            w_board * peso_board
            + w_auditoria * peso_auditoria
            + w_bureau * peso_bureau
        )

        resultado = {
            "NOTA_AUDITORIA": nota_auditoria,
            "PESO_BOARD": peso_board,
            "PESO_AUDITORIA": peso_auditoria,
            "PESO_BUREAU": peso_bureau,
            "SCORE_QUALITATIVO": score_qualitativo,
        }

        if logger is not None:
            logger.info(
                "Score qualitativo CPURA calculado. "
                "CNPJ=%s SCORE_QUALITATIVO=%s",
                registro.get("CNPJ"),
                score_qualitativo,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score qualitativo CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )
        raise

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
## src\services\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Serviços de processamento do sistema BDC."""

```


---
## src\services\audit_service.py
Linhas: 162
Classes: -
Funções: registrar_inicio_pipeline, registrar_fim_pipeline, registrar_documento, registrar_linhagem_campos
```python
"""Serviços de Auditoria do Pipeline (§11.5 — Tabelas de Controle).

Registra cada execução do pipeline (ctl_run_pipeline) e cada documento
processado (ctl_documento) em tabelas persistentes.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from storage.silver_store import write_silver_dataset


LOGGER = logging.getLogger("bdc.auditoria")


# ==============================================================================
# ctl_run_pipeline — Uma linha por execução do pipeline
# ==============================================================================
def registrar_inicio_pipeline(
    run_id: str,
    etapas_planejadas: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o início de uma execução do pipeline."""
    registro = {
        "RUN_ID": run_id,
        "DT_INICIO": datetime.now().isoformat(timespec="seconds"),
        "DT_FIM": None,
        "STATUS_GERAL": "EM_EXECUCAO",
        "TOTAL_ETAPAS": etapas_planejadas,
        "ETAPAS_OK": 0,
        "ETAPAS_FALHA": 0,
        "VERSAO_SISTEMA": "BDC_v06",
    }
    LOGGER.info("Pipeline iniciado (run_id=%s).", run_id)
    return registro


def registrar_fim_pipeline(
    registro_inicio: dict[str, Any],
    etapas_ok: int,
    etapas_falha: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o fim de uma execução do pipeline e persiste em ctl_run_pipeline."""
    registro = registro_inicio.copy()
    registro["DT_FIM"] = datetime.now().isoformat(timespec="seconds")
    registro["STATUS_GERAL"] = "SUCESSO" if etapas_falha == 0 else "PARCIAL"
    registro["ETAPAS_OK"] = etapas_ok
    registro["ETAPAS_FALHA"] = etapas_falha

    control_dir.mkdir(parents=True, exist_ok=True)

    # Append-only: cada execução é uma nova linha no arquivo de controle
    ctl_path = control_dir / "ctl_run_pipeline.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    csv_path = control_dir / "ctl_run_pipeline.csv"
    df_combined.to_csv(csv_path, index=False, encoding="utf-8-sig", sep=";")

    LOGGER.info(
        "Pipeline finalizado (run_id=%s). Status=%s. OK=%d, Falha=%d.",
        registro["RUN_ID"], registro["STATUS_GERAL"],
        etapas_ok, etapas_falha,
    )
    return registro


# ==============================================================================
# ctl_documento — Uma linha por documento processado
# ==============================================================================
def registrar_documento(
    documento_id: str,
    run_id: str,
    arquivo_origem: str,
    hash_arquivo: str | None,
    tipo_ficha: str,
    status_classificacao: str,
    status_extracao: str,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra um documento processado na tabela ctl_documento (append-only)."""
    registro = {
        "DOCUMENTO_ID": documento_id,
        "RUN_ID": run_id,
        "ARQUIVO_ORIGEM": arquivo_origem,
        "HASH_ARQUIVO": hash_arquivo,
        "TIPO_FICHA": tipo_ficha,
        "STATUS_CLASSIFICACAO": status_classificacao,
        "STATUS_EXTRACAO": status_extracao,
        "DT_PROCESSAMENTO": datetime.now().isoformat(timespec="seconds"),
    }

    control_dir.mkdir(parents=True, exist_ok=True)

    ctl_path = control_dir / "ctl_documento.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    LOGGER.info(
        "Documento registrado: %s (tipo=%s, status=%s).",
        documento_id, tipo_ficha, status_extracao,
    )
    return registro


# ==============================================================================
# ctl_campo_origem — Uma linha por campo extraído (Linhagem)
# ==============================================================================
def registrar_linhagem_campos(
    documento_id: str,
    run_id: str,
    campos_metadata: list[dict[str, Any]],
    control_dir: Path,
) -> None:
    """Registra a linhagem (aba, célula, método) de cada campo extraído."""
    if not campos_metadata:
        return

    registros = []
    dt_proc = datetime.now().isoformat(timespec="seconds")
    for cm in campos_metadata:
        registros.append({
            "DOCUMENTO_ID": documento_id,
            "RUN_ID": run_id,
            "CAMPO": cm.get("campo"),
            "ABA_ORIGEM": cm.get("aba_origem"),
            "CELULA_ORIGEM": cm.get("celula_origem"),
            "METODO_EXTRACAO": cm.get("metodo"),
            "VALOR_EXTRAIDO": str(cm.get("valor"))[:255] if cm.get("valor") is not None else None,
            "DT_PROCESSAMENTO": dt_proc,
        })

    control_dir.mkdir(parents=True, exist_ok=True)
    ctl_path = control_dir / "ctl_campo_origem.parquet"
    
    df_new = pd.DataFrame(registros)
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_parquet(ctl_path, index=False)
    LOGGER.debug("Registrada linhagem de %d campos para documento %s.", len(registros), documento_id)

```


---
## src\services\dedup_service.py
Linhas: 70
Classes: -
Funções: has_duplicate_hash, has_duplicate_business_key, upsert_business_key_in_history
```python
"""Regras de deduplicação e atualização incremental do sistema."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def has_duplicate_hash(
    history: list[dict[str, Any]],
    hash_value: str | None,
) -> bool:
    """Indica se o hash já foi processado anteriormente."""
    if not hash_value:
        return False

    return any(item.get("hash_arquivo") == hash_value for item in history)


def has_duplicate_business_key(
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


def upsert_business_key_in_history(
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
## src\services\denodo_connector.py
Linhas: 144
Classes: DenodoConnectionError
Funções: _request_with_retry, _find_latest_bronze_snapshot, fetch_denodo_rest
```python
"""Conector central para o virtualizador Denodo via API RESTful.

feat(T2.1.1): Adicionados retry com backoff exponencial e fallback para
último snapshot Bronze em caso de indisponibilidade.
Ref: §3.4 do Planejamento Funcional.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Desativa alertas de certificado SSL interno da rede corporativa
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = logging.getLogger(__name__)

# Parâmetros de retry (§3.4 — tratamento de indisponibilidade)
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 2.0


class DenodoConnectionError(Exception):
    """Exceção levantada para falhas de conexão na API do Denodo."""


def _request_with_retry(url: str, params, auth, max_retries: int = MAX_RETRIES) -> requests.Response:
    """Executa GET com retry e backoff exponencial."""
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                params=params,
                auth=auth,
                verify=False,
                timeout=300,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            if attempt < max_retries:
                wait = BACKOFF_BASE_SECONDS ** attempt
                LOGGER.warning(
                    "Tentativa %s/%s falhou para '%s'. Retry em %.1fs. Erro: %s",
                    attempt, max_retries, url, wait, exc,
                )
                time.sleep(wait)
            else:
                LOGGER.error("Todas as %s tentativas falharam para '%s'.", max_retries, url)
    raise last_exc  # type: ignore[misc]


def _find_latest_bronze_snapshot(bronze_dir: Path, prefix: str = "raw_contratos") -> Path | None:
    """Localiza o snapshot Bronze mais recente para fallback."""
    if not bronze_dir.exists():
        return None
    snapshots = [
        f for f in bronze_dir.iterdir()
        if f.is_file() and f.name.startswith(prefix) and f.suffix == ".parquet"
    ]
    if not snapshots:
        return None
    return max(snapshots, key=lambda f: f.stat().st_mtime)


def fetch_denodo_rest(
    view_name: str,
    params: dict[str, Any] | None = None,
    bronze_fallback_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Consome uma view do Denodo via API REST (JSON).
    Gerencia paginação automaticamente, retornando um DataFrame consolidado.

    Se todas as tentativas falharem e `bronze_fallback_dir` for informado,
    tenta ler o último snapshot Bronze disponível (§3.4 — fallback para
    snapshot anterior em caso de indisponibilidade).
    """
    base_url = os.getenv("DENODO_REST_BASE_URL", "https://vidgcpprd.copel.nt:9443/denodo-restfulws/com/views")
    url = f"{base_url}/{view_name}"

    user = os.getenv("DENODO_USER")
    pwd = os.getenv("DENODO_PWD")

    if not all([user, pwd]):
        raise ValueError("Credenciais DENODO_USER ou DENODO_PWD não encontradas no arquivo .env.")

    req_params: dict[str, Any] | None = {"$format": "json"}
    if params:
        req_params.update(params)

    auth = HTTPBasicAuth(user, pwd)
    all_elements: list[dict[str, Any]] = []

    try:
        LOGGER.info("Iniciando extração da view '%s' via REST API...", view_name)

        while url:
            response = _request_with_retry(url, params=req_params, auth=auth)

            data = response.json()
            elements = data.get("elements", [])

            if not elements:
                break

            all_elements.extend(elements)

            links = data.get("links", [])
            next_link = next((link["href"] for link in links if link.get("rel") == "next"), None)

            if next_link:
                url = next_link
                req_params = None
            else:
                url = None  # type: ignore[assignment]

        LOGGER.info("Extração via REST finalizada. %s registros carregados.", len(all_elements))
        return pd.DataFrame(all_elements)

    except (requests.exceptions.RequestException, DenodoConnectionError) as exc:
        LOGGER.exception("Falha na comunicação com a API REST do Denodo.")

        # Fallback: tenta ler último snapshot Bronze (§3.4)
        if bronze_fallback_dir:
            snapshot = _find_latest_bronze_snapshot(bronze_fallback_dir)
            if snapshot:
                LOGGER.warning(
                    "Usando fallback: lendo último snapshot Bronze '%s'.", snapshot.name
                )
                return pd.read_parquet(snapshot)
            LOGGER.error("Nenhum snapshot Bronze encontrado para fallback em '%s'.", bronze_fallback_dir)

        raise DenodoConnectionError(f"Erro ao acessar endpoint '{view_name}': {exc}") from exc
```


---
## src\services\fato_analise_credito_service.py
Linhas: 47
Classes: -
Funções: build_fato_analise_credito
```python
"""Construção da tabela Fato de Análise de Crédito (fato_analise_credito)."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from app.context import AppContext
from storage.silver_store import write_silver_dataset

def build_fato_analise_credito(
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
        
    for col in ["ANALISE_ID", "DATA_ANALISE", "RATING_FINAL", "PD_FINAL", "SCORE_CALCULADO", "CLASSE_RISCO", "MODELO_METODOLOGICO", "DATA_DEMONSTRACAO_FINANCEIRA"]:
        if col not in df_fato.columns: df_fato[col] = None

    rename_map = {
        "CNPJ": "CNPJ", "DATA_ANALISE": "DATA_ANALISE", "RATING_FINAL": "RATING",
        "PD_FINAL": "PD_PERCENTUAL", "SCORE_CALCULADO": "SCORE", "CLASSE_RISCO": "CLASSE",
        "MODELO_METODOLOGICO": "MODELO", "DATA_DEMONSTRACAO_FINANCEIRA": "DATA_BALANCO_USADO"
    }
    df_final = df_fato[list(rename_map.keys())].rename(columns=rename_map).copy()
    
    df_final["ETL_RUN_ID"] = run_id
    relational_dir = context.path("relational_facts")
    relational_dir.mkdir(parents=True, exist_ok=True)
    write_silver_dataset(records=df_final.to_dict(orient="records"), output_dir=relational_dir, filename="fato_analise_credito")
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}
```


---
## src\services\ficha_extractor.py
Linhas: 140
Classes: -
Funções: parse_date_safely, extract_field_value, extract_record
```python
"""Serviço de extração de dados das fichas Excel."""

from datetime import datetime
from typing import Dict, Any, Optional
import openpyxl

from common.excel import find_cell_by_regex, read_cell
from openpyxl.utils.datetime import from_excel

CUTOFF_DATE_LAYOUT_CHANGE = datetime(2025, 4, 30)

def parse_date_safely(date_val: Any) -> Optional[datetime]:
    """Converte valores heterogêneos de data para o tipo datetime, incluindo seriais do Excel."""
    if isinstance(date_val, datetime):
        return date_val
        
    if isinstance(date_val, (int, float)):
        try:
            return from_excel(date_val)
        except ValueError:
            return None

    if isinstance(date_val, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d"):
            try:
                return datetime.strptime(date_val.strip(), fmt)
            except ValueError:
                pass
    return None


def extract_field_value(
    worksheet: openpyxl.worksheet.worksheet.Worksheet,
    field_config: Dict[str, Any],
    ficha_date: Optional[datetime],
    field_name: str,
) -> tuple[Any, dict[str, Any]]:
    """
    Extrai o valor de um campo aplicando a estratégia híbrida e retorna (valor, meta).
    """
    static_cell = field_config.get("value_cell")
    search_pattern = field_config.get("search_pattern")
    
    offset_col = field_config.get("offset_col", 1)
    offset_row = field_config.get("offset_row", 0)
    
    is_post_cutoff = ficha_date is not None and ficha_date > CUTOFF_DATE_LAYOUT_CHANGE
    
    val = None
    meta = {"campo": field_name, "aba_origem": worksheet.title, "celula_origem": None, "metodo": None, "valor": None}
    
    # 1. Estratégia Dinâmica (Para fichas pós-abril/2025 ou se não houver célula estática)
    if (is_post_cutoff or not static_cell) and search_pattern:
        val, meta_inf = find_cell_by_regex(
            worksheet=worksheet,
            search_pattern=search_pattern,
            offset_col=offset_col,
            offset_row=offset_row,
            return_meta=True
        )
        if val is not None:
            meta.update({"metodo": "dinamico_regex", "valor": val})
            if meta_inf:
                meta.update({"aba_origem": meta_inf["aba"], "celula_origem": meta_inf["celula"]})
            return val, meta
            
    # 2. Estratégia Estática (Legado <= 04/2025)
    if static_cell:
        val, meta_inf = read_cell(worksheet, static_cell, return_meta=True)
        if val is not None and str(val).strip() != "":
            meta.update({"metodo": "estatico_fixo", "valor": val})
            if meta_inf:
                meta.update({"aba_origem": meta_inf["aba"], "celula_origem": meta_inf["celula"]})
            return val, meta
            
    # 3. Fallback Dinâmico (Se a coordenada estática falhou em ficha antiga)
    if not is_post_cutoff and search_pattern:
        val, meta_inf = find_cell_by_regex(
            worksheet=worksheet,
            search_pattern=search_pattern,
            offset_col=offset_col,
            offset_row=offset_row,
            return_meta=True
        )
        if val is not None:
            meta.update({"metodo": "dinamico_fallback", "valor": val})
            if meta_inf:
                meta.update({"aba_origem": meta_inf["aba"], "celula_origem": meta_inf["celula"]})
            return val, meta
        
    return val, meta


def extract_record(
    workbook: openpyxl.workbook.workbook.Workbook, 
    layout_schema: Dict[str, Any]
) -> tuple[Dict[str, Any], list[dict[str, Any]]]:
    """
    Executa a extração completa de uma ficha Excel utilizando o catálogo de layout.
    Retorna os dados extraídos e a lista de metadados da linhagem.
    """
    extracted_data = {}
    metadata_list = []
    
    # A chave correta nos seus JSONs é field_map, não fields.
    field_map = layout_schema.get("field_map", {})
    
    # Extrai primeiro a data da DF para definir a estratégia de corte do layout
    date_config = field_map.get("DATA_DEMONSTRACAO_FINANCEIRA", {})
    
    # Define a aba correta para buscar a data
    date_sheet_name = date_config.get("sheet")
    if date_sheet_name and date_sheet_name in workbook.sheetnames:
        ws_date = workbook[date_sheet_name]
    else:
        ws_date = workbook.active
        
    # Extrai a data baseando-se no value_cell (pois a config usa value_cell, não cell)
    raw_date = read_cell(ws_date, date_config.get("value_cell", "A1")) if date_config else None
    ficha_date = parse_date_safely(raw_date)
    
    for field_name, field_config in field_map.items():
        # Define a aba correta dinamicamente para cada campo
        sheet_name = field_config.get("sheet")
        if sheet_name and sheet_name in workbook.sheetnames:
            ws = workbook[sheet_name]
        else:
            ws = workbook.active
            
        val, meta = extract_field_value(
            worksheet=ws,
            field_config=field_config,
            ficha_date=ficha_date,
            field_name=field_name
        )
        extracted_data[field_name] = val
        if meta:
            metadata_list.append(meta)
        
    return extracted_data, metadata_list
```


---
## src\services\fichas_consumidores_service.py
Linhas: 689
Classes: -
Funções: is_valid_cnpj, _is_disk_full_error, _build_run_id, _build_target_name, _resolve_bronze_subfolder, _move_to_rejected, _move_to_processed, _build_pd_info, _build_processing_queue, _process_single_file, process_fichas_consumidores, calc_digit
```python
"""Serviço principal refatorado do pipeline de fichas de consumidores."""

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
from control.layout_catalog import load_layouts_consumidores
from control.mapping_loader import load_mapping_fichas_consumidores
from control.quality_loader import load_data_quality_rules_consumidores
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


def is_valid_cnpj(value: str | None) -> bool:
    """Valida se o valor é um CNPJ válido."""
    if value is None:
        return False

    digits = "".join(ch for ch in str(value) if ch.isdigit())

    if len(digits) != 14:
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
    source = Path(original_name)
    stem = source.stem[:40]

    parts: list[str] = [stem]

    if versao_ficha:
        parts.append(versao_ficha)

    if cnpj:
        safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit())
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
    safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit())
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
    logger: Any,
    source_file: Path,
    manifest: DocumentManifest,
) -> dict[str, Any]:
    """Calcula a PD ajustada para o registro normalizado de consumidor."""
    segmento_pd: str | None = None

    try:
        registro_pd = dict(normalized)
        registro_pd["TIPO_FICHA"] = "CONSUMIDOR"

        segmento_pd = definir_segmento_metodologico(registro_pd)
        registro_pd["SEGMENTO_PD"] = segmento_pd

        pd_info = calcular_pd_ajustada(
            registro=registro_pd,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=None,
            score_cpura_config=None,
            logger=logger,
        )

        logger.info(
            "PD ajustada calculada para %s. Segmento=%s RATING_FINAL=%s PD_FINAL=%s",
            source_file.name,
            pd_info.get("SEGMENTO_PD"),
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
            "PD_BASE": None,
            "RATING_FINAL": None,
            "PD_MIN_FAIXA": None,
            "PD_MAX_FAIXA": None,
            "PERCENTIL_PD_BASE": None,
            "PD_FINAL": None,
            "PD_METODO": None,
            "PD_Q_NORMALIZADA": None,
            "PD_Q_CAP": None,
            "PD_Z_T": None,
            "PD_Z_ESCALADO": None,
            "PD_U_INTERPOLACAO": None,
        }


def _build_processing_queue(
    context: AppContext,
) -> list[tuple[Path, str, Path, Path]]:
    """Monta a fila de processamento normal e reprocessamento."""
    normal_files = discover_pending_excels(
        context.path("input_fichas_consumidores_pendentes")
    )
    reprocess_files = discover_pending_excels(
        context.path("input_reprocessamento_consumidores_pendentes")
    )

    queue: list[tuple[Path, str, Path, Path]] = []

    for file_path in normal_files:
        queue.append(
            (
                file_path,
                "incremental",
                context.path("input_fichas_consumidores_processadas"),
                context.path("input_fichas_consumidores_rejeitadas"),
            )
        )

    for file_path in reprocess_files:
        queue.append(
            (
                file_path,
                "reprocess",
                context.path("input_reprocessamento_consumidores_processados"),
                context.path("input_reprocessamento_consumidores_rejeitados"),
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
    required_fields: Any,
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    quality_rules: dict[str, Any],
    control_dir: Path | None = None,
) -> Optional[dict[str, Any]]:
    """Processa isoladamente um único arquivo de ficha de consumidor."""
    workbook = None
    manifest = DocumentManifest(
        documento_id=str(uuid.uuid4()),
        run_id=run_id,
        ambiente=context.app_config["env"],
        tipo_ficha="consumidor",
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

        # 1. Duplicidade por Hash
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
        staging_dir = context.path("staging_fichas_consumidores")
        staging_name = _build_target_name(
            original_name=source_file.name,
            versao_ficha=None,
            cnpj=None,
            data_df=None,
            hash_value=manifest.hash_arquivo,
        )
        staging_file = copy_to_staging(source_file, staging_dir, staging_name)
        manifest.caminho_staging = str(staging_file)

        # 3. Abertura e Classificação
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
            
        slug = "field_types_fichas_consumidores"
        normalized = normalize_record(raw_record, context, slug, logger)
        normalized.pop("DADOS_CADASTRAIS", None)

        manifest.cnpj_extraido = normalize_cnpj(normalized.get("CNPJ"))
        normalized["CNPJ"] = manifest.cnpj_extraido
        manifest.data_demonstracao_financeira = normalized.get(
            "DATA_DEMONSTRACAO_FINANCEIRA"
        )
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        # 5. Validações Técnicas e CNPJ
        errors, warnings = validate_record(
            normalized, required_fields, logger=logger, quality_rules=quality_rules
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

        # 7. Cálculo das Regras de Negócio (PD)
        pd_info = _build_pd_info(
            normalized=normalized,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            logger=logger,
            source_file=source_file,
            manifest=manifest,
        )

        # 8. Movimentação para Bronze e Processadas
        bronze_root_dir = context.path("bronze_fichas_consumidores_raw")
        bronze_name = _build_target_name(
            original_name=source_file.name,
            versao_ficha=manifest.versao_ficha,
            cnpj=manifest.cnpj_extraido,
            data_df=manifest.data_demonstracao_financeira,
            hash_value=manifest.hash_arquivo,
        )

        bronze_subfolder = _resolve_bronze_subfolder(
            manifest.cnpj_extraido,
            normalized.get("EMPRESA"),
        )

        bronze_staging = copy_to_staging(
            staging_file, staging_dir, bronze_name
        )
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

        # 9. Retorno dos Dados Estruturados
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


def process_fichas_consumidores(
    context: AppContext,
) -> dict[str, Any]:
    """Executa o pipeline completo das fichas de consumidores."""
    run_id = _build_run_id(context)

    log_file = (
        context.path("log_runner") / f"{run_id}__fichas_consumidores.log"
    )
    logger = get_logger("bdc.consumidores", log_file)

    _ = load_mapping_fichas_consumidores(context, logger)

    layouts = load_layouts_consumidores(context, logger)
    quality_rules = load_data_quality_rules_consumidores(context, logger)

    required_fields = quality_rules.get("required_fields")

    ingestion_log_path = (
        context.path("bronze_ingestion_log")
        / "fichas_consumidores_ingestion.jsonl"
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

    try:
        pd_faixas = read_json(context.control_file("pd_faixas"))
        logger.info("Faixas de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_faixas.")
        raise

    try:
        pd_transform_rules = read_json(
            context.control_file("pd_transform_rules")
        )
        logger.info("Regras de transformação de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_transform_rules.")
        raise

    # Processa os arquivos da fila
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

    # Gravação na Camada Silver e Arquivo de Controle
    silver_output_dir = context.path("silver_fichas_consumidores_extraidas")
    docs_output_dir = context.path("silver_documentos_classificados")

    if silver_records:
        merge_silver_dataset_by_business_key(
            records=silver_records,
            output_dir=silver_output_dir,
            filename="fichas_consumidores_extraidas.csv",
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
## src\services\override_service.py
Linhas: 79
Classes: -
Funções: processar_solicitacao_override
```python
"""Serviço de Gestão de Overrides e Exceções (Módulo de Governança).

feat(T4.2.1): Serviço para aplicar, aprovar e monitorar vigência de Overrides.
Ref: §11.7 do Planejamento Funcional.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from domain.enums import StatusAprovacao
from storage.silver_store import write_silver_dataset


def processar_solicitacao_override(
    context: AppContext,
    solicitacao: dict[str, Any]
) -> dict[str, Any]:
    """
    Processa um pedido de Override (sobreposição de regra/rating/limite).
    Exige justificativa, evidência e alçada (aprovador ≠ solicitante).
    """
    run_id = f"OVR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.governanca.override")
    
    logger.info("Iniciando solicitação de Override (run_id=%s).", run_id)

    # Validações de Governança (§11.7)
    campos_obrigatorios = [
        "CNPJ", "TIPO_OVERRIDE", "VALOR_ANTES", "VALOR_DEPOIS",
        "JUSTIFICATIVA", "EVIDENCIA", "SOLICITANTE", "APROVADOR", "DATA_EXPIRACAO"
    ]
    
    for campo in campos_obrigatorios:
        if campo not in solicitacao or solicitacao[campo] is None:
            raise ValueError(f"Campo obrigatório '{campo}' ausente na solicitação de Override.")

    solicitante = str(solicitacao["SOLICITANTE"]).strip().upper()
    aprovador = str(solicitacao["APROVADOR"]).strip().upper()

    if solicitante == aprovador:
        raise ValueError(
            "Conflito de Segregação de Função: Solicitante e Aprovador não podem ser a mesma pessoa (§11.7)."
        )

    # Verifica expiração imediata
    expiracao = pd.to_datetime(solicitacao["DATA_EXPIRACAO"])
    hoje = datetime.now()
    if expiracao < hoje:
        raise ValueError("Data de expiração do Override já passou.")

    # Registro aprovado
    registro = solicitacao.copy()
    registro["STATUS"] = StatusAprovacao.APROVADO.value
    registro["DATA_APROVACAO"] = hoje.isoformat(timespec="seconds")
    registro["RUN_ID"] = run_id

    # Salva na Silver (tabela fato_overrides)
    silver_dir = context.path("silver") / "governanca_overrides"
    if not silver_dir.exists():
        silver_dir.mkdir(parents=True, exist_ok=True)
        
    write_silver_dataset(
        records=[registro],
        output_dir=silver_dir,
        filename=f"solicitacao_override_{run_id}"
    )

    logger.info("Override aprovado e registrado para CNPJ %s.", registro["CNPJ"])

    return {
        "run_id": run_id,
        "cnpj": registro["CNPJ"],
        "status": StatusAprovacao.APROVADO.value
    }

```


---
## src\services\receita_ingestion_service.py
Linhas: 130
Classes: ReceitaIngestionError
Funções: _listar_cnpjs_de_entrada, _save_raw_snapshot, ingest_receita_data
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
from services.receita_connector import fetch_receita_data_batch
from storage.silver_store import write_silver_dataset

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

def _save_raw_snapshot(context: AppContext, payload: list[dict[str, Any]]) -> Path:
    bronze_dir = context.path("bronze") / "snapshots_fontes" / "receita"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    filename = f"raw_receita_{date.today().strftime('%Y%m%d')}.json"
    target = bronze_dir / filename
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target

def ingest_receita_data(context: AppContext) -> dict[str, Any]:
    run_id = f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.receita")

    cnpjs = _listar_cnpjs_de_entrada(context)
    if not cnpjs:
        logger.warning("Nenhum CNPJ encontrado nas bases da Silver para consulta na Receita.")
        return {"run_id": run_id, "linhas_processadas": 0, "alertas_gerados_cad001": 0, "status": "SEM_DADOS"}

    logger.info("Iniciando consulta na BrasilAPI para %d CNPJ(s). Pode levar alguns minutos (Cache ativo)...", len(cnpjs))
    df_receita = fetch_receita_data_batch(cnpjs, context)
    
    if df_receita.empty:
        logger.warning("Consulta da Receita retornou DataFrame vazio.")
        return {"run_id": run_id, "linhas_processadas": 0, "alertas_gerados_cad001": 0, "status": "SEM_DADOS"}

    payload = df_receita.to_dict(orient="records")
    _save_raw_snapshot(context, payload)

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
        write_silver_dataset(
            records=df_alertas.to_dict(orient="records"),
            output_dir=context.path("silver") / "alertas_credito",
            filename=f"alertas_cadastrais_receita_{run_id}",
        )

    silver_dir = context.path("silver") / "receita_silver"
    write_silver_dataset(
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
## src\services\salesforce_connector.py
Linhas: 74
Classes: SalesforceConnectionError
Funções: fetch_salesforce_data
```python
"""Conector de integração de arquivos extraídos do Salesforce (via Power Query)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

class SalesforceConnectionError(Exception):
    """Exceção levantada quando a base do Salesforce não pode ser obtida."""


def fetch_salesforce_data(
    input_dir: Path | str,
    logger: Any | None = None,
) -> Dict[str, pd.DataFrame]:
    """
    Lê o arquivo salesforce.xlsx atualizado via Power Query contendo as abas:
    Conta, Cotação, Chamado e Contrato. Retorna um dicionário de DataFrames.
    """
    diretorio = Path(input_dir)
    arquivo_sf = diretorio / "salesforce.xlsx"
    
    if logger:
        logger.info("Iniciando leitura da base local do Salesforce: %s", arquivo_sf)
        
    if not arquivo_sf.exists():
        if logger:
            logger.error("Arquivo %s não encontrado.", arquivo_sf)
        raise FileNotFoundError(f"Arquivo Salesforce não encontrado na pasta: {arquivo_sf}")

    resultados_df = {}
    
    # Mapeamento das abas do Excel para os nomes lógicos exigidos pelo sistema
    mapa_abas = {
        "Conta": "Account",
        "Cotação": "Cotacao",
        "Chamado": "Chamado",
        "Contrato": "Contrato"
    }

    try:
        for aba_excel, chave_dict in mapa_abas.items():
            if logger:
                logger.info("Lendo aba '%s' do Salesforce...", aba_excel)
            
            # Lendo tudo como string (dtype=str) para não corromper 'Id' e 'AccountId'
            df = pd.read_excel(arquivo_sf, sheet_name=aba_excel, dtype=str)
            
            # Tratamento de nulos vindos do Excel (transforma "nan" string em real None ou string vazia)
            df = df.fillna("")
            df = df.replace("nan", "")
            
            # Normalização específica da máscara de CNPJ na aba Conta
            if chave_dict == "Account" and "CNPJ__c" in df.columns:
                df["CNPJ__c"] = (
                    df["CNPJ__c"]
                    .astype(str)
                    .str.replace(r"\D", "", regex=True) # Remove pontos, traços e barras
                    .str.zfill(14) # Garante os 14 dígitos com zeros à esquerda
                )
            
            resultados_df[chave_dict] = df
            
            if logger:
                logger.info("Aba '%s' carregada com sucesso. %s registros processados.", aba_excel, len(df))

        return resultados_df

    except Exception as exc:
        if logger:
            logger.exception("Falha crítica ao ler o arquivo local do Salesforce.")
        raise SalesforceConnectionError(f"Erro ao processar as planilhas do Salesforce: {exc}") from exc
```


---
## src\services\salesforce_ingestion_service.py
Linhas: 134
Classes: SalesforceIngestionError
Funções: ingest_salesforce_data, enriquecer_com_cnpj
```python
"""Serviço de ingestão e normalização da base do Salesforce."""

from __future__ import annotations

import shutil
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from common.logging_utils import get_logger
from services.salesforce_connector import fetch_salesforce_data
from storage.silver_store import write_silver_dataset


class SalesforceIngestionError(Exception):
    """Exceção para falhas na ingestão da base do Salesforce."""


def ingest_salesforce_data(context: AppContext) -> dict[str, Any]:
    """
    Lê o arquivo do Salesforce (via conector), salva o snapshot na Bronze,
    deduplica os registros, enriquece as tabelas filhas com o CNPJ da Conta
    e persiste na camada Silver.
    """
    run_id = f"SF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__ingestao_salesforce.log"
    logger = get_logger("bdc.salesforce", log_file)

    try:
        logger.info("Iniciando processo de ingestão da base do Salesforce.")

        input_dir = context.path("entradas") / "salesforce"
        arquivo_bruto = input_dir / "salesforce.xlsx"

        if not arquivo_bruto.exists():
            logger.warning("Arquivo salesforce.xlsx não encontrado na entrada.")
            return {"run_id": run_id, "status": "SEM_DADOS"}

        # 1. Copia o snapshot bruto intacto para a Bronze
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "salesforce"
        bronze_dir.mkdir(parents=True, exist_ok=True)

        nome_bronze = f"raw_salesforce_{datetime.now().strftime('%Y%m%d')}_{arquivo_bruto.name}"
        caminho_bronze = bronze_dir / nome_bronze
        shutil.copy2(arquivo_bruto, caminho_bronze)
        logger.info("Snapshot bruto salvo na Bronze em: %s", caminho_bronze.name)

        # 2. Extração via Conector
        dfs_sf = fetch_salesforce_data(input_dir=input_dir, logger=logger)
        
        df_account = dfs_sf.get("Account", pd.DataFrame())
        df_cotacao = dfs_sf.get("Cotacao", pd.DataFrame())
        df_chamado = dfs_sf.get("Chamado", pd.DataFrame())
        df_contrato = dfs_sf.get("Contrato", pd.DataFrame())

        # 3. Deduplicação (Mantém apenas o último registro de cada Id inserido pelo Power Query)
        df_account = df_account.drop_duplicates(subset=["Id"], keep="last") if not df_account.empty else df_account
        df_cotacao = df_cotacao.drop_duplicates(subset=["Id"], keep="last") if not df_cotacao.empty else df_cotacao
        df_chamado = df_chamado.drop_duplicates(subset=["Id"], keep="last") if not df_chamado.empty else df_chamado
        df_contrato = df_contrato.drop_duplicates(subset=["Id"], keep="last") if not df_contrato.empty else df_contrato

        # Padroniza nome da coluna CNPJ na Account para facilitar os cruzamentos
        if "CNPJ__c" in df_account.columns:
            df_account = df_account.rename(columns={"CNPJ__c": "CNPJ"})

        # 4. Enriquecimento: Traz o CNPJ da Conta (Account) para os objetos filhos
        if not df_account.empty and "CNPJ" in df_account.columns:
            account_map = df_account[["Id", "CNPJ"]].rename(columns={"Id": "AccountId_Join"})
            
            def enriquecer_com_cnpj(df_filho: pd.DataFrame) -> pd.DataFrame:
                if df_filho.empty or "AccountId" not in df_filho.columns:
                    return df_filho
                
                # Faz o Procv/Join: Filho[AccountId] == Conta[Id]
                df_merged = pd.merge(
                    df_filho, 
                    account_map, 
                    left_on="AccountId", 
                    right_on="AccountId_Join", 
                    how="left"
                )
                df_merged = df_merged.drop(columns=["AccountId_Join"])
                
                # Se não encontrou CNPJ (conta órfã), preenche com zeros para evitar quebra de contrato
                if "CNPJ" in df_merged.columns:
                    df_merged["CNPJ"] = df_merged["CNPJ"].fillna("00000000000000")
                return df_merged

            df_cotacao = enriquecer_com_cnpj(df_cotacao)
            df_chamado = enriquecer_com_cnpj(df_chamado)
            df_contrato = enriquecer_com_cnpj(df_contrato)

        # Adiciona metadados de rastreabilidade
        for df in [df_account, df_cotacao, df_chamado, df_contrato]:
            if not df.empty:
                df["RUN_ID"] = run_id
                df["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        # 5. Persistência na Silver (CSV + Parquet) separada por objeto
        silver_dir = context.path("silver") / "salesforce_silver"
        
        datasets = {
            "account": df_account,
            "cotacao": df_cotacao,
            "chamado": df_chamado,
            "contrato": df_contrato
        }

        arquivos_salvos = []
        for nome, df in datasets.items():
            if not df.empty:
                csv_p, pqt_p = write_silver_dataset(
                    records=df.to_dict(orient="records"),
                    output_dir=silver_dir / nome,
                    filename=f"salesforce_{nome}"
                )
                arquivos_salvos.append(nome)

        logger.info("Ingestão do Salesforce concluída. Objetos salvos: %s", ", ".join(arquivos_salvos))

        return {
            "run_id": run_id,
            "linhas_account": len(df_account),
            "linhas_cotacao": len(df_cotacao),
            "linhas_chamado": len(df_chamado),
            "linhas_contrato": len(df_contrato),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica na ingestão do Salesforce.")
        raise SalesforceIngestionError(f"Erro ao ingerir base do Salesforce: {exc}") from exc
```


---
## src\tests\test_context.py
Linhas: 131
Classes: -
Funções: setup_env, test_cenario_1_sucesso, test_cenario_2_diretorio_inexistente, test_cenario_3_arquivo_config_ausente, test_cenario_4_control_files_ausente, test_cenario_5_schema_nao_encontrado_no_disco, test_cenario_6_schema_invalido_campo_ausente, test_cenario_7_schema_invalido_tipo_errado
```python
import json
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.context import load_context

@pytest.fixture
def setup_env(tmp_path):
    """Fixture que simula a estrutura de arquivos e schemas necessários para os testes."""
    configs_dir = tmp_path / "configs"
    configs_dir.mkdir()
    
    schema_dir = tmp_path / "control" / "schemas"
    schema_dir.mkdir(parents=True)
    
    schema_app_path = schema_dir / "schema_app_config.json"
    schema_config_path = schema_dir / "schema_config.json"
    
    # 1. Schemas de simulação (mock) com regras estritas
    schema_app_config = {
        "type": "object",
        "required": ["env", "control_files"],
        "properties": {
            "env": {"type": "string"},
            "control_files": {"type": "object"}
        }
    }
    schema_config = {
        "type": "object",
        "required": ["system_name"],
        "properties": {
            "system_name": {"type": "string"}
        }
    }
    schema_app_path.write_text(json.dumps(schema_app_config))
    schema_config_path.write_text(json.dumps(schema_config))
    
    # 2. Configurações válidas (Happy Path)
    valid_app_config = {
        "env": "dev",
        "paths": {},
        "naming": {},
        "control_files": {
            "schema_app_config": str(schema_app_path),
            "schema_config": str(schema_config_path)
        }
    }
    valid_config = {
        "system_name": "BDC"
    }
    
    app_config_file = configs_dir / "app_config.json"
    config_file = configs_dir / "config.json"
    
    app_config_file.write_text(json.dumps(valid_app_config))
    config_file.write_text(json.dumps(valid_config))
    
    return {
        "configs_dir": configs_dir,
        "app_config_file": app_config_file,
        "config_file": config_file,
        "valid_app_config": valid_app_config,
        "valid_config": valid_config
    }


# ==============================================================================
# CENÁRIOS DE TESTE T1.1.1
# ==============================================================================

def test_cenario_1_sucesso(setup_env):
    """Cenário 1: Configurações perfeitas passam na validação do schema."""
    ctx = load_context(setup_env["configs_dir"])
    assert ctx.app_config["env"] == "dev"
    assert ctx.config["system_name"] == "BDC"

def test_cenario_2_diretorio_inexistente(tmp_path):
    """Cenário 2: Diretório de configs passado não existe."""
    with pytest.raises(SystemExit) as e:
        load_context(tmp_path / "pasta_invalida")
    assert e.value.code == 1

def test_cenario_3_arquivo_config_ausente(setup_env):
    """Cenário 3: Faltando um dos arquivos base (config.json)."""
    setup_env["config_file"].unlink()
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1

def test_cenario_4_control_files_ausente(setup_env):
    """Cenário 4: app_config sem a chave control_files (quebra o boot do schema)."""
    bad_config = setup_env["valid_app_config"].copy()
    del bad_config["control_files"]
    setup_env["app_config_file"].write_text(json.dumps(bad_config))
    
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1

def test_cenario_5_schema_nao_encontrado_no_disco(setup_env):
    """Cenário 5: Os caminhos do schema no JSON apontam para lugar nenhum."""
    bad_config = setup_env["valid_app_config"].copy()
    bad_config["control_files"]["schema_app_config"] = "/caminho/falso/schema.json"
    setup_env["app_config_file"].write_text(json.dumps(bad_config))
    
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1

def test_cenario_6_schema_invalido_campo_ausente(setup_env):
    """Cenário 6: O JSON existe, mas falta um campo exigido pelo schema."""
    bad_config = setup_env["valid_app_config"].copy()
    del bad_config["env"] # O schema mock exige "env"
    setup_env["app_config_file"].write_text(json.dumps(bad_config))
    
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1

def test_cenario_7_schema_invalido_tipo_errado(setup_env):
    """Cenário 7: O JSON existe, o campo existe, mas o tipo de dado está errado."""
    bad_config = setup_env["valid_config"].copy()
    bad_config["system_name"] = 12345 # O schema mock exige string, não int
    setup_env["config_file"].write_text(json.dumps(bad_config))
    
    with pytest.raises(SystemExit) as e:
        load_context(setup_env["configs_dir"])
    assert e.value.code == 1
```


---
## src\tests\test_enquadramento.py
Linhas: 42
Classes: MockContext
Funções: test_t213_calculo_volume_enquadramento, path
```python
import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.enquadramento_service import calcular_enquadramento_consumidor

def test_t213_calculo_volume_enquadramento(tmp_path):
    """Valida se o sistema calcula corretamente o maior volume mensal e o corte de 5 MWm."""
    
    silver_dir = tmp_path / "SAIDAS" / "silver" / "denodo_contratos_padronizados"
    silver_dir.mkdir(parents=True)
    
    dados_mock = pd.DataFrame([
        {"CNPJ": "11111111000111", "CONTRATO": "C1", "COMPETENCIA": "202608", "VOLUME_MWM": 4.0, "STATUS": "Ativo"},
        {"CNPJ": "11111111000111", "CONTRATO": "C2", "COMPETENCIA": "202608", "VOLUME_MWM": 2.0, "STATUS": "Ativo"},
        {"CNPJ": "22222222000222", "CONTRATO": "C3", "COMPETENCIA": "202608", "VOLUME_MWM": 2.5, "STATUS": "Ativo"},
    ])
    
    competencia = "202608"
    dados_mock.to_parquet(silver_dir / f"contratos_correntes_{competencia}.parquet", index=False)
    
    class MockContext:
        def path(self, key):
            if key == "silver":
                return tmp_path / "SAIDAS" / "silver"
            if key == "relational_configs":
                return tmp_path / "SAIDAS" / "relational" / "configs"
            return tmp_path

    df_res = calcular_enquadramento_consumidor(competencia, MockContext())
    
    cons_a = df_res[df_res["CNPJ"] == "11111111000111"].iloc[0]
    cons_b = df_res[df_res["CNPJ"] == "22222222000222"].iloc[0]
    
    assert cons_a["VOLUME_ENQUADRAMENTO_MWM"] == 6.0
    assert bool(cons_a["POSSUI_PELO_MENOS_5_MWM"]) is True  # Conversão explícita para bool nativo
    
    assert cons_b["VOLUME_ENQUADRAMENTO_MWM"] == 2.5
    assert bool(cons_b["POSSUI_PELO_MENOS_5_MWM"]) is False
```


---
## src\tests\test_mtm_connector.py
Linhas: 46
Classes: -
Funções: test_t221_leitura_mtm_local
```python
import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.mtm_connector import fetch_mtm_consolidado

def test_t221_leitura_mtm_local(tmp_path):
    """Valida se o conector de MtM lê o arquivo CSV real, mapeia colunas e normaliza os dados."""
    
    # 1. Simula a pasta de entrada ENTRADAS/mtm
    mtm_dir = tmp_path / "mtm"
    mtm_dir.mkdir(parents=True)
    
    # 2. Cria um arquivo CSV de exemplo com o layout real fornecido
    csv_content = (
        "COD_CONTRATO;CONTRAPARTE;CNPJ;TIPO_CONTRATO;SUBMERCADO;FONTE;PORTFOLIO;DATA_FECHAMENTO;MES_SUPRIMENTO;ENERGIA_MWM;ENERGIA_MWH;PRECO_REAJUSTADO;PRECO_MERCADO;MTM_UNITARIA;MTM_TOTAL;TAXA_DESCONTO;MTM_VPL;DATA_AVALIACAO\n"
        "GERENCIAL 2024-00007552;COPEL COM - GERENCIAL;19125927000186;Compra;S;convencional;direcional;2026-04-14;2027-07-01;4,5;3348,0;155,02;286,41;131,38;439876,53;1,121572;392196,42;2026-08-10\n"
        "GERENCIAL 2024-00007553;OUTRA EMPRESA;123456780001;Venda;S;convencional;direcional;2026-04-14;2027-07-01;2,0;1000,0;100,0;200,0;50,0;-1000,0;1,0;-900,0;2026-08-10"
    )
    
    arquivo_csv = mtm_dir / "mtm_amostra_real.csv"
    arquivo_csv.write_text(csv_content, encoding="utf-8-sig")
    
    # 3. Executa a função do conector apontando para a pasta temporária
    df = fetch_mtm_consolidado(input_dir=mtm_dir)
    
    # 4. Validações Estruturais e de Regra de Negócio
    assert not df.empty, "O DataFrame do MtM não deveria estar vazio."
    
    colunas_esperadas = ["CNPJ", "CONTRATO", "DATA_BASE", "MTM_POSITIVO", "MTM_NEGATIVO", "NOTIONAL"]
    for col in colunas_esperadas:
        assert col in df.columns, f"A coluna obrigatória '{col}' está ausente."
        
    # Valida normalização estrita do CNPJ (14 dígitos, preservando zeros à esquerda)
    assert df.iloc[0]["CNPJ"] == "19125927000186"
    assert df.iloc[1]["CNPJ"] == "00123456780001", "Deveria ter preenchido os zeros à esquerda com zfill(14)."
    
    # Valida mapeamento do contrato
    assert df.iloc[0]["CONTRATO"] == "GERENCIAL 2024-00007552"
    
    # Valida tratamento de MTM Positivo (valores negativos na base original devem virar 0.0 no positivo puro)
    assert df.iloc[0]["MTM_POSITIVO"] == 439876.53
    assert df.iloc[1]["MTM_POSITIVO"] == 0.0, "Valores negativos no MTM_TOTAL devem ser isolados no MTM_POSITIVO."
```


---
## src\tests\test_receita_ingestion.py
Linhas: 133
Classes: MockContext, DummyResponse
Funções: _write_cnpj_list_file, test_consulta_brasilapi_sucesso, test_cache_local_receita, test_geracao_alerta_cad001, __init__, path, fake_get, fake_get, __init__, json
```python
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.receita_connector import consultar_cnpj_brasilapi, fetch_receita_data_batch
from services.receita_ingestion_service import ingest_receita_data


class MockContext:
    def __init__(self, root: Path):
        self.root = root

    def path(self, key: str) -> Path:
        mapping = {
            "entradas": self.root / "ENTRADAS",
            "bronze": self.root / "SAIDAS" / "bronze",
            "silver": self.root / "SAIDAS" / "silver",
            "log_runner": self.root / "LOGS" / "runner",
        }
        return mapping[key]


def _write_cnpj_list_file(base_dir: Path) -> Path:
    receita_dir = base_dir / "receita"
    receita_dir.mkdir(parents=True, exist_ok=True)
    csv_path = receita_dir / "lista_cnpjs.csv"
    pd.DataFrame({"CNPJ": ["12.345.678/0001-99"]}).to_csv(csv_path, index=False)
    return csv_path


def test_consulta_brasilapi_sucesso(monkeypatch):
    class DummyResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {
                "cnpj": "12345678000199",
                "data_abertura": "2020-01-15",
                "cnae_fiscal": "6201500",
                "natureza_juridica": "213-5 - SOCIEDADE EMPRESARIA LIMITADA",
                "descricao_situacao_cadastral": "ATIVA",
                "nome_fantasia": "Empresa Teste",
            }

    def fake_get(*args, **kwargs):
        return DummyResponse()

    monkeypatch.setattr("services.receita_connector.requests.get", fake_get)

    resultado = consultar_cnpj_brasilapi("12.345.678/0001-99")

    assert resultado["CNPJ"] == "12345678000199"
    assert resultado["SITUACAO_CADASTRAL"] == "ATIVA"
    assert resultado["DATA_ABERTURA"] == "2020-01-15"
    assert resultado["CNAE_PRINCIPAL"] == "6201500"
    assert resultado["NATUREZA_JURIDICA"] == "213-5 - SOCIEDADE EMPRESARIA LIMITADA"
    assert resultado["DATA_CONSULTA"]


def test_cache_local_receita(tmp_path, monkeypatch):
    entradas = tmp_path / "ENTRADAS" / "receita" / "cache"
    entradas.mkdir(parents=True, exist_ok=True)
    cache_path = entradas / "receita_cache.json"
    cache_path.write_text(
        json.dumps(
            {
                "12345678000199": {
                    "CNPJ": "12345678000199",
                    "SITUACAO_CADASTRAL": "ATIVA",
                    "DATA_ABERTURA": "2023-01-01",
                    "CNAE_PRINCIPAL": "6201500",
                    "NATUREZA_JURIDICA": "213-5",
                    "DATA_CONSULTA": "2026-08-11T12:00:00",
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    context = MockContext(tmp_path)
    called = {"value": False}

    def fake_get(*args, **kwargs):
        called["value"] = True
        raise AssertionError("Requisição HTTP não deveria ocorrer quando o CNPJ já está em cache valido")

    monkeypatch.setattr("services.receita_connector.requests.get", fake_get)

    df = fetch_receita_data_batch(["12.345.678/0001-99"], context)

    assert called["value"] is False
    assert len(df) == 1
    assert df.iloc[0]["CNPJ"] == "12345678000199"


def test_geracao_alerta_cad001(tmp_path, monkeypatch):
    context = MockContext(tmp_path)
    _write_cnpj_list_file(context.path("entradas"))

    df = pd.DataFrame(
        [
            {
                "CNPJ": "12345678000199",
                "SITUACAO_CADASTRAL": "BAIXADA",
                "DATA_ABERTURA": "2020-01-15",
                "CNAE_PRINCIPAL": "6201500",
                "NATUREZA_JURIDICA": "213-5 - SOCIEDADE EMPRESARIA LIMITADA",
                "DATA_CONSULTA": "2026-08-11T10:00:00",
            }
        ]
    )

    monkeypatch.setattr("services.receita_ingestion_service.fetch_receita_data_batch", lambda cnpjs, context: df)

    resultado = ingest_receita_data(context)

    assert resultado["status"] == "SUCESSO"
    assert resultado["alertas_gerados_cad001"] == 1

    alertas_dir = context.path("silver") / "alertas_credito"
    arquivos = sorted(alertas_dir.glob("*.csv"))
    assert arquivos, "Arquivo de alertas não foi persistido."

    df_alertas = pd.read_csv(arquivos[0])
    assert df_alertas.iloc[0]["CODIGO"] == "CAD_001"
    assert df_alertas.iloc[0]["CNPJ"] == "12345678000199"

```


---
## src\tests\test_salesforce_ingestion.py
Linhas: 107
Classes: MockContext
Funções: mock_context, criar_mock_excel_salesforce, test_t232_ingestao_salesforce_sucesso, test_t232_ingestao_salesforce_arquivo_inexistente, path
```python
import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.salesforce_ingestion_service import ingest_salesforce_data


@pytest.fixture
def mock_context(tmp_path):
    """Fixture que cria o contexto de diretórios temporários para o teste."""
    class MockContext:
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


def criar_mock_excel_salesforce(diretorio_entradas: Path):
    """Cria um arquivo Excel simulando a saída do Power Query do Salesforce."""
    dir_sf = diretorio_entradas / "salesforce"
    dir_sf.mkdir(parents=True, exist_ok=True)
    
    arquivo_sf = dir_sf / "salesforce.xlsx"
    
    # 1. Conta (Com registros duplicados e CNPJ com máscara)
    df_conta = pd.DataFrame([
        {"Id": "A1", "Name": "Empresa 1 Antiga", "CNPJ__c": "05.276.991/0014-78"},
        {"Id": "A1", "Name": "Empresa 1 Atualizada", "CNPJ__c": "05.276.991/0014-78"}, # Deve sobrescrever a anterior
        {"Id": "A2", "Name": "Empresa 2", "CNPJ__c": "11111111000199"}
    ])
    
    # 2. Cotação (C1 ligada na A1, C2 ligada em conta inexistente)
    df_cotacao = pd.DataFrame([
        {"Id": "Q1", "AccountId": "A1", "Cotacao_Aprovada__c": "Sim"},
        {"Id": "Q2", "AccountId": "A99", "Cotacao_Aprovada__c": "Nao"} # Conta órfã
    ])
    
    # 3. Chamado
    df_chamado = pd.DataFrame([
        {"Id": "C1", "AccountId": "A2", "Risk3_Score__c": "85"}
    ])
    
    # 4. Contrato
    df_contrato = pd.DataFrame([
        {"Id": "CT1", "AccountId": "A1", "Status": "Ativo"}
    ])
    
    # Escreve todas as abas no Excel
    with pd.ExcelWriter(arquivo_sf) as writer:
        df_conta.to_excel(writer, sheet_name="Conta", index=False)
        df_cotacao.to_excel(writer, sheet_name="Cotação", index=False)
        df_chamado.to_excel(writer, sheet_name="Chamado", index=False)
        df_contrato.to_excel(writer, sheet_name="Contrato", index=False)


def test_t232_ingestao_salesforce_sucesso(mock_context):
    """Garante a leitura, normalização de CNPJ, deduplicação e enriquecimento das tabelas."""
    # Prepara massa de dados
    criar_mock_excel_salesforce(mock_context.path("entradas"))
    
    # Executa ingestão
    res = ingest_salesforce_data(mock_context)
    
    assert res["status"] == "SUCESSO"
    assert res["linhas_account"] == 2  # Deduplicou 3 linhas para 2 únicas
    assert res["linhas_cotacao"] == 2
    
    # Validações da Camada Silver
    silver_dir = mock_context.path("silver") / "salesforce_silver"
    
    # Validação da Account (Conta)
    df_silver_account = pd.read_parquet(silver_dir / "account" / "salesforce_account.parquet")
    assert len(df_silver_account) == 2
    
    empresa_1 = df_silver_account[df_silver_account["Id"] == "A1"].iloc[0]
    assert empresa_1["Name"] == "Empresa 1 Atualizada", "Deduplicação 'keep=last' falhou."
    assert empresa_1["CNPJ"] == "05276991001478", "Remoção da máscara do CNPJ falhou."
    
    # Validação da Cotação (Enriquecimento de CNPJ)
    df_silver_cotacao = pd.read_parquet(silver_dir / "cotacao" / "salesforce_cotacao.parquet")
    
    cotacao_valida = df_silver_cotacao[df_silver_cotacao["Id"] == "Q1"].iloc[0]
    assert cotacao_valida["CNPJ"] == "05276991001478", "Enriquecimento de CNPJ na Cotação falhou."
    
    cotacao_orfa = df_silver_cotacao[df_silver_cotacao["Id"] == "Q2"].iloc[0]
    assert cotacao_orfa["CNPJ"] == "00000000000000", "Fallback de CNPJ para contas órfãs falhou."


def test_t232_ingestao_salesforce_arquivo_inexistente(mock_context):
    """Garante que a ingestão não quebra se o Power Query não gerar o arquivo no dia."""
    
    # Executa ingestão SEM criar o arquivo Excel antes
    res = ingest_salesforce_data(mock_context)
    
    assert res["status"] == "SEM_DADOS"
```
