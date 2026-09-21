"""Serviços de Auditoria do Pipeline (§11.5 — Tabelas de Controle).

Registra cada execução do pipeline (ctl_run_pipeline) e cada documento
processado (ctl_documento) em tabelas persistentes.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any
import os

import pandas as pd

from storage.escrever_dados import escrever_conjunto_de_dados_silver


LOGGER = logging.getLogger("bdc.auditoria")

def registrar_inicio_pipeline(
    run_id: str,
    etapas_planejadas: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o início de uma execução do pipeline."""
    registro = {
        "RUN_ID": run_id,
        "DT_INICIO": datetime.now().isoformat(timespec="seconds"),
        "DT_FIM": None,
        "STATUS_GERAL": "EM_EXECUCAO",
        "TOTAL_ETAPAS": etapas_planejadas,
        "ETAPAS_OK": 0,
        "ETAPAS_FALHA": 0,
        "VERSAO_SISTEMA": "BDC_v06",
    }
    LOGGER.info("Pipeline iniciado (run_id=%s).", run_id)
    return registro


def registrar_fim_pipeline(
    registro_inicio: dict[str, Any],
    etapas_ok: int,
    etapas_falha: int,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra o fim de uma execução do pipeline e persiste em ctl_run_pipeline."""
    registro = registro_inicio.copy()
    registro["DT_FIM"] = datetime.now().isoformat(timespec="seconds")
    registro["STATUS_GERAL"] = "SUCESSO" if etapas_falha == 0 else "PARCIAL"
    registro["ETAPAS_OK"] = etapas_ok
    registro["ETAPAS_FALHA"] = etapas_falha

    control_dir.mkdir(parents=True, exist_ok=True)

    ctl_path = control_dir / "ctl_run_pipeline.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    csv_path = control_dir / "ctl_run_pipeline.csv"
    df_combined.to_csv(csv_path, index=False, encoding="utf-8-sig", sep=";")

    LOGGER.info(
        "Pipeline finalizado (run_id=%s). Status=%s. OK=%d, Falha=%d.",
        registro["RUN_ID"], registro["STATUS_GERAL"],
        etapas_ok, etapas_falha,
    )
    return registro

def registrar_documento(
    documento_id: str,
    run_id: str,
    arquivo_origem: str,
    hash_arquivo: str | None,
    tipo_ficha: str,
    status_classificacao: str,
    status_extracao: str,
    control_dir: Path,
) -> dict[str, Any]:
    """Registra um documento processado na tabela ctl_documento (append-only)."""
    registro = {
        "DOCUMENTO_ID": documento_id,
        "RUN_ID": run_id,
        "ARQUIVO_ORIGEM": arquivo_origem,
        "HASH_ARQUIVO": hash_arquivo,
        "TIPO_FICHA": tipo_ficha,
        "STATUS_CLASSIFICACAO": status_classificacao,
        "STATUS_EXTRACAO": status_extracao,
        "DT_PROCESSAMENTO": datetime.now().isoformat(timespec="seconds"),
    }

    control_dir.mkdir(parents=True, exist_ok=True)

    ctl_path = control_dir / "ctl_documento.parquet"
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([registro])

    df_combined.to_parquet(ctl_path, index=False)

    LOGGER.info(
        "Documento registrado: %s (tipo=%s, status=%s).",
        documento_id, tipo_ficha, status_extracao,
    )
    return registro

def registrar_linhagem_campos(
    documento_id: str,
    run_id: str,
    campos_metadata: list[dict[str, Any]],
    control_dir: Path,
) -> None:
    """Registra a linhagem (aba, célula, método) de cada campo extraído."""
    if not campos_metadata:
        return

    registros = []
    dt_proc = datetime.now().isoformat(timespec="seconds")
    for cm in campos_metadata:
        registros.append({
            "DOCUMENTO_ID": documento_id,
            "RUN_ID": run_id,
            "CAMPO": cm.get("campo"),
            "ABA_ORIGEM": cm.get("aba_origem"),
            "CELULA_ORIGEM": cm.get("celula_origem"),
            "METODO_EXTRACAO": cm.get("metodo"),
            "VALOR_EXTRAIDO": str(cm.get("valor"))[:255] if cm.get("valor") is not None else None,
            "DT_PROCESSAMENTO": dt_proc,
        })

    control_dir.mkdir(parents=True, exist_ok=True)
    ctl_path = control_dir / "ctl_campo_origem.parquet"
    
    df_new = pd.DataFrame(registros)
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_parquet(ctl_path, index=False)
    LOGGER.debug("Registrada linhagem de %d campos para documento %s.", len(registros), documento_id)

def _append_to_ctl(control_dir: Path, table_name: str, records: list[dict[str, Any]]) -> None:
    if not records:
        return
    control_dir.mkdir(parents=True, exist_ok=True)
    ctl_path = control_dir / f"{table_name}.parquet"
    df_new = pd.DataFrame(records)
    if ctl_path.exists():
        df_existing = pd.read_parquet(ctl_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_parquet(ctl_path, index=False)

def get_responsavel_pipeline() -> str:
    return os.environ.get("RESPONSAVEL_PIPELINE", os.getlogin() if hasattr(os, "getlogin") else "SISTEMA")

def registrar_evento_processamento(control_dir: Path, evento: str, entidade: str, status_anterior: str, status_novo: str, mensagem: str) -> None:
    _append_to_ctl(control_dir, "ctl_evento_processamento", [{
        "evento": evento,
        "entidade": entidade,
        "status_anterior": status_anterior,
        "status_novo": status_novo,
        "timestamp": pd.Timestamp.now().isoformat(),
        "responsavel": get_responsavel_pipeline(),
        "mensagem": mensagem
    }])

def registrar_regra_aplicada(control_dir: Path, regra_id: str, versao: str, entradas: str, parametros: str, saida: str, calculo_id: str) -> None:
    _append_to_ctl(control_dir, "ctl_regra_aplicada", [{
        "regra_id": regra_id,
        "versao": versao,
        "entradas": entradas,
        "parametros": parametros,
        "saida": saida,
        "calculo_id": calculo_id
    }])

def registrar_reconciliacao(control_dir: Path, origem: str, destino: str, metrica: str, valor_esperado: float, valor_observado: float, diferenca: float, tolerancia: float, status: str) -> None:
    _append_to_ctl(control_dir, "ctl_reconciliacao", [{
        "origem_destino": f"{origem}_{destino}",
        "metrica": metrica,
        "valor_esperado": valor_esperado,
        "valor_observado": valor_observado,
        "diferenca": diferenca,
        "tolerancia": tolerancia,
        "status": status
    }])

def registrar_override(control_dir: Path, campo_resultado: str, valor_anterior: str, valor_novo: str, motivo: str, evidencia: str, solicitante: str, aprovador: str, vigencia: str) -> None:
    _append_to_ctl(control_dir, "ctl_override", [{
        "campo_resultado_alterado": campo_resultado,
        "valor_anterior": valor_anterior,
        "valor_novo": valor_novo,
        "motivo": motivo,
        "evidencia": evidencia,
        "solicitante": solicitante,
        "aprovador": aprovador,
        "vigencia": vigencia
    }])

def registrar_publicacao(control_dir: Path, publicacao_id: str, arquivos_tabelas: str, hashes: str, quantidade_linhas: int, status: str) -> None:
    _append_to_ctl(control_dir, "ctl_publicacao", [{
        "publicacao_id": publicacao_id,
        "arquivos_tabelas": arquivos_tabelas,
        "hashes": hashes,
        "quantidade_linhas": quantidade_linhas,
        "data": pd.Timestamp.now().isoformat(),
        "aprovador": get_responsavel_pipeline(),
        "status": status
    }])

def registrar_mudanca_config(control_dir: Path, configuracao: str, antes: str, depois: str, ambiente: str, vigencia: str) -> None:
    _append_to_ctl(control_dir, "ctl_mudanca_config", [{
        "configuracao_alterada": configuracao,
        "antes": antes,
        "depois": depois,
        "solicitante": get_responsavel_pipeline(),
        "aprovacao": "PENDENTE_APROVACAO_FORMAL",
        "ambiente": ambiente,
        "vigencia": vigencia
    }])

def registrar_aprovacao_manual(control_dir: Path, registro_manual_id: str, solicitante: str, aprovador: str, decisao: str, comentario: str, alcada: str, evidencia: str, vigencia: str) -> None:
    _append_to_ctl(control_dir, "ctl_aprovacao_manual", [{
        "registro_manual_id": registro_manual_id,
        "solicitante": solicitante,
        "aprovador": aprovador,
        "decisao": decisao,
        "data_hora": pd.Timestamp.now().isoformat(),
        "comentario": comentario,
        "alcada": alcada,
        "evidencia": evidencia,
        "vigencia": vigencia
    }])

def registrar_validacao_qualidade(control_dir: Path, regra: str, severidade: str, valor: str, resultado: str, tolerancia: str, acao: str) -> None:
    _append_to_ctl(control_dir, "ctl_validacao_qualidade", [{
        "regra_qualidade": regra,
        "severidade": severidade,
        "valor": valor,
        "resultado": resultado,
        "tolerancia": tolerancia,
        "acao": acao
    }])
