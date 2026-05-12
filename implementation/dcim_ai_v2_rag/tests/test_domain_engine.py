from dcim_ai.domain.domain_engine import DomainEngine

def test_domain_activation():
    engine = DomainEngine()
    z_map = {"cpu_usage": 5, "memory_usage": 0}
    state = engine.compute(z_map)

    assert "compute" in state.active_domains