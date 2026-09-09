import json
import logging
import openpyxl
from pathlib import Path
import sys
base_dir = Path(r"c:\Users\C807951\Desktop\BDC")
sys.path.insert(0, str(base_dir))
sys.path.insert(0, str(base_dir / "src"))
from domain.fichas.extrator import LeitorPlanilha, extrair_registro

logging.basicConfig(level=logging.ERROR)

def main():
    processadas_dir = base_dir / "ENTRADAS" / "fichas" / "comercializadoras" / "processadas"
    
    # Carrega master catalog
    catalog_path = base_dir / "ENTRADAS" / "control" / "quality" / "master_catalog_comercializadoras.json"
    with open(catalog_path, "r", encoding="utf-8") as f:
        master_catalog = json.load(f)
        
    # Amostras para testar
    amostras = {
        "padrao_2": "TRADENER 29_08_2022.xlsx",
        "padrao_4": "BOENERGY_08052023.xlsx"
    }
    
    print("="*80)
    print("TESTE A/B: EXTRAÇÃO COM VS SEM SEMÂNTICA (REGEX)")
    print("="*80)
    
    for padrao, arquivo in amostras.items():
        print(f"\n[{padrao}] Arquivo: {arquivo}")
        
        # Carrega o layout correspondente
        layout_path = base_dir / "ENTRADAS" / "control" / "layouts" / f"layout_ficha_comercializadora_v{padrao[-1]}.json"
        with open(layout_path, "r", encoding="utf-8") as f:
            layout_schema = json.load(f)
            
        caminho_arquivo = processadas_dir / arquivo
        if not caminho_arquivo.exists():
            print(f"  -> Arquivo {arquivo} não encontrado na pasta processadas.")
            continue
            
        # Carrega a planilha na memória
        wb = openpyxl.load_workbook(caminho_arquivo, data_only=True)
        leitor = LeitorPlanilha.do_workbook(wb)
        
        # TESTE 1: REGRA ANTIGA (Sem Semântica)
        dados_antigo, _ = extrair_registro(leitor, layout_schema, master_catalog, allow_semantic=False)
        lucro_antigo = dados_antigo.get("LUCRO_LIQUIDO")
        
        # TESTE 2: REGRA NOVA (Com Semântica Forçada)
        # Atenção: Precisamos garantir que o campo tem search_pattern no layout!
        dados_novo, _ = extrair_registro(leitor, layout_schema, master_catalog, allow_semantic=True)
        lucro_novo = dados_novo.get("LUCRO_LIQUIDO")
        
        print(f"  -> ANTES  (Semântica OFF): LUCRO_LIQUIDO = {lucro_antigo}")
        print(f"  -> DEPOIS (Semântica ON) : LUCRO_LIQUIDO = {lucro_novo}")

if __name__ == "__main__":
    main()
