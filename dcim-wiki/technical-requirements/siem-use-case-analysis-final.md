---
title: "SIEM — Use Case Analysis (Final)"
created: 2026-06-25
updated: 2026-06-25
type: use-case-analysis
status: final
tags: [siem, security, use-case-analysis, wazuh, soar, correlation, compliance, ueba, detection-engineering, ml-triage, physical-cyber, deception, threat-hunting, xdr, soc]
sources:
  - IF-Use_Case_Analysis_SIEM-FIT041-20260121.md
  - block6-siem-soc-v3.md
  - siem-soar.md
  - siem-soar-actual-architecture.md
  - siem-soc.md
  - siem-correlation-rules.md
  - siem-investigation-runbook.md
  - fit041-siem-use-case-komparasi.md
  - fit041-siem-komparasi.md
confidence: high
purpose: >
  FINAL Use Case Analysis untuk SIEM/SOC. Merged dari FIT041 (3 UCs) + DCIM-Wiki (20 UCs).
  7 categories, 20 use cases, 25 API endpoints, 5 SLA tiers, source system matrix,
  data quality requirements, downstream consumers, acceptance criteria.
---

# SIEM — Use Case Analysis (Final)

> **Purpose:** Use Case Analysis komprehensif untuk SIEM/SOC — security event ingestion, detection, correlation, incident response, compliance, advanced threat detection, SOC operations.
> **Sources:** FIT041 Use Case Analysis (3 UCs) + DCIM-Wiki Block 6 v3 + SIEM SOAR Reference Design + SIEM SOAR Actual Architecture + Entity Pages + Concepts
> **Method:** MCP Sequential Thinking (4 steps) + MCP Context7 (Wazuh docs) + dcim-comparison skill
> **Status:** FINAL — merged dari Phase 1 (DCIM-Wiki) + Phase 2 (FIT041 comparison) + Phase 3 (merge)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Use Case Taxonomy](#2-use-case-taxonomy)
3. [Category 1: Security Event Ingestion & Processing](#3-category-1-security-event-ingestion--processing)
4. [Category 2: Detection & Correlation](#4-category-2-detection--correlation)
5. [Category 3: Alert Triage & Enrichment](#5-category-3-alert-triage--enrichment)
6. [Category 4: Incident Response & Case Management](#6-category-4-incident-response--case-management)
7. [Category 5: Physical-Cyber Security](#7-category-5-physical-cyber-security)
8. [Category 6: Advanced Threat Detection](#8-category-6-advanced-threat-detection)
9. [Category 7: Compliance & Audit](#9-category-7-compliance--audit)
10. [Category 8: SOC Operations](#10-category-8-soc-operations)
11. [Source System → Use Case Matrix](#11-source-system--use-case-matrix)
12. [Pipeline Requirements per Use Case](#12-pipeline-requirements-per-use-case)
13. [SLA & Latency Requirements](#13-sla--latency-requirements)
14. [Data Quality Requirements per Use Case](#14-data-quality-requirements-per-use-case)
15. [Downstream Consumer Mapping](#15-downstream-consumer-mapping)
16. [Merge Summary](#16-merge-summary)
17. [Gaps & Recommendations](#17-gaps--recommendations)
18. [Acceptance Criteria](#18-acceptance-criteria)

---

## 1. Executive Summary

| Aspek | Value |
|-------|-------|
| **Total Use Cases** | 20 |
| **Categories** | 8 |
| **API Endpoints** | 25 |
| **SLA Tiers** | 5 (Real-time, Near-RT, Batch, Async, On-demand) |
| **Data Quality Rules** | 15 |
| **Downstream Consumers** | 8 |
| **FIT041 UCs Absorbed** | 3 (Threat Detection → UC1-4, UEBA → UC20, Compliance → UC17) |
| **Acceptance Criteria** | 22 |
| **Architecture** | Wazuh → Kafka → Elasticsearch → Detection → ML Triage → SOAR → IRIS |

### Use Case Categories

| # | Category | UCs | Priority | Processing Mode |
|---|----------|-----|----------|-----------------|
| 1 | Security Event Ingestion & Processing | UC1-UC3 | P1 | Real-time |
| 2 | Detection & Correlation | UC4-UC6 | P1 | Real-time |
| 3 | Alert Triage & Enrichment | UC7-UC8 | P1 | Near-RT |
| 4 | Incident Response & Case Management | UC9-UC12 | P1 | Near-RT |
| 5 | Physical-Cyber Security | UC13-UC14 | P1 | Near-RT |
| 6 | Advanced Threat Detection | UC15-UC16 | P2 | Near-RT |
| 7 | Compliance & Audit | UC17-UC18 | P2 | Batch |
| 8 | SOC Operations | UC19-UC20 | P2 | Mixed |

---

## 2. Use Case Taxonomy

| UC ID | Name | Category | Priority | Processing Mode | SLA Tier | FIT041 Source |
|-------|------|----------|----------|-----------------|----------|---------------|
| UC1 | Security Event Collection & Normalization | Ingestion | P1 | Real-time | Tier 1 (<1s) | — |
| UC2 | Log Decoding & Field Extraction | Ingestion | P1 | Real-time | Tier 1 (<1s) | — |
| UC3 | Security Event Schema & Storage | Ingestion | P1 | Real-time | Tier 1 (<1s) | — |
| UC4 | Correlation Engine | Detection | P1 | Real-time | Tier 1 (<1s) | — |
| UC5 | Detection Engineering (Detection-as-Code) | Detection | P1 | Real-time | Tier 1 (<1s) | — |
| UC6 | MITRE ATT&CK Mapping | Detection | P1 | Batch | Tier 4 (15-60m) | — |
| UC7 | ML Alert Triage | Triage | P2 | Near-RT | Tier 2 (1-30s) | — |
| UC8 | Alert Enrichment Pipeline | Triage | P1 | Near-RT | Tier 2 (1-30s) | — |
| UC9 | Incident Response Workflow | Response | P1 | Near-RT | Tier 2 (1-30s) | — |
| UC10 | SOAR Automated Response | Response | P1 | Near-RT | Tier 2 (1-30s) | — |
| UC11 | Case Management (DFIR-IRIS) | Response | P1 | Near-RT | Tier 2 (1-30s) | — |
| UC12 | Escalation Workflow | Response | P1 | Near-RT | Tier 2 (1-30s) | — |
| UC13 | Physical-Cyber Correlation | Physical | P1 | Near-RT | Tier 2 (1-30s) | — |
| UC14 | Deception Technology (Honeypots) | Physical | P3 | Real-time | Tier 1 (<1s) | — |
| UC15 | Threat Hunting | Advanced | P2 | On-demand | Tier 5 (on-demand) | — |
| UC16 | XDR Integration | Advanced | P2 | Near-RT | Tier 2 (1-30s) | — |
| UC17 | Compliance & Audit Reporting | Compliance | P2 | Batch | Tier 3 (1-5m) | ✅ FIT041 UC3 |
| UC18 | CIS Benchmark Compliance | Compliance | P2 | Batch | Tier 3 (1-5m) | — |
| UC19 | SOC Dashboard & Visualization | Operations | P2 | Real-time | Tier 1 (<1s) | — |
| UC20 | User & Entity Behavior Analytics (UEBA) | Operations | P2 | Near-RT | Tier 2 (1-30s) | ✅ FIT041 UC2 |

---

## 3. Category 1: Security Event Ingestion & Processing

### UC1: Security Event Collection & Normalization

| Aspect | Detail |
|--------|--------|
| **ID** | UC1 |
| **Priority** | P1 |
| **Processing Mode** | Real-time |
| **SLA** | < 1 second from receipt to index |
| **Actor(s)** | Wazuh Agent, Syslog Source, Wazuh Manager |
| **Trigger** | Server/Network/Device mengirim log event |
| **Pre-conditions** | Wazuh Agent terinstall & registered, Wazuh Manager running, Network connectivity |
| **Flow** | 1. Agent kirim raw log via Syslog (TCP/UDP 514) → 2. Wazuh Manager terima & decode → 3. Normalize ke common schema (ECS) → 4. Index ke Elasticsearch (dcim-siem-*) |
| **Alt Flow** | Decode gagal → log masuk quarantine, alert error generated |
| **Postcondition** | Event tersimpan di Elasticsearch, siap untuk visualization, correlation, & forwarding |
| **Success Criteria** | ≥ 99.9% delivery rate, < 1s ingestion latency, zero data loss |

**Source Systems:**

| Source | Protocol | Volume | Enrichment |
|--------|----------|--------|------------|
| Server OS (Linux/Windows) | Wazuh Agent (TCP 1514) | High | CI type, owner, criticality |
| Network Devices | Syslog (TCP/UDP 514) | High | Device type, location |
| Applications | Wazuh Agent / Syslog | Medium | App name, version |
| Cloud Services | API / Syslog | Medium | Cloud region, account |
| OT/DCIM Devices | Syslog / MQTT | Low-Medium | Device type, rack location |

**Data Quality:**

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99.9% (zero data loss) |
| Accuracy | Field-level validation per schema |
| Timeliness | < 1s from source to ES index |
| Consistency | ECS normalization across all sources |
| Validity | Schema validation on ingest |

---

### UC2: Log Decoding & Field Extraction

| Aspect | Detail |
|--------|--------|
| **ID** | UC2 |
| **Priority** | P1 |
| **Processing Mode** | Real-time |
| **SLA** | < 500ms per event |
| **Actor(s)** | Wazuh Manager (analysisd), Decoder Engine |
| **Trigger** | Raw log received from agent/source |
| **Flow** | 1. Wazuh Manager apply decoders (syslog, JSON, Windows event, Apache, etc.) → 2. Extract fields (srcip, dstip, user, program, action) → 3. Map ke ECS schema → 4. Forward ke rule evaluation |

**Decoder Categories:**

| Decoder Type | Source | Example Fields |
|-------------|--------|----------------|
| Syslog | Network devices, Linux servers | program, pid, message |
| JSON | Applications, cloud services | All JSON keys |
| Windows Event | Windows servers | EventID, User, Process |
| Apache/Nginx | Web servers | status, method, url, srcip |
| Custom | DCIM-specific | device_type, rack_id, sensor |

---

### UC3: Security Event Schema & Storage

| Aspect | Detail |
|--------|--------|
| **ID** | UC3 |
| **Priority** | P1 |
| **Processing Mode** | Real-time |
| **SLA** | < 1s write latency |
| **Actor(s)** | Elasticsearch, Index Lifecycle Manager |
| **Trigger** | Normalized event ready for storage |
| **Flow** | 1. Write to Elasticsearch index (dcim-siem-*) → 2. Apply index lifecycle (Hot → Warm → Cold → Delete) → 3. Replicate (RF=1 single-node, RF=2 cluster) |

**Index Lifecycle:**

| Tier | Duration | Storage | Action |
|------|----------|---------|--------|
| Hot | 0-7 days | SSD | Active queries |
| Warm | 7-30 days | HDD | Read-only, force merge |
| Cold | 30-90 days | HDD | Compressed, frozen |
| Delete | 90+ days | — | Purge |

---

## 4. Category 2: Detection & Correlation

### UC4: Correlation Engine

| Aspect | Detail |
|--------|--------|
| **ID** | UC4 |
| **Priority** | P1 |
| **Processing Mode** | Real-time |
| **SLA** | < 30s from event to alert |
| **Actor(s)** | Wazuh Rules Engine, Correlation Engine |
| **Trigger** | Normalized event matches detection rule |
| **Pre-conditions** | Detection rules active (custom + built-in), correlation rules configured |
| **Flow** | 1. Apply rule-based detection → 2. Apply threshold detection (frequency, timeframe) → 3. Apply pattern detection (sequence, cross-source) → 4. Generate alert with severity level → 5. Forward to Elasticsearch for storage & visualization |
| **Success Criteria** | < 30s alert generation latency, < 5% false positive rate |

**Correlation Rule Types:**

| Rule Type | Example | Detection |
|-----------|---------|-----------|
| Threshold | 5 failed logins in 1 min | Brute force |
| Frequency | Same IP, 10 events in 5 min | Scan/attack |
| Pattern | Failed login → successful login → privilege escalation | Chained attack |
| Cross-source | Door access + network scan from same subnet | Physical-cyber |
| Custom | Mimikatz process execution | Malware |

**Alert Priority Levels:**

| Level | Severity | Description | Action |
|-------|----------|-------------|--------|
| 1-3 | Low | Informational, no action | Log only |
| 4-6 | Medium | Suspicious activity | ElastAlert → Tracecat |
| 7-9 | High | Confirmed threat | ElastAlert → Tracecat (priority) |
| 10-12 | Critical | Active attack | ElastAlert → Tracecat → DFIR-IRIS |

**MITRE ATT&CK Mapping (per UC6):**

| Tactic | Technique | Rule Category |
|--------|-----------|---------------|
| Initial Access | T1190 (Exploit Public App) | Web server rules |
| Execution | T1059 (Command & Script) | Process monitoring |
| Persistence | T1053 (Scheduled Task) | FIM rules |
| Privilege Escalation | T1068 (Exploitation) | System rules |
| Credential Access | T1110 (Brute Force) | Auth rules |
| Discovery | T1046 (Network Scan) | Network rules |
| Lateral Movement | T1021 (Remote Services) | SMB/RDP rules |
| Exfiltration | T1041 (Exfil Over C2) | Network rules |

---

### UC5: Detection Engineering (Detection-as-Code)

| Aspect | Detail |
|--------|--------|
| **ID** | UC5 |
| **Priority** | P1 |
| **Processing Mode** | Real-time (rules), Batch (CI/CD) |
| **SLA** | < 24h from rule creation to production |
| **Actor(s)** | Detection Engineer, CI/CD Pipeline, Git Repository |
| **Trigger** | New threat identified, rule update needed, new source onboarded |
| **Pre-conditions** | Git repository configured, CI/CD pipeline active, staging environment ready |
| **Flow** | 1. Write detection rule (YAML) → 2. Commit to Git → 3. CI validates (syntax, MITRE mapping, FP test) → 4. Staging deployment (7-day soak) → 5. Peer review (2 analysts min) → 6. Production promotion |
| **Success Criteria** | < 24h rule-to-production, > 70% ATT&CK coverage, 0 production incidents from bad rules |

**Detection Rule Format:**

```yaml
name: Brute Force Detection
id: 100001
version: 2
status: production
severity: high
mitre_attack:
  - tactic: credential-access
    technique: T1110
sources:
  - wazuh
detection:
  selection:
    event_type: failed_login
  condition: selection | count() by srcip >= 5 within 60s
false_positives:
  - Legitimate admin testing
  - Automated monitoring tools
```

**Rule Categories (Target):**

| Category | Count Target | Priority |
|----------|-------------|----------|
| Endpoint Detection | 150+ | P1 |
| Network Detection | 100+ | P1 |
| Identity Detection | 60+ | P1 |
| Cloud Detection | 80+ | P2 |
| OT/IoT Detection | 50+ | P2 |
| Application Detection | 40+ | P3 |
| **Total** | **480+** | — |

---

### UC6: MITRE ATT&CK Mapping

| Aspect | Detail |
|--------|--------|
| **ID** | UC6 |
| **Priority** | P1 |
| **Processing Mode** | Batch |
| **SLA** | Monthly coverage review |
| **Actor(s)** | Detection Engineer, Compliance Officer |
| **Trigger** | Monthly review, new ATT&CK techniques released |
| **Flow** | 1. Map existing rules to ATT&CK matrix → 2. Identify coverage gaps → 3. Prioritize new rules for uncovered techniques → 4. Generate coverage report → 5. Track progress over time |

---

## 5. Category 3: Alert Triage & Enrichment

### UC7: ML Alert Triage

| Aspect | Detail |
|--------|--------|
| **ID** | UC7 |
| **Priority** | P2 |
| **Processing Mode** | Near-RT |
| **SLA** | < 30s triage latency |
| **Actor(s)** | ML Triage Engine, SOC Analyst (feedback loop) |
| **Trigger** | New alert generated by correlation engine |
| **Pre-conditions** | ML models trained & deployed, labeled data available for retraining |
| **Flow** | 1. Receive alert → 2. Extract features (asset criticality, vuln score, threat intel match, user risk, geo risk, time risk, frequency) → 3. Run 4 models (Risk Scoring, Anomaly Detection, Alert Clustering, FP Prediction) → 4. Assign risk score (0-100) → 5. Route based on score |
| **Success Criteria** | > 90% risk scoring accuracy, > 95% FP prediction accuracy, < 20% alert fatigue reduction target |

**ML Models:**

| Model | Type | Purpose | Accuracy Target |
|-------|------|---------|-----------------|
| Risk Scoring | Gradient Boosting | Risk score 0-100 | > 90% |
| Anomaly Detection | Isolation Forest | Behavioral anomalies | > 85% |
| Alert Clustering | DBSCAN | Deduplication | > 80% |
| FP Prediction | Logistic Regression | False positive prediction | > 95% |

**Risk Score Routing:**

| Risk Score | Action | Target |
|------------|--------|--------|
| 0-30 | Auto-close (log only) | — |
| 31-60 | Queue for L1 review | SOC L1 |
| 61-80 | Escalate to L2 | SOC L2 |
| 81-100 | Immediate escalation + SOAR | SOC L2 + SOAR |

---

### UC8: Alert Enrichment Pipeline

| Aspect | Detail |
|--------|--------|
| **ID** | UC8 |
| **Priority** | P1 |
| **Processing Mode** | Near-RT |
| **SLA** | < 60s total enrichment |
| **Actor(s)** | Enrichment Service, AbuseIPDB, VirusTotal, GeoIP, CMDB, MISP |
| **Trigger** | Alert forwarded from ElastAlert to Tracecat |
| **Pre-conditions** | API keys configured (AbuseIPDB, VirusTotal), CMDB accessible, GeoIP DB loaded |
| **Flow** | 1. Receive alert → 2. Query AbuseIPDB (source IP reputation) → 3. Query VirusTotal (file hash scan) → 4. Query GeoIP (IP geolocation) → 5. Query CMDB (asset context: CI type, owner, criticality) → 6. Query MISP (threat intel match) → 7. AI Agent generate summary + recommendations → 8. Attach enrichment to alert |
| **Success Criteria** | < 60s total enrichment, ≥ 95% enrichment coverage |

**Enrichment Sources:**

| Source | Type | Latency | Data |
|--------|------|---------|------|
| AbuseIPDB | IP reputation | < 5s | Abuse confidence, country, ISP, reports |
| VirusTotal | File hash scan | < 10s | Malware detection, reputation, file type |
| GeoIP (MaxMind) | IP geolocation | < 10ms | Country, city, coordinates, ASN |
| CMDB | Asset context | < 20ms | CI type, owner, criticality, location |
| MISP | Threat intel | < 50ms | IOC match, threat level, tags |
| User Context (AD) | Identity | < 15ms | User role, department, risk score |

**Enrichment Schema:**

```json
{
  "enrichment": {
    "abuseipdb": {
      "abuse_confidence": 85,
      "country_code": "XX",
      "isp": "Malicious ISP",
      "total_reports": 150
    },
    "virustotal": {
      "malicious": 45,
      "suspicious": 5,
      "reputation": -85
    },
    "geoip": {
      "country": "ID",
      "city": "Jakarta",
      "asn": "AS17974"
    },
    "asset": {
      "ci_id": "CI-SERVER-001",
      "criticality": "P1",
      "owner": "IT-Infrastructure",
      "location": "DC-Jakarta-Rack-A1"
    },
    "threat_intel": {
      "misp_event_id": "12345",
      "threat_level": "high",
      "tags": ["apt28", "phishing"]
    },
    "ai_analysis": {
      "summary": "Multiple failed login attempts from known malicious IP...",
      "recommendations": ["Block IP", "Check accounts", "Review SSH logs"],
      "severity_assessment": "HIGH",
      "mitre_attack": {
        "tactic": "credential-access",
        "technique": "T1110"
      }
    }
  }
}
```

---

## 6. Category 4: Incident Response & Case Management

### UC9: Incident Response Workflow

| Aspect | Detail |
|--------|--------|
| **ID** | UC9 |
| **Priority** | P1 |
| **Processing Mode** | Near-RT |
| **SLA** | MTTA < 15 min, MTTC < 30 min, MTTR < 4 hours |
| **Actor(s)** | SOC Analyst, SOC Manager, Incident Commander |
| **Trigger** | Enriched alert requires investigation |
| **Pre-conditions** | DFIR-IRIS running, escalation matrix configured, playbooks available |
| **Flow** | 1. Receive enriched alert → 2. Classify severity (S1-S4) → 3. Assign analyst → 4. Investigate (collect evidence, analyze timeline) → 5. Contain (block IP, isolate host) → 6. Remediate → 7. Document findings → 8. Close incident |
| **Success Criteria** | MTTA < 15 min, MTTC < 30 min, MTTR < 4 hours, PIR completed for all S1/S2 |

**Incident Severity:**

| Severity | Meaning | Response |
|----------|---------|----------|
| S1 Critical | Total failure or P1 source failure | Immediate triage + escalation |
| S2 High | P2 failure or major degradation | Fast owner assignment |
| S3 Medium | Persistent latency, sync issue | Planned remediation |
| S4 Low | Ad-hoc report, minor request | Normal queue |

---

### UC10: SOAR Automated Response

| Aspect | Detail |
|--------|--------|
| **ID** | UC10 |
| **Priority** | P1 |
| **Processing Mode** | Near-RT |
| **SLA** | < 60s playbook execution |
| **Actor(s)** | Tracecat SOAR, Playbook Engine, Temporal Workflow |
| **Trigger** | Alert enriched + AI analysis complete |
| **Pre-conditions** | Tracecat running, playbooks configured, enrichment APIs available |
| **Flow** | 1. Receive enriched alert → 2. Execute playbook (YAML-based) → 3. Enrichment (AbuseIPDB + VirusTotal) → 4. AI Agent analysis → 5. Auto-containment (if Critical) → 6. Create incident in DFIR-IRIS → 7. Notify SOC team |
| **OT-Safe Rule** | ⚠️ NO auto-reboot/patch for DCIM critical systems. Approval required for P1 assets. |

**Playbook Actions:**

| Category | Actions | Safety |
|----------|---------|--------|
| Auto-Containment | Block IP, isolate host, disable user | Requires approval for P1 assets |
| Enrichment | Query TIP, CMDB, GeoIP | Always safe |
| Notification | Email, Slack, Teams, SMS | Always safe |
| Ticketing | Create/update ITSM ticket | Always safe |
| Forensics | Collect logs, memory dump, PCAP | Read-only, safe |
| Remediation | Reset password, revoke token | ⚠️ No reboot for DCIM |

---

### UC11: Case Management (DFIR-IRIS)

| Aspect | Detail |
|--------|--------|
| **ID** | UC11 |
| **Priority** | P1 |
| **Processing Mode** | Near-RT |
| **SLA** | < 120s incident creation latency |
| **Actor(s)** | SOC Analyst, DFIR-IRIS System |
| **Trigger** | SOAR creates enriched incident |
| **Flow** | 1. Tracecat POST enriched incident → 2. DFIR-IRIS create incident (status: New) → 3. Auto-assign to SOC queue → 4. SOC analyst investigate → 5. Document findings → 6. Resolve & close |

**Incident Lifecycle:**

```
New → Assigned → Investigating → Resolved → Closed
                                            ↕
                                    Reopened / Escalated
```

**Incident Metrics:**

| Metric | Target |
|--------|--------|
| MTTA (Mean Time to Acknowledge) | < 15 min |
| MTTC (Mean Time to Contain) | < 30 min |
| MTTR (Mean Time to Resolve) | < 4 hours |
| Auto-closure Rate | > 60% |
| Escalation Rate | < 25% |

---

### UC12: Escalation Workflow

| Aspect | Detail |
|--------|--------|
| **ID** | UC12 |
| **Priority** | P1 |
| **Processing Mode** | Near-RT |
| **SLA** | < 5 min escalation notification |
| **Actor(s)** | SOC Analyst, SOC Manager, CISO |
| **Trigger** | SLA breach, complexity threshold, P1/P2 asset |
| **Flow** | 1. Analyst identify escalation need → 2. Escalate to L2/L3 → 3. SOC Manager assign → 4. Notify stakeholder → 5. Track timeline |

**Escalation Matrix:**

| Level | Role | Trigger |
|-------|------|---------|
| L1 | SOC Analyst | Initial triage |
| L2 | Security Engineer | Complex investigation, P1/P2 assets |
| L3 | CISO / Incident Commander | S1 Critical, executive notification |

---

## 7. Category 5: Physical-Cyber Security

### UC13: Physical-Cyber Correlation

| Aspect | Detail |
|--------|--------|
| **ID** | UC13 |
| **Priority** | P1 |
| **Processing Mode** | Near-RT |
| **SLA** | < 30s correlation window |
| **Actor(s)** | Correlation Engine, OT Sensors, Access Control, BMS |
| **Trigger** | Physical alert + Cyber alert from same asset/subnet/timeframe |
| **Pre-conditions** | Physical sources connected (access control, CCTV, environmental), Cyber sources active |
| **Flow** | 1. Receive physical alert (door access, temp spike, power event) → 2. Receive cyber alert (network scan, brute force, malware) → 3. Correlate by asset/subnet/timeframe → 4. Generate combined alert → 5. Create incident if confirmed |

**Correlation Scenarios:**

| Scenario | Physical Alert | Cyber Alert | Correlation |
|----------|----------------|-------------|-------------|
| Physical Intrusion + Network Scan | Door access after hours | Port scan from same subnet | High |
| Power Manipulation | UPS bypass activated | PDU firmware change attempt | Critical |
| Cooling Attack | Temperature spike | BMS credentials brute force | High |
| Environmental Anomaly | Water leak sensor | BMS system compromised | Critical |
| Access Control Bypass | Badge cloned detection | Lateral movement detected | High |

---

### UC14: Deception Technology (Honeypots)

| Aspect | Detail |
|--------|--------|
| **ID** | UC14 |
| **Priority** | P3 |
| **Processing Mode** | Real-time |
| **SLA** | < 1s alert on honeypot access |
| **Actor(s)** | T-Pot (IT), Conpot (OT), Custom Honey Credentials |
| **Trigger** | Any access to honeypot (99% confidence — all access is suspicious) |
| **Flow** | 1. Deploy honeypots (DMZ + Internal + OT) → 2. Monitor for access → 3. Alert on any interaction → 4. Capture forensics → 5. Isolate source → 6. Notify SOC |

**Honeypot Types:**

| Type | Platform | Purpose | Deployment |
|------|----------|---------|------------|
| IT Honeypot | T-Pot | Detect lateral movement | DMZ + Internal |
| OT Honeypot | Conpot | Detect OT reconnaissance | OT Network |
| Honey Credentials | Custom | Detect credential theft | Domain Controllers |
| Honey Files | Custom | Detect data exfiltration | File Servers |

---

## 8. Category 6: Advanced Threat Detection

### UC15: Threat Hunting

| Aspect | Detail |
|--------|--------|
| **ID** | UC15 |
| **Priority** | P2 |
| **Processing Mode** | On-demand |
| **SLA** | < 24h mean time to hunt |
| **Actor(s)** | SOC Hunter (L2/L3), Data Analyst |
| **Trigger** | Proactive schedule, threat intel, anomaly signal |
| **Pre-conditions** | Historical logs available in ES, hunting tools configured |
| **Flow** | 1. Formulate hypothesis → 2. Query Elasticsearch (ad-hoc) → 3. Analyze patterns → 4. Identify IoC → 5. Create incident if confirmed → 6. Update detection rules |

**Hunting Hypotheses:**

| Hypothesis | Data Sources | Queries | Frequency |
|------------|--------------|---------|-----------|
| Lateral Movement | Endpoint, Network | Unusual SMB, RDP, WMI | Daily |
| Data Exfiltration | Network, DLP | Large transfers, DNS tunneling | Daily |
| Persistence | Endpoint | Scheduled tasks, registry, services | Weekly |
| Privilege Escalation | Identity, Endpoint | Unusual sudo, admin group changes | Daily |
| C2 Communication | Network, DNS | Beaconing, unusual DNS patterns | Daily |

**Hunting Metrics:**

| Metric | Target |
|--------|--------|
| Hunting Queries/Week | > 50 |
| New Detections from Hunting | > 5/month |
| ATT&CK Coverage | > 70% |
| Mean Time to Hunt | < 24h |

---

### UC16: XDR Integration

| Aspect | Detail |
|--------|--------|
| **ID** | UC16 |
| **Priority** | P2 |
| **Processing Mode** | Near-RT |
| **SLA** | < 30s data normalization |
| **Actor(s)** | XDR Adapters, EDR (CrowdStrike, SentinelOne), NDR (Zeek, Suricata), Cloud (GuardDuty, Sentinel) |
| **Trigger** | New event from XDR source |
| **Flow** | 1. Receive event from EDR/NDR/Cloud → 2. Normalize to ECS → 3. Store in ES (xdr-* indices) → 4. Correlate with SIEM events → 5. Dashboard visualization |

**XDR Sources:**

| Source | Type | Data | Integration |
|--------|------|------|-------------|
| CrowdStrike Falcon | EDR | Endpoint telemetry | API polling |
| SentinelOne | EDR | Endpoint events | Webhook |
| Zeek | Network | Network metadata | Kafka |
| Suricata | NDR | IDS alerts | Syslog |
| AWS GuardDuty | Cloud | Cloud findings | SQS → Lambda |
| Azure Sentinel | Cloud | Cloud alerts | API |

---

## 9. Category 7: Compliance & Audit

### UC17: Compliance & Audit Reporting

| Aspect | Detail |
|--------|--------|
| **ID** | UC17 |
| **Priority** | P2 |
| **Processing Mode** | Batch |
| **SLA** | < 5 min report generation |
| **Actor(s)** | Auditor, Compliance Officer, Reporting Engine |
| **Trigger** | Scheduled audit (quarterly) or ad-hoc request |
| **Pre-conditions** | Log retention policy active, reporting templates configured |
| **Flow** | 1. Compliance Officer request report → 2. Query log repository → 3. Format raw logs → 4. Verify with Workflow Automation → 5. Export to audit file share |
| **Success Criteria** | 100% data completeness in reports, < 5 min generation time |

> **FIT041 Traceability:** FIT041 UC3 (Compliance & Audit Reporting) — Actors: Auditor, Compliance Officer, SIEM Reporting Engine. Pre-conditions: Log retention active, reporting templates configured. Flow: Request → Data Retrieval → Report Generation → Verification → Output. Success Criteria: 100% data completeness.

**Compliance Standards:**

| Standard | Scope | Report Types |
|----------|-------|--------------|
| ISO 27001 | Information Security | Access events, change events, audit trails |
| SOC 2 | Service Organization | Security, availability, processing integrity |
| PCI DSS | Payment Card | Cardholder data access, network segmentation |
| GDPR | Data Protection | Data access, processing, deletion |

---

### UC18: CIS Benchmark Compliance

| Aspect | Detail |
|--------|--------|
| **ID** | UC18 |
| **Priority** | P2 |
| **Processing Mode** | Batch |
| **SLA** | < 1 hour full scan |
| **Actor(s)** | CIS Scanner, Compliance Engine, SOC Analyst |
| **Trigger** | Daily scan schedule or policy change |
| **Flow** | 1. Run CIS benchmark scan → 2. Compare against baseline → 3. Identify gaps → 4. Generate remediation recommendations → 5. Track compliance score over time |

**CIS Standards Supported:**

| Standard | Scope | Scan Frequency |
|----------|-------|----------------|
| CIS Windows Server 2022 | Servers | Daily |
| CIS RHEL 8/9 | Linux Servers | Daily |
| CIS Docker | Containers | Daily |
| CIS Kubernetes | Orchestration | Daily |
| CIS AWS/Azure/GCP | Cloud | Daily |

---

## 10. Category 8: SOC Operations

### UC19: SOC Dashboard & Visualization

| Aspect | Detail |
|--------|--------|
| **ID** | UC19 |
| **Priority** | P2 |
| **Processing Mode** | Real-time |
| **SLA** | < 3s dashboard load |
| **Actor(s)** | SOC Analyst, SOC Manager |
| **Trigger** | SOC team access dashboard |
| **Flow** | 1. Open Kibana dashboard → 2. View real-time alert volume → 3. View severity distribution → 4. Drill-down to specific alerts → 5. View threat map (geographic) → 6. View compliance score |

**Dashboard Views:**

| View | Purpose | Refresh |
|------|---------|---------|
| Alert Overview | Real-time alert volume, severity | Real-time |
| Threat Map | Geographic visualization of attacks | Real-time |
| Compliance Score | CIS benchmark status | Daily |
| SOC Metrics | MTTA, MTTC, MTTR | Real-time |
| XDR View | Cross-source event correlation | Real-time |

---

### UC20: User & Entity Behavior Analytics (UEBA)

| Aspect | Detail |
|--------|--------|
| **ID** | UC20 |
| **Priority** | P2 |
| **Processing Mode** | Near-RT |
| **SLA** | < 30s anomaly detection |
| **Actor(s)** | UEBA Engine, User Accounts, Servers/VMs |
| **Trigger** | User/entity action deviates from historical baseline |
| **Pre-conditions** | Behavioral baselines established (learning phase complete), CMDB integration active |
| **Flow** | 1. Ingest user/entity activity logs → 2. Compare against historical baseline (time, location, volume, frequency) → 3. Statistical model assign risk score → 4. If risk score > 80, enrich with CMDB asset context → 5. Generate "Insider Threat Anomaly" alert |
| **Success Criteria** | Risk score > 80 flagged, < 5% false positive rate |

> **FIT041 Traceability:** FIT041 UC2 (User & Entity Behavior Analytics) — Actors: User Accounts, Servers/VMs, SIEM Behavior Engine. Pre-conditions: Learning phase complete for behavioral baselines. Flow: Data Ingestion → Baseline Comparison → Scoring → CMDB Integration → Output. Success Criteria: Risk score > 80 flagged without excessive false positives.

**UEBA Baseline Dimensions:**

| Dimension | Baseline Source | Anomaly Threshold |
|-----------|----------------|-------------------|
| Login Time | Historical pattern | Off-hours deviation |
| Login Location | GeoIP history | New country/city |
| Data Volume | Transfer history | > 2x normal |
| Access Pattern | Resource access log | New resource access |
| Process Execution | Process history | Unknown process |

---

## 11. Source System → Use Case Matrix

| Source System | UC1 | UC2 | UC3 | UC4 | UC5 | UC7 | UC8 | UC13 | UC16 | UC20 |
|--------------|-----|-----|-----|-----|-----|-----|-----|------|------|------|
| Wazuh Agent (Server) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | ✅ |
| Wazuh Agent (Network) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Syslog (Devices) | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | — | — | — |
| Elasticsearch | — | — | ✅ | ✅ | — | — | — | — | — | — |
| AbuseIPDB | — | — | — | — | — | — | ✅ | — | — | — |
| VirusTotal | — | — | — | — | — | — | ✅ | — | — | — |
| GeoIP (MaxMind) | — | — | — | — | — | — | ✅ | — | — | — |
| CMDB | — | — | — | — | — | — | ✅ | ✅ | — | ✅ |
| MISP (Threat Intel) | — | — | — | — | — | — | ✅ | — | — | — |
| Access Control (OT) | — | — | — | — | — | — | — | ✅ | — | — |
| BMS / Environmental | — | — | — | — | — | — | — | ✅ | — | — |
| CrowdStrike / SentinelOne | — | — | — | — | — | — | — | — | ✅ | — |
| Zeek / Suricata | — | — | — | — | — | — | — | — | ✅ | — |
| AWS GuardDuty / Azure | — | — | — | — | — | — | — | — | ✅ | — |
| Active Directory / IAM | — | — | — | — | — | — | ✅ | — | — | ✅ |
| T-Pot / Conpot (Honeypots) | — | — | — | — | — | — | — | — | — | — |

---

## 12. Pipeline Requirements per Use Case

| Use Case | Mode | Kafka Topics (read) | Kafka Topics (write) | Consumer |
|----------|------|--------------------|--------------------|----------|
| UC1-3 (Ingestion) | Real-time | — | `dcim.siem.events` | ES Indexer |
| UC4-6 (Detection) | Real-time | `dcim.siem.events` | `dcim.siem.alerts` | Correlation Engine |
| UC7 (ML Triage) | Near-RT | `dcim.siem.alerts` | `dcim.siem.triaged` | ML Service |
| UC8 (Enrichment) | Near-RT | `dcim.siem.triaged` | `dcim.siem.enriched` | SOAR (Tracecat) |
| UC9-12 (Response) | Near-RT | `dcim.siem.enriched` | `dcim.siem.incidents` | DFIR-IRIS |
| UC13 (Physical-Cyber) | Near-RT | `dcim.physical.events`, `dcim.siem.events` | `dcim.siem.correlated` | Correlation Engine |
| UC14 (Deception) | Real-time | — | `dcim.siem.deception` | SOAR |
| UC16 (XDR) | Near-RT | `dcim.xdr.events` | `dcim.siem.events` | ES Indexer |
| UC20 (UEBA) | Near-RT | `dcim.siem.events` | `dcim.siem.ueba` | Alert Engine |

---

## 13. SLA & Latency Requirements

| SLA Tier | Latency | Use Cases | Processing Mode |
|----------|---------|-----------|-----------------|
| **Tier 1 (Real-time)** | < 1s | UC1-6, UC14, UC19 | Kafka → Stream Processor |
| **Tier 2 (Near-RT)** | 1-30s | UC7-13, UC16, UC20 | Kafka → Consumer |
| **Tier 3 (Batch)** | 1-5 min | UC17-18 | NiFi Scheduled |
| **Tier 4 (Batch)** | 15-60 min | UC6 (MITRE mapping) | Background Jobs |
| **Tier 5 (On-demand)** | Variable | UC15 (Threat Hunting) | Ad-hoc Query |

---

## 14. Data Quality Requirements per Use Case

| Use Case | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| UC1 (Collection) | ≥ 99.9% | Field validation | < 1s | ECS schema | Schema check |
| UC4 (Correlation) | ≥ 99% | Rule accuracy | < 30s | Cross-source | Rule match |
| UC7 (ML Triage) | ≥ 98% | Model accuracy > 90% | < 30s | Feature consistency | Model drift |
| UC8 (Enrichment) | ≥ 95% | API response validation | < 60s | Cross-source | Schema check |
| UC11 (Case Mgmt) | ≥ 100% | Field completeness | < 120s | IRIS schema | Required fields |
| UC13 (Physical-Cyber) | ≥ 99% | Correlation accuracy | < 30s | Cross-domain | Time window |
| UC17 (Compliance) | ≥ 100% | Report accuracy | < 5 min | Audit format | Template match |
| UC20 (UEBA) | ≥ 98% | Model accuracy > 85% | < 30s | Baseline consistency | Threshold check |

---

## 15. Downstream Consumer Mapping

| Use Case | Primary Consumer | Secondary Consumer | Protocol |
|----------|-----------------|-------------------|----------|
| UC1-3 (Ingestion) | Elasticsearch | Kibana | ES API |
| UC4-6 (Detection) | Kibana (Dashboard) | ElastAlert → Tracecat | ES Query |
| UC7 (ML Triage) | SOC Analyst (L1/L2) | — | DFIR-IRIS |
| UC8 (Enrichment) | Tracecat SOAR | DFIR-IRIS | REST API |
| UC9-12 (Response) | DFIR-IRIS | SOC Team (Email/Slack) | REST API / SMTP |
| UC13 (Physical-Cyber) | Tracecat SOAR | DFIR-IRIS | Webhook |
| UC14 (Deception) | Tracecat SOAR | SOC Analyst | Webhook |
| UC15 (Threat Hunting) | SOC Hunter | — | Kibana / Jupyter |
| UC16 (XDR) | Elasticsearch | Kibana (XDR View) | ES API |
| UC17-18 (Compliance) | Auditor | Management | Report Export |
| UC19 (Dashboard) | SOC Team | Management | Kibana Web |
| UC20 (UEBA) | SOC Analyst (L2) | DFIR-IRIS | Alert Engine |

---

## 16. Merge Summary

| FIT041 UC | DCIM-Wiki UC(s) Enriched | Absorption Details |
|-----------|-------------------------|-------------------|
| **FIT041 UC1** (Threat Detection) | UC1, UC2, UC3, UC4, UC5, UC7, UC8 | Actors, triggers, pre-conditions, flow steps, success criteria absorbed into ingestion, detection, triage, enrichment UCs |
| **FIT041 UC2** (UEBA) | UC20 | Complete use case adopted as new UC20 with behavioral baselines, learning phase, risk score threshold |
| **FIT041 UC3** (Compliance) | UC17 | Actors, pre-conditions, flow steps, success criteria absorbed. ISO 27001 + SOC 2 compliance scope added |

### Merge Statistics

| Metric | Value |
|--------|-------|
| FIT041 UCs Absorbed | 3/3 (100%) |
| DCIM-Wiki UCs Total | 20 |
| UCs Enriched by FIT041 | 4 (UC1-3, UC17, UC20) |
| New UCs from FIT041 | 1 (UC20: UEBA) |
| FIT041 Unique Concepts Adopted | 3 (UEBA baselines, compliance breadth, learning phase) |
| Traceability Markers | 2 (UC17, UC20) |

---

## 17. Gaps & Recommendations

### 17.1 P1 Gaps (Must Implement)

| # | Gap | Source | Action |
|---|-----|--------|--------|
| 1 | Kafka HA (single broker RF=1) | v4.2 Architecture | Upgrade to 3-broker cluster, RF=3 |
| 2 | TraceCat SOAR not deployed | Actual Architecture | Deploy TraceCat with Temporal + IRIS |
| 3 | Enrichment Pipeline missing | Block 6 §3 | Implement 6-source enrichment service |
| 4 | Detection Engineering not implemented | Block 6 §4 | Setup Git repo + CI/CD for rules |
| 5 | OT-Safe Enforcement missing | SIEM SOAR Ref §5.4 | Add safety guards to playbooks |
| 6 | MITRE ATT&CK mapping missing | Block 6 §4, §6 | Map all rules to ATT&CK matrix |
| 7 | Physical-Cyber Correlation not built | Block 6 §8 | Connect OT sources (access, BMS, env) |

### 17.2 P2 Gaps (Should Implement)

| # | Gap | Source | Action |
|---|-----|--------|--------|
| 8 | ML Alert Triage not deployed | Block 6 §5 | Train models, deploy triage service |
| 9 | Threat Hunting framework missing | Block 6 §11 | Setup hunting tools, hypotheses library |
| 10 | XDR Integration not configured | Block 6 §12 | Connect EDR/NDR/Cloud sources |
| 11 | SOC API missing | Block 6 §14 | Implement 12 REST endpoints |
| 12 | UEBA baselines not established | FIT041 UC2 | Run learning phase, establish baselines |
| 13 | Compliance scope limited (CIS only) | FIT041 UC3 | Add ISO 27001 + SOC 2 templates |
| 14 | Prometheus + Grafana missing | Block 6 §18 | Deploy monitoring stack |
| 15 | SOC Dashboard views incomplete | Block 6 §19 | Build 5 dashboard views |

### 17.3 P3 Gaps (Nice-to-Have)

| # | Gap | Source | Action |
|---|-----|--------|--------|
| 16 | Deception Technology not deployed | Block 6 §10 | Deploy T-Pot + Conpot honeypots |
| 17 | MCP AI Agent not integrated | SIEM SOAR Ref §6 | Connect LLM for triage assistance |
| 18 | Documentation/Training missing | FIT041 Requirements | Create SOC onboarding guide |

---

## 18. Acceptance Criteria

### Per Use Case

| UC | Acceptance Criteria |
|----|-------------------|
| UC1 | ✅ Event teringest < 1s dari source ke ES index<br>✅ ≥ 99.9% delivery rate<br>✅ Zero data loss |
| UC2 | ✅ Decode accuracy > 99%<br>✅ All 5 decoder types functional<br>✅ ECS schema compliance > 95% |
| UC3 | ✅ Write latency < 1s<br>✅ Index lifecycle active (Hot→Warm→Cold→Delete)<br>✅ Retention policy enforced |
| UC4 | ✅ Alert generation < 30s<br>✅ < 5% false positive rate<br>✅ All 8 correlation rule types functional |
| UC5 | ✅ Rule-to-production < 24h<br>✅ CI/CD pipeline validates all rules<br>✅ > 70% ATT&CK coverage |
| UC6 | ✅ Monthly ATT&CK coverage report generated<br>✅ Gap prioritization complete |
| UC7 | ✅ Risk scoring accuracy > 90%<br>✅ FP prediction accuracy > 95%<br>✅ Alert fatigue reduction > 20% |
| UC8 | ✅ Total enrichment < 60s<br>✅ ≥ 95% enrichment coverage<br>✅ All 6 enrichment sources active |
| UC9 | ✅ MTTA < 15 min<br>✅ MTTC < 30 min<br>✅ MTTR < 4 hours<br>✅ PIR for all S1/S2 |
| UC10 | ✅ Playbook execution < 60s<br>✅ OT-safe enforcement active<br>✅ Zero unauthorized auto-reboot |
| UC11 | ✅ Incident creation < 120s<br>✅ Auto-assign functional<br>✅ Lifecycle states: New→Assigned→Investigating→Resolved→Closed |
| UC12 | ✅ Escalation notification < 5 min<br>✅ 3-level matrix (L1→L2→L3) |
| UC13 | ✅ Correlation window < 30s<br>✅ All 5 scenarios functional<br>✅ OT sources connected |
| UC14 | ✅ Honeypot alert < 1s<br>✅ All 4 honeypot types deployed |
| UC15 | ✅ Mean time to hunt < 24h<br>✅ > 50 hunting queries/week<br>✅ > 5 new detections/month |
| UC16 | ✅ XDR data normalization < 30s<br>✅ ≥ 4 XDR sources connected<br>✅ ECS normalization functional |
| UC17 | ✅ Report generation < 5 min<br>✅ 100% data completeness<br>✅ ISO 27001 + SOC 2 templates |
| UC18 | ✅ Full CIS scan < 1 hour<br>✅ Compliance score tracked daily<br>✅ Remediation recommendations generated |
| UC19 | ✅ Dashboard load < 3s<br>✅ 5 dashboard views functional<br>✅ Real-time refresh |
| UC20 | ✅ Anomaly detection < 30s<br>✅ Risk score > 80 flagged<br>✅ < 5% false positive rate<br>✅ Baseline learning phase complete |

### Cross-Cutting

| Criteria | Target |
|----------|--------|
| Total EPS | ≥ 5,000 (target 10K-20K per FIT041) |
| End-to-end latency (P1) | < 30s |
| Data completeness (P1) | ≥ 99.9% |
| DLQ rate | < 1% |
| Correlation engine uptime | ≥ 99.9% |
| Search speed (30-day) | ≤ 5s |
| Log retention (Hot) | 0-7 days |
| Log retention (Cold) | 30-90 days |
| TLS version | ≥ TLS 1.2 |
| RBAC | All components |
| Secret management | Vault / Kubernetes Secrets |
| Audit trail | All actions logged |

---

**Document Version:** v1.0 (FINAL)
**Last Updated:** 2026-06-25
**Sources Merged:** FIT041 Use Case Analysis (3 UCs) + DCIM-Wiki Block 6 v3 + SIEM SOAR Reference + SIEM SOAR Actual + Entity Pages + Concepts
**Method:** MCP Sequential Thinking (4 steps) + MCP Context7 (Wazuh docs) + dcim-comparison skill
