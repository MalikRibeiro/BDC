
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
