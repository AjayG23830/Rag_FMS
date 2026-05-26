"""
FMS Phase 2 — Analytics Router
Read analytics tables populated by ETL and expose them as APIs.
Also provides POST /analytics/run-etl to trigger pipeline from the UI.
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Optional
from database import get_db
import subprocess, os, sys

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/program-stats")
def program_stats(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT program_name, feedback_count, avg_rating, min_rating, max_rating "
                           "FROM analytics_program_stats ORDER BY feedback_count DESC")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/rating-distribution")
def rating_distribution(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT rating, count FROM analytics_rating_distribution ORDER BY rating")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/monthly-trend")
def monthly_trend(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT month, feedback_count, avg_rating FROM analytics_monthly_trend ORDER BY month")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    """KPIs derived from analytics tables."""
    total = db.execute(text("SELECT COUNT(*) AS c FROM analytics_feedback_clean")).scalar() or 0
    avg = db.execute(text("SELECT AVG(rating) AS a FROM analytics_feedback_clean")).scalar()
    programs = db.execute(text("SELECT COUNT(*) AS c FROM analytics_program_stats")).scalar() or 0
    last_run = db.execute(text("SELECT run_at, rows_extracted, rows_loaded, status "
                               "FROM etl_runs ORDER BY run_id DESC LIMIT 1")).mappings().first()
    return {
        "total_clean_records": total,
        "overall_avg_rating": round(float(avg), 2) if avg else 0,
        "total_programs": programs,
        "last_etl_run": dict(last_run) if last_run else None,
    }


@router.post("/run-etl")
def run_etl(dataset_path: Optional[str] = None):
    """Trigger the ETL pipeline. Returns stdout / stderr for transparency."""
    script_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "etl")
    script_dir = os.path.abspath(script_dir)
    cmd = [sys.executable, "run_etl.py"]
    if dataset_path: cmd.append(dataset_path)
    try:
        result = subprocess.run(cmd, cwd=script_dir, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise HTTPException(500, f"ETL failed: {result.stderr or result.stdout}")
        return {"status": "success", "output": result.stdout}
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "ETL timeout")
    except Exception as e:
        raise HTTPException(500, f"ETL error: {str(e)}")
