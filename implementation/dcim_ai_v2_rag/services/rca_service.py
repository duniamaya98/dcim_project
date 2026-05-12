from sqlalchemy import text
from psycopg2.extras import Json
from dcim_ai.core.data_loader import get_db_engine


def save_root_cause(result: dict):

    engine = get_db_engine()

    # Convert dict fields to JSON wrapper
    result["domain_probabilities"] = Json(result["domain_probabilities"])
    result["causal_chain"] = Json(result["causal_chain"])
    result["metadata"] = Json(result["metadata"])

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO incident_root_causes (
                incident_id,
                root_domain,
                confidence,
                entropy,
                domain_probabilities,
                causal_chain,
                explanation,
                metadata
            )
            VALUES (
                :incident_id,
                :root_domain,
                :confidence,
                :entropy,
                :domain_probabilities,
                :causal_chain,
                :explanation,
                :metadata
            )
            ON CONFLICT (incident_id)
            DO UPDATE SET
                root_domain = EXCLUDED.root_domain,
                confidence = EXCLUDED.confidence,
                entropy = EXCLUDED.entropy,
                domain_probabilities = EXCLUDED.domain_probabilities,
                causal_chain = EXCLUDED.causal_chain,
                explanation = EXCLUDED.explanation,
                metadata = EXCLUDED.metadata
        """), result)