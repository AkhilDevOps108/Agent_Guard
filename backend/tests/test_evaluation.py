from app.agent.service import CustomerSupportAgent
from app.evaluation.quality import QUALITY_CASES, run_quality_case
from app.evaluation.security import SECURITY_CASES, run_security_case


def test_security_engine_rejects_unauthorized_tool_requests():
    result = run_security_case(SECURITY_CASES[2], CustomerSupportAgent())

    assert result["passed"] is True
    assert not {"create_ticket", "escalate_to_human", "get_customer", "get_order"}.intersection(
        event["name"] for event in result["trace"]
    )


def test_quality_engine_scores_grounded_order_answer():
    result = run_quality_case(QUALITY_CASES[0], CustomerSupportAgent())

    assert result["passed"] is True
    assert result["score"] == 1.0