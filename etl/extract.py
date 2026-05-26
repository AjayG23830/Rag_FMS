"""EXTRACT — read raw feedback data from CSV / Excel into a pandas DataFrame."""
import pandas as pd
from pathlib import Path


def extract(file_path: str) -> pd.DataFrame:
    """Read CSV or Excel file based on extension."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    ext = p.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    print(f"[EXTRACT] Loaded {len(df)} raw rows from {file_path}")
    return df


if __name__ == "__main__":
    df = extract("datasets/feedback_raw.csv")
    print(df.head())
    print(f"\nColumns: {list(df.columns)}")
    print(f"Dtypes:\n{df.dtypes}")
