# CÓDIGO PARTE 2

Arquivos consolidados por afinidade de domínio, mantendo arquivos pequenos relacionados juntos.


# GRUPO: common


---

## `src/common/__init__.py`

- Linhas: 1
- SHA-256: `8da5e1c3376bdb71a74c9cda926c3fb1b5a4999da8a293dae8fafb8c948c96d2`
- Classes: -
- Funções: -

```python
# Init para o pacote comum de domínios
```


---

## `src/common/dados.py`

- Linhas: 128
- SHA-256: `f4c9349c58834c93dc1f08dd1274e052f122883e1b38d76d06aefee76fb6a22a`
- Classes: -
- Funções: normalizar_coluna_cnpj, normalizar_coluna_auditor, normalizar_coluna_percentual, validar_coluna_cnpj_canonica, aplicar_schema_dataframe, validar_schema_dataframe

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from common.dominio import normalizar_auditor
from common.identificadores import ResultadoCNPJ, normalizar_cnpj
from common.numeros import to_percentual_br

def normalizar_coluna_cnpj(
    df: pd.DataFrame,
    *,
    coluna_origem: str = "CNPJ",
    coluna_cnpj: str = "CNPJ",
    coluna_raiz: str = "CNPJ_RAIZ",
    coluna_status: str = "CNPJ_STATUS",
    validar_digitos: bool = True,
) -> pd.DataFrame:
    if coluna_origem not in df.columns:
        raise KeyError(
            f"Coluna obrigatória não encontrada: {coluna_origem}"
        )

    resultado = df.copy()

    normalizados: pd.Series = resultado[coluna_origem].map(
        lambda valor: normalizar_cnpj(
            valor,
            preencher_zeros=True,
            validar_digitos=validar_digitos,
        )
    )

    resultado[coluna_cnpj] = pd.Series(
        [item.cnpj for item in normalizados],
        index=resultado.index,
        dtype="string",
    )

    resultado[coluna_raiz] = pd.Series(
        [item.raiz for item in normalizados],
        index=resultado.index,
        dtype="string",
    )

    resultado[coluna_status] = pd.Series(
        [item.status.value for item in normalizados],
        index=resultado.index,
        dtype="string",
    )

    return resultado

def normalizar_coluna_auditor(
    df: pd.DataFrame,
    dicionario: Mapping[str, Sequence[str]],
    *,
    coluna: str = "AUDITOR",
) -> pd.DataFrame:
    if coluna not in df.columns:
        return df.copy()

    resultado = df.copy()

    resultado[coluna] = (
        resultado[coluna]
        .map(lambda valor: normalizar_auditor(valor, dicionario))
        .astype("string")
    )

    return resultado

def normalizar_coluna_percentual(
    df: pd.DataFrame,
    *,
    coluna: str,
    casas_decimais: int = 6,
) -> pd.DataFrame:
    if coluna not in df.columns:
        return df.copy()

    resultado = df.copy()

    resultado[coluna] = resultado[coluna].map(
        lambda valor: to_percentual_br(
            valor,
            casas_decimais=casas_decimais,
        )
    )

    resultado[coluna] = pd.to_numeric(
        resultado[coluna],
        errors="coerce",
    ).astype("Float64")

    return resultado

def validar_coluna_cnpj_canonica(
    df: pd.DataFrame,
    coluna: str = "CNPJ",
) -> list[str]:
    erros = []
    
    if coluna not in df.columns:
        return [f"A coluna '{coluna}' não existe no DataFrame."]

    if not isinstance(df[coluna].dtype, pd.StringDtype):
        erros.append(f"A coluna '{coluna}' não está com o tipo de dado 'string'.")

    inconsistentes = df[~df[coluna].isna() & ~df[coluna].astype(str).str.match(r"^\d{14}$")]
    
    if not inconsistentes.empty:
        erros.append(f"A coluna '{coluna}' possui {len(inconsistentes)} registros com formato inválido (deve ser exatamente 14 dígitos numéricos).")

    return erros

def aplicar_schema_dataframe(df: pd.DataFrame, colunas_schema: list[str]) -> pd.DataFrame:
    cols = [col for col in colunas_schema if col in df.columns]
    return df[cols].copy()

def validar_schema_dataframe(df: pd.DataFrame, colunas_obrigatorias: list[str]) -> list[str]:
    erros = []
    for col in colunas_obrigatorias:
        if col not in df.columns:
            erros.append(f"Coluna obrigatória não encontrada no DataFrame: '{col}'.")
    return erros
```


---

## `src/common/datas.py`

- Linhas: 83
- SHA-256: `0b71d83bb9293f2fc593edea1f89cb319da85f46f4f877c0ef7f2053124b078f`
- Classes: -
- Funções: normalizar_data, normalizar_competencia, normalizar_data_demonstracao_financeira

```python
from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd


def normalizar_data(
    valor: Any,
    *,
    formato_saida: str = "%Y-%m-%d",
) -> str | None:
    if valor is None:
        return None

    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor.strftime(formato_saida)

    if isinstance(valor, datetime):
        return valor.date().strftime(formato_saida)

    texto = str(valor).strip()

    from common.nulos import is_nulo_textual
    if is_nulo_textual(texto):
        return None

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        convertido = pd.to_datetime(
            texto,
            dayfirst=True,
            errors="coerce",
        )

    if pd.isna(convertido):
        return None

    return convertido.date().strftime(formato_saida)

def normalizar_competencia(valor: Any) -> str | None:
    data_normalizada = normalizar_data(valor)

    if data_normalizada is None:
        return None

    return data_normalizada[:7]

import re

def normalizar_data_demonstracao_financeira(value: Any) -> tuple[str | None, str | None, bool]:
    """Normaliza DATA_DEMONSTRACAO_FINANCEIRA para dd/mm/aaaa.
    Retorna: (data_normalizada, valor_original_corrompido, flag_corrigida)
    """
    if value is None:
        return None, None, False

    if isinstance(value, datetime) and 1900 <= value.year <= 1920:
        dias = (value - datetime(1899, 12, 30)).days
        if 1950 <= dias <= 2100:
            return f"31/12/{dias}", value.strftime("%Y-%m-%d %H:%M:%S"), True

    texto = str(value).strip()
    if not texto:
        return None, None, False

    if re.fullmatch(r"\d{4}", texto):
        return f"31/12/{texto}", texto, True

    texto = texto.split()[0]

    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]

    for fmt in formatos:
        try:
            dt = datetime.strptime(texto, fmt)
            return dt.strftime("%d/%m/%Y"), None, False
        except ValueError:
            continue

    return None, None, False
```


---

## `src/common/dominio.py`

- Linhas: 90
- SHA-256: `f237ada9872212a26da1d58acc30d0c46a519c325f0b9737895e18668f70b6fc`
- Classes: -
- Funções: _criar_indice_aliases, normalizar_valor_dominio, normalizar_auditor, normalizar_agencia, normalizar_rating

```python
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from common.texto import normalizar_chave_textual


def _criar_indice_aliases(
    dicionario: Mapping[str, Sequence[str]],
) -> dict[str, str]:
    indice: dict[str, str] = {}

    for canonico, aliases in dicionario.items():
        chave_canonica = normalizar_chave_textual(canonico)

        if chave_canonica:
            indice[chave_canonica] = canonico

        for alias in aliases:
            chave_alias = normalizar_chave_textual(alias)

            if chave_alias:
                indice[chave_alias] = canonico

    return indice

def normalizar_valor_dominio(
    valor: Any,
    dicionario: Mapping[str, Sequence[str]],
    *,
    valor_desconhecido: str | None = None,
) -> str | None:
    chave = normalizar_chave_textual(valor)

    if chave is None:
        return None

    indice = _criar_indice_aliases(dicionario)

    if chave in indice:
        return indice[chave]

    candidatos: list[tuple[int, str]] = []

    for alias, canonico in indice.items():
        if len(alias) < 4:
            continue

        padrao = rf"(?<![A-Z0-9]){re.escape(alias)}(?![A-Z0-9])"

        if re.search(padrao, chave):
            candidatos.append((len(alias), canonico))

    if candidatos:
        candidatos.sort(reverse=True)
        return candidatos[0][1]

    return valor_desconhecido

def normalizar_auditor(
    valor: Any,
    dicionario: Mapping[str, Sequence[str]],
) -> str | None:
    return normalizar_valor_dominio(
        valor,
        dicionario,
        valor_desconhecido="OUTRO",
    )

def normalizar_agencia(
    valor: Any,
    dicionario: Mapping[str, Sequence[str]],
) -> str | None:
    return normalizar_valor_dominio(
        valor,
        dicionario,
        valor_desconhecido=None,
    )

def normalizar_rating(
    valor: Any,
    dicionario: Mapping[str, Sequence[str]],
) -> str | None:
    return normalizar_valor_dominio(
        valor,
        dicionario,
        valor_desconhecido=None,
    )
```


---

## `src/common/excel.py`

- Linhas: 85
- SHA-256: `0c9d939cd7a0c68d6b6db7d493267614da3e29aa0ba7836e68df6bf2d4a8b914`
- Classes: -
- Funções: abrir_pasta, fechar_pasta, ler_celula, localizar_celula_por_regex

```python
"""Operações de leitura e fechamento seguro de workbooks Excel."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import get_column_letter


def abrir_pasta(path: str | Path) -> Any:
    """Abre um workbook Excel em modo somente leitura."""
    return load_workbook(
        filename=Path(path),
        data_only=True,
        read_only=True,
        keep_links=False,
    )

def fechar_pasta(workbook: Any) -> None:
    """Fecha um workbook ignorando falhas de liberação."""
    if workbook is None:
        return
    try:
        workbook.close()
    except Exception:
        return

def ler_celula(worksheet: Worksheet, cell_ref: str, return_meta: bool = False) -> Any:
    """Lê o valor de uma célula a partir de uma referência A1 (ex: 'A19')."""
    if not cell_ref or cell_ref == "0":
        return (None, None) if return_meta else None
    val = worksheet[cell_ref].value
    if return_meta:
        return val, {"aba": worksheet.title, "celula": cell_ref}
    return val

def localizar_celula_por_regex(
    worksheet: Worksheet,
    search_pattern: str,
    offset_col: int = 1,
    offset_row: int = 0,
    max_search_rows: int = 150,
    max_search_cols: int = 30,
    return_meta: bool = False
) -> Optional[Any]:
    """
    Varre a aba procurando uma expressão e retorna a célula adjacente.
    """
    if not search_pattern:
        return (None, None) if return_meta else None

    try:
        regex = re.compile(search_pattern, re.IGNORECASE)
    except re.error:
        return (None, None) if return_meta else None

    max_r = max_search_rows + max(0, offset_row)
    max_c = max_search_cols + max(0, offset_col)
    
    grid = []
    for row_vals in worksheet.iter_rows(min_row=1, max_row=max_r, min_col=1, max_col=max_c, values_only=True):
        grid.append(row_vals)

    for r_idx in range(min(max_search_rows, len(grid))):
        row_data = grid[r_idx]
        for c_idx in range(min(max_search_cols, len(row_data))):
            cell_value = row_data[c_idx]
            
            if cell_value and isinstance(cell_value, str):
                if regex.search(cell_value.strip()):
                    target_r = r_idx + offset_row
                    target_c = c_idx + offset_col
                    
                    if target_r < len(grid) and target_c < len(grid[target_r]):
                        val = grid[target_r][target_c]
                        if return_meta:
                            celula_ref = f"{get_column_letter(target_c + 1)}{target_r + 1}"
                            return val, {"aba": worksheet.title, "celula": celula_ref}
                        return val

    return (None, None) if return_meta else None
```


---

## `src/common/hashing.py`

- Linhas: 21
- SHA-256: `e3985a2e5d4874fdbe5c302a1ce1dd121710ad8a040bf548e8538115ed8bbea3`
- Classes: -
- Funções: arquivo_hash

```python
"""Geração de hash para arquivos do sistema BDC."""

from __future__ import annotations

import hashlib
from pathlib import Path


def arquivo_hash(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Calcula o hash SHA-256 de um arquivo."""
    file_path = Path(path)
    hasher = hashlib.sha256()

    with file_path.open("rb") as file_obj:
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()
```


---

## `src/common/identificadores.py`

- Linhas: 127
- SHA-256: `068b1c7f37064585dcb52c7800100ec97a00a197af4a893e0e47bf411329b3b5`
- Classes: StatusCNPJ, ResultadoCNPJ
- Funções: valido, _valor_nulo, _extrair_digitos_identificador, validar_digitos_cnpj, calcular_digito, normalizar_cnpj_raiz, normalizar_cnpj

```python
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
```


---

## `src/common/json.py`

- Linhas: 33
- SHA-256: `1acf34a81e04873760dcab6f32c7625153b5f3d1834283908746ddff42696521`
- Classes: -
- Funções: ler_json, validar_esquema_json

```python
"""Leitura, escrita e validação estrutural de arquivos JSON do sistema BDC."""

from __future__ import annotations

import json
import sys
import logging
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema.exceptions import ValidationError

logger = logging.getLogger(__name__)


def ler_json(path: str | Path) -> Any:
    """Lê um arquivo JSON e devolve seu conteúdo."""
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def validar_esquema_json(instance: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    """Valida um dicionário contra um JSON Schema e aborta a execução em caso de falha."""
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except ValidationError as e:
        logger.critical(
            "Falha de validação estrutural no arquivo %s. Caminho do erro: %s. Motivo: %s",
            label, e.json_path, e.message,
        )
        sys.exit(1)
```


---

## `src/common/nulos.py`

- Linhas: 31
- SHA-256: `d6ae48a8d014187b5026a05b97a72150441fbfc77a737e0e9b9594291d295f0b`
- Classes: -
- Funções: is_nulo_textual

```python
"""
Definição canônica de valores textuais que devem ser tratados como nulos (vazios).
Centraliza as verificações que antes estavam espalhadas pelo código.
"""

# Conjunto canônico de representações textuais de valor nulo/vazio.
# Importante: Todas as strings devem estar em letras maiúsculas e sem espaços nas bordas.
VALORES_NULOS_TEXTUAIS = frozenset({
    "",
    "NAN",
    "NONE",
    "<NA>",
    "N/A",
    "NA",
    "NULL",
    "N/D",
    "ND",
    "-",
    "--",
    "NAT",
    "NAO APLICAVEL",
    "NÃO APLICÁVEL",
    "NAO_APLICAVEL"
})

def is_nulo_textual(valor: str | None | float) -> bool:
    """Verifica se uma string (ou qualquer valor convertido para string) é um nulo textual."""
    import pandas as pd
    if valor is None or pd.isna(valor):
        return True
    return str(valor).strip().upper() in VALORES_NULOS_TEXTUAIS
```


---

## `src/common/numeros.py`

- Linhas: 84
- SHA-256: `c4fb6437c9b64aa6cd796f627b6cd828a1e0581fcbef9a10930a66a609a9e895`
- Classes: -
- Funções: _texto_numerico, to_decimal_br, to_float_br, to_int_br, to_percentual_br

```python
from __future__ import annotations

import math
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


def _texto_numerico(valor: Any) -> str | None:
    if valor is None:
        return None

    if isinstance(valor, float) and math.isnan(valor):
        return None

    texto = str(valor).strip()

    from common.nulos import is_nulo_textual
    if is_nulo_textual(texto):
        return None

    return texto

def to_decimal_br(valor: Any, *, casas_decimais: int | None = None) -> Decimal | None:
    """Converte padrão brasileiro para Decimal puro."""
    texto = _texto_numerico(valor)

    if texto is None:
        return None

    texto = texto.replace("R$", "").replace(" ", "")

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")

    elif "," in texto:
        texto = texto.replace(",", ".")

    texto = re.sub(r"[^0-9eE+\-.]", "", texto)

    try:
        numero = Decimal(texto)
    except InvalidOperation:
        return None

    if casas_decimais is not None:
        numero = numero.quantize(Decimal("1.000000"), rounding=ROUND_HALF_UP)

    return numero

def to_float_br(valor: Any) -> float | None:
    """Converte padrão brasileiro para Float puro."""
    dec = to_decimal_br(valor)
    return float(dec) if dec is not None else None

def to_int_br(valor: Any) -> int | None:
    """Converte padrão brasileiro para Int puro (apenas se não houver perda fracionária)."""
    dec = to_decimal_br(valor)
    if dec is None or dec != dec.to_integral_value():
        return None
    return int(dec)

def to_percentual_br(valor: Any, *, casas_decimais: int = 6) -> float | None:
    """Converte padrão brasileiro para percentual (divide por 100 se houver '%'). NÃO impõe limite de 0 a 1."""
    texto = _texto_numerico(valor)
    if texto is None:
        return None
    
    possui_percentual = "%" in texto
    dec = to_decimal_br(texto.replace("%", ""))
    
    if dec is None:
        return None
        
    if possui_percentual:
        dec /= Decimal("100")
        
    quantizador = Decimal("1").scaleb(-casas_decimais)
    dec = dec.quantize(quantizador, rounding=ROUND_HALF_UP)
    
    return float(dec)
```


---

## `src/common/paths.py`

- Linhas: 16
- SHA-256: `2d930628cb2adfb30703b443281259e35098998b05d084d14ffed9f3a88cd7fa`
- Classes: -
- Funções: sanitizar_nome_da_pasta

```python
"""Funções utilitárias para nomes de paths e diretórios."""

from __future__ import annotations

import re


_INVALID_PATH_CHARS = r'[<>:"/\\|?*]+'


def sanitizar_nome_da_pasta(value: str) -> str:
    """Sanitiza um texto para uso seguro em nome de pasta."""
    cleaned = re.sub(_INVALID_PATH_CHARS, "_", value.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("._ ")
```


---

## `src/common/servico_desduplicacao.py`

- Linhas: 67
- SHA-256: `96c06dbb862b44008d9868c8a2d93253189a1ef9b781c8f0148203d8526e6c90`
- Classes: -
- Funções: tem_hash_duplicado, tem_chave_de_negocio_duplicada, virar_chave_de_negocio_no_historico

```python
"""Regras de deduplicação e atualização incremental do sistema."""

from __future__ import annotations

from datetime import datetime
from typing import Any

def tem_hash_duplicado(
    history: list[dict[str, Any]],
    hash_value: str | None,
) -> bool:
    """Indica se o hash já foi processado anteriormente."""
    if not hash_value:
        return False

    return any(item.get("hash_arquivo") == hash_value for item in history)

def tem_chave_de_negocio_duplicada(
    history: list[dict[str, Any]],
    cnpj: str | None,
    data_demonstracao_financeira: str | None,
) -> bool:
    """Indica se a chave de negócio já existe com sucesso."""
    if not cnpj or not data_demonstracao_financeira:
        return False

    for item in history:
        if item.get("status_extracao") != "SUCESSO":
            continue

        if item.get("cnpj_extraido") != cnpj:
            continue

        if (
            item.get("data_demonstracao_financeira")
            != data_demonstracao_financeira
        ):
            continue

        return True

    return False

def virar_chave_de_negocio_no_historico(
    history: list[dict[str, Any]],
    manifest_record: dict[str, Any],
) -> None:
    """Atualiza o histórico em memória com a chave de negócio corrente.

    Em modo reprocess, MARCA registros anteriores como SUBSTITUIDO
    em vez de removê-los, preservando o histórico completo (§1.5 — imutabilidade).
    """
    load_mode = manifest_record.get("load_mode")
    cnpj = manifest_record.get("cnpj_extraido")
    data_df = manifest_record.get("data_demonstracao_financeira")

    if load_mode == "reprocess" and cnpj and data_df:
        for item in history:
            if (
                item.get("status_extracao") == "SUCESSO"
                and item.get("cnpj_extraido") == cnpj
                and item.get("data_demonstracao_financeira") == data_df
            ):
                item["status_extracao"] = "SUBSTITUIDO"
                item["dt_substituicao"] = datetime.now().isoformat(timespec="seconds")

    history.append(manifest_record)
```


---

## `src/common/texto.py`

- Linhas: 99
- SHA-256: `15c98e40b30aae443db8f0b035afc7d07d1c7ef48cf86fce66ce524443aec382`
- Classes: -
- Funções: texto_ou_none, remover_acentos, normalizar_texto, normalizar_chave_textual

```python
from __future__ import annotations

import re
import unicodedata
from typing import Any


_VALORES_NULOS_TEXTUAIS = {
    "",
    "NAN",
    "NONE",
    "NULL",
    "N/A",
    "NA",
    "-",
    "--",
}


def texto_ou_none(valor: Any) -> str | None:
    """
    Converte um valor em texto, preservando nulos como None.
    """
    if valor is None:
        return None

    texto = str(valor).strip()

    if texto.upper() in _VALORES_NULOS_TEXTUAIS:
        return None

    return texto


def remover_acentos(valor: Any) -> str | None:
    """
    Remove acentos sem aplicar outras regras de normalização.
    """
    texto = texto_ou_none(valor)

    if texto is None:
        return None

    normalizado = unicodedata.normalize("NFKD", texto)

    return "".join(
        caractere
        for caractere in normalizado
        if not unicodedata.combining(caractere)
    )


def normalizar_texto(
    valor: Any,
    *,
    caixa_alta: bool = True,
    remover_acentuacao: bool = False,
) -> str | None:
    """
    Normaliza espaços e, opcionalmente, caixa e acentuação.
    """
    texto = texto_ou_none(valor)

    if texto is None:
        return None

    texto = re.sub(r"\s+", " ", texto).strip()

    if remover_acentuacao:
        texto = remover_acentos(texto)

    if texto is None:
        return None

    return texto.upper() if caixa_alta else texto


def normalizar_chave_textual(valor: Any) -> str | None:
    """
    Gera uma chave textual para comparações de domínio.

    Exemplo:
        "Deloitte Touche & Tohmatsu Ltda."
        -> "DELOITTE TOUCHE E TOHMATSU LTDA"
    """
    texto = normalizar_texto(
        valor,
        caixa_alta=True,
        remover_acentuacao=True,
    )

    if texto is None:
        return None

    texto = texto.replace("&", " E ")
    texto = re.sub(r"[^A-Z0-9]+", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto or None
```


---

## `src/common/utils_orquestracao.py`

- Linhas: 199
- SHA-256: `24ef2835bfd06370f87bad1282d66a94dae1714c366335288157b98b755d71bf`
- Classes: -
- Funções: registrar_rejeicao_json, disco_cheio_erro, criar_run_id, criar_nome_arquivo_padronizado, resolver_subpasta_bronze, criar_fila_processamento, mover_para_rejeitados, mover_para_processados

```python
"""Funções utilitárias compartilhadas entre os orquestradores do BDC."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.context import AppContext
from common.paths import sanitizar_nome_da_pasta
from storage.estado_armazenamento import DocumentManifest
from staging.descoberta import detectar_arquivos_excel_pendentes
from storage.operacao_arquivo import mover_arquivo_com_tentativa_adicional
from storage.armazenamento_manifest import anexar_registro_de_manifesto

try:
    from domain.auditoria.servico_auditoria import registrar_documento
except ImportError:
    registrar_documento = None

def registrar_rejeicao_json(manifest: DocumentManifest, source_file: Path) -> None:
    """Grava metadados de rejeição de forma estruturada para reprocessamento."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    dir_rejeitados = Path("LOGS/rejeitados")
    dir_rejeitados.mkdir(parents=True, exist_ok=True)
    arquivo_json = dir_rejeitados / f"{hoje}_rejeicoes.json"
    
    registro = {
        "timestamp": datetime.now().isoformat(),
        "arquivo": str(source_file.name),
        "status": getattr(manifest, "status_extracao", "ERRO_DESCONHECIDO"),
        "erros": getattr(manifest, "erros", [])
    }
    try:
        dados = json.loads(arquivo_json.read_text(encoding="utf-8")) if arquivo_json.exists() else []
        dados.append(registro)
        arquivo_json.write_text(json.dumps(dados, indent=4, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Falha ao registrar JSON de rejeição para %s: %s", source_file.name, exc)


def disco_cheio_erro(exc: Exception) -> bool:
    """Indica se a exceção representa falta de espaço em disco."""
    if not isinstance(exc, OSError):
        return False

    text = str(exc).lower()

    return (
        getattr(exc, "winerror", None) == 112
        or getattr(exc, "errno", None) == 28
        or "no space left on device" in text
        or "espaço insuficiente no disco" in text
    )


def criar_run_id(context: AppContext) -> str:
    """Monta o identificador textual da execução."""
    prefix = context.naming.get("run_id_prefix", "BDC")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"

def criar_nome_arquivo_padronizado(
    original_name: str,
    versao_ficha: str | None,
    cnpj: str | None,
    data_df: str | None,
    hash_value: str | None,
) -> str:
    """Monta o nome técnico do arquivo processado (Substitui criar_nome_arquivo e criar_alvo_nome)."""
    source = Path(original_name)
    stem = source.stem[:40]

    parts: list[str] = [stem]

    if versao_ficha:
        parts.append(versao_ficha)

    if cnpj:
        safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
        if safe_cnpj:
            parts.append(safe_cnpj)

    if data_df:
        safe_data_df = "".join(ch for ch in str(data_df) if ch.isdigit())
        if safe_data_df:
            parts.append(safe_data_df[:8])

    if hash_value:
        parts.append(hash_value[:8])

    return "__".join(parts) + source.suffix.lower()


def resolver_subpasta_bronze(cnpj: str | None, sigla: str | None) -> str:
    """Resolve a subpasta da bronze organizada por CNPJ e sigla."""
    if not cnpj:
        raise ValueError("Não é possível publicar em bronze sem CNPJ válido.")
    safe_cnpj = "".join(ch for ch in str(cnpj) if ch.isdigit()) if cnpj else None
    safe_sigla = sanitizar_nome_da_pasta(sigla or "")
    if safe_sigla:
        return f"{safe_cnpj}__{safe_sigla}"

    return safe_cnpj or "SEM_CNPJ"

def criar_fila_processamento(
    context: AppContext,
    tipo_ficha: str
) -> list[tuple[Path, str, Path, Path]]:
    """Monta a fila de processamento de forma dinâmica baseada no tipo da ficha."""
    
    normal_files = detectar_arquivos_excel_pendentes(context.path(f"input_fichas_{tipo_ficha}_pendentes"))
    reprocess_files = detectar_arquivos_excel_pendentes(context.path(f"input_reprocessamento_{tipo_ficha}_pendentes"))

    queue: list[tuple[Path, str, Path, Path]] = []

    for file_path in normal_files:
        queue.append((
            file_path,
            "incremental",
            context.path(f"input_fichas_{tipo_ficha}_processadas"),
            context.path(f"input_fichas_{tipo_ficha}_rejeitadas"),
        ))

    for file_path in reprocess_files:
        queue.append((
            file_path,
            "reprocess",
            context.path(f"input_reprocessamento_{tipo_ficha}_processadas"),
            context.path(f"input_reprocessamento_{tipo_ficha}_rejeitadas"),
        ))

    return queue


def mover_para_rejeitados(
    source_file: Path,
    rejected_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
    control_dir: Path | None = None,
) -> None:
    """Move o arquivo para rejeitados, gera log estruturado e grava manifest."""
    target = rejected_dir / source_file.name

    registrar_rejeicao_json(manifest, source_file)

    try:
        if source_file.exists():
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para rejeitados: {exc}")
        logger.exception("Falha ao mover %s para rejeitados.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
        if control_dir and registrar_documento:
            registrar_documento(
                manifest.documento_id, manifest.run_id, manifest.arquivo_nome,
                manifest.hash_arquivo, manifest.tipo_ficha, manifest.status_classificacao or "N/A",
                manifest.status_extracao or "N/A", control_dir
            )
    except Exception:
        logger.exception("Falha ao gravar manifest de rejeição para %s.", source_file.name)
        raise


def mover_para_processados(
    source_file: Path,
    processed_dir: Path,
    manifest: DocumentManifest,
    ingestion_log_path: Path,
    logger: Any,
    control_dir: Path | None = None,
) -> None:
    """Move o arquivo para processadas e grava o manifest."""
    target = processed_dir / source_file.name

    try:
        if source_file.exists():
            mover_arquivo_com_tentativa_adicional(source_file, target)
    except Exception as exc:
        manifest.erros.append(f"Falha ao mover para processadas: {exc}")
        logger.exception("Falha ao mover %s para processadas.", source_file.name)

    try:
        anexar_registro_de_manifesto(str(ingestion_log_path), manifest.to_dict())
        if control_dir and registrar_documento:
            registrar_documento(
                manifest.documento_id, manifest.run_id, manifest.arquivo_nome,
                manifest.hash_arquivo, manifest.tipo_ficha, manifest.status_classificacao or "N/A",
                manifest.status_extracao or "N/A", control_dir
            )
    except Exception:
        logger.exception("Falha ao gravar manifest de processamento para %s.", source_file.name)
        raise
```


# GRUPO: gerar_contexto_ia.py


---

## `gerar_contexto_ia.py`

- Linhas: 877
- SHA-256: `76d881e95595f097fc4a0b9ba8c427c94df791382813838c890f54e3010f1c05`
- Classes: SymbolInfo, FileAnalysis, Alert
- Funções: parse_args, is_ignored, is_sensitive_file, read_text_safe, sanitize_text, sha256_file, dotted_name, decorator_names, analyze_python, scan_alerts, build_tree, discover_files, module_group, distribute_semantically, detect_internal_dependencies, write_readme, write_context, write_structure, code_fence_language, write_configurations, format_symbol, write_technical_summary, write_dependencies, write_alerts, write_code_parts, write_manifest, main

```python
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent
from typing import Iterable


DEFAULT_IGNORE = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".coverage",
    "htmlcov",
    "AI_CONTEXT",
}

CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "cp1252", "latin-1")

SENSITIVE_FILE_PATTERNS = (
    re.compile(r"(^|[._-])\.env($|[._-])", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"credential", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"\.pem$", re.IGNORECASE),
    re.compile(r"\.key$", re.IGNORECASE),
    re.compile(r"\.pfx$", re.IGNORECASE),
    re.compile(r"\.p12$", re.IGNORECASE),
)

SENSITIVE_VALUE_PATTERNS = (
    re.compile(
        r'(?im)^(\s*["\']?(?:password|passwd|pwd|token|secret|api[_-]?key|client[_-]?secret)'
        r'["\']?\s*[:=]\s*)[^\n,}]+',
    ),
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+/=-]+"),
    re.compile(r"(?i)(mongodb(?:\+srv)?://[^:\s/]+:)[^@\s]+@"),
    re.compile(r"(?i)(postgres(?:ql)?://[^:\s/]+:)[^@\s]+@"),
)


@dataclass
class SymbolInfo:
    name: str
    kind: str
    line: int
    end_line: int | None = None
    decorators: list[str] = field(default_factory=list)


@dataclass
class FileAnalysis:
    path: str
    lines: int = 0
    bytes: int = 0
    sha256: str = ""
    encoding: str = ""
    imports: list[str] = field(default_factory=list)
    import_details: list[dict] = field(default_factory=list)
    classes: list[SymbolInfo] = field(default_factory=list)
    functions: list[SymbolInfo] = field(default_factory=list)
    docstring: str = ""
    syntax_error: str | None = None
    read_error: str | None = None


@dataclass
class Alert:
    path: str
    line: int
    severity: str
    category: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera um pacote Markdown consolidado para análise de um projeto Python por IA."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Raiz do projeto. Padrão: diretório atual.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Diretório de saída. Padrão: <root>/AI_CONTEXT.",
    )
    parser.add_argument(
        "--partes",
        type=int,
        default=3,
        help="Quantidade de arquivos consolidados de código. Padrão: 3.",
    )
    parser.add_argument(
        "--max-config-bytes",
        type=int,
        default=300_000,
        help="Tamanho máximo de cada configuração incluída integralmente.",
    )
    parser.add_argument(
        "--sem-sanitizacao",
        action="store_true",
        help="Desativa a máscara de possíveis segredos. Não recomendado.",
    )
    return parser.parse_args()


def is_ignored(path: Path, root: Path, out: Path, ignore: set[str]) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True

    if path == out or out in path.parents:
        return True

    return any(part in ignore for part in relative.parts)


def is_sensitive_file(path: Path) -> bool:
    name = path.name
    return any(pattern.search(name) for pattern in SENSITIVE_FILE_PATTERNS)


def read_text_safe(path: Path) -> tuple[str, str]:
    last_error: Exception | None = None

    for encoding in TEXT_ENCODINGS:
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError as exc:
            last_error = exc
        except OSError:
            raise

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        str(last_error or "Codificação não reconhecida"),
    )


def sanitize_text(text: str) -> tuple[str, int]:
    replacements = 0
    sanitized = text

    for pattern in SENSITIVE_VALUE_PATTERNS:
        if pattern.groups:
            sanitized, count = pattern.subn(r"\1<REDACTED>", sanitized)
        else:
            sanitized, count = pattern.subn("<REDACTED>", sanitized)
        replacements += count

    user_path_patterns = (
        re.compile(r"(?i)C:\\Users\\[^\\\s\"']+"),
        re.compile(r"<USER_HOME>/\s\"']+"),
        re.compile(r"<USER_HOME>/\s\"']+"),
    )
    for pattern in user_path_patterns:
        sanitized, count = pattern.subn("<USER_HOME>", sanitized)
        replacements += count

    return sanitized, replacements


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return dotted_name(node.func)
    return ""


def decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> list[str]:
    return [name for dec in node.decorator_list if (name := dotted_name(dec))]


def analyze_python(path: Path, root: Path) -> FileAnalysis:
    relative = path.relative_to(root).as_posix()
    info = FileAnalysis(path=relative, bytes=path.stat().st_size, sha256=sha256_file(path))

    try:
        text, encoding = read_text_safe(path)
        info.encoding = encoding
        info.lines = len(text.splitlines())
    except (OSError, UnicodeError) as exc:
        info.read_error = f"{type(exc).__name__}: {exc}"
        return info

    try:
        tree = ast.parse(text, filename=relative)
    except SyntaxError as exc:
        info.syntax_error = f"linha {exc.lineno}: {exc.msg}"
        return info

    info.docstring = ast.get_docstring(tree, clean=True) or ""

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                info.imports.append(alias.name)
                info.import_details.append(
                    {"module": alias.name, "name": None, "line": node.lineno}
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            info.imports.append(module)
            for alias in node.names:
                info.import_details.append(
                    {"module": module, "name": alias.name, "line": node.lineno}
                )
        elif isinstance(node, ast.ClassDef):
            info.classes.append(
                SymbolInfo(
                    name=node.name,
                    kind="class",
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", None),
                    decorators=decorator_names(node),
                )
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "async function" if isinstance(node, ast.AsyncFunctionDef) else "function"
            info.functions.append(
                SymbolInfo(
                    name=node.name,
                    kind=kind,
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", None),
                    decorators=decorator_names(node),
                )
            )

    info.imports = sorted(set(filter(None, info.imports)))
    info.classes.sort(key=lambda item: item.line)
    info.functions.sort(key=lambda item: item.line)
    return info


def scan_alerts(path: Path, root: Path) -> list[Alert]:
    alerts: list[Alert] = []
    relative = path.relative_to(root).as_posix()

    try:
        text, _ = read_text_safe(path)
    except (OSError, UnicodeError):
        return alerts

    try:
        tree = ast.parse(text, filename=relative)
    except SyntaxError as exc:
        return [
            Alert(relative, exc.lineno or 0, "ALTA", "SYNTAX_ERROR", exc.msg)
        ]

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            called = dotted_name(node.func)
            if called == "sys.exit":
                alerts.append(
                    Alert(relative, node.lineno, "MÉDIA", "SYS_EXIT", "sys.exit fora da camada de interface deve ser revisado.")
                )
            elif called == "print":
                alerts.append(
                    Alert(relative, node.lineno, "BAIXA", "PRINT", "Uso de print; avaliar logging estruturado.")
                )

        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                alerts.append(
                    Alert(relative, node.lineno, "ALTA", "BARE_EXCEPT", "Bloco except sem tipo de exceção.")
                )
            elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    alerts.append(
                        Alert(relative, node.lineno, "ALTA", "SILENT_EXCEPTION", "except Exception com pass oculta falhas.")
                    )

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if end - node.lineno + 1 >= 100:
                alerts.append(
                    Alert(
                        relative,
                        node.lineno,
                        "MÉDIA",
                        "LONG_FUNCTION",
                        f"Função {node.name} possui {end - node.lineno + 1} linhas.",
                    )
                )

        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if re.search(r"(?i)[A-Z]:\\Users\\", value) or re.search(r"/(home|Users)/[^/]+", value):
                alerts.append(
                    Alert(relative, getattr(node, "lineno", 0), "MÉDIA", "ABSOLUTE_USER_PATH", "Caminho absoluto de usuário encontrado.")
                )

    return alerts


def build_tree(folder: Path, root: Path, out: Path, ignore: set[str], prefix: str = "") -> list[str]:
    try:
        items = [
            item
            for item in folder.iterdir()
            if not is_ignored(item, root, out, ignore) and not is_sensitive_file(item)
        ]
    except OSError:
        return [prefix + "[Erro ao listar diretório]"]

    items.sort(key=lambda item: (item.is_file(), item.name.lower()))
    lines: list[str] = []

    for index, item in enumerate(items):
        last = index == len(items) - 1
        connector = "└── " if last else "├── "
        suffix = "/" if item.is_dir() else ""
        lines.append(f"{prefix}{connector}{item.name}{suffix}")

        if item.is_dir():
            extension = "    " if last else "│   "
            lines.extend(build_tree(item, root, out, ignore, prefix + extension))

    return lines


def discover_files(root: Path, out: Path, ignore: set[str]) -> tuple[list[Path], list[Path], list[Path]]:
    python_files: list[Path] = []
    config_files: list[Path] = []
    skipped_sensitive: list[Path] = []

    for path in root.rglob("*"):
        if is_ignored(path, root, out, ignore) or not path.is_file():
            continue

        if is_sensitive_file(path):
            skipped_sensitive.append(path)
            continue

        suffix = path.suffix.lower()
        if suffix == ".py":
            python_files.append(path)
        elif suffix in CONFIG_EXTENSIONS:
            config_files.append(path)

    python_files.sort(key=lambda path: path.relative_to(root).as_posix().lower())
    config_files.sort(key=lambda path: path.relative_to(root).as_posix().lower())
    skipped_sensitive.sort(key=lambda path: path.relative_to(root).as_posix().lower())
    return python_files, config_files, skipped_sensitive


def module_group(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    parts = [part.lower() for part in relative.parts]

    if "tests" in parts or relative.name.lower().startswith("test_"):
        return "tests"
    if "scripts" in parts:
        return "scripts"
    if "common" in parts or "shared" in parts:
        return "common"
    if "app" in parts or "application" in parts or "cli" in parts:
        return "application"
    if "domain" in parts or "services" in parts:
        return "domain_services"
    if any(name in parts for name in ("storage", "staging", "silver", "gold", "connectors", "infrastructure")):
        return "data_infrastructure"
    return parts[0] if parts else "root"


def distribute_semantically(files: list[Path], root: Path, part_count: int) -> list[list[Path]]:
    """
    Agrupa arquivos relacionados e distribui os grupos entre as partes.

    Arquivos pequenos do mesmo domínio ficam juntos no mesmo Markdown, em vez
    de serem espalhados apenas para equilibrar bytes.
    """
    groups: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        groups[module_group(path, root)].append(path)

    weighted_groups = sorted(
        groups.items(),
        key=lambda item: sum(path.stat().st_size for path in item[1]),
        reverse=True,
    )

    parts: list[list[Path]] = [[] for _ in range(part_count)]
    sizes = [0] * part_count

    for _, grouped_files in weighted_groups:
        small_files = [path for path in grouped_files if path.stat().st_size <= 30_000]
        large_files = [path for path in grouped_files if path.stat().st_size > 30_000]

        if small_files:
            index = sizes.index(min(sizes))
            parts[index].extend(small_files)
            sizes[index] += sum(path.stat().st_size for path in small_files)

        for path in large_files:
            index = sizes.index(min(sizes))
            parts[index].append(path)
            sizes[index] += path.stat().st_size

    for part in parts:
        part.sort(key=lambda path: (module_group(path, root), path.relative_to(root).as_posix().lower()))

    return parts


def detect_internal_dependencies(analyses: list[FileAnalysis], python_files: list[Path], root: Path) -> dict[str, list[str]]:
    module_to_path: dict[str, str] = {}

    for path in python_files:
        relative = path.relative_to(root)
        parts = list(relative.with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        module_to_path[".".join(parts)] = relative.as_posix()
        if parts and parts[0] == "src":
            module_to_path[".".join(parts[1:])] = relative.as_posix()

    dependencies: dict[str, list[str]] = {}
    for analysis in analyses:
        resolved: set[str] = set()
        for imported in analysis.imports:
            candidates = [imported]
            pieces = imported.split(".")
            candidates.extend(".".join(pieces[:i]) for i in range(len(pieces) - 1, 0, -1))
            for candidate in candidates:
                if candidate in module_to_path and module_to_path[candidate] != analysis.path:
                    resolved.add(module_to_path[candidate])
                    break
        dependencies[analysis.path] = sorted(resolved)

    return dependencies


def write_readme(out: Path, part_count: int) -> None:
    order = [
        "01_CONTEXTO.md",
        "02_ESTRUTURA.md",
        "03_CONFIGURACOES.md",
        "04_RESUMO_TECNICO.md",
        "05_DEPENDENCIAS.md",
        "06_ALERTAS.md",
    ]
    order.extend(f"{7 + index:02d}_CODIGO_PARTE_{index + 1}.md" for index in range(part_count))
    order.append("manifest.json")

    lines = [
        "# AI_CONTEXT",
        "",
        "Pacote gerado automaticamente para análise do projeto por IA.",
        "",
        "## Ordem sugerida de leitura",
        "",
    ]
    lines.extend(f"{index}. `{name}`" for index, name in enumerate(order, start=1))
    lines.extend(
        [
            "",
            "## Observações",
            "",
            "- Os arquivos Python menores são consolidados junto a outros arquivos do mesmo domínio.",
            "- O código-fonte permanece integral nos arquivos `CODIGO_PARTE_*`.",
            "- Possíveis segredos e caminhos de usuário são mascarados por padrão.",
            "- Arquivos potencialmente sensíveis, como `.env`, chaves e credenciais, não são incluídos.",
            "- `manifest.json` registra hashes e estatísticas para confirmar qual versão foi enviada à IA.",
        ]
    )
    (out / "00_README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_context(
    out: Path,
    root: Path,
    python_files: list[Path],
    config_files: list[Path],
    analyses: list[FileAnalysis],
    skipped_sensitive: list[Path],
) -> None:
    total_lines = sum(item.lines for item in analyses)
    total_bytes = sum(path.stat().st_size for path in python_files + config_files)
    syntax_errors = sum(1 for item in analyses if item.syntax_error)
    read_errors = sum(1 for item in analyses if item.read_error)

    content = dedent(
        f"""\
        # CONTEXTO

        ## Projeto

        - Nome: `{root.name}`
        - Raiz analisada: `{root}`
        - Gerado em UTC: `{datetime.now(timezone.utc).isoformat()}`

        ## Inventário

        - Arquivos Python: **{len(python_files)}**
        - Arquivos de configuração: **{len(config_files)}**
        - Linhas Python: **{total_lines}**
        - Volume analisado: **{total_bytes} bytes**
        - Erros de sintaxe detectados: **{syntax_errors}**
        - Erros de leitura: **{read_errors}**
        - Arquivos sensíveis ignorados: **{len(skipped_sensitive)}**

        ## Finalidade

        Este pacote fornece estrutura, configurações sanitizadas, inventário de símbolos,
        dependências internas, alertas estatísticos e código-fonte consolidado para auditoria por IA.
        """
    )
    (out / "01_CONTEXTO.md").write_text(content, encoding="utf-8")


def write_structure(out: Path, root: Path, ignore: set[str]) -> None:
    lines = ["# ESTRUTURA", "", f"{root.name}/"]
    lines.extend(build_tree(root, root, out, ignore))
    (out / "02_ESTRUTURA.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def code_fence_language(path: Path) -> str:
    return {
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
        ".py": "python",
    }.get(path.suffix.lower(), "text")


def write_configurations(
    out: Path,
    root: Path,
    config_files: list[Path],
    sanitize: bool,
    max_bytes: int,
) -> dict[str, int]:
    report = {"sanitized_values": 0, "oversized_configs": 0, "read_errors": 0}

    with (out / "03_CONFIGURACOES.md").open("w", encoding="utf-8") as stream:
        stream.write("# CONFIGURAÇÕES\n\n")
        stream.write("As configurações abaixo foram sanitizadas quando necessário.\n")

        for path in config_files:
            relative = path.relative_to(root).as_posix()
            stream.write(f"\n\n---\n\n## `{relative}`\n\n")
            stream.write(f"- Tamanho: {path.stat().st_size} bytes\n")
            stream.write(f"- SHA-256: `{sha256_file(path)}`\n\n")

            if path.stat().st_size > max_bytes:
                report["oversized_configs"] += 1
                stream.write("[Conteúdo omitido por exceder o limite configurado.]\n")
                continue

            try:
                text, _ = read_text_safe(path)
            except (OSError, UnicodeError) as exc:
                report["read_errors"] += 1
                stream.write(f"[Erro ao ler: {type(exc).__name__}: {exc}]\n")
                continue

            if sanitize:
                text, replacements = sanitize_text(text)
                report["sanitized_values"] += replacements

            language = code_fence_language(path)
            stream.write(f"```{language}\n{text.rstrip()}\n```\n")

    return report


def format_symbol(symbol: SymbolInfo) -> str:
    interval = str(symbol.line)
    if symbol.end_line and symbol.end_line != symbol.line:
        interval = f"{symbol.line}-{symbol.end_line}"
    decorators = f" | decorators: {', '.join(symbol.decorators)}" if symbol.decorators else ""
    return f"- `{symbol.name}` ({symbol.kind}, linhas {interval}){decorators}"


def write_technical_summary(out: Path, analyses: list[FileAnalysis]) -> None:
    with (out / "04_RESUMO_TECNICO.md").open("w", encoding="utf-8") as stream:
        stream.write("# RESUMO TÉCNICO\n")

        for info in analyses:
            stream.write(f"\n\n---\n\n## `{info.path}`\n\n")
            stream.write(f"- Linhas: {info.lines}\n")
            stream.write(f"- Bytes: {info.bytes}\n")
            stream.write(f"- Codificação: `{info.encoding or '-'}`\n")
            stream.write(f"- SHA-256: `{info.sha256}`\n")

            if info.read_error:
                stream.write(f"- Erro de leitura: `{info.read_error}`\n")
            if info.syntax_error:
                stream.write(f"- Erro de sintaxe: `{info.syntax_error}`\n")

            stream.write("\n### Imports\n\n")
            if info.imports:
                stream.write("\n".join(f"- `{item}`" for item in info.imports) + "\n")
            else:
                stream.write("- Nenhum import detectado.\n")

            stream.write("\n### Classes\n\n")
            if info.classes:
                stream.write("\n".join(format_symbol(item) for item in info.classes) + "\n")
            else:
                stream.write("- Nenhuma classe detectada.\n")

            stream.write("\n### Funções e métodos\n\n")
            if info.functions:
                stream.write("\n".join(format_symbol(item) for item in info.functions) + "\n")
            else:
                stream.write("- Nenhuma função detectada.\n")

            if info.docstring:
                stream.write("\n### Docstring do módulo\n\n")
                stream.write(info.docstring.strip() + "\n")


def write_dependencies(out: Path, dependencies: dict[str, list[str]]) -> None:
    reverse: dict[str, list[str]] = defaultdict(list)
    for source, targets in dependencies.items():
        for target in targets:
            reverse[target].append(source)

    with (out / "05_DEPENDENCIAS.md").open("w", encoding="utf-8") as stream:
        stream.write("# DEPENDÊNCIAS INTERNAS\n\n")
        stream.write("Mapa aproximado baseado em imports estáticos analisáveis por AST.\n")

        for source in sorted(dependencies):
            stream.write(f"\n## `{source}`\n\n")
            targets = dependencies[source]
            if targets:
                stream.write("\n".join(f"- importa `{target}`" for target in targets) + "\n")
            else:
                stream.write("- Nenhuma dependência interna resolvida.\n")

        stream.write("\n# MÓDULOS INTERNOS MAIS REFERENCIADOS\n\n")
        ranking = sorted(reverse.items(), key=lambda item: len(item[1]), reverse=True)
        for target, sources in ranking:
            stream.write(f"- `{target}`: {len(sources)} consumidor(es)\n")


def write_alerts(out: Path, alerts: list[Alert]) -> None:
    severity_order = {"ALTA": 0, "MÉDIA": 1, "BAIXA": 2}
    alerts.sort(key=lambda item: (severity_order.get(item.severity, 9), item.path, item.line))

    with (out / "06_ALERTAS.md").open("w", encoding="utf-8") as stream:
        stream.write("# ALERTAS ESTATÍSTICOS\n\n")
        stream.write(
            "Alertas heurísticos para orientar revisão humana. Eles não provam que o código está incorreto.\n\n"
        )

        if not alerts:
            stream.write("Nenhum alerta heurístico encontrado.\n")
            return

        counts: dict[str, int] = defaultdict(int)
        for alert in alerts:
            counts[alert.severity] += 1

        stream.write("## Resumo\n\n")
        for severity in ("ALTA", "MÉDIA", "BAIXA"):
            stream.write(f"- {severity}: {counts[severity]}\n")

        stream.write("\n## Ocorrências\n")
        for alert in alerts:
            stream.write(
                f"\n- **{alert.severity}** | `{alert.category}` | "
                f"`{alert.path}:{alert.line}` | {alert.message}\n"
            )


def write_code_parts(
    out: Path,
    root: Path,
    parts: list[list[Path]],
    analyses_by_path: dict[str, FileAnalysis],
    sanitize: bool,
) -> dict[str, int]:
    report = {"sanitized_values": 0, "read_errors": 0}

    for index, paths in enumerate(parts, start=1):
        output_name = f"{6 + index:02d}_CODIGO_PARTE_{index}.md"
        with (out / output_name).open("w", encoding="utf-8") as stream:
            stream.write(f"# CÓDIGO PARTE {index}\n\n")
            stream.write(
                "Arquivos consolidados por afinidade de domínio, mantendo arquivos pequenos relacionados juntos.\n"
            )

            current_group = None
            for path in paths:
                group = module_group(path, root)
                if group != current_group:
                    stream.write(f"\n\n# GRUPO: {group}\n")
                    current_group = group

                relative = path.relative_to(root).as_posix()
                info = analyses_by_path[relative]
                stream.write(f"\n\n---\n\n## `{relative}`\n\n")
                stream.write(f"- Linhas: {info.lines}\n")
                stream.write(f"- SHA-256: `{info.sha256}`\n")
                stream.write(
                    f"- Classes: {', '.join(item.name for item in info.classes) or '-'}\n"
                )
                stream.write(
                    f"- Funções: {', '.join(item.name for item in info.functions) or '-'}\n\n"
                )

                try:
                    text, _ = read_text_safe(path)
                except (OSError, UnicodeError) as exc:
                    report["read_errors"] += 1
                    stream.write(f"[Erro ao ler: {type(exc).__name__}: {exc}]\n")
                    continue

                if sanitize:
                    text, replacements = sanitize_text(text)
                    report["sanitized_values"] += replacements

                stream.write(f"```python\n{text.rstrip()}\n```\n")

    return report


def write_manifest(
    out: Path,
    root: Path,
    analyses: list[FileAnalysis],
    config_files: list[Path],
    skipped_sensitive: list[Path],
    part_count: int,
    sanitization_enabled: bool,
    sanitization_count: int,
) -> None:
    manifest = {
        "generator": "gerar_contexto_ia.py",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_name": root.name,
        "project_root": str(root),
        "parts": part_count,
        "sanitization_enabled": sanitization_enabled,
        "sanitized_occurrences": sanitization_count,
        "python_files": [asdict(item) for item in analyses],
        "config_files": [
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in config_files
        ],
        "skipped_sensitive_files": [
            path.relative_to(root).as_posix() for path in skipped_sensitive
        ],
    }

    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    out = (args.out.resolve() if args.out else root / "AI_CONTEXT")
    ignore = set(DEFAULT_IGNORE)
    ignore.add(out.name)

    if args.partes < 1:
        raise ValueError("--partes deve ser maior ou igual a 1.")
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Raiz inválida: {root}")
    if out == root:
        raise ValueError("O diretório de saída não pode ser igual à raiz do projeto.")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    python_files, config_files, skipped_sensitive = discover_files(root, out, ignore)
    analyses = [analyze_python(path, root) for path in python_files]
    analyses_by_path = {item.path: item for item in analyses}

    alerts: list[Alert] = []
    for path in python_files:
        alerts.extend(scan_alerts(path, root))

    dependencies = detect_internal_dependencies(analyses, python_files, root)
    parts = distribute_semantically(python_files, root, args.partes)
    sanitize = not args.sem_sanitizacao

    write_readme(out, args.partes)
    write_context(out, root, python_files, config_files, analyses, skipped_sensitive)
    write_structure(out, root, ignore)
    config_report = write_configurations(
        out,
        root,
        config_files,
        sanitize=sanitize,
        max_bytes=args.max_config_bytes,
    )
    write_technical_summary(out, analyses)
    write_dependencies(out, dependencies)
    write_alerts(out, alerts)
    code_report = write_code_parts(out, root, parts, analyses_by_path, sanitize=sanitize)

    sanitization_count = (
        config_report["sanitized_values"] + code_report["sanitized_values"]
    )
    write_manifest(
        out,
        root,
        analyses,
        config_files,
        skipped_sensitive,
        args.partes,
        sanitize,
        sanitization_count,
    )

    print("Contexto para IA gerado com sucesso.")
    print(f"Saída: {out}")
    print(f"Python: {len(python_files)} arquivo(s)")
    print(f"Configurações: {len(config_files)} arquivo(s)")
    print(f"Partes de código: {args.partes}")
    print(f"Alertas: {len(alerts)}")
    print(f"Arquivos sensíveis ignorados: {len(skipped_sensitive)}")
    print(f"Ocorrências sanitizadas: {sanitization_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```


# GRUPO: src


---

## `src/control/__init__.py`

- Linhas: 1
- SHA-256: `d3ca3f3a650cfe2dba096307c2555bde1882db0a709abfc618fe728324844a25`
- Classes: -
- Funções: -

```python
"""Carregadores de arquivos de controle do sistema BDC."""
```


---

## `src/control/carregador_de_mapeamento.py`

- Linhas: 73
- SHA-256: `623f9ff6574ace3c82363e7948de33e0d031dec66fb84c9729840e74c754dffd`
- Classes: -
- Funções: carregar_e_validar_mapeamento, mapeamento_de_carga_fichas_comercializadoras, mapeamento_de_carga_fichas_consumidores

```python
"""Carregamento e validação estrita dos mappings das fichas."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.context import AppContext
from common.json import ler_json
from common.json import validar_esquema_json

def carregar_e_validar_mapeamento(
    mapping_path: Path,
    schema_path: Path,
    descricao: str,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega um mapping de fichas e valida estritamente contra seu JSON Schema."""
    try:
        logger.info("Carregando %s: %s", descricao, mapping_path)

        if not mapping_path.exists():
            raise FileNotFoundError(f"Arquivo de mapping não encontrado: {mapping_path}")
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_path}")

        content = ler_json(mapping_path)
        schema = ler_json(schema_path)

        validar_esquema_json(instance=content, schema=schema, label=descricao)

        if not isinstance(content, list):
            raise ValueError(f"O {descricao} deve ser uma lista.")

        logger.info(
            "%s carregado e validado com sucesso. Quantidade de registros: %s",
            descricao,
            len(content),
        )

        return content

    except Exception:
        logger.exception("Falha crítica ao carregar e validar %s", descricao)
        raise


def mapeamento_de_carga_fichas_comercializadoras(
    context: AppContext,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega e valida o mapping de fichas de comercializadoras."""
    return carregar_e_validar_mapeamento(
        mapping_path=context.control_file("mapping_fichas_comercializadoras"),
        schema_path=context.control_file("schema_mapping_fichas_comercializadoras"),
        descricao="Mapping de Comercializadoras",
        logger=logger,
    )


def mapeamento_de_carga_fichas_consumidores(
    context: AppContext,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    """Carrega e valida o mapping de fichas de consumidores."""
    return carregar_e_validar_mapeamento(
        mapping_path=context.control_file("mapping_fichas_consumidores"),
        schema_path=context.control_file("schema_mapping_fichas_consumidores"),
        descricao="Mapping de Consumidores",
        logger=logger,
    )
```


---

## `src/control/layout_catalog.py`

- Linhas: 123
- SHA-256: `89ed7f9d677d522a831f5cd944071b45eca1efbe266b05cf6fc3ff99129476eb`
- Classes: -
- Funções: validar_estrutura_do_layout, carregar_catalogo_de_layouts, carregar_layouts_comercializadoras, carregar_layouts_consumidores

```python
"""Carregamento e validação dos layouts de fichas."""

from __future__ import annotations

import sys
from typing import Any

from app.context import AppContext
from common.json import ler_json


def validar_estrutura_do_layout(layout: dict[str, Any], versao: str, logger: Any) -> None:
    """Valida se o layout possui a estrutura mínima para não quebrar o extrator."""
    if "field_map" not in layout:
        logger.critical("Layout '%s' inválido: chave 'field_map' ausente.", versao)
        sys.exit(1)
        
    for field_name, config in layout["field_map"].items():
        if not config.get("implemented", True):
            continue
            
        has_static = "value_cell" in config and config["value_cell"] not in [None, "0", 0]
        has_dynamic = "search_pattern" in config and config["search_pattern"] not in [None, ""]
        
        if not has_static and not has_dynamic:
            logger.debug(
                "Layout '%s' - Campo '%s': sem âncora estática ou dinâmica. Retornará vazio.", 
                versao, field_name
            )


def carregar_catalogo_de_layouts(
    catalog_path: str,
    logger: Any | None = None,
) -> dict[str, Any]:
    """Carrega o catálogo consolidado de layouts."""
    try:
        if logger is not None:
            logger.info("Carregando catálogo de layouts: %s", catalog_path)

        catalog = ler_json(catalog_path)

        if logger is not None:
            logger.info("Catálogo de layouts carregado com sucesso.")

        return catalog

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar catálogo de layouts: %s", catalog_path)
        raise


def carregar_layouts_comercializadoras(
    context: AppContext,
    logger: Any | None = None,
) -> dict[str, dict[str, Any]]:
    """Carrega e valida os layouts de fichas de comercializadoras."""
    layouts: dict[str, dict[str, Any]] = {}

    try:
        if logger is not None:
            logger.info("Iniciando carga dos layouts de comercializadoras.")

        for version in range(1, 8):
            key = f"layout_ficha_comercializadora_v{version}"
            layout_path = context.control_file(key)

            layout_data = ler_json(layout_path)
            
            if logger is not None:
                validar_estrutura_do_layout(layout_data, key, logger)

            layouts[f"padrao_{version}"] = layout_data

        if logger is not None:
            logger.info(
                "Layouts de comercializadoras carregados com sucesso. Quantidade: %s",
                len(layouts),
            )

        return layouts

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar layouts de comercializadoras.")
        raise


def carregar_layouts_consumidores(
    context: AppContext,
    logger: Any | None = None,
) -> dict[str, dict[str, Any]]:
    """Carrega e valida os layouts de fichas de consumidores."""
    layouts: dict[str, dict[str, Any]] = {}

    try:
        if logger is not None:
            logger.info("Iniciando carga dos layouts de consumidores.")

        for version in range(1, 4):
            key = f"layout_ficha_consumidor_v{version}"
            layout_path = context.control_file(key)

            layout_data = ler_json(layout_path)
            
            if logger is not None:
                validar_estrutura_do_layout(layout_data, key, logger)

            layouts[f"padrao_{version}"] = layout_data

        if logger is not None:
            logger.info(
                "Layouts de consumidores carregados com sucesso. Quantidade: %s",
                len(layouts),
            )

        return layouts

    except Exception:
        if logger is not None:
            logger.exception("Falha ao carregar layouts de consumidores.")
        raise
```


---

## `src/control/logger.py`

- Linhas: 44
- SHA-256: `a7cc9461c938145db6ff54a50b1ed369a6575ebb00c1dd0387ce94971fc184e0`
- Classes: -
- Funções: obter_logger

```python
"""Configuração padronizada de loggers do sistema BDC."""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

def obter_logger(name: str, file_path: str | Path | None = None) -> logging.Logger:
    """Cria ou devolve um logger com saída centralizada em arquivo e console."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    logger.propagate = False 

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if file_path:
        target = Path(file_path)
    else:
        hoje = datetime.now().strftime("%Y-%m-%d")
        log_dir = Path("LOGS/general")
        target = log_dir / f"{hoje}_general.log"
        
    target.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(target, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
```


---

## `src/control/quality_loader.py`

- Linhas: 71
- SHA-256: `4a3636b5650dfcea38005004b36cb5cf4b1ef1b7db0079d87f5ef41e02cae20e`
- Classes: -
- Funções: _carregar_e_validar_regras_de_qualidade, carregar_regras_de_qualidade_de_dados_comercializadoras, carregar_regras_de_qualidade_de_dados_consumidores

```python
"""Carregamento e validação estrita das regras de qualidade da entidade.

feat(T1.1.2): Integra validação contra JSON Schema (mesmo padrão de mapping_loader.py).
Regras malformadas geram erro descritivo antes do processamento de qualquer ficha.
Ref: §5.2, §5.3 do Planejamento Funcional.
"""
from __future__ import annotations

from typing import Any
from pathlib import Path

from app.context import AppContext
from common.json import ler_json
from common.json import validar_esquema_json


def _carregar_e_validar_regras_de_qualidade(
    rules_path: Path,
    schema_path: Path,
    descricao: str,
    logger: Any,
) -> dict[str, Any]:
    """Carrega um arquivo de quality rules e valida contra seu JSON Schema."""
    try:
        logger.info("Carregando %s: %s", descricao, rules_path)

        if not rules_path.exists():
            raise FileNotFoundError(f"Arquivo de quality rules não encontrado: {rules_path}")

        if not schema_path.exists():
            raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_path}")

        content = ler_json(rules_path)
        schema = ler_json(schema_path)

        validar_esquema_json(instance=content, schema=schema, label=descricao)

        if not isinstance(content, dict):
            raise ValueError(f"O {descricao} deve ser um objeto JSON.")

        logger.info("%s carregado e validado com sucesso.", descricao)

        return content

    except Exception:
        logger.exception("Falha crítica ao carregar e validar %s", descricao)
        raise


def carregar_regras_de_qualidade_de_dados_comercializadoras(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega as regras de qualidade das fichas de comercializadoras usando o novo master_catalog."""
    
    master_catalog_path = context.path("control_quality") / "master_catalog_comercializadoras.json"
    
    logger.info("Lendo master catalog: %s", master_catalog_path)
    return ler_json(master_catalog_path)


def carregar_regras_de_qualidade_de_dados_consumidores(
    context: AppContext,
    logger: Any,
) -> dict[str, Any]:
    """Carrega as regras de qualidade das fichas de consumidores usando o novo master_catalog."""
    
    master_catalog_path = context.path("control_quality") / "master_catalog_consumidores.json"
    
    logger.info("Lendo master catalog consumidores: %s", master_catalog_path)
    return ler_json(master_catalog_path)
```


---

## `src/relational/dimensions/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/relational/dimensions/dim_contraparte.py`

- Linhas: 89
- SHA-256: `73d2734e2e5fe0bf781bda66192ef275d9ba65b5752ee6923d65048fb1c17347`
- Classes: -
- Funções: criar_dim_contraparte

```python
"""Serviço de consolidação da Dimensão de Contraparte."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def criar_dim_contraparte(
    context: AppContext, 
    df_silver_receita: pd.DataFrame, 
    df_silver_segmentacao: pd.DataFrame,
    df_silver_salesforce_account: pd.DataFrame = None,
    df_silver_fichas: pd.DataFrame = None
) -> dict[str, Any]:
    run_id = f"DIM_CTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = logging.getLogger("bdc.gold.dim_contraparte")

    if df_silver_receita.empty:
        df_silver_receita = pd.DataFrame(columns=["CNPJ", "SITUACAO_CADASTRAL", "NATUREZA_JURIDICA", "CNAE_PRINCIPAL"])
    if df_silver_segmentacao.empty:
        df_silver_segmentacao = pd.DataFrame(columns=["CNPJ", "VOLUME_ENQUADRAMENTO_MWM", "POSSUI_PELO_MENOS_5_MWM", "SEGMENTO_METODOLOGICO"])

    from common.identificadores import normalizar_cnpj
    df_silver_receita["CNPJ"] = df_silver_receita["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    df_silver_segmentacao["CNPJ"] = df_silver_segmentacao["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)

    df_dim = pd.merge(df_silver_receita, df_silver_segmentacao, on="CNPJ", how="outer")

    if df_silver_fichas is not None and not df_silver_fichas.empty:
        df_fichas = df_silver_fichas.copy()
        df_fichas["CNPJ"] = df_fichas["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
        df_fichas["NOME_FICHA"] = df_fichas.get("EMPRESA", None)
        df_fichas["SIGLA_FICHA"] = df_fichas.get("SIGLA", None)
        
        col_sort = "DT_PROCESSAMENTO" if "DT_PROCESSAMENTO" in df_fichas.columns else "CNPJ"
        df_id_fichas = df_fichas.sort_values(col_sort).drop_duplicates("CNPJ", keep="last")[["CNPJ", "NOME_FICHA", "SIGLA_FICHA"]]
        df_dim = pd.merge(df_dim, df_id_fichas, on="CNPJ", how="outer")
    else:
        df_dim["NOME_FICHA"] = None
        df_dim["SIGLA_FICHA"] = None

    if df_silver_salesforce_account is not None and not df_silver_salesforce_account.empty:
        df_sf = df_silver_salesforce_account.copy()
        df_sf["CNPJ"] = df_sf["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
        sf_cols = {"CNPJ": "CNPJ", "Name": "NOME_SF", "Sigla__c": "SIGLA_SF"}
        df_sf_id = df_sf[[c for c in sf_cols.keys() if c in df_sf.columns]].rename(columns=sf_cols)
        df_sf_id = df_sf_id.drop_duplicates(subset=["CNPJ"], keep="last")
        df_dim = pd.merge(df_dim, df_sf_id, on="CNPJ", how="outer")
    else:
        df_dim["NOME_SF"] = None
        df_dim["SIGLA_SF"] = None

    for col_safe in ["NOME_SF", "SIGLA_SF", "NOME_FICHA", "SIGLA_FICHA"]:
        if col_safe not in df_dim.columns:
            df_dim[col_safe] = None

    df_dim["NOME"] = df_dim["NOME_SF"].combine_first(df_dim["NOME_FICHA"])
    df_dim["SIGLA"] = df_dim["SIGLA_SF"].combine_first(df_dim["SIGLA_FICHA"])

    df_dim = df_dim.dropna(subset=["CNPJ"])
    df_dim = df_dim.dropna(subset=["CNPJ"])
    df_dim["CNPJ_RAIZ"] = df_dim["CNPJ"].str[:8]
    
    # Garante a existência das colunas para evitar KeyError
    for col in ["SITUACAO_CADASTRAL", "SEGMENTO_METODOLOGICO", "CNAE_PRINCIPAL"]:
        if col not in df_dim.columns:
            df_dim[col] = None
            
    df_dim["SITUACAO_CADASTRAL"] = df_dim["SITUACAO_CADASTRAL"].fillna("NAO_INFORMADO")
    df_dim["SEGMENTO_METODOLOGICO"] = df_dim["SEGMENTO_METODOLOGICO"].fillna("NAO_ENQUADRADO")

    schema_dim = {
        "CNPJ": "CNPJ", "NOME": "NOME", "SIGLA": "SIGLA", "CNPJ_RAIZ": "CNPJ_RAIZ", 
        "SITUACAO_CADASTRAL": "SITUACAO_CADASTRAL", "CNAE_PRINCIPAL": "SETOR", 
        "SEGMENTO_METODOLOGICO": "SEGMENTO_METODOLOGICO"
    }
    
    df_final = df_dim[list(schema_dim.keys())].rename(columns=schema_dim).copy()
    
    relational_dir = context.path("relational_dimensions") / "contrapartes"
    relational_dir.mkdir(parents=True, exist_ok=True)
    escrever_conjunto_de_dados_silver(df_final.to_dict(orient="records"), relational_dir, f"dim_contraparte_{run_id}")
    df_final.to_parquet(relational_dir / "dim_contraparte.parquet", index=False)

    logger.info("Dimensão Contraparte construída com COALESCE. Registros: %d", len(df_final))
    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}
```


---

## `src/relational/facts/__init__.py`

- Linhas: 0
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classes: -
- Funções: -

```python

```


---

## `src/relational/facts/fato_alerta_util.py`

- Linhas: 134
- SHA-256: `560e0a1056c94affa33d93150d8c15785cf13b4094863dd6597e952b89931a34`
- Classes: -
- Funções: registrar_alerta, registrar_alertas_em_lote

```python
"""Serviço de registro unificado de alertas no modelo Star Schema (Fato Alerta)."""
from typing import Any
import pandas as pd
from datetime import datetime
from pathlib import Path

def registrar_alerta(
    codigo: str,
    severidade: str,
    regra: str,
    mensagem: str,
    campo_afetado: str | None,
    valor_observado: Any,
    limite_esperado: Any,
    contraparte_id: str | None,
    run_id: str,
    context: Any,
    status_tratamento: str = "ABERTO",
    responsavel: str | None = None,
    evidencia_encerramento: str | None = None,
) -> None:
    """Registra um único alerta de negócio na Fato Alerta de Crédito (Star Schema)."""
    
    agora = datetime.now()
    novo_alerta = {
        "CNPJ": str(contraparte_id) if contraparte_id else None,
        "CODIGO_ALERTA": str(codigo),
        "SEVERIDADE": str(severidade),
        "REGRA": str(regra),
        "MENSAGEM_DESCRITIVA": str(mensagem),
        "DATA_DETECCAO": agora,
        "CAMPO_AFETADO": str(campo_afetado) if campo_afetado else None,
        "VALOR_OBSERVADO": str(valor_observado) if valor_observado is not None else None,
        "LIMITE_ESPERADO": str(limite_esperado) if limite_esperado is not None else None,
        "STATUS_TRATAMENTO": str(status_tratamento),
        "RESPONSAVEL": str(responsavel) if responsavel else None,
        "EVIDENCIA_ENCERRAMENTO": str(evidencia_encerramento) if evidencia_encerramento else None,
        "RUN_ID": str(run_id)
    }
    
    colunas_exigidas = [
        "CNPJ", "CODIGO_ALERTA", "SEVERIDADE", "REGRA", "MENSAGEM_DESCRITIVA", 
        "DATA_DETECCAO", "CAMPO_AFETADO", "VALOR_OBSERVADO", "LIMITE_ESPERADO", 
        "STATUS_TRATAMENTO", "RESPONSAVEL", "EVIDENCIA_ENCERRAMENTO", "RUN_ID"
    ]
    
    df_novo = pd.DataFrame([novo_alerta], columns=colunas_exigidas)
    
    out_dir = context.path("relational_facts") / "alertas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_parquet = out_dir / "fato_alerta_credito.parquet"
    out_csv = out_dir / "fato_alerta_credito.csv"
    
    if out_parquet.exists():
        try:
            df_existente = pd.read_parquet(out_parquet)
            for col in colunas_exigidas:
                if col not in df_existente.columns:
                    df_existente[col] = None
            df_existente = df_existente[colunas_exigidas]
            df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        except Exception:
            df_final = df_novo
    else:
        df_final = df_novo
        
    # Defesa contra PyArrow: Homogeneização estrita dos tipos antes da serialização
    df_final["DATA_DETECCAO"] = pd.to_datetime(df_final["DATA_DETECCAO"], errors="coerce")
    for col in colunas_exigidas:
        if col != "DATA_DETECCAO":
            df_final[col] = df_final[col].astype("string")
        
    df_final.to_parquet(out_parquet, index=False)
    df_final.to_csv(out_csv, index=False, sep=";", encoding="utf-8-sig")

def registrar_alertas_em_lote(alertas_list: list[dict], run_id: str, context: Any) -> None:
    """Registra múltiplos alertas de negócio de uma vez, otimizando I/O."""
    if not alertas_list:
        return
        
    agora = datetime.now()
    
    colunas_exigidas = [
        "CNPJ", "CODIGO_ALERTA", "SEVERIDADE", "REGRA", "MENSAGEM_DESCRITIVA", 
        "DATA_DETECCAO", "CAMPO_AFETADO", "VALOR_OBSERVADO", "LIMITE_ESPERADO", 
        "STATUS_TRATAMENTO", "RESPONSAVEL", "EVIDENCIA_ENCERRAMENTO", "RUN_ID"
    ]
    
    novos_alertas = []
    for alerta in alertas_list:
        novos_alertas.append({
            "CNPJ": str(alerta.get("contraparte_id")) if alerta.get("contraparte_id") else None,
            "CODIGO_ALERTA": str(alerta.get("codigo")),
            "SEVERIDADE": str(alerta.get("severidade")),
            "REGRA": str(alerta.get("regra")),
            "MENSAGEM_DESCRITIVA": str(alerta.get("mensagem")),
            "DATA_DETECCAO": agora,
            "CAMPO_AFETADO": str(alerta.get("campo_afetado")) if alerta.get("campo_afetado") else None,
            "VALOR_OBSERVADO": str(alerta.get("valor_observado")) if alerta.get("valor_observado") is not None else None,
            "LIMITE_ESPERADO": str(alerta.get("limite_esperado")) if alerta.get("limite_esperado") is not None else None,
            "STATUS_TRATAMENTO": str(alerta.get("status_tratamento", "ABERTO")),
            "RESPONSAVEL": str(alerta.get("responsavel")) if alerta.get("responsavel") else None,
            "EVIDENCIA_ENCERRAMENTO": str(alerta.get("evidencia_encerramento")) if alerta.get("evidencia_encerramento") else None,
            "RUN_ID": str(run_id)
        })
        
    df_novo = pd.DataFrame(novos_alertas, columns=colunas_exigidas)
    
    out_dir = context.path("relational_facts") / "alertas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_parquet = out_dir / "fato_alerta_credito.parquet"
    out_csv = out_dir / "fato_alerta_credito.csv"
    
    if out_parquet.exists():
        try:
            df_existente = pd.read_parquet(out_parquet)
            for col in colunas_exigidas:
                if col not in df_existente.columns:
                    df_existente[col] = None
            df_existente = df_existente[colunas_exigidas]
            df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        except Exception:
            df_final = df_novo
    else:
        df_final = df_novo
        
    # Defesa contra PyArrow: Homogeneização estrita dos tipos antes da serialização
    df_final["DATA_DETECCAO"] = pd.to_datetime(df_final["DATA_DETECCAO"], errors="coerce")
    for col in colunas_exigidas:
        if col != "DATA_DETECCAO":
            df_final[col] = df_final[col].astype("string")
        
    df_final.to_parquet(out_parquet, index=False)
    df_final.to_csv(out_csv, index=False, sep=";", encoding="utf-8-sig")
```


---

## `src/relational/facts/fato_alertas.py`

- Linhas: 136
- SHA-256: `9f7395b590bcb6a02f8faf0de518b3b75c94e85d336c9d61039fb4c3c5d613d4`
- Classes: -
- Funções: gerar_fato_alertas_credito

```python
"""Serviço de geração de alertas de crédito no padrão Star Schema (Fato Alerta)."""
import pandas as pd
from datetime import datetime
from typing import Any

from pathlib import Path
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def gerar_fato_alertas_credito(context: Any) -> dict[str, Any]:
    run_id = f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.alertas", Path("LOGS/relacional") / f"{run_id}__servico_alertas.log")
    logger.info("Iniciando geração da Fato Alerta de Crédito (Star Schema)...")

    colunas_exigidas = [
        "CNPJ", "CODIGO_ALERTA", "SEVERIDADE", "REGRA", "MENSAGEM_DESCRITIVA", 
        "DATA_DETECCAO", "CAMPO_AFETADO", "VALOR_OBSERVADO", "LIMITE_ESPERADO", 
        "STATUS_TRATAMENTO", "RESPONSAVEL", "EVIDENCIA_ENCERRAMENTO"
    ]

    path_gold = context.path("saidas") / "gold" / "visao_operacional_negocio" / "Visao_Operacional_BDC_LATEST.parquet"
    if not path_gold.exists():
        logger.warning(f"Base Gold LATEST não encontrada em {path_gold}. Abortando alertas.")
        return {"run_id": run_id, "alertas_gerados": 0, "status": "SEM_BASE"}

    df_gold = pd.read_parquet(path_gold)
    
    alertas = []
    agora = datetime.now()

    for _, row in df_gold.iterrows():
        cnpj = row.get("CNPJ")
        if pd.isna(cnpj) or not str(cnpj).strip():
            continue
            
        status_contratual = str(row.get("STATUS_CONTRATUAL", ""))
        sit_analise = str(row.get("SITUACAO_ANALISE", ""))
        metodologia = str(row.get("METODOLOGIA_EXIGIDA", ""))
        vol_mwm = pd.to_numeric(row.get("VOLUME_MWM"), errors="coerce")
        if pd.isna(vol_mwm): vol_mwm = 0.0

        status_calculo_pd = str(row.get("STATUS_CALCULO_PD", ""))

        if status_calculo_pd == "PENDENTE":
            alertas.append({
                "CNPJ": cnpj,
                "CODIGO_ALERTA": "PD_002",
                "SEVERIDADE": "ALTO",
                "REGRA": "Cálculo de PD Suspenso (Falta Insumo)",
                "MENSAGEM_DESCRITIVA": "O motor de crédito suspendeu o cálculo da PD devido à falta de insumos obrigatórios (ex: Rating).",
                "DATA_DETECCAO": agora,
                "CAMPO_AFETADO": "STATUS_CALCULO_PD",
                "VALOR_OBSERVADO": status_calculo_pd,
                "LIMITE_ESPERADO": "CONCLUIDO",
                "STATUS_TRATAMENTO": pd.NA,
                "RESPONSAVEL": pd.NA,
                "EVIDENCIA_ENCERRAMENTO": pd.NA
            })

        if status_contratual == "CONTRATO_VIGENTE" and sit_analise == "VENCIDA":
            alertas.append({
                "CNPJ": cnpj,
                "CODIGO_ALERTA": "ANA_001",
                "SEVERIDADE": "ALTO",
                "REGRA": "Análise Vencida com Contrato Vigente",
                "MENSAGEM_DESCRITIVA": "A contraparte possui contrato ativo, mas sua análise de crédito encontra-se expirada.",
                "DATA_DETECCAO": agora,
                "CAMPO_AFETADO": "SITUACAO_ANALISE",
                "VALOR_OBSERVADO": sit_analise,
                "LIMITE_ESPERADO": "VIGENTE",
                "STATUS_TRATAMENTO": pd.NA,
                "RESPONSAVEL": pd.NA,
                "EVIDENCIA_ENCERRAMENTO": pd.NA
            })

        if status_contratual == "CONTRATO_VIGENTE" and metodologia == "DF_DETALHADA" and sit_analise != "VIGENTE":
            alertas.append({
                "CNPJ": cnpj,
                "CODIGO_ALERTA": "SEG_001",
                "SEVERIDADE": "CRITICO",
                "REGRA": ">= 5MWm sem DF ou Irregular",
                "MENSAGEM_DESCRITIVA": "Volume exige demonstração financeira (>= 5 MWm), mas análise não está vigente.",
                "DATA_DETECCAO": agora,
                "CAMPO_AFETADO": "METODOLOGIA_EXIGIDA",
                "VALOR_OBSERVADO": f"Volume: {vol_mwm:.2f} MWm",
                "LIMITE_ESPERADO": "DF Vigente",
                "STATUS_TRATAMENTO": pd.NA,
                "RESPONSAVEL": pd.NA,
                "EVIDENCIA_ENCERRAMENTO": pd.NA
            })

        if status_contratual == "CONTRATO_VIGENTE" and metodologia == "BUREAU" and sit_analise != "VIGENTE":
            alertas.append({
                "CNPJ": cnpj,
                "CODIGO_ALERTA": "SEG_002",
                "SEVERIDADE": "MEDIO",
                "REGRA": "< 5MWm sem Bureau",
                "MENSAGEM_DESCRITIVA": "Volume permite Bureau (< 5 MWm), mas não há análise vigente.",
                "DATA_DETECCAO": agora,
                "CAMPO_AFETADO": "METODOLOGIA_EXIGIDA",
                "VALOR_OBSERVADO": f"Volume: {vol_mwm:.2f} MWm",
                "LIMITE_ESPERADO": "Bureau Vigente",
                "STATUS_TRATAMENTO": pd.NA,
                "RESPONSAVEL": pd.NA,
                "EVIDENCIA_ENCERRAMENTO": pd.NA
            })

    if alertas:
        from relational.facts.fato_alerta_util import registrar_alertas_em_lote
        
        # Mapeando os dicionários para o formato esperado pelo registrar_alertas_em_lote
        alertas_formatados = []
        for alerta in alertas:
            alertas_formatados.append({
                "contraparte_id": alerta.get("CNPJ"),
                "codigo": alerta.get("CODIGO_ALERTA"),
                "severidade": alerta.get("SEVERIDADE"),
                "regra": alerta.get("REGRA"),
                "mensagem": alerta.get("MENSAGEM_DESCRITIVA"),
                "campo_afetado": alerta.get("CAMPO_AFETADO"),
                "valor_observado": alerta.get("VALOR_OBSERVADO"),
                "limite_esperado": alerta.get("LIMITE_ESPERADO"),
                "status_tratamento": alerta.get("STATUS_TRATAMENTO", "ABERTO"),
                "responsavel": alerta.get("RESPONSAVEL"),
                "evidencia_encerramento": alerta.get("EVIDENCIA_ENCERRAMENTO")
            })
            
        registrar_alertas_em_lote(alertas_formatados, run_id, context)

    logger.info(f"Fato Alerta gerada com sucesso. Total de alertas: {len(alertas)}")
    
    return {
        "status": "SUCESSO",
        "total_alertas": len(alertas)
    }
```


---

## `src/relational/facts/fato_alertas_manuais.py`

- Linhas: 142
- SHA-256: `6bbba55379f649acda1edb70691d0829563751556acc2dc78b6844b06e2e49d5`
- Classes: -
- Funções: gerar_fato_alertas_manuais

```python
"""Serviço de geração de alertas da esteira de Carga Manual e Exceções (MAN_* e EXC_*)."""
from typing import Any
import pandas as pd
from datetime import datetime
from pathlib import Path

from control.logger import obter_logger
from relational.facts.fato_alerta_util import registrar_alertas_em_lote

def gerar_fato_alertas_manuais(context: Any) -> dict[str, Any]:
    run_id = f"MAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.alertas_manuais", Path("LOGS/relacional") / f"{run_id}__alertas_manuais.log")
    logger.info("Iniciando varredura da camada Silver para Alertas de Carga Manual...")

    alertas = []
    
    # Paths da Silver
    dir_silver = context.path("silver")
    path_comerc = dir_silver / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"
    path_consum = dir_silver / "fichas_consumidores_extraidas" / "fichas_consumidores_extraidas.parquet"
    
    dfs_para_varrer = []
    
    if path_comerc.exists():
        df_com = pd.read_parquet(path_comerc)
        df_com["_tipo_base"] = "COMERCIALIZADORA"
        dfs_para_varrer.append(df_com)
    else:
        logger.warning(f"Base Silver de Comercializadoras não encontrada: {path_comerc}")
        
    if path_consum.exists():
        df_con = pd.read_parquet(path_consum)
        df_con["_tipo_base"] = "CONSUMIDOR"
        dfs_para_varrer.append(df_con)
    else:
        logger.warning(f"Base Silver de Consumidores não encontrada: {path_consum}")
        
    if not dfs_para_varrer:
        logger.warning("Nenhuma base Silver encontrada. Abortando varredura de Carga Manual.")
        return {"run_id": run_id, "alertas_gerados": 0, "status": "SEM_BASE"}
        
    df_silver = pd.concat(dfs_para_varrer, ignore_index=True)
    logger.info(f"Total de registros a varrer na Silver: {len(df_silver)}")
    
    for _, row in df_silver.iterrows():
        cnpj = row.get("CNPJ")
        tipo_base = row.get("_tipo_base")
        tipo_ficha = str(row.get("TIPO_FICHA", "PENDENTE")).upper()
        
        # 1. MAN_002: Identificação Crítica Vazia (Fichas sem CNPJ)
        if pd.isna(cnpj) or not str(cnpj).strip():
            alertas.append({
                "codigo": "MAN_002",
                "severidade": "CRITICO",
                "regra": "Ficha sem Identificação (CNPJ)",
                "mensagem": "Extrator não conseguiu ler o CNPJ da ficha. Exige Override/Carga Manual.",
                "campo_afetado": "CNPJ",
                "valor_observado": "VAZIO",
                "limite_esperado": "CNPJ Válido",
                "contraparte_id": "DESCONHECIDO",
                "run_id": run_id
            })
            continue # Sem CNPJ, nem avalia o resto.
            
        cnpj_str = str(cnpj)
            
        # 2. MAN_003: Tipo de Ficha Pendente (Classificação Documental Falhou)
        if tipo_ficha in ("PENDENTE", "DESCONHECIDA", "DESCONHECIDO"):
            alertas.append({
                "codigo": "MAN_003",
                "severidade": "ALTO",
                "regra": "Classificação Documental Pendente",
                "mensagem": "O Motor Semântico não conseguiu classificar o tipo do documento.",
                "campo_afetado": "TIPO_FICHA",
                "valor_observado": tipo_ficha,
                "limite_esperado": "COMERCIALIZADORA / CONSUMIDOR",
                "contraparte_id": cnpj_str,
                "run_id": run_id
            })
            
        # 3. MAN_001 e DF_001: Data da DF Vazia
        data_df = row.get("DATA_DEMONSTRACAO_FINANCEIRA")
        
        if tipo_base == "COMERCIALIZADORA":
            if pd.isna(data_df) or str(data_df).strip() in ("", "NaT", "None"):
                alertas.append({
                    "codigo": "MAN_001",
                    "severidade": "ALTO",
                    "regra": "Data de Demonstração Financeira Ausente",
                    "mensagem": "Comercializadoras obrigatoriamente precisam de Data da DF válida.",
                    "campo_afetado": "DATA_DEMONSTRACAO_FINANCEIRA",
                    "valor_observado": "VAZIO",
                    "limite_esperado": "Data Válida",
                    "contraparte_id": cnpj_str,
                    "run_id": run_id
                })
                
        elif tipo_base == "CONSUMIDOR":
            vol_mwm = pd.to_numeric(row.get("VOLUME_MWM", 0), errors="coerce")
            if pd.isna(vol_mwm): vol_mwm = 0.0
            
            # Consumidores >= 5 MWm precisam ter DF
            if vol_mwm >= 5.0:
                if pd.isna(data_df) or str(data_df).strip() in ("", "NaT", "None"):
                    alertas.append({
                        "codigo": "DF_001",
                        "severidade": "CRITICO",
                        "regra": "Consumidor >= 5MWm Sem DF",
                        "mensagem": "A ficha não apresentou DF estruturada, mas o enquadramento (>5MWm) exige.",
                        "campo_afetado": "DATA_DEMONSTRACAO_FINANCEIRA",
                        "valor_observado": "VAZIO",
                        "limite_esperado": "Data Válida",
                        "contraparte_id": cnpj_str,
                        "run_id": run_id
                    })
                    
        # 4. MAN_004: Outros Campos Obrigatórios Vazios
        # Verificando PL (Patrimônio Líquido) que é crítico para Rating.
        pl = row.get("PATRIMONIO_LIQUIDO")
        if (pd.isna(pl) or str(pl).strip() in ("", "None")) and not (tipo_base == "CONSUMIDOR" and vol_mwm < 5.0):
            alertas.append({
                "codigo": "MAN_004",
                "severidade": "MEDIO",
                "regra": "Campo Crítico de Risco Vazio (PL)",
                "mensagem": "O Patrimônio Líquido não foi lido ou está nulo. Pode corromper o cálculo de PD.",
                "campo_afetado": "PATRIMONIO_LIQUIDO",
                "valor_observado": "VAZIO",
                "limite_esperado": "Valor Numérico",
                "contraparte_id": cnpj_str,
                "run_id": run_id
            })

    if alertas:
        registrar_alertas_em_lote(alertas, run_id, context)
        logger.info(f"Varredura concluída. Foram gravados {len(alertas)} alertas de Carga Manual/Exceção.")
    else:
        logger.info("Varredura concluída. Nenhum alerta de Carga Manual detectado na Silver.")

    return {
        "status": "SUCESSO",
        "total_alertas_manuais": len(alertas)
    }
```


---

## `src/relational/facts/fato_analise_credito.py`

- Linhas: 156
- SHA-256: `8c1594e1fe254940444a131e3a5b6767c545aeaf74a6d6bedcf732d2afac6659`
- Classes: -
- Funções: construir_fato_analise_credito

```python
"""Construção da tabela Fato de Análise de Crédito e Execução do Motor de Risco."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd

from app.context import AppContext
from storage.escrever_dados import escrever_conjunto_de_dados_silver
from common.json import ler_json
from pathlib import Path
from control.logger import obter_logger
from domain.contrapartes.segmentacao import definir_segmento_metodologico
from domain.credito.pd_motor import calcular_pd_ajustada
from domain.credito.pd_exceptions import PdInputValidationError

def construir_fato_analise_credito(
    context: AppContext,
    df_silver_analises: pd.DataFrame,
    df_dim_contraparte: pd.DataFrame,
) -> dict[str, Any]:
    run_id = f"FATO_ANL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.gold.fato_analise_credito", Path("LOGS/relacional") / f"{run_id}__fato_analise_credito.log")
    logger.info("Iniciando carga de fato_analise_credito e execução do Motor de Crédito (run_id=%s).", run_id)

    if df_silver_analises.empty:
        return {"run_id": run_id, "linhas": 0, "status": "SEM_DADOS"}

    df_fato = df_silver_analises.copy()
    from common.identificadores import normalizar_cnpj
    df_fato["CNPJ"] = df_fato["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    df_fato["CNPJ_RAIZ"] = df_fato["CNPJ"].str[:8]

    try:
        pd_faixas = ler_json(context.control_file("pd_faixas"))
        pd_cpura_config = ler_json(context.control_file("pd_cpura_config"))
        score_cpura_config = ler_json(context.control_file("score_cpura_config"))
        pd_transform_rules = ler_json(context.control_file("pd_transform_rules"))
    except Exception:
        logger.exception("Falha ao carregar configurações do motor de crédito")
        raise

    resultados = []
    erros_qualidade = []
    alertas_db = []
    
    for _, row in df_fato.iterrows():
        registro = row.to_dict()
        registro["TIPO_FICHA"] = registro.get("TIPO_FICHA", "COMERCIALIZADORA")
        cnpj = registro.get("CNPJ")

        try:
            segmento = definir_segmento_metodologico(registro)
            registro["SEGMENTO_PD"] = segmento
            
            if segmento == "NAO_ENQUADRADO":
                erros_qualidade.append({
                    "CNPJ": cnpj,
                    "RUN_ID": run_id,
                    "REGRA_QUALIDADE": "Enquadramento Metodológico",
                    "VALOR_OBSERVADO": "NAO_ENQUADRADO",
                    "MENSAGEM_ERRO": "Segmento NAO_ENQUADRADO, regras de crédito suspensas."
                })
                registro["RATING_FINAL"] = pd.NA
                registro["PD_FINAL"] = pd.NA
                registro["SCORE_TOTAL"] = pd.NA
                resultados.append(registro)
                continue
                
            pd_info = calcular_pd_ajustada(
                registro=registro,
                pd_faixas=pd_faixas,
                pd_transform_rules=pd_transform_rules,
                pd_cpura_config=pd_cpura_config,
                score_cpura_config=score_cpura_config,
                logger=logger
            )
            registro.update(pd_info)
            
        except (PdInputValidationError, ValueError) as e:
            logger.warning("[CNPJ: %s] Falha no cálculo (Insumo Inválido): %s", cnpj, e)
            valor_obs = str(registro.get("RATING_COPEL") or registro.get("NOTA_CREDITO") or registro.get("RATING") or registro.get("RATING_FINAL") or "None")
            alertas_db.append({
                "codigo": "PD_ERR_001",
                "severidade": "ALTO",
                "regra": "Validação de Domínio Motor PD",
                "mensagem": str(e),
                "campo_afetado": "RATING/PD",
                "valor_observado": valor_obs,
                "limite_esperado": "VÁLIDO",
                "contraparte_id": cnpj
            })
            registro["RATING_FINAL"] = pd.NA
            registro["PD_FINAL"] = pd.NA
            registro["SCORE_TOTAL"] = pd.NA
            
        except Exception as e:
            logger.exception("Falha sistêmica no cálculo de crédito para CNPJ %s: %s", cnpj, e)
            alertas_db.append({
                "codigo": "PD_SYS_001",
                "severidade": "CRITICO",
                "regra": "Execução Motor PD",
                "mensagem": f"Erro sistêmico: {str(e)}",
                "campo_afetado": "MOTOR_PD",
                "valor_observado": "ERRO",
                "limite_esperado": "SUCESSO",
                "contraparte_id": cnpj
            })
            registro["RATING_FINAL"] = pd.NA
            registro["PD_FINAL"] = pd.NA
            registro["SCORE_TOTAL"] = pd.NA

        resultados.append(registro)

    if alertas_db:
        from relational.facts.fato_alerta_util import registrar_alertas_em_lote
        registrar_alertas_em_lote(alertas_db, run_id, context)

    df_processado = pd.DataFrame(resultados)

    if "DATA_CALCULO" in df_processado.columns and "DATA_ANALISE" not in df_processado.columns:
        df_processado["DATA_ANALISE"] = df_processado["DATA_CALCULO"]
    if "RATING_FINAL" not in df_processado.columns and "RATING_COPEL" in df_processado.columns:
        df_processado["RATING_FINAL"] = df_processado["RATING_COPEL"]
    if "MODELO_METODOLOGICO" not in df_processado.columns and "versao_ficha" in df_processado.columns:
        df_processado["MODELO_METODOLOGICO"] = df_processado["versao_ficha"]

    for col in ["ANALISE_ID", "DATA_ANALISE", "RATING_FINAL", "PD_FINAL", "SCORE_TOTAL", "CLASSE_RISCO", "MODELO_METODOLOGICO", "DATA_DEMONSTRACAO_FINANCEIRA", "SEGMENTO_PD", "TIPO_FICHA", "PATRIMONIO_LIQUIDO", "SITUACAO_DF", "SITUACAO_ANALISE", "CNPJ_RAIZ", "STATUS_CALCULO_PD"]:
        if col not in df_processado.columns:
            df_processado[col] = None

    rename_map = {
        "CNPJ": "CNPJ", "CNPJ_RAIZ": "CNPJ_RAIZ", "DATA_ANALISE": "DATA_ANALISE", "RATING_FINAL": "RATING",
        "PD_FINAL": "PD_PERCENTUAL", "SCORE_TOTAL": "SCORE", "CLASSE_RISCO": "CLASSE",
        "MODELO_METODOLOGICO": "MODELO", "DATA_DEMONSTRACAO_FINANCEIRA": "DATA_BALANCO_USADO",
        "SEGMENTO_PD": "SEGMENTO_METODOLOGICO_FICHA", "TIPO_FICHA": "TIPO_FICHA",
        "PATRIMONIO_LIQUIDO": "PATRIMONIO_LIQUIDO", "SITUACAO_DF": "SITUACAO_DF",
        "SITUACAO_ANALISE": "SITUACAO_ANALISE", "STATUS_CALCULO_PD": "STATUS_CALCULO_PD"
    }

    df_final = df_processado[[c for c in rename_map.keys() if c in df_processado.columns]].rename(columns=rename_map).copy()
    df_final["ETL_RUN_ID"] = run_id

    relational_dir = context.path("relational_facts") / "credito"
    relational_dir.mkdir(parents=True, exist_ok=True)
    escrever_conjunto_de_dados_silver(records=df_final.to_dict(orient="records"), output_dir=relational_dir, filename="fato_analise_credito")
    df_final.to_parquet(relational_dir / "fato_analise_credito.parquet", index=False)
    
    if erros_qualidade:
        df_erros = pd.DataFrame(erros_qualidade)
        erros_dir = context.path("silver") / "ctl_validacao_qualidade_credito"
        erros_dir.mkdir(parents=True, exist_ok=True)
        escrever_conjunto_de_dados_silver(records=df_erros.to_dict(orient="records"), output_dir=erros_dir, filename=f"pendencias_{run_id}")
        logger.info("Foram registradas %d pendências em ctl_validacao_qualidade_credito", len(erros_qualidade))

    return {"run_id": run_id, "linhas": len(df_final), "status": "SUCESSO"}
```


---

## `src/relational/facts/fato_exposicao_risco.py`

- Linhas: 122
- SHA-256: `a930e59730131b3f69f470f2c38782d365b6c922a104f396d5ec79b295ad863c`
- Classes: -
- Funções: construir_fato_exposicao_risco

```python
"""Serviço de construção da tabela Fato Exposição de Risco."""
from __future__ import annotations
import logging
import math
from datetime import datetime
from typing import Any
import pandas as pd
from pathlib import Path

from app.context import AppContext
from control.logger import obter_logger
from storage.escrever_dados import escrever_conjunto_de_dados_silver

from domain.credito.motor_ead import calcular_ead
from domain.credito.motor_lgd import calcular_lgd
from domain.credito.motor_pe import calcular_perda_esperada
from domain.credito.motor_taxa_risco import calcular_taxa_risco

def construir_fato_exposicao_risco(
    context: AppContext,
    df_exposicoes: pd.DataFrame,
    fator_conversao_ead: float = 1.0,
    config_lgd: dict[str, Any] | None = None
) -> dict[str, Any]:
    run_id = f"RSK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.fato_risco", Path("LOGS/relacional") / f"{run_id}__fato_risco.log")
    logger.info("Iniciando Fato Exposição de Risco (run_id=%s)", run_id)
    
    garantias_path = context.path("silver") / "garantias_silver" / "fato_garantia.parquet"
    df_garantias = pd.read_parquet(garantias_path) if garantias_path.exists() else pd.DataFrame()

    resultados_fatos = []
    pe_total_carteira = 0.0
    notional_total_carteira = 0.0
    alertas = []

    df_exposicoes["MTM_POSITIVO_TOTAL"] = pd.to_numeric(df_exposicoes.get("MTM_POSITIVO_TOTAL", 0), errors="coerce").fillna(0.0)
    df_exposicoes["NOTIONAL_TOTAL"]     = pd.to_numeric(df_exposicoes.get("NOTIONAL_TOTAL", 0), errors="coerce").fillna(0.0)
    df_exposicoes["PD_FINAL"] = pd.to_numeric(df_exposicoes.get("PD_FINAL"), errors="coerce")

    if "CNPJ_RAIZ" not in df_exposicoes.columns:
        from common.identificadores import normalizar_cnpj
        df_exposicoes["CNPJ_RAIZ"] = df_exposicoes["CNPJ"].apply(lambda x: normalizar_cnpj(x).raiz if normalizar_cnpj(x).valido else None)

    for idx, row in df_exposicoes.iterrows():
        cnpj      = row.get("CNPJ")
        cnpj_raiz = str(row.get("CNPJ_RAIZ", str(cnpj)[:8]))
        mtm_positivo = row.get("MTM_POSITIVO_TOTAL")
        notional     = row.get("NOTIONAL_TOTAL")
        segmento     = row.get("SEGMENTO_METODOLOGICO", "CGRUPO")
        pd_final     = row.get("PD_FINAL")

        cobertura_aplicada = 0.0
        if not df_garantias.empty and "CNPJ_CONTRAPARTE" in df_garantias.columns:
            filtro = (
                df_garantias["CNPJ_CONTRAPARTE"].astype(str).str[:8] == cnpj_raiz
            ) & (
                df_garantias["STATUS"].astype(str).str.strip().str.upper() == "VIGENTE"
                if "STATUS" in df_garantias.columns
                else True
            )
            if filtro.any():
                cobertura_calculada = df_garantias.loc[filtro, "PERCENTUAL_COBERTURA"].sum()
                cobertura_aplicada  = min(float(cobertura_calculada), 1.0)

        res_ead = calcular_ead(mtm_positivo_total=mtm_positivo, fator_conversao=fator_conversao_ead)
        res_lgd = calcular_lgd(segmento=segmento, cobertura_garantias=cobertura_aplicada, config=config_lgd)
        res_pe = calcular_perda_esperada(
            ead=res_ead.get("ead_valor"), 
            lgd_liquida=res_lgd.get("lgd_liquida"), 
            pd_final=pd_final, 
            notional=notional
        )

        pe_val = res_pe.get("pe_reais", 0.0)
        if pe_val is not None and not (isinstance(pe_val, float) and math.isnan(pe_val)):
            pe_total_carteira += float(pe_val)
        if notional is not None and not (isinstance(notional, float) and math.isnan(notional)):
            notional_total_carteira += float(notional)

        fato = {
            "RUN_ID": run_id, "CNPJ": cnpj, "SEGMENTO": segmento,
            "DT_CALCULO": res_pe.get("dt_calculo"),
            "CALCULO_ID_EAD": res_ead.get("calculo_id"), "EAD_VALOR": res_ead.get("ead_valor", 0.0),
            "FATOR_CONVERSAO_EAD": res_ead.get("fator_conversao"), "CONFIG_SNAPSHOT_EAD": res_ead.get("config_snapshot_id"),
            "CALCULO_ID_LGD": res_lgd.get("calculo_id"), "LGD_BRUTA": res_lgd.get("lgd_bruta"),
            "LGD_LIQUIDA": res_lgd.get("lgd_liquida", 0.0), "COBERTURA_GARANTIAS": res_lgd.get("cobertura_garantias"),
            "CONFIG_SNAPSHOT_LGD": res_lgd.get("config_snapshot_id"),
            "PD_UTILIZADA": pd_final,
            "CALCULO_ID_PE": res_pe.get("calculo_id"), "PE_REAIS": res_pe.get("pe_reais", 0.0),
            "PE_PERCENTUAL": res_pe.get("pe_percentual", 0.0),
        }
        resultados_fatos.append(fato)

    res_taxa = calcular_taxa_risco(pe_total=pe_total_carteira, notional_total=notional_total_carteira, run_id=run_id, context=context)
    taxa_val = res_taxa.get("taxa_risco")
    taxa_print = f"{taxa_val*100:.4f}%" if taxa_val is not None else "0.00% (Notional Zerado na Origem)"
    
    if res_taxa.get("alertas"): alertas.extend(res_taxa["alertas"])

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        df_alertas["RUN_ID"] = run_id
        df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
        df_alertas["STATUS_ALERTA"] = "ABERTO"
        escrever_conjunto_de_dados_silver(records=df_alertas.to_dict(orient="records"), output_dir=context.path("silver") / "alertas_credito", filename=f"alertas_risco_{run_id}")

    if resultados_fatos:
        df_fatos = pd.DataFrame(resultados_fatos)
        relational_dir = context.path("relational_facts") / "risco"
        relational_dir.mkdir(parents=True, exist_ok=True)
        
        escrever_conjunto_de_dados_silver(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename=f"fato_exposicao_risco_{run_id}")
        escrever_conjunto_de_dados_silver(records=df_fatos.to_dict(orient="records"), output_dir=relational_dir, filename="fato_exposicao_risco_LATEST")
        
    logger.info("Fato Exposição de Risco concluída. Taxa Carteira: %s", taxa_print)

    return {
        "run_id": run_id, "linhas_processadas": len(resultados_fatos),
        "taxa_risco_carteira": taxa_val, "pe_total_carteira": pe_total_carteira,
        "notional_total_carteira": notional_total_carteira, "calculo_id_taxa": res_taxa.get("calculo_id")
    }
```


---

## `src/relational/facts/fato_garantia.py`

- Linhas: 151
- SHA-256: `848f5a631f5d935a5bcb33a4687500ef270ffc4f0be26666069873cf71f1e8ce`
- Classes: -
- Funções: gerar_fato_garantia

```python
"""Serviço de construção da tabela Fato Garantia (Star Schema)."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
import pandas as pd
from pathlib import Path

from app.context import AppContext
from control.logger import obter_logger
from domain.enums import StatusGarantia
from relational.facts.fato_alerta_util import registrar_alertas_em_lote
from storage.escrever_dados import escrever_conjunto_de_dados_silver

COBERTURA_MINIMA = 0.5

def gerar_fato_garantia(context: AppContext) -> dict[str, Any]:
    run_id = f"F_GAR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.fato_garantia", Path("LOGS/relacional") / f"{run_id}__fato_garantia.log")
    logger.info("Iniciando construção da Fato Garantia (run_id=%s)", run_id)
    
    silver_path = context.path("silver") / "garantias_silver" / "garantia_silver.parquet"
    if not silver_path.exists():
        logger.warning("Base Silver de garantias não encontrada em %s. Abortando.", silver_path)
        return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_BASE"}

    df_garantias = pd.read_parquet(silver_path)
    
    if df_garantias.empty:
        return {"run_id": run_id, "linhas_processadas": 0, "status": "SEM_DADOS"}

    hoje = pd.Timestamp(datetime.now().date())
    alertas = []
    alertas_fato = []
    status_list = []

    for _, row in df_garantias.iterrows():
        garantia_id = row.get("GARANTIA_ID")
        cnpj = row.get("CNPJ_CONTRAPARTE")
        data_fim = pd.to_datetime(row.get("VENCIMENTO"), errors="coerce")
        cobertura = float(row.get("PERCENTUAL_COBERTURA", 1.0))

        dias_para_vencimento = (data_fim - hoje).days if pd.notnull(data_fim) else -1

        if dias_para_vencimento < 0:
            status_garantia = StatusGarantia.VENCIDA.value
            data_fmt = data_fim.strftime('%Y-%m-%d') if pd.notnull(data_fim) else "N/A"
            msg = f"Garantia {garantia_id} está vencida desde {data_fmt}."
            alertas.append({
                "CODIGO": "GAR_001",
                "CNPJ": cnpj,
                "SEVERIDADE": "ALTO",
                "MENSAGEM": msg
            })
            alertas_fato.append({
                "codigo": "GAR_001",
                "severidade": "ALTO",
                "regra": "Garantia Vencida",
                "mensagem": msg,
                "campo_afetado": "VENCIMENTO",
                "valor_observado": data_fmt,
                "limite_esperado": "VIGENTE",
                "contraparte_id": cnpj
            })
        elif 0 <= dias_para_vencimento <= 30:
            status_garantia = StatusGarantia.PROXIMA_VENCIMENTO.value
            msg = f"Garantia {garantia_id} próxima do vencimento ({dias_para_vencimento} dias)."
            alertas.append({
                "CODIGO": "GAR_001",
                "CNPJ": cnpj,
                "SEVERIDADE": "MEDIO",
                "MENSAGEM": msg
            })
            alertas_fato.append({
                "codigo": "GAR_001",
                "severidade": "MEDIO",
                "regra": "Garantia Próxima ao Vencimento",
                "mensagem": msg,
                "campo_afetado": "VENCIMENTO",
                "valor_observado": dias_para_vencimento,
                "limite_esperado": "> 30 dias",
                "contraparte_id": cnpj
            })
        else:
            status_garantia = StatusGarantia.VIGENTE.value

        if cobertura < COBERTURA_MINIMA:
            msg = f"Garantia {garantia_id} com cobertura insuficiente ({cobertura*100:.1f}%)."
            alertas.append({
                "CODIGO": "GAR_002",
                "CNPJ": cnpj,
                "SEVERIDADE": "MEDIO",
                "MENSAGEM": msg
            })
            alertas_fato.append({
                "codigo": "GAR_002",
                "severidade": "MEDIO",
                "regra": "Cobertura Insuficiente",
                "mensagem": msg,
                "campo_afetado": "PERCENTUAL_COBERTURA",
                "valor_observado": cobertura,
                "limite_esperado": COBERTURA_MINIMA,
                "contraparte_id": cnpj
            })

        status_list.append(status_garantia)

    df_garantias["STATUS"] = status_list
    df_garantias["VENCIMENTO"] = pd.to_datetime(df_garantias["VENCIMENTO"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_garantias["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")
    df_garantias["RUN_ID"] = run_id

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        df_alertas["RUN_ID"] = run_id
        df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
        df_alertas["STATUS_ALERTA"] = "ABERTO"

        escrever_conjunto_de_dados_silver(
            records=df_alertas.to_dict(orient="records"),
            output_dir=context.path("silver") / "alertas_credito",
            filename=f"alertas_garantias_{run_id}"
        )
        logger.info("Gerados %s alertas de garantias na Silver.", len(alertas))
        
        if alertas_fato:
            registrar_alertas_em_lote(alertas_fato, run_id, context)
            logger.info("Registrados %s alertas de garantias no Fato Alertas.", len(alertas_fato))

    relational_dir = context.path("relational_facts") / "garantias"
    relational_dir.mkdir(parents=True, exist_ok=True)
    
    escrever_conjunto_de_dados_silver(
        records=df_garantias.to_dict(orient="records"),
        output_dir=relational_dir,
        filename=f"fato_garantia_{run_id}"
    )
    escrever_conjunto_de_dados_silver(
        records=df_garantias.to_dict(orient="records"),
        output_dir=relational_dir,
        filename="fato_garantia"
    )

    logger.info("Construção da Fato Garantia concluída. Registros salvos: %s", len(df_garantias))

    return {
        "run_id": run_id,
        "linhas_processadas": len(df_garantias),
        "alertas_gerados": len(alertas),
        "status": "SUCESSO"
    }
```


---

## `src/relational/facts/fato_reconciliacao_contrato_mtm.py`

- Linhas: 174
- SHA-256: `3cf48f5936a9e1de78c2e57a5746ee32fb86f13ac5c040125b884819a56cf92b`
- Classes: ReconciliacaoDataError
- Funções: executar_reconciliacao_denodo_mtm

```python
"""Serviço de reconciliação entre contratos do Denodo e posições consolidadas de MtM."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from app.context import AppContext
from control.logger import obter_logger
from domain.enums import StatusAlerta
from relational.facts.fato_alerta_util import registrar_alerta
from storage.escrever_dados import escrever_conjunto_de_dados_silver


class ReconciliacaoDataError(Exception):
    """Exceção levantada quando os dados fonte para a reconciliação estão inacessíveis ou vazios."""

def executar_reconciliacao_denodo_mtm(context: AppContext) -> dict[str, Any]:
    """
    Cruza o consolidado de contratos do Denodo com posições do MtM na camada Silver por CNPJ.
    Classifica as contrapartes e dispara os alertas CTR_001 e CTR_002.
    """
    run_id = f"REC_MTM_DENODO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log_file = Path("LOGS/auditoria") / f"{run_id}__reconciliacao.log"
    logger = obter_logger("bdc.reconciliacao", log_file)

    try:
        logger.info("Iniciando reconciliação entre Denodo e MtM por Contraparte.")

        silver_mtm_path = context.path("silver") / "mtm_consolidado_silver" / "mtm_agregado_contraparte.parquet"
        silver_denodo_path = context.path("silver") / "denodo_contratos_silver" / "contratos_correntes.parquet"

        if not silver_mtm_path.exists() or not silver_denodo_path.exists():
            raise ReconciliacaoDataError("As bases Silver do Denodo ou MtM não foram encontradas para a reconciliação.")

        df_mtm = pd.read_parquet(silver_mtm_path)
        df_denodo_full = pd.read_parquet(silver_denodo_path)

        if df_mtm.empty or df_denodo_full.empty:
            logger.warning("Uma das bases Silver está vazia. Cancelando reconciliação.")
            return {"run_id": run_id, "linhas_conciliadas": 0, "status": "SEM_DADOS"}

        df_denodo_full["CNPJ"] = df_denodo_full["CNPJ"].astype(str).str.replace(r"\D", "", regex=True)
        df_denodo_full["CNPJ"] = df_denodo_full["CNPJ"].apply(lambda x: x if len(x) == 14 else None)

        df_mtm["CNPJ"] = df_mtm["CNPJ"].astype(str).str.replace(r"\D", "", regex=True)
        df_mtm["CNPJ"] = df_mtm["CNPJ"].apply(lambda x: x if len(x) == 14 else None)

        df_denodo = df_denodo_full[["CNPJ"]].drop_duplicates()
        df_denodo["TEM_CONTRATO"] = True

        df_merged = pd.merge(
            df_denodo, 
            df_mtm, 
            on="CNPJ", 
            how="outer", 
            indicator=True
        )

        conditions = [
            df_merged["_merge"] == "both",
            df_merged["_merge"] == "left_only",
            df_merged["_merge"] == "right_only"
        ]
        choices = ["CONCILIADO", "CONTRATO_SEM_MTM", "MTM_SEM_CONTRATO"]
        
        df_merged["STATUS_CONCILIACAO"] = np.select(conditions, choices, default="DIVERGENTE")

        alertas = []
        alertas_db = []
        
        mask_ctr_001 = df_merged["STATUS_CONCILIACAO"] == "CONTRATO_SEM_MTM"
        for row in df_merged[mask_ctr_001].to_dict(orient="records"):
            msg = f"A contraparte (CNPJ {row['CNPJ']}) possui contrato(s) no Denodo, mas não tem posição na base de MtM."
            alertas.append({
                "CODIGO": "CTR_001",
                "CNPJ": row["CNPJ"],
                "SEVERIDADE": "MEDIO",
                "MENSAGEM": msg
            })
            alertas_db.append({
                "codigo": "CTR_001",
                "severidade": "MEDIO",
                "regra": "Contrato sem MtM",
                "mensagem": msg,
                "campo_afetado": "STATUS_CONCILIACAO",
                "valor_observado": "CONTRATO_SEM_MTM",
                "limite_esperado": "CONCILIADO",
                "contraparte_id": row["CNPJ"]
            })

        mask_ctr_002 = df_merged["STATUS_CONCILIACAO"] == "MTM_SEM_CONTRATO"
        for row in df_merged[mask_ctr_002].to_dict(orient="records"):
            msg = f"Posição de MtM identificada para a contraparte {row['CNPJ']}, mas nenhum contrato corrente consta no Denodo."
            alertas.append({
                "CODIGO": "CTR_002",
                "CNPJ": row["CNPJ"],
                "SEVERIDADE": "ALTO",
                "MENSAGEM": msg
            })
            alertas_db.append({
                "codigo": "CTR_002",
                "severidade": "ALTO",
                "regra": "MtM sem Contrato",
                "mensagem": msg,
                "campo_afetado": "STATUS_CONCILIACAO",
                "valor_observado": "MTM_SEM_CONTRATO",
                "limite_esperado": "CONCILIADO",
                "contraparte_id": row["CNPJ"]
            })

        if alertas_db:
            from relational.facts.fato_alerta_util import registrar_alertas_em_lote
            registrar_alertas_em_lote(alertas_db, run_id, context)

        if alertas:
            df_alertas = pd.DataFrame(alertas)
            df_alertas["RUN_ID"] = run_id
            df_alertas["DATA_DETECCAO"] = datetime.now().isoformat(timespec="seconds")
            df_alertas["STATUS_ALERTA"] = StatusAlerta.ABERTO.value
            
            alertas_output_dir = context.path("silver") / "alertas_credito"
            escrever_conjunto_de_dados_silver(
                records=df_alertas.to_dict(orient="records"),
                output_dir=alertas_output_dir,
                filename=f"alertas_reconciliacao_{run_id}"
            )
            logger.info("Gerados %s alertas de negócio na reconciliação.", len(alertas))

        colunas_saida = [
            "CNPJ", "STATUS_CONCILIACAO", 
            "MTM_POSITIVO_TOTAL", "MTM_NEGATIVO_TOTAL", "NOTIONAL_TOTAL"
        ]
        
        colunas_disponiveis = [col for col in colunas_saida if col in df_merged.columns]
        df_reconciliacao = df_merged[colunas_disponiveis].copy()
        
        df_reconciliacao["RUN_ID"] = run_id
        df_reconciliacao["DT_PROCESSAMENTO"] = datetime.now().isoformat(timespec="seconds")

        reconciliacao_output_dir = context.path("silver") / "reconciliacao_contratos_mtm"
        csv_path, parquet_path = escrever_conjunto_de_dados_silver(
            records=df_reconciliacao.to_dict(orient="records"),
            output_dir=reconciliacao_output_dir,
            filename="fato_reconciliacao_contrato_mtm"
        )
        
        relational_output_dir = context.path("relational_facts") / "reconciliacao"
        escrever_conjunto_de_dados_silver(
            records=df_reconciliacao.to_dict(orient="records"),
            output_dir=relational_output_dir,
            filename="fato_reconciliacao_contrato_mtm"
        )

        logger.info(
            "Reconciliação Denodo x MtM finalizada. %s contrapartes cruzadas. Relatórios: \n - %s\n - %s",
            len(df_reconciliacao), csv_path.name, parquet_path.name
        )

        return {
            "run_id": run_id,
            "linhas_conciliadas": len(df_reconciliacao),
            "alertas_gerados_ctr001": mask_ctr_001.sum(),
            "alertas_gerados_ctr002": mask_ctr_002.sum(),
            "status": "SUCESSO"
        }

    except Exception as exc:
        logger.exception("Falha crítica no serviço de reconciliação Denodo x MtM.")
        raise ReconciliacaoDataError(f"Erro ao processar reconciliação: {exc}") from exc
```


---

## `src/relational/facts/fato_reconciliacao_fichas_salesforce.py`

- Linhas: 127
- SHA-256: `009ac40145dde5e412a4a5538392d8829f043ed2271eb631cb995727e13e78c6`
- Classes: -
- Funções: executar_reconciliacao_fichas_salesforce

```python
"""
Serviço de Reconciliação: Fichas de Crédito vs Salesforce.
Verifica se todas as contrapartes com ficha de crédito estão devidamente cadastradas no CRM.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Any

import pandas as pd

from app.context import AppContext
from common.identificadores import normalizar_cnpj
from control.logger import obter_logger
from relational.facts.fato_alerta_util import registrar_alerta
from storage.escrever_dados import escrever_conjunto_de_dados_silver

def executar_reconciliacao_fichas_salesforce(context: AppContext) -> dict[str, Any]:
    run_id = f"REC_SF_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = obter_logger("bdc.reconciliacao.salesforce", Path("LOGS/auditoria") / f"{run_id}__salesforce_reconciliacao.log")
    
    silver_dir = context.path("silver")

    df_fichas = pd.DataFrame()
    for segmento in ["fichas_comercializadoras_extraidas", "fichas_consumidores_extraidas"]:
        path_seg = silver_dir / segmento
        if path_seg.exists():
            parquets = list(path_seg.glob("*.parquet"))
            if parquets:
                df_seg = pd.read_parquet(max(parquets, key=lambda f: f.stat().st_mtime))
                df_fichas = pd.concat([df_fichas, df_seg], ignore_index=True)

    df_sf = pd.DataFrame()
    
    arquivos_sf = list(silver_dir.rglob("account*.parquet"))
    if not arquivos_sf:
        arquivos_sf = list(silver_dir.rglob("*salesforce*account*.parquet"))
        
    if arquivos_sf:
        arquivo_sf_mais_recente = max(arquivos_sf, key=lambda f: f.stat().st_mtime)
        df_sf = pd.read_parquet(arquivo_sf_mais_recente)

    if df_fichas.empty:
        logger.warning("Base de Fichas está vazia. Abortando reconciliação.")
        return {"run_id": run_id, "status": "SEM_DADOS_FICHAS"}
        
    if df_sf.empty:
        logger.warning("Base do Salesforce (Account) não foi encontrada na Silver. Abortando.")
        return {"run_id": run_id, "status": "SEM_DADOS_SF"}

    from common.identificadores import normalizar_cnpj
    df_fichas["CNPJ_FICHAS"] = df_fichas["CNPJ"].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    df_fichas_unique = df_fichas.drop_duplicates(subset=["CNPJ_FICHAS"]).copy()

    col_cnpj_sf = "CNPJ" if "CNPJ" in df_sf.columns else next((c for c in df_sf.columns if "CNPJ" in str(c).upper() or "DOCUMENTO" in str(c).upper()), None)
    
    if not col_cnpj_sf:
        logger.warning("Coluna de CNPJ não encontrada na base do Salesforce.")
        return {"run_id": run_id, "status": "FALHA_MAPEAMENTO_SF"}

    df_sf["CNPJ_SF"] = df_sf[col_cnpj_sf].apply(lambda x: normalizar_cnpj(x).cnpj if normalizar_cnpj(x).valido else None)
    df_sf_unique = df_sf.drop_duplicates(subset=["CNPJ_SF"]).copy()

    df_merge = pd.merge(df_fichas_unique, df_sf_unique, left_on="CNPJ_FICHAS", right_on="CNPJ_SF", how="left", indicator=True)
    
    alertas = []
    df_missing_in_sf = df_merge[df_merge["_merge"] == "left_only"]
    
    for _, row in df_missing_in_sf.iterrows():
        cnpj = row["CNPJ_FICHAS"]
        if cnpj == "00000000000000": continue
        
        msg = "Contraparte possui Ficha de Crédito, mas NÃO foi encontrada na base de Contas do CRM (Salesforce)."
        alertas.append({
            "CODIGO": "SF_001",
            "CNPJ": cnpj,
            "MENSAGEM": msg,
            "SEVERIDADE": "MÉDIA",
            "RUN_ID": run_id,
            "DT_DETECCAO": datetime.now().isoformat(timespec="seconds"),
            "STATUS_ALERTA": "ABERTO"
        })
        registrar_alerta(
            codigo="SF_001",
            severidade="MEDIO",
            regra="Ficha sem Conta CRM",
            mensagem=msg,
            campo_afetado="STATUS_RECONCILIACAO",
            valor_observado="PENDENTE_NO_SALESFORCE",
            limite_esperado="SINCRONIZADO",
            contraparte_id=cnpj,
            run_id=run_id,
            context=context
        )

    relational_dir = context.path("relational_facts") / "reconciliacao"
    relational_dir.mkdir(parents=True, exist_ok=True)
    
    df_resultado = df_merge[["CNPJ_FICHAS", "CNPJ_SF", "_merge"]].copy()
    df_resultado.columns = ["CNPJ", "CNPJ_SALESFORCE", "STATUS_RECONCILIACAO"]
    df_resultado["STATUS_RECONCILIACAO"] = df_resultado["STATUS_RECONCILIACAO"].map({
        "both": "SINCRONIZADO", 
        "left_only": "PENDENTE_NO_SALESFORCE", 
        "right_only": "SOMENTE_SALESFORCE"
    })

    df_resultado.to_csv(relational_dir / "fato_reconciliacao_fichas_salesforce.csv", index=False, sep=";", decimal=",")
    df_resultado.to_parquet(relational_dir / "fato_reconciliacao_fichas_salesforce.parquet", index=False)

    if alertas:
        df_alertas = pd.DataFrame(alertas)
        escrever_conjunto_de_dados_silver(
            records=df_alertas.to_dict(orient="records"), 
            output_dir=silver_dir / "alertas_credito", 
            filename=f"alertas_reconciliacao_sf_{run_id}"
        )

    logger.info("Reconciliação CRM concluída. %d Fichas sem cadastro correspondente no Salesforce.", len(alertas))
    
    return {
        "run_id": run_id, 
        "status": "SUCESSO", 
        "fichas_cruzadas": len(df_fichas_unique),
        "alertas_gerados": len(alertas)
    }
```


---

## `src/ui/app.py`

- Linhas: 45
- SHA-256: `1b927dd2eb4066e85524c45e73c40b2a6a71c555fae482a68ea8255c9ad5d906`
- Classes: -
- Funções: main

```python
import streamlit as st
from pathlib import Path
import sys

# Garante o src no PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ui.views.visao_orquestrador import render_visao_orquestrador
from ui.views.visao_carga_manual import render_visao_carga_manual
from ui.views.visao_carteira import render_visao_carteira
from ui.views.visao_silver import render_visao_silver

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    with st.sidebar:
        st.title("BDC")
        st.markdown("---")

        menu = st.radio(
            "Navegação:",
            [
                "Orquestrador",
                "Visão da Carteira",
                "Carga Manual",
                "Visão Silver",
            ],
            index=1
        )
        st.markdown("---")

    if menu == "Orquestrador":
        render_visao_orquestrador()
    elif menu == "Visão da Carteira":
        render_visao_carteira()
    elif menu == "Carga Manual":
        render_visao_carga_manual()
    elif menu == "Visão Silver":
        render_visao_silver()

if __name__ == "__main__":
    main()
```


---

## `src/ui/views/visao_carga_manual.py`

- Linhas: 308
- SHA-256: `676ed06dc31a745fb12a655c6073f894425a0ac3d61539ce09c24c07a2606adc`
- Classes: -
- Funções: formatar_cnpj_canonico, formatar_data_canonica, montar_chave_pendencia, carregar_dados, salvar_form_rascunho, limpar_rascunho, render_visao_carga_manual

```python
import streamlit as st
import pandas as pd
from pathlib import Path
import os
import sys
import json

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from domain.diagnostico.servico_diagnostico import gerar_diagnostico
from domain.diagnostico.servico_exportacao import exportar_carga_manual
from common.identificadores import normalizar_cnpj
from common.datas import normalizar_data

BASE_DIR = Path(".")
DIAGNOSTICO_DIR = BASE_DIR / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico"
FILA_PATH = DIAGNOSTICO_DIR / "fila_pendencias.csv"
RASCUNHO_PATH = DIAGNOSTICO_DIR / "rascunho_carga_manual.csv"
SCHEMA_PATH = BASE_DIR / "ENTRADAS" / "control" / "schemas" / "schema_carga_manual.json"

# Carrega opções do JSON Schema obrigatoriamente (Governança Estrita)
try:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    MOTIVOS_PERMITIDOS = schema.get("properties", {}).get("MOTIVO", {}).get("enum", [])
    SOLICITANTES_PERMITIDOS = schema.get("properties", {}).get("SOLICITANTE", {}).get("enum", [])
except Exception:
    MOTIVOS_PERMITIDOS = []
    SOLICITANTES_PERMITIDOS = []

def formatar_cnpj_canonico(val: str) -> str:
    res = normalizar_cnpj(val)
    return res.cnpj if res.cnpj else str(val or "").strip()

def formatar_data_canonica(val: str) -> str:
    res = normalizar_data(val)
    return res if res else str(val or "").strip()[:10]

def montar_chave_pendencia(row) -> str:
    c = formatar_cnpj_canonico(row.get("CNPJ", ""))
    d = formatar_data_canonica(row.get("DATA_DEMONSTRACAO_FINANCEIRA", ""))
    f = str(row.get("CAMPO_FALTANTE", "")).strip().upper()
    return f"{c}_{d}_{f}"

def carregar_dados():
    if FILA_PATH.exists():
        df_fila = pd.read_csv(FILA_PATH, sep=";", dtype=str).fillna("")
        df_fila.columns = df_fila.columns.str.strip()
        for col in df_fila.columns:
            df_fila[col] = df_fila[col].astype(str).str.strip()
    else:
        df_fila = pd.DataFrame(columns=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA", "CAMPO_FALTANTE", "STATUS", "VALOR_RECUPERADO"])

    if RASCUNHO_PATH.exists():
        df_rascunho = pd.read_csv(RASCUNHO_PATH, sep=";", dtype=str).fillna("")
        df_rascunho.columns = df_rascunho.columns.str.strip()
        for col in df_rascunho.columns:
            df_rascunho[col] = df_rascunho[col].astype(str).str.strip()
    else:
        df_rascunho = pd.DataFrame(columns=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA", "CAMPO_FALTANTE", "VALOR_NOVO", "FONTE", "MOTIVO", "SOLICITANTE", "TIPO_EVENTO"])
        
    return df_fila, df_rascunho

def salvar_form_rascunho(cnpj, data_df, empresa, campos):
    df_fila, df_rascunho = carregar_dados()
    novas_linhas = []
    
    for campo in campos:
        key_prefix = f"{cnpj}_{data_df}_{empresa}_{campo}"
        valor = st.session_state.get(f"{key_prefix}_valor", "")
        fonte = st.session_state.get(f"{key_prefix}_fonte", "FICHA")
        motivo = st.session_state.get(f"{key_prefix}_motivo", "")
        solicitante = st.session_state.get(f"{key_prefix}_solicitante", "")
        
        if str(valor).strip() != "":
            cnpj_canonico = formatar_cnpj_canonico(cnpj)
            data_canonica = formatar_data_canonica(data_df)
            novas_linhas.append({
                "CNPJ": cnpj_canonico,
                "DATA_DEMONSTRACAO_FINANCEIRA": str(data_df).strip(),
                "EMPRESA": str(empresa).strip(),
                "CAMPO_FALTANTE": str(campo).strip(),
                "VALOR_NOVO": str(valor).strip(),
                "FONTE": str(fonte).strip(),
                "MOTIVO": str(motivo).strip(),
                "SOLICITANTE": str(solicitante).strip(),
                "TIPO_EVENTO": "COMPLEMENTACAO"
            })
            
            # Remove se já existir para dar update
            if not df_rascunho.empty:
                df_rascunho = df_rascunho[~(
                    (df_rascunho["CNPJ"].apply(formatar_cnpj_canonico) == cnpj_canonico) & 
                    (df_rascunho["DATA_DEMONSTRACAO_FINANCEIRA"].apply(formatar_data_canonica) == data_canonica) & 
                    (df_rascunho["CAMPO_FALTANTE"].astype(str).str.strip().str.upper() == str(campo).strip().upper())
                )]
                                        
    if novas_linhas:
        df_rascunho = pd.concat([df_rascunho, pd.DataFrame(novas_linhas)], ignore_index=True)
        DIAGNOSTICO_DIR.mkdir(parents=True, exist_ok=True)
        df_rascunho.to_csv(RASCUNHO_PATH, index=False, sep=";")

def limpar_rascunho():
    if RASCUNHO_PATH.exists():
        RASCUNHO_PATH.unlink()

def render_visao_carga_manual():
    st.header("Carga Manual")
    
    if st.session_state.pop("sucesso_salvamento", False):
        st.success("Resoluções salvas com sucesso! Os campos foram transferidos para a aba 'Resoluções Salvas'.")
        
    df_fila, df_rascunho = carregar_dados()
    
    with st.sidebar:
        st.header("Operações de Diagnóstico")
        if st.button("Gerar Diagnóstico Atualizado", use_container_width=True):
            with st.spinner("Lendo Silver e gerando fila de pendências..."):
                gerar_diagnostico()
            st.success("Diagnóstico concluído!")
            st.rerun()
            
        if st.button("Exportar Carga Manual", use_container_width=True, type="primary"):
            with st.spinner("Exportando..."):
                sucesso = exportar_carga_manual()
                if sucesso:
                    st.success("Carga exportada com sucesso!")
                    st.rerun()
                else:
                    st.warning("Nada para exportar (Rascunho vazio).")
                    
        st.markdown("---")
        st.subheader("Configurações de Exibição")
        itens_por_pagina = st.selectbox("Fichas por página:", [5, 10, 20, 50], index=1)

    # Filtra as pendências que já estão resolvidas no rascunho
    if not df_rascunho.empty and not df_fila.empty:
        chaves_resolvidas = set(df_rascunho.apply(montar_chave_pendencia, axis=1))
        chaves_fila = df_fila.apply(montar_chave_pendencia, axis=1)
        df_fila_pendente = df_fila[~chaves_fila.isin(chaves_resolvidas)].copy()
    else:
        df_fila_pendente = df_fila.copy()

    # Métricas gerais no topo
    grupos_totais = list(df_fila_pendente.groupby(["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA"])) if not df_fila_pendente.empty else []
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Campos Pendentes", len(df_fila_pendente))
    col_m2.metric("Fichas a Resolver", len(grupos_totais))
    col_m3.metric("Campos Resolvidos", len(df_rascunho) if not df_rascunho.empty else 0)

    st.markdown("---")

    # Abas para separar Pendências de Resoluções Salvas
    tab_pendencias, tab_rascunho = st.tabs([
        f"Pendências ({len(df_fila_pendente)})", 
        f"Resoluções Salvas ({len(df_rascunho)})"
    ])

    # ---------------- ABA 1: PENDÊNCIAS ----------------
    with tab_pendencias:
        if df_fila_pendente.empty:
            if not df_rascunho.empty:
                st.success("🎉 Todas as pendências foram preenchidas e estão salvas no rascunho! Vá para a aba 'Resoluções Salvas' para conferir e exportar a carga.")
            else:
                st.info("Nenhuma pendência na fila. Clique em 'Gerar Diagnóstico Atualizado' para varrer a camada Silver.")
        else:
            # Corrige bug visual do Pandas que oculta registros com chaves nulas no groupby
            df_fila_pendente["CNPJ"] = df_fila_pendente["CNPJ"].replace("", "CNPJ_DESCONHECIDO")
            df_fila_pendente["DATA_DEMONSTRACAO_FINANCEIRA"] = df_fila_pendente["DATA_DEMONSTRACAO_FINANCEIRA"].replace("", "DATA_DESCONHECIDA")
            df_fila_pendente["EMPRESA"] = df_fila_pendente["EMPRESA"].replace("", "EMPRESA_DESCONHECIDA")

            # Barra de busca rápida
            busca = st.text_input("Filtrar por Empresa, CNPJ ou Campo:", placeholder="Digite o nome da empresa, CNPJ ou campo para filtrar...", key="busca_pendencias")
            
            if busca.strip():
                termo = busca.strip().lower()
                df_filtrado = df_fila_pendente[
                    df_fila_pendente["EMPRESA"].astype(str).str.lower().str.contains(termo) |
                    df_fila_pendente["CNPJ"].astype(str).str.lower().str.contains(termo) |
                    df_fila_pendente["CAMPO_FALTANTE"].astype(str).str.lower().str.contains(termo)
                ]
            else:
                df_filtrado = df_fila_pendente

            if df_filtrado.empty:
                st.warning(f"Nenhum registro encontrado para a busca '{busca}'.")
            else:
                grupos = list(df_filtrado.groupby(["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA"]))
                total_fichas = len(grupos)
                total_paginas = max(1, (total_fichas + itens_por_pagina - 1) // itens_por_pagina)
                
                if "pagina_carga" not in st.session_state:
                    st.session_state["pagina_carga"] = 1
                if st.session_state["pagina_carga"] > total_paginas:
                    st.session_state["pagina_carga"] = total_paginas
                    
                pagina_atual = st.session_state["pagina_carga"]
                inicio = (pagina_atual - 1) * itens_por_pagina
                fim = min(inicio + itens_por_pagina, total_fichas)
                
                st.caption(f"Exibindo fichas **{inicio + 1}** até **{fim}** de **{total_fichas}** fichas ({len(df_filtrado)} campos pendentes nesta visão).")
                
                grupos_pagina = grupos[inicio:fim]

                for (cnpj, data_df, empresa), grupo in grupos_pagina:
                    try:
                        data_df_exibicao = pd.to_datetime(data_df).strftime("%d/%m/%Y")
                    except Exception:
                        data_df_exibicao = str(data_df).split(" ")[0]
                        
                    with st.expander(f"🏢 {empresa} | CNPJ: {cnpj} | DF: {data_df_exibicao} ({len(grupo)} campos pendentes)", expanded=True):
                        arquivo_origem = grupo.iloc[0].get("ARQUIVO_ORIGEM", "Desconhecido")
                        st.info(f"Ficha mapeada: {arquivo_origem}")
                        st.markdown("---")
                        
                        with st.form(key=f"form_{cnpj}_{data_df}_{empresa}"):
                            campos_do_grupo = []
                            for _, row in grupo.iterrows():
                                campo = row["CAMPO_FALTANTE"]
                                status = row["STATUS"]
                                campos_do_grupo.append(campo)
                                
                                col1, col2, col3, col4, col5 = st.columns([1.2, 1.2, 1.2, 1.5, 1.5])
                                
                                key_prefix = f"{cnpj}_{data_df}_{empresa}_{campo}"
                                
                                with col1:
                                    st.text_input(
                                        "Campo Faltante", 
                                        value=campo, 
                                        disabled=True, 
                                        key=f"{key_prefix}_nome"
                                    )
                                
                                with col2:
                                    st.text_input(
                                        "Novo Valor", 
                                        key=f"{key_prefix}_valor"
                                    )
                                with col3:
                                    st.selectbox(
                                        "Fonte", 
                                        ["FICHA", "DEMONSTRACAO_FINANCEIRA", "CONSULTA_PUBLICA"], 
                                        key=f"{key_prefix}_fonte"
                                    )
                                with col4:
                                    st.selectbox(
                                        "Motivo", 
                                        MOTIVOS_PERMITIDOS,
                                        key=f"{key_prefix}_motivo"
                                    )
                                with col5:
                                    st.selectbox(
                                        "Solicitante", 
                                        SOLICITANTES_PERMITIDOS,
                                        key=f"{key_prefix}_solicitante"
                                    )
                                    
                            submit = st.form_submit_button("Salvar Resoluções")
                            if submit:
                                salvar_form_rascunho(cnpj, data_df, empresa, campos_do_grupo)
                                st.session_state["sucesso_salvamento"] = True
                                st.rerun()
                                
                # Renderização dos botões de paginação no final
                st.markdown("<br>", unsafe_allow_html=True)
                col_p1, col_p2, col_p3 = st.columns([1, 3, 1])
                with col_p1:
                    if st.button("Anterior", disabled=st.session_state["pagina_carga"] <= 1, use_container_width=True, key="btn_prev_pend"):
                        st.session_state["pagina_carga"] -= 1
                        st.rerun()
                with col_p2:
                    st.markdown(f"<div style='text-align: center; margin-top: 5px; font-size: 16px;'>Página <b>{st.session_state['pagina_carga']}</b> de {total_paginas}</div>", unsafe_allow_html=True)
                with col_p3:
                    if st.button("Próxima", disabled=st.session_state["pagina_carga"] >= total_paginas, use_container_width=True, key="btn_next_pend"):
                        st.session_state["pagina_carga"] += 1
                        st.rerun()

    # ---------------- ABA 2: RESOLUÇÕES SALVAS (RASCUNHO) ----------------
    with tab_rascunho:
        if df_rascunho.empty:
            st.info("Nenhuma resolução salva no rascunho ainda. Preencha os valores na aba 'Pendências' e clique em 'Salvar Resoluções'.")
        else:
            st.success(f"Você possui **{len(df_rascunho)}** campos resolvidos prontos para exportação.")
            
            col_b1, col_b2 = st.columns([1, 4])
            with col_b1:
                if st.button("Exportar Carga Manual", key="btn_exportar_tab", type="primary", use_container_width=True):
                    with st.spinner("Exportando..."):
                        sucesso = exportar_carga_manual()
                        if sucesso:
                            st.success("Carga exportada com sucesso!")
                            st.rerun()
            with col_b2:
                if st.button("Limpar Rascunho", key="btn_limpar_tab"):
                    limpar_rascunho()
                    st.warning("Rascunho limpo com sucesso!")
                    st.rerun()
                    
            st.markdown("---")
            colunas_exibir = [c for c in ["EMPRESA", "CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "CAMPO_FALTANTE", "VALOR_NOVO", "FONTE", "MOTIVO", "SOLICITANTE", "TIPO_EVENTO"] if c in df_rascunho.columns]
            st.dataframe(
                df_rascunho[colunas_exibir],
                use_container_width=True,
                hide_index=True
            )
```


---

## `src/ui/views/visao_carteira.py`

- Linhas: 278
- SHA-256: `ca35059c92d4e51ad08291aaae3fe58b49f5342ad4a101f22a5c1feb376a5505`
- Classes: -
- Funções: ler_parquet_ou_csv, carregar_dados_carteira, render_visao_carteira

```python
import streamlit as st
import pandas as pd
from pathlib import Path
import os
import sys

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

BASE_DIR = Path(".")

def ler_parquet_ou_csv(caminho_dir: Path, nome_base: str) -> pd.DataFrame:
    parquet_path = caminho_dir / f"{nome_base}.parquet"
    csv_path = caminho_dir / f"{nome_base}.csv"
    
    df = pd.DataFrame()
    if parquet_path.exists():
        try:
            df = pd.read_parquet(parquet_path)
        except Exception:
            pass
            
    if df.empty and csv_path.exists():
        try:
            df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig", dtype=str)
        except Exception:
            try:
                df = pd.read_csv(csv_path, sep=",", encoding="utf-8-sig", dtype=str)
            except Exception:
                pass
                
    if not df.empty:
        # Normaliza cabeçalhos em maiúsculo e remove colunas duplicadas
        df.columns = [str(c).replace("\ufeff", "").strip().upper() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()].copy()
        
    return df

def carregar_dados_carteira() -> pd.DataFrame:
    # Lê exclusivamente da Camada Gold (Visão Consolidada Final)
    gold_dir = BASE_DIR / "SAIDAS" / "gold" / "visao_operacional_negocio"
    df_gold = ler_parquet_ou_csv(gold_dir, "Visao_Operacional_BDC_LATEST")
    
    if df_gold.empty:
        raise FileNotFoundError("Base Gold consolidada não encontrada em SAIDAS/gold/visao_operacional_negocio.")
        
    # Remove a trava para permitir exibir todos (Com Contrato, Sem Contrato)
    pass
        
    linhas_carteira = []
    
    for _, row in df_gold.iterrows():
        cnpj_c = str(row.get("CNPJ", "")).strip()
        contraparte = str(row.get("NOME") or row.get("SIGLA") or f"CNPJ {cnpj_c}").strip()
        
        # Mapeamentos De -> Para diretos da Gold
        rating = str(row.get("RATING_FINAL", "")).strip()
        
        pd_raw = row.get("PD_FINAL")
        if pd.notna(pd_raw) and str(pd_raw).strip() not in ["", "nan", "None", "<NA>"]:
            try:
                pd_val = float(str(pd_raw).replace(',', '.'))
            except Exception:
                pd_val = None
        else:
            pd_val = None
            
        score = str(row.get("SCORE_BUREAU", "")).strip()
        restritivos = str(row.get("RESTRITIVOS", "")).strip()
        
        data_df_raw = row.get("DATA_DA_ANALISE")
        data_df = ""
        if pd.notna(data_df_raw) and str(data_df_raw).strip() not in ["", "nan", "None", "NaT"]:
            try:
                data_df = pd.to_datetime(data_df_raw).strftime("%d/%m/%Y")
            except Exception:
                data_df = str(data_df_raw).split(" ")[0]
                
        # Status de Fornecimento derivado da Gold
        status_ctr = str(row.get("STATUS_CONTRATUAL", "")).strip()
        if status_ctr == "CONTRATO_VIGENTE":
            status_fornecimento = "Em Fornecimento"
        elif status_ctr == "CONTRATO_FUTURO":
            status_fornecimento = "A Fornecer"
        else:
            status_fornecimento = "Desconhecido"
            
        # Tipo de Análise direto da Metodologia Exigida da Gold
        metodologia = str(row.get("METODOLOGIA_EXIGIDA", "")).strip().upper()
        if metodologia == "DF_DETALHADA":
            tipo_analise = "Análise DF"
        elif metodologia == "BUREAU":
            tipo_analise = "Análise Bureau"
        elif metodologia == "DISPENSADA":
            tipo_analise = "Dispensada"
        else:
            tipo_analise = "Sem Análise"
            
        # Datas de vigência formatadas
        dt_inicio = row.get("PROXIMO_INICIO")
        dt_fim = row.get("PROXIMO_FIM")
        
        vigencia_inicio = pd.to_datetime(dt_inicio).strftime("%d/%m/%Y") if pd.notna(dt_inicio) else None
        vigencia_fim = pd.to_datetime(dt_fim).strftime("%d/%m/%Y") if pd.notna(dt_fim) else None
        
        linhas_carteira.append({
            "CNPJ": cnpj_c,
            "Contraparte": contraparte,
            "Quantidade de contratos": int(row.get("QUANTIDADE_CONTRATOS", 0)) if pd.notna(row.get("QUANTIDADE_CONTRATOS")) else 0,
            "Numero do contrato": str(row.get("NUMERACAO_CONTRATOS", "")).strip() or None,
            "Rating": rating if rating and rating.lower() != "nan" else None,
            "Probabilidade de default": pd_val,
            "Score": score if score and score.lower() != "nan" else None,
            "Restritivos": restritivos if restritivos and restritivos.lower() != "nan" else None,
            "Data da Analise": data_df if data_df and data_df.lower() != "nat" else None,
            "Tipo de analise": tipo_analise,
            "Status_Fornecimento": status_fornecimento,
            "Posicao_MtM_MW": float(row.get("POSICAO_MTM_MW", 0.0)) if pd.notna(row.get("POSICAO_MTM_MW")) else 0.0,
            "Status_Conciliacao": str(row.get("STATUS_CONCILIACAO", "DIVERGENTE")).strip(),
            "Ano_Inicio": row.get("ANO_INICIO_CONTRATO", 0),
            "Vigencia_Inicio": vigencia_inicio,
            "Vigencia_Fim": vigencia_fim
        })
        
    return pd.DataFrame(linhas_carteira)

def render_visao_carteira():
    st.title("Visão das Carteiras")

    with st.expander("Dicionário de Dados da Visão Carteira", expanded=False):
        st.markdown("""
        ### Bloco 1: Identificação da Contraparte
        * **Contraparte:** Origem: Denodo Contratos -> Metadado: `CONTRAPARTE_APELIDO`. Nome Fantasia ou Razão Social consolidada.
        * **CNPJ:** Origem: Denodo Contratos -> Metadado: `CNPJ`. Chave de integração unificada e normalizada.

        ### Bloco 2: Posição Contratual
        * **Status de Fornecimento:** Origem: Denodo Contratos -> Transformação: Mapeado via lógica temporal (`EH_VIGENTE`, `EH_FUTURO`) em `servico_gold.py`.
        * **Quantidade de Contratos:** Origem: Denodo Contratos -> Transformação: `nunique()` da coluna `col_id` por CNPJ em `servico_gold.py`.
        * **Número do Contrato:** Origem: Denodo Contratos -> Transformação: Junção textual de todos os IDs de contratos associados na Gold.
        * **Vigência (Início / Fim):** Origem: Denodo Contratos -> Transformação: Extremos temporais (`min` e `max` de vigência) extraídos em `servico_gold.py`.
        * **Volume de Enquadramento (MWm):** Origem: Denodo Contratos -> Transformação: Agregação sumária na dimensão de contraparte. Define a Metodologia (DF vs Bureau).

        ### Bloco 3: Metodologia e Governança
        * **Tipo de Análise (Metodologia Exigida):** Origem: `fato_exposicao_risco` e `servico_gold.py` -> Regra de Destino: `DF_DETALHADA` (Volume >= 5 MWm) ou `BUREAU` (Volume < 5 MWm).

        ### Bloco 4: Indicadores de Risco de Crédito
        * **Rating Final:** Origem: Fichas (DF) ou RISK3 (Bureau) -> Filtro: Passa pela validação de domínio estrito `{A, B, C, D, E, F, NAO_ENQUADRADO}` no motor (`fato_analise_credito.py`). Respeita exclusividade mútua via `servico_gold.py`.
        * **Probabilidade de Default (PD):** Origem: Motor de Cálculo (Fato) ou RISK3 -> Regra de Destino: Float representando a (%) de risco de inadimplência associada ao Rating Final.
        * **Score Bureau:** Origem: RISK3 -> Regra de Destino: Pontuação quantitativa consumida independentemente do volume contratado (Fallback opcional).
        * **Restritivos:** Origem: RISK3 -> Regra de Destino: Marcador booleano/textual sobre alertas legais detectados.

        ### Bloco 5: Rastreabilidade
        * **Data da Análise:** Origem: Master Join (`servico_gold.py`) -> Regra de Destino: Herda a `DATA_BALANCO_USADO` (se DF) ou `DATA_CONSULTA` (se Bureau).
        """)

    try:
        df_carteira = carregar_dados_carteira()
    except FileNotFoundError as e:
        st.warning(f"⚠️ {e} Por favor, execute o ETL principal para gerar a camada Silver.")
        return
    except Exception as e:
        st.error(f"Erro ao processar visão da carteira: {e}")
        return

    if df_carteira.empty:
        st.info("Nenhum contrato ativo ou futuro encontrado na base do Denodo.")
        return

    # ---------------- FILTROS SUPERIORES ----------------
    st.markdown("Filtros de Carteira")
    f1, f2, f3, f4, f5 = st.columns([1, 1, 1, 1.2, 2])
    
    anos_disponiveis = sorted([int(a) for a in df_carteira["Ano_Inicio"].unique() if a > 0])
    with f1:
        anos_sel = st.multiselect("Ano Início:", anos_disponiveis, default=[])
        
    tipos_analise_disponiveis = ["Todos"] + sorted(list(df_carteira["Tipo de analise"].unique()))
    with f2:
        tipo_sel = st.selectbox("Tipo de Análise:", tipos_analise_disponiveis)
        
    with f3:
        status_sel = st.selectbox("Fornecimento:", ["Todos", "Em Fornecimento", "A Fornecer", "Sem Contrato"])

    with f4:
        mtm_sel = st.selectbox("Status MtM:", ["Todos", "Com MtM", "Sem MtM", "Análise Sem Contrato"])
        
    with f5:
        busca = st.text_input("Buscar por Contraparte/CNPJ:", placeholder="Filtrar...")

    # Aplicação dos Filtros
    df_filtrado = df_carteira.copy()
    
    if anos_sel:
        df_filtrado = df_filtrado[df_filtrado["Ano_Inicio"].isin(anos_sel)]
        
    if tipo_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Tipo de analise"] == tipo_sel]
        
    if status_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Status_Fornecimento"] == status_sel]
        
    if mtm_sel == "Com MtM":
        df_filtrado = df_filtrado[df_filtrado["Posicao_MtM_MW"] > 0]
    elif mtm_sel == "Sem MtM":
        df_filtrado = df_filtrado[df_filtrado["Posicao_MtM_MW"] == 0]
    elif mtm_sel == "Análise Sem Contrato":
        df_filtrado = df_filtrado[
            (df_filtrado["Tipo de analise"] != "Sem Análise") & 
            (df_filtrado["Status_Fornecimento"] == "Sem Contrato")
        ]
        
    if busca.strip():
        termo = busca.strip().lower()
        df_filtrado = df_filtrado[
            df_filtrado["Contraparte"].astype(str).str.lower().str.contains(termo) |
            df_filtrado["CNPJ"].astype(str).str.lower().str.contains(termo) |
            df_filtrado["Numero do contrato"].astype(str).str.lower().str.contains(termo)
        ]

    st.markdown("---")

    # ---------------- INSIGHTS / KPIS ----------------
    total_contrapartes = len(df_filtrado)
    total_contratos_reais = int(df_filtrado["Quantidade de contratos"].sum()) if not df_filtrado.empty and "Quantidade de contratos" in df_filtrado.columns else 0
    total_ativos = sum(df_filtrado["Status_Fornecimento"] == "Em Fornecimento")
    total_futuros = sum(df_filtrado["Status_Fornecimento"] == "A Fornecer")
    
    com_rating = sum(df_filtrado["Rating"].notna())
    pct_rating = (com_rating / total_contrapartes * 100) if total_contrapartes > 0 else 0
    
    com_score = sum(df_filtrado["Score"].notna() & (df_filtrado["Score"] != ""))
    pct_score = (com_score / total_contrapartes * 100) if total_contrapartes > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total de Contratos", f"{total_contratos_reais:,}".replace(",", "."))
    k2.metric("Contrapartes em Fornecimento", f"{total_ativos:,}".replace(",", "."))
    k3.metric("Contrapartes a Fornecer", f"{total_futuros:,}".replace(",", "."))
    k4.metric("Cobertura Rating (DF)", f"{pct_rating:.1f}%", f"{com_rating} clientes", delta_color="normal")
    k5.metric("Cobertura RISK3", f"{pct_score:.1f}%", f"{com_score} clientes", delta_color="normal")

    st.markdown("---")

    # ---------------- TABELA DE DADOS EXIGIDA ----------------
    st.subheader(f"Contrapartes da Carteira ({total_contrapartes} contrapartes)")
    
    colunas_exibicao = [
        "Contraparte",
        "CNPJ",
        "Quantidade de contratos",
        "Numero do contrato",
        "Rating",
        "Probabilidade de default",
        "Score",
        "Restritivos",
        "Data da Analise",
        "Tipo de analise",
        "Status_Fornecimento",
        "Posicao_MtM_MW",
        "Status_Conciliacao",
        "Vigencia_Inicio",
        "Vigencia_Fim"
    ]
    
    st.dataframe(
        df_filtrado[colunas_exibicao],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Probabilidade de default": st.column_config.NumberColumn(
                "PD (%)",
                format="%.4f%%"
            ),
            "Posicao_MtM_MW": st.column_config.NumberColumn(
                "MtM (MWm)",
                format="%.2f"
            )
        }
    )
```


---

## `src/ui/views/visao_orquestrador.py`

- Linhas: 111
- SHA-256: `87fdc451ce9d1906806db88a7e17d01ed1eb7fc69e2644ef68e440579550a410`
- Classes: -
- Funções: obter_ultimo_log_runner, render_visao_orquestrador

```python
import streamlit as st
import subprocess
import sys
import os
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(".")

def obter_ultimo_log_runner() -> tuple[Path | None, str]:
    logs_dir = BASE_DIR / "LOGS" / "runner"
    if not logs_dir.exists():
        logs_dir = BASE_DIR / "LOGS" / "execucao"
        
    if not logs_dir.exists():
        return None, "Pasta de logs não encontrada."
        
    arquivos_log = list(logs_dir.glob("*.log"))
    if not arquivos_log:
        return None, "Nenhum arquivo de log encontrado."
        
    arquivos_log.sort(key=os.path.getmtime, reverse=True)
    ultimo_log = arquivos_log[0]
    
    try:
        with open(ultimo_log, "r", encoding="utf-8", errors="replace") as f:
            linhas = f.readlines()
            ultimas_linhas = linhas[-80:] if len(linhas) > 80 else linhas
            return ultimo_log, "".join(ultimas_linhas)
    except Exception as e:
        return ultimo_log, f"Erro ao ler log: {e}"

def render_visao_orquestrador():
    st.header("Pipeline BDC")
    
    # Inicializa estado do processo e arquivo de saída
    if "pipeline_proc" not in st.session_state:
        st.session_state.pipeline_proc = None
        st.session_state.pipeline_inicio = None
        st.session_state.pipeline_log_file = None
        
    proc = st.session_state.pipeline_proc
    esta_executando = False
    
    if proc is not None:
        codigo_retorno = proc.poll()
        if codigo_retorno is None:
            esta_executando = True
        else:
            if codigo_retorno == 0:
                st.success("Última execução do pipeline foi concluída com sucesso!")
            else:
                st.error(f"O pipeline terminou com código de erro: {codigo_retorno}")
            st.session_state.pipeline_proc = None

    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if esta_executando:
            tempo_decorrido = int((datetime.now() - st.session_state.pipeline_inicio).total_seconds()) if st.session_state.pipeline_inicio else 0
            st.warning(f"Pipeline em execução... ({tempo_decorrido}s decorridos)")
            if st.button("Interromper Execução (Kill)", type="secondary"):
                proc.terminate()
                st.session_state.pipeline_proc = None
                st.warning("Processo interrompido.")
                st.rerun()
        else:
            if st.button("Executar", type="primary", use_container_width=True):
                try:
                    runner_logs_dir = BASE_DIR / "LOGS" / "runner"
                    runner_logs_dir.mkdir(parents=True, exist_ok=True)
                    log_stdout_path = runner_logs_dir / f"STDOUT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                    
                    # Abre arquivo de saída para redirecionar stdout/stderr sem risco de deadlock de buffer
                    log_file_handle = open(log_stdout_path, "w", encoding="utf-8")
                    
                    novo_proc = subprocess.Popen(
                        [sys.executable, "main.py"],
                        cwd=str(BASE_DIR.resolve()),
                        stdout=log_file_handle,
                        stderr=subprocess.STDOUT
                    )
                    st.session_state.pipeline_proc = novo_proc
                    st.session_state.pipeline_inicio = datetime.now()
                    st.session_state.pipeline_log_file = str(log_stdout_path)
                    st.success("Pipeline iniciado em segundo plano!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Falha ao iniciar processo: {e}")

    with col3:
        if st.button("Atualizar Log", use_container_width=True):
            st.rerun()
            
    st.markdown("---")
    
    # Monitor de Logs em Tempo Real
    st.subheader("Log de Execução do Pipeline")
    caminho_log, conteudo_log = obter_ultimo_log_runner()
    
    if caminho_log:
        st.caption(f"Visualizando arquivo: `{caminho_log}` (últimas 80 linhas)")
        st.code(conteudo_log, language="log")
    else:
        st.info(conteudo_log)

    # Se o pipeline estiver rodando, faz polling/refresh a cada 2 segundos
    if esta_executando:
        time.sleep(2)
        st.rerun()
```


---

## `src/ui/views/visao_silver.py`

- Linhas: 208
- SHA-256: `ce48c46304579ee762f5caddff1f83079cfb245ca3d5b535adc22236c4679a01`
- Classes: -
- Funções: ler_arquivo_silver, registrar_correcao_rascunho, render_visao_silver, aplicar_filtro

```python
import streamlit as st
import pandas as pd
from pathlib import Path
import os
import sys
import json

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from common.identificadores import normalizar_cnpj
from common.datas import normalizar_data

BASE_DIR = Path(".")
DIAGNOSTICO_DIR = BASE_DIR / "ENTRADAS" / "atualizacoes_manuais" / "diagnostico"
RASCUNHO_PATH = DIAGNOSTICO_DIR / "rascunho_carga_manual.csv"
SCHEMA_PATH = BASE_DIR / "ENTRADAS" / "control" / "schemas" / "schema_carga_manual.json"

try:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)
    MOTIVOS_PERMITIDOS = schema.get("properties", {}).get("MOTIVO", {}).get("enum", ["Outro"])
    SOLICITANTES_PERMITIDOS = schema.get("properties", {}).get("SOLICITANTE", {}).get("enum", ["Outro..."])
except Exception:
    MOTIVOS_PERMITIDOS = ["Correção de Falhas na Origem", "Atualização Histórica", "Intervenção de Alçada (Override)", "Outro"]
    SOLICITANTES_PERMITIDOS = ["Malik Ribeiro Mourad", "Eduardo Suzuki Yamauti"]

def ler_arquivo_silver(caminho_base: Path, nome_arquivo: str) -> pd.DataFrame | None:
    parquet_path = caminho_base / f"{nome_arquivo}.parquet"
    csv_path = caminho_base / f"{nome_arquivo}.csv"
    
    if parquet_path.exists():
        try:
            return pd.read_parquet(parquet_path)
        except Exception:
            pass
            
    if csv_path.exists():
        try:
            return pd.read_csv(csv_path, sep=";", encoding="utf-8-sig", dtype=str)
        except Exception:
            pass
            
    return None

def registrar_correcao_rascunho(cnpj: str, data_df: str, empresa: str, campo: str, valor_novo: str, motivo: str, solicitante: str):
    res_cnpj = normalizar_cnpj(cnpj)
    cnpj_norm = res_cnpj.cnpj if res_cnpj.cnpj else cnpj.strip()
    data_norm = normalizar_data(data_df) or data_df.strip()
    
    if RASCUNHO_PATH.exists():
        try:
            df_rascunho = pd.read_csv(RASCUNHO_PATH, sep=";", dtype=str).fillna("")
        except Exception:
            df_rascunho = pd.DataFrame()
    else:
        df_rascunho = pd.DataFrame(columns=["CNPJ", "DATA_DEMONSTRACAO_FINANCEIRA", "EMPRESA", "CAMPO_FALTANTE", "VALOR_NOVO", "FONTE", "MOTIVO", "SOLICITANTE", "TIPO_EVENTO"])

    nova_linha = {
        "CNPJ": cnpj_norm,
        "DATA_DEMONSTRACAO_FINANCEIRA": data_norm,
        "EMPRESA": empresa.strip(),
        "CAMPO_FALTANTE": campo.strip(),
        "VALOR_NOVO": str(valor_novo).strip(),
        "FONTE": "OVERRIDE_MANUAL_SILVER",
        "MOTIVO": motivo,
        "SOLICITANTE": solicitante,
        "TIPO_EVENTO": "CORRECAO"
    }

    if not df_rascunho.empty:
        df_rascunho = df_rascunho[~(
            (df_rascunho["CNPJ"].astype(str).str.strip() == cnpj_norm) & 
            (df_rascunho["DATA_DEMONSTRACAO_FINANCEIRA"].astype(str).str.strip() == data_norm) & 
            (df_rascunho["CAMPO_FALTANTE"].astype(str).str.strip().str.upper() == campo.strip().upper())
        )]

    df_rascunho = pd.concat([df_rascunho, pd.DataFrame([nova_linha])], ignore_index=True)
    DIAGNOSTICO_DIR.mkdir(parents=True, exist_ok=True)
    df_rascunho.to_csv(RASCUNHO_PATH, index=False, sep=";")

def render_visao_silver():
    st.header("Visão da Camada Silver")

    # Formulário de Correção / Override
    with st.expander("Criar Correção de Dado Incorreto", expanded=False):
        st.markdown("Utilize este formulário para solicitar a **correção de um dado incorreto** já extraído na Silver. A correção será gravada como evento `CORRECAO` e aplicada na próxima execução.")
        
        with st.form("form_correcao_silver"):
            c1, c2, c3 = st.columns(3)
            with c1:
                cnpj_input = st.text_input("CNPJ da Empresa:", placeholder="Ex: 00.001.180/0001-26")
            with c2:
                data_input = st.text_input("Data da DF (YYYY-MM-DD ou DD/MM/YYYY):", placeholder="Ex: 2024-12-31")
            with c3:
                empresa_input = st.text_input("Nome da Empresa / Sigla:", placeholder="Ex: ELETROBRAS")

            c4, c5, c6 = st.columns(3)
            with c4:
                campo_input = st.text_input("Nome da Coluna / Campo Afetado:", placeholder="Ex: PATRIMONIO_LIQUIDO")
            with c5:
                valor_antigo_input = st.text_input("Valor Anterior (Referência):", placeholder="Ex: 1000000")
            with c6:
                valor_novo_input = st.text_input("Novo Valor Correto:", placeholder="Ex: 1250000")

            c7, c8 = st.columns(2)
            with c7:
                motivo_sel = st.selectbox("Motivo da Correção:", MOTIVOS_PERMITIDOS)
            with c8:
                solicitante_sel = st.selectbox("Solicitante:", SOLICITANTES_PERMITIDOS)

            submit_correcao = st.form_submit_button("Salvar Correção no Rascunho", type="primary")
            if submit_correcao:
                if not cnpj_input.strip() or not campo_input.strip() or not valor_novo_input.strip():
                    st.error("CNPJ, Campo Afetado e Novo Valor são obrigatórios.")
                else:
                    registrar_correcao_rascunho(
                        cnpj=cnpj_input,
                        data_df=data_input,
                        empresa=empresa_input,
                        campo=campo_input,
                        valor_novo=valor_novo_input,
                        motivo=motivo_sel,
                        solicitante=solicitante_sel
                    )
                    st.success(f"Correção para o campo '{campo_input}' registrada com sucesso no rascunho de carga manual!")

    st.markdown("---")
    
    busca = st.text_input("Buscar por Contraparte, CNPJ ou Contrato:", placeholder="Digite um termo para filtrar em todas as bases...")

    # Abas de Consulta dos Datasets
    tab_com, tab_cons, tab_denodo, tab_sf, tab_rec = st.tabs([
        "Comercializadoras",
        "Consumidores",
        "Denodo (Contratos)",
        "Salesforce (Accounts)",
        "Receita Federal"
    ])

    silver_base = BASE_DIR / "SAIDAS" / "silver"

    def aplicar_filtro(df):
        if not busca.strip() or df is None or df.empty:
            return df
        termo = busca.strip().lower()
        
        colunas_alvo = [
            "CNPJ", "CONTRAPARTE_CNPJ", 
            "EMPRESA", "SIGLA", "CONTRAPARTE_NOME_FANTASIA", "NAME", "NOME_EMPRESARIAL", 
            "CONTRATO", "NUMERO_REFERENCIA_CONTRATO"
        ]
        
        colunas_busca = [col for col in df.columns if col.upper() in colunas_alvo]
        
        if not colunas_busca:
            colunas_busca = df.columns
            
        mask = pd.Series(False, index=df.index)
        for col in colunas_busca:
            mask = mask | df[col].astype(str).str.lower().str.contains(termo, regex=False, na=False)
            
        return df[mask]

    with tab_com:
        df = ler_arquivo_silver(silver_base / "fichas_comercializadoras_extraidas", "fichas_comercializadoras_extraidas")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Registros", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base de Comercializadoras não encontrada em SAIDAS/silver/fichas_comercializadoras_extraidas. Execute o pipeline primeiro.")

    with tab_cons:
        df = ler_arquivo_silver(silver_base / "fichas_consumidores_extraidas", "fichas_consumidores_extraidas")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Registros", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base de Consumidores não encontrada em SAIDAS/silver/fichas_consumidores_extraidas. Execute o pipeline primeiro.")

    with tab_denodo:
        df = ler_arquivo_silver(silver_base / "denodo_contratos_silver", "contratos_correntes")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Contratos", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base do Denodo não encontrada em SAIDAS/silver/denodo_contratos_silver. Execute o pipeline primeiro.")

    with tab_sf:
        df = ler_arquivo_silver(silver_base / "salesforce_silver" / "account", "salesforce_account")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Contas Salesforce", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base do Salesforce não encontrada em SAIDAS/silver/salesforce_silver/account. Execute o pipeline primeiro.")

    with tab_rec:
        df = ler_arquivo_silver(silver_base / "receita_silver", "receita_cadastral_silver")
        if df is not None and not df.empty:
            df_filtrado = aplicar_filtro(df)
            st.metric("Total de Registros Cadastrais", len(df_filtrado))
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("Base da Receita Federal não encontrada em SAIDAS/silver/receita_silver. Execute o pipeline primeiro.")
```
