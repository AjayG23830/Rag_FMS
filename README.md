# FMS Phase 2 — ETL Pipeline & Analytics Dashboard

Extension to Phase 1 Feedback Management System adding **ETL-based feedback analytics**.

---

## 📦 Phase 2 Deliverables (this folder)

```
FMS/
├── etl/
│   ├── generate_dataset.py   # creates 150+ sample records (CSV)
│   ├── extract.py            # EXTRACT — read CSV/Excel into DataFrame
│   ├── transform.py          # TRANSFORM — clean & aggregate with Pandas
│   ├── load.py               # LOAD — write to analytics_* tables in SQLite
│   └── run_etl.py            # Orchestrator (runs E→T→L)
├── datasets/
│   └── feedback_raw.csv      # 155 sample feedback records
├── backend/
│   ├── routers/analytics.py  # NEW: /analytics/* endpoints
│   └── main_patch.py         # 2-line snippet to wire it into main.py
└── frontend/
    └── src/pages/Analytics.js # NEW: dashboard with bar/line charts
```

---

## 🔄 ETL Workflow

**Source dataset:** `datasets/feedback_raw.csv` — 155 feedback records intentionally containing:
- Invalid ratings (0, 7) — outside the 1–5 range
- Whitespace-padded names
- All-caps comments (noise)
- 5 exact duplicate rows

### EXTRACT (`etl/extract.py`)
Reads CSV or Excel via pandas. Returns a raw DataFrame with all rows.

### TRANSFORM (`etl/transform.py`)
1. Strips whitespace from all text columns
2. Normalizes ALL-CAPS comments to sentence case
3. Drops rows where rating ∉ {1, 2, 3, 4, 5}
4. Parses `submitted_at` and drops rows that fail to parse
5. Removes exact duplicates
6. Builds 3 aggregate DataFrames:
   - `program_stats` — feedback count, avg/min/max rating per program
   - `rating_distribution` — count per 1–5 star
   - `monthly_trend` — monthly feedback count + avg rating

### LOAD (`etl/load.py`)
Writes to SQLite tables in `backend/feedback.db`:
- `analytics_feedback_clean` — cleaned record-level data
- `analytics_program_stats`
- `analytics_rating_distribution`
- `analytics_monthly_trend`
- `etl_runs` — audit log of each ETL run

Each run **truncates and replaces** the analytics tables (idempotent).

---

## 🚀 How to Run

### 1. Install Pandas
```bash
cd backend
pip install pandas openpyxl
```

### 2. Wire up the analytics router
Open `backend/main.py` (from Phase 1) and add:
```python
from routers import analytics
app.include_router(analytics.router)
```

### 3. Run the ETL
```bash
cd etl
python generate_dataset.py    # only if you need to regenerate the CSV
python run_etl.py             # runs full pipeline
```
Expected output:
```
[EXTRACT] Loaded 155 raw rows
[TRANSFORM] Cleaned: 155 → 147 rows (8 dropped)
[LOAD] 147 cleaned rows + aggregates written
 ETL COMPLETED SUCCESSFULLY ✅
```

### 4. View the dashboard
- Start backend: `uvicorn main:app --reload --port 8000`
- Start frontend: `npm start`
- Add to App.js:
  ```jsx
  import Analytics from "./pages/Analytics";
  <Route path="/analytics" element={<Analytics />} />
  ```
- Add to navbar: `<NavLink to="/analytics">Analytics</NavLink>`
- Visit http://localhost:3000/analytics

### 5. Trigger ETL from UI
The dashboard has a **🔄 Run ETL Pipeline** button that triggers the same script via `POST /analytics/run-etl`.

---

## 📊 Analytics Features
- KPI cards: clean records, avg rating, total programs, last ETL run timestamp
- Bar chart: feedback count by program (with avg rating)
- Bar chart: rating distribution 1★ → 5★ (with %)
- Line chart: monthly feedback volume trend

---

## 📚 API Endpoints (Phase 2)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /analytics/summary | KPI summary |
| GET | /analytics/program-stats | Per-program stats |
| GET | /analytics/rating-distribution | Rating histogram |
| GET | /analytics/monthly-trend | Monthly volume + rating |
| POST | /analytics/run-etl | Trigger ETL from UI |

---

## ✅ Phase 2 Checklist
- [x] Python ETL scripts using Pandas ✓
- [x] CSV dataset (`datasets/feedback_raw.csv`) ✓
- [x] Extract / Transform / Load stages clearly separated ✓
- [x] Cleaned data in analytics tables ✓
- [x] Frontend dashboard with charts ✓
- [x] Daily GitHub commits — _your responsibility_
- [x] datasets/ folder included ✓
- [x] README with ETL workflow explanation ✓
- [ ] Submit screenshots of ETL run + dashboard

Repo naming: `AFDE_Jan26_<YourName>_FMS`
