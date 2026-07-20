# 2026-07-17 — Block 7 API Bug Fixes Report

> **Author:** Fakhri Aulia R (DCIM Block 7 Lead)
> **Date:** 2026-07-17
> **Status:** ✅ Resolved
> **Related:** MT-023, Block 7 Analytics & AI Engine
> **API Base:** `http://localhost:8000/api/v1`

---

## Overview

Audit & bug fix pada Block 7 Analytics API (22 endpoint, 8 kategori).
Temuan: 2 P1 bug + 1 config issue. Semua resolved dan diverifikasi.

---

## Temuan & Fix

### Bug 1 (P1): RCA `/history` → HTTP 404

**Root Cause:** Route `/{incident_id}` didefinisikan sebelum `/history` di `api/routers/rca.py`.
FastAPI match route secara registration order, sehingga path `/history` ditangkap
oleh handler `/{incident_id}` dengan `incident_id="history"`.

**Fix:** Menukar urutan definisi route — `/history` dipindahkan ke atas, `/{incident_id}` ke bawah.

**File:** `implementation/dcim_ai_v2_rag/api/routers/rca.py`

**Before:**
```
@router.get("/{incident_id}")       # ← line 166 (menangkap /history duluan)
async def get_rca_report(...)

@router.get("/history")              # ← line 234 (tidak pernah match)
async def get_rca_history(...)
```

**After:**
```
@router.get("/history")              # ← sekarang di atas, match duluan
async def get_rca_history(...)

@router.get("/{incident_id}")       # ← di bawah, hanya match non-literal paths
async def get_rca_report(...)
```

---

### Bug 2 (P1): Anomaly Detect POST → HTTP 500 `KeyError: 'time'`

**Root Cause:** Query SQL di `trigger_detection` (line 311) mengambil kolom
`value, ci_id, asset_id, source, unit, tags` tapi tidak include kolom `time`,
sementara di line 325 dipanggil `latest["time"]`.

**Fix:** Menambahkan kolom `time` ke SELECT query.

**File:** `implementation/dcim_ai_v2_rag/api/routers/anomalies.py`

**Before (line 311):**
```sql
SELECT value, ci_id, asset_id, source, unit, tags
FROM metrics WHERE metric_name = %s AND time > NOW() - INTERVAL '6 hours'
```

**After:**
```sql
SELECT value, time, ci_id, asset_id, source, unit, tags
FROM metrics WHERE metric_name = %s AND time > NOW() - INTERVAL '6 hours'
```

---

### Issue 3: DB Password Mismatch

**.env** file masih pakai password lama (`ai_team_access_pass`), sementara
DB TimescaleDB sudah di-update ke `Inovasi@0918` pada 2026-07-15.
Akibatnya semua endpoint yang akses DB gagal dengan `FATAL: password authentication failed`.

**Fix:** Update `TIMESCALEDB_PASSWORD` di `.env`.

---

## Verification

| # | Test | Sebelum | Sesudah |
|---|------|---------|---------|
| 1 | `GET /analytics/rca/history` | HTTP 404 | HTTP 200 (2 records, paginated) |
| 2 | `GET /analytics/rca/INC-20260715-001` | — | HTTP 200 (single report) |
| 3 | `POST /analytics/anomalies/detect` | HTTP 500 `KeyError: 'time'` | HTTP 200 (zscore=1.26, severity=low) |
| 4 | `GET /health` | degraded (DB unhealthy) | healthy (DB + API) |

---

## Data Source Audit (Bonus)

Audit apakah data endpoint berasal dari TimescaleDB (real) atau synthetic fallback.

| Endpoint | Source | Notes |
|----------|--------|-------|
| `GET /anomalies` | ✅ TimescaleDB | 6 records dari `anomaly_events` |
| `POST /anomalies/detect` | ✅ TimescaleDB | source: timescaledb, sample_size=100 |
| `GET /rca/history` | ✅ TimescaleDB | 2 records dari `rca_reports` |
| `GET /rca/{id}` | ✅ TimescaleDB | Query by incident_id |
| `POST /llm/query` | ✅ LLM | Gemma 4 12B via llama-server, no context data |
| `GET /predictions` | ⚠️ Empty | Tabel `predictions` ada tapi 0 records |
| `POST /predictions/forecast` | ⚠️ Synthetic fallback | `_fetch_live_metrics()` return None → `_generate_synthetic_metrics()` |
| `GET /capacity` | ⚠️ Empty | Tabel `capacity_forecasts` ada tapi 0 records |
| `POST /capacity/forecast` | ⚠️ Synthetic fallback | <7 data point → `_generate_synthetic_data()` |
| `GET /energy/pue` | ❌ Synthetic hardcoded | Metric `total_facility_power` & `it_equipment_power` tidak ada di DB |
| `POST /energy/optimize` | ❌ Synthetic hardcoded | Sama — DB query kosong |
| `GET /models` | ❌ Hardcoded `return []` | Model registry belum terintegrasi |

---

## Next Steps (Recommendation)

1. **Generate sample data** untuk `predictions` & `capacity_forecasts` table biar GET endpoint tidak kosong.
2. **Energy metrics** — tambahin metric `total_facility_power` & `it_equipment_power` ke pipeline ingestion, atau remap ke metric name yang sudah ada di DB.
3. **Model Registry** — integrasikan `GET /models` dengan registry/model_registry.py yang sudah ada, jangan hardcoded `return []`.
4. **Full endpoint test** — 11 endpoint (POST/PUT) yang belum diverifikasi secara fungsional.

---

## Files Changed

```
implementation/dcim_ai_v2_rag/api/routers/rca.py       — route reorder
implementation/dcim_ai_v2_rag/api/routers/anomalies.py  — SQL column fix
implementation/dcim_ai_v2_rag/.env                      — password update
```
