"""
Metrics Ingestion Consumer

Consumes metrics from dcim.analytics.metrics topic and stores in TimescaleDB.

Flow:
  Kafka (dcim.analytics.metrics) → Validate → TimescaleDB (metrics table)

Reference: block7-analytics-ai-engine.md §2.1
"""

import logging
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from typing import Dict, Any, List
import os

from .base_consumer import BaseKafkaConsumer

logger = logging.getLogger(__name__)


class MetricsIngestionConsumer(BaseKafkaConsumer):
    """
    Kafka consumer for metrics ingestion into TimescaleDB.

    Consumes from: dcim.analytics.metrics
    Stores to: metrics (TimescaleDB hypertable)
    """

    def __init__(
        self,
        bootstrap_servers: str = None,
        group_id: str = "ai-team-metrics-ingestion",
        db_config: Dict[str, Any] = None
    ):
        bootstrap_servers = bootstrap_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "10.70.0.56:9092")
        topic = os.getenv("KAFKA_TOPIC_METRICS", "dcim.analytics.metrics")
        dlq_topic = os.getenv("KAFKA_TOPIC_DLQ", "dcim.analytics.dlq")

        super().__init__(
            topic=topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            dlq_topic=dlq_topic,
            auto_commit=False
        )

        # Database connection config
        self.db_config = db_config or {
            "host": os.getenv("TIMESCALEDB_HOST", "10.70.0.56"),
            "port": int(os.getenv("TIMESCALEDB_PORT", "5433")),
            "database": os.getenv("TIMESCALEDB_DATABASE", "dcim_analytics"),
            "user": os.getenv("TIMESCALEDB_USER", "ai_team"),
            "password": os.environ["TIMESCALEDB_PASSWORD"]
        }

        # Connection pool (reuse connection)
        self.conn = None
        self._connect_db()

        # Batch buffer
        self.batch_buffer: List[Dict] = []
        self.batch_size = 100

    def _connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info(f"Connected to TimescaleDB: {self.db_config['host']}:{self.db_config['port']}")
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            raise

    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Validate message format.

        Required fields:
        - timestamp (ISO 8601)
        - metric_name (non-empty string)
        - payload.value (numeric)
        - source_system (string)
        """
        required_fields = ["timestamp", "metric_name", "source_system", "payload"]

        for field in required_fields:
            if field not in message:
                logger.warning(f"Missing required field: {field}")
                return False

        # Validate payload.value
        payload = message.get("payload", {})
        if "value" not in payload:
            logger.warning("Missing payload.value")
            return False

        try:
            float(payload["value"])
        except (ValueError, TypeError):
            logger.warning(f"Invalid numeric value: {payload['value']}")
            return False

        # Validate timestamp
        try:
            datetime.fromisoformat(message["timestamp"].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.warning(f"Invalid timestamp format: {message.get('timestamp')}")
            return False

        return True

    def transform_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Kafka message to TimescaleDB row format"""
        payload = message.get("payload", {})

        return {
            "time": message["timestamp"],
            "metric_name": message["metric_name"],
            "ci_id": message.get("ci_id"),
            "asset_id": message.get("asset_id"),
            "source": message["source_system"],
            "value": float(payload["value"]),
            "unit": payload.get("unit"),
            "tags": message.get("metadata", {}).get("tags", {})
        }

    def insert_batch(self, batch: List[Dict[str, Any]]):
        """Bulk insert batch into TimescaleDB"""
        if not batch:
            return

        try:
            cur = self.conn.cursor()

            # Prepare values
            values = [
                (
                    row["time"],
                    row["metric_name"],
                    row["ci_id"],
                    row["asset_id"],
                    row["source"],
                    row["value"],
                    row["unit"],
                    psycopg2.extras.Json(row["tags"])
                )
                for row in batch
            ]

            # Bulk insert
            execute_values(
                cur,
                """
                INSERT INTO metrics (time, metric_name, ci_id, asset_id, source, value, unit, tags)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                values
            )

            self.conn.commit()
            logger.info(f"Inserted {len(batch)} metrics into TimescaleDB")

        except Exception as e:
            logger.error(f"Failed to insert batch: {e}", exc_info=True)
            self.conn.rollback()
            raise

    def process_message(self, message: Any) -> bool:
        """Process single Kafka message"""
        try:
            data = message.value

            # Validate
            if not self.validate_message(data):
                logger.warning(f"Invalid message format, skipping: {data}")
                return True  # Skip invalid messages (don't retry)

            # Transform
            row = self.transform_message(data)

            # Add to batch buffer
            self.batch_buffer.append(row)

            # Flush batch if full
            if len(self.batch_buffer) >= self.batch_size:
                self.insert_batch(self.batch_buffer)
                self.batch_buffer = []

            return True

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return False

    def close(self):
        """Flush remaining batch and close connections"""
        try:
            # Flush remaining batch
            if self.batch_buffer:
                logger.info(f"Flushing remaining {len(self.batch_buffer)} messages")
                self.insert_batch(self.batch_buffer)
                self.batch_buffer = []
        except Exception as e:
            logger.error(f"Error flushing batch: {e}")
        finally:
            if self.conn:
                self.conn.close()
            super().close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    consumer = MetricsIngestionConsumer()
    consumer.run()
