from typing import Dict, List


DEFAULT_CAUSAL_GRAPH: Dict[str, Dict[str, float]] = {
    # upstream → downstream (influence weight)

    "power": {
        "cooling": 0.9,
        "compute": 0.7
    },
    "cooling": {
        "compute": 0.8
    },
    "compute": {
        "memory": 0.6,
        "network": 0.5,
        "storage": 0.4
    },
    "storage": {
        "compute": 0.3
    },
    "network": {},
    "memory": {}
}