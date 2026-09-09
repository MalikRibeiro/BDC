from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent
from typing import Iterable


DEFAULT_IGNORE = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".coverage",
    "htmlcov",
    "AI_CONTEXT",
}

CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "cp1252", "latin-1")

SENSITIVE_FILE_PATTERNS = (
    re.compile(r"(^|[._-])\.env($|[._-])", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"credential", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"\.pem$", re.IGNORECASE),
    re.compile(r"\.key$", re.IGNORECASE),
    re.compile(r"\.pfx$", re.IGNORECASE),
    re.compile(r"\.p12$", re.IGNORECASE),
)

SENSITIVE_VALUE_PATTERNS = (
    re.compile(
        r'(?im)^(\s*["\']?(?:password|passwd|pwd|token|secret|api[_-]?key|client[_-]?secret)'
        r'["\']?\s*[:=]\s*)[^\n,}]+',
    ),
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+/=-]+"),
    re.compile(r"(?i)(mongodb(?:\+srv)?://[^:\s/]+:)[^@\s]+@"),
    re.compile(r"(?i)(postgres(?:ql)?://[^:\s/]+:)[^@\s]+@"),
)


@dataclass
class SymbolInfo:
    name: str
    kind: str
    line: int
    end_line: int | None = None
    decorators: list[str] = field(default_factory=list)


@dataclass
class FileAnalysis:
    path: str
    lines: int = 0
    bytes: int = 0
    sha256: str = ""
    encoding: str = ""
    imports: list[str] = field(default_factory=list)
    import_details: list[dict] = field(default_factory=list)
    classes: list[SymbolInfo] = field(default_factory=list)
    functions: list[SymbolInfo] = field(default_factory=list)
    docstring: str = ""
    syntax_error: str | None = None
    read_error: str | None = None


@dataclass
class Alert:
    path: str
    line: int
    severity: str
    category: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera um pacote Markdown consolidado para análise de um projeto Python por IA."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Raiz do projeto. Padrão: diretório atual.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Diretório de saída. Padrão: <root>/AI_CONTEXT.",
    )
    parser.add_argument(
        "--partes",
        type=int,
        default=3,
        help="Quantidade de arquivos consolidados de código. Padrão: 3.",
    )
    parser.add_argument(
        "--max-config-bytes",
        type=int,
        default=300_000,
        help="Tamanho máximo de cada configuração incluída integralmente.",
    )
    parser.add_argument(
        "--sem-sanitizacao",
        action="store_true",
        help="Desativa a máscara de possíveis segredos. Não recomendado.",
    )
    return parser.parse_args()


def is_ignored(path: Path, root: Path, out: Path, ignore: set[str]) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True

    if path == out or out in path.parents:
        return True

    return any(part in ignore for part in relative.parts)


def is_sensitive_file(path: Path) -> bool:
    name = path.name
    return any(pattern.search(name) for pattern in SENSITIVE_FILE_PATTERNS)


def read_text_safe(path: Path) -> tuple[str, str]:
    last_error: Exception | None = None

    for encoding in TEXT_ENCODINGS:
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError as exc:
            last_error = exc
        except OSError:
            raise

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        str(last_error or "Codificação não reconhecida"),
    )


def sanitize_text(text: str) -> tuple[str, int]:
    replacements = 0
    sanitized = text

    for pattern in SENSITIVE_VALUE_PATTERNS:
        if pattern.groups:
            sanitized, count = pattern.subn(r"\1<REDACTED>", sanitized)
        else:
            sanitized, count = pattern.subn("<REDACTED>", sanitized)
        replacements += count

    user_path_patterns = (
        re.compile(r"(?i)C:\\Users\\[^\\\s\"']+"),
        re.compile(r"/home/[^/\s\"']+"),
        re.compile(r"/Users/[^/\s\"']+"),
    )
    for pattern in user_path_patterns:
        sanitized, count = pattern.subn("<USER_HOME>", sanitized)
        replacements += count

    return sanitized, replacements


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return dotted_name(node.func)
    return ""


def decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> list[str]:
    return [name for dec in node.decorator_list if (name := dotted_name(dec))]


def analyze_python(path: Path, root: Path) -> FileAnalysis:
    relative = path.relative_to(root).as_posix()
    info = FileAnalysis(path=relative, bytes=path.stat().st_size, sha256=sha256_file(path))

    try:
        text, encoding = read_text_safe(path)
        info.encoding = encoding
        info.lines = len(text.splitlines())
    except (OSError, UnicodeError) as exc:
        info.read_error = f"{type(exc).__name__}: {exc}"
        return info

    try:
        tree = ast.parse(text, filename=relative)
    except SyntaxError as exc:
        info.syntax_error = f"linha {exc.lineno}: {exc.msg}"
        return info

    info.docstring = ast.get_docstring(tree, clean=True) or ""

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                info.imports.append(alias.name)
                info.import_details.append(
                    {"module": alias.name, "name": None, "line": node.lineno}
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            info.imports.append(module)
            for alias in node.names:
                info.import_details.append(
                    {"module": module, "name": alias.name, "line": node.lineno}
                )
        elif isinstance(node, ast.ClassDef):
            info.classes.append(
                SymbolInfo(
                    name=node.name,
                    kind="class",
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", None),
                    decorators=decorator_names(node),
                )
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "async function" if isinstance(node, ast.AsyncFunctionDef) else "function"
            info.functions.append(
                SymbolInfo(
                    name=node.name,
                    kind=kind,
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", None),
                    decorators=decorator_names(node),
                )
            )

    info.imports = sorted(set(filter(None, info.imports)))
    info.classes.sort(key=lambda item: item.line)
    info.functions.sort(key=lambda item: item.line)
    return info


def scan_alerts(path: Path, root: Path) -> list[Alert]:
    alerts: list[Alert] = []
    relative = path.relative_to(root).as_posix()

    try:
        text, _ = read_text_safe(path)
    except (OSError, UnicodeError):
        return alerts

    try:
        tree = ast.parse(text, filename=relative)
    except SyntaxError as exc:
        return [
            Alert(relative, exc.lineno or 0, "ALTA", "SYNTAX_ERROR", exc.msg)
        ]

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            called = dotted_name(node.func)
            if called == "sys.exit":
                alerts.append(
                    Alert(relative, node.lineno, "MÉDIA", "SYS_EXIT", "sys.exit fora da camada de interface deve ser revisado.")
                )
            elif called == "print":
                alerts.append(
                    Alert(relative, node.lineno, "BAIXA", "PRINT", "Uso de print; avaliar logging estruturado.")
                )

        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                alerts.append(
                    Alert(relative, node.lineno, "ALTA", "BARE_EXCEPT", "Bloco except sem tipo de exceção.")
                )
            elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    alerts.append(
                        Alert(relative, node.lineno, "ALTA", "SILENT_EXCEPTION", "except Exception com pass oculta falhas.")
                    )

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if end - node.lineno + 1 >= 100:
                alerts.append(
                    Alert(
                        relative,
                        node.lineno,
                        "MÉDIA",
                        "LONG_FUNCTION",
                        f"Função {node.name} possui {end - node.lineno + 1} linhas.",
                    )
                )

        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if re.search(r"(?i)[A-Z]:\\Users\\", value) or re.search(r"/(home|Users)/[^/]+", value):
                alerts.append(
                    Alert(relative, getattr(node, "lineno", 0), "MÉDIA", "ABSOLUTE_USER_PATH", "Caminho absoluto de usuário encontrado.")
                )

    return alerts


def build_tree(folder: Path, root: Path, out: Path, ignore: set[str], prefix: str = "") -> list[str]:
    try:
        items = [
            item
            for item in folder.iterdir()
            if not is_ignored(item, root, out, ignore) and not is_sensitive_file(item)
        ]
    except OSError:
        return [prefix + "[Erro ao listar diretório]"]

    items.sort(key=lambda item: (item.is_file(), item.name.lower()))
    lines: list[str] = []

    for index, item in enumerate(items):
        last = index == len(items) - 1
        connector = "└── " if last else "├── "
        suffix = "/" if item.is_dir() else ""
        lines.append(f"{prefix}{connector}{item.name}{suffix}")

        if item.is_dir():
            extension = "    " if last else "│   "
            lines.extend(build_tree(item, root, out, ignore, prefix + extension))

    return lines


def discover_files(root: Path, out: Path, ignore: set[str]) -> tuple[list[Path], list[Path], list[Path]]:
    python_files: list[Path] = []
    config_files: list[Path] = []
    skipped_sensitive: list[Path] = []

    for path in root.rglob("*"):
        if is_ignored(path, root, out, ignore) or not path.is_file():
            continue

        if is_sensitive_file(path):
            skipped_sensitive.append(path)
            continue

        suffix = path.suffix.lower()
        if suffix == ".py":
            python_files.append(path)
        elif suffix in CONFIG_EXTENSIONS:
            config_files.append(path)

    python_files.sort(key=lambda path: path.relative_to(root).as_posix().lower())
    config_files.sort(key=lambda path: path.relative_to(root).as_posix().lower())
    skipped_sensitive.sort(key=lambda path: path.relative_to(root).as_posix().lower())
    return python_files, config_files, skipped_sensitive


def module_group(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    parts = [part.lower() for part in relative.parts]

    if "tests" in parts or relative.name.lower().startswith("test_"):
        return "tests"
    if "scripts" in parts:
        return "scripts"
    if "common" in parts or "shared" in parts:
        return "common"
    if "app" in parts or "application" in parts or "cli" in parts:
        return "application"
    if "domain" in parts or "services" in parts:
        return "domain_services"
    if any(name in parts for name in ("storage", "staging", "silver", "gold", "connectors", "infrastructure")):
        return "data_infrastructure"
    return parts[0] if parts else "root"


def distribute_semantically(files: list[Path], root: Path, part_count: int) -> list[list[Path]]:
    """
    Agrupa arquivos relacionados e distribui os grupos entre as partes.

    Arquivos pequenos do mesmo domínio ficam juntos no mesmo Markdown, em vez
    de serem espalhados apenas para equilibrar bytes.
    """
    groups: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        groups[module_group(path, root)].append(path)

    weighted_groups = sorted(
        groups.items(),
        key=lambda item: sum(path.stat().st_size for path in item[1]),
        reverse=True,
    )

    parts: list[list[Path]] = [[] for _ in range(part_count)]
    sizes = [0] * part_count

    for _, grouped_files in weighted_groups:
        small_files = [path for path in grouped_files if path.stat().st_size <= 30_000]
        large_files = [path for path in grouped_files if path.stat().st_size > 30_000]

        if small_files:
            index = sizes.index(min(sizes))
            parts[index].extend(small_files)
            sizes[index] += sum(path.stat().st_size for path in small_files)

        for path in large_files:
            index = sizes.index(min(sizes))
            parts[index].append(path)
            sizes[index] += path.stat().st_size

    for part in parts:
        part.sort(key=lambda path: (module_group(path, root), path.relative_to(root).as_posix().lower()))

    return parts


def detect_internal_dependencies(analyses: list[FileAnalysis], python_files: list[Path], root: Path) -> dict[str, list[str]]:
    module_to_path: dict[str, str] = {}

    for path in python_files:
        relative = path.relative_to(root)
        parts = list(relative.with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        module_to_path[".".join(parts)] = relative.as_posix()
        if parts and parts[0] == "src":
            module_to_path[".".join(parts[1:])] = relative.as_posix()

    dependencies: dict[str, list[str]] = {}
    for analysis in analyses:
        resolved: set[str] = set()
        for imported in analysis.imports:
            candidates = [imported]
            pieces = imported.split(".")
            candidates.extend(".".join(pieces[:i]) for i in range(len(pieces) - 1, 0, -1))
            for candidate in candidates:
                if candidate in module_to_path and module_to_path[candidate] != analysis.path:
                    resolved.add(module_to_path[candidate])
                    break
        dependencies[analysis.path] = sorted(resolved)

    return dependencies


def write_readme(out: Path, part_count: int) -> None:
    order = [
        "01_CONTEXTO.md",
        "02_ESTRUTURA.md",
        "03_CONFIGURACOES.md",
        "04_RESUMO_TECNICO.md",
        "05_DEPENDENCIAS.md",
        "06_ALERTAS.md",
    ]
    order.extend(f"{7 + index:02d}_CODIGO_PARTE_{index + 1}.md" for index in range(part_count))
    order.append("manifest.json")

    lines = [
        "# AI_CONTEXT",
        "",
        "Pacote gerado automaticamente para análise do projeto por IA.",
        "",
        "## Ordem sugerida de leitura",
        "",
    ]
    lines.extend(f"{index}. `{name}`" for index, name in enumerate(order, start=1))
    lines.extend(
        [
            "",
            "## Observações",
            "",
            "- Os arquivos Python menores são consolidados junto a outros arquivos do mesmo domínio.",
            "- O código-fonte permanece integral nos arquivos `CODIGO_PARTE_*`.",
            "- Possíveis segredos e caminhos de usuário são mascarados por padrão.",
            "- Arquivos potencialmente sensíveis, como `.env`, chaves e credenciais, não são incluídos.",
            "- `manifest.json` registra hashes e estatísticas para confirmar qual versão foi enviada à IA.",
        ]
    )
    (out / "00_README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_context(
    out: Path,
    root: Path,
    python_files: list[Path],
    config_files: list[Path],
    analyses: list[FileAnalysis],
    skipped_sensitive: list[Path],
) -> None:
    total_lines = sum(item.lines for item in analyses)
    total_bytes = sum(path.stat().st_size for path in python_files + config_files)
    syntax_errors = sum(1 for item in analyses if item.syntax_error)
    read_errors = sum(1 for item in analyses if item.read_error)

    content = dedent(
        f"""\
        # CONTEXTO

        ## Projeto

        - Nome: `{root.name}`
        - Raiz analisada: `{root}`
        - Gerado em UTC: `{datetime.now(timezone.utc).isoformat()}`

        ## Inventário

        - Arquivos Python: **{len(python_files)}**
        - Arquivos de configuração: **{len(config_files)}**
        - Linhas Python: **{total_lines}**
        - Volume analisado: **{total_bytes} bytes**
        - Erros de sintaxe detectados: **{syntax_errors}**
        - Erros de leitura: **{read_errors}**
        - Arquivos sensíveis ignorados: **{len(skipped_sensitive)}**

        ## Finalidade

        Este pacote fornece estrutura, configurações sanitizadas, inventário de símbolos,
        dependências internas, alertas estatísticos e código-fonte consolidado para auditoria por IA.
        """
    )
    (out / "01_CONTEXTO.md").write_text(content, encoding="utf-8")


def write_structure(out: Path, root: Path, ignore: set[str]) -> None:
    lines = ["# ESTRUTURA", "", f"{root.name}/"]
    lines.extend(build_tree(root, root, out, ignore))
    (out / "02_ESTRUTURA.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def code_fence_language(path: Path) -> str:
    return {
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
        ".py": "python",
    }.get(path.suffix.lower(), "text")


def write_configurations(
    out: Path,
    root: Path,
    config_files: list[Path],
    sanitize: bool,
    max_bytes: int,
) -> dict[str, int]:
    report = {"sanitized_values": 0, "oversized_configs": 0, "read_errors": 0}

    with (out / "03_CONFIGURACOES.md").open("w", encoding="utf-8") as stream:
        stream.write("# CONFIGURAÇÕES\n\n")
        stream.write("As configurações abaixo foram sanitizadas quando necessário.\n")

        for path in config_files:
            relative = path.relative_to(root).as_posix()
            stream.write(f"\n\n---\n\n## `{relative}`\n\n")
            stream.write(f"- Tamanho: {path.stat().st_size} bytes\n")
            stream.write(f"- SHA-256: `{sha256_file(path)}`\n\n")

            if path.stat().st_size > max_bytes:
                report["oversized_configs"] += 1
                stream.write("[Conteúdo omitido por exceder o limite configurado.]\n")
                continue

            try:
                text, _ = read_text_safe(path)
            except (OSError, UnicodeError) as exc:
                report["read_errors"] += 1
                stream.write(f"[Erro ao ler: {type(exc).__name__}: {exc}]\n")
                continue

            if sanitize:
                text, replacements = sanitize_text(text)
                report["sanitized_values"] += replacements

            language = code_fence_language(path)
            stream.write(f"```{language}\n{text.rstrip()}\n```\n")

    return report


def format_symbol(symbol: SymbolInfo) -> str:
    interval = str(symbol.line)
    if symbol.end_line and symbol.end_line != symbol.line:
        interval = f"{symbol.line}-{symbol.end_line}"
    decorators = f" | decorators: {', '.join(symbol.decorators)}" if symbol.decorators else ""
    return f"- `{symbol.name}` ({symbol.kind}, linhas {interval}){decorators}"


def write_technical_summary(out: Path, analyses: list[FileAnalysis]) -> None:
    with (out / "04_RESUMO_TECNICO.md").open("w", encoding="utf-8") as stream:
        stream.write("# RESUMO TÉCNICO\n")

        for info in analyses:
            stream.write(f"\n\n---\n\n## `{info.path}`\n\n")
            stream.write(f"- Linhas: {info.lines}\n")
            stream.write(f"- Bytes: {info.bytes}\n")
            stream.write(f"- Codificação: `{info.encoding or '-'}`\n")
            stream.write(f"- SHA-256: `{info.sha256}`\n")

            if info.read_error:
                stream.write(f"- Erro de leitura: `{info.read_error}`\n")
            if info.syntax_error:
                stream.write(f"- Erro de sintaxe: `{info.syntax_error}`\n")

            stream.write("\n### Imports\n\n")
            if info.imports:
                stream.write("\n".join(f"- `{item}`" for item in info.imports) + "\n")
            else:
                stream.write("- Nenhum import detectado.\n")

            stream.write("\n### Classes\n\n")
            if info.classes:
                stream.write("\n".join(format_symbol(item) for item in info.classes) + "\n")
            else:
                stream.write("- Nenhuma classe detectada.\n")

            stream.write("\n### Funções e métodos\n\n")
            if info.functions:
                stream.write("\n".join(format_symbol(item) for item in info.functions) + "\n")
            else:
                stream.write("- Nenhuma função detectada.\n")

            if info.docstring:
                stream.write("\n### Docstring do módulo\n\n")
                stream.write(info.docstring.strip() + "\n")


def write_dependencies(out: Path, dependencies: dict[str, list[str]]) -> None:
    reverse: dict[str, list[str]] = defaultdict(list)
    for source, targets in dependencies.items():
        for target in targets:
            reverse[target].append(source)

    with (out / "05_DEPENDENCIAS.md").open("w", encoding="utf-8") as stream:
        stream.write("# DEPENDÊNCIAS INTERNAS\n\n")
        stream.write("Mapa aproximado baseado em imports estáticos analisáveis por AST.\n")

        for source in sorted(dependencies):
            stream.write(f"\n## `{source}`\n\n")
            targets = dependencies[source]
            if targets:
                stream.write("\n".join(f"- importa `{target}`" for target in targets) + "\n")
            else:
                stream.write("- Nenhuma dependência interna resolvida.\n")

        stream.write("\n# MÓDULOS INTERNOS MAIS REFERENCIADOS\n\n")
        ranking = sorted(reverse.items(), key=lambda item: len(item[1]), reverse=True)
        for target, sources in ranking:
            stream.write(f"- `{target}`: {len(sources)} consumidor(es)\n")


def write_alerts(out: Path, alerts: list[Alert]) -> None:
    severity_order = {"ALTA": 0, "MÉDIA": 1, "BAIXA": 2}
    alerts.sort(key=lambda item: (severity_order.get(item.severity, 9), item.path, item.line))

    with (out / "06_ALERTAS.md").open("w", encoding="utf-8") as stream:
        stream.write("# ALERTAS ESTATÍSTICOS\n\n")
        stream.write(
            "Alertas heurísticos para orientar revisão humana. Eles não provam que o código está incorreto.\n\n"
        )

        if not alerts:
            stream.write("Nenhum alerta heurístico encontrado.\n")
            return

        counts: dict[str, int] = defaultdict(int)
        for alert in alerts:
            counts[alert.severity] += 1

        stream.write("## Resumo\n\n")
        for severity in ("ALTA", "MÉDIA", "BAIXA"):
            stream.write(f"- {severity}: {counts[severity]}\n")

        stream.write("\n## Ocorrências\n")
        for alert in alerts:
            stream.write(
                f"\n- **{alert.severity}** | `{alert.category}` | "
                f"`{alert.path}:{alert.line}` | {alert.message}\n"
            )


def write_code_parts(
    out: Path,
    root: Path,
    parts: list[list[Path]],
    analyses_by_path: dict[str, FileAnalysis],
    sanitize: bool,
) -> dict[str, int]:
    report = {"sanitized_values": 0, "read_errors": 0}

    for index, paths in enumerate(parts, start=1):
        output_name = f"{6 + index:02d}_CODIGO_PARTE_{index}.md"
        with (out / output_name).open("w", encoding="utf-8") as stream:
            stream.write(f"# CÓDIGO PARTE {index}\n\n")
            stream.write(
                "Arquivos consolidados por afinidade de domínio, mantendo arquivos pequenos relacionados juntos.\n"
            )

            current_group = None
            for path in paths:
                group = module_group(path, root)
                if group != current_group:
                    stream.write(f"\n\n# GRUPO: {group}\n")
                    current_group = group

                relative = path.relative_to(root).as_posix()
                info = analyses_by_path[relative]
                stream.write(f"\n\n---\n\n## `{relative}`\n\n")
                stream.write(f"- Linhas: {info.lines}\n")
                stream.write(f"- SHA-256: `{info.sha256}`\n")
                stream.write(
                    f"- Classes: {', '.join(item.name for item in info.classes) or '-'}\n"
                )
                stream.write(
                    f"- Funções: {', '.join(item.name for item in info.functions) or '-'}\n\n"
                )

                try:
                    text, _ = read_text_safe(path)
                except (OSError, UnicodeError) as exc:
                    report["read_errors"] += 1
                    stream.write(f"[Erro ao ler: {type(exc).__name__}: {exc}]\n")
                    continue

                if sanitize:
                    text, replacements = sanitize_text(text)
                    report["sanitized_values"] += replacements

                stream.write(f"```python\n{text.rstrip()}\n```\n")

    return report


def write_manifest(
    out: Path,
    root: Path,
    analyses: list[FileAnalysis],
    config_files: list[Path],
    skipped_sensitive: list[Path],
    part_count: int,
    sanitization_enabled: bool,
    sanitization_count: int,
) -> None:
    manifest = {
        "generator": "gerar_contexto_ia.py",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_name": root.name,
        "project_root": str(root),
        "parts": part_count,
        "sanitization_enabled": sanitization_enabled,
        "sanitized_occurrences": sanitization_count,
        "python_files": [asdict(item) for item in analyses],
        "config_files": [
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in config_files
        ],
        "skipped_sensitive_files": [
            path.relative_to(root).as_posix() for path in skipped_sensitive
        ],
    }

    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    out = (args.out.resolve() if args.out else root / "AI_CONTEXT")
    ignore = set(DEFAULT_IGNORE)
    ignore.add(out.name)

    if args.partes < 1:
        raise ValueError("--partes deve ser maior ou igual a 1.")
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Raiz inválida: {root}")
    if out == root:
        raise ValueError("O diretório de saída não pode ser igual à raiz do projeto.")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    python_files, config_files, skipped_sensitive = discover_files(root, out, ignore)
    analyses = [analyze_python(path, root) for path in python_files]
    analyses_by_path = {item.path: item for item in analyses}

    alerts: list[Alert] = []
    for path in python_files:
        alerts.extend(scan_alerts(path, root))

    dependencies = detect_internal_dependencies(analyses, python_files, root)
    parts = distribute_semantically(python_files, root, args.partes)
    sanitize = not args.sem_sanitizacao

    write_readme(out, args.partes)
    write_context(out, root, python_files, config_files, analyses, skipped_sensitive)
    write_structure(out, root, ignore)
    config_report = write_configurations(
        out,
        root,
        config_files,
        sanitize=sanitize,
        max_bytes=args.max_config_bytes,
    )
    write_technical_summary(out, analyses)
    write_dependencies(out, dependencies)
    write_alerts(out, alerts)
    code_report = write_code_parts(out, root, parts, analyses_by_path, sanitize=sanitize)

    sanitization_count = (
        config_report["sanitized_values"] + code_report["sanitized_values"]
    )
    write_manifest(
        out,
        root,
        analyses,
        config_files,
        skipped_sensitive,
        args.partes,
        sanitize,
        sanitization_count,
    )

    print("Contexto para IA gerado com sucesso.")
    print(f"Saída: {out}")
    print(f"Python: {len(python_files)} arquivo(s)")
    print(f"Configurações: {len(config_files)} arquivo(s)")
    print(f"Partes de código: {args.partes}")
    print(f"Alertas: {len(alerts)}")
    print(f"Arquivos sensíveis ignorados: {len(skipped_sensitive)}")
    print(f"Ocorrências sanitizadas: {sanitization_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
