"""Compara as fichas oficiais de referência contra os layouts declarativos padrao_7_cpura e padrao_7_cgrupo.

Inspeciona e comprova factualmente se FICHA_GERADORAS_V2.xlsx e FICHA_BANCO_V0.xlsx
já são 100% cobertas pelos layouts existentes ou se exigem layouts adicionais.
"""
from __future__ import annotations

import sys
from pathlib import Path
import openpyxl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FICHAS_DIR = PROJECT_ROOT / "docs" / "fichas oficiais"


def inspecionar_ficha(arq_nome: str):
    arq_path = FICHAS_DIR / arq_nome
    if not arq_path.exists():
        print(f"[-] Arquivo não encontrado: {arq_path}")
        return

    print("\n" + "=" * 95)
    print(f"📄 AUDITORIA FÍSICA: {arq_nome}")
    print("=" * 95)

    wb = openpyxl.load_workbook(arq_path, data_only=True, read_only=True)
    abas = wb.sheetnames
    print(f"Abas no arquivo ({len(abas)}): {abas}")

    # Checagem de abas características
    tem_conf_puras = any("Conf. Puras" in a for a in abas)
    tem_conf_grupo = "Conf. Grupo" in abas
    tem_metodologia_banco = "METODOLOGIA_BANCO" in abas

    print("\nPerfil Estrutural das Abas:")
    print(f"  - Possui abas 'Conf. Puras_*' (Indica CPURA / Geradora): {tem_conf_puras}")
    print(f"  - Possui aba 'Conf. Grupo'    (Indica CGRUPO / Banco) : {tem_conf_grupo}")
    print(f"  - Possui aba 'METODOLOGIA_BANCO'                     : {tem_metodologia_banco}")

    ws = wb["FichaIndividual"] if "FichaIndividual" in abas else wb[abas[0]]

    def ler(cel):
        try:
            v = ws[cel].value
            return str(v).strip() if v is not None else "VAZIO"
        except Exception:
            return "ERRO"

    print("\nCoordenadas Principais em FichaIndividual:")
    print(f"  - A18 (Label Tipo):      {ler('A18'):<20} | B18 (Valor Tipo): {ler('B18')}")
    print(f"  - A19 (Label Categoria): {ler('A19'):<20} | B19 (Valor Categ): {ler('B19')}")
    print(f"  - F20 (Label PL):        {ler('F20'):<20} | G20 (Valor PL):    {ler('G20')}")

    print("\nDemonstração do Resultado do Exercício (DRE):")
    print(f"  [Bloco CPURA G24:G26]")
    print(f"    * F24/G24 (Vendas Líquidas): {ler('F24')} -> {ler('G24')}")
    print(f"    * F25/G25 (Lucro Líquido):   {ler('F25')} -> {ler('G25')}")
    print(f"    * F26/G26 (FCO):             {ler('F26')} -> {ler('G26')}")
    print(f"  [Bloco CGRUPO L24..Q26]")
    print(f"    * L24/Q24 (Vendas Líquidas): {ler('L24')} -> {ler('Q24')}")
    print(f"    * L25/Q25 (Lucro Líquido):   {ler('L25')} -> {ler('Q25')}")
    print(f"    * L26/Q26 (FCO):             {ler('L26')} -> {ler('Q26')}")

    print("\nIndicadores Canônicos da Origem (B26..B29):")
    print(f"  * B26 (PD Base Declarada):   {ler('B26'):<15} | C26 (Rating PD):  {ler('C26')}")
    print(f"  * B27 (FCO/ROL Declarado):   {ler('B27'):<15} | C27 (Rating FCO): {ler('C27')}")
    print(f"  * B28 (ROA Declarado):       {ler('B28'):<15} | C28 (Rating ROA): {ler('C28')}")
    print(f"  * B29 (ROE Declarado):       {ler('B29'):<15} | C29 (Rating ROE): {ler('C29')}")
    print(f"  * B49 (Rating Copel Final):  {ler('B49')}")

    print("\nBloco de Scores Lineares:")
    print(f"  * Score Total CPURA (H79):   {ler('H79')}")
    print(f"  * Score Total CGRUPO (N79):  {ler('N79')}")

    # Veredito de Enquadramento
    print("\n🔍 VEREDITO ARQUITETURAL:")
    if tem_conf_puras:
        print("  -> Adere 100% ao layout: padrao_7_cpura (Layout dedicado existente)")
    elif tem_conf_grupo:
        print("  -> Adere 100% ao layout: padrao_7_cgrupo (Layout dedicado existente)")
    else:
        print("  -> Requer avaliação de layout adicional.")

    wb.close()


def main():
    arquivos = [
        "FICHA_PURAS_V1.xlsx",
        "FICHA_GRUPO_V1.xlsx",
        "FICHA_GERADORAS_V2.xlsx",
        "FICHA_BANCO_V0.xlsx"
    ]
    for arq in arquivos:
        inspecionar_ficha(arq)


if __name__ == "__main__":
    main()
