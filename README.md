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

1. Create a virtual environment.
2. Install requirements.
3. Copy `.env.example` to `.env`.
4. Start local services with Docker Compose.
5. Run tests with pytest.

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
