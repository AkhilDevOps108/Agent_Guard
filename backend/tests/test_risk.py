from app.services.risk import _p95


def test_p95_latency_is_calculated_for_multiple_samples():
    assert _p95([1.0, 2.0, 3.0, 4.0, 5.0]) == 4.8