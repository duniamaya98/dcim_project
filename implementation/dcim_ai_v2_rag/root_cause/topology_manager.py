from typing import Dict
import json
from pathlib import Path

from .causal_topology import DEFAULT_CAUSAL_GRAPH


class CausalTopologyManager:

    def __init__(self, registry_path: str = "dcim_ai/registry/registry.json"):
        self.registry_path = registry_path
        self.graph = DEFAULT_CAUSAL_GRAPH.copy()
        self._load_override()

    def _load_override(self):
        """
        Jika registry memiliki rca_topology_override,
        maka override default graph.
        """

        try:
            registry_file = Path(self.registry_path)

            if not registry_file.exists():
                return

            with open(registry_file, "r") as f:
                registry = json.load(f)

            override = registry.get("rca_topology_override")

            if override:
                self.graph.update(override)

        except Exception:
            # Fail-safe: gunakan default topology
            pass

    def get_downstream(self, domain: str) -> Dict[str, float]:
        return self.graph.get(domain, {})

    def get_upstream(self, domain: str) -> Dict[str, float]:

        upstream = {}

        for src, targets in self.graph.items():
            if domain in targets:
                upstream[src] = targets[domain]

        return upstream

    def get_full_graph(self) -> Dict[str, Dict[str, float]]:
        return self.graph