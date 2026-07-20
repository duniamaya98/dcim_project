# DCIM AI Deployment Plan

Tanggal: 2026-06-05
Lokasi proyek: `/home/infra/dcim_project`
Status dokumen: Draft perencanaan deployment

## 1. Tujuan

Dokumen ini menjadi acuan perencanaan deployment DCIM AI Platform dari rancangan staging sampai rilis ke server production. Fokus utama dokumen ini adalah:

- Menentukan rancangan environment staging dan production.
- Menyusun alur build, validasi, deployment, observability, dan rollback.
- Memetakan komponen yang ada di direktori proyek saat ini ke kebutuhan deployment.
- Memastikan deployment dilakukan secara terkendali tanpa langsung mengubah konfigurasi yang sudah ada.

## 2. Scope

### In scope

- DCIM AI v2 RAG sebagai implementasi utama:
  - Path: `implementation/dcim_ai_v2_rag/`
  - API anomaly/inference: `implementation/dcim_ai_v2_rag/api/inference_service.py`
  - Model registry ML: `implementation/dcim_ai_v2_rag/registry/registry.json`
  - Model manager dan hot reload: `implementation/dcim_ai_v2_rag/inference/model_manager.py`
- Private LLM Platform dari implementasi v1:
  - Path: `implementation/dcim_ai_v1/`
  - Docker Compose awal: `implementation/dcim_ai_v1/docker-compose.yml`
  - LLM wrapper API: `implementation/dcim_ai_v1/llm/inference_api.py`
- Komponen pendukung:
  - PostgreSQL untuk data metrik, audit, dan registry.
  - Qdrant untuk vector database/RAG.
  - vLLM untuk serving LLM.
  - Prometheus endpoint dari FastAPI service.
  - Model artifact dan registry untuk promotion/rollback.

### Out of scope

- Perubahan source code aplikasi.
- Eksekusi deployment langsung ke staging atau production.
- Migrasi data production aktual.
- Penulisan file konfigurasi baru selain dokumen perencanaan ini.

## 3. Baseline Proyek Saat Ini

### Komponen aplikasi

| Komponen | Path | Fungsi | Catatan deployment |
| --- | --- | --- | --- |
| DCIM AI v2 RAG | `implementation/dcim_ai_v2_rag/` | Core analytics, anomaly detection, drift, domain scoring, correlation, RCA | Implementasi utama untuk API analytics |
| Inference API v2 | `implementation/dcim_ai_v2_rag/api/inference_service.py` | FastAPI endpoint `/`, `/predict`, `/metrics` | Membutuhkan model artifact, registry, dan dependency Python |
| Model registry ML | `implementation/dcim_ai_v2_rag/registry/registry.json` | Menentukan `current_production` model ML | Saat dokumen dibuat, `current_production` adalah `v1.4` |
| Model manager ML | `implementation/dcim_ai_v2_rag/inference/model_manager.py` | Load model dan hot reload registry setiap 10 detik | Deployment harus menjaga path registry dan artifacts konsisten |
| LLM wrapper API | `implementation/dcim_ai_v1/llm/inference_api.py` | FastAPI endpoint `/health` dan `/llm/inference` | Proxy ke vLLM OpenAI-compatible API |
| Docker Compose awal | `implementation/dcim_ai_v1/docker-compose.yml` | vLLM, LLM API, Qdrant, central service | Cocok sebagai referensi awal staging, perlu hardening untuk production |
| LLM pipeline | `implementation/dcim_ai_v2_rag/llm/` | Dataset generation, fine-tuning, registry LLM, export GGUF | Baseline LLM production: `dcim_assistant v1.0` menurut README |
| Benchmark | `implementation/dcim_benchmark/` | Latency, TTFT, context length, load test | Dipakai untuk acceptance test staging dan pre-production |

### Dependency utama

- OS: Ubuntu 20.04+ atau Ubuntu 24.04 LTS.
- Python: 3.10+ untuk v1, Python 3.12 tercatat pada dokumentasi LLM.
- GPU: NVIDIA RTX 3070 Ti 8 GB VRAM atau lebih baik; production disarankan GPU server dedicated.
- CUDA: 11.8+ atau 12.x sesuai driver.
- Database: PostgreSQL 14+ atau 16.
- Vector database: Qdrant.
- LLM engine: vLLM atau llama.cpp sesuai mode deployment model.
- Observability: Prometheus metrics endpoint, log collector, GPU metrics exporter.

### Endpoint yang perlu dijaga

| Service | Endpoint | Tujuan |
| --- | --- | --- |
| DCIM AI v2 API | `GET /` | Health check dan active model version |
| DCIM AI v2 API | `POST /predict` | Inference anomaly, drift, correlation, incident |
| DCIM AI v2 API | `GET /metrics` | Prometheus metrics |
| LLM wrapper API | `GET /health` | Health check LLM API wrapper |
| LLM wrapper API | `POST /llm/inference` | Unified LLM inference endpoint |
| vLLM | `/v1/chat/completions` | Backend OpenAI-compatible API untuk LLM wrapper |
| Qdrant | `6333` internal | Vector search/RAG |
| PostgreSQL | `5432` internal | Data metrik, audit, registry |

## 4. Prinsip Deployment

- Setiap perubahan harus masuk staging terlebih dahulu.
- Production hanya menerima artifact yang sudah lolos staging.
- Artifact aplikasi dan artifact model dipromosikan secara terpisah.
- Rollback harus tersedia untuk aplikasi, model ML, model LLM, dan database.
- Secret tidak boleh disimpan di repository atau image.
- Port database, Qdrant, dan vLLM tidak boleh dibuka langsung ke publik.
- Observability harus aktif sebelum traffic production diarahkan.
- Deployment harus repeatable, terdokumentasi, dan bisa diaudit.

## 5. Rancangan Environment

### 5.1 Development/local

Tujuan:

- Validasi perubahan cepat oleh developer.
- Unit test dan simulasi sederhana.
- Tidak menggunakan data production mentah.

Komponen minimal:

- Python virtual environment.
- PostgreSQL lokal atau database development.
- Qdrant lokal jika fitur RAG diuji.
- Mock vLLM atau vLLM kecil untuk pengujian endpoint.

### 5.2 Staging

Tujuan:

- Menyerupai production dengan skala lebih kecil.
- Menjalankan test integrasi, load test, model validation, dan rehearsal rollback.
- Menjadi gate sebelum production.

Rancangan staging:

```text
QA / Internal Client
        |
        v
Reverse Proxy / Internal LB
        |
        +--> DCIM AI API Staging
        |       - GET /
        |       - POST /predict
        |       - GET /metrics
        |
        +--> LLM API Wrapper Staging
                - GET /health
                - POST /llm/inference

Internal services:
        - vLLM staging GPU worker
        - Qdrant staging
        - PostgreSQL staging
        - Model artifact volume staging
        - Prometheus + Grafana staging
        - Log collector staging
```

Minimum staging requirement:

| Area | Rekomendasi |
| --- | --- |
| Compute | 1 server CPU untuk API, 1 GPU node jika LLM diuji penuh |
| GPU | Minimal 1 GPU 8 GB VRAM untuk LLM staging |
| RAM | Minimal 16 GB, rekomendasi 32 GB |
| Storage | Minimal 100 GB untuk model, logs, dataset staging |
| Network | Internal-only DB/Qdrant/vLLM, reverse proxy untuk API |
| Data | Sanitized production snapshot atau synthetic dataset |
| Secrets | `.env` staging atau secret manager, tidak commit ke git |

Data staging:

- Gunakan subset data production yang sudah disanitasi.
- Jika snapshot production tidak tersedia, gunakan dataset synthetic dari pipeline LLM dan sample metrics.
- Jangan menyalin password production ke staging.
- Pisahkan registry model staging dari production.

### 5.3 Production

Tujuan:

- Menjalankan layanan stabil untuk workload DCIM.
- Memastikan keamanan, monitoring, backup, dan rollback tersedia.
- Memisahkan control plane deployment dari data/model state.

Rancangan production:

```text
Internal DCIM System / Operator Dashboard
        |
        v
Production Load Balancer / Reverse Proxy / TLS
        |
        +--> DCIM AI API Production replica 1
        +--> DCIM AI API Production replica 2
        |
        +--> LLM API Wrapper Production
                |
                v
             vLLM GPU Worker Pool

Stateful services:
        - PostgreSQL production
        - Qdrant production
        - Model artifact storage
        - Registry storage
        - Backup storage

Observability:
        - Prometheus
        - Grafana
        - Log aggregation
        - Alertmanager
        - GPU metrics exporter
```

Production server layout yang disarankan:

```text
/opt/dcim-ai/
    releases/
        <release-id>/
    current -> releases/<active-release>

/etc/dcim-ai/
    app.env
    llm.env
    qdrant.env

/var/lib/dcim-ai/
    models/
    registry/
    qdrant/

/var/log/dcim-ai/
    api/
    llm/
    deployment/
```

Catatan penting:

- Source repository boleh berada di `/opt/dcim-ai/releases/<release-id>`, tetapi model artifact dan registry sebaiknya berada di persistent volume.
- Jika menjalankan kode v2 secara langsung, pastikan package import `dcim_ai.*` sesuai dengan layout runtime. Saat ini folder proyek bernama `dcim_ai_v2_rag`, sementara beberapa modul mengimpor `dcim_ai.*`. Production harus menetapkan layout package yang konsisten, misalnya melalui packaging, container image, atau symlink yang terdokumentasi.
- Current code ML registry memakai path relatif `dcim_ai/registry/registry.json` dan `dcim_ai/artifacts/models`. Deployment harus menjalankan service dari working directory yang benar atau menyediakan path tersebut melalui image/volume.

## 6. Strategi Artifact

### Artifact aplikasi

Rekomendasi:

- Build container image untuk setiap service.
- Tag image dengan format:
  - `dcim-ai-api:<git-sha>`
  - `dcim-ai-api:<semver>`
  - `dcim-llm-api:<git-sha>`
  - `dcim-llm-api:<semver>`
- Jangan build langsung di production.
- Image staging dan production harus identik; perbedaannya hanya environment config.

Jika container belum siap:

- Gunakan release directory berbasis git archive.
- Install dependency ke virtual environment per release.
- Symlink `/opt/dcim-ai/current` diarahkan ke release aktif.
- Gunakan systemd service untuk API dan LLM wrapper.

### Artifact model ML

Model ML production terdiri dari:

- `models.pkl`
- `pipeline.pkl`
- `baseline_stats.json`
- `metadata.json`
- Registry `registry.json`

Baseline saat dokumen dibuat:

- Registry ML: `implementation/dcim_ai_v2_rag/registry/registry.json`
- `current_production`: `v1.4`
- Available models: `v1.0` sampai `v1.10`
- Correlation strategy: `temporal_multi_domain_v1`

Prinsip deployment model ML:

- Model baru masuk registry sebagai candidate.
- Model hanya dipromosikan jika lolos evaluation gate.
- Promotion mengubah pointer `current_production`.
- Service mendukung hot reload sehingga rollback model dapat dilakukan dengan mengembalikan pointer registry ke versi sebelumnya.

### Artifact model LLM

Baseline menurut dokumentasi proyek:

- Nama: `dcim_assistant`
- Version: `v1.0`
- Base model: `Qwen/Qwen2.5-3B-Instruct`
- Adapter path: `implementation/dcim_ai_v2_rag/llm/models/v1.0/adapter/`

Mode serving yang dapat dipilih:

| Mode | Kapan dipakai | Catatan |
| --- | --- | --- |
| vLLM + LoRA adapter | Production throughput lebih tinggi | Cocok jika GPU cukup dan model dilayani via OpenAI-compatible API |
| llama.cpp + GGUF | Deployment lebih sederhana/hemat | Cocok untuk quantized model dan footprint lebih kecil |
| Mock vLLM | Staging ringan atau CI | Hanya untuk test kontrak API, bukan evaluasi kualitas |

## 7. Konfigurasi Per Environment

Konfigurasi wajib dipisahkan dari source code.

| Variable | Staging contoh | Production contoh | Keterangan |
| --- | --- | --- | --- |
| `APP_ENV` | `staging` | `production` | Identitas environment |
| `DATABASE_URL` | Secret staging | Secret production | PostgreSQL connection string |
| `QDRANT_URL` | `http://qdrant-staging:6333` | `http://qdrant-prod:6333` | Internal URL |
| `VLLM_API_URL` | `http://vllm-staging:8000/v1` | `http://vllm-prod:8000/v1` | Dipakai LLM wrapper |
| `LLM_API_URL` | `http://llm-api-staging:8080/llm/inference` | `http://llm-api-prod:8080/llm/inference` | Dipakai central service |
| `MODEL_REGISTRY_PATH` | Env/volume staging | Env/volume production | Perlu standardisasi karena code saat ini memakai path relatif |
| `MODELS_DIR` | Env/volume staging | Env/volume production | Perlu standardisasi karena code saat ini memakai path relatif |
| `LOG_LEVEL` | `INFO` atau `DEBUG` | `INFO` | Hindari debug di production |

Hardening yang disarankan sebelum production:

- Pindahkan path registry dan model artifact dari constant hard-coded ke environment variable.
- Pindahkan database credential dari dokumentasi ke secret manager.
- Tetapkan `.env.example` tanpa nilai secret asli.
- Pastikan image tidak membawa dataset sensitif.

## 8. Rancangan Network dan Security

### Public/internal exposure

| Komponen | Exposure |
| --- | --- |
| Reverse proxy/API gateway | Bisa diakses dari jaringan internal perusahaan atau public sesuai kebutuhan |
| DCIM AI API | Internal behind proxy |
| LLM API Wrapper | Internal behind proxy atau service mesh |
| vLLM | Internal only |
| Qdrant | Internal only |
| PostgreSQL | Internal only |
| Prometheus | Internal ops only |
| Grafana | Internal ops only dengan auth |

### Security checklist

- TLS aktif di reverse proxy.
- API production memakai authentication dan authorization yang sesuai integrasi DCIM.
- Secret dikelola melalui vault, Docker secret, Kubernetes secret, atau mekanisme setara.
- DB/Qdrant/vLLM tidak dipublish langsung ke internet.
- Backup terenkripsi.
- Log tidak menyimpan prompt/input sensitif secara penuh tanpa masking.
- Akses model artifact dibatasi ke service account.
- Audit trail deployment disimpan.

## 9. Observability

### Metrics aplikasi v2

Endpoint `GET /metrics` sudah menyediakan metric Prometheus berikut:

- `dcim_requests_total`
- `dcim_anomalies_total`
- `dcim_normals_total`
- `dcim_retrain_total`
- `dcim_inference_latency_seconds`
- `dcim_correlation_incidents_total`
- `dcim_critical_incidents_total`
- `dcim_multi_domain_incidents_total`
- `dcim_correlation_confidence`
- `dcim_domain_active_count`
- `dcim_temporal_anomaly_ratio`

### Metrics tambahan yang perlu disiapkan

- CPU, memory, disk, network host.
- GPU utilization, VRAM usage, temperature, power draw.
- vLLM latency, token throughput, queue length.
- Qdrant latency dan collection size.
- PostgreSQL connections, slow query, replication lag jika ada.
- HTTP 4xx/5xx rate per endpoint.

### Alert minimum

| Alert | Threshold awal |
| --- | --- |
| API health down | 2 consecutive checks gagal |
| P95 `/predict` latency | > 2 detik selama 5 menit |
| LLM P95 latency | > 10 detik selama 5 menit |
| Error rate | > 2 persen selama 5 menit |
| GPU VRAM | > 90 persen selama 10 menit |
| Disk usage | > 80 persen warning, > 90 persen critical |
| PostgreSQL unavailable | Segera critical |
| Registry/model artifact missing | Segera critical |

## 10. Pipeline CI/CD

### Branch dan tag policy

- `main`: kandidat production.
- `develop` atau branch integrasi: kandidat staging.
- Feature branch: perubahan individual.
- Release tag: `vYYYY.MM.DD.<build>` atau semantic version.

### Tahapan pipeline

```text
1. Source checkout
2. Static validation
3. Unit test
4. Integration test dengan dependency mock
5. Build image atau release artifact
6. Vulnerability scan
7. Push artifact ke registry
8. Deploy otomatis ke staging
9. Smoke test staging
10. Load/benchmark test staging
11. Manual approval
12. Backup production state
13. Deploy production canary/blue-green
14. Post-deployment validation
15. Monitor burn-in window
```

### Test gate minimum

- Unit test:
  - `implementation/dcim_ai_v2_rag/tests/`
  - `model_specification_test/tests/`
- Contract test:
  - `GET /`
  - `POST /predict`
  - `GET /metrics`
  - `GET /health`
  - `POST /llm/inference`
- Model validation:
  - Registry terbaca.
  - Artifact model active tersedia.
  - Inference memakai versi model yang diharapkan.
  - Drift/correlation response schema stabil.
- Performance:
  - Benchmark latency `/predict`.
  - Benchmark LLM TTFT dan throughput.
  - Load test burst sesuai perkiraan traffic.

## 11. Rencana Deployment Staging

### 11.1 Preparation

Checklist:

- [ ] Tentukan hostname staging.
- [ ] Siapkan server/API node.
- [ ] Siapkan GPU node jika LLM diuji penuh.
- [ ] Install NVIDIA driver, CUDA runtime, dan NVIDIA container toolkit jika memakai Docker.
- [ ] Siapkan PostgreSQL staging.
- [ ] Siapkan Qdrant staging.
- [ ] Siapkan secret staging.
- [ ] Siapkan storage model artifact staging.
- [ ] Siapkan Prometheus/Grafana/log collector.

### 11.2 Build artifact

Target:

- Build image atau release artifact dari commit yang sama.
- Simpan tag release dan git SHA.
- Simpan manifest deployment berisi:
  - Git SHA.
  - Image tag.
  - Model ML version.
  - Model LLM version.
  - Migration version.
  - Config version.

### 11.3 Deploy service staging

Urutan:

1. Deploy PostgreSQL staging dan restore/sediakan data staging.
2. Deploy Qdrant staging dan load collection RAG staging bila diperlukan.
3. Deploy vLLM staging.
4. Deploy LLM API wrapper staging.
5. Deploy DCIM AI API staging.
6. Hubungkan reverse proxy internal.
7. Aktifkan Prometheus scrape.

### 11.4 Smoke test staging

Test wajib:

```text
GET /                         -> status running dan model_version benar
GET /metrics                  -> Prometheus metrics tersedia
POST /predict                 -> response prediction, severity, drift, incident
GET /health LLM wrapper       -> status healthy
POST /llm/inference           -> response text dan usage
Qdrant health                 -> service reachable internal
PostgreSQL connection         -> service bisa membaca data/registry
```

Contoh payload `/predict`:

```json
{
  "cpu_usage": 80.0,
  "memory_usage": 75.0,
  "disk_io": 120.0,
  "net_rx": 1000.0,
  "net_tx": 800.0
}
```

### 11.5 Staging acceptance

Staging dianggap lolos jika:

- Semua smoke test berhasil.
- Tidak ada error kritikal pada log selama burn-in minimal 2 jam.
- Prometheus menerima metrics dari API.
- Grafana dashboard dasar tersedia.
- Model version di health response sesuai registry staging.
- Rollback rehearsal berhasil.
- Benchmark tidak melewati threshold yang disepakati.

## 12. Rencana Deployment Production

### 12.1 Production pre-check

Checklist sebelum deployment:

- [ ] Change request disetujui.
- [ ] Release note tersedia.
- [ ] Artifact yang akan dideploy sama dengan artifact staging.
- [ ] Staging acceptance sudah ditandatangani.
- [ ] Backup database production selesai dan tervalidasi.
- [ ] Backup registry dan model artifact selesai.
- [ ] Rollback plan sudah disiapkan.
- [ ] Maintenance window atau canary window disepakati.
- [ ] Monitoring dan alert aktif.
- [ ] On-call PIC tersedia.

### 12.2 Backup production

Backup minimum:

- PostgreSQL dump atau snapshot.
- Qdrant snapshot/backup collection.
- Model registry production.
- Active model artifacts.
- Reverse proxy config.
- Environment config yang aktif.

Backup harus punya:

- Timestamp.
- Release ID sebelum deployment.
- Lokasi backup.
- Hasil restore validation minimal untuk database atau snapshot metadata.

### 12.3 Production deployment strategy

Rekomendasi utama: blue-green atau canary.

Blue-green:

1. Environment `blue` tetap menerima traffic.
2. Deploy release baru ke `green`.
3. Jalankan smoke test internal pada `green`.
4. Alihkan traffic dari `blue` ke `green`.
5. Monitor burn-in.
6. Simpan `blue` sebagai rollback target sampai burn-in selesai.

Canary:

1. Deploy release baru ke sebagian kecil replica.
2. Arahkan 5-10 persen traffic internal ke canary.
3. Monitor latency, error, dan prediction consistency.
4. Naikkan ke 25 persen, 50 persen, lalu 100 persen jika stabil.
5. Rollback canary jika metric memburuk.

Jika hanya tersedia satu server:

- Gunakan release directory dan symlink atomic.
- Stop service singkat.
- Switch symlink ke release baru.
- Start service.
- Jalankan smoke test.
- Rollback dengan mengembalikan symlink ke release sebelumnya.

### 12.4 Urutan production deployment

1. Freeze release.
2. Ambil backup production.
3. Deploy dependency stateful bila ada perubahan terencana.
4. Deploy vLLM/model serving jika ada perubahan LLM serving.
5. Deploy LLM API wrapper.
6. Deploy DCIM AI API.
7. Jalankan health check internal.
8. Jalankan smoke test endpoint.
9. Alihkan traffic secara canary/blue-green.
10. Pantau burn-in minimal 30-60 menit.
11. Tandai release sebagai production active.
12. Simpan deployment report.

### 12.5 Production post-check

Checklist:

- [ ] `GET /` mengembalikan status running.
- [ ] `model_version` sesuai expected production registry.
- [ ] `/metrics` bisa di-scrape Prometheus.
- [ ] `/predict` berhasil dengan sample valid.
- [ ] LLM wrapper `/health` healthy.
- [ ] `/llm/inference` berhasil.
- [ ] Error rate stabil.
- [ ] Latency stabil.
- [ ] GPU memory stabil.
- [ ] Log tidak menunjukkan registry/model artifact missing.
- [ ] Alertmanager tidak menembakkan alert kritikal.

## 13. Model Promotion dan Rollback

### 13.1 ML model promotion

Alur promotion:

1. Train model candidate.
2. Simpan artifact ke model directory candidate.
3. Daftarkan metadata model.
4. Jalankan evaluation gate.
5. Deploy candidate ke staging.
6. Jalankan staging validation.
7. Promote registry production.
8. Service hot reload mengambil versi baru.
9. Monitor prediction quality.

Command referensi dari proyek:

```bash
python -m dcim_ai.registry.promote_model <version>
```

Catatan:

- Command tersebut mengubah registry dan metadata model.
- Jalankan hanya pada environment target.
- Backup registry sebelum promotion.
- Pastikan artifact version tersedia sebelum pointer `current_production` diganti.

### 13.2 ML model rollback

Rollback model ML:

1. Tentukan versi production sebelumnya.
2. Pastikan artifact versi sebelumnya masih tersedia.
3. Restore registry backup atau promote versi sebelumnya.
4. Tunggu hot reload service.
5. Verifikasi `GET /` mengembalikan model version yang benar.
6. Jalankan smoke test `/predict`.

### 13.3 LLM model promotion

Alur promotion LLM:

1. Candidate adapter/model masuk registry LLM.
2. Evaluasi kualitas jawaban domain DCIM.
3. Jalankan benchmark TTFT, throughput, context length.
4. Deploy ke staging vLLM atau llama.cpp.
5. Validasi `/llm/inference`.
6. Promote candidate menjadi active production model.
7. Restart atau reload model server sesuai engine.

### 13.4 LLM model rollback

Rollback LLM:

1. Kembalikan model serving ke adapter/GGUF sebelumnya.
2. Restart/reload vLLM atau llama.cpp.
3. Verifikasi `/health`.
4. Jalankan `/llm/inference` dengan prompt smoke test.
5. Pantau latency dan error.

## 14. Database dan Migration Plan

### Prinsip

- Migration harus idempotent jika memungkinkan.
- Migration harus punya rollback script atau restore path.
- Backup wajib sebelum migration production.
- Migration dijalankan sebelum aplikasi baru menerima traffic jika schema baru dibutuhkan.

### PostgreSQL

Table yang disebut dalam dokumentasi:

- `server_metrics`
- `anomaly_events`
- `model_registry`
- `llm_model_registry`

Checklist:

- [ ] Verifikasi koneksi DB dari API.
- [ ] Verifikasi user DB memiliki privilege minimal.
- [ ] Verifikasi index untuk query utama.
- [ ] Verifikasi backup dan restore.
- [ ] Verifikasi migration SQL jika ada perubahan schema.

### Qdrant

Checklist:

- [ ] Collection staging dan production dipisah.
- [ ] Snapshot collection tersedia sebelum deploy.
- [ ] Schema/vector size sesuai embedding model.
- [ ] Reindexing dilakukan di staging terlebih dahulu.

## 15. Operational Runbook

### Start/stop service

Jika menggunakan container:

```bash
docker compose up -d
docker compose ps
docker compose logs -f
```

Jika menggunakan systemd:

```bash
sudo systemctl start dcim-ai-api
sudo systemctl status dcim-ai-api
sudo journalctl -u dcim-ai-api -f
```

Nama service final perlu ditetapkan saat implementasi deployment.

### Health check

```bash
curl -fsS http://<dcim-ai-api>/ 
curl -fsS http://<dcim-ai-api>/metrics
curl -fsS http://<llm-api>/health
```

### Smoke test `/predict`

```bash
curl -fsS -X POST http://<dcim-ai-api>/predict \
  -H "Content-Type: application/json" \
  -d '{"cpu_usage":80.0,"memory_usage":75.0,"disk_io":120.0,"net_rx":1000.0,"net_tx":800.0}'
```

### Smoke test `/llm/inference`

```bash
curl -fsS -X POST http://<llm-api>/llm/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Jelaskan kondisi DCIM jika CPU dan memory meningkat bersamaan.","max_tokens":128,"temperature":0.2,"top_p":0.95}'
```

## 16. Rollback Plan

### Trigger rollback

Rollback dilakukan jika salah satu terjadi:

- API health check gagal.
- Error rate naik signifikan.
- Latency melewati threshold selama burn-in.
- Model artifact tidak bisa dimuat.
- Prediction response schema berubah tidak kompatibel.
- LLM wrapper gagal mencapai vLLM.
- Qdrant/PostgreSQL dependency tidak stabil.
- Alert kritikal muncul setelah deployment.

### Rollback aplikasi

Container:

1. Deploy ulang image tag sebelumnya.
2. Restart service.
3. Jalankan smoke test.
4. Monitor metrics.

Release directory:

1. Ubah symlink `current` ke release sebelumnya.
2. Restart service.
3. Jalankan smoke test.
4. Monitor metrics.

### Rollback database

Urutan:

1. Stop traffic aplikasi jika schema incompatible.
2. Restore backup atau jalankan down migration.
3. Verifikasi schema dan data.
4. Start aplikasi versi sebelumnya.
5. Jalankan smoke test.

### Rollback model

Gunakan prosedur pada bagian "Model Promotion dan Rollback".

## 17. Timeline Implementasi

Estimasi 4 minggu:

| Minggu | Fokus | Output |
| --- | --- | --- |
| 1 | Hardening repository dan deployment design | Final environment matrix, secret plan, packaging/container decision |
| 2 | Build staging | Staging server siap, dependency stateful siap, pipeline deploy staging |
| 3 | Validation dan observability | Smoke test, integration test, load test, dashboard, alert |
| 4 | Production readiness dan go-live | Backup/rollback rehearsal, approval, canary/blue-green production |

Detail kegiatan:

### Minggu 1: Readiness

- Tetapkan target runtime: Docker Compose, systemd, atau Kubernetes.
- Tetapkan layout package untuk `dcim_ai`.
- Externalize config yang masih hard-coded.
- Siapkan `.env.example` tanpa secret.
- Tetapkan artifact model storage.
- Tetapkan naming release dan tagging.

### Minggu 2: Staging build

- Provision staging.
- Deploy PostgreSQL dan Qdrant staging.
- Deploy vLLM dan LLM wrapper staging.
- Deploy DCIM AI API staging.
- Hubungkan metrics/logging.
- Jalankan smoke test awal.

### Minggu 3: Validation

- Jalankan unit/integration test.
- Jalankan benchmark latency dan load.
- Validasi model registry dan hot reload.
- Rehearsal rollback aplikasi.
- Rehearsal rollback model.
- Tuning alert threshold.

### Minggu 4: Production

- Review change request.
- Ambil backup production.
- Deploy production dengan canary/blue-green.
- Monitor burn-in.
- Dokumentasikan hasil deployment.
- Finalisasi runbook operasional.

## 18. RACI

| Aktivitas | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| Staging provisioning | Infra/DevOps | Infra Lead | Backend, Security | Project Owner |
| CI/CD pipeline | DevOps | Engineering Lead | Backend | QA |
| API deployment | Backend/DevOps | Engineering Lead | Infra | Project Owner |
| Model promotion | ML Engineer | AI Lead | Backend, QA | Project Owner |
| Database backup/migration | DBA/Infra | Infra Lead | Backend | Security |
| Security review | Security | Security Lead | Infra, Backend | Project Owner |
| Production approval | Project Owner | Project Owner | Engineering Lead, Infra Lead | All stakeholders |

## 19. Risk Register

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Package path `dcim_ai.*` tidak cocok dengan layout deployment | Service gagal start | Standardisasi packaging atau symlink dalam image/release |
| Registry/model path relatif tidak ditemukan | Model gagal load | Gunakan working directory konsisten atau externalize path ke env |
| Secret tertulis di dokumentasi lama | Risiko keamanan | Pindahkan ke secret manager dan rotasi credential sebelum production |
| vLLM membutuhkan GPU lebih besar dari kapasitas server | LLM latency tinggi atau OOM | Benchmark staging, pilih quantization/GGUF, scale GPU worker |
| Qdrant atau PostgreSQL terbuka ke network publik | Data exposure | Internal-only network, firewall, security group |
| Rollback database tidak diuji | Downtime panjang saat incident | Rehearsal restore di staging |
| Model baru menurunkan kualitas prediksi | False positive/negative naik | Evaluation gate, canary model, rollback registry |
| Log menyimpan prompt/data sensitif | Compliance issue | Masking, log sampling, retention policy |

## 20. Go/No-Go Criteria

### Go

- Staging acceptance lengkap.
- Backup production tervalidasi.
- Rollback rehearsal berhasil.
- Monitoring dan alert aktif.
- Security review selesai.
- Artifact release immutable.
- PIC deployment dan on-call tersedia.

### No-go

- Smoke test staging gagal.
- Model artifact production tidak lengkap.
- Backup tidak tersedia.
- Registry tidak bisa di-restore.
- Dependency utama belum dimonitor.
- Ada secret production di repository/image.
- Rollback belum diuji.

## 21. Deliverable Akhir

Deliverable deployment yang harus tersedia sebelum go-live:

- Deployment architecture final.
- Environment variable matrix.
- Secret management procedure.
- CI/CD pipeline definition.
- Staging deployment report.
- Staging test report.
- Production runbook.
- Backup dan restore procedure.
- Rollback procedure.
- Monitoring dashboard.
- Alert rule baseline.
- Production deployment report.

## 22. Checklist Ringkas

### Staging

- [ ] Server dan dependency siap.
- [ ] Secret staging siap.
- [ ] Artifact aplikasi ter-build.
- [ ] Artifact model tersedia.
- [ ] Registry staging valid.
- [ ] API staging healthy.
- [ ] LLM staging healthy.
- [ ] `/predict` smoke test berhasil.
- [ ] `/llm/inference` smoke test berhasil.
- [ ] Metrics masuk Prometheus.
- [ ] Rollback rehearsal berhasil.

### Production

- [ ] Approval production tersedia.
- [ ] Backup selesai.
- [ ] Artifact sama dengan staging.
- [ ] Registry/model production tervalidasi.
- [ ] Deployment strategy dipilih.
- [ ] Traffic switch/canary siap.
- [ ] Smoke test production berhasil.
- [ ] Monitoring stabil selama burn-in.
- [ ] Deployment report dibuat.
- [ ] Release lama disimpan untuk rollback.

## 23. Catatan Implementasi Berikutnya

Sebelum deployment production benar-benar dilakukan, rekomendasi teknis yang perlu ditutup:

1. Buat Dockerfile production untuk DCIM AI API v2 jika container dipilih.
2. Buat Dockerfile production untuk LLM API wrapper jika belum final.
3. Externalize `REGISTRY_PATH` dan `MODELS_DIR`.
4. Rapikan layout package agar import `dcim_ai.*` konsisten.
5. Buat `.env.example` tanpa secret.
6. Buat health check dan readiness check yang eksplisit untuk dependency.
7. Tambahkan deployment manifest per release.
8. Tetapkan dashboard Grafana baseline.
9. Jalankan benchmark staging sebelum production approval.

