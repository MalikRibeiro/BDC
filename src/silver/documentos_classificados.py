from __future__ import annotations

def criar_documento_classificado(
    documento_id: str,
    run_id: str,
    ambiente: str,
    arquivo_nome: str,
    versao_ficha: str,
    TIPO_FICHA: str,
    hash_arquivo: str,
) -> dict[str, str]:
    """Monta o registro silver de documento classificado."""
    return {
        "documento_id": documento_id,
        "run_id": run_id,
        "ambiente": ambiente,
        "arquivo_nome": arquivo_nome,
        "versao_ficha": versao_ficha,
        "TIPO_FICHA": TIPO_FICHA,
        "hash_arquivo": hash_arquivo,
    }
