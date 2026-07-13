# MT-023 — Empirical Model Capability Test Results

> **Dokumen:** Hasil pengujian empiris 23 capability parameter pada 6 model LLM
> **Tanggal:** 2–4 Juni 2026
> **Server:** srv-rnd-llm (192.168.100.35)
> **Test Suite:** `/home/infra/dcim_project/model_specification_test/`
> **Platform:** Ollama + llama.cpp

---

## 1. Ringkasan Eksekutif

### Overall Ranking — 6 Model

| Rank | Model | Platform | Total Score | Avg Score | Pass Rate | Grade | Rating |
|------|-------|----------|-------------|-----------|-----------|-------|--------|
| 🥇 1 | **Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M** | llama.cpp | **18.436** | **0.802** | **100.0%** (23/23) | **B+** | ✅ Good |
| 🥈 2 | **Smoffyy/Qwen3.5-4B-Instruct-Pure-GGUF:Q4_K_M** | llama.cpp | **15.369** | **0.668** | **73.9%** (17/23) | **C+** | 🟡 Acceptable |
| 🥉 3 | **unsloth/gemma-4-12b-it-GGUF:UD-Q4_K_XL** | llama.cpp | **14.125** | **0.614** | **69.6%** (16/23) | **C+** | 🟡 Acceptable |
| 4 | microsoft/phi-4-gguf:Q4_K_S | llama.cpp | 8.836 | 0.384 | 34.8% (8/23) | D | 🔴 Poor |
| 5 | bartowski/Qwen2.5.1-Coder-7B-Instruct-GGUF:Q4_K_M | llama.cpp | 8.353 | 0.363 | 26.1% (6/23) | D | 🔴 Poor |
| 6 | qwen2.5-coder:1.5b | Ollama | 7.722 | 0.336 | 26.1% (6/23) | D | 🔴 Poor |

### Key Findings

- **Qwen3-VL-4B mendominasi** — satu-satunya model yang lulus semua 23 test (100% pass rate)
- **Qwen3.5-4B-Pure** — terbaik di tool calling, context engine, mixture of agents (semua 1.000)
- **Gemma-4-12B** — balance baik, unggul di RAG (0.926) dan messaging (0.913)
- **phi-4, Qwen2.5.1-Coder-7B, qwen2.5-coder:1.5b** — performa rendah karena banyak capability = 0.000 (test awal sebelum fix)
- **Test date berpengaruh** — hasil awal (3 Juni) vs hasil terbaru (4 Juni) menunjukkan peningkatan signifikan setelah test suite diperbaiki

---

## 2. Detail Hasil per Model

### 2.1 Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M — 🥇 Best Overall

**Test Date:** 4 Juni 2026, 15:52 WIB
**Platform:** llama.cpp (port 8080)

| Metric | Value |
|--------|-------|
| Total Score | 18.436 |
| Average Score | 0.802 |
| Grade | B+ |
| Rating | ✅ Good |
| Passed | 23 / 23 (100.0%) |
| Failed | 0 |

#### Capability Breakdown

| Rank | Capability | Score | Rating | Grade |
|------|------------|-------|--------|-------|
| 1 | Tool Calling | 1.000 | ✅ Perfect | A |
| 2 | RAG | 1.000 | ✅ Perfect | A |
| 3 | Vision | 1.000 | ✅ Perfect | A |
| 4 | Code Execution | 0.987 | ✅ Perfect | A |
| 5 | Messaging | 0.913 | ✅ Perfect | A |
| 6 | Session Search | 0.896 | ✅ Good | B+ |
| 7 | Streaming | 0.868 | ✅ Good | B+ |
| 8 | JSON Mode | 0.840 | ✅ Good | B+ |
| 9 | Structured Output | 0.840 | ✅ Good | B+ |
| 10 | Cron | 0.817 | ✅ Good | B+ |
| 11 | Mixture of Agents | 0.806 | ✅ Good | B+ |
| 12 | Web Search | 0.800 | ✅ Good | B+ |
| 13 | File Operations | 0.790 | ✅ Good | B |
| 14 | Delegation | 0.767 | ✅ Good | B |
| 15 | Chain-of-Thought | 0.766 | ✅ Good | B |
| 16 | Terminal | 0.764 | ✅ Good | B |
| 17 | Memory | 0.750 | ✅ Good | B |
| 18 | Context Engine | 0.750 | ✅ Good | B |
| 19 | Multi-turn | 0.725 | 🟡 Acceptable | B |
| 20 | Skills | 0.688 | 🟡 Acceptable | C+ |
| 21 | Clarifying | 0.602 | 🟡 Acceptable | C+ |
| 22 | Task Planning | 0.561 | 🟡 Acceptable | C |
| 23 | Agent | 0.506 | 🟡 Acceptable | C |

**Keunggulan:**
- ✅ **Satu-satunya model dengan 100% pass rate**
- ✅ **Vision sempurna (1.000)** — multimodal capability
- ✅ **Tool Calling sempurna (1.000)** — function calling terbaik
- ✅ **RAG sempurna (1.000)** — retrieval-augmented generation terbaik
- ✅ **Code Execution hampir sempurna (0.987)**
- ✅ **Tidak ada capability yang gagal**

**Keterbatasan:**
- 🟡 Task Planning (0.561) dan Agent (0.506) masih di batas acceptable

**Rekomendasi:** **Best overall untuk DCIM Platform** — cocok untuk semua use-case.

---

### 2.2 Smoffyy/Qwen3.5-4B-Instruct-Pure-GGUF:Q4_K_M — 🥈 Best Tool User

**Test Date:** 4 Juni 2026, 16:11 WIB
**Platform:** llama.cpp (port 8080)

| Metric | Value |
|--------|-------|
| Total Score | 15.369 |
| Average Score | 0.668 |
| Grade | C+ |
| Rating | 🟡 Acceptable |
| Passed | 17 / 23 (73.9%) |
| Failed | 6 |

#### Capability Breakdown

| Rank | Capability | Score | Rating | Grade |
|------|------------|-------|--------|-------|
| 1 | Tool Calling | 1.000 | ✅ Perfect | A |
| 2 | Context Engine | 1.000 | ✅ Perfect | A |
| 3 | Mixture of Agents | 1.000 | ✅ Perfect | A |
| 4 | Delegation | 0.950 | ✅ Perfect | A |
| 5 | Vision | 0.922 | ✅ Perfect | A |
| 6 | Messaging | 0.913 | ✅ Perfect | A |
| 7 | Web Search | 0.900 | ✅ Perfect | A |
| 8 | Session Search | 0.896 | ✅ Good | B+ |
| 9 | Memory | 0.883 | ✅ Good | B+ |
| 10 | File Operations | 0.790 | ✅ Good | B |
| 11 | Cron | 0.775 | ✅ Good | B |
| 12 | Terminal | 0.743 | 🟡 Acceptable | B |
| 13 | JSON Mode | 0.720 | 🟡 Acceptable | B |
| 14 | Skills | 0.688 | 🟡 Acceptable | C+ |
| 15 | Structured Output | 0.640 | 🟡 Acceptable | C+ |
| 16 | Code Execution | 0.587 | 🟡 Acceptable | C |
| 17 | Streaming | 0.550 | 🟡 Acceptable | C |
| 18 | Clarifying | 0.475 | 🔴 Poor | D+ |
| 19 | Agent | 0.417 | 🔴 Poor | D+ |
| 20 | Chain-of-Thought | 0.288 | 🔴 Poor | F |
| 21 | RAG | 0.167 | ❌ Failed | F |
| 22 | Task Planning | 0.065 | ❌ Failed | F |
| 23 | Multi-turn | 0.000 | ❌ Failed | F |

**Keunggulan:**
- ✅ **Tool Calling sempurna (1.000)** — function calling terbaik
- ✅ **Context Engine sempurna (1.000)** — context switching terbaik
- ✅ **Mixture of Agents sempurna (1.000)** — multi-model orchestration
- ✅ **Delegation sangat baik (0.950)** — task routing terbaik
- ✅ **Vision sangat baik (0.922)** — multimodal capability

**Keterbatasan:**
- ❌ **Multi-turn gagal total (0.000)** — tidak bisa maintain conversation context
- ❌ **Task Planning sangat buruk (0.065)** — tidak bisa breakdown task
- ❌ **RAG gagal (0.167)** — retrieval-augmented generation buruk
- ❌ **Chain-of-Thought buruk (0.288)** — reasoning step-by-step lemah

**Rekomendasi:** **Best untuk tool-based tasks** — cocok untuk automation, function calling, context switching. Tidak cocok untuk conversational AI atau complex reasoning.

---

### 2.3 unsloth/gemma-4-12b-it-GGUF:UD-Q4_K_XL — 🥉 Best Balanced

**Test Date:** 4 Juni 2026, 14:56 WIB
**Platform:** llama.cpp (port 8080)

| Metric | Value |
|--------|-------|
| Total Score | 14.125 |
| Average Score | 0.614 |
| Grade | C+ |
| Rating | 🟡 Acceptable |
| Passed | 16 / 23 (69.6%) |
| Failed | 7 |

#### Capability Breakdown

| Rank | Capability | Score | Rating | Grade |
|------|------------|-------|--------|-------|
| 1 | RAG | 0.926 | ✅ Perfect | A |
| 2 | Messaging | 0.913 | ✅ Perfect | A |
| 3 | Tool Calling | 0.900 | ✅ Perfect | A |
| 4 | Session Search | 0.896 | ✅ Good | B+ |
| 5 | Memory | 0.858 | ✅ Good | B+ |
| 6 | JSON Mode | 0.840 | ✅ Good | B+ |
| 7 | Structured Output | 0.840 | ✅ Good | B+ |
| 8 | Cron | 0.833 | ✅ Good | B+ |
| 9 | Code Execution | 0.800 | ✅ Good | B+ |
| 10 | Vision | 0.783 | ✅ Good | B |
| 11 | Terminal | 0.764 | ✅ Good | B |
| 12 | Clarifying | 0.717 | 🟡 Acceptable | B |
| 13 | Chain-of-Thought | 0.684 | 🟡 Acceptable | C+ |
| 14 | Multi-turn | 0.621 | 🟡 Acceptable | C+ |
| 15 | File Operations | 0.620 | 🟡 Acceptable | C+ |
| 16 | Streaming | 0.539 | 🟡 Acceptable | C |
| 17 | Task Planning | 0.485 | 🔴 Poor | D+ |
| 18 | Web Search | 0.400 | 🔴 Poor | D+ |
| 19 | Skills | 0.312 | 🔴 Poor | D |
| 20 | Delegation | 0.200 | ❌ Failed | F |
| 21 | Agent | 0.194 | ❌ Failed | F |
| 22 | Context Engine | 0.000 | ❌ Failed | F |
| 23 | Mixture of Agents | 0.000 | ❌ Failed | F |

**Keunggulan:**
- ✅ **RAG sangat baik (0.926)** — retrieval-augmented generation terbaik kedua
- ✅ **Messaging sangat baik (0.913)** — cross-platform messaging
- ✅ **Tool Calling sangat baik (0.900)** — function calling kuat
- ✅ **Memory sangat baik (0.858)** — store/recall accuracy tinggi
- ✅ **Balance baik** — 16 dari 23 capability lulus

**Keterbatasan:**
- ❌ **Context Engine gagal (0.000)** — context switching tidak berfungsi
- ❌ **Mixture of Agents gagal (0.000)** — multi-model orchestration tidak berfungsi
- ❌ **Agent gagal (0.194)** — multi-step task completion buruk
- 🔴 **Task Planning buruk (0.485)** — task decomposition lemah

**Rekomendasi:** **Best balanced model** — cocok untuk RAG, messaging, tool calling. Tidak cocok untuk agent-based workflows.

---

### 2.4 microsoft/phi-4-gguf:Q4_K_S

**Test Date:** 4 Juni 2026, 14:27 WIB
**Platform:** llama.cpp (port 8080)

| Metric | Value |
|--------|-------|
| Total Score | 8.836 |
| Average Score | 0.384 |
| Grade | D |
| Rating | 🔴 Poor |
| Passed | 8 / 23 (34.8%) |
| Failed | 15 |

#### Capability Breakdown

| Rank | Capability | Score | Rating | Grade |
|------|------------|-------|--------|-------|
| 1 | RAG | 1.000 | ✅ Perfect | A |
| 2 | Code Execution | 1.000 | ✅ Perfect | A |
| 3 | Streaming | 0.875 | ✅ Good | B+ |
| 4 | JSON Mode | 0.840 | ✅ Good | B+ |
| 5 | Structured Output | 0.840 | ✅ Good | B+ |
| 6 | Chain-of-Thought | 0.688 | 🟡 Acceptable | C+ |
| 7 | Clarifying | 0.663 | 🟡 Acceptable | C+ |
| 8 | Task Planning | 0.612 | 🟡 Acceptable | C+ |
| 9 | Multi-turn | 0.498 | 🔴 Poor | D+ |
| 10 | Tool Calling | 0.400 | 🔴 Poor | D+ |
| 11 | Web Search | 0.400 | 🔴 Poor | D+ |
| 12 | Agent | 0.370 | 🔴 Poor | D |
| 13 | Session Search | 0.250 | 🔴 Poor | F |
| 14 | Memory | 0.200 | ❌ Failed | F |
| 15 | Delegation | 0.200 | ❌ Failed | F |
| 16–23 | Vision, Terminal, File Ops, Cron, Messaging, Skills, Context Engine, MoA | 0.000 | ❌ Failed | F |

**Keunggulan:**
- ✅ **RAG sempurna (1.000)**
- ✅ **Code Execution sempurna (1.000)**
- ✅ **Task Planning terbaik di model D-grade (0.612)**

**Keterbatasan:**
- ❌ **8 capability = 0.000** — Vision, Terminal, File Ops, Cron, Messaging, Skills, Context Engine, MoA

**Rekomendasi:** **Cocok untuk RAG + Code tasks** — tidak cocok untuk agent workflows.

---

### 2.5 bartowski/Qwen2.5.1-Coder-7B-Instruct-GGUF:Q4_K_M

**Test Date:** 3 Juni 2026, 11:56 WIB
**Platform:** llama.cpp (port 8080)

| Metric | Value |
|--------|-------|
| Total Score | 8.353 |
| Average Score | 0.363 |
| Grade | D |
| Rating | 🔴 Poor |
| Passed | 6 / 23 (26.1%) |
| Failed | 17 |

#### Capability Breakdown

| Rank | Capability | Score | Rating | Grade |
|------|------------|-------|--------|-------|
| 1 | Code Execution | 1.000 | ✅ Perfect | A |
| 2 | RAG | 0.964 | ✅ Perfect | A |
| 3 | Streaming | 0.910 | ✅ Perfect | A |
| 4 | JSON Mode | 0.840 | ✅ Good | B+ |
| 5 | Structured Output | 0.840 | ✅ Good | B+ |
| 6 | Chain-of-Thought | 0.828 | ✅ Good | B+ |
| 7 | Task Planning | 0.462 | 🔴 Poor | D+ |
| 8 | Clarifying | 0.448 | 🔴 Poor | D+ |
| 9 | Tool Calling | 0.400 | 🔴 Poor | D+ |
| 10 | Web Search | 0.400 | 🔴 Poor | D+ |
| 11 | Agent | 0.340 | 🔴 Poor | D |
| 12 | Multi-turn | 0.271 | 🔴 Poor | F |
| 13 | Session Search | 0.250 | 🔴 Poor | F |
| 14 | Memory | 0.200 | ❌ Failed | F |
| 15 | Delegation | 0.200 | ❌ Failed | F |
| 16–23 | Vision, Terminal, File Ops, Cron, Messaging, Skills, Context Engine, MoA | 0.000 | ❌ Failed | F |

**Keunggulan:**
- ✅ **Code Execution sempurna (1.000)**
- ✅ **RAG sangat baik (0.964)**
- ✅ **Streaming sangat baik (0.910)**
- ✅ **Chain-of-Thought baik (0.828)**

**Keterbatasan:**
- ❌ **8 capability = 0.000**
- 🔴 **Tool Calling buruk (0.400)** — function calling lemah

**Rekomendasi:** **Cocok untuk code generation + RAG** — tidak cocok untuk agent workflows.

---

### 2.6 qwen2.5-coder:1.5b — Lightweight

**Test Date:** 3 Juni 2026, 11:40 WIB
**Platform:** Ollama (port 11434)

| Metric | Value |
|--------|-------|
| Total Score | 7.722 |
| Average Score | 0.336 |
| Grade | D |
| Rating | 🔴 Poor |
| Passed | 6 / 23 (26.1%) |
| Failed | 17 |

#### Capability Breakdown

| Rank | Capability | Score | Rating | Grade |
|------|------------|-------|--------|-------|
| 1 | Code Execution | 1.000 | ✅ Perfect | A |
| 2 | Streaming | 0.908 | ✅ Perfect | A |
| 3 | RAG | 0.850 | ✅ Good | B+ |
| 4 | Structured Output | 0.744 | 🟡 Acceptable | B |
| 5 | JSON Mode | 0.680 | 🟡 Acceptable | C+ |
| 6 | Chain-of-Thought | 0.576 | 🟡 Acceptable | C |
| 7 | Task Planning | 0.476 | 🔴 Poor | D+ |
| 8 | Clarifying | 0.448 | 🔴 Poor | D+ |
| 9 | Tool Calling | 0.400 | 🔴 Poor | D+ |
| 10 | Web Search | 0.400 | 🔴 Poor | D+ |
| 11 | Multi-turn | 0.365 | 🔴 Poor | D |
| 12 | Session Search | 0.250 | 🔴 Poor | F |
| 13 | Agent | 0.225 | ❌ Failed | F |
| 14 | Memory | 0.200 | ❌ Failed | F |
| 15 | Delegation | 0.200 | ❌ Failed | F |
| 16–23 | Vision, Terminal, File Ops, Cron, Messaging, Skills, Context Engine, MoA | 0.000 | ❌ Failed | F |

**Keunggulan:**
- ✅ **Code Execution sempurna (1.000)**
- ✅ **Streaming sangat baik (0.908)**
- ✅ **Paling ringan (1.5B params)** — cocok untuk edge deployment

**Keterbatasan:**
- ❌ **8 capability = 0.000**
- 🔴 **Tool Calling buruk (0.400)**

**Rekomendasi:** **Cocok untuk lightweight code assistant** — tidak cocok untuk complex workflows.

---

## 3. Perbandingan Lintas Model

### 3.1 Capability Matrix — Semua Model

| Capability | Qwen3-VL-4B | Qwen3.5-4B-Pure | Gemma-4-12B | phi-4 | Qwen2.5.1-Coder-7B | qwen2.5-coder:1.5b |
|------------|:-----------:|:---------------:|:-----------:|:-----:|:------------------:|:------------------:|
| **Tool Calling** | ✅ 1.00 | ✅ 1.00 | ✅ 0.90 | 🔴 0.40 | 🔴 0.40 | 🔴 0.40 |
| **RAG** | ✅ 1.00 | ❌ 0.17 | ✅ 0.93 | ✅ 1.00 | ✅ 0.96 | 🟡 0.85 |
| **Vision** | ✅ 1.00 | ✅ 0.92 | ✅ 0.78 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 |
| **Code Execution** | ✅ 0.99 | 🟡 0.59 | ✅ 0.80 | ✅ 1.00 | ✅ 1.00 | ✅ 1.00 |
| **Messaging** | ✅ 0.91 | ✅ 0.91 | ✅ 0.91 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 |
| **Session Search** | ✅ 0.90 | ✅ 0.90 | ✅ 0.90 | 🔴 0.25 | 🔴 0.25 | 🔴 0.25 |
| **Streaming** | ✅ 0.87 | 🟡 0.55 | 🟡 0.54 | ✅ 0.88 | ✅ 0.91 | ✅ 0.91 |
| **JSON Mode** | ✅ 0.84 | 🟡 0.72 | ✅ 0.84 | ✅ 0.84 | ✅ 0.84 | 🟡 0.68 |
| **Structured Output** | ✅ 0.84 | 🟡 0.64 | ✅ 0.84 | ✅ 0.84 | ✅ 0.84 | 🟡 0.74 |
| **Cron** | ✅ 0.82 | ✅ 0.78 | ✅ 0.83 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 |
| **Mixture of Agents** | ✅ 0.81 | ✅ 1.00 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 |
| **Web Search** | ✅ 0.80 | ✅ 0.90 | 🔴 0.40 | 🔴 0.40 | 🔴 0.40 | 🔴 0.40 |
| **File Operations** | ✅ 0.79 | ✅ 0.79 | 🟡 0.62 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 |
| **Delegation** | ✅ 0.77 | ✅ 0.95 | ❌ 0.20 | ❌ 0.20 | ❌ 0.20 | ❌ 0.20 |
| **Chain-of-Thought** | ✅ 0.77 | 🔴 0.29 | 🟡 0.68 | 🟡 0.69 | ✅ 0.83 | 🟡 0.58 |
| **Terminal** | ✅ 0.76 | 🟡 0.74 | ✅ 0.76 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 |
| **Memory** | ✅ 0.75 | ✅ 0.88 | ✅ 0.86 | ❌ 0.20 | ❌ 0.20 | ❌ 0.20 |
| **Context Engine** | ✅ 0.75 | ✅ 1.00 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 |
| **Multi-turn** | 🟡 0.73 | ❌ 0.00 | 🟡 0.62 | 🔴 0.50 | 🔴 0.27 | 🔴 0.37 |
| **Skills** | 🟡 0.69 | 🟡 0.69 | 🔴 0.31 | ❌ 0.00 | ❌ 0.00 | ❌ 0.00 |
| **Clarifying** | 🟡 0.60 | 🔴 0.48 | 🟡 0.72 | 🟡 0.66 | 🔴 0.45 | 🔴 0.45 |
| **Task Planning** | 🟡 0.56 | ❌ 0.07 | 🔴 0.49 | 🟡 0.61 | 🔴 0.46 | 🔴 0.48 |
| **Agent** | 🟡 0.51 | 🔴 0.42 | ❌ 0.19 | 🔴 0.37 | 🔴 0.34 | ❌ 0.23 |

**Legend:** ✅ ≥0.75 | 🟡 0.50–0.74 | 🔴 0.25–0.49 | ❌ <0.25

### 3.2 Best per Capability

| Capability | Best Model | Score |
|------------|-----------|-------|
| Tool Calling | Qwen3-VL-4B, Qwen3.5-4B-Pure | 1.000 |
| RAG | phi-4, Qwen3-VL-4B | 1.000 |
| Vision | Qwen3-VL-4B | 1.000 |
| Code Execution | phi-4, Qwen2.5.1-Coder-7B, qwen2.5-coder:1.5b | 1.000 |
| Messaging | Qwen3-VL-4B, Qwen3.5-4B-Pure, Gemma-4-12B | 0.913 |
| Session Search | Qwen3-VL-4B, Qwen3.5-4B-Pure, Gemma-4-12B | 0.896 |
| Streaming | Qwen2.5.1-Coder-7B, qwen2.5-coder:1.5b | 0.910 |
| JSON Mode | Qwen3-VL-4B, phi-4, Gemma-4-12B, Qwen2.5.1-Coder-7B | 0.840 |
| Structured Output | Qwen3-VL-4B, phi-4, Gemma-4-12B, Qwen2.5.1-Coder-7B | 0.840 |
| Cron | Gemma-4-12B | 0.833 |
| Mixture of Agents | Qwen3.5-4B-Pure | 1.000 |
| Web Search | Qwen3.5-4B-Pure | 0.900 |
| File Operations | Qwen3-VL-4B, Qwen3.5-4B-Pure | 0.790 |
| Delegation | Qwen3.5-4B-Pure | 0.950 |
| Chain-of-Thought | Qwen2.5.1-Coder-7B | 0.828 |
| Terminal | Qwen3-VL-4B, Gemma-4-12B | 0.764 |
| Memory | Qwen3.5-4B-Pure | 0.883 |
| Context Engine | Qwen3.5-4B-Pure | 1.000 |
| Multi-turn | Qwen3-VL-4B | 0.725 |
| Skills | Qwen3-VL-4B, Qwen3.5-4B-Pure | 0.688 |
| Clarifying | Gemma-4-12B | 0.717 |
| Task Planning | phi-4 | 0.612 |
| Agent | Qwen3-VL-4B | 0.506 |

### 3.3 Capability yang Konsisten Kuat (semua model ≥ 0.5)

| Capability | Min Score | Max Score | Avg Score |
|------------|-----------|-----------|-----------|
| Code Execution | 0.587 | 1.000 | 0.898 |
| RAG | 0.167 | 1.000 | 0.818 |
| Streaming | 0.539 | 0.910 | 0.775 |
| JSON Mode | 0.680 | 0.840 | 0.794 |
| Structured Output | 0.640 | 0.840 | 0.774 |

### 3.4 Capability yang Konsisten Lemah (semua model < 0.5)

| Capability | Min Score | Max Score | Avg Score |
|------------|-----------|-----------|-----------|
| Agent | 0.194 | 0.506 | 0.342 |
| Task Planning | 0.065 | 0.612 | 0.356 |
| Web Search | 0.400 | 0.900 | 0.567 |
| Tool Calling | 0.400 | 1.000 | 0.683 |

---

## 4. Rekomendasi per Use-Case

| Use-Case | Best Model | Score | Alasan |
|----------|-----------|-------|--------|
| **General Purpose / All-in-One** | Qwen3-VL-4B | 0.802 | 100% pass rate, balance semua capability |
| **Tool Calling / Function Calling** | Qwen3-VL-4B, Qwen3.5-4B-Pure | 1.000 | Tool calling sempurna |
| **RAG / Knowledge Base** | phi-4, Qwen3-VL-4B | 1.000 | RAG sempurna |
| **Code Generation** | phi-4, Qwen2.5.1-Coder-7B, qwen2.5-coder:1.5b | 1.000 | Code execution sempurna |
| **Multimodal (Vision + Text)** | Qwen3-VL-4B | 1.000 | Vision sempurna, satu-satunya model multimodal |
| **Context Switching** | Qwen3.5-4B-Pure | 1.000 | Context engine sempurna |
| **Multi-Model Orchestration** | Qwen3.5-4B-Pure | 1.000 | Mixture of agents sempurna |
| **Task Delegation** | Qwen3.5-4B-Pure | 0.950 | Delegation terbaik |
| **Memory / Store-Recall** | Qwen3.5-4B-Pure | 0.883 | Memory terbaik |
| **Web Search** | Qwen3.5-4B-Pure | 0.900 | Web search terbaik |
| **Messaging** | Qwen3-VL-4B, Qwen3.5-4B-Pure, Gemma-4-12B | 0.913 | Messaging sempurna |
| **Chain-of-Thought Reasoning** | Qwen2.5.1-Coder-7B | 0.828 | CoT reasoning terbaik |
| **Task Planning** | phi-4 | 0.612 | Task planning terbaik |
| **Clarifying Questions** | Gemma-4-12B | 0.717 | Clarifying terbaik |
| **Lightweight / Edge** | qwen2.5-coder:1.5b | 0.336 | 1.5B params, code execution sempurna |

---

## 5. Catatan Penting

### 5.1 Evolusi Hasil Test

Hasil test mengalami peningkatan signifikan antara 3 Juni dan 4 Juni 2026:

| Model | Test Date (awal) | Avg Score (awal) | Test Date (terbaru) | Avg Score (terbaru) | Perubahan |
|-------|-----------------|-----------------|-------------------|-------------------|-----------|
| Qwen3-VL-4B | 3 Juni | 0.356 | 4 Juni | 0.802 | **+125%** |
| Qwen2.5.1-Coder-7B | 3 Juni | 0.363 | - | 0.363 | - |
| phi-4 | 3 Juni | 0.378 | 4 Juni | 0.384 | +2% |
| qwen2.5-coder:1.5b | 3 Juni | 0.336 | - | 0.336 | - |

**Penyebab peningkatan:** Test suite diperbaiki untuk mengirim prompt yang lebih sesuai dengan format model, sehingga banyak capability yang sebelumnya 0.000 sekarang mendapat skor tinggi.

### 5.2 Limitasi Test Suite

- **Vision test** — Mengirim base64 image, tapi beberapa model tidak support format ini
- **Tool Calling** — Bergantung pada kemampuan model menghasilkan JSON function call yang valid
- **Agent, Context Engine, MoA** — Memerlukan backend implementation, bukan murni model capability
- **Score 0.000** — Bisa berarti model tidak support ATAU test prompt tidak sesuai format model

### 5.3 Cara Menjalankan Test Ulang

```bash
cd /home/infra/dcim_project/model_specification_test

# Auto-detect running models
/home/infra/dcim_project/ragavenv/bin/python3 run_tests.py --auto

# Specific model
/home/infra/dcim_project/ragavenv/bin/python3 run_tests.py --model <model-name>

# Platform filter
/home/infra/dcim_project/ragavenv/bin/python3 run_tests.py --platform llama.cpp
```

---

## 6. Kesimpulan

**Qwen3-VL-4B-Instruct-GGUF:Q4_K_M** adalah model terbaik untuk DCIM Platform:
- ✅ **100% pass rate** — satu-satunya model yang lulus semua 23 test
- ✅ **Average score 0.802 (B+)** — tertinggi dari semua model
- ✅ **Multimodal** — bisa proses gambar + teks
- ✅ **Tool calling sempurna** — function calling terbaik
- ✅ **RAG sempurna** — retrieval-augmented generation terbaik
- ✅ **Tidak ada capability yang gagal**

**Qwen3.5-4B-Instruct-Pure-GGUF:Q4_K_M** adalah runner-up terbaik untuk tool-based tasks:
- ✅ **Tool calling, context engine, mixture of agents sempurna (1.000)**
- ✅ **Delegation terbaik (0.950)**
- ❌ **Multi-turn gagal total (0.000)** — tidak cocok untuk conversational AI

**Gemma-4-12B** adalah model balance terbaik:
- ✅ **RAG, messaging, tool calling sangat baik**
- ✅ **16 dari 23 capability lulus**
- ❌ **Context engine dan MoA gagal**
