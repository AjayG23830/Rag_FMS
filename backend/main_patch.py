"""
PHASE 2 WIRE-UP — How to add the analytics router to your Phase 1 main.py

Open backend/main.py from your Phase 1 project and add these 2 lines:

    from routers import analytics
    app.include_router(analytics.router)

That's it. The analytics router auto-creates the analytics_* tables on first
ETL run, so no migration needed.

If your routers/ folder doesn't have an __init__.py, create an empty one.
"""
