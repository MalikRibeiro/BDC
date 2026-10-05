"""Cálculo das notas quantitativas de CPURA."""

from __future__ import annotations

from typing import Any

from common.numeros import to_float_br
from domain.credito.pd_exceptions import (
    PdConfigurationError,
    PdInputValidationError,
)


def _obter_valor_numerico(
    registro: dict[str, Any],
    campo: str,
) -> float:
    """Obtém e valida um valor numérico do registro."""
    valor = to_float_br(registro.get(campo))

    if valor is None:
        raise PdInputValidationError(
            f"{campo} não informado."
        )

    return float(valor)


def _normalizar_pd(valor: float) -> float:
    """Normaliza PD para escala decimal [0, 1]."""
    if valor < 0:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT negativa: {valor}"
        )

    if valor > 1:
        valor = valor / 100.0

    if valor > 1:
        raise PdInputValidationError(
            f"PROBABILIDADE_DEFAULT fora do intervalo após normalização: {valor}"
        )

    return valor


def _obter_faixas_notas(
    score_cpura_config: dict[str, Any],
    indicador: str,
) -> list[dict[str, Any]]:
    """Obtém as faixas de notas de um indicador."""
    faixas_root = score_cpura_config.get("faixas_notas_quantitativas")

    if not isinstance(faixas_root, dict):
        raise PdConfigurationError(
            "Bloco 'faixas_notas_quantitativas' ausente ou inválido."
        )

    faixas = faixas_root.get(indicador)

    if not isinstance(faixas, list) or not faixas:
        raise PdConfigurationError(
            f"Faixas quantitativas ausentes ou inválidas para {indicador}."
        )

    return faixas


def _atribuir_nota_por_faixa(
    valor: float,
    faixas: list[dict[str, Any]],
    indicador: str,
) -> str:
    """Atribui nota A-E conforme a faixa parametrizada."""
    for faixa in faixas:
        try:
            nota = str(faixa["nota"]).strip().upper()
            minimo = float(faixa["min"])
            maximo = float(faixa["max"])
        except KeyError as exc:
            raise PdConfigurationError(
                f"Faixa incompleta em {indicador}: {exc}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise PdConfigurationError(
                f"Faixa inválida em {indicador}."
            ) from exc

        if minimo > maximo:
            raise PdConfigurationError(
                f"Faixa inválida em {indicador}: min > max."
            )

        if minimo <= valor <= maximo:
            return nota

    raise PdInputValidationError(
        f"Valor sem faixa configurada para {indicador}: {valor}"
    )


def calcular_notas_quantitativas_cpura(
    registro: dict[str, Any],
    score_cpura_config: dict[str, Any],
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula as notas quantitativas de CPURA."""
    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo das notas quantitativas CPURA. "
                "CNPJ=%s",
                registro.get("CNPJ"),
            )

        # 1. PD Base: calculado via Z-Score ou fallback soberano da ficha (B26)
        pd_raw = registro.get("PD_BASE")
        if pd_raw is None or to_float_br(pd_raw) is None:
            pd_raw = registro.get("PROBABILIDADE_DEFAULT")
        pd_num = to_float_br(pd_raw)
        if pd_num is None:
            raise PdInputValidationError("PD_BASE ou PROBABILIDADE_DEFAULT não informado.")
        pd_valor = _normalizar_pd(float(pd_num))

        # 2. FCO / ROL: extraído diretamente (B27) ou calculado a partir dos campos da DRE
        fco_rol_raw = registro.get("FCO_ROL")
        if fco_rol_raw is not None and to_float_br(fco_rol_raw) is not None:
            fco_rol_valor = float(to_float_br(fco_rol_raw))
        else:
            fco_raw = (
                registro.get("FCO") or
                registro.get("FLUXO_DE_CAIXA_DAS_ATIVIDADES_OPERACIONAIS") or
                registro.get("FLUXO_CAIXA_OP")
            )
            rol_raw = (
                registro.get("ROL") or
                registro.get("VENDAS_LIQUIDAS") or
                registro.get("RECEITA_OPERACIONAL_LIQUIDA")
            )
            fco_val = to_float_br(fco_raw)
            rol_val = to_float_br(rol_raw)
            if fco_val is not None and rol_val is not None:
                fco_rol_valor = (float(fco_val) / float(rol_val)) if float(rol_val) != 0 else 0.0
            else:
                raise PdInputValidationError("FCO_ROL ou (FCO e ROL) não informados.")

        # 3. ROE: extraído diretamente (B29) ou derivado de Lucro Líquido / Patrimônio Líquido
        roe_raw = registro.get("ROE")
        if roe_raw is not None and to_float_br(roe_raw) is not None:
            roe_valor = float(to_float_br(roe_raw))
        else:
            ll_val = to_float_br(registro.get("LUCRO_LIQUIDO"))
            pl_val = to_float_br(registro.get("PATRIMONIO_LIQUIDO"))
            if ll_val is not None and pl_val is not None and float(pl_val) != 0:
                roe_valor = float(ll_val) / float(pl_val)
            else:
                raise PdInputValidationError("ROE ou (LUCRO_LIQUIDO e PATRIMONIO_LIQUIDO) não informados.")

        # 4. ROA: extraído diretamente (B28) ou derivado de Lucro Líquido / Ativo Total
        roa_raw = registro.get("ROA")
        if roa_raw is not None and to_float_br(roa_raw) is not None:
            roa_valor = float(to_float_br(roa_raw))
        else:
            ll_val = to_float_br(registro.get("LUCRO_LIQUIDO"))
            at_val = to_float_br(registro.get("ATIVO_TOTAL"))
            if ll_val is not None and at_val is not None and float(at_val) != 0:
                roa_valor = float(ll_val) / float(at_val)
            else:
                raise PdInputValidationError("ROA ou (LUCRO_LIQUIDO e ATIVO_TOTAL) não informados.")

        segmento = str(registro.get("SEGMENTO_PD", "")).strip().upper()
        indicador_pd = "PD_CONSUMIDOR_GT_5" if segmento == "CONSUMIDOR_GT_5" else "PD"

        nota_pd = _atribuir_nota_por_faixa(
            valor=pd_valor,
            faixas=_obter_faixas_notas(score_cpura_config, indicador_pd),
            indicador="PD",
        )
        nota_fco_rol = _atribuir_nota_por_faixa(
            valor=fco_rol_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "FCO_ROL"),
            indicador="FCO_ROL",
        )
        nota_roe = _atribuir_nota_por_faixa(
            valor=roe_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "ROE"),
            indicador="ROE",
        )
        nota_roa = _atribuir_nota_por_faixa(
            valor=roa_valor,
            faixas=_obter_faixas_notas(score_cpura_config, "ROA"),
            indicador="ROA",
        )

        resultado = {
            "NOTA_PD": nota_pd,
            "NOTA_FCO_ROL": nota_fco_rol,
            "NOTA_ROE": nota_roe,
            "NOTA_ROA": nota_roa,
        }

        if logger is not None:
            logger.info(
                "Notas quantitativas CPURA calculadas. "
                "CNPJ=%s NOTA_PD=%s NOTA_FCO_ROL=%s NOTA_ROE=%s NOTA_ROA=%s",
                registro.get("CNPJ"),
                resultado["NOTA_PD"],
                resultado["NOTA_FCO_ROL"],
                resultado["NOTA_ROE"],
                resultado["NOTA_ROA"],
            )

        return resultado

    except Exception:
        if logger is not None:
            logger.warning("Falha no cálculo das notas quantitativas CPURA (Insumo Pendente). CNPJ=%s", registro.get('CNPJ'))
        raise
