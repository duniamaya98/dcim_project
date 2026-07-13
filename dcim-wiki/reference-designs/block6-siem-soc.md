---
title: "Block 6 — SIEM/SOC: Reference Design Spec"
created: 2026-06-23
updated: 2026-06-23
type: reference-design
block: 6
phase: 2
status: generated
confidence: high
tags: [siem, soc, security, wazuh, correlation, incident-response, compliance, cis-benchmark]
wiki_pages:
  - siem-soc
  - data-ingestion-integration
  - elasticsearch
  - workflow-automation
  - web-dashboard
  - siem-investigation-runbook
  - siem-solution-comparison
purpose: >
  Reference design spec untuk Block 6 SIEM/SOC.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# Block 6 — SIEM/SOC: Reference Design Spec

> **Purpose:** Dokumen referensi lengkap untuk SIEM/SOC — security event ingestion, correlation, incident response, compliance.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi. Setiap gap = connection point.
> **Architecture Diagram:** `diagrams/block6-siem-soc-architecture.html`
> **Depends on:** Block 1 (Infrastructure), Block 2 (DI&I)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Security Event Ingestion](#2-security-event-ingestion)
3. [Security Event Schema](#3-security-event-schema)
4. [Correlation Engine](#4-correlation-engine)
5. [Incident Response Workflow](#5-incident-response-workflow)
6. [CIS Benchmark Compliance](#6-cis-benchmark-compliance)
7. [SOC API](#7-soc-api)
8. [Elasticsearch Configuration](#8-elasticsearch-configuration)
9. [Data Retention & Archival](#9-data-retention--archival)
10. [Security](#10-security)
11. [Monitoring & Alerting](#11-monitoring--alerting)
12. [Acceptance Criteria](#12-acceptance-criteria)
13. [Gap Comparison Template](#13-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                        SIEM/SOC                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Security Event Ingestion                     │  │
│  │  Wazuh Agents → Syslog → Kafka (dcim.siem.events)       │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐  │
│  │              Correlation Engine                           │  │
│  │  Rule-based • Threshold • Pattern • Cross-source          │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│              ┌────────────┴────────────┐                       │
│              ▼                         ▼                       │
│  ┌───────────────────┐    ┌────────────────────┐              │
│  │  Alert Engine     │    │ Incident Response  │              │
│  │  (real-time)      │    │ (workflow)         │              │
│  └────────┬──────────┘    └────────┬───────────┘              │
│           │                         │                          │
│  ┌────────┴──────────┐    ┌────────┴───────────┐              │
│  │  Elasticsearch    │    │  Workflow Engine   │              │
│  │  (security store) │    │  (escalation)      │              │
│  └───────────────────┘    └────────────────────┘              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Compliance Engine                            │  │
│  │  CIS Benchmark • Gap Analysis • Remediation              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
Security Sources (servers, network, apps, cloud)
  → Wazuh Agents → Syslog (UDP/TCP 514)
    → NiFi Syslog Processor → Kafka (dcim.siem.events)
      → Elasticsearch (dcim-siem-*)
        → Correlation Engine → Alerts
          → Incident Response → Workflow Automation

Compliance Sources → CIS Scanner → Compliance Engine → Reports
```

### 1.3 Core Responsibilities

| Responsibility | Description | SLA |
|---------------|-------------|-----|
| Event Ingestion | Collect from all security sources | < 5s latency |
| Event Storage | Elasticsearch with ILM | 90-day retention |
| Correlation | Rule-based + pattern detection | Real-time |
| Alerting | Real-time alerts on suspicious activity | < 30s from detection |
| Incident Response | Auto-create, classify, escalate | < 1min from alert |
| Compliance | CIS benchmark checks | Daily scan |
| Investigation | Search, filter, correlate events | p99 < 2s |

---

## 2. Security Event Ingestion

### 2.1 Ingestion Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Wazuh Agent │───→│  Syslog      │───→│  Kafka       │───→│  Elasticsearch│
│  (per host)  │    │  Collector   │    │  dcim.siem   │    │  dcim-siem-* │
│              │    │  :514 UDP/TCP│    │  .events     │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
     │                   │                    │                    │
     │                   │                    │                    │
     ▼                   ▼                    ▼                    ▼
  Agent data         NiFi processor       12 partitions        ILM policy
  (OSSEC format)     (parse + normalize)  RF=3, 90d           (hot/warm/cold)
```

### 2.2 Wazuh Agent Configuration

```xml
<!-- /var/ossec/etc/ossec.conf -->
<ossec_config>
  <!-- Syslog output -->
  <syslog_output>
    <level>3</level>
    <server>syslog-collector</server>
    <port>514</port>
    <format>json</format>
  </syslog_output>

  <!-- Monitored directories -->
  <syscheck>
    <frequency>3600</frequency>
    <directories check_all="yes">/etc,/usr/bin,/usr/sbin</directories>
    <ignore>/etc/mtab</ignore>
  </syscheck>

  <!-- Active response -->
  <active-response>
    <command>firewall-drop</command>
    <location>local</location>
  </active-response>

  <!-- Rules -->
  <rule>
    <description>Failed login attempt</description>
    <level>7</level>
    <frequency>5</frequency>
    <timeframe>60</timeframe>
  </rule>
</ossec_config>
```

### 2.3 Syslog → Kafka Pipeline

```python
# siem/ingestion.py

import json
from datetime import datetime

class SecurityEventIngestion:
    def __init__(self, kafka_producer, es_client):
        self.kafka = kafka_producer
        self.es = es_client
        self.topic = "dcim.siem.events"

    async def ingest_syslog(self, raw_event: dict) -> dict:
        """Parse and normalize syslog event."""

        # Normalize to standard schema
        normalized = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source_type": self._detect_source_type(raw_event),
            "severity": self._map_severity(raw_event.get("level", 0)),
            "category": self._classify_event(raw_event),
            "title": raw_event.get("description", "Security Event"),
            "description": raw_event.get("full_log", ""),
            "source_ip": raw_event.get("src_ip"),
            "destination_ip": raw_event.get("dst_ip"),
            "source_port": raw_event.get("src_port"),
            "destination_port": raw_event.get("dst_port"),
            "user": raw_event.get("data", {}).get("user"),
            "process": raw_event.get("data", {}).get("process"),
            "command": raw_event.get("data", {}).get("command"),
            "rule_id": raw_event.get("rule", {}).get("id"),
            "rule_description": raw_event.get("rule", {}).get("description"),
            "agent_name": raw_event.get("agent", {}).get("name"),
            "agent_ip": raw_event.get("agent", {}).get("ip"),
            "raw_event": json.dumps(raw_event),
            "tags": []
        }

        # Enrich with asset info
        if normalized["agent_ip"]:
            asset_info = await self._lookup_asset(normalized["agent_ip"])
            if asset_info:
                normalized["asset_id"] = asset_info.get("asset_id")
                normalized["ci_id"] = asset_info.get("ci_id")
                normalized["location"] = asset_info.get("location")
                normalized["owner_dept"] = asset_info.get("owner_dept")

        # Publish to Kafka
        await self.kafka.send(
            self.topic,
            key=normalized["agent_ip"],
            value=json.dumps(normalized)
        )

        return normalized

    def _detect_source_type(self, event: dict) -> str:
        """Detect source type from event."""
        if "agent" in event:
            return "wazuh"
        if "program" in event:
            return event["program"]  # sshd, nginx, etc.
        return "unknown"

    def _map_severity(self, level: int) -> str:
        """Map Wazuh level to severity."""
        if level >= 10:
            return "critical"
        elif level >= 7:
            return "high"
        elif level >= 4:
            return "medium"
        elif level >= 1:
            return "low"
        return "info"

    def _classify_event(self, event: dict) -> str:
        """Classify event category."""
        rule_id = event.get("rule", {}).get("id", "")

        classification_map = {
            "5712": "authentication",      # Failed login
            "5715": "authentication",      # Successful login
            "5720": "privilege_escalation", # Sudo usage
            "5716": "authentication",      # Logon denied
            "5402": "file_integrity",      # FIM alert
            "5502": "process",             # Process anomaly
            "5503": "network",             # Network anomaly
            "5504": "malware",             # Malware detection
            "5765": "compliance",          # CIS benchmark
        }

        return classification_map.get(rule_id, "other")
```

### 2.4 Event Sources

| Source | Agent/Method | Protocol | Events/day | Priority |
|--------|-------------|----------|------------|----------|
| Servers (Linux/Windows) | Wazuh agent | Syslog | ~50,000 | P1 |
| Network devices | Wazuh + SNMP traps | Syslog | ~20,000 | P1 |
| Applications | Wazuh agent + custom | REST API | ~30,000 | P1 |
| Cloud (AWS/GCP/Azure) | CloudTrail + agent | REST API | ~10,000 | P2 |
| Access control | Badge system | REST API | ~5,000 | P2 |
| Database audit | PostgreSQL audit log | Syslog | ~15,000 | P1 |
| **Total** | | | **~130,000/day** | |

---

## 3. Security Event Schema

### 3.1 Normalized Security Event

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DCIM Security Event",
  "type": "object",
  "required": ["event_id", "timestamp", "severity", "category", "title"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "source_type": { "type": "string", "enum": ["wazuh", "syslog", "cloudtrail", "access_control", "database", "custom"] },
    "severity": { "type": "string", "enum": ["critical", "high", "medium", "low", "info"] },
    "category": { "type": "string", "enum": ["authentication", "authorization", "privilege_escalation", "file_integrity", "process", "network", "malware", "compliance", "data_breach", "denial_of_service", "other"] },
    "title": { "type": "string" },
    "description": { "type": "string" },
    "source_ip": { "type": "string" },
    "destination_ip": { "type": "string" },
    "source_port": { "type": "integer" },
    "destination_port": { "type": "integer" },
    "user": { "type": "string" },
    "process": { "type": "string" },
    "command": { "type": "string" },
    "rule_id": { "type": "string" },
    "rule_description": { "type": "string" },
    "agent_name": { "type": "string" },
    "agent_ip": { "type": "string" },
    "asset_id": { "type": "string" },
    "ci_id": { "type": "string" },
    "location": { "type": "object" },
    "owner_dept": { "type": "string" },
    "tags": { "type": "array", "items": { "type": "string" } },
    "correlation_id": { "type": "string" },
    "incident_id": { "type": "string" },
    "raw_event": { "type": "string" }
  }
}
```

---

## 4. Correlation Engine

### 4.1 Correlation Rules

| Rule ID | Name | Condition | Window | Threshold | Severity |
|---------|------|-----------|--------|-----------|----------|
| CR-001 | Brute Force Login | Failed login from same IP | 1 min | 5 attempts | High |
| CR-002 | Credential Stuffing | Failed login different users same IP | 5 min | 10 users | Critical |
| CR-003 | Privilege Escalation | sudo usage outside business hours | — | 1 | High |
| CR-004 | File Tampering | FIM alert on critical files | — | 1 | Critical |
| CR-005 | Malware Detection | AV/EDR detection event | — | 1 | Critical |
| CR-006 | Lateral Movement | Successful login after failed from different IP | 10 min | 2 IPs | High |
| CR-007 | Data Exfiltration | Large outbound data transfer | 1 hour | > 1GB | Critical |
| CR-008 | Configuration Change | Config file modification | — | 1 | Medium |
| CR-009 | Service Stop | Critical service stopped | — | 1 | High |
| CR-010 | Compliance Violation | CIS benchmark failure | — | 1 | Medium |

### 4.2 Correlation Implementation

```python
# siem/correlation.py

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio

@dataclass
class CorrelationRule:
    rule_id: str
    name: str
    category: str
    condition: dict
    window_minutes: int
    threshold: int
    severity: str

@dataclass
class CorrelationAlert:
    alert_id: str
    rule_id: str
    rule_name: str
    severity: str
    triggered_at: datetime
    matched_events: List[dict]
    affected_assets: List[dict]
    description: str
    recommended_action: str

class CorrelationEngine:
    def __init__(self, es_client, kafka_producer, incident_service):
        self.es = es_client
        self.kafka = kafka_producer
        self.incidents = incident_service
        self.rules = self._load_rules()

    async def evaluate(self, event: dict) -> Optional[CorrelationAlert]:
        """Evaluate event against all correlation rules."""

        for rule in self.rules:
            if not self._matches_category(rule, event):
                continue

            # Query matching events in time window
            matches = await self._query_matches(
                rule=rule,
                event=event,
                window=rule.window_minutes
            )

            if len(matches) >= rule.threshold:
                alert = self._create_alert(rule, matches, event)

                # Publish alert
                await self.kafka.send(
                    "dcim.siem.alerts",
                    key=alert.alert_id,
                    value=json.dumps(alert.__dict__, default=str)
                )

                # Auto-create incident for critical/high
                if alert.severity in ("critical", "high"):
                    await self.incidents.create_from_alert(alert)

                return alert

        return None

    async def _query_matches(self, rule: CorrelationRule, event: dict, window: int) -> List[dict]:
        """Query Elasticsearch for matching events in time window."""

        query = {
            "bool": {
                "must": [
                    {"term": {"category": rule.category}},
                    {"range": {
                        "timestamp": {
                            "gte": (datetime.utcnow() - timedelta(minutes=window)).isoformat()
                        }
                    }}
                ],
                "filter": []
            }
        }

        # Add rule-specific filters
        if rule.rule_id == "CR-001":  # Brute force
            query["bool"]["filter"].append({"term": {"source_ip": event.get("source_ip")}})
            query["bool"]["filter"].append({"term": {"severity": "low"}})  # failed logins are low
            query["bool"]["must"].append({"term": {"category": "authentication"}})

        result = await self.es.search(
            index="dcim-siem-*",
            query=query,
            size=100
        )

        return [hit["_source"] for hit in result["hits"]["hits"]]

    def _create_alert(self, rule: CorrelationRule, matches: List[dict], trigger_event: dict) -> CorrelationAlert:
        """Create correlation alert."""

        affected_assets = list(set([
            m.get("asset_id") for m in matches if m.get("asset_id")
        ]))

        affected_ips = list(set([
            m.get("source_ip") for m in matches if m.get("source_ip")
        ]))

        return CorrelationAlert(
            alert_id=str(uuid.uuid4()),
            rule_id=rule.rule_id,
            rule_name=rule.name,
            severity=rule.severity,
            triggered_at=datetime.utcnow(),
            matched_events=matches[:10],  # Limit to 10
            affected_assets=[{"asset_id": a} for a in affected_assets],
            description=f"{rule.name}: {len(matches)} events from {affected_ips} in {rule.window_minutes}min window",
            recommended_action=self._get_recommended_action(rule.rule_id)
        )

    def _get_recommended_action(self, rule_id: str) -> str:
        """Get recommended action for rule."""
        actions = {
            "CR-001": "Block source IP, investigate account for compromise",
            "CR-002": "Block IP immediately, force password reset for affected accounts",
            "CR-003": "Verify user identity, check for unauthorized access",
            "CR-004": "Isolate system, investigate file changes, restore from backup",
            "CR-005": "Isolate system immediately, run full AV scan",
            "CR-006": "Investigate both IPs, check for lateral movement",
            "CR-007": "Block outbound transfer, investigate data access",
            "CR-008": "Review change log, verify change is authorized",
            "CR-009": "Investigate service stop cause, restart if needed",
            "CR-010": "Apply remediation per CIS benchmark guide",
        }
        return actions.get(rule_id, "Investigate manually")
```

### 4.3 Alert Flow

```
Correlation Alert Created
  │
  ├── Severity: Critical/High
  │   ├── Auto-create incident (workflow-automation)
  │   ├── Send Slack/Email/PagerDuty notification
  │   └── Update SOC dashboard (WebSocket push)
  │
  ├── Severity: Medium
  │   ├── Log alert (no auto-incident)
  │   ├── Send Slack notification
  │   └── Update SOC dashboard
  │
  └── Severity: Low/Info
      └── Log alert only
```

---

## 5. Incident Response Workflow

### 5.1 Incident Lifecycle

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Created │───→│Triaging  │───→│Investigat│───→│ Remediat │───→│ Resolved │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                    │                │
                                    ▼                ▼
                               ┌──────────┐    ┌──────────┐
                               │ Escalated│    │ Closed   │
                               └──────────┘    └──────────┘
```

### 5.2 Incident Data Model

```sql
CREATE TABLE siem_incident (
    incident_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    status VARCHAR(20) NOT NULL DEFAULT 'created'
        CHECK (status IN ('created', 'triaging', 'investigating', 'remediating', 'escalated', 'resolved', 'closed')),

    -- Source
    alert_id UUID,
    rule_id VARCHAR(20),
    correlation_id UUID,

    -- Affected assets
    affected_assets JSONB DEFAULT '[]',
    affected_cis JSONB DEFAULT '[]',

    -- Assignment
    assigned_to VARCHAR(100),
    assigned_team VARCHAR(100),

    -- Timeline
    created_at TIMESTAMPTZ DEFAULT NOW(),
    triaged_at TIMESTAMPTZ,
    investigating_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,

    -- SLA
    sla_deadline TIMESTAMPTZ,
    sla_breached BOOLEAN DEFAULT FALSE,

    -- Resolution
    root_cause TEXT,
    resolution TEXT,
    lessons_learned TEXT,

    -- Metadata
    created_by VARCHAR(100) DEFAULT 'system',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE siem_incident_event (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID NOT NULL REFERENCES siem_incident(incident_id),
    action VARCHAR(50) NOT NULL,
    actor VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 5.3 SLA Matrix

| Severity | Response Time | Resolution Time | Escalation |
|----------|--------------|-----------------|------------|
| Critical | < 15 min | < 4 hours | Immediate to SOC Lead + Management |
| High | < 30 min | < 8 hours | After 2h → SOC Lead |
| Medium | < 2 hours | < 24 hours | After 12h → SOC Lead |
| Low | < 8 hours | < 72 hours | After 48h → SOC Lead |

### 5.4 Auto-Response Actions

| Alert Type | Auto-Action | Approval Required |
|------------|------------|-------------------|
| Malware detected | Isolate host (network quarantine) | No (auto) |
| Brute force (>10) | Block source IP | No (auto) |
| Data exfiltration | Block outbound + alert | No (auto) |
| Config change | Log + notify owner | No (auto) |
| Service stop | Restart service + alert | Yes (if critical) |

---

## 6. CIS Benchmark Compliance

### 6.1 Supported Benchmarks

| Benchmark | Scope | Version |
|-----------|-------|---------|
| CIS Ubuntu 22.04 LTS | Linux servers | v1.0 |
| CIS CentOS 8 | Linux servers | v1.0 |
| CIS Windows Server 2022 | Windows servers | v1.0 |
| CIS PostgreSQL 16 | Database | v1.0 |
| CIS Docker | Containers | v1.0 |
| CIS Kubernetes | Orchestration | v1.0 |

### 6.2 Compliance Check Categories

| Category | Checks | Severity if Failed |
|----------|--------|-------------------|
| Access Control | Password policies, SSH config, sudo rules | High |
| Network | Firewall rules, open ports, TLS config | High |
| Audit | Logging enabled, log rotation, auditd | Medium |
| System | File permissions, kernel params, updates | Medium |
| Database | Auth config, encryption, backup, roles | Critical |
| Container | Image scanning, runtime config, secrets | High |

### 6.3 Compliance Report Schema

```json
{
  "report_id": "uuid",
  "benchmark": "CIS Ubuntu 22.04",
  "target": "web-server-01",
  "scan_date": "2026-06-23T02:00:00Z",
  "overall_score": 78.5,
  "total_checks": 250,
  "passed": 196,
  "failed": 42,
  "not_applicable": 12,
  "categories": [
    {
      "name": "Access Control",
      "score": 85.0,
      "passed": 45,
      "failed": 8,
      "checks": [
        {
          "check_id": "5.4.1",
          "description": "Ensure password creation policy is configured",
          "status": "pass",
          "severity": "medium"
        }
      ]
    }
  ],
  "remediation": [
    {
      "check_id": "5.2.1",
      "description": "Ensure password expiration is 365 days or less",
      "current_value": "99999",
      "recommended_value": "365",
      "command": "sed -i 's/PASS_MAX_DAYS.*/PASS_MAX_DAYS 365/' /etc/login.defs"
    }
  ]
}
```

---

## 7. SOC API

### 7.1 API Design

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/soc/events` | soc:read | Query security events |
| GET | `/api/v1/soc/events/{id}` | soc:read | Get event detail |
| GET | `/api/v1/soc/alerts` | soc:read | List correlation alerts |
| GET | `/api/v1/soc/alerts/{id}` | soc:read | Get alert detail |
| GET | `/api/v1/soc/incidents` | soc:read | List incidents |
| POST | `/api/v1/soc/incidents` | soc:write | Create incident |
| GET | `/api/v1/soc/incidents/{id}` | soc:read | Get incident detail |
| PUT | `/api/v1/soc/incidents/{id}` | soc:write | Update incident |
| POST | `/api/v1/soc/incidents/{id}/assign` | soc:write | Assign incident |
| POST | `/api/v1/soc/incidents/{id}/resolve` | soc:write | Resolve incident |
| GET | `/api/v1/soc/compliance` | soc:read | List compliance reports |
| GET | `/api/v1/soc/compliance/{id}` | soc:read | Get compliance report |
| GET | `/api/v1/soc/reports/export` | soc:read | Export report (CSV/JSON) |
| GET | `/api/v1/soc/dashboard` | soc:read | SOC dashboard summary |

### 7.2 Query Parameters

```
GET /api/v1/soc/events?
  severity=high,critical
  &category=authentication
  &source_ip=10.70.0.50
  &from=2026-06-23T00:00:00Z
  &to=2026-06-23T23:59:59Z
  &page=1
  &limit=50
  &sort=timestamp:desc
```

### 7.3 SOC Dashboard Summary

```json
{
  "timestamp": "2026-06-23T14:30:00Z",
  "summary": {
    "total_events_today": 134567,
    "events_by_severity": {
      "critical": 12,
      "high": 45,
      "medium": 234,
      "low": 1245,
      "info": 133031
    },
    "active_alerts": 8,
    "open_incidents": 3,
    "incidents_by_severity": {
      "critical": 1,
      "high": 1,
      "medium": 1,
      "low": 0
    },
    "mttr_hours": 2.5,
    "compliance_score": 78.5,
    "top_attacked_assets": [
      {"asset_id": "...", "name": "web-server-01", "alerts": 5},
      {"asset_id": "...", "name": "db-primary", "alerts": 3}
    ]
  }
}
```

---

## 8. Elasticsearch Configuration

### 8.1 Index Templates

```json
{
  "index_patterns": ["dcim-siem-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.lifecycle.name": "dcim-siem-policy",
      "index.lifecycle.rollover_alias": "dcim-siem"
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "event_id": { "type": "keyword" },
        "source_type": { "type": "keyword" },
        "severity": { "type": "keyword" },
        "category": { "type": "keyword" },
        "title": { "type": "text", "fields": { "keyword": { "type": "keyword" } } },
        "description": { "type": "text" },
        "source_ip": { "type": "ip" },
        "destination_ip": { "type": "ip" },
        "user": { "type": "keyword" },
        "agent_name": { "type": "keyword" },
        "agent_ip": { "type": "ip" },
        "asset_id": { "type": "keyword" },
        "ci_id": { "type": "keyword" },
        "rule_id": { "type": "keyword" },
        "tags": { "type": "keyword" }
      }
    }
  }
}
```

### 8.2 ILM Policy

```json
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": { "max_primary_shard_size": "30gb", "max_age": "1d" },
          "set_priority": { "priority": 100 }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 },
          "set_priority": { "priority": 50 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": { "set_priority": { "priority": 0 } }
      },
      "delete": {
        "min_age": "90d",
        "actions": { "delete": {} }
      }
    }
  }
}
```

---

## 9. Data Retention & Archival

| Data Type | Hot | Warm | Cold | Delete | Total |
|-----------|-----|------|------|--------|-------|
| Security events | 7d | 23d | 60d | 90d | 90d |
| Correlation alerts | 30d | 60d | — | 180d | 180d |
| Incidents | — | — | — | — | Indefinite |
| Compliance reports | — | — | — | — | 7 years |
| Audit logs | — | — | — | — | 7 years |

---

## 10. Security

### 10.1 Security Controls

| Control | Implementation |
|---------|---------------|
| TLS 1.2+ | All SIEM traffic encrypted |
| RBAC | 4 roles: soc_admin, soc_analyst, soc_viewer, auditor |
| Audit trail | Every action logged |
| Data classification | Security events = Confidential |
| Encryption at rest | AES-256 for Elasticsearch |
| Access logging | All API calls logged |
| Secret management | Vault for credentials |

### 10.2 RBAC Matrix

| Role | Events | Alerts | Incidents | Compliance | Admin |
|------|--------|--------|-----------|------------|-------|
| soc_admin | ✅ | ✅ | ✅ CRUD | ✅ | ✅ |
| soc_analyst | ✅ | ✅ | ✅ Update | ✅ | ❌ |
| soc_viewer | ✅ | ✅ | ✅ Read | ✅ | ❌ |
| auditor | ✅ | ✅ | ✅ Read | ✅ | ❌ |

---

## 11. Monitoring & Alerting

### 11.1 Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `siem_events_ingested_total` | Counter | Events ingested |
| `siem_events_by_severity` | Counter | Events by severity |
| `siem_correlation_alerts_total` | Counter | Correlation alerts |
| `siem_incidents_open` | Gauge | Open incidents |
| `siem_incidents_by_severity` | Gauge | Incidents by severity |
| `siem_mttr_hours` | Gauge | Mean time to resolve |
| `siem_compliance_score` | Gauge | Overall compliance score |
| `siem_ingestion_latency_seconds` | Histogram | Ingestion latency |
| `siem_correlation_latency_seconds` | Histogram | Correlation latency |
| `siem_es_index_size_bytes` | Gauge | ES index size |

### 11.2 Alert Rules

```yaml
groups:
  - name: siem-soc
    rules:
      - alert: SIEMIngestionRateDrop
        expr: rate(siem_events_ingested_total[5m]) < 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "SIEM ingestion rate dropped below 100 eps"

      - alert: SIEMCriticalIncidentOpen
        expr: siem_incidents_by_severity{severity="critical"} > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Critical security incident open"

      - alert: SIEMMTTRHigh
        expr: siem_mttr_hours > 4
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "MTTR exceeded 4 hours"

      - alert: SIEMComplianceScoreLow
        expr: siem_compliance_score < 70
        for: 7d
        labels:
          severity: warning
        annotations:
          summary: "Compliance score below 70%"

      - alert: SIEMIngestionLatencyHigh
        expr: histogram_quantile(0.99, rate(siem_ingestion_latency_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "SIEM ingestion p99 latency > 10s"
```

---

## 12. Acceptance Criteria — Block 6 Complete

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | Wazuh agents deployed | Agents on all servers | ⬜ |
| 2 | Syslog → Kafka pipeline | Events flow to dcim.siem.events | ⬜ |
| 3 | Events stored in ES | dcim-siem-* indices created | ⬜ |
| 4 | Security event schema | Normalized schema defined | ⬜ |
| 5 | Correlation engine working | 10 rules tested | ⬜ |
| 6 | Alerting working | Real-time alerts fire | ⬜ |
| 7 | Incident auto-creation | Critical/High → incident | ⬜ |
| 8 | Incident workflow | Create → triage → investigate → resolve | ⬜ |
| 9 | SLA enforcement | SLA tracking + breach alert | ⬜ |
| 10 | CIS benchmark checks | Automated scan runs | ⬜ |
| 11 | Compliance reports | Report generation works | ⬜ |
| 12 | SOC API working | All endpoints tested | ⬜ |
| 13 | SOC dashboard | Summary view in dashboard | ⬜ |
| 14 | RBAC enforced | Unauthorized access blocked | ⬜ |
| 15 | Monitoring dashboards | Grafana shows SIEM metrics | ⬜ |
| 16 | Alert rules active | Test alert fires | ⬜ |

---

## 13. Gap Comparison Template

### Gap: [Component Name]

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Ingestion | [spec pipeline] | [aktual pipeline] | [match/mismatch] | P1-P4 |
| Schema | [spec fields] | [aktual fields] | [gap detail] | P1-P4 |
| Correlation | [spec rules] | [aktual rules] | [gap detail] | P1-P4 |
| Incident response | [spec workflow] | [aktual workflow] | [gap detail] | P1-P4 |
| Compliance | [spec benchmarks] | [aktual benchmarks] | [gap detail] | P1-P4 |
| SOC API | [spec endpoints] | [aktual endpoints] | [gap detail] | P1-P4 |
| Retention | [spec periods] | [aktual periods] | [gap detail] | P1-P4 |
| Security | [spec controls] | [aktual controls] | [gap detail] | P1-P4 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

## References

- [[siem-soc]]
- [[data-ingestion-integration]] — event pipeline
- [[elasticsearch]] — security event storage
- [[workflow-automation]] — incident escalation
- [[web-dashboard]] — SOC view
- [[siem-investigation-runbook]]
- [[siem-solution-comparison]]
- [[dcim-core-platform]]

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-23
> **Purpose:** Reference for team comparison → gap identification → connection dots
> **Phase 2 Progress:** Block 5 ✅ → Block 6 ✅ → Block 7 ⬜ → Block 8 ⬜ → Block 9 ⬜
