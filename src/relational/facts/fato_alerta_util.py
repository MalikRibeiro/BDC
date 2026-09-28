"""Serviço de registro unificado de alertas no modelo Star Schema (Fato Alerta)."""
import logging
from typing import Any
import pandas as pd
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

COLUNAS_FATO_ALERTA: list[str] = [
    "CNPJ", "CODIGO_ALERTA", "SEVERIDADE", "REGRA", "MENSAGEM_DESCRITIVA",
    "DATA_DETECCAO", "CAMPO_AFETADO", "VALOR_OBSERVADO", "LIMITE_ESPERADO",
    "STATUS_TRATAMENTO", "RESPONSAVEL", "EVIDENCIA_ENCERRAMENTO", "RUN_ID"
]

def registrar_alertas_em_lote(alertas_list: list[dict], run_id: str, context: Any) -> None:
    """Registra múltiplos alertas de negócio de uma vez, otimizando I/O."""
    if not alertas_list:
        return

    agora = datetime.now()

    novos_alertas = []
    for alerta in alertas_list:
        novos_alertas.append({
            "CNPJ": str(alerta.get("contraparte_id")) if alerta.get("contraparte_id") else None,
            "CODIGO_ALERTA": str(alerta.get("codigo")),
            "SEVERIDADE": str(alerta.get("severidade")),
            "REGRA": str(alerta.get("regra")),
            "MENSAGEM_DESCRITIVA": str(alerta.get("mensagem")),
            "DATA_DETECCAO": agora,
            "CAMPO_AFETADO": str(alerta.get("campo_afetado")) if pd.notna(alerta.get("campo_afetado")) and alerta.get("campo_afetado") is not None else None,
            "VALOR_OBSERVADO": str(alerta.get("valor_observado")) if pd.notna(alerta.get("valor_observado")) and alerta.get("valor_observado") is not None else None,
            "LIMITE_ESPERADO": str(alerta.get("limite_esperado")) if pd.notna(alerta.get("limite_esperado")) and alerta.get("limite_esperado") is not None else None,
            "STATUS_TRATAMENTO": str(alerta.get("status_tratamento", "ABERTO")),
            "RESPONSAVEL": str(alerta.get("responsavel")) if pd.notna(alerta.get("responsavel")) and alerta.get("responsavel") is not None else None,
            "EVIDENCIA_ENCERRAMENTO": str(alerta.get("evidencia_encerramento")) if pd.notna(alerta.get("evidencia_encerramento")) and alerta.get("evidencia_encerramento") is not None else None,
            "RUN_ID": str(run_id)
        })

    df_novo = pd.DataFrame(novos_alertas, columns=COLUNAS_FATO_ALERTA)

    out_dir = context.path("relational_facts") / "alertas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_parquet = out_dir / "fato_alerta_credito.parquet"
    out_csv = out_dir / "fato_alerta_credito.csv"

    if out_parquet.exists():
        try:
            df_existente = pd.read_parquet(out_parquet)
            for col in COLUNAS_FATO_ALERTA:
                if col not in df_existente.columns:
                    df_existente[col] = None
            df_existente = df_existente[COLUNAS_FATO_ALERTA]
            df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        except Exception as e:
            logger.warning("Parquet de alertas existente corrompido, recriando. Erro: %s", e)
            df_final = df_novo
    else:
        df_final = df_novo

    # Defesa contra PyArrow: Homogeneização estrita dos tipos antes da serialização
    df_final["DATA_DETECCAO"] = pd.to_datetime(df_final["DATA_DETECCAO"], errors="coerce")
    for col in COLUNAS_FATO_ALERTA:
        if col != "DATA_DETECCAO":
            df_final[col] = df_final[col].astype("string")

    df_final.to_parquet(out_parquet, index=False)
    df_final.to_csv(out_csv, index=False, sep=";", encoding="utf-8-sig")
