from __future__ import annotations

from typing import Any

from domain.credito.notas_quantitativas_cpura import (
    calcular_notas_quantitativas_cpura,
)
from domain.credito.pd_base import calcular_pd_base
from domain.credito.pd_exceptions import (
    PdCalculationError,
    PdConfigurationError,
)
from domain.credito.pd_transform import transformar_pd_por_segmento
from domain.credito.pd_validator import validar_insumos_pd, _is_blank
from datetime import datetime
import hashlib
import json
def _is_expired(data_str: Any, dias_validade: int) -> bool:
    if data_str is None or _is_blank(data_str):
        return True
    try:
        import pandas as _pd
        dt = _pd.to_datetime(data_str, errors="coerce")
        if _pd.isna(dt):
            return True
        idade_dias = (datetime.now() - dt.to_pydatetime()).days
        return idade_dias > dias_validade
    except Exception:
        return True
from domain.credito.rating import calcular_rating_final
from domain.credito.score_qualitativo import calcular_score_qualitativo_cpura
from domain.credito.score_quantitativo import calcular_score_quantitativo_cpura
from domain.credito.score_total import calcular_score_total_cpura
from common.texto import normalizar_texto


def calcular_pd_ajustada(
    registro: dict[str, Any],
    pd_faixas: dict[str, Any],
    pd_transform_rules: dict[str, Any] | None = None,
    pd_cpura_config: dict[str, Any] | None = None,
    score_cpura_config: dict[str, Any] | None = None,
    pd_zscore_config: dict[str, Any] | None = None,
    peer_group: list[float] | None = None,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Calcula a PD ajustada/final da contraparte."""
    segmento_pd = str(registro.get("SEGMENTO_PD", "")).strip().upper()
    config_usada = {
        "pd_faixas": pd_faixas,
        "pd_transform_rules": pd_transform_rules,
        "pd_cpura_config": pd_cpura_config,
        "score_cpura_config": score_cpura_config,
        "pd_zscore_config": pd_zscore_config,
    }
    config_snapshot_id = hashlib.sha256(
        json.dumps(config_usada, sort_keys=True).encode()
    ).hexdigest()[:16]

    try:
        if logger is not None:
            logger.info(
                "Iniciando cálculo de PD ajustada. "
                "CNPJ=%s SEGMENTO_PD=%s",
                registro.get("CNPJ"),
                segmento_pd,
            )

        # --- FAIL-SAFE DE RECUPERACAO JUDICIAL ---
        if str(registro.get("RECUPERACAO_JUDICIAL", "")).strip().upper() == "SIM":
            if logger is not None:
                logger.warning("Curto-circuito: RJ acionada para CNPJ=%s", registro.get("CNPJ"))
            data_df = registro.get("DATA_DEMONSTRACAO_FINANCEIRA")
            data_bureau = registro.get("DATA_BUREAU") or registro.get("DATA_CONSULTA")
            import pandas as _pd
            fim_vig_rj = None
            if segmento_pd == "CONSUMIDOR_LE_5" and data_bureau:
                dt_b = _pd.to_datetime(data_bureau, errors="coerce")
                if not _pd.isna(dt_b):
                    fim_vig_rj = (dt_b + _pd.DateOffset(months=12)).strftime("%Y-%m-%d")
            elif data_df:
                dt_d = _pd.to_datetime(data_df, errors="coerce")
                if not _pd.isna(dt_d):
                    fim_vig_rj = (dt_d + _pd.DateOffset(months=18)).strftime("%Y-%m-%d")
            return {
                "SEGMENTO_PD": segmento_pd,
                "STATUS_CALCULO_PD": "RECUPERACAO_JUDICIAL",
                "PD_BASE": None,
                "PD_FINAL": 1.0,
                "RATING_FINAL": "E",
                "PD_METODO": "OVERRIDE_RECUPERACAO_JUDICIAL",
                "CONFIG_SNAPSHOT_PD": config_snapshot_id,
                "FIM_VIGENCIA_ANALISE": fim_vig_rj
            }

        validar_insumos_pd(registro, segmento_pd)

        # --- VALIDADE DAS INFORMACOES (METADADOS DE GOVERNANCA) ---
        data_df = registro.get("DATA_DEMONSTRACAO_FINANCEIRA")
        data_bureau = registro.get("DATA_BUREAU") or registro.get("DATA_CONSULTA")
        data_rating = registro.get("DATA_RATING_PUBLICO") or registro.get("DATA_RATING_AGENCIA")
        
        import pandas as _pd
        def _calcular_validade_meses(data_val: Any, meses: int) -> str | None:
            if data_val is None or _is_blank(data_val):
                return None
            try:
                dt = _pd.to_datetime(data_val, errors="coerce")
                if _pd.isna(dt):
                    return None
                return (dt + _pd.DateOffset(months=meses)).strftime("%Y-%m-%d")
            except Exception:
                return None

        # Validades específicas
        validade_df = _calcular_validade_meses(data_df, 18)
        validade_bureau = _calcular_validade_meses(data_bureau, 4 if segmento_pd == "CPURA" else 12)
        validade_rating = _calcular_validade_meses(data_rating, 18)

        # Regra canônica de FIM_VIGENCIA_ANALISE por metodologia:
        # - Bureau (Consumidor <= 5MWm): 12 meses a partir da data de consulta/bureau
        # - DF (Comercializadoras e Consumidor > 5MWm): 18 meses a partir da demonstração financeira
        if segmento_pd == "CONSUMIDOR_LE_5" or str(registro.get("TIPO_ANALISE", "")).strip().startswith("Análise Bureau"):
            fim_vigencia_analise = _calcular_validade_meses(data_bureau, 12)
        else:
            fim_vigencia_analise = _calcular_validade_meses(data_df, 18)

        pd_base = calcular_pd_base(registro, segmento_pd, pd_zscore_config, logger)

        registro_calculo = dict(registro)
        registro_calculo["PD_BASE"] = pd_base

        resultado_scores: dict[str, Any] = {}

        if segmento_pd in ("CPURA", "CONSUMIDOR_GT_5"):
            if not score_cpura_config:
                raise PdConfigurationError(
                    f"score_cpura_config não informado para {segmento_pd}."
                )

            if not pd_cpura_config:
                raise PdConfigurationError(
                    "pd_cpura_config não informado para CPURA."
                )



            notas_quant_info = calcular_notas_quantitativas_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(notas_quant_info)

            score_qual_info = calcular_score_qualitativo_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(score_qual_info)

            score_quant_info = calcular_score_quantitativo_cpura(
                registro=registro_calculo,
                score_cpura_config=score_cpura_config,
                logger=logger,
            )
            registro_calculo.update(score_quant_info)

            score_total_info = calcular_score_total_cpura(
                score_quant_info=score_quant_info,
                score_qual_info=score_qual_info,
                logger=logger,
            )
            registro_calculo.update(score_total_info)

            rating_final = calcular_rating_final(
                registro=registro_calculo,
                segmento_pd=segmento_pd,
                pd_cpura_config=pd_cpura_config,
            )
            registro_calculo["RATING_FINAL"] = rating_final

            resultado_scores.update(notas_quant_info)
            resultado_scores.update(score_qual_info)
            resultado_scores.update(score_quant_info)
            resultado_scores.update(score_total_info)

        if segmento_pd in {"CGRUPO", "CONSUMIDOR_GT_5"} and not pd_transform_rules:
            raise PdConfigurationError(
                f"pd_transform_rules não informado para {segmento_pd}."
            )
        
        # Só transformamos se não tivermos abortado lá em cima
        resultado_transformacao = transformar_pd_por_segmento(
            registro=registro_calculo,
            segmento_pd=segmento_pd,
            pd_base=pd_base,
            pd_faixas=pd_faixas,
            pd_transform_rules=pd_transform_rules,
            pd_cpura_config=pd_cpura_config,
            peer_group=peer_group,
            logger=logger,
            rating_final=(
                registro_calculo.get("RATING_FINAL")
                or registro_calculo.get("RATING_COPEL")
            ),
        )

        resultado = {
            "SEGMENTO_PD": segmento_pd,
            "PD_BASE": pd_base,
            "STATUS_CALCULO_PD": "CONCLUIDO",
            "CONFIG_SNAPSHOT_PD": config_snapshot_id,
            "VALIDADE_DF": validade_df,
            "VALIDADE_BUREAU": validade_bureau,
            "VALIDADE_RATING_PUBLICO": validade_rating,
            "FIM_VIGENCIA_ANALISE": fim_vigencia_analise,
            **resultado_scores,
            **resultado_transformacao,
        }

        if logger is not None:
            logger.info(
                "PD ajustada calculada com sucesso. "
                "CNPJ=%s SEGMENTO_PD=%s PD_BASE=%s "
                "RATING_FINAL=%s SCORE_TOTAL=%s PD_FINAL=%s METODO=%s",
                registro.get("CNPJ"),
                segmento_pd,
                resultado.get("PD_BASE"),
                resultado.get("RATING_FINAL"),
                resultado.get("SCORE_TOTAL"),
                resultado.get("PD_FINAL"),
                resultado.get("PD_METODO"),
            )

        return resultado

    except PdCalculationError:
        if logger is not None:
            logger.warning("Cálculo de PD não concluído (Insumo Pendente). CNPJ=%s SEGMENTO_PD=%s", registro.get('CNPJ'), segmento_pd)
        raise

    except Exception:
        if logger is not None:
            logger.exception(
                "Falha crítica no cálculo de PD ajustada. "
                "CNPJ=%s SEGMENTO_PD=%s",
                registro.get("CNPJ"),
                segmento_pd,
            )
        raise
