# dcim_ai/config/domain_mapping.py

DOMAIN_FEATURE_MAP = {
    "compute": [
        "cpu_usage",
        "cpu_load",
        "thread_count"
    ],
    "memory": [
        "memory_usage",
        "swap_usage"
    ],
    "power": [
        "power_watt",
        "voltage"
    ],
    "cooling": [
        "temp_in",
        "temp_out"
    ],
    "network": [
        "packet_loss",
        "throughput"
    ]
}

# Severity influence weight (untuk fase correlation)
DOMAIN_SEVERITY_WEIGHT = {
    "compute": 1.0,
    "memory": 0.9,
    "power": 1.2,
    "cooling": 1.1,
    "network": 0.8
}