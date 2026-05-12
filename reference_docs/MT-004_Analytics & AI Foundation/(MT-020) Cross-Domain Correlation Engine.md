# (MT-020) Cross-Domain Correlation Engine

# 1 . Domain Abstraction & Correlation Design

## Objective

Membangun lapisan abstraksi domain untuk mentransformasikan telemetry mentah (CPU, memory, disk, network, dll.) menjadi entitas logis berbasis domain infrastruktur.

Tujuannya adalah memindahkan sistem dari pendekatan feature-level anomaly menjadi domain-aware anomaly intelligence.

## Architectural Concept

```
Raw Metrics
     ↓
Drift Detection (Z-score)
     ↓
DomainEngine
     ↓
DomainState
```

## Implementation

Core Components

* `DOMAIN_FEATURE_MAP`
  Mapping fitur → domain logis (compute, memory, storage, network, power, cooling)
* `DomainEngine`
  * Mengkalkulasi domain\_score berbasis drift
  * Mengidentifikasi active\_domains
  * Menghasilkan domain\_strength\_index
* `DomainState` (Structured Output)
  * domain\_scores
  * active\_domains
  * domain\_strength\_index

## Intelligence Level

Sistem kini mampu:

* Mengidentifikasi domain mana yang terdampak
* Mendeteksi interaksi lintas domain
* Mengukur kekuatan gangguan pada level domain
* Tidak lagi bergantung pada feature-level raw anomaly



***

# 2. Correlation Feature Aggregation

## Objective

Menambahkan temporal intelligence melalui mekanisme rolling window aggregation untuk mendeteksi pola, bukan hanya snapshot anomaly.

## Architectural Concept

```
Domain Snapshot
     ↓
CorrelationBuffer (Rolling Window)
     ↓
AggregationEngine
     ↓
AggregationState
```

## Implementation Highlights

CorrelationBuffer

* Rolling window berbasis waktu (misalnya 5 menit)
* Menyimpan snapshot domain + anomaly + drift

AggregationEngine

* Menghitung metrik agregasi dari buffer

Menghasilkan:

* **window\_size**

  Jumlah snapshot yang tersimpan dalam rolling window saat ini.

  Merepresentasikan panjang observasi temporal yang digunakan dalam korelasi.

  Semakin besar window\_size → semakin stabil analisis pola jangka pendek.


* anomaly\_ratio

  Rasio jumlah anomaly terhadap total snapshot dalan window.

  Rumus sederhana:

  anomaly\_ratio = anomaly\_count / window\_size

  Digunakan untuk:
  * Escalation detection
  * Burst anomaly detection
  * Retraining trigger
  Contoh:

  Jika 5 dari 5 snapshot adalah anomaly → anomaly\_ratio = 1.0


* drift\_ratio

  Rasio jumlah snapshot dengan status severe\_drift terhadap window\_size.

  Digunakan untuk:
  * Menentukan apakah perubahan sistem bersifat struktural
  * Membedakan anomaly karena fluktuasi vs pergeseran baseline



* domain\_activity\_count

  Menghitung berapa kali suatu domain aktif dalam window.

  Contoh:

  compute = 4 berarti domain compute aktif di 4 snapshot terakhir.


* domain\_presistence\_ratio

  Mengukur konsistensi domain aktif dalam window.

  Rumus:

  domain\_persistence\_ratio = domain\_activity\_count / window\_size

  Digunakan untuk:
  * Mendeteksi persistent issue
  * Menghindari false positive akibat spike sesaat



* co\_occurrence\_matrix

  Mencatat kombinasi domain yang aktif secara bersamaan.

  Contoh:

  compute ↔  memory = 5

  Artinya kedua domain aktif bersamaan dalam 5 snapshot

  Digunakan untuk:
  * Deteksi interaksi lintas domain
  * Indikasi potensi root cause kompleks



* domain\_trend (increasing / stable / decreasing)

  Menganalisis slope domain\_score dalam window.
  * increasing → gangguan semakin memburuk
  * stable → kondisi stagnan
  * decreasing → gangguan mereda
  Digunakan untuk:
  * Escalation logic
  * Alert priorization

## Intelligence Level

Sistem kini mampu:

* Mendeteksi anomaly persistence
* Mengidentifikasi cross-domain interaction
* Mendeteksi burst anomaly
* Menghitung probabilitas eskalasi bedasarkan pola
* Melakukan trend detection per domain



***

# 3. Correlation Engine Core

## Objective

Menggabungkan snapshot anomaly + drift + domain state + temporal aggregation menjadi incident terstruktur.

Sistem tidak lagi mengembalikan hanya anomaly, tetapi:

> Incident-aware intelligence

## Architectual Concept

```
DomainState
+
AggregationState
+
Snapshot Severity
      ↓
CorrelationEngine
      ↓
Incident Object
```

## Implementation

Components

* `severity_matrix.py`
* `incident_builder.py`
* `correlation_engine.py`

Incident Output Structure

```
{
  incident_id,
  timestamp,
  severity,
  confidence,
  active_domains,
  root_cause_hint
}
```

## Escalation Logic

Severity kini berbasis:

* Snapshot voting
* Temporal anomaly\_ratio
* Domain persistence
* Drift ratio
* Multi-domain interaction

Confidence dihitung sebagai fungsi agregasi anomaly\_ratio + drift\_ratio



***

# 4. Integration with Inference & Registry

## Objective

Membuat correlation engine lifecycle-aware dan version-controlled.

## Implementation

registry.json Extended

Menambahkan:

```
correlation_config:
    correlation_version
    correlation_strategy
    severity_matrix_version
```

ModelManager Extended

* Hot reload correlation metadata
* Lifecycle safe
* Backward compatible

API Response Extended

Response sekarang mengandung:

```ini
correlation_version #Menunjukan versi strategi korelasi yang digunakan pada production model
correlation_strategy #Nama strategi korelasi (misal: temporal_multi_domain_v1).
```

## Lifecycle Result

* Model Promotion ↔ Correlation strategy linked
* Rollback safe
* Production metadata aware
* No breaking changes



***

# 5. Monitoring, Automation & Testing

## Objective

Membuat sistem observable, measureable, adaptive, dan teruji.

## Monitoring (Prometheus)

Metrics tambahan:

| **Metrics**                           | **Penjelasan**                                                    |
| ------------------------------------- | ----------------------------------------------------------------- |
| dcim\_correlation\_incidents\_total   | Menghitung total incident hasil correlation engine                |
| dcim\_critical\_incidents\_total      | Jumlah incident dengan severity = critical                        |
| dcim\_multi\_domain\_incidents\_total | Jumlah incident dengan lebih dari satu domain aktif               |
| dcim\_correlation\_confidence         | Distribusi confidence incident dalam bentuk histogram             |
| dcim\_domain\_active\_count           | Jumlah domain aktif pada incident terakhir                        |
| dcim\_temporal\_anomaly\_ratio        | Menampilkan anomaly\_ratio saat ini untuk observability real-time |

Sistem kini incident-centric, bukan hanya model-centric.

## Automation

Retrain Trigger

* Drift-based retrain
* Temporal anomaly\_ratio retrain
* Cooldown-protected

Escalation Logic

* Burst detection
* Multi-domain escalation
* Anti-spam alert control

## Testing Coverage

* Unit Test: DomainEngine
* Unit Test: AggregationEngine
* Unit Test: CorrelationEngine
* Integration Test: FastAPI endpoint



***

