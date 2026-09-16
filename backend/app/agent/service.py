import time
import uuid
from datetime import datetime, timezone
from typing import Any

from langchain_openai import ChatOpenAI

from app.agent.graph import build_graph
from app.core.config import get_settings


class CustomerSupportAgent:
    """Runnable customer support graph with optional OpenAI-compatible generation."""

    def __init__(self, model: Any | None = None) -> None:
        self.graph = build_graph()
        settings = get_settings()
        self.model = model
        if self.model is None and settings.openai_api_key:
            self.model = ChatOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                model=settings.openai_model,
                temperature=0,
            )

    def invoke(self, message: str, customer_id: str | None = None) -> dict[str, Any]:
        if not message.strip():
            raise ValueError("Message must not be empty")
        result = self.graph.invoke(
            {
                "message": message.strip(),
                "customer_id": customer_id,
                "trace": [],
            }
        )
        result["message"] = message.strip()
        if self.model is not None:
            result["response"] = self._generate_response(result)
        return {
            "response": result["response"],
            "trace": result.get("trace", []),
            "tool_calls": [event["name"] for event in result.get("trace", []) if event["type"] == "tool"],
        }

    def _generate_response(self, result: dict[str, Any]) -> str:
        started = time.perf_counter()
        event: dict[str, Any] = {
            "span_id": str(uuid.uuid4()),
            "type": "llm",
            "component": "customer_support_agent",
            "name": "final_response",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "status": "ok",
        }
        try:
            prompt = (
                "Answer the customer using only the observed support data below. "
                "Do not invent order status, customer data, ticket IDs, or actions. "
                f"Customer message: {result['message']}\n"
                f"Tool trace: {result.get('trace', [])}\n"
                f"Draft answer: {result['response']}"
            )
            response = self.model.invoke(
                [
                    ("system", "You are a concise, safety-conscious customer support agent."),
                    ("human", prompt),
                ]
            )
            content = getattr(response, "content", response)
            event["output"] = content
            return str(content)
        except Exception as exc:
            event["status"] = "error"
            event["error"] = str(exc)
            return result["response"]
        finally:
            event["end_time"] = datetime.now(timezone.utc).isoformat()
            event["duration"] = round(time.perf_counter() - started, 6)
            result.setdefault("trace", []).append(event)