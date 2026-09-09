import os
from pathlib import Path

def main():
    # 1. Delete field_types
    file_path = Path(r"c:\Users\C807951\Desktop\BDC\ENTRADAS\control\quality\field_types_fichas_consumidores.json")
    if file_path.exists():
        file_path.unlink()
        print(f"Arquivo removido com sucesso: {file_path}")
    else:
        print(f"Arquivo não encontrado: {file_path}")

    # 2. Delete pd_transform_rules old location
    old_rules_file = Path(r"c:\Users\C807951\Desktop\BDC\ENTRADAS\control\rules\pd_transform_rules.json")
    if old_rules_file.exists():
        old_rules_file.unlink()
        print(f"Arquivo legado removido com sucesso: {old_rules_file}")
    
    # 3. Delete rules folder if empty
    rules_dir = Path(r"c:\Users\C807951\Desktop\BDC\ENTRADAS\control\rules")
    if rules_dir.exists() and not any(rules_dir.iterdir()):
        rules_dir.rmdir()
        print(f"Diretório removido com sucesso: {rules_dir}")

if __name__ == "__main__":
    main()
