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

# 6. Addendum v1.2.0 — Penyesuaian untuk Use Case 1, 2, 3

> **Tanggal:** 20 Mei 2026
> **Tujuan:** Mengaktifkan domain `power` & `cooling`, menambahkan `capacity_state`, asset/topology context, dan multi-resolution window agar correlation engine siap melayani UC1/UC2/UC3.
> **Sifat:** Addendum non-destruktif — bagian 1–5 di atas tetap berlaku.

## 6.1 Ringkasan Gap

| Area | Kondisi Saat Ini | Kebutuhan UC | Status |
| --- | --- | --- | --- |
| Domain feature map | `power` & `cooling` tercantum tapi belum ada fitur konkret | UC3 perlu mapping nyata ke metrik energi/lingkungan | ❌ Tambah |
| Capacity awareness | Tidak ada | UC2 perlu indikator utilization/headroom/occupancy | ❌ Tambah |
| Asset context | Stateless, tidak tahu rack/zone/site | UC1/UC2/UC3 perlu konteks fisik | ❌ Tambah |
| Window granularity | Single rolling window (mis. 5 menit) | UC1 (1h–24h), UC2 (7d–90d), UC3 (1m–15m) | ⚠️ Multi-resolution |
| Co-occurrence weighting | Tanpa bobot per-domain | UC1/UC3 butuh power+cooling co-occur lebih kritikal | ⚠️ Diperluas |

## 6.2 Domain Feature Map (Diperluas)

`DOMAIN_FEATURE_MAP` diperluas — entri lama tetap, entri baru ditambahkan.

```python
DOMAIN_FEATURE_MAP = {
    # existing
    "compute":  ["cpu_usage", "gpu_util"],
    "memory":   ["memory_usage", "gpu_mem_used"],
    "storage":  ["disk_io"],
    "network":  ["net_rx", "net_tx"],

    # baru — diaktifkan oleh feature group dari MT-018 §11
    "power":    ["power_w", "voltage", "current", "pue"],
    "cooling":  ["temp_inlet", "temp_outlet", "humidity", "dewpoint"],
    "hardware": ["smart_reallocated_sectors", "smart_temp", "fan_speed"],  # UC1
}
```

**Activation rule:** domain hanya aktif bila feature group-nya tersedia di sumber data. Tidak menyebabkan breaking change pada deployment yang hanya punya `server_metrics`.

## 6.3 Capacity State (Komponen Baru)

`DomainState` ditambah representasi kapasitas — bukan anomaly, melainkan indikator kondisi struktural.

```python
@dataclass
class CapacityState:
    domain: str
    utilization_p50: float       # rolling 30d median
    utilization_p95: float
    headroom_pct: float          # 100 - p95
    occupancy_pct: float | None  # dari NetBox (rack U usage)
    trend_30d: str               # 'increasing' | 'stable' | 'decreasing'
    underutilized: bool          # p95 < threshold (default 30%)
    saturating: bool             # p95 > threshold (default 85%)
```

Dipakai oleh UC2 sebagai input ke modul capacity reasoning (lihat MT-022 §6.4).

## 6.4 Asset/Topology Context

Correlation engine sekarang stateless terhadap aset fisik. Tambahkan resolver:

```python
class AssetContextResolver:
    source: str                  # 'netbox' | 'static_yaml'
    def resolve(asset_id: str) -> AssetContext: ...

@dataclass
class AssetContext:
    asset_id: str
    site: str
    rack: str
    zone: str                    # 'cooling_zone_2', dll.
    criticality: str             # 'tier1' | 'tier2' | 'tier3'
    role: str                    # 'database', 'compute', 'storage', dll.
    upstream_pdu: str | None
    upstream_ups: str | None
```

`Incident` output diperkaya:
```
incident_id, timestamp, severity, confidence,
active_domains, root_cause_hint,
asset_context: AssetContext        # baru
```

Untuk UC2/UC3, satu PDU/UPS bisa dipetakan ke banyak rack, sehingga severity dapat diagregasi per zone.

## 6.5 Multi-Resolution Window

Rolling window single-fixed digantikan dengan **buffer hierarkis**:

| Resolution | Use For | Window |
| --- | --- | --- |
| `realtime`  | UC3 PUE drift             | 1m / 5m / 15m  |
| `incident`  | UC1 anomaly correlation   | 15m / 1h / 6h  |
| `predictive`| UC1 forecast input        | 6h / 24h       |
| `capacity`  | UC2 utilization trend     | 7d / 30d / 90d |

`CorrelationBuffer` mendukung **multiple buffers per resolution**, tiap buffer punya `aggregation_engine` sendiri. Default behavior (single 5-menit) tetap berjalan jika konfigurasi multi-resolution tidak diaktifkan.

## 6.6 Domain Criticality Weighting

Co-occurrence matrix ditambah bobot per-domain (configurable):

```yaml
domain_criticality_weights:
  power:    1.5    # gangguan power = paling kritikal
  cooling:  1.4
  storage:  1.2
  compute:  1.0
  memory:   1.0
  network:  1.0
  hardware: 1.3
```

Severity score multi-domain dihitung sebagai:
```
weighted_score = Σ (domain_score_i × criticality_weight_i)
```

Efek: incident yang melibatkan **power + cooling** otomatis severity lebih tinggi daripada **compute + network**, sesuai realitas DCIM.

## 6.7 Causal Topology Update

Causal topology default diperluas (sumber kebenaran tunggal, dipakai juga oleh MT-022):

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

Override registry (`correlation_strategy`) tetap berlaku.

## 6.8 Mapping ke Use Case

| UC | Bagian Addendum yang Dipakai |
| --- | --- |
| UC1 | 6.2 (`hardware`), 6.4 (asset context), 6.5 (`incident`+`predictive` window), 6.6 (weighting), 6.7 (`hardware → storage/compute`) |
| UC2 | 6.3 (`CapacityState`), 6.4 (`occupancy_pct` dari NetBox), 6.5 (`capacity` window 7d/30d/90d) |
| UC3 | 6.2 (`power`, `cooling`), 6.4 (`upstream_pdu/ups`, `zone`), 6.5 (`realtime` 1m/5m/15m), 6.6 (criticality `power=1.5`), 6.7 (`power → cooling → compute`) |

## 6.9 Changelog

| Date       | Versi | Auth         | Note                                                                  |
| ---------- | ----- | ------------ | --------------------------------------------------------------------- |
| 20/05/2026 | 1.2.0 | DCIM AI Team | Domain power/cooling/hardware aktif, capacity state, asset context, multi-resolution window, criticality weighting |

