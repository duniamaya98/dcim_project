import uuid
import time


def build_incident(domain_state, aggregation_state, final_severity):

    incident_id = str(uuid.uuid4())

    confidence = 0.5

    if aggregation_state:
        confidence = min(
            1.0,
            aggregation_state.anomaly_ratio +
            aggregation_state.drift_ratio
        )

    # ----------------------------
    # Root Cause Hint (Legacy)
    # ----------------------------
    root_cause_hint = "unknown"

    if len(domain_state.active_domains) == 1:
        root_cause_hint = domain_state.active_domains[0]

    elif len(domain_state.active_domains) >= 2:
        root_cause_hint = "multi_domain_interaction"

    # ----------------------------
    # Incident Enrichment
    # ----------------------------
    return {
        "incident_id": incident_id,
        "timestamp": int(time.time()),
        "severity": final_severity,
        "confidence": round(confidence, 3),

        # Existing
        "active_domains": domain_state.active_domains,
        "root_cause_hint": root_cause_hint,

        # 🔥 DOMAIN INTELLIGENCE
        "domain_scores": domain_state.domain_scores,
        "domain_strength_index": domain_state.domain_strength_index,

        # 🔥 TEMPORAL INTELLIGENCE
        "anomaly_ratio": aggregation_state.anomaly_ratio if aggregation_state else 0,
        "drift_ratio": aggregation_state.drift_ratio if aggregation_state else 0,
        "domain_persistence_ratio": aggregation_state.domain_persistence_ratio if aggregation_state else {},
        "domain_trend": aggregation_state.domain_trend if aggregation_state else {},
        "co_occurrence_matrix": aggregation_state.co_occurrence_matrix if aggregation_state else {}
    }