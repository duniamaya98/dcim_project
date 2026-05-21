# DCIM AI - Quick Reference Card

## 🚀 Quick Start

### Deploy Model
```bash
cd /home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0
ollama create dcim-ai -f Modelfile
ollama run dcim-ai
```

### Test Script
```bash
cd /home/infra/dcim_project
python3 test_dcim_ai.py interactive
```

---

## 💬 Top 10 Chat Examples

### 1. Deteksi Anomali
```
Apakah ada anomali yang terdeteksi? CPU: 8%, Memory: 23%, Disk I/O: 623766
```

### 2. Analisis Drift
```
Bagaimana kondisi drift pada metrik ini?
```

### 3. Root Cause
```
Apa yang menyebabkan masalah pada infrastruktur ini?
```

### 4. Rekomendasi
```
Rekomendasikan tindakan mitigasi untuk memory usage tinggi
```

### 5. Analisis Lengkap
```
Berikan analisis komprehensif dari kondisi infrastruktur ini
```

### 6. Pola Temporal
```
Apakah ada pola berulang dalam data ini?
```

### 7. Analisis Domain
```
Bagaimana kondisi domain komputasi (CPU)?
```

### 8. Estimasi Dampak
```
Seberapa besar dampak masalah ini terhadap sistem?
```

### 9. Summary
```
Ringkas kondisi sistem saat ini
```

### 10. Multi-Aspect
```
Analisis sistem ini: CPU 15%, Memory 80%, Disk I/O tinggi.
Apakah ada anomali? Apa penyebabnya? Apa rekomendasinya?
```

---

## 📊 Model Info

- **Model**: Qwen2.5-3B-Instruct + LoRA
- **Size**: 1.8GB (Q4_K_M quantized)
- **VRAM**: ~1.8GB
- **Training**: 3,816 instructions, 9 categories
- **Language**: Bahasa Indonesia
- **Context**: 512 tokens

---

## 🔧 API Usage

### Ollama
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "dcim-ai",
  "prompt": "Apakah ada anomali?",
  "stream": false
}'
```

### llama-server (OpenAI compatible)
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Apakah ada anomali?"}
    ],
    "temperature": 0.3
  }'
```

---

## 📁 Files

- **Model**: `/home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/dcim-ai-Q4_K_M.gguf`
- **Examples**: `/home/infra/dcim_project/DCIM_AI_CHAT_EXAMPLES.md`
- **Test Script**: `/home/infra/dcim_project/test_dcim_ai.py`
- **Documentation**: `/home/infra/dcim_project/(MT-023) Private LLM Platform.md`

---

## 🎯 Tips

1. **Sertakan nilai metrik** untuk hasil terbaik
2. **Gunakan Bahasa Indonesia**
3. **Temperature 0.3** untuk analisis teknis
4. **Spesifik dalam pertanyaan**
5. **Kombinasi multi-aspect** untuk analisis lengkap
