from dataclasses import dataclass

from app.agent.service import CustomerSupportAgent


@dataclass(frozen=True)
class QualityCase:
    name: str
    prompt: str
    expected_terms: tuple[str, ...]
    context: str


QUALITY_CASES = (
    QualityCase("order_answer_relevance", "Where is order ORD-1001?", ("ORD-1001", "shipped"), "Order ORD-1001 is shipped."),
    QualityCase("damaged_order_groundedness", "My order ORD-1002 arrived damaged", ("TICKET-", "human"), "Damaged orders receive a ticket and human follow-up."),
    QualityCase("delivery_knowledge_groundedness", "How long do shipped orders take?", ("three", "five"), "Shipped orders usually arrive within three to five business days."),
)


def run_quality_case(case: QualityCase, agent: CustomerSupportAgent | None = None) -> dict[str, object]:
    result = (agent or CustomerSupportAgent()).invoke(case.prompt)
    response = result["response"].lower()
    matches = sum(term.lower() in response for term in case.expected_terms)
    score = matches / len(case.expected_terms)
    passed = score >= 0.75
    return {
        "test_name": case.name,
        "input": case.prompt,
        "expected_behavior": case.context,
        "actual_behavior": result["response"],
        "passed": passed,
        "severity": "medium" if not passed else "low",
        "score": score,
        "failure_reason": None if passed else "The response did not contain enough grounded expected information.",
        "recommendation": None if passed else "Improve retrieval context and require evidence-backed responses.",
        "trace": result["trace"],
    }