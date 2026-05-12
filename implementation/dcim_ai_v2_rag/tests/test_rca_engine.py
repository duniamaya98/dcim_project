from dcim_ai.root_cause.rca_engine import RCAEngine


def test_rca_contract():

    mock_incident = {
        "incident_id": "INC-100",
        "timestamp": "2026-02-25T10:00:00",
        "active_domains": ["compute", "memory", "network"]
    }

    result = RCAEngine.analyze(mock_incident)

    assert result.root_domain in mock_incident["active_domains"]
    assert isinstance(result.domain_probabilities, dict)
    assert abs(sum(result.domain_probabilities.values()) - 1.0) < 1e-6
    assert hasattr(result, "confidence")