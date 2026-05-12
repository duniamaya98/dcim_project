from .severity_matrix import compute_severity
from .incident_builder import build_incident
from dcim_ai.root_cause.rca_engine import RCAEngine
from dcim_ai.root_cause.lifecycle_manager import RootCauseLifecycleManager

lifecycle_manager = RootCauseLifecycleManager(window_size=20)


class CorrelationEngine:

    def evaluate(self,
                 domain_state,
                 aggregation_state,
                 snapshot_severity):

        final_severity = compute_severity(
            domain_state,
            aggregation_state,
            snapshot_severity
        )

        incident = build_incident(
            domain_state,
            aggregation_state,
            final_severity
        )

        # ✅ RCA harus di sini
        rca_result = RCAEngine.analyze(incident)
        incident["root_cause"] = rca_result.to_dict()

        # 🔥 Update lifecycle
        lifecycle_manager.update(rca_result)
        summary = lifecycle_manager.summary()
        governance = lifecycle_manager.governance_status()

        incident["root_cause_lifecycle"] = {
            **summary,
            "governance": governance
        }
        if governance["governance_flag"]:
            print("[RCA-GOVERNANCE] RCA instability detected.")
            print(f"  - Unstable: {governance['rca_unstable']}")
            print(f"  - Low Confidence: {governance['low_confidence']}")
            print(f"  - High Entropy: {governance['high_entropy']}")
        return incident