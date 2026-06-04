# (MT-023) Private LLM Platform

## Dokumentasi Lengkap: Platform Setup, Benchmark Multi-Model, Quantization Analysis, Model Preparation & Fine-Tuning

> **Pendekatan:** Benchmark-driven deployment
> **Status:** COMPLETED — Platform Benchmark, Model Preparation & Fine-Tuning terdokumentasi
> **File Script:** `benchmark_all_v4.py` | **Lines:** 1.025 | **Benchmarks:** 14 total (7 performance + 7 capability)
> **Benchmark dilaksanakan pada:** 22 April 2026 | **Created By:** FIT098
> **Location (Original):** `/home/infra/benchmark_model/benchmark_comparation/`
> **Location (Consolidated):** `/home/infra/dcim_project/implementation/dcim_benchmark/benchmark_comparation/`
> **Project Consolidation:** 12 Mei 2026 — Semua file DCIM dikonsolidasikan ke `/home/infra/dcim_project/`

***

## Daftar Isi

1. [Overview & Tujuan](#1-overview--tujuan)
2. [Environment & Spesifikasi Hardware](#2-environment--spesifikasi-hardware)
3. [Platform LLM yang Digunakan](#3-platform-llm-yang-digunakan)
4. [Arsitektur Benchmark & Flow](#4-arsitektur-benchmark--flow)
5. [Prerequisites & Konfigurasi Script](#5-prerequisites--konfigurasi-script)
6. [14 Metrik Benchmark — Penjelasan, Cara Ukur & Threshold](#6-14-metrik-benchmark--penjelasan-cara-ukur--threshold)
7. [Hasil Benchmark via Ollama](#7-hasil-benchmark-via-ollama)
8. [Hasil Benchmark via llama.cpp](#8-hasil-benchmark-via-llamacpp)
9. [Perbandingan Lintas Platform](#9-perbandingan-lintas-platform)
10. [Quantization Analysis](#10-quantization-analysis)
11. [Analisis Mendalam: Qwen3.5:4B vs Gemma4](#11-analisis-mendalam-qwen354b-vs-gemma4)
12. [Final Recommendation untuk DCIM](#12-final-recommendation-untuk-dcim)
13. [Cara Menjalankan Benchmark](#13-cara-menjalankan-benchmark)
14. [Migrasi & Optimasi llama.cpp (V5 Extension)](#14-migrasi--optimasi-llamacpp-v5-extension)
15. [Model Preparation — LLM Dataset Generation Pipeline](#15-model-preparation--llm-dataset-generation-pipeline)
16. [Fine-Tuning dengan Unsloth](#16-fine-tuning-dengan-unsloth)
17. [Project Consolidation & New Structure](#17-project-consolidation--new-structure)

***

## 1. Overview & Tujuan

Dokumen ini merupakan dokumentasi lengkap dari MT-023 yang mencakup seluruh siklus evaluasi platform LLM privat — mulai dari setup infrastruktur, desain metodologi benchmark, eksekusi pengujian multi-model, hingga analisis quantization, rekomendasi deployment akhir, pipeline persiapan dataset, dan proses fine-tuning dengan Unsloth.

**Tujuan utama:**

* Mengevaluasi performa model LLM lokal secara objektif dan terukur
* Membandingkan dua platform inferensi: **Ollama** dan **llama.cpp**
* Menentukan model dan konfigurasi optimal untuk use-case **DCIM (Data Center Infrastructure Management)**
* Memberikan dasar teknis yang solid untuk tahap Model Preparation (MT-024)
* Membangun pipeline dataset dan melakukan fine-tuning LLM domain DCIM

***

## 2. Environment & Spesifikasi Hardware

> **Catatan penting:** Semua hasil benchmark sangat bergantung pada hardware. Model yang sama dapat menghasilkan performa berbeda di mesin lain.

### Server

| Komponen   | Spesifikasi                |
| ---------- | -------------------------- |
| Hostname   | srv-rnd-llm                |
| Platform   | Virtual Machine (QEMU/KVM) |
| IP Address | 192.168.100.35/23          |

### Hardware

| Komponen   | Spesifikasi                     | Catatan                                              |
| ---------- | ------------------------------- | ---------------------------------------------------- |
| CPU        | Intel Core i7-11700KF @ 3.60GHz | 8 cores, 11th Gen Rocket Lake, AVX-512 support       |
| RAM        | 30 GB (ECC)                     | \~22 GB available saat benchmark, no swap configured |
| GPU 0      | NVIDIA GeForce RTX 3070 Ti      | 8.192 MB VRAM, Compute Capability 8.6                |
| GPU 1      | NVIDIA GeForce RTX 3070 Ti      | 8.192 MB VRAM, Compute Capability 8.6                |
| Total VRAM | 16.384 MB (2 × 8 GB)            | Ollama default hanya pakai 1 GPU per model           |
| Storage    | 1 TB Virtual Disk (SSD)         | 647 GB available, 38% used                           |

```mermaid
flowchart LR
    subgraph SERVER["srv-rnd-llm"]
        CPU["Intel i7-11700KF\\n8 cores @ 3.6GHz"]
        RAM["30 GB ECC RAM"]
        subgraph GPUS["Dual GPU Setup"]
            GPU0["GPU 0: RTX 3070 Ti\\n8 GB VRAM"]
            GPU1["GPU 1: RTX 3070 Ti\\n8 GB VRAM"]
        end
        DISK["1 TB SSD"]
    end
    OLLAMA["Ollama v0.21.0"] --> GPU0
    OLLAMA -.->|"Not used by default"| GPU1
```

> **⚠️ Perhatian Multi-GPU:** Ollama secara default hanya menggunakan **1 GPU** per model. Meskipun server memiliki 2× RTX 3070 Ti, benchmark ini hanya memanfaatkan 1 GPU (8 GB VRAM). Untuk multi-GPU, perlu konfigurasi `OLLAMA_GPU_DEVICES` atau gunakan framework lain (vLLM, llama.cpp).

### Operating System & Software Stack

| Komponen      | Versi / Detail                                        |
| ------------- | ----------------------------------------------------- |
| OS            | Ubuntu 24.04.3 LTS (Noble Numbat)                     |
| Kernel        | 6.8.0-110-generic (x86\_64, PREEMPT\_DYNAMIC)         |
| Python        | 3.12.3                                                |
| Ollama        | 0.21.0 — LLM inference server (OpenAI-compatible API) |
| NVIDIA Driver | 575.51.03                                             |
| CUDA          | 12.0                                                  |
| Docker        | Installed (tersedia, tidak dipakai untuk benchmark)   |

### Model yang Di-benchmark (Perbandingan Awal)

| Model             | Parameter   | Format           | VRAM Usage               |
| ----------------- | ----------- | ---------------- | ------------------------ |
| **Qwen3.5:4B**    | \~4 Billion | GGUF (quantized) | \~5.910 MB (72% of 8 GB) |
| **Gemma4:latest** | \~4 Billion | GGUF (quantized) | \~7.680 MB (94% of 8 GB) |

> **⚠️ Perhatian VRAM:** Gemma4 menggunakan 94% VRAM dari RTX 3070 Ti — sangat mepet. Context window yang besar atau batch processing bisa menyebabkan OOM (Out Of Memory). Qwen lebih aman di 72%.

***

## 3. Platform LLM yang Digunakan

Dua platform inferensi digunakan dalam benchmark ini, masing-masing dengan karakteristik berbeda:

| Aspek                | Ollama                             | llama.cpp                        |
| -------------------- | ---------------------------------- | -------------------------------- |
| Kemudahan Setup      | ✅ Sangat mudah, one-command deploy | ⚙️ Lebih teknis, perlu kompilasi |
| Latency              | ✅ Rendah, cocok real-time          | ⚠️ Sedikit lebih tinggi          |
| Kontrol Quantization | ⚠️ Terbatas                        | ✅ Granular & fleksibel           |
| Kualitas Output      | ⭐ Baik                             | ✅ Lebih tinggi secara konsisten  |
| Use Case Utama       | Production real-time, prototyping  | Advanced optimization, research  |

**Kesimpulan platform:**

* **Ollama** → cocok untuk deployment production yang mengutamakan kemudahan dan latensi rendah
* **llama.cpp** → cocok untuk optimasi lanjutan dan kontrol penuh terhadap quantization

***

## 4. Arsitektur Benchmark & Flow

### Perubahan dari V3 ke V4

| Area              | V3               | V4                                                                                             |
| ----------------- | ---------------- | ---------------------------------------------------------------------------------------------- |
| Total benchmarks  | 5                | **14**                                                                                         |
| Capability tests  | Quality only     | **+7 new** (Reasoning, RCA, Tools, Long Context, Hallucination, Consistency, Domain Knowledge) |
| Output format     | stdout dict only | stdout table **+ JSON file**                                                                   |
| Progress tracking | None             | **Step counter** `[1/14]`…`[14/14]`                                                            |
| Helper functions  | Inline           | **`send_prompt()`** shared helper                                                              |
| Error handling    | Crash on failure | **Try/except with timeout**                                                                    |

### Flow Benchmark

```mermaid
flowchart TB
    subgraph PERF["Performance Benchmarks (from V3)"]
        B1["1. Latency + TPS"]
        B2["2. TTFT"]
        B3["3. Throughput"]
        B4["4. Quality"]
        B5["5. GPU Monitoring"]
    end

    subgraph CAP["Capability Benchmarks (NEW in V4)"]
        B6["6. Reasoning"]
        B7["7. RCA"]
        B8["8. Tool Use"]
        B9["9. Long Context"]
        B10["10. Hallucination"]
        B11["11. Consistency"]
        B12["12. Domain Knowledge"]
    end

    A[Start] --> W[Warm-up] --> GPU[Detect GPU]
    GPU --> PERF --> CAP
    CAP --> R[Results Dict]
    R --> T[Print Table]
    R --> J[Save JSON]
```

***

## 5. Prerequisites & Konfigurasi Script

### Dependencies

```shellscript
pip install requests numpy pynvml
```

### Pull Model (Ollama)

```shellscript
ollama pull qwen2.5-coder:1.5b
ollama pull phi4:14b
# atau sesuai model yang ingin diuji
ollama pull qwen3.5:4b
ollama pull gemma4:latest
```

### Konfigurasi Script

```python
URL = "http://localhost:11434/api/generate"

MODELS = [
    "qwen3.5:4b",
    "gemma4:latest"
    # tambahkan model lain sesuai kebutuhan
]

PROMPT = "Explain clearly in 2 sentences: What is CPU spike?"  # Used for latency/throughput/TTFT

OPTIONS = {
    "num_predict": 100,
    "temperature": 0.7,
    "top_p": 0.9
}

N_RUNS = 5               # Latency iterations
THROUGHPUT_REQUESTS = 10  # Concurrent threads for throughput
CONSISTENCY_RUNS = 3      # Repetitions per consistency prompt
```

***

## 6. 14 Metrik Benchmark — Penjelasan, Cara Ukur & Threshold

### Tabel Ringkasan Semua Benchmark

| #  | Benchmark            | Metric Keys                                    | What It Measures                                          |
| -- | -------------------- | ---------------------------------------------- | --------------------------------------------------------- |
| 1  | **Latency + TPS**    | `latency_avg`, `latency_p95`, `tokens_per_sec` | Waktu respons dari awal hingga akhir dan generation speed |
| 2  | **TTFT**             | `ttft`                                         | Waktu hingga token pertama tiba (streaming)               |
| 3  | **Throughput**       | `throughput`                                   | Penanganan request secara bersamaan (request per detik)   |
| 4  | **Quality**          | `quality_score`                                | Pemeriksaan substansi respons dasar                       |
| 5  | **GPU Monitoring**   | `gpu_util_avg`, `gpu_vram_avg_mb`              | Penggunaan komputasi dan memori GPU selama inferensi      |
| 6  | **Reasoning**        | `reasoning_score`                              | Multi-step logical reasoning                              |
| 7  | **RCA**              | `rca_score`                                    | Analisis root cause dari symptoms                         |
| 8  | **Tool Use**         | `tool_use_score`                               | Akurasi function calling                                  |
| 9  | **Long Context**     | `long_context_score`                           | Pengambilan informasi dari konteks yang besar             |
| 10 | **Hallucination**    | `hallucination_score`                          | Ketahanan terhadap fabrikasi                              |
| 11 | **Consistency**      | `consistency_score`                            | Stabilitas jawaban di seluruh percobaan                   |
| 12 | **Domain Knowledge** | `domain_knowledge_score`                       | Infrastructure/DCIM domain expertise                      |

### Tabel Interpretasi Cepat

| Metric                   | 🟢 Good    | 🟡 Acceptable | 🔴 Poor       |
| ------------------------ | ---------- | ------------- | ------------- |
| `latency_avg`            | < 3s       | 3–5s          | > 5s          |
| `latency_p95`            | < 5s       | 5–10s         | > 10s         |
| `tokens_per_sec`         | > 30       | 15–30         | < 15          |
| `ttft`                   | < 0.5s     | 0.5–1.5s      | > 1.5s        |
| `throughput`             | > 2 req/s  | 1–2 req/s     | < 1 req/s     |
| `quality_score`          | 1.0        | 0.67          | < 0.67        |
| `gpu_util_avg`           | 60–90%     | 40–60%        | < 40% / > 95% |
| `gpu_vram_avg_mb`        | < 70% VRAM | 70–90%        | > 90%         |
| `reasoning_score`        | > 0.75     | 0.5–0.75      | < 0.5         |
| `rca_score`              | > 0.75     | 0.5–0.75      | < 0.5         |
| `tool_use_score`         | > 0.75     | 0.5–0.75      | < 0.5         |
| `long_context_score`     | > 0.75     | 0.5–0.75      | < 0.5         |
| `hallucination_score`    | > 0.8      | 0.6–0.8       | < 0.6         |
| `consistency_score`      | > 0.7      | 0.5–0.7       | < 0.5         |
| `domain_knowledge_score` | > 0.8      | 0.6–0.8       | < 0.6         |

> **⚠️ CRITICAL untuk DCIM Production:** Prioritaskan `hallucination_score > 0.8`, `rca_score > 0.75`, dan `domain_knowledge_score > 0.8`. Model yang mengarang data atau tidak bisa mendiagnosis masalah infrastruktur **sangat berbahaya** dalam monitoring production.

### Dasar Penentuan Threshold

```mermaid
mindmap
  root((Threshold Sources))
    Performance
      Latency: Web UX research, Nielsen Norman Group
      P95: Cloud SLA standards, AWS/GCP/Azure
      TPS: Human reading speed, 4 words/sec baseline
      TTFT: Jakob Nielsen response time research
      Throughput: DCIM alert volume estimation
    Infrastructure
      GPU Util: NVIDIA inference best practices
      VRAM: Hardware-specific, % of available memory
    Capability
      Reasoning: MMLU/GSM8K passing grade, 75%
      RCA: Google SRE Handbook competency level
      Tool Use: UC Berkeley Gorilla paper
      Long Context: Needle-in-haystack test, Liu et al 2023
      Hallucination: Microsoft Research enterprise risk, higher bar due to impact
      Consistency: Jaccard similarity IR research
      Domain Knowledge: Professional certification analogy, 80%
```

***

### Performance Benchmark 1: Latency Avg (s)

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| < 3s    | 3–5s          | > 5s    |

**Apa ini?** Waktu total dari kirim prompt sampai terima jawaban lengkap, dirata-ratakan dari `N_RUNS` (default: 5) kali percobaan.

**Cara ukur di script:**

```python
start = time.time()
res = requests.post(URL, json=payload)
end = time.time()
latency = end - start  # diulang 5x, lalu di-mean()
```

**Dasar threshold:**

| Threshold             | Dasar                                                                                                                                                                                                     |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **< 3s (Good)**       | Standar industri untuk API real-time. Google merekomendasikan response time < 3 detik untuk web service. Dalam konteks DCIM monitoring, alert harus tiba dalam hitungan detik setelah anomali terdeteksi. |
| **3–5s (Acceptable)** | Masih bisa dipakai untuk batch processing atau background task. Nielsen Norman Group: 5 detik adalah batas dimana user mulai kehilangan fokus.                                                            |
| **> 5s (Poor)**       | Terlalu lambat untuk interactive use. Untuk monitoring real-time, 5s delay bisa berarti missed alert window.                                                                                              |

***

### Performance Benchmark 2: Latency P95 (s)

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| < 5s    | 5–10s         | > 10s   |

**Apa ini?** Percentile ke-95 dari semua latency. Artinya: **95% dari semua request selesai di bawah waktu ini**. Mengukur "seburuk apa di kondisi terburuk yang realistis" (bukan outlier ekstrem).

**Cara ukur di script:**

```python
float(np.percentile(latencies, 95))
```

**Dasar threshold:**

| Threshold              | Dasar                                                                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **< 5s (Good)**        | SLA di industri cloud umumnya mensyaratkan P95 latency < 5s untuk API tier-1. AWS, GCP, dan Azure menggunakan P95/P99 sebagai standard SLA metric. |
| **5–10s (Acceptable)** | Masih dalam batas timeout default kebanyakan HTTP client. Cocok untuk background/async workflow.                                                   |
| **> 10s (Poor)**       | Banyak HTTP client timeout di 10–15s. Menandakan model terlalu berat atau server overloaded.                                                       |

> **Kenapa P95, bukan P99 atau max?** P99 dan max terlalu sensitif terhadap outlier. P95 adalah standar industri (dipakai oleh AWS CloudWatch, Datadog, Grafana) karena memberikan gambaran worst-case yang realistis tanpa noise dari outlier ekstrem.

***

### Performance Benchmark 3: Tokens/sec

| 🟢 Good    | 🟡 Acceptable | 🔴 Poor    |
| ---------- | ------------- | ---------- |
| > 30 tok/s | 15–30 tok/s   | < 15 tok/s |

**Apa ini?** Berapa token (≈ kata) yang dihasilkan model per detik. Semakin tinggi = semakin cepat teks muncul di layar user.

**Cara ukur di script:**

```python
tokens = data.get("eval_count", len(data["response"].split()))
tps = tokens / latency  # per run, lalu di-mean()
```

**Dasar threshold:**

| Threshold                    | Dasar                                                                                                                                                           |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **> 30 tok/s (Good)**        | Rata-rata manusia membaca \~4 kata/detik. Pada 30 tok/s model generate teks **7–8x lebih cepat** dari yang bisa dibaca manusia — terasa instan.                 |
| **15–30 tok/s (Acceptable)** | Masih lebih cepat dari kecepatan baca manusia, tapi untuk pipeline automation berthroughput tinggi, ini mulai jadi bottleneck.                                  |
| **< 15 tok/s (Poor)**        | Streaming response terasa lambat. Untuk jawaban panjang (500+ token), user harus menunggu 30+ detik. Menandakan bottleneck hardware (VRAM penuh, layer di CPU). |

***

### Performance Benchmark 4: TTFT (s) — Time To First Token

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| < 0.5s  | 0.5–1.5s      | > 1.5s  |

**Apa ini?** Waktu dari kirim prompt sampai **huruf pertama muncul**. Ini yang dirasakan user sebagai "kecepatan respons".

**Cara ukur di script:**

```python
start = time.time()
with requests.post(URL, json=payload, stream=True) as r:
    for chunk in r.iter_lines():
        if chunk:
            return time.time() - start  # waktu sampai chunk pertama
```

**Dasar threshold:**

| Threshold                 | Dasar                                                                                                                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **< 0.5s (Good)**         | Riset UX dari Jakob Nielsen: response < 0.1s terasa "instan", < 1s user masih merasa "langsung dijawab". ChatGPT dan Gemini menargetkan TTFT < 0.5s untuk chat yang natural. |
| **0.5–1.5s (Acceptable)** | User sadar ada delay tapi masih menunggu. Setara dengan typing indicator.                                                                                                    |
| **> 1.5s (Poor)**         | User mulai berpikir "apa ini hang?". Di atas 2 detik, banyak UI menampilkan loading spinner.                                                                                 |

> **Catatan:** TTFT dipengaruhi oleh 2 faktor: (1) prompt processing time (makin panjang prompt, makin lama), dan (2) model loading time kalau model belum di-cache di GPU. Warmup di script sudah handle poin ke-2.

***

### Performance Benchmark 5: Throughput (req/s)

| 🟢 Good   | 🟡 Acceptable | 🔴 Poor   |
| --------- | ------------- | --------- |
| > 2 req/s | 1–2 req/s     | < 1 req/s |

**Apa ini?** Berapa request yang bisa dilayani per detik saat ada **banyak request bersamaan** (default: 10 thread simultan).

**Cara ukur di script:**

```python
# 10 thread kirim request bersamaan
total_requests / total_elapsed_time = req/s
```

**Dasar threshold:**

| Threshold                  | Dasar                                                                                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **> 2 req/s (Good)**       | Untuk DCIM monitoring dengan \~50 alert/menit (worst case), 2 req/s = 120 req/menit — cukup.                                                |
| **1–2 req/s (Acceptable)** | Cukup untuk moderate monitoring load. 1 req/s = 60 inference per menit.                                                                     |
| **< 1 req/s (Poor)**       | Setiap request butuh > 1 detik dan queue menumpuk. Ini terjadi karena **Ollama memproses sequential by default** (`OLLAMA_NUM_PARALLEL=1`). |

> **Tip:** Throughput rendah **bukan berarti model buruk** — ini limitasi Ollama. Set `OLLAMA_NUM_PARALLEL=2` atau gunakan vLLM/TGI untuk throughput lebih tinggi.

***

### Performance Benchmark 6: Quality Score

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| 1.0     | 0.67          | < 0.67  |

**Apa ini?** Apakah model menghasilkan jawaban yang panjang dan substantif (> 50 karakter) untuk 3 pertanyaan domain.

**Cara ukur di script:**

```python
# 3 pertanyaan: CPU spike, anomaly detection, memory leak
# Setiap jawaban > 50 char = 1 point
score = passed / 3  # menghasilkan 0.0, 0.33, 0.67, atau 1.0
```

> **Catatan:** Quality score ini **hanya sanity check**, bukan evaluasi kualitas sebenarnya. Hanya mengecek panjang teks, bukan kebenaran konten. Untuk evaluasi lebih dalam, lihat Reasoning, RCA, dan Domain Knowledge.

***

### Performance Benchmark 7: GPU Metrics

#### GPU Util Avg (%)

| 🟢 Good | 🟡 Acceptable      | 🔴 Poor          |
| ------- | ------------------ | ---------------- |
| 60–90%  | 40–60% atau 90–95% | < 40% atau > 95% |

**Apa ini?** Persentase waktu dimana GPU compute cores sedang aktif bekerja, disampling setiap 200ms selama inference.

**Cara ukur di script:**

```python
# 15 samples × 200ms = 3 detik sampling
util = pynvml.nvmlDeviceGetUtilizationRates(handle)
# util.gpu = persentase utilisasi
```

**Dasar threshold:**

| Threshold               | Dasar                                                                                                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **60–90% (Good)**       | Model memanfaatkan GPU secara efisien. Ruang headroom 10–40% memungkinkan burst tanpa throttling. Range optimal menurut NVIDIA best practices untuk inference workload. |
| **40–60% (Acceptable)** | GPU kurang dimanfaatkan — kemungkinan bottleneck di tempat lain (CPU preprocessing, memory bandwidth, I/O).                                                             |
| **90–95% (Borderline)** | Hampir saturasi. Bisa menyebabkan thermal throttling jika sustained.                                                                                                    |
| **< 40% (Poor)**        | GPU jelas idle — model mungkin offloaded ke CPU, atau timing sampling tidak overlap dengan inference.                                                                   |
| **> 95% (Poor)**        | GPU saturated — thermal throttling kemungkinan terjadi, performance drop incoming. Perlu cek cooling.                                                                   |

#### GPU VRAM Avg (MB)

| 🟢 Good    | 🟡 Acceptable | 🔴 Poor    |
| ---------- | ------------- | ---------- |
| < 70% VRAM | 70–90% VRAM   | > 90% VRAM |

**Apa ini?** Berapa MB VRAM (memory di GPU) yang dipakai model saat inference.

**Dasar threshold (untuk RTX 3070 Ti = 8.192 MB):**

| Threshold               | MB             | Dasar                                                                                                                |
| ----------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------- |
| **< 70% (Good)**        | < 5.734 MB     | Cukup ruang untuk context window besar, batch processing, atau menjalankan model kedua.                              |
| **70–90% (Acceptable)** | 5.734–7.373 MB | Model muat tapi tidak banyak ruang. Context window besar bisa memicu OOM. Qwen di 5.910 MB (72%) — pas di batas ini. |
| **> 90% (Poor)**        | > 7.373 MB     | Hampir penuh. Resiko OOM saat context panjang. Gemma4 di 7.680 MB (94%) — **sangat mepet**.                          |

> **Catatan:** VRAM threshold ini **relatif terhadap GPU anda**. Di GPU 24GB (RTX 4090), 7.680 MB hanya 32% — perfectly fine.

***

### Capability Benchmark 8: Reasoning (`reasoning_score`)

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| > 0.75  | 0.5–0.75      | < 0.5   |

**Apa ini?** Kemampuan model melakukan penalaran multi-langkah: dependency analysis, aritmatika, kalkulasi waktu, redistribusi proporsional.

**4 Test Cases:**

| Test             | Scenario                               | Required Keywords | What It Probes                  |
| ---------------- | -------------------------------------- | ----------------- | ------------------------------- |
| Dependency chain | Services A→B→C, C goes down            | `a`, `b`          | Transitive dependency reasoning |
| Arithmetic       | RAM calculation: 20+15+25+10 vs 64GB   | `60`, `no`        | Numeric computation             |
| Time calculation | Cooling fail, 2°C/hr, 22°C→35°C        | `8`, `am`         | Sequential temporal reasoning   |
| Proportional     | Load redistribution after server crash | `60`, `40`        | Proportional math               |

**Scoring:** Untuk setiap test, `keywords_found / total_keywords`. Partial credit diberikan. Final score = average across all tests (0.0–1.0).

***

### Capability Benchmark 9: RCA — Root Cause Analysis (`rca_score`)

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| > 0.75  | 0.5–0.75      | < 0.5   |

**Apa ini?** Kemampuan model mendiagnosa root cause dari skenario incident infrastructure.

**4 Test Cases:**

| Test           | Scenario                                        | Key Signals          | Expected Diagnosis                    |
| -------------- | ----------------------------------------------- | -------------------- | ------------------------------------- |
| CPU spike      | Cron ETL at 3AM, CPU 98%                        | `cron`, `etl`        | Cron job is the root cause            |
| Memory cascade | 95% RAM, 80% swap, GC storms                    | `memory`, `swap`     | Memory exhaustion causing swap thrash |
| Network loop   | 15% packet loss, new switch, STP changes        | `switch`, `spanning` | Spanning tree misconfiguration        |
| Disk failure   | 10x slower queries, RAID degraded, SMART errors | `disk`, `raid`       | Failing disk in RAID array            |

**Scoring:** Keyword-match approach. Requires minimum 80 characters for substantive explanation.

***

### Capability Benchmark 10: Tool Use / Function Calling (`tool_use_score`)

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| > 0.75  | 0.5–0.75      | < 0.5   |

**Apa ini?** Kemampuan model memilih tool yang tepat, mengisi parameter yang benar, dan menulis syntax function call yang valid.

**3 Test Cases:**

| Test               | Scenario                         | Expected Behavior                            |
| ------------------ | -------------------------------- | -------------------------------------------- |
| Sequential chain   | High CPU alert workflow          | Call `check_cpu()` → `send_alert()`          |
| Under pressure     | API gateway scaling decision     | Call `get_metrics()` or `scale_replicas()`   |
| Network diagnostic | Server unreachable investigation | Call `check_network()` or `run_diagnostic()` |

**Scoring:** Checks for regex pattern matches on tool names/parameters + function call syntax. Full credit jika keduanya match; 50% credit jika hanya pattern yang match.

***

### Capability Benchmark 11: Long Context (`long_context_score`)

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| > 0.75  | 0.5–0.75      | < 0.5   |

**Apa ini?** Kemampuan model menemukan informasi spesifik yang "tersembunyi" di dalam \~200 baris log server.

**4 Questions tentang hidden facts:**

| Question                       | Expected Answer    |
| ------------------------------ | ------------------ |
| Which server had an ERROR?     | `srv-analytics-07` |
| What type of error?            | `OutOfMemoryError` |
| How many restarts?             | `3`                |
| What time was the first error? | `14:32:05`         |

**Scoring:** Exact substring match (case-insensitive). Binary per question: 1 if found, 0 if not.

> **Kenapa kedua model rendah?** Model 4B parameter punya kemampuan retrieval dari konteks panjang yang lemah berdasarkan riset "Lost in the Middle" (Liu et al., 2023 — Stanford): LLM cenderung mengingat awal dan akhir konteks, tapi kehilangan informasi di tengah.

***

### Capability Benchmark 12: Hallucination Resistance (`hallucination_score`)

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| > 0.8   | 0.6–0.8       | < 0.6   |

**Apa ini?** Kemampuan model untuk **TIDAK mengarang** informasi. Diuji dengan 3 pertanyaan tentang hal **fiktif** (harus bilang "tidak ada") dan 2 pertanyaan tentang hal **nyata** (harus menjawab benar).

**5 Test Cases:**

| Test                                            | Type              | Expected Behavior               |
| ----------------------------------------------- | ----------------- | ------------------------------- |
| "XYZZY protocol" RFC                            | **Should refuse** | Say it doesn't exist            |
| "Quantum Memory Defragmentation" in Linux       | **Should refuse** | Say it doesn't exist            |
| What does `top` command do?                     | **Should answer** | Real answer with valid keywords |
| "NeuroAdaptive Cooling Algorithm" by Dr. Müller | **Should refuse** | Acknowledge it can't verify     |
| Intel Xeon 8490H core count                     | **Should answer** | Provide real hardware specs     |

> **⚠️ Caution:** Hallucination resistance punya threshold lebih tinggi (0.8) dibanding metrik lain (0.75) karena **dampak false positive di monitoring system jauh lebih besar**. Model yang halusinasi = false alarm atau missed real incident.

***

### Capability Benchmark 13: Consistency (`consistency_score`)

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| > 0.7   | 0.5–0.7       | < 0.5   |

**Apa ini?** Apakah model menjawab dengan **konsisten** saat ditanya hal yang sama berulang kali. Diukur dengan Jaccard similarity pada keyword set.

**3 Prompts** (each run `CONSISTENCY_RUNS` times, default 3):

| Prompt                                     | Expected Stable Answer |
| ------------------------------------------ | ---------------------- |
| "3 main types of cloud computing services" | IaaS, PaaS, SaaS       |
| "Default SSH port number"                  | 22                     |
| "What does RAID 5 provide?"                | Striping with parity   |

**Cara ukur:**

```python
# Setiap prompt dijalankan 3 kali
# Jaccard = |intersection| / |union| dari keyword sets
# 1.0 = jawaban identik, 0.0 = tidak ada keyword yang sama
```

**Cara memperbaiki consistency rendah:**

```python
"temperature": 0,   # Deterministic output
"seed": 42          # Fixed random seed
```

***

### Capability Benchmark 14: Domain Knowledge (`domain_knowledge_score`)

| 🟢 Good | 🟡 Acceptable | 🔴 Poor |
| ------- | ------------- | ------- |
| > 0.8   | 0.6–0.8       | < 0.6   |

**Apa ini?** Pengetahuan teknis model tentang infrastruktur dan data center: PUE, hot/cold aisle cooling, SNMP, UPS, IPMI.

**5 Test Cases:**

| Test    | Topic                      | Required Keywords   | Any-of Keywords (need ≥2)                    |
| ------- | -------------------------- | ------------------- | -------------------------------------------- |
| PUE     | Data center efficiency     | `total`, `it`, `1.` | `energy`, `power`, `efficiency`, `cooling`   |
| Cooling | Hot/cold aisle containment | `hot`, `cold`       | `aisle`, `containment`, `cooling`, `air`     |
| SNMP    | Monitoring protocol        | `snmp`              | `oid`, `monitor`, `trap`, `mib`, `agent`     |
| UPS     | Power infrastructure       | `ups`, `power`      | `battery`, `online`, `offline`, `backup`     |
| IPMI    | Remote management          | `ipmi`              | `bmc`, `remote`, `management`, `out-of-band` |

**Scoring:**

* **Full credit (1.0):** All required keywords + ≥2 any-of keywords + length > 50
* **Partial credit (0.5):** All required keywords + ≥1 any-of keywords + length > 50
* **Fail (0.0):** Missing required keywords

***

## 7. Hasil Benchmark via Ollama

**Total model diuji:** 19 model

### Top 3 Model Terbaik (Ollama)

| Peringkat | Model                                  | Total Score | Latency Avg (s) | Tokens/sec | Reasoning | Hallucination Resist | Consistency |
| --------- | -------------------------------------- | ----------- | --------------- | ---------- | --------- | -------------------- | ----------- |
| 🥇 1      | **qwen2.5-coder:1.5b**                 | 88.76       | 0.332           | 178.12     | 0.625     | 1.0                  | 0.802       |
| 🥈 2      | **phi4:14b**                           | 86.77       | 1.119           | 53.75      | 1.0       | 1.0                  | 0.404       |
| 🥉 3      | **LiquidAI/LFM2-8B-A1B-GGUF:Q4\_K\_M** | 85.41       | 0.284           | 178.53     | 0.625     | 1.0                  | 0.632       |

### Data Lengkap Semua Model (Ollama)

| Nama Model                           | Latency Avg (s) | Tokens/sec | TTFT (s) | Reasoning | RCA   | Tool Use | Long Context | Hallucination | Consistency | Domain Know. | **Total Score** |
| ------------------------------------ | --------------- | ---------- | -------- | --------- | ----- | -------- | ------------ | ------------- | ----------- | ------------ | --------------- |
| qwen2.5-coder:1.5b                   | 0.332           | 178.12     | 0.096    | 0.625     | 1.0   | 1.0      | 0.5          | 1.0           | 0.802       | 1.0          | **88.76**       |
| phi4:14b                             | 1.119           | 53.75      | 0.077    | 1.0       | 1.0   | 1.0      | 0.75         | 1.0           | 0.404       | 1.0          | **86.77**       |
| LiquidAI/LFM2-8B:Q4\_K\_M            | 0.284           | 178.53     | 0.057    | 0.625     | 1.0   | 1.0      | 0.0          | 1.0           | 0.632       | 1.0          | **85.41**       |
| llama3.1:8b                          | 0.810           | 83.44      | 0.111    | 0.5       | 1.0   | 1.0      | 0.75         | 1.0           | 0.493       | 1.0          | **85.22**       |
| qwen3.5:9b-q8\_0                     | 2.188           | 45.71      | 0.189    | 1.0       | 1.0   | 1.0      | 0.25         | 1.0           | 0.514       | 1.0          | **84.82**       |
| ministral-3:3b                       | 0.532           | 141.35     | 0.115    | 0.625     | 1.0   | 0.833    | 0.25         | 1.0           | 0.550       | 1.0          | **84.58**       |
| qwen3.5:4b-unsloth                   | 1.093           | 83.81      | 0.151    | 1.0       | 1.0   | 1.0      | 0.0          | 1.0           | 0.529       | 1.0          | **83.65**       |
| qwen3.5:9b                           | 1.561           | 64.08      | 0.181    | 1.0       | 1.0   | 1.0      | 0.0          | 1.0           | 0.509       | 1.0          | **83.55**       |
| MiniMaxAI/SynLogic-7B:Q2\_K          | 0.726           | 87.06      | 0.095    | 0.75      | 0.875 | 1.0      | 0.5          | 0.8           | 0.264       | 1.0          | **81.67**       |
| qwen3:1.7b                           | 0.518           | 200.01     | 0.085    | 0.625     | 1.0   | 0.833    | 0.0          | 0.8           | 0.634       | 1.0          | **81.35**       |
| gpt-oss:20b                          | 1.095           | 88.16      | 0.211    | 0.5       | 0.875 | 1.0      | 0.75         | 0.8           | 0.278       | 1.0          | **80.49**       |
| qwen3.5:4b                           | 1.192           | 83.92      | 0.173    | 0.5       | 1.0   | 1.0      | 0.25         | 1.0           | 0.403       | 0.8          | **78.27**       |
| deepseek-r1:1.5b                     | 0.490           | 204.32     | 0.090    | 0.75      | 0.75  | 1.0      | 0.25         | 0.6           | 0.295       | 0.8          | **77.93**       |
| Opus4.7-GODs.Ghost.Codex-4B:Q4\_K\_M | 1.198           | 83.50      | 0.153    | 0.875     | 0.875 | 1.0      | 0.0          | 0.6           | 0.318       | 0.4          | **72.29**       |
| gemma4:e4b latest                    | 1.356           | 73.76      | 2.693    | 0.5       | 0.875 | 1.0      | 0.25         | 0.8           | 0.551       | 1.0          | **68.36**       |
| mistral-small:24b                    | 6.364           | 9.14       | 0.235    | 1.0       | 1.0   | 1.0      | 0.25         | 1.0           | 0.339       | 1.0          | **65.95**       |
| qwen2.5-coder:32b                    | 105.847         | 2.11       | 0.365    | 0.75      | 0.75  | 1.0      | 0.5          | 0.2           | 0.557       | 1.0          | **53.69**       |
| gemma3:27b                           | 8.627           | 6.85       | 0.464    | 0.375     | 1.0   | 1.0      | 0.25         | 0.4           | 0.667       | 1.0          | **51.47**       |
| qwen3.6:27b                          | 31.116          | 3.21       | 1.374    | 0.0       | 0.0   | 0.0      | 0.0          | 0.2           | 0.471       | 0.0          | **12.42**       |

### Analisis Top 3 Model (Ollama)

#### 🥇 1. qwen2.5-coder:1.5b — Skor: 88.76

Model ini meraih skor tertinggi di antara seluruh model yang diuji via Ollama, menonjol berkat kombinasi **kecepatan tinggi** dan **kualitas yang kompetitif**.

* **Kecepatan:** Latency rata-rata hanya 0.332 detik dengan throughput 178.12 tokens/detik — salah satu model tercepat dalam pengujian ini.
* **Kualitas:** Skor sempurna pada RCA, Tool Use, dan Hallucination Resistance. Reasoning (0.625) dan Consistency (0.802) tetap kompetitif.
* **Efisiensi:** Penggunaan GPU sangat rendah (GPU 0: 0%, GPU 1: 0.542%) dengan VRAM minimal (\~1.2 GB / \~1.9 GB).
* **Ideal untuk:** Use case yang membutuhkan respons cepat dan efisiensi energi tinggi, terutama task coding dan analisis teknis pada hardware terbatas.

#### 🥈 2. phi4:14b — Skor: 86.77

Model dari Microsoft ini menunjukkan **kualitas penalaran terbaik** di antara semua model Ollama, meski dengan kecepatan lebih moderat.

* **Kecepatan:** Latency 1.119 detik dan throughput 53.75 tokens/detik — wajar untuk model 14B.
* **Kualitas:** Skor sempurna pada Reasoning (1.0), RCA, Tool Use, dan Hallucination Resistance. Menjadikannya model paling *reliable* untuk tugas berketelitian tinggi.
* **Kelemahan:** Consistency hanya 0.404 — paling rendah di top 3, menunjukkan variabilitas output.
* **Ideal untuk:** Aplikasi yang mengutamakan **akurasi dan reasoning mendalam** — analisis teknis kompleks, audit logika, tugas yang tidak toleran terhadap kesalahan faktual.

#### 🥉 3. LiquidAI/LFM2-8B:Q4\_K\_M — Skor: 85.41

Model dari LiquidAI ini menawarkan **keseimbangan terbaik antara kecepatan, kualitas, dan penggunaan memori** di kelas model menengah.

* **Kecepatan:** Latency tercepat di top 3 (0.284 detik) dengan throughput 178.53 tokens/detik — nyaris setara qwen2.5-coder:1.5b.
* **Kualitas:** Skor sempurna pada RCA, Tool Use, dan Hallucination Resistance.
* **Catatan:** Long Context mendapat skor 0 — tidak optimal untuk pemrosesan dokumen atau konteks panjang.
* **Ideal untuk:** Deployment produksi dengan kebutuhan **throughput tinggi dan latensi rendah** tanpa kebutuhan konteks sangat panjang.

***

## 8. Hasil Benchmark via llama.cpp

**Total model diuji:** 13 model

### Top 3 Model Terbaik (llama.cpp)

| Peringkat | Model                                          | Total Score | Latency Avg (s) | Tokens/sec | Reasoning | Hallucination Resist | Consistency |
| --------- | ---------------------------------------------- | ----------- | --------------- | ---------- | --------- | -------------------- | ----------- |
| 🥇 1      | **Qwen/Qwen3-VL-4B-Instruct-GGUF**             | 92.34       | 1.196           | 51.55      | 1.0       | 1.0                  | 0.668       |
| 🥈 2      | **bartowski/Qwen2.5.1-Coder-7B-Instruct-GGUF** | 91.47       | 0.811           | 83.76      | 0.75      | 1.0                  | 0.760       |
| 🥉 3      | **microsoft/phi-4-gguf**                       | 90.685      | 1.375           | 48.86      | 1.0       | 1.0                  | 0.503       |

### Data Lengkap Semua Model (llama.cpp)

| Nama Model                              | Latency Avg (s) | Tokens/sec | TTFT (s) | Reasoning | RCA   | Tool Use | Long Context | Hallucination | Consistency | Domain Know. | **Total Score** |
| --------------------------------------- | --------------- | ---------- | -------- | --------- | ----- | -------- | ------------ | ------------- | ----------- | ------------ | --------------- |
| Qwen3-VL-4B-Instruct-GGUF               | 1.196           | 51.55      | 0.047    | 1.0       | 1.0   | 1.0      | 1.0          | 1.0           | 0.668       | 1.0          | **92.34**       |
| Qwen2.5.1-Coder-7B-Instruct-GGUF        | 0.811           | 83.76      | 0.022    | 0.75      | 1.0   | 0.917    | 1.0          | 1.0           | 0.760       | 1.0          | **91.47**       |
| microsoft/phi-4-gguf                    | 1.375           | 48.86      | 0.037    | 1.0       | 1.0   | 0.917    | 1.0          | 1.0           | 0.503       | 1.0          | **90.69**       |
| unsloth/Gemma-4-E4B                     | 4.663           | 66.90      | 0.060    | 1.0       | 1.0   | 0.917    | 1.0          | 1.0           | 0.796       | 1.0          | **84.15**       |
| unsloth/SmolLM3-3B-128K-GGUF            | 1.940           | 136.84     | 0.027    | 1.0       | 1.0   | 0.917    | 1.0          | 0.5           | 0.371       | 1.0          | **81.03**       |
| unsloth/Qwen3.5-9B-GGUF                 | 19.100          | 63.73      | 0.118    | 1.0       | 1.0   | 0.917    | 1.0          | 1.0           | 0.768       | 1.0          | **79.01**       |
| unsloth/Qwen3.5-4B-GGUF                 | 38.532          | 27.61      | 0.403    | 1.0       | 1.0   | 1.0      | 1.0          | 1.0           | 0.789       | 1.0          | **76.95**       |
| unsloth/DeepSeek-R1-Distill-Qwen-7B     | 4.573           | 82.19      | 0.028    | 0.75      | 1.0   | 1.0      | 1.0          | 1.0           | 0.315       | 1.0          | **75.08**       |
| unsloth/Qwen3-4B-Thinking-2507-GGUF     | 6.559           | 51.42      | 0.044    | 1.0       | 1.0   | 0.917    | 1.0          | 1.0           | 0.412       | 1.0          | **74.57**       |
| nvidia/NVIDIA-Nemotron-3-Nano-4B        | 6.686           | 14.01      | 0.828    | 1.0       | 1.0   | 0.917    | 1.0          | 1.0           | 0.764       | 1.0          | **67.99**       |
| Vezora/Mistral-22B-v0.2                 | 36.873          | 27.84      | 0.239    | 0.5       | 0.875 | 0.917    | 1.0          | 0.5           | 0.248       | 1.0          | **61.16**       |
| unsloth/NVIDIA-Nemotron-3-Nano-4B (alt) | 6.275           | 14.33      | 0.817    | 0.75      | 1.0   | 0.917    | 1.0          | 0.5           | 0.790       | 1.0          | **59.62**       |
| unsloth/Qwen3.6-27B                     | 3.794           | 26.36      | 0.297    | 0.25      | 0.75  | 0.333    | 0.0          | 0.5           | 0.500       | 0.0          | **47.83**       |

### Analisis Top 3 Model (llama.cpp)

#### 🥇 1. Qwen3-VL-4B-Instruct-GGUF — Skor: 92.34 ⭐ Best Overall

Model ini meraih **skor tertinggi di seluruh benchmark** (kedua platform), menjadikannya model terbaik secara keseluruhan.

* **Kecepatan:** TTFT sangat rendah (0.047 detik), hampir tanpa jeda respons awal. Latency 1.196 detik masih sangat baik untuk model 4B VL.
* **Kualitas:** Skor sempurna pada hampir semua dimensi: Reasoning (1.0), RCA (1.0), Tool Use (1.0), Long Context (1.0), dan Hallucination Resistance (1.0) — profil kualitas terlengkap dalam seluruh benchmark.
* **Multimodal:** Sebagai model Vision-Language (VL), mampu memproses input gambar dan teks secara bersamaan.
* **Ideal untuk:** Aplikasi yang membutuhkan kapabilitas lengkap — reasoning, tool use, long context, dan dukungan multimodal.

#### 🥈 2. Qwen2.5.1-Coder-7B-Instruct-GGUF — Skor: 91.47

Model ini menawarkan **kecepatan terbaik di antara top 3 llama.cpp** dengan kualitas yang hampir sempurna.

* **Kecepatan:** Latency 0.811 detik dengan throughput 83.76 tokens/detik. TTFT terendah di seluruh benchmark (0.022 detik).
* **Kualitas:** Long Context (1.0) dan Hallucination Resistance (1.0) sempurna. Tool Use (0.917) dan Consistency (0.760) sangat baik.
* **Spesialisasi:** Unggul dalam pembuatan dan analisis kode, debugging, serta penjelasan teknis.
* **Ideal untuk:** Developer tools, code assistant, dan aplikasi dengan kebutuhan respons cepat pada lingkungan llama.cpp.

#### 🥉 3. microsoft/phi-4-gguf — Skor: 90.685

Model phi-4 via llama.cpp menunjukkan **reasoning terkuat bersama model VL** dengan profil kualitas yang sangat seimbang.

* **Kecepatan:** TTFT sangat cepat (0.037 detik). Latency 1.375 detik kompetitif untuk model dengan kapabilitas tinggi.
* **Kualitas:** Reasoning sempurna (1.0), RCA (1.0), Long Context (1.0), dan Hallucination Resistance (1.0). Konsumsi VRAM moderat (\~6.600 MB per GPU).
* **Ideal untuk:** Tugas analitis kompleks, penelitian, dan aplikasi enterprise yang membutuhkan reasoning mendalam dan akurasi faktual tinggi.

***

## 9. Perbandingan Lintas Platform

| Aspek                    | Ollama (Terbaik)           | llama.cpp (Terbaik)          |
| ------------------------ | -------------------------- | ---------------------------- |
| **Skor Tertinggi**       | 88.76 (qwen2.5-coder:1.5b) | 92.34 (Qwen3-VL-4B)          |
| **Latency Terendah**     | 0.284 s (LFM2-8B)          | 0.811 s (Qwen2.5.1-Coder-7B) |
| **Throughput Tertinggi** | 178.53 tok/s (LFM2-8B)     | 136.84 tok/s (SmolLM3-3B)    |
| **TTFT Tercepat**        | 0.057 s (LFM2-8B)          | 0.022 s (Qwen2.5.1-Coder-7B) |
| **Reasoning Terbaik**    | 1.0 (phi4:14b)             | 1.0 (Qwen3-VL-4B & phi-4)    |

### Temuan Utama

1. **llama.cpp** secara konsisten menghasilkan skor kualitas lebih tinggi, khususnya pada dimensi Long Context dan Tool Use.
2. **Ollama** unggul dalam **latensi dan throughput mentah**, cocok untuk skenario real-time dan prototyping cepat.
3. Keluarga model **Qwen** (Alibaba) mendominasi peringkat teratas di **kedua platform**, menunjukkan konsistensi arsitektur yang kuat dan sangat relevan untuk DCIM use-case.

***

## 10. Quantization Analysis

### Jenis Quantization yang Digunakan

| Tipe Quantization | Karakteristik                                               | Rekomendasi                             |
| ----------------- | ----------------------------------------------------------- | --------------------------------------- |
| **Q2\_K**         | Ultra ringan, VRAM minimal, kualitas lebih rendah           | Development / hardware sangat terbatas  |
| **Q4\_K\_M**      | Balance antara kecepatan, VRAM, dan kualitas                | **Recommended untuk production**        |
| **Q8\_0**         | Kualitas tinggi, mendekati full precision, VRAM lebih besar | Research / benchmark / quality-critical |

### Implementasi Quantization

Quantization dilakukan melalui dua metode:

* **Model GGUF (pre-quantized)** — diunduh langsung dari Hugging Face
* **Load via llama.cpp / Ollama** — runtime inference engine

### Perbandingan Dampak Quantization

| Model      | Quant    | Latency Avg | VRAM     | Total Score |
| ---------- | -------- | ----------- | -------- | ----------- |
| qwen3.5:9b | Q8\_0    | 2.188 s     | \~7.8 GB | 84.82       |
| qwen3.5:4b | Q4       | 1.192 s     | \~5.9 GB | 78.27       |
| LFM2-8B    | Q4\_K\_M | 0.284 s     | \~7.8 GB | 85.41       |

### Insight Quantization

| Quant | Dampak                             |
| ----- | ---------------------------------- |
| Q2    | ❌ Reasoning rusak — score bisa = 0 |
| Q4    | ✅ Optimal — balance terbaik        |
| Q8    | ✅ Akurat tapi lebih berat di VRAM  |

> **🔥 Critical Finding:** Quantization terlalu agresif (Q2) bisa membuat model gagal total di reasoning. Untuk DCIM production, **Q4\_K\_M** adalah titik keseimbangan optimal (Speed vs Quality).

***

## 11. Analisis Mendalam: Qwen3.5:4B vs Gemma4

> *Analisis ini berasal dari benchmark awal (benchmark\_all\_v4.py) sebelum ekspansi ke 19+ model*

### Ringkasan Perbandingan

```mermaid
flowchart LR
    subgraph QWEN["🏆 Qwen3.5:4B — 9 wins"]
        Q1["⚡ Faster (1.19s vs 1.36s)"]
        Q2["🚀 Higher TPS (84 vs 73)"]
        Q3["⏱️ Way better TTFT (0.18s vs 2.57s)"]
        Q4["🧠 Perfect Reasoning (1.0)"]
        Q5["🔍 Perfect RCA (1.0)"]
        Q6["🛡️ Perfect Hallucination (1.0)"]
        Q7["💾 Less VRAM (5.9GB vs 7.7GB)"]
        Q8["📊 Higher Throughput"]
        Q9["⚙️ Better GPU Utilization"]
    end
    subgraph GEMMA["🥈 Gemma4 — 2 wins"]
        G1["📚 Perfect Domain Knowledge (1.0)"]
        G2["🔄 Slightly better Consistency"]
    end
```

> **Verdict:** Qwen3.5:4B menang telak untuk deployment di DCIM/infrastructure monitoring. Lebih cepat, lebih akurat di reasoning & RCA, dan tidak pernah hallucinate.

### Scorecard

| Kategori              | Qwen3.5:4B | Gemma4:latest |
| --------------------- | ---------- | ------------- |
| Performance           | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐          |
| Reasoning             | ⭐⭐⭐⭐⭐      | ⭐⭐⭐           |
| RCA                   | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐          |
| Tool Use              | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐⭐         |
| Long Context          | ⭐          | ⭐             |
| Hallucination Resist. | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐          |
| Consistency           | ⭐⭐         | ⭐⭐            |
| Domain Knowledge      | ⭐⭐⭐⭐       | ⭐⭐⭐⭐⭐         |
| VRAM Efficiency       | ⭐⭐⭐⭐⭐      | ⭐⭐⭐           |

### Analisis Performa Detail

#### Performance Metrics

| Metric          | Qwen3.5:4B | Gemma4    | Pemenang     | Cara Baca                                                                               |
| --------------- | ---------- | --------- | ------------ | --------------------------------------------------------------------------------------- |
| **Latency Avg** | 🟢 1.191s  | 🟢 1.361s | Qwen         | Rata-rata waktu dari kirim prompt sampai terima jawaban penuh. Dua-duanya < 3s = bagus. |
| **Latency P95** | 🟢 1.208s  | 🟢 1.375s | Qwen         | Worst-case realistis (95% request selesai di bawah waktu ini). Qwen lebih stabil.       |
| **Tokens/sec**  | 🟢 83.99   | 🟢 73.49  | Qwen         | \~83 kata/detik. Dua-duanya sangat cepat (> 30 = bagus).                                |
| **TTFT**        | 🟢 0.179s  | 🔴 2.569s | **Qwen >>>** | **Gemma 14x lebih lambat.** User harus menunggu hampir 3 detik sebelum jawaban muncul.  |
| **Throughput**  | 🟡 0.932   | 🟡 0.833  | Qwen         | Request per detik saat concurrent. Normal untuk single-GPU (Ollama sequential).         |

#### GPU Metrics

| Metric           | Qwen3.5:4B  | Gemma4      | Cara Baca                                                                                       |
| ---------------- | ----------- | ----------- | ----------------------------------------------------------------------------------------------- |
| **GPU Util Avg** | 🟢 84.8%    | 🔴 7.67%    | Qwen memanfaatkan GPU secara efisien. Gemma hanya 7.67% — kemungkinan ada timing sampling miss. |
| **GPU VRAM Avg** | 🟢 5.910 MB | 🟡 7.680 MB | Qwen butuh \~5.9GB VRAM, Gemma butuh \~7.7GB. **Di GPU 8GB, Gemma hampir penuh.**               |

#### Capability Metrics

| Capability           | Qwen3.5:4B   | Gemma4       | Analisis                                                                                |
| -------------------- | ------------ | ------------ | --------------------------------------------------------------------------------------- |
| **Reasoning**        | 🟢 **1.000** | 🔴 **0.500** | Qwen sempurna di 4 soal logika. Gemma gagal di soal redistribusi load.                  |
| **RCA**              | 🟢 **1.000** | 🟢 **0.875** | Qwen perfect di semua root cause. Gemma miss satu (cron tidak disebutkan eksplisit).    |
| **Tool Use**         | 🟢 **1.000** | 🟢 **1.000** | Keduanya sempurna dalam memilih tool dan menulis syntax function call.                  |
| **Long Context**     | 🔴 **0.250** | 🔴 **0.250** | ⚠️ Kelemahan besar keduanya. Hanya benar 1 dari 4 pertanyaan dari \~200 baris log.      |
| **Hallucination**    | 🟢 **1.000** | 🟡 **0.800** | Qwen sempurna. Gemma gagal di 1 test (respons terpotong saat ditanya Intel Xeon 8490H). |
| **Consistency**      | 🔴 **0.380** | 🔴 **0.390** | Keduanya rendah. Perlu `temperature: 0` untuk deterministic output.                     |
| **Domain Knowledge** | 🟡 **0.800** | 🟢 **1.000** | Gemma sempurna di 5 topik infra. Qwen PASS di 4, partial di 1.                          |

### Isu Bersama yang Perlu Diatasi

| Masalah                      | Solusi                                                                                                 |
| ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| Long Context rendah (\~0.25) | Gunakan **RAG (Retrieval Augmented Generation)** untuk log analysis — jangan kirim semua log sekaligus |
| Consistency rendah (\~0.38)  | Set `temperature: 0` untuk pipeline automation, atau gunakan structured JSON output                    |

***

## 12. Final Recommendation untuk DCIM

### Rekomendasi Berdasarkan Skenario

| Skenario                          | Model Rekomendasi                | Platform  |
| --------------------------------- | -------------------------------- | --------- |
| **Performa serba-bisa terbaik**   | Qwen3-VL-4B-Instruct-GGUF        | llama.cpp |
| **Developer & coding assistant**  | Qwen2.5.1-Coder-7B-Instruct-GGUF | llama.cpp |
| **Analisis & reasoning mendalam** | microsoft/phi-4-gguf             | llama.cpp |
| **Deployment ringan & cepat**     | qwen2.5-coder:1.5b               | Ollama    |
| **Akurasi tinggi via Ollama**     | phi4:14b                         | Ollama    |

### Konfigurasi Deployment DCIM

| Aspek                   | Rekomendasi                                         |
| ----------------------- | --------------------------------------------------- |
| **Model Family**        | Qwen series (dominan di kedua platform)             |
| **Quantization**        | Q4\_K\_M (balance antara kualitas dan efisiensi)    |
| **Platform Production** | Ollama (kemudahan, latensi rendah)                  |
| **Platform Optimasi**   | llama.cpp (kualitas lebih tinggi, kontrol granular) |

### Alasan Pemilihan Qwen sebagai Model Utama

| Alasan            | Detail                                                     |
| ----------------- | ---------------------------------------------------------- |
| Tidak hallucinate | Skor 1.0 pada Hallucination Resistance                     |
| RCA sempurna      | Mampu mendiagnosis semua skenario infrastruktur            |
| Reasoning kuat    | Bisa menghitung dan menganalisis dependency chain          |
| Efisiensi VRAM    | Lebih aman di RTX 3070 Ti dibanding model lain             |
| TTFT rendah       | User experience jauh lebih baik untuk real-time monitoring |

### Best Practice Deployment

| Layer           | Rekomendasi |
| --------------- | ----------- |
| Fast API        | Ollama      |
| Heavy reasoning | llama.cpp   |
| Quantization    | Q4\_K\_M    |
| Multi-GPU       | llama.cpp   |

***

## 13. Cara Menjalankan Benchmark

### Prerequisites

```shellscript
pip install requests numpy pynvml
```

### Pull Model

```shellscript
ollama pull qwen2.5-coder:1.5b
ollama pull phi4:14b
```

### Jalankan Script (V4)

```shellscript
cd /home/infra/benchmark_model/benchmark_comparation
python benchmark_all_v4.py
```

### Terminal Output

```
============================================================
  BENCHMARK ALL v4 — Full LLM Evaluation Suite
  Models: qwen3.5:4b, gemma4:latest
  Endpoint: http://localhost:11434/api/generate
  Benchmarks: 14 (7 performance + 7 capability)
============================================================

  TESTING: qwen3.5:4b
  [0/14] Warming up model...
  [1/14] Latency + TPS...
  [2/14] TTFT...
  ...
  [12/14] Domain Knowledge (Infra/DCIM)...
```

### Estimasi Runtime

| Phase                            | Per Model         | Catatan                          |
| -------------------------------- | ----------------- | -------------------------------- |
| Performance benchmarks (1–5)     | \~2 menit         | Sama seperti v3                  |
| Reasoning (4 tests)              | \~1 menit         | 500 tokens each                  |
| RCA (4 tests)                    | \~2 menit         | 800 tokens each                  |
| Tool Use (3 tests)               | \~1.5 menit       | 800 tokens each                  |
| Long Context (4 questions)       | \~2 menit         | Large prompt + 200-token answers |
| Hallucination (5 tests)          | \~1.5 menit       | 400 tokens each                  |
| Consistency (3 prompts × 3 runs) | \~2 menit         | 9 total inferences               |
| Domain Knowledge (5 tests)       | \~2 menit         | 600 tokens each                  |
| **Total per model**              | **\~12–15 menit** |                                  |
| **Total (2 model)**              | **\~25–30 menit** |                                  |

### Output JSON

Hasil benchmark tersimpan otomatis ke `benchmark_v4_results.json`:

```json
[
  {
    "model": "qwen2.5-coder:1.5b",
    "latency_avg": 0.332,
    "reasoning_score": 0.625,
    "rca_score": 1.0,
    "hallucination_score": 1.0,
    "total_score": 88.76
  }
]
```

***

## 14. Migrasi & Optimasi llama.cpp (V5 Extension)

### Latar Belakang Migrasi

Pada implementasi awal (V4), benchmark menggunakan **Ollama** sebagai backend. Namun ditemukan limitasi utama:

> ⚠️ Ollama hanya menggunakan **1 GPU per model**, padahal server memiliki 2× NVIDIA RTX 3070 Ti.

**Solusi:** Migrasi ke **llama.cpp (llama-server)**

Keuntungan llama.cpp:

* Multi-GPU support via `-ngl`
* Kontrol penuh terhadap inference
* Lebih optimal untuk benchmarking advanced

### Arsitektur Baru (V5)

| Komponen | V4 (Ollama)     | V5 (llama.cpp)             |
| -------- | --------------- | -------------------------- |
| Endpoint | `/api/generate` | `/v1/chat/completions`     |
| Format   | Prompt-based    | Chat-based (OpenAI format) |
| GPU      | Single GPU      | Multi-GPU                  |
| Kontrol  | Limited         | Full control               |

### Cara Menjalankan Benchmark V5

#### Step 1 — Start Server

```shellscript
/home/infra/llama.cpp/build/bin/llama-server \
  -hf unsloth/Qwen1.5-4B-Chat-GGUF:Q8_0 \
  -c 4096 \
  -ngl 99 \
  --port 8080
```

| Parameter | Fungsi                 |
| --------- | ---------------------- |
| `-hf`     | Auto download model    |
| `-c`      | Context window         |
| `-ngl`    | GPU layers (multi-GPU) |
| `--port`  | API endpoint           |

#### Step 2 — Jalankan Benchmark

```shellscript
python3 benchmark_all_v5.py "Qwen1.5-4B-Q8"
```

Output: `benchmark_v5_<model>.json`

### Perubahan Script (V4 → V5)

#### JSON Request

V4:

```json
{"prompt": "text"}
```

V5:

```json
{
  "messages": [
    {"role": "user", "content": "text"}
  ]
}
```

#### Response Parsing

Harus handle:

```json
data["choices"][0]["message"]["content"]
```

### Technical Challenges & Fixes

#### 1. Segmentation Fault (KV Cache)

|             |                                                            |
| ----------- | ---------------------------------------------------------- |
| **Masalah** | `max_tokens = 10000` → context overflow                    |
| **Solusi**  | Limit ke 1500 (default), hanya reasoning pakai high tokens |

#### 2. Scoring Error (Jawaban Pendek)

|             |                                                         |
| ----------- | ------------------------------------------------------- |
| **Masalah** | Model jawab "no." → dianggap salah                      |
| **Solusi**  | Hapus limit panjang teks, gunakan keyword-based scoring |

#### 3. Tool Calling Invisible

|                |                                                        |
| -------------- | ------------------------------------------------------ |
| **Masalah**    | Output kosong                                          |
| **Root cause** | `tool_call` masuk JSON, bukan text                     |
| **Fix**        | `if "tool_calls" in response: extract function + args` |

#### 4. Empty Output (Chat Template Bug)

|             |                                                                                                            |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| **Masalah** | Model langsung EOS                                                                                         |
| **Fix**     | Tambahkan system prompt: `{"role": "system", "content": "You are a helpful IT infrastructure assistant."}` |

### Multi-GPU Optimization

**Konfigurasi optimal:**

```shellscript
-ngl 99
```

Artinya semua layer masuk GPU dengan load balance ke multi GPU.

| Metric     | Before | After        |
| ---------- | ------ | ------------ |
| Latency    | Tinggi | Lebih rendah |
| Throughput | Normal | Lebih tinggi |
| GPU usage  | 1 GPU  | 2 GPU        |

### Model Management (llama.cpp)

```shellscript
# Cek model aktif
curl http://localhost:8080/v1/models

# Lokasi model cache
~/.cache/huggingface/hub/

# Jalankan model lokal
llama-server -m /path/model.gguf

# Swap model
Ctrl + C
llama-server -m model_baru.gguf
```

***

## 15. Model Preparation — LLM Dataset Generation Pipeline

> **Tanggal dibuat:** 4 Mei 2026 | **Terakhir diupdate:** 4 Mei 2026
> **Konteks:** Kelanjutan dari MT-023 — menyiapkan dataset dan fine-tuning LLM domain DCIM

### 15.1 Overview Pipeline

Pipeline ini mengubah output dari sistem DCIM AI (MT-018 s.d MT-022) menjadi dataset training untuk fine-tuning LLM agar menjadi domain-aware DCIM AI Assistant.

#### Arsitektur Pipeline

```
PostgreSQL (server_metrics: 19.347 rows)
        ↓
[1] Dataset Generator (simulasi full pipeline)
        ↓
    raw_incidents.jsonl (2.088 records)
        ↓
[2] Text Enrichment (JSON → Natural Language)
        ↓
    enriched_incidents.jsonl (2.088 records)
        ↓
[3] Instruction Builder (→ instruction tuning format)
        ↓
    dcim_instructions.jsonl (3.816 samples)
        ↓
[4] Fine-Tuning (QLoRA) ← NEXT STEP
        ↓
    DCIM AI Assistant Model
```

### 15.2 Konfigurasi Sistem

#### Environment

| Komponen            | Detail                                  |
| ------------------- | --------------------------------------- |
| Server              | srv-rnd-llm (VM QEMU/KVM)               |
| OS                  | Ubuntu 24.04 LTS                        |
| Python              | 3.12.3                                  |
| Virtual Environment | `/home/infra/rnd_rag-anything/ragavenv` |
| Working Directory   | `/home/infra/rnd_rag-anything/`         |

#### Database

| Parameter      | Nilai                                                             |
| -------------- | ----------------------------------------------------------------- |
| Engine         | PostgreSQL 16                                                     |
| Connection     | `postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai` |
| Tabel utama    | `server_metrics` (19.442 rows, 12-19 Feb 2026)                    |
| Tabel audit    | `anomaly_events` (47 rows)                                        |
| Tabel registry | `model_registry` (5 rows)                                         |

#### Model ML (Production)

| Parameter | Nilai                                                      |
| --------- | ---------------------------------------------------------- |
| Version   | v1.4                                                       |
| Algoritma | Ensemble (IsolationForest + LOF + OCSVM)                   |
| Features  | `cpu_usage`, `memory_usage`, `disk_io`, `net_rx`, `net_tx` |
| Artifacts | `dcim_ai/artifacts/models/v1.4/`                           |
| Registry  | `dcim_ai/registry/registry.json`                           |

#### Python Dependencies (sudah terinstall di ragavenv)

```
torch==2.9.1
transformers==4.57.5
huggingface-hub==0.36.0
numpy
pandas
scikit-learn
sqlalchemy
psycopg2-binary
joblib
```

### 15.3 File yang Dibuat

#### Scripts

| File                                 | Fungsi                                 | Lines |
| ------------------------------------ | -------------------------------------- | ----- |
| `dcim_ai/llm/__init__.py`            | Module init                            | 1     |
| `dcim_ai/llm/dataset_generator.py`   | Simulasi full DCIM pipeline → raw JSON | \~380 |
| `dcim_ai/llm/text_enrichment.py`     | Konversi JSON → natural language       | \~280 |
| `dcim_ai/llm/instruction_builder.py` | Build instruction tuning dataset       | \~300 |

#### Output Datasets

| File                                            | Records | Size   | Deskripsi                    |
| ----------------------------------------------- | ------- | ------ | ---------------------------- |
| `dcim_ai/llm/datasets/raw_incidents.jsonl`      | 2.088   | 2.9 MB | Structured JSON per incident |
| `dcim_ai/llm/datasets/enriched_incidents.jsonl` | 2.088   | 6.5 MB | + Natural language fields    |
| `dcim_ai/llm/datasets/dcim_instructions.jsonl`  | 3.816   | 2.8 MB | Format instruction tuning    |

### 15.4 Detail Setiap Komponen

#### 15.4.1 Dataset Generator (`dataset_generator.py`)

**Fungsi:** Mensimulasikan seluruh pipeline DCIM AI terhadap data `server_metrics` untuk menghasilkan dataset structured JSON.

**Pipeline yang disimulasikan:**

1. **Ensemble Prediction** — 3 model (IForest, LOF, OCSVM), majority vote ≥2/3
2. **Drift Detection** — Z-score terhadap baseline mean/std
3. **Domain Scoring** — Map feature z-scores ke domain (compute, memory, storage, network)
4. **Temporal Correlation** — Sliding window 20 snapshots
5. **Aggregation** — anomaly\_ratio, domain\_persistence, co-occurrence, trend
6. **Severity Matrix** — Escalation rules
7. **Root Cause Analysis** — Softmax + composite scoring + causal chain (DFS)

**Konfigurasi:**

```python
DB_URL = "postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai"
WINDOW_SIZE = 20  # sliding window untuk temporal correlation
FEATURE_COLUMNS = ["cpu_usage", "memory_usage", "disk_io", "net_rx", "net_tx"]
DOMAIN_ACTIVATION_THRESHOLD = 3.0  # z-score threshold
```

**Output record structure:**

```json
{
  "id": 1,
  "timestamp": "2026-02-12 ...",
  "hostname": "srv-rnd-llm",
  "model_version": "v1.4",
  "metrics": {"cpu_usage": 85.2, "memory_usage": 72.1, ...},
  "prediction": {"result": "anomaly", "anomaly_votes": 3, "severity": "critical", ...},
  "drift": {"score": 2.5, "status": "moderate_drift", "feature_z_scores": {...}},
  "domain_state": {"domain_scores": {...}, "active_domains": [...], ...},
  "aggregation": {"anomaly_ratio": 0.8, "domain_trend": {...}, ...},
  "incident": {"severity": "critical", "confidence": 0.95},
  "rca": {"root_domain": "memory", "confidence": 0.88, "causal_chain": [...], ...}
}
```

**Filter:** Hanya menyimpan record yang memiliki "signal" (anomaly, drift non-stable, atau active domains).

#### 15.4.2 Text Enrichment (`text_enrichment.py`)

**Fungsi:** Mengkonversi setiap field structured JSON menjadi natural language explanation.

**7 jenis enrichment yang dihasilkan:**

| Field                 | Deskripsi           | Contoh                                                                                        |
| --------------------- | ------------------- | --------------------------------------------------------------------------------------------- |
| `nl_summary`          | Ringkasan kondisi   | "Sistem mendeteksi anomali dengan kondisi KRITIS pada domain memori (RAM)..."                 |
| `nl_metrics`          | Deskripsi metrik    | "CPU usage tinggi (85.2%); memory usage kritis (92.1%)..."                                    |
| `nl_drift`            | Analisis drift      | "Drift score: 2.50 (moderate\_drift). Fitur dengan drift tertinggi: memory\_usage (z=4.2)..." |
| `nl_domain`           | Analisis domain     | "Domain aktif: memori (RAM) (skor: 4.2). Domain strength index: 3.8..."                       |
| `nl_temporal`         | Analisis temporal   | "Dalam window 20 snapshot terakhir: rasio anomali 80%, tren meningkat pada memori..."         |
| `nl_rca`              | Analisis root cause | "Root cause: domain memori (RAM) sebagai penyebab utama dengan confidence 88%..."             |
| `nl_recommendation`   | Rekomendasi         | "Eskalasi segera. Periksa memory leak, pertimbangkan restart service..."                      |
| `nl_full_explanation` | Gabungan semua      | Semua field di atas digabung                                                                  |

#### 15.4.3 Instruction Builder (`instruction_builder.py`)

**Fungsi:** Mengkonversi enriched records menjadi format instruction tuning `{instruction, input, output}`.

**9 kategori instruction:**

| Kategori         | Variasi Prompt | Contoh                                                       |
| ---------------- | -------------- | ------------------------------------------------------------ |
| `summary`        | 6              | "Jelaskan kondisi sistem berdasarkan data berikut."          |
| `anomaly`        | 5              | "Apakah ada anomali yang terdeteksi? Jelaskan."              |
| `root_cause`     | 6              | "Apa root cause dari masalah ini?"                           |
| `impact`         | 5              | "Apa dampak dari kondisi ini terhadap infrastruktur?"        |
| `recommendation` | 6              | "Apa rekomendasi tindakan untuk kondisi ini?"                |
| `drift`          | 4              | "Analisis drift dari data monitoring berikut."               |
| `domain`         | 4              | "Domain infrastruktur mana yang terpengaruh?"                |
| `temporal`       | 4              | "Bagaimana tren temporal dari kondisi ini?"                  |
| `full_analysis`  | 4              | "Lakukan analisis lengkap terhadap data monitoring berikut." |

**Output format:**

```json
{
  "id": 1,
  "instruction": "Apa root cause dari masalah ini?",
  "input": "Server metrics — cpu_usage: 0.6, memory_usage: 29.7...",
  "output": "Root cause analysis menunjukkan domain memori (RAM) sebagai penyebab utama...",
  "metadata": {
    "source_id": 1263,
    "instruction_type": "root_cause",
    "severity": "critical",
    "prediction": "anomaly",
    "root_domain": "memory",
    "timestamp": "2026-02-12 09:02:44..."
  }
}
```

### 15.5 Statistik Dataset Final

#### Distribusi Instruction Type

| Type           | Count | %     |
| -------------- | ----- | ----- |
| drift          | 757   | 19.8% |
| summary        | 713   | 18.7% |
| temporal       | 643   | 16.9% |
| recommendation | 324   | 8.5%  |
| anomaly        | 323   | 8.5%  |
| root\_cause    | 321   | 8.4%  |
| full\_analysis | 320   | 8.4%  |
| domain         | 295   | 7.7%  |
| impact         | 120   | 3.1%  |

#### Distribusi Severity

| Severity     | Count | %     |
| ------------ | ----- | ----- |
| normal       | 2.093 | 54.8% |
| warning      | 870   | 22.8% |
| weak\_signal | 542   | 14.2% |
| critical     | 306   | 8.0%  |
| high         | 5     | 0.1%  |

#### Distribusi Root Domain

| Root Domain | Count                |
| ----------- | -------------------- |
| unknown     | 1.728 (82.8% of raw) |
| memory      | 245 (11.7%)          |
| compute     | 115 (5.5%)           |

### 15.6 Cara Menjalankan Pipeline

#### Prerequisites

```shellscript
# Aktivasi virtual environment
source /home/infra/rnd_rag-anything/ragavenv/bin/activate

# Pastikan working directory
cd /home/infra/rnd_rag-anything
```

#### Step 1: Generate Raw Dataset

```shellscript
python -m dcim_ai.llm.dataset_generator
```

**Output:** `dcim_ai/llm/datasets/raw_incidents.jsonl`
**Durasi:** \~2-3 menit (19.347 samples)
**Requirement:** PostgreSQL running, model artifacts di `dcim_ai/artifacts/models/v1.4/`

> **⚠️ Troubleshooting: FileNotFoundError registry.json**
>
> Jika muncul error:
> ```
> FileNotFoundError: [Errno 2] No such file or directory:
> '/home/infra/dcim_project/implementation/dcim_ai/registry/registry.json'
> ```
>
> **Penyebab:** `dcim_ai` di `/home/infra/rnd_rag-anything/` adalah symlink ke `/home/infra/dcim_project/implementation/dcim_ai_v2_rag/`. Script menggunakan `Path(__file__).resolve()` yang mengikuti symlink, sehingga PROJECT_ROOT terhitung dari lokasi asli symlink, bukan lokasi kerja.
>
> **Solusi:** Sudah diperbaiki di kode dengan mengubah urutan resolve:
> ```python
> # Before (salah):
> PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
>
> # After (benar):
> PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
> ```
>
> Dengan cara ini, path parent dihitung dulu sebelum resolve, sehingga PROJECT_ROOT menunjuk ke `/home/infra/rnd_rag-anything` (lokasi symlink), bukan lokasi asli file.

#### Step 2: Text Enrichment

```shellscript
python -m dcim_ai.llm.text_enrichment
```

**Output:** `dcim_ai/llm/datasets/enriched_incidents.jsonl`
**Durasi:** \~10 detik

#### Step 3: Build Instruction Dataset

```shellscript
python -m dcim_ai.llm.instruction_builder --target 1500
```

**Output:** `dcim_ai/llm/datasets/dcim_instructions.jsonl`
**Durasi:** \~5 detik
**Parameter:** `--target` = target jumlah samples (default: 1000)

#### Run All (Sequential)

```shellscript
cd /home/infra/rnd_rag-anything
source ragavenv/bin/activate

python -m dcim_ai.llm.dataset_generator && \
python -m dcim_ai.llm.text_enrichment && \
python -m dcim_ai.llm.instruction_builder --target 1500
```

### 15.7 Testing & Verifikasi

#### Verifikasi File Output

```shellscript
du -sh dcim_ai/llm/datasets/*.jsonl
wc -l dcim_ai/llm/datasets/*.jsonl
```

Expected:

```
2.9M    raw_incidents.jsonl
6.5M    enriched_incidents.jsonl
2.8M    dcim_instructions.jsonl

2088 raw_incidents.jsonl
2088 enriched_incidents.jsonl
3816 dcim_instructions.jsonl
```

#### Verifikasi Kualitas Dataset

```shellscript
python3 -c "
import json
from collections import Counter

with open('dcim_ai/llm/datasets/dcim_instructions.jsonl') as f:
    records = [json.loads(l) for l in f]

print(f'Total samples: {len(records)}')

types = Counter(r['metadata']['instruction_type'] for r in records)
print(f'Instruction types: {dict(types)}')

sevs = Counter(r['metadata']['severity'] for r in records)
print(f'Severity: {dict(sevs)}')
"
```

### 15.8 Troubleshooting Pipeline

| Error                              | Penyebab                        | Solusi                                                                |
| ---------------------------------- | ------------------------------- | --------------------------------------------------------------------- |
| `Failed postgresql+psycopg2://...` | PostgreSQL tidak berjalan       | `sudo systemctl status postgresql`                                    |
| `FileNotFoundError: models.pkl`    | Artifacts model tidak ditemukan | `ls dcim_ai/artifacts/models/v1.4/`                                   |
| Empty Dataset (0 records)          | Data server\_metrics NULL       | Cek `SELECT COUNT(*) FROM server_metrics WHERE cpu_usage IS NOT NULL` |

### 15.9 Keterkaitan dengan Dokumen Referensi

| Dokumen                                  | Relevansi                                                |
| ---------------------------------------- | -------------------------------------------------------- |
| MT-018 (Traditional ML Model)            | Source: model artifacts, feature columns, baseline stats |
| MT-019 (Anomaly Detection Framework)     | Source: ensemble voting, drift detection, model registry |
| MT-020 (Cross-Domain Correlation Engine) | Source: domain mapping, correlation buffer, aggregation  |
| MT-021 (Model Training Lifecycle)        | Source: training orchestrator, artifact structure        |
| MT-022 (Root Cause Analysis Engine)      | Source: RCA engine, causal topology, lifecycle manager   |
| MT-023 (Private LLM Platform)            | Context: benchmark results, model selection (Qwen3.5:4B) |

### 15.10 Fine-Tuning Configuration (QLoRA)

#### Base Model

| Parameter          | Nilai                                                         |
| ------------------ | ------------------------------------------------------------- |
| Model              | `Qwen/Qwen2.5-3B-Instruct`                                    |
| Method             | QLoRA (BitsAndBytes 4-bit NF4)                                |
| Size               | 6.2 GB full-weight (lokal di HF cache)                        |
| Architecture       | Qwen2, 36 layers, hidden=2048, vocab=152064                   |
| Location           | `~/.cache/huggingface/hub/models--Qwen--Qwen2.5-3B-Instruct/` |
| VRAM saat training | \~5.5 GB (muat di 1× RTX 3070 Ti 8GB)                         |

#### Kenapa Qwen2.5-3B-Instruct?

| Pertimbangan                     | Detail                                                                                       |
| -------------------------------- | -------------------------------------------------------------------------------------------- |
| **VRAM constraint**              | 1× RTX 3070 Ti = 8GB. Model 7B QLoRA butuh \~10-12GB → OOM. Model 3B QLoRA = \~5.5GB → muat. |
| **AWQ deprecated**               | `Qwen2.5-7B-AWQ` tidak bisa dipakai — `autoawq` incompatible dengan `transformers 4.57.5`    |
| **GGUF tidak bisa di-fine-tune** | Model GGUF hanya untuk llama.cpp/Ollama — tidak bisa di-load dengan PEFT/LoRA                |
| **Narrow domain**                | Task DCIM terstruktur dan repetitif — 3B parameter + LoRA sudah cukup                        |

#### Parameter Fine-Tuning

```python
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
BATCH_SIZE = 1
GRAD_ACCUM = 16          # effective batch = 16
MAX_SEQ_LEN = 512
EPOCHS = 3
LR = 2e-4
QUANTIZATION = "BitsAndBytes NF4 (load_in_4bit)"
OPTIMIZER = "paged_adamw_8bit"
TRAINABLE_PARAMS = "29.9M / 3.1B (0.96%)"
```

#### Baseline Evaluation (Pre-Fine-Tune)

Model base (Qwen3-VL-4B) dievaluasi terhadap 6 test DCIM:

| Metric            | Score                    |
| ----------------- | ------------------------ |
| Overall Relevance | **0.83 / 1.0** (🟢 GOOD) |
| Keyword Score     | 0.69 / 1.0               |
| Average Latency   | 4.8s                     |
| Tests Passed      | **6/6**                  |

Per-category:

* ✅ anomaly\_detection: 100% keywords
* ✅ root\_cause: 75% keywords
* ✅ recommendation: 80% keywords
* ✅ drift\_analysis: 50% keywords
* ✅ normal\_condition: 67% keywords
* ✅ multi\_domain: 40% keywords

#### Synthetic Dataset Enhancement

| Metric                       | Nilai                              |
| ---------------------------- | ---------------------------------- |
| Samples enhanced             | 200 / 200 (0 failed)               |
| Avg output length (LLM)      | **1.259 chars**                    |
| Avg output length (template) | 194 chars                          |
| Enhancement ratio            | 6.5x lebih kaya                    |
| Output file                  | `dcim_instructions_enhanced.jsonl` |

#### Cara Menjalankan Fine-Tuning

```shellscript
# 1. Stop llama-server (free GPU VRAM)
# 2. Jalankan fine-tuning
cd /home/infra/rnd_rag-anything
source ragavenv/bin/activate
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
python -m dcim_ai.llm.finetune_qlora \
    --epochs 3 --batch-size 1 --grad-accum 16 \
    --max-seq-len 512 --gpu 0 --version v1.0

# 3. Evaluate
python -m dcim_ai.llm.evaluate_model --adapter dcim_ai/llm/models/v1.0/adapter

# 4. Export ke GGUF
python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step all

# 5. Deploy via Ollama
ollama create dcim-ai -f dcim_ai/llm/models/v1.0/Modelfile
```

#### Error yang Ditemui & Solusi (Model Preparation)

| Error                             | Penyebab                                                  | Solusi                                            |
| --------------------------------- | --------------------------------------------------------- | ------------------------------------------------- |
| `ImportError: autoawq`            | AWQ library belum terinstall                              | `pip install autoawq`                             |
| `cannot import 'PytorchGELUTanh'` | AutoAWQ deprecated, incompatible dengan transformers 4.57 | Switch ke BitsAndBytes QLoRA + model full-weight  |
| `TypeError: max_seq_length`       | trl 1.3.0 menggunakan `SFTConfig.max_length`              | Gunakan `SFTConfig(max_length=512)`               |
| `NotImplementedError: BFloat16`   | fp16 grad scaler tidak support BFloat16                   | Set `bf16=True, fp16=False`                       |
| `CUDA out of memory`              | batch\_size=2 + seq\_len=1024 + 3B model                  | Turunkan ke batch\_size=1, seq\_len=512 (\~5.5GB) |

### 15.11 Task 4 — Model Versioning & Deployment

#### Struktur Artifact (Setelah Fine-Tune)

**Status Saat Ini (Setelah Training):**
```
dcim_ai/llm/models/
└── v1.0/
    ├── adapter/           # ✅ LoRA adapter weights (TERSEDIA)
    │   ├── adapter_config.json
    │   ├── adapter_model.safetensors
    │   └── tokenizer files
    ├── checkpoints/       # ✅ Training checkpoints (TERSEDIA)
    │   ├── checkpoint-600/
    │   └── checkpoint-645/
    ├── metadata.json      # ✅ Training metadata (TERSEDIA)
    └── train_metrics.json # ✅ Training loss/metrics (TERSEDIA)
```

**Struktur Lengkap (Setelah Export - ✅ SELESAI):**
```
dcim_ai/llm/models/
└── v1.0/
    ├── adapter/           # ✅ LoRA adapter weights
    ├── checkpoints/       # ✅ Training checkpoints
    ├── merged/            # ✅ Full merged model (HF format, 5.9GB)
    ├── dcim-ai-f16.gguf  # ✅ GGUF F16 (5.9GB)
    ├── dcim-ai-Q4_K_M.gguf  # ✅ GGUF quantized (1.8GB)
    ├── Modelfile          # ✅ Ollama deployment file (using Q4_K_M)
    ├── metadata.json      # ✅ Training metadata
    └── train_metrics.json # ✅ Training loss/metrics
```

> **✅ Export Berhasil Lengkap!**
> - Merge: ✅ Berhasil (merged model 5.9GB)
> - Convert: ✅ Berhasil (dcim-ai-f16.gguf 5.9GB)
> - Quantize: ✅ Berhasil (dcim-ai-Q4_K_M.gguf 1.8GB)
> - Modelfile: ✅ Dibuat (menggunakan Q4_K_M untuk efisiensi VRAM)

#### Cara Export ke GGUF (Optional)

```shellscript
# Merge adapter + convert ke GGUF + quantize
python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step all

# Atau step by step:
python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step merge
python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step convert
python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step quantize
```

> **⚠️ Troubleshooting: Export GGUF Issues (RESOLVED)**
>
> **Masalah 1: BASE_MODEL tidak sesuai** ✅ FIXED
> - Script `export_gguf.py` awalnya menggunakan `Qwen/Qwen2.5-7B-Instruct-AWQ`
> - Tapi training menggunakan `Qwen/Qwen2.5-3B-Instruct` (lihat `metadata.json`)
> - **Solusi:** Sudah diperbaiki ke `Qwen/Qwen2.5-3B-Instruct`
>
> **Masalah 2: Path symlink (sama seperti dataset_generator)** ✅ FIXED
> - `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent` mengikuti symlink
> - `LLAMA_CPP_DIR = PROJECT_ROOT.parent / "llama.cpp"` mencari di lokasi salah
> - **Solusi:** Ubah ke `PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()`
>
> **Masalah 3: AWQ model tidak bisa di-load ke CPU** ✅ FIXED
> - Error: `AWQ model with a device_map that contains a CPU or disk device`
> - Base model ternyata AWQ variant, tidak support CPU-only loading
> - **Solusi:** Ubah `device_map="cpu"` ke `device_map="auto"` (gunakan GPU)
>
> **Masalah 4: quantize binary path salah** ✅ FIXED
> - Script mencari di `/build/tools/quantize` (direktori, bukan file)
> - Binary sebenarnya di `/build/bin/llama-quantize`
> - **Solusi:** Cek multiple paths dan validasi dengan `.is_file()`
>
> **Masalah 5: llama-quantize binary tidak ada** ✅ FIXED
> - Binary tidak di-build saat compile llama.cpp
> - **Solusi:** Build dengan `cmake --build . --target llama-quantize`
>
> **Status Export Final:**
> - ✅ Merge: Berhasil (merged model 5.9GB)
> - ✅ Convert: Berhasil (dcim-ai-f16.gguf 5.9GB)
> - ✅ Quantize: Berhasil (dcim-ai-Q4_K_M.gguf 1.8GB)
> - ✅ Modelfile: Dibuat (menggunakan Q4_K_M)
>
> **Requirement untuk export:**
> - llama.cpp sudah di-build: `cd llama.cpp && make`
> - llama-quantize binary: `cd llama.cpp/build && cmake --build . --target llama-quantize`
> - VRAM cukup untuk load base model (3B model ~6-7GB untuk merge)
> - Disk space ~15GB untuk merged model + GGUF files

#### Deployment Options

| Method        | Command                                                    | Use Case            | Status      | VRAM    |
| ------------- | ---------------------------------------------------------- | ------------------- | ----------- | ------- |
| Python (PEFT) | `evaluate_model.py --adapter path/to/adapter`              | Development/testing | ✅ Tersedia | ~6-7GB  |
| Ollama (Q4)   | `ollama create dcim-ai -f Modelfile && ollama run dcim-ai` | Easy deployment (recommended) | ✅ Tersedia | ~1.8GB  |
| llama-server (Q4) | `llama-server -m dcim-ai-Q4_K_M.gguf -ngl 99 --port 8080`  | Production API (optimized) | ✅ Tersedia | ~1.8GB  |
| llama-server (F16) | `llama-server -m dcim-ai-f16.gguf -ngl 99 --port 8080` | Production API (full precision) | ✅ Tersedia | ~5.9GB  |

**Cara Deploy dengan Ollama (Recommended):**
```bash
cd /home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0
ollama create dcim-ai -f Modelfile
ollama run dcim-ai

# Test query
ollama run dcim-ai "Jelaskan apa itu anomaly detection dalam DCIM"
```

**Cara Deploy dengan llama-server:**
```bash
cd /home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0
llama-server -m dcim-ai-Q4_K_M.gguf -ngl 99 --port 8080 --host 0.0.0.0

# Test dengan curl
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Apa itu drift detection?"}],
    "temperature": 0.3
  }'
```

### 15.12 Contoh Chat Instruction

Model telah di-training dengan **3,816 instruction samples** dalam **9 kategori** analisis DCIM. Lihat dokumentasi lengkap:

📖 **[DCIM_AI_CHAT_EXAMPLES.md](./DCIM_AI_CHAT_EXAMPLES.md)** - Contoh lengkap dengan expected output
📋 **[DCIM_AI_QUICK_REF.md](./DCIM_AI_QUICK_REF.md)** - Quick reference card
🧪 **[test_dcim_ai.py](./test_dcim_ai.py)** - Interactive test script

#### Quick Examples

**1. Deteksi Anomali**
```
Apakah ada anomali yang terdeteksi? CPU: 8%, Memory: 23%, Disk I/O: 623766
```

**2. Root Cause Analysis**
```
Apa yang menyebabkan masalah pada infrastruktur ini?
```

**3. Rekomendasi**
```
Rekomendasikan tindakan mitigasi untuk memory usage tinggi
```

**4. Analisis Lengkap**
```
Berikan analisis komprehensif dari kondisi infrastruktur ini
```

**5. Multi-Aspect Query**
```
Analisis sistem: CPU 15%, Memory 80%, Disk I/O tinggi.
Apakah ada anomali? Apa penyebabnya? Apa rekomendasinya?
```

#### Test dengan Script
```bash
cd /home/infra/dcim_project
python3 test_dcim_ai.py interactive
```

### 15.13 Dataset Files Summary

| File                               | Records | Size   | Deskripsi                             |
| ---------------------------------- | ------- | ------ | ------------------------------------- |
| `raw_incidents.jsonl`              | 2.088   | 2.9 MB | Structured JSON per incident          |
| `enriched_incidents.jsonl`         | 2.088   | 6.5 MB | + Natural language fields             |
| `dcim_instructions.jsonl`          | 3.816   | 2.8 MB | Instruction tuning (template)         |
| `dcim_instructions_enhanced.jsonl` | 3.816   | 3.0 MB | Instruction tuning (200 LLM-enhanced) |
| `eval_baseline.json`               | 6 tests | -      | Baseline evaluation report            |

**Instruction Categories:**
- Summary (683), Drift (723), Temporal (701), Anomaly (340), Domain (291)
- Root Cause (329), Recommendation (316), Full Analysis (312), Impact (121)

### 15.14 Catatan VRAM & Hardware

| Operasi                                  | VRAM Dibutuhkan          | GPU                    |
| ---------------------------------------- | ------------------------ | ---------------------- |
| Fine-tuning QLoRA (3B, batch=1, seq=512) | \~5.5 GB                 | 1× RTX 3070 Ti         |
| llama-server (Qwen3-VL-4B GGUF)          | \~7.2 GB                 | 1× RTX 3070 Ti         |
| Fine-tuning + inference                  | **Tidak bisa bersamaan** | Harus pilih salah satu |

> llama-server harus di-stop dulu saat fine-tuning. Setelah fine-tune, export ke GGUF dan jalankan kembali llama-server. Untuk model 7B: butuh multi-GPU split (2× 8GB) atau GPU lebih besar.

***

## 16. Fine-Tuning dengan Unsloth

> **Tanggal:** 7 Mei 2026 | **Server:** srv-rnd-llm (192.168.100.35)

### 16.1 Overview

Project ini menggunakan **Unsloth** untuk melakukan fine-tuning Large Language Model (LLM) dengan teknik **QLoRA** (Quantized Low-Rank Adaptation). Fine-tuning memungkinkan model pre-trained beradaptasi dengan knowledge/domain spesifik (contoh: SOP IT perusahaan) tanpa melatih ulang seluruh model.

#### Teknologi yang Digunakan

| Komponen     | Versi       | Fungsi                                          |
| ------------ | ----------- | ----------------------------------------------- |
| Unsloth      | 2026.5.2    | Framework fine-tuning (2-5x lebih cepat)        |
| PyTorch      | 2.7.0+cu126 | Deep learning framework                         |
| Transformers | 5.5.0       | HuggingFace model library                       |
| PEFT         | 0.19.1      | Parameter-Efficient Fine-Tuning (LoRA)          |
| TRL          | 0.24.0      | Transformer Reinforcement Learning (SFTTrainer) |
| bitsandbytes | 0.49.2      | 4-bit quantization                              |
| Triton       | 3.3.0       | GPU kernel compiler                             |

### 16.2 Kapasitas Model per Konfigurasi

| Model Size  | 4-bit VRAM | 1 GPU (7.7GB)        | 2 GPU (15.4GB) |
| ----------- | ---------- | -------------------- | -------------- |
| 1B          | \~1.5 GB   | ✅ Lancar             | ✅              |
| 3B          | \~2.5 GB   | ✅ Ketat              | ✅              |
| 7B          | \~5 GB     | ⚠️ OOM saat training | ✅              |
| 14B (Phi-4) | \~9 GB     | ❌                    | ✅ Berhasil     |
| 70B         | \~40 GB    | ❌                    | ❌              |

### 16.3 Instalasi Environment

#### Clone Repository

```shellscript
cd /home/infra/unsloth
git clone https://github.com/unslothai/unsloth.git
```

#### Buat Virtual Environment

```shellscript
cd /home/infra/unsloth/unsloth
python3 -m venv venv
source venv/bin/activate
```

#### Install PyTorch + CUDA

```shellscript
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

#### Install Unsloth

```shellscript
pip install -e ".[huggingface]"
pip install "torchao>=0.16.0"
pip install bitsandbytes
```

#### Verifikasi Instalasi

```shellscript
python -c "
from unsloth import FastLanguageModel
print('✅ Unsloth ready!')
"
```

### 16.4 Struktur Direktori

```
/home/infra/unsloth/
├── unsloth/                    # Repository Unsloth (source code)
│   └── venv/                   # Virtual environment
│
└── Fine-Tuning/                # Project fine-tuning
    ├── DOKUMENTASI.md          # Dokumentasi ini
    ├── README.md               # Quick start guide
    │
    ├── finetune.py             # Training 1 GPU (Llama 1B, Alpaca dataset)
    ├── finetune_sop.py         # Training 2 GPU (Phi-4, SOP dataset)
    ├── finetune_phi4_dual_gpu.py  # Training 2 GPU (Phi-4, Alpaca demo)
    ├── finetune_custom_dataset.py # Training CLI (custom dataset)
    │
    ├── tools/
    │   └── sop_to_jsonl.py     # Konverter SOP Markdown → JSONL
    │
    ├── docs/                   # Dokumen SOP sumber
    │   └── sample_sop_it.md    # Contoh SOP IT
    │
    ├── data/                   # Dataset training (JSONL)
    │   ├── sop_training.jsonl  # Dataset SOP (60 samples)
    │   ├── example_chat.jsonl  # Contoh format chat
    │   └── example_instruction.jsonl  # Contoh format instruction
    │
    ├── outputs/                # Hasil training Llama 1B
    │   └── lora_adapters/
    │
    └── outputs_phi4/           # Hasil training Phi-4
        └── lora_adapters/
```

### 16.5 Alur Kerja Fine-Tuning

```
┌─────────────────────────────────────────────────────────────┐
│  1. PERSIAPAN DATA                                          │
│     Dokumen SOP (.md) → sop_to_jsonl.py → dataset (.jsonl)  │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  2. LOAD MODEL                                              │
│     Download model dari HuggingFace → Quantize ke 4-bit     │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  3. INJECT LoRA                                             │
│     Tambah adapter matrices → Hanya 0.2-1.4% params trained │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  4. TRAINING (SFT)                                          │
│     Forward → Loss → Backward → Update LoRA weights         │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  5. SAVE & EXPORT                                           │
│     LoRA adapters / Merged model / GGUF (untuk Ollama)      │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  6. DEPLOY                                                  │
│     llama-server / Ollama / HuggingFace Inference           │
└─────────────────────────────────────────────────────────────┘
```

### 16.6 Script yang Tersedia

#### `finetune.py` — Training Dasar (1 GPU)

**Model:** Llama-3.2-1B-Instruct | **GPU:** 1 GPU

```shellscript
source /home/infra/unsloth/unsloth/venv/bin/activate
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python finetune.py
```

#### `finetune_sop.py` — Training SOP (2 GPU) ⭐

**Model:** Phi-4 (14B) | **GPU:** 2 GPU (device\_map="auto")

```shellscript
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python finetune_sop.py
```

#### `finetune_phi4_dual_gpu.py` — Phi-4 Demo (2 GPU)

**Model:** Phi-4 (14B) | **GPU:** 2 GPU

```shellscript
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python finetune_phi4_dual_gpu.py
```

#### `finetune_custom_dataset.py` — CLI Fleksibel

```shellscript
python finetune_custom_dataset.py \
    --dataset ./data/sop_training.jsonl \
    --format chat \
    --model unsloth/Llama-3.2-3B-Instruct \
    --max-steps 200 \
    --save-gguf
```

#### `tools/sop_to_jsonl.py` — Konverter Dokumen

```shellscript
# 1 file
python tools/sop_to_jsonl.py --input docs/sop.md --output data/training.jsonl

# Seluruh folder
python tools/sop_to_jsonl.py --input docs/ --output data/all_training.jsonl

# Lebih banyak variasi pertanyaan
python tools/sop_to_jsonl.py --input docs/ --output data/training.jsonl --variations 4
```

### 16.7 Persiapan Dataset

#### Format yang Didukung

**Chat Format (Recommended):**

```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

**Instruction Format:**

```json
{"instruction": "...", "input": "...", "output": "..."}
```

**Plain Text:**

```json
{"text": "Full formatted text..."}
```

#### Konversi dari Dokumen SOP

1. Simpan dokumen SOP dalam format Markdown di folder `docs/`
2. Jalankan konverter:

```shellscript
python tools/sop_to_jsonl.py --input docs/ --output data/sop_training.jsonl
```

1. Hasil: file JSONL dengan pasangan Q\&A otomatis (60 Q\&A pairs dari 1 file SOP)

#### Tips Kualitas Dataset

| Tips                    | Penjelasan                               |
| ----------------------- | ---------------------------------------- |
| Minimal 200-500 samples | Untuk hasil yang terlihat signifikan     |
| Konsisten format        | Jangan campur style dalam 1 dataset      |
| Jawaban lengkap         | Model belajar dari detail response       |
| Hindari data sensitif   | Jangan masukkan password/credential asli |
| Domain fokus            | 500 data berkualitas > 5000 data random  |

#### Sumber Data yang Bisa Digunakan

* SOP dan prosedur operasional
* FAQ internal / knowledge base
* Dokumentasi teknis
* Runbook / playbook
* Tiket support + resolusi
* Chat log helpdesk (anonimkan data pribadi)

### 16.8 Menjalankan Training

#### Aktivasi Environment

```shellscript
source /home/infra/unsloth/unsloth/venv/bin/activate
cd /home/infra/unsloth/Fine-Tuning
```

#### Training dengan Data SOP (Recommended)

```shellscript
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python finetune_sop.py
```

#### Parameter Penting

| Parameter                     | Nilai                    | Penjelasan                    |
| ----------------------------- | ------------------------ | ----------------------------- |
| `model_name`                  | `unsloth/phi-4-bnb-4bit` | Model base                    |
| `max_seq_length`              | 512                      | Panjang sequence (hemat VRAM) |
| `lora_r`                      | 16                       | LoRA rank (8-64)              |
| `num_train_epochs`            | 3                        | Jumlah epoch                  |
| `learning_rate`               | 2e-4                     | Learning rate                 |
| `device_map`                  | `"auto"`                 | Split ke 2 GPU                |
| `per_device_train_batch_size` | 1                        | Batch size per GPU            |
| `gradient_accumulation_steps` | 4-8                      | Kompensasi batch kecil        |

#### Estimasi Waktu Training

| Model             | Dataset    | Steps                 | Waktu      |
| ----------------- | ---------- | --------------------- | ---------- |
| Llama 1B (1 GPU)  | 51K Alpaca | 100                   | \~6 menit  |
| Phi-4 14B (2 GPU) | 10K Alpaca | 60                    | \~16 menit |
| Phi-4 14B (2 GPU) | 60 SOP     | 3 epochs (\~45 steps) | \~12 menit |

### 16.9 Hasil Training

#### Training Llama-3.2-1B (1 GPU)

```
Model:           unsloth/Llama-3.2-1B-Instruct
Dataset:         yahma/alpaca-cleaned (51,760 samples)
Steps:           100
Training Loss:   1.702 → 1.189 (final avg: 1.262)
Runtime:         5 menit 59 detik
Speed:           ~3.6 s/step
GPU Memory:      ~5.7 GB / 7.7 GB (GPU 0)
Output:          ./outputs/lora_adapters/
```

#### Training Phi-4 14B (2 GPU)

```
Model:           unsloth/phi-4-bnb-4bit
Dataset:         yahma/alpaca-cleaned (10,000 subset)
Steps:           60
Training Loss:   1.65 → 0.88 (final avg: 1.056)
Runtime:         16 menit 23 detik
Speed:           ~16.4 s/step
GPU Memory:      GPU 0: 2.94 GB, GPU 1: 5.56 GB
Output:          ./outputs_phi4/lora_adapters/
```

#### Inference Test (Phi-4)

```
Q: Explain quantum computing in simple terms.
A: Quantum computing is a type of computing that uses the principles of
   quantum mechanics to process information. Unlike traditional computers,
   which use bits to represent information as either 0s or 1s, quantum
   computers use quantum bits, or qubits, which can exist in multiple
   states at once.
```

### 16.10 Export & Deployment

#### Save LoRA Adapters (Default)

```python
model.save_pretrained("./outputs/lora_adapters")
```

* Ukuran: \~50-100 MB
* Untuk: load kembali dengan Unsloth/PEFT

#### Export ke GGUF (untuk Ollama/llama.cpp)

```python
model.save_pretrained_gguf("./outputs/gguf", tokenizer)
```

Lalu deploy:

```shellscript
# Buat Modelfile
echo 'FROM ./outputs/gguf/unsloth.Q4_K_M.gguf' > Modelfile

# Import ke Ollama
ollama create my-sop-assistant -f Modelfile

# Jalankan
ollama run my-sop-assistant
```

#### Export Merged Model (Full)

```python
model.save_pretrained_merged("./outputs/merged", tokenizer, save_method="merged_16bit")
```

* Ukuran: \~2-28 GB (tergantung model)
* Untuk: deploy tanpa perlu model base

#### Push ke HuggingFace Hub

```python
model.push_to_hub_merged("username/my-model", tokenizer, save_method="merged_16bit", token="hf_xxx")
```

### 16.11 Troubleshooting (Unsloth)

| Error                                                   | Penyebab                               | Solusi                                                                                                                            |
| ------------------------------------------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `torch.OutOfMemoryError: CUDA out of memory`            | VRAM tidak cukup                       | Tambah `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, kurangi batch\_size/seq\_len/lora\_r, atau gunakan `device_map="auto"` |
| `ImportError: Found an incompatible version of torchao` | Versi torchao tidak kompatibel         | `pip install "torchao>=0.16.0"`                                                                                                   |
| Flash Attention Warning                                 | Instalasi FA2 bermasalah               | Tidak kritis — Unsloth otomatis fallback ke Xformers                                                                              |
| Training Loss tidak turun                               | Epoch/data kurang atau LR tidak tepat  | Naikkan epoch (3-5), naikkan max\_steps, turunkan LR → 1e-4, tambah data                                                          |
| Model tidak menjawab sesuai SOP                         | Data training kurang atau format salah | Tambah data (target: 500+ samples), tambah variasi, naikkan epoch 5-10                                                            |

### 16.12 Referensi

| Resource           | URL                                  |
| ------------------ | ------------------------------------ |
| Unsloth GitHub     | https://github.com/unslothai/unsloth |
| Unsloth Wiki       | https://docs.unsloth.ai              |
| HuggingFace Models | https://huggingface.co/unsloth       |
| TRL Documentation  | https://huggingface.co/docs/trl      |
| PEFT Documentation | https://huggingface.co/docs/peft     |
| LoRA Paper         | https://arxiv.org/abs/2106.09685     |
| QLoRA Paper        | https://arxiv.org/abs/2305.14314     |

### 16.13 Changelog Unsloth

| Tanggal    | Perubahan                                                     |
| ---------- | ------------------------------------------------------------- |
| 2026-05-07 | Initial setup: install environment, training Llama 1B & Phi-4 |
| 2026-05-07 | Buat script konverter SOP → JSONL                             |
| 2026-05-07 | Training Phi-4 14B berhasil di 2 GPU                          |
| 2026-05-07 | Dokumentasi lengkap                                           |

***

## Kesimpulan

MT-023 telah berhasil mencakup seluruh siklus evaluasi dan persiapan:

* ✅ **Platform setup** — Ollama & llama.cpp terkonfigurasi dan tervalidasi
* ✅ **Model selection** — 32 model dievaluasi di dua platform (19 via Ollama, 13 via llama.cpp)
* ✅ **Quantization implementation** — Q2\_K / Q4\_K\_M / Q8\_0 dianalisis
* ✅ **Benchmark analysis** — 14 metrik komprehensif (performance + capability)
* ✅ **DCIM recommendation** — Qwen series dengan Q4\_K\_M pada Ollama (production) / llama.cpp (optimization)
* ✅ **Dataset pipeline** — 3.816 instruction samples dari 19.347 rows server metrics, dengan 200 LLM-enhanced samples
* ✅ **Fine-tuning infrastructure** — QLoRA via BitsAndBytes (model preparation) + Unsloth framework (general fine-tuning)
* ✅ **Deployment options** — llama-server, Ollama, PEFT adapter, GGUF export terdokumentasi

**Status: COMPLETED**

***

*Dokumen digabungkan dari:*

* ***`MT-023_Private_LLM_Platform_MERGED.md`****&#x20;— Benchmark Platform & Quantization Analysis*
* ***`modelpreparation.md`****&#x20;— Model Preparation & Dataset Generation Pipeline*
* ***`DOKUMENTASIfine_tuning.md`****&#x20;— Fine-Tuning dengan Unsloth*

*Benchmark dilaksanakan pada: 22 April 2026 | Platform: srv-rnd-llm*
*Dataset pipeline dijalankan: 4 Mei 2026 | Data: 12-19 Februari 2026*
*Fine-tuning Unsloth: 7 Mei 2026*
*Project consolidation: 12 Mei 2026*

***

## 17. Project Consolidation & New Structure

> **Tanggal konsolidasi:** 12 Mei 2026
> **Tujuan:** Mengorganisir semua file terkait DCIM AI ke dalam struktur folder yang terkonsolidasi dan mudah dikelola

### 17.1 Perubahan Lokasi File

Semua file terkait project DCIM (termasuk benchmark, implementasi, dan dokumentasi) telah dipindahkan ke struktur folder baru yang terorganisir:

#### Lokasi Baru (Consolidated)

```
/home/infra/dcim_project/
├── README.md                          # Project overview & quick start
├── QUICK_START.md                     # Panduan cepat
├── MIGRATION_GUIDE.md                 # Panduan migrasi detail
├── CONSOLIDATION_SUMMARY.md           # Ringkasan konsolidasi
├── BENCHMARK_ADDED.md                 # Summary penambahan benchmark
├── dcim_shortcuts.sh                  # Shortcut commands (executable)
│
├── documentation/                     # 📚 Semua dokumentasi project (11 files)
│   ├── DCIM_AI_ANALYSIS.md
│   ├── DCIM_AI_IMPLEMENTATION_ANALYSIS.md
│   ├── DCIM_AI_PATH_REFERENCE.md
│   ├── DCIM_AI_RECONCILIATION.md
│   ├── DCIM_AI_SUMMARY.md
│   ├── dcim_ai_plan.md
│   ├── MT-023_COMPLETION_CERTIFICATE.md
│   ├── MT-023_IMPLEMENTATION_SUMMARY.md
│   ├── MT-023_LLM_Inference_Service_API_Layer.md
│   ├── MT-023_Model_Preparation_Detail.md
│   └── MT-023_UNSLOTH_INTEGRATION_ANALYSIS.md
│
├── implementation/                    # 💻 Semua kode implementasi
│   ├── dcim_ai_v1/                   # Original DCIM AI implementation
│   │   ├── llm/
│   │   ├── rag/
│   │   ├── query_engine/
│   │   ├── prompting/
│   │   └── simulation/
│   │
│   ├── dcim_ai_v2_rag/               # ⭐ Main implementation (MT-023)
│   │   ├── llm/                      # LLM fine-tuning & model registry
│   │   │   ├── dataset_generator.py
│   │   │   ├── text_enrichment.py
│   │   │   ├── instruction_builder.py
│   │   │   ├── finetune_qlora.py
│   │   │   ├── finetune_unsloth.py
│   │   │   ├── model_registry.py
│   │   │   ├── model_registry_standalone.py
│   │   │   ├── datasets/             # Generated datasets
│   │   │   │   ├── raw_incidents.jsonl (2,088 records)
│   │   │   │   ├── enriched_incidents.jsonl (2,088 records)
│   │   │   │   └── dcim_instructions.jsonl (3,816 samples)
│   │   │   ├── models/               # Fine-tuned models
│   │   │   │   └── v1.0/
│   │   │   │       ├── adapter/      # LoRA adapter (~50 MB)
│   │   │   │       └── metadata.json
│   │   │   ├── MT-023_COMPLETE_DOCUMENTATION.md
│   │   │   ├── QUICK_REFERENCE.md
│   │   │   ├── STATUS.txt
│   │   │   ├── FINAL_REPORT.txt
│   │   │   └── UNSLOTH_GUIDE.md
│   │   ├── rag/                      # RAG implementation
│   │   ├── query_engine/             # Query processing
│   │   ├── prompting/                # Prompt engineering
│   │   ├── core/                     # Core modules (MT-018 to MT-022)
│   │   ├── features/                 # Feature engineering
│   │   ├── models/                   # ML models
│   │   ├── training/                 # Training orchestration
│   │   ├── registry/                 # Model registry
│   │   ├── monitoring/               # Monitoring & drift detection
│   │   ├── correlation/              # Cross-domain correlation
│   │   ├── root_cause/               # RCA engine
│   │   └── tests/                    # Unit & integration tests
│   │
│   ├── dcim_benchmark/               # 📊 Benchmarking tools (dari benchmark_model)
│   │   ├── README.md                 # Dokumentasi benchmark lengkap
│   │   ├── benchmark.py              # Basic latency/throughput test
│   │   ├── benchmark_context_length.py
│   │   ├── benchmark_ttft.py         # Time To First Token
│   │   ├── load_test.py              # Concurrent load testing
│   │   ├── gpu_log.csv               # GPU utilization logs
│   │   └── benchmark_comparation/    # ⭐ Hasil benchmark lengkap
│   │       ├── benchmark_all_v4.py   # Script benchmark 14 metrik
│   │       ├── benchmark_all_v5.py   # llama.cpp version
│   │       ├── benchmark_v4_results.json
│   │       └── benchmark_v5_*.json   # Hasil per model
│   │
│   └── dcim_rnd_llm/                 # LLM research & experiments
│       ├── api.py
│       ├── chunking.py
│       ├── embedding.py
│       ├── query.py
│       └── vector_store.py
│
├── reference_docs/                    # 📖 Dokumentasi referensi
│   └── MT-004_Analytics & AI Foundation/
│       ├── (MT-018) Traditional Machine Learning Model.md
│       ├── (MT-019) Anomaly Detection Framework.md
│       ├── (MT-020) Cross-Domain Correlation Engine.md
│       ├── (MT-021) Model Training & Evaluation Lifecycle.md
│       └── (MT-022) Root Cause Analysis Engine.md
│
└── analysis/                          # 📊 Dokumen analisis
    └── ANALYSIS_INDEX.md
```

### 17.2 Mapping Lokasi Lama → Baru

#### Benchmark Files

```
LAMA: /home/infra/benchmark_model/
BARU: /home/infra/dcim_project/implementation/dcim_benchmark/

File yang dipindahkan:
- benchmark.py
- benchmark_context_length.py
- benchmark_ttft.py
- load_test.py
- gpu_log.csv
- benchmark_comparation/ (folder lengkap dengan semua hasil)
```

#### Implementation Files

```
LAMA: /home/infra/rnd_rag-anything/dcim_ai/
BARU: /home/infra/dcim_project/implementation/dcim_ai_v2_rag/

Symbolic link dibuat untuk backward compatibility:
/home/infra/rnd_rag-anything/dcim_ai → /home/infra/dcim_project/implementation/dcim_ai_v2_rag
```

#### Documentation Files

```
LAMA: /home/infra/MT-023_*.md, DCIM_AI_*.md (scattered)
BARU: /home/infra/dcim_project/documentation/

11 file dokumentasi dipindahkan ke folder documentation
```

### 17.3 Quick Access dengan Shortcuts

Untuk memudahkan navigasi, gunakan shortcut commands:

```shellscript
# Load shortcuts
source /home/infra/dcim_project/dcim_shortcuts.sh

# Available shortcuts:
dcim                  # Go to project root
dcim-docs             # Go to documentation folder
dcim-impl             # Go to implementation folder
dcim-v2               # Go to DCIM AI v2 (main implementation)
dcim-llm              # Go to LLM folder (MT-023)
dcim-models           # Go to models folder
dcim-benchmark        # Go to benchmark folder ⭐ NEW
dcim-ref              # Go to reference docs
dcim-analysis         # Go to analysis folder

# Environment & tools
dcim-activate         # Activate Python virtual environment
dcim-registry-list    # List all model versions
dcim-registry-active  # Show active production model

# Information
dcim-tree             # Show project structure
dcim-status           # Show MT-023 status
dcim-readme           # Show project README
dcim-help             # Show all shortcuts
```

### 17.4 Cara Menjalankan Benchmark (Lokasi Baru)

#### Option 1: Dengan Shortcuts

```shellscript
# Load shortcuts
source /home/infra/dcim_project/dcim_shortcuts.sh

# Go to benchmark folder
dcim-benchmark

# Activate environment
dcim-activate

# Run benchmark
python benchmark_comparation/benchmark_all_v4.py
```

#### Option 2: Direct Path

```shellscript
cd /home/infra/dcim_project/implementation/dcim_benchmark
source /home/infra/rnd_rag-anything/ragavenv/bin/activate
python benchmark_comparation/benchmark_all_v4.py
```

### 17.5 Cara Menjalankan Fine-Tuning (Lokasi Baru)

```shellscript
# Option 1: Dengan shortcuts
dcim-llm
dcim-activate
python finetune_qlora.py

# Option 2: Direct path
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm
source /home/infra/rnd_rag-anything/ragavenv/bin/activate
python finetune_qlora.py
```

### 17.6 Model Registry (Lokasi Baru)

```shellscript
# Check active model
dcim-llm
python model_registry_standalone.py active --name dcim_assistant

# List all versions
python model_registry_standalone.py list --name dcim_assistant

# Register new model
python model_registry_standalone.py register \
    --name dcim_assistant \
    --version v1.1 \
    --adapter-path models/v1.1/adapter

# Promote to production
python model_registry_standalone.py promote \
    --name dcim_assistant \
    --version v1.1
```

### 17.7 Dokumentasi Lengkap

Semua dokumentasi tersedia di folder project:

1. **Project Overview**: `/home/infra/dcim_project/README.md`
2. **Quick Start**: `/home/infra/dcim_project/QUICK_START.md`
3. **Migration Guide**: `/home/infra/dcim_project/MIGRATION_GUIDE.md`
4. **Consolidation Summary**: `/home/infra/dcim_project/CONSOLIDATION_SUMMARY.md`
5. **Benchmark Guide**: `/home/infra/dcim_project/implementation/dcim_benchmark/README.md`
6. **MT-023 Complete Guide**: `/home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/MT-023_COMPLETE_DOCUMENTATION.md`
7. **Quick Reference**: `/home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/QUICK_REFERENCE.md`

### 17.8 Status Production Model

**Model aktif saat ini:**

```
Name:          dcim_assistant
Version:       v1.0
Status:        ✅ PRODUCTION (Active)
Base Model:    Qwen/Qwen2.5-3B-Instruct
Training Loss: 0.310
Dataset Size:  3,816 samples
Epochs:        3
Adapter Path:  /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/models/v1.0/adapter/
Registered:    2026-05-11 15:37:13
Activated:     2026-05-11 15:37:30
```

### 17.9 Keuntungan Struktur Baru

#### Sebelum (Scattered)

* ❌ File tersebar di berbagai lokasi
* ❌ Sulit mencari dokumentasi
* ❌ Tidak ada struktur yang jelas
* ❌ Benchmark terpisah dari implementasi

#### Sesudah (Consolidated)

* ✅ Semua file DCIM dalam 1 folder
* ✅ Struktur jelas dan logis
* ✅ Dokumentasi lengkap dan terorganisir
* ✅ Benchmark terintegrasi dengan implementasi
* ✅ Mudah di-backup dan dikelola
* ✅ Siap untuk scaling dan kolaborasi
* ✅ Shortcut commands untuk akses cepat

### 17.10 Backward Compatibility

Untuk menjaga kompatibilitas dengan script lama:

1. **Symbolic Link**: Dibuat di `/home/infra/rnd_rag-anything/dcim_ai` → folder baru
2. **Database Paths**: Diupdate ke lokasi baru
3. **Virtual Environment**: Tetap di lokasi lama (`/home/infra/rnd_rag-anything/ragavenv`)
4. **Old Scripts**: Masih bisa berjalan dengan symbolic link

### 17.11 Next Steps

1. ✅ Project consolidation complete
2. ✅ Documentation updated
3. ✅ Shortcuts created
4. ✅ Database paths updated
5. ✅ Model registry verified

* [ ] Update CI/CD pipelines (jika ada)
* [ ] Team notification & training
* [ ] Archive old backup folders

***

**Project Status**: ✅ **CONSOLIDATED & PRODUCTION READY**
**Location**: `/home/infra/dcim_project/`
**Last Updated**: 12 Mei 2026
