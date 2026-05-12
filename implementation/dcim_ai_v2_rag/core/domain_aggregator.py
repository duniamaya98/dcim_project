from dcim_ai.config.domain_mapping import DOMAIN_FEATURE_MAP

def map_features_to_domain(feature_scores: dict):
    """
    feature_scores: {
        "cpu_usage": -1,
        "memory_usage": 1,
        ...
    }

    Return:
    {
        "compute": 0.75,
        "memory": 0.2,
        ...
    }
    """

    domain_scores = {}

    for domain, features in DOMAIN_FEATURE_MAP.items():
        scores = []

        for f in features:
            if f in feature_scores:
                scores.append(abs(feature_scores[f]))

        if scores:
            domain_scores[domain] = sum(scores) / len(scores)
        else:
            domain_scores[domain] = 0.0

    return domain_scores