---
title: Asset Data Model
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [asset-repository, architecture, data-quality]
sources: []
confidence: high
---

# Asset Data Model

Data model untuk Asset Repository.

## Core Tables

### asset
```sql
asset_id        VARCHAR(50) PRIMARY KEY
serial_number   VARCHAR(100) UNIQUE NOT NULL
asset_tag       VARCHAR(100) UNIQUE
name            VARCHAR(255) NOT NULL
model           VARCHAR(100)
manufacturer    VARCHAR(100)
owner_dept      VARCHAR(100)
location_id     VARCHAR(50)
po_number       VARCHAR(100)
purchase_date   DATE
purchase_cost   DECIMAL(15,2)
warranty_start  DATE
warranty_end    DATE
contract_id     VARCHAR(50)
lifecycle_status VARCHAR(50) NOT NULL
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### asset_location
```sql
location_id     VARCHAR(50) PRIMARY KEY
building        VARCHAR(100)
floor           VARCHAR(50)
room            VARCHAR(100)
rack            VARCHAR(50)
position_u      VARCHAR(20)
latitude        DECIMAL(10,8)
longitude       DECIMAL(11,8)
created_at      TIMESTAMP
```

### asset_financial
```sql
asset_id              VARCHAR(50) REFERENCES asset(asset_id)
depreciation_method   VARCHAR(50)
useful_life_years     INT
book_value            DECIMAL(15,2)
last_depreciation_date DATE
```

### asset_contract
```sql
contract_id     VARCHAR(50) PRIMARY KEY
vendor          VARCHAR(100)
contract_type   VARCHAR(50)
start_date      DATE
end_date        DATE
sla_terms       TEXT
renewal_date    DATE
```

## Lifecycle States
On Order → Received → Deployed → In Storage → Maintenance → Retired → Disposed

## Related
- [[asset-repository]]
- [[postgresql]]
- [[redis]]
- [[dcim-core-platform]]
- [[cmdb-reconciliation-runbook]]
