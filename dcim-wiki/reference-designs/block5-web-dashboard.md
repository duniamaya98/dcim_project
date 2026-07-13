---
title: "Block 5 — Web Dashboard: Reference Design Spec"
created: 2026-06-23
updated: 2026-06-23
type: reference-design
block: 5
phase: 2
status: generated
confidence: high
tags: [dashboard, frontend, react, api-gateway, rbac, sso, noc, soc, cmdb-explorer]
wiki_pages:
  - web-dashboard
  - cmdb
  - analytics-ai-engine
  - workflow-automation
  - siem-soc
  - dashboard-framework-comparison
  - dcim-dashboard-design
purpose: >
  Reference design spec untuk Block 5 Web Dashboard.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# Block 5 — Web Dashboard: Reference Design Spec

> **Purpose:** Dokumen referensi lengkap untuk Web Dashboard — presentation layer NOC, SOC, Facilities, Management.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi. Setiap gap = connection point.
> **Architecture Diagram:** `diagrams/block5-web-dashboard-architecture.html`
> **Depends on:** Phase 1 (B1-B4), Block 1 (Infrastructure), Block 4 (CMDB)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Frontend Stack](#2-frontend-stack)
3. [API Gateway](#3-api-gateway)
4. [Authentication & RBAC](#4-authentication--rbac)
5. [NOC View](#5-noc-view)
6. [SOC View](#6-soc-view)
7. [Facilities View](#7-facilities-view)
8. [CMDB Explorer](#8-cmdb-explorer)
9. [SLA/KPI Dashboard](#9-slakpi-dashboard)
10. [Log Viewer](#10-log-viewer)
11. [Task Board](#11-task-board)
12. [Responsive Design](#12-responsive-design)
13. [Performance & Optimization](#13-performance--optimization)
14. [Security](#14-security)
15. [Acceptance Criteria](#15-acceptance-criteria)
16. [Gap Comparison Template](#16-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                      Web Dashboard                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Frontend (React/Vue)                     │  │
│  │  NOC • SOC • Facilities • CMDB Explorer • SLA • Logs    │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │ REST / GraphQL                      │
│  ┌────────────────────────┴─────────────────────────────────┐  │
│  │                  API Gateway (FastAPI)                     │  │
│  │  Auth • Rate Limit • RBAC • Request Transform • Cache    │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐  │
│  │              Backend Services                             │  │
│  │  CMDB API • Asset API • Analytics • SIEM • Workflow       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
User Browser
  → API Gateway (auth + rate limit + RBAC)
    → Backend Services (CMDB, Asset, Analytics, SIEM, Workflow)
      → Data Stores (PostgreSQL, Redis, Elasticsearch)
        → Response → Frontend Rendering
```

### 1.3 View Matrix

| View | Primary Users | Refresh | Data Sources | Priority |
|------|--------------|---------|-------------|----------|
| NOC | NOC Operators | 5s auto | Prometheus, Grafana, CMDB | P1 Critical |
| SOC | SOC Analysts | 10s auto | Elasticsearch, SIEM | P1 Critical |
| Facilities | Facilities Mgr | 30s auto | BMS/EPMS, Prometheus | P1 Critical |
| CMDB Explorer | IT Ops, Change Mgr | Manual | CMDB API | P2 High |
| SLA/KPI | Management | 5min | Analytics, CMDB | P2 High |
| Log Viewer | Ops, Dev, Security | Manual | Elasticsearch | P2 High |
| Task Board | IT Ops, Workflow | 30s auto | Workflow API | P3 Medium |

---

## 2. Frontend Stack

### 2.1 Technology Selection

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| Framework | **Vue 3** + Composition API | Simpler learning curve, excellent reactivity, smaller bundle |
| State Management | **Pinia** | Official Vue store, TypeScript support |
| Routing | **Vue Router 4** | Official, lazy loading, guards |
| UI Library | **Element Plus** or **Naive UI** | Mature component set, dark theme |
| Charts | **ECharts** via vue-echarts | Rich chart types, dark theme, real-time |
| Graph Viz | **D3.js** + custom renderer | CMDB topology, service maps |
| Build Tool | **Vite** | Fast HMR, ES modules |
| HTTP Client | **Axios** | Interceptors, retry, cancel |
| Auth | **Pinia OIDC Store** | SSO/OIDC integration |
| CSS | **Tailwind CSS** | Utility-first, dark theme |
| i18n | **vue-i18n** | Multi-language support |

### 2.2 Project Structure

```
dcim-core/frontend/
├── src/
│   ├── assets/                 # Static assets
│   ├── components/
│   │   ├── common/             # Shared components
│   │   │   ├── DataTable.vue
│   │   │   ├── StatusBadge.vue
│   │   │   ├── AlertBanner.vue
│   │   │   └── LoadingSpinner.vue
│   │   ├── charts/             # Chart components
│   │   │   ├── TimeSeriesChart.vue
│   │   │   ├── BarChart.vue
│   │   │   ├── PieChart.vue
│   │   │   └── GaugeChart.vue
│   │   ├── topology/           # CMDB graph
│   │   │   ├── TopologyGraph.vue
│   │   │   ├── TopologyNode.vue
│   │   │   └── TopologyEdge.vue
│   │   └── layout/             # Layout components
│   │       ├── AppHeader.vue
│   │       ├── AppSidebar.vue
│   │       └── AppFooter.vue
│   ├── views/                  # Page views
│   │   ├── NOCView.vue
│   │   ├── SOCView.vue
│   │   ├── FacilitiesView.vue
│   │   ├── CMDBExplorer.vue
│   │   ├── SLADashboard.vue
│   │   ├── LogViewer.vue
│   │   ├── TaskBoard.vue
│   │   └── Settings.vue
│   ├── stores/                 # Pinia stores
│   │   ├── auth.ts
│   │   ├── noc.ts
│   │   ├── soc.ts
│   │   ├── cmdb.ts
│   │   └── alerts.ts
│   ├── services/               # API services
│   │   ├── api.ts              # Base axios instance
│   │   ├── cmdbService.ts
│   │   ├── assetService.ts
│   │   ├── analyticsService.ts
│   │   ├── siemService.ts
│   │   └── workflowService.ts
│   ├── router/
│   │   └── index.ts
│   ├── composables/            # Reusable logic
│   │   ├── useWebSocket.ts
│   │   ├── useAutoRefresh.ts
│   │   └── useRBAC.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── validators.ts
│   ├── App.vue
│   └── main.ts
├── public/
├── package.json
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

### 2.3 Build & Deploy

```bash
# Development
npm run dev          # Vite dev server (:5173)

# Production
npm run build        # Output: dist/
npm run preview      # Preview production build

# Docker
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

---

## 3. API Gateway

### 3.1 Purpose

Central entry point untuk semua frontend requests. Handles auth, rate limiting, routing, caching.

### 3.2 API Design

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/summary` | Aggregated dashboard data |
| GET | `/api/v1/dashboard/noc` | NOC view data |
| GET | `/api/v1/dashboard/soc` | SOC view data |
| GET | `/api/v1/dashboard/facilities` | Facilities view data |
| GET | `/api/v1/dashboard/health` | System health overview |

### 3.3 Gateway Features

| Feature | Implementation | Config |
|---------|---------------|--------|
| Authentication | JWT validation | 5min token cache |
| Rate limiting | Per-user, sliding window | 100 req/min read, 20 req/min write |
| RBAC | Role + resource permissions | Cached in Redis |
| CORS | Allow frontend origin | Access-Control headers |
| Request transform | Query param normalization | — |
| Response cache | Redis cache per endpoint | 5s-60s TTL |
| Request logging | Structured JSON logs | All requests |
| Circuit breaker | Per backend service | 5 failures → open |

### 3.4 Rate Limiting

```python
# api/gateway.py

from fastapi import FastAPI, Request
from redis import asyncio as aioredis

app = FastAPI()
redis = aioredis.from_url("redis://redis:6379")

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_id = request.state.user_id
    endpoint = request.url.path
    method = request.method

    # Different limits per endpoint type
    if method == "GET":
        limit = 100  # per minute
    else:
        limit = 20

    key = f"ratelimit:{user_id}:{endpoint}"
    current = await redis.incr(key)

    if current == 1:
        await redis.expire(key, 60)

    if current > limit:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(limit - current)
    return response
```

---

## 4. Authentication & RBAC

### 4.1 SSO Integration

| Provider | Protocol | Config |
|----------|----------|--------|
| Keycloak | OIDC | issuer URL, client ID, scopes |
| Auth0 | OIDC | domain, client ID, audience |
| Azure AD | OIDC | tenant ID, client ID |

### 4.2 RBAC Model

| Role | Permissions | Description |
|------|------------|-------------|
| admin | * | Full access to all views and actions |
| operator | noc:read, soc:read, facilities:read, cmdb:read+write, workflow:read+write | Operational access |
| viewer | noc:read, soc:read, facilities:read, cmdb:read, sla:read | Read-only access |
| auditor | cmdb:read, audit:read, sla:read | Audit-only access |
| noc_operator | noc:*, facilities:* | NOC-specific access |
| soc_analyst | soc:*, cmdb:read | SOC-specific access |

### 4.3 Auth Flow

```
1. User opens dashboard → Redirect to SSO login
2. SSO authenticates → Returns JWT token
3. Frontend stores token (Pinia + localStorage)
4. Every API request → Authorization: Bearer <token>
5. API Gateway validates JWT → Extracts role + permissions
6. RBAC check → Allow/Deny
7. Token refresh → Silent refresh before expiry
```

### 4.4 JWT Payload

```json
{
  "sub": "user-id-uuid",
  "email": "operator@dcim.local",
  "name": "NOC Operator",
  "roles": ["noc_operator"],
  "permissions": ["noc:read", "noc:write", "facilities:read", "facilities:write"],
  "iat": 1750000000,
  "exp": 1750003600
}
```

---

## 5. NOC View

### 5.1 Components

| Component | Description | Refresh | Data Source |
|-----------|-------------|---------|-------------|
| Infrastructure Health | Real-time status of all components | 5s | Prometheus |
| Active Alerts | Current active alerts | 5s | Alertmanager |
| Capacity Overview | CPU, memory, disk, network | 30s | Prometheus |
| Uptime Tracker | Service uptime % | 1min | Prometheus |
| Event Timeline | Recent events stream | 5s | Kafka consumer |
| Quick Actions | Acknowledge, escalate, mute | Manual | Workflow API |

### 5.2 Layout

```
┌─────────────────────────────────────────────────────────────┐
│ NOC Dashboard                                    [Refresh]  │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│ │ Health Score│ │Active Alerts│ │  Uptime %   │ │Events/h││
│ │    95/100   │ │     3       │ │   99.95%    │ │  1,247 ││
│ └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
│                                                             │
│ ┌──────────────────────┐ ┌────────────────────────────────┐│
│ │   Infrastructure     │ │       Alert List               ││
│ │   Health Map         │ │  🔴 P1: PostgreSQL repl lag    ││
│ │                      │ │  🟡 P2: Kafka consumer lag     ││
│ │  [Server] [Switch]   │ │  🟡 P2: ES disk 82%            ││
│ │  [Storage] [Network] │ │  🟢 P3: Redis memory 70%      ││
│ │                      │ │                                ││
│ └──────────────────────┘ └────────────────────────────────┘│
│                                                             │
│ ┌──────────────────────────────────────────────────────────┐│
│ │              Event Timeline (live)                       ││
│ │ 14:32:01 INFO  web-server-01 CPU OK                      ││
│ │ 14:32:00 WARN  switch-floor3 Gi0/1 flapping              ││
│ │ 14:31:59 INFO  ups-rack-a1 load 85%                      ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Real-time Updates

```typescript
// composables/useWebSocket.ts
import { ref, onMounted, onUnmounted } from 'vue'

export function useWebSocket(url: string) {
  const data = ref(null)
  const connected = ref(false)
  let ws: WebSocket | null = null

  onMounted(() => {
    ws = new WebSocket(url)
    ws.onopen = () => { connected.value = true }
    ws.onmessage = (event) => {
      data.value = JSON.parse(event.data)
    }
    ws.onclose = () => {
      connected.value = false
      setTimeout(reconnect, 3000)
    }
  })

  onUnmounted(() => { ws?.close() })

  return { data, connected }
}
```

---

## 6. SOC View

### 6.1 Components

| Component | Description | Data Source |
|-----------|-------------|-------------|
| Security Events | Real-time security events | Elasticsearch |
| Incident List | Active security incidents | SIEM API |
| Threat Map | Geographic threat visualization | Elasticsearch |
| Compliance Status | CIS benchmark compliance | Wazuh |
| Access Anomalies | Unusual access patterns | Elasticsearch |
| Investigation Panel | Event detail + timeline | Elasticsearch |

### 6.2 Event Table Schema

```typescript
interface SecurityEvent {
  id: string
  timestamp: string
  source: string           // 'wazuh', 'siem', 'access_control'
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  category: string         // 'intrusion', 'policy_violation', 'anomaly'
  title: string
  description: string
  source_ip: string
  destination_ip: string
  asset_id?: string
  ci_id?: string
  status: 'new' | 'investigating' | 'resolved' | 'false_positive'
  assigned_to?: string
  correlation_id?: string
}
```

---

## 7. Facilities View

### 7.1 Components

| Component | Description | Refresh | Data Source |
|-----------|-------------|---------|-------------|
| Power Overview | UPS status, PDU load, power consumption | 30s | BMS/EPMS |
| Cooling Status | CRAC/CRAH status, temperature map | 30s | BMS |
| Environmental | Temperature, humidity, water leak | 30s | BMS |
| Rack Map | Physical rack visualization | 1min | CMDB + BMS |
| Energy Metrics | PUE, kWh, cost | 5min | Analytics |
| Capacity Planning | Rack space, power, cooling capacity | 1h | Analytics |

### 7.2 Temperature Heatmap

```
┌─────────────────────────────────────────┐
│            Floor 3 Temperature Map       │
│                                          │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
│  │22°C │ │23°C │ │21°C │ │24°C │      │
│  │  🟢 │ │  🟢 │ │  🟢 │ │  🟡 │      │
│  └─────┘ └─────┘ └─────┘ └─────┘      │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
│  │21°C │ │22°C │ │25°C │ │23°C │      │
│  │  🟢 │ │  🟢 │ │  🔴 │ │  🟢 │      │
│  └─────┘ └─────┘ └─────┘ └─────┘      │
│                                          │
│  🟢 Normal (18-24°C) 🟡 Warning (24-27°C) 🔴 Critical (>27°C) │
└─────────────────────────────────────────┘
```

---

## 8. CMDB Explorer

### 8.1 Components

| Component | Description |
|-----------|-------------|
| Topology Graph | Interactive D3.js graph visualization |
| CI Search | Search by name, type, serial, IP |
| CI Detail Panel | Full CI attributes + relationships |
| Relationship Editor | Add/remove relationships |
| Impact View | "What breaks if..." analysis |
| Filter Panel | Filter by type, status, owner, location |

### 8.2 Topology Graph Features

| Feature | Implementation |
|---------|---------------|
| Node rendering | Circle by CI type, color by status |
| Edge rendering | Line by relationship type, style by direction |
| Zoom/Pan | D3.js zoom behavior |
| Click node | Open CI detail panel |
| Drag node | Reposition for layout |
| Search | Highlight matching nodes |
| Filter | Show/hide by type |
| Depth control | BFS depth slider (1-5) |
| Impact mode | Highlight impact path |

### 8.3 Node Styling

| CI Type | Shape | Color |
|---------|-------|-------|
| Server | Rectangle | Blue |
| NetworkDevice | Hexagon | Green |
| Storage | Cylinder | Purple |
| VM | Diamond | Cyan |
| Application | Rounded Rect | Orange |
| Service | Star | Gold |
| Rack | Tall Rect | Gray |

### 8.4 Status Colors

| Status | Color |
|--------|-------|
| Active | Green |
| Planned | Blue |
| Maintenance | Yellow |
| In Use | Cyan |
| Retired | Gray |
| Disposed | Dark Gray |
| Error | Red |

---

## 9. SLA/KPI Dashboard

### 9.1 SLA Metrics

| Metric | Target | Calculation | Display |
|--------|--------|-------------|---------|
| System Uptime | 99.9% | (total - downtime) / total | Gauge |
| Incident Response Time | < 15min | Time to first response | Trend |
| MTTR | < 4h | Mean time to resolve | Trend |
| MTBF | > 720h | Mean time between failures | Trend |
| Change Success Rate | > 95% | Successful changes / total | Bar |
| Data Quality Score | > 90% | Completeness + accuracy | Gauge |

### 9.2 KPI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ SLA/KPI Dashboard                              Period: 30d  │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│ │   Uptime    │ │ MTTR        │ │  MTBF       │ │ Data   ││
│ │   99.97%    │ │   2.5h      │ │   840h      │ │ 94%    ││
│ │  ✅ On Track│ │ ✅ On Track  │ │ ✅ On Track  │ │ ⚠️     ││
│ └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
│                                                             │
│ ┌──────────────────────┐ ┌────────────────────────────────┐│
│ │   SLA Compliance     │ │      Incident Trend            ││
│ │   Trend (30 days)    │ │      (30 days)                 ││
│ │   [Line chart]       │ │      [Bar chart]               ││
│ └──────────────────────┘ └────────────────────────────────┘│
│                                                             │
│ ┌──────────────────────┐ ┌────────────────────────────────┐│
│ │   Top Issues         │ │      Team Performance          ││
│ │   1. Network flapping│ │      [Table: assignee, MTTR]   ││
│ │   2. Disk space      │ │                                ││
│ │   3. SSL expiry      │ │                                ││
│ └──────────────────────┘ └────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Log Viewer

### 10.1 Features

| Feature | Description |
|---------|-------------|
| Full-text search | Elasticsearch query DSL |
| Time range picker | Predefined (1h, 6h, 24h, 7d) + custom |
| Source filter | Filter by source system |
| Severity filter | Critical, Error, Warning, Info, Debug |
| Real-time tail | Live log streaming |
| Correlation | Link events by correlation_id |
| Export | CSV/JSON download |

### 10.2 Log Entry Schema

```typescript
interface LogEntry {
  id: string
  timestamp: string
  level: 'error' | 'warn' | 'info' | 'debug'
  service: string
  source: string
  message: string
  host: string
  correlation_id?: string
  metadata?: Record<string, any>
}
```

### 10.3 Search Syntax

```
# Basic search
postgresql replication lag

# Field-specific
service:postgresql level:error

# Time range
@timestamp:[2026-06-23T14:00:00 TO 2026-06-23T15:00:00]

# Boolean
level:error AND service:postgresql
level:error OR level:warn

# Wildcard
service:postgres*
```

---

## 11. Task Board

### 11.1 Kanban Columns

| Column | Description | SLA |
|--------|-------------|-----|
| Backlog | Tasks not yet scheduled | — |
| To Do | Scheduled for execution | — |
| In Progress | Currently being worked on | Countdown active |
| Review | Pending review/approval | 24h |
| Done | Completed | — |

### 11.2 Task Card Schema

```typescript
interface TaskCard {
  id: string
  title: string
  description: string
  status: 'backlog' | 'todo' | 'in_progress' | 'review' | 'done'
  priority: 'P1' | 'P2' | 'P3' | 'P4'
  assignee?: string
  sla_deadline?: string
  sla_remaining?: number  // seconds
  tags: string[]
  created_at: string
  updated_at: string
}
```

---

## 12. Responsive Design

### 12.1 Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 768px | Single column, stacked |
| Tablet | 768-1024px | 2-column grid |
| Desktop | > 1024px | Full layout |
| Large | > 1440px | Extended sidebar |

### 12.2 Responsive Rules

| Component | Desktop | Tablet | Mobile |
|-----------|---------|--------|--------|
| Sidebar | Always visible | Collapsible | Hidden (hamburger) |
| Dashboard grid | 4 columns | 2 columns | 1 column |
| Topology graph | Full screen | Scaled down | Simplified view |
| Log viewer | Side panel | Full width | Full width |
| Task board | 5 columns | 3 columns | Horizontal scroll |

---

## 13. Performance & Optimization

### 13.1 Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint | < 1.5s | Lighthouse |
| Largest Contentful Paint | < 2.5s | Lighthouse |
| Time to Interactive | < 3s | Lighthouse |
| Bundle Size (gzipped) | < 500KB | Webpack bundle analyzer |
| API Response Time | < 200ms (p95) | Browser devtools |

### 13.2 Optimization Strategies

| Strategy | Implementation |
|----------|---------------|
| Code splitting | Lazy load views by route |
| Tree shaking | ECharts, D3.js modular imports |
| Caching | Service worker for static assets |
| WebSocket | Real-time updates (avoid polling) |
| Virtual scrolling | Large log tables, event lists |
| Debounced search | 300ms debounce on search inputs |
| Image optimization | SVG icons, no raster |
| CDN | Static assets from CDN |

---

## 14. Security

### 14.1 Frontend Security

| Control | Implementation |
|---------|---------------|
| XSS prevention | Vue template escaping + CSP headers |
| CSRF | SameSite cookies + CSRF token |
| Auth token storage | Pinia store + httpOnly cookie |
| Route guards | Vue Router beforeEach钩子 |
| Content Security Policy | Strict CSP headers |
| Dependency scanning | npm audit in CI |

---

## 15. Acceptance Criteria — Block 5 Complete

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | Frontend scaffold created | `npm run dev` starts | ⬜ |
| 2 | API Gateway working | Routes, rate limit, auth | ⬜ |
| 3 | RBAC/SSO integration | Login, role-based access | ⬜ |
| 4 | NOC View functional | Real-time health, alerts | ⬜ |
| 5 | SOC View functional | Security events, incidents | ⬜ |
| 6 | Facilities View functional | Power, cooling, environment | ⬜ |
| 7 | CMDB Explorer functional | Topology graph, search, filter | ⬜ |
| 8 | SLA/KPI Dashboard functional | Metrics, trends, compliance | ⬜ |
| 9 | Log Viewer functional | Search, filter, export | ⬜ |
| 10 | Task Board functional | Kanban, drag-drop, SLA | ⬜ |
| 11 | Responsive design | Desktop, tablet, mobile | ⬜ |
| 12 | Performance targets met | Lighthouse score > 80 | ⬜ |
| 13 | Security controls | XSS, CSRF, CSP | ⬜ |
| 14 | Dark theme | Consistent dark UI | ⬜ |

---

## 16. Gap Comparison Template

### Gap: [Component Name]

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Frontend stack | [spec choices] | [aktual choices] | [match/mismatch] | P1-P4 |
| API Gateway | [spec features] | [aktual features] | [gap detail] | P1-P4 |
| RBAC/SSO | [spec roles] | [aktual roles] | [gap detail] | P1-P4 |
| NOC View | [spec components] | [aktual components] | [gap detail] | P1-P4 |
| SOC View | [spec components] | [aktual components] | [gap detail] | P1-P4 |
| Facilities View | [spec components] | [aktual components] | [gap detail] | P1-P4 |
| CMDB Explorer | [spec features] | [aktual features] | [gap detail] | P1-P4 |
| SLA/KPI | [spec metrics] | [aktual metrics] | [gap detail] | P1-P4 |
| Log Viewer | [spec features] | [aktual features] | [gap detail] | P1-P4 |
| Task Board | [spec columns] | [aktual columns] | [gap detail] | P1-P4 |
| Responsive | [spec breakpoints] | [aktual breakpoints] | [gap detail] | P1-P4 |
| Performance | [spec targets] | [aktual metrics] | [gap detail] | P1-P4 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

## References

- [[web-dashboard]]
- [[cmdb]] — CMDB explorer
- [[analytics-ai-engine]] — analytics visualization
- [[workflow-automation]] — task board
- [[siem-soc]] — SOC view
- [[dashboard-framework-comparison]]
- [[dcim-dashboard-design]]
- [[dcim-core-platform]]

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-23
> **Purpose:** Reference for team comparison → gap identification → connection dots
> **Phase 2 Start:** Block 5 Web Dashboard (1 of 5)
