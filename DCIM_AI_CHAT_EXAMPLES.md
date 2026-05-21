# Contoh Chat Instruction untuk DCIM AI Model

Model DCIM AI telah di-training dengan 3,816 instruction samples yang mencakup 9 kategori analisis infrastruktur data center. Berikut adalah contoh pertanyaan yang bisa Anda coba.

## 📋 Kategori Instruction

| Kategori | Jumlah | Deskripsi |
|----------|--------|-----------|
| **Summary** | 683 | Ringkasan kondisi sistem secara umum |
| **Drift** | 723 | Analisis pergeseran distribusi data |
| **Temporal** | 701 | Analisis pola berulang dalam time series |
| **Anomaly** | 340 | Deteksi dan penjelasan anomali |
| **Domain** | 291 | Analisis per-domain (compute, memory, storage, network) |
| **Root Cause** | 329 | Identifikasi akar masalah |
| **Recommendation** | 316 | Saran tindakan mitigasi |
| **Full Analysis** | 312 | Analisis komprehensif end-to-end |
| **Impact** | 121 | Estimasi dampak masalah |

---

## 🎯 Contoh Chat Instruction

### 1. Deteksi Anomali

**Pertanyaan:**
```
Apakah ada anomali yang terdeteksi? Jelaskan.
```

**Contoh Input (metrics):**
```json
{
  "cpu_usage": 8.0,
  "memory_usage": 23.0,
  "disk_io": 623766.377,
  "net_rx": 245831.9693,
  "net_tx": 6487.865
}
```

**Expected Output:**
> Hasil deteksi: anomaly. Voting ensemble: 2/3 model mendeteksi anomali (IsolationForest=-1, LOF=1, OCSVM=-1). Severity: warning. Kondisi metrik: CPU usage rendah (8.0%); memory usage rendah (23.0%); disk I/O sangat tinggi (623766.4); network RX=245832.0, TX=6487.9.

---

### 2. Analisis Drift

**Pertanyaan:**
```
Bagaimana kondisi drift pada metrik ini?
```

**Expected Output:**
> Drift score: 1.53 (mild_drift). Fitur dengan drift tertinggi: memory_usage (z=2.73). Distribusi data mengalami pergeseran ringan dari baseline.

**Variasi Pertanyaan:**
- "Apakah ada pergeseran pola data?"
- "Jelaskan drift detection pada sistem ini"
- "Seberapa jauh data saat ini dari baseline?"

---

### 3. Root Cause Analysis

**Pertanyaan:**
```
Apa yang menyebabkan masalah pada infrastruktur ini?
```

**Expected Output:**
> Root cause analysis menunjukkan domain komputasi (CPU) sebagai penyebab utama dengan confidence 64%. Rantai kausal: komputasi (CPU) → memori (RAM). Domain lain yang berpotensi: memori (RAM) (36%).

**Variasi Pertanyaan:**
- "Apa akar penyebab anomali ini?"
- "Domain mana yang menjadi sumber masalah?"
- "Jelaskan rantai kausal dari masalah ini"

---

### 4. Rekomendasi Tindakan

**Pertanyaan:**
```
Rekomendasikan tindakan mitigasi.
```

**Expected Output:**
> Rekomendasi: Periksa memory leak, pertimbangkan restart service atau penambahan RAM. Monitor penggunaan memori secara berkala.

**Variasi Pertanyaan:**
- "Apa yang harus dilakukan untuk mengatasi masalah ini?"
- "Berikan saran perbaikan"
- "Langkah mitigasi apa yang diperlukan?"

---

### 5. Analisis Komprehensif

**Pertanyaan:**
```
Berikan analisis komprehensif dari kondisi infrastruktur ini.
```

**Expected Output:**
> Sistem mendeteksi **kondisi tidak biasa** dengan sinyal lemah yang menunjukkan potensi masalah pada domain memori (RAM). Distribusi data mengalami pergeseran ringan dari baseline.
>
> Kondisi metrik: CPU usage rendah (2.3%); memory usage rendah (23.9%); disk I/O sangat tinggi (623707.7); network RX=245663.9, TX=6385.7.
>
> Rekomendasi: Monitor trend memori, periksa aplikasi yang menggunakan RAM tinggi.

**Variasi Pertanyaan:**
- "Analisis lengkap kondisi server ini"
- "Berikan overview menyeluruh dari sistem"
- "Jelaskan secara detail kondisi infrastruktur saat ini"

---

### 6. Analisis Temporal

**Pertanyaan:**
```
Apakah ada pola berulang dalam data ini?
```

**Expected Output:**
> Dalam window 20 snapshot terakhir: rasio anomali 0%, rasio drift berat 0%. Tidak terdeteksi pola anomali berulang.

**Variasi Pertanyaan:**
- "Apakah masalah ini terjadi berulang?"
- "Bagaimana tren metrik dalam 20 snapshot terakhir?"
- "Apakah ada pola musiman atau siklik?"

---

### 7. Analisis Per-Domain

**Pertanyaan:**
```
Bagaimana kondisi domain komputasi (CPU)?
```

**Expected Output:**
> Domain compute: score 0.55 (normal). CPU usage rendah (2.2%), tidak ada aktivasi domain. Tidak terdeteksi masalah pada komputasi.

**Variasi Pertanyaan:**
- "Bagaimana kondisi memori (RAM)?"
- "Apakah ada masalah pada storage?"
- "Jelaskan kondisi network"
- "Domain mana yang paling bermasalah?"

---

### 8. Estimasi Dampak

**Pertanyaan:**
```
Seberapa besar dampak masalah ini terhadap sistem?
```

**Expected Output:**
> Severity: warning. Dampak: Potensi degradasi performa pada aplikasi yang memory-intensive. Risiko: Medium. Perlu monitoring lanjutan.

**Variasi Pertanyaan:**
- "Apakah masalah ini kritis?"
- "Seberapa urgent untuk ditangani?"
- "Apa konsekuensi jika tidak ditangani?"

---

### 9. Summary Kondisi

**Pertanyaan:**
```
Ringkas kondisi sistem saat ini.
```

**Expected Output:**
> Status: Normal dengan mild drift. Tidak ada anomali terdeteksi. Semua domain dalam kondisi stabil. Monitoring rutin tetap diperlukan.

**Variasi Pertanyaan:**
- "Berikan ringkasan singkat"
- "Apa kesimpulan dari analisis ini?"
- "Status sistem saat ini?"

---

## 🚀 Cara Mencoba dengan Ollama

### Setup Model
```bash
cd /home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0
ollama create dcim-ai -f Modelfile
```

### Test Chat Interaktif
```bash
ollama run dcim-ai
```

### Contoh Sesi Chat

```
>>> Apakah ada anomali yang terdeteksi? Jelaskan.

Hasil deteksi: anomaly. Voting ensemble: 2/3 model mendeteksi anomali...

>>> Apa yang menyebabkan masalah ini?

Root cause analysis menunjukkan domain komputasi (CPU) sebagai penyebab utama...

>>> Rekomendasikan tindakan mitigasi.

Rekomendasi: Periksa memory leak, pertimbangkan restart service...
```

---

## 🔧 Test dengan llama-server (API)

### Start Server
```bash
cd /home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0
llama-server -m dcim-ai-Q4_K_M.gguf -ngl 99 --port 8080 --host 0.0.0.0
```

### Test dengan curl
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "Kamu adalah DCIM AI Assistant, asisten cerdas untuk monitoring dan analisis infrastruktur data center."
      },
      {
        "role": "user",
        "content": "Apakah ada anomali yang terdeteksi? CPU: 8%, Memory: 23%, Disk I/O: 623766"
      }
    ],
    "temperature": 0.3,
    "max_tokens": 512
  }'
```

### Test dengan Python
```python
import requests

url = "http://localhost:8080/v1/chat/completions"
headers = {"Content-Type": "application/json"}

data = {
    "messages": [
        {
            "role": "system",
            "content": "Kamu adalah DCIM AI Assistant untuk analisis infrastruktur data center."
        },
        {
            "role": "user",
            "content": "Bagaimana kondisi drift pada metrik ini? CPU: 2%, Memory: 23%, Disk I/O: 623766"
        }
    ],
    "temperature": 0.3,
    "max_tokens": 512
}

response = requests.post(url, headers=headers, json=data)
print(response.json()["choices"][0]["message"]["content"])
```

---

## 📊 Tips Penggunaan

### 1. **Berikan Konteks Metrik**
Model di-training dengan format metrik spesifik. Sertakan nilai metrik untuk hasil terbaik:
```
CPU: X%, Memory: Y%, Disk I/O: Z, Network RX: A, TX: B
```

### 2. **Gunakan Bahasa Indonesia**
Model di-training dengan instruksi dan output dalam Bahasa Indonesia.

### 3. **Spesifik dalam Pertanyaan**
- ❌ "Bagaimana sistemnya?"
- ✅ "Apakah ada anomali yang terdeteksi pada metrik ini?"

### 4. **Kombinasi Pertanyaan**
Anda bisa menggabungkan beberapa aspek:
```
Analisis kondisi sistem ini: CPU 15%, Memory 80%, Disk I/O tinggi.
Apakah ada anomali? Apa penyebabnya? Apa rekomendasinya?
```

### 5. **Temperature Setting**
- `0.1-0.3`: Untuk analisis teknis (recommended)
- `0.5-0.7`: Untuk penjelasan lebih kreatif
- `0.8-1.0`: Untuk eksplorasi ide

---

## 🎓 Contoh Use Case Lengkap

### Scenario: Server dengan Memory Usage Tinggi

**Step 1: Deteksi**
```
User: Apakah ada anomali? CPU: 5%, Memory: 85%, Disk I/O: 500000, Net RX: 200000, TX: 5000

AI: Hasil deteksi: anomaly. Severity: warning. Memory usage sangat tinggi (85%),
potensi memory leak atau aplikasi memory-intensive.
```

**Step 2: Root Cause**
```
User: Apa penyebab masalah ini?

AI: Root cause analysis menunjukkan domain memori (RAM) sebagai penyebab utama
dengan confidence 78%. Tidak ada rantai kausal ke domain lain.
```

**Step 3: Rekomendasi**
```
User: Rekomendasikan tindakan mitigasi.

AI: Rekomendasi:
1. Identifikasi proses dengan memory usage tertinggi (top, htop)
2. Periksa memory leak pada aplikasi
3. Pertimbangkan restart service yang bermasalah
4. Jika persisten, tambahkan kapasitas RAM
5. Setup alert untuk memory usage > 80%
```

**Step 4: Monitoring**
```
User: Apakah ada pola berulang dalam 20 snapshot terakhir?

AI: Dalam window 20 snapshot terakhir: rasio anomali 15%, rasio drift berat 5%.
Terdeteksi pola anomali berulang pada domain memori, menunjukkan masalah sistemik.
```

---

## 📝 Catatan Penting

1. **Model Size**: Q4_K_M (1.8GB) - Optimal untuk production
2. **VRAM Required**: ~1.8GB untuk inference
3. **Context Length**: 512 tokens (default)
4. **Training Data**: 3,816 instruction samples dari 2,088 incident records
5. **Base Model**: Qwen2.5-3B-Instruct + LoRA fine-tuning

---

## 🔗 Referensi

- Model Path: `/home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/`
- Dataset: `/home/infra/rnd_rag-anything/dcim_ai/llm/datasets/dcim_instructions.jsonl`
- Dokumentasi: `/home/infra/dcim_project/(MT-023) Private LLM Platform.md`

---

**Model siap digunakan untuk analisis DCIM real-time!** 🚀
