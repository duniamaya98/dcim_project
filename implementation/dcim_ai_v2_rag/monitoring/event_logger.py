import psycopg2
import os

def log_event(payload):
    conn = psycopg2.connect(
        host="localhost",
        database="dcim_ai",
        user="infra",
        password="StrongPassword123"
    )

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO anomaly_events (
            model_version,
            prediction,
            severity,
            ensemble_score,
            drift_score,
            drift_status,
            cpu_usage,
            memory_usage,
            disk_io,
            net_rx,
            net_tx
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        payload["model_version"],
        payload["prediction"],
        payload["severity"],
        payload["ensemble_score"],
        payload["drift_score"],
        payload["drift_status"],
        payload["cpu_usage"],
        payload["memory_usage"],
        payload["disk_io"],
        payload["net_rx"],
        payload["net_tx"]
    ))

    conn.commit()
    cur.close()
    conn.close()
