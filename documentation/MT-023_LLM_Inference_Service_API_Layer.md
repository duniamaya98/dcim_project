# MT-023 — LLM Inference Service (FastAPI) Detailed Task Documentation

## 1. Overview

Task ini berfokus pada pembangunan **LLM Inference Service** sebagai layer integrasi antara sistem DCIM AI (MT-018 s.d MT-022) dengan model LLM (llama.cpp / Ollama / fine-tuned model).

Service ini bertanggung jawab untuk:
- Menerima request dari sistem atau user
- Mengirim prompt ke LLM
- Mengelola performa (async, queue, retry)
- Menyediakan logging dan observability

---

## 2. Arsitektur Komponen

```
Client / DCIM System
        ↓
FastAPI (/llm/inference)
        ↓
Async Queue Worker
        ↓
LLM Engine (llama.cpp / Ollama)
        ↓
Response + Logging
```

---

## 3. Subtask Detail

---

## 3.1 Buat FastAPI Service `/llm/inference`

### Objective
Menyediakan REST API untuk inference LLM.

### Endpoint Design

```
POST /llm/inference
```

### Request Example
```json
{
  "instruction": "Jelaskan kondisi sistem",
  "input": {...},
  "context": "optional"
}
```

### Response Example
```json
{
  "status": "success",
  "output": "Sistem mengalami kondisi kritis...",
  "latency": 1.23
}
```

---

## 3.2 Implement Async Queue Worker

### Objective
Menghindari bottleneck saat banyak request masuk.

---

## 3.3 Timeout & Retry Mechanism

### Objective
Menjaga stabilitas layanan inference LLM.

---

## 3.4 Logging Request & Response

### Objective
Monitoring, debugging, dan audit system.

---

## 4. Dependency dengan Sistem Sebelumnya

| Module | Hubungan |
|--------|--------|
| MT-018 | source data metrics |
| MT-019 | anomaly data |
| MT-020 | correlation |
| MT-022 | RCA |
| MT-023 | model LLM |

---

## 5. Output

Setelah task ini selesai:
- API inference siap digunakan
- Bisa handle concurrent request
- Stabil (retry & timeout)
- Observable (logging)

---

## 6. Kesimpulan

Task ini adalah:
> "Jembatan antara DCIM AI system dengan LLM intelligence"
