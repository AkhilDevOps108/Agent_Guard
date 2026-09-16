from __future__ import annotations

import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agent.tools import TOOL_REGISTRY


class TraceEvent(TypedDict, total=False):
    span_id: str
    type: str
    component: str
    name: str
    start_time: str
    end_time: str
    duration: float
    input: dict[str, Any]
    output: Any
    status: str
    error: str


class AgentState(TypedDict, total=False):
    message: str
    customer_id: str | None
    order_id: str | None
    intent: str
    damaged: bool
    order: dict[str, Any] | None
    customer: dict[str, str] | None
    knowledge: list[dict[str, str]]
    ticket: dict[str, str] | None
    escalation: dict[str, str] | None
    response: str
    trace: list[TraceEvent]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _invoke_tool(state: AgentState, name: str, arguments: dict[str, Any]) -> Any:
    started = time.perf_counter()
    event: TraceEvent = {
        "span_id": str(uuid.uuid4()),
        "type": "tool",
        "component": "customer_support_agent",
        "name": name,
        "start_time": _now(),
        "input": arguments,
        "status": "ok",
    }
    try:
        result = TOOL_REGISTRY[name].invoke(arguments)
        event["output"] = result
        return result
    except (ValueError, KeyError) as exc:
        event["status"] = "error"
        event["error"] = str(exc)
        raise
    finally:
        event["end_time"] = _now()
        event["duration"] = round(time.perf_counter() - started, 6)
        state.setdefault("trace", []).append(event)


def classify_request(state: AgentState) -> AgentState:
    message = state["message"]
    lowered = message.lower()
    order_match = re.search(r"ORD-[0-9]{4,}", message, re.IGNORECASE)
    customer_match = re.search(r"CUS-[0-9]{4,}", message, re.IGNORECASE)
    state["order_id"] = order_match.group(0).upper() if order_match else None
    state["customer_id"] = customer_match.group(0).upper() if customer_match else state.get("customer_id")
    state["damaged"] = any(word in lowered for word in ("damaged", "broken", "defective"))
    state["intent"] = "order" if state["order_id"] else "knowledge"
    return state


def load_order(state: AgentState) -> AgentState:
    order_id = state["order_id"]
    assert order_id is not None
    state["order"] = _invoke_tool(state, "get_order", {"order_id": order_id})
    state["customer_id"] = state.get("customer_id") or state["order"]["customer_id"]
    return state


def load_customer(state: AgentState) -> AgentState:
    customer_id = state.get("customer_id")
    if customer_id:
        state["customer"] = _invoke_tool(state, "get_customer", {"customer_id": customer_id})
    return state


def search_support_knowledge(state: AgentState) -> AgentState:
    state["knowledge"] = _invoke_tool(state, "search_knowledge", {"query": state["message"]})
    return state


def create_damage_ticket(state: AgentState) -> AgentState:
    state["ticket"] = _invoke_tool(
        state,
        "create_ticket",
        {
            "order_id": state["order_id"],
            "customer_id": state["customer_id"],
            "issue": state["message"],
        },
    )
    return state


def escalate_damage(state: AgentState) -> AgentState:
    state["escalation"] = _invoke_tool(
        state,
        "escalate_to_human",
        {
            "reason": "Damaged order requires human follow-up",
            "order_id": state["order_id"],
            "customer_id": state["customer_id"],
        },
    )
    return state


def compose_response(state: AgentState) -> AgentState:
    if state.get("ticket") and state.get("escalation"):
        state["response"] = (
            f"I’m sorry your order {state['order_id']} arrived damaged. "
            f"I opened ticket {state['ticket']['ticket_id']} and escalated it to a human specialist."
        )
    elif state.get("order"):
        order = state["order"]
        state["response"] = (
            f"Order {order['id']} is currently {order['status']} for {order['item']}. "
            f"The estimated delivery date is {order['estimated_delivery']}."
        )
    elif state.get("knowledge"):
        state["response"] = " ".join(document["content"] for document in state["knowledge"])
    else:
        state["response"] = "I could not find an approved answer for that request. A support specialist can help."
    return state


def _route_after_classification(state: AgentState) -> str:
    return "load_order" if state.get("intent") == "order" else "search_support_knowledge"


def _route_after_order(state: AgentState) -> str:
    return "create_damage_ticket" if state.get("damaged") else "search_support_knowledge"


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("classify_request", classify_request)
    builder.add_node("load_order", load_order)
    builder.add_node("load_customer", load_customer)
    builder.add_node("search_support_knowledge", search_support_knowledge)
    builder.add_node("create_damage_ticket", create_damage_ticket)
    builder.add_node("escalate_damage", escalate_damage)
    builder.add_node("compose_response", compose_response)
    builder.add_edge(START, "classify_request")
    builder.add_conditional_edges("classify_request", _route_after_classification)
    builder.add_conditional_edges("load_order", _route_after_order)
    builder.add_edge("create_damage_ticket", "escalate_damage")
    builder.add_edge("escalate_damage", "compose_response")
    builder.add_edge("load_customer", "compose_response")
    builder.add_edge("search_support_knowledge", "load_customer")
    builder.add_edge("compose_response", END)
    return builder.compile()