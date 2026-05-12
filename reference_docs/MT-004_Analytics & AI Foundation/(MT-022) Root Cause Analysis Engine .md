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

