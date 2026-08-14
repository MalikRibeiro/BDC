"""Definição programática e tipada dos domínios de campos (Substitui os JSONs legados)."""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FieldTypeConfig:
    """Configuração dos tipos de campos para normalização estrutural."""
    entity: str
    date_fields: list[str] = field(default_factory=list)
    float_fields: list[str] = field(default_factory=list)
    text_fields: list[str] = field(default_factory=list)
    cnpj_fields: list[str] = field(default_factory=list)


COMERCIALIZADORAS_FIELD_TYPES = FieldTypeConfig(
    entity="fichas_comercializadoras",
    date_fields=[
        "DATA_DEMONSTRACAO_FINANCEIRA", "DATA_ADESAO_CCEE", 
        "DATA_CALCULO", "DATA_RATING_AGENCIA"
    ],
    float_fields=[
        "PATRIMONIO_LIQUIDO", "PROBABILIDADE_DEFAULT", "ATIVO_CIRCULANTE_FINANCEIRO",
        "CAPITAL_SOCIAL", "ATIVO_CIRCULANTE_AJUSTADO", "ATIVO_TOTAL_AJUSTADO",
        "PASSIVO_CIRCULANTE_AJUSTADO", "PASSIVO_CIRCULANTE_FINANCEIRO_AJUSTADO",
        "PASSIVO_NAO_CIRCULANTE_FINANCEIRO_AJUSTADO", "LUCROS_ACUMULADOS",
        "RESERVA_DE_LUCROS", "VENDAS_LIQUIDAS", "LUCRO_LIQUIDO",
        "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "LIQUIDEZ_CORRENTE_AJUSTADO",
        "INDICE_SOLVENCIA_GERAL_AJUSTADO", "INDICE_COBERTURA_DE_DESPESA_COM_PESSOAL",
        "PAYOUT_AJUSTADO", "CAPITAL_CIRCULANTE_LIQUIDO_AJUSTADO", "ROE", "ROA", "MFCO",
        "SCORE_BUREAU", "QUANTIDADE_RESTRITIVOS", "ROL", "LUCRO_BRUTO", "LAJIR", "LAIR",
        "PL_CONTROLADOR", "PERCENTUAL_CONTROLADOR"
    ],
    text_fields=[
        "CODIGO_CCEE", "SIGLA", "RATING_COPEL", "AGENCIA", "NOTA_CREDITO", "AUDITOR", 
        "NOTA_BOARD", "NOTA_BUREAU", "TIPO_COMERCIALIZADORA", "CONTROLADOR"
    ],
    cnpj_fields=[
        "CNPJ", "CNPJ_BBCE", "CNPJ_CONTROLADOR"
    ]
)

CONSUMIDORES_FIELD_TYPES = FieldTypeConfig(
    entity="fichas_consumidores",
    date_fields=[
        "DATA_DEMONSTRACAO_FINANCEIRA", "DATA_CALCULO", "DATA_ABERTURA", 
        "DATA_RATING_CONTROLADOR"
    ],
    float_fields=[
        "CAPITAL_SOCIAL", "ATIVO_CIRCULANTE", "ATIVO_CIRCULANTE_FINANCEIRO", "ATIVO_TOTAL",
        "PASSIVO_CIRCULANTE", "PASSIVO_CIRCULANTE_FINANCEIRO", "PASSIVO_NAO_CIRCULANTE_FINANCEIRO",
        "PATRIMONIO_LIQUIDO", "LUCROS_ACUMULADOS", "RESERVA_DE_LUCROS", "VENDAS_LIQUIDAS",
        "PROBABILIDADE_DEFAULT", "FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS", "MFCO", "ROA", "ROE",
        "ROL", "LUCRO_BRUTO", "LAJIR", "LAIR", "LUCRO_LIQUIDO", "SCORE_BUREAU", "QUANTIDADE_RESTRITIVOS",
        "PL_CONTROLADOR", "PERCENTUAL_CONTROLADOR", "CAPITAL_CIRCULANTE_LIQUIDO", "NECESSIDADE_CAPITAL_GIRO",
        "INDICE_AUTO_FINANCIAMENTO", "LIQUIDEZ_SECA", "INDICE_SOLVENCIA_GERAL", "MARGEM_LIQUIDA"
    ],
    text_fields=[
        "EMPRESA", "CEP", "ENDERECO", "AUDITOR", "AGENCIA", "NOTA_CREDITO", "NOTA_BOARD",
        "NOTA_BUREAU", "RATING_COPEL", "CONTROLADOR", "NOTA_CREDITO_CONTROLADOR", "AGENCIA_CONTROLADOR"
    ],
    cnpj_fields=[
        "CNPJ", "CNPJ_CONTROLADOR"
    ]
)

# Catálogo em memória que substitui a busca no disco
FIELD_TYPES_CATALOG = {
    "field_types_fichas_comercializadoras": COMERCIALIZADORAS_FIELD_TYPES,
    "field_types_fichas_consumidores": CONSUMIDORES_FIELD_TYPES,
}

def get_field_type_config(slug: str) -> Optional[FieldTypeConfig]:
    """Retorna a configuração de tipagem em memória correspondente ao slug."""
    return FIELD_TYPES_CATALOG.get(slug)