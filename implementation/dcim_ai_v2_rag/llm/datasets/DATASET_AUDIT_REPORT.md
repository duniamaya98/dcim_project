# Dataset Quality Audit Report
> **Tanggal:** 21 Juli 2026

## Ringkasan Eksekusi Fase 1 (T1.2)
Telah dilakukan audit otomatis pada file dataset fine-tuning:
1. `dcim_instructions.jsonl` (3,816 baris)
2. `dcim_instructions_enhanced.jsonl` (3,816 baris)

### 🚨 Temuan Kritis
- **Duplikasi Instruksi Ekstrem (98.8%)**: Hanya terdapat **44** `instruction` unik dari total 3,816 baris. 
  Contoh instruksi yang diulang >500 kali: 
  - *"Apakah ada pola berulang dalam data ini?"*
  - *"Rekomendasikan tindakan mitigasi."*
- **Output Terlalu Pendek**: Rata-rata panjang kolom `output` hanya 195 karakter. Ini akan merusak kemampuan *reasoning* LLM jika dilatih langsung (LLM akan terbiasa menjawab dengan 1 kalimat pendek).
- **Variasi Input Rendah**: Nilai metrik (seperti `cpu_usage: 2.2` vs `cpu_usage: 1.8`) berubah, tetapi struktur kalimat input dan output hampir 100% homogen.

### ⚠️ Risiko jika dilatih tanpa perbaikan:
1. **Catastrophic Overfitting**: LLM akan menghafal struktur kalimat kaku ini dan kehilangan kemampuan *instruction-following* umum.
2. **Robotic Responses**: Model tidak akan bisa menjelaskan Root Cause Analysis (RCA) secara naratif yang baik.

## 🛠️ Action Items Selanjutnya (T1.1 & T1.3)
1. Lakukan deduplikasi berdasar `instruction` (batasi maksimal 50 variasi per instruksi).
2. Lakukan *Augmentasi Prompt* menggunakan variasi natural language.
3. Pisahkan dataset bersih menjadi `train` (70%), `validation` (15%), dan `test` (15%).