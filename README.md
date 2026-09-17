# AgentGuard

AgentGuard is an AI agent evaluation, security, and reliability platform designed for portfolio use.

## Problem

AI agents can fail on safety, quality, and operational reliability. AgentGuard provides a structured way to evaluate agent behavior, inspect traces, and enforce deployment gates.

## Architecture

The backend exposes API endpoints, persists results in PostgreSQL, schedules evaluation jobs through Redis/Celery, and supports observability through Prometheus and Grafana.

## Features

- Agent registry
- Test runner and evaluation engine
- Security and reliability checks
- Trace collection and visualization
- Risk engine and deployment gating
- Docker and Kubernetes foundations

## Technology stack

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Celery
- Docker
- Prometheus
- Grafana
- OpenTelemetry

## Local setup

Phase 1 provides the FastAPI foundation, PostgreSQL schema, Redis service, and
environment-driven local configuration. Phase 2 adds a LangGraph customer
support agent with validated tools and structured execution traces. Phases 3-7
add the agent registry, persisted traces, test-run execution, security tests,
and deterministic quality evaluation. The frontend and deployment platform
remain later phases.

1. Create and activate a virtual environment:

	```bash
	python3.12 -m venv venv
	source venv/bin/activate
	```

2. Install backend dependencies:

	```bash
	pip install -r requirements.txt
	```

3. Create local configuration:

	```bash
	cp .env.example .env
	```

4. Run the tests without external services:

	```bash
	pytest -q backend
	```

5. Start the Phase 1 services:

	```bash
	docker compose up --build -d
	```

6. Apply the database migration:

	```bash
	alembic upgrade head
	```

7. Verify the API:

	```bash
	curl http://localhost:8000/health
	curl http://localhost:8000/
	```

8. Stop the services when finished:

	```bash
	docker compose down
	```

The initial migration creates the `agents`, `test_runs`,
`evaluation_results`, and `trace_records` tables. Set `DATABASE_URL` in `.env`
to use a different PostgreSQL instance. The Phase 2 agent works without an API
key using deterministic local support data. Set `OPENAI_API_KEY`,
`OPENAI_BASE_URL`, and `OPENAI_MODEL` to enable an OpenAI-compatible response
model when needed.

### Phase 2 agent demo

Start the API, then run:

```bash
curl -X POST http://localhost:8000/api/v1/agent/invoke \
	-H 'Content-Type: application/json' \
	-d '{"message":"My order ORD-1002 arrived damaged"}'
```

The damaged-order flow calls `get_order`, `create_ticket`, and
`escalate_to_human`. Every tool span includes arguments, output, timing, and
status so later AgentGuard trace collection can persist it.

### Phases 3-7 API

Register an agent before creating a test run:

```bash
curl -X POST http://localhost:8000/api/v1/agents \
	-H 'Content-Type: application/json' \
	-d '{"name":"Customer Support Agent","description":"Phase 2 demo agent"}'
```

The registry endpoints are:

```text
POST  /api/v1/agents
GET   /api/v1/agents
GET   /api/v1/agents/{id}
PATCH /api/v1/agents/{id}
```

Test runs support `security` and `quality` categories. They are queued through
Celery when Redis is available and fall back to the local FastAPI background
runner for development:

```bash
curl -X POST http://localhost:8000/api/v1/test-runs \
	-H 'Content-Type: application/json' \
	-d '{"agent_id":"AGENT_ID","categories":["security","quality"]}'
```

Inspect a run with:

```text
GET /api/v1/test-runs/{id}
GET /api/v1/test-runs/{id}/results
GET /api/v1/test-runs/{id}/traces
GET /api/v1/evaluations/{id}
```

For production-style asynchronous execution, run a worker alongside Redis:

```bash
celery -A app.worker.celery_app worker --loglevel=info
```

The security engine currently covers prompt injection, system-prompt leakage,
tool abuse, sensitive-data exposure, and indirect prompt injection. The
quality engine currently checks answer relevance and groundedness against
approved local context. These are internal evaluation heuristics, not
industry-standard scores; DeepEval and Ragas adapters are planned for a later
quality expansion.

### Phases 8-11: reliability, risk, and console

Reliability runs cover loop detection, maximum steps, tool failure handling,
and latency budgets. The configurable risk policy returns `PASS`, `WARNING`,
or `BLOCKED` from:

```text
GET /api/v1/test-runs/{id}/risk
GET /api/v1/dashboard/summary
```

Policy thresholds are configured with `RISK_*` environment variables. The
dashboard is a Next.js application in `frontend/`; it reads the summary and
trace endpoints and does not contain fake evaluation metrics.

Run it locally with:

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000`. The same frontend is included in Docker
Compose and serves on port 3000.

## Example agent

Customer support agent with tools for knowledge lookup, customer memory, order retrieval, ticket creation, and human escalation.

## Example security attack

Prompt injection attempts that instruct the agent to ignore rules, reveal hidden instructions, or execute unauthorized tools.

## Evaluation results

Metrics are generated from backend test runs and persisted.

## CI/CD architecture

GitHub Actions runs tests, executes evaluation jobs, applies the risk gate, and fails deployment when policy is violated.

## Kubernetes architecture

The project includes a Kubernetes manifests structure for the API, worker, frontend, Postgres, Redis, and observability tools.

## AWS architecture

Terraform modules are structured for VPC, EKS, RDS, ElastiCache, ECR, IAM, and S3.

## Screenshots placeholders

- Dashboard screenshot
- Agent detail view
- Trace viewer
- Security results table

## Future roadmap

- Full frontend dashboard
- DeepEval and Ragas integration
- Kubernetes manifests and Helm values
- AWS Terraform deployment automation
