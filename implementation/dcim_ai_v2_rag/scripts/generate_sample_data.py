#!/usr/bin/env python3
"""
Sample Data Generator for DCIM Block 7 Analytics & AI Engine

Generates realistic synthetic metrics data with anomaly patterns for:
1. Direct TimescaleDB insertion (for API testing)
2. Kafka publish (dcim.analytics.metrics) for stream processing testing
3. JSON file export (offline use)

Usage:
    python generate_sample_data.py                          # Default: TimescaleDB, 1 hour, 10s interval
    python generate_sample_data.py --output kafka           # Publish to Kafka
    python generate_sample_data.py --output file            # Export to JSON
    python generate_sample_data.py --hours 24 --output all  # 24h data, all outputs

Metrics generated:
    - cpu_usage_percent       (server domain)
    - memory_usage_percent    (server domain)
    - disk_io_percent         (server domain)
    - network_throughput_mbps (network domain)
    - disk_usage_percent      (storage domain)
    - temperature_celsius     (cooling domain)
    - power_consumption_watts (power domain)
    - pue_ratio               (energy domain)

Anomaly patterns injected:
    - Spike (sudden abnormal high)
    - Dip (sudden abnormal low)
    - Gradual drift (slow degradation)
    - Oscillation (intermittent failure)

Reference:
    dcim-wiki/reference-designs/block7-analytics-ai-engine.md §2.1, §2.2
    MT-023 §2.1, §2.2
"""

import argparse
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterator, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================================
# Metric Configuration
# ============================================================================

METRIC_DEFINITIONS = {
    "cpu_usage_percent": {
        "unit": "%",
        "domain": "server",
        "normal_range": (5.0, 60.0),
        "mean": 25.0,
        "stddev": 12.0,
        "trend_per_hour": 0.2,
        "ci_prefix": "CI-SRV",
    },
    "memory_usage_percent": {
        "unit": "%",
        "domain": "server",
        "normal_range": (20.0, 80.0),
        "mean": 55.0,
        "stddev": 10.0,
        "trend_per_hour": 0.1,
        "ci_prefix": "CI-SRV",
    },
    "disk_io_percent": {
        "unit": "%",
        "domain": "server",
        "normal_range": (0.0, 40.0),
        "mean": 15.0,
        "stddev": 8.0,
        "trend_per_hour": 0.05,
        "ci_prefix": "CI-SRV",
    },
    "network_throughput_mbps": {
        "unit": "Mbps",
        "domain": "network",
        "normal_range": (10.0, 500.0),
        "mean": 150.0,
        "stddev": 80.0,
        "trend_per_hour": 2.0,
        "ci_prefix": "CI-NET",
    },
    "disk_usage_percent": {
        "unit": "%",
        "domain": "storage",
        "normal_range": (30.0, 90.0),
        "mean": 60.0,
        "stddev": 3.0,
        "trend_per_hour": 0.15,
        "ci_prefix": "CI-STO",
    },
    "temperature_celsius": {
        "unit": "°C",
        "domain": "cooling",
        "normal_range": (18.0, 28.0),
        "mean": 22.0,
        "stddev": 1.5,
        "trend_per_hour": 0.05,
        "ci_prefix": "CI-RACK",
    },
    "power_consumption_watts": {
        "unit": "W",
        "domain": "power",
        "normal_range": (500.0, 5000.0),
        "mean": 2500.0,
        "stddev": 500.0,
        "trend_per_hour": 10.0,
        "ci_prefix": "CI-PDU",
    },
    "pue_ratio": {
        "unit": "ratio",
        "domain": "energy",
        "normal_range": (1.1, 1.8),
        "mean": 1.25,
        "stddev": 0.1,
        "trend_per_hour": 0.001,
        "ci_prefix": "CI-DC",
    },
}

# Anomaly Patterns to Inject
ANOMALY_PATTERNS = [
    {"type": "spike", "multiplier": 3.5, "duration_sec": 120, "ci_idx": 0, "metric": "cpu_usage_percent"},
    {"type": "spike", "multiplier": 2.8, "duration_sec": 90, "ci_idx": 1, "metric": "memory_usage_percent"},
    {"type": "dip", "multiplier": 0.1, "duration_sec": 180, "ci_idx": 2, "metric": "network_throughput_mbps"},
    {"type": "drift", "rate_per_minute": 0.5, "duration_sec": 600, "ci_idx": 0, "metric": "temperature_celsius"},
    {"type": "spike", "multiplier": 4.0, "duration_sec": 60, "ci_idx": 0, "metric": "disk_io_percent"},
    {"type": "oscillation", "amplitude": 3.0, "frequency_sec": 30, "duration_sec": 300, "ci_idx": 1, "metric": "power_consumption_watts"},
    {"type": "drift", "rate_per_minute": 0.3, "duration_sec": 900, "ci_idx": 3, "metric": "disk_usage_percent"},
]

# CI IDs (consistent across metrics)
CI_IDS = [
    str(uuid.UUID("11111111-1111-1111-1111-111111111111")),
    str(uuid.UUID("22222222-2222-2222-2222-222222222222")),
    str(uuid.UUID("33333333-3333-3333-3333-333333333333")),
    str(uuid.UUID("44444444-4444-4444-4444-444444444444")),
    str(uuid.UUID("55555555-5555-5555-5555-555555555555")),
]

ASSET_IDS = [f"AST-00{i+1}" for i in range(5)]


class SampleDataGenerator:
    """Generates synthetic DCIM metrics with realistic patterns and anomalies."""

    def __init__(
        self,
        start_time: datetime = None,
        duration_hours: float = 1.0,
        interval_seconds: int = 10,
        num_cis: int = 3,
    ):
        self.start_time = start_time or datetime.now(timezone.utc) - timedelta(hours=duration_hours)
        self.duration_hours = duration_hours
        self.interval_seconds = interval_seconds
        self.num_cis = num_cis
        self.total_points = int(duration_hours * 3600 / interval_seconds)
        self.generated_count = 0

    def _get_anomaly_multiplier(
        self, timestamp: datetime, metric_name: str, ci_idx: int
    ) -> float:
        """Check if this (timestamp, metric, ci) falls within an anomaly window."""
        for pattern in ANOMALY_PATTERNS:
            if pattern["ci_idx"] != ci_idx:
                continue
            if pattern["metric"] != metric_name:
                continue

            # Anomaly time window: starts at 40% through the time range
            anomaly_start = self.start_time + timedelta(
                hours=self.duration_hours * 0.4
            )
            anomaly_end = anomaly_start + timedelta(seconds=pattern["duration_sec"])

            if not (anomaly_start <= timestamp <= anomaly_end):
                continue

            anomaly_type = pattern["type"]
            elapsed = (timestamp - anomaly_start).total_seconds()

            if anomaly_type == "spike":
                return pattern["multiplier"]
            elif anomaly_type == "dip":
                return pattern["multiplier"]
            elif anomaly_type == "drift":
                drift_amount = elapsed / 60.0 * pattern["rate_per_minute"]
                return max(1.0, 1.0 + drift_amount / 10.0)
            elif anomaly_type == "oscillation":
                import math
                freq = pattern["frequency_sec"]
                return 1.0 + pattern["amplitude"] * math.sin(2 * math.pi * elapsed / freq) / 10.0

        return 1.0

    def generate_metrics(self) -> Iterator[Dict[str, Any]]:
        """Generate metrics one by one as an iterator. Each yield is a Kafka-compatible event."""
        ci_idx_cycle = 0

        for point_idx in range(self.total_points):
            timestamp = self.start_time + timedelta(seconds=point_idx * self.interval_seconds)
            ci_idx = ci_idx_cycle % self.num_cis
            ci_idx_cycle += 1

            for metric_name in sorted(METRIC_DEFINITIONS.keys()):
                # Only generate domain-appropriate metrics for each CI type
                if metric_name == "network_throughput_mbps" and ci_idx > 1:
                    continue
                if metric_name == "pue_ratio" and ci_idx > 0:
                    continue

                cfg = METRIC_DEFINITIONS[metric_name]
                ci_id = CI_IDS[ci_idx]
                asset_id = ASSET_IDS[ci_idx]

                # Base value with noise
                import random
                hours_elapsed = (timestamp - self.start_time).total_seconds() / 3600.0
                base_value = cfg["mean"] + cfg["trend_per_hour"] * hours_elapsed
                noise = random.gauss(0, cfg["stddev"])
                value = base_value + noise

                # Apply anomaly modifier
                anomaly_mult = self._get_anomaly_multiplier(timestamp, metric_name, ci_idx)
                if anomaly_mult != 1.0 and anomaly_mult < 0.2:
                    value = cfg["normal_range"][0] * anomaly_mult * 2
                else:
                    value *= anomaly_mult

                # Ensure minimum values
                value = max(0.01, value)

                # Build event
                event = {
                    "timestamp": timestamp.isoformat(),
                    "metric_name": metric_name,
                    "ci_id": ci_id,
                    "asset_id": asset_id,
                    "source_system": "sample_data_generator",
                    "payload": {
                        "value": round(value, 4),
                        "unit": cfg["unit"],
                    },
                    "metadata": {
                        "domain": cfg["domain"],
                        "tags": {
                            "environment": "staging",
                            "generator": "sample_data",
                            "ci_index": ci_idx,
                        },
                    },
                }

                yield event
                self.generated_count += 1

    def to_json_file(self, output_path: str) -> str:
        """Write all metrics to a JSON lines file."""
        with open(output_path, "w") as f:
            for event in self.generate_metrics():
                f.write(json.dumps(event) + "\n")
        logger.info(f"Exported {self.generated_count} events to {output_path}")
        return output_path

    def to_timescaledb(self, db_config: Dict[str, str]) -> int:
        """Insert metrics directly into TimescaleDB."""
        import psycopg2
        from psycopg2.extras import execute_values

        conn = psycopg2.connect(**db_config)
        inserted = 0

        try:
            batch = []
            for event in self.generate_metrics():
                payload = event["payload"]
                tags = event.get("metadata", {}).get("tags", {})

                batch.append((
                    event["timestamp"],
                    event["metric_name"],
                    event.get("ci_id"),
                    event.get("asset_id"),
                    event["source_system"],
                    float(payload["value"]),
                    payload.get("unit"),
                    json.dumps(tags),
                ))

                if len(batch) >= 500:
                    with conn.cursor() as cur:
                        execute_values(cur, """
                            INSERT INTO metrics (time, metric_name, ci_id, asset_id, source, value, unit, tags)
                            VALUES %s
                            ON CONFLICT DO NOTHING
                        """, batch)
                    conn.commit()
                    inserted += len(batch)
                    logger.info(f"Inserted {inserted} metrics...")
                    batch = []

            # Flush remaining
            if batch:
                with conn.cursor() as cur:
                    execute_values(cur, """
                        INSERT INTO metrics (time, metric_name, ci_id, asset_id, source, value, unit, tags)
                        VALUES %s
                        ON CONFLICT DO NOTHING
                    """, batch)
                conn.commit()
                inserted += len(batch)

        finally:
            conn.close()

        logger.info(f"Total inserted: {inserted} metrics into TimescaleDB")
        return inserted

    def to_kafka(self, producer, batch_size: int = 100) -> int:
        """Publish metrics to Kafka topic."""
        success = 0
        batch = []

        for event in self.generate_metrics():
            batch.append(event)
            if len(batch) >= batch_size:
                success += producer.publish_batch(batch, key_field="ci_id")
                batch = []
                time.sleep(0.1)  # Rate limiting

        if batch:
            success += producer.publish_batch(batch, key_field="ci_id")

        producer.flush()
        logger.info(f"Published {success} events to Kafka topic {producer.topic}")
        return success


def main():
    parser = argparse.ArgumentParser(
        description="Generate sample DCIM metrics data for Block 7 Analytics & AI"
    )
    parser.add_argument(
        "--output",
        choices=["db", "kafka", "file", "all"],
        default="file",
        help="Output target (default: file)",
    )
    parser.add_argument(
        "--hours", type=float, default=1.0,
        help="Hours of data to generate (default: 1.0)",
    )
    parser.add_argument(
        "--interval", type=int, default=10,
        help="Seconds between data points (default: 10)",
    )
    parser.add_argument(
        "--ci-count", type=int, default=3, dest="ci_count",
        help="Number of CIs to simulate (default: 3)",
    )
    parser.add_argument(
        "--db-host", default=os.getenv("TIMESCALEDB_HOST", "10.70.0.56"),
    )
    parser.add_argument(
        "--db-port", type=int, default=int(os.getenv("TIMESCALEDB_PORT", "5433")),
    )
    parser.add_argument(
        "--db-name", default=os.getenv("TIMESCALEDB_DATABASE", "dcim_analytics"),
    )
    parser.add_argument(
        "--db-user", default=os.getenv("TIMESCALEDB_USER", "ai_team"),
    )
    parser.add_argument(
        "--db-password",
        default=os.getenv("TIMESCALEDB_PASSWORD", ""),
    )
    parser.add_argument(
        "--output-file", default=None,
        help="Output JSON file path (default: auto-generated)",
    )

    args = parser.parse_args()

    generator = SampleDataGenerator(
        duration_hours=args.hours,
        interval_seconds=args.interval,
        num_cis=args.ci_count,
    )

    output = args.output
    filename = args.output_file or f"sample_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    filepath = os.path.join(os.path.dirname(__file__) or ".", filename)

    results = {}

    if output in ("db", "all"):
        db_config = {
            "host": args.db_host,
            "port": args.db_port,
            "database": args.db_name,
            "user": args.db_user,
            "password": args.db_password,
        }
        try:
            inserted = generator.to_timescaledb(db_config)
            results["timescaledb"] = inserted
        except Exception as e:
            logger.warning(f"TimescaleDB insert failed: {e}")

    if output in ("kafka", "all"):
        try:
            from producers import BaseKafkaProducer
            producer = BaseKafkaProducer(topic="dcim.analytics.metrics")
            published = generator.to_kafka(producer)
            results["kafka"] = published
            producer.close()
        except ImportError:
            logger.error("kafka-python not installed. Skipping Kafka output.")
        except Exception as e:
            logger.warning(f"Kafka publish failed: {e}")

    if output in ("file", "all"):
        filepath = generator.to_json_file(filepath)
        results["file"] = filepath

    # Summary
    print(f"\n{'='*60}")
    print(f"  Sample Data Generation Complete")
    print(f"  Total events: {generator.generated_count:,}")
    print(f"  Time range: {generator.start_time.isoformat()} → "
          f"{(generator.start_time + timedelta(hours=args.hours)).isoformat()}")
    for target, result in results.items():
        print(f"  {target}: {result}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
