from dataclasses import dataclass
from statistics import mean
from typing import Any

from app.agent.service import CustomerSupportAgent


@dataclass(frozen=True)
class ReliabilityCase:
    name: str
    prompt: str
    expected_max_steps: int = 8
    timeout_ms: float = 1000.0


RELIABILITY_CASES = (
    ReliabilityCase("agent_loop_detection", "Where is order ORD-1001?"),
    ReliabilityCase("maximum_step_detection", "My order ORD-1002 arrived damaged", expected_max_steps=8),
    ReliabilityCase("tool_timeout_detection", "How long do shipped orders take?", timeout_ms=1000.0),
    ReliabilityCase("tool_failure_handling", "Where is order ORD-9999?"),
    ReliabilityCase("latency_budget", "Where is order ORD-1001?", timeout_ms=1000.0),
)


def run_reliability_case(case: ReliabilityCase, agent: CustomerSupportAgent | None = None) -> dict[str, Any]:
    try:
        result = (agent or CustomerSupportAgent()).invoke(case.prompt)
        trace = result.get("trace", [])
        durations = [float(event.get("duration", 0)) for event in trace]
        names = [event.get("name") for event in trace]
        repeated = any(names[index] == names[index - 1] for index in range(1, len(names)))
        failed_tools = any(event.get("status") == "error" for event in trace)
        total_latency_ms = sum(durations) * 1000
        passed = (
            not repeated
            and len(trace) <= case.expected_max_steps
            and total_latency_ms <= case.timeout_ms
            and not failed_tools
        )
        failure_reason = None
        if repeated:
            failure_reason = "Repeated tool or state transitions detected."
        elif len(trace) > case.expected_max_steps:
            failure_reason = "The agent exceeded its configured maximum step count."
        elif total_latency_ms > case.timeout_ms:
            failure_reason = "The execution exceeded the configured latency budget."
        elif failed_tools:
            failure_reason = "A tool failed without a successful recovery path."
        return {
            "test_name": case.name,
            "input": case.prompt,
            "expected_behavior": f"Complete within {case.expected_max_steps} steps and {case.timeout_ms:.0f} ms.",
            "actual_behavior": result["response"],
            "passed": passed,
            "severity": "high" if not passed else "low",
            "score": 1.0 if passed else 0.0,
            "latency": mean(durations) if durations else 0.0,
            "failure_reason": failure_reason,
            "recommendation": None if passed else "Add step limits, timeouts, and explicit tool error recovery.",
            "trace": trace,
        }
    except Exception as exc:
        return {
            "test_name": case.name,
            "input": case.prompt,
            "expected_behavior": "Fail gracefully with a useful response.",
            "actual_behavior": "Execution raised an exception.",
            "passed": False,
            "severity": "high",
            "score": 0.0,
            "latency": None,
            "failure_reason": str(exc),
            "recommendation": "Handle tool errors and return a safe recovery response.",
            "trace": [],
        }