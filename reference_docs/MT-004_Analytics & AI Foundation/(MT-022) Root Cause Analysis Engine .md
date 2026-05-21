# (MT-022) Root Cause Analysis Engine 

# 1. Root Cause Data Modeling & Contract Layer

## Objective

Menyediakan kontrak data (data contract) yang konsisten, serializable, dan production-safe untuk seluruh output Root Cause Analysis (RCA).

## Core Components

`RootCauseResult`

Sturuktur standar yang mencakup:

* `incident_id`

  Identifier unik setiap incident yang dihasilkan oleh sistem correlation engine.

  Digunakan untuk:
  * Melacak kejadian anomaly secara individual
  * Menghubungkan hasil RCA dengan incident monitoring
  * Memastikan setiap event memiliki refrensi yang dapat ditelusuri
  Contoh:
  ```
  ed41740a-2141-431e-91b2-f2c4293f8161
  ```
* `timestamp` (robust: int / ISO / datetime)

  Waktu terjadinya incident yang dianalisis oleh sistem.

  Mendukung sebagai format:
  * UNIX timestamp
  * ISO datetime string
  * Python datetime object
  Digunakan untuk:
  * Menyinkronkan event dengan telemetry monitoring
  * Analisis kronologi incident
  * Audit log sistem
* `domain_probabilities` (softmax normalized)

  Distribusi probabilitas yang menunjukan kemungkinan setiap domain menjadi penyebab utama incident.

  Nilai dihitung menggunakan softmax normalization dari skor kausal.

  Contoh:
  ```
  storage  = 0.33
  compute  = 0.29
  memory   = 0.20
  network  = 0.16
  ```
  Interprestasi:

  Semakin tinggi nilai probabilitas → semakin besar kemungkinan domain tersebut menjadi root cause.
* `root_domain`

  Domain dengan probabilitas tertinggi yang dianggap sebagai penyebab utama incident.

  Contoh:
  ```
  root_domain = storage
  ```
  Artinya sistem menilai bahwa gangguan kemungkinan besar berasal dari domain storage.
* `ranked_domains`

  Daftar domain yang diurutkan berdasarkan porbabilitas root cause dari tertinggi ke terendah.

  Digunakan untuk:
  * Menunjukan prioritas investigasi
  * Memberikan alternatif root cause kemungkinan kedua atau ketiga
  * Mendukung analisis multi-domain failure
* `causal_chain`

  Rantai propagasi masalah antar domain yang diperkirakan terjadi.

  Contoh:
  ```
  storage → compute → memory
  ```
  Interpretasi:

  Masalah kemungkinan dimulai dari storage, kemudian berdampak ke compute, dan akhirnya mempengaruhi memory.

  Digunakan untuk memahami alur dampak sistem.
* `impact_domains`

  Daftar domain yang terdampak oleh incident.

  Berbeda dengan root cause karena:
  * Root cause = sumber masalah
  * Impact domains = domain yang ikut terkena dampak
* `confidence`

  Nilai keyakinan sistem terhadap root cause yang dipilih.

  Nilai berada pada range:
  ```
  0 → 1
  ```
  Interprestasi:

| Confidence | Arti                    |
| ---------- | ----------------------- |
| >0.7       | Root cause sangat jelas |
| 0.4-0.7    | Root cause cukup jelas  |
| <0.4       | Root cause ambigu       |

* `entropy`

  Mengukur tingkat ketidakpastian distribusi root cause.

  Semakin tinggi entropy → semakin sulit menentukan root cause yang jelas.

  Contoh interpretasi:

| Entropy | Makna                  |
| ------- | ---------------------- |
| rendah  | root cause jelas       |
| sedang  | beberapa kandidat root |
| tinggi  | multi-domain failure   |

* `metadata`

  Informasi tambahan yang menyertakan data pendukung RCA.

  Contoh isi:
  ```
  num_domains
  max_proability
  ```
  Digunakan untuk analisis tambahan dan debugging.
* `explanation`

  Deskripsi naratif yang menjelaskan bagaimana sistem menarik kesimpulan root cause.

  Contoh:
  ```
  Root cause chain reconstructed: storage → compute → memory.
  Composite scoring applied (topology + domain strength + persistence + trend + drift).
  ```
  Digunakan untuk:
  * Interpretasi manusia
  * Audit AI decision
  * Dokumentasi incident

## Key Capabilities

* Softmax probalistic distribution
* Entropy calculation untuk ambiguity detection
* JSON-serializable output
* PostgreSQL JSONB persistence
* Schema-synchronized DB storage
* Deterministic reproducibility

## Result

✔ Production-ready RCA output contract
✔ API-safe
✔ DB-safe
✔ Governance-compatible



***

# 2. Casual Topology & Dependency Intelligence

## Objective

Mengintegrasikan dependency graph antar domain untuk memberikan structural causality reasoning.

## Core Mechanism

* Directed causal graph
* Upstream & downstream mapping
* Weight edge influence
* Hybrid override via registry

## Structural Reasoning Model

Setiap domain dinilai bedasarkan:

```
topology_score =
    downstream_weight * 0.6
  + upstream_weight * 0.4
```

Penjelasan:

`downstream_weight`

Mengukur seberapa besar pengaruh domain terhadap domain lain di sistem.

Jika domain A sering mempengaruhi domain lain, maka nilai downstream akan tinggi.

Contoh:

```
storage → compute
```

Masalah storage dapat memicu masalah compute.

`upstream_weight`

Mengukur seberapa besar domain dipengaruhi oleh domain lain.

Jika banyak domain mempengaruhi domain ini, upstream weight meningkat.

Digunakan untuk memahami dependency sistem.

`topology_score`

Skor yang menunjukan kekuatan posisi domain dalam graph dependency sistem.

semakin tinggi nilai ini → semakin besar kemungkinan domain tersebut menjadi sumber masalah.

## Result

✔ Topology-aware scoring
✔ Structural causality inference
✔ Override-capable architecture
✔ DFS-safe traversal



***

# 3. Causal Scoring & Root Ranking Engine

## Objective

Menghasilkan ranking root cause berbasis composite intelligance.

## Composite Scoring Formula

```
root_score(domain) =
    0.30 * topology_score
  + 0.25 * domain_strength
  + 0.20 * persistence_ratio
  + 0.10 * trend_weight
  + 0.10 * anomaly_ratio
  + 0.05 * drift_ratio
```

Penjelasan:

`domain_strength`

&#x20;   Mengukur seberapa besar gangguan pada domain tertentu dibanding domain lain.

Biasanya dihitung dari magnitude Z-score domain.

Semakin besar besar nilainya → semakin kuat indikasi gangguan.

`persistence_ratio`

&#x20;   Mengukur seberapa sering domain muncul sebagai domain aktif dalam window waktu.

Contoh:

```
compute aktif di 4 dari 5 snapshot
persistence_ratio = 0.8
```

Digunakan untuk membedakan antara:

* spike sesaat
* masalah yang konsisten

`trend_weight`

Menunjukan arah perkembangan gangguan domain

Kategori:

| Trend      | Makna                 |
| ---------- | --------------------- |
| increasing | masalah semakin parah |
| stable     | kondisi tidak berubah |
| decreasing | gangguan mereda       |

Digunakan untuk escalation logic.

`anomaly_ratio`

Persentase snapshot anomaly dalam window waktu.

Rumus:

```
anomaly_ratio = anomaly_count / window_size
```

Digunakan untuk mendeteksi **burst anomaly.**

`drift_ratio`

Persentase snapshot yang mengalami severe drift.

Digunakan untuk membedakan:

* anomaly biasa
* perubahan sistem yang struktural

Kemudian:

* Softmax normalization
* Confidence extraction
* Entropy calculation

## Signal Used

* Domain Z-score magnitude
* Temporal persistence ratio
* Drift ratio
* Anomaly ratio
* Trend direction
* Topological influence

## Result

✔ Topology-dominant bias removed
✔ Drift-aware reasoning
✔ Temporal-sensitive ranking
✔ Explainable probabilistic inference



***

# 4. Casual Chain Reconstruction & Explanation Layer

## Objective

Merekonstruksi jalur propagasi kasual dari root domain ke domain terdampak.

## Chain Reconstruction Strategy

* Depth-limited DFS traversal

  Algoritma pencarian graph yang membatasi kedalaman pencarian.

  Tujuannya:
  * Menghindari chain terlalu panjang
  * Mencegah over-analysis
* Cycle-safe

  Mencegah infinite loop pada graph dependency.

  Jika domain sudah pernah dikunjugi, traversal berhenti.
* Active-domain filtering

  Hanya domain aktif dalam incident yang dipertimbangkan dalam causal chain.

  Ini menghindari noise dari domain yang tidak relevan.
* Probability-based pruning ( < 0.15 excluded)

  Domain dengan probabilitas root cause sangat kecil (<0.15) tidak dimasukkan ke chain.

  Digunakan untuk:
  * mengurangi noise
  * membuat chain lebih interpretabel
* Downstream-only propagation

  Chain hanya mengikuti arah dependency sistem.

  Artinya:
  ```
  storage → compute
  ```
  bukan:
  ```
  compute → storage
  ```

## Example Output

```json
"causal_chain": ["storage", "compute"]
```

## Explaination Builder

Dynamic explanation:

```
Root cause chain reconstructed: storage → compute.
Composite scoring applied (topology + domain strength + persistence + trend + drift).
```

## Result

✔ Deterministic chain
✔ Noise reduction via probability pruning
✔ Human-readable explanation
✔ Governance-ready reasoning



***

# 5. Lifecycle Integration, Evaluation & Monitoring

## Objective

Membuat RCA menjadi self-governed dan stability-aware

## Lifecycle Metrics

* `root_stability`

  Mengukur konsistensi root cause dalam window.

  Rumus sederhana:
  ```
  root_stability =
  jumlah root yang sama / total window
  ```
  Nilai tinggi → root cause konsisten.
* `root_shift_frequency`

  Jumlah perubahan root dalam window.

  Digunakan untuk mendeteksi:
  * RCA instability
  * perubahan pola gangguan
* `avg_confidence`

  Rata-rata nilai confidence dari beberapa incident terakhir.

  Digunakan untuk menilai apakah RCA cukup yakin atau tidak.
* `avg_entropy`

  Rata-rata entropy dari hasil RCA.

  Semakin tinggi → root cause semakin ambigu.

Stability Score

```
stability_score =
    0.5 * root_stability
  + 0.3 * avg_confidence
  + 0.2 * entropy_penalty
```

* `entropy_penalty`

  Penalty yang diberikan jika entropy terlalu tinggi.

  Entropy dinormalisasi terhadap jumlah domain (`log(N)`).

  Digunakan untuk mengurangi stability ketika root cause terlalu ambigu.

## Governance Output

```json
"governance": {
  "rca_unstable": false,
  "low_confidence": false,
  "high_entropy": false,
  "governance_flag": false,
  "stability_score": 0.629,
  "severity_level": "moderate"
}
```

## Governance Metrics

* `rca_unstable`

  Menunjukan apakah root cause sering berubah dalam window.
* `low_confidence`

  Menunjukan apakah confidence RCA terlalu rendah.
* `high_entropy`

  Menunjukan apakah distribusi root cause terlalu ambigu.
* `governance_flag`

  Flag utama yang aktif jika terdapat masalah dalam kualitas RCA.

  Digunakan untuk:
  * alert AI governance
  * evaluasi model
  * monitoring sistem
* `stability_score`

  Skor stabilitas keseluruhan RCA.

  Digunakan untuk menilai kualitas analisis root cause.
* `severity_level`

  Klasifikasi stabilitas RCA.

| **Score** | **Severity** |
| --------- | ------------ |
| ≥ 0.75    | Stable       |
| 0.5–0.75  | Moderete     |
| < 0.5     | Unstable     |

## Result

✔ Root volatility detection
✔ Entropy-aware governance
✔ Confidence degradation monitoring
✔ Promotion-gate compatible stability index
✔ Drift-to-root sensitivity awareness



***

# 6. Addendum v1.2.0 — Penyesuaian untuk Use Case 1, 2, 3

> **Tanggal:** 20 Mei 2026
> **Tujuan:** Memperluas RCA engine agar mendukung mode predictive (UC1), capacity reasoning (UC2), domain energi (UC3), dan output yang siap dikonsumsi LLM.
> **Sifat:** Addendum non-destruktif — bagian 1–5 di atas tetap berlaku.

## 6.1 Ringkasan Gap

| Area | Kondisi Saat Ini | Kebutuhan UC | Status |
| --- | --- | --- | --- |
| Domain coverage | Topology fokus compute/memory/storage/network | UC1/UC3 perlu edge ke power & cooling | ❌ Tambah |
| Predictive RCA | Reaktif — RCA dijalankan setelah incident | UC1 perlu RCA forward dari forecast | ❌ Tambah |
| Capacity reasoning | Tidak relevan untuk RCA klasik | UC2 perlu modul terpisah berbasis CapacityState | ❌ Tambah |
| Asset enrichment | RCA result minim konteks fisik | UC1/UC2/UC3 perlu lokasi rack, criticality, PDU/UPS | ⚠️ Diperluas |
| LLM contract | `RootCauseResult` serializable, tapi prompt template belum standar | LLM `dcim_assistant` perlu format konsisten | ⚠️ Distandardisasi |

## 6.2 Domain Coverage (Topology Diperluas)

Causal topology default disinkronkan dengan MT-020 §6.7:

```
power    → compute
power    → cooling
cooling  → compute
cooling  → memory
cooling  → storage
hardware → storage
hardware → compute
storage  → compute
compute  → memory
network  → compute
```

Composite scoring formula (existing) tidak berubah. Hanya `topology_score` sekarang dapat menghasilkan domain `power` / `cooling` / `hardware` sebagai root domain.

## 6.3 Predictive RCA (Forward Reasoning)

Mode RCA baru: **forward** — dijalankan terhadap output forecast model UC1 (lihat MT-019 §6.3 + MT-021 §7.2).

```python
class RCAMode(Enum):
    REACTIVE = 'reactive'      # existing — incident yang sudah terjadi
    FORWARD  = 'forward'       # baru   — projected incident dari forecast
    HYBRID   = 'hybrid'        # gabungkan keduanya untuk early warning

class ForwardRCAInput:
    forecast_id: str           # InferenceResult dengan model_type=forecast
    horizon_h: int             # 24 atau 48
    forecasted_domains: dict   # domain → forecasted_score
    asset_id: str
```

Output `RootCauseResult` sama strukturnya, dengan tambahan field opsional:
```
mode: 'reactive' | 'forward' | 'hybrid'
forecast_horizon_h: int | None
forecast_confidence: float | None
```

**Implementasi (v1.2.0 — selesai 20 Mei 2026):**

| Komponen | Lokasi | Catatan |
| --- | --- | --- |
| Field opsional `mode`, `forecast_horizon_h`, `forecast_confidence`, `asset_context`, `governance` | `dcim_ai/root_cause/rca_models.py` | Default `mode = 'reactive'` → backward compatible |
| `RCAEngine.analyze_forward(forecast_payload)` | `dcim_ai/root_cause/rca_engine.py` | Menerima dict `{incident_id, timestamp, forecast_horizon_h, forecasted_domains, forecast_confidence, asset_id}`. Reuse `analyze()` via synthetic incident. |
| `RCAEngine.analyze_hybrid(incident, forecast_payload, forecast_weight=0.4)` | `dcim_ai/root_cause/rca_engine.py` | Weighted merge probabilitas: `(1-w)·reactive + w·forward`, lalu re-rank & rebuild causal chain. |
| Governance flag `forward_low_confidence` | otomatis aktif bila `forecast_confidence < 0.5` | Sesuai §6.7 |
| Test coverage | `dcim_ai/tests/test_rca_forward.py` | 11 test (reactive backcompat, forward, hybrid, serialization) |

Manfaat: RCA bisa menjawab "kalau forecast 24 jam ke depan menunjukkan failure di server X, kemungkinan rantai penyebabnya apa?" — sesuai UC1 success criteria (alert 24–48 jam sebelum kegagalan).

## 6.4 Capacity Reasoning (Modul Baru, UC2)

RCA klasik tidak relevan untuk capacity recommendation. Tambahkan modul terpisah dengan kontrak output sendiri.

```python
@dataclass
class CapacityRecommendation:
    recommendation_id: str
    timestamp: datetime
    scope: str                  # 'rack' | 'zone' | 'site'
    asset_ids: list[str]
    finding: str                # 'underutilized' | 'saturating' | 'imbalanced'
    metrics: dict               # utilization_p50, p95, headroom_pct
    suggested_action: str       # 'consolidate', 'redistribute', 'scale_out'
    estimated_savings: dict     # {'capacity_pct': 12.5, 'power_kw': 4.2}
    confidence: float
    narrative: str              # diisi LLM
    evidence: list[dict]        # CapacityState snapshots
```

Algoritma:
1. Konsumsi `CapacityState` dari MT-020 §6.3.
2. Clustering workload (KMeans) per `feature_group=capacity_metrics`.
3. Bin-packing simulator (heuristic) untuk skenario konsolidasi.
4. LLM (`dcim_assistant`) merangkum hasil jadi narasi.

## 6.5 Asset Context Enrichment

`RootCauseResult` & `CapacityRecommendation` wajib di-enrich dengan `AssetContext` dari MT-020 §6.4. Penambahan field:

```
asset_context: {
  asset_id, site, rack, zone,
  criticality, role,
  upstream_pdu, upstream_ups
}
```

Manfaat:
* UC1: alert tahu rack & criticality tier → prioritas eskalasi.
* UC3: alert energi tahu PDU/zone terdampak → "Baris C, PDU-05" sesuai use case doc.
* LLM bisa narasikan dengan referensi fisik.

**Implementasi (v1.2.0 — selesai 20 Mei 2026):**

| Komponen | Lokasi | Catatan |
| --- | --- | --- |
| `AssetEnricher` | `dcim_ai/inference/asset_enricher.py` | Wrapper di atas `AssetContextResolver` — best-effort, idempotent |
| `enrich_inference(result, force=False)` | s.d.a. | Set `InferenceResult.asset_context` (object form) |
| `enrich_rca(result, asset_id=None, force=False)` | s.d.a. | Set `RootCauseResult.asset_context` (dict form). Sumber asset_id: argumen → `metadata['asset_id']` (di-set otomatis oleh `analyze_forward()`) |
| `enrich_capacity(recommendation, force=False)` | s.d.a. | Resolve seluruh `asset_ids` → list `AssetContext` |
| `get_default_enricher()` / `set_default_enricher()` | s.d.a. | Singleton untuk runtime, override-able untuk testing |
| Auto-set governance flag `asset_context_missing` | bila resolve UNKNOWN | Sesuai §6.7 |
| Auto-set governance flag `cross_domain_power_cooling` | bila root_domain ∈ {power, cooling} & impact > 1 domain | Sesuai §6.7 |
| Test coverage | `dcim_ai/tests/test_asset_enricher.py` | 14 test (resolve, inference enrich, RCA enrich, capacity enrich, governance flags) |

## 6.6 LLM Contract Standar

Untuk integrasi dengan `dcim_assistant` (MT-023), tambahkan prompt template fixed.

```yaml
prompt_template:
  system: |
    Anda adalah DCIM AI Assistant. Berikan analisis root cause yang ringkas,
    teknis, dan actionable berdasarkan struktur input.
  user_template: |
    Incident: {incident_id} pada {timestamp}
    Asset: {asset_context.role} di {asset_context.rack} ({asset_context.site}),
    criticality {asset_context.criticality}
    Mode: {mode}
    Root domain: {root_domain} (confidence={confidence:.2f}, entropy={entropy:.2f})
    Causal chain: {causal_chain}
    Evidence: {explanation}

    Berikan:
    1. Penjelasan root cause dalam 2-3 kalimat.
    2. Estimasi dampak.
    3. Rekomendasi tindakan operator (maks 3 langkah).
```

Format output LLM dipaksa JSON (`response_format=json_object`) agar parsable downstream:
```json
{
  "summary": "...",
  "impact":  "...",
  "actions": ["...", "...", "..."]
}
```

### 6.6.1 Status Implementasi v1.2.0-impl-4

Kontrak prompt/output sudah diimplementasikan sebagai modul deterministic contract builder dan validator. Modul ini tidak melakukan inference LLM; hanya membentuk prompt dan memvalidasi respons sebelum dipakai dashboard/incident management.

| Komponen | File / API | Status |
| --- | --- | --- |
| System prompt fixed | `dcim_ai/llm/rca_prompt_contract.py::SYSTEM_PROMPT` | Implemented |
| User prompt builder | `build_rca_user_prompt(rca_result)` | Implemented; menerima `RootCauseResult` atau dict-like object |
| Chat message payload | `build_rca_chat_messages(rca_result)` | Implemented; format OpenAI/Ollama-compatible (`system`, `user`) |
| Deterministic Ollama options | `build_ollama_options()` | Implemented; `temperature=0`, `top_p=0.9`, `num_predict=512` |
| Output validator | `validate_rca_llm_response(raw)` | Implemented; strict JSON object dengan key persis `summary`, `impact`, `actions` |
| Narrative dataclass | `RCAAlertNarrative` | Implemented; serializable via `to_dict()` |
| Validation result | `LLMValidationResult` | Implemented; menyimpan `valid`, `narrative`, `errors`, `raw` |
| Test coverage | `dcim_ai/tests/test_llm_rca_prompt_contract.py` | 9 test pass |

Validasi runtime menggunakan virtual environment lokal project:

- Venv aktif: `/home/infra/dcim_project/ragavenv`
- Path lama `/home/infra/rnd_rag-anything/ragavenv` sudah dipakai hanya sebagai sumber awal migrasi.
- Script/shebang venv hasil copy sudah diarahkan ke `/home/infra/dcim_project/ragavenv`.

Aturan validator:
- `summary` wajib string non-empty.
- `impact` wajib string non-empty.
- `actions` wajib list string non-empty dengan 1–3 item.
- Key tambahan ditolak agar schema downstream stabil.
- JSON invalid / non-object ditolak dengan error eksplisit.

## 6.7 Governance Update

`governance_flag` existing diperluas dengan flag baru:

| Flag | Trigger |
| --- | --- |
| `forward_low_confidence` | mode=forward & forecast_confidence < 0.5 |
| `cross_domain_power_cooling` | root_domain ∈ {power, cooling} & impact > 1 domain |
| `asset_context_missing` | asset_context tidak teresolusi (NetBox down / mapping hilang) |

Flag ini memicu `REVIEW` di gatekeeper sebelum alert dipublish ke incident management.

## 6.8 Mapping ke Use Case

| UC | Bagian Addendum yang Dipakai |
| --- | --- |
| UC1 | 6.2 (topology hardware), 6.3 (mode FORWARD/HYBRID), 6.5 (criticality untuk eskalasi), 6.6 (LLM contract), 6.7 (`forward_low_confidence`) |
| UC2 | 6.4 (`CapacityRecommendation`), 6.5 (occupancy_pct), 6.6 (LLM narasi rekomendasi) |
| UC3 | 6.2 (topology power/cooling), 6.5 (`upstream_pdu/ups`, `zone`), 6.6 (LLM contextual alert), 6.7 (`cross_domain_power_cooling`) |

## 6.9 Changelog

| Date       | Versi | Auth         | Note                                                                                                              |
| ---------- | ----- | ------------ | ----------------------------------------------------------------------------------------------------------------- |
| 20/05/2026 | 1.2.0 | DCIM AI Team | Topology power/cooling/hardware, predictive RCA (FORWARD/HYBRID), CapacityRecommendation, asset enrichment, LLM contract |

