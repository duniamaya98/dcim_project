---
title: "Block 9 — External Integrations: Reference Design Spec"
created: 2026-06-23
updated: 2026-06-23
type: reference-design
block: 9
phase: 2
status: generated
confidence: high
tags: [integrations, adapter-pattern, itsm, erp, dms, nms, cloud, aws, gcp, azure, health-monitoring]
wiki_pages:
  - external-integration
  - data-ingestion-integration
  - cmdb
  - asset-repository
  - integration-health-runbook
  - integration-patterns
  - cloud-provider-comparison
  - erp-solution-comparison
  - itsm-solution-comparison
  - network-monitoring-comparison
  - dcim-integration-architecture
purpose: >
  Reference design spec untuk Block 9 External Integrations.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# Block 9 — External Integrations: Reference Design Spec

> **Purpose:** Dokumen referensi lengkap untuk External Integrations — adapter pattern framework, 10 connectors, health monitoring.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi. Setiap gap = connection point.
> **Architecture Diagram:** `diagrams/block9-external-integrations-architecture.html`
> **Depends on:** Block 2 (DI&I), Block 3 (Asset Repository), Block 4 (CMDB)
> **Note:** Block terakhir Phase 2 — seluruh reference design selesai setelah ini.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Adapter Framework](#2-adapter-framework)
3. [ITSM Connectors](#3-itsm-connectors)
4. [ERP Connectors](#4-erp-connectors)
5. [DMS Connector](#5-dms-connector)
6. [NMS Connector](#6-nms-connector)
7. [Cloud Connectors](#7-cloud-connectors)
8. [Integration Health Monitoring](#8-integration-health-monitoring)
9. [Data Mapping & Normalization](#9-data-mapping--normalization)
10. [Security](#10-security)
11. [Monitoring & Alerting](#11-monitoring--alerting)
12. [Acceptance Criteria](#12-acceptance-criteria)
13. [Gap Comparison Template](#13-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                   External Integrations                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Adapter Framework                            │  │
│  │  Base Adapter • Normalizer • Error Handler • Health Check │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐  │
│  │              Connectors                                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ServiceNow│ │  Jira    │ │   SAP    │ │  Oracle  │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │   DMS    │ │   NMS    │ │   AWS    │ │   GCP    │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  │  ┌──────────┐                                           │  │
│  │  │  Azure   │                                           │  │
│  │  └──────────┘                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Health Monitoring                            │  │
│  │  Connectivity • Sync Status • Alert • Dashboard           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                 │                │
         ▼                 ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │   CMDB   │    │  Asset   │    │   DI&I       │
  │(CI sync) │    │ Repository│   │ (pipeline)   │
  └──────────┘    └──────────┘    └──────────────┘
```

### 1.2 Adapter Pattern

```
External System → Adapter (per-system) → Normalizer → DCIM Core
                                                      │
                                         ┌─────────────┴─────────────┐
                                         ▼                           ▼
                                    CMDB/Asset                 DI&I Pipeline
```

### 1.3 Connector Matrix

| Connector | Category | Protocol | Sync | Auth | Frequency |
|-----------|----------|----------|------|------|-----------|
| ServiceNow | ITSM | REST API | Bidirectional | OAuth2 | Real-time + polling |
| Jira | ITSM | REST API | Bidirectional | API Key | Real-time + polling |
| SAP | ERP | RFC/REST | Outbound | SSO | Batch (daily) |
| Oracle | ERP | REST API | Outbound | OAuth2 | Batch (daily) |
| DMS | Documents | REST API | Bidirectional | API Key | Event-driven |
| NMS | Network | SNMP/REST | Outbound | SNMPv3 | Polling (5min) |
| AWS | Cloud | REST API | Outbound | IAM Role | Polling (5min) |
| GCP | Cloud | REST API | Outbound | Service Account | Polling (5min) |
| Azure | Cloud | REST API | Outbound | Managed Identity | Polling (5min) |

---

## 2. Adapter Framework

### 2.1 Base Adapter Interface

```python
# integrations/base_adapter.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class BaseAdapter(ABC):
    """Base class for all external system adapters."""

    def __init__(self, config: dict, db, redis_client, kafka_producer):
        self.config = config
        self.db = db
        self.redis = redis_client
        self.kafka = kafka_producer
        self.name = config.get("name", "unknown")
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

    @abstractmethod
    async def test_connection(self) -> dict:
        """Test connectivity to external system."""
        pass

    @abstractmethod
    async def pull_data(self, since: Optional[datetime] = None) -> List[dict]:
        """Pull data from external system."""
        pass

    @abstractmethod
    async def push_data(self, data: List[dict]) -> dict:
        """Push data to external system."""
        pass

    @abstractmethod
    async def normalize(self, raw_data: List[dict]) -> List[dict]:
        """Normalize external data to DCIM format."""
        pass

    async def sync(self, direction: str = "pull") -> dict:
        """Execute sync operation with error handling."""

        sync_log = {
            "connector": self.name,
            "direction": direction,
            "started_at": datetime.utcnow(),
            "status": "running"
        }

        try:
            if direction == "pull":
                raw_data = await self.pull_data()
                normalized = await self.normalize(raw_data)
                result = await self._process_normalized(normalized)
            else:
                result = await self.push_data(await self._prepare_push_data())

            sync_log["status"] = "completed"
            sync_log["records_processed"] = result.get("count", 0)

        except Exception as e:
            sync_log["status"] = "failed"
            sync_log["error"] = str(e)

            # Publish to DLQ
            await self.kafka.send(
                "dcim.integration.dlq",
                key=self.name,
                value=json.dumps(sync_log)
            )

        sync_log["completed_at"] = datetime.utcnow()
        sync_log["duration_ms"] = (sync_log["completed_at"] - sync_log["started_at"]).total_seconds() * 1000

        # Store sync log
        await self.db.log_sync(sync_log)

        # Update health status
        await self._update_health(sync_log)

        return sync_log

    async def _process_normalized(self, data: List[dict]) -> dict:
        """Process normalized data into DCIM core."""

        created = updated = errors = 0

        for record in data:
            try:
                # Determine action (create/update)
                existing = await self._find_existing(record)

                if existing:
                    await self._update_record(existing, record)
                    updated += 1
                else:
                    await self._create_record(record)
                    created += 1

            except Exception as e:
                errors += 1
                await self._log_error(record, str(e))

        return {"created": created, "updated": updated, "errors": errors, "count": len(data)}
```

### 2.2 Circuit Breaker

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker open for {self.name}")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        return (datetime.utcnow() - self.last_failure_time).total_seconds() > self.recovery_timeout
```

### 2.3 Normalizer

```python
# integrations/normalizer.py

class DataNormalizer:
    """Normalize external system data to DCIM standard format."""

    def __init__(self):
        self.mappers = {}
        self._load_mappers()

    def normalize_asset(self, external_data: dict, source_system: str) -> dict:
        """Normalize external asset data to DCIM asset format."""

        mapper = self.mappers.get(source_system)
        if not mapper:
            raise ValueError(f"No mapper for source: {source_system}")

        normalized = {}
        for dcim_field, mapping in mapper["fields"].items():
            value = self._extract_value(external_data, mapping["source_field"])

            # Apply transformation
            if mapping.get("transform"):
                value = self._apply_transform(value, mapping["transform"])

            # Apply default
            if value is None and mapping.get("default"):
                value = mapping["default"]

            normalized[dcim_field] = value

        # Add metadata
        normalized["_source"] = source_system
        normalized["_normalized_at"] = datetime.utcnow().isoformat()

        return normalized

    def normalize_ci(self, external_data: dict, source_system: str) -> dict:
        """Normalize external CI data to DCIM CI format."""

        mapper = self.mappers.get(source_system)
        if not mapper:
            raise ValueError(f"No mapper for source: {source_system}")

        normalized = {}
        for dcim_field, mapping in mapper.get("ci_fields", {}).items():
            value = self._extract_value(external_data, mapping["source_field"])
            if mapping.get("transform"):
                value = self._apply_transform(value, mapping["transform"])
            normalized[dcim_field] = value

        normalized["_source"] = source_system
        normalized["_normalized_at"] = datetime.utcnow().isoformat()

        return normalized
```

---

## 3. ITSM Connectors

### 3.1 ServiceNow Adapter

```python
# integrations/servicenow.py

class ServiceNowAdapter(BaseAdapter):
    def __init__(self, config, db, redis, kafka):
        super().__init__(config, db, redis, kafka)
        self.base_url = config["snow_url"]
        self.auth = OAuth2Auth(config["client_id"], config["client_secret"])

    async def test_connection(self) -> dict:
        result = await self.auth.get(f"{self.base_url}/api/now/table/sys_user?sysparm_limit=1")
        return {"status": "ok" if result else "failed", "system": "ServiceNow"}

    async def pull_data(self, since=None) -> List[dict]:
        query = "sys_updated_on>javascript:gs.hoursAgoStart(1)"
        if since:
            query = f"sys_updated_on>{since.isoformat()}"

        incidents = await self.auth.get(
            f"{self.base_url}/api/now/table/incident",
            params={"sysparm_query": query, "sysparm_limit": 1000}
        )

        return incidents

    async def normalize(self, data) -> List[dict]:
        return [
            {
                "ticket_number": inc["number"],
                "title": inc["short_description"],
                "description": inc["description"],
                "severity": self._map_severity(inc["severity"]),
                "priority": self._map_priority(inc["priority"]),
                "status": inc["state"],
                "assignee": inc["assigned_to"],
                "category": inc["category"],
                "created_at": inc["sys_created_on"],
                "updated_at": inc["sys_updated_on"],
            }
            for inc in data
        ]

    async def push_data(self, data) -> dict:
        """Push DCIM alerts to ServiceNow as incidents."""
        created = 0
        for alert in data:
            incident = await self.auth.post(
                f"{self.base_url}/api/now/table/incident",
                json={
                    "short_description": alert["title"],
                    "description": alert["description"],
                    "priority": self._map_priority(alert["severity"]),
                    "category": "hardware",
                    "assignment_group": self._get_assignment_group(alert),
                }
            )
            created += 1
        return {"created": created}
```

### 3.2 Jira Adapter

```python
class JiraAdapter(BaseAdapter):
    def __init__(self, config, db, redis, kafka):
        super().__init__(config, db, redis, kafka)
        self.base_url = config["jira_url"]
        self.auth = APIKeyAuth(config["email"], config["api_key"])

    async def pull_data(self, since=None) -> List[dict]:
        jql = f"updated >= '{(since or datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%d')}'"

        issues = await self.auth.get(
            f"{self.base_url}/rest/api/3/search",
            params={"jql": jql, "maxResults": 1000}
        )

        return [self._normalize_issue(issue) for issue in issues.get("issues", [])]

    async def push_data(self, data) -> dict:
        """Create Jira issues from DCIM alerts."""
        created = 0
        for alert in data:
            await self.auth.post(
                f"{self.base_url}/rest/api/3/issue",
                json={
                    "fields": {
                        "project": {"key": "DCIM"},
                        "issuetype": {"name": "Incident"},
                        "summary": alert["title"],
                        "description": alert["description"],
                        "priority": {"name": self._map_priority(alert["severity"])},
                    }
                }
            )
            created += 1
        return {"created": created}
```

---

## 4. ERP Connectors

### 4.1 SAP Adapter

```python
class SAPAdapter(BaseAdapter):
    def __init__(self, config, db, redis, kafka):
        super().__init__(config, db, redis, kafka)
        self.base_url = config["sap_url"]
        self.auth = SAPAuth(config["client_id"], config["client_secret"])

    async def pull_data(self, since=None) -> List[dict]:
        """Pull asset master data from SAP."""

        # Pull from SAP Asset Master
        assets = await self.auth.get(
            f"{self.base_url}/sap/bc/rest/asset_master",
            params={"$filter": f"ModifiedAt gt {since or ''}"}
        )

        return assets

    async def normalize(self, data) -> List[dict]:
        return [
            {
                "serial_number": sap_asset["SerialNumber"],
                "name": sap_asset["AssetDescription"],
                "manufacturer": sap_asset["Manufacturer"],
                "model": sap_asset["ModelNumber"],
                "purchase_cost": float(sap_asset.get("AcquisitionValue", 0)),
                "purchase_date": sap_asset.get("AcquisitionDate"),
                "depreciation_method": self._map_depreciation(sap_asset["DepreciationKey"]),
                "useful_life_years": int(sap_asset.get("UsefulLifeYears", 5)),
                "book_value": float(sap_asset.get("NetBookValue", 0)),
                "sap_asset_id": sap_asset["AssetNumber"],
                "sap_cost_center": sap_asset.get("CostCenter"),
                "_source": "sap"
            }
            for sap_asset in data
        ]
```

### 4.2 Oracle Adapter

```python
class OracleERPAdapter(BaseAdapter):
    def __init__(self, config, db, redis, kafka):
        super().__init__(config, db, redis, kafka)
        self.base_url = config["oracle_url"]
        self.auth = OAuth2Auth(config["client_id"], config["client_secret"])

    async def pull_data(self, since=None) -> List[dict]:
        """Pull procurement and inventory data from Oracle."""

        # Pull purchase orders
        pos = await self.auth.get(
            f"{self.base_url}/fscmRestApi/resources/latest/purchaseOrders",
            params={"q": f"LastUpdateDate>='{since or ''}'"}
        )

        return pos

    async def normalize(self, data) -> List[dict]:
        return [
            {
                "po_number": po["PoNumber"],
                "vendor": po["SupplierName"],
                "total_amount": float(po.get("Amount", 0)),
                "status": po["Status"],
                "line_items": [
                    {
                        "item": item["ItemDescription"],
                        "quantity": item["Quantity"],
                        "unit_price": float(item.get("UnitPrice", 0)),
                    }
                    for item in po.get("LineItems", [])
                ],
                "_source": "oracle"
            }
            for po in data
        ]
```

---

## 5. DMS Connector

```python
# integrations/dms.py

class DMSAdapter(BaseAdapter):
    def __init__(self, config, db, redis, kafka):
        super().__init__(config, db, redis, kafka)
        self.base_url = config["dms_url"]
        self.auth = APIKeyAuth(config["api_key"])

    async def pull_data(self, since=None) -> List[dict]:
        """Pull documents related to CIs and assets."""

        docs = await self.auth.get(
            f"{self.base_url}/api/v1/documents",
            params={"modified_after": since.isoformat() if since else None}
        )

        return docs

    async def link_to_ci(self, document_id: str, ci_id: str, doc_type: str):
        """Link document to CI in DMS."""

        await self.auth.post(
            f"{self.base_url}/api/v1/documents/{document_id}/links",
            json={
                "entity_type": "ci",
                "entity_id": ci_id,
                "link_type": doc_type,  # 'sop', 'manual', 'certificate', 'diagram'
            }
        )

    async def get_documents_for_ci(self, ci_id: str) -> List[dict]:
        """Get all documents linked to a CI."""

        links = await self.auth.get(
            f"{self.base_url}/api/v1/links",
            params={"entity_type": "ci", "entity_id": ci_id}
        )

        return [await self._get_document(link["document_id"]) for link in links]
```

---

## 6. NMS Connector

```python
# integrations/nms.py

class NMSAdapter(BaseAdapter):
    def __init__(self, config, db, redis, kafka):
        super().__init__(config, db, redis, kafka)
        self.base_url = config["nms_url"]
        self.auth = SNMPAuth(config["community"], config.get("version", "v3"))

    async def pull_data(self, since=None) -> List[dict]:
        """Pull network device data from NMS."""

        # Discover devices
        devices = await self._discover_devices()

        # Pull performance metrics
        for device in devices:
            metrics = await self._poll_metrics(device)
            device["metrics"] = metrics

        return devices

    async def _discover_devices(self) -> List[dict]:
        """Discover network devices via SNMP."""

        # SNMP walk for device inventory
        devices = await self.auth.walk(
            oid="1.3.6.1.2.1.1.1.0",  # sysDescr
            target=self.config["nms_host"]
        )

        return devices

    async def normalize(self, data) -> List[dict]:
        return [
            {
                "ci_type": "network_device",
                "name": device.get("sysName", device.get("hostname")),
                "ip_address": device.get("ipAddress"),
                "vendor": self._detect_vendor(device.get("sysDescr", "")),
                "model": device.get("model"),
                "os_version": device.get("sysDescr"),
                "status": "active" if device.get("reachable") else "error",
                "interfaces": device.get("interfaces", []),
                "metrics": device.get("metrics", {}),
                "_source": "nms"
            }
            for device in data
        ]
```

---

## 7. Cloud Connectors

### 7.1 AWS Adapter

```python
# integrations/aws.py

class AWSAdapter(BaseAdapter):
    def __init__(self, config, db, redis, kafka):
        super().__init__(config, db, redis, kafka)
        self.session = boto3.Session(
            aws_access_key_id=config["access_key"],
            aws_secret_access_key=config["secret_key"],
            region_name=config["region"]
        )

    async def pull_data(self, since=None) -> List[dict]:
        """Pull AWS resources (EC2, RDS, S3)."""

        resources = []

        # EC2 instances
        ec2 = self.session.client('ec2')
        instances = ec2.describe_instances()
        for reservation in instances["Reservations"]:
            for instance in reservation["Instances"]:
                resources.append(self._normalize_ec2(instance))

        # RDS instances
        rds = self.session.client('rds')
        dbs = rds.describe_db_instances()
        for db in dbs["DBInstances"]:
            resources.append(self._normalize_rds(db))

        # S3 buckets
        s3 = self.session.client('s3')
        buckets = s3.list_buckets()
        for bucket in buckets["Buckets"]:
            resources.append(self._normalize_s3(bucket))

        return resources

    def _normalize_ec2(self, instance: dict) -> dict:
        return {
            "ci_type": "server",
            "name": self._get_tag(instance.get("Tags", []), "Name") or instance["InstanceId"],
            "cloud_provider": "aws",
            "cloud_service": "ec2",
            "cloud_resource_id": instance["InstanceId"],
            "ip_address": instance.get("PrivateIpAddress"),
            "os": instance.get("Platform", "linux"),
            "instance_type": instance.get("InstanceType"),
            "status": "active" if instance["State"]["Name"] == "running" else instance["State"]["Name"],
            "region": self.config["region"],
            "tags": {t["Key"]: t["Value"] for t in instance.get("Tags", [])},
            "_source": "aws"
        }

    def _normalize_rds(self, db: dict) -> dict:
        return {
            "ci_type": "storage",
            "name": db["DBInstanceIdentifier"],
            "cloud_provider": "aws",
            "cloud_service": "rds",
            "cloud_resource_id": db["DBInstanceArn"],
            "model": db.get("Engine"),
            "capacity_gb": db.get("AllocatedStorage"),
            "status": "active" if db["DBInstanceStatus"] == "available" else db["DBInstanceStatus"],
            "_source": "aws"
        }
```

### 7.2 GCP Adapter

```python
class GCPAdapter(BaseAdapter):
    def __init__(self, config, db, redis, kafka):
        super().__init__(config, db, redis, kafka)
        self.compute = compute_v1.InstancesClient()
        self.project = config["project_id"]
        self.zone = config["zone"]

    async def pull_data(self, since=None) -> List[dict]:
        """Pull GCP Compute Engine instances."""

        instances = self.compute.list(request={"project": self.project, "zone": self.zone})

        return [self._normalize_instance(inst) for inst in instances]
```

### 7.3 Azure Adapter

```python
class AzureAdapter(BaseAdapter):
    def __init__(self, config, db, redis, kafka):
        super().__init__(config, db, redis, kafka)
        self.credential = DefaultAzureCredential()
        self.compute_client = ComputeManagementClient(self.credential, config["subscription_id"])

    async def pull_data(self, since=None) -> List[dict]:
        """Pull Azure VMs."""

        vms = self.compute_client.virtual_machines.list_all()

        return [self._normalize_vm(vm) for vm in vms]
```

---

## 8. Integration Health Monitoring

### 8.1 Health Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `integration_status` | Gauge | 1=healthy, 0=down |
| `integration_last_sync_at` | Gauge | Timestamp of last successful sync |
| `integration_sync_duration_seconds` | Histogram | Sync duration |
| `integration_records_synced_total` | Counter | Total records synced |
| `integration_sync_errors_total` | Counter | Total sync errors |
| `integration_circuit_breaker_state` | Gauge | 0=closed, 1=open, 2=half-open |
| `integration_queue_depth` | Gauge | Pending items in DLQ |

### 8.2 Health Check Implementation

```python
# integrations/health_monitor.py

class IntegrationHealthMonitor:
    def __init__(self, db, redis, kafka_producer):
        self.db = db
        self.redis = redis
        self.kafka = kafka_producer
        self.adapters = {}

    async def check_all_health(self) -> dict:
        """Check health of all integrations."""

        results = {}

        for name, adapter in self.adapters.items():
            health = await self._check_health(adapter)
            results[name] = health

            # Store in Redis for dashboard
            await self.redis.setex(
                f"integration:health:{name}",
                300,  # 5 min TTL
                json.dumps(health)
            )

        return results

    async def _check_health(self, adapter) -> dict:
        """Check health of a single integration."""

        health = {
            "connector": adapter.name,
            "checked_at": datetime.utcnow().isoformat(),
        }

        # 1. Connectivity test
        try:
            conn_result = await adapter.test_connection()
            health["connectivity"] = conn_result["status"]
        except Exception as e:
            health["connectivity"] = "failed"
            health["connectivity_error"] = str(e)

        # 2. Last sync status
        last_sync = await self.db.get_last_sync(adapter.name)
        health["last_sync"] = last_sync

        if last_sync:
            health["last_sync_ago_minutes"] = (
                datetime.utcnow() - datetime.fromisoformat(last_sync["completed_at"])
            ).total_seconds() / 60

        # 3. Error rate (last hour)
        error_count = await self.db.get_sync_errors(adapter.name, hours=1)
        health["errors_last_hour"] = error_count
        health["error_rate"] = "normal" if error_count < 5 else "elevated" if error_count < 20 else "critical"

        # 4. Circuit breaker state
        health["circuit_breaker"] = adapter.circuit_breaker.state.value

        # 5. Overall status
        health["status"] = self._determine_status(health)

        return health

    def _determine_status(self, health: dict) -> str:
        """Determine overall integration health."""

        if health.get("connectivity") == "failed":
            return "down"
        if health.get("error_rate") == "critical":
            return "critical"
        if health.get("error_rate") == "elevated":
            return "degraded"
        if health.get("circuit_breaker") == "open":
            return "circuit_open"

        return "healthy"
```

### 8.3 Alert Rules

```yaml
groups:
  - name: integration-health
    rules:
      - alert: IntegrationDown
        expr: integration_status == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Integration {{ $labels.connector }} is down"

      - alert: IntegrationSyncStale
        expr: time() - integration_last_sync_at > 7200
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Integration {{ $labels.connector }} hasn't synced in 2 hours"

      - alert: IntegrationCircuitOpen
        expr: integration_circuit_breaker_state == 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Circuit breaker open for {{ $labels.connector }}"

      - alert: IntegrationErrorRateHigh
        expr: rate(integration_sync_errors_total[1h]) > 10
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "High error rate for {{ $labels.connector }}"
```

---

## 9. Data Mapping & Normalization

### 9.1 Mapping Configuration

```yaml
# integrations/mappers/servicenow_asset.yaml

mapper:
  source: servicenow
  target: asset
  fields:
    asset_tag:
      source_field: "asset_tag"
      required: true
    serial_number:
      source_field: "serial_number"
      required: true
    name:
      source_field: "display_name"
      required: true
    manufacturer:
      source_field: "manufacturer.display_value"
      transform: "uppercase"
    model:
      source_field: "model_name"
    owner_dept:
      source_field: "assigned_to.department.name"
    purchase_cost:
      source_field: "cost"
      transform: "to_float"
    lifecycle_status:
      source_field: "install_status"
      transform: "map_lifecycle_status"
      mapping:
        1: "deployed"
        2: "in_storage"
        6: "retired"
        7: "disposed"
```

---

## 10. Security

| Control | Implementation |
|---------|---------------|
| Credential storage | Vault for all API keys and tokens |
| OAuth2 token refresh | Automatic refresh before expiry |
| API key rotation | 90-day rotation policy |
| TLS 1.2+ | All external connections encrypted |
| IP whitelisting | Where supported by external system |
| Audit logging | Every API call logged |
| Least privilege | Minimal required permissions |
| Circuit breaker | Prevent cascade failures |

---

## 11. Monitoring & Alerting

| Metric | Type | Description |
|--------|------|-------------|
| `integration_connectors_total` | Gauge | Total configured connectors |
| `integration_healthy_total` | Gauge | Healthy connectors |
| `integration_down_total` | Gauge | Down connectors |
| `integration_sync_total` | Counter | Total sync operations |
| `integration_sync_duration_seconds` | Histogram | Sync duration |
| `integration_records_synced_total` | Counter | Records synced |
| `integration_sync_errors_total` | Counter | Sync errors |
| `integration_dlq_depth` | Gauge | DLQ queue depth |

---

## 12. Acceptance Criteria — Block 9 Complete

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | Adapter framework working | Base adapter + normalizer | ⬜ |
| 2 | Circuit breaker working | Open/half-open/closed states | ⬜ |
| 3 | ServiceNow connector | Pull/push/normalize tested | ⬜ |
| 4 | Jira connector | Pull/push/normalize tested | ⬜ |
| 5 | SAP connector | Pull/normalize tested | ⬜ |
| 6 | Oracle connector | Pull/normalize tested | ⬜ |
| 7 | DMS connector | Link/unlink documents | ⬜ |
| 8 | NMS connector | SNMP discovery + metrics | ⬜ |
| 9 | AWS connector | EC2/RDS/S3 discovery | ⬜ |
| 10 | GCP connector | Compute Engine discovery | ⬜ |
| 11 | Azure connector | VM discovery | ⬜ |
| 12 | Health monitoring | All connectors status | ⬜ |
| 13 | DLQ handling | Failed syncs → DLQ | ⬜ |
| 14 | Sync logging | Every sync logged | ⬜ |
| 15 | Alert rules | Health alerts fire | ⬜ |
| 16 | Dashboard integration | Integration health view | ⬜ |

---

## 13. Gap Comparison Template

### Gap: [Connector Name]

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Framework | [spec features] | [aktual features] | [match/mismatch] | P1-P4 |
| Auth | [spec method] | [aktual method] | [gap detail] | P1-P4 |
| Sync direction | [spec direction] | [aktual direction] | [gap detail] | P1-P4 |
| Data mapping | [spec fields] | [aktual fields] | [gap detail] | P1-P4 |
| Error handling | [spec strategy] | [aktual strategy] | [gap detail] | P1-P4 |
| Health monitoring | [spec metrics] | [aktual metrics] | [gap detail] | P1-P4 |
| Performance | [spec targets] | [aktual metrics] | [gap detail] | P1-P4 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

## References

- [[external-integration]]
- [[data-ingestion-integration]] — data pipeline
- [[cmdb]] — CI enrichment from external sources
- [[asset-repository]] — asset sync
- [[integration-health-runbook]]
- [[integration-patterns]]
- [[cloud-provider-comparison]]
- [[erp-solution-comparison]]
- [[itsm-solution-comparison]]
- [[network-monitoring-comparison]]
- [[dcim-integration-architecture]]
- [[dcim-core-platform]]

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-23
> **Purpose:** Reference for team comparison → gap identification → connection dots
> **🎉 ALL PHASE 2 BLOCKS COMPLETE — PROJECT REFERENCE DESIGN FINISHED**
