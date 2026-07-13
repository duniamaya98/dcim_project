---
title: CMDB Data Model
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [cmdb, architecture, data-quality]
sources: []
confidence: high
---

# CMDB Data Model

Data model untuk Configuration Management Database.

## CI Types
- Server
- NetworkDevice
- Storage
- VM
- Application
- Service
- Rack
- Building
- Floor
- Room

## Core Tables

### ci
```sql
ci_id          VARCHAR(50) PRIMARY KEY
ci_type        VARCHAR(50) NOT NULL
name           VARCHAR(255) NOT NULL
status         VARCHAR(50) NOT NULL -- lifecycle status
owner          VARCHAR(100)
location_id    VARCHAR(50)
serial_number  VARCHAR(100)
created_at     TIMESTAMP
updated_at     TIMESTAMP
```

### ci_attribute
```sql
ci_id          VARCHAR(50) REFERENCES ci(ci_id)
attr_name      VARCHAR(100)
attr_value     TEXT
attr_type      VARCHAR(50)
PRIMARY KEY (ci_id, attr_name)
```

### ci_relationship
```sql
source_ci_id   VARCHAR(50) REFERENCES ci(ci_id)
target_ci_id   VARCHAR(50) REFERENCES ci(ci_id)
relationship_type VARCHAR(50) -- contains, depends_on, connected_to
metadata       JSONB
PRIMARY KEY (source_ci_id, target_ci_id, relationship_type)
```

### ci_lifecycle
```sql
ci_id          VARCHAR(50) REFERENCES ci(ci_id)
status         VARCHAR(50)
changed_by     VARCHAR(100)
changed_at     TIMESTAMP
reason         TEXT
```

## Lifecycle States
Planned → Active → Maintenance → Retired → Disposed

## Relationship Types
- **Containment**: Rack contains Server
- **Dependency**: Service depends on Application
- **Connectivity**: Server connected_to Switch

## Related
- [[cmdb]]
- [[postgresql]]
- [[dcim-core-platform]]
