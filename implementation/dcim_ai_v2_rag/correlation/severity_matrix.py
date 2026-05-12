# dcim_ai/correlation/severity_matrix.py

def compute_severity(domain_state, aggregation_state, snapshot_severity):

    # Escalation by repetition
    if aggregation_state and aggregation_state.anomaly_ratio >= 0.6:
        return "critical"

    # Multi-domain persistence
    if aggregation_state:
        persistent_domains = [
            d for d, ratio in aggregation_state.domain_persistence_ratio.items()
            if ratio >= 0.5
        ]
        if len(persistent_domains) >= 2:
            return "high"

    # High domain strength
    if domain_state.domain_strength_index > 5:
        return "warning"

    return snapshot_severity