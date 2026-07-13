# Level-Based Capability Testing System

## Overview

Sistem pengujian level-based yang menguji setiap capability model AI di **5 level kesulitan**, memberikan insight granular tentang kemampuan maksimal model dan di level mana model mulai gagal.

## 5 Level Kesulitan

| Level | Nama | Kapasitas | Deskripsi | Icon |
|-------|------|-----------|-----------|------|
| 1 | **Basic** | 25% | Operasi sederhana, kompleksitas minimal | 🟢 |
| 2 | **Medium** | 50% | Operasi standar, kompleksitas moderat | 🟡 |
| 3 | **Intermediate** | 75% | Operasi kompleks, kompleksitas tinggi | 🟠 |
| 4 | **Expert** | 100% | Operasi sangat kompleks, kompleksitas maksimal | 🔴 |
| 5 | **Master** | 125% | Operasi ekstrem, melebihi spesifikasi normal | 🟣 |

## 23 Capabilities yang Diuji

Setiap capability diuji di semua 5 level dengan test cases yang semakin kompleks:

### 1. **Tool Calling** 🛠️
Kemampuan memanggil fungsi/tools dengan parameter yang benar
- **Level 1**: Single tool call, alert tool call
- **Level 2**: Log check, multi tool selection
- **Level 3**: Complex multi-tool, conditional tool calling
- **Level 4**: Multi-step workflow, error handling
- **Level 5**: Extreme multi-tool, parallel execution

### 2. **Vision** 👁️
Kemampuan analisis gambar dan visual data
- **Level 1**: Simple image description, basic object detection
- **Level 2**: Dashboard analysis, alert interpretation
- **Level 3**: Complex dashboard analysis, multi-image comparison
- **Level 4**: Detailed visual analysis, visual data extraction
- **Level 5**: Extreme visual reasoning, 3D visualization

### 3. **RAG** 📚
Retrieval Augmented Generation - menggunakan konteks untuk menjawab
- **Level 1**: Simple document retrieval, basic Q&A
- **Level 2**: Multi-document retrieval, contextual answering
- **Level 3**: Complex RAG chain, multi-hop reasoning
- **Level 4**: Advanced context understanding, document comparison
- **Level 5**: Extreme RAG scenario, multi-source synthesis

### 4. **Code Execution** 💻
Kemampuan generate dan execute code yang correct
- **Level 1**: Simple Python script, basic bash command
- **Level 2**: Python CPU monitor, bash log parser
- **Level 3**: Complex script generation, multi-language execution
- **Level 4**: Advanced system script, error handling code
- **Level 5**: Extreme code generation, parallel execution

### 5. **Terminal** 💻
Kemampuan execute terminal commands dan interpret output
- **Level 1**: Simple command execution, basic process listing
- **Level 2**: Check CPU usage, list processes
- **Level 3**: Complex terminal workflow, multi-command sequence
- **Level 4**: Advanced system monitoring, error recovery
- **Level 5**: Extreme terminal automation, parallel execution

### 6. **JSON Mode** 📋
Kemampuan menghasilkan output JSON yang valid
- **Level 1**: Simple JSON, basic JSON schema
- **Level 2**: Nested JSON, array JSON
- **Level 3**: Schema compliance, JSON with explanation
- **Level 4**: Complex JSON schema, JSON validation
- **Level 5**: Extreme JSON generation, JSON transformation

### 7. **Structured Output** 📊
Kemampuan menghasilkan output terstruktur sesuai format
- **Level 1**: Basic structured output, simple list
- **Level 2**: Markdown table, structured report
- **Level 3**: Complex structured output, multi-format output
- **Level 4**: Advanced structured output, conditional output
- **Level 5**: Extreme structured output, dynamic output

### 8. **Multi-turn** 💬
Kemampuan maintain context dalam multi-turn conversation
- **Level 1**: Basic context retention, simple follow-up
- **Level 2**: Multi-turn context, context switching
- **Level 3**: Complex multi-turn, context recovery
- **Level 4**: Advanced multi-turn, context summarization
- **Level 5**: Extreme multi-turn, context evolution

### 9. **Streaming** 🌊
Kemampuan streaming response yang smooth dan complete
- **Level 1**: Basic streaming, simple stream complete
- **Level 2**: Medium stream, stream with structure
- **Level 3**: Long stream, stream with code
- **Level 4**: Complex stream, stream error handling
- **Level 5**: Extreme stream, stream with interruption

### 10. **Chain-of-Thought** 🧠
Chain-of-Thought reasoning capabilities
- **Level 1**: Basic CoT, simple reasoning
- **Level 2**: Moderate CoT, comparative reasoning
- **Level 3**: Complex CoT, multi-factor reasoning
- **Level 4**: Advanced CoT, counterfactual reasoning
- **Level 5**: Extreme CoT, meta reasoning

### 11. **Agent** 🤖
Agent capabilities - planning, tool use, decision making
- **Level 1**: Basic agent task, simple agent workflow
- **Level 2**: Multi-step agent, conditional agent
- **Level 3**: Complex agent workflow, adaptive agent
- **Level 4**: Advanced agent, learning agent
- **Level 5**: Extreme agent, collaborative agent

### 12. **Web Search** 🔍
Web search dan information retrieval capabilities
- **Level 1**: Basic search, simple query
- **Level 2**: Targeted search, multi-source search
- **Level 3**: Complex search, comparative search
- **Level 4**: Advanced research, fact verification
- **Level 5**: Extreme research, real-time intelligence

### 13. **File Operations** 📁
File operations capabilities
- **Level 1**: Basic file read, simple file write
- **Level 2**: File search, file copy/move
- **Level 3**: Complex file ops, file processing
- **Level 4**: Advanced file ops, file transformation
- **Level 5**: Extreme file ops, distributed file ops

### 14. **Memory** 🧠
Memory and context retention capabilities
- **Level 1**: Basic memory, simple recall
- **Level 2**: Multi-item memory, contextual memory
- **Level 3**: Complex memory, memory with updates
- **Level 4**: Advanced memory, memory synthesis
- **Level 5**: Extreme memory, memory evolution

### 15. **Task Planning** 📋
Task planning and decomposition capabilities
- **Level 1**: Basic planning, simple decomposition
- **Level 2**: Multi-step planning, conditional planning
- **Level 3**: Complex planning, resource planning
- **Level 4**: Advanced planning, adaptive planning
- **Level 5**: Extreme planning, strategic planning

### 16. **Cron** ⏰
Cron job and scheduling capabilities
- **Level 1**: Basic cron, simple schedule
- **Level 2**: Complex cron, cron with logging
- **Level 3**: Cron workflow, conditional cron
- **Level 4**: Advanced cron, cron monitoring
- **Level 5**: Extreme cron, self-healing cron

### 17. **Messaging** 📨
Messaging and notification capabilities
- **Level 1**: Basic message, simple notification
- **Level 2**: Formatted message, targeted message
- **Level 3**: Complex messaging, message routing
- **Level 4**: Advanced messaging, message analytics
- **Level 5**: Extreme messaging, multi-channel messaging

### 18. **Session Search** 🔎
Session search and history capabilities
- **Level 1**: Basic search, simple history
- **Level 2**: Filtered search, contextual search
- **Level 3**: Complex search, semantic search
- **Level 4**: Advanced search, search analytics
- **Level 5**: Extreme search, knowledge graph search

### 19. **Clarifying** ❓
Clarifying questions and disambiguation capabilities
- **Level 1**: Basic clarify, simple disambiguate
- **Level 2**: Targeted clarify, contextual clarify
- **Level 3**: Complex clarify, proactive clarify
- **Level 4**: Advanced clarify, clarify with reasoning
- **Level 5**: Extreme clarify, meta clarify

### 20. **Delegation** 🤝
Task delegation and coordination capabilities
- **Level 1**: Basic delegation, simple assignment
- **Level 2**: Multi delegation, delegation with context
- **Level 3**: Complex delegation, delegation tracking
- **Level 4**: Advanced delegation, delegation optimization
- **Level 5**: Extreme delegation, autonomous delegation

### 21. **Skills** 🎯
Skills and specialized capabilities
- **Level 1**: Basic skill, simple specialization
- **Level 2**: Multi skill, skill selection
- **Level 3**: Complex skills, skill adaptation
- **Level 4**: Advanced skills, skill synthesis
- **Level 5**: Extreme skills, skill evolution

### 22. **Context Engine** 🔄
Context engineering and management capabilities
- **Level 1**: Basic context, simple context switch
- **Level 2**: Context management, context prioritization
- **Level 3**: Complex context, context synthesis
- **Level 4**: Advanced context, context optimization
- **Level 5**: Extreme context, context intelligence

### 23. **Mixture of Agents** 🌐
Multi-agent collaboration capabilities
- **Level 1**: Basic MoA, simple coordination
- **Level 2**: Multi-agent task, agent specialization
- **Level 3**: Complex MoA, agent consensus
- **Level 4**: Advanced MoA, agent learning
- **Level 5**: Extreme MoA, agent swarm

## Cara Penggunaan

### 1. Run Level Tests untuk Satu Model

```bash
# Run semua level untuk semua capabilities
python run_level_tests.py --model "Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M"

# Run level tertentu saja
python run_level_tests.py --model "model_name" --level 1 2 3

# Run capability tertentu saja
python run_level_tests.py --model "model_name" --capability tool_calling vision --level all
```

### 2. Jalankan Bertahap untuk Hemat Waktu

```bash
# Smoke test satu capability di level awal
python run_level_tests.py --model "model_name" --capability json_mode --level 1

# Uji capability prioritas saja
python run_level_tests.py --model "model_name" --capability tool_calling rag terminal --level all

# Uji penuh 23 capability x 5 level x 2 test
python run_level_tests.py --model "model_name" --level all
```

### 3. Analyze Existing Results

```bash
# Placeholder untuk analisis hasil lama
python run_level_tests.py --analyze-all
```

Catatan: level assessment yang akurat membutuhkan run level test baru karena hasil lama hanya menguji tiap capability satu kali.

### 4. Output

Hasil pengujian disimpan di:
- `results/level_reports/<model>_level_report.md` - Markdown report
- `results/level_reports/<model>_level_report.json` - JSON report

## Scoring System

### Score per Test
- **0.0 - 0.25**: ❌ Failed
- **0.25 - 0.50**: 🔴 Poor
- **0.50 - 0.75**: 🟡 Acceptable
- **0.75 - 0.90**: ✅ Good
- **0.90 - 1.00**: ✅ Perfect

### Distance Metric
Setiap test memiliki `distance_weight` yang menunjukkan kontribusi terhadap "jarak" yang ditempuh model:
- Level 1: 25-30 weight per test
- Level 2: 30-40 weight per test
- Level 3: 50-60 weight per test
- Level 4: 75-80 weight per test
- Level 5: 100 weight per test

**Distance Covered** = (Total distance achieved / Max possible distance) × 100%

### Level Completion
- **Assessed Level**: Level tertinggi dimana rata-rata score level, distance, dan pass ratio memenuhi threshold 60%.
- **Failure Level**: Level pertama yang tidak memenuhi threshold 60%.
- **Level 0 - Not Qualified**: Capability belum lulus Level 1, sehingga tidak direkomendasikan untuk capability tersebut.

## Model Selection Guide

Berdasarkan hasil level testing, pilih model sesuai kebutuhan:

### General Purpose Assistant
- **Required**: Tool Calling L4, RAG L3, Messaging L3
- **Recommended**: Model dengan max level ≥ 4 di capabilities tersebut

### IT Operations Specialist
- **Required**: Tool Calling L5, Terminal L4, File Operations L3
- **Recommended**: Model dengan max level ≥ 4 di capabilities tersebut

### Multimodal Analyst
- **Required**: Vision L4, Tool Calling L3, RAG L3
- **Recommended**: Model dengan max level ≥ 4 di capabilities tersebut

### Code Assistant
- **Required**: Code Execution L4, Terminal L3, JSON Mode L3
- **Recommended**: Model dengan max level ≥ 4 di capabilities tersebut

### Research Assistant
- **Required**: RAG L5, Web Search L4, Multi-turn L4
- **Recommended**: Model dengan max level ≥ 4 di capabilities tersebut

## File Structure

```
model_specification_test/
├── level_test_definitions.py      # Definisi lengkap 23 capabilities × 5 levels
├── run_level_tests.py             # Main runner untuk level-based testing
├── test_adapter.py                # Adapter untuk integrasi dengan test suite existing
├── tests/
│   ├── test_helper.py             # Helper functions untuk run_single_test
│   ├── test_tool_calling.py       # Bisa punya run_single_test khusus
│   ├── test_vision.py             # Didukung fallback executor generic
│   └── ... (23 test modules)
└── results/
    └── level_reports/             # Output reports
        ├── <model>_level_report.md
        └── <model>_level_report.json
```

## Next Steps

1. **Run smoke test**: `python run_level_tests.py --model "model_name" --capability json_mode --level 1`
2. **Run capability prioritas**: contoh `tool_calling rag terminal json_mode` sebelum full run
3. **Run full level tests**: `python run_level_tests.py --model "model_name" --level all`
4. **Analyze results**: lihat `Assessed Level`, `Failure Level`, dan `Recommendation` di `results/level_reports/`
5. **Select model**: gunakan level capability yang sesuai kebutuhan use case

## Benefits

✅ **Granular Insight**: Tahu persis di level mana model berada untuk setiap capability
✅ **Model Selection**: Pilih model berdasarkan capability level yang dibutuhkan
✅ **Progress Tracking**: Track improvement model dari waktu ke waktu
✅ **Use Case Matching**: Match model dengan use case spesifik
✅ **Comprehensive**: 23 capabilities × 5 levels = 115+ test cases per model
