"""
Base Kafka Producer

Provides base class for publishing to dcim.analytics.* output topics.

Reference:
- dcim-wiki/reference-designs/block7-analytics-ai-engine.md §2.2
- dcim-wiki/reference-designs/block7-analytics-ai-engine-technical-requirements.md §2.3
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class BaseKafkaProducer:
    """
    Base Kafka producer for Block 7 Analytics & AI output topics.

    Publishes structured JSON to dcim.analytics.* topics.
    """

    def __init__(
        self,
        topic: str,
        bootstrap_servers: str = None,
        client_id: str = None,
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "10.70.0.56:9092"
        )
        self.client_id = client_id or f"dcim-analytics-producer-{topic.replace('.', '-')}"
        self.producer: Optional[KafkaProducer] = None
        self._connect()

    def _connect(self):
        """Establish Kafka producer connection"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers.split(","),
                client_id=self.client_id,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",  # Wait for all replicas (durability)
                retries=3,
                max_in_flight_requests_per_connection=1,  # Ordering guarantee
                compression_type="gzip",
            )
            logger.info(
                f"Kafka producer connected: {self.bootstrap_servers} → {self.topic}"
            )
        except Exception as e:
            logger.error(f"Failed to create Kafka producer for {self.topic}: {e}")
            raise

    def publish(
        self,
        value: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        sync: bool = False,
    ) -> bool:
        """
        Publish message to Kafka topic.

        Args:
            value: Message body (dict, will be JSON-serialized)
            key: Optional partitioning key (e.g., ci_id, incident_id)
            headers: Optional Kafka message headers
            sync: If True, wait for ack (slower but guaranteed). Default async (fire-and-forget).

        Returns:
            True if queued/accepted, False if error
        """
        if self.producer is None:
            logger.error("Producer not connected")
            return False

        # Add metadata
        value["_producer"] = self.client_id
        value["_produced_at"] = datetime.now(timezone.utc).isoformat()

        try:
            kafka_headers = [
                (k, v.encode("utf-8")) for k, v in (headers or {}).items()
            ]

            future = self.producer.send(
                topic=self.topic,
                value=value,
                key=key,
                headers=kafka_headers,
            )

            if sync:
                record_metadata = future.get(timeout=10)
                logger.debug(
                    f"Published to {self.topic} partition {record_metadata.partition} "
                    f"offset {record_metadata.offset}"
                )
            return True

        except KafkaError as e:
            logger.error(f"Kafka error publishing to {self.topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing to {self.topic}: {e}")
            return False

    def publish_batch(
        self,
        messages: list[Dict[str, Any]],
        key_field: str = "id",
    ) -> int:
        """Publish batch of messages. Returns count of successful sends."""
        success_count = 0
        for msg in messages:
            key = msg.get(key_field, None)
            if self.publish(msg, key=key):
                success_count += 1
        logger.info(
            f"Batch published to {self.topic}: {success_count}/{len(messages)} succeeded"
        )
        return success_count

    def flush(self):
        """Wait for all buffered messages to be delivered"""
        if self.producer:
            self.producer.flush(timeout=30)

    def close(self):
        """Flush and close producer"""
        if self.producer:
            logger.info(f"Flushing and closing producer for {self.topic}")
            self.producer.flush(timeout=30)
            self.producer.close(timeout=10)
            self.producer = None


# ---------------------------------------------------------------------------
# Topic-specific producer factories
# ---------------------------------------------------------------------------

class AnomalyProducer(BaseKafkaProducer):
    """Publish anomaly events to dcim.analytics.anomalies"""
    def __init__(self, **kwargs):
        topic = os.getenv("KAFKA_TOPIC_ANOMALIES", "dcim.analytics.anomalies")
        super().__init__(topic=topic, client_id="dcim-analytics-producer-anomalies", **kwargs)


class PredictionProducer(BaseKafkaProducer):
    """Publish predictions to dcim.analytics.predictions"""
    def __init__(self, **kwargs):
        topic = os.getenv("KAFKA_TOPIC_PREDICTIONS", "dcim.analytics.predictions")
        super().__init__(topic=topic, client_id="dcim-analytics-producer-predictions", **kwargs)


class RCAProducer(BaseKafkaProducer):
    """Publish RCA results to dcim.analytics.rca"""
    def __init__(self, **kwargs):
        topic = os.getenv("KAFKA_TOPIC_RCA", "dcim.analytics.rca")
        super().__init__(topic=topic, client_id="dcim-analytics-producer-rca", **kwargs)


class CapacityProducer(BaseKafkaProducer):
    """Publish capacity forecasts to dcim.analytics.capacity"""
    def __init__(self, **kwargs):
        topic = os.getenv("KAFKA_TOPIC_CAPACITY", "dcim.analytics.capacity")
        super().__init__(topic=topic, client_id="dcim-analytics-producer-capacity", **kwargs)


class EnergyProducer(BaseKafkaProducer):
    """Publish energy reports to dcim.analytics.energy"""
    def __init__(self, **kwargs):
        topic = os.getenv("KAFKA_TOPIC_ENERGY", "dcim.analytics.energy")
        super().__init__(topic=topic, client_id="dcim-analytics-producer-energy", **kwargs)


__all__ = [
    "BaseKafkaProducer",
    "AnomalyProducer",
    "PredictionProducer",
    "RCAProducer",
    "CapacityProducer",
    "EnergyProducer",
]
