# Model Specification Test Suite

> **Tujuan:** Pengujian empiris 22 capability parameter pada model LLM yang di-benchmark di MT-023
> **Tanggal:** 2 Juni 2026
> **Server:** srv-rnd-llm (192.168.100.35)

## Overview

Test suite ini melakukan **pengujian aktual** terhadap setiap capability parameter — bukan berdasarkan general knowledge, tapi berdasarkan **hasil eksekusi script** terhadap model yang sedang berjalan.

## Struktur

```
model_specification_test/
├── config.py              # Konfigurasi model & endpoint
├── requirements.txt       # Dependencies
├── run_tests.py           # Main test runner
├── tests/                 # Test modules per capability
│   ├── test_tool_calling.py
│   ├── test_rag.py
│   ├── test_code_execution.py
│   ├── test_vision.py
│   ├── test_json_mode.py
│   ├── test_structured_output.py
│   ├── test_multiturn.py
│   ├── test_streaming.py
│   ├── test_cot_reasoning.py
│   ├── test_agent.py
│   ├── test_web_search.py
│   ├── test_terminal.py
│   ├── test_file_ops.py
│   ├── test_memory.py
│   ├── test_task_planning.py
│   ├── test_cron.py
│   ├── test_messaging.py
│   ├── test_session_search.py
│   ├── test_clarifying.py
│   ├── test_delegation.py
│   ├── test_skills.py
│   └── test_context_engine.py
├── utils/
│   ├── scoring.py         # Scoring logic
│   └── report.py          # Report generation
└── results/               # Generated test results
    ├── raw/               # Raw JSON results
    └── reports/           # Formatted reports
```

## Cara Menjalankan

### Prerequisites

```bash
# 1. Pastikan model sudah running
# Ollama:
ollama run qwen2.5-coder:1.5b

# Atau llama.cpp:
llama-server -m model.gguf -ngl 99 --port 8080

# 2. Install dependencies
pip install -r requirements.txt

# 3. Edit config.py sesuai endpoint model
```

### 1. Auto-Detect & Jalankan (Rekomendasi)

Script akan otomatis mendeteksi model mana yang sedang berjalan (via endpoint `/v1/models`) dan langsung menjalankannya. Jika lebih dari 1 model terdeteksi, akan otomatis menjalankan mode perbandingan (`--compare`).

```bash
/home/infra/dcim_project/ragavenv/bin/python3 run_tests.py --auto
```

### 2. Jalankan Berdasarkan Platform

Memfilter dan menjalankan model berdasarkan platform yang dipilih (hanya model yang `enabled: True` di `config.py`).

```bash
# Hanya test model yang berjalan di Ollama
/home/infra/dcim_project/ragavenv/bin/python3 run_tests.py --platform ollama

# Hanya test model yang berjalan di llama.cpp
/home/infra/dcim_project/ragavenv/bin/python3 run_tests.py --platform llama.cpp
```

### 3. Jalankan untuk Model Spesifik

Jika ingin memaksa menjalankan model tertentu (pastikan model tersebut sedang running dan `enabled: True` di `config.py`).

```bash
/home/infra/dcim_project/ragavenv/bin/python3 run_tests.py --model Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M
```

### 4. Jalankan Perbandingan (Comparison)

Menjalankan test pada semua model yang `enabled` di `config.py` dan menghasilkan laporan perbandingan.

```bash
/home/infra/dcim_project/ragavenv/bin/python3 run_tests.py --compare
```

### 5. Lihat Daftar Model Tersedia

```bash
/home/infra/dcim_project/ragavenv/bin/python3 run_tests.py --list-models
```

### Output

Hasil test tersimpan di direktori `results/`. Nama file model akan disanitasi (karakter `/` dan `:` diganti `_`) agar valid sebagai nama file.

- `results/raw/<sanitized_model_name>_<timestamp>.json` — Raw results
- `results/reports/<sanitized_model_name>_<timestamp>.md` — Formatted Markdown report
- `results/reports/<sanitized_model_name>_<timestamp>.json` — Formatted JSON report
- `results/reports/comparison_<timestamp>.md` — Laporan perbandingan (jika menggunakan `--auto` dengan >1 model atau `--compare`)

## Scoring

Setiap capability diuji dengan **3-5 test cases** dan di-scoring:

| Score | Rating | Kriteria |
|-------|--------|----------|
| 1.0 | ✅ Perfect | Semua test cases pass |
| 0.75 | ✅ Good | 75%+ test cases pass |
| 0.5 | 🟡 Acceptable | 50-74% test cases pass |
| 0.25 | 🔴 Poor | 25-49% test cases pass |
| 0.0 | ❌ Failed | < 25% test cases pass |

## Capability Parameters yang Diuji

| # | Parameter | Test Method |
|---|-----------|-------------|
| 1 | Tool Calling | Function call accuracy, parameter extraction |
| 2 | RAG | Context retrieval, answer accuracy |
| 3 | Code Execution | Code generation, execution success |
| 4 | Vision | Image analysis accuracy (multimodal only) |
| 5 | JSON Mode | Valid JSON output, schema compliance |
| 6 | Structured Output | Format compliance, field accuracy |
| 7 | Multi-turn | Context retention, follow-up accuracy |
| 8 | Streaming | TTFT measurement, token streaming |
| 9 | Chain-of-Thought | Step-by-step reasoning quality |
| 10 | Agent | Multi-step task completion |
| 11 | Web Search | Search accuracy, result relevance |
| 12 | Terminal | Command execution, output parsing |
| 13 | File Operations | Read/write/search accuracy |
| 14 | Memory | Store/recall accuracy |
| 15 | Task Planning | Step breakdown quality |
| 16 | Cron | Schedule creation, management |
| 17 | Messaging | Message delivery, format |
| 18 | Session Search | Search accuracy, relevance |
| 19 | Clarifying | Question quality, relevance |
| 20 | Delegation | Task routing accuracy |
| 21 | Skills | Skill listing, execution |
| 22 | Context Engine | Context switching, tool loading |

## Model yang Diuji

| Model | Endpoint | Platform |
|-------|----------|----------|
| qwen2.5-coder:1.5b | http://localhost:11434 | Ollama |
| Qwen3-VL-4B-Instruct | http://localhost:8080 | llama.cpp |
| Qwen2.5.1-Coder-7B-Instruct | http://localhost:8081 | llama.cpp |
| microsoft/phi-4 | http://localhost:8082 | llama.cpp |
| dcim_assistant v1.0 | http://localhost:11435 | Ollama |

## Referensi

- [MT-023 Private LLM Platform](../(MT-023)%20Private%20LLM%20Platform.md)
- [MT-023 AI Model Specifications](../documentation/MT-023_AI_Model_Specifications.md)
