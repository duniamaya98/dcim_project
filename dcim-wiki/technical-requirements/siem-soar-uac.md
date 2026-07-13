---
title: "SIEM/SOAR — User Acceptance Criteria (UAC)"
created: 2026-06-26
updated: 2026-06-26
type: acceptance-criteria
status: draft
author: Maday (requested) / Hermes (generated)
baseline: SIEM SOAR Actual Architecture §11 (15 criteria)
sources:
  - reference-designs/siem-soar-actual-architecture.md (§11 — 15 criteria)
  - reference-designs/siem-soar.md (§14 — 20 criteria)
  - concepts/siem-soar-sla-prioritization-framework-final.md (§15 — 21 criteria)
  - technical-requirements/siem-use-case-analysis-final.md (§18 — 22 criteria)
purpose: >
  User Acceptance Criteria untuk validasi SIEM/SOAR deployment aktual.
  Baseline: Actual Architecture (LME + Tracecat + DFIR-IRIS).
  Setiap criteria punya: ID, kategori, deskripsi, test method, expected result, evidence, status.
---

# SIEM/SOAR — User Acceptance Criteria (UAC)

> **Baseline:** SIEM SOAR Actual Architecture (§11 — 15 core criteria)
> **Stack:** LME (Wazuh + ES + Kibana + ElastAlert) → Tracecat → DFIR-IRIS
> **Sources enriched from:** Reference Design, SLA Framework, Use Case Analysis
> **Total criteria:** 15 core + 8 supplementary = **23 criteria**

---

## Table of Contents

1. [Acceptance Matrix](#1-acceptance-matrix)
   - A. Infrastructure & Health
   - B. Data Ingestion Pipeline
   - C. Detection & Alerting
   - D. Alert Bridge (ElastAlert → Tracecat)
   - E. Threat Intelligence Enrichment
   - F. AI-Assisted Triage
   - G. Case Management & Investigation
   - H. End-to-End Validation
   - I. Retention & Compliance
2. [Supplementary Criteria](#2-supplementary-criteria)
3. [Cross-Cutting Requirements](#3-cross-cutting-requirements)
4. [Sign-Off](#4-sign-off)

---

## 1. Acceptance Matrix

### A. Infrastructure & Health

| UAC ID | Criterion | Test Method | Expected Result | Evidence | Status |
|--------|-----------|-------------|-----------------|----------|--------|
| UAC-01 | Semua komponen SIEM/SOAR healthy | Cek health endpoint setiap komponen: Wazuh Manager, ES, Kibana, ElastAlert, Tracecat, DFIR-IRIS | Semua komponen return HTTP 200 / status healthy | Health check screenshot/log | ⬜ |
| UAC-02 | Wazuh Agent terhubung ke Wazuh Manager | Cek agent status di Wazuh UI → Agents | Semua agent status "Active" | Wazuh UI agent list | ⬜ |

**Catatan:**
- Single instance untuk semua komponen (belum HA/DR) — perlu N+1 untuk production
- Health endpoint harus di-monitor via Prometheus + Grafana

---

### B. Data Ingestion Pipeline

| UAC ID | Criterion | Test Method | Expected Result | Evidence | Status |
|--------|-----------|-------------|-----------------|----------|--------|
| UAC-03 | Wazuh Manager berhasil encode/decode logs | Kirim test log dari agent, cek decoded alert di Kibana | Alert muncul dengan field ter-decode (source IP, rule ID, severity, timestamp) | Kibana alert screenshot | ⬜ |
| UAC-04 | Event teringest dari source ke ES index | Kirim log dari berbagai source (server, network, app), query ES | Semua event tersimpan di index `wazuh-*` / `dcim-siem-*` | ES query result | ⬜ |

**Test Procedure:**
1. Login ke Wazuh Agent di source machine
2. Trigger test event: `logger -p local0.warning "UAC TEST EVENT"`
3. Tunggu ≤ 60 detik
4. Buka Kibana → Discover → filter by "UAC TEST EVENT"
5. Verifikasi: event ada, decoded correctly, fields complete

---

### C. Detection & Alerting

| UAC ID | Criterion | Test Method | Expected Result | Evidence | Status |
|--------|-----------|-------------|-----------------|----------|--------|
| UAC-05 | Detection rules trigger alert yang benar | Kirim test log yang memicu known rule (contoh: SSH brute force) | Alert di-generate dengan rule ID, severity, dan MITRE ATT&CK mapping | Kibana alert + rule detail | ⬜ |
| UAC-06 | Alerts tersimpan di Elasticsearch | Query ES untuk test alert | Alert ada di index, semua field terisi (event_id, rule_id, severity, timestamp, source_ip) | ES query result | ⬜ |
| UAC-07 | Kibana menampilkan alerts dengan benar | Buka Kibana → Security Events dashboard | Dashboard menampilkan alerts dengan visualisasi: timeline, severity distribution, top sources | Dashboard screenshot | ⬜ |

**Test Procedure:**
1. Kirim test log brute force: 10x failed SSH login dalam 1 menit
2. Verifikasi Wazuh rule terpicu (rule ID 5712 atau similar)
3. Cek alert di Kibana
4. Verifikasi severity, source IP, rule description

---

### D. Alert Bridge (ElastAlert → Tracecat)

| UAC ID | Criterion | Test Method | Expected Result | Evidence | Status |
|--------|-----------|-------------|-----------------|----------|--------|
| UAC-08 | ElastAlert mendeteksi alerts baru dari ES | Cek ElastAlert logs setelah alert baru | ElastAlert logs menunjukkan "alert triggered" untuk test alert | ElastAlert log | ⬜ |
| UAC-09 | ElastAlert forward alerts ke Tracecat | Cek Tracecat alert inbox setelah ElastAlert trigger | Alert muncul di Tracecat dengan semua field dari ElastAlert | Tracecat UI screenshot | ⬜ |

**Test Procedure:**
1. Pastikan ElastAlert running: `systemctl status elastalert`
2. Kirim test alert (seperti UAC-05)
3. Cek ElastAlert logs: `journalctl -u elastalert --since "5 minutes ago"`
4. Cek Tracecat → Alerts inbox
5. Verifikasi alert sampai dengan field lengkap

---

### E. Threat Intelligence Enrichment

| UAC ID | Criterion | Test Method | Expected Result | Evidence | Status |
|--------|-----------|-------------|-----------------|----------|--------|
| UAC-10 | Tracecat enrich alert dengan AbuseIPDB | Cek enrichment data pada alert yang punya IP address | AbuseIPDB score, country, ISP, usage type ter-attach ke alert | Tracecat enrichment panel | ⬜ |
| UAC-11 | Tracecat enrich alert dengan VirusTotal | Cek enrichment data pada alert yang punya hash/URL | VirusTotal detection ratio, file details ter-attach ke alert | Tracecat enrichment panel | ⬜ |

**Test Procedure:**
1. Kirim alert dengan IP address known malicious (contoh dari AbuseIPDB test IP)
2. Tunggu enrichment selesai (≤ 60s)
3. Buka alert di Tracecat → Periksa enrichment panel
4. Verifikasi: AbuseIPDB score muncul, country, ISP
5. Ulangi dengan known malicious hash untuk VirusTotal

---

### F. AI-Assisted Triage

| UAC ID | Criterion | Test Method | Expected Result | Evidence | Status |
|--------|-----------|-------------|-----------------|----------|--------|
| UAC-12 | AI Agent generate summary + recommendations | Review AI output pada alert | AI memberikan: (1) ringkasan alert, (2) risk assessment, (3) rekomendasi response | AI output screenshot | ⬜ |

**Test Procedure:**
1. Pilih alert yang sudah ter-enrich
2. Trigger AI triage (manual atau otomatis sesuai konfigurasi)
3. Review output AI:
   - Summary harus explain apa yang terjadi
   - Risk assessment harus ada (Low/Medium/High/Critical)
   - Recommendations harus actionable (contoh: "Isolate host", "Block IP", "Create ticket")

---

### G. Case Management & Investigation

| UAC ID | Criterion | Test Method | Expected Result | Evidence | Status |
|--------|-----------|-------------|-----------------|----------|--------|
| UAC-13 | Tracecat buat incident di DFIR-IRIS | Cek DFIR-IRIS incident list setelah alert diproses | Incident muncul di DFIR-IRIS dengan: title, severity, status, timeline | DFIR-IRIS incident screenshot | ⬜ |
| UAC-14 | SOC analyst bisa investigate incident | Login ke DFIR-IRIS, buka incident, review timeline | Analyst bisa: lihat timeline, lihat evidence, tambah notes, ubah status | Investigation walkthrough | ⬜ |

**Test Procedure:**
1. Setelah UAC-13 pass, buka DFIR-IRIS
2. Login sebagai SOC analyst
3. Buka incident yang baru dibuat
4. Verifikasi:
   - Timeline lengkap (alert → enrichment → triage → case creation)
   - Evidence ter-attach
   - Bisa tambah notes
   - Bisa ubah status (New → Investigating → Resolved → Closed)
   - Bisa assign ke analyst lain

---

### H. End-to-End Validation

| UAC ID | Criterion | Test Method | Expected Result | Evidence | Status |
|--------|-----------|-------------|-----------------|----------|--------|
| UAC-15 | E2E flow dari alert ke case < 5 menit | Kirim test alert, track melalui seluruh pipeline | Alert sampai ke DFIR-IRIS sebagai incident dalam ≤ 5 menit | Timestamp log: Wazuh → ES → ElastAlert → Tracecat → DFIR-IRIS | ⬜ |

**Test Procedure:**
1. Record timestamp: kirim test alert
2. Wazuh Manager: alert received (catat waktu)
3. Elasticsearch: alert indexed (catat waktu)
4. ElastAlert: alert triggered (catat waktu)
5. Tracecat: alert received + enrichment (catat waktu)
6. DFIR-IRIS: incident created (catat waktu)
7. Hitung total time: dari step 1 ke step 6
8. Pass jika ≤ 5 menit

---

### I. Retention & Compliance

| UAC ID | Criterion | Test Method | Expected Result | Evidence | Status |
|--------|-----------|-------------|-----------------|----------|--------|
| UAC-16 | Log retention sesuai policy | Cek ES index lifecycle management (ILM) | Hot: 7 hari, Warm: 30 hari, Cold: 90 hari, Delete: sesuai policy | ILM policy screenshot + index stats | ⬜ |

---

## 2. Supplementary Criteria

Dari source lain (Reference Design §14 + SLA Framework §15) yang belum tercakup di core:

| UAC ID | Criterion | Source | Test Method | Expected Result | Status |
|--------|-----------|--------|-------------|-----------------|--------|
| UAC-17 | Webhook HMAC authentication aktif | Reference Design §14.4 | Kirim request tanpa HMAC signature | Request ditolak (HTTP 401/403) | ⬜ |
| UAC-18 | OT-safe enforcement aktif | Reference Design §14.8 + SLA §15.14 | Coba jalankan forbidden action via playbook | Action diblokir, audit log tercatat | ⬜ |
| UAC-19 | Playbook execution < 60s p99 | SLA Framework §15.13 | Jalankan 10 playbook instances, ukur waktu | 99th percentile ≤ 60 detik | ⬜ |
| UAC-20 | RBAC aktif di semua komponen | Cross-cutting | Login dengan role berbeda, coba akses resource | Role restriction enforced | ⬜ |
| UAC-21 | Audit trail lengkap | Cross-cutting | Lakukan action (create case, update status, delete) | Semua action ter-log dengan: user, timestamp, action, result | ⬜ |
| UAC-22 | Notification delivery (email + Slack) | Reference Design §14.14 | Trigger notification event | Email terkirim, Slack message sampai | ⬜ |
| UAC-23 | TLS ≥ 1.2 antar komponen | Cross-cutting | Cek TLS config di nginx/reverse proxy | Semua connection pakai TLS 1.2+ | ⬜ |

---

## 3. Cross-Cutting Requirements

Kriteria ini berlaku untuk semua UAC di atas:

| # | Requirement | Target |
|---|-------------|--------|
| 1 | Total EPS capacity | ≥ 5,000 EPS (target 10K-20K per FIT041) |
| 2 | End-to-end latency (P1 alerts) | < 30 detik |
| 3 | Data completeness (P1) | ≥ 99.9% |
| 4 | DLQ rate | < 1% |
| 5 | Correlation engine uptime | ≥ 99.9% |
| 6 | Search speed (30 hari data) | ≤ 5 detik |
| 7 | TLS version | ≥ TLS 1.2 |
| 8 | Secret management | Vault / Kubernetes Secrets (no hardcoded) |

---

## 4. Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| DCIM Owner | | | |
| Security Manager | | | |
| SOC Lead | | | |
| Infrastructure Lead | | | |

### Pass Criteria

- **Core (UAC-01 s/d UAC-16):** Semua harus PASS
- **Supplementary (UAC-17 s/d UAC-23):** Minimal 5/7 PASS
- **Cross-cutting:** Semua harus terpenuhi

### Known Limitations (saat ini)

| # | Limitation | Impact | Remediation |
|---|-----------|--------|-------------|
| 1 | Single instance (belum HA/DR) | Jika node down, SIEM/SOAR offline | Deploy N+1 untuk ES, Tracecat, DFIR-IRIS |
| 2 | Belum ada network segmentation | Semua tier dalam 1 trust zone | Implementasi VLAN/microsegmentation |
| 3 | Belum ada encryption-at-rest | Data ES belum ter-encrypt | Aktifkan ES index encryption |
| 4 | Belum ada DCIM data sources (BMS, EPMS, PDU, etc.) | Physical-cyber correlation belum aktif | Integrasi Modbus, BACnet, SNMPv3 traps |

---

**Document Version:** v1.0 (DRAFT)
**Last Updated:** 2026-06-26
**Baseline Source:** `reference-designs/siem-soar-actual-architecture.md` §11
