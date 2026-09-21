import os
import pandas as pd
from typing import Any
from pathlib import Path
import logging

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
