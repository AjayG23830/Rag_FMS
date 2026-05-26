"""
ETL Pipeline orchestrator for FMS Phase 2.

Usage:
    python run_etl.py                              # default dataset
    python run_etl.py datasets/feedback_raw.csv    # explicit dataset
"""
import os
from pathlib import Path
# Ensure script runs from project root regardless of cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

import sys
from extract import extract
from transform import transform
from load import load


def run_etl(dataset_path: str = "datasets/feedback_raw.csv", db_path: str = "backend/feedback.db"):
    print("=" * 60)
    print(f" FMS ETL PIPELINE — {dataset_path}")
    print("=" * 60)
    df_raw = extract(dataset_path)
    out = transform(df_raw)
    load(out, rows_extracted=len(df_raw), db_path=db_path)
    print("=" * 60)
    print(" ETL COMPLETED SUCCESSFULLY ✅")
    print("=" * 60)
    return {"extracted": len(df_raw), "loaded": len(out["cleaned"])}


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "datasets/feedback_raw.csv"
    run_etl(path)
