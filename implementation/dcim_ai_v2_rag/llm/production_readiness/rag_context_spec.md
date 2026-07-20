# DCIM RAG Context Assembly Spec

## Goal

Memberi model konteks incident yang cukup untuk RCA dan SOP execution tanpa
membuka ruang hallucination pada hostname, metric, timestamp, atau action.

## Context Shape

```json
{
  "incident_state": {
    "incident_id": "inc-20260611-001",
    "trigger": "thermal_alarm",
    "severity": "critical",
    "opened_at": "2026-06-11T09:12:00Z",
    "affected_assets": ["srv-app-05"],
    "current_status": "investigating"
  },
  "retrieved_sop": [],
  "live_metrics": [],
  "logs": [],
  "tool_results": [],
  "asset_context": [],
  "operator_notes": []
}
```

## Retrieval Layers

| Layer | Source | Retrieval |
|---|---|---|
| SOP/runbook | SOP, vendor manual, escalation matrix | Hybrid BM25 + vector, filter by domain/severity/site |
| Asset context | DCIM/CMDB/NetBox | Exact lookup by asset ID, rack, site, upstream PDU/UPS |
| Metrics | Prometheus/Grafana/DCIM API | Time-window query, include unit and aggregation |
| Logs/events | Loki/ELK/Splunk/BMS events | Keyword + time-window + asset filter |
| Tickets | Jira/ServiceNow | Incident ID, asset ID, alert fingerprint |

## Assembly Rules

- Use external incident state; do not rely on model memory.
- Every context item must include `source`, `timestamp`, and `asset_id`.
- Prefer fresh live data over stale retrieved text for operational state.
- SOP snippets must include `sop_id`, `version`, `section`, and `effective_date`.
- If evidence conflicts, include both observations and set status
  `needs_more_data`.
- Keep context budget in this order: current incident state, relevant SOP,
  live metrics, logs/events, asset dependencies, prior tickets.

## RAG Output Requirements

The assembled context passed to the model must contain:

- `incident_state` exactly once.
- `retrieved_sop` top 3 snippets max for normal incidents, top 5 for critical.
- `live_metrics` for affected assets and direct dependencies.
- `logs` limited to the incident time window plus 15 minutes before trigger.
- `asset_context` for affected asset, rack, upstream PDU, UPS, and cooling zone.
- `operator_notes` only from current incident or verified handover.

## Failure Modes

| Condition | Required agent behavior |
|---|---|
| SOP not found | Do not remediate; retrieve SOP or escalate. |
| Metric stale | Mark missing evidence; query fresh metric. |
| Logs unavailable | Continue with lower confidence and request log query retry. |
| Asset not in CMDB | Use `asset_id=unknown` or provided ID only; do not invent topology. |
| Conflicting sources | Keep both evidence items and request human review or extra tool call. |
