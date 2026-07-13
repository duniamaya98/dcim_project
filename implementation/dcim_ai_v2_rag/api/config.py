"""
Configuration module for Analytics & AI Engine API
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    # Database Configuration
    TIMESCALEDB_HOST: str = os.getenv("TIMESCALEDB_HOST", "10.70.0.56")
    TIMESCALEDB_PORT: int = int(os.getenv("TIMESCALEDB_PORT", "5433"))
    TIMESCALEDB_DATABASE: str = os.getenv("TIMESCALEDB_DATABASE", "dcim_analytics")
    TIMESCALEDB_USER: str = os.getenv("TIMESCALEDB_USER", "ai_team")
    TIMESCALEDB_PASSWORD: str = os.getenv("TIMESCALEDB_PASSWORD", "")

    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "10.70.0.56:9092")
    KAFKA_CONSUMER_GROUP: str = os.getenv("KAFKA_CONSUMER_GROUP", "ai-team-consumer")

    # Topics
    KAFKA_TOPIC_METRICS: str = "dcim.analytics.metrics"
    KAFKA_TOPIC_ENRICHED: str = "dcim.enriched.events"
    KAFKA_TOPIC_ANOMALIES: str = "dcim.analytics.anomalies"
    KAFKA_TOPIC_PREDICTIONS: str = "dcim.analytics.predictions"
    KAFKA_TOPIC_RCA: str = "dcim.analytics.rca"
    KAFKA_TOPIC_CAPACITY: str = "dcim.analytics.capacity"
    KAFKA_TOPIC_ENERGY: str = "dcim.analytics.energy"

    # Redis Configuration (optional, for caching)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "3"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    # Model Registry
    MODEL_REGISTRY_PATH: str = os.getenv("MODEL_REGISTRY_PATH", "/opt/dcim/models")

    # Authentication (placeholder - integrate with IAM later)
    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "false").lower() == "true"
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")

    # Performance Limits
    MAX_PAGE_SIZE: int = 100
    DEFAULT_PAGE_SIZE: int = 25

    # Anomaly Detection
    ANOMALY_ZSCORE_THRESHOLD: float = 3.0
    ANOMALY_WINDOW_SIZE: int = 100

    # RCA
    RCA_TIMEOUT_SECONDS: int = 30
    RCA_TOPOLOGY_DEPTH: int = 3

    # LLM/RAG
    LLM_BACKEND: str = os.getenv("LLM_BACKEND", "local")  # local, openai, claude
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5-3b-instruct")
    LLM_TIMEOUT_SECONDS: int = 10

    @field_validator("DEBUG", mode="before")
    @classmethod

    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return value

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
