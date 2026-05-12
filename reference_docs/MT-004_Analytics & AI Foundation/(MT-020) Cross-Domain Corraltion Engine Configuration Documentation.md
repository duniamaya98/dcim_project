# (MT-020) Cross-Domain Corraltion Engine Configuration Documentation

Brush Stroke

# 1. Domain Abstraction & Corretion Design

## Objective

Membangun lapisan abstraksi domain untuk mentransformasikan telemetry mentah menjadi entitas domain logis sehingga sistem dapat memahami gangguan pada level infrastruktur, bukan hanya pada level fitur individual. [(MT-020) Cross-Domain Correlation Engine](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/dnYp6l89De)

## 1.1. Domain Mapping Configuration

File konfigurasi:

`dcim_ai/config/domain_mapping.py`

DOMAIN\_FEATURE\_MAP

Mapping fitur telemetry ke domain infrastruktur.

```python
DOMAIN_FEATURE_MAP = {

    "compute": [
        "cpu_usage"
    ],

    "memory": [
        "memory_usage"
    ],

    "storage": [
        "disk_io"
    ],

    "network": [
        "net_rx",
        "net_tx"
    ],

    "power": [],

    "cooling": []
}
```

Fungsi:

* Mengelompokan metric menjadi domain logis
* Digunakan oleh DomainEngine untuk menghitung domain\_score
* Memungkinkan analisis cross-domain correlation

## 1.2. Domain Engine Implementation

File:

`dcim_ai/domain/domain_engine.py`

Code:

```python
from dataclasses import dataclass
from dcim_ai.config.domain_mapping import DOMAIN_FEATURE_MAP

@dataclass
class DomainState:

    domain_scores: dict
    active_domains: list
    domain_strength_index: float


class DomainEngine:

    def __init__(self, activation_threshold=3.0):
        self.activation_threshold = activation_threshold

    def compute(self, feature_z_scores):

        domain_scores = {}

        for domain, features in DOMAIN_FEATURE_MAP.items():

            scores = [
                abs(feature_z_scores[f])
                for f in features
                if f in feature_z_scores
            ]

            domain_scores[domain] = max(scores) if scores else 0

        active_domains = [
            d for d, score in domain_scores.items()
            if score >= self.activation_threshold
        ]

        domain_strength_index = sum(domain_scores.values())

        return DomainState(
            domain_scores=domain_scores,
            active_domains=active_domains,
            domain_strength_index=domain_strength_index
        )
```

## Domain Parameters

| Parameter               | Fungsi                         |
| ----------------------- | ------------------------------ |
| activation\_threshold   | Threshold aktivasi domain      |
| domain\_scores          | Drift magnitude per domain     |
| active\_domain          | Domain yang melewati threshold |
| domain\_strength\_index | Total gangguan lintas domain   |



***

# 2. Correlation Feature Aggregation

## Objective

Menambahkan analisis temporal menggunakan rolling window untuk mendeteksi pola anomali jangka pendek. [(MT-020) Cross-Domain Correlation Engine](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/dnYp6l89De)

## 2.1. Correlation Buffer Configuration

File:

`dcim_ai/correlation/correlation_buffer.py`

Code:

```python
import time
from collections import deque


class CorrelationBuffer:

    def __init__(self, window_seconds=300):

        self.window_seconds = window_seconds
        self.buffer = deque()

    def add_snapshot(self, domain_scores, prediction, drift_level):

        self.buffer.append({
            "timestamp": time.time(),
            "domain_scores": domain_scores,
            "prediction": prediction,
            "drift_level": drift_level
        })

        self.cleanup()

    def cleanup(self):

        now = time.time()

        while self.buffer and now - self.buffer[0]["timestamp"] > self.window_seconds:
            self.buffer.popleft()

    def get_buffer(self):
        return list(self.buffer)
```

## Configuration

| Parameter       | Value | Deskripsi              |
| --------------- | ----- | ---------------------- |
| window\_seconds | 300   | Rolling window 5 menit |
| buffer          | deque | Penyimpanan snapshot   |

## 2.2. Aggregation Engine

File:

`dcim_ai/correlation/aggregation_engine.py`

Code:

```python
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class AggregationState:

    window_size: int
    anomaly_ratio: float
    drift_ratio: float
    domain_activity_count: dict
    domain_persistence_ratio: dict
    co_occurrence_matrix: dict
    domain_trend: dict


class AggregationEngine:

    def compute(self, snapshots):

        window_size = len(snapshots)

        if window_size == 0:
            return None

        anomaly_count = sum(
            1 for s in snapshots
            if s["prediction"] == -1
        )

        drift_count = sum(
            1 for s in snapshots
            if s["drift_level"] == "severe_drift"
        )

        anomaly_ratio = anomaly_count / window_size
        drift_ratio = drift_count / window_size

        domain_activity = defaultdict(int)

        for s in snapshots:
            for d, score in s["domain_scores"].items():
                if score > 3:
                    domain_activity[d] += 1

        domain_persistence_ratio = {
            d: count / window_size
            for d, count in domain_activity.items()
        }

        return AggregationState(
            window_size=window_size,
            anomaly_ratio=anomaly_ratio,
            drift_ratio=drift_ratio,
            domain_activity_count=dict(domain_activity),
            domain_persistence_ratio=domain_persistence_ratio,
            co_occurrence_matrix={},
            domain_trend={}
        )
```

## Aggregation Metrics

| Parameter                  | Fungsi                       |
| -------------------------- | ---------------------------- |
| window\_size               | Jumlah snapshot dalam window |
| anolamy\_ratio             | Rasio anomaly                |
| drift\_ratio               | Rasio severe drift           |
| domain\_activity\_count    | Frekuensi domain aktif       |
| domain\_persistence\_ratio | Persistensi domain           |



***

# 3. Correlation Engine Core

## Objective

Menggabungkan snapshot anomaly, domain state, dan temporal aggregation menjadi incident terstruktur. [(MT-020) Cross-Domain Correlation Engine](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/dnYp6l89De)

## 3.1. Correlation Engine

File:

`dcim_ai/correlation/correlation_engine.py`

Code:

```python
import uuid
import time


class CorrelationEngine:

    def evaluate(self, domain_state, aggregation_state, snapshot_severity):

        severity = snapshot_severity

        if aggregation_state:

            if aggregation_state.anomaly_ratio >= 0.8:
                severity = "critical"

            elif aggregation_state.anomaly_ratio >= 0.5:
                severity = "warning"

        confidence = min(
            1.0,
            aggregation_state.anomaly_ratio +
            aggregation_state.drift_ratio
        )

        return {

            "incident_id": str(uuid.uuid4()),

            "timestamp": int(time.time()),

            "severity": severity,

            "confidence": confidence,

            "active_domains": domain_state.active_domains,

            "root_cause_hint":
                "multi_domain_interaction"
                if len(domain_state.active_domains) >= 2
                else "single_domain_issue"
        }
```

## Incident Output Structure

```json
{
  "incident_id": "...",
  "timestamp": 1771836136,
  "severity": "critical",
  "confidence": 1.0,
  "active_domains": ["compute","memory"],
  "root_cause_hint": "multi_domain_interaction"
}
```



***

# 4. Integration with Inference & Registry

## Objective

Menyatukan correlation engine dengan lifecycle model registry. [(MT-020) Cross-Domain Correlation Engine](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/dnYp6l89De)

## 4.1. Registry Configuration

File:

`dcim_ai/registry/registry.json`

Configuration:

```json
{
  "current_production": "v1.4",

  "available_models": [
    "v1.0",
    "v1.1",
    "v1.2",
    "v1.3",
    "v1.4"
  ],

  "correlation_config": {

    "correlation_version": "c1.0",

    "correlation_strategy": "temporal_multi_domain_v1",

    "severity_matrix_version": "sm1"
  }
}
```

## 4.2. Model Manager Integration

File:

`dcim_ai/inference/model_manager.py`

Load registry metadata:

```python
def get(self):

    registry = load_registry()

    correlation_config = registry.get(
        "correlation_config",
        {}
    )

    return (
        self.models,
        self.pipeline,
        self.baseline_stats,
        registry["current_production"],
        correlation_config
    )
```

## 4.3. Inference Integration

File:

`dcim_ai/api/inference_service.py`

Correlation integration:

```python
correlation_buffer.add_snapshot(
    domain_scores=domain_scores,
    prediction=-1 if final_prediction == "anomaly" else 1,
    drift_level=drift_status
)

aggregation_state = aggregation_engine.compute(
    correlation_buffer.get_buffer()
)

incident = correlation_engine.evaluate(
    domain_state,
    aggregation_state,
    severity
)
```

## API Response Extention

```json
{
 "correlation_version": "c1.0",
 "correlation_strategy": "temporal_multi_domain_v1",
 "incident": {...}
}
```



***

# 5. Monitoring Configuration

## Prometheus Metrics

Monitoring metrics:

```python
CORRELATION_INCIDENT_TOTAL = Counter(
 "dcim_correlation_incidents_total"
)

CRITICAL_INCIDENT_TOTAL = Counter(
 "dcim_critical_incidents_total"
)

MULTI_DOMAIN_INCIDENT_TOTAL = Counter(
 "dcim_multi_domain_incidents_total"
)

CORRELATION_CONFIDENCE = Histogram(
 "dcim_correlation_confidence"
)

DOMAIN_ACTIVITY_GAUGE = Gauge(
 "dcim_domain_active_count"
)

ANOMALY_RATIO_GAUGE = Gauge(
 "dcim_temporal_anomaly_ratio"
)
```



***

# 6. Automation Configuration

## Retrain Trigger

```python
if aggregation_state.anomaly_ratio >= 0.8:
    trigger_retraining()
```

## Drift Trigger

```python
if drift_status == "severe_drift":
    trigger_retraining()
```



***

# 7. Testing Configuration

Testing coverage:

```
tests/
   test_domain_engine.py
   test_aggregation_engine.py
   test_correlation_engine.py
```

Integration test:

```
POST /predict
GET /metrics
```



***

# Final System Configuration

System sekarang memiliki:

* Feature-level anomaly detection [(MT-019) Anomaly Detection Framework](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep)
* Multi-model ensemble detection [(MT-018) Traditional Machine Learning Model](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/I44pKpyLLU9mmFHCLBRgw)
* Domain abstraction intelligence [(MT-020) Cross-Domain Correlation Engine](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/dnYp6l89De)
* Temporal anomaly correlation
* Incident-aware registry integration
* Observability via Prometheus

Architecture:

Adaptive Multi-Domain Temporal Incident Platform.



***

