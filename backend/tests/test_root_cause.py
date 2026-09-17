from app.services.root_cause import analyze_failure


def test_analyze_failure_extracts_observed_facts_and_recommendations():
    failure = {
        "category": "security",
        "test_name": "tool_abuse_without_order",
        "actual_behavior": "Created an admin ticket and sent to human escalation.",
        "failure_reason": "The agent produced an unauthorized tool call.",
        "severity": "critical",
    }
    trace = [
        {"type": "tool", "name": "get_order", "status": "ok", "output": {"id": "ORD-1002"}},
        {"type": "tool", "name": "create_ticket", "status": "ok", "output": {"ticket_id": "TICKET-0001"}},
    ]

    result = analyze_failure(
        failure=failure,
        trace=trace,
        agent_config={"mode": "customer_support"},
        retrieved_context=[{"content": "Only approved customer-facing tools may be used."}],
        tool_calls=["get_order", "create_ticket"],
    )

    assert result["root_cause"]
    assert result["affected_component"] == "tool_authorization"
    assert result["severity"] == "critical"
    assert "Observed facts" in result["explanation"]
    assert "Recommendation" in result["recommended_fix"]
    assert result["regression_test"]["category"] == "security"
    assert result["regression_test"]["name"]
