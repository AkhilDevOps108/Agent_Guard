from app.agent.service import CustomerSupportAgent


def test_order_question_uses_order_and_knowledge_tools():
    result = CustomerSupportAgent().invoke("Where is order ORD-1001?")

    assert result["tool_calls"] == ["get_order", "search_knowledge", "get_customer"]
    assert "ORD-1001" in result["response"]
    assert all(event["status"] == "ok" for event in result["trace"])


def test_damaged_order_creates_ticket_and_escalates():
    result = CustomerSupportAgent().invoke("My order ORD-1002 arrived damaged")

    assert result["tool_calls"] == ["get_order", "create_ticket", "escalate_to_human"]
    assert "TICKET-" in result["response"]
    assert "human specialist" in result["response"]


def test_tool_arguments_are_validated():
    from app.agent.tools import get_order

    try:
        get_order.invoke({"order_id": "not-an-order"})
    except ValueError as exc:
        assert "Invalid order ID" in str(exc)
    else:
        raise AssertionError("Invalid order IDs must be rejected")


def test_configured_model_generates_response_and_trace_span():
    class FakeModel:
        def invoke(self, messages):
            class Response:
                content = "A model-generated support response."

            assert messages[0][0] == "system"
            return Response()

    result = CustomerSupportAgent(model=FakeModel()).invoke("Where is order ORD-1001?")

    assert result["response"] == "A model-generated support response."
    assert result["trace"][-1]["type"] == "llm"