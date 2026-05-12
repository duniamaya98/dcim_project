def evaluate_basic_rules(domain_scores: dict, drift_level: str):

    # Domain dianggap aktif jika drift > 3 (lebih realistis)
    active_domains = [
        d for d, score in domain_scores.items()
        if score > 3.0
    ]

    multi_domain = len(active_domains) >= 2

    if multi_domain and drift_level == "severe_drift":
        severity = "critical"
    elif multi_domain:
        severity = "high"
    elif active_domains:
        severity = "moderate"
    else:
        severity = "normal"

    return {
        "active_domains": active_domains,
        "multi_domain": multi_domain,
        "severity": severity
    }