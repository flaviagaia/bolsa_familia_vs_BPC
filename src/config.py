from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_BOLSA_PATH = BASE_DIR / "data" / "raw" / "al_bolsa_familia_municipios.csv"
RAW_MUNICIPALITIES_PATH = BASE_DIR / "data" / "raw" / "al_municipios_base.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
COMPARISON_PATH = PROCESSED_DIR / "territorial_comparison.parquet"
SUMMARY_PATH = PROCESSED_DIR / "summary.json"
YEAR_REFERENCE = 2023
