"""Modelo de dados formal para o domínio de Garantias."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class GarantiaModel:
    garantia_id: str
    cnpj_contraparte: str
    grupo_economico: Optional[str]
    contrato_vinculado: Optional[str]
    tipo: Optional[str]
    modalidade: Optional[str]
    garantidor_emissor: Optional[str]
    cnpj_garantidor: Optional[str]
    instituicao_financeira: Optional[str]
    beneficiario: Optional[str]
    valor_nominal: Optional[float]
    valor_atualizado: Optional[float]
    moeda: Optional[str]
    data_avaliacao: Optional[str]
    percentual_cobertura: Optional[float]
    data_inicio: Optional[str]
    vencimento: Optional[str]
    status: str
    elegibilidade: str
    data_ultima_validacao: Optional[str]