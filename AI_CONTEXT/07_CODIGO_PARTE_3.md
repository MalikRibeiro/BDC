# CÓDIGO PARTE 3


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
Funções: resolve_configs_dir, aplicativo_bootstrap
```python
import os
from pathlib import Path
from typing import Optional, Union

from src.app.context import AppContext, carregar_contexto
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


def aplicativo_bootstrap(configs_dir: Optional[Union[str, Path]] = None) -> AppContext:
    """
    Realiza o bootstrap da aplicação e carrega o AppContext.

    Args:
        configs_dir: Caminho explícito ou opcional para o diretório de configurações.

    Returns:
        AppContext: Contexto inicializado da aplicação.
    """
    resolved_dir = resolve_configs_dir(configs_dir)
    return carregar_contexto(resolved_dir)
```


---
## src\app\comercializadoras\orquestrador.py
Linhas: 768
Classes: -
Funções: disco_cheio_erro, criar_run_id, criar_nome_arquivo, resolver_subpasta_bronze, mover_para_rejeitados, mover_para_processados, criar_info_pd, criar_fila_processamento, processar_arquivo_individual, process_fichas_comercializadoras
```python
"""Serviço principal refatorado do pipeline de fichas de comercializadoras."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.context import AppContext
from common.excel import  abrir_pasta, fechar_pasta
from common.hashing import arquivo_hash
from common.json import ler_json
from control.logger import obter_logger
from silver.normalizadores import padronizar_cnpj
from common.paths import sanitizar_nome_da_pasta

from control.layout_catalog import carregar_layouts_comercializadoras
from control.carregador_de_mapeamento import mapeamento_de_carga_fichas_comercializadoras
from domain.contrapartes.segmentacao import definir_segmento_metodologico
from domain.credito.pd_motor import calcular_pd_ajustada
from domain.auditoria.servico_auditoria import registrar_documento, registrar_linhagem_campos
from common.servico_desduplicacao import (
    tem_chave_de_negocio_duplicada,
    tem_hash_duplicado,
    virar_chave_de_negocio_no_historico,
)
from domain.fichas.validador import validar_registro
from silver.documentos_classificados import criar_documento_classificado
from silver.normalizador_de_tipo_de_campo import normalizar_registro
from staging.descoberta import detectar_arquivos_excel_pendentes
from staging.staging_arquivo import copiar_para_staging
from storage.bronze_arquivo import publicar_arquivo_bruto
from storage.operacao_arquivo import mover_arquivo_com_tentativa_adicional
from storage.armazenamento_manifest import (
    anexar_registro_de_manifesto,
    historico_de_ingestao_de_carga,
)
from storage.escrever_dados import (
    mesclar_conjunto_de_dados_prata_por_chave_de_negocio,
    escrever_conjunto_de_dados_silver,
)
from storage.estado_armazenamento import DocumentManifest

def disco_cheio_erro(exc: Exception) -> bool:
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


def criar_run_id(context: AppContext) -> str:
    """Monta o identificador textual da execução."""
    prefix = context.naming.get("run_id_prefix", "BDC")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"


def criar_nome_arquivo(
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


def resolver_subpasta_bronze(
    cnpj: str | None,
    sigla: str | None,
) -> str:
    """Resolve a subpasta da bronze organizada por CNPJ e sigla."""
    if not cnpj:
        raise ValueError("Não é possível publicar em bronze sem CNPJ válido.")
    safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
    safe_sigla = sanitizar_nome_da_pasta(sigla or "")
    if safe_sigla:
        return f"{safe_cnpj}__{safe_sigla}"

    return safe_cnpj


def mover_para_rejeitados(
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
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para rejeitados: {exc}")
        logger.exception("Falha ao mover %s para rejeitados.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
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


def mover_para_processados(
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
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para processadas: {exc}")
        logger.exception("Falha ao mover %s para processadas.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
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


def criar_info_pd(
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
        
    except Exception as exc:
        logger.error("Falha bloqueante no motor de crédito para %s. Motivo: %s", source_file.name, exc)
        manifest.avisos.append(f"PD ajustada não calculada: {exc}")
        raise ValueError(f"Insumo obrigatório ausente ou falha no motor: {exc}")


def criar_fila_processamento(
    context: AppContext,
) -> list[tuple[Path, str, Path, Path]]:
    """Monta a fila de processamento normal e reprocessamento."""
    normal_files = detectar_arquivos_excel_pendentes(
        context.path("input_fichas_comercializadoras_pendentes")
    )
    reprocess_files = detectar_arquivos_excel_pendentes(
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


def processar_arquivo_individual(
    source_file: Path,
    load_mode: str,
    processed_dir: Path,
    rejected_dir: Path,
    context: AppContext,
    layouts: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_cpura_config: dict[str, Any],
    score_cpura_config: dict[str, Any],
    pd_transform_rules: dict[str, Any],
    history: list[dict[str, Any]],
    ingestion_log_path: Path,
    logger: Any,
    run_id: str,
    master_catalog: dict[str, Any],
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

        manifest.hash_arquivo = arquivo_hash(source_file)

        # 1. Checagem de Hash em Carga Incremental
        if load_mode == "incremental" and tem_hash_duplicado(
            history, manifest.hash_arquivo
        ):
            manifest.status_extracao = "ERRO_DUPLICIDADE_HASH"
            manifest.erros.append("Hash já processado anteriormente.")
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        # 2. Copia para Staging
        staging_dir = context.path("staging_fichas_comercializadoras")
        staging_name = criar_nome_arquivo(
            original_name=source_file.name,
            versao_ficha=None,
            cnpj=None,
            data_df=None,
            hash_value=manifest.hash_arquivo,
        )
        staging_file = copiar_para_staging(source_file, staging_dir, staging_name)
        manifest.caminho_staging = str(staging_file)

        # 3 & 4. Extração Competitiva (Tournament Extraction)
        workbook = abrir_pasta(staging_file)
        from domain.fichas.extrator import extrair_registro_do_vencedor
        raw_record, metadata_list, winner_layout = extrair_registro_do_vencedor(workbook, layouts, master_catalog)
        
        if winner_layout == "DOC_001_ESTRUTURA_INCOMPATIVEL":
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_LAYOUT"
            manifest.erros.append("DOC_001_ESTRUTURA_INCOMPATIVEL: Nenhuma aba compativel com o layout esperada foi encontrada.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None
            
        score_campeao = raw_record.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        
        # Validar aprovação (GATES e Score Ponderado)
        if raw_record.get("_FALHA_GATE_CRITICO"):
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_DADOS_CRITICOS_AUSENTES"
            manifest.erros.append("Ficha falhou nos GATES de segurança (Campos obrigatórios ausentes).")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None
            
        if not winner_layout or winner_layout == "NENHUM" or score_campeao < 40.0:
            manifest.status_classificacao = "REJEITADO"
            manifest.status_extracao = "ERRO_INTEGRIDADE"
            manifest.erros.append(f"Score insuficiente: {score_campeao}%. Minimo exigido: 40.0%.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        manifest.versao_ficha = winner_layout
        manifest.status_classificacao = "CLASSIFICADO"
        
        logger.info(
            "Extração competitiva: Vencedor %s identificado para %s.",
            winner_layout,
            source_file.name,
        )

        classification = type("MockClassification", (), {"versao_ficha": winner_layout})()
        
        if control_dir and metadata_list:
            registrar_linhagem_campos(
                manifest.documento_id,
                manifest.run_id,
                metadata_list,
                control_dir
            )
            
        slug = "field_types_fichas_comercializadoras"
        normalized = normalizar_registro(raw_record, context, slug, logger)
        
        # 4b. Normalização Semântica de Domínio (Negócio)
        from common.domain_normalizer import aplicar_normalizacao_de_dominio
        normalized = aplicar_normalizacao_de_dominio(normalized, context, logger)
        
        # 4c. Derivação Financeira (Calcula DERIVED fields caso não existam)
        from domain.fichas.derivador_financeiro import calcular_indicadores_derivados
        normalized = calcular_indicadores_derivados(normalized)

        manifest.cnpj_extraido = normalized.get("CNPJ")

        manifest.data_demonstracao_financeira = normalized.get(
            "DATA_DEMONSTRACAO_FINANCEIRA"
        )
        manifest.data_calculo = normalized.get("DATA_CALCULO")

        # 5. Validação Técnica (GATES e Sanity Checks)
        errors, warnings = validar_registro(
            record=normalized,
            master_catalog=master_catalog,
            logger=logger
        )
        
        integridade = normalized.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        
        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO_GATES"
            
        manifest.erros.extend(errors)
        manifest.avisos.extend(warnings)
        
        if integridade < 40.0:
            manifest.status_extracao = "ERRO_INTEGRIDADE"
            manifest.erros.append(f"Integridade baixa: {integridade}% (mínimo 40%). Ficha rejeitada.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if not manifest.cnpj_extraido:
            manifest.status_extracao = "ERRO_SEM_CNPJ"
            manifest.erros.append("Ficha sem CNPJ válido.")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if not padronizar_cnpj(manifest.cnpj_extraido):
            manifest.status_extracao = "ERRO_CNPJ_INVALIDO"
            manifest.erros.append(f"CNPJ inválido: {manifest.cnpj_extraido}")
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        if errors:
            manifest.status_extracao = "ERRO_VALIDACAO_GATES"
            fechar_pasta(workbook)
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
            return None

        # 6. Checagem de Duplicidade de Negócio e Versionamento
        duplicate_business = tem_chave_de_negocio_duplicada(
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

        fechar_pasta(workbook)
        workbook = None

        # 7. Regras de Negócio de Crédito (PD / Scoring)
        try:
            pd_info = criar_info_pd(
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
        except ValueError as pd_error:
            manifest.status_extracao = "ERRO_MOTOR_CREDITO"
            manifest.erros.append(str(pd_error))
            fechar_pasta(workbook)
            mover_para_rejeitados(source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir)
            return None

        # 8. Verificação de Caminhos e Publicação Bronze
        bronze_root_dir = context.path("bronze_fichas_comercializadoras_raw")
        bronze_name = criar_nome_arquivo(
            original_name=source_file.name,
            versao_ficha=manifest.versao_ficha,
            cnpj=manifest.cnpj_extraido,
            data_df=manifest.data_demonstracao_financeira,
            hash_value=manifest.hash_arquivo,
        )

        bronze_subfolder = resolver_subpasta_bronze(
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

        bronze_staging = copiar_para_staging(staging_file, staging_dir, bronze_name)
        bronze_file = publicar_arquivo_bruto(
            source_file=bronze_staging,
            bronze_root_dir=bronze_root_dir / bronze_subfolder,
        )
        manifest.caminho_bronze = str(bronze_file)
        manifest.status_extracao = "SUCESSO"

        mover_para_processados(
            source_file, processed_dir, manifest, ingestion_log_path, logger, control_dir
        )
        virar_chave_de_negocio_no_historico(history, manifest.to_dict())

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
            "METADADOS_EXTRACAO": metadata_list,
        }

        classified_document = criar_documento_classificado(
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
            fechar_pasta(workbook)
        manifest.status_extracao = "ERRO_PROCESSAMENTO"
        manifest.erros.append(str(exc))

        if disco_cheio_erro(exc):
            logger.exception(
                "Execução interrompida por falta de espaço em disco ao processar %s.",
                source_file.name,
            )
            raise

        try:
            mover_para_rejeitados(
                source_file, rejected_dir, manifest, ingestion_log_path, logger, control_dir
            )
        except Exception as move_exc:
            if disco_cheio_erro(move_exc):
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
    run_id = criar_run_id(context)

    log_file = (
        context.path("log_runner") / f"{run_id}__fichas_comercializadoras.log"
    )
    logger = obter_logger("bdc.comercializadoras", log_file)

    _ = mapeamento_de_carga_fichas_comercializadoras(context, logger)

    layouts = carregar_layouts_comercializadoras(context, logger)
    
    catalog_path = Path("ENTRADAS/control/quality/master_catalog_comercializadoras.json")
    logger.info(f"Carregando Master Catalog definitivo: {catalog_path}")
    master_catalog = ler_json(catalog_path)

    try:
        pd_faixas = ler_json(context.control_file("pd_faixas"))
        logger.info("Faixas de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_faixas.")
        raise

    try:
        pd_cpura_config = ler_json(context.control_file("pd_cpura_config"))
        logger.info("Configuração de CPURA carregada com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_cpura_config.")
        raise

    try:
        score_cpura_config = ler_json(
            context.control_file("score_cpura_config")
        )
        logger.info("Configuração de score de CPURA carregada com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar score_cpura_config.")
        raise

    try:
        pd_transform_rules = ler_json(
            context.control_file("pd_transform_rules")
        )
        logger.info("Regras de transformação de PD carregadas com sucesso.")
    except Exception:
        logger.exception("Falha ao carregar pd_transform_rules.")
        raise

    ingestion_log_path = (
        context.path("bronze_ingestion_log")
        / "fichas_comercializadoras_ingestion.jsonl"
    )
    history = historico_de_ingestao_de_carga(ingestion_log_path)

    silver_records: list[dict[str, Any]] = []
    classified_documents: list[dict[str, Any]] = []

    queue = criar_fila_processamento(context)

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
        result = processar_arquivo_individual(
            source_file=source_file,
            load_mode=load_mode,
            processed_dir=processed_dir,
            rejected_dir=rejected_dir,
            context=context,
            layouts=layouts,
            pd_faixas=pd_faixas,
            pd_cpura_config=pd_cpura_config,
            score_cpura_config=score_cpura_config,
            pd_transform_rules=pd_transform_rules,
            history=history,
            ingestion_log_path=ingestion_log_path,
            logger=logger,
            run_id=run_id,
            master_catalog=master_catalog,
            control_dir=context.path("relational_control") if hasattr(context, "path") and context.path("relational_control") else Path("SAIDAS/relational/control"),
        )

        if result:
            silver_records.append(result["silver_record"])
            classified_documents.append(result["classified_document"])

    silver_output_dir = context.path("silver_fichas_comercializadoras_extraidas")
    docs_output_dir = context.path("silver_documentos_classificados")

    if silver_records:
        mesclar_conjunto_de_dados_prata_por_chave_de_negocio(
            records=silver_records,
            output_dir=silver_output_dir,
            filename="fichas_comercializadoras_extraidas.csv",
            business_keys=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA"],
        )

    if classified_documents:
        escrever_conjunto_de_dados_silver(
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
## src\control\field_types.py
Linhas: 50
Classes: FieldTypeConfig
Funções: obter_config_tipo_campo
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
        "PROBABILIDADE_DEFAULT", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "FCO", "ROA", "ROE",
        "ROL", "LUCRO_BRUTO", "LAJIR", "LAIR", "LUCRO_LIQUIDO", "SCORE_BUREAU", "QUANTIDADE_RESTRITIVOS",
        "PL_CONTROLADOR", "PERCENTUAL_CONTROLADOR", "CAPITAL_CIRCULANTE_LIQUIDO", "NECESSIDADE_CAPITAL_GIRO",
        "INDICE_AUTO_FINANCIAMENTO", "LIQUIDEZ_SECA", "INDICE_SOLVENCIA_GERAL", "MARGEM_LIQUIDA",
        "SCORE_QUANTITATIVO", "SCORE_QUALITATIVO",
        "SCORE_PD", "SCORE_FCO_ROL", "SCORE_ROA", "SCORE_ROE",
        "LUCRO_LIQUIDO_SOBRE_ROL"
    ],
    text_fields=[
        "EMPRESA", "CEP", "ENDERECO", "AUDITOR", "AGENCIA", "NOTA_CREDITO", "NOTA_BOARD",
        "NOTA_BUREAU", "RATING_COPEL", "CONTROLADOR", "NOTA_CREDITO_CONTROLADOR", "AGENCIA_CONTROLADOR",
        "SITUACAO_CADASTRAL", "NATUREZA_JURIDICA", "CNAE", "NOTA_AUDITORIA"
    ],
    cnpj_fields=[
        "CNPJ", "CNPJ_CONTROLADOR"
    ]
)

# Catálogo em memória que substitui a busca no disco
FIELD_TYPES_CATALOG = {
    "field_types_fichas_consumidores": CONSUMIDORES_FIELD_TYPES,
}

def obter_config_tipo_campo(slug: str) -> Optional[FieldTypeConfig]:
    """Retorna a configuração de tipagem em memória correspondente ao slug."""
    return FIELD_TYPES_CATALOG.get(slug)
```


---
## src\control\quality_loader.py
Linhas: 71
Classes: -
Funções: _carregar_e_validar_regras_de_qualidade, carregar_regras_de_qualidade_de_dados_comercializadoras, carregar_regras_de_qualidade_de_dados_consumidores
```python
"""Carregamento e validação estrita das regras de qualidade da entidade.

feat(T1.1.2): Integra validação contra JSON Schema (mesmo padrão de mapping_loader.py).
Regras malformadas geram erro descritivo antes do processamento de qualquer ficha.
Ref: §5.2, §5.3 do Planejamento Funcional.
"""
from __future__ import annotations

from typing import Any
from pathlib import Path

from app.context import AppContext
from common.json import ler_json
from common.validador import validar_esquema_json


def _carregar_e_validar_regras_de_qualidade(
    rules_path: Path,
    schema_path: Path,
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

        content = ler_json(rules_path)
        schema = ler_json(schema_path)

        # Validação Estrita (Fail-Fast)
        validar_esquema_json(instance=content, schema=schema, label=descricao)

        if not isinstance(content, dict):
            raise ValueError(f"O {descricao} deve ser um objeto JSON.")

        logger.info("%s carregado e validado com sucesso.", descricao)

        return content

    except Exception:
        logger.exception("Falha crítica ao carregar e validar %s", descricao)
        raise


def carregar_regras_de_qualidade_de_dados_comercializadoras(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega as regras de qualidade das fichas de comercializadoras usando o novo master_catalog."""
    master_catalog_path = context.control_file("schema_data_quality_rules").parent / "master_catalog_comercializadoras.json"
    logger.info("Lendo master catalog temporário: %s", master_catalog_path)
    return ler_json(master_catalog_path)


def carregar_regras_de_qualidade_de_dados_consumidores(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega e valida as regras de qualidade das fichas de consumidores."""
    return _carregar_e_validar_regras_de_qualidade(
        rules_path=context.control_file("data_quality_rules_fichas_consumidores"),
        schema_path=context.control_file("schema_data_quality_rules"),
        descricao="Regras de Qualidade de Consumidores",
        logger=logger,
    )

```


---
## src\domain\cadastro\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\cadastro\servico_bureau.py
Linhas: 69
Classes: -
Funções: inserir_dados_bureau
```python
"""Serviço de Ingestão e Persistência do Bureau RISK3."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from services.connectors.risk3_connector import buscar_bureau_risk3
from storage.escrever_dados import escrever_conjunto_de_dados_silver

LOGGER = logging.getLogger(__name__)

def inserir_dados_bureau(context: AppContext) -> dict[str, Any]:
    run_id = f"BUR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.bureau")

    try:
        # 1. Busca Consumidores enquadrados no motor de volume
        path_enq = context.path("relational_configs")
        arquivos = list(path_enq.glob("enquadramento_consumidores_*.parquet"))
        if not arquivos:
            logger.warning("Nenhum enquadramento encontrado para guiar o Bureau.")
            return {"run_id": run_id, "status": "SEM_DADOS_ENQUADRAMENTO"}
            
        df_enq = pd.read_parquet(max(arquivos, key=lambda f: f.stat().st_mtime))
        
        # 2. Filtra os clientes que exigem Bureau (< 5 MWm)
        df_le5 = df_enq[df_enq["POSSUI_PELO_MENOS_5_MWM"] == False]
        cnpjs_alvo = df_le5["CNPJ"].dropna().unique().tolist()
        
        if not cnpjs_alvo:
            return {"run_id": run_id, "status": "NENHUM_CLIENTE_ELEGIVEL"}

        # 3. Consulta a API RISK3
        df_bureau = buscar_bureau_risk3(cnpjs_alvo, context)

        if df_bureau.empty:
            return {"run_id": run_id, "status": "SEM_RETORNO_API"}

        # 4. Salva Snapshot na Bronze
        bronze_dir = context.path("bronze") / "snapshots_fontes" / "bureau"
        bronze_dir.mkdir(parents=True, exist_ok=True)
        df_bureau.to_parquet(bronze_dir / f"raw_bureau_{run_id}.parquet", index=False)

        # 5. Salva Fato na Silver (Para consumo pela Camada Gold)
        df_silver = df_bureau[df_bureau["STATUS"] == "SUCESSO"].copy()
        
        if df_silver.empty:
            return {"run_id": run_id, "status": "FALHA_OU_BLOQUEIO_DE_REDE"}
            
        df_silver["RUN_ID"] = run_id
        df_silver["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
        
        silver_dir = context.path("silver") / "fato_bureau_silver"
        escrever_conjunto_de_dados_silver(
            records=df_silver.to_dict(orient="records"), 
            output_dir=silver_dir, 
            filename="fato_bureau_silver"
        )

        logger.info("Ingestão do Bureau concluída. %d registros na Silver.", len(df_silver))
        return {"run_id": run_id, "status": "SUCESSO", "linhas": len(df_silver)}

    except Exception as e:
        logger.exception("Falha crítica na ingestão do Bureau RISK3.")
        raise
```


---
## src\domain\carga_manual\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\carga_manual\servico_carga_manual.py
Linhas: 75
Classes: -
Funções: inserir_dados_carga_manual
```python
"""Serviço de Carga Manual e Eventos de Negócio."""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from pathlib import Path

from app.context import AppContext
from common.validador import validar_esquema_json
from common.json import ler_json
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def inserir_dados_carga_manual(context: AppContext) -> dict[str, Any]:
    run_id = f"MAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.governanca.carga_manual")
    
    input_dir = context.path("entradas") / "atualizacoes_manuais" / "pendentes"
    input_dir.mkdir(parents=True, exist_ok=True)

    arquivos = list(input_dir.glob("*.csv")) + list(input_dir.glob("*.xlsx"))
    if not arquivos:
        return {"run_id": run_id, "processados": 0, "status": "SEM_DADOS"}

    schema_path = context.path("control_schemas") / "schema_carga_manual.json"
    schema = ler_json(schema_path) if schema_path.exists() else None

    processados = []
    agora = datetime.now().isoformat(timespec="seconds")

    for arquivo in arquivos:
        try:
            if arquivo.suffix == ".csv":
                df = pd.read_csv(arquivo, sep=";", dtype=str)
            else:
                df = pd.read_excel(arquivo, dtype=str)

            registros = df.to_dict(orient="records")

            for idx, reg in enumerate(registros):
                if schema:
                    try:
                        validar_esquema_json(reg, schema, f"Registro [{idx}] do arquivo {arquivo.name}")
                    except Exception as exc:
                        logger.warning("Registro %s inválido: %s. Ignorando.", idx, exc)
                        continue

                novo_reg = reg.copy()
                novo_reg["DATA_REGISTRO_SISTEMA"] = agora
                novo_reg["RUN_ID"] = run_id
                processados.append(novo_reg)

            # Move para aprovadas
            target_dir = context.path("entradas") / "atualizacoes_manuais" / "aprovadas"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.rename(target_dir / arquivo.name)
            
        except Exception as e:
            logger.error("Erro ao processar arquivo %s: %s", arquivo.name, e)
            target_dir = context.path("entradas") / "atualizacoes_manuais" / "rejeitadas"
            target_dir.mkdir(parents=True, exist_ok=True)
            arquivo.rename(target_dir / arquivo.name)

    if processados:
        silver_dir = context.path("silver") / "governanca_carga_manual"
        df_manual = pd.DataFrame(processados)
        escrever_conjunto_de_dados_silver(
            records=df_manual.to_dict(orient="records"),
            output_dir=silver_dir,
            filename=f"eventos_manuais_{run_id}"
        )

    logger.info("Carga manual concluída. %d eventos registrados.", len(processados))
    return {"run_id": run_id, "eventos_processados": len(processados), "status": "SUCESSO"}
```


---
## src\domain\contrapartes\servico_enquadramento.py
Linhas: 173
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
    simultâneo por raiz de CNPJ (Matriz + Filiais) e retorna a base consolidada
    de enquadramento propagada para todos os CNPJs completos.
    """
    silver_dir = context.path("silver") / "denodo_contratos_padronizados"
    parquet_path = silver_dir / f"contratos_correntes_{competencia_base}.parquet"

    if not parquet_path.exists():
        raise FileNotFoundError(
            f"Base Silver de contratos do Denodo não encontrada para a competência "
            f"{competencia_base} em: {parquet_path}. "
            "Execute a ingestão (T2.1.2) primeiro."
        )

    df_contratos = pd.read_parquet(parquet_path)

    if df_contratos.empty:
        return pd.DataFrame(
            columns=[
                "CNPJ",
                "VOLUME_ENQUADRAMENTO_MWM",
                "POSSUI_PELO_MENOS_5_MWM",
            ]
        )

    # 1. Filtra apenas contratos ativos/válidos se houver coluna de status
    if "STATUS" in df_contratos.columns:
        # Padroniza para capturar variações como:
        # 'Ativo', 'ATIVO', 'Ativo/Fechado', etc.
        df_contratos["STATUS_UP"] = (
            df_contratos["STATUS"]
            .astype(str)
            .str.upper()
        )

        df_ativos = df_contratos[
            df_contratos["STATUS_UP"].str.contains("ATIVO", na=False)
        ].copy()
    else:
        df_ativos = df_contratos.copy()

    if df_ativos.empty:
        return pd.DataFrame(
            columns=[
                "CNPJ",
                "VOLUME_ENQUADRAMENTO_MWM",
                "POSSUI_PELO_MENOS_5_MWM",
            ]
        )

    # 2. Cria/valida a raiz do CNPJ para agregar Matriz e Filiais.
    # Prefere a coluna CNPJ_RAIZ já vinda padronizada da Silver (8 dígitos garantidos).
    # Caso não exista (bases legadas), recalcula a partir do CNPJ de 14 dígitos.
    if "CNPJ_RAIZ" not in df_ativos.columns:
        df_ativos["CNPJ_RAIZ"] = (
            df_ativos["CNPJ"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .str[:8]
        )

    # Resolução case-insensitive das colunas de competência (ANO/ano, MES/mes).
    # A Silver do Denodo pode entregar em maiúsculas ou minúsculas dependendo
    # da versão da ingestão.
    col_ano = next((c for c in df_ativos.columns if c.upper() == "ANO"), None)
    col_mes = next((c for c in df_ativos.columns if c.upper() == "MES"), None)

    # Resolução case-insensitive da coluna de volume
    col_vol = next(
        (c for c in df_ativos.columns if c.upper() in {"VOLUME_CONTRATADO_MENSAL_MWM", "VOLUME_MWM"}),
        None,
    )
    if col_vol is None:
        raise KeyError(
            "Coluna de volume (VOLUME_CONTRATADO_MENSAL_MWM ou VOLUME_MWM) "
            "não encontrada na base de contratos."
        )
    if col_vol != "VOLUME_CONTRATADO_MENSAL_MWM":
        df_ativos = df_ativos.rename(columns={col_vol: "VOLUME_CONTRATADO_MENSAL_MWM"})

    # Garante competência: se não existir como coluna, monta a partir de ANO+MES
    if "COMPETENCIA" not in df_ativos.columns and col_ano and col_mes:
        df_ativos["COMPETENCIA"] = (
            df_ativos[col_ano].astype(str).str.replace(r"\.0$", "", regex=True)
            + df_ativos[col_mes].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(2)
        )

    # 3. Agrupa por CNPJ_RAIZ e Competência para somar volumes
    # simultâneos de Matriz + Filiais do mesmo grupo.
    df_mensal = (
        df_ativos.groupby(
            ["CNPJ_RAIZ", "COMPETENCIA"],
            as_index=False,
        )["VOLUME_CONTRATADO_MENSAL_MWM"]
        .sum()
        .rename(
            columns={
                "VOLUME_CONTRATADO_MENSAL_MWM": "VOLUME_CONSOLIDADO_MENSAL"
            }
        )
    )

    # 4. Regra de Negócio:
    # O volume de enquadramento do Grupo é o MAIOR volume mensal consolidado.
    df_enq_raiz = (
        df_mensal.groupby(
            "CNPJ_RAIZ",
            as_index=False,
        )["VOLUME_CONSOLIDADO_MENSAL"]
        .max()
        .rename(
            columns={
                "VOLUME_CONSOLIDADO_MENSAL": "VOLUME_ENQUADRAMENTO_MWM"
            }
        )
    )

    # 5. Deriva o indicador booleano de corte.
    # Parametrizado em 5.0 MWm conforme Planejamento §6.2.
    LIMIAR_MWM = 5.0

    df_enq_raiz["POSSUI_PELO_MENOS_5_MWM"] = (
        df_enq_raiz["VOLUME_ENQUADRAMENTO_MWM"] >= LIMIAR_MWM
    )

    # 6. Propaga o enquadramento da raiz de volta para todos os CNPJs
    # completos (14 dígitos) encontrados na base.
    #
    # Isso garante que:
    # - a Matriz herde o volume consolidado das Filiais;
    # - as Filiais herdem o mesmo enquadramento da Matriz;
    # - todos os estabelecimentos do mesmo grupo tenham o mesmo critério
    #   de enquadramento.
    df_enquadramento = pd.merge(
        df_ativos[["CNPJ", "CNPJ_RAIZ"]].drop_duplicates(),
        df_enq_raiz,
        on="CNPJ_RAIZ",
        how="left",
    ).drop(columns=["CNPJ_RAIZ"])

    # Persiste o resultado resumido na camada Relacional
    # (Dimensions/Configs).
    relational_dir = context.path("relational_configs")
    relational_dir.mkdir(parents=True, exist_ok=True)

    output_path = (
        relational_dir
        / f"enquadramento_consumidores_{competencia_base}.csv"
    )

    df_enquadramento.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return df_enquadramento
```


---
## src\domain\credito\notas_quantitativas_cpura.py
Linhas: 170
Classes: -
Funções: _obter_valor_numerico, _normalizar_pd, _obter_faixas_notas, _atribuir_nota_por_faixa, calcular_notas_quantitativas_cpura
```python
# -*- coding: utf-8 -*-
"""Cálculo das notas quantitativas de CPURA."""

from __future__ import annotations

from typing import Any

from silver.normalizadores import normalizar_float
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_valor_numerico(
    registro: dict[str, Any],
    campo: str,
) -> float:
    """Obtém e valida um valor numérico do registro."""
    valor = normalizar_float(registro.get(campo))

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
        fco_rol_valor = _obter_valor_numerico(registro, "FCO")
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

    except Exception as e:
        if logger is not None:
            logger.error(
                f"Falha no cálculo das notas quantitativas CPURA. CNPJ={registro.get('CNPJ')} - Motivo: {str(e)}"
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

from silver.normalizadores import normalizar_float
from domain.credito.pd_exceptions import PdCalculationError, PdInputValidationError

def calcular_pd_final_consumidor_le5(
    registro: dict[str, Any],
    pd_faixas: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula PD via score de bureau e restritivos (Sem DFs)."""
    try:
        score = normalizar_float(registro.get("SCORE_BUREAU"))
        restritivos = normalizar_float(registro.get("QUANTIDADE_RESTRITIVOS")) or 0.0

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
## src\domain\credito\pd_validator.py
Linhas: 104
Classes: -
Funções: _is_blank, validar_insumos_pd
```python
"""Validação dos insumos do cálculo de PD ajustada."""

from __future__ import annotations

from typing import Any

from silver.normalizadores import normalizar_string, normalizar_float
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
    pd_base = normalizar_float(pd_base_raw)

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

        # Rating pode estar vazio na extração inicial (é output do cálculo
        # de crédito para comercializadoras). Valida somente se informado.
        if not _is_blank(rating):
            rating_normalizado = normalizar_string(str(rating), upper=True)
            ratings_validos = {"A", "B", "C", "D", "E"}

            if rating_normalizado not in ratings_validos:
                raise PdInputValidationError(
                    f"Rating inválido para {segmento_pd}: {rating_normalizado!r}"
                )

    if segmento_pd in {"CPURA", "CGRUPO"}:
        tipo_comercializadora = normalizar_string(
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

        rating_norm = normalizar_string(rating, upper=True)
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

from silver.normalizadores import normalizar_string
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
    nota_normalizada = normalizar_string(nota, upper=True)

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
## src\domain\credito\servico_risco.py
Linhas: 124
Classes: -
Funções: rodar_pipeline_risco
```python
"""Orquestrador do Pipeline de Risco de Crédito."""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from domain.credito.ead_engine import calcular_ead
from domain.credito.lgd_engine import calcular_lgd
from domain.credito.pe_engine import calcular_perda_esperada
from domain.credito.taxa_risco_engine import calcular_taxa_risco
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def rodar_pipeline_risco(
    context: AppContext,
    df_exposicoes: pd.DataFrame,
    fator_conversao_ead: float = 1.0,
    config_lgd: dict[str, Any] | None = None
) -> dict[str, Any]:
    run_id = f"RSK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.risco", context.path("log_runner") / f"{run_id}__pipeline_risco.log")
    logger.info("Iniciando Pipeline de Risco de Crédito (run_id=%s)", run_id)
    
    garantias_path = context.path("silver") / "garantias_silver" / "fato_garantia.parquet"
    df_garantias = pd.read_parquet(garantias_path) if garantias_path.exists() else pd.DataFrame()

    resultados_fatos = []
    pe_total_carteira = 0.0
    notional_total_carteira = 0.0
    alertas = []

    df_exposicoes["MTM_POSITIVO_TOTAL"] = pd.to_numeric(df_exposicoes.get("MTM_POSITIVO_TOTAL", 0), errors="coerce").fillna(0.0)
    df_exposicoes["NOTIONAL_TOTAL"]     = pd.to_numeric(df_exposicoes.get("NOTIONAL_TOTAL", 0), errors="coerce").fillna(0.0)
    # PD ausente (NaN) é preservada — não zeramos para não mascarar contrapartes sem rating.
    df_exposicoes["PD_FINAL"] = pd.to_numeric(df_exposicoes.get("PD_FINAL"), errors="coerce")

    # Garante CNPJ_RAIZ (8 dígitos) para o filtro de garantias por grupo econômico.
    # Usa a coluna da Silver quando disponível; recalcula como fallback.
    if "CNPJ_RAIZ" not in df_exposicoes.columns:
        df_exposicoes["CNPJ_RAIZ"] = (
            df_exposicoes["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str[:8]
        )

    for idx, row in df_exposicoes.iterrows():
        cnpj      = row.get("CNPJ")
        cnpj_raiz = str(row.get("CNPJ_RAIZ", str(cnpj)[:8]))
        mtm_positivo = row.get("MTM_POSITIVO_TOTAL")
        notional     = row.get("NOTIONAL_TOTAL")
        segmento     = row.get("SEGMENTO_METODOLOGICO", "CGRUPO")
        pd_final     = row.get("PD_FINAL")

        cobertura_aplicada = 0.0
        # Filtro de garantias por CNPJ_RAIZ (cobre Matriz e Filiais do mesmo grupo)
        # e STATUS normalizado (strip + upper) para evitar falhas por espaços.
        if not df_garantias.empty and "CNPJ_CONTRAPARTE" in df_garantias.columns:
            filtro = (
                df_garantias["CNPJ_CONTRAPARTE"].astype(str).str[:8] == cnpj_raiz
            ) & (
                df_garantias["STATUS"].astype(str).str.strip().str.upper() == "VIGENTE"
                if "STATUS" in df_garantias.columns
                else True
            )
            if filtro.any():
                cobertura_calculada = df_garantias.loc[filtro, "PERCENTUAL_COBERTURA"].sum()
                cobertura_aplicada  = min(float(cobertura_calculada), 1.0)

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
        escrever_conjunto_de_dados_silver(records=df_alertas.to_dict(orient="records"), output_dir=context.path("silver") / "alertas_credito", filename=f"alertas_risco_{run_id}")

    if resultados_fatos:
        df_fatos = pd.DataFrame(resultados_fatos)
        relational_dir = context.path("relational_facts")
        relational_dir.mkdir(parents=True, exist_ok=True)
        
        escrever_conjunto_de_dados_silver(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename=f"fato_exposicao_risco_{run_id}")
        escrever_conjunto_de_dados_silver(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename="fato_exposicao_risco_LATEST")
        
    logger.info("Pipeline de Risco concluído. Taxa Carteira: %s", taxa_print)

    return {
        "run_id": run_id, "linhas_processadas": len(resultados_fatos),
        "taxa_risco_carteira": taxa_val, "pe_total_carteira": pe_total_carteira,
        "notional_total_carteira": notional_total_carteira, "calculo_id_taxa": res_taxa.get("calculo_id")
    }
```


---
## src\domain\fichas\derivador_financeiro.py
Linhas: 74
Classes: -
Funções: divisao_segura, calcular_indicadores_derivados
```python
import logging

logger = logging.getLogger(__name__)

def divisao_segura(num, den):
    if num is None or den is None:
        return None
    try:
        f_num = float(num)
        f_den = float(den)
        if f_den == 0.0:
            return None
        return f_num / f_den
    except (ValueError, TypeError):
        return None

def calcular_indicadores_derivados(record: dict) -> dict:
    """
    Calcula os indicadores derivados (DERIVED) de forma segura.
    Princípio: PRESERVAÇÃO DO FATO. Se o campo já possui valor extraído, não sobrescreve.
    """
    
    # Valores base
    ativo_circulante = record.get("ATIVO_CIRCULANTE_AJUSTADO")
    passivo_circulante = record.get("PASSIVO_CIRCULANTE_AJUSTADO")
    ativo_total = record.get("ATIVO_TOTAL_AJUSTADO")
    passivo_nao_circulante = record.get("PASSIVO_NAO_CIRCULANTE_FINANCEIRO_AJUSTADO")
    lucro_liquido = record.get("LUCRO_LIQUIDO")
    patrimonio_liquido = record.get("PATRIMONIO_LIQUIDO")
    fluxo_caixa = record.get("FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS")
    
    rol = record.get("ROL")
    vendas = record.get("VENDAS_LIQUIDAS")
    receita_base = rol if rol is not None else vendas

    # AC_PC
    if record.get("AC_PC") is None:
        val = divisao_segura(ativo_circulante, passivo_circulante)
        if val is not None:
            record["AC_PC"] = val
            
    # AT_PT
    if record.get("AT_PT") is None:
        if passivo_circulante is not None and passivo_nao_circulante is not None:
            passivo_total = float(passivo_circulante) + float(passivo_nao_circulante)
            val = divisao_segura(ativo_total, passivo_total)
            if val is not None:
                record["AT_PT"] = val
                
    # ROA
    if record.get("ROA") is None:
        val = divisao_segura(lucro_liquido, ativo_total)
        if val is not None:
            record["ROA"] = val
            
    # ROE
    if record.get("ROE") is None:
        val = divisao_segura(lucro_liquido, patrimonio_liquido)
        if val is not None:
            record["ROE"] = val
            
    # FCO
    if record.get("FCO") is None:
        val = divisao_segura(fluxo_caixa, receita_base)
        if val is not None:
            record["FCO"] = val
            
    # LUCRO_LIQUIDO_SOBRE_ROL
    if record.get("LUCRO_LIQUIDO_SOBRE_ROL") is None:
        val = divisao_segura(lucro_liquido, receita_base)
        if val is not None:
            record["LUCRO_LIQUIDO_SOBRE_ROL"] = val
            
    return record

```


---
## src\domain\fichas\ficha_extractor.py
Linhas: 424
Classes: -
Funções: analisar_data_com_seguranca, valor_extraido_limpo, _tipo_extraido_valido, busca_omnidirecional, extrair_registro, extrair_registro_do_vencedor, norm_tab
```python
# -*- coding: utf-8 -*-
"""Serviço de extração de dados dinâmico e omnidirecional das fichas Excel."""

from __future__ import annotations

import re
import math
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils.datetime import from_excel
from openpyxl.utils import get_column_letter

from common.excel import ler_celula

logger = logging.getLogger(__name__)

CUTOFF_DATE_LAYOUT_CHANGE = datetime(2025, 4, 30)

# ==============================================================================
# DICIONÁRIO DE INTELIGÊNCIA SEMÂNTICA UNIVERSAL (FALLBACK CONSUMIDORES)
# Mantido apenas para garantir a retrocompatibilidade com fichas de consumidores
# que ainda não foram migradas para o Master Catalog.
# ==============================================================================
MAPA_SEMANTICO_INTELIGENTE = {
    "CNPJ": r"^\s*CNPJ\b(?!.*(?:BBCE|CONTROLADOR))",
    "SIGLA": r"SIGLA",
    "FCO": r"FCO|MARGEM\s*DE\s*FLUXO\s*DE\s*CAIXA",
    "PATRIMONIO_LIQUIDO": r"PATRIM[OÔ]NIO\s*L[IÍ]QUIDO",
    "LUCRO_LIQUIDO": r"LUCRO\s*L[IÍ]QUIDO|RESULTADO\s*L[IÍ]QUIDO|LUCRO/PREJUIZO DO EXERCICIO",
    "PROBABILIDADE_DEFAULT": r"PROBABILIDADE\s*DEFAULT|PD\b|PD\s*=",
    "DATA_DEMONSTRACAO_FINANCEIRA": r"DATA\s*DA\s*DEMONSTRA[CÇ][AÃ]O|DATA\s*BASE|DATA\s*DA\s*DF",
    "RECEITA_LIQUIDA": r"RECEITA\s*L[IÍ]QUIDA|VENDAS\s*L[IÍ]QUIDAS|ROL",
    "VENDAS_LIQUIDAS": r"VENDAS\s*L[IÍ]QUIDAS|ROL|RECEITA\s*OPERACIONAL\s*L[IÍ]QUIDA",
    "ATIVO_TOTAL": r"ATIVO\s*TOTAL",
    "PASSIVO_CIRCULANTE": r"PASSIVO\s*CIRCULANTE",
    "ATIVO_CIRCULANTE": r"ATIVO\s*CIRCULANTE",
    "LUCRO_BRUTO": r"LUCRO\s*BRUTO",
    "LAJIR": r"LAJIR|RESULTADO\s*OPERACIONAL",
    "LAIR": r"LAIR|LUCRO\s*ANTES\s*DO\s*IMPOSTO",
    "ATIVO_CIRCULANTE_FINANCEIRO": r"ATIVO\s*CIRCULANTE\s*FINANCEIRO",
    "PASSIVO_CIRCULANTE_FINANCEIRO": r"PASSIVO\s*CIRCULANTE\s*FINANCEIRO",
    "PASSIVO_NAO_CIRCULANTE_FINANCEIRO": r"PASSIVO\s*N[AÃ]O\s*CIRCULANTE\s*FINANCEIRO",
    "EMPRESA": r"EMPRESA|RAZ[AÃ]O\s*SOCIAL",
    "TIPO_COMERCIALIZADORA": r"TIPO\s*DE\s*COMERCIALIZADORA",
    "DATA_ADESAO_CCEE": r"DATA\s*DE\s*ADES[AÃ]O",
    "CODIGO_CCEE": r"C[OÓ]DIGO\s*CCEE",
    "DATA_CALCULO": r"DATA\s*DA\s*FICHA",
    "SCORE_BUREAU": r"SCORE\s*BUREAU|SCORE\b",
    "QUANTIDADE_RESTRITIVOS": r"QUANTIDADE\s*DE\s*RESTRITIVOS",
    "CAPITAL_SOCIAL": r"CAPITAL\s*SOCIAL",
    "LUCROS_ACUMULADOS": r"LUCROS\s*ACUMULADOS",
    "RESERVA_DE_LUCROS": r"RESERVA\s*DE\s*LUCROS",
    "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS": r"FLUXO\s*DE\s*CAIXA\s*OPERACIONAL|CAIXA\s*L[IÍ]QUIDO\s*GERADO",
    "AGENCIA": r"AG[EÊ]NCIA",
    "NOTA_CREDITO": r"NOTA\s*DE\s*CR[EÉ]DITO",
    "ROL": r"RECEITA\s*OPERACIONAL\s*L[IÍ]QUIDA|ROL",
    "AC_PC": r"AC\s*/\s*PC|ATIVO\s*CIRCULANTE\s*/\s*PASSIVO\s*CIRCULANTE",
    "AT_PT": r"AT\s*/\s*PT|ATIVO\s*TOTAL\s*/\s*PASSIVO\s*TOTAL",
    "MTM_TOTAL_PL": r"MTM\s*TOTAL\s*/\s*PL|MTM\s*/\s*PATRIM[OÔ]NIO",
    "DIVIDENDOS_JCP_LUCRO_LIQUIDO": r"\(?DIVIDENDOS\s*\+\s*JCP\)?\s*/\s*LUCRO\s*L[IÍ]QUIDO|DIVIDENDOS\s*E\s*JCP",
    "CAPITAL_CIRCULANTE_LIQUIDO": r"CAPITAL\s*CIRCULANTE\s*L[IÍ]QUIDO|CCL\b",
    "RESTRITIVOS": r"RESTRITIVOS|APONTAMENTOS\s*RESTRITIVOS",
    "CNAE": r"CNAE\b|C[OÓ]DIGO\s*DE\s*ATIVIDADE",
    "NATUREZA_JURIDICA": r"NATUREZA\s*JUR[IÍ]DICA",
    "ENDERECO": r"ENDERE[CÇ]O|LOGRADOURO",
    "ROA": r"ROA\b|RETORNO\s*SOBRE\s*ATIVO",
    "ROE": r"ROE\b|RETORNO\s*SOBRE\s*PATRIM[OÔ]NIO",
    "FCO_ROL": r"FCO\s*/\s*ROL|FLUXO\s*DE\s*CAIXA\s*/\s*RECEITA",
    "CNPJ_BBCE": r"CNPJ\s*BBCE",
    "RATING_COPEL": r"RATING\s*COPEL",
    "RATING_PUBLICO": r"RATING\s*P[UÚ]BLICO",
    "SCORE_QUANTITATIVO": r"SCORE\s*QUANTITATIVO",
    "SCORE_QUALITATIVO": r"SCORE\s*QUALITATIVO"
}

def analisar_data_com_seguranca(date_val: Any) -> Optional[datetime]:
    if isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, (int, float)):
        try:
            return from_excel(date_val)
        except Exception:
            return None
    if isinstance(date_val, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_val.strip(), fmt)
            except ValueError:
                pass
    return None

def valor_extraido_limpo(val: Any, data_type: Optional[str] = None) -> Any:
    """Higieniza o valor extraído e garante o casting correto."""
    if val is None:
        return None
    
    dt_str = str(data_type).lower() if data_type else ""
    
    if isinstance(val, str):
        s_upper = val.strip().upper()
        if not s_upper or s_upper.startswith("#") or s_upper in ("NAN", "NONE", "<NA>", "N/A", "NULL", "N/D", "-", "--"):
            return None

    if any(t in dt_str for t in ("float", "num", "dec", "int", "moeda", "percent", "taxa", "valor", "score")):
        if isinstance(val, (int, float)):
            if math.isnan(val) or math.isinf(val):
                return None
            return float(val)
        
        clean = str(val).strip()
        # Notação contábil negativa (1.500) -> -1.500
        if clean.startswith("(") and clean.endswith(")"):
            clean = "-" + clean[1:-1].strip()
        
        # Limpa tudo que não for dígito, vírgula, ponto ou sinal de menos (remove R$, $, %, letras)
        clean = re.sub(r"[^\d\,\.-]", "", clean)
        
        if not clean:
            return None
            
        # Resolução de pontuação (milhar vs decimal)
        last_comma = clean.rfind(",")
        last_dot = clean.rfind(".")
        
        try:
            if last_comma > last_dot:
                # Padrão Brasileiro: 1.500,50 -> 1500.50
                clean = clean.replace(".", "").replace(",", ".")
            elif last_dot > last_comma:
                # Padrão Americano: 1,500.50 -> 1500.50
                if "," in clean:
                    clean = clean.replace(",", "")
                else:
                    # Só tem ponto: "1.500" ou "1.5"
                    if clean.count(".") > 1:
                        # Vários pontos: "1.500.000" -> "1500000"
                        clean = clean.replace(".", "")
                    else:
                        # Exatamente um ponto. Se tiver 3 dígitos depois do ponto, no Brasil quase sempre é milhar se a origem for string suja de excel.
                        # Exceções: taxas ou percentuais (onde 1.500 pode ser 1.5%)
                        parts = clean.split(".")
                        if len(parts[1]) == 3 and not any(t in dt_str for t in ("percent", "taxa")):
                            clean = clean.replace(".", "")
            
            return float(clean)
        except ValueError:
            return None

    if any(t in dt_str for t in ("date", "data")):
        return analisar_data_com_seguranca(val)

    if isinstance(val, float) and val.is_integer():
        val = int(val) 
    return str(val).strip()

def _tipo_extraido_valido(val: Any, data_type: str, field_name: str = "") -> bool:
    if val is None:
        return False
    dt_str = str(data_type).lower() if data_type else ""
    if any(t in dt_str for t in ("float", "num", "dec", "int", "moeda", "percent", "taxa", "valor", "score", "pd")):
        return isinstance(val, (int, float))
    if any(t in dt_str for t in ("date", "data")):
        return isinstance(val, datetime)
        
    # Sanity checks for strings to avoid grabbing headers or explanatory text
    if isinstance(val, str):
        v = val.lower().strip()
        if not v or v in ("tipo", "valor", "data", "descrição", "ajustado"):
            return False
        
        fn_lower = field_name.lower()
        
        # Rejeitar strings maiores que 60 chars (rodapés, observações), exceto se for endereço
        if len(v) > 60 and "endereco" not in fn_lower and "endereço" not in fn_lower:
            return False
            
        # Rejeitar números disfarçados de string em campos puramente de texto
        if fn_lower in ("auditor", "empresa", "sigla") and v.replace(".", "").replace(",", "").isdigit():
            return False
        
        # Heurísticas específicas por campo para evitar falsos positivos
        if "agencia" in fn_lower or "agência" in fn_lower:
            if not any(k in v for k in ("fitch", "mood", "s&p", "sp", "standard")): 
                return False
        if "nota" in fn_lower or "rating" in fn_lower:
            if len(v) > 5 or any(k in v for k in ("menor", "qualidade", "classificação", "agência", "risco")): 
                return False
        if "auditor" in fn_lower:
            if len(v) > 40: return False
            
    return True

def busca_omnidirecional(workbook: openpyxl.workbook.workbook.Workbook, search_pattern: str, data_type: str, sheet_hint: str = None, field_name: str = "", grid_cache: Dict[str, List[Tuple]] = None) -> Tuple[Any, dict]:
    """
    Caçador Universal (Refatorado para Performance in-memory RAM GRID):
    Varre TODAS as abas do Excel atrás da Regex através de uma matriz em memória.
    """
    if grid_cache is None:
        grid_cache = {}

    try:
        regex = re.compile(search_pattern, re.IGNORECASE)
    except re.error:
        return None, {}

    sheet_names = workbook.sheetnames
    if sheet_hint:
        hint_clean = str(sheet_hint).replace(" ", "").lower()
        sheet_names = sorted(sheet_names, key=lambda x: 0 if hint_clean in x.replace(" ", "").lower() else 1)

    for sheet_name in sheet_names:
        if sheet_name not in grid_cache:
            ws = workbook[sheet_name]
            # Convert worksheet to in-memory grid
            grid_cache[sheet_name] = list(ws.iter_rows(min_row=1, max_row=150, min_col=1, max_col=30, values_only=True))
            
        grid = grid_cache[sheet_name]
        
        for r_idx, row_tuple in enumerate(grid):
            for c_idx, cell_value in enumerate(row_tuple):
                if cell_value and isinstance(cell_value, str):
                    if regex.search(cell_value.strip()):
                        # Alvos: até 6 colunas à direita, e até 2 linhas abaixo
                        targets = [(r_idx, c_idx + offset) for offset in range(1, 7)]
                        targets.extend([(r_idx + offset, c_idx) for offset in range(1, 3)])
                        
                        for tr, tc in targets:
                            if 0 <= tr < len(grid) and 0 <= tc < len(grid[tr]):
                                raw_val = grid[tr][tc]
                                cleaned_val = valor_extraido_limpo(raw_val, data_type)
                                
                                if cleaned_val is not None and _tipo_extraido_valido(cleaned_val, data_type, field_name):
                                    col_letter = get_column_letter(tc + 1)
                                    coord = f"{col_letter}{tr + 1}"
                                    return cleaned_val, {
                                        "celula_origem": coord,
                                        "aba_origem": sheet_name,
                                        "metodo": "omnidirectional_regex"
                                    }
    return None, {}

def extrair_registro(workbook: openpyxl.workbook.workbook.Workbook, layout_schema: Dict[str, Any], master_catalog: Dict[str, Any] = None, grid_cache: Dict[str, List[Tuple]] = None) -> Tuple[Dict[str, Any], List[dict[str, Any]]]:
    extracted_data = {}
    metadata_list = []
    
    fields_to_extract = {}
    max_score = 0.0
    gates_to_check = []
    
    # 3. PROTEÇÃO AO LEGADO (Fallback)
    if master_catalog and "fields" in master_catalog:
        for mc_field, mc_config in master_catalog["fields"].items():
            if mc_config.get("nature") == "OBSERVED":
                fields_to_extract[mc_field] = dict(mc_config)
                max_score += float(mc_config.get("weight", 0))
                if mc_config.get("criticality") == "GATE_ENGINE":
                    gates_to_check.append(mc_field)
    else:
        # Fallback Consumidores
        field_map = layout_schema.get("field_map", {})
        fields_to_extract = dict(field_map)
        for sm_field in MAPA_SEMANTICO_INTELIGENTE.keys():
            if sm_field not in fields_to_extract:
                fields_to_extract[sm_field] = {}
        max_score = len(fields_to_extract) # each field weight = 1
        
    score_obtido = 0.0

    for field_name, field_config in fields_to_extract.items():
        data_type = field_config.get("data_type") or field_config.get("type")
        if not data_type:
            # Inferência de tipagem semântica para impedir que a busca omnidirecional aceite lixo (strings) no lugar de números
            fn_lower = field_name.lower()
            if any(t in fn_lower for t in ("ativo", "passivo", "lucro", "patrimonio", "capital", "venda", "receita", "lair", "lajir", "fco", "fluxo", "probabilidade", "pd", "rol", "reserva", "imposto", "resultado", "score", "ac_pc", "at_pt", "mtm", "dividendos")):
                data_type = "float"
            elif any(t in fn_lower for t in ("data", "dt")):
                data_type = "date"
            else:
                data_type = "string"
                
        sheet_hint = field_config.get("sheet")
        
        # 2. INTEGRAÇÃO COM O MASTER CATALOG E SCORING PONDERADO
        if master_catalog and "fields" in master_catalog:
            patterns = field_config.get("search_patterns")
            if patterns and isinstance(patterns, list) and len(patterns) > 0:
                search_pattern = "|".join(patterns)
            else:
                search_pattern = field_name.replace("_", r"\s*")
        else:
            search_pattern = MAPA_SEMANTICO_INTELIGENTE.get(field_name) or field_config.get("search_pattern")
            if not search_pattern:
                search_pattern = field_name.replace("_", r"\s*")
                
        val, meta_inf = busca_omnidirecional(workbook, search_pattern, data_type, sheet_hint, field_name, grid_cache)
        
        meta = {
            "campo": field_name,
            "aba_origem": meta_inf.get("aba_origem"),
            "celula_origem": meta_inf.get("celula_origem"),
            "metodo": meta_inf.get("metodo", "falha_extracao"),
            "valor": val
        }
        
        # Se a busca dinâmica falhar miseravelmente, tenta a coordenada fixa cega como último recurso
        # Isso ocorre apenas se não houver Master Catalog ou se o legacy mantiver coords.
        if val is None and not (master_catalog and "fields" in master_catalog):
            static_cell = field_config.get("value_cell") or field_config.get("cell")
            if static_cell and str(static_cell).strip() not in ("0", ""):
                try:
                    # Usa a aba sugerida no JSON ou a ativa
                    ws_estatico = workbook.active
                    if sheet_hint:
                        hint_clean = str(sheet_hint).replace(" ", "").lower()
                        for aba_real in workbook.sheetnames:
                            if hint_clean in aba_real.replace(" ", "").lower():
                                ws_estatico = workbook[aba_real]
                                break

                    raw_val, static_meta = ler_celula(ws_estatico, static_cell, return_meta=True)
                    clean_val = valor_extraido_limpo(raw_val, data_type)
                    if clean_val is not None and _tipo_extraido_valido(clean_val, data_type, field_name):
                        val = clean_val
                        meta.update({
                            "aba_origem": ws_estatico.title,
                            "celula_origem": static_cell,
                            "metodo": "estatico_fixo_fallback",
                            "valor": val
                        })
                except Exception:
                    pass

        extracted_data[field_name] = val
        if meta["metodo"] != "falha_extracao":
            metadata_list.append(meta)
            
        if val is not None:
            if master_catalog and "fields" in master_catalog:
                score_obtido += float(field_config.get("weight", 0))
            else:
                score_obtido += 1

    # Calcula a Integridade da Ficha
    score = (score_obtido / max_score) * 100 if max_score > 0 else 0
    extracted_data["INTEGRIDADE_EXTRAIDA_PERCENTUAL"] = round(score, 2)
    
    # 4. GATES de Segurança
    falha_gate = False
    for gate in gates_to_check:
        if extracted_data.get(gate) is None:
            falha_gate = True
            logger.warning(f"[GATE_ENGINE] Falha Crítica! Campo {gate} (GATE) ausente.")
            break
            
    extracted_data["_FALHA_GATE_CRITICO"] = falha_gate
    
    if falha_gate:
        # Penaliza severamente (zera o score) se o gate crítico falhou
        score = 0.0
        extracted_data["INTEGRIDADE_EXTRAIDA_PERCENTUAL"] = 0.0
        logger.warning("[INTEGRIDADE] Ficha recusada: Falha no GATE Crítico.")
    elif score >= 40.0:
        logger.info(f"[INTEGRIDADE] Ficha aprovada com {score:.2f}% de integridade (Score: {score_obtido}/{max_score}).")
    else:
        logger.warning(f"[INTEGRIDADE] Ficha recusada: apenas {score:.2f}% de integridade (Score: {score_obtido}/{max_score}).")

    return extracted_data, metadata_list

def extrair_registro_do_vencedor(
    workbook: openpyxl.workbook.workbook.Workbook,
    layouts: Dict[str, Any],
    master_catalog: Dict[str, Any] = None,
) -> Tuple[Dict[str, Any], List[dict[str, Any]], str]:
    """
    Motor Competitivo (Tournament Extraction):
    Ignora classificação cega baseada em uma única célula. 
    Testa a ficha contra TODOS os layouts e elege como 'Campeão' aquele que 
    atingir a maior integridade (porcentagem de campos com match válido).
    """
    from silver.normalizadores import normalizar_string

    # Veto por tipo de documento baseado em abas esperadas (Crítico #3)
    expected_tabs_raw = {
        "V0", "Para_Limite_Comercializadoras", "Premissas", 
        "FichaIndividual", "Memória de Cálculo", "Conf. Puras_DRE", 
        "Dados Gerais e Qualitativos", "DRE", "Dem.Fin."
    }
    
    def norm_tab(t: str) -> str:
        s = normalizar_string(t, upper=True)
        return s.replace(" ", "") if s else ""
        
    expected_tabs_norm = {norm_tab(t) for t in expected_tabs_raw}
    workbook_tabs_norm = {norm_tab(t) for t in workbook.sheetnames}
    
    if not expected_tabs_norm.intersection(workbook_tabs_norm):
        logger.warning(f"[VETO] Documento rejeitado. Nenhuma aba bate com as abas de layout: {workbook.sheetnames}")
        return {}, [], "DOC_001_ESTRUTURA_INCOMPATIVEL"

    best_score = -1.0
    champion_data = {}
    champion_meta = []
    champion_name = "NENHUM"
    
    grid_cache = {}

    for layout_name, layout_schema in layouts.items():
        extracted, metadata = extrair_registro(workbook, layout_schema, master_catalog, grid_cache, allow_semantic=True)
        score = extracted.get("INTEGRIDADE_EXTRAIDA_PERCENTUAL", 0)
        
        logger.info(f"Challenger {layout_name} obteve score: {score:.2f}%")
        
        if score > best_score:
            best_score = score
            champion_data = extracted
            champion_meta = metadata
            champion_name = layout_name

    logger.info(f"[CHAMPION] Torneio finalizado. Vencedor: '{champion_name}' com score de {best_score:.2f}%.")
    return champion_data, champion_meta, champion_name
```


---
## src\domain\mtm\__init__.py
Linhas: 0
Classes: -
Funções: -
```python

```


---
## src\domain\mtm\servico_denodo_mtm_reconciliacao.py
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
from control.logger import obter_logger
from domain.enums import StatusAlerta
from storage.escrever_dados import escrever_conjunto_de_dados_silver


class ReconciliacaoDataError(Exception):
    """Exceção levantada quando os dados fonte para a reconciliação estão inacessíveis ou vazios."""

def executar_reconciliacao_denodo_mtm(context: AppContext) -> dict[str, Any]:
    """
    Cruza o consolidado de contratos do Denodo com posições do MtM na camada Silver por CNPJ.
    Classifica as contrapartes e dispara os alertas CTR_001 e CTR_002.
    """
    run_id = f"REC_MTM_DENODO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = context.path("log_runner") / f"{run_id}__reconciliacao.log"
    logger = obter_logger("bdc.reconciliacao", log_file)

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
            escrever_conjunto_de_dados_silver(
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
        csv_path, parquet_path = escrever_conjunto_de_dados_silver(
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
## src\domain\salesforce\servico_salesforce_reconciliacao.py
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
from storage.escrever_dados import escrever_conjunto_de_dados_silver

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
        escrever_conjunto_de_dados_silver(
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
## src\services\connectors\mtm_connector.py
Linhas: 84
Classes: MtmConnectionError
Funções: _encontrar_arquivo_mtm_recente, buscar_mtm_consolidado
```python
"""Conector de integração com a base de MtM (Risco de Mercado)."""

from __future__ import annotations
from pathlib import Path
from typing import Any
from datetime import datetime
import pandas as pd

from silver.normalizadores import padronizar_cnpj

class MtmConnectionError(Exception):
    """Exceção levantada quando a base de MtM não pode ser obtida."""

def _encontrar_arquivo_mtm_recente(diretorio: Path) -> Path:
    arquivos = [f for f in diretorio.iterdir() if f.is_file() and f.suffix.lower() in {".xlsx", ".xls", ".csv"} and not f.name.startswith("~$")]
    if not arquivos: raise FileNotFoundError(f"Nenhum arquivo de MtM encontrado na pasta: {diretorio}")
    return max(arquivos, key=lambda f: f.stat().st_mtime)

def buscar_mtm_consolidado(input_dir: Path | str, logger: Any | None = None) -> pd.DataFrame:
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

        # 1. CNPJ — via validador centralizado
        col_cnpj = next((c for c in df_bruto.columns if "CNPJ" in c and "CONTROLADOR" not in c), None)
        if col_cnpj:
            parsed       = df_bruto[col_cnpj].map(padronizar_cnpj)
            cnpj_series  = parsed.map(lambda t: t[0])
            raiz_series  = parsed.map(lambda t: t[1])
            status_series = parsed.map(lambda t: t[2])
        else:
            cnpj_series   = pd.Series(["00000000000000"] * len(df_bruto), name="CNPJ")
            raiz_series   = pd.Series(["00000000"] * len(df_bruto), name="CNPJ_RAIZ")
            status_series = pd.Series(["CNPJ_AUSENTE"] * len(df_bruto), name="STATUS_CNPJ")

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
            "CNPJ":        cnpj_series,
            "CNPJ_RAIZ":   raiz_series,
            "STATUS_CNPJ": status_series,
            "CONTRATO":    contrato_series,
            "DATA_BASE":   data_base_series,
            "MTM_TOTAL":   valores_mtm,
            "NOTIONAL":    valores_notional
        })

        # Filtra registros com CNPJ inválido ou ausente
        df_resultado = df_resultado[df_resultado["STATUS_CNPJ"] == "CNPJ_VALIDO"].copy()

        if logger: logger.info("MtM lido. Notional convertido para Financeiro (R$).")
        return df_resultado

    except Exception as exc:
        if logger: logger.exception("Falha ao processar o arquivo local de MtM.")
        raise MtmConnectionError(f"Erro ao ler base de MtM: {exc}") from exc
```


---
## src\services\connectors\risk3_connector.py
Linhas: 130
Classes: -
Funções: _obter_token_auth, buscar_bureau_risk3
```python
"""Conector oficial para a API Expresso RISK3 (Bureau de Crédito)."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from app.context import AppContext
from silver.normalizadores import padronizar_cnpj

LOGGER = logging.getLogger(__name__)

def _obter_token_auth() -> str | None:
    """Autentica na API da RISK3 e obtém um token de sessão via POST."""
    base_url = os.getenv("RISK3_BASE_URL")
    user = os.getenv("RISK3_USER")
    pwd = os.getenv("RISK3_PWD")

    if not all([base_url, user, pwd]):
        LOGGER.warning("Credenciais RISK3_BASE_URL, RISK3_USER ou RISK3_PWD ausentes no .env")
        return None

    proxies = {"http": None, "https": None} # Tenta bypass de proxy local

    try:
        url = f"{base_url.rstrip('/')}/api/v0/login"
        resp = requests.post(url, json={"username": user, "password": pwd}, timeout=15, verify=False, proxies=proxies)
        
        # Bloqueio de rede detectado
        if "Acesso Bloqueado" in resp.text or "Netskope" in resp.text:
            LOGGER.error("Conexão interceptada pelo Netskope/Firewall da Copel.")
            return None

        if resp.status_code == 200:
            return resp.json().get("data")
            
        LOGGER.error("Falha na autenticação RISK3. HTTP %s", resp.status_code)
        return None
    except Exception as e:
        LOGGER.error("Falha de conexão na RISK3: %s", e)
        return None

def buscar_bureau_risk3(cnpjs: list[str], context: AppContext) -> pd.DataFrame:
    """Orquestra a consulta em lote na RISK3 utilizando cache local."""
    cache_path = context.path("entradas") / "bureau" / "cache" / "risk3_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    cache = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    token = _obter_token_auth()
    if not token:
        LOGGER.warning("Sem token da RISK3. Abortando consulta de Bureau.")
        return pd.DataFrame()

    base_url = os.getenv("RISK3_BASE_URL", "").rstrip('/')
    proxies = {"http": None, "https": None}
    
    cnpjs_unicos = sorted(list(set(padronizar_cnpj(c)[0] for c in cnpjs if padronizar_cnpj(c))))
    results = []
    
    print(f"\n--- INICIANDO CONSULTA RISK3 BUREAU ({len(cnpjs_unicos)} CNPJs) ---")
    
    for i, cnpj in enumerate(cnpjs_unicos):
        # Validação de Cache (30 dias para não gastar chamadas do contrato)
        cached = cache.get(cnpj)
        if cached and cached.get("STATUS") == "SUCESSO":
            data_cons = cached.get("DATA_CONSULTA")
            if data_cons:
                if (datetime.now() - datetime.fromisoformat(data_cons)).days < 30:
                    print(f"[{i + 1}/{len(cnpjs_unicos)}] CNPJ {cnpj} -> CACHE (Válido)")
                    results.append(cached)
                    continue

        print(f"[{i + 1}/{len(cnpjs_unicos)}] CNPJ {cnpj} -> Consultando API...", end=" ", flush=True)
        
        url = f"{base_url}/api/v0/analises/cnpj/{cnpj}"
        headers = {"Venidera-AuthToken": token}
        
        resultado = {
            "CNPJ": cnpj,
            "DATA_CONSULTA": datetime.now().isoformat(timespec="seconds"),
            "STATUS": "FALHA"
        }

        try:
            resp = requests.get(url, headers=headers, timeout=20, verify=False, proxies=proxies)
            
            if "Netskope" in resp.text or "Acesso Bloqueado" in resp.text:
                resultado["STATUS"] = "BLOQUEIO_FIREWALL"
                print("BLOQUEIO_FIREWALL")
            elif resp.status_code == 200:
                data_obj = resp.json().get("data", {})
                resultado["RAW_DATA"] = json.dumps(data_obj, ensure_ascii=False)
                resultado["STATUS"] = "SUCESSO"
                print("SUCESSO")
            elif resp.status_code in (404, 422):
                resultado["STATUS"] = "NAO_ENCONTRADO"
                print("NAO_ENCONTRADO")
            else:
                resultado["STATUS"] = f"ERRO_HTTP_{resp.status_code}"
                print(f"ERRO_HTTP_{resp.status_code}")
        except Exception:
            resultado["STATUS"] = "ERRO_CONEXAO"
            print("ERRO_CONEXAO")

        if resultado["STATUS"] in ["SUCESSO", "NAO_ENCONTRADO"]:
            cache[cnpj] = resultado
            
        results.append(resultado)
        time.sleep(0.5)

    if results:
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    return pd.DataFrame(results)
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
Funções: criar_documento_classificado
```python
"""Builders da camada silver para documentos classificados."""

from __future__ import annotations


def criar_documento_classificado(
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
## src\silver\normalizador_de_tipo_de_campo.py
Linhas: 140
Classes: -
Funções: _obter_campos, normalizar_registro
```python
"""Normalização técnica das fichas."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from anyio import Path

from app.context import AppContext
from silver.normalizadores import (
    normalize_date,
    normalize_string,
    normalize_float,
    normalize_data_demonstracao_financeira
)
from common.json import ler_json
from control.field_types import obter_config_tipo_campo


def _obter_campos(field_types: dict[str, Any], key: str) -> list[str]:
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


def normalizar_registro(
    record: dict[str, Any],
    context: AppContext,
    slug: str,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Normaliza o registro bruto extraído da ficha."""
    try:
        # T1.3.1: Uso da Classe Python Tipada com prioridade sobre o JSON
        config_class = obter_config_tipo_campo(slug)

        if config_class:
            if logger is not None:
                logger.info("Carregando tipagem da classe Python: %s", slug)
            date_fields = config_class.date_fields
            float_fields = config_class.float_fields
            text_fields = config_class.text_fields
            cnpj_fields = config_class.cnpj_fields
        else:
            if logger is not None:
                logger.info("Classe Python não encontrada. Fallback: %s", slug)
            
            if slug == "field_types_fichas_comercializadoras":
                master_catalog_path = Path("ENTRADAS/control/quality/master_catalog_comercializadoras.json")
                catalog = ler_json(master_catalog_path)
                fields = catalog.get("fields", {})
                date_fields = [k for k, v in fields.items() if v.get("type") == "date"]
                float_fields = [k for k, v in fields.items() if v.get("type") == "float"]
                text_fields = [k for k, v in fields.items() if v.get("type") == "string"]
                cnpj_fields = [k for k, v in fields.items() if v.get("type") == "cnpj"]
            else:
                field_types_path = context.control_file(slug)
                field_types = ler_json(field_types_path)

                date_fields = _obter_campos(field_types, "date_fields")
                float_fields = _obter_campos(field_types, "float_fields")
                text_fields = _obter_campos(field_types, "text_fields")
                cnpj_fields = _obter_campos(field_types, "cnpj_fields")

        out = dict(record)

        from silver.normalizadores import padronizar_cnpj
        
        for field in cnpj_fields:
            if field in out:
                try:
                    c_14, c_raiz, c_status = padronizar_cnpj(out.get(field))
                    if c_14 is not None:
                        out[field] = c_14
                        if field == "CNPJ":
                            out["CNPJ_RAIZ"] = c_raiz
                            out["STATUS_CNPJ"] = c_status
                    else:
                        out[field] = None
                        if field == "CNPJ":
                            out["CNPJ_RAIZ"] = None
                            out["STATUS_CNPJ"] = c_status
                except Exception as exc:
                    if logger: logger.exception("Erro CNPJ: '%s'", field)
                    raise ValueError(f"Falha ao normalizar campo CNPJ '{field}'.") from exc

        for field in date_fields:
            if field in out:
                try:
                    if field == "DATA_DEMONSTRACAO_FINANCEIRA":
                        val_norm, epoch_orig, was_corrected = normalize_data_demonstracao_financeira(out.get(field))
                        out[field] = val_norm
                        out["FLAG_DATA_DF_CORRIGIDA"] = was_corrected
                        out["DATA_DF_EPOCH_ORIGINAL"] = epoch_orig
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
## src\storage\__init__.py
Linhas: 1
Classes: -
Funções: -
```python
"""Camada de persistência física do sistema BDC."""

```


---
## src\storage\armazenamento_manifest.py
Linhas: 39
Classes: -
Funções: anexar_registro_de_manifesto, historico_de_ingestao_de_carga
```python
"""Persistência do manifest de ingestão em formato JSONL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def anexar_registro_de_manifesto(
    output_file: str | Path,
    record: dict[str, Any],
) -> None:
    """Acrescenta um registro no arquivo JSONL de ingestão."""
    target = Path(output_file)
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(record, ensure_ascii=False) + "\n")


def historico_de_ingestao_de_carga(
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
## src\storage\operacao_arquivo.py
Linhas: 34
Classes: -
Funções: mover_arquivo_com_tentativa_adicional
```python
"""Operações robustas de arquivo para ambiente Windows."""

from __future__ import annotations

import shutil
import time
from pathlib import Path


def mover_arquivo_com_tentativa_adicional(
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
