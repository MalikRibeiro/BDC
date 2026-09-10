import json
import os

BASE_DIR = r"c:\Users\C807951\Desktop\BDC\ENTRADAS\control"

f_master = os.path.join(BASE_DIR, "quality", "master_catalog_comercializadoras.json")
f_schema = os.path.join(BASE_DIR, "schemas", "schema_ficha_comercializadora_extraida.json")
f_mapping = os.path.join(BASE_DIR, "mappings", "mapping_fichas_comercializadoras.json")

def restore_data_calculo():
    # 1. Master Catalog
    with open(f_master, "r", encoding="utf-8") as f:
        master = json.load(f)
        
    master["fields"]["DATA_CALCULO"] = {
        "nature": "OBSERVED",
        "type": "date",
        "criticality": "OPTIONAL",
        "weight": 10,
        "search_patterns": ["DATA\\s*DA\\s*FICHA"]
    }
        
    with open(f_master, "w", encoding="utf-8") as f:
        json.dump(master, f, indent=4, ensure_ascii=False)
        
    # 2. Schema
    with open(f_schema, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    schema["properties"]["DATA_CALCULO"] = {
        "type": ["string", "null"]
    }
        
    with open(f_schema, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4, ensure_ascii=False)
        
    # 3. Mapping
    with open(f_mapping, "r", encoding="utf-8") as f:
        mapping = json.load(f)
        
    if not any(m.get("RUBRICAS") == "DATA_CALCULO" for m in mapping):
        novo_map = {
            "RUBRICAS": "DATA_CALCULO",
            "ABA_PADRAO_1": "V0",
            "CELULA_RUBRICA_PADRAO_1": "B5",
            "CELULA_PADRAO_1": "E5",
            "ABA_PADRAO_2": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_2": "A1",
            "CELULA_PADRAO_2": "E1",
            "ABA_PADRAO_3": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_3": "C7",
            "CELULA_PADRAO_3": "D7",
            "ABA_PADRAO_4": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_4": "C9",
            "CELULA_PADRAO_4": "D9",
            "ABA_PADRAO_5": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_5": "C8",
            "CELULA_PADRAO_5": "D8",
            "ABA_PADRAO_6": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_6": "C7",
            "CELULA_PADRAO_6": "D7",
            "ABA_PADRAO_7": "FichaIndividual",
            "CELULA_RUBRICA_PADRAO_7": "C7",
            "CELULA_PADRAO_7": "D7"
        }
        mapping.append(novo_map)
            
    with open(f_mapping, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    restore_data_calculo()
    print("DATA_CALCULO RESTAURADA COM SUCESSO!")
