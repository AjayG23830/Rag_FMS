"""TRANSFORM — clean and reshape the feedback DataFrame ready for analytics."""
import pandas as pd


def transform(df: pd.DataFrame) -> dict:
    """Clean records and return cleaned df + aggregated analytics DataFrames."""
    rows_before = len(df)

    # 1. Strip whitespace on text columns
    df["participant_name"] = df["participant_name"].astype(str).str.strip()
    df["program_name"]     = df["program_name"].astype(str).str.strip()
    df["comments"]         = df["comments"].fillna("").astype(str).str.strip()

    # 2. Standardize comments to sentence case (avoid SHOUTY input)
    df["comments"] = df["comments"].apply(lambda s: s if s.islower() or not s.isupper() else s.capitalize())

    # 3. Drop rows where rating is invalid (must be 1..5)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df[df["rating"].between(1, 5)].copy()
    df["rating"] = df["rating"].astype(int)

    # 4. Parse submitted_at and drop rows where parsing fails
    df["submitted_at"] = pd.to_datetime(df["submitted_at"], errors="coerce")
    df = df.dropna(subset=["submitted_at"]).copy()

    # 5. Remove exact duplicates
    df = df.drop_duplicates(subset=["participant_name", "program_name", "rating", "submitted_at"])

    rows_after = len(df)
    print(f"[TRANSFORM] Cleaned: {rows_before} → {rows_after} rows ({rows_before - rows_after} dropped)")

    # ─── AGGREGATIONS for analytics tables ─────────────────────────────
    # Per-program: avg rating, count, distribution
    prog = df.groupby("program_name").agg(
        feedback_count=("rating", "count"),
        avg_rating=("rating", "mean"),
        min_rating=("rating", "min"),
        max_rating=("rating", "max"),
    ).round(2).reset_index()

    # Rating distribution (overall)
    dist = df["rating"].value_counts().reindex([1,2,3,4,5], fill_value=0).reset_index()
    dist.columns = ["rating", "count"]

    # Monthly feedback trend
    df["month"] = df["submitted_at"].dt.to_period("M").astype(str)
    monthly = df.groupby("month").agg(
        feedback_count=("rating", "count"),
        avg_rating=("rating", "mean"),
    ).round(2).reset_index().sort_values("month")

    print(f"[TRANSFORM] Built {len(prog)} program rows, {len(dist)} dist rows, {len(monthly)} monthly rows")
    return {"cleaned": df, "program_stats": prog, "rating_distribution": dist, "monthly_trend": monthly}


if __name__ == "__main__":
    from extract import extract
    df = extract("datasets/feedback_raw.csv")
    out = transform(df)
    print("\n── Program stats ──")
    print(out["program_stats"])
    print("\n── Rating distribution ──")
    print(out["rating_distribution"])
    print("\n── Monthly trend (last 5) ──")
    print(out["monthly_trend"].tail(5))
