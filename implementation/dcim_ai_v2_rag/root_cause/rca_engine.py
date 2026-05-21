from typing import Dict, Any
from datetime import datetime
import numpy as np

from .rca_models import (
    RootCauseResult,
    RCA_MODE_FORWARD,
    RCA_MODE_HYBRID,
)
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

    # =====================================================
    # v1.2.0 — FORWARD MODE (MT-022 §6.3)
    # =====================================================

    @staticmethod
    def analyze_forward(forecast_payload: Dict[str, Any]) -> RootCauseResult:
        """
        Predictive RCA berdasarkan output forecast model (UC1).

        Berbeda dengan ``analyze()`` yang reaktif terhadap incident yang
        sudah terjadi, ``analyze_forward()`` menerima projeksi forecast
        (lihat ``MT-022 §6.3``) dan menjawab:

            "Kalau forecast 24/48 jam ke depan menunjukkan failure di
             aset X, kemungkinan rantai penyebabnya apa?"

        Parameters
        ----------
        forecast_payload : dict
            Minimal harus mengandung:

            ``incident_id``           — identifier hasil forecast
            ``timestamp``             — waktu projeksi
            ``forecast_horizon_h``    — 24 atau 48 (jam)
            ``forecasted_domains``    — dict domain → forecasted_score
            ``forecast_confidence``   — confidence forecast model (0..1)
            ``asset_id``              — opsional, untuk enrichment

            Field lain yang dipakai oleh ``analyze()`` (anomaly_ratio,
            persistence, dst.) tetap dihormati bila ada — kalau tidak
            ada, default ke 0 sehingga komponen scoring lain "diam".

        Returns
        -------
        RootCauseResult
            Dengan ``mode='forward'`` dan ``forecast_horizon_h``,
            ``forecast_confidence`` terisi.
        """
        forecasted = forecast_payload.get("forecasted_domains") or {}
        if not forecasted:
            ts = forecast_payload.get("timestamp", datetime.utcnow())
            if isinstance(ts, int):
                ts = datetime.fromtimestamp(ts)
            elif isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            elif not isinstance(ts, datetime):
                ts = datetime.utcnow()
            return RootCauseResult(
                incident_id=forecast_payload.get("incident_id", "fwd-unknown"),
                timestamp=ts,
                domain_probabilities={"unknown": 1.0},
                root_domain="unknown",
                ranked_domains=["unknown"],
                causal_chain=[],
                impact_domains=[],
                confidence=1.0,
                explanation="No forecasted domains supplied to forward RCA.",
                metadata={"num_domains": 0, "mode_origin": "forward"},
                mode=RCA_MODE_FORWARD,
                forecast_horizon_h=forecast_payload.get("forecast_horizon_h"),
                forecast_confidence=forecast_payload.get("forecast_confidence"),
            )

        # Bentuk incident "virtual" agar reuse pipeline analyze().
        # Skor forecast dipakai sebagai domain_scores; aktifkan domain
        # yang skornya > 0. Persistence/trend/drift = 0 (tidak relevan).
        active = [d for d, s in forecasted.items() if s and s > 0]

        synthetic_incident = {
            "incident_id": forecast_payload.get("incident_id", "fwd-synthetic"),
            "timestamp": forecast_payload.get("timestamp", datetime.utcnow()),
            "active_domains": active,
            "domain_scores": forecasted,
            "domain_strength_index": sum(forecasted.values()) or 1.0,
            "anomaly_ratio": 0.0,
            "drift_ratio": 0.0,
            "domain_persistence_ratio": {d: 1.0 for d in active},
            "domain_trend": {d: "stable" for d in active},
        }

        result = RCAEngine.analyze(synthetic_incident)

        # Patch metadata mode + forecast context
        result.mode = RCA_MODE_FORWARD
        result.forecast_horizon_h = forecast_payload.get("forecast_horizon_h")
        result.forecast_confidence = forecast_payload.get("forecast_confidence")
        result.metadata = dict(result.metadata or {})
        result.metadata.update({
            "mode_origin": "forward",
            "asset_id": forecast_payload.get("asset_id"),
        })

        # Governance flag untuk low-confidence forecast (MT-022 §6.7).
        confidence = forecast_payload.get("forecast_confidence")
        if isinstance(confidence, (int, float)) and confidence < 0.5:
            gov = dict(result.governance or {})
            gov["forward_low_confidence"] = True
            gov["governance_flag"] = True
            result.governance = gov

        return result

    @staticmethod
    def analyze_hybrid(
        incident: Dict[str, Any],
        forecast_payload: Dict[str, Any],
        forecast_weight: float = 0.4,
    ) -> RootCauseResult:
        """
        HYBRID mode: gabungkan REACTIVE (incident saat ini) dan
        FORWARD (projeksi forecast) menjadi satu RCA.

        Strategi:
            1. Jalankan ``analyze()`` untuk reactive base.
            2. Jalankan ``analyze_forward()`` untuk forward base.
            3. Gabungkan ``domain_probabilities`` dengan weighted sum:
                p_hybrid[d] = (1 - w) * p_reactive[d] + w * p_forward[d]
               dengan ``w = forecast_weight`` (default 0.4).
            4. Recompute ranked_domains, root_domain, causal_chain.

        Parameters
        ----------
        incident : dict
            Sama seperti input ``analyze()``.
        forecast_payload : dict
            Sama seperti input ``analyze_forward()``.
        forecast_weight : float
            Bobot kontribusi forecast (default 0.4). Range [0, 1].

        Returns
        -------
        RootCauseResult
            Dengan ``mode='hybrid'``.
        """
        if not (0.0 <= forecast_weight <= 1.0):
            raise ValueError("forecast_weight harus dalam [0, 1]")

        reactive = RCAEngine.analyze(incident)
        forward = RCAEngine.analyze_forward(forecast_payload)

        # Gabungkan probabilities — pastikan semua domain ter-cover.
        domains = set(reactive.domain_probabilities) | set(forward.domain_probabilities)
        w = forecast_weight
        merged = {
            d: (1 - w) * reactive.domain_probabilities.get(d, 0.0)
               + w * forward.domain_probabilities.get(d, 0.0)
            for d in domains
        }
        # Normalisasi agar tetap distribusi probabilitas valid.
        total = sum(merged.values()) or 1.0
        merged = {d: v / total for d, v in merged.items()}

        ranked = sorted(merged, key=merged.get, reverse=True)
        root_domain = ranked[0] if ranked else "unknown"
        confidence = merged.get(root_domain, 0.0)

        # Causal chain pakai aktif domain reactive ∪ forward.
        active_union = list(set(reactive.impact_domains) | set(forward.impact_domains))
        causal_chain = RCAEngine._build_causal_chain(root_domain, active_union, merged)

        explanation = (
            f"[HYBRID] {RCAEngine._generate_explanation(root_domain, causal_chain)} "
            f"Forecast weight={forecast_weight:.2f}."
        )

        return RootCauseResult(
            incident_id=reactive.incident_id,
            timestamp=reactive.timestamp,
            domain_probabilities=merged,
            root_domain=root_domain,
            ranked_domains=ranked,
            causal_chain=causal_chain,
            impact_domains=active_union,
            confidence=confidence,
            explanation=explanation,
            metadata={
                "num_domains": len(merged),
                "max_probability": confidence,
                "mode_origin": "hybrid",
                "forecast_weight": forecast_weight,
                "reactive_root": reactive.root_domain,
                "forward_root": forward.root_domain,
            },
            mode=RCA_MODE_HYBRID,
            forecast_horizon_h=forward.forecast_horizon_h,
            forecast_confidence=forward.forecast_confidence,
            governance=dict(forward.governance or {}),
        )