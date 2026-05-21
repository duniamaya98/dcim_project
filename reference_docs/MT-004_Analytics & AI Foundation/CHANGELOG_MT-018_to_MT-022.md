# CHANGELOG — MT-018 s.d MT-022 (Analytics & AI Foundation)

> **Cakupan:** Penyesuaian dokumentasi MT-018, MT-019, MT-020, MT-021, MT-022 agar selaras dengan tiga use case Analytics & AI Engine: UC1 Predictive Failure Alerting, UC2 Capacity Optimization, UC3 Energy/PUE Drift.
> **Sifat:** Semua perubahan bersifat **addendum non-destruktif**. Bagian asli setiap dokumen tetap dipertahankan sebagai jejak audit. Tidak ada breaking change pada deployment yang sudah berjalan.
> **Tanggal:** 20 Mei 2026
> **Author:** DCIM AI Team
> **Versi paket:** v1.2.0

---

## Ringkasan Tujuan Penyesuaian

| UC | Goal Use Case Doc | Fondasi yang Dibutuhkan |
| --- | --- | --- |
| UC1 | Alert kegagalan 24–48 jam sebelum failure aktual | Forecasting + supervised labeling + predictive RCA + asset criticality |
| UC2 | Rekomendasi konsolidasi dengan penghematan ≥10%/kuartal | Clustering + capacity state + NetBox integration + capacity reasoning |
| UC3 | Anomali energi >5% terdeteksi ≤15 menit | Streaming ingestion + power/cooling domain + Isolation Forest + contextual alert |

## Prinsip Perubahan

1. **Non-destruktif** — semua dokumen lama ditambah section "Addendum v1.2.0", bukan diubah isinya.
2. **Backward compatible** — feature lama (single ensemble anomaly, single window 5 menit, single-domain registry) tetap berjalan tanpa konfigurasi tambahan.
3. **Opt-in** — kapabilitas baru hanya aktif bila profil/feature group/domain barunya dikonfigurasi.
4. **Konsisten lintas MT** — schema `AssetContext`, causal topology, dan inference contract dipakai sebagai sumber kebenaran tunggal lintas dokumen.

---

## Perubahan per Dokumen

### MT-018 — Traditional Machine Learning Model
**File:** `(MT-018) Traditional Machine Learning Model.md`
**Versi:** 1.1.2 → 1.2.0
**Section baru:** §11. Addendum v1.2.0

| Sub | Perubahan | UC |
| --- | --- | --- |
| 11.2 | Perluasan feature scope: `server_health`, `power_metrics`, `environment_metrics`, `capacity_metrics` | UC1, UC2, UC3 |
| 11.3 | Generalisasi data source via `MetricSource` (ServerMetricsSource / PowerMetricsSource / EnvironmentMetricsSource / NetBoxAssetSource) | UC2, UC3 |
| 11.4 | Forecasting profile baru (Prophet/XGBoost baseline → LSTM/TFT advanced) dengan output `failure_probability_24h/48h` | UC1 |
| 11.5 | Tabel `failure_events` untuk supervised labeling | UC1 |
| 11.6 | Strategi imputation & noise handling (forward-fill, interpolation, median, drop + flagging) | UC3 |
| 11.7 | Garansi backward compatibility (semua opt-in) | semua |
| 11.8 | Mapping addendum → UC | semua |

### MT-019 — Anomaly Detection Framework
**File:** `(MT-019) Anomaly Detection Framework.md`
**Section baru:** §6. Addendum v1.2.0

| Sub | Perubahan | UC |
| --- | --- | --- |
| 6.2 | Multi-model registry: field `type`, `domain`, `inference_mode`, `data_contract_version`; struktur `current_production` per type | UC1, UC2, UC3 |
| 6.3 | Inference contract `InferenceResult` standar lintas modul (model_id, model_type, severity, confidence, evidence, forecast_horizon_h) | semua |
| 6.4 | Streaming inference adapter (MQTT/Kafka), windowed 1m/5m/15m, latency target ≤15 menit | UC3 |
| 6.5 | Distribution drift tambahan: PSI & Kolmogorov-Smirnov untuk window 90 hari | UC2 |
| 6.6 | `DriftWatcher` runtime eksplisit + Prometheus metrics (`dcim_drift_score`, `dcim_drift_severe_total`, `dcim_retrain_triggered_total`) | semua |
| 6.7 | Mapping addendum → UC | semua |

### MT-020 — Cross-Domain Correlation Engine
**File:** `(MT-020) Cross-Domain Correlation Engine.md`
**Section baru:** §6. Addendum v1.2.0

| Sub | Perubahan | UC |
| --- | --- | --- |
| 6.2 | `DOMAIN_FEATURE_MAP` diperluas dengan `power`, `cooling`, `hardware` (aktif bila feature group tersedia) | UC1, UC3 |
| 6.3 | `CapacityState` baru: utilization_p50/p95, headroom, occupancy, trend_30d, underutilized, saturating | UC2 |
| 6.4 | `AssetContextResolver` & `AssetContext` (site, rack, zone, criticality, role, upstream_pdu/ups) — sumber kebenaran tunggal lintas MT | semua |
| 6.5 | Multi-resolution window: realtime / incident / predictive / capacity (1m s.d 90d) | semua |
| 6.6 | Domain criticality weighting (power=1.5, cooling=1.4, dst.) untuk severity multi-domain | UC1, UC3 |
| 6.7 | Causal topology default diperluas dengan edge dari power/cooling/hardware | UC1, UC3 |
| 6.8 | Mapping addendum → UC | semua |

### MT-021 — Model Training & Evaluation Lifecycle
**File:** `(MT-021) Model Training & Evaluation Lifecycle Engine.md`
**Section baru:** §7. Addendum v1.2.0

| Sub | Perubahan | UC |
| --- | --- | --- |
| 7.2 | `TrainingProfile` multi-task: `anomaly` (existing), `forecast`, `forecast_advanced`, `clustering`, `energy_anomaly` | semua |
| 7.3 | Evaluation metric catalog: MAPE, RMSE, coverage_95, failure_recall_24h, failure_precision_24h, silhouette, davies_bouldin, detection_latency_p95, FPR | semua |
| 7.4 | `TrainingSchedule` (cron + drift_trigger + on_demand) dengan default per profil | semua |
| 7.5 | Data window strategy: rolling_30m / rolling_7d / rolling_30d / rolling_90d / failure_event_centered | semua |
| 7.6 | Reproducibility diperketat: dataset_snapshot.sha256, random_seed, code_revision di metadata | semua |
| 7.7 | Promotion gatekeeper diperluas per profil (`mape_safe`, `coverage_safe`, `failure_recall_safe`, `silhouette_safe`, `latency_safe`, `fpr_safe`) | semua |
| 7.8 | Mapping addendum → UC | semua |

### MT-022 — Root Cause Analysis Engine
**File:** `(MT-022) Root Cause Analysis Engine .md`
**Section baru:** §6. Addendum v1.2.0

| Sub | Perubahan | UC |
| --- | --- | --- |
| 6.2 | Causal topology default selaras dengan MT-020 §6.7 (power, cooling, hardware sebagai possible root domain) | UC1, UC3 |
| 6.3 | `RCAMode` (REACTIVE / FORWARD / HYBRID) — predictive RCA terhadap output forecast | UC1 |
| 6.4 | `CapacityRecommendation` sebagai modul reasoning terpisah (clustering + bin-packing + LLM narrative) | UC2 |
| 6.5 | Asset context enrichment di `RootCauseResult` & `CapacityRecommendation` | semua |
| 6.6 | LLM contract standar: prompt template fixed, output JSON ({summary, impact, actions}) | semua |
| 6.7 | Governance flags baru: `forward_low_confidence`, `cross_domain_power_cooling`, `asset_context_missing` | UC1, UC3 |
| 6.8 | Mapping addendum → UC | semua |

---

## Kontrak Lintas-MT (Cross-Cutting Contracts)

Beberapa kontrak menjadi sumber kebenaran tunggal yang dirujuk di banyak MT. Disarankan diekstrak ke `data_contract.md` terpisah pada iterasi berikutnya.

| Kontrak | Definisi di | Dipakai di |
| --- | --- | --- |
| `MetricSource` | MT-018 §11.3 | MT-019 (loader inference), MT-021 (loader training) |
| `InferenceResult` | MT-019 §6.3 | MT-022 (input RCA), MT-023 (input LLM) |
| `AssetContext` | MT-020 §6.4 | MT-019 (enrichment alert), MT-022 (enrichment RCA), MT-023 (LLM prompt) |
| `CapacityState` | MT-020 §6.3 | MT-022 §6.4 (CapacityRecommendation) |
| `RootCauseResult` (extended) | MT-022 §6.3, §6.5 | MT-023 (LLM input), Dashboard, Incident Mgmt |
| `CapacityRecommendation` | MT-022 §6.4 | MT-023 (LLM narasi), Dashboard |
| Causal topology default | MT-020 §6.7 ↔ MT-022 §6.2 | MT-022 (chain reconstruction) |

---

## Mapping Addendum → Use Case

| UC | MT-018 | MT-019 | MT-020 | MT-021 | MT-022 |
| --- | --- | --- | --- | --- | --- |
| **UC1** Predictive Failure | 11.2, 11.4, 11.5, 11.6 | 6.2, 6.3, 6.6 | 6.2, 6.4, 6.5, 6.6, 6.7 | 7.2, 7.3, 7.5, 7.7 | 6.2, 6.3, 6.5, 6.6, 6.7 |
| **UC2** Capacity Optimization | 11.2, 11.3 | 6.2, 6.5, 6.6 | 6.3, 6.4, 6.5 | 7.2, 7.3, 7.5, 7.7 | 6.4, 6.5, 6.6 |
| **UC3** Energy/PUE Drift | 11.2, 11.3, 11.6 | 6.2, 6.4, 6.6 | 6.2, 6.4, 6.5, 6.6, 6.7 | 7.2, 7.3, 7.4, 7.7 | 6.2, 6.5, 6.6, 6.7 |

---

## Implementasi Berikutnya (Tindak Lanjut Kode)

Penyesuaian dokumentasi di atas perlu diiringi perubahan repo `dcim_ai_v2_rag/`. Daftar ini sebagai panduan, bukan bagian dari changelog itu sendiri.

| Modul Repo | Perubahan | Mengikuti |
| --- | --- | --- |
| `dcim_ai/features/` | Tambah loader `MetricSource` + variannya | MT-018 §11.3 |
| `dcim_ai/training/` | Tambah `TrainingProfile`, scheduler, evaluation catalog | MT-021 §7.2–7.7 |
| `dcim_ai/registry/` | Skema multi-model + `inference_mode` + `data_contract_version` | MT-019 §6.2 |
| `dcim_ai/inference/` | `InferenceResult` standar + `streaming_adapter.py` | MT-019 §6.3, §6.4 |
| `dcim_ai/domain/` | `DOMAIN_FEATURE_MAP` diperluas + criticality weights | MT-020 §6.2, §6.6 |
| `dcim_ai/correlation/` | Multi-resolution buffer + `AssetContextResolver` | MT-020 §6.4, §6.5 |
| `dcim_ai/root_cause/` | `RCAMode`, `CapacityRecommendation`, governance flags | MT-022 §6.3, §6.4, §6.7 |
| `dcim_ai/llm/` | Prompt template fixed + output JSON validator | MT-022 §6.6, MT-023 |
| Schema DB | `failure_events`, `power_metrics`, `environment_metrics`, `inference_results` | MT-018 §11.5, UC3 todo |

---

## Riwayat Versi Paket Addendum

| Tanggal | Versi | Author | Catatan |
| --- | --- | --- | --- |
| 20/05/2026 | 1.2.0 | DCIM AI Team | Penyesuaian awal MT-018 s.d MT-022 untuk UC1/UC2/UC3 |
| 20/05/2026 | 1.2.0-impl-1 | DCIM AI Team | Implementasi fondasi: `dcim_ai/contracts/`, `dcim_ai/domain/asset_resolver.py`, `dcim_ai/core/metric_sources.py`, extension `domain_config.py` & `model_registry.py`, SQL migration `2026_05_20_v1_2_0_multi_model.sql`. 31 unit test pass. |
| 20/05/2026 | 1.2.0-impl-2 | DCIM AI Team | Implementasi RCA FORWARD & HYBRID mode (MT-022 §6.3): extension `rca_models.py` dengan field `mode`, `forecast_horizon_h`, `forecast_confidence`, `asset_context`, `governance`; tambah `RCAEngine.analyze_forward()` dan `analyze_hybrid()`; governance flag `forward_low_confidence` otomatis. 11 unit test pass (test_rca_forward). Backward compatible: `analyze()` lama tetap default `mode='reactive'`. |
| 20/05/2026 | 1.2.0-impl-3 | DCIM AI Team | Implementasi Asset Enricher (MT-019 §6.3, MT-022 §6.5): module baru `dcim_ai/inference/asset_enricher.py` dengan `AssetEnricher.enrich_inference()`, `enrich_rca()`, `enrich_capacity()`; singleton `get_default_enricher()` / `set_default_enricher()`; auto-set governance flag `asset_context_missing` (asset belum diregistrasi) dan `cross_domain_power_cooling` (root_domain ∈ {power,cooling} & impact > 1 domain). Best-effort, idempotent. 14 unit test pass (test_asset_enricher). Total kumulatif: 56 unit test pass. |
| 20/05/2026 | 1.2.0-impl-4 | DCIM AI Team | Implementasi LLM RCA prompt/output contract (MT-022 §6.6): module baru `dcim_ai/llm/rca_prompt_contract.py` dengan fixed system prompt, `build_rca_user_prompt()`, `build_rca_chat_messages()`, `build_ollama_options()`, strict validator `validate_rca_llm_response()`, dan dataclass `RCAAlertNarrative` / `LLMValidationResult`. Output dipaksa schema JSON persis `summary`, `impact`, `actions`; key ekstra ditolak. 9 unit test pass (test_llm_rca_prompt_contract). Total kumulatif: 65 unit test pass. |
| 20/05/2026 | 1.2.0-env-1 | DCIM AI Team | Migrasi virtual environment runtime dari `/home/infra/rnd_rag-anything/ragavenv` ke `/home/infra/dcim_project/ragavenv`; script/shebang dan `pyvenv.cfg` venv hasil copy sudah diarahkan ke path baru; `.gitignore` ditambah `ragavenv/` agar dependency besar tidak masuk source control; package `PyYAML` diverifikasi ulang setelah copy. Validasi: Python 3.12.3, `numpy 2.2.6`, `pip 26.1.1` dari path baru. Cumulative test MT-018..MT-022: 65 unit test pass. |
