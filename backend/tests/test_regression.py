from app.services.regression import generate_regression_test


def test_generate_regression_test_creates_executable_policy_guard():
    result = generate_regression_test(
        name="tool_abuse_without_order",
        category="security",
        severity="critical",
        root_cause="The agent executed a sensitive tool without authorizing the request.",
        fix="Add an explicit allowlist and block writes unless policy validation passes.",
    )

    assert result["name"].endswith("_regression")
    assert result["category"] == "security"
    assert result["severity"] == "critical"
    assert "assert" in result["test_body"].lower()
    assert "unauthorized" in result["test_body"].lower() or "policy" in result["test_body"].lower()
    assert result["prompt"]
