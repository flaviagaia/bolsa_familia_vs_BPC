from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .config import COMPARISON_PATH, PROCESSED_DIR, RAW_BOLSA_PATH, RAW_MUNICIPALITIES_PATH, SUMMARY_PATH, YEAR_REFERENCE


def load_bolsa_familia_year(year_reference: int = YEAR_REFERENCE) -> pd.DataFrame:
    raw_df = pd.read_csv(RAW_BOLSA_PATH)
    raw_df = raw_df[raw_df["social_categoria"] == "Bolsa Família"].copy()
    raw_df = raw_df[raw_df["ano"].astype(int) == year_reference].copy()

    pivot_df = (
        raw_df.pivot_table(
            index=["co_mun", "no_mun", "ano"],
            columns="social_subcategoria",
            values="valor",
            aggfunc="first",
        )
        .reset_index()
        .rename(
            columns={
                "co_mun": "codigo_municipio",
                "no_mun": "municipio",
                "Valor Total Repassado do Bolsa Família": "valor_bolsa_familia",
                "Famílias beneficiárias": "familias_bolsa_familia",
                "Benefício médio recebido pelas famílias do Bolsa Família": "beneficio_medio_bolsa_familia",
            }
        )
    )
    pivot_df["codigo_municipio"] = pivot_df["codigo_municipio"].astype(str)
    pivot_df["ano"] = pivot_df["ano"].astype(int)
    return pivot_df[
        [
            "codigo_municipio",
            "municipio",
            "ano",
            "valor_bolsa_familia",
            "familias_bolsa_familia",
            "beneficio_medio_bolsa_familia",
        ]
    ].sort_values("municipio")


def load_municipalities() -> pd.DataFrame:
    raw_df = pd.read_csv(RAW_MUNICIPALITIES_PATH)
    municipalities = raw_df[["co_mun", "no_mun"]].drop_duplicates().rename(
        columns={"co_mun": "codigo_municipio", "no_mun": "municipio"}
    )
    municipalities["codigo_municipio"] = municipalities["codigo_municipio"].astype(str)
    return municipalities.sort_values("municipio").reset_index(drop=True)


def build_synthetic_bpc_year(year_reference: int = YEAR_REFERENCE, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    municipalities = load_municipalities()
    min_wage = {2023: 1320.0, 2024: 1412.0, 2025: 1518.0}
    year_value = min_wage[year_reference]

    records: list[dict[str, object]] = []
    for idx, row in municipalities.iterrows():
        municipal_factor = 0.65 + (idx / len(municipalities)) * 1.7
        judicial_base = 0.05 + ((idx % 9) / 100)
        if row["municipio"] in {"Maceió", "Arapiraca", "Palmeira dos Índios"}:
            judicial_base += 0.08

        annual_benefits = 0
        annual_judicial = 0
        annual_value = 0.0
        annual_judicial_value = 0.0

        for month in range(1, 13):
            seasonal = 1.02 if month in (1, 2) else 1.0 if month <= 10 else 1.04
            base_benefits = int(max(55, rng.normal(loc=260 * municipal_factor * seasonal, scale=18)))
            judicial_share = min(0.30, max(0.03, rng.normal(loc=judicial_base, scale=0.015)))
            judicial_count = max(1, int(round(base_benefits * judicial_share)))

            annual_benefits += base_benefits
            annual_judicial += judicial_count
            annual_value += base_benefits * year_value
            annual_judicial_value += judicial_count * year_value

        records.append(
            {
                "codigo_municipio": row["codigo_municipio"],
                "municipio": row["municipio"],
                "ano": year_reference,
                "valor_bpc": round(annual_value, 2),
                "beneficios_bpc": int(annual_benefits),
                "beneficio_medio_bpc": float(year_value),
                "beneficios_judiciais_bpc": int(annual_judicial),
                "valor_judicial_bpc": round(annual_judicial_value, 2),
            }
        )

    bpc_df = pd.DataFrame(records)
    bpc_df["taxa_judicializacao_bpc_pct"] = (
        (bpc_df["beneficios_judiciais_bpc"] / bpc_df["beneficios_bpc"]) * 100
    ).round(2)
    return bpc_df.sort_values("municipio")


def build_comparison_dataset(year_reference: int = YEAR_REFERENCE) -> pd.DataFrame:
    bolsa_df = load_bolsa_familia_year(year_reference)
    bpc_df = build_synthetic_bpc_year(year_reference)
    comparison_df = bolsa_df.merge(
        bpc_df,
        on=["codigo_municipio", "municipio", "ano"],
        how="inner",
    )
    comparison_df["valor_total_transferencias"] = (
        comparison_df["valor_bolsa_familia"] + comparison_df["valor_bpc"]
    )
    comparison_df["participacao_bolsa_pct"] = (
        comparison_df["valor_bolsa_familia"] / comparison_df["valor_total_transferencias"] * 100
    ).round(2)
    comparison_df["participacao_bpc_pct"] = (
        comparison_df["valor_bpc"] / comparison_df["valor_total_transferencias"] * 100
    ).round(2)
    comparison_df["razao_bolsa_bpc"] = (
        comparison_df["valor_bolsa_familia"] / comparison_df["valor_bpc"]
    ).round(3)
    comparison_df["perfil_territorial"] = comparison_df["participacao_bolsa_pct"].map(
        lambda value: "Predomínio Bolsa Família"
        if value >= 65
        else "Predomínio BPC"
        if value <= 35
        else "Equilíbrio relativo"
    )
    comparison_df["indice_pressao_assistencial"] = (
        (
            comparison_df["valor_total_transferencias"] / comparison_df["valor_total_transferencias"].mean()
        )
        * (
            (comparison_df["taxa_judicializacao_bpc_pct"] / comparison_df["taxa_judicializacao_bpc_pct"].mean())
        )
        * (comparison_df["participacao_bpc_pct"] / 100 + 0.5)
    ).round(3)
    comparison_df["alerta_prioritario"] = comparison_df["indice_pressao_assistencial"].map(
        lambda value: "alto" if value >= 2.1 else "moderado" if value >= 1.3 else "baixo"
    )
    return comparison_df.sort_values("valor_total_transferencias", ascending=False).reset_index(drop=True)


def build_summary_dict(comparison_df: pd.DataFrame) -> dict[str, object]:
    top_total = comparison_df.sort_values("valor_total_transferencias", ascending=False).iloc[0]
    top_bolsa = comparison_df.sort_values("participacao_bolsa_pct", ascending=False).iloc[0]
    top_bpc = comparison_df.sort_values("participacao_bpc_pct", ascending=False).iloc[0]
    top_alert = comparison_df.sort_values("indice_pressao_assistencial", ascending=False).iloc[0]
    return {
        "ano_referencia": int(comparison_df["ano"].max()),
        "municipios_cobertos": int(comparison_df["codigo_municipio"].nunique()),
        "valor_total_bolsa_familia": float(round(comparison_df["valor_bolsa_familia"].sum(), 2)),
        "valor_total_bpc": float(round(comparison_df["valor_bpc"].sum(), 2)),
        "valor_total_transferencias": float(round(comparison_df["valor_total_transferencias"].sum(), 2)),
        "municipio_maior_volume_total": str(top_total["municipio"]),
        "municipio_maior_participacao_bolsa": str(top_bolsa["municipio"]),
        "municipio_maior_participacao_bpc": str(top_bpc["municipio"]),
        "municipio_maior_alerta": str(top_alert["municipio"]),
        "taxa_media_judicializacao_bpc_pct": float(round(comparison_df["taxa_judicializacao_bpc_pct"].mean(), 2)),
    }


def run_pipeline() -> dict[str, object]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    comparison_df = build_comparison_dataset()
    summary = build_summary_dict(comparison_df)
    comparison_df.to_csv(COMPARISON_PATH, index=False)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary
