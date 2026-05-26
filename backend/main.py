"""FMS Analytics API — standalone FastAPI entry point for Render deployment."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import subprocess, sys, os

ETL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "etl")


def _run_startup_etl():
    """Seed the SQLite database on every startup (Render filesystem is ephemeral)."""
    print("[STARTUP] Running ETL to populate analytics tables...")
    result = subprocess.run(
        [sys.executable, "run_etl.py"],
        cwd=ETL_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        print(f"[STARTUP] ETL warning:\n{result.stderr}")
    else:
        print(result.stdout)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_startup_etl()
    yield


app = FastAPI(
    title="FMS Analytics API",
    description="Feedback Management System — Phase 2 Analytics",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import analytics  # noqa: E402  (import after app init)
app.include_router(analytics.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "FMS Analytics API is running",
        "docs": "/docs",
        "endpoints": [
            "GET  /analytics/summary",
            "GET  /analytics/program-stats",
            "GET  /analytics/rating-distribution",
            "GET  /analytics/monthly-trend",
            "POST /analytics/run-etl",
        ],
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}
