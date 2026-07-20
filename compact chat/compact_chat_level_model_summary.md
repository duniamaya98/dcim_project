# Compact Chat Summary

## Konteks Proyek

- Direktori kerja: `/home/infra/dcim_project`
- Fokus utama: `model_specification_test/`
- Tujuan: membuat sistem pengujian capability model LLM berbasis level, bukan hanya satu kali test per capability.
- Total capability: 23 capability.
- Level penilaian:
  - Level 1: Basic
  - Level 2: Medium
  - Level 3: Intermediate
  - Level 4: Expert
  - Level 5: Master

## Perubahan yang Sudah Dilakukan

### `model_specification_test/level_based_testing.py`

Error awal:

```text
TypeError: '<' not supported between instances of 'TestLevel' and 'TestLevel'
```

Penyebab: `TestLevel` memakai `Enum`, sehingga tidak bisa dibandingkan atau di-sort langsung.

Perbaikan: `Enum` diganti menjadi `IntEnum`.

### `model_specification_test/level_test_definitions.py`

- `TestLevel` diganti dari `Enum` ke `IntEnum`.
- Label level diselaraskan menjadi:
  - `Basic`
  - `Medium`
  - `Intermediate`
  - `Expert`
  - `Master`
- Terdeteksi 23 capability.
- Masing-masing capability punya 5 level.
- Masing-masing level punya 2 test.
- Full run berarti `23 x 5 x 2 = 230` test per model.

### `model_specification_test/run_level_tests.py`

- Ditambahkan `LEVEL_PASS_THRESHOLD = 0.60`.
- Ditambahkan helper:
  - `format_level_badge(level_value)`
  - `recommendation_for_level(level_value)`
- Report sekarang menampilkan:
  - `Assessed Level`
  - `Failure Level`
  - `Recommendation`
  - `Level Distribution`
  - `Level 0 - Not Qualified`
- Ditambahkan fallback generic executor untuk modul test yang belum punya `run_single_test`.
- Dengan fallback ini, 23 capability bisa dijalankan tanpa harus menambahkan `run_single_test` manual ke semua file test.
- Fallback executor menilai berdasarkan field seperti:
  - `expected_keywords`
  - `expected_tool`
  - `expected_tools`
  - `expected_params`
  - `expected_fields`
  - `expected_format`
  - `expected_behavior`
  - `expected_context`
  - `expected_reasoning`
  - `language`
- Streaming punya jalur khusus dengan `stream=True`.
- Untuk `json_mode` dan `structured_output`, runner mencoba `response_format={"type":"json_object"}` lalu retry tanpa `response_format` jika server tidak support.

### `model_specification_test/LEVEL_TESTING_GUIDE.md`

- Dokumentasi diperbarui agar sesuai level baru.
- Ditambahkan instruksi smoke test dan full run.
- Dijelaskan bahwa hasil lama satu kali test tidak cukup untuk level assessment akurat.

## Validasi yang Sudah Dilakukan

```bash
python3 -m py_compile model_specification_test/run_level_tests.py model_specification_test/level_test_definitions.py
```

Hasil: berhasil.

Dry-run internal memastikan:

- 23 capability terdeteksi.
- Label level: `['Basic', 'Medium', 'Intermediate', 'Expert', 'Master']`.
- Semua capability punya 2 test di tiap level.
- `format_level_badge(0)` aman dan menghasilkan `Level 0 - Not Qualified`.

## Catatan Git dan Sandbox

File-file ini muncul sebagai untracked di git:

```text
?? model_specification_test/LEVEL_TESTING_GUIDE.md
?? model_specification_test/level_test_definitions.py
?? model_specification_test/run_level_tests.py
```

Sandbox beberapa kali gagal dengan:

```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

Karena itu beberapa operasi baca/tulis dilakukan dengan eskalasi.

## Cara Menjalankan Level Test

Masuk ke direktori test:

```bash
cd ~/dcim_project/model_specification_test
```

Smoke test cepat:

```bash
python run_level_tests.py --model "model_name" --capability json_mode --level 1
```

Capability prioritas:

```bash
python run_level_tests.py --model "model_name" --capability tool_calling rag terminal json_mode --level all
```

Full run semua capability:

```bash
python run_level_tests.py --model "model_name" --level all
```

Output:

```text
results/level_reports/<model>_level_report.md
results/level_reports/<model>_level_report.json
```

## Memeriksa Model yang Tersedia

Ada script:

```bash
cd ~/dcim_project/model_specification_test
python detect_models.py
```

Output JSON:

```bash
python detect_models.py --json
```

Auto-update config:

```bash
python detect_models.py --update-config
```

Dari `config.py` saat dibaca, model aktif/terdeteksi adalah:

```text
unsloth/gpt-oss-20b-GGUF:UD-Q4_K_XL
```

Endpoint:

```text
http://localhost:8080/v1
```

`DEFAULT_MODEL` mengarah ke model tersebut.

## Error Model Tidak Ada di Config

User sempat menjalankan:

```bash
python run_level_tests.py --model "unsloth/gemma-4-12b-it-GGUF:UD-Q4_K_XL" --level all
```

Error:

```text
Error: Model 'unsloth/gemma-4-12b-it-GGUF:UD-Q4_K_XL' not found in configuration
Available models: [...]
```

Penjelasan:

- Nama Gemma itu tidak ada di `MODELS` pada `config.py` saat itu.
- Report Gemma lama kemungkinan hasil pengujian sebelumnya.
- Kalau Gemma sedang running, jalankan:

```bash
python detect_models.py --update-config
```

Kalau tidak, pakai model yang tersedia:

```bash
python run_level_tests.py --model "unsloth/gpt-oss-20b-GGUF:UD-Q4_K_XL" --level all
```

Atau cukup:

```bash
python run_level_tests.py --level all
```

## Open Tabs Terakhir

- `model_specification_test/results/level_reports/unsloth_gemma-4-12b-it-GGUF_UD-Q4_K_XL_level_report.md`
- `model_specification_test/results/level_reports/Qwen_Qwen3-VL-4B-Instruct-GGUF_Q4_K_M_level_report.md`
- `model_specification_test/results/model_recommendations.md`
- `Baseline Query Database .md`
