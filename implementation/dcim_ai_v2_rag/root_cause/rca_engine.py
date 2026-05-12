from typing import Dict, Any
from datetime import datetime
import numpy as np

from .rca_models import RootCauseResult
from .topology_manager import CausalTopologyManager


class RCAEngine:

    # =====================================================
    # SOFTMAX
    # =====================================================

    @staticmethod
    def _softmax(scores: Dict[str, float]) -> Dict[str, float]:
        if not scores:
            return {"unknown": 1.0}

        values = np.array(list(scores.values()))
        exp_values = np.exp(values - np.max(values))
        probs = exp_values / exp_values.sum()

        return dict(zip(scores.keys(), probs.tolist()))

    # =====================================================
    # CAUSAL CHAIN RECONSTRUCTION
    # =====================================================

    @staticmethod
    def _build_causal_chain(root_domain, active_domains, domain_probabilities):

        topology = CausalTopologyManager()

        visited = set()
        chain = []

        def dfs(domain, depth=0, max_depth=3):

            if depth > max_depth:
                return

            if domain in visited:
                return

            visited.add(domain)

            # 🔥 Probability-based pruning
            if domain_probabilities.get(domain, 0) < 0.15:
                return

            if domain in active_domains:
                chain.append(domain)

            downstream = topology.get_downstream(domain)

            for next_domain in downstream:
                if next_domain in active_domains:
                    dfs(next_domain, depth + 1, max_depth)

        dfs(root_domain)

        return chain

    # =====================================================
    # EXPLANATION BUILDER
    # =====================================================

    @staticmethod
    def _generate_explanation(root_domain, chain):

        if not chain or len(chain) == 1:
            return f"{root_domain} identified as primary root cause based on composite scoring."

        chain_text = " → ".join(chain)

        return (
            f"Root cause chain reconstructed: {chain_text}. "
            f"Composite scoring applied (topology + domain strength + persistence + trend + drift)."
        )

    # =====================================================
    # MAIN ANALYZE
    # =====================================================

    @staticmethod
    def analyze(incident: Dict[str, Any]) -> RootCauseResult:

        incident_id = incident.get("incident_id")
        timestamp = incident.get("timestamp")

        # --------------------------
        # Robust Timestamp Handling
        # --------------------------
        if isinstance(timestamp, int):
            timestamp = datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif not isinstance(timestamp, datetime):
            timestamp = datetime.utcnow()

        active_domains = incident.get("active_domains", [])

        if not active_domains:
            return RootCauseResult(
                incident_id=incident_id,
                timestamp=timestamp,
                domain_probabilities={"unknown": 1.0},
                root_domain="unknown",
                ranked_domains=["unknown"],
                causal_chain=[],
                impact_domains=[],
                confidence=1.0,
                explanation="No active domains detected.",
                metadata={"num_domains": 0}
            )

        topology = CausalTopologyManager()

        raw_scores = {}

        domain_strength_index = incident.get("domain_strength_index", 0)
        anomaly_ratio = incident.get("anomaly_ratio", 0)
        drift_ratio = incident.get("drift_ratio", 0)
        persistence = incident.get("domain_persistence_ratio", {})
        domain_trend = incident.get("domain_trend", {})
        domain_scores = incident.get("domain_scores", {})

        for domain in active_domains:

            # ---------------------------
            # 1️⃣ Topology Score
            # ---------------------------
            upstream = topology.get_upstream(domain)
            downstream = topology.get_downstream(domain)

            topology_score = (
                sum(downstream.values()) * 0.6 +
                sum(upstream.values()) * 0.4
            )

            # ---------------------------
            # 2️⃣ Domain Strength
            # ---------------------------
            strength_score = (
                domain_scores.get(domain, 0)
                / (domain_strength_index + 1e-6)
            )

            # ---------------------------
            # 3️⃣ Persistence
            # ---------------------------
            persistence_score = persistence.get(domain, 0)

            # ---------------------------
            # 4️⃣ Trend
            # ---------------------------
            trend_value = domain_trend.get(domain, "stable")
            if trend_value == "increasing":
                trend_score = 1.0
            elif trend_value == "decreasing":
                trend_score = -0.5
            else:
                trend_score = 0.2

            # ---------------------------
            # 5️⃣ Global Ratios
            # ---------------------------
            anomaly_score = anomaly_ratio
            drift_score = drift_ratio

            # ---------------------------
            # Composite Weighted Formula
            # ---------------------------
            score = (
                0.30 * topology_score +
                0.25 * strength_score +
                0.20 * persistence_score +
                0.10 * trend_score +
                0.10 * anomaly_score +
                0.05 * drift_score
            )

            raw_scores[domain] = score

        # --------------------------
        # Normalize via Softmax
        # --------------------------
        domain_probabilities = RCAEngine._softmax(raw_scores)

        ranked_domains = sorted(
            domain_probabilities,
            key=domain_probabilities.get,
            reverse=True
        )

        root_domain = ranked_domains[0]
        confidence = max(domain_probabilities.values())

        # --------------------------
        # Build Causal Chain
        # --------------------------
        causal_chain = RCAEngine._build_causal_chain(
            root_domain,
            active_domains,
            domain_probabilities
        )

        explanation = RCAEngine._generate_explanation(
            root_domain,
            causal_chain
        )

        metadata = {
            "num_domains": len(domain_probabilities),
            "max_probability": confidence
        }

        return RootCauseResult(
            incident_id=incident_id,
            timestamp=timestamp,
            domain_probabilities=domain_probabilities,
            root_domain=root_domain,
            ranked_domains=ranked_domains,
            causal_chain=causal_chain,
            impact_domains=active_domains,
            confidence=confidence,
            explanation=explanation,
            metadata=metadata
        )