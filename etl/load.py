"""LOAD — write cleaned + aggregated data into SQLite analytics tables."""
import sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = "../backend/feedback.db"  # relative to etl/ folder; adjust if needed


def _connect(db_path: str = DB_PATH):
    return sqlite3.connect(db_path)


def _create_analytics_tables(conn):
    """Create analytics tables if they don't exist."""
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS analytics_feedback_clean (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant_name TEXT, program_name TEXT, rating INTEGER,
        comments TEXT, submitted_at TIMESTAMP, loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_program_stats (
        program_name TEXT PRIMARY KEY,
        feedback_count INTEGER, avg_rating REAL, min_rating INTEGER, max_rating INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_rating_distribution (
        rating INTEGER PRIMARY KEY, count INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS analytics_monthly_trend (
        month TEXT PRIMARY KEY,
        feedback_count INTEGER, avg_rating REAL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS etl_runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rows_extracted INTEGER, rows_loaded INTEGER, status TEXT, notes TEXT
    );
    """)
    conn.commit()


def load(transformed: dict, rows_extracted: int, db_path: str = DB_PATH):
    """Wipe and rewrite analytics tables with the latest aggregations."""
    conn = _connect(db_path)
    try:
        _create_analytics_tables(conn)
        cur = conn.cursor()

        # Cleaned records (replace)
        cur.execute("DELETE FROM analytics_feedback_clean")
        transformed["cleaned"][["participant_name","program_name","rating","comments","submitted_at"]] \
            .to_sql("analytics_feedback_clean", conn, if_exists="append", index=False)

        # Aggregates (replace)
        for table, df in [
            ("analytics_program_stats",        transformed["program_stats"]),
            ("analytics_rating_distribution",  transformed["rating_distribution"]),
            ("analytics_monthly_trend",        transformed["monthly_trend"]),
        ]:
            cur.execute(f"DELETE FROM {table}")
            df.to_sql(table, conn, if_exists="append", index=False)

        rows_loaded = len(transformed["cleaned"])
        cur.execute("INSERT INTO etl_runs (rows_extracted, rows_loaded, status, notes) VALUES (?,?,?,?)",
                    (rows_extracted, rows_loaded, "success", "FMS feedback ETL"))
        conn.commit()
        print(f"[LOAD] {rows_loaded} cleaned rows + aggregates written to analytics tables")
    finally:
        conn.close()


if __name__ == "__main__":
    from extract import extract
    from transform import transform
    df = extract("datasets/feedback_raw.csv")
    out = transform(df)
    load(out, rows_extracted=len(df))
