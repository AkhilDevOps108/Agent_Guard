from collections import Counter


COUNTERS: Counter[str] = Counter()


def increment(name: str) -> None:
    COUNTERS[name] += 1


def prometheus_text() -> str:
    lines = []
    for name, value in sorted(COUNTERS.items()):
        metric = f"agentguard_{name}"
        lines.extend((f"# TYPE {metric} counter", f"{metric} {value}"))
    return "\n".join(lines) + ("\n" if lines else "")
