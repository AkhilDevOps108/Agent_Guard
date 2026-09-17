from app.agent.service import CustomerSupportAgent
from app.evaluation.reliability import RELIABILITY_CASES, run_reliability_case


def test_reliability_engine_measures_tool_execution():
    result = run_reliability_case(RELIABILITY_CASES[0], CustomerSupportAgent())

    assert result["passed"] is True
    assert result["latency"] is not None