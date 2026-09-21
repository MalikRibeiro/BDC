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
    if not data_str:
        return True
    try:
        dt = datetime.fromisoformat(str(data_str)[:10])
        idade_dias = (datetime.now() - dt).days
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
            return {
                "SEGMENTO_PD": segmento_pd,
                "STATUS_CALCULO_PD": "RECUPERACAO_JUDICIAL",
                "PD_BASE": None,
                "PD_FINAL": 1.0,
                "RATING_FINAL": "E",
                "PD_METODO": "OVERRIDE_RECUPERACAO_JUDICIAL",
                "CONFIG_SNAPSHOT_PD": config_snapshot_id
            }

        validar_insumos_pd(registro, segmento_pd)

        # --- FALLBACKS E VALIDADE DAS INFORMACOES ---
        data_df = registro.get("DATA_DEMONSTRACAO_FINANCEIRA")
        data_bureau = registro.get("DATA_BUREAU")
        data_rating = registro.get("DATA_RATING_PUBLICO")
        
        pd_risk3_val = registro.get("PD_RISK3")
        try:
            pd_risk3 = float(pd_risk3_val) if pd_risk3_val is not None else 0.15 # fallback 15%
        except (ValueError, TypeError):
            pd_risk3 = 0.15
            
        df_vencida = _is_expired(data_df, 540) # 18 meses
        bureau_vencido = _is_expired(data_bureau, 120) if segmento_pd == "CPURA" else _is_expired(data_bureau, 365)
        rating_vencido = _is_expired(data_rating, 540)
        
        from datetime import timedelta
        
        validade_df = (datetime.fromisoformat(str(data_df)[:10]) + timedelta(days=540)).isoformat()[:10] if data_df and not _is_blank(data_df) else None
        validade_bureau = (datetime.fromisoformat(str(data_bureau)[:10]) + timedelta(days=120 if segmento_pd == "CPURA" else 365)).isoformat()[:10] if data_bureau and not _is_blank(data_bureau) else None
        validade_rating = (datetime.fromisoformat(str(data_rating)[:10]) + timedelta(days=540)).isoformat()[:10] if data_rating and not _is_blank(data_rating) else None
        
        fallback_acionado = False
        pd_sub = None
        motivo_sub = None

        if segmento_pd == "CPURA" and df_vencida:
            fallback_acionado = True
            pd_sub = max(pd_risk3, 0.10)
            motivo_sub = "DF > 18 meses"
        elif segmento_pd == "CGRUPO" and (df_vencida or rating_vencido):
            fallback_acionado = True
            try:
                ultima_pd = float(registro.get("PD_ULTIMA_VALIDA", 0.0))
            except (ValueError, TypeError):
                ultima_pd = 0.0
            pd_sub = max(ultima_pd, 0.15)
            motivo_sub = "DF > 18 meses ou Rating Publico Vencido"
        elif segmento_pd == "CONSUMIDOR_GT_5" and df_vencida:
            fallback_acionado = True
            pd_sub = max(pd_risk3, 0.50)
            motivo_sub = "DF > 18 meses"
            
        if fallback_acionado:
            if logger is not None:
                logger.warning("Fallback acionado para CNPJ=%s: %s", registro.get("CNPJ"), motivo_sub)
            return {
                "SEGMENTO_PD": segmento_pd,
                "STATUS_CALCULO_PD": "CONCLUIDO_COM_PD_SUB",
                "PD_BASE": None,
                "PD_FINAL": pd_sub,
                "RATING_FINAL": "E" if pd_sub >= 0.10 else "D", # Estimativa conservadora
                "PD_METODO": "PD_SUBSTITUTA",
                "MOTIVO_PD_SUB": motivo_sub,
                "DATA_ACIONAMENTO_PD_SUB": datetime.now().isoformat(timespec="seconds"),
                "FONTE_PD_SUB": "REGRA_FALLBACK",
                "VALOR_PD_SUB": pd_sub,
                "CONFIG_SNAPSHOT_PD": config_snapshot_id,
                "VALIDADE_DF": validade_df,
                "VALIDADE_BUREAU": validade_bureau,
                "VALIDADE_RATING_PUBLICO": validade_rating
            }

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
            logger.exception("Erro controlado no cálculo de PD ajustada. CNPJ=%s SEGMENTO_PD=%s", registro.get('CNPJ'), segmento_pd)
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
