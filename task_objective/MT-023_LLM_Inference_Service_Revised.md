# MT-023 — LLM Inference Service (Production-Grade Detailed Documentation)

# 1. Overview

Dokumen ini merupakan revisi detail dari task:
- FastAPI Inference Service
- Async Queue Worker
- Timeout & Retry Mechanism
- Logging & Observability

Task ini berfungsi sebagai:
> "Jembatan antara sistem DCIM AI (MT-018 s.d MT-022) dengan LLM Intelligence Layer"

Inference service bertanggung jawab untuk:
- menerima request dari sistem DCIM
- membangun prompt
- mengelola inference LLM
- menangani concurrency
- menjaga reliability
- menyediakan observability

---

# 2. Hubungan dengan MT-018 s.d MT-022

| Module | Fungsi |
|---|---|
| MT-018 | Prediction output |
| MT-019 | Anomaly & drift |
| MT-020 | Correlation & incident |
| MT-022 | Root Cause Analysis |
| MT-021 | Lifecycle & governance |
| MT-023 | LLM intelligence layer |

---

# 3. High-Level Architecture

```text
Telemetry Data
        ↓
MT-018 Prediction
        ↓
MT-019 Anomaly Framework
        ↓
MT-020 Correlation Engine
        ↓
MT-022 RCA Engine
        ↓
LLM Inference Service
        ↓
LLM Engine (llama.cpp / Ollama)
        ↓
Natural Language Explanation
```

---

# 4. FastAPI Inference Service

## 4.1 Objective

Menyediakan REST API sebagai entry point inference LLM.

## 4.2 Kenapa FastAPI?

- async native
- latency rendah
- high concurrency
- mudah scaling

## 4.3 Endpoint Design

```http
POST /llm/inference
```

### Request Example

```json
{
  "instruction": "Jelaskan kondisi sistem",
  "input": {
    "severity": "critical"
  }
}
```

### Response Example

```json
{
  "status": "success",
  "model": "qwen2.5",
  "latency": 1.24,
  "output": "Sistem mengalami overload..."
}
```

---

## 4.4 Internal Flow

```text
API Request
    ↓
Request Validation
    ↓
Prompt Builder
    ↓
Async Queue
    ↓
LLM Worker
    ↓
Response Formatter
    ↓
Logging & Metrics
```

---

# 5. Async Queue Worker

## 5.1 Objective

Menghindari:
- blocking request
- GPU overload
- inference bottleneck

## 5.2 Queue Architecture

```text
Client Request
      ↓
FastAPI Gateway
      ↓
Async Queue
      ↓
Worker Pool
      ↓
LLM Engine
```

## 5.3 Worker Lifecycle

```text
Receive Request
      ↓
Enqueue
      ↓
Worker Fetch Task
      ↓
Run Inference
      ↓
Return Result
      ↓
Cleanup GPU Memory
```

## 5.4 Queue Strategy

| Parameter | Value |
|---|---|
| max_workers | 2–4 |
| queue_size | 100 |
| timeout | 10s |
| retry | 2–3 |

## 5.5 Priority Queue

- critical incident → high priority
- normal summary → low priority

## 5.6 Example Async Queue

```python
import asyncio

queue = asyncio.Queue()

async def worker():
    while True:
        task = await queue.get()
        result = call_llm(task["prompt"])
        task["future"].set_result(result)
        queue.task_done()
```

---

# 6. Timeout & Retry Mechanism

## 6.1 Objective

Menjaga reliability inference service.

## 6.2 Failure Scenario

- GPU OOM
- model hang
- context terlalu panjang
- inference timeout

## 6.3 Timeout Strategy

| Request Type | Timeout |
|---|---|
| summary | 5s |
| RCA explanation | 15s |
| long analysis | 30s |

## 6.4 Retry Strategy

```text
Attempt 1
   ↓
Retry
   ↓
Attempt 2
   ↓
Fallback Model
   ↓
Fail Response
```

## 6.5 Fallback Model

- Primary: Qwen
- Fallback: Phi

## 6.6 Retry Example

```python
def call_with_retry(prompt, retries=3):
    for i in range(retries):
        try:
            return call_llm(prompt)
        except Exception:
            if i == retries - 1:
                return "Failed"
```

---

# 7. Logging & Observability

## 7.1 Objective

Digunakan untuk:
- monitoring
- debugging
- optimization
- audit

## 7.2 Logging Flow

```text
Request
   ↓
Inference
   ↓
Metrics Collector
   ↓
Log Storage
```

## 7.3 Data yang Harus Di-log

| Field | Purpose |
|---|---|
| timestamp | audit |
| request_id | tracing |
| model | tracking |
| prompt | debugging |
| latency | performance |
| error | troubleshooting |

## 7.4 Observability Stack

| Component | Tool |
|---|---|
| Metrics | Prometheus |
| Dashboard | Grafana |
| Logs | Loki / ELK |

## 7.5 Metrics yang Dipantau

| Metric | Tujuan |
|---|---|
| latency | performance |
| GPU usage | optimization |
| request/sec | scalability |
| failure rate | reliability |

---

# 8. Integrasi dengan llama.cpp / Ollama

## llama.cpp

```bash
./server -m model.gguf --host 0.0.0.0 --port 8080
```

## Ollama

```http
POST /api/generate
```

---

# 9. Scalability Strategy

## Horizontal Scaling

```text
Load Balancer
    ↓
Inference Node 1
Inference Node 2
Inference Node 3
```

## Multi-Model Routing

- Qwen → RCA
- Phi → reasoning
- Small model → summary

---

# 10. Security Consideration

- Internal network only
- API token authentication
- Request validation
- Rate limiting

---

# 11. Expected Output

- inference service production-ready
- scalable
- observable
- reliable

---

# 12. Kesimpulan

Task ini bukan sekadar endpoint API,
tetapi production-grade AI inference infrastructure
untuk seluruh pipeline DCIM AI.
