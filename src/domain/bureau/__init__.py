"""Domínio de Bureau de Crédito (RISK3).

Fachada de integração com o serviço de bureau de crédito externo.
"""

from domain.cadastro.servico_bureau import inserir_dados_bureau
from services.connectors.risk3_connector import buscar_bureau_risk3

__all__ = ["buscar_bureau_risk3", "inserir_dados_bureau"]
