from sqlalchemy import text
import json
from dcim_ai.core.data_loader import get_db_engine

engine = get_db_engine()


def register_model(model_name, version, contamination, training_window, artifact_path, metrics):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO model_registry 
            (model_name, version, contamination, training_window, artifact_path, metrics_json)
            VALUES (:model_name, :version, :contamination, :training_window, :artifact_path, :metrics)
        """), {
            "model_name": model_name,
            "version": version,
            "contamination": contamination,
            "training_window": training_window,
            "artifact_path": artifact_path,
            "metrics": json.dumps(metrics)
        })
        conn.commit()


def activate_model(model_name, version):
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE model_registry
            SET is_active = FALSE
            WHERE model_name = :model_name
        """), {"model_name": model_name})

        conn.execute(text("""
            UPDATE model_registry
            SET is_active = TRUE
            WHERE model_name = :model_name
              AND version = :version
        """), {"model_name": model_name, "version": version})

        conn.commit()


def get_active_model(model_name):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT artifact_path
            FROM model_registry
            WHERE model_name = :model_name
            AND is_active = TRUE
            LIMIT 1
        """), {"model_name": model_name})

        row = result.fetchone()

        if row is None:
            return None

        # SQLAlchemy 2.x safe access
        return row._mapping["artifact_path"]