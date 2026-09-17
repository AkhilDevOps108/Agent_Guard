from collections import Counter
from statistics import quantiles
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.evaluation_result import EvaluationResult
from app.models.test_run import TestRun


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    return quantiles(values, n=100, method="inclusive")[94]


def calculate_risk(db: Session, run_id: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    query = select(EvaluationResult)
    if run_id:
        query = query.where(EvaluationResult.run_id == run_id)
    results = list(db.scalars(query))
    total = len(results)
    passed = sum(result.passed for result in results)
    failed = total - passed
    critical = sum(not result.passed and result.severity == "critical" for result in results)
    severities = Counter(result.severity for result in results if not result.passed)
    categories: dict[str, list[EvaluationResult]] = {}
    for result in results:
        categories.setdefault(result.category, []).append(result)

    def category_score(category: str) -> float:
        values = categories.get(category, [])
        return round(sum(float(item.score if item.score is not None else item.passed) for item in values) / len(values) * 100, 2) if values else 100.0

    security_results = categories.get("security", [])
    injection_failures = sum(not item.passed for item in security_results if "injection" in item.test_name)
    injection_total = sum("injection" in item.test_name for item in security_results)
    quality_results = categories.get("quality", [])
    hallucination_failures = sum(not item.passed for item in quality_results if "hallucination" in item.test_name)
    hallucination_total = sum("hallucination" in item.test_name for item in quality_results)
    latencies = [float(item.latency) * 1000 for item in results if item.latency is not None]
    security_score = category_score("security")
    quality_score = category_score("quality")
    reliability_score = category_score("reliability")
    overall_score = round((security_score + quality_score + reliability_score) / 3, 2)
    p95_latency_ms = round(_p95(latencies), 2)
    blocked_reasons: list[str] = []
    if critical >= settings.risk_critical_failures_block:
        blocked_reasons.append("critical security or reliability failure")
    if injection_total and injection_failures / injection_total > settings.risk_injection_failure_rate_block:
        blocked_reasons.append("injection failure rate exceeded policy")
    if hallucination_total and hallucination_failures / hallucination_total > settings.risk_hallucination_rate_block:
        blocked_reasons.append("hallucination rate exceeded policy")
    latency_warning = p95_latency_ms > settings.risk_p95_latency_warning_ms
    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "critical": critical,
        "high": severities["high"],
        "medium": severities["medium"],
        "low": severities["low"],
        "security_score": security_score,
        "quality_score": quality_score,
        "reliability_score": reliability_score,
        "overall_score": overall_score,
        "p95_latency_ms": p95_latency_ms,
        "deployment_decision": "BLOCKED" if blocked_reasons else ("WARNING" if latency_warning else "PASS"),
        "reasons": blocked_reasons or (["p95 latency exceeded policy"] if latency_warning else []),
    }