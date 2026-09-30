from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class StatusCNPJ(str, Enum):
    VALIDO = "CNPJ_VALIDO"
    VAZIO = "CNPJ_VAZIO"
    FORMATO_INVALIDO = "CNPJ_FORMATO_INVALIDO"
    DIGITOS_INVALIDOS = "CNPJ_DIGITOS_INVALIDOS"


@dataclass(frozen=True, slots=True)
class ResultadoCNPJ:
    cnpj: str | None
    raiz: str | None
    status: StatusCNPJ
    valor_original: Any = None
    zeros_adicionados: int = 0

    @property
    def valido(self) -> bool:
        return self.status == StatusCNPJ.VALIDO
    
from common.nulos import is_nulo_textual

def _valor_nulo(valor: Any) -> bool:
    return is_nulo_textual(valor)

def _extrair_digitos_identificador(valor: Any) -> str | None:
    if _valor_nulo(valor):
        return None

    texto = str(valor).strip()

    if re.fullmatch(r"\d+\.0", texto):
        texto = texto[:-2]

    digitos = re.sub(r"\D", "", texto)
    return digitos or None

def validar_digitos_cnpj(cnpj: str) -> bool:
    if not re.fullmatch(r"\d{14}", cnpj):
        return False

    if cnpj == cnpj[0] * 14:
        return False

    def calcular_digito(base: str, pesos: list[int]) -> str:
        soma = sum(int(numero) * peso for numero, peso in zip(base, pesos))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    primeiro = calcular_digito(
        cnpj[:12],
        [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
    )

    segundo = calcular_digito(
        cnpj[:12] + primeiro,
        [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
    )

    return cnpj[-2:] == primeiro + segundo

def normalizar_cnpj_raiz(valor: Any) -> str | None:
    resultado = normalizar_cnpj(valor)
    return resultado.raiz if resultado.valido else None

def normalizar_cnpj_coluna(valor: Any) -> str | None:
    """Normaliza CNPJ para uso em df.apply() — chamada única por célula."""
    r = normalizar_cnpj(valor)
    return r.cnpj if r.valido else None

def normalizar_cnpj(
    valor: Any,
    *,
    preencher_zeros: bool = True,
    validar_digitos: bool = True,
) -> ResultadoCNPJ:
    digitos = _extrair_digitos_identificador(valor)

    if digitos is None:
        return ResultadoCNPJ(
            cnpj=None,
            raiz=None,
            status=StatusCNPJ.VAZIO,
            valor_original=valor,
        )

    if len(digitos) > 14:
        return ResultadoCNPJ(
            cnpj=None,
            raiz=None,
            status=StatusCNPJ.FORMATO_INVALIDO,
            valor_original=valor,
        )

    zeros_adicionados = 0

    if len(digitos) < 14:
        if not preencher_zeros:
            return ResultadoCNPJ(
                cnpj=None,
                raiz=None,
                status=StatusCNPJ.FORMATO_INVALIDO,
                valor_original=valor,
            )

        zeros_adicionados = 14 - len(digitos)
        digitos = digitos.zfill(14)

    if validar_digitos and not validar_digitos_cnpj(digitos):
        return ResultadoCNPJ(
            cnpj=digitos,
            raiz=digitos[:8],
            status=StatusCNPJ.DIGITOS_INVALIDOS,
            valor_original=valor,
            zeros_adicionados=zeros_adicionados,
        )

    return ResultadoCNPJ(
        cnpj=digitos,
        raiz=digitos[:8],
        status=StatusCNPJ.VALIDO,
        valor_original=valor,
        zeros_adicionados=zeros_adicionados,
    )


def calcular_cnpj_matriz(cnpj_ou_raiz: Any) -> str | None:
    """Calcula deterministamente o CNPJ da matriz (terminação 0001-XX) via Módulo 11."""
    digitos = _extrair_digitos_identificador(cnpj_ou_raiz)
    if not digitos or len(digitos) < 8:
        return None
    raiz = digitos[:8]
    base = raiz + "0001"

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma1 = sum(int(num) * peso for num, peso in zip(base, pesos1))
    resto1 = soma1 % 11
    d1 = "0" if resto1 < 2 else str(11 - resto1)

    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    base2 = base + d1
    soma2 = sum(int(num) * peso for num, peso in zip(base2, pesos2))
    resto2 = soma2 % 11
    d2 = "0" if resto2 < 2 else str(11 - resto2)

    cnpj_matriz = base + d1 + d2
    return cnpj_matriz if validar_digitos_cnpj(cnpj_matriz) else None