"""
Kafka Consumer Base Class

Reusable consumer with error handling, retry, DLQ support.
"""

import logging
from typing import Callable, Optional, Dict, Any
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import json
import time

logger = logging.getLogger(__name__)


class BaseKafkaConsumer:
    """Base Kafka Consumer with built-in error handling"""

    def __init__(
        self,
        topic: str,
        bootstrap_servers: str,
        group_id: str,
        dlq_topic: Optional[str] = None,
        auto_commit: bool = False,
        value_deserializer: Optional[Callable] = None
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.dlq_topic = dlq_topic
        self.auto_commit = auto_commit

        # Default JSON deserializer
        if value_deserializer is None:
            value_deserializer = lambda m: json.loads(m.decode('utf-8'))

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            enable_auto_commit=auto_commit,
            value_deserializer=value_deserializer,
            auto_offset_reset='earliest',
            max_poll_records=100,
            # Prevent metadata refresh that causes localhost redirect
            metadata_max_age_ms=300000,  # 5 minutes
            connections_max_idle_ms=540000,  # 9 minutes
            request_timeout_ms=60000  # 60 seconds
        )

        # DLQ producer (lazy init)
        self._dlq_producer = None

        logger.info(f"Consumer initialized: topic={topic}, group={group_id}")

    def _get_dlq_producer(self):
        """Lazy init DLQ producer"""
        if self._dlq_producer is None and self.dlq_topic:
            self._dlq_producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        return self._dlq_producer

    def send_to_dlq(self, message: Any, error: str):
        """Send failed message to Dead Letter Queue"""
        if not self.dlq_topic:
            logger.warning("DLQ topic not configured, dropping failed message")
            return

        producer = self._get_dlq_producer()
        if producer:
            dlq_payload = {
                "original_message": message.value if hasattr(message, 'value') else message,
                "error": str(error),
                "timestamp": time.time(),
                "topic": self.topic,
                "partition": message.partition if hasattr(message, 'partition') else None,
                "offset": message.offset if hasattr(message, 'offset') else None
            }
            producer.send(self.dlq_topic, dlq_payload)
            producer.flush()
            logger.info(f"Sent message to DLQ: {self.dlq_topic}")

    def process_message(self, message: Any) -> bool:
        """
        Override this method in subclass to process messages.
        Return True if successful, False to retry or send to DLQ.
        """
        raise NotImplementedError("Subclass must implement process_message()")

    def run(self, max_retries: int = 3):
        """
        Run consumer loop with retry logic.

        Args:
            max_retries: Number of retries before sending to DLQ
        """
        logger.info(f"Starting consumer loop for topic: {self.topic}")

        try:
            for message in self.consumer:
                retry_count = 0
                success = False

                while retry_count < max_retries and not success:
                    try:
                        success = self.process_message(message)

                        if success:
                            # Commit offset if manual commit
                            if not self.auto_commit:
                                self.consumer.commit()
                        else:
                            retry_count += 1
                            if retry_count < max_retries:
                                logger.warning(f"Retry {retry_count}/{max_retries} for message")
                                time.sleep(2 ** retry_count)  # Exponential backoff

                    except Exception as e:
                        logger.error(f"Error processing message: {e}", exc_info=True)
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(2 ** retry_count)

                # After all retries failed, send to DLQ
                if not success:
                    logger.error(f"Message failed after {max_retries} retries, sending to DLQ")
                    self.send_to_dlq(message, "Max retries exceeded")

        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            self.close()

    def close(self):
        """Close consumer and producer connections"""
        logger.info("Closing consumer")
        self.consumer.close()
        if self._dlq_producer:
            self._dlq_producer.close()
