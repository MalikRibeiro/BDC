import sys
from pathlib import Path

# Adiciona o diretório 'src' ao sys.path para que os testes encontrem os módulos
src_dir = str(Path(__file__).parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
