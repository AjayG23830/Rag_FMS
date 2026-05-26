"""RAG chat over FMS feedback data — uses OpenAI with analytics tables as context."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
import os

router = APIRouter(prefix="/analytics", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str


def _build_context(db: Session) -> str:
    total = db.execute(text("SELECT COUNT(*) FROM analytics_feedback_clean")).scalar() or 0
    avg = db.execute(text("SELECT AVG(rating) FROM analytics_feedback_clean")).scalar()
    prog_count = db.execute(text("SELECT COUNT(*) FROM analytics_program_stats")).scalar() or 0

    programs = db.execute(text(
        "SELECT program_name, feedback_count, avg_rating, min_rating, max_rating "
        "FROM analytics_program_stats ORDER BY feedback_count DESC"
    )).mappings().all()

    dist = db.execute(text(
        "SELECT rating, count FROM analytics_rating_distribution ORDER BY rating"
    )).mappings().all()

    trend = db.execute(text(
        "SELECT month, feedback_count, avg_rating FROM analytics_monthly_trend ORDER BY month"
    )).mappings().all()

    samples = db.execute(text(
        "SELECT participant_name, program_name, rating, comments "
        "FROM analytics_feedback_clean ORDER BY RANDOM() LIMIT 30"
    )).mappings().all()

    prog_lines = "\n".join(
        f"  - {r['program_name']}: {r['feedback_count']} feedbacks, "
        f"avg {r['avg_rating']:.2f} stars (min {r['min_rating']}, max {r['max_rating']})"
        for r in programs
    )
    dist_lines = "\n".join(f"  - {r['rating']} stars: {r['count']} responses" for r in dist)
    trend_lines = "\n".join(
        f"  - {r['month']}: {r['feedback_count']} feedbacks, avg {r['avg_rating']:.2f} stars"
        for r in trend
    )
    sample_lines = "\n".join(
        f"  - [{r['program_name']}] {r['participant_name']} rated {r['rating']}★: \"{r['comments']}\""
        for r in samples
    )

    return f"""You are an analyst for FMS (Feedback Management System).
Answer questions using ONLY the data below. Be concise and specific.

=== SUMMARY ===
Total feedback records (cleaned): {total}
Overall average rating: {round(float(avg), 2) if avg else "N/A"} / 5.0
Total programs tracked: {prog_count}

=== PROGRAM PERFORMANCE ===
{prog_lines}

=== RATING DISTRIBUTION ===
{dist_lines}

=== MONTHLY TREND ===
{trend_lines}

=== SAMPLE FEEDBACK RECORDS ===
{sample_lines}
"""


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set on the server.")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    context = _build_context(db)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": req.question},
            ],
            max_tokens=512,
            temperature=0.3,
        )
        return {"answer": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")
