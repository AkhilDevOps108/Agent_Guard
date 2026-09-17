'use client';

import { useEffect, useState } from 'react';
import { Activity, ShieldCheck, Gauge, GitBranch, ArrowUpRight } from 'lucide-react';

type Summary = {
  agents: number; test_runs: number; evaluations: number; pass_rate: number;
  critical_failures: number; security_score: number; quality_score: number;
  reliability_score: number; overall_score: number; deployment_decision: string;
  recent_runs: { id: string; agent_id: string; status: string; score: number | null }[];
};
type Trace = { id: string; status: string; duration: number | null; payload: { spans?: Record<string, unknown>[] } | null };

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

function Metric({ label, value, tone = '' }: { label: string; value: string | number; tone?: string }) {
  return <div className="metric"><div className="metric-label">{label}</div><div className={`metric-value ${tone}`}>{value}</div></div>;
}

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [traces, setTraces] = useState<Trace[]>([]);
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${API}/api/v1/dashboard/summary`).then((response) => {
      if (!response.ok) throw new Error('Dashboard API unavailable');
      return response.json();
    }).then(setSummary).catch((reason: Error) => setError(reason.message));
  }, []);

  async function showTrace(runId: string) {
    setSelectedRun(runId);
    const response = await fetch(`${API}/api/v1/test-runs/${runId}/traces`);
    if (response.ok) setTraces(await response.json());
  }

  return <div className="console">
    <aside className="sidebar">
      <div className="brand">AGENT<span>GUARD</span></div>
      <div className="eyebrow">Control room</div>
      <nav className="nav"><button className="active">Overview</button><button>Agents</button><button>Test runs</button><button>Policy</button></nav>
      <div className="sidebar-note">Evaluation data is read from the AgentGuard API. Scores are configurable internal risk signals.</div>
    </aside>
    <main className="main">
      <header className="header"><div><div className="kicker">Platform telemetry / live</div><h1>Deployment confidence.</h1></div><div className="status"><span className="dot" /> API connected</div></header>
      {error && <div className="error">{error}. Start the FastAPI backend to load live data.</div>}
      {summary && <>
        <section className="metrics">
          <Metric label="Registered agents" value={summary.agents} />
          <Metric label="Evaluation runs" value={summary.test_runs} />
          <Metric label="Pass rate" value={`${summary.pass_rate}%`} tone="teal" />
          <Metric label="Critical failures" value={summary.critical_failures} tone="coral" />
        </section>
        <section className="grid">
          <div className="panel"><h2>Risk signal by domain</h2>
            {([['Security', summary.security_score], ['Quality', summary.quality_score], ['Reliability', summary.reliability_score]] as [string, number][]).map(([label, score]) => <div className="score-row" key={label}><div><div>{label}</div><div className="bar"><div style={{ width: `${score}%` }} /></div></div><div className="score">{score}</div></div>)}
          </div>
          <div className={`gate ${summary.deployment_decision.toLowerCase()}`}><div className="kicker">Deployment gate</div><strong>{summary.deployment_decision}</strong><p>Overall internal risk score: <span className="mono">{summary.overall_score}</span></p></div>
        </section>
        <section className="panel" style={{ marginTop: 18 }}><h2>Recent test runs</h2><div className="run-list">{summary.recent_runs.length ? summary.recent_runs.map((run) => <div className="run" key={run.id}><div><div className="mono">{run.id.slice(0, 8)}...</div><div className="trace-detail">Agent {run.agent_id.slice(0, 8)} · {run.status}</div></div><span>{run.score ?? '—'}</span><button onClick={() => showTrace(run.id)}>Trace <ArrowUpRight size={13} /></button></div>) : <div className="trace-detail">No persisted runs yet.</div>}</div></section>
        {selectedRun && <section className="panel trace"><h2>Execution trace <span className="trace-detail mono">{selectedRun}</span></h2>{traces.flatMap((record) => (record.payload?.spans ?? []).map((span, index) => <div className="trace-event" key={`${record.id}-${index}`}><div className="trace-type">{String(span.type ?? 'span')}</div><div><div className="trace-name">{String(span.name ?? span.component ?? 'event')}</div><div className="trace-detail">{String(span.status ?? 'unknown')} · {String(span.duration ?? 0)}s</div></div><div className="mono">{record.status}</div></div>))}</section>}
      </>}
      {!summary && !error && <div className="panel">Loading live platform data...</div>}
    </main>
  </div>;
}
