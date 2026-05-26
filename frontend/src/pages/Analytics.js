/**
 * FMS Phase 2 — Analytics Page
 * Reads /analytics/* endpoints and renders charts using simple SVG bars
 * (no extra dependency needed). Drop this file into:
 *     frontend/src/pages/Analytics.js
 *
 * Then in App.js:
 *   import Analytics from "./pages/Analytics";
 *   <Route path="/analytics" element={<Analytics />} />
 *
 * And add <NavLink to="/analytics">Analytics</NavLink> to the navbar.
 */
import React, { useEffect, useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "https://rag-fms.onrender.com";

function Bar({ label, value, max, color = "#2563eb", suffix = "" }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div style={{ marginBottom: "0.6rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.2rem" }}>
        <span style={{ fontWeight: 600 }}>{label}</span>
        <span style={{ color: "#64748b" }}>{value}{suffix}</span>
      </div>
      <div style={{ height: 14, background: "#f1f5f9", borderRadius: 8, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", background: color, transition: "width 0.4s" }} />
      </div>
    </div>
  );
}

function LineChart({ data, height = 200 }) {
  if (!data.length) return <p style={{ color: "#94a3b8" }}>No data</p>;
  const max = Math.max(...data.map(d => d.feedback_count));
  const W = Math.max(data.length * 60, 400);
  const H = height;
  const pad = 35;
  const points = data.map((d, i) => {
    const x = pad + (i * (W - 2 * pad)) / Math.max(data.length - 1, 1);
    const y = H - pad - ((d.feedback_count / max) * (H - 2 * pad));
    return { x, y, ...d };
  });
  const pathD = points.map((p, i) => (i === 0 ? "M" : "L") + p.x + " " + p.y).join(" ");
  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={W} height={H} style={{ display: "block" }}>
        <line x1={pad} y1={H - pad} x2={W - pad} y2={H - pad} stroke="#cbd5e1" />
        <line x1={pad} y1={pad} x2={pad} y2={H - pad} stroke="#cbd5e1" />
        <path d={pathD} fill="none" stroke="#2563eb" strokeWidth="2" />
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r="4" fill="#2563eb" />
            <text x={p.x} y={H - pad + 15} textAnchor="middle" fontSize="10" fill="#64748b">{p.month}</text>
            <text x={p.x} y={p.y - 8} textAnchor="middle" fontSize="10" fill="#1e293b" fontWeight="600">{p.feedback_count}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

function Analytics() {
  const [summary, setSummary] = useState(null);
  const [programs, setPrograms] = useState([]);
  const [dist, setDist] = useState([]);
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [s, p, d, t] = await Promise.all([
        axios.get(`${API}/analytics/summary`),
        axios.get(`${API}/analytics/program-stats`),
        axios.get(`${API}/analytics/rating-distribution`),
        axios.get(`${API}/analytics/monthly-trend`),
      ]);
      setSummary(s.data);
      setPrograms(p.data);
      setDist(d.data);
      setTrend(t.data);
    } catch {
      setMsg({ type: "error", text: "Failed to load analytics. Run the ETL first." });
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const triggerETL = async () => {
    setRunning(true); setMsg({ type: "", text: "" });
    try {
      await axios.post(`${API}/analytics/run-etl`);
      setMsg({ type: "success", text: "ETL completed successfully! Refreshing data..." });
      await load();
    } catch (err) {
      setMsg({ type: "error", text: err.response?.data?.detail || "ETL failed" });
    } finally { setRunning(false); }
  };

  const askChat = async () => {
    const q = chatInput.trim();
    if (!q) return;
    setChatInput("");
    setChatHistory(h => [...h, { role: "user", text: q }]);
    setChatLoading(true);
    try {
      const res = await axios.post(`${API}/analytics/chat`, { question: q });
      setChatHistory(h => [...h, { role: "ai", text: res.data.answer }]);
    } catch (err) {
      setChatHistory(h => [...h, { role: "ai", text: "Error: " + (err.response?.data?.detail || "Could not reach AI.") }]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) return <div className="loading">⏳ Loading analytics...</div>;

  const maxProgCount = Math.max(...programs.map(p => p.feedback_count), 1);
  const maxDist = Math.max(...dist.map(d => d.count), 1);
  const totalDist = dist.reduce((s, d) => s + d.count, 0) || 1;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700 }}>📈 Feedback Analytics</h1>
          <p style={{ color: "#64748b", fontSize: "0.9rem" }}>ETL-powered insights from cleaned feedback data</p>
        </div>
        <button className="btn btn-primary" onClick={triggerETL} disabled={running}>
          {running ? "⏳ Running ETL..." : "🔄 Run ETL Pipeline"}
        </button>
      </div>

      {msg.text && <div className={`alert alert-${msg.type === "error" ? "error" : "success"}`}>{msg.text}</div>}

      {summary && (
        <div className="stats-grid" style={{ marginBottom: "1.5rem" }}>
          <div className="stat-card"><div className="stat-icon">📊</div><div className="stat-value">{summary.total_clean_records}</div><div className="stat-label">Clean Records</div></div>
          <div className="stat-card"><div className="stat-icon">⭐</div><div className="stat-value">{summary.overall_avg_rating}</div><div className="stat-label">Avg Rating</div></div>
          <div className="stat-card"><div className="stat-icon">🎯</div><div className="stat-value">{summary.total_programs}</div><div className="stat-label">Programs</div></div>
          <div className="stat-card"><div className="stat-icon">🕒</div><div style={{ fontSize: "0.85rem", marginTop: "0.4rem", color: "#475569" }}>{summary.last_etl_run ? new Date(summary.last_etl_run.run_at).toLocaleString("en-IN") : "Never"}</div><div className="stat-label">Last ETL Run</div></div>
        </div>
      )}

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📚 Feedback Count by Program</h3>
        {programs.length === 0 ? <p style={{ color: "#94a3b8" }}>No data yet.</p> : programs.map(p => (
          <Bar key={p.program_name} label={`${p.program_name} (avg ⭐ ${p.avg_rating})`} value={p.feedback_count} max={maxProgCount} />
        ))}
      </div>

      <div className="card" style={{ marginBottom: "1rem" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>⭐ Rating Distribution</h3>
        {dist.map(d => (
          <Bar key={d.rating} label={`${"★".repeat(d.rating)}${"☆".repeat(5 - d.rating)} (${d.rating})`} value={d.count} max={maxDist}
            color={d.rating >= 4 ? "#16a34a" : d.rating === 3 ? "#d97706" : "#dc2626"}
            suffix={` (${Math.round(d.count / totalDist * 100)}%)`} />
        ))}
      </div>

      <div className="card">
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "1rem" }}>📅 Monthly Feedback Trend</h3>
        <LineChart data={trend} />
      </div>

      <div className="card" style={{ marginTop: "1rem" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "0.5rem" }}>🤖 Ask AI about your Feedback Data</h3>
        <p style={{ color: "#64748b", fontSize: "0.85rem", marginBottom: "1rem" }}>
          Ask questions like "Which program has the lowest rating?" or "How many 5-star reviews did we get?"
        </p>

        <div style={{ maxHeight: 320, overflowY: "auto", marginBottom: "0.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {chatHistory.length === 0 && (
            <p style={{ color: "#94a3b8", fontSize: "0.85rem", textAlign: "center", padding: "1rem 0" }}>No messages yet. Ask something above!</p>
          )}
          {chatHistory.map((m, i) => (
            <div key={i} style={{
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? "#2563eb" : "#f1f5f9",
              color: m.role === "user" ? "#fff" : "#1e293b",
              borderRadius: 12,
              padding: "0.5rem 0.85rem",
              maxWidth: "80%",
              fontSize: "0.875rem",
              whiteSpace: "pre-wrap",
            }}>
              {m.text}
            </div>
          ))}
          {chatLoading && (
            <div style={{ alignSelf: "flex-start", color: "#94a3b8", fontSize: "0.85rem", padding: "0.5rem 0" }}>⏳ Thinking...</div>
          )}
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <input
            type="text"
            value={chatInput}
            onChange={e => setChatInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !chatLoading && askChat()}
            placeholder="Ask a question about the feedback data..."
            disabled={chatLoading}
            style={{
              flex: 1, padding: "0.5rem 0.75rem", borderRadius: 8,
              border: "1px solid #cbd5e1", fontSize: "0.875rem", outline: "none",
            }}
          />
          <button className="btn btn-primary" onClick={askChat} disabled={chatLoading || !chatInput.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
