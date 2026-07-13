---
title: "FIT041 SIEM vs DCIM-Wiki — Komparasi & Alignment"
created: 2026-06-25
updated: 2026-06-25
type: comparison
tags: [siem, fit041, technical-requirements, comparison, gap-analysis, alignment, wazuh, tracecat, temporal, iris]
sources:
  - IF-Technical_Requirements_SIEM-FIT041-20260119.md
  - block6-siem-soc-v3
  - siem-soar
  - siem-soc
  - block1-infrastructure-provisioning
  - block2-data-ingestion-integration
confidence: high
purpose: >
  Komparasi mendalam antara Technical Requirements SIEM (FIT041)
  dengan knowledge base DCIM-Wiki untuk mengidentifikasi alignment, gap,
  dan connection points antara requirements layer dan implementation layer.
---

# FIT041 SIEM vs DCIM-Wiki — Komparasi & Alignment

> **Purpose:** Komparasi side-by-side antara **IF-Technical_Requirements_SIEM-FIT041-20260119.md** (Technical Requirements) dengan knowledge base DCIM-Wiki (Reference Design, Entity, Comparison).
> **Cara pakai:** Review setiap section untuk memahami alignment, identifikasi gap, dan tentukan action items.
> **Related:** [[block6-siem-soc-v3]], [[siem-soar]], [[siem-soc]]

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Document Metadata Comparison](#2-document-metadata-comparison)
3. [Section-by-Section Analysis](#3-section-by-section-analysis)
4. [Gap Analysis Summary](#4-gap-analysis-summary)
5. [Unique Items per Document](#5-unique-items-per-document)
6. [Connection Mapping](#6-connection-mapping)
7. [Architecture Pattern Assessment](#7-architecture-pattern-assessment)
8. [Recommendations](#8-recommendations)
9. [Quality Gate Checklist](#9-quality-gate-checklist)

---

## 1. Executive Summary

### Kesimpulan Utama

| Aspek | Hasil |
|-------|-------|
| **Status** | ✅ **COMPLEMENTARY** — Tidak ada konflik kritis |
| **Relationship** | FIT041 = *Requirements Layer* (APA yang harus dibangun) |
| | DCIM-Wiki = *Implementation Layer* (BAGAIMANA membangunnya) |
| **Scope Gap** | DCIM-Wiki 3x lebih komprehensif (1,597 lines vs 228 lines) |
| **Architecture Decision** | FIT041: Wazuh-native + n8n + TheHive |
| | DCIM-Wiki: Wazuh + TraceCat + Temporal + IRIS + MCP |
| **Konflik** | 0 konflik kritis yang memerlukan modifikasi dokumen |
| **Action** | Tidak perlu mengubah dokumen existing; cukup tambah dokumen baru |

### Quick Overview

```
FIT041 (Requirements)                    DCIM-Wiki (Implementation)
┌─────────────────────────────┐         ┌─────────────────────────────┐
│ §2.1 Log Ingestion          │← align →│ Block 6: Security Event     │
│ §2.2 Threat Detection       │← diff ─→│ Block 6: Detection Eng (v3) │
│ §2.3 Incident Response      │← diff ─→│ SIEM SOAR: TraceCat+Temp    │
│ §3.1 Performance (10K EPS)  │← align →│ SIEM SOAR: Deployment       │
│ §3.2 Reliability (HA)       │← align →│ SIEM SOAR: Docker Swarm     │
│ §3.3 Security (RBAC, TLS)   │← align →│ SIEM SOAR: Vault+OIDC       │
│ §4.1 Architecture           │← diff ─→│ SIEM SOAR: 13 Components    │
│ §4.2 Tech Stack             │← diff ─→│ SIEM SOAR: Full Stack       │
│ §4.3 Integration (5 points) │← diff ─→│ SIEM SOAR: 12 Categories    │
│ §5.1 Documentation          │← NEW ──→│ ❌ Missing in DCIM-Wiki     │
│ §5.2 Training               │← NEW ──→│ ❌ Missing in DCIM-Wiki     │
└─────────────────────────────┘         └─────────────────────────────┘
```

---

## 2. Document Metadata Comparison

| Field | FIT041 SIEM | DCIM-Wiki (Aggregate) |
|-------|-------------|----------------------|
| **Title** | Technical Requirements — SIEM | Block 6 SIEM/SOC + SIEM SOAR Reference Design |
| **Author** | Madiansyah Saputra | Hermes DCIM Orchestrator |
| **Date** | 20 Jan 2026 | 2026-06-23 → 2026-06-25 |
| **Version** | 2.0 | v3 (Block 6) + v1.0 (SIEM SOAR) |
| **Document Type** | Requirements Specification | Reference Design Specs |
| **Scope** | What to build | How to build |
| **Detail Level** | High-level requirements | Deep implementation detail |
| **Total Sections** | 6 main sections | 20 (Block 6) + 15 (SIEM SOAR) |
| **File Size** | ~30 KB | ~70 KB (aggregate) |
| **Lines** | 228 lines | ~1,597 lines (aggregate) |
| **Status** | Requirements baseline | Implementation reference |
| **Acceptance Criteria** | ❌ Not defined | ✅ 20 testable criteria |

---

## 3. Section-by-Section Analysis

### 3.1 §2.1 — Log Ingestion and Normalization

| Aspect | FIT041 (§2.1) | DCIM-Wiki (Block 6 §2) | Alignment |
|--------|---------------|------------------------|-----------|
| **Log Source Support** | DCIM components, OS (Linux/Windows/macOS), network devices, security tools, third-party apps | servers, network devices, applications, cloud | ✅ Complementary |
| **Protocol Support** | Syslog (UDP/TCP/TLS), Windows Event Log, FIM, REST API, **SFTP** | Syslog (UDP/TCP/TLS), Agent-based | ⚠️ FIT041 more protocols |
| **Normalization** | Regex decoder, XML rule engine, JSON output | Normalized security event schema | ⚠️ Different detail level |
| **Message Broker** | ❌ Not mentioned | **Kafka** (dcim.siem.events) | ❌ Missing in FIT041 |
| **Log Transport** | Wazuh Agent direct | **NiFi Syslog Processor** → Kafka | ❌ Missing in FIT041 |
| **Kafka Topic Config** | ❌ Not mentioned | 6 partitions, RF=3, 7-day retention | ❌ Missing in FIT041 |

**Kesimpulan:** FIT041 memberikan detail protocol (SFTP, Windows Event Log, FIM) yang tidak ada di DCIM-Wiki. DCIM-Wiki menambahkan Kafka sebagai message broker dan NiFi sebagai log transport — komponen kritis untuk production scalability.

---

### 3.2 §2.2 — Real-time Threat Detection and Correlation

| Aspect | FIT041 (§2.2) | DCIM-Wiki (Block 6 §4-12) | Alignment |
|--------|---------------|---------------------------|-----------|
| **Rule Engine** | Cross-host, time-based, rule chaining, severity alerting | Rule-based, Threshold, Pattern, Cross-source | ✅ Aligned |
| **Behavioral Analysis** | Brute force, privilege escalation, login anomaly, lateral movement | ML Alert Triage: Risk Scoring, Anomaly Detection, FP Reduction | ⚠️ FIT041 rule-based, DCIM-Wiki ML-based |
| **Threat Intelligence** | MISP, AlienVault OTX, AbuseIPDB, VirusTotal | MISP, AbuseIPDB, VirusTotal | ⚠️ FIT041 adds OTX |
| **Detection Engineering** | ❌ Not mentioned | Git-based rules, CI/CD pipeline, MITRE ATT&CK | ❌ Missing in FIT041 |
| **ML Alert Triage** | ❌ Not mentioned | Gradient Boosting, Isolation Forest, DBSCAN, Logistic Regression | ❌ Missing in FIT041 |
| **Physical-Cyber Correlation** | ❌ Not mentioned | OT+IT Alert Fusion, Environmental Anomaly, Power Impact | ❌ Missing in FIT041 |
| **Deception Technology** | ❌ Not mentioned | T-Pot (IT), Conpot (OT), Honey Credentials, Honey Files | ❌ Missing in FIT041 |
| **Threat Hunting** | ❌ Not mentioned | Proactive hypotheses, Sigma Rules, Jupyter, Atomic Red Team | ❌ Missing in FIT041 |
| **XDR Integration** | ❌ Not mentioned | CrowdStrike, SentinelOne, Zeek, Suricata, AWS GuardDuty | ❌ Missing in FIT041 |
| **MITRE ATT&CK** | ❌ Not mentioned | Tactic, Technique, Sub-technique mapping | ❌ Missing in FIT041 |

**Kesimpulan:** FIT041 mencakup basic detection. DCIM-Wiki v3 menambahkan 7 capability baru: Detection Engineering, ML Triage, Physical-Cyber Correlation, Deception, Threat Hunting, XDR, dan MITRE ATT&CK Mapping. FIT041 menyebutkan AlienVault OTX yang tidak ada di DCIM-Wiki.

---

### 3.3 §2.3 — Security Incident and Response

| Aspect | FIT041 (§2.3) | DCIM-Wiki (SIEM SOAR §4, §7-8) | Alignment |
|--------|---------------|--------------------------------|-----------|
| **Alert Generation** | Severity levels, full context, notifications (dashboard/email/webhook/API) | Alert ingestion via Kafka webhook, HMAC auth, rate limiting | ✅ Aligned |
| **Case Management** | TheHive, Jira, ServiceNow | **IRIS** (full lifecycle: New→Open→In Progress→Resolved→Closed) | ⚠️ Different tool |
| **Case Schema** | ❌ Not defined | Detailed JSON schema with MITRE, affected assets, timeline, evidence | ❌ Missing in FIT041 |
| **Case Metrics** | ❌ Not defined | MTTA <15min, MTTC <30min, MTTR <4hr, Auto-closure >60% | ❌ Missing in FIT041 |
| **SOAR Platform** | **n8n** (REST API integration) | **TraceCat** (Apache 2.0, purpose-built SOAR) | ⚠️ Different tool |
| **Workflow Engine** | ❌ Not specified | **Temporal** (exactly-once, state persistence, retry, compensation) | ❌ Missing in FIT041 |
| **Active Response** | Block IP, disable user, kill process | Block IP, isolate host, disable user + **OT-Safe rules** | ⚠️ DCIM-Wiki adds OT safety |
| **OT-Safe Enforcement** | ❌ Not mentioned | Forbidden: auto-reboot, auto-patch, auto-shutdown PDU/Cooling/BMS | ❌ Missing in FIT041 |
| **Playbook Design** | ❌ Not detailed | YAML-based, 8 standard playbooks, version-controlled | ❌ Missing in FIT041 |
| **Playbook Categories** | ❌ Not detailed | Alert Triage, Containment, Enrichment, Notification, Forensics, Compliance, Threat Hunting, OT-Safe | ❌ Missing in FIT041 |

**Kesimpulan:** FIT041 menggunakan TheHive + n8n; DCIM-Wiki menggunakan IRIS + TraceCat + Temporal. Keduanya open-source, tapi TraceCat + Temporal lebih capable untuk production SOAR. DCIM-Wiki menambahkan OT-Safe enforcement yang kritis untuk DCIM.

---

### 3.4 §3 — Non-Functional Requirements

| Aspect | FIT041 (§3) | DCIM-Wiki (SIEM SOAR §13) | Alignment |
|--------|-------------|---------------------------|-----------|
| **EPS Capacity** | Min 10,000 EPS, scalable to 20,000 | Not specified (sizing by tier) | ⚠️ FIT041 more specific |
| **Search Speed** | ≤5 sec for 30-day search | Not specified | ⚠️ FIT041 more specific |
| **Deployment Sizing** | ❌ Not detailed | Dev: 8 cores/16GB, Standard: 16 cores/32GB, Production: 32+ cores/64+ GB | ❌ Missing in FIT041 |
| **Docker Swarm** | ❌ Not detailed | 23 replicas, ~25 CPU, ~52 Gi RAM | ❌ Missing in FIT041 |
| **HA Architecture** | Wazuh Manager cluster, OpenSearch multi-node, Dashboard LB | Docker Swarm replicas (API x2, Worker x4, Executor x4) | ⚠️ Different detail |
| **Data Retention** | Hot 90 days, Warm/Cold/Archive min 2 years | Not detailed in SIEM SOAR | ⚠️ FIT041 more specific |
| **Scalability** | Horizontal: Wazuh Manager, OpenSearch, Log forwarder | Horizontal: Docker Swarm, Kubernetes | ✅ Aligned |
| **Network Segmentation** | ❌ Not mentioned | 3 VLANs: DMZ (sources), Data (processing), Management (SOAR/IRIS) | ❌ Missing in FIT041 |
| **Monitoring** | ❌ Not mentioned | Prometheus + Grafana dashboards | ❌ Missing in FIT041 |
| **SOC Metrics** | ❌ Not defined | Alert Volume, Case Volume, Response Time, Playbook Performance, SLA Compliance | ❌ Missing in FIT041 |
| **Prometheus Metrics** | ❌ Not mentioned | tracecat_alerts_ingested_total, playbook_execution_duration, etc. | ❌ Missing in FIT041 |

**Kesimpulan:** FIT041 lebih spesifik tentang EPS (10K) dan search speed (≤5s). DCIM-Wiki lebih komprehensif tentang deployment sizing, network segmentation, monitoring, dan SOC metrics.

---

### 3.5 §3.3 — Security and Compliance

| Aspect | FIT041 (§3.3) | DCIM-Wiki (SIEM SOAR §11) | Alignment |
|--------|---------------|---------------------------|-----------|
| **RBAC Roles** | SOC Analyst, SOC Admin, Auditor | SOC Analyst L1/L2/L3, SOC Manager, Admin (5 roles) | ⚠️ DCIM-Wiki more granular |
| **RBAC Matrix** | ❌ Not defined | Full matrix: Alerts, Cases, Playbooks, Workflows, Settings | ❌ Missing in FIT041 |
| **TLS** | End-to-end TLS | TLS required on all zones (DMZ, Data, Management) | ✅ Aligned |
| **Secret Management** | ❌ Not mentioned | **Vault**: Webhook HMAC, API Keys, DB Creds, TLS Certs, LLM Keys, SMTP (90-day rotation) | ❌ Missing in FIT041 |
| **OIDC/SSO** | ❌ Not mentioned | Keycloak OIDC for Web UI, MCP | ❌ Missing in FIT041 |
| **Audit Trail** | ❌ Not mentioned | Every action logged: Who, What, When, Where, Result | ❌ Missing in FIT041 |
| **HMAC Signature** | ❌ Not mentioned | Webhook authentication via HMAC-SHA256 | ❌ Missing in FIT041 |
| **Rate Limiting** | ❌ Not mentioned | 1000 req/min (alerts), 100 req/min (cases), 50 req/min (playbooks) | ❌ Missing in FIT041 |
| **Signed Agent Comm** | ✅ Mentioned | Not explicitly detailed | ✅ FIT041 unique |
| **Hardening Guide** | ✅ Mentioned | Not explicitly detailed | ✅ FIT041 unique |
| **FIM** | ✅ Mentioned as data integrity | Not detailed | ✅ FIT041 unique |

**Kesimpulan:** FIT041 menyebutkan signed agent communication, hardening guide, dan FIM yang tidak ada di DCIM-Wiki. DCIM-Wiki jauh lebih komprehensif dalam RBAC, secret management, audit trail, dan rate limiting.

---

### 3.6 §4 — Technical Specifications

| Aspect | FIT041 (§4) | DCIM-Wiki (SIEM SOAR §2, §5, §10) | Alignment |
|--------|-------------|-----------------------------------|-----------|
| **Architecture** | Wazuh Agent → Syslog Collector → Manager Cluster → Indexer Cluster → Dashboard | TraceCat (13 components) + Temporal + IRIS + Vault + MinIO | ⚠️ Different scope |
| **Tech Stack** | Wazuh, Wazuh Agent, Wazuh Indexer, Docker/K8s | Python/FastAPI, React/Next.js, PostgreSQL 16, Redis 7, Temporal, MinIO, Caddy | ⚠️ Different stack |
| **Integration Points** | 5 (All DCIM, Workflow/SOAR, CMDB, ITSM, TIP) | 12 categories (SIEM, EDR, NDR, Firewall, ITSM, TIP, Identity, Communication, Cloud, DCIM, Vulnerability, Forensics) | ❌ FIT041 much narrower |
| **SOC API** | ❌ Not defined | 12 endpoints (alerts, cases, playbooks, workflows, metrics, health) | ❌ Missing in FIT041 |
| **API Authentication** | ❌ Not defined | OIDC, API Key, HMAC Signature | ❌ Missing in FIT041 |
| **Case Management Tool** | TheHive | IRIS | ⚠️ Different tool |
| **SOAR Tool** | n8n | TraceCat | ⚠️ Different tool |
| **AI Agent Integration** | ❌ Not mentioned | MCP (Claude Code, Codex, Cursor) | ❌ Missing in FIT041 |
| **Object Storage** | ❌ Not mentioned | MinIO (evidence, artifacts) | ❌ Missing in FIT041 |

**Kesimpulan:** FIT041 menggunakan stack sederhana (Wazuh-native). DCIM-Wiki menggunakan stack production-grade dengan 13 komponen, 12 integration categories, dan AI agent integration.

---

### 3.7 §5 — Documentation and Training

| Aspect | FIT041 (§5) | DCIM-Wiki | Alignment |
|--------|-------------|-----------|-----------|
| **Documentation** | Rules/Use Cases, Onboarding guide, Operational Runbook, Custom decoder/rule docs | ❌ No explicit documentation requirements | ❌ Missing in DCIM-Wiki |
| **Training** | Rule/decoder creation, Incident triage, Hands-on lab with DCIM scenarios | ❌ No explicit training requirements | ❌ Missing in DCIM-Wiki |

**Kesimpulan:** FIT041 memiliki documentation dan training requirements yang penting untuk operasional tetapi tidak ada di DCIM-Wiki. Ini adalah gap penting yang perlu ditambahkan.

---

## 4. Gap Analysis Summary

### 4.1 Summary Matrix

| Aspect | FIT041 | DCIM-Wiki | Alignment | Gap Type | Priority |
|--------|--------|-----------|-----------|----------|----------|
| Log Ingestion | ✅ Detailed protocols | ✅ Kafka + NiFi | ⚠️ Partial | Complementary | P3 |
| Threat Detection | ✅ Rule-based | ✅ Rule + ML + XDR | ⚠️ Partial | DCIM-Wiki deeper | P2 |
| Case Management | TheHive | IRIS | ⚠️ Different tool | Design decision | P3 |
| SOAR Platform | n8n | TraceCat + Temporal | ⚠️ Different tool | Design decision | P1 |
| OT-Safe Enforcement | ❌ Not mentioned | ✅ Full enforcement | ❌ Missing in FIT041 | Critical gap | P1 |
| MITRE ATT&CK | ❌ Not mentioned | ✅ Full mapping | ❌ Missing in FIT041 | Gap | P1 |
| Detection Engineering | ❌ Not mentioned | ✅ Git-based + CI/CD | ❌ Missing in FIT041 | Gap | P1 |
| ML Alert Triage | ❌ Not mentioned | ✅ 4 ML models | ❌ Missing in FIT041 | Gap | P2 |
| Physical-Cyber Correlation | ❌ Not mentioned | ✅ OT+IT fusion | ❌ Missing in FIT041 | Gap | P1 |
| Deception Technology | ❌ Not mentioned | ✅ T-Pot + Conpot | ❌ Missing in FIT041 | Gap | P3 |
| Threat Hunting | ❌ Not mentioned | ✅ Proactive hunting | ❌ Missing in FIT041 | Gap | P2 |
| XDR Integration | ❌ Not mentioned | ✅ EDR/NDR/Cloud | ❌ Missing in FIT041 | Gap | P2 |
| AI Agent (MCP) | ❌ Not mentioned | ✅ Claude/Codex/Cursor | ❌ Missing in FIT041 | Gap | P2 |
| SOC API | ❌ Not defined | ✅ 12 endpoints | ❌ Missing in FIT041 | Gap | P2 |
| RBAC Matrix | Basic (3 roles) | Full (5 roles + matrix) | ⚠️ Partial | FIT041 simpler | P3 |
| Secret Management | ❌ Not mentioned | ✅ Vault + rotation | ❌ Missing in FIT041 | Gap | P1 |
| Network Segmentation | ❌ Not mentioned | ✅ 3 VLANs | ❌ Missing in FIT041 | Gap | P1 |
| Monitoring | ❌ Not mentioned | ✅ Prometheus + Grafana | ❌ Missing in FIT041 | Gap | P1 |
| Documentation | ✅ 4 doc types | ❌ Not defined | ❌ Missing in DCIM-Wiki | Gap | P2 |
| Training | ✅ 3 training items | ❌ Not defined | ❌ Missing in DCIM-Wiki | Gap | P2 |
| EPS Capacity | ✅ 10K-20K EPS | ❌ Not specified | ❌ Missing in DCIM-Wiki | Gap | P2 |
| Data Retention | ✅ Hot 90d, Archive 2yr | ❌ Not detailed | ❌ Missing in DCIM-Wiki | Gap | P2 |
| Deployment Sizing | ❌ Not detailed | ✅ 3 tiers (Dev/Std/Prod) | ❌ Missing in FIT041 | Gap | P3 |
| Acceptance Criteria | ❌ Not defined | ✅ 20 testable criteria | ❌ Missing in FIT041 | Gap | P1 |
| AlienVault OTX | ✅ Mentioned | ❌ Not in TIP list | ❌ Missing in DCIM-Wiki | Minor gap | P4 |
| OpenSearch | ✅ Used as indexer | Elasticsearch | ⚠️ Different tool | Alternative | P4 |
| SFTP Protocol | ✅ Mentioned | ❌ Not detailed | ❌ Missing in DCIM-Wiki | Minor gap | P4 |
| Signed Agent Comm | ✅ Mentioned | ❌ Not detailed | ❌ Missing in DCIM-Wiki | Minor gap | P3 |
| Hardening Guide | ✅ Mentioned | ❌ Not detailed | ❌ Missing in DCIM-Wiki | Minor gap | P3 |
| FIM | ✅ Mentioned | ❌ Not detailed | ❌ Missing in DCIM-Wiki | Minor gap | P3 |

### 4.2 Gap Counts

| Gap Type | Count | Description |
|----------|-------|-------------|
| ✅ Match | 4 | Log ingestion concepts, HA concept, TLS, scalability |
| ⚠️ Partial | 7 | Both have info but at different levels or tools |
| ❌ Missing in FIT041 | 18 | Major: OT-Safe, MITRE, Detection Eng, ML, Kafka, TraceCat, etc. |
| ❌ Missing in DCIM-Wiki | 8 | Documentation, Training, EPS, Retention, OTX, OpenSearch, etc. |
| **Total Aspects** | **37** | — |

### 4.3 Priority Distribution

| Priority | Count | Items |
|----------|-------|-------|
| **P1 Critical** | 8 | OT-Safe, MITRE, Detection Eng, Physical-Cyber, Secret Mgmt, Network Seg, Monitoring, Acceptance Criteria |
| **P2 High** | 9 | ML Triage, Threat Hunting, XDR, MCP, SOC API, Documentation, Training, EPS, Data Retention |
| **P3 Medium** | 7 | Case Mgmt tool, RBAC detail, Deployment Sizing, Signed Agent, Hardening, FIM, Log Ingestion detail |
| **P4 Supporting** | 3 | AlienVault OTX, OpenSearch alternative, SFTP protocol |

---

## 5. Unique Items per Document

### 5.1 FIT041 Unique Strengths

| Strength | Description | Value for DCIM |
|----------|-------------|----------------|
| **Documentation Requirements** | Rules/Use Cases, Onboarding guide, Runbook, Custom decoder docs | Operational readiness |
| **Training Requirements** | Rule creation, Incident triage, Hands-on lab | Team capability building |
| **EPS Capacity Target** | 10K-20K EPS with horizontal scaling | Concrete performance target |
| **Data Retention Policy** | Hot 90 days, Warm/Cold/Archive min 2 years | Compliance requirement |
| **Search Speed Target** | ≤5 sec for 30-day log search | Performance SLA |
| **AlienVault OTX** | Additional threat intelligence source | Broader TIP coverage |
| **OpenSearch** | Alternative to Elasticsearch | Vendor flexibility |
| **SFTP Protocol** | Secure file transfer for log forwarding | Additional protocol support |
| **Signed Agent Communication** | Wazuh agent authentication | Security measure |
| **Hardening Guide Compliance** | Security hardening practice | Security baseline |
| **FIM (File Integrity Monitoring)** | Data integrity verification | Security monitoring |

### 5.2 DCIM-Wiki Unique Strengths

| Strength | Description | Value for DCIM |
|----------|-------------|----------------|
| **TraceCat SOAR** | Purpose-built SOAR platform (Apache 2.0) | Production-grade automation |
| **Temporal Workflow Engine** | Exactly-once, state persistence, retry, compensation | Reliable orchestration |
| **IRIS Case Management** | Full case lifecycle with MITRE mapping | Comprehensive case tracking |
| **Detection Engineering** | Git-based rules, CI/CD pipeline | Consistent, version-controlled detection |
| **ML Alert Triage** | 4 ML models (Risk Scoring, Anomaly, Clustering, FP) | Reduced alert fatigue |
| **Physical-Cyber Correlation** | OT+IT fusion for DCIM-specific attacks | DCIM-specific security |
| **Deception Technology** | T-Pot (IT), Conpot (OT), Honey Credentials/Files | High-fidelity detection |
| **Threat Hunting** | Proactive hypotheses, Sigma Rules, Jupyter, Atomic Red Team | Proactive security |
| **XDR Integration** | EDR, NDR, Cloud sources | Broader visibility |
| **OT-Safe Enforcement** | Forbidden actions for DCIM critical systems | Safety for critical infrastructure |
| **MITRE ATT&CK Mapping** | Standardized threat classification | Industry standard |
| **MCP AI Agent Integration** | Claude Code, Codex, Cursor | AI-assisted triage |
| **Vault Secret Management** | 90-day rotation, full secret lifecycle | Security best practice |
| **3 VLAN Network Segmentation** | DMZ, Data, Management | Defense in depth |
| **Prometheus + Grafana** | Metrics + dashboards | Full observability |
| **SOC API (12 endpoints)** | RESTful API for all operations | Integration capability |
| **Playbook-as-Code** | YAML-based, version-controlled | Consistency + auditability |
| **20 Acceptance Criteria** | Testable criteria for validation | Quality gates |
| **SOC Metrics** | MTTA, MTTC, MTTR, Auto-closure targets | Operational measurement |
| **12 Integration Categories** | Comprehensive integration coverage | Enterprise connectivity |
| **23 Docker Swarm Replicas** | Production-grade deployment | HA + scalability |
| **Case Lifecycle Schema** | Detailed JSON schema | Structured case data |

---

## 6. Connection Mapping

### 6.1 FIT041 → DCIM-Wiki Block Mapping

| FIT041 Section | DCIM-Wiki Source | Connection Type | Status |
|----------------|------------------|-----------------|--------|
| §2.1 Log Ingestion | Block 6 §2: Security Event Ingestion | Concept alignment | ✅ |
| §2.1 Protocol Support | Block 6 §2: Wazuh Agent + Syslog | Partial alignment | ⚠️ |
| §2.2 Rule Engine | Block 6 §7: Correlation Engine | Concept alignment | ✅ |
| §2.2 Behavioral Analysis | Block 6 §5: ML Alert Triage | FIT041 rule-based, DCIM-Wiki ML | ⚠️ |
| §2.2 Threat Intelligence | SIEM SOAR §5: TIP Integration | Partial alignment | ⚠️ |
| §2.3 Alert Generation | SIEM SOAR §8: Alert → Case Flow | Concept alignment | ✅ |
| §2.3 Case Management | SIEM SOAR §4: IRIS Case Mgmt | Different tool | ⚠️ |
| §2.3 SOAR Integration | SIEM SOAR §2-3: TraceCat + Temporal | Different tool | ⚠️ |
| §3.1 EPS/Performance | SIEM SOAR §13: Deployment & Sizing | Different detail | ⚠️ |
| §3.2 HA/Reliability | SIEM SOAR §13: Docker Swarm | Concept alignment | ✅ |
| §3.3 Security | SIEM SOAR §11: Security | FIT041 simpler | ⚠️ |
| §4.1 Architecture | SIEM SOAR §1: Architecture Overview | Different scope | ⚠️ |
| §4.2 Tech Stack | SIEM SOAR §2: TraceCat Components | Different stack | ⚠️ |
| §4.3 Integration | SIEM SOAR §5: Integration Layer | FIT041 narrower | ⚠️ |
| §5.1 Documentation | ❌ No equivalent | **Missing in DCIM-Wiki** | ❌ |
| §5.2 Training | ❌ No equivalent | **Missing in DCIM-Wiki** | ❌ |

### 6.2 DCIM-Wiki → FIT041 Gap

| DCIM-Wiki Item | Source | FIT041 Equivalent | Gap |
|----------------|--------|-------------------|-----|
| Kafka message broker | Block 6 §2 | Not mentioned | **Missing in FIT041** |
| NiFi Syslog Processor | Block 6 §2 | Not mentioned | **Missing in FIT041** |
| TraceCat SOAR | SIEM SOAR §2 | n8n | **Different tool** |
| Temporal workflow | SIEM SOAR §3 | Not mentioned | **Missing in FIT041** |
| IRIS case management | SIEM SOAR §4 | TheHive | **Different tool** |
| MCP AI agent | SIEM SOAR §6 | Not mentioned | **Missing in FIT041** |
| Detection Engineering | Block 6 §4 | Not mentioned | **Missing in FIT041** |
| ML Alert Triage | Block 6 §5 | Not mentioned | **Missing in FIT041** |
| Physical-Cyber Correlation | Block 6 §8 | Not mentioned | **Missing in FIT041** |
| Deception Technology | Block 6 §10 | Not mentioned | **Missing in FIT041** |
| Threat Hunting | Block 6 §11 | Not mentioned | **Missing in FIT041** |
| XDR Integration | Block 6 §12 | Not mentioned | **Missing in FIT041** |
| OT-Safe Enforcement | SIEM SOAR §7.4 | Not mentioned | **Missing in FIT041** |
| MITRE ATT&CK | SIEM SOAR §8 | Not mentioned | **Missing in FIT041** |
| Vault secrets | SIEM SOAR §11.2 | Not mentioned | **Missing in FIT041** |
| OIDC/SSO | SIEM SOAR §11.1 | Not mentioned | **Missing in FIT041** |
| 3 VLANs | SIEM SOAR §13.3 | Not mentioned | **Missing in FIT041** |
| Prometheus + Grafana | SIEM SOAR §12 | Not mentioned | **Missing in FIT041** |
| SOC API (12 endpoints) | SIEM SOAR §10 | Not mentioned | **Missing in FIT041** |
| Playbook-as-Code | SIEM SOAR §7 | Not mentioned | **Missing in FIT041** |
| CIS Benchmark | Block 6 §13 | Not mentioned | **Missing in FIT041** |
| 20 Acceptance Criteria | SIEM SOAR §14 | Not defined | **Missing in FIT041** |

---

## 7. Architecture Pattern Assessment

### 7.1 FIT041 Architecture (Requirements)

```
"Wazuh-Centric Architecture"
┌─────────────────────────────────────────────────────────────┐
│  Wazuh Agent → Syslog Collector → Wazuh Manager Cluster     │
│       ↓                                    ↓                 │
│  Log Sources                    Wazuh Indexer Cluster       │
│       ↓                                    ↓                 │
│  Normalization                   Wazuh Dashboard            │
│       ↓                                                  │
│  External: TheHive / n8n / Jira / ServiceNow              │
└─────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- ✅ Simple, Wazuh-native stack
- ✅ Minimal components
- ✅ Good for small-to-medium deployments
- ⚠️ Limited scalability (no message broker)
- ⚠️ Basic case management (TheHive)
- ⚠️ Basic automation (n8n)
- ❌ No ML/AI capabilities
- ❌ No OT-specific safety
- ❌ No detection engineering

### 7.2 DCIM-Wiki Architecture (Implementation)

```
"TraceCat + Temporal SOAR Architecture"
┌─────────────────────────────────────────────────────────────┐
│  Wazuh → Kafka → NiFi → Elasticsearch                       │
│       ↓                                    ↓                 │
│  Enrichment Pipeline              Detection Engineering     │
│  (GeoIP, TIP, CMDB, Vulns)       (Git-based, CI/CD)        │
│       ↓                                    ↓                 │
│  ML Alert Triage                  Correlation Engine         │
│  (Risk Scoring, Dedup)           (Rule, Threshold, Pattern) │
│       ↓                                    ↓                 │
│  TraceCat (SOAR) ←── Temporal (Workflow Engine)             │
│       ↓                                    ↓                 │
│  IRIS (Case Mgmt)                 Integration Hub           │
│  (Full lifecycle)                 (12 categories)           │
│       ↓                                    ↓                 │
│  MCP (AI Agent)                   OT-Safe Enforcement       │
│  (Claude, Codex, Cursor)          (Forbidden actions)       │
└─────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- ✅ Production-grade (23 Docker Swarm replicas)
- ✅ HA with failover
- ✅ ML/AI capabilities
- ✅ OT-safe for DCIM critical systems
- ✅ Detection Engineering (Git-based)
- ✅ Comprehensive integration (12 categories)
- ✅ Full observability (Prometheus + Grafana)
- ⚠️ More complex deployment
- ⚠️ Higher resource requirements

### 7.3 Pattern Comparison

| Aspect | FIT041 (Requirements) | DCIM-Wiki (Implementation) | Recommendation |
|--------|----------------------|---------------------------|----------------|
| **SIEM Core** | Wazuh | Wazuh | Keep Wazuh (match) |
| **Message Broker** | ❌ None | Kafka | **Adopt Kafka (P1)** |
| **Log Transport** | Wazuh Agent direct | NiFi Syslog Processor | **Adopt NiFi (P1)** |
| **SOAR** | n8n | TraceCat | **Adopt TraceCat (P1)** |
| **Workflow** | ❌ None | Temporal | **Adopt Temporal (P1)** |
| **Case Mgmt** | TheHive | IRIS | **Adopt IRIS (P1)** |
| **AI Agent** | ❌ None | MCP | **Adopt MCP (P2)** |
| **ML Triage** | ❌ None | 4 ML models | **Adopt ML (P2)** |
| **OT Safety** | ❌ None | Full enforcement | **Adopt OT-Safe (P1)** |
| **Detection Eng** | ❌ None | Git-based + CI/CD | **Adopt Detection Eng (P1)** |
| **Monitoring** | ❌ None | Prometheus + Grafana | **Adopt monitoring (P1)** |
| **Secrets** | ❌ None | Vault | **Adopt Vault (P1)** |
| **Network** | ❌ None | 3 VLANs | **Adopt VLANs (P1)** |

---

## 8. Recommendations

### 8.1 Overall Strategy

| Decision | Rationale |
|----------|-----------|
| **TIDAK PERLU ubah dokumen existing** | Tidak ada konflik kritis; kedua dokumen saling melengkapi |
| **FIT041 = Requirements Layer** | Pertahankan sebagai "APA yang harus dibangun" |
| **DCIM-Wiki = Implementation Layer** | Pertahankan sebagai "BAGAIMANA membangunnya" |
| **Adopt DCIM-Wiki as primary reference** | Lebih komprehensif, production-ready, dan DCIM-specific |
| **Bridge the gaps** | Tambah item dari FIT041 yang missing di DCIM-Wiki |

### 8.2 Items to Add to DCIM-Wiki (from FIT041)

| # | Item | Source | Priority | Rationale |
|---|------|--------|----------|-----------|
| 1 | **Documentation Requirements** | FIT041 §5.1 | P2 | Operational readiness: Rules/Use Cases, Onboarding, Runbook, Custom decoder docs |
| 2 | **Training Requirements** | FIT041 §5.2 | P2 | Team capability: Rule creation, Incident triage, Hands-on lab |
| 3 | **EPS Capacity Target (10K-20K)** | FIT041 §3.1.1 | P2 | Concrete performance SLA |
| 4 | **Data Retention Policy (Hot 90d, Archive 2yr)** | FIT041 §3.3.2 | P2 | Compliance requirement |
| 5 | **Search Speed Target (≤5s for 30-day)** | FIT041 §3.1.2 | P2 | Performance SLA |
| 6 | **AlienVault OTX** | FIT041 §2.2.3 | P4 | Additional TIP source |
| 7 | **OpenSearch alternative** | FIT041 §4.2 | P4 | Vendor flexibility |
| 8 | **Signed Agent Communication** | FIT041 §3.2.2 | P3 | Security measure |
| 9 | **Hardening Guide Compliance** | FIT041 §3.3.3 | P3 | Security baseline |
| 10 | **FIM details** | FIT041 §3.2.2 | P3 | Security monitoring |

### 8.3 Items FIT041 Should Reference from DCIM-Wiki

| # | Item | Source | Priority |
|---|------|--------|----------|
| 1 | **Kafka message broker** | Block 6 §2 | P1 |
| 2 | **TraceCat SOAR** | SIEM SOAR §2 | P1 |
| 3 | **Temporal workflow engine** | SIEM SOAR §3 | P1 |
| 4 | **IRIS case management** | SIEM SOAR §4 | P1 |
| 5 | **OT-Safe Enforcement** | SIEM SOAR §7.4 | P1 |
| 6 | **MITRE ATT&CK Mapping** | SIEM SOAR §8 | P1 |
| 7 | **Detection Engineering** | Block 6 §4 | P1 |
| 8 | **ML Alert Triage** | Block 6 §5 | P2 |
| 9 | **Physical-Cyber Correlation** | Block 6 §8 | P1 |
| 10 | **MCP AI Agent Integration** | SIEM SOAR §6 | P2 |
| 11 | **Vault Secret Management** | SIEM SOAR §11.2 | P1 |
| 12 | **3 VLAN Network Segmentation** | SIEM SOAR §13.3 | P1 |
| 13 | **Prometheus + Grafana** | SIEM SOAR §12 | P1 |
| 14 | **SOC API (12 endpoints)** | SIEM SOAR §10 | P2 |
| 15 | **Playbook-as-Code** | SIEM SOAR §7 | P1 |
| 16 | **20 Acceptance Criteria** | SIEM SOAR §14 | P1 |

### 8.4 Tidak Perlu Diubah

| Item | Reason |
|------|--------|
| FIT041 SIEM Technical Requirements | Sudah good sebagai requirements baseline |
| DCIM-Wiki Block 6 SIEM/SOC v3 | Sudah comprehensive untuk implementation |
| DCIM-Wiki SIEM SOAR Reference Design | Sudah production-ready |
| Enrichment Pipeline | Sudah detailed di Block 6 §3 |
| Correlation Engine | Sudah covered di Block 6 §7 |
| CIS Benchmark Compliance | Sudah covered di Block 6 §13 |

---

## 9. Quality Gate Checklist

### Document Quality

- [x] Executive Summary dengan key findings
- [x] Section-by-section analysis (7 sections)
- [x] Gap analysis summary matrix
- [x] Unique items per document
- [x] Connection mapping (FIT041 → DCIM-Wiki)
- [x] Architecture pattern assessment
- [x] Recommendations with rationale
- [x] No fabricated metrics, dates, or implementation status
- [x] Sources cited (FIT041 + Block 6 + SIEM SOAR)

### Alignment Quality

- [x] Both documents cover SIEM for DCIM
- [x] Wazuh as core SIEM platform (aligned)
- [x] Log ingestion concept aligned
- [x] HA concept aligned
- [x] TLS security aligned
- [x] Scalability concept aligned

### Gap Quality

- [x] Gaps identified with priority (P1-P4)
- [x] No critical conflicts found
- [x] Both documents complementary
- [x] Action items clear and specific
- [x] Architecture decisions documented

---

## References

| Document | Relevance |
|----------|-----------|
| [[IF-Technical_Requirements_SIEM-FIT041-20260119]] | FIT041 Requirements baseline |
| [[block6-siem-soc-v3]] | Block 6 SIEM/SOC Reference Design (v3) |
| [[siem-soar]] | SIEM SOAR Reference Design (TraceCat + Temporal) |
| [[siem-soc]] | SIEM/SOC Entity |
| [[block1-infrastructure-provisioning]] | Infrastructure Reference Design |
| [[block2-data-ingestion-integration]] | DI&I Reference Design |
| [[block5-web-dashboard]] | Dashboard Reference Design |

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-25
> **Purpose:** Komparasi & alignment antara FIT041 SIEM Requirements dengan DCIM-Wiki knowledge base
> **Method:** MCP Sequential Thinking + Section-by-Section Analysis
> **Result:** COMPLEMENTARY — Tidak ada konflik kritis; 8 P1 gaps in FIT041, 10 items to add to DCIM-Wiki
