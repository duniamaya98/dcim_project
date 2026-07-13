---
title: "Block 6 — SIEM/SOC: Reference Design Spec (v3 Improved)"
created: 2026-06-23
updated: 2026-06-25
type: reference-design
block: 6
phase: 2
status: improved
confidence: high
tags: [siem, soc, security, wazuh, correlation, incident-response, compliance, cis-benchmark, ml, xdr, deception, threat-hunting]
wiki_pages:
  - siem-soc
  - data-ingestion-integration
  - elasticsearch
  - workflow-automation
  - web-dashboard
  - siem-investigation-runbook
  - siem-solution-comparison
purpose: >
  Reference design spec untuk Block 6 SIEM/SOC (v3 Improved).
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
  v3 menambahkan Detection Engineering, ML Triage, Enrichment Pipeline, Physical-Cyber Correlation, Deception, Threat Hunting, XDR.
architecture_diagram: diagrams/block6-siem-soc-improved-v3.html
previous_version: diagrams/block6-siem-soc-improved-v2.html
---

# Block 6 — SIEM/SOC: Reference Design Spec (v3 Improved)

> **Purpose:** Dokumen referensi lengkap untuk SIEM/SOC — security event ingestion, correlation, incident response, compliance, dengan peningkatan v3.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi. Setiap gap = connection point.
> **Architecture Diagram:** `diagrams/block6-siem-soc-improved-v3.html`
> **Previous Version:** `diagrams/block6-siem-soc-improved-v2.html`
> **Depends on:** Block 1 (Infrastructure), Block 2 (DI&I)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Security Event Ingestion](#2-security-event-ingestion)
3. [Enrichment Pipeline (NEW v3)](#3-enrichment-pipeline-new-v3)
4. [Detection Engineering (NEW v3)](#4-detection-engineering-new-v3)
5. [ML-Based Alert Triage (NEW v3)](#5-ml-based-alert-triage-new-v3)
6. [Security Event Schema](#6-security-event-schema)
7. [Correlation Engine](#7-correlation-engine)
8. [Physical-Cyber Correlation (NEW v3)](#8-physical-cyber-correlation-new-v3)
9. [Incident Response Workflow](#9-incident-response-workflow)
10. [Deception Technology (NEW v3)](#10-deception-technology-new-v3)
11. [Threat Hunting (NEW v3)](#11-threat-hunting-new-v3)
12. [XDR Integration (NEW v3)](#12-xdr-integration-new-v3)
13. [CIS Benchmark Compliance](#13-cis-benchmark-compliance)
14. [SOC API](#14-soc-api)
15. [Elasticsearch Configuration](#15-elasticsearch-configuration)
16. [Data Retention & Archival](#16-data-retention--archival)
17. [Security](#17-security)
18. [Monitoring & Alerting](#18-monitoring--alerting)
19. [Acceptance Criteria](#19-acceptance-criteria)
20. [Gap Comparison Template](#20-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context (v3)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SIEM/SOC (v3)                                     │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              Security Event Ingestion                                 │  │
│  │  Wazuh Agents → Syslog → Kafka (dcim.siem.events)                   │  │
│  └────────────────────────┬─────────────────────────────────────────────┘  │
│                           │                                                 │
│  ┌────────────────────────┴─────────────────────────────────────────────┐  │
│  │              Enrichment Pipeline (NEW v3)                             │  │
│  │  GeoIP • Threat Intel • CMDB • Vulnerability • User Context          │  │
│  └────────────────────────┬─────────────────────────────────────────────┘  │
│                           │                                                 │
│  ┌────────────────────────┴─────────────────────────────────────────────┐  │
│  │              Detection Engineering (NEW v3)                           │  │
│  │  Git-based Rules • CI/CD Pipeline • MITRE ATT&CK Validation         │  │
│  └────────────────────────┬─────────────────────────────────────────────┘  │
│                           │                                                 │
│  ┌────────────────────────┴─────────────────────────────────────────────┐  │
│  │              Correlation Engine                                       │  │
│  │  Rule-based • Threshold • Pattern • Cross-source                     │  │
│  └────────────────────────┬─────────────────────────────────────────────┘  │
│                           │                                                 │
│  ┌────────────────────────┴─────────────────────────────────────────────┐  │
│  │              ML Alert Triage (NEW v3)                                 │  │
│  │  Risk Scoring • Anomaly Detection • FP Reduction • Deduplication     │  │
│  └────────────────────────┬─────────────────────────────────────────────┘  │
│                           │                                                 │
│              ┌────────────┴────────────┐                                   │
│              ▼                         ▼                                   │
│  ┌───────────────────┐    ┌────────────────────┐                          │
│  │  Alert Engine     │    │ Incident Response  │                          │
│  │  (real-time)      │    │ (workflow)         │                          │
│  └────────┬──────────┘    └────────┬───────────┘                          │
│           │                         │                                      │
│  ┌────────┴──────────┐    ┌────────┴───────────┐                          │
│  │  Elasticsearch    │    │  Workflow Engine   │                          │
│  │  (security store) │    │  (escalation)      │                          │
│  └───────────────────┘    └────────────────────┘                          │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              Physical-Cyber Correlation (NEW v3)                     │  │
│  │  OT+IT Alert Fusion • Environmental Anomaly • Power Impact          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              Deception Technology (NEW v3)                            │  │
│  │  IT Honeypots (T-Pot) • OT Honeypots (Conpot) • High-Fidelity       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              Compliance Engine                                        │  │
│  │  CIS Benchmark • Gap Analysis • Remediation • Continuous Monitoring  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow (v3)

```
Security Sources (servers, network, apps, cloud)
  → Wazuh Agents → Syslog (UDP/TCP 514)
    → NiFi Syslog Processor → Kafka (dcim.siem.events)
      → Enrichment Pipeline (GeoIP, TIP, CMDB, Vulns)
        → Logstash (ECS Normalization)
          → Elasticsearch (dcim-siem-*)
            → Detection Rules (Git-based, CI/CD)
              → ML Alert Triage (Risk Scoring, Dedup)
                → Alerts
                  → Incident Response → Workflow Automation

Physical-Cyber Correlation:
  OT Sources (Power/Cooling/Env) → Physical-Cyber Correlation Engine → Alerts

Deception:
  IT/OT Honeypots → Deception Alerts → SOAR

Compliance Sources → CIS Scanner → Compliance Engine → Reports (Continuous)
```

---

## 3. Enrichment Pipeline (NEW v3)

### 3.1 Purpose

Menambahkan konteks ke security events sebelum detection, mengurangi false positives dan meningkatkan kualitas alert.

### 3.2 Enrichment Sources

| Source | Type | Latency | Data |
|--------|------|---------|------|
| GeoIP (MaxMind) | IP geolocation | <10ms | Country, city, coordinates, ASN |
| Threat Intel (MISP) | IOC enrichment | <50ms | Malicious IPs, domains, hashes |
| CMDB | Asset context | <20ms | CI type, owner, criticality, location |
| Vulnerability (Tenable) | Vuln context | <30ms | CVE, CVSS, exploit availability |
| User Context (AD/IAM) | Identity context | <15ms | User role, department, risk score |
| Passive DNS | DNS history | <25ms | Domain history, related IPs |

### 3.3 Enrichment Schema

```json
{
  "enrichment": {
    "geoip": {
      "country": "ID",
      "city": "Jakarta",
      "asn": "AS17974",
      "coordinates": {"lat": -6.2088, "lon": 106.8456}
    },
    "threat_intel": {
      "misp_event_id": "12345",
      "threat_level": "high",
      "tags": ["apt28", "phishing"]
    },
    "asset": {
      "ci_id": "CI-SERVER-001",
      "criticality": "P1",
      "owner": "IT-Infrastructure",
      "location": "DC-Jakarta-Rack-A1"
    },
    "vulnerability": {
      "cve_count": 3,
      "max_cvss": 9.8,
      "has_exploit": true
    },
    "user": {
      "username": "admin",
      "role": "Domain Admin",
      "department": "IT",
      "risk_score": 85
    }
  }
}
```

### 3.4 Implementation

- **Service:** Python/FastAPI microservice
- **Cache:** Redis (TTL 5min for GeoIP, 1h for CMDB)
- **Integration:** Kafka consumer → Enrichment → Kafka producer (enriched topic)
- **HA:** 2 replicas, load balanced
- **Monitoring:** Latency percentiles, enrichment coverage %

---

## 4. Detection Engineering (NEW v3)

### 4.1 Purpose

Detection-as-Code: version-controlled detection rules dengan CI/CD pipeline untuk konsistensi dan quality assurance.

### 4.2 Detection Rule Format (YAML)

```yaml
# detection-rules/windows/lateral-movement/psexec.yml
name: PsExec Lateral Movement
id: 1001
version: 2
status: production
severity: high
mitre_attack:
  - tactic: lateral-movement
    technique: T1021.002
    sub_technique: Remote Services: SMB/Windows Admin Shares
tags: [windows, lateral-movement, psexec]
authors:
  - name: SOC Team
    email: soc@dcim.example.com

sources:
  - wazuh
  - sysmon

detection:
  selection:
    event_id: 4624
    logon_type: 3
    process_name|contains:
      - 'PSEXESVC.exe'
      - 'psexec'
  condition: selection

false_positives:
  - Administrative tools usage
  - Legitimate remote management

references:
  - https://attack.mitre.org/techniques/T1021/002/

tags:
  - critical-infrastructure
  - data-center
```

### 4.3 CI/CD Pipeline

```
Git Push → CI Pipeline → Validation → Staging → Approval → Production
```

**CI Steps:**
1. YAML syntax validation
2. MITRE ATT&CK mapping validation
3. False positive test cases
4. Performance test (query latency)
5. Coverage analysis (ATT&CK matrix)
6. Peer review (2 analysts minimum)
7. Staging deployment (7-day soak)
8. Production promotion (manual approval)

### 4.4 Rule Categories

| Category | Count (Target) | Priority |
|----------|----------------|----------|
| Endpoint Detection | 150+ | P1 |
| Network Detection | 100+ | P1 |
| Cloud Detection | 80+ | P2 |
| OT/IoT Detection | 50+ | P2 |
| Identity Detection | 60+ | P1 |
| Application Detection | 40+ | P3 |

---

## 5. ML-Based Alert Triage (NEW v3)

### 5.1 Purpose

Mengurangi false positives dan alert fatigue dengan ML-based risk scoring dan deduplication.

### 5.2 ML Models

| Model | Type | Purpose | Accuracy Target |
|-------|------|---------|-----------------|
| Risk Scoring | Gradient Boosting | Risk score 0-100 | >90% |
| Anomaly Detection | Isolation Forest | Behavioral anomalies | >85% |
| Alert Clustering | DBSCAN | Deduplication | >80% |
| FP Prediction | Logistic Regression | False positive prediction | >95% |

### 5.3 Risk Scoring Features

```python
features = {
    "asset_criticality": 0-5,      # From CMDB
    "vulnerability_score": 0-10,   # CVSS score
    "threat_intel_match": 0-1,     # Boolean
    "user_risk_score": 0-100,      # From IAM
    "geo_risk": 0-1,              # Unusual location
    "time_risk": 0-1,             # Off-hours activity
    "frequency": 0-10,            # Alert frequency
    "correlation_count": 0-5      # Related alerts
}
```

### 5.4 Triage Actions

| Risk Score | Action |
|------------|--------|
| 0-30 | Auto-close (log only) |
| 31-60 | Queue for L1 review |
| 61-80 | Escalate to L2 |
| 81-100 | Immediate escalation + SOAR |

### 5.5 Implementation

- **Service:** Python/FastAPI + scikit-learn
- **Model Training:** Weekly retraining on labeled data
- **Feedback Loop:** Analyst feedback improves model
- **Monitoring:** Model drift detection, accuracy metrics

---

## 8. Physical-Cyber Correlation (NEW v3)

### 8.1 Purpose

Menggabungkan alert physical (OT/DCIM) dengan alert cyber untuk mendeteksi sophisticated attacks yang melibatkan both domains.

### 8.2 Correlation Scenarios

| Scenario | Physical Alert | Cyber Alert | Correlation |
|----------|----------------|-------------|-------------|
| Physical Intrusion + Network Scan | Door access after hours | Port scan from same subnet | High |
| Power Manipulation | UPS bypass activated | PDU firmware change attempt | Critical |
| Cooling Attack | Temperature spike | BMS credentials brute force | High |
| Environmental Anomaly | Water leak sensor | BMS system compromised | Critical |
| Access Control Bypass | Badge cloned detection | Lateral movement detected | High |

### 8.3 Correlation Rules

```yaml
name: Physical Intrusion + Network Anomaly
id: PC-001
severity: critical
physical_sources:
  - access_control
  - cctv
  - environmental
cyber_sources:
  - network
  - endpoint
correlation_window: 30m
rules:
  - condition: "door_access_anomaly AND network_scan_same_subnet"
    action: "create_incident"
    priority: "critical"
```

### 8.4 Implementation

- **Service:** Python correlation engine
- **Data Sources:** Kafka topics (dcim.physical.events, dcim.siem.events)
- **Storage:** PostgreSQL for correlation rules, Redis for state
- **Alert:** Webhook to SOAR

---

## 10. Deception Technology (NEW v3)

### 10.1 Purpose

Mendeteksi attacker dengan honeypots sebagai high-fidelity sensors (low false positives).

### 10.2 Honeypot Types

| Type | Platform | Purpose | Deployment |
|------|----------|---------|------------|
| IT Honeypot | T-Pot | Detect lateral movement | DMZ + Internal |
| OT Honeypot | Conpot | Detect OT reconnaissance | OT Network |
| Honey Credentials | Custom | Detect credential theft | Domain Controllers |
| Honey Files | Custom | Detect data exfiltration | File Servers |

### 10.3 Deception Rules

```yaml
name: Honeypot Access Alert
id: DECOY-001
severity: critical
confidence: 99%  # Any access to honeypot is suspicious
action:
  - create_incident
  - capture_forensics
  - isolate_source
  - notify_soc
```

### 10.4 Implementation

- **T-Pot:** Docker-based, multi honeypot
- **Conpot:** ICS/SCADA honeypot for OT
- **Integration:** Kafka → Alert Engine → SOAR
- **Monitoring:** Honeypot health, interaction logs

---

## 11. Threat Hunting (NEW v3)

### 11.1 Purpose

Proactive hunting for threats yang mungkin bypass detection rules.

### 11.2 Hunting Hypotheses

| Hypothesis | Data Sources | Queries | Frequency |
|------------|--------------|---------|-----------|
| Lateral Movement | Endpoint, Network | Unusual SMB, RDP, WMI | Daily |
| Data Exfiltration | Network, DLP | Large transfers, DNS tunneling | Daily |
| Persistence | Endpoint | Scheduled tasks, registry, services | Weekly |
| Privilege Escalation | Identity, Endpoint | Unusual sudo, admin group changes | Daily |
| C2 Communication | Network, DNS | Beaconing, unusual DNS patterns | Daily |

### 11.3 Hunting Tools

- **Kibana:** Ad-hoc queries, visualizations
- **Jupyter Notebooks:** Python-based hunting
- **Sigma Rules:** Portable detection logic
- **Atomic Red Team:** Testing detection coverage

### 11.4 Metrics

| Metric | Target |
|--------|--------|
| Hunting Queries/Week | >50 |
| New Detections from Hunting | >5/month |
| ATT&CK Coverage | >70% |
| Mean Time to Hunt | <24h |

---

## 12. XDR Integration (NEW v3)

### 12.1 Purpose

Extended Detection and Response: mengintegrasikan EDR, NDR, Cloud detection ke SIEM.

### 12.2 Integration Sources

| Source | Type | Data | Integration |
|--------|------|------|-------------|
| CrowdStrike Falcon | EDR | Endpoint telemetry | API polling |
| SentinelOne | EDR | Endpoint events | Webhook |
| Zeek | Network | Network metadata | Kafka |
| Suricata | NDR | IDS alerts | Syslog |
| AWS GuardDuty | Cloud | Cloud findings | SQS → Lambda |
| Azure Sentinel | Cloud | Cloud alerts | API |

### 12.3 Data Normalization

```json
{
  "xdr_event": {
    "source": "crowdstrike",
    "normalized": {
      "event_type": "process_execution",
      "severity": "high",
      "source_ip": "10.0.1.50",
      "user": "admin",
      "process": "mimikatz.exe",
      "hash": "abc123..."
    }
  }
}
```

### 12.4 Implementation

- **Adapters:** Python connectors for each source
- **Normalization:** ECS (Elastic Common Schema)
- **Storage:** Elasticsearch (xdr-* indices)
- **Dashboard:** Kibana XDR view

---

## 13. CIS Benchmark Compliance

### 13.1 Standards Supported

| Standard | Scope | Scan Frequency |
|----------|-------|----------------|
| CIS Windows Server 2022 | Servers | Daily |
| CIS RHEL 8/9 | Linux Servers | Daily |
| CIS Docker | Containers | Daily |
| CIS Kubernetes | Orchestration | Daily |
| CIS AWS/Azure/GCP | Cloud | Daily |

### 13.2 Compliance Dashboard

- Real-time compliance score
- Gap analysis by standard
- Remediation tracking
- Executive reporting

---

## 20. Gap Comparison Template

| Component | v2 Status | v3 Status | Gap | Priority | Owner | ETA |
|-----------|-----------|-----------|-----|----------|-------|-----|
| Detection Engineering | ❌ Missing | ✅ Designed | Implementation | P1 | SOC Team | TBD |
| Enrichment Pipeline | ❌ Missing | ✅ Designed | Implementation | P1 | Platform Team | TBD |
| ML Alert Triage | ❌ Missing | ✅ Designed | Implementation | P2 | Data Science | TBD |
| Physical-Cyber Correlation | ❌ Missing | ✅ Designed | Implementation | P1 | DCIM Team | TBD |
| Deception Technology | ❌ Missing | ✅ Designed | Implementation | P3 | SOC Team | TBD |
| Threat Hunting | ❌ Missing | ✅ Designed | Process Setup | P2 | SOC Team | TBD |
| XDR Integration | ❌ Missing | ✅ Designed | Implementation | P2 | Platform Team | TBD |

---

## v3 Improvement Summary

| Improvement | Benefit | Complexity | Priority |
|-------------|---------|------------|----------|
| Detection Engineering | Consistent, version-controlled rules | Medium | P1 |
| Enrichment Pipeline | Better alert context, fewer FPs | Medium | P1 |
| ML Alert Triage | Reduced alert fatigue, faster triage | High | P2 |
| Physical-Cyber Correlation | DCIM-specific attack detection | High | P1 |
| Deception Technology | High-fidelity attack detection | Medium | P3 |
| Threat Hunting | Proactive threat detection | Medium | P2 |
| XDR Integration | Broader visibility | Medium | P2 |

---

**Document Version:** v3.0
**Last Updated:** 2026-06-25
**Architecture Diagram:** `diagrams/block6-siem-soc-improved-v3.html`
**Previous Version:** `diagrams/block6-siem-soc-improved-v2.html`
