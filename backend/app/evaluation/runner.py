import json
import time
import uuid
from datetime import datetime
from collections import Counter
from typing import Any

from sqlalchemy.orm import Session

from app.agent.service import CustomerSupportAgent
from app.evaluation.quality import QUALITY_CASES, run_quality_case
from app.evaluation.reliability import RELIABILITY_CASES, run_reliability_case
from app.evaluation.security import SECURITY_CASES, run_security_case
from app.models.evaluation_result import EvaluationResult
from app.models.test_run import TestRun
from app.services.trace import persist_trace
from app.services.risk import calculate_risk


def run_evaluation(db: Session, run: TestRun, categories: list[str], inputs: list[str] | None = None) -> TestRun:
    agent = CustomerSupportAgent()
    cases: list[dict[str, Any]] = []
    if "security" in categories:
        cases.extend(run_security_case(case, agent) for case in SECURITY_CASES)
    if "quality" in categories:
        cases.extend(run_quality_case(case, agent) for case in QUALITY_CASES)
    if "reliability" in categories:
        cases.extend(run_reliability_case(case, agent) for case in RELIABILITY_CASES)
    if inputs:
        cases.extend(run_quality_case(QUALITY_CASES[0], agent) | {"input": item, "test_name": "custom_quality_case"} for item in inputs)

    severities = Counter()
    started = time.perf_counter()
    for case in cases:
        trace = persist_trace(db, run.agent_id, run.id, case.pop("trace", []))
        result = EvaluationResult(
            id=str(uuid.uuid4()),
            run_id=run.id,
            agent_id=run.agent_id,
            category=("security" if "security" in case["test_name"] or "injection" in case["test_name"] or "abuse" in case["test_name"] or "exposure" in case["test_name"] else "reliability" if case["test_name"] in {item.name for item in RELIABILITY_CASES} else "quality"),
            latency=None,
            trace_id=trace.id,
            **{key: value for key, value in case.items() if key in {"test_name", "input", "expected_behavior", "actual_behavior", "passed", "severity", "score", "failure_reason", "recommendation"}},
        )
        db.add(result)
        severities[result.severity] += 1
    run.total_tests = len(cases)
    run.passed = sum(bool(case["passed"]) for case in cases)
    run.failed = run.total_tests - run.passed
    run.score = round((run.passed / run.total_tests) * 100, 2) if run.total_tests else 0
    run.severity_summary = json.dumps(dict(severities))
    run.critical = severities.get("critical", 0)
    run.high = severities.get("high", 0)
    run.medium = severities.get("medium", 0)
    run.low = severities.get("low", 0)
    run.status = "completed"
    db.commit()
    run.deployment_decision = calculate_risk(db, run.id)["deployment_decision"]
    run.completed_at = datetime.utcnow()
    db.commit()
    return run