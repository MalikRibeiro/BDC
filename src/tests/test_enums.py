import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from storage.state_store import DocumentManifest

def test_t133_rejeicao_valor_fora_do_dominio():
    """Garante que o manifesto rejeita strings inválidas e levanta erro claro."""
    with pytest.raises(ValueError) as exc:
        DocumentManifest(
            documento_id="123",
            run_id="run_1",
            ambiente="dev",
            tipo_ficha="comercializadora",
            status_extracao="FALHA_NA_PLANILHA" # Valor não mapeado no Enum
        )
    
    assert "Valor rejeitado para status_extracao" in str(exc.value)
    assert "ERRO_PROCESSAMENTO" in str(exc.value)

def test_t133_conversao_string_valida_para_enum():
    """Garante que strings minúsculas/maiúsculas sejam corrigidas para o Enum correspondente."""
    manifest = DocumentManifest(
        documento_id="123",
        run_id="run_1",
        ambiente="dev",
        tipo_ficha="COMERCIALIZADORA", # Enviado maiúsculo, mas o Enum é minúsculo
        status_extracao="sucesso" # Enviado minúsculo, mas o Enum é maiúsculo
    )
    
    # O método to_dict extrai o valor consolidado correto para persistência
    data = manifest.to_dict()
    assert data["tipo_ficha"] == "comercializadora"
    assert data["status_extracao"] == "SUCESSO"