"""
Anomaly Detection Stream Processor

Consumes metrics from TimescaleDB, applies Z-score anomaly detection in real-time,
and publishes anomalies to Kafka topic dcim.analytics.anomalies.

Flow:
  TimescaleDB (metrics) → Z-score Detection → Kafka (dcim.analytics.anomalies)

Reference: block7-analytics-ai-engine.md §3
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from kafka import KafkaProducer
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import numpy as np
import time
import os
import uuid

logger = logging.getLogger(__name__)


class AnomalyDetectionProcessor:
    """
    Real-time anomaly detection using Z-score method.

    Detects anomalies by comparing current metric values against
    historical mean and standard deviation.
    """

    def __init__(
        self,
        db_config: Dict[str, Any] = None,
        kafka_bootstrap_servers: str = None,
        zscore_threshold: float = 3.0,
        window_size: int = 100,
        check_interval_seconds: int = 30
    ):
        # Database connection
        self.db_config = db_config or {
            "host": os.getenv("TIMESCALEDB_HOST", "10.70.0.56"),
            "port": int(os.getenv("TIMESCALEDB_PORT", "5433")),
            "database": os.getenv("TIMESCALEDB_DATABASE", "dcim_analytics"),
            "user": os.getenv("TIMESCALEDB_USER", "ai_team"),
            "password": os.environ["TIMESCALEDB_PASSWORD"]
        }

        # Kafka producer
        kafka_bootstrap_servers = kafka_bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "10.70.0.56:9092")
        self.anomaly_topic = os.getenv("KAFKA_TOPIC_ANOMALIES", "dcim.analytics.anomalies")

        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Detection parameters
        self.zscore_threshold = zscore_threshold
        self.window_size = window_size
        self.check_interval = check_interval_seconds

        # Connection
        self.conn = None
        self._connect_db()

        logger.info(f"Anomaly detector initialized (threshold={zscore_threshold}, window={window_size})")

    def _connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                **self.db_config,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Connected to TimescaleDB: {self.db_config['host']}:{self.db_config['port']}")
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            raise

    def get_recent_metrics(self, metric_name: str, ci_id: Optional[str] = None) -> List[Dict]:
        """Fetch recent metrics for Z-score calculation"""
        try:
            cur = self.conn.cursor()

            query = """
                SELECT time, value
                FROM metrics
                WHERE metric_name = %s
            """
            params = [metric_name]

            if ci_id:
                query += " AND ci_id = %s"
                params.append(ci_id)

            query += """
                AND time > NOW() - INTERVAL '1 hour'
                ORDER BY time DESC
                LIMIT %s
            """
            params.append(self.window_size)

            cur.execute(query, params)
            rows = cur.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to fetch metrics: {e}")
            return []

    def calculate_zscore(self, values: List[float], current_value: float) -> float:
        """Calculate Z-score for current value against historical values"""
        if len(values) < 10:
            # Not enough data
            return 0.0

        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            return 0.0

        zscore = abs((current_value - mean) / std)
        return zscore

    def classify_severity(self, zscore: float) -> str:
        """Classify anomaly severity based on Z-score"""
        if zscore >= 5.0:
            return "critical"
        elif zscore >= 4.0:
            return "high"
        elif zscore >= 3.0:
            return "medium"
        else:
            return "low"

    def detect_anomalies_for_metric(self, metric_name: str):
        """Detect anomalies for a specific metric"""
        try:
            # Get latest value
            cur = self.conn.cursor()
            cur.execute("""
                SELECT time, ci_id, asset_id, value, source, unit, tags
                FROM metrics
                WHERE metric_name = %s
                AND time > NOW() - INTERVAL '5 minutes'
                ORDER BY time DESC
                LIMIT 1
            """, (metric_name,))

            latest = cur.fetchone()
            if not latest:
                return

            latest_dict = dict(latest)
            current_value = latest_dict["value"]
            ci_id = latest_dict.get("ci_id")

            # Get historical data
            historical = self.get_recent_metrics(metric_name, ci_id)
            if len(historical) < 10:
                logger.debug(f"Not enough historical data for {metric_name}")
                return

            historical_values = [h["value"] for h in historical]

            # Calculate Z-score
            zscore = self.calculate_zscore(historical_values, current_value)

            # Check if anomaly
            if zscore >= self.zscore_threshold:
                self._handle_anomaly(latest_dict, zscore, historical_values)

        except Exception as e:
            logger.error(f"Error detecting anomalies for {metric_name}: {e}", exc_info=True)

    def _handle_anomaly(self, latest: Dict, zscore: float, historical_values: List[float]):
        """Handle detected anomaly - store and publish"""
        try:
            # Calculate expected range
            mean = np.mean(historical_values)
            std = np.std(historical_values)
            expected_min = mean - (self.zscore_threshold * std)
            expected_max = mean + (self.zscore_threshold * std)

            # Classify severity
            severity = self.classify_severity(zscore)

            # Build anomaly event
            anomaly_event = {
                "anomaly_id": str(uuid.uuid4()),
                "timestamp": latest["time"].isoformat() if hasattr(latest["time"], 'isoformat') else str(latest["time"]),
                "metric_name": latest.get("metric_name", "unknown"),
                "ci_id": str(latest.get("ci_id")) if latest.get("ci_id") else None,
                "asset_id": str(latest.get("asset_id")) if latest.get("asset_id") else None,
                "detection_method": "zscore",
                "current_value": float(latest["value"]),
                "expected_min": float(expected_min),
                "expected_max": float(expected_max),
                "anomaly_score": float(min(zscore / 10.0, 1.0)),  # Normalize to 0-1
                "severity": severity,
                "description": f"{latest.get('metric_name')} value {latest['value']} exceeds expected range [{expected_min:.2f}, {expected_max:.2f}] (Z-score: {zscore:.2f})",
                "possible_causes": [],
                "recommended_actions": []
            }

            # Store in database
            self._store_anomaly(anomaly_event)

            # Publish to Kafka
            self.producer.send(self.anomaly_topic, anomaly_event)
            self.producer.flush()

            logger.info(f"Anomaly detected: {anomaly_event['metric_name']} (severity={severity}, zscore={zscore:.2f})")

        except Exception as e:
            logger.error(f"Failed to handle anomaly: {e}", exc_info=True)

    def _store_anomaly(self, anomaly: Dict):
        """Store anomaly in TimescaleDB"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO anomaly_events (
                    anomaly_id, timestamp, metric_name, ci_id, asset_id,
                    detection_method, current_value, expected_min, expected_max,
                    anomaly_score, severity, description, possible_causes, recommended_actions
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                anomaly["anomaly_id"],
                anomaly["timestamp"],
                anomaly["metric_name"],
                anomaly["ci_id"],
                anomaly["asset_id"],
                anomaly["detection_method"],
                anomaly["current_value"],
                anomaly["expected_min"],
                anomaly["expected_max"],
                anomaly["anomaly_score"],
                anomaly["severity"],
                anomaly["description"],
                json.dumps(anomaly["possible_causes"]),
                json.dumps(anomaly["recommended_actions"])
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to store anomaly: {e}")
            self.conn.rollback()

    def get_active_metrics(self) -> List[str]:
        """Get list of active metrics from last 10 minutes"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT DISTINCT metric_name
                FROM metrics
                WHERE time > NOW() - INTERVAL '10 minutes'
            """)
            rows = cur.fetchall()
            return [row["metric_name"] for row in rows]
        except Exception as e:
            logger.error(f"Failed to get active metrics: {e}")
            return []

    def run(self):
        """Run anomaly detection loop"""
        logger.info("Starting anomaly detection processor")

        try:
            while True:
                # Get active metrics
                metrics = self.get_active_metrics()
                logger.info(f"Checking {len(metrics)} active metrics")

                # Check each metric
                for metric_name in metrics:
                    self.detect_anomalies_for_metric(metric_name)

                # Sleep until next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("Processor interrupted by user")
        finally:
            self.close()

    def close(self):
        """Close connections"""
        if self.conn:
            self.conn.close()
        if self.producer:
            self.producer.close()
        logger.info("Anomaly detection processor closed")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    processor = AnomalyDetectionProcessor()
    processor.run()
