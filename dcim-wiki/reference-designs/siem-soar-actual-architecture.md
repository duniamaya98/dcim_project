---
title: "SIEM SOAR — Arsitektur Design (Current Implementation)"
created: 2026-06-25
updated: 2026-06-25
type: architecture-design
status: current
confidence: high
tags: [siem, soar, wazuh, lme, tracecat, dfir-iris, elastalert, abuseipdb, virustotal, ai-agent, soc]
purpose: >
  Arsitektur design SIEM SOAR berdasarkan implementasi aktual.
  Dokumen ini mendokumentasikan stack, flow, dan integrasi yang sedang berjalan.
---

# SIEM SOAR — Arsitektur Design (Current Implementation)

> **Purpose:** Dokumentasi arsitektur SIEM SOAR berdasarkan stack aktual yang sedang berjalan.
> **Stack:** LME (Wazuh + ES + Kibana + ElastAlert) + Tracecat + DFIR-IRIS
> **Architecture Diagram:** `diagrams/siem-soar-actual-architecture.html`

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Core Stack](#2-core-stack)
3. [Data Flow](#3-data-flow)
4. [LME Stack (SIEM)](#4-lme-stack-siem)
5. [Tracecat (SOAR)](#5-tracecat-soar)
6. [DFIR-IRIS (ITSM)](#6-dfir-iris-itsm)
7. [Integration Points](#7-integration-points)
8. [Security Considerations](#8-security-considerations)
9. [Monitoring & Observability](#9-monitoring--observability)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Acceptance Criteria](#11-acceptance-criteria)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIEM SOAR (Current Implementation)                   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              LME — Logging Made Easy                                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │  │
│  │  │ Wazuh Agent │  │ Wazuh Agent │  │ Syslog      │                 │  │
│  │  │ (Server)    │  │ (Network)   │  │ (Devices)   │                 │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │  │
│  │         │                │                │                          │  │
│  │         └────────────────┼────────────────┘                          │  │
│  │                          │                                            │  │
│  │                   ┌──────┴──────┐                                    │  │
│  │                   │ Wazuh Mgr   │                                    │  │
│  │                   │ (Encode/    │                                    │  │
│  │                   │  Decode +   │                                    │  │
│  │                   │  Rules)     │                                    │  │
│  │                   └──────┬──────┘                                    │  │
│  │                          │                                            │  │
│  │              ┌───────────┼───────────┐                               │  │
│  │              ▼           ▼           ▼                               │  │
│  │  ┌───────────────┐ ┌───────────┐ ┌───────────┐                     │  │
│  │  │ Elasticsearch │ │  Kibana   │ │ ElastAlert│                     │  │
│  │  │ (Storage)     │ │ (Viz)     │ │ (Bridge)  │                     │  │
│  │  └───────────────┘ └───────────┘ └─────┬─────┘                     │  │
│  └────────────────────────────────────────┼────────────────────────────┘  │
│                                           │                                │
│                                           ▼                                │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              Tracecat (SOAR)                                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │  │
│  │  │  Enrichment │  │  AI Agent   │  │  Playbook   │                 │  │
│  │  │  AbuseIPDB  │  │  Summary +  │  │  Automation │                 │  │
│  │  │  VirusTotal │  │  Recommend  │  │             │                 │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                               │                                            │
│                               ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              DFIR-IRIS (ITSM)                                        │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │  Incident Management → SOC Investigation → Resolution       │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow (Actual)

```
1. COLLECTION
   Wazuh Agent / Syslog Source
     → Wazuh Manager (port 514/TCP/UDP)

2. PROCESSING
   Wazuh Manager
     → Encode & Decode log
     → Apply detection rules
     → Generate alerts (prioritized)

3. STORAGE & VISUALIZATION
   Wazuh Manager
     → Elasticsearch (index: wazuh-*)
     → Kibana (dashboard: alert visualization)

4. ALERT BRIDGE
   ElastAlert
     → Monitors Elasticsearch for new alerts
     → Filters by severity/rules
     → Forwards matching alerts to Tracecat

5. SOAR PROCESSING (Tracecat)
   Alert received
     → Enrichment:
        ├─ AbuseIPDB (IP reputation scan)
        └─ VirusTotal (file hash scan)
     → AI Agent Analysis:
        ├─ Summary generation
        └─ Recommendation
     → Case creation in DFIR-IRIS

6. INCIDENT MANAGEMENT (DFIR-IRIS)
   Incident created
     → SOC analyst assignment
     → Investigation workflow
     → Evidence collection
     → Resolution & closure
```

---

## 2. Core Stack

### 2.1 Component Summary

| # | Component | Technology | Version | Role |
|---|-----------|------------|---------|------|
| 1 | **LME (SIEM)** | Wazuh Manager + Elasticsearch + Kibana + ElastAlert | Wazuh 4.x, ES 8.x, Kibana 8.x | Log collection, detection, visualization |
| 2 | **SOAR** | Tracecat | latest | Security orchestration, automation, response |
| 3 | **ITSM** | DFIR-IRIS | latest | Incident management, SOC investigation |

### 2.2 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Log Collection** | Wazuh Agent, Syslog (TCP/UDP 514) | Agent-based + agentless log collection |
| **Log Processing** | Wazuh Manager | Encode/decode, rule evaluation, alert generation |
| **Storage** | Elasticsearch 8.x | Security event storage, indexing, search |
| **Visualization** | Kibana 8.x | Alert dashboard, threat hunting, reporting |
| **Alert Bridge** | ElastAlert | Rule-based alert forwarding from ES to Tracecat |
| **SOAR** | Tracecat | Workflow automation, enrichment, case management |
| **Enrichment** | AbuseIPDB, VirusTotal | IP reputation, file hash analysis |
| **AI Analysis** | Tracecat AI Agent | Alert summary, recommendations |
| **ITSM** | DFIR-IRIS | Incident tracking, SOC investigation |

---

## 3. Data Flow

### 3.1 Step-by-Step Flow

| Step | Source | Destination | Data | Protocol | Description |
|------|--------|-------------|------|----------|-------------|
| 1 | Wazuh Agent / Syslog | Wazuh Manager | Raw logs | Syslog (TCP/UDP 514) | Log collection dari servers, network devices |
| 2 | Wazuh Manager | — | Encoded/Decoded logs | Internal | Decode log format, normalize fields |
| 3 | Wazuh Manager | — | Detection rules | Internal | Apply rules, generate alerts (prioritized) |
| 4 | Wazuh Manager | Elasticsearch | Alerts | Wazuh API / Indexer | Store alerts di Elasticsearch |
| 5 | Elasticsearch | Kibana | Alerts | Internal | Visualize alerts di dashboard |
| 6 | Elasticsearch | ElastAlert | Alerts | ES Query | ElastAlert query ES untuk new alerts |
| 7 | ElastAlert | Tracecat | Filtered alerts | Webhook / API | Forward alerts ke Tracecat untuk processing |
| 8 | Tracecat | AbuseIPDB | Source IP | REST API | Scan IP reputation penyerang |
| 9 | Tracecat | VirusTotal | File hash | REST API | Scan hash file yang berubah |
| 10 | Tracecat AI Agent | — | Summary + Recommendation | Internal | AI analyze alert, buat summary |
| 11 | Tracecat | DFIR-IRIS | Enriched incident | REST API | Create incident untuk SOC investigation |

### 3.2 Flow Diagram

```
                    ┌──────────────────┐
                    │  Wazuh Agent     │
                    │  / Syslog Source │
                    └────────┬─────────┘
                             │ Syslog (TCP/UDP 514)
                             ▼
                    ┌──────────────────┐
                    │  Wazuh Manager   │
                    │  ┌────────────┐  │
                    │  │ Encode /   │  │
                    │  │ Decode     │  │
                    │  ├────────────┤  │
                    │  │ Rules      │  │
                    │  │ Engine     │  │
                    │  └────────────┘  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌──────────────┐ ┌───────────┐ ┌──────────────┐
     │ Elasticsearch│ │  Kibana   │ │ ElastAlert   │
     │ (Storage)    │ │ (Viz)     │ │ (Bridge)     │
     │              │ │           │ │              │
     │ wazuh-*      │ │ Dashboard │ │ Query ES     │
     │ index        │ │ Alert Viz │ │ Filter rules │
     └──────────────┘ └───────────┘ └──────┬───────┘
                                           │ Webhook/API
                                           ▼
                                  ┌──────────────────┐
                                  │    Tracecat      │
                                  │    (SOAR)        │
                                  │                  │
                                  │  ┌────────────┐  │
                                  │  │ Enrichment │  │
                                  │  │ ├ AbuseIPDB│  │
                                  │  │ └ VirusTotal│ │
                                  │  ├────────────┤  │
                                  │  │ AI Agent   │  │
                                  │  │ Summary +  │  │
                                  │  │ Recommend  │  │
                                  │  └────────────┘  │
                                  └────────┬─────────┘
                                           │ REST API
                                           ▼
                                  ┌──────────────────┐
                                  │   DFIR-IRIS      │
                                  │   (ITSM)         │
                                  │                  │
                                  │  Incident → SOC  │
                                  │  Investigation   │
                                  └──────────────────┘
```

---

## 4. LME Stack (SIEM)

### 4.1 Wazuh Manager

**Role:** Core SIEM engine — log collection, decoding, rule evaluation, alert generation.

| Aspect | Detail |
|--------|--------|
| **Input** | Wazuh Agent (TCP 1514), Syslog (TCP/UDP 514) |
| **Processing** | Log decoding (syslog, JSON, Windows event), rule matching |
| **Output** | Alerts → Elasticsearch, Kibana API |
| **Rules** | Custom rules untuk alert prioritization |
| **Config** | `/var/ossec/etc/ossec.conf` |

#### Detection Rules (Custom)

```xml
<!-- Contoh: Brute Force Detection -->
<rule id="100001" level="10">
  <if_sid>5712</if_sid>
  <frequency>5</frequency>
  <timeframe>60</timeframe>
  <description>Multiple authentication failures detected</description>
  <group>authentication_failures,pci_dss_10.2.4</group>
</rule>

<!-- Contoh: Suspicious Process -->
<rule id="100002" level="12">
  <decoded_as>syslog</decoded_as>
  <field name="process_name">mimikatz</field>
  <description>Suspicious process detected: mimikatz</description>
  <group>process_execution,suspicious</group>
</rule>

<!-- Contoh: File Integrity Alert -->
<rule id="100003" level="10">
  <if_sid>550</if_sid>
  <description>File integrity change detected</description>
  <group>file_integrity,syscheck</group>
</rule>
```

#### Alert Priority Levels

| Level | Severity | Description | Action |
|-------|----------|-------------|--------|
| 1-3 | Low | Informational, no action | Log only |
| 4-6 | Medium | Suspicious activity | ElastAlert → Tracecat |
| 7-9 | High | Confirmed threat | ElastAlert → Tracecat (priority) |
| 10-12 | Critical | Active attack | ElastAlert → Tracecat → DFIR-IRIS |

### 4.2 Elasticsearch

**Role:** Security event storage, indexing, full-text search.

| Aspect | Detail |
|--------|--------|
| **Index Pattern** | `wazuh-*` |
| **Retention** | Configure via ISM (Index State Management) |
| **Replicas** | 1 (single-node) / 2 (cluster) |
| **Shards** | 1 primary per index |
| **Hot Nodes** | 3+ (production) |
| **Storage** | SSD recommended |

#### Index Lifecycle

```
Hot (0-7 days) → Warm (7-30 days) → Cold (30-90 days) → Delete (90+ days)
```

### 4.3 Kibana

**Role:** Alert visualization, dashboard, threat hunting.

| Feature | Description |
|---------|-------------|
| **Alert Dashboard** | Real-time alert volume, severity distribution |
| **Threat Map** | Geographic visualization of attacks |
| **Rule Management** | Wazuh rules UI |
| **Discover** | Ad-hoc log search |
| **Dashboards** | Custom SOC dashboards |

### 4.4 ElastAlert

**Role:** Alert bridge — query Elasticsearch, filter, forward ke Tracecat.

| Aspect | Detail |
|--------|--------|
| **Mode** | Alert only (no suppression) |
| **Query** | `wazuh-*` index, last N minutes |
| **Filter** | By rule level (≥4 untuk forward) |
| **Output** | Webhook → Tracecat API |
| **Frequency** | Check every 1-5 minutes |

#### ElastAlert Configuration

```yaml
# elastalert_config.yaml
rules_folder: /etc/elastalert/rules
run_every:
  minutes: 1
buffer_time:
  minutes: 15
es_host: localhost
es_port: 9200
writeback_index: elastalert_status
alert_time_limit:
  days: 2
```

#### ElastAlert Rule (Forward to Tracecat)

```yaml
# rules/tracecat_forward.yaml
name: "Forward Alerts to Tracecat"
type: any
index: wazuh-*
filter:
  - query:
      query:
        range:
          rule.level:
            gte: 4
alert: post
http_post_url: "http://tracecat:8080/api/v1/alerts/ingest"
http_post_headers:
  Content-Type: "application/json"
alert_text_type: alert_text_only
alert_text: |
  {
    "alert_id": "{alert_id}",
    "timestamp": "{timestamp}",
    "rule_id": "{rule_id}",
    "rule_description": "{rule.description}",
    "rule_level": "{rule.level}",
    "agent_name": "{agent.name}",
    "agent_ip": "{agent.ip}",
    "source_ip": "{data.srcip}",
    "user": "{data.user}",
    "program": "{data.program}",
    "full_log": "{full_log}"
  }
```

---

## 5. Tracecat (SOAR)

### 5.1 Role

Security Orchestration, Automation & Response — enrich alerts, analyze with AI, create incidents.

### 5.2 Capabilities

| Capability | Description |
|------------|-------------|
| **Alert Ingestion** | Receive alerts dari ElastAlert via webhook |
| **Enrichment** | AbuseIPDB (IP scan), VirusTotal (hash scan) |
| **AI Analysis** | Summary generation, recommendation |
| **Case Management** | Create/manage cases internally |
| **Incident Creation** | Push enriched incident ke DFIR-IRIS |
| **Playbook** | Workflow automation untuk repetitive tasks |

### 5.3 Enrichment Pipeline

```
Alert Received (from ElastAlert)
  │
  ├─► AbuseIPDB Enrichment
  │    ├─ Query: source_ip
  │    ├─ Response: IP reputation, abuse confidence, country, ISP
  │    └─ Attach to alert
  │
  ├─► VirusTotal Enrichment
  │    ├─ Query: file hash (if available)
  │    ├─ Response: malware detection, file type, reputation
  │    └─ Attach to alert
  │
  └─► AI Agent Analysis
       ├─ Input: original alert + enriched data
       ├─ Process: LLM analysis
       ├─ Output: Summary + Recommended Actions
       └─ Attach to alert
```

### 5.4 AbuseIPDB Integration

| Aspect | Detail |
|--------|--------|
| **API Endpoint** | `https://api.abuseipdb.com/api/v2/check` |
| **Input** | Source IP address |
| **Output** | Abuse confidence score, country, ISP, usage type, reports |
| **Rate Limit** | Free: 1000 req/day, Paid: higher |
| **Use Case** | Identify known malicious IPs |

#### AbuseIPDB Query Example

```json
// Request
GET https://api.abuseipdb.com/api/v2/check?ipAddress=203.0.113.50
Headers: Key: {API_KEY}, Accept: application/json

// Response
{
  "data": {
    "ipAddress": "203.0.113.50",
    "abuseConfidenceScore": 85,
    "countryCode": "XX",
    "isp": "Malicious ISP",
    "usageType": "Data Center/Web Hosting",
    "totalReports": 150,
    "lastReportedAt": "2026-06-25T10:00:00Z"
  }
}
```

### 5.5 VirusTotal Integration

| Aspect | Detail |
|--------|--------|
| **API Endpoint** | `https://www.virustotal.com/api/v3/files/{hash}` |
| **Input** | File hash (MD5, SHA1, SHA256) |
| **Output** | Malware detection, file type, reputation, community score |
| **Rate Limit** | Free: 4 req/min, Paid: higher |
| **Use Case** | Identify malicious files |

#### VirusTotal Query Example

```json
// Request
GET https://www.virustotal.com/api/v3/files/{sha256_hash}
Headers: x-apikey: {API_KEY}

// Response
{
  "data": {
    "attributes": {
      "last_analysis_stats": {
        "malicious": 45,
        "suspicious": 5,
        "undetected": 20
      },
      "meaningful_name": "malware.exe",
      "reputation": -85
    }
  }
}
```

### 5.6 AI Agent Analysis

| Aspect | Detail |
|--------|--------|
| **Input** | Original alert + AbuseIPDB + VirusTotal results |
| **Process** | LLM-based analysis |
| **Output** | Summary (what happened) + Recommendations (what to do) |
| **Model** | Tracecat built-in AI / configurable LLM |

#### AI Output Example

```json
{
  "summary": "Multiple failed login attempts detected from IP 203.0.113.50 targeting server DC-SERVER-01. AbuseIPDB reports this IP has 85% abuse confidence with 150 reports. Attack pattern suggests brute force attempt against SSH service.",
  "recommendations": [
    "Block IP 203.0.113.50 at firewall immediately",
    "Check if any accounts were compromised",
    "Review SSH access logs for successful logins",
    "Notify affected account owners",
    "Update detection rules if needed"
  ],
  "severity_assessment": "HIGH",
  "mitre_attack": {
    "tactic": "credential-access",
    "technique": "T1110 - Brute Force"
  }
}
```

---

## 6. DFIR-IRIS (ITSM)

### 6.1 Role

Incident Management — create, track, and manage security incidents untuk SOC investigation.

### 6.2 Incident Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  New     │───→│ Assigned │───→│Investiga-│───→│ Resolved │───→│ Closed   │
│          │    │          │    │ ting     │    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     │               │               │               ▼
     │               │          ┌────┴────┐    ┌──────────┐
     │               │          │Escalated│    │ Reopened │
     │               │          └─────────┘    └──────────┘
```

### 6.3 Integration with Tracecat

| Aspect | Detail |
|--------|--------|
| **Trigger** | Tracecat sends enriched incident after AI analysis |
| **API** | DFIR-IRIS REST API |
| **Data** | Alert details, enrichment, AI summary, recommendations |
| **Assignment** | Auto-assign to SOC queue or specific analyst |
| **Priority** | Based on alert severity + AI assessment |

### 6.4 Incident Schema (from Tracecat)

```json
{
  "incident": {
    "title": "Brute Force Attack from 203.0.113.50",
    "severity": "high",
    "status": "new",
    "source": "wazuh",
    "alerts": ["ALERT-001", "ALERT-002"],
    "enrichment": {
      "abuseipdb": {
        "abuse_confidence": 85,
        "country": "XX",
        "isp": "Malicious ISP"
      },
      "virustotal": null
    },
    "ai_analysis": {
      "summary": "Multiple failed login attempts...",
      "recommendations": ["Block IP", "Check accounts", "..."],
      "severity_assessment": "HIGH",
      "mitre_attack": {
        "tactic": "credential-access",
        "technique": "T1110"
      }
    },
    "timeline": [
      {
        "timestamp": "2026-06-25T10:30:00Z",
        "action": "incident_created",
        "actor": "tracecat-soar",
        "details": "Auto-created from enriched alert"
      }
    ]
  }
}
```

### 6.5 SOC Workflow

| Step | Actor | Action |
|------|-------|--------|
| 1 | Tracecat | Create incident di DFIR-IRIS |
| 2 | DFIR-IRIS | Auto-assign ke SOC queue |
| 3 | SOC Analyst | Review incident + AI recommendations |
| 4 | SOC Analyst | Investigate (collect evidence, analyze) |
| 5 | SOC Analyst | Take action (contain, remediate) |
| 6 | SOC Analyst | Document findings |
| 7 | SOC Analyst | Resolve & close incident |

---

## 7. Integration Points

### 7.1 Integration Matrix

| Source | Destination | Protocol | Data | Frequency |
|--------|-------------|----------|------|-----------|
| Wazuh Agent | Wazuh Manager | Syslog (TCP/UDP 514) | Raw logs | Real-time |
| Wazuh Manager | Elasticsearch | Wazuh API / Indexer | Alerts | Real-time |
| Elasticsearch | Kibana | Internal | Alerts | Real-time |
| Elasticsearch | ElastAlert | ES Query | Alerts | Every 1-5 min |
| ElastAlert | Tracecat | Webhook / API | Filtered alerts | Every 1-5 min |
| Tracecat | AbuseIPDB | REST API | IP reputation | Per alert |
| Tracecat | VirusTotal | REST API | File hash scan | Per alert |
| Tracecat | DFIR-IRIS | REST API | Enriched incident | Per analyzed alert |

### 7.2 API Endpoints

| Component | Endpoint | Method | Purpose |
|-----------|----------|--------|---------|
| Wazuh Manager | `/var/ossec/api/shared/syslog` | POST | Agent log submission |
| Elasticsearch | `/_search` | POST | ElastAlert query |
| Tracecat | `/api/v1/alerts/ingest` | POST | Alert ingestion from ElastAlert |
| Tracecat | `/api/v1/cases` | POST | Case management |
| DFIR-IRIS | `/api/v2/incidents` | POST | Incident creation |
| DFIR-IRIS | `/api/v2/incidents/{id}` | PUT | Incident update |

### 7.3 Data Format (ElastAlert → Tracecat)

```json
{
  "alert_id": "WAZUH-2026-06-25-001234",
  "timestamp": "2026-06-25T10:30:00Z",
  "rule_id": 100001,
  "rule_description": "Multiple authentication failures",
  "rule_level": 10,
  "agent_name": "dc-server-01",
  "agent_ip": "10.0.1.50",
  "source_ip": "203.0.113.50",
  "user": "admin",
  "program": "sshd",
  "full_log": "Jun 25 10:30:00 dc-server-01 sshd[12345]: Failed password for admin from 203.0.113.50 port 22 ssh2"
}
```

---

## 8. Security Considerations

### 8.1 Access Control

| Component | Access | Auth Method |
|-----------|--------|-------------|
| Wazuh Manager | Admin only | OS-level + API token |
| Elasticsearch | Internal only | API key / basic auth |
| Kibana | SOC team | Username/password + RBAC |
| ElastAlert | Service account | Config file |
| Tracecat | SOC team | OIDC / API key |
| DFIR-IRIS | SOC team | Username/password + API key |

### 8.2 Secret Management

| Secret | Storage | Rotation |
|--------|---------|----------|
| Wazuh API token | Wazuh config | Manual |
| Elasticsearch credentials | Config / Env | Manual |
| ElastAlert config | Config file | Manual |
| Tracecat secrets | Tracecat config | Manual |
| AbuseIPDB API key | Tracecat config | 90 days |
| VirusTotal API key | Tracecat config | 90 days |
| DFIR-IRIS API key | Tracecat config | 90 days |

### 8.3 Network Security

| Zone | Components | Access |
|------|------------|--------|
| **DMZ** | Wazuh Agents, Syslog sources | → Wazuh Manager only |
| **SIEM** | Wazuh Manager, Elasticsearch, Kibana, ElastAlert | Internal |
| **SOAR** | Tracecat | Internal, API access |
| **ITSM** | DFIR-IRIS | Internal, SOC team |

### 8.4 Data Protection

| Data Type | Protection |
|-----------|------------|
| Logs | Encrypted at rest (ES) |
| Alerts | Encrypted at rest (ES) |
| API keys | Config files (restrict permissions) |
| Enrichment data | Stored in Tracecat (encrypted) |
| Incidents | DFIR-IRIS database (encrypted) |

---

## 9. Monitoring & Observability

### 9.1 Health Checks

| Component | Health Check | Interval |
|-----------|-------------|----------|
| Wazuh Manager | `systemctl status wazuh-manager` | 5 min |
| Elasticsearch | `GET /_cluster/health` | 1 min |
| Kibana | `GET /api/status` | 1 min |
| ElastAlert | Process check | 1 min |
| Tracecat | `GET /api/v1/health` | 1 min |
| DFIR-IRIS | `GET /api/v2/health` | 5 min |

### 9.2 Key Metrics

| Metric | Target | Alert |
|--------|--------|-------|
| Log ingestion rate | >1000 events/sec | <500 events/sec |
| Alert generation latency | <30s | >60s |
| ElastAlert check interval | 1 min | >5 min |
| Tracecat alert processing | <60s | >120s |
| Enrichment latency (AbuseIPDB) | <5s | >10s |
| Enrichment latency (VirusTotal) | <10s | >20s |
| Incident creation latency | <120s | >300s |

### 9.3 Log Files

| Component | Log Location | Purpose |
|-----------|-------------|---------|
| Wazuh Manager | `/var/ossec/logs/ossec.log` | SIEM operations |
| Elasticsearch | `/var/log/elasticsearch/` | ES cluster logs |
| Kibana | `/var/log/kibana/` | Kibana logs |
| ElastAlert | `/var/log/elastalert/` | Alert bridge logs |
| Tracecat | Docker logs | SOAR operations |
| DFIR-IRIS | Docker logs | ITSM operations |

---

## 10. Deployment Architecture

### 10.1 Single-Node (Development)

```
┌─────────────────────────────────────────────────────────┐
│                    Single Server                         │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Wazuh Mgr   │  │ Elasticsearch│  │ Kibana      │   │
│  │ :514        │  │ :9200        │  │ :5601       │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ ElastAlert  │  │ Tracecat    │  │ DFIR-IRIS   │   │
│  │ :config     │  │ :8080       │  │ :443        │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                         │
│  Resources: 8 CPU, 32 GB RAM, 500 GB SSD              │
└─────────────────────────────────────────────────────────┘
```

### 10.2 Multi-Node (Production)

```
┌─────────────────────────────────────────────────────────┐
│                   SIEM Server                            │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Wazuh Mgr   │  │ Elasticsearch│  │ Kibana      │   │
│  │ (Primary)   │  │ (3 nodes)    │  │ :5601       │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                         │
│  ┌─────────────┐                                       │
│  │ ElastAlert  │                                       │
│  │ :config     │                                       │
│  └─────────────┘                                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   SOAR Server                            │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐                      │
│  │ Tracecat    │  │ Tracecat    │                      │
│  │ (API + UI)  │  │ (Worker)    │                      │
│  │ :8080       │  │ :config     │                      │
│  └─────────────┘  └─────────────┘                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   ITSM Server                            │
│                                                         │
│  ┌─────────────┐                                       │
│  │ DFIR-IRIS   │                                       │
│  │ :443        │                                       │
│  └─────────────┘                                       │
└─────────────────────────────────────────────────────────┘

Resources:
- SIEM Server: 16 CPU, 64 GB RAM, 1 TB SSD
- SOAR Server: 8 CPU, 16 GB RAM, 200 GB SSD
- ITSM Server: 4 CPU, 8 GB RAM, 200 GB SSD
```

### 10.3 Network Requirements

| Port | Protocol | Source | Destination | Purpose |
|------|----------|--------|-------------|---------|
| 514 | TCP/UDP | Wazuh Agents | Wazuh Manager | Log collection |
| 1514 | TCP | Wazuh Agents | Wazuh Manager | Agent communication |
| 9200 | TCP | ElastAlert | Elasticsearch | ES query |
| 9200 | TCP | Kibana | Elasticsearch | ES query |
| 5601 | TCP | SOC Analysts | Kibana | Web UI |
| 8080 | TCP | ElastAlert | Tracecat | Webhook |
| 443 | TCP | SOC Analysts | DFIR-IRIS | Web UI |
| 443 | TCP | Tracecat | AbuseIPDB | API enrichment |
| 443 | TCP | Tracecat | VirusTotal | API enrichment |

---

## 11. Acceptance Criteria

| # | Criterion | Test Method | Status |
|---|-----------|-------------|--------|
| 1 | Wazuh Agent successfully sends logs to Wazuh Manager | Check agent status in Wazuh UI | ⬜ |
| 2 | Wazuh Manager correctly encodes/decodes logs | Check decoded alerts in Kibana | ⬜ |
| 3 | Detection rules trigger correct alerts | Send test log, verify alert generated | ⬜ |
| 4 | Alerts stored in Elasticsearch | Query ES for test alert | ⬜ |
| 5 | Kibana displays alerts correctly | Check dashboard visualization | ⬜ |
| 6 | ElastAlert picks up new alerts from ES | Check ElastAlert logs | ⬜ |
| 7 | ElastAlert forwards alerts to Tracecat | Check Tracecat alert inbox | ⬜ |
| 8 | Tracecat enriches with AbuseIPDB | Check enrichment data on alert | ⬜ |
| 9 | Tracecat enriches with VirusTotal | Check enrichment data on alert | ⬜ |
| 10 | AI Agent generates summary + recommendations | Check AI output on alert | ⬜ |
| 11 | Tracecat creates incident in DFIR-IRIS | Check DFIR-IRIS incident list | ⬜ |
| 12 | SOC analyst can investigate incident | Login to DFIR-IRIS, review incident | ⬜ |
| 13 | End-to-end flow works (<5 min) | Send test alert, track through all systems | ⬜ |
| 14 | All components are healthy | Check health endpoints | ⬜ |
| 15 | Logs are retained per policy | Check ES index lifecycle | ⬜ |

---

**Document Version:** v1.0
**Last Updated:** 2026-06-25
**Architecture Diagram:** `diagrams/siem-soar-actual-architecture.html`
