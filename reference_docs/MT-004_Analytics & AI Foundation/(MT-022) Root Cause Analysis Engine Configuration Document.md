# (MT-022) Root Cause Analysis Engine Configuration Document

# 1. Overview

Root Cause Analysis Engine (RCA Engine) bertugas:

* Mengidentifikasi domain penyebab utama anomaly
* Melakukan ranking probabilistik root cause
* Merekonstruksi jalur propagasi kausal
* Memonitor stabilitas RCA dari waktu ke waktu
* Memberikan Governance signal terhadap kualitas inference

Engine bekerja setelah:

* Anomaly Detection Engine
* Drift Detection
* Domain Abstraction
* Temporal Correlation Engine



***

# 2. RCA Output Contract

File:

`dcim_ai/root_cause/rca_models.py`

## RootCauseResult Structure

```python
@dataclass
class RootCauseResult:
    incident_id: str
    timestamp: datetime
    domain_probabilities: Dict[str, float]
    root_domain: str
    ranked_domains: List[str]
    causal_chain: List[str]
    impact_domains: List[str]
    confidence: float
    explanation: str
    metadata: Dict[str, Any]
```

## Entropy Calculation

```python
def entropy(self):
    probs = np.array(list(self.domain_probabilities.values()))
    return float(-np.sum(probs * np.log(probs + 1e-12)))
```



***

# 3. RCA Engine Configuration

File:

`dcim_ai/root_cause/rca_engine.py`

## Softmax Normalization

```python
@staticmethod
def _softmax(scores):
    values = np.array(list(scores.values()))
    exp = np.exp(values - np.max(values))
    probs = exp / exp.sum()
    return dict(zip(scores.keys(), probs))
```

## Composite Root Score Formula

```
root_score =
    0.30 * topology_score
  + 0.25 * domain_strength
  + 0.20 * persistence_ratio
  + 0.10 * trend_weight
  + 0.10 * anomaly_ratio
  + 0.05 * drift_ratio
```

## Configuration Constants

```python
WEIGHTS = {
    "topology": 0.30,
    "strength": 0.25,
    "persistence": 0.20,
    "trend": 0.10,
    "anomaly": 0.10,
    "drift": 0.05
}
```



***

# 4. Causal Topology Configuration

File:

`dcim_ai/root_cause/topology_manager.py`

## Example Dependency Graph

```python
TOPOLOGY = {
    "storage": ["compute"],
    "compute": ["memory"],
    "memory": [],
    "network": ["compute"]
}
```

## Topology Score Formula

```
topology_score =
    downstream_weight * 0.6
  + upstream_weight * 0.4
```



***

# 5. Causal Chain Reconstruction Config

## Chain Algorithm

* DFS traversal
* Max depth = 3
* Cycle safe
* Active domain filter
* Probability pruning

```python
MIN_CHAIN_PROB = 0.15
MAX_CHAIN_DEPTH = 3
```

## Chain Builder Code

```python
def _build_causal_chain(root, active, probs):

    visited = set()
    chain = []

    def dfs(domain, depth=0):
        if depth > MAX_CHAIN_DEPTH:
            return
        if domain in visited:
            return
        visited.add(domain)

        if probs.get(domain, 0) < MIN_CHAIN_PROB:
            return

        if domain in active:
            chain.append(domain)

        for nxt in topology.get(domain, []):
            dfs(nxt, depth + 1)

    dfs(root)
    return chain
```

***

# 6. Lifecycle Manager Configuration

File:

`dcim_ai/root_cause/lifecycle_manager.py`

## Lifecycle Window

```python
WINDOW_SIZE = 20
```

Digunakan untuk:

* Root stability tracking
* Confidence averaging
* Entropy averaging

## Stability Score Formula (Final Enterprise Version)

```
stability_score =
    0.5 * root_stability
  + 0.3 * avg_confidence
  + 0.2 * entropy_penalty
```

## Entropy Normalization

```python
max_entropy = np.log(domain_count)
normalized_entropy = avg_entropy / max_entropy
entropy_penalty = 1 - (normalized_entropy ** 1.5)
```

## Governance Thresholds

```python
SHIFT_THRESHOLD = 3
CONFIDENCE_THRESHOLD = 0.4
ENTROPY_THRESHOLD = 1.2
```

## Governance Severity Bands

```python
if score >= 0.75:
    stable
elif score >= 0.5:
    moderate
else:
    unstable
```

***

# 7. Integration with Correlation Engine

File:

`dcim_ai/correlation/correlation_engine.py`

## RCA Invocation

```python
rca_result = RCAEngine.analyze(incident)
incident["root_cause"] = rca_result.to_dict()

lifecycle_manager.update(rca_result)
incident["root_cause_lifecycle"] = {
    **lifecycle_manager.summary(),
    "governance": lifecycle_manager.governance_status()
}
```

***

# 8. Database Persistence Config

Table:

```sql
incident_root_causes
```

## Table Schema

```sql
CREATE TABLE incident_root_causes (
    incident_id TEXT PRIMARY KEY,
    root_domain TEXT,
    confidence FLOAT,
    entropy FLOAT,
    domain_probabilities JSONB,
    causal_chain JSONB,
    explanation TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

***

# 9. RCA Response Payload Example

```json
{
  "root_domain": "storage",
  "confidence": 0.33,
  "entropy": 1.34,
  "causal_chain": ["storage","compute","memory"],
  "governance_flag": true,
  "stability_score": 0.60,
  "severity_level": "moderate"
}
```



***

# 10. Operational Interpretation

| Scenario                      | Meaning              |
| ----------------------------- | -------------------- |
| High confidence + low entropy | clear root           |
| Low confidance + high entropy | multi-domain failure |
| Root shift high               | unstable system      |
| Stability score low           | RCA unreliable       |
| Governance flag true          | investigation needed |
