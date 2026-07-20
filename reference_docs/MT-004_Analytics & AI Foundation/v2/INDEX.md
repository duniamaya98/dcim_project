---
title: "Indeks Dokumentasi v2 — MT-018 s.d MT-022 (Analytics & AI Foundation)"
version: 2.0
created: 2026-07-10
author: Fakhri Aulia R
status: Done
scope: MT-018, MT-019, MT-020, MT-021, MT-022
related_uc: [UC1 Predictive Failure Alerting, UC2 Capacity Optimization, UC3 Energy/PUE Drift]
block: block7-analytics-ai-engine
---

# Indeks Dokumentasi v2 — MT-018 s.d MT-022

> **Tujuan:** Menyediakan indeks pusat untuk seluruh dokumen referensi v2 Analytics & AI Foundation (MT-018 hingga MT-022), beserta pemetaan ke Google Sheets task tracker dan dcim-wiki Block 7 Reference Design.

---

## Daftar Dokumen v2

| MT Task | Judul | Assignee | dcim-wiki Section | Alignment Score | File |
|---------|-------|----------|-------------------|-----------------|------|
| **MT-018** | Traditional Machine Learning Model | Fakhri Aulia R | Block 7 — Data Processing & ML Pipeline | ~80% | `[(MT-018) Traditional Machine Learning Model v2.md]((MT-018)%20Traditional%20Machine%20Learning%20Model%20v2.md)` |
| **MT-019** | Anomaly Detection Framework | Fakhri Aulia R | Block 7 — Section 3: Anomaly Detection, Section 12: Monitoring | ~70% | `v2_(MT-019) Anomaly Detection Framework.md` + `v2_(MT-019) Anomaly Detection Framework Configuration Documentation.md` |
| **MT-020** | Cross-Domain Correlation Engine | Fakhri Aulia R | Block 7 — Cross-Domain Correlation & Root Cause | ~80% | `[(MT-020) Cross-Domain Correlation Engine v2.md]((MT-020)%20Cross-Domain%20Correlation%20Engine%20v2.md)` |
| **MT-021** | Model Training & Evaluation Lifecycle Engine | Fakhri Aulia R | Block 7 — ML Lifecycle & MLOps | ~80% | `[(MT-021) Model Training & Evaluation Lifecycle Engine v2.md]((MT-021)%20Model%20Training%20%26%20Evaluation%20Lifecycle%20Engine%20v2.md)` |
| **MT-022** | Root Cause Analysis Engine | Fakhri Aulia R | Block 7 — Root Cause Analysis & Reasoning | ~80% | `[(MT-022) Root Cause Analysis Engine v2.md]((MT-022)%20Root%20Cause%20Analysis%20Engine%20v2.md)` |

---

## Ringkasan

| Metrik | Nilai |
|--------|-------|
| Jumlah task | 5 |
| Status | ✅ Semua Done |
| Assignee tunggal | Fakhri Aulia R |
| Alignment score rata-rata | ~80% |
| Cakupan use case | UC1 (Predictive Failure Alerting), UC2 (Capacity Optimization), UC3 (Energy/PUE Drift) |
| Referensi dcim-wiki | Block 7 — Analytics & AI Engine Reference Design |
| Google Sheets task range | MT-018 hingga MT-022 |
| Versi dokumentasi | v2 (revisi dari v1, Juli 2026) |

---

## Pemetaan ke Google Sheets & dcim-wiki

### Google Sheets Task Tracker

Seluruh task MT-018 s.d MT-022 tercatat dalam Google Sheets task tracker Analytics & AI Foundation. Setiap baris task memiliki:

- **Task ID** — MT-018, MT-019, MT-020, MT-021, MT-022
- **Status** — Done
- **Assignee** — Fakhri Aulia R
- **Dokumen output** — File-file v2 yang terindeks di tabel atas

### dcim-wiki Block 7 — Analytics & AI Engine Reference Design

Dokumen v2 ini selaras dengan **dcim-wiki Block 7 Reference Design** yang mencakup:

| Komponen Block 7 | MT Task Terkait | Keterangan |
|-------------------|-----------------|------------|
| Data Processing & ML Pipeline | MT-018 | Feature engineering, model config, data source abstraction |
| Anomaly Detection & Alerting | MT-019 | Multi-model registry, streaming inference, drift detection |
| Cross-Domain Correlation & Root Cause | MT-020 | Domain feature map, asset context, causal topology |
| ML Lifecycle & MLOps | MT-021 | Training profiles, evaluation metrics, promotion gates |
| Root Cause Analysis & Reasoning | MT-022 | RCA modes, capacity recommendation, LLM contract |

---

## Referensi Silang

- **CHANGELOG asli (v1):** [`CHANGELOG_MT-018_to_MT-022.md`](../CHANGELOG_MT-018_to_MT-022.md)
- **CHANGELOG v2:** [`CHANGELOG_v2.md`](CHANGELOG_v2.md)
- **dcim-wiki Block 7:** `reference-designs/block7-analytics-ai-engine.md`
- **Google Sheets:** Task tracker Analytics & AI Foundation (MT-018 s.d MT-022)

---

*Terakhir diperbarui: 10 Juli 2026*
