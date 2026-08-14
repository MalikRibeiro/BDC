"""Exceções do motor de probabilidade de default."""

from __future__ import annotations


class PdCalculationError(Exception):
    """Erro base do cálculo de PD ajustada."""


class PdInputValidationError(PdCalculationError):
    """Erro de validação dos insumos de PD."""


class PdConfigurationError(PdCalculationError):
    """Erro de configuração do motor de PD."""
