# Compressed Manual Test for All 23 Capabilities

Panduan ini adalah versi ringkas untuk menguji semua capability model melalui web UI `llama.cpp` tanpa menjalankan full manual test 230 prompt.

Targetnya:

```text
Full level test otomatis : 23 capability x 5 level x 2 prompt = 230 prompt
Compressed manual test   : 23 capability x 1 prompt = 23 prompt
```

Dokumen ini tidak menggantikan `run_level_tests.py`. Gunakan ini untuk screening cepat, demo manual, atau evaluasi kualitatif sebelum automated run.

## Prinsip Kompresi

Setiap capability diuji dengan satu prompt komposit. Di dalam jawaban, model harus mengerjakan bukti Level 1 sampai Level 5 dalam format yang sama:

```text
L1 Basic: ...
L2 Medium: ...
L3 Intermediate: ...
L4 Expert: ...
L5 Master: ...
Risks / assumptions: ...
```

Skor tetap diberikan per level:

| Skor | Kriteria |
|---:|---|
| `1.00` | Benar, lengkap, format patuh, minim halusinasi |
| `0.75` | Tujuan level tercapai, hanya minor issue |
| `0.50` | Sebagian benar, ada gap signifikan |
| `0.25` | Banyak salah, hanya sedikit elemen relevan |
| `0.00` | Gagal atau tidak mengikuti instruksi |

Level dianggap pass jika skor minimal `0.60`.

Assessed level:

```text
Level tertinggi yang pass secara berurutan dari Level 1.
```

Jika L1-L3 pass, L4 fail, L5 pass, hasil tetap Level 3. Level harus kontigu.

## Parameter Keberhasilan Capability

Gunakan parameter ini saat memberi skor L1-L5. Setiap level dinilai dari tiga lapis bukti:

1. Instruksi dipatuhi: model mengikuti format `L1-L5`, tidak melewati level, dan menjawab sesuai scope.
2. Jawaban benar: isi relevan dengan konteks DCIM, tidak mengarang hasil tool nyata, dan tidak bertentangan dengan SOP.
3. Capability terlihat: output menunjukkan kemampuan spesifik capability, bukan sekadar jawaban umum.

Hard fail umum untuk sebuah level:

- model tidak menjawab level tersebut;
- model mengaku menjalankan tool/file/terminal/web search padahal tidak tersedia;
- output melanggar format wajib, misalnya `json_mode` menghasilkan prose di luar JSON;
- jawaban menyarankan aksi berbahaya tanpa guardrail, approval, rollback, atau verifikasi;
- jawaban mengabaikan konteks yang diberikan dan mengganti dengan asumsi yang tidak ditandai.

Tabel berikut adalah parameter keberhasilan per capability:

| # | Capability | Parameter keberhasilan utama | Bukti minimal L1-L3 | Bukti kuat L4-L5 |
|---:|---|---|---|---|
| 1 | `tool_calling` | Memilih tool benar, parameter benar, urutan dan conditional logic tepat | Tool call memakai hostname/severity/log level yang benar dan urutan masuk akal | Ada branching, fallback saat tool tidak tersedia, parallel/aggregation plan, dan alert condition |
| 2 | `vision` | Jawaban grounded pada gambar, mampu ekstraksi visual dan analisis anomali | Mendeskripsikan objek/metric/severity yang benar dari gambar | Menghitung/mengekstrak angka, membandingkan tren, memberi prediksi dengan uncertainty |
| 3 | `rag` | Menggunakan konteks yang diberikan dan tidak menambah klaim tanpa sumber | Mengutip atau menerapkan SOP CPU/memory/disk dengan tepat | Mensintesis multi-SOP, membandingkan kebijakan, membuat decision tree yang konsisten |
| 4 | `code_execution` | Kode masuk akal, sintaks valid, dependency jelas, ada safety | Script sederhana sampai monitor multi-metric bisa dibaca dan logis | Ada error handling, retry, timeout, guardrail auto-remediation, dan arsitektur distributed |
| 5 | `terminal` | Command realistis, aman, urutan benar, interpretasi output tepat | Command dasar Linux benar dan menjelaskan kolom/output penting | Ada script dengan recovery, parallel checks, aggregation, logging, dan safety check |
| 6 | `json_mode` | JSON valid, schema sesuai, tidak ada markdown/prose di luar JSON | Field wajib ada, tipe data masuk akal, nested object/array benar | Struktur kompleks tetap valid, required fields lengkap, conditional config jelas |
| 7 | `structured_output` | Format sesuai instruksi dan mudah discan | Table/list/report punya kolom/section yang diminta | Ada dashboard/report conditional, prioritas, SLA, owner, rollback, checklist |
| 8 | `multiturn` | Mampu mempertahankan, mengganti, dan memulihkan konteks | Fakta awal diingat dan tidak tertukar antar asset | Ada summary state, context recovery, perubahan hipotesis, dan daftar evidence terbaru |
| 9 | `streaming` | Respons mengalir lengkap, cepat mulai, tidak rusak format | Stream selesai dan struktur dasar tidak putus | Jawaban panjang tetap koheren, checkpoint jelas, table/code tidak rusak di tengah |
| 10 | `cot_reasoning` | Reasoning ringkas, logis, dapat diverifikasi, tanpa hidden-chain demand | Keputusan punya alasan dan faktor prioritas jelas | Ada counterfactual, verification plan, asumsi, failure modes, dan self-check |
| 11 | `agent` | Ada loop observe-plan-act-verify dan pelaporan hasil | Rencana agent sederhana, action dan report jelas | Ada prioritization, stop condition, autonomy boundary, learning/prevention guardrail |
| 12 | `web_search` | Tidak mengarang fakta real-time; punya strategi source dan verifikasi | Query dan source plan relevan | Ada primary-source preference, freshness check, cross-reference, citation requirement |
| 13 | `file_ops` | Operasi file aman, path/aksi jelas, ada verifikasi/integrity | Read/search/copy/manifest dijelaskan dengan input-output jelas | Ada backup, checksum, compression, transform, sync/versioning, audit trail |
| 14 | `memory` | Fakta disimpan, di-recall, di-update tanpa bocor konteks lain | Recall akurat dan update old/new value jelas | Ada pattern recognition, memory evolution, privacy boundary, dan insight lintas incident |
| 15 | `task_planning` | Plan berurutan, punya dependencies, owner, risiko, dan exit criteria | Langkah troubleshooting runtut dan mencakup metrics/logs/escalation | Ada parallel workstream, rollback, decision point, governance, roadmap, success metrics |
| 16 | `cron` | Cron syntax benar, logging dan failure handling jelas | Jadwal dasar dan redirect log/stderr benar | Ada dependency check, missed-run alert, lock, retry, failover, audit trail |
| 17 | `messaging` | Pesan jelas, tepat audience, severity/action/owner lengkap | Alert punya impact, action, owner, dan target team | Ada routing multi-channel, ack tracking, escalation timing, deduplication, SLA update |
| 18 | `session_search` | Search relevan, filter/ranking jelas, sintesis tidak mengarang history | Bisa menemukan/filter snippet berdasarkan asset/severity | Ada ranking rationale, pattern synthesis, knowledge graph entity-relation-action-outcome |
| 19 | `clarifying` | Bertanya sebelum menyimpulkan, pertanyaan relevan dan diprioritaskan | Pertanyaan mencakup impact, scope, timeline, recent changes | Ada strategi klarifikasi bertahap, alasan tiap pertanyaan, data requirements, hypothesis map |
| 20 | `delegation` | Tugas diberikan ke role tepat, handoff dan tracking jelas | Role/team assignment sesuai domain incident | Ada dependency coordination, dynamic reassignment, workload awareness, governance/audit |
| 21 | `skills` | Skill dipilih sesuai masalah dan dapat dikombinasikan | Skill selection tepat dan alasan jelas | Ada skill synthesis, adaptation, feedback loop, evaluation, dan evolution plan |
| 22 | `context_engine` | Konteks dipilih, dipisah, diringkas, dan diprioritaskan dengan benar | Tidak mencampur context incident dan model evaluation | Ada preload/drop/request policy, optimization, privacy, traceability, learning loop |
| 23 | `mixture_of_agents` | Multi-agent punya spesialisasi, koordinasi, consensus, dan owner final | Agent assignment jelas dan output digabungkan | Ada disagreement resolution, confidence scoring, fault tolerance, governance, audit trail |

Panduan skor praktis per level:

| Skor | Bukti yang terlihat pada level tersebut |
|---:|---|
| `1.00` | Semua parameter utama terlihat, format benar, tidak ada risiko besar |
| `0.75` | Parameter utama terlihat, ada kekurangan kecil pada detail atau kelengkapan |
| `0.50` | Capability terlihat sebagian, tetapi ada gap pada correctness, format, atau completeness |
| `0.25` | Jawaban mostly generik; hanya satu-dua indikator capability terlihat |
| `0.00` | Capability tidak terlihat, format gagal, atau ada hard-fail |

Untuk hasil yang lebih konsisten, tulis alasan skor dalam `Notes` dengan format singkat:

```text
Pass evidence: ...
Missing evidence: ...
Risk/hallucination: ...
```


## Bentuk Output yang Dinilai per Level

Gunakan checklist ini saat membaca jawaban model. Skor setiap level berdasarkan apakah output pada level tersebut memenuhi bentuk minimum di bawah. Jika output hanya terdengar bagus tetapi tidak memiliki bukti yang diminta, turunkan skor.

### 1. Tool Calling

- L1: satu tool call jelas, misalnya `get_server_metrics`, dengan `hostname` benar.
- L2: dua tool call atau lebih dengan urutan benar, misalnya metrics lalu logs, serta parameter `level`/`since` masuk akal.
- L3: multi-tool workflow lengkap untuk satu incident, mencakup metrics, logs, top processes, dan hostname konsisten.
- L4: workflow bercabang memakai `if/then`, fallback saat tool tidak tersedia, dan alert condition eksplisit.
- L5: rencana parallel atau batch untuk banyak server, agregasi hasil, threshold alert, dan ringkasan output akhir.

### 2. Vision

- L1: deskripsi objek visual utama, bukan tebakan umum; menyebut elemen seperti dashboard, chart, server, alert, atau metric jika terlihat.
- L2: identifikasi server/severity/metric yang tampak dan pemisahan antara fakta visual vs asumsi.
- L3: analisis tren atau prioritas tindakan berdasarkan bukti visual.
- L4: ekstraksi angka, perhitungan sederhana, dan deteksi anomali dari data yang terlihat.
- L5: prediksi kondisi berikutnya, rekomendasi proaktif, serta uncertainty jika data visual kurang lengkap.

### 3. RAG

- L1: jawaban langsung memakai SOP/konteks yang diberikan, bukan best practice umum.
- L2: menerapkan SOP ke kasus konkret, menyebut durasi/threshold yang relevan.
- L3: checklist gabungan dari beberapa konteks dengan urutan troubleshooting yang masuk akal.
- L4: perbandingan multi-SOP, menyebut persamaan, perbedaan, dan eskalasi.
- L5: sintesis berbentuk decision tree/runbook yang tetap konsisten dengan semua konteks.

### 4. Code Execution / Code Generation

- L1: kode kecil valid dan langsung menjalankan tujuan sederhana.
- L2: kode punya loop/schedule logic, timestamp, threshold, dan output warning.
- L3: kode mencakup beberapa metric, logging, konfigurasi threshold, dan contoh cron.
- L4: ada struktur modular, error handling, retry/timeout, JSON report, dan guardrail untuk aksi berisiko.
- L5: ada arsitektur distributed, concurrency/worker, aggregation, anomaly detection, remediation policy, dan skeleton kode yang realistis.

### 5. Terminal

- L1: command benar dan output yang perlu diperiksa dijelaskan.
- L2: command monitoring/top process benar, kolom penting dijelaskan, dan sorting sesuai kebutuhan.
- L3: sequence command lengkap, aman, dan hasil akhirnya jelas.
- L4: script/command punya check status, recovery action, log inspection, dan error path.
- L5: automation mencakup parallel checks, aggregation, report, alerting, logging, dan safety guard.

### 6. JSON Mode

- L1: JSON valid saja, field wajib ada, tipe data masuk akal.
- L2: nested object/array valid, tidak ada markdown/prose di luar JSON.
- L3: schema kompleks dipatuhi, field tidak hilang, array/object konsisten.
- L4: banyak object tetap lengkap, ada validasi required fields, struktur tidak berubah di tengah.
- L5: konfigurasi besar tetap valid, nested, conditional logic terwakili sebagai data, dan tidak menjadi penjelasan bebas.

### 7. Structured Output

- L1: table/list sederhana dengan kolom atau nomor yang diminta.
- L2: markdown table/report section rapi dan semua kolom wajib terisi.
- L3: report punya executive summary, detail, analisis, dan action items yang saling konsisten.
- L4: dashboard/report punya KPI, visualisasi teks bila diminta, prioritas, dan rekomendasi operasional.
- L5: output conditional berubah sesuai severity, mencakup SLA, owner, rollback, escalation, dan checklist.

### 8. Multi-turn

- L1: mengingat satu fakta yang baru diberikan dan menggunakannya di follow-up.
- L2: mempertahankan beberapa fakta tanpa tertukar antar asset.
- L3: mampu context switch lalu kembali ke konteks sebelumnya dengan benar.
- L4: merangkum state percakapan, constraints, keputusan, dan next action.
- L5: memperbarui hipotesis saat evidence berubah dan menjelaskan fakta lama vs fakta baru.

### 9. Streaming

- L1: stream mulai dan selesai untuk jawaban pendek tanpa putus.
- L2: struktur sedang tetap rapi sampai akhir.
- L3: jawaban panjang dengan code/table tetap lengkap dan tidak kehilangan format.
- L4: report kompleks tetap konsisten, tidak berhenti sebelum final section.
- L5: runbook panjang punya checkpoint, alur tetap koheren, dan completion jelas.

### 10. Chain-of-Thought / Reasoning

- L1: memberi keputusan sederhana dengan alasan ringkas yang benar.
- L2: membandingkan dua kondisi dan memilih prioritas berdasarkan faktor jelas.
- L3: menghubungkan beberapa sinyal menjadi diagnosis/hypothesis yang masuk akal.
- L4: counterfactual jelas, menunjukkan keputusan berbeda untuk penyebab berbeda.
- L5: verification plan lengkap, mencakup asumsi, data yang harus dicek, failure modes, dan self-check.

### 11. Agent

- L1: ada plan, action, dan report untuk tugas sederhana.
- L2: investigasi multi-step punya observasi, aksi, dan kriteria keputusan.
- L3: workflow multi-domain punya prioritas dan next action.
- L4: menangani beberapa incident dengan stop condition, owner, dan resolution criteria.
- L5: agent loop lengkap: observe, plan, act, verify, learn, prevent, dengan autonomy boundary.

### 12. Web Search

- L1: query relevan dan source target masuk akal.
- L2: query lebih spesifik, memecah masalah ke beberapa pencarian.
- L3: membandingkan jenis sumber dan memilih sumber primer/tepercaya.
- L4: workflow verifikasi fakta punya cross-check, freshness, dan primary source.
- L5: real-time brief workflow punya citation requirement, recency check, confidence, dan actionability.

### 13. File Operations

- L1: operasi read/summarize menyebut path, target field, dan output yang diharapkan.
- L2: search/copy punya pattern, source, destination, dan verifikasi hasil.
- L3: manifest/report mencakup file input, field ekstraksi, dan format output.
- L4: backup/transform punya checksum, compression, error handling, dan rollback/safety.
- L5: distributed workflow punya sync, versioning, integrity check, audit trail, dan conflict handling.

### 14. Memory

- L1: recall satu fakta secara akurat.
- L2: recall beberapa fakta dan mengaitkan dengan asset yang benar.
- L3: update memory membedakan old value, new value, dan waktu/perubahan.
- L4: memory diringkas menjadi insight operasional tanpa kehilangan fakta penting.
- L5: memory evolution menunjukkan pattern lintas incident, privacy boundary, dan rule untuk data retention.

### 15. Task Planning

- L1: plan pendek berurutan dan actionable.
- L2: plan mencakup metrics, logs, process check, dan escalation trigger.
- L3: plan multi-domain menyebut dependencies, owner, risk, dan prioritas.
- L4: plan adaptif punya parallel workstream, decision point, rollback, komunikasi, dan exit criteria.
- L5: strategy jangka panjang punya roadmap, governance, security, automation, evaluation, dan success metrics.

### 16. Cron

- L1: cron syntax benar untuk jadwal sederhana.
- L2: cron job punya command, log redirection, stderr handling, dan path jelas.
- L3: workflow scheduling menyebut urutan job, dependency, dan output report.
- L4: monitoring cron mencakup missed-run detection, alerting, retry, dan health check.
- L5: distributed/self-healing scheduler punya lock, failover, idempotency, audit trail, dan recovery.

### 17. Messaging

- L1: pesan alert singkat berisi asset, severity, dan masalah.
- L2: alert terformat punya impact, action, owner/team, dan timestamp atau SLA.
- L3: routing ke beberapa team sesuai domain dan kondisi incident.
- L4: template system punya acknowledgement, escalation, personalization, dan tracking.
- L5: multi-channel orchestration punya deduplication, escalation timing, unified status, dan SLA communication.

### 18. Session Search

- L1: menyebut query/filter untuk menemukan satu fakta session.
- L2: filter berdasarkan asset/severity/timeframe dan output snippet relevan.
- L3: sintesis pola dari beberapa hasil search, bukan sekadar daftar.
- L4: ranking hasil punya alasan, confidence, dan summary.
- L5: knowledge graph mencakup entity, relation, incident, hypothesis, action, outcome, dan discovery flow.

### 19. Clarifying

- L1: pertanyaan dasar relevan sebelum troubleshooting.
- L2: maksimal 5 pertanyaan paling penting, diprioritaskan.
- L3: pertanyaan dikelompokkan berdasarkan impact, scope, timeline, recent changes.
- L4: setiap pertanyaan punya alasan mengapa penting dan data apa yang dicari.
- L5: strategi klarifikasi bertahap dengan hypothesis map, blast radius, data requirements, dan stop condition.

### 20. Delegation

- L1: tugas diberikan ke role/team yang tepat dengan output yang diharapkan.
- L2: incident dibagi ke beberapa domain team dan tanggung jawab jelas.
- L3: dependency, handoff, status tracking, dan escalation path terlihat.
- L4: ada dynamic reassignment saat prioritas/team capacity berubah.
- L5: enterprise delegation punya governance, auditability, ownership, policy, dan cross-functional coordination.

### 21. Skills

- L1: memilih skill yang tepat untuk satu masalah dan alasan singkat.
- L2: mengombinasikan dua skill dengan pembagian tugas jelas.
- L3: mengadaptasi skill untuk masalah baru/multi-sinyal.
- L4: mensintesis beberapa skill menjadi reusable workflow atau runbook.
- L5: skill evolution punya feedback loop, evaluation metric, retraining/update process, dan versioning.

### 22. Context Engine

- L1: mengidentifikasi konteks aktif dan data yang relevan.
- L2: memisahkan dua konteks tanpa mencampur instruksi atau tujuan.
- L3: menyintesis SOP, metrics, logs, dan constraints menjadi action context.
- L4: menentukan context yang perlu preload, summarize, drop, atau request dengan alasan.
- L5: self-optimizing context design punya learning loop, privacy, traceability, evaluation, dan failure handling.

### 23. Mixture of Agents

- L1: dua agent punya role berbeda dan hasilnya digabungkan.
- L2: beberapa agent spesialis ditugaskan sesuai domain incident.
- L3: disagreement/consensus workflow menghasilkan keputusan final yang beralasan.
- L4: orchestration punya load balancing, confidence scoring, fault tolerance, dan owner final.
- L5: enterprise multi-agent system punya self-organization, self-healing, governance, audit trail, dan continuous improvement.

## Contoh Cara Memberi Skor Satu Level

Jika prompt `tool_calling` L4 menghasilkan workflow bercabang tetapi tidak menyebut fallback saat tool `kill` tidak tersedia:

```text
Score L4: 0.75
Pass evidence: urutan metrics -> top processes -> alert ada; conditional CPU high ada.
Missing evidence: fallback saat kill tool tidak tersedia kurang eksplisit.
Risk/hallucination: tidak ada klaim tool sudah dijalankan.
```

Jika prompt `json_mode` L3 menghasilkan JSON valid tetapi ada satu field wajib hilang:

```text
Score L3: 0.50
Pass evidence: JSON valid dan nested metrics benar.
Missing evidence: field alerts tidak ada.
Risk/hallucination: tidak ada.
```

## Kapan Harus Pakai Full Automated Test

Pakai `run_level_tests.py` jika:

- hasil akan dipakai untuk keputusan model final;
- perlu report kuantitatif yang bisa dibandingkan antar model;
- perlu memverifikasi OpenAI-compatible API, JSON mode, streaming, dan response format;
- capability bergantung pada tool nyata, file system, shell, vision upload, atau web search.

Command full run:

```bash
cd /home/infra/dcim_project/model_specification_test
python run_level_tests.py --model "Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M" --level all
```

## Setting Web UI

Gunakan setting yang sama selama satu run:

| Setting | Rekomendasi |
|---|---:|
| Temperature | `0.3` |
| Max tokens | `2048-4096` |
| Context size | `8192+` |
| Chat session | satu session per capability |
| System prompt | konsisten untuk semua capability |

System prompt opsional:

```text
You are a DCIM operations assistant. Follow the requested structure exactly. If a capability requires external tools, file access, terminal execution, web search, memory, or images that are not available in this chat UI, simulate the intended action and explicitly mark it as simulated. Do not invent real tool results.
```

## Template Pencatatan

```markdown
# Compressed Manual Capability Test Result

Model:
Endpoint:
Date:
Tester:
Temperature:
Max tokens:
Context size:

| # | Capability | L1 | L2 | L3 | L4 | L5 | Assessed Level | Notes |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | tool_calling |  |  |  |  |  |  |  |
| 2 | vision |  |  |  |  |  |  |  |
| 3 | rag |  |  |  |  |  |  |  |
| 4 | code_execution |  |  |  |  |  |  |  |
| 5 | terminal |  |  |  |  |  |  |  |
| 6 | json_mode |  |  |  |  |  |  |  |
| 7 | structured_output |  |  |  |  |  |  |  |
| 8 | multiturn |  |  |  |  |  |  |  |
| 9 | streaming |  |  |  |  |  |  |  |
| 10 | cot_reasoning |  |  |  |  |  |  |  |
| 11 | agent |  |  |  |  |  |  |  |
| 12 | web_search |  |  |  |  |  |  |  |
| 13 | file_ops |  |  |  |  |  |  |  |
| 14 | memory |  |  |  |  |  |  |  |
| 15 | task_planning |  |  |  |  |  |  |  |
| 16 | cron |  |  |  |  |  |  |  |
| 17 | messaging |  |  |  |  |  |  |  |
| 18 | session_search |  |  |  |  |  |  |  |
| 19 | clarifying |  |  |  |  |  |  |  |
| 20 | delegation |  |  |  |  |  |  |  |
| 21 | skills |  |  |  |  |  |  |  |
| 22 | context_engine |  |  |  |  |  |  |  |
| 23 | mixture_of_agents |  |  |  |  |  |  |  |
```


## Contoh Output Template Pencatatan

Contoh berikut memakai skor simulasi. Angka ini bukan hasil benchmark model tertentu, tetapi contoh format final setelah kamu menilai output dari web UI.

```markdown
# Compressed Manual Capability Test Result

Model: Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M
Endpoint: http://localhost:8080
Date: 2026-06-10
Tester: Manual evaluator
Temperature: 0.3
Max tokens: 4096
Context size: 8192

| # | Capability | L1 | L2 | L3 | L4 | L5 | Assessed Level | Notes |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | tool_calling | 1.00 | 0.75 | 0.75 | 0.50 | 0.25 | Level 3 - Intermediate | Tool dan parameter benar sampai L3; L4 kurang fallback eksplisit; L5 belum ada agregasi matang. |
| 2 | vision | 1.00 | 0.75 | 0.50 | 0.25 | 0.00 | Level 2 - Medium | Deskripsi dan severity cukup; ekstraksi angka/anomali lemah; L5 terlalu spekulatif. |
| 3 | rag | 1.00 | 1.00 | 0.75 | 0.75 | 0.50 | Level 4 - Expert | Konteks SOP dipakai konsisten; decision tree L5 kurang lengkap. |
| 4 | code_execution | 1.00 | 0.75 | 0.75 | 0.50 | 0.25 | Level 3 - Intermediate | Kode dasar baik; L4 kurang retry/timeout; L5 masih desain umum. |
| 5 | terminal | 1.00 | 0.75 | 0.75 | 0.50 | 0.25 | Level 3 - Intermediate | Command benar; L4 recovery kurang aman; L5 belum ada parallel implementation jelas. |
| 6 | json_mode | 1.00 | 1.00 | 0.75 | 0.75 | 0.50 | Level 4 - Expert | JSON valid sampai L4; L5 kurang jumlah field/conditional detail. |
| 7 | structured_output | 1.00 | 1.00 | 0.75 | 0.75 | 0.50 | Level 4 - Expert | Struktur rapi; L5 conditional report kurang SLA detail. |
| 8 | multiturn | 1.00 | 0.75 | 0.50 | 0.50 | 0.25 | Level 2 - Medium | Retensi fakta dasar baik; context recovery L3 belum stabil. |
| 9 | streaming | 1.00 | 0.75 | 0.75 | 0.50 | 0.50 | Level 3 - Intermediate | Stream selesai dan format stabil sampai L3; L4 panjang mulai kehilangan struktur. |
| 10 | cot_reasoning | 1.00 | 0.75 | 0.75 | 0.75 | 0.50 | Level 4 - Expert | Reasoning ringkas dan counterfactual cukup; L5 verification plan kurang failure modes. |
| 11 | agent | 1.00 | 0.75 | 0.75 | 0.50 | 0.25 | Level 3 - Intermediate | Workflow agent jelas; autonomy boundary dan learning loop belum kuat. |
| 12 | web_search | 0.75 | 0.75 | 0.50 | 0.50 | 0.25 | Level 2 - Medium | Search plan masuk akal; tidak ada real search; source verification belum detail. |
| 13 | file_ops | 0.75 | 0.75 | 0.50 | 0.50 | 0.25 | Level 2 - Medium | Simulasi operasi aman; manifest/checksum belum cukup detail. |
| 14 | memory | 1.00 | 0.75 | 0.50 | 0.50 | 0.25 | Level 2 - Medium | Recall dasar baik; update old/new value kurang jelas. |
| 15 | task_planning | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Plan runtut, adaptif, punya roadmap dan success metrics. |
| 16 | cron | 1.00 | 0.75 | 0.75 | 0.50 | 0.25 | Level 3 - Intermediate | Syntax dan logging baik; distributed failover belum matang. |
| 17 | messaging | 1.00 | 1.00 | 0.75 | 0.75 | 0.50 | Level 4 - Expert | Alert dan routing baik; L5 kurang deduplication policy. |
| 18 | session_search | 0.75 | 0.75 | 0.50 | 0.50 | 0.25 | Level 2 - Medium | Search strategy ada; ranking dan knowledge graph masih konseptual. |
| 19 | clarifying | 1.00 | 1.00 | 0.75 | 0.75 | 0.75 | Level 5 - Master | Pertanyaan terstruktur, prioritas jelas, strategi bertahap lengkap. |
| 20 | delegation | 1.00 | 0.75 | 0.75 | 0.50 | 0.50 | Level 3 - Intermediate | Role assignment benar; dynamic reassignment/governance kurang kuat. |
| 21 | skills | 1.00 | 0.75 | 0.75 | 0.50 | 0.50 | Level 3 - Intermediate | Skill selection baik; skill evolution masih kurang metrik evaluasi. |
| 22 | context_engine | 1.00 | 0.75 | 0.75 | 0.75 | 0.50 | Level 4 - Expert | Context separation dan preload/drop policy baik; L5 learning loop kurang konkret. |
| 23 | mixture_of_agents | 1.00 | 0.75 | 0.75 | 0.50 | 0.50 | Level 3 - Intermediate | Agent specialization dan consensus cukup; fault tolerance/governance belum matang. |

## Summary

| Metric | Value |
|---|---:|
| Average assessed level | 3.17 |
| Level 5 capability count | 2 |
| Level 4 capability count | 6 |
| Level 3 capability count | 9 |
| Level 2 capability count | 6 |
| Level 1 capability count | 0 |
| Level 0 capability count | 0 |

## Recommendation

Model layak untuk screening DCIM assistant sampai workload Level 3, dengan beberapa capability kuat di Level 4-5 seperti `task_planning`, `clarifying`, `rag`, `json_mode`, `structured_output`, dan `context_engine`. Capability yang membutuhkan tool nyata seperti `web_search`, `file_ops`, `memory`, `vision`, dan `session_search` perlu diuji ulang dengan input/tool aktual sebelum dipakai untuk keputusan final.
```

Format notes yang lebih detail bisa ditulis seperti ini untuk capability tertentu:

```text
Capability: tool_calling
Assessed Level: Level 3 - Intermediate
Pass evidence:
- L1 memilih get_server_metrics(hostname=srv-web-01).
- L2 memilih get_server_metrics dan check_logs dengan urutan benar.
- L3 mencakup metrics, logs, dan top processes untuk srv-db-02.
Missing evidence:
- L4 tidak menjelaskan fallback saat kill tool tidak tersedia.
- L5 tidak menunjukkan agregasi hasil lintas server.
Risk/hallucination:
- Tidak ada klaim tool benar-benar dijalankan, aman untuk simulasi web UI.
```

## Shared Context untuk Prompt DCIM

Paste ini sekali di awal jika prompt membutuhkan konteks DCIM:

```text
DCIM context:
- srv-web-01: CPU 85%, memory 72%, disk 68%, status warning.
- srv-web-03: intermittent latency, suspected logs and CPU issue.
- srv-db-01: CPU 92%, memory 88%, disk 74%, critical workload.
- srv-db-02: high memory and slow query alerts.
- srv-app-05: critical app alert, suspected memory leak.
- srv-app-10: production app, service restart needs approval.
- SOP CPU: if CPU > 90% for more than 5 minutes, inspect top processes, check cron or ETL, avoid killing scheduled ETL, escalate if service impact persists beyond 10 minutes.
- SOP Memory: memory leak means rising memory, frequent GC, and swap activity; collect snapshot before restart; production restart requires approval.
- SOP Disk: if disk > 85%, check large files and log rotation; if disk > 95%, stop non-critical jobs; never delete database files without DBA approval.
```

## 23 Compressed Capability Prompts

### 1. Tool Calling

```text
Evaluate tool calling in one compact answer. Available tools:
- get_server_metrics(hostname)
- check_logs(hostname, level, since)
- get_top_processes(hostname, sort_by, limit)
- send_alert(severity, hostname, message)

Output JSON only with keys L1, L2, L3, L4, L5, risks.
L1: create the tool call to check CPU usage for srv-web-01.
L2: create ordered tool calls to inspect metrics and error logs for slow srv-web-03.
L3: create ordered tool calls for srv-db-02 high memory: metrics, logs, top processes.
L4: create conditional workflow for srv-app-10: metrics -> if CPU high then top processes -> if unknown process and kill tool unavailable then alert.
L5: create parallel/aggregated monitoring plan for srv-web-01, srv-web-02, srv-db-01, srv-db-02, srv-app-01; alert critical when CPU > 85%.
```

Parameter keberhasilan: tool names, parameter accuracy, sequence, conditional logic, aggregation.

### 2. Vision

Use a dashboard or alert image if the web UI supports upload. If no image support, use the simulated prompt below and mark the result as simulation.

```text
Evaluate vision capability from the attached DCIM dashboard image. If no image is attached, clearly say vision input is unavailable and provide only the expected analysis structure.

Return sections L1-L5.
L1: describe visible dashboard elements and main objects.
L2: identify affected server, severity, and visible metrics.
L3: analyze trend and recommend immediate action.
L4: extract numeric data, calculate average CPU/memory if visible, and identify anomalies.
L5: predict likely state in 1 hour and propose proactive actions with uncertainty.
```

Parameter keberhasilan: visual grounding, metric extraction, anomaly reasoning, uncertainty handling.

### 3. RAG

Paste the shared DCIM context first, then send:

```text
Using only the provided DCIM context and SOP, answer in sections L1-L5.
L1: what should be done if CPU > 90%?
L2: srv-web-01 has CPU 95% for 7 minutes. What should be done?
L3: make a troubleshooting checklist for CPU high plus memory leak.
L4: compare CPU alert SOP and Disk alert SOP, including escalation differences.
L5: create a concise decision tree for server issues across CPU, memory, and disk.
Do not use outside knowledge unless marked as assumption.
```

Parameter keberhasilan: context usage, no unsupported claims, synthesis, decision structure.

### 4. Code Execution / Code Generation

```text
Evaluate code generation in one answer. Return sections L1-L5. Include code blocks only where useful.
L1: Python hello world.
L2: Python CPU monitor every 5 minutes with timestamp and warning if CPU > 80%.
L3: Python monitor for CPU, memory, disk with threshold logging and a cron entry every 10 minutes.
L4: robust system monitor design/code with CPU, memory, disk, network, processes, JSON report, retry/error handling, and safe service restart placeholder.
L5: distributed monitoring architecture and Python skeleton for multiple servers, aggregation, anomaly detection, auto-remediation guardrails, and dashboard output.
```

Parameter keberhasilan: syntax, executable structure, safety, error handling, architecture.

### 5. Terminal

```text
Evaluate terminal capability. Return sections L1-L5. If command execution is unavailable, provide commands and expected interpretation, clearly marked as not executed.
L1: command for uname -a and what to inspect.
L2: command to list top 10 processes by CPU and explain key columns.
L3: command sequence to check disk usage and list files > 1GB sorted by size.
L4: command/script to check nginx, start it if stopped, and inspect logs if start fails.
L5: shell automation design to run CPU, memory, disk, and network checks in parallel, aggregate results, generate daily report, and send email alert.
```

Parameter keberhasilan: command correctness, ordering, safe guards, interpretation.

### 6. JSON Mode

```text
Output valid JSON only, no markdown. The JSON must contain keys L1, L2, L3, L4, L5, validation_notes.
L1: server status for srv-web-01 with hostname, cpu, memory, status.
L2: nested object for srv-db-01 with metrics and anomalies array.
L3: schema-compliant incident object with hostname, metrics, alerts array, recommendations array.
L4: array of 5 servers, each with hostname, cpu, memory, disk, status, recommendations, required_fields_present.
L5: monitoring configuration with nested thresholds, alert routing, escalation, retention, conditional logic, and at least 25 meaningful fields.
```

Parameter keberhasilan: valid JSON, schema consistency, nested structures, no prose outside JSON.

### 7. Structured Output

```text
Evaluate structured output. Return exactly sections L1-L5.
L1: simple table of 3 servers with hostname, cpu, memory.
L2: markdown comparison table with hostname, cpu, memory, status, recommendation.
L3: incident report with Executive Summary, Detailed Metrics, Trend Analysis, Action Items.
L4: dashboard-style report with KPI summary, ASCII trend chart, prioritized recommendations.
L5: conditional report: if severity is critical include command structure, escalation matrix, SLA timer, owner, rollback, post-incident checklist; otherwise include operational summary.
```

Parameter keberhasilan: format compliance, completeness, readability, conditional structure.

### 8. Multi-turn

Best manual method is 3 turns. For compressed mode, use this single prompt, but mark result as approximate.

```text
Simulate a multi-turn DCIM conversation and show how you retain context. Return sections L1-L5.
L1: remember that srv-web-01 has CPU 85%; answer a follow-up about its CPU.
L2: maintain context for srv-web-01 and srv-db-01, then answer which is more critical.
L3: handle a context switch from CPU investigation to memory leak, then recover the previous CPU context.
L4: summarize the conversation state and make a decision with retained constraints.
L5: show how context evolves after new evidence changes the initial hypothesis, and list what changed.
```

Strict variant: run the L1-L5 tasks as separate chat turns and score retention after each turn.

Parameter keberhasilan: context retention, consistency, recovery, summary quality.

### 9. Streaming

This capability is partly UI/runtime behavior. Use stopwatch for TTFT if possible.

```text
Generate a streaming-friendly response in sections L1-L5.
L1: short 5-step CPU troubleshooting list.
L2: medium structured server health summary.
L3: longer incident analysis with a code block.
L4: complex report with headings, tables, and consistent formatting until the end.
L5: very long but organized operational runbook; include checkpoints every few paragraphs and maintain coherence.
```

Record manually:

```text
TTFT:
Tokens/second if visible:
Did stream start quickly:
Did formatting break mid-stream:
Did response complete:
```

Parameter keberhasilan: stream starts, smoothness, completeness, no formatting collapse.

### 10. Chain-of-Thought / Reasoning

Do not require hidden chain-of-thought. Ask for concise reasoning summary.

```text
Evaluate reasoning with concise visible rationale only. Return sections L1-L5.
L1: decide whether CPU 85% is warning or critical and explain briefly.
L2: compare CPU 92% on database vs memory 88% on app; pick priority and justify.
L3: diagnose likely cause when latency, CPU spike, and slow queries occur together.
L4: give counterfactual analysis: what changes if high CPU is caused by scheduled ETL vs unknown process?
L5: produce a verification plan that checks your own diagnosis, assumptions, and failure modes.
```

Parameter keberhasilan: logical correctness, factor coverage, counterfactual quality, self-verification.

### 11. Agent

```text
Act as a DCIM incident agent. Return sections L1-L5.
L1: plan and report a simple CPU check for srv-web-01.
L2: investigate slow srv-web-03 using metrics, logs, and decision criteria.
L3: run a simulated multi-step workflow for app latency, database CPU, and network latency; include next actions.
L4: prioritize multiple concurrent incidents, assign actions, define stop conditions, and resolution criteria.
L5: design an autonomous incident agent loop with observation, planning, action, verification, learning, and prevention guardrails.
```

Parameter keberhasilan: planning, autonomy, decision quality, verification, guardrails.

### 12. Web Search

If real web search is not integrated, score as simulated only.

```text
Evaluate web search behavior. If real search is unavailable, do not invent current facts; provide search plan and query strategy. Return sections L1-L5.
L1: formulate a simple search query for llama.cpp server JSON mode documentation.
L2: formulate targeted queries to troubleshoot llama-server slow generation.
L3: compare what sources you would use for llama.cpp, vLLM, and Ollama inference features.
L4: describe a fact-verification workflow using primary sources and cross-checks.
L5: design a real-time intelligence brief workflow for model serving incidents, including freshness checks and citation requirements.
```

Parameter keberhasilan: source strategy, refusal to fabricate, verification plan, actionability.

### 13. File Operations

If file tools are unavailable in web UI, request a safe simulation.

```text
Evaluate file operation capability. If file access is unavailable, provide exact intended operations and safety checks, marked simulated. Return sections L1-L5.
L1: read a config file and summarize target fields.
L2: search files for ERROR logs and copy matching files to a backup folder.
L3: find JSON reports, extract model names and assessed levels, and create a manifest.
L4: backup, compress, checksum, and transform level reports into a summary table.
L5: design distributed file sync/backup/versioning/integrity workflow for model reports across servers.
```

Parameter keberhasilan: safe file handling, exact paths/operations, verification, integrity checks.

### 14. Memory

True memory requires multiple turns. This prompt is a compressed approximation.

```text
Evaluate memory behavior. Return sections L1-L5.
L1: store and recall: srv-web-01 CPU is 85%.
L2: store three facts about srv-web-01, srv-db-01, srv-app-05 and recall them accurately.
L3: update memory when srv-web-01 CPU changes from 85% to 95%; distinguish old vs new value.
L4: summarize remembered incident facts into operational insight.
L5: describe how memory should evolve across repeated incidents and identify patterns without leaking unrelated session data.
```

Strict variant: give facts in one turn, ask recall in later turns.

Parameter keberhasilan: recall accuracy, update handling, synthesis, privacy boundaries.

### 15. Task Planning

```text
Evaluate task planning. Return sections L1-L5.
L1: 3-step plan for troubleshooting high CPU on one server.
L2: plan for slow server investigation covering metrics, logs, processes, escalation.
L3: plan for multi-domain incident: app latency, database CPU, network latency, with dependencies.
L4: adaptive production outage plan with parallel workstreams, rollback criteria, communication, and decision points.
L5: 90-day reliability improvement strategy for DCIM operations with observability, automation, evaluation, governance, security, and metrics.
```

Parameter keberhasilan: sequence, dependencies, prioritization, risk management, feasibility.

### 16. Cron

```text
Evaluate cron and scheduling. Return sections L1-L5.
L1: cron expression to run a CPU check every 5 minutes.
L2: cron job with logging and stderr handling for a monitoring script.
L3: scheduled workflow that runs health checks, rotates logs, and triggers report generation.
L4: cron monitoring plan with dependency checks, missed-run detection, and alerting.
L5: self-healing distributed scheduling design with failover, lock handling, retries, and audit trail.
```

Parameter keberhasilan: cron syntax, logging, dependencies, monitoring, failover.

### 17. Messaging

```text
Evaluate messaging and notification. Return sections L1-L5.
L1: write a simple critical alert message for srv-db-01 down.
L2: formatted alert with severity, impact, affected service, action, owner.
L3: route messages to platform, app, and network teams based on incident clues.
L4: design notification templates with personalization, escalation, acknowledgement tracking, and analytics.
L5: multi-channel incident communication orchestration with deduplication, escalation timing, SLA, and unified status updates.
```

Parameter keberhasilan: clarity, routing, escalation, tracking, multi-channel consistency.

### 18. Session Search

```text
Evaluate session search. If actual session history search is unavailable, simulate search strategy and output format. Return sections L1-L5.
L1: find prior mention of srv-web-01 CPU.
L2: search session for critical database incidents and filter by severity.
L3: synthesize repeated patterns from past CPU, memory, and disk incidents.
L4: rank relevant session snippets and summarize why each matters.
L5: design a knowledge-graph style session search for assets, incidents, hypotheses, actions, and outcomes.
```

Parameter keberhasilan: relevance, filtering, ranking, synthesis, graph reasoning.

### 19. Clarifying

```text
Evaluate clarifying ability. Return sections L1-L5.
L1: ask essential questions for "server lambat".
L2: ask at most 5 priority questions for a CPU high alert.
L3: for "semua aplikasi down", group questions by impact, scope, timeline, recent changes.
L4: for intermittent multi-region latency, ask questions and explain why each matters.
L5: for "DCIM tidak akurat dan beberapa workflow gagal", create a staged clarification strategy to discover scope, blast radius, root hypotheses, and required data.
```

Parameter keberhasilan: asks before assuming, question relevance, structure, reasoning.

### 20. Delegation

```text
Evaluate delegation. Return sections L1-L5.
L1: delegate a CPU check to the right role/team.
L2: split a slow application incident among app, platform, database, and network roles.
L3: coordinate dependencies and handoffs for a multi-domain incident, including status tracking.
L4: optimize delegation dynamically when one team is overloaded and new evidence changes priority.
L5: design enterprise autonomous delegation with governance, escalation, auditability, ownership, and cross-functional coordination.
```

Parameter keberhasilan: role fit, dependency management, tracking, dynamic adjustment, governance.

### 21. Skills

```text
Evaluate skills/specialization. Assume these skills exist: incident_analysis, log_triage, metrics_analysis, report_writer, runbook_builder. Return sections L1-L5.
L1: choose one skill for CPU alert handling and explain why.
L2: combine two skills for slow server investigation.
L3: adapt skills for a novel incident involving CPU, memory leak, and latency.
L4: synthesize multiple skills into a reusable incident response workflow.
L5: propose how the skill set should evolve after repeated incidents, including feedback and evaluation.
```

Parameter keberhasilan: skill selection, combination, adaptation, synthesis, improvement loop.

### 22. Context Engine

```text
Evaluate context engineering. Return sections L1-L5.
L1: identify the active context from a CPU alert.
L2: manage two contexts: incident triage and model evaluation, and keep them separate.
L3: synthesize context from SOP, metrics, logs, and user constraints into an action context.
L4: decide what context should be preloaded, summarized, dropped, or requested for a production outage.
L5: design a self-optimizing context engine that learns which context improves DCIM incident outcomes while preserving privacy and traceability.
```

Parameter keberhasilan: context separation, prioritization, synthesis, optimization, governance.

### 23. Mixture of Agents

```text
Evaluate mixture-of-agents coordination. Return sections L1-L5.
L1: coordinate two agents: metrics analyst and incident reporter.
L2: assign specialized agents for app, database, network, and platform investigation.
L3: produce a consensus workflow when agents disagree about root cause.
L4: design dynamic agent orchestration with load balancing, fault tolerance, confidence scoring, and final decision ownership.
L5: design enterprise multi-agent incident response with self-organization, self-healing, governance, audit trail, and continuous improvement.
```

Parameter keberhasilan: specialization, consensus, orchestration, fault tolerance, governance.

## Interpretasi Hasil

Gunakan ringkasan ini untuk keputusan awal:

| Pola hasil | Interpretasi |
|---|---|
| Mayoritas capability berhenti di L1-L2 | Model belum layak untuk DCIM assistant serius |
| Banyak capability sampai L3 | Layak untuk assistant operasional dengan guardrail |
| Capability inti sampai L4 | Layak diuji full otomatis dan pilot terbatas |
| Banyak L5 pass | Kandidat kuat, tetap perlu automated test dan validasi tool nyata |

Capability inti untuk DCIM assistant:

```text
json_mode, structured_output, rag, tool_calling, task_planning, clarifying, code_execution, terminal, context_engine, agent
```

## Rekomendasi Alur Cepat

1. Jalankan 23 prompt kompresi ini di web UI.
2. Catat skor L1-L5 per capability.
3. Pilih 5-10 capability dengan skor tertinggi dan terendah.
4. Jalankan automated subset untuk capability tersebut.
5. Jika hasil manual dan otomatis konsisten, lanjut full run.

Automated subset contoh:

```bash
cd /home/infra/dcim_project/model_specification_test
python run_level_tests.py \
  --model "Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M" \
  --capability json_mode structured_output rag tool_calling task_planning clarifying code_execution terminal context_engine agent \
  --level all
```

## Catatan Penting

- Prompt kompresi mengurangi beban manual, tetapi juga mengurangi sensitivitas evaluasi.
- Satu jawaban panjang bisa terlihat bagus walau model gagal dalam interaksi nyata.
- Capability seperti `multiturn`, `memory`, `streaming`, `vision`, `terminal`, `file_ops`, dan `web_search` lebih akurat jika diuji dengan tool/input nyata.
- Untuk keputusan final, gunakan report otomatis di `results/level_reports/`.
