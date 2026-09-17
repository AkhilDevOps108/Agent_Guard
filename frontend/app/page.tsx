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
type AgentRecord = { id: string; name: string; description: string | null; version: string; status: string };
type TestRunRecord = { id: string; agent_id: string; status: string; total_tests: number; passed: number; failed: number; score: number | null };
type Policy = { risk_critical_failures_block: number; risk_injection_failure_rate_block: number; risk_hallucination_rate_block: number; risk_p95_latency_warning_ms: number };
type Tab = 'overview' | 'agents' | 'test-runs' | 'policy';

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

function Metric({ label, value, tone = '' }: { label: string; value: string | number; tone?: string }) {
  return <div className="metric"><div className="metric-label">{label}</div><div className={`metric-value ${tone}`}>{value}</div></div>;
}

export default function Dashboard() {
  const [tab, setTab] = useState<Tab>('overview');
  const [summary, setSummary] = useState<Summary | null>(null);
  const [agents, setAgents] = useState<AgentRecord[] | null>(null);
  const [testRuns, setTestRuns] = useState<TestRunRecord[] | null>(null);
  const [policy, setPolicy] = useState<Policy | null>(null);
  const [traces, setTraces] = useState<Trace[]>([]);
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${API}/api/v1/dashboard/summary`).then((response) => {
      if (!response.ok) throw new Error('Dashboard API unavailable');
      return response.json();
    }).then(setSummary).catch((reason: Error) => setError(reason.message));
  }, []);

  useEffect(() => {
    if (tab === 'agents' && agents === null) {
      fetch(`${API}/api/v1/agents`).then((response) => (response.ok ? response.json() : [])).then(setAgents).catch(() => setAgents([]));
    }
    if (tab === 'test-runs' && testRuns === null) {
      fetch(`${API}/api/v1/test-runs`).then((response) => (response.ok ? response.json() : [])).then(setTestRuns).catch(() => setTestRuns([]));
    }
    if (tab === 'policy' && policy === null) {
      fetch(`${API}/api/v1/dashboard/policy`).then((response) => (response.ok ? response.json() : null)).then(setPolicy).catch(() => setPolicy(null));
    }
  }, [tab, agents, testRuns, policy]);

  async function showTrace(runId: string) {
    setSelectedRun(runId);
    const response = await fetch(`${API}/api/v1/test-runs/${runId}/traces`);
    if (response.ok) setTraces(await response.json());
  }

  return <div className="console">
    <aside className="sidebar">
      <div className="brand">AGENT<span>GUARD</span></div>
      <div className="eyebrow">Control room</div>
      <nav className="nav">
        <button className={tab === 'overview' ? 'active' : ''} onClick={() => setTab('overview')}>Overview</button>
        <button className={tab === 'agents' ? 'active' : ''} onClick={() => setTab('agents')}>Agents</button>
        <button className={tab === 'test-runs' ? 'active' : ''} onClick={() => setTab('test-runs')}>Test runs</button>
        <button className={tab === 'policy' ? 'active' : ''} onClick={() => setTab('policy')}>Policy</button>
      </nav>
      <div className="sidebar-note">Evaluation data is read from the AgentGuard API. Scores are configurable internal risk signals.</div>
    </aside>
    <main className="main">
      <header className="header"><div><div className="kicker">Platform telemetry / live</div><h1>Deployment confidence.</h1></div><div className="status"><span className="dot" /> API connected</div></header>
      {error && <div className="error">{error}. Start the FastAPI backend to load live data.</div>}

      {tab === 'overview' && summary && <>
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
      {tab === 'overview' && !summary && !error && <div className="panel">Loading live platform data...</div>}

      {tab === 'agents' && <section className="panel"><h2>Registered agents</h2>
        {agents === null && <div className="trace-detail">Loading agents...</div>}
        {agents !== null && agents.length === 0 && <div className="trace-detail">No agents registered yet. POST to /api/v1/agents to add one.</div>}
        {agents !== null && agents.length > 0 && <div className="run-list">{agents.map((agent) => <div className="run" key={agent.id}><div><div>{agent.name}</div><div className="trace-detail">{agent.description ?? 'No description'} · v{agent.version}</div></div><span>{agent.status}</span><span className="mono">{agent.id.slice(0, 8)}</span></div>)}</div>}
      </section>}

      {tab === 'test-runs' && <section className="panel"><h2>All test runs</h2>
        {testRuns === null && <div className="trace-detail">Loading test runs...</div>}
        {testRuns !== null && testRuns.length === 0 && <div className="trace-detail">No test runs yet. POST to /api/v1/test-runs to start one.</div>}
        {testRuns !== null && testRuns.length > 0 && <div className="run-list">{testRuns.map((run) => <div className="run" key={run.id}><div><div className="mono">{run.id.slice(0, 8)}...</div><div className="trace-detail">Agent {run.agent_id.slice(0, 8)} · {run.status} · {run.passed}/{run.total_tests} passed</div></div><span>{run.score ?? '—'}</span><button onClick={() => { setTab('overview'); showTrace(run.id); }}>Trace <ArrowUpRight size={13} /></button></div>)}</div>}
      </section>}

      {tab === 'policy' && <section className="panel"><h2>Risk gate policy</h2>
        {policy === null && <div className="trace-detail">Loading policy...</div>}
        {policy && <div className="run-list">
          <div className="run"><div>Critical failures block threshold</div><span className="mono">{policy.risk_critical_failures_block}</span></div>
          <div className="run"><div>Injection failure rate block threshold</div><span className="mono">{policy.risk_injection_failure_rate_block}</span></div>
          <div className="run"><div>Hallucination rate block threshold</div><span className="mono">{policy.risk_hallucination_rate_block}</span></div>
          <div className="run"><div>P95 latency warning threshold (ms)</div><span className="mono">{policy.risk_p95_latency_warning_ms}</span></div>
        </div>}
        <div className="trace-detail" style={{ marginTop: 14 }}>Configured via RISK_* environment variables in the backend.</div>
      </section>}
    </main>
  </div>;
}

