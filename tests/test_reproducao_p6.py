"""Teste de reprodução da PD base real corrigida contra as fichas de padrao_6 CPURA vigentes.

Critério de Aceite: 83 de 83 fichas de padrao_6 com insumos contábeis válidos
devem reproduzir a PD declarada da ficha com tolerância < 1e-6.
"""
from __future__ import annotations

import sys
import json
import math
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from domain.credito.pd_base import calcular_pd_base
from common.numeros import to_float_br


def main() -> int:
    print("\n" + "=" * 90)
    print("🔬 BDC — TESTE DE REPRODUÇÃO REAL DA PD BASE (PADRÃO 6 CPURA VIGENTES)")
    print("=" * 90)

    cfg_path = PROJECT_ROOT / "ENTRADAS" / "control" / "configs" / "pd_zscore_config.json"
    if not cfg_path.exists():
        print(f"[-] Configuração não encontrada: {cfg_path}")
        return 1

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    # Carregar Silver
    silver_csv = PROJECT_ROOT / "SAIDAS" / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.csv"
    silver_parquet = PROJECT_ROOT / "SAIDAS" / "silver" / "fichas_comercializadoras_extraidas" / "fichas_comercializadoras_extraidas.parquet"

    if silver_parquet.exists():
        df_silver = pd.read_parquet(silver_parquet)
    elif silver_csv.exists():
        df_silver = pd.read_csv(silver_csv, sep=";")
    else:
        print("[-] Base Silver não encontrada. Abortando.")
        return 1

    # Filtrar vigentes de padrao_6 CPURA
    status_col = "_STATUS_REGISTRO" if "_STATUS_REGISTRO" in df_silver.columns else None
    if status_col:
        vig = df_silver[df_silver[status_col] == "VIGENTE"].copy()
    else:
        vig = df_silver.copy()

    tipo_col = "TIPO_COMERCIALIZADORA" if "TIPO_COMERCIALIZADORA" in vig.columns else "CATEGORIA"
    p6_cpura = vig[(vig["versao_ficha"] == "padrao_6") & (vig[tipo_col] == "CPURA")]

    print(f"[+] Total de fichas padrao_6 CPURA vigentes avaliadas: {len(p6_cpura)}")

    class _LogMudo:
        def warning(self, *a, **kw): pass

    reproduzidos_1e6 = 0
    reproduzidos_1e4 = 0
    insumos_invalidos = 0
    linhas = []

    for _, r in p6_cpura.iterrows():
        reg = {k: (None if pd.isna(v) else v) for k, v in r.to_dict().items()}
        reg.pop("PD_BASE", None)

        pd_calc = calcular_pd_base(reg, "CPURA", cfg, _LogMudo())
        pd_decl = to_float_br(r.get("PROBABILIDADE_DEFAULT"))

        if pd_calc is None:
            insumos_invalidos += 1
            dif = None
        else:
            dif = abs(pd_calc - pd_decl) if pd_decl is not None else None
            if dif is not None:
                if dif < 1e-6:
                    reproduzidos_1e6 += 1
                if dif < 1e-4:
                    reproduzidos_1e4 += 1

        linhas.append({
            "arquivo": r.get("arquivo_nome"),
            "cnpj": r.get("CNPJ"),
            "pd_declarada": pd_decl,
            "pd_calculada_real": pd_calc,
            "diferenca": dif,
        })

    df_comp = pd.DataFrame(linhas)
    total_validos = len(p6_cpura) - insumos_invalidos

    print("\n" + "=" * 90)
    print("📊 RESULTADO DO CONFRONTO CONTRA A BASE VIGENTE:")
    print("=" * 90)
    print(f"Total avaliado:                      {len(p6_cpura)}")
    print(f"Insumos ausentes/inválidos (None):   {insumos_invalidos} (conforme regra de negócio D5)")
    print(f"Com insumos válidos:                 {total_validos}")
    print(f"Reprodução exata (tol < 1e-6):       {reproduzidos_1e6} de {total_validos} ({reproduzidos_1e6/total_validos*100:.1f}%)")
    print(f"Reprodução tolerante (tol < 1e-4):   {reproduzidos_1e4} de {total_validos} ({reproduzidos_1e4/total_validos*100:.1f}%)")

    print("\n" + "=" * 90)
    print("🔍 AMOSTRA DE 10 REGISTROS CONFRONTADOS:")
    print("=" * 90)
    print(df_comp.dropna(subset=["diferenca"]).head(10).to_string(index=False))

    print("\n" + "=" * 90)
    if reproduzidos_1e6 == total_validos:
        print("✅ SUCESSO: 100% das fichas com insumos contábeis válidos reproduzem a PD com precisão < 1e-6!")
        print("=" * 90 + "\n")
        return 0
    else:
        print(f"❌ ATENÇÃO: {total_validos - reproduzidos_1e6} fichas divergiram além da tolerância.")
        print("=" * 90 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
