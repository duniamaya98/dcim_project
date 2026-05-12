from dcim_ai.correlation.aggregation_engine import AggregationEngine

def test_anomaly_ratio():
    engine = AggregationEngine()
    buffer = [
        {"prediction": -1, "drift_level": "stable", "domain_scores": {"compute": 5}},
        {"prediction": -1, "drift_level": "stable", "domain_scores": {"compute": 5}},
    ]

    state = engine.compute(buffer)
    assert state.anomaly_ratio == 1.0