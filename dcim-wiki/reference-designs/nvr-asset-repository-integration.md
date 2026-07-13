---
title: "NVR → Asset Repository Integration: Reference Design Spec"
created: 2026-06-25
updated: 2026-06-25
type: reference-design
phase: 1
status: generated
confidence: high
tags: [nvr, surveillance, onvif, snmp, asset-repository, camera, location-validation, multi-vendor]
wiki_pages:
  - nvr-integration
  - asset-repository
  - data-ingestion-integration
  - infrastructure-provisioning
  - network-architecture
purpose: >
  Reference design spec untuk integrasi NVR (Network Video Recorder) ke DCIM Asset Repository.
  Fokus: metadata NVR & kamera sebagai aset, validasi lokasi via kamera, health monitoring.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# NVR → Asset Repository Integration: Reference Design Spec

> **Purpose:** Dokumen referensi integrasi NVR sebagai data source untuk Asset Repository — device discovery, camera mapping, location validation, health monitoring.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi aktual. Setiap gap dicatat sebagai connection point.
> **Architecture Diagram:** `diagrams/nvr-asset-repository-integration.html` — buka di browser.
> **Depends on:** Block 1 (Infrastructure), Block 2 (DI&I), Block 3 (Asset Repository)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [NVR Data Model](#2-nvr-data-model)
3. [PostgreSQL Schema](#3-postgresql-schema)
4. [Protocol Integration](#4-protocol-integration)
5. [NiFi Flow Designs](#5-nifi-flow-designs)
6. [Kafka Topics](#6-kafka-topics)
7. [Asset Repository API Extensions](#7-asset-repository-api-extensions)
8. [Location Validation Engine](#8-location-validation-engine)
9. [Data Quality Framework](#9-data-quality-framework)
10. [Security](#10-security)
11. [Monitoring & Alerting](#11-monitoring--alerting)
12. [Acceptance Criteria](#12-acceptance-criteria)
13. [Gap Comparison Template](#13-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    NVR Integration Layer                                 │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│  │  NVR Head   │  │  NVR Head   │  │  NVR Head   │  ← ONVIF/SNMP     │
│  │  Unit 1     │  │  Unit 2     │  │  Unit N     │                    │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │                    │
│  │ │Camera 1 │ │  │ │Camera 1 │ │  │ │Camera 1 │ │                    │
│  │ │Camera 2 │ │  │ │Camera 2 │ │  │ │Camera 2 │ │                    │
│  │ │  ...    │ │  │ │  ...    │ │  │ │  ...    │ │                    │
│  │ │Camera N │ │  │ │Camera N │ │  │ │Camera N │ │                    │
│  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │                    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                    │
│         │                │                │                             │
│  ┌──────┴────────────────┴────────────────┴──────┐                    │
│  │           NiFi NVR Connector Layer             │                    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐       │                    │
│  │  │ ONVIF    │ │ SNMP     │ │ Syslog   │       │                    │
│  │  │Discovery │ │ Poller   │ │ Receiver │       │                    │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘       │                    │
│  └───────┼─────────────┼───────────┼──────────────┘                    │
│          │             │           │                                    │
│  ┌───────┴─────────────┴───────────┴──────────────┐                   │
│  │              Kafka Topics                       │                   │
│  │  dcim.nvr.discovery │ dcim.nvr.health │ nvr.events                 │
│  └──────────────────────┬──────────────────────────┘                   │
│                         │                                               │
│  ┌──────────────────────┴──────────────────────────┐                   │
│  │         NVR Asset Sync Consumer                   │                   │
│  │  Match → Upsert → Validate Location → Audit      │                   │
│  └──────────────────────┬──────────────────────────┘                   │
│                         │                                               │
│  ┌──────────────────────┴──────────────────────────┐                   │
│  │              PostgreSQL (Asset DB)                │                   │
│  │  asset │ asset_nvr │ asset_camera │ asset_location│                  │
│  └──────────────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow Summary

```
NVR Device → [ONVIF/SNMP/Syslog] → NiFi Connector → Kafka (nvr.*) → Consumer → PostgreSQL (Asset DB)
       │                                                                      ↑
       │ ONVIF                                                              Reconcile
       ▼                                                                      │
  IP Cameras ←── location validate ────────────────────────→ asset_location
```

### 1.3 Integration Scope

| Component | Scope | Priority |
|-----------|-------|----------|
| NVR Device Discovery | ONVIF WS-Discovery, auto-register as asset | P1 |
| NVR Health Monitoring | SNMP polling, storage capacity, recording status | P1 |
| Camera Registry | Camera-to-NVR mapping, channel assignment | P1 |
| Location Validation | Camera positions validate asset_location | P1 |
| Event Streaming | Camera offline, disk full, tamper alerts | P2 |
| Vendor Extensions | Hikvision ISAPI, Axis VAPIX, Dahua HTTP | P3 |

### 1.4 Multi-Vendor Strategy

**Layer 1: ONVIF Standard (Universal)**
- Device discovery (WS-Discovery)
- Device info (serial, model, firmware, IP)
- Stream URL (RTSP)
- Basic network config

**Layer 2: Vendor Extension (Optional)**
- Hikvision: ISAPI REST API
- Dahua: HTTP API
- Axis: VAPIX API
- Frigate: REST API (open-source)
- Generic ONVIF: Fallback

| Vendor | Adapter | Storage API | Analytics | Priority |
|--------|---------|-------------|-----------|----------|
| Hikvision | ISAPI | ✅ | ✅ | P1 |
| Dahua | HTTP | ✅ | ⚠️ Limited | P1 |
| Axis | VAPIX | ✅ | ✅ | P2 |
| Frigate | REST | ✅ | ✅ | P3 |
| Generic ONVIF | ONVIF only | ⚠️ Limited | ❌ | P4 |

---

## 2. NVR Data Model

### 2.1 Entity Relationship Diagram

```
┌──────────────────┐       ┌──────────────────┐
│      asset       │       │    asset_nvr     │
│──────────────────│       │──────────────────│
│ asset_id (PK)    │──1:1──│ asset_id (PK,FK) │
│ serial_number    │       │ storage_capacity │
│ asset_tag        │       │ storage_used     │
│ name             │       │ retention_days   │
│ model            │       │ firmware_version │
│ manufacturer     │       │ channel_count    │
│ connector_type   │←NEW   │ onvif_profile    │
│ owner_dept       │       │ management_ip    │
│ location_id (FK) │       │ last_sync_at     │
│ lifecycle_status │       │ sync_status      │
└──────────────────┘       └──────────────────┘
        │                          │
        │                          │ 1:N
        │                          ▼
        │                   ┌──────────────────┐
        │                   │  asset_camera    │
        │                   │──────────────────│
        │                   │ asset_id (PK,FK) │
        │                   │ nvr_asset_id(FK) │
        │                   │ channel_number   │
        │                   │ resolution       │
        │                   │ lens_type        │
        │                   │ night_vision     │
        │                   │ stream_url       │
        │                   │ motion_detection │
        │                   │ location_verified│
        │                   │ status           │
        │                   └──────────────────┘
        │                          │
        │                          │ N:M
        │                          ▼
        │                   ┌──────────────────┐
        └──────FK──────────→│  asset_location  │
                            │──────────────────│
                            │ location_id (PK) │
                            │ camera_verified  │←NEW
                            │ camera_verified_at│←NEW
                            │ building         │
                            │ room             │
                            │ rack             │
                            └──────────────────┘
```

### 2.2 Asset Lifecycle for NVR Devices

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ On Order │───→│ Received │───→│ Deployed │───→│  Online   │
└─────────┘    └──────────┘    └──────────┘    └─────┬─────┘
                                                      │
                                    ┌─────────────────┼─────────────────┐
                                    ▼                 ▼                 ▼
                              ┌──────────┐    ┌──────────┐    ┌──────────┐
                              │ Firmware │    │ Degraded │    │ Offline  │
                              │ Update   │    │(disk warn)│   │ (alert)  │
                              └────┬─────┘    └────┬─────┘    └────┬─────┘
                                   │               │               │
                                   └───────────────┼───────────────┘
                                                   ▼
                                             ┌──────────┐
                                             │ Retired  │
                                             └──────────┘
```

### 2.3 Field Specifications

#### NVR-Specific Fields (asset_nvr)

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `asset_id` | UUID | Yes | FK → asset | NVR device asset |
| `storage_capacity_gb` | INTEGER | Yes | > 0 | Total disk capacity |
| `storage_used_gb` | INTEGER | Yes | ≥ 0, ≤ capacity | Current usage |
| `recording_retention_days` | INTEGER | Yes | > 0, ≤ 365 | Days of retention |
| `firmware_version` | VARCHAR(50) | No | — | Current firmware |
| `channel_count` | INTEGER | Yes | > 0, ≤ 256 | Max camera channels |
| `onvif_profile` | VARCHAR(20) | Yes | S, T, G | ONVIF profile |
| `management_ip` | INET | Yes | Unique | Management interface |
| `rtsp_port` | INTEGER | No | Default 554 | RTSP streaming port |
| `http_port` | INTEGER | No | Default 80 | HTTP/HTTPS port |
| `last_sync_at` | TIMESTAMPTZ | Auto | — | Last ONVIF sync |
| `sync_status` | VARCHAR(20) | Yes | synced/pending/error/offline | Sync state |

#### Camera-Specific Fields (asset_camera)

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `asset_id` | UUID | Yes | FK → asset | Camera device asset |
| `nvr_asset_id` | UUID | Yes | FK → asset_nvr | Parent NVR |
| `channel_number` | INTEGER | Yes | > 0, ≤ channel_count | NVR channel |
| `resolution` | VARCHAR(20) | No | e.g. 1920x1080 | Video resolution |
| `lens_type` | VARCHAR(30) | No | fixed/varifocal/dome/bullet | Lens type |
| `night_vision` | BOOLEAN | No | Default false | IR/night capability |
| `onvif_profile` | VARCHAR(20) | Yes | S, T | Camera ONVIF profile |
| `stream_url` | VARCHAR(500) | No | RTSP format | Primary stream URL |
| `motion_detection` | BOOLEAN | No | Default true | Motion detection enabled |
| `tamper_detection` | BOOLEAN | No | Default false | Tamper detection enabled |
| `location_verified` | BOOLEAN | Auto | Default false | Verified by camera view |
| `last_online_at` | TIMESTAMPTZ | Auto | — | Last seen online |
| `status` | VARCHAR(20) | Yes | online/offline/maintenance/unknown | Current status |

---

## 3. PostgreSQL Schema

### 3.1 Tables

```sql
-- Migration 010: NVR Integration Tables

-- ============================================
-- Extend asset table with connector_type
-- ============================================
ALTER TABLE asset ADD COLUMN connector_type VARCHAR(30) DEFAULT 'manual'
    CHECK (connector_type IN ('manual', 'api', 'discovery', 'nvr', 'snmp', 'ssh'));

-- ============================================
-- asset_nvr
-- ============================================
CREATE TABLE asset_nvr (
    asset_id UUID PRIMARY KEY REFERENCES asset(asset_id) ON DELETE CASCADE,
    storage_capacity_gb INTEGER NOT NULL CHECK (storage_capacity_gb > 0),
    storage_used_gb INTEGER DEFAULT 0 CHECK (storage_used_gb >= 0),
    recording_retention_days INTEGER DEFAULT 30 CHECK (recording_retention_days > 0 AND recording_retention_days <= 365),
    firmware_version VARCHAR(50),
    channel_count INTEGER NOT NULL CHECK (channel_count > 0 AND channel_count <= 256),
    onvif_profile VARCHAR(20) NOT NULL DEFAULT 'S'
        CHECK (onvif_profile IN ('S', 'T', 'G')),
    management_ip INET NOT NULL UNIQUE,
    rtsp_port INTEGER DEFAULT 554,
    http_port INTEGER DEFAULT 80,
    last_sync_at TIMESTAMPTZ,
    sync_status VARCHAR(20) DEFAULT 'pending'
        CHECK (sync_status IN ('synced', 'pending', 'error', 'offline')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_nvr_storage CHECK (storage_used_gb <= storage_capacity_gb)
);

-- ============================================
-- asset_camera
-- ============================================
CREATE TABLE asset_camera (
    asset_id UUID PRIMARY KEY REFERENCES asset(asset_id) ON DELETE CASCADE,
    nvr_asset_id UUID NOT NULL REFERENCES asset_nvr(asset_id) ON DELETE CASCADE,
    channel_number INTEGER NOT NULL,
    resolution VARCHAR(20),
    lens_type VARCHAR(30)
        CHECK (lens_type IN ('fixed', 'varifocal', 'dome', 'bullet', 'ptz', 'panoramic')),
    night_vision BOOLEAN DEFAULT false,
    onvif_profile VARCHAR(20) NOT NULL DEFAULT 'S'
        CHECK (onvif_profile IN ('S', 'T')),
    stream_url VARCHAR(500),
    motion_detection BOOLEAN DEFAULT true,
    tamper_detection BOOLEAN DEFAULT false,
    location_verified BOOLEAN DEFAULT false,
    last_online_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'unknown'
        CHECK (status IN ('online', 'offline', 'maintenance', 'unknown')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_nvr_channel UNIQUE (nvr_asset_id, channel_number)
);

-- ============================================
-- Extend asset_location with camera verification
-- ============================================
ALTER TABLE asset_location ADD COLUMN camera_verified BOOLEAN DEFAULT false;
ALTER TABLE asset_location ADD COLUMN camera_verified_at TIMESTAMPTZ;

-- ============================================
-- camera_location_map (multi-camera per location)
-- ============================================
CREATE TABLE camera_location_map (
    camera_asset_id UUID REFERENCES asset_camera(asset_id) ON DELETE CASCADE,
    location_id UUID REFERENCES asset_location(location_id) ON DELETE CASCADE,
    coverage_type VARCHAR(20) DEFAULT 'full'
        CHECK (coverage_type IN ('full', 'partial', 'entrance', 'rack')),
    verified_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (camera_asset_id, location_id)
);
```

### 3.2 Indexes

```sql
-- Migration 011: NVR Indexes

-- NVR searches
CREATE INDEX idx_nvr_management_ip ON asset_nvr(management_ip);
CREATE INDEX idx_nvr_sync_status ON asset_nvr(sync_status);
CREATE INDEX idx_nvr_storage_used ON asset_nvr(storage_used_gb);

-- Camera searches
CREATE INDEX idx_camera_nvr ON asset_camera(nvr_asset_id);
CREATE INDEX idx_camera_status ON asset_camera(status);
CREATE INDEX idx_camera_location_verified ON asset_camera(location_verified);

-- Composite indexes
CREATE INDEX idx_camera_nvr_channel ON asset_camera(nvr_asset_id, channel_number);
CREATE INDEX idx_camera_nvr_status ON asset_camera(nvr_asset_id, status);

-- Location verification
CREATE INDEX idx_location_camera_verified ON asset_location(camera_verified);
CREATE INDEX idx_location_camera_verified_at ON asset_location(camera_verified_at);

-- Camera-location mapping
CREATE INDEX idx_camloc_location ON camera_location_map(location_id);
```

### 3.3 Triggers

```sql
-- Auto-update updated_at for NVR tables
CREATE TRIGGER trg_nvr_updated
    BEFORE UPDATE ON asset_nvr
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_camera_updated
    BEFORE UPDATE ON asset_camera
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Auto-update storage_used_gb from asset_camera count
CREATE OR REPLACE FUNCTION update_nvr_storage_used()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE asset_nvr
    SET storage_used_gb = (
        SELECT COALESCE(SUM(
            CASE WHEN NEW.status = 'online' THEN 1 ELSE 0 END
        ), 0) * 10  -- rough estimate: 10GB per active camera
        FROM asset_camera
        WHERE nvr_asset_id = NEW.nvr_asset_id
    )
    WHERE asset_id = NEW.nvr_asset_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. Protocol Integration

### 4.1 ONVIF Protocol

| Operation | ONVIF Method | Use Case | Frequency |
|-----------|-------------|----------|-----------|
| Discovery | WS-Discovery | Find NVR on network | Daily |
| Device Info | GetDeviceInformation | Register/update asset | On discovery |
| Network Config | GetNetworkInterfaces | IP, MAC, DNS | On discovery |
| Media Profiles | GetProfiles | Camera channels | On discovery |
| Stream URL | GetStreamUri | RTSP endpoints | On discovery |
| PTZ Capabilities | GetCapabilities | Camera features | On discovery |

**ONVIF Discovery Flow:**
```
1. Send WS-Discovery ProbeMulticast to 239.255.255.250:3702
2. Receive ProbeMatches from NVR devices
3. For each device:
   a. GetDeviceInformation → serial, model, firmware, manufacturer
   b. GetNetworkInterfaces → IP, MAC
   c. GetCapabilities → supported services
   d. GetProfiles → camera channels
   e. GetStreamUri → RTSP URLs
4. Normalize to DCIM event schema
5. Publish to Kafka (dcim.nvr.discovery)
```

### 4.2 SNMP Protocol

| OID | Metric | Type | Unit |
|-----|--------|------|------|
| 1.3.6.1.4.1.30495.1.2.1.1 | NVR Name | String | — |
| 1.3.6.1.4.1.30495.1.2.1.2 | NVR Status | Integer | 1=ok, 2=fail |
| 1.3.6.1.4.1.30495.1.2.1.3 | CPU Usage | Integer | % |
| 1.3.6.1.4.1.30495.1.2.1.4 | Memory Usage | Integer | % |
| 1.3.6.1.4.1.30495.1.2.1.5 | Disk Status | Integer | 1=ok, 2=degraded, 3=fail |
| 1.3.6.1.4.1.30495.1.2.1.6 | Recording Status | Integer | 1=active, 2=inactive |
| 1.3.6.1.4.1.30495.1.2.1.7 | Camera Online Count | Integer | Count |
| 1.3.6.1.4.1.30495.1.2.1.8 | Camera Offline Count | Integer | Count |

**Note:** OID base `1.3.6.1.4.1.30495` is vendor-specific (Hikvision example). Use vendor MIB or generic HOST-RESOURCES-MIB for cross-vendor.

### 4.3 Syslog

| Facility | Severity | Event | Action |
|----------|----------|-------|--------|
| local0 | notice | Camera online | Update status |
| local0 | warning | Camera offline | Create event |
| local0 | error | Disk failure | Create event + alert |
| local0 | critical | NVR failure | Create event + alert |
| local0 | info | Motion detected | Optional: create event |

**Syslog Format (CEF):**
```
CEF:0|Vendor|NVR|1.0|1001|CameraOffline|1|src=10.70.2.100 dst=10.70.2.1 dhost=Camera-RackA1-01
```

### 4.4 Vendor Extensions (Optional)

**Hikvision ISAPI:**
```
GET /ISAPI/ContentMgmt/record/tracks
GET /ISAPI/ContentMgmt/deviceInfo
GET /ISAPI/System/deviceInfo
```

**Axis VAPIX:**
```
GET /axis-cgi/param.cgi?action=list&group=Properties.System
GET /axis-cgi/recorddisk.cgi?action=list
```

---

## 5. NiFi Flow Designs

### 5.1 NVR ONVIF Discovery Flow

| Processor | Class | Config |
|-----------|-------|--------|
| **TimerDrivenExecute** | `o.a.n.p.standard.ExecuteProcess` | Command: `python3 onvif_discover.py`, Period: 24h |
| **JoltTransformJSON** | `o.a.n.p.standard.JoltTransformJSON` | Spec: `nvr-normalize.jolt` |
| **ValidateRecord** | `o.a.n.p.standard.ValidateRecord` | Schema: `nvr-event-schema.avsc` |
| **PublishKafka_2_0** | `o.a.n.p.kafka.PublishKafka_2_0` | Topic: `dcim.nvr.discovery`, Key: `${management_ip}` |

### 5.2 NVR SNMP Health Flow

| Processor | Class | Config |
|-----------|-------|--------|
| **TimerDrivenExecute** | `o.a.n.p.standard.ExecuteProcess` | Command: `python3 nvr_snmp_poll.py`, Period: 5min |
| **SplitRecord** | `o.a.n.p.standard.SplitRecord` | Reader: JSON, Writer: JSON |
| **JoltTransformJSON** | `o.a.n.p.standard.JoltTransformJSON` | Spec: `nvr-health-normalize.jolt` |
| **PublishKafka_2_0** | `o.a.n.p.kafka.PublishKafka_2_0` | Topic: `dcim.nvr.health`, Key: `${nvr_id}` |

### 5.3 NVR Syslog Event Flow

| Processor | Class | Config |
|-----------|-------|--------|
| **ListenSyslog** | `o.a.n.p.sys ListenSyslog` | Port: 5140, Protocol: UDP |
| **ParseCEF** | Custom processor or `JoltTransformJSON` | CEF parser spec |
| **EnrichWithAsset** | `o.a.n.p.lookup.LookupRecord` | Asset lookup from PostgreSQL |
| **PublishKafka_2_0** | `o.a.n.p.kafka.PublishKafka_2_0` | Topic: `dcim.nvr.events`, Key: `${nvr_id}` |

### 5.4 NVR Asset Sync Consumer Flow

| Processor | Class | Config |
|-----------|-------|--------|
| **ConsumeKafka_2_0** | `o.a.n.p.kafka.ConsumeKafka_2_0` | Topic: `dcim.nvr.discovery`, Group: `nvr-asset-sync` |
| **JoltTransformJSON** | `o.a.n.p.standard.JoltTransformJSON` | Transform to asset schema |
| **UpdateAttribute** | `o.a.n.p.standard.UpdateAttribute` | Set `asset_type=nvr` |
| **InvokeHTTP** | `o.a.n.p.standard.InvokeHTTP` | URL: `${asset.api.url}/api/v1/assets/nvr`, Method: PUT |
| **LogAttribute** | `o.a.n.p.standard.LogAttribute` | Log success/failure |

---

## 6. Kafka Topics

| Topic | Partitions | RF | Retention | Purpose |
|-------|-----------|-----|-----------|---------|
| `dcim.nvr.discovery` | 3 | 3 | 7 days | ONVIF probe results |
| `dcim.nvr.health` | 6 | 3 | 3 days | SNMP polling metrics |
| `dcim.nvr.events` | 6 | 3 | 30 days | Syslog events |
| `dcim.nvr.cameras` | 3 | 3 | 7 days | Camera registry sync |
| `dcim.nvr.location` | 3 | 3 | 30 days | Location validation events |

### 6.1 Event Schema (NVR Discovery)

```json
{
  "event_id": "uuid",
  "timestamp": "2026-06-25T10:00:00Z",
  "source_system": "nvr",
  "event_type": "security.nvr.discovery",
  "payload": {
    "nvr": {
      "serial_number": "DS-7600NI-K4/8P",
      "model": "DS-7600NI-K4/8P",
      "manufacturer": "Hikvision",
      "firmware_version": "V4.62.000",
      "management_ip": "10.70.2.10",
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "channel_count": 8,
      "onvif_profile": "S",
      "storage_capacity_gb": 4000,
      "storage_used_gb": 1200,
      "recording_retention_days": 30
    },
    "cameras": [
      {
        "channel_number": 1,
        "serial_number": "DS-2CD2143G2-I",
        "model": "DS-2CD2143G2-I",
        "manufacturer": "Hikvision",
        "resolution": "2688x1520",
        "lens_type": "dome",
        "night_vision": true,
        "onvif_profile": "S",
        "stream_url": "rtsp://10.70.2.10:554/Streaming/Channels/101",
        "motion_detection": true
      }
    ]
  },
  "metadata": {
    "priority": "P3",
    "category": "security",
    "tags": ["nvr", "discovery", "hikvision"],
    "schema_version": "1.0.0"
  }
}
```

---

## 7. Asset Repository API Extensions

### 7.1 New Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/assets/nvr` | asset.write | Register NVR device |
| GET | `/api/v1/assets/nvr` | asset.read | List NVR devices |
| GET | `/api/v1/assets/nvr/{id}` | asset.read | Get NVR with cameras |
| PUT | `/api/v1/assets/nvr/{id}/sync` | asset.write | Trigger ONVIF sync |
| GET | `/api/v1/assets/nvr/{id}/cameras` | asset.read | List cameras on NVR |
| POST | `/api/v1/assets/nvr/{id}/cameras` | asset.write | Register camera |
| GET | `/api/v1/assets/cameras` | asset.read | List all cameras |
| GET | `/api/v1/assets/cameras/{id}` | asset.read | Get camera details |
| GET | `/api/v1/assets/location/{id}/cameras` | asset.read | Cameras covering location |
| POST | `/api/v1/assets/location/{id}/verify` | asset.write | Trigger location verification |

### 7.2 Request/Response Examples

#### Register NVR

```json
// POST /api/v1/assets/nvr
{
  "asset_tag": "NVR-RACK-A1-001",
  "serial_number": "DS-7600NI-K4/8P",
  "name": "Hikvision NVR - Rack A1",
  "model": "DS-7600NI-K4/8P",
  "manufacturer": "Hikvision",
  "owner_dept": "Security",
  "location_id": "uuid-of-location",
  "connector_type": "nvr",
  "nvr": {
    "storage_capacity_gb": 4000,
    "recording_retention_days": 30,
    "channel_count": 8,
    "onvif_profile": "S",
    "management_ip": "10.70.2.10"
  }
}
```

#### Response

```json
{
  "asset_id": "uuid-of-nvr-asset",
  "asset_tag": "NVR-RACK-A1-001",
  "name": "Hikvision NVR - Rack A1",
  "connector_type": "nvr",
  "lifecycle_status": "deployed",
  "nvr": {
    "storage_capacity_gb": 4000,
    "storage_used_gb": 0,
    "recording_retention_days": 30,
    "channel_count": 8,
    "management_ip": "10.70.2.10",
    "sync_status": "pending",
    "last_sync_at": null
  },
  "cameras": [],
  "created_at": "2026-06-25T10:00:00Z"
}
```

---

## 8. Location Validation Engine

### 8.1 Validation Rules

| Rule | Condition | Action | Priority |
|------|-----------|--------|----------|
| R1 | Location has ≥1 covering camera | Mark `camera_verified=true` | P2 |
| R2 | Camera offline >5h | Skip validation, alert | P3 |
| R3 | Camera sees unregistered device | Create investigation ticket | P2 |
| R4 | Asset moved without work order | Alert + create incident | P1 |
| R5 | Location has no camera coverage | Add to coverage gap report | P4 |

### 8.2 Validation Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Camera      │────→│  Location    │────→│  Asset       │
│  Online?     │     │  Coverage?   │     │  Match?      │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
  ┌─────────┐         ┌─────────┐         ┌─────────┐
  │  Yes:   │         │  Yes:   │         │  Yes:   │
  │  Proceed│         │  Mark   │         │  Verify │
  └─────────┘         │  verified│        └─────────┘
       │              └─────────┘              │
       ▼                                       ▼
  ┌─────────┐                           ┌─────────┐
  │  No:    │                           │  No:    │
  │  Alert  │                           │  Alert  │
  └─────────┘                           └─────────┘
```

### 8.3 Reconciliation Schedule

| Task | Frequency | Description |
|------|-----------|-------------|
| ONVIF Discovery | Daily 02:00 | Probe all NVR on network |
| SNMP Health | Every 5 min | Poll NVR health metrics |
| Camera Status | Every 1 min | Check camera online/offline |
| Location Verify | Daily 03:00 | Verify all asset_locations |
| Storage Alert | Every 15 min | Check storage capacity |

---

## 9. Data Quality Framework

### 9.1 Validation Rules

| Rule | Field | Check | Action on Fail |
|------|-------|-------|----------------|
| DQ1 | `management_ip` | Valid IPv4/IPv6 | Reject |
| DQ2 | `serial_number` | Non-empty, unique | Reject |
| DQ3 | `storage_used_gb` | ≤ storage_capacity_gb | Auto-correct |
| DQ4 | `channel_number` | ≤ channel_count | Reject |
| DQ5 | `stream_url` | Valid RTSP format | Warn |
| DQ6 | `onvif_profile` | S, T, or G | Default to S |
| DQ7 | `nvr_asset_id` | Must exist in asset_nvr | Reject |

### 9.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Device discovery accuracy | > 95% | ONVIF matches actual inventory |
| Camera registration completeness | > 90% | All cameras registered |
| Location verification coverage | > 80% | Locations with camera_verified |
| Sync success rate | > 99% | Successful ONVIF/SNMP syncs |
| Event capture rate | > 99% | Syslog events received |

---

## 10. Security

### 10.1 RBAC Matrix

| Role | NVR Read | NVR Write | Camera Read | Camera Write | Location Verify |
|------|----------|-----------|-------------|--------------|-----------------|
| admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| security_admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| operator | ✅ | ❌ | ✅ | ❌ | ❌ |
| viewer | ✅ | ❌ | ✅ | ❌ | ❌ |

### 10.2 Protocol Security

| Protocol | Security Measure |
|----------|------------------|
| ONVIF | WS-Security (UsernameToken), HTTPS |
| SNMP | SNMPv3 (authPriv), no v1/v2c in production |
| Syslog | TLS 1.2+ for syslog-ng, no UDP in production |
| RTSP | TLS for stream URLs, digest auth |

### 10.3 Network Security

| VLAN | Purpose | NVR Access |
|------|---------|------------|
| Management (10.70.0.0/24) | NVR management interface | Yes |
| Data (10.70.1.0/24) | Camera data traffic | Yes |
| DMZ (10.70.2.0/24) | External access (blocked) | No |

---

## 11. Monitoring & Alerting

### 11.1 Prometheus Metrics

```yaml
# NVR-specific metrics
- nvr_devices_total{status="online|offline|degraded"}
- nvr_cameras_total{nvr_id="...", status="online|offline"}
- nvr_storage_used_percent{nvr_id="..."}
- nvr_recording_status{nvr_id="...", channel="..."}  # 1=ok, 0=fail
- nvr_events_total{type="disk_full|camera_offline|tamper|nvr_failure"}
- nvr_sync_last_success_timestamp{nvr_id="..."}
- nvr_sync_duration_seconds{nvr_id="..."}
- nvr_onvif_discovery_total{vendor="..."}
- nvr_asset_location_verified_percent
```

### 11.2 Alert Rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| NVR Offline | `nvr_devices_total{status="offline"} > 0` | P1 | Immediate escalation |
| Camera Offline >5h | `nvr_cameras_total{status="offline"} > 0` for 5h | P2 | Create incident |
| Storage >85% | `nvr_storage_used_percent > 85` | P2 | Alert + capacity plan |
| Storage >95% | `nvr_storage_used_percent > 95` | P1 | Alert + immediate action |
| Sync Failed | `nvr_sync_last_success_timestamp` > 48h | P3 | Alert ops team |
| Location Coverage Gap | `nvr_asset_location_verified_percent < 80` | P4 | Monthly report |

### 11.3 Grafana Dashboard

**Dashboard: NVR Overview**
- NVR device status (online/offline/degraded)
- Camera status per NVR
- Storage capacity utilization
- Recording status per channel
- Event timeline (last 24h)
- Location verification coverage map

---

## 12. Acceptance Criteria

| # | Criterion | Test Method |
|---|-----------|-------------|
| 1 | NVR auto-discovered via ONVIF | `dcim.nvr.discovery` topic has records |
| 2 | NVR registered as asset | `SELECT * FROM asset_nvr` returns data |
| 3 | Camera mapped to NVR channel | `SELECT * FROM asset_camera` with valid nvr_asset_id |
| 4 | Location verified by camera | `asset_location.camera_verified = true` for covered areas |
| 5 | Health metrics flowing | `nvr_devices_total` in Prometheus |
| 6 | Events captured | `nvr_events_total` counter increases on camera offline |
| 7 | Storage capacity tracked | `nvr_storage_used_percent` accurate |
| 8 | Reconciliation works | ONVIF probe matches existing asset records |
| 9 | Audit trail complete | `asset_audit_log` has NVR-related entries |
| 10 | Multi-vendor support | Test with 2+ brands (e.g., Hikvision + Axis) |
| 11 | RBAC enforced | Non-admin cannot write NVR assets |
| 12 | TLS on all protocols | ONVIF, SNMPv3, syslog-ng with TLS |
| 13 | Alert rules active | NVR offline triggers P1 alert |
| 14 | Storage alert works | >85% capacity triggers P2 alert |
| 15 | API endpoints functional | All CRUD + sync endpoints return 200 |

---

## 13. Gap Comparison Template

### Gap: NVR Device Discovery

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Protocol | ONVIF WS-Discovery | | | |
| Auto-registration | Yes (daily probe) | | | |
| Vendor support | Multi-vendor (Hikvision, Dahua, Axis, Frigate) | | | |
| Discovery interval | 24h | | | |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

### Gap: Camera Location Validation

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Location verification | Camera-based (`camera_verified` flag) | | | |
| Coverage tracking | `camera_location_map` table | | | |
| Alert on gap | Monthly coverage report | | | |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

### Gap: NVR Health Monitoring

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Protocol | SNMPv3 + Syslog | | | |
| Metrics | Prometheus exporter | | | |
| Alert on offline | 5h threshold | | | |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

### Gap: Asset Repository Integration

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| New tables | asset_nvr, asset_camera, camera_location_map | | | |
| API endpoints | 10 new endpoints for NVR/Camera CRUD | | | |
| Kafka topics | 5 new topics (nvr.*) | | | |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

## References

- Block 1: Infrastructure Provisioning (`block1-infrastructure-provisioning.md`)
- Block 2: Data Ingestion & Integration (`block2-data-ingestion-integration.md`)
- Block 3: Asset Repository (`block3-asset-repository.md`)
- ONVIF Core Specification: https://www.onvif.org/specs/
- Hikvision ISAPI: https://www.hikvision.com/en/support/IP-Products/Manuals/
- Axis VAPIX: https://www.axis.com/support/developer-support/vapix
- Frigate NVR: https://frigate.video/
