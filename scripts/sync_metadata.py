import json
import os
import copy

BASE_DIR = r"c:\Users\C807951\Desktop\BDC\ENTRADAS\control"

f_master = os.path.join(BASE_DIR, "quality", "master_catalog_comercializadoras.json")
f_schema = os.path.join(BASE_DIR, "schemas", "schema_ficha_comercializadora_extraida.json")
f_mapping = os.path.join(BASE_DIR, "mappings", "mapping_fichas_comercializadoras.json")

campos_remover = [
    "DATA_CALCULO", "DATA_ABERTURA", "CEP", "ENDERECO", "AGENCIA", "DATA_RATING_AGENCIA", 
    "LUCRO_BRUTO", "LAJIR", "LAIR", "CONTROLADOR", "CNPJ_CONTROLADOR", "PL_CONTROLADOR", "PERCENTUAL_CONTROLADOR"
]

campos_injetar = {
    "CNPJ_BBCE": {"type": "string", "regex": ["CNPJ\\s*BBCE", "BBCE"]},
    "CODIGO_CCEE": {"type": "string", "regex": ["C[OÓ]DIGO\\s*CCEE", "CCEE"]},
    "DATA_ADESAO_CCEE": {"type": "date", "regex": ["DATA\\s*ADES[AÃ]O", "ADES[AÃ]O\\s*CCEE"]},
    "MATURIDADE_CALCULADA": {"type": "float", "regex": ["MATURIDADE", "MATURIDADE\\s*CALCULADA"]},
    "CATEGORIA": {"type": "string", "regex": ["CATEGORIA"]},
    "RATING_PUBLICO": {"type": "string", "regex": ["RATING\\s*P[UÚ]BLICO", "RATING\\s*AG[EÊ]NCIA"]},
    "SCORES_INDIVIDUAIS": {"type": "string", "regex": ["SCORES\\s*INDIVIDUAIS"]},
    "SCORE_QUANTITATIVO": {"type": "float", "regex": ["SCORE\\s*QUANTITATIVO", "SCORE\\s*QUANT"]},
    "DEMONSTRACOES_FINANCEIRAS_AUDITADAS": {"type": "string", "regex": ["DEMONSTRA[CÇ][OÕ]ES.*AUDITADAS", "DF.*AUDITADA"]},
    "RATING_SCORE_DE_AUDITORIA": {"type": "string", "regex": ["RATING.*AUDITORIA", "SCORE.*AUDITORIA"]},
    "RATING_SCORE_DE_BUREAU": {"type": "string", "regex": ["RATING.*BUREAU", "SCORE.*BUREAU"]},
    "RESTRITIVOS": {"type": "string", "regex": ["RESTRITIVOS", "APONTA.*RESTRITIVOS"]},
    "SCORE_QUALITATIVO": {"type": "float", "regex": ["SCORE\\s*QUALITATIVO", "SCORE\\s*QUAL"]},
    "MARGEM_DESPESA_PESSOAL": {"type": "float", "regex": ["MARGEM\\s*DESPESA", "RECEITA.*CUSTO.*PESSOAL"]},
    "MTM_TOTAL_PL": {"type": "float", "regex": ["MTM.*PL", "MTM.*PATRIM[OÔ]NIO"]},
    "DIVIDENDOS_LUCRO_LIQUIDO": {"type": "float", "regex": ["DIVIDENDOS.*LUCRO", "JCP.*LUCRO"]},
    "CAPITAL_CIRCULANTE_LIQUIDO": {"type": "float", "regex": ["CAPITAL\\s*CIRCULANTE\\s*L[IÍ]QUIDO", "CCL\\b"]}
}

def clean_and_inject():
    # 1. Master Catalog
    with open(f_master, "r", encoding="utf-8") as f:
        master = json.load(f)
        
    for c in campos_remover:
        if c in master["fields"]:
            del master["fields"][c]
            
    for c, meta in campos_injetar.items():
        master["fields"][c] = {
            "nature": "OBSERVED",
            "type": meta["type"],
            "criticality": "OPTIONAL",
            "weight": 10,
            "allow_semantic": True,
            "search_patterns": meta["regex"]
        }
        
    with open(f_master, "w", encoding="utf-8") as f:
        json.dump(master, f, indent=4, ensure_ascii=False)
        
    # 2. Schema
    with open(f_schema, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    for c in campos_remover:
        if c in schema["properties"]:
            del schema["properties"][c]
            
    for c, meta in campos_injetar.items():
        json_type = "number" if meta["type"] == "float" else "string"
        schema["properties"][c] = {"type": [json_type, "null"]}
        
    with open(f_schema, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4, ensure_ascii=False)
        
    # 3. Mapping
    with open(f_mapping, "r", encoding="utf-8") as f:
        mapping = json.load(f)
        
    mapping = [m for m in mapping if m.get("RUBRICAS") not in campos_remover]
    
    for c in campos_injetar.keys():
        if not any(m.get("RUBRICAS") == c for m in mapping):
            novo_map = {"RUBRICAS": c}
            for i in range(1, 8):
                novo_map[f"ABA_PADRAO_{i}"] = "0"
                novo_map[f"CELULA_RUBRICA_PADRAO_{i}"] = "0"
                novo_map[f"CELULA_PADRAO_{i}"] = "0"
            mapping.append(novo_map)
            
    with open(f_mapping, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    clean_and_inject()
    print("ARQUIVOS JSON ATUALIZADOS COM SUCESSO!")
