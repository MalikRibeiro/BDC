"""Domínios controlados e enumeradores do sistema BDC."""

from enum import Enum, unique


@unique
class TipoFicha(str, Enum):
    """Domínio para os tipos de fichas processadas."""
    COMERCIALIZADORA = "COMERCIALIZADORA"
    CONSUMIDOR = "CONSUMIDOR"


@unique
class LoadMode(str, Enum):
    """Domínio para os modos de carga do orquestrador."""
    INCREMENTAL = "incremental"
    REPROCESS = "reprocess"


@unique
class StatusIngestao(str, Enum):
    """Domínio para o status de movimentação dos arquivos na camada Bronze."""
    INICIADO = "INICIADO"
    SUCESSO = "SUCESSO"
    ERRO = "ERRO"
    REJEITADO = "REJEITADO"


@unique
class StatusClassificacao(str, Enum):
    """Domínio para os resultados do motor de classificação de layouts."""
    CLASSIFICADO = "CLASSIFICADO"
    REJEITADO = "REJEITADO"
    NAO_CLASSIFICADO = "NAO_CLASSIFICADO"


@unique
class StatusExtracao(str, Enum):
    """Domínio detalhado para os estados de extração e validação técnica."""
    NAO_EXECUTADO = "NAO_EXECUTADO"
    SUCESSO = "SUCESSO"
    ERRO = "ERRO"
    ERRO_VALIDACAO = "ERRO_VALIDACAO"
    ERRO_DUPLICIDADE_HASH = "ERRO_DUPLICIDADE_HASH"
    ERRO_DUPLICIDADE_NEGOCIO = "ERRO_DUPLICIDADE_NEGOCIO"
    ERRO_PROCESSAMENTO = "ERRO_PROCESSAMENTO"
    ERRO_LAYOUT = "ERRO_LAYOUT"
    ERRO_SEM_CNPJ = "ERRO_SEM_CNPJ"
    ERRO_CNPJ_INVALIDO = "ERRO_CNPJ_INVALIDO"


@unique
class SegmentoMetodologico(str, Enum):
    """Domínio das segmentações metodológicas de crédito."""
    CPURA = "CPURA"
    CGRUPO = "CGRUPO"
    CONSUMIDOR_GT_5 = "CONSUMIDOR_GT_5"
    CONSUMIDOR_LE_5 = "CONSUMIDOR_LE_5"


@unique
class TipoAnalise(str, Enum):
    """Domínio para a origem ou tipo de análise gerada."""
    AUTOMATICA = "AUTOMATICA"
    MANUAL = "MANUAL"
    MANUAL_AJUSTADA = "MANUAL_AJUSTADA"


@unique
class SeveridadeAlerta(str, Enum):
    """Domínio para a classificação de alertas do sistema."""
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"
    
@unique
class StatusGarantia(str, Enum):
    """Domínio para os estados de vigência de garantias (§6.8)."""
    VIGENTE = "VIGENTE"
    PROXIMA_VENCIMENTO = "PROXIMA_VENCIMENTO"
    VENCIDA = "VENCIDA"
    CANCELADA = "CANCELADA"
    NAO_ELEGIVEL = "NAO_ELEGIVEL"


@unique
class StatusAnalise(str, Enum):
    """Domínio para o ciclo de vida de uma análise de crédito (§4.2, Apêndice A)."""
    VIGENTE = "VIGENTE"
    PROXIMA_VENCIMENTO = "PROXIMA_VENCIMENTO"
    VENCIDA = "VENCIDA"
    EM_RENOVACAO = "EM_RENOVACAO"
    SUSPENSA = "SUSPENSA"


@unique
class StatusDocumento(str, Enum):
    """Domínio para o estado de processamento de um documento/ficha (§4.2, Apêndice A)."""
    DESCOBERTO = "DESCOBERTO"
    EM_STAGING = "EM_STAGING"
    INGERIDO = "INGERIDO"
    CLASSIFICADO = "CLASSIFICADO"
    EXTRAIDO = "EXTRAIDO"
    VALIDADO = "VALIDADO"
    PUBLICADO = "PUBLICADO"
    PENDENTE = "PENDENTE"
    REJEITADO = "REJEITADO"


@unique
class StatusAlerta(str, Enum):
    """Domínio para os estados de resolução de alertas (§6.10)."""
    ABERTO = "ABERTO"
    EM_TRATAMENTO = "EM_TRATAMENTO"
    RESOLVIDO = "RESOLVIDO"
    IGNORADO = "IGNORADO"


@unique
class StatusAprovacao(str, Enum):
    """Domínio para o fluxo de aprovação de carga manual e overrides (§11.7)."""
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"
    EXPIRADO = "EXPIRADO"