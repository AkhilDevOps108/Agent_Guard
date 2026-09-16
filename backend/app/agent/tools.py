import re
from typing import Any

from langchain_core.tools import tool


_ORDER_PATTERN = re.compile(r"^ORD-[0-9]{4,}$")
_CUSTOMER_PATTERN = re.compile(r"^CUS-[0-9]{4,}$")

_CUSTOMERS: dict[str, dict[str, str]] = {
    "CUS-1001": {"id": "CUS-1001", "name": "Avery Stone", "tier": "standard"},
    "CUS-1002": {"id": "CUS-1002", "name": "Jordan Lee", "tier": "premium"},
}
_ORDERS: dict[str, dict[str, Any]] = {
    "ORD-1001": {
        "id": "ORD-1001",
        "customer_id": "CUS-1001",
        "status": "shipped",
        "item": "Wireless keyboard",
        "estimated_delivery": "2026-09-20",
        "damaged": False,
    },
    "ORD-1002": {
        "id": "ORD-1002",
        "customer_id": "CUS-1002",
        "status": "delivered",
        "item": "Noise-cancelling headphones",
        "estimated_delivery": "2026-09-12",
        "damaged": True,
    },
}
_KNOWLEDGE: tuple[dict[str, str], ...] = (
    {
        "title": "Delivery estimates",
        "content": "Shipped orders usually arrive within three to five business days.",
    },
    {
        "title": "Damaged orders",
        "content": "Damaged deliveries receive a support ticket and human follow-up.",
    },
    {
        "title": "Returns",
        "content": "Customers can request a return within 30 days of delivery.",
    },
)
_TICKETS: list[dict[str, str]] = []
_ESCALATIONS: list[dict[str, str]] = []


def _validate_identifier(value: str, pattern: re.Pattern[str], label: str) -> str:
    if not pattern.fullmatch(value):
        raise ValueError(f"Invalid {label} format")
    return value


@tool
def search_knowledge(query: str) -> list[dict[str, str]]:
    """Search approved customer-support knowledge for a query."""
    if not query.strip():
        raise ValueError("Knowledge query must not be empty")
    terms = set(query.lower().split())
    return [
        document
        for document in _KNOWLEDGE
        if terms.intersection(set(document["title"].lower().split() + document["content"].lower().split()))
    ]


@tool
def get_customer(customer_id: str) -> dict[str, str]:
    """Retrieve a customer using a validated customer identifier."""
    customer_id = _validate_identifier(customer_id, _CUSTOMER_PATTERN, "customer ID")
    customer = _CUSTOMERS.get(customer_id)
    if customer is None:
        raise ValueError("Customer not found")
    return customer


@tool
def get_order(order_id: str) -> dict[str, Any]:
    """Retrieve order status and fulfillment details."""
    order_id = _validate_identifier(order_id, _ORDER_PATTERN, "order ID")
    order = _ORDERS.get(order_id)
    if order is None:
        raise ValueError("Order not found")
    return order


@tool
def create_ticket(order_id: str, customer_id: str, issue: str) -> dict[str, str]:
    """Create a support ticket for a customer order issue."""
    order_id = _validate_identifier(order_id, _ORDER_PATTERN, "order ID")
    customer_id = _validate_identifier(customer_id, _CUSTOMER_PATTERN, "customer ID")
    if not issue.strip():
        raise ValueError("Ticket issue must not be empty")
    if order_id not in _ORDERS or customer_id not in _CUSTOMERS:
        raise ValueError("Ticket references an unknown customer or order")
    ticket = {
        "ticket_id": f"TICKET-{len(_TICKETS) + 1:04d}",
        "order_id": order_id,
        "customer_id": customer_id,
        "issue": issue.strip(),
        "status": "open",
    }
    _TICKETS.append(ticket)
    return ticket


@tool
def escalate_to_human(reason: str, order_id: str, customer_id: str) -> dict[str, str]:
    """Escalate a support issue to a human specialist."""
    order_id = _validate_identifier(order_id, _ORDER_PATTERN, "order ID")
    customer_id = _validate_identifier(customer_id, _CUSTOMER_PATTERN, "customer ID")
    if not reason.strip():
        raise ValueError("Escalation reason must not be empty")
    escalation = {
        "escalation_id": f"ESC-{len(_ESCALATIONS) + 1:04d}",
        "order_id": order_id,
        "customer_id": customer_id,
        "reason": reason.strip(),
        "status": "queued",
    }
    _ESCALATIONS.append(escalation)
    return escalation


TOOL_REGISTRY = {
    tool.name: tool
    for tool in (search_knowledge, get_customer, get_order, create_ticket, escalate_to_human)
}