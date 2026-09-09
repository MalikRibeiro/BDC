import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from common.texto import normalizar_texto
from domain.fichas.extrator import LeitorPlanilha, avaliar_vencedor_por_grid, busca_omnidirecional, _tipo_extraido_valido

def test_contrato_normalizar_texto_caixa_alta():
    resultado = normalizar_texto(" Dem.Fin. ", caixa_alta=True)
    assert resultado == "DEM.FIN."

def test_leitor_planilha_em_memoria():
    grid = {
        "Planilha1": [
            ("A", "B", "C"),
            ("CNPJ", "12345678000195", None)
        ]
    }
    leitor = LeitorPlanilha(grid, "Planilha1")
    val = leitor.ler_celula("Planilha1", "B2")
    assert val == "12345678000195"

def test_busca_omnidirecional_mock():
    grid = {
        "DRE": [
            ("RECEITA LÍQUIDA", 5000.50),
            ("LUCRO LÍQUIDO", 1200.00)
        ]
    }
    leitor = LeitorPlanilha(grid, "DRE")
    val, meta = busca_omnidirecional(leitor, r"RECEITA\s*L[IÍ]QUIDA", "float", field_name="RECEITA_LIQUIDA")
    assert val == 5000.5
    assert meta["aba_origem"] == "DRE"

def test_tipo_extraido_valido_regras():
    # Passivo não pode ser zero? O validador checa
    assert _tipo_extraido_valido(0.0, "float", "ativo_total") == False
    assert _tipo_extraido_valido(100.0, "float", "ativo_total") == True
    # PD tem que ser entre 0 e 1
    assert _tipo_extraido_valido(1.5, "float", "pd") == False
    assert _tipo_extraido_valido(0.05, "float", "pd") == True

def test_avaliar_vencedor_por_grid_sem_planilha():
    grid = {
        "Dados Gerais e Qualitativos": [
            ("CNPJ", "12345678000195"),
            ("DATA DA DF", "2024-12-31")
        ]
    }
    leitor = LeitorPlanilha(grid, "Dados Gerais e Qualitativos")
    
    layouts = {
        "LAYOUT_TESTE": {
            "field_map": {
                "CNPJ": {"type": "string"},
                "DATA_DEMONSTRACAO_FINANCEIRA": {"type": "date"}
            }
        }
    }
    
    dados, meta, nome = avaliar_vencedor_por_grid(leitor, layouts)
    assert nome == "LAYOUT_TESTE"
    assert dados["CNPJ"] == "12345678000195"
    assert "INTEGRIDADE_EXTRAIDA_PERCENTUAL" in dados