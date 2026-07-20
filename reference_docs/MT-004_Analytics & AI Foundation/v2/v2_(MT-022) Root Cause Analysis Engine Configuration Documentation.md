---
title: "(MT-022) Root Cause Analysis Engine Configuration Documentation"
created: 2026-05-20
updated: 2026-07-10
version: 2.0
type: configuration-document
task_id: MT-022
block: 7
assignee: Fakhri Aulia R
status: done
dcim_wiki_section: "5. Root Cause Analysis (RCA)"
tags:
  - rca
  - root-cause-analysis
  - configuration
  - topology
  - scoring
  - lifecycle
  - governance
  - database
  - dcim-ai
---

# (MT-022) Root Cause Analysis Engine Configuration Documentation

> **Version 2.0** — Restrukturisasi lengkap dengan dcim-wiki alignment, actual code location, dan improved structure.

---

## Daftar Isi

1. [Overview](#1-overview)
2. [RCA Output Contract](#2-rca-output-contract)
3. [RCA Engine Configuration](#3-rca-engine-configuration)
4. [Causal Topology Configuration](#4-causal-topology-configuration)
5. [Causal Chain Reconstruction Config](#5-causal-chain-reconstruction-config)
6. [Lifecycle Manager Configuration](#6-lifecycle-manager-configuration)
7. [Integration with Correlation Engine](#7-integration-with-correlation-engine)
8. [Database Persistence Config](#8-database-persistence-config)
9. [RCA Response Payload Example](#9-rca-response-payload-example)
10. [Operational Interpretation](#10-operational-interpretation)
11. [dcim-wiki Alignment](#11-dcim-wiki-alignment)
12. [Actual Code Location](#12-actual-code-location)

---

## 1. Overview

Root Cause Analysis Engine (RCA Engine) bertugas:

* Mengidentifikasi domain penyebab utama anomaly
* Melakukan ranking probabilistic root cause
* Merekonstruksi jalur propagasi kausal
* Memonitor stabilitas RCA dari waktu ke waktu
* Memberikan Governance signal terhadap kualitas inference

### Pipeline Flow

```
Incident/Anomaly Detected
  → Anomaly Detection Engine
  → Drift Detection
  → Domain Abstraction
  → Temporal Correlation Engine
  → RCA Engine (analyze / analyze_forward / analyze_hybrid)
  → Root Cause Result + Governance Output
```

### RCA Modes

| Mode | Fungsi | Trigger |
| --- | --- | --- |
| `reactive` | RCA terhadap incident yang sudah terjadi | Default — incident dari correlation engine |
| `forward` | RCA terhadap projected incident dari forecast | Forecast output UC1 (MT-019/MT-021) |
| `hybrid` | Weighted merge reactive + forward | Early warning — `(1-w)·reactive + w·forward` |

---

## 2. RCA Output Contract

**File:** `dcim_ai/root_cause/rca_models.py`

### RootCauseResult Structure

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

### Extended Fields (v1.2.0)

```python
    mode: str = 'reactive'                    # 'reactive' | 'forward' | 'hybrid'
    forecast_horizon_h: Optional[int] = None   # 24 atau 48 (untuk forward/hybrid)
    forecast_confidence: Optional[float] = None # confidence dari forecast model
    asset_context: Optional[dict] = None        # AssetContext enrichment
    governance: Optional[dict] = None           # Governance flags & scores
```

### Entropy Calculation

```python
def entropy(self):
    probs = np.array(list(self.domain_probabilities.values()))
    return float(-np.sum(probs * np.log(probs + 1e-12)))
```

---

## 3. RCA Engine Configuration

**File:** `dcim_ai/root_cause/rca_engine.py`

### Softmax Normalization

```python
@staticmethod
def _softmax(scores):
    values = np.array(list(scores.values()))
    exp = np.exp(values - np.max(values))
    probs = exp / exp.sum()
    return dict(zip(scores.keys(), probs))
```

### Composite Root Score Formula

```
root_score =
    0.30 * topology_score
  + 0.25 * domain_strength
  + 0.20 * persistence_ratio
  + 0.10 * trend_weight
  + 0.10 * anomaly_ratio
  + 0.05 * drift_ratio
```

### Configuration Constants

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

### RCA Mode Enum

```python
class RCAMode(Enum):
    REACTIVE = 'reactive'      # incident yang sudah terjadi
    FORWARD  = 'forward'       # projected incident dari forecast
    HYBRID   = 'hybrid'        # weighted merge keduanya
```

---

## 4. Causal Topology Configuration

**File:** `dcim_ai/root_cause/topology_manager.py`

### Default Dependency Graph

```python
TOPOLOGY = {
    "storage": ["compute"],
    "compute": ["memory"],
    "memory": [],
    "network": ["compute"]
}
```

### Extended Topology (v1.2.0 — UC1/UC3)

Disinkronkan dengan MT-020 §6.7:

```
power    → compute
power    → cooling
cooling  → compute
cooling  → memory
cooling  → storage
hardware → storage
hardware → compute
storage  → compute
compute  → memory
network  → compute
```

### Topology Score Formula

```
topology_score =
    downstream_weight * 0.6
  + upstream_weight * 0.4
```

---

## 5. Causal Chain Reconstruction Config

### Chain Algorithm

* DFS traversal
* Max depth = 3
* Cycle safe
* Active domain filter
* Probability pruning

### Configuration Constants

```python
MIN_CHAIN_PROB = 0.15
MAX_CHAIN_DEPTH = 3
```

### Chain Builder Code

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

---

## 6. Lifecycle Manager Configuration

**File:** `dcim_ai/root_cause/lifecycle_manager.py`

### Lifecycle Window

```python
WINDOW_SIZE = 20
```

Digunakan untuk:
* Root stability tracking
* Confidence averaging
* Entropy averaging

### Stability Score Formula (Final Enterprise Version)

```
stability_score =
    0.5 * root_stability
  + 0.3 * avg_confidence
  + 0.2 * entropy_penalty
```

### Entropy Normalization

```python
max_entropy = np.log(domain_count)
normalized_entropy = avg_entropy / max_entropy
entropy_penalty = 1 - (normalized_entropy ** 1.5)
```

### Governance Thresholds

```python
SHIFT_THRESHOLD = 3
CONFIDENCE_THRESHOLD = 0.4
ENTROPY_THRESHOLD = 1.2
```

### Governance Severity Bands

```python
if score >= 0.75:
    severity = "stable"
elif score >= 0.5:
    severity = "moderate"
else:
    severity = "unstable"
```

### Extended Governance Flags (v1.2.0)

| Flag | Trigger |
| --- | --- |
| `forward_low_confidence` | mode=forward & forecast_confidence < 0.5 |
| `cross_domain_power_cooling` | root_domain ∈ {power, cooling} & impact > 1 domain |
| `asset_context_missing` | asset_context tidak teresolusi (NetBox down / mapping hilang) |

---

## 7. Integration with Correlation Engine

**File:** `dcim_ai/correlation/correlation_engine.py`

### RCA Invocation

```python
rca_result = RCAEngine.analyze(incident)
incident["root_cause"] = rca_result.to_dict()

lifecycle_manager.update(rca_result)
incident["root_cause_lifecycle"] = {
    **lifecycle_manager.summary(),
    "governance": lifecycle_manager.governance_status()
}
```

---

## 8. Database Persistence Config

**Table:** `incident_root_causes`

### Table Schema

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

---

## 9. RCA Response Payload Example

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

---

## 10. Operational Interpretation

| Scenario | Meaning |
| --- | --- |
| High confidence + low entropy | Clear root — root cause jelas, investigasi langsung ke domain tersebut |
| Low confidence + high entropy | Multi-domain failure — perlu investigasi lebih dalam di beberapa domain |
| Root shift high | Unstable system — RCA sering berubah, pola gangguan tidak konsisten |
| Stability score low | RCA unreliable — hasil RCA tidak bisa diandalkan, perlu manual review |
| Governance flag true | Investigation needed — ada masalah kualitas RCA yang perlu ditinjau |

---

## 11. dcim-wiki Alignment

### Mapping ke dcim-wiki block7 §5: Root Cause Analysis

| dcim-wiki Spec | Config Location | Implementation |
| --- | --- | --- |
| **Incident timeline reconstruction** | §5 Chain Builder (`_build_causal_chain`) | DFS traversal merekonstruksi urutan propagasi. Forward RCA menggunakan forecast timeline |
| **Multi-source event correlation** | §3 Composite Scoring (WEIGHTS dict) | 6 sinyal dikorelasikan: topology(0.30), strength(0.25), persistence(0.20), trend(0.10), anomaly(0.10), drift(0.05) |
| **CMDB topology traversal (depth 3)** | §4 TOPOLOGY dict + `MAX_CHAIN_DEPTH=3` | Directed causal graph dengan traversal depth limit 3. Extended topology termasuk power/cooling/hardware |
| **Root cause hypotheses ranked by confidence** | §2 RootCauseResult structure | `domain_probabilities` (softmax), `ranked_domains`, `confidence` — ranked hypotheses tersedia |
| **Recommended remediation** | §7 Integration + LLM Contract | `RCAEngine.analyze()` → `lifecycle_manager.summary()` → LLM prompt → remediation actions |
| **< 30s per incident** | §3-§5 Engine config | Pure Python scoring, depth-limited traversal, probability pruning — target achievable pada spec hardware dcim-wiki |
| **3 RCA modes** | §3 `RCAMode` enum | `reactive` (default), `forward` (forecast-based), `hybrid` (weighted merge) |

### Alignment Score: ~90%

**Aligned:** Semua 7 spesifikasi utama dcim-wiki §5 terpenuhi dalam konfigurasi MT-022.

**Gap minor:**
- dcim-wiki menunjukkan async implementation — MT-022 config masih synchronous
- dcim-wiki spec menyebut explicit client dependencies (ES, TSDB, CMDB, Kafka) — belum terdokumentasikan di config
- Timeline reconstruction di dcim-wiki berbasis Elasticsearch query — MT-022 masih graph-based abstraction

---

## 12. Actual Code Location

| Komponen | File Path |
| --- | --- |
| RCA Engine (3 modes) | `dcim_ai/root_cause/rca_engine.py` |
| RCA Data Models | `dcim_ai/root_cause/rca_models.py` |
| Topology Manager | `dcim_ai/root_cause/topology_manager.py` |
| Causal Topology | `dcim_ai/root_cause/causal_topology.py` |
| Lifecycle Manager | `dcim_ai/root_cause/lifecycle_manager.py` |
| RCA Service | `dcim_ai/services/rca_service.py` |
| LLM Prompt Contract | `dcim_ai/llm/rca_prompt_contract.py` |
| API Router | `dcim_ai/api/routers/rca.py` |
| Config Constants (WEIGHTS) | `dcim_ai/root_cause/rca_engine.py` |
| Chain Config (MIN_CHAIN_PROB, MAX_CHAIN_DEPTH) | `dcim_ai/root_cause/rca_engine.py` |
| Governance Thresholds | `dcim_ai/root_cause/lifecycle_manager.py` |
| Database Table | PostgreSQL `incident_root_causes` |
| Tests (forward) | `dcim_ai/tests/test_rca_forward.py` |
| Tests (LLM contract) | `dcim_ai/tests/test_llm_rca_prompt_contract.py` |
| Tests (asset enricher) | `dcim_ai/tests/test_asset_enricher.py` |

---

## Changelog

| Date | Version | Author | Note |
| --- | --- | --- | --- |
| 20/05/2026 | 1.2.0 | DCIM AI Team | Initial configuration document |
| 10/07/2026 | 2.0 | Fakhri Aulia R | Restrukturisasi v2 — YAML frontmatter, daftar isi, dcim-wiki alignment, actual code location, extended governance flags |
