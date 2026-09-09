"""Estruturas de estado e manifesto do processamento."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from domain.enums import (
    LoadMode,
    StatusClassificacao,
    StatusExtracao,
    TipoFicha,
)

@dataclass
class DocumentManifest:
    """Representa o manifesto técnico de uma ficha processada."""

    documento_id: str
    run_id: str
    ambiente: str
    tipo_ficha: TipoFicha | str
    arquivo_nome: str | None = None
    caminho_origem: str | None = None
    caminho_staging: str | None = None
    caminho_bronze: str | None = None
    hash_arquivo: str | None = None
    versao_ficha: str | None = None
    cnpj_extraido: str | None = None
    data_demonstracao_financeira: str | None = None
    data_calculo: str | None = None
    status_classificacao: StatusClassificacao | str | None = None
    status_extracao: StatusExtracao | str | None = None
    load_mode: LoadMode | str | None = None
    reprocessed: bool | None = None
    previous_record_found: bool | None = None
    erros: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Garante que os atributos controlados pertençam aos domínios nativos."""
        if isinstance(self.tipo_ficha, str):
            try:
                self.tipo_ficha = TipoFicha(self.tipo_ficha.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para tipo_ficha: '{self.tipo_ficha}'. Domínios válidos: {[e.value for e in TipoFicha]}")

        if isinstance(self.status_classificacao, str):
            try:
                self.status_classificacao = StatusClassificacao(self.status_classificacao.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para status_classificacao: '{self.status_classificacao}'. Domínios válidos: {[e.value for e in StatusClassificacao]}")

        if isinstance(self.status_extracao, str):
            try:
                self.status_extracao = StatusExtracao(self.status_extracao.upper())
            except ValueError:
                raise ValueError(f"Valor rejeitado para status_extracao: '{self.status_extracao}'. Domínios válidos: {[e.value for e in StatusExtracao]}")
                
        if isinstance(self.load_mode, str):
            try:
                self.load_mode = LoadMode(self.load_mode.lower())
            except ValueError:
                raise ValueError(f"Valor rejeitado para load_mode: '{self.load_mode}'. Domínios válidos: {[e.value for e in LoadMode]}")

    def to_dict(self) -> dict[str, Any]:
        """Serializa o manifesto convertendo os Enums para seus valores primitivos (strings)."""
        manifest_dict = asdict(self)
        for key, value in manifest_dict.items():
            if hasattr(value, "value"):
                manifest_dict[key] = value.value
        return manifest_dict