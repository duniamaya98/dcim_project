from dcim_ai.correlation.correlation_engine import CorrelationEngine

def test_incident_generation():
    engine = CorrelationEngine()

    class DummyDomain:
        active_domains = ["compute"]
        domain_strength_index = 6

    class DummyAgg:
        anomaly_ratio = 0.8
        drift_ratio = 0.5
        domain_persistence_ratio = {"compute": 0.8}

    incident = engine.evaluate(DummyDomain(), DummyAgg(), "warning")

    assert incident["severity"] in ["critical", "high", "warning"]