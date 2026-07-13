# Manual Testing via llama.cpp Web UI

Panduan ini menjelaskan cara menguji model secara manual melalui web UI `llama.cpp`, dengan acuan yang sama seperti sistem level-based testing di `run_level_tests.py`.

Dokumen ini cocok dipakai ketika:

- ingin melihat perilaku model langsung dari chat UI;
- ingin melakukan sanity check sebelum full automated test;
- ingin membandingkan kualitas jawaban model secara kualitatif;
- ingin menguji model yang sedang berjalan di `llama-server` tanpa menulis script baru.

## Ringkasan

Level test otomatis di project ini memakai 23 capability, 5 level, dan 2 test per level. Full run berarti:

```text
23 capability x 5 level x 2 test = 230 test per model
```

Untuk uji manual, jangan langsung menjalankan semua 230 prompt. Mulai dari subset prioritas:

1. `json_mode`
2. `structured_output`
3. `rag`
4. `tool_calling`
5. `task_planning`
6. `clarifying`
7. `code_execution`
8. `terminal`

Jika model lolos subset ini, lanjutkan capability lain atau jalankan automated test penuh.

Jika ingin mencakup semua 23 capability dengan jumlah prompt jauh lebih sedikit, gunakan dokumen kompresi:

- [ALL_CAPABILITIES_COMPRESSED_WEBUI_TESTING.md](ALL_CAPABILITIES_COMPRESSED_WEBUI_TESTING.md)

## Model dan Endpoint Saat Ini

Berdasarkan `model_specification_test/config.py`, model aktif saat dokumen ini dibuat:

```text
Model    : Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M
Endpoint : http://localhost:8080/v1
Web UI   : http://localhost:8080
Platform : llama.cpp
```

Jika model yang sedang berjalan berbeda, jalankan:

```bash
cd /home/infra/dcim_project/model_specification_test
python detect_models.py --update-config
```

## Menjalankan llama.cpp Web UI

`llama-server` menyediakan REST API dan web UI. Web UI aktif secara default pada server terbaru. Port default adalah `8080`, dan host default adalah `127.0.0.1`.

Contoh start server lokal:

```bash
llama-server \
  -m /path/to/model.gguf \
  --host 127.0.0.1 \
  --port 8080 \
  -c 8192 \
  -ngl auto
```

Jika diakses dari mesin lain dalam jaringan internal:

```bash
llama-server \
  -m /path/to/model.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  -c 8192 \
  -ngl auto
```

Buka browser:

```text
http://localhost:8080
```

Atau jika server ada di host lain:

```text
http://<ip-server>:8080
```

Catatan keamanan: jangan expose `llama-server` ke internet tanpa auth, firewall, dan segmentasi jaringan.

## Setting UI yang Disarankan

Gunakan setting yang konsisten supaya hasil manual bisa dibandingkan antar model:

| Setting | Nilai rekomendasi | Catatan |
|---|---:|---|
| Temperature | `0.3` | Lebih deterministik untuk evaluasi |
| Max tokens | `1024` atau lebih | Naikkan untuk Level 4-5 |
| Context size | `8192+` | Sesuaikan VRAM/RAM dan model |
| System prompt | kosong atau standar project | Jangan ubah di tengah run |
| New chat | per capability | Mengurangi kontaminasi context |

System prompt opsional:

```text
You are a DCIM operations assistant. Answer accurately, follow the requested format, and do not invent tool results. If a tool, file, terminal, web, or external system is required but unavailable, state the intended action and expected parameters.
```

## Batasan Manual Testing

Manual testing di web UI tidak selalu sama dengan automated test:

| Capability | Manual Web UI | Catatan |
|---|---|---|
| JSON Mode | Bisa | Validasi dengan JSON parser |
| Structured Output | Bisa | Cek format dan kelengkapan |
| RAG | Bisa simulasi | Paste konteks SOP ke chat |
| Vision | Bisa jika build/model support multimodal | Upload gambar dashboard/alert |
| Tool Calling | Bisa simulasi, atau real jika tools diaktifkan | Cek nama tool dan parameter |
| Terminal/File Ops | Simulasi default; real jika built-in tools aktif | Jangan aktifkan tools di environment tidak dipercaya |
| Web Search | Simulasi default | Butuh integrasi search nyata untuk hasil real-time |
| Streaming | Bisa diamati | Catat TTFT manual dengan stopwatch |
| Agent/Delegation/Skills | Simulasi | Nilai planning, routing, dan konsistensi |

Untuk menguji built-in tools `llama.cpp`, server dapat dijalankan dengan:

```bash
llama-server -m /path/to/model.gguf --host 127.0.0.1 --port 8080 --tools all
```

Gunakan hanya di mesin/lingkungan terpercaya, karena tool seperti file access dan shell command bisa berisiko.

## Rubrik Skor Manual

Gunakan skor `0.0` sampai `1.0` untuk setiap prompt:

| Skor | Label | Kriteria |
|---:|---|---|
| `1.00` | Perfect | Format benar, isi benar, tidak ada halusinasi penting |
| `0.75` | Good | Minor issue, tetapi tujuan test terpenuhi |
| `0.50` | Acceptable | Sebagian benar, ada kekurangan signifikan |
| `0.25` | Poor | Banyak salah, hanya sedikit elemen yang benar |
| `0.00` | Failed | Tidak menjawab kebutuhan test |

Level dianggap lolos jika rata-rata skor pada level tersebut minimal:

```text
0.60
```

Assessed level manual:

```text
Level tertinggi yang lolos secara berurutan dari Level 1.
```

Contoh:

| Level | Avg score | Status |
|---:|---:|---|
| 1 | 0.90 | Pass |
| 2 | 0.80 | Pass |
| 3 | 0.65 | Pass |
| 4 | 0.45 | Fail |
| 5 | skipped | Not tested |

Hasil:

```text
Assessed Level : Level 3 - Intermediate
Failure Level  : Level 4 - Expert
Recommendation : Pakai untuk workload sampai intermediate; hindari workflow expert tanpa guardrail.
```

## Template Pencatatan Manual

Salin template ini untuk setiap model:

```markdown
# Manual llama.cpp Web UI Test Result

Model:
GGUF quant:
Endpoint:
Tanggal:
Tester:
Temperature:
Max tokens:
Context size:

## Summary

| Capability | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 | Assessed Level | Catatan |
|---|---:|---:|---:|---:|---:|---|---|
| json_mode |  |  |  |  |  |  |  |
| structured_output |  |  |  |  |  |  |  |
| rag |  |  |  |  |  |  |  |
| tool_calling |  |  |  |  |  |  |  |
| task_planning |  |  |  |  |  |  |  |
| clarifying |  |  |  |  |  |  |  |
| code_execution |  |  |  |  |  |  |  |
| terminal |  |  |  |  |  |  |  |

## Detail

### Capability: json_mode

| Level | Prompt | Score | Pass/Fail | Catatan |
|---:|---|---:|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |
```

## Protokol Uji Manual

1. Start `llama-server`.
2. Buka `http://localhost:8080`.
3. Set parameter UI sesuai bagian "Setting UI yang Disarankan".
4. Buat chat baru untuk satu capability.
5. Kirim prompt Level 1.
6. Beri skor `0.0-1.0`.
7. Jika Level 1 pass, lanjut Level 2.
8. Stop pada level pertama yang fail, kecuali ingin eksplorasi tambahan.
9. Catat assessed level dan failure level.
10. Ulangi untuk capability berikutnya.

## Prompt Manual Prioritas

Prompt di bawah diambil dari definisi level test project dan disesuaikan agar enak digunakan di web UI.

### 1. JSON Mode

Level 1:

```text
Output server status sebagai JSON valid saja, tanpa markdown dan tanpa penjelasan:
hostname=srv-web-01, cpu=85, memory=72, status=warning
```

Lulus jika output valid JSON dan memiliki field `hostname`, `cpu`, `memory`, `status`.

Level 2:

```text
Output sebagai JSON valid saja:
server srv-db-01 dengan metrics {cpu: 90, memory: 88} dan anomalies [{type: memory_leak, severity: high}]
```

Lulus jika nested JSON benar dan field `server`, `metrics`, `anomalies` ada.

Level 3:

```text
Output JSON valid sesuai schema:
{
  "hostname": string,
  "metrics": {"cpu": number, "memory": number},
  "alerts": [{"type": string, "severity": string}]
}

Gunakan contoh data DCIM realistis.
```

Lulus jika schema dipatuhi dan JSON tetap valid.

Level 4:

```text
Generate JSON valid untuk 5 server dengan metrics lengkap. Setiap server wajib punya hostname, cpu, memory, disk, status, dan recommendations. Validasi semua field required di dalam output.
```

Lulus jika semua item lengkap, tidak ada komentar di luar JSON, dan struktur konsisten.

Level 5:

```text
Generate JSON configuration untuk monitoring system DCIM dengan 50+ fields, nested structures, arrays, alert routing, threshold policy, escalation policy, retention policy, dan conditional logic. Output JSON valid saja.
```

Lulus jika kompleks, valid, dan tidak berubah menjadi prose.

### 2. Structured Output

Level 1:

```text
Output daftar 3 server dalam format table dengan kolom: hostname, cpu, memory.
```

Level 2:

```text
Buat markdown table comparison 3 servers: hostname, cpu, memory, status, recommendation.
```

Level 3:

```text
Buat comprehensive report dengan sections: executive summary, detailed metrics table, trend analysis, action items.
```

Level 4:

```text
Buat dashboard report dengan: KPI summary, trend charts dalam ASCII, detailed tables, dan recommendations yang diprioritaskan.
```

Level 5:

```text
Buat dynamic incident report untuk 5 server. Jika severity critical, tampilkan incident command section, escalation matrix, SLA timer, action owner, rollback plan, dan post-incident review checklist. Jika tidak critical, tampilkan operational summary saja.
```

Lulus jika struktur mengikuti instruksi, mudah dibaca, dan tidak mencampur format secara kacau.

### 3. RAG Manual

Sebelum prompt, paste konteks SOP berikut ke chat:

```text
KONTEKS SOP CPU:
- Jika CPU > 90% selama lebih dari 5 menit, jalankan top process analysis.
- Cek apakah ada cron job, backup, atau ETL job yang sedang berjalan.
- Jika penyebabnya ETL terjadwal, jangan kill proses; pantau sampai selesai.
- Jika proses tidak dikenal memakai CPU tinggi, eskalasi ke tim platform.
- Jika CPU > 90% lebih dari 10 menit dan service terdampak, kirim alert critical.

KONTEKS SOP MEMORY:
- Memory leak ditandai penggunaan memory meningkat terus, GC sering, dan swap mulai aktif.
- Ambil heap/process snapshot sebelum restart.
- Restart service hanya setelah approval jika service production.
- Eskalasi ke tim aplikasi jika memory tidak turun setelah restart.

KONTEKS SOP DISK:
- Jika disk > 85%, cek file besar dan log rotation.
- Jika disk > 95%, hentikan job non-kritis dan eskalasi segera.
- Jangan hapus file database tanpa approval DBA.
```

Level 1:

```text
Berdasarkan SOP di atas, apa yang harus dilakukan jika CPU > 90%?
```

Level 2:

```text
Server srv-web-01 CPU 95% selama 7 menit. Apa yang harus dilakukan sesuai SOP?
```

Level 3:

```text
Berdasarkan semua SOP, buat checklist troubleshooting untuk server dengan CPU tinggi dan memory leak bersamaan.
```

Level 4:

```text
Bandingkan SOP CPU alert dan Disk alert. Apa persamaan dan perbedaan langkah eskalasinya?
```

Level 5:

```text
Berdasarkan semua SOP, buat decision tree troubleshooting server issues dalam format markdown.
```

Lulus jika jawaban memakai konteks yang diberikan, bukan jawaban umum.

### 4. Tool Calling

Jika tools nyata tidak tersedia di web UI, nilai kemampuan model menghasilkan rencana tool call. Minta model output JSON agar mudah dinilai.

System/user preface:

```text
Anggap tools berikut tersedia:
- get_server_metrics(hostname)
- check_logs(hostname, level, since)
- get_top_processes(hostname, sort_by, limit)
- send_alert(severity, hostname, message)

Untuk setiap instruksi, output JSON berisi ordered_tool_calls saja. Jangan menjalankan tool sungguhan.
```

Level 1:

```text
Cek CPU usage server srv-web-01.
```

Lulus jika memilih `get_server_metrics` dengan `hostname=srv-web-01`.

Level 2:

```text
Server srv-web-03 lambat, cek metrics dan logs.
```

Lulus jika memilih `get_server_metrics` dan `check_logs`.

Level 3:

```text
Server srv-db-02 high memory. Cek metrics, logs, dan top processes.
```

Lulus jika memilih tiga tool yang relevan dengan parameter hostname benar.

Level 4:

```text
Investigasi server srv-app-10: cek metrics -> jika CPU tinggi cek processes -> jika process aneh kill tidak tersedia, maka kirim alert.
```

Lulus jika model mengikuti urutan, sadar tool `kill` tidak tersedia, dan memilih alert sebagai fallback.

Level 5:

```text
Monitoring 5 server sekaligus: srv-web-01, srv-web-02, srv-db-01, srv-db-02, srv-app-01. Cek semua metrics, logs, processes. Server dengan CPU > 85% kirim alert critical.
```

Lulus jika rencana mencakup semua server, semua tool observasi, conditional alert, dan agregasi hasil.

### 5. Task Planning

Level 1:

```text
Buat rencana 3 langkah untuk troubleshooting CPU tinggi pada satu server.
```

Level 2:

```text
Buat rencana investigasi server lambat yang mencakup metrics, logs, proses, dan eskalasi jika perlu.
```

Level 3:

```text
Buat rencana troubleshooting untuk incident multi-domain: aplikasi lambat, database CPU tinggi, dan network latency naik.
```

Level 4:

```text
Buat adaptive incident response plan untuk outage production. Sertakan decision points, rollback criteria, komunikasi stakeholder, dan post-incident review.
```

Level 5:

```text
Buat strategic 90-day plan untuk meningkatkan reliability DCIM operations. Sertakan observability, automation, model evaluation, governance, security, dan success metrics.
```

Lulus jika planning makin matang di setiap level, bukan sekadar daftar generik.

### 6. Clarifying

Level 1:

```text
Server lambat. Ajukan pertanyaan klarifikasi yang perlu sebelum melakukan troubleshooting.
```

Level 2:

```text
Ada alert CPU tinggi. Ajukan maksimal 5 pertanyaan klarifikasi yang paling penting untuk menentukan prioritas.
```

Level 3:

```text
User berkata "semua aplikasi down". Ajukan pertanyaan klarifikasi, kelompokkan berdasarkan impact, scope, timeline, dan recent changes.
```

Level 4:

```text
Ada laporan intermittent latency di beberapa region, tetapi data belum lengkap. Ajukan pertanyaan klarifikasi dan jelaskan mengapa setiap pertanyaan penting.
```

Level 5:

```text
Kamu menerima incident ambigu: "DCIM tidak akurat dan beberapa workflow gagal". Buat strategi klarifikasi bertahap untuk menemukan scope, blast radius, root hypothesis, dan data yang harus dikumpulkan.
```

Lulus jika model bertanya sebelum mengambil kesimpulan.

### 7. Code Execution / Code Generation

Di web UI, nilai kode yang dihasilkan. Jika ingin memverifikasi, salin kode ke environment terpisah yang aman.

Level 1:

```text
Buat script Python print "Hello World".
```

Level 2:

```text
Buat script Python untuk monitoring CPU usage setiap 5 menit. Print timestamp dan CPU percentage. Jika CPU > 80%, print warning.
```

Level 3:

```text
Buat script Python yang monitoring CPU, memory, disk. Jika ada yang > threshold, kirim alert ke file log. Run setiap 10 menit via cron.
```

Level 4:

```text
Buat script Python comprehensive system monitor: CPU, memory, disk, network, processes. Generate report JSON. Auto-restart service jika crash.
```

Level 5:

```text
Buat distributed monitoring system: monitor multiple servers, aggregate data, detect anomalies, auto-remediate, generate dashboard. Jelaskan arsitektur dan berikan skeleton kode Python.
```

Lulus jika kode sintaksnya masuk akal, dependency disebutkan, ada error handling pada level tinggi, dan tidak memberikan command berbahaya tanpa guardrail.

### 8. Terminal

Jika shell tool tidak aktif, minta model memberikan command dan interpretasi expected output.

Level 1:

```text
Berikan command Linux untuk menjalankan uname -a dan jelaskan output pentingnya.
```

Level 2:

```text
Berikan command Linux untuk list top 10 processes by CPU usage dan jelaskan kolom pentingnya.
```

Level 3:

```text
Buat sequence command untuk check disk usage, find file lebih besar dari 1GB, lalu list sorted by size.
```

Level 4:

```text
Buat command/script untuk check apakah service nginx running. Jika tidak, start service. Jika start gagal, check logs dan report error.
```

Level 5:

```text
Buat rancangan terminal automation untuk monitor CPU, memory, disk, network secara paralel, aggregate result, generate daily report, dan send email alert. Sertakan command atau script skeleton.
```

Lulus jika command realistis, urutan benar, dan ada safety check.

## Smoke Test Cepat

Jika hanya punya waktu 10-15 menit, jalankan ini:

| Capability | Level | Prompt |
|---|---:|---|
| JSON Mode | 1 | Output server status sebagai JSON valid saja: hostname=srv-web-01, cpu=85, memory=72, status=warning |
| Structured Output | 2 | Buat markdown table comparison 3 servers: hostname, cpu, memory, status, recommendation |
| RAG | 2 | Server srv-web-01 CPU 95% selama 7 menit. Apa yang harus dilakukan sesuai SOP? |
| Tool Calling | 2 | Server srv-web-03 lambat, cek metrics dan logs |
| Task Planning | 3 | Buat rencana troubleshooting untuk incident multi-domain: aplikasi lambat, database CPU tinggi, dan network latency naik |

Interpretasi:

- Jika banyak gagal di Level 1-2, model belum layak untuk DCIM assistant.
- Jika lulus sampai Level 3, model layak untuk workload operasional terbatas.
- Jika lulus Level 4-5, lanjutkan automated full run untuk bukti kuantitatif.

## Setelah Manual Test

Manual test membantu membaca karakter model, tetapi hasil final tetap sebaiknya divalidasi dengan runner otomatis:

```bash
cd /home/infra/dcim_project/model_specification_test
python run_level_tests.py --model "Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M" --level all
```

Untuk subset prioritas:

```bash
python run_level_tests.py \
  --model "Qwen/Qwen3-VL-4B-Instruct-GGUF:Q4_K_M" \
  --capability json_mode structured_output rag tool_calling task_planning clarifying code_execution terminal \
  --level all
```

Output otomatis:

```text
results/level_reports/<model>_level_report.md
results/level_reports/<model>_level_report.json
```

## Referensi

- Project summary: `compact chat/compact_chat_level_model_summary.md`
- Level guide: `model_specification_test/LEVEL_TESTING_GUIDE.md`
- Level definitions: `model_specification_test/level_test_definitions.py`
- llama.cpp server docs: https://github.com/ggml-org/llama.cpp/tree/master/tools/server
