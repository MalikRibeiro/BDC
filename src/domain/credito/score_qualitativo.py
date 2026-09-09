"""Cálculo do score qualitativo para CPURA."""

from __future__ import annotations

from typing import Any

from common.texto import normalizar_texto
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_nota_auditoria(
    auditor: Any,
    auditor_para_nota: dict[str, str],
) -> str:
    """Converte o auditor em nota qualitativa."""
    auditor_normalizado = normalizar_texto(auditor)

    if not auditor_normalizado:
        raise PdInputValidationError("AUDITOR não informado.")

    nota = auditor_para_nota.get(auditor_normalizado)

    if nota is None:
        raise PdInputValidationError(
            f"AUDITOR sem mapeamento qualitativo: {auditor!r}"
        )

    return nota


def _obter_peso_nota(
    nota: Any,
    nota_para_peso: dict[str, Any],
    nome_campo: str,
) -> float:
    """Obtém o peso numérico da nota qualitativa."""
    nota_normalizada = normalizar_texto(nota)

    if not nota_normalizada:
        raise PdInputValidationError(
            f"{nome_campo} não informada."
        )

    if nota_normalizada not in nota_para_peso:
        raise PdInputValidationError(
            f"{nome_campo} inválida: {nota!r}"
        )

    try:
        return float(nota_para_peso[nota_normalizada])
    except (TypeError, ValueError) as exc:
        raise PdConfigurationError(
            f"Peso inválido para nota {nota_normalizada}."
        ) from exc


def calcular_score_qualitativo_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula o score qualitativo de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando score qualitativo CPURA. CNPJ=%s",
                registro.get("CNPJ"),
            )

        nota_para_peso = score_cpura_config.get("nota_para_peso")
        pesos_qualitativos = score_cpura_config.get("pesos_qualitativos")
        auditor_para_nota = score_cpura_config.get("auditor_para_nota")

        if not isinstance(nota_para_peso, dict):
            raise PdConfigurationError(
                "Bloco 'nota_para_peso' ausente ou inválido."
            )

        if not isinstance(pesos_qualitativos, dict):
            raise PdConfigurationError(
                "Bloco 'pesos_qualitativos' ausente ou inválido."
            )

        if not isinstance(auditor_para_nota, dict):
            raise PdConfigurationError(
                "Bloco 'auditor_para_nota' ausente ou inválido."
            )

        nota_board = registro.get("NOTA_BOARD")
        nota_bureau = registro.get("NOTA_BUREAU")
        auditor = registro.get("AUDITOR")

        nota_auditoria = _obter_nota_auditoria(
            auditor,
            auditor_para_nota,
        )

        peso_board = _obter_peso_nota(
            nota_board,
            nota_para_peso,
            "NOTA_BOARD",
        )
        peso_bureau = _obter_peso_nota(
            nota_bureau,
            nota_para_peso,
            "NOTA_BUREAU",
        )
        peso_auditoria = _obter_peso_nota(
            nota_auditoria,
            nota_para_peso,
            "NOTA_AUDITORIA",
        )

        try:
            w_board = float(pesos_qualitativos["BOARD"])
            w_auditoria = float(pesos_qualitativos["AUDITORIA"])
            w_bureau = float(pesos_qualitativos["BUREAU"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Peso qualitativo ausente: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                "Pesos qualitativos inválidos."
            ) from exc

        score_qualitativo = (
            w_board * peso_board
            + w_auditoria * peso_auditoria
            + w_bureau * peso_bureau
        )

        resultado = {
            "NOTA_AUDITORIA": nota_auditoria,
            "PESO_BOARD": peso_board,
            "PESO_AUDITORIA": peso_auditoria,
            "PESO_BUREAU": peso_bureau,
            "SCORE_QUALITATIVO": score_qualitativo,
        }

        if logger is not None:
            logger.info(
                "Score qualitativo CPURA calculado. "
                "CNPJ=%s SCORE_QUALITATIVO=%s",
                registro.get("CNPJ"),
                score_qualitativo,
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha no cálculo do score qualitativo CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )
        raise
