---
title: "Block 7 — MT-018 to MT-022 v2 Documentation Index"
created: 2026-07-10
updated: 2026-07-10
version: 2.0
type: task-spec
block: 7
phase: 2
owner: Fakhri Aulia R (Analytics & AI Team)
status: active
confidence: 95%
tags: [analytics, ai, mt-018, mt-019, mt-020, mt-021, mt-022, block7, v2]
reference_design: dcim-wiki/reference-designs/block7-analytics-ai-engine.md
---

# Block 7 — MT-018 to MT-022: v2 Documentation Index

> **Purpose:** Dokumentasi v2 untuk MT-018 s/d MT-022 yang di-revisi agar sejalan
> dengan dcim-wiki reference designs dan kode implementasi aktual.
> **Owner:** Fakhri Aulia R (Analytics & AI Team)
> **Assignee di Google Sheets:** Fakhri Aulia R
> **Status:** Semua Done

---

## Daftar Dokumen v2

| Doc | Task ID | Task Name | dcim-wiki Mapping | Status |
|-----|---------|-----------|-------------------|--------|
| [v2_MT-018.md](v2_MT-018.md) | MT-018 | Traditional ML Models | §3 Anomaly Detection | ✅ Done |
| [v2_MT-019.md](v2_MT-019.md) | MT-019 | Anomaly Detection Framework | §3 Anomaly Detection | ✅ Done |
| [v2_MT-020.md](v2_MT-020.md) | MT-020 | Cross-Domain Correlation Engine | §3 + §5 RCA | ✅ Done |
| [v2_MT-021.md](v2_MT-021.md) | MT-021 | Model Training & Evaluation | §8 Model Training Pipeline | ✅ Done |
| [v2_MT-022.md](v2_MT-022.md) | MT-022 | Root Cause Analysis Engine | §5 RCA | ✅ Done |

---

## Mapping: Google Sheets Task → dcim-wiki Reference Design

```
Google Sheets (MT-018 s/d MT-022)     dcim-wiki Block 7 Reference Design
──────────────────────────────────     ───────────────────────────────────
MT-018 Traditional ML Models      ──▶  §3 Anomaly Detection (Z-score, IF)
MT-019 Anomaly Detection Framework──▶  §3 Anomaly Detection (multi-model)
MT-020 Cross-Domain Correlation   ──▶  §3 + §5 RCA (domain scoring)
MT-021 Model Training & Evaluation──▶  §8 Model Training Pipeline
MT-022 Root Cause Analysis Engine ──▶  §5 RCA (causal chain, scoring)
```

---

## Kode Lokasi

Semua kode ada di:
```
/home/infra/dcim_project/implementation/dcim_ai_v2_rag/
```

---

## Team

| Assignee | Role | Tasks |
|----------|------|-------|
| Fakhri Aulia R | Analytics & AI Engineer | MT-018 s/d MT-022 |
| Imam Syauqi Achmad | Infrastructure Engineer | MT-012 s/d MT-017 |
| Shuffahaq Gilang Zhesa | Project Owner / Lead | MT-001 s/d MT-011 |

---

**Last Updated:** 2026-07-10
**Maintained By:** Fakhri Aulia R
