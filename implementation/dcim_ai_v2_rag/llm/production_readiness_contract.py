"""
DCIM AI production-readiness contract for supervised operations agents.

This module keeps the production agent interface strict without depending on
external schema libraries. It complements ``rca_prompt_contract.py`` by covering
incident operations: evidence, tool calls, approval requests, and agent output.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union


SCHEMA_VERSION = "dcim-agent-response/v1"

STATUS_VALUES = {
    "investigating",
    "needs_more_data",
    "ready_for_approval",
    "action_executed",
    "escalated",
    "resolved",
}

RISK_LEVELS = {"low", "medium", "high", "critical"}

READ_ONLY_ACTION_TYPES = {
    "read_metrics",
    "query_logs",
    "lookup_asset",
    "search_ticket",
    "retrieve_sop",
}

SAFE_WRITE_ACTION_TYPES = {
    "create_ticket",
    "update_ticket",
    "notify",
    "request_approval",
}

DESTRUCTIVE_ACTION_TYPES = {
    "restart_service",
    "restart_host",
    "power_cycle",
    "change_config",
    "suppress_alert",
    "close_high_severity_incident",
}

ACTION_TYPES = READ_ONLY_ACTION_TYPES | SAFE_WRITE_ACTION_TYPES | DESTRUCTIVE_ACTION_TYPES

SYSTEM_PROMPT = """
Anda adalah DCIM Operations Agent untuk data center production.

Misi:
- Bantu monitoring, alert triage, incident response, SOP execution, dan handover.
- Gunakan hanya evidence yang tersedia dari incident_state, retrieved_sop,
  live_metrics, logs, tool_results, asset_context, dan operator_notes.
- Jangan mengarang hostname, metric, timestamp, ticket, SOP ID, atau status tool.
- Jika data kurang, isi missing_evidence dan pilih action read-only untuk
  mengumpulkan evidence.

Aturan output:
- Jawab hanya JSON valid sesuai schema dcim-agent-response/v1.
- Bedakan fact, live observation, dan inference pada setiap evidence item.
- Semua tool call harus punya action_type, tool_name, arguments, risk,
  requires_approval, dan reason.
- Aksi restart, power cycle, config change, suppress alert, atau close incident
  severity tinggi wajib requires_approval=true dan approval_request terisi.
- Jangan mengeksekusi remediation jika confidence rendah, SOP tidak ditemukan,
  evidence bertentangan, atau maintenance window tidak jelas.
- Vision/dashboard screenshot hanya supporting signal; validasi dengan metric
  atau log sebelum rekomendasi aksi.
""".strip()

TOP_LEVEL_KEYS = {
    "schema_version",
    "incident_id",
    "status",
    "summary",
    "evidence",
    "risk",
    "recommended_action",
    "tool_calls",
    "requires_human_approval",
    "approval_request",
    "missing_evidence",
    "confidence",
}

EVIDENCE_KEYS = {
    "id",
    "source",
    "timestamp",
    "asset_id",
    "kind",
    "summary",
    "confidence",
    "value",
    "metadata",
}

TOOL_CALL_KEYS = {
    "id",
    "action_type",
    "tool_name",
    "arguments",
    "risk",
    "requires_approval",
    "reason",
    "timeout_seconds",
}

APPROVAL_KEYS = {
    "id",
    "requested_action_id",
    "approver_role",
    "reason",
    "risk",
    "evidence_ids",
    "expires_at",
}


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    raw: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"valid": self.valid, "errors": list(self.errors), "raw": self.raw}


@dataclass
class EvidenceItem:
    id: str
    source: str
    timestamp: str
    asset_id: str
    kind: str
    summary: str
    confidence: float
    value: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ToolCall:
    id: str
    action_type: str
    tool_name: str
    arguments: Dict[str, Any]
    risk: str
    requires_approval: bool
    reason: str
    timeout_seconds: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ApprovalRequest:
    id: str
    requested_action_id: str
    approver_role: str
    reason: str
    risk: str
    evidence_ids: List[str]
    expires_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_dcim_operations_messages(context: Mapping[str, Any]) -> List[Dict[str, str]]:
    """
    Build OpenAI/Ollama-compatible messages for the supervised DCIM agent.

    ``context`` should already be assembled by the RAG/context engine and should
    include sections such as incident_state, retrieved_sop, live_metrics, logs,
    tool_results, asset_context, and operator_notes.
    """
    context_json = json.dumps(context, ensure_ascii=False, indent=2, sort_keys=True)
    user_prompt = (
        "Analisis konteks DCIM berikut dan hasilkan JSON valid sesuai "
        f"{SCHEMA_VERSION}. Jangan gunakan data di luar konteks.\n\n"
        f"{context_json}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def action_requires_approval(action_type: str) -> bool:
    """Return True when an action type must be approved by a human operator."""
    return action_type in DESTRUCTIVE_ACTION_TYPES


def _coerce_json(raw: Union[str, Mapping[str, Any]]) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    if isinstance(raw, Mapping):
        return dict(raw), []
    if not isinstance(raw, str):
        return None, ["Agent response must be a JSON string or mapping."]
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [f"Invalid JSON: {exc}"]
    if not isinstance(parsed, dict):
        return None, ["Agent response JSON must be an object."]
    return parsed, []


def _require_keys(payload: Mapping[str, Any], required: set, label: str, errors: List[str]) -> None:
    missing = sorted(required - set(payload.keys()))
    if missing:
        errors.append(f"{label} missing required keys: {missing}")


def _reject_extra_keys(payload: Mapping[str, Any], allowed: set, label: str, errors: List[str]) -> None:
    extra = sorted(set(payload.keys()) - allowed)
    if extra:
        errors.append(f"{label} has unexpected keys: {extra}")


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_confidence(value: Any) -> bool:
    return isinstance(value, (int, float)) and 0 <= float(value) <= 1


def _validate_evidence(item: Any, index: int, errors: List[str]) -> None:
    label = f"evidence[{index}]"
    if not isinstance(item, Mapping):
        errors.append(f"{label} must be an object.")
        return

    _require_keys(item, EVIDENCE_KEYS, label, errors)
    _reject_extra_keys(item, EVIDENCE_KEYS, label, errors)

    for key in ("id", "source", "timestamp", "asset_id", "kind", "summary"):
        if key in item and not _non_empty_string(item[key]):
            errors.append(f"{label}.{key} must be a non-empty string.")
    if "confidence" in item and not _valid_confidence(item["confidence"]):
        errors.append(f"{label}.confidence must be a number between 0 and 1.")
    if "metadata" in item and not isinstance(item["metadata"], Mapping):
        errors.append(f"{label}.metadata must be an object.")


def _validate_tool_call(item: Any, index: int, errors: List[str]) -> None:
    label = f"tool_calls[{index}]"
    if not isinstance(item, Mapping):
        errors.append(f"{label} must be an object.")
        return

    _require_keys(item, TOOL_CALL_KEYS, label, errors)
    _reject_extra_keys(item, TOOL_CALL_KEYS, label, errors)

    for key in ("id", "action_type", "tool_name", "reason"):
        if key in item and not _non_empty_string(item[key]):
            errors.append(f"{label}.{key} must be a non-empty string.")

    action_type = item.get("action_type")
    if "action_type" in item and action_type not in ACTION_TYPES:
        errors.append(f"{label}.action_type is not allowed: {action_type}")

    risk = item.get("risk")
    if "risk" in item and risk not in RISK_LEVELS:
        errors.append(f"{label}.risk must be one of {sorted(RISK_LEVELS)}.")

    if "arguments" in item and not isinstance(item["arguments"], Mapping):
        errors.append(f"{label}.arguments must be an object.")

    requires_approval = item.get("requires_approval")
    if "requires_approval" in item and not isinstance(requires_approval, bool):
        errors.append(f"{label}.requires_approval must be boolean.")

    timeout_seconds = item.get("timeout_seconds")
    if "timeout_seconds" in item and (
        not isinstance(timeout_seconds, int) or timeout_seconds <= 0 or timeout_seconds > 300
    ):
        errors.append(f"{label}.timeout_seconds must be an integer from 1 to 300.")

    if isinstance(action_type, str) and action_requires_approval(action_type) and requires_approval is not True:
        errors.append(f"{label}.{action_type} requires human approval.")


def _validate_approval_request(payload: Any, errors: List[str]) -> None:
    label = "approval_request"
    if payload is None:
        return
    if not isinstance(payload, Mapping):
        errors.append(f"{label} must be null or an object.")
        return

    _require_keys(payload, APPROVAL_KEYS, label, errors)
    _reject_extra_keys(payload, APPROVAL_KEYS, label, errors)

    for key in ("id", "requested_action_id", "approver_role", "reason", "expires_at"):
        if key in payload and not _non_empty_string(payload[key]):
            errors.append(f"{label}.{key} must be a non-empty string.")

    risk = payload.get("risk")
    if "risk" in payload and risk not in RISK_LEVELS:
        errors.append(f"{label}.risk must be one of {sorted(RISK_LEVELS)}.")

    evidence_ids = payload.get("evidence_ids")
    if "evidence_ids" in payload:
        if not isinstance(evidence_ids, list) or not evidence_ids:
            errors.append(f"{label}.evidence_ids must be a non-empty list.")
        elif any(not _non_empty_string(item) for item in evidence_ids):
            errors.append(f"{label}.evidence_ids items must be non-empty strings.")


def validate_dcim_agent_response(raw: Union[str, Mapping[str, Any]]) -> ValidationResult:
    """
    Validate a DCIM agent response before downstream tool execution.

    The validator is deliberately strict because the capability test found
    json_mode, context_engine, memory, and multi-turn gaps that matter for
    production operations.
    """
    payload, errors = _coerce_json(raw)
    if payload is None:
        return ValidationResult(valid=False, errors=errors, raw=raw)

    _require_keys(payload, TOP_LEVEL_KEYS, "response", errors)
    _reject_extra_keys(payload, TOP_LEVEL_KEYS, "response", errors)

    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")

    for key in ("incident_id", "summary", "recommended_action"):
        if key in payload and not _non_empty_string(payload[key]):
            errors.append(f"{key} must be a non-empty string.")

    status = payload.get("status")
    if "status" in payload and status not in STATUS_VALUES:
        errors.append(f"status must be one of {sorted(STATUS_VALUES)}.")

    risk = payload.get("risk")
    if "risk" in payload and risk not in RISK_LEVELS:
        errors.append(f"risk must be one of {sorted(RISK_LEVELS)}.")

    if "confidence" in payload and not _valid_confidence(payload["confidence"]):
        errors.append("confidence must be a number between 0 and 1.")

    requires_human_approval = payload.get("requires_human_approval")
    if "requires_human_approval" in payload and not isinstance(requires_human_approval, bool):
        errors.append("requires_human_approval must be boolean.")

    evidence = payload.get("evidence", [])
    if "evidence" in payload:
        if not isinstance(evidence, list):
            errors.append("evidence must be a list.")
            evidence = []
        for index, item in enumerate(evidence):
            _validate_evidence(item, index, errors)

    tool_calls = payload.get("tool_calls", [])
    if "tool_calls" in payload:
        if not isinstance(tool_calls, list):
            errors.append("tool_calls must be a list.")
            tool_calls = []
        for index, item in enumerate(tool_calls):
            _validate_tool_call(item, index, errors)

    missing_evidence = payload.get("missing_evidence", [])
    if "missing_evidence" in payload:
        if not isinstance(missing_evidence, list):
            errors.append("missing_evidence must be a list.")
        elif any(not _non_empty_string(item) for item in missing_evidence):
            errors.append("missing_evidence items must be non-empty strings.")

    _validate_approval_request(payload.get("approval_request"), errors)

    has_approval_request = isinstance(payload.get("approval_request"), Mapping)
    if requires_human_approval is True and not has_approval_request:
        errors.append("requires_human_approval=true requires approval_request object.")

    if requires_human_approval is False:
        for index, item in enumerate(tool_calls):
            if isinstance(item, Mapping) and action_requires_approval(str(item.get("action_type"))):
                errors.append(f"tool_calls[{index}] requires top-level human approval.")

    return ValidationResult(valid=not errors, errors=errors, raw=payload)


__all__ = [
    "SCHEMA_VERSION",
    "SYSTEM_PROMPT",
    "STATUS_VALUES",
    "RISK_LEVELS",
    "ACTION_TYPES",
    "READ_ONLY_ACTION_TYPES",
    "SAFE_WRITE_ACTION_TYPES",
    "DESTRUCTIVE_ACTION_TYPES",
    "EvidenceItem",
    "ToolCall",
    "ApprovalRequest",
    "ValidationResult",
    "action_requires_approval",
    "build_dcim_operations_messages",
    "validate_dcim_agent_response",
]
