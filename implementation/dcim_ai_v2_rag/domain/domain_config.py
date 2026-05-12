# dcim_ai/domain/domain_config.py

DOMAIN_FEATURE_MAP = {
    "compute": ["cpu_usage"],
    "memory": ["memory_usage"],
    "storage": ["disk_io"],
    "network": ["net_rx", "net_tx"],
}

DOMAIN_SEVERITY_WEIGHT = {
    "compute": 1.0,
    "memory": 1.2,
    "storage": 0.9,
    "network": 0.8,
}

DOMAIN_ACTIVATION_THRESHOLD = 3.0  # z-score threshold