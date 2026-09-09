import json
from pathlib import Path
from typing import Any

def anexar_registro_de_manifesto(file_path: str, record: dict[str, Any]) -> None:
    """Anexa um novo manifesto em formato JSON Lines ao histórico."""
    target = Path(file_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    
    with target.open("a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

def historico_de_ingestao_de_carga(file_path: Path) -> list[dict[str, Any]]:
    """Lê o histórico completo de ingestão em formato JSONL."""
    history = []
    if not file_path.exists():
        return history
    
    with file_path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if line.strip():
                try:
                    history.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return history