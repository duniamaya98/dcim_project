# DCIM Core Platform Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a complete DCIM Core Platform for visibility, control, automation, analytics, and audit of data center infrastructure.

**Architecture:** Layered architecture: Source Systems → Data Ingestion & Integration → Core Data Stores → Intelligence → Automation → Presentation. Single gateway (DI&I) ingests all data, normalizes, validates, enriches, and routes to CMDB, Asset Repository, time-series, and SIEM stores.

**Tech Stack:** PostgreSQL 16, Redis 7, Kafka 3.x (KRaft), NiFi 1.x, Elasticsearch 8.x, Prometheus, Grafana, Vault, Docker/K8s, React/Vue, Python/Go

**Source:** DCIM Wiki (~/dcim-wiki/) — 147 pages, 19 entities, 79 concepts, 33 comparisons, 16 queries

---

## Overview

```
Phase 1: Infrastructure & Core Foundation (32 tasks, 4 blocks)
  Block 1: Infrastructure Provisioning (11 tasks)
  Block 2: Data Ingestion & Integration (12 tasks)
  Block 3: Asset Repository (8 tasks)
  Block 4: CMDB (10 tasks)

Phase 2: Intelligence, Automation & Presentation (30 tasks, 5 blocks)
  Block 5: Web Dashboard (11 tasks)
  Block 6: SIEM/SOC (6 tasks)
  Block 7: Analytics & AI Engine (8 tasks)
  Block 8: Workflow Automation (7 tasks)
  Block 9: External Integration (11 tasks)
```

**Critical Path:** ~27.5 hari single-threaded / 15-18 hari dengan 2 parallel teams

---

## Phase 1: Infrastructure & Core Foundation

### Block 1: Infrastructure Provisioning

**Objective:** Provision all infrastructure components as Docker Compose (dev/staging) or Kubernetes manifests (production)

**Dependencies:** None (foundation)

#### Task 1.1: Project Structure Setup

**Objective:** Create DCIM project directory structure and base configuration

**Files:**
- Create: `dcim-core/docker-compose.yml`
- Create: `dcim-core/.env.example`
- Create: `dcim-core/Makefile`
- Create: `dcim-core/README.md`

**Steps:**
1. Create directory structure
2. Create docker-compose.yml with all services
3. Create .env.example with configuration template
4. Create Makefile with common commands
5. Verify: `docker-compose config` passes

---

#### Task 1.2: PostgreSQL 16 Setup

**Objective:** Deploy PostgreSQL 16 with streaming replication for HA

**Files:**
- Create: `dcim-core/docker-compose.yml` (postgres service)
- Create: `dcim-core/postgres/init.sql`
- Create: `dcim-core/postgres/replication.conf`

**Steps:**
1. Add postgres service to docker-compose.yml
2. Configure streaming replication (primary + replica)
3. Set up PgBouncer for connection pooling
4. Create init.sql for database initialization
5. Verify: `docker-compose up -d postgres && docker-compose exec postgres psql -U dcim -c "SELECT version();"`

---

#### Task 1.3: Redis 7 Setup

**Objective:** Deploy Redis 7 with Sentinel for HA caching and session store

**Files:**
- Create: `dcim-core/docker-compose.yml` (redis service)
- Create: `dcim-core/redis/redis.conf`
- Create: `dcim-core/redis/sentinel.conf`

**Steps:**
1. Add redis service to docker-compose.yml
2. Configure Redis Sentinel for failover
3. Set up Redis persistence (RDB + AOF)
4. Verify: `docker-compose up -d redis && docker-compose exec redis redis-cli ping`

---

#### Task 1.4: Kafka 3.x Cluster Setup

**Objective:** Deploy Kafka 3.x cluster with KRaft (no ZooKeeper) for event streaming

**Files:**
- Create: `dcim-core/docker-compose.yml` (kafka services)
- Create: `dcim-core/kafka/kraft-config.sh`
- Create: `dcim-core/kafka/topics.sh`

**Steps:**
1. Add 3 kafka broker services to docker-compose.yml
2. Configure KRaft mode (no ZooKeeper)
3. Create topic structure:
   - `dcim.events.raw`
   - `dcim.events.validated`
   - `dcim.events.enriched`
   - `dcim.events.dlq`
   - `dcim.cmdb.updates`
   - `dcim.asset.updates`
4. Set replication factor: 3, min.insync.replicas: 2
5. Verify: `docker-compose up -d kafka && docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list`

---

#### Task 1.5: NiFi 1.x Deployment

**Objective:** Deploy Apache NiFi for data flow orchestration

**Files:**
- Create: `dcim-core/docker-compose.yml` (nifi service)
- Create: `dcim-core/nifi/flows/`

**Steps:**
1. Add nifi service to docker-compose.yml
2. Configure NiFi for DCIM data flows
3. Set up source connectors (BMS, NMS, Server, Cloud)
4. Verify: `docker-compose up -d nifi && curl -k https://localhost:8443/nifi-api/system-diagnostics`

---

#### Task 1.6: Elasticsearch 8.x Cluster

**Objective:** Deploy Elasticsearch 8.x for central logging and SIEM data store

**Files:**
- Create: `dcim-core/docker-compose.yml` (elasticsearch service)
- Create: `dcim-core/elasticsearch/elasticsearch.yml`
- Create: `dcim-core/elasticsearch/ilm-policy.json`

**Steps:**
1. Add elasticsearch service to docker-compose.yml
2. Configure cluster (3 nodes for HA)
3. Set up Index Lifecycle Management (ILM)
4. Configure security (TLS, authentication)
5. Verify: `docker-compose up -d elasticsearch && curl -k https://localhost:9200/_cluster/health`

---

#### Task 1.7: Prometheus + Grafana Base

**Objective:** Deploy Prometheus for metrics collection and Grafana for visualization

**Files:**
- Create: `dcim-core/docker-compose.yml` (prometheus, grafana services)
- Create: `dcim-core/prometheus/prometheus.yml`
- Create: `dcim-core/grafana/dashboards/`
- Create: `dcim-core/grafana/provisioning/`

**Steps:**
1. Add prometheus and grafana services to docker-compose.yml
2. Configure Prometheus scrape targets
3. Set up Grafana data sources (Prometheus, Elasticsearch, PostgreSQL)
4. Create base dashboards (infrastructure health)
5. Verify: `docker-compose up -d prometheus grafana && curl http://localhost:9090/api/v1/targets`

---

#### Task 1.8: HashiCorp Vault Deployment

**Objective:** Deploy Vault for secret management and dynamic credentials

**Files:**
- Create: `dcim-core/docker-compose.yml` (vault service)
- Create: `dcim-core/vault/config.hcl`
- Create: `dcim-core/vault/policies/dcim-policy.hcl`

**Steps:**
1. Add vault service to docker-compose.yml
2. Configure Vault for DCIM secrets
3. Set up policies for DCIM services
4. Enable audit logging
5. Verify: `docker-compose up -d vault && docker vault status`

---

#### Task 1.9: Network Segmentation

**Objective:** Configure VLAN segmentation and firewall rules

**Files:**
- Create: `dcim-core/network/vlan-config.yml`
- Create: `dcim-core/network/firewall-rules.sh`

**Steps:**
1. Define VLANs:
   - Management: 10.70.0.0/24
   - Data: 10.70.1.0/24
   - DMZ: 10.70.2.0/24
2. Configure firewall rules (default deny, allow required ports)
3. Enable TLS 1.2+ for all internal traffic
4. Verify: network connectivity tests

---

#### Task 1.10: Docker Compose / K8s Manifests

**Objective:** Create deployment manifests for development and production

**Files:**
- Create: `dcim-core/docker-compose.yml` (complete)
- Create: `dcim-core/k8s/namespace.yml`
- Create: `dcim-core/k8s/deployments/`
- Create: `dcim-core/k8s/services/`
- Create: `dcim-core/k8s/ingress.yml`

**Steps:**
1. Complete docker-compose.yml with all services
2. Create Kubernetes namespace, deployments, services
3. Configure Ingress for external access
4. Verify: `docker-compose config` and `kubectl apply -f k8s/ --dry-run=client`

---

#### Task 1.11: Base Monitoring

**Objective:** Configure base monitoring and alerting for all infrastructure components

**Files:**
- Create: `dcim-core/monitoring/alerts/`
- Create: `dcim-core/monitoring/dashboards/`

**Steps:**
1. Configure Prometheus alerting rules
2. Set up Grafana alerting
3. Configure notification channels (email, Slack)
4. Create base dashboards for all components
5. Verify: alerts fire correctly

---

### Block 2: Data Ingestion & Integration (DI&I)

**Objective:** Build single gateway for all data ingestion, validation, enrichment, and routing

**Dependencies:** Block 1 (Infrastructure)

#### Task 2.1: Normalized Event Schema Design

**Objective:** Design unified event schema for all DCIM events

**Files:**
- Create: `dcim-core/schemas/event-schema.json`
- Create: `dcim-core/schemas/event-types.json`

**Steps:**
1. Define base event schema:
   ```json
   {
     "event_id": "string (UUID)",
     "timestamp": "ISO 8601",
     "source_system": "string",
     "event_type": "string",
     "payload": "object",
     "metadata": {
       "priority": "P1-P4",
       "category": "string",
       "tags": ["string"]
     }
   }
   ```
2. Define event types per source system
3. Validate schema with JSON Schema
4. Verify: schema validation tests pass

---

#### Task 2.2: Kafka Topic Structure

**Objective:** Create and configure all Kafka topics for DCIM event streaming

**Files:**
- Create: `dcim-core/kafka/topics/create-topics.sh`
- Create: `dcim-core/kafka/topics/topic-config.json`

**Steps:**
1. Create topic creation script
2. Configure topic settings:
   - Replication factor: 3
   - Min.insync.replicas: 2
   - Retention: 7 days (raw), 30 days (validated, enriched)
3. Create all topics:
   - dcim.events.raw
   - dcim.events.validated
   - dcim.events.enriched
   - dcim.events.dlq
   - dcim.cmdb.updates
   - dcim.asset.updates
4. Verify: `kafka-topics --bootstrap-server localhost:9092 --list`

---

#### Task 2.3: NiFi Integration — BMS/EPMS

**Objective:** Configure NiFi flow for BMS/EPMS data ingestion

**Files:**
- Create: `dcim-core/nifi/flows/bms-epms-flow.xml`

**Steps:**
1. Create NiFi flow for BMS/EPMS
2. Configure processors:
   - GetFile/GetHTTP (ingest)
   - ValidateRecord (validation)
   - JoltTransformJSON (normalization)
   - PublishKafka (output)
3. Set up error handling (DLQ)
4. Verify: flow imports successfully

---

#### Task 2.4: NiFi Integration — NMS

**Objective:** Configure NiFi flow for NMS data ingestion

**Files:**
- Create: `dcim-core/nifi/flows/nms-flow.xml`

**Steps:**
1. Create NiFi flow for NMS
2. Configure SNMP/REST processors
3. Set up validation and normalization
4. Verify: flow imports successfully

---

#### Task 2.5: NiFi Integration — Server/Storage

**Objective:** Configure NiFi flow for server and storage monitoring data

**Files:**
- Create: `dcim-core/nifi/flows/server-storage-flow.xml`

**Steps:**
1. Create NiFi flow for server/storage
2. Configure SSH/REST processors
3. Set up validation and normalization
4. Verify: flow imports successfully

---

#### Task 2.6: NiFi Integration — Virtualization/Cloud

**Objective:** Configure NiFi flow for virtualization and cloud platform data

**Files:**
- Create: `dcim-core/nifi/flows/virtualization-cloud-flow.xml`

**Steps:**
1. Create NiFi flow for virtualization/cloud
2. Configure VMware/AWS/GCP/Azure connectors
3. Set up validation and normalization
4. Verify: flow imports successfully

---

#### Task 2.7: NiFi Integration — Access Control

**Objective:** Configure NiFi flow for access control and surveillance data

**Files:**
- Create: `dcim-core/nifi/flows/access-control-flow.xml`

**Steps:**
1. Create NiFi flow for access control
2. Configure badge/CCTV integrations
3. Set up validation and normalization
4. Verify: flow imports successfully

---

#### Task 2.8: Validation Processor

**Objective:** Implement event validation with schema, type, and range checks

**Files:**
- Create: `dcim-core/processors/validation.py`
- Create: `dcim-core/processors/tests/test_validation.py`

**Steps:**
1. Create validation processor
2. Implement:
   - Schema validation
   - Type checking
   - Range validation
   - Format validation
   - Duplicate detection (event_id + source_system)
3. Write tests
4. Verify: `pytest dcim-core/processors/tests/test_validation.py -v`

---

#### Task 2.9: Enrichment Processor

**Objective:** Implement event enrichment with CI reference, location, and priority metadata

**Files:**
- Create: `dcim-core/processors/enrichment.py`
- Create: `dcim-core/processors/tests/test_enrichment.py`

**Steps:**
1. Create enrichment processor
2. Implement:
   - CI reference lookup (from CMDB)
   - Location enrichment
   - Priority metadata assignment
   - Enrichment status tracking
3. Write tests
4. Verify: `pytest dcim-core/processors/tests/test_enrichment.py -v`

---

#### Task 2.10: DLQ Handling

**Objective:** Implement Dead Letter Queue handling with retry mechanism

**Files:**
- Create: `dcim-core/processors/dlq_handler.py`
- Create: `dcim-core/processors/tests/test_dlq.py`

**Steps:**
1. Create DLQ handler
2. Implement:
   - DLQ routing
   - Retry mechanism (exponential backoff)
   - Max retry limit
   - DLQ monitoring
3. Write tests
4. Verify: `pytest dcim-core/processors/tests/test_dlq.py -v`

---

#### Task 2.11: Data Lineage Tracking

**Objective:** Implement data lineage tracking from source to store

**Files:**
- Create: `dcim-core/processors/lineage.py`
- Create: `dcim-core/processors/tests/test_lineage.py`

**Steps:**
1. Create lineage tracker
2. Implement:
   - Source → validation → enrichment → store tracking
   - Event metadata enrichment
   - Lineage storage (PostgreSQL)
3. Write tests
4. Verify: `pytest dcim-core/processors/tests/test_lineage.py -v`

---

#### Task 2.12: ITSM/ERP/DMS Connectors

**Objective:** Implement connectors for ITSM, ERP, and DMS systems

**Files:**
- Create: `dcim-core/connectors/itsm.py`
- Create: `dcim-core/connectors/erp.py`
- Create: `dcim-core/connectors/dms.py`
- Create: `dcim-core/connectors/tests/test_connectors.py`

**Steps:**
1. Create base connector pattern
2. Implement ITSM connector (ServiceNow/Jira)
3. Implement ERP connector (SAP/Oracle)
4. Implement DMS connector
5. Write tests
6. Verify: `pytest dcim-core/connectors/tests/test_connectors.py -v`

---

### Block 3: Asset Repository

**Objective:** Build SSOT for asset physical, financial, and contract data

**Dependencies:** Block 1 (Infrastructure)

#### Task 3.1: Asset Data Model Design

**Objective:** Design asset data model with all required attributes

**Files:**
- Create: `dcim-core/models/asset.py`
- Create: `dcim-core/schemas/asset-schema.json`

**Steps:**
1. Design asset data model:
   - Asset_ID (AST-{seq})
   - Serial Number (unique per manufacturer)
   - Asset Tag (internal barcode/RFID)
   - Owner, PO Number, Warranty, Contract
   - Financial attributes (cost, depreciation, book value)
   - Lifecycle Status (On Order → Received → Deployed → In Storage → Maintenance → Retired → Disposed)
2. Create JSON Schema
3. Verify: schema validation tests pass

---

#### Task 3.2: PostgreSQL Schema

**Objective:** Create PostgreSQL schema for Asset Repository

**Files:**
- Create: `dcim-core/migrations/asset/001_create_tables.sql`
- Create: `dcim-core/migrations/asset/002_create_indexes.sql`

**Steps:**
1. Create tables:
   - asset (asset_id, serial_number, asset_tag, name, model, manufacturer, owner_dept, location_id, po_number, purchase_date, purchase_cost, warranty_start, warranty_end, contract_id, lifecycle_status, created_at, updated_at)
   - asset_location (location_id, building, floor, room, rack, position_u, latitude, longitude, created_at)
   - asset_financial (asset_id, depreciation_method, useful_life_years, book_value, last_depreciation_date)
   - asset_contract (contract_id, vendor, contract_type, start_date, end_date, sla_terms, renewal_date)
2. Create indexes for performance
3. Verify: `psql -f migrations/asset/001_create_tables.sql`

---

#### Task 3.3: CRUD API

**Objective:** Implement Asset CRUD API

**Files:**
- Create: `dcim-core/api/asset_router.py`
- Create: `dcim-core/api/tests/test_asset_api.py`

**Steps:**
1. Create FastAPI router for assets
2. Implement endpoints:
   - POST /api/v1/assets (create)
   - GET /api/v1/assets (list with pagination)
   - GET /api/v1/assets/{id} (get by ID)
   - PUT /api/v1/assets/{id} (update)
   - DELETE /api/v1/assets/{id} (delete)
3. Add validation and error handling
4. Write tests
5. Verify: `pytest dcim-core/api/tests/test_asset_api.py -v`

---

#### Task 3.4: Bulk Import API

**Objective:** Implement bulk import API for assets (CSV/JSON)

**Files:**
- Create: `dcim-core/api/asset_bulk.py`
- Create: `dcim-core/api/tests/test_asset_bulk.py`

**Steps:**
1. Create bulk import endpoint: POST /api/v1/assets/bulk
2. Support CSV and JSON formats
3. Implement validation and error reporting
4. Add idempotency (upsert on serial_number + manufacturer)
5. Write tests
6. Verify: `pytest dcim-core/api/tests/test_asset_bulk.py -v`

---

#### Task 3.5: Reconciliation Engine

**Objective:** Implement reconciliation engine for CMDB and discovery data

**Files:**
- Create: `dcim-core/services/asset_reconciliation.py`
- Create: `dcim-core/services/tests/test_asset_reconciliation.py`

**Steps:**
1. Create reconciliation engine
2. Implement matching logic:
   - Match with CMDB by serial_number + asset_tag
   - Match with discovery data
3. Conflict resolution: newer data wins
4. Log all changes
5. Write tests
6. Verify: `pytest dcim-core/services/tests/test_asset_reconciliation.py -v`

---

#### Task 3.6: Audit Trails

**Objective:** Implement audit trails for all asset changes

**Files:**
- Create: `dcim-core/services/audit_trail.py`
- Create: `dcim-core/services/tests/test_audit_trail.py`

**Steps:**
1. Create audit trail service
2. Log all create/update/delete operations
3. Store: user, timestamp, old_value, new_value
4. API endpoint: GET /api/v1/assets/{id}/audit-trail
5. Write tests
6. Verify: `pytest dcim-core/services/tests/test_audit_trail.py -v`

---

#### Task 3.7: Enrichment API

**Objective:** Implement read-optimized enrichment API for CMDB and analytics

**Files:**
- Create: `dcim-core/api/asset_enrichment.py`
- Create: `dcim-core/api/tests/test_asset_enrichment.py`

**Steps:**
1. Create enrichment endpoint: GET /api/v1/assets/enrich/{ci_id}
2. Return: asset_id, serial, owner, warranty_status, contract_status, location
3. Implement Redis cache (TTL 15 min)
4. Write tests
5. Verify: `pytest dcim-core/api/tests/test_asset_enrichment.py -v`

---

#### Task 3.8: Asset Repository Testing

**Objective:** Complete testing for Asset Repository

**Files:**
- Create: `dcim-core/api/tests/test_asset_integration.py`

**Steps:**
1. Write integration tests
2. Test all CRUD operations
3. Test bulk import
4. Test reconciliation
5. Test enrichment API
6. Verify: `pytest dcim-core/api/tests/test_asset_integration.py -v`

---

### Block 4: CMDB

**Objective:** Build SSOT for Configuration Items and relationships

**Dependencies:** Block 1 (Infrastructure), Block 3 (Asset Repository)

#### Task 4.1: CMDB Data Model Design

**Objective:** Design CMDB data model with CI types and relationships

**Files:**
- Create: `dcim-core/models/cmdb.py`
- Create: `dcim-core/schemas/cmdb-schema.json`

**Steps:**
1. Design CI data model:
   - CI_ID (CI-{type}-{seq})
   - CI Type (Server, NetworkDevice, Storage, VM, Application, Service, etc.)
   - Mandatory Attributes (name, type, status, owner, location, serial_number)
   - Lifecycle Status (Planned → Active → Maintenance → Retired → Disposed)
2. Design relationship model:
   - Containment (Rack contains Server)
   - Dependency (Service depends on Application)
   - Connectivity (Server connected_to Switch)
   - Impact (Change on Server impacts Service)
3. Create JSON Schema
4. Verify: schema validation tests pass

---

#### Task 4.2: PostgreSQL Schema

**Objective:** Create PostgreSQL schema for CMDB

**Files:**
- Create: `dcim-core/migrations/cmdb/001_create_tables.sql`
- Create: `dcim-core/migrations/cmdb/002_create_indexes.sql`

**Steps:**
1. Create tables:
   - ci (ci_id, ci_type, name, status, owner, location_id, serial_number, created_at, updated_at)
   - ci_attribute (ci_id, attr_name, attr_value, attr_type)
   - ci_relationship (source_ci_id, target_ci_id, relationship_type, metadata)
   - ci_lifecycle (ci_id, status, changed_by, changed_at, reason)
2. Create indexes for performance
3. Verify: `psql -f migrations/cmdb/001_create_tables.sql`

---

#### Task 4.3: CI CRUD API

**Objective:** Implement CI CRUD API

**Files:**
- Create: `dcim-core/api/cmdb_router.py`
- Create: `dcim-core/api/tests/test_cmdb_api.py`

**Steps:**
1. Create FastAPI router for CIs
2. Implement endpoints:
   - POST /api/v1/cmdb/ci (create)
   - GET /api/v1/cmdb/ci (list with pagination)
   - GET /api/v1/cmdb/ci/{id} (get by ID)
   - PUT /api/v1/cmdb/ci/{id} (update)
   - DELETE /api/v1/cmdb/ci/{id} (delete)
   - POST /api/v1/cmdb/ci/bulk (bulk import)
3. Add validation and error handling
4. Write tests
5. Verify: `pytest dcim-core/api/tests/test_cmdb_api.py -v`

---

#### Task 4.4: Relationship Modeling

**Objective:** Implement CI relationship modeling

**Files:**
- Create: `dcim-core/services/relationship.py`
- Create: `dcim-core/services/tests/test_relationship.py`

**Steps:**
1. Create relationship service
2. Implement relationship types:
   - Containment
   - Dependency
   - Connectivity
   - Impact
3. API endpoint: POST /api/v1/cmdb/ci/{id}/relationships
4. Write tests
5. Verify: `pytest dcim-core/services/tests/test_relationship.py -v`

---

#### Task 4.5: Topology Engine

**Objective:** Implement graph-based topology engine for service mapping

**Files:**
- Create: `dcim-core/services/topology.py`
- Create: `dcim-core/services/tests/test_topology.py`

**Steps:**
1. Create topology engine
2. Implement graph traversal
3. Service mapping: end-to-end dependency view
4. API endpoint: GET /api/v1/cmdb/topology/{ci_id}
5. Write tests
6. Verify: `pytest dcim-core/services/tests/test_topology.py -v`

---

#### Task 4.6: Impact Analysis

**Objective:** Implement impact analysis for CI failures

**Files:**
- Create: `dcim-core/services/impact.py`
- Create: `dcim-core/services/tests/test_impact.py`

**Steps:**
1. Create impact analysis service
2. Implement "what breaks if this CI fails?" logic
3. Use topology engine for traversal
4. API endpoint: GET /api/v1/cmdb/impact/{ci_id}
5. Write tests
6. Verify: `pytest dcim-core/services/tests/test_impact.py -v`

---

#### Task 4.7: Asset Reconciliation

**Objective:** Implement reconciliation between CMDB and Asset Repository

**Files:**
- Create: `dcim-core/services/cmdb_asset_reconciliation.py`
- Create: `dcim-core/services/tests/test_cmdb_asset_reconciliation.py`

**Steps:**
1. Create reconciliation engine
2. Match by serial_number + asset_tag
3. Conflict resolution: newer data wins
4. Reconciliation frequency: daily for asset
5. Write tests
6. Verify: `pytest dcim-core/services/tests/test_cmdb_asset_reconciliation.py -v`

---

#### Task 4.8: Discovery Reconciliation

**Objective:** Implement reconciliation between CMDB and discovery data

**Files:**
- Create: `dcim-core/services/discovery_reconciliation.py`
- Create: `dcim-core/services/tests/test_discovery_reconciliation.py`

**Steps:**
1. Create discovery reconciliation engine
2. Match discovered CIs with CMDB entries
3. Conflict resolution: newer data wins
4. Reconciliation frequency: hourly for discovery
5. Write tests
6. Verify: `pytest dcim-core/services/tests/test_discovery_reconciliation.py -v`

---

#### Task 4.9: Service Mapping

**Objective:** Implement service mapping for end-to-end service views

**Files:**
- Create: `dcim-core/services/service_mapping.py`
- Create: `dcim-core/services/tests/test_service_mapping.py`

**Steps:**
1. Create service mapping service
2. Build service dependency graphs
3. Visualize service health
4. API endpoint: GET /api/v1/cmdb/services/{id}/mapping
5. Write tests
6. Verify: `pytest dcim-core/services/tests/test_service_mapping.py -v`

---

#### Task 4.10: Health Dashboard

**Objective:** Implement CMDB health dashboard API

**Files:**
- Create: `dcim-core/api/cmdb_health.py`
- Create: `dcim-core/api/tests/test_cmdb_health.py`

**Steps:**
1. Create health dashboard endpoint: GET /api/v1/cmdb/health
2. Return:
   - Total CIs by type
   - CIs by lifecycle status
   - Reconciliation status
   - Data quality metrics
3. Write tests
4. Verify: `pytest dcim-core/api/tests/test_cmdb_health.py -v`

---

## Phase 2: Intelligence, Automation & Presentation

### Block 5: Web Dashboard

**Objective:** Build presentation layer for NOC, SOC, Facilities, and management views

**Dependencies:** Phase 1 complete

#### Task 5.1: React/Vue Frontend Scaffold

**Objective:** Scaffold frontend application

**Files:**
- Create: `dcim-core/frontend/`
- Create: `dcim-core/frontend/package.json`
- Create: `dcim-core/frontend/src/`

**Steps:**
1. Initialize React/Vue project
2. Set up project structure
3. Configure build tools
4. Verify: `npm run dev` starts successfully

---

#### Task 5.2: API Gateway

**Objective:** Configure API gateway for frontend

**Files:**
- Create: `dcim-core/api/gateway.py`
- Create: `dcim-core/api/tests/test_gateway.py`

**Steps:**
1. Create API gateway
2. Configure routing
3. Implement rate limiting
4. Add request/response transformation
5. Verify: gateway starts and routes correctly

---

#### Task 5.3: RBAC/SSO Integration

**Objective:** Implement RBAC and SSO integration

**Files:**
- Create: `dcim-core/auth/rbac.py`
- Create: `dcim-core/auth/sso.py`
- Create: `dcim-core/auth/tests/test_auth.py`

**Steps:**
1. Implement RBAC (Admin, Operator, Viewer, Auditor)
2. Configure SSO (Keycloak/Auth0)
3. JWT token handling
4. Resource-level permissions
5. Write tests
6. Verify: `pytest dcim-core/auth/tests/test_auth.py -v`

---

#### Task 5.4: NOC View

**Objective:** Implement NOC dashboard view

**Files:**
- Create: `dcim-core/frontend/src/views/NOC.vue`

**Steps:**
1. Create NOC view component
2. Display real-time infrastructure health
3. Show alerts and capacity
4. Implement auto-refresh
5. Verify: view renders correctly

---

#### Task 5.5: SOC View

**Objective:** Implement SOC dashboard view

**Files:**
- Create: `dcim-core/frontend/src/views/SOC.vue`

**Steps:**
1. Create SOC view component
2. Display security events and incidents
3. Show compliance status
4. Implement filtering
5. Verify: view renders correctly

---

#### Task 5.6: Facilities View

**Objective:** Implement Facilities dashboard view

**Files:**
- Create: `dcim-core/frontend/src/views/Facilities.vue`

**Steps:**
1. Create Facilities view component
2. Display power, cooling, environmental monitoring
3. Show real-time metrics
4. Implement alerts
5. Verify: view renders correctly

---

#### Task 5.7: CMDB Explorer

**Objective:** Implement CMDB explorer with interactive topology

**Files:**
- Create: `dcim-core/frontend/src/views/CMDBExplorer.vue`

**Steps:**
1. Create CMDB explorer component
2. Implement interactive topology graph
3. CI search and filter
4. Relationship visualization
5. Impact analysis view
6. Verify: explorer renders correctly

---

#### Task 5.8: SLA/KPI Dashboard

**Objective:** Implement SLA/KPI dashboard

**Files:**
- Create: `dcim-core/frontend/src/views/SLADashboard.vue`

**Steps:**
1. Create SLA/KPI dashboard component
2. Display SLA compliance tracking
3. Show KPI metrics visualization
4. Implement trend analysis
5. Verify: dashboard renders correctly

---

#### Task 5.9: Log Viewer

**Objective:** Implement centralized log viewer

**Files:**
- Create: `dcim-core/frontend/src/views/LogViewer.vue`

**Steps:**
1. Create log viewer component
2. Implement centralized log search
3. Filter by source, severity, time range
4. Correlation with events
5. Export capability
6. Verify: viewer renders correctly

---

#### Task 5.10: Task Board

**Objective:** Implement Kanban-style task board

**Files:**
- Create: `dcim-core/frontend/src/views/TaskBoard.vue`

**Steps:**
1. Create task board component
2. Implement Kanban-style workflow view
3. Assignment and status tracking
4. SLA countdown
5. Priority filtering
6. Verify: board renders correctly

---

#### Task 5.11: Responsive Design

**Objective:** Implement responsive design for all views

**Files:**
- Modify: `dcim-core/frontend/src/views/*.vue`

**Steps:**
1. Add responsive CSS
2. Test on desktop, tablet, mobile
3. Verify: all views responsive

---

### Block 6: SIEM/SOC

**Objective:** Build security event ingestion, correlation, and incident response

**Dependencies:** Block 2 (DI&I), Block 1 (Infrastructure)

#### Task 6.1: Security Event Ingestion

**Objective:** Configure security event ingestion (Wazuh/Syslog → Kafka → ES)

**Files:**
- Create: `dcim-core/siem/ingestion.py`
- Create: `dcim-core/siem/tests/test_ingestion.py`

**Steps:**
1. Create security event ingestion service
2. Configure Wazuh agents
3. Set up Syslog → Kafka pipeline
4. Normalize security event schema
5. Write tests
6. Verify: `pytest dcim-core/siem/tests/test_ingestion.py -v`

---

#### Task 6.2: Correlation Engine

**Objective:** Implement correlation engine for security events

**Files:**
- Create: `dcim-core/siem/correlation.py`
- Create: `dcim-core/siem/tests/test_correlation.py`

**Steps:**
1. Create correlation engine
2. Implement rule-based correlation
3. Threshold alerts (e.g., 5 failed logins in 1 min)
4. Pattern detection
5. Cross-source correlation
6. Write tests
7. Verify: `pytest dcim-core/siem/tests/test_correlation.py -v`

---

#### Task 6.3: Incident Response Workflow

**Objective:** Implement incident response workflow

**Files:**
- Create: `dcim-core/siem/incident_response.py`
- Create: `dcim-core/siem/tests/test_incident_response.py`

**Steps:**
1. Create incident response service
2. Auto-create security incidents
3. Severity classification
4. Integration with workflow-automation
5. Forensics data collection
6. Write tests
7. Verify: `pytest dcim-core/siem/tests/test_incident_response.py -v`

---

#### Task 6.4: CIS Benchmark Compliance

**Objective:** Implement CIS benchmark compliance checks

**Files:**
- Create: `dcim-core/siem/compliance.py`
- Create: `dcim-core/siem/tests/test_compliance.py`

**Steps:**
1. Create compliance service
2. Automated compliance checks
3. Gap analysis
4. Remediation recommendations
5. Compliance reporting
6. Write tests
7. Verify: `pytest dcim-core/siem/tests/test_compliance.py -v`

---

#### Task 6.5: SOC API

**Objective:** Implement SOC API

**Files:**
- Create: `dcim-core/api/soc_router.py`
- Create: `dcim-core/api/tests/test_soc_api.py`

**Steps:**
1. Create SOC API router
2. Endpoints:
   - GET /api/v1/soc/events (query security events)
   - GET /api/v1/soc/incidents (get incident status)
   - PUT /api/v1/soc/incidents/{id} (update incident)
   - GET /api/v1/soc/reports (export reports)
3. Write tests
4. Verify: `pytest dcim-core/api/tests/test_soc_api.py -v`

---

#### Task 6.6: SIEM/SOC Integration Testing

**Objective:** Complete testing for SIEM/SOC integration

**Files:**
- Create: `dcim-core/siem/tests/test_siem_integration.py`

**Steps:**
1. Write integration tests
2. Test event ingestion
3. Test correlation
4. Test incident response
5. Test compliance checks
6. Verify: `pytest dcim-core/siem/tests/test_siem_integration.py -v`

---

### Block 7: Analytics & AI Engine

**Objective:** Build intelligence layer for anomaly detection, predictive maintenance, RCA, and optimization

**Dependencies:** Block 2 (DI&I), Block 4 (CMDB)

#### Task 7.1: Time-Series Pipeline

**Objective:** Configure time-series pipeline (Kafka → TimescaleDB/InfluxDB → Grafana)

**Files:**
- Create: `dcim-core/analytics/timeseries_pipeline.py`
- Create: `dcim-core/analytics/tests/test_timeseries.py`

**Steps:**
1. Create time-series pipeline
2. Configure Kafka → TimescaleDB/InfluxDB
3. Set up retention policies
4. Configure Grafana data source
5. Write tests
6. Verify: `pytest dcim-core/analytics/tests/test_timeseries.py -v`

---

#### Task 7.2: Anomaly Detection

**Objective:** Implement anomaly detection (Isolation Forest, Z-score)

**Files:**
- Create: `dcim-core/analytics/anomaly_detection.py`
- Create: `dcim-core/analytics/tests/test_anomaly.py`

**Steps:**
1. Create anomaly detection service
2. Implement Isolation Forest for multivariate anomaly
3. Implement Z-score for univariate threshold
4. Real-time scoring via Kafka → Flink/Python
5. Alert generation to workflow-automation
6. Write tests
7. Verify: `pytest dcim-core/analytics/tests/test_anomaly.py -v`

---

#### Task 7.3: Predictive Maintenance

**Objective:** Implement predictive maintenance (Prophet, LSTM)

**Files:**
- Create: `dcim-core/analytics/predictive_maintenance.py`
- Create: `dcim-core/analytics/tests/test_predictive.py`

**Steps:**
1. Create predictive maintenance service
2. Time-series forecasting (Prophet, LSTM)
3. Failure probability scoring
4. Maintenance window optimization
5. Integration with CMDB for CI health history
6. Write tests
7. Verify: `pytest dcim-core/analytics/tests/test_predictive.py -v`

---

#### Task 7.4: RCA Engine

**Objective:** Implement Root Cause Analysis engine

**Files:**
- Create: `dcim-core/analytics/rca_engine.py`
- Create: `dcim-core/analytics/tests/test_rca.py`

**Steps:**
1. Create RCA engine
2. Correlation engine: event → metric → topology
3. Graph-based traversal via CMDB topology
4. Timeline reconstruction
5. Suggested remediation
6. Write tests
7. Verify: `pytest dcim-core/analytics/tests/test_rca.py -v`

---

#### Task 7.5: Capacity Forecasting

**Objective:** Implement capacity forecasting

**Files:**
- Create: `dcim-core/analytics/capacity_forecasting.py`
- Create: `dcim-core/analytics/tests/test_capacity.py`

**Steps:**
1. Create capacity forecasting service
2. CPU, memory, storage, network trend analysis
3. Growth projection (linear, exponential)
4. Capacity threshold alerts
5. Planning recommendations
6. Write tests
7. Verify: `pytest dcim-core/analytics/tests/test_capacity.py -v`

---

#### Task 7.6: Energy Optimization

**Objective:** Implement energy optimization

**Files:**
- Create: `dcim-core/analytics/energy_optimization.py`
- Create: `dcim-core/analytics/tests/test_energy.py`

**Steps:**
1. Create energy optimization service
2. PUE (Power Usage Effectiveness) calculation
3. Cooling optimization
4. Power load balancing
5. Carbon footprint tracking
6. Write tests
7. Verify: `pytest dcim-core/analytics/tests/test_energy.py -v`

---

#### Task 7.7: Model Training Pipeline

**Objective:** Implement model training pipeline

**Files:**
- Create: `dcim-core/analytics/model_training.py`
- Create: `dcim-core/analytics/tests/test_model_training.py`

**Steps:**
1. Create model training pipeline
2. Data collection from time-series store
3. Feature engineering
4. Model training (offline)
5. Model registry
6. Deployment to scoring service
7. A/B testing support
8. Write tests
9. Verify: `pytest dcim-core/analytics/tests/test_model_training.py -v`

---

#### Task 7.8: LLM/RAG Explanation Layer

**Objective:** Implement LLM/RAG explanation layer

**Files:**
- Create: `dcim-core/analytics/llm_rag.py`
- Create: `dcim-core/analytics/tests/test_llm_rag.py`

**Steps:**
1. Create LLM/RAG service
2. Natural language explanation of anomalies
3. Query interface for operators
4. RAG: retrieval from CMDB, logs, runbooks
5. Context-aware recommendations
6. Write tests
7. Verify: `pytest dcim-core/analytics/tests/test_llm_rag.py -v`

---

### Block 8: Workflow Automation

**Objective:** Build automation layer for ticketing, approval, runbook, remediation, and escalation

**Dependencies:** Block 2 (DI&I), Block 4 (CMDB)

#### Task 8.1: Workflow State Machine

**Objective:** Implement workflow state machine

**Files:**
- Create: `dcim-core/workflow/state_machine.py`
- Create: `dcim-core/workflow/tests/test_state_machine.py`

**Steps:**
1. Create workflow state machine
2. Define states: pending → in_progress → waiting_approval → approved → executing → completed/failed
3. Custom states per workflow type
4. Timeout handling
5. State persistence
6. Write tests
7. Verify: `pytest dcim-core/workflow/tests/test_state_machine.py -v`

---

#### Task 8.2: ITSM Ticketing Integration

**Objective:** Implement ITSM ticketing integration (ServiceNow/Jira)

**Files:**
- Create: `dcim-core/workflow/itsm_integration.py`
- Create: `dcim-core/workflow/tests/test_itsm.py`

**Steps:**
1. Create ITSM integration service
2. Auto-create tickets from alerts
3. Bi-directional sync with ServiceNow/Jira
4. Ticket lifecycle management
5. SLA tracking
6. Write tests
7. Verify: `pytest dcim-core/workflow/tests/test_itsm.py -v`

---

#### Task 8.3: Multi-Level Approval Workflows

**Objective:** Implement multi-level approval workflows

**Files:**
- Create: `dcim-core/workflow/approval.py`
- Create: `dcim-core/workflow/tests/test_approval.py`

**Steps:**
1. Create approval workflow service
2. Configurable approval chains
3. Role-based approvers
4. Timeout escalation
5. Batch approval support
6. Write tests
7. Verify: `pytest dcim-core/workflow/tests/test_approval.py -v`

---

#### Task 8.4: Runbook Engine

**Objective:** Implement runbook engine

**Files:**
- Create: `dcim-core/workflow/runbook_engine.py`
- Create: `dcim-core/workflow/tests/test_runbook.py`

**Steps:**
1. Create runbook engine
2. Execute predefined procedures
3. Conditional logic
4. Manual step support
5. Audit trail
6. Write tests
7. Verify: `pytest dcim-core/workflow/tests/test_runbook.py -v`

---

#### Task 8.5: Auto-Remediation

**Objective:** Implement auto-remediation with safety guards

**Files:**
- Create: `dcim-core/workflow/auto_remediation.py`
- Create: `dcim-core/workflow/tests/test_remediation.py`

**Steps:**
1. Create auto-remediation service
2. Triggered by anomaly/alert thresholds
3. Safety guards: blast radius check, approval for critical actions
4. Rollback capability
5. Integration with CMDB for impact assessment
6. Write tests
7. Verify: `pytest dcim-core/workflow/tests/test_remediation.py -v`

---

#### Task 8.6: Escalation Rules

**Objective:** Implement escalation rules

**Files:**
- Create: `dcim-core/workflow/escalation.py`
- Create: `dcim-core/workflow/tests/test_escalation.py`

**Steps:**
1. Create escalation service
2. Time-based escalation
3. Severity-based routing
4. On-call schedule integration
5. Notification channels: email, SMS, Slack, Teams
6. Write tests
7. Verify: `pytest dcim-core/workflow/tests/test_escalation.py -v`

---

#### Task 8.7: n8n/Temporal Integration

**Objective:** Integrate with n8n/Temporal for workflow orchestration

**Files:**
- Create: `dcim-core/workflow/orchestration.py`
- Create: `dcim-core/workflow/tests/test_orchestration.py`

**Steps:**
1. Create orchestration service
2. Integrate with n8n/Temporal
3. REST API for custom integrations
4. Webhook support
5. Event-driven triggers from DI&I
6. Write tests
7. Verify: `pytest dcim-core/workflow/tests/test_orchestration.py -v`

---

### Block 9: External Integration

**Objective:** Build adapter pattern framework for external system integration

**Dependencies:** Block 2 (DI&I), Block 4 (CMDB), Block 3 (Asset Repository)

#### Task 9.1: Adapter Framework

**Objective:** Create base adapter pattern framework

**Files:**
- Create: `dcim-core/integrations/base_adapter.py`
- Create: `dcim-core/integrations/normalizer.py`

**Steps:**
1. Create base adapter class
2. Define adapter interface
3. Create normalizer for data format unification
4. Implement error handling (DLQ + retry)
5. Add health monitoring
6. Verify: adapter framework compiles

---

#### Task 9.2: ServiceNow Connector

**Objective:** Implement ServiceNow connector

**Files:**
- Create: `dcim-core/integrations/servicenow.py`
- Create: `dcim-core/integrations/tests/test_servicenow.py`

**Steps:**
1. Create ServiceNow adapter
2. Implement ticket creation, status sync, SLA tracking
3. Bi-directional sync
4. Webhook + REST API
5. Write tests
6. Verify: `pytest dcim-core/integrations/tests/test_servicenow.py -v`

---

#### Task 9.3: Jira Connector

**Objective:** Implement Jira connector

**Files:**
- Create: `dcim-core/integrations/jira.py`
- Create: `dcim-core/integrations/tests/test_jira.py`

**Steps:**
1. Create Jira adapter
2. Implement issue tracking, sprint integration
3. Bi-directional sync
4. Webhook + REST API
5. Write tests
6. Verify: `pytest dcim-core/integrations/tests/test_jira.py -v`

---

#### Task 9.4: SAP Connector

**Objective:** Implement SAP connector

**Files:**
- Create: `dcim-core/integrations/sap.py`
- Create: `dcim-core/integrations/tests/test_sap.py`

**Steps:**
1. Create SAP adapter
2. Implement asset master data, financial data sync
3. Batch sync + event-driven
4. Write tests
5. Verify: `pytest dcim-core/integrations/tests/test_sap.py -v`

---

#### Task 9.5: Oracle Connector

**Objective:** Implement Oracle connector

**Files:**
- Create: `dcim-core/integrations/oracle.py`
- Create: `dcim-core/integrations/tests/test_oracle.py`

**Steps:**
1. Create Oracle adapter
2. Implement procurement, inventory sync
3. Batch sync + event-driven
4. Write tests
5. Verify: `pytest dcim-core/integrations/tests/test_oracle.py -v`

---

#### Task 9.6: DMS Connector

**Objective:** Implement DMS connector

**Files:**
- Create: `dcim-core/integrations/dms.py`
- Create: `dcim-core/integrations/tests/test_dms.py`

**Steps:**
1. Create DMS adapter
2. Document linking for CIs and assets
3. SOP/manual attachment
4. Version control
5. Write tests
6. Verify: `pytest dcim-core/integrations/tests/test_dms.py -v`

---

#### Task 9.7: NMS Connector

**Objective:** Implement NMS connector

**Files:**
- Create: `dcim-core/integrations/nms.py`
- Create: `dcim-core/integrations/tests/test_nms.py`

**Steps:**
1. Create NMS adapter
2. Network device discovery
3. Topology import
4. Performance metrics
5. Write tests
6. Verify: `pytest dcim-core/integrations/tests/test_nms.py -v`

---

#### Task 9.8: AWS Connector

**Objective:** Implement AWS connector

**Files:**
- Create: `dcim-core/integrations/aws.py`
- Create: `dcim-core/integrations/tests/test_aws.py`

**Steps:**
1. Create AWS adapter
2. Implement EC2, RDS, S3, CloudWatch integration
3. Resource discovery and sync
4. Write tests
5. Verify: `pytest dcim-core/integrations/tests/test_aws.py -v`

---

#### Task 9.9: GCP Connector

**Objective:** Implement GCP connector

**Files:**
- Create: `dcim-core/integrations/gcp.py`
- Create: `dcim-core/integrations/tests/test_gcp.py`

**Steps:**
1. Create GCP adapter
2. Implement Compute Engine, Cloud SQL, Monitoring integration
3. Resource discovery and sync
4. Write tests
5. Verify: `pytest dcim-core/integrations/tests/test_gcp.py -v`

---

#### Task 9.10: Azure Connector

**Objective:** Implement Azure connector

**Files:**
- Create: `dcim-core/integrations/azure.py`
- Create: `dcim-core/integrations/tests/test_azure.py`

**Steps:**
1. Create Azure adapter
2. Implement VMs, SQL, Monitor integration
3. Resource discovery and sync
4. Write tests
5. Verify: `pytest dcim-core/integrations/tests/test_azure.py -v`

---

#### Task 9.11: Integration Health Monitoring

**Objective:** Implement health monitoring for all integrations

**Files:**
- Create: `dcim-core/integrations/health_monitor.py`
- Create: `dcim-core/integrations/tests/test_health.py`

**Steps:**
1. Create health monitoring service
2. Monitor connectivity and sync status
3. Alert on integration failures
4. Dashboard for integration health
5. Write tests
6. Verify: `pytest dcim-core/integrations/tests/test_health.py -v`

---

## Cross-Cutting Concerns

### Security

**Objective:** Implement security across all components

**Tasks:**
- [ ] RBAC implemented
- [ ] TLS 1.2+ configured
- [ ] Vault integration completed
- [ ] Audit trail implemented
- [ ] Security testing completed

### Monitoring

**Objective:** Configure monitoring and alerting

**Tasks:**
- [ ] Prometheus metrics configured
- [ ] Grafana dashboards created
- [ ] Alerting rules configured
- [ ] Log aggregation configured

### Testing

**Objective:** Complete testing coverage

**Tasks:**
- [ ] Unit tests implemented
- [ ] Integration tests implemented
- [ ] E2E tests implemented
- [ ] Performance tests completed
- [ ] Security tests completed

### Documentation

**Objective:** Complete documentation

**Tasks:**
- [ ] Architecture documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] SOPs documented
- [ ] Runbooks documented
- [ ] Training materials created

---

## Execution Strategy

### Parallelization

**Option A: Single Team (27.5 days)**
- Sequential execution through all blocks

**Option B: Two Parallel Teams (15-18 days)**
- Team 1: Block 1 → Block 2 → Block 4 → Block 7
- Team 2: Block 1 → Block 3 → Block 5 → Block 6

### Quality Gates

After each block:
1. Code review
2. Unit tests pass
3. Integration tests pass
4. Documentation updated
5. Deployment verified

### Rollback Strategy

- Git version control for all changes
- Database migrations with rollback scripts
- Docker/K8s rollback capability
- Backup before major changes

---

## Open Questions

- Timeline kickoff belum ditentukan
- Environment production vs staging belum didefinisikan
- Tim development belum diidentifikasi
- Pilihan deployment: Docker Compose vs Kubernetes

---

## Next Step

1. **Tentukan kickoff date** dan environment strategy
2. **Identifikasi tim** (2 parallel teams untuk optimal timeline)
3. **Mulai Block 1** — Infrastructure Provisioning sebagai foundation
4. **Setup CI/CD pipeline** untuk automated testing dan deployment

---

*Plan saved: ~/.hermes/plans/2026-06-23_dcim-core-platform-implementation.md*
*Source: DCIM Wiki (~/dcim-wiki/) — 147 pages, 19 entities, 79 concepts, 33 comparisons, 16 queries*
