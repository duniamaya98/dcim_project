"""
DCIM AI — RCA LLM Prompt Contract (MT-022 §6.6)

Tujuan:
    - Membuat prompt RCA yang fixed dan konsisten untuk dcim_assistant.
    - Memaksa struktur output JSON agar downstream parser aman.
    - Memberi validator ringan untuk output LLM sebelum dikirim ke dashboard
      atau incident management.

Tidak melakukan inference LLM. Modul ini hanya membuat payload prompt dan
memvalidasi respons.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union


SYSTEM_PROMPT = (
    "Anda adalah DCIM AI Assistant. Berikan analisis root cause yang ringkas, "
    "teknis, dan actionable berdasarkan struktur input. "
    "Jangan mengarang data di luar evidence. Jika konteks tidak lengkap, sebutkan keterbatasannya."
)

REQUIRED_RESPONSE_KEYS = ("summary", "impact", "actions")
MAX_ACTIONS = 3


@dataclass
class RCAAlertNarrative:
    """Output JSON terstandardisasi dari LLM."""

    summary: str
    impact: str
    actions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LLMValidationResult:
    """Hasil validasi respons LLM."""

    valid: bool
    narrative: Optional[RCAAlertNarrative] = None
    errors: List[str] = field(default_factory=list)
    raw: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "narrative": self.narrative.to_dict() if self.narrative else None,
            "errors": self.errors,
            "raw": self.raw,
        }


# ============================================================================
# Prompt builder
# ============================================================================


def _safe_get(mapping: Optional[Mapping[str, Any]], key: str, default: str = "unknown") -> Any:
    if not mapping:
        return default
    value = mapping.get(key, default)
    return default if value in (None, "") else value


def _format_chain(chain: Union[str, Sequence[str], None]) -> str:
    if chain is None:
        return "unknown"
    if isinstance(chain, str):
        return chain or "unknown"
    if not chain:
        return "unknown"
    return " → ".join(str(item) for item in chain)


def _format_float(value: Any, default: float = 0.0) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return f"{default:.2f}"


def build_rca_user_prompt(rca_result: Any) -> str:
    """
    Build user prompt dari RootCauseResult-like object.

    Menerima object dengan method ``to_dict()`` atau dict biasa.
    Field yang diharapkan mengikuti MT-022 §6.6.
    """
    data = rca_result.to_dict() if hasattr(rca_result, "to_dict") else dict(rca_result)
    asset = data.get("asset_context") or {}

    timestamp = data.get("timestamp", "unknown")
    incident_id = data.get("incident_id", "unknown")
    mode = data.get("mode", "reactive")
    root_domain = data.get("root_domain", "unknown")
    confidence = _format_float(data.get("confidence"))
    entropy = _format_float(data.get("entropy"))
    chain = _format_chain(data.get("causal_chain"))
    evidence = data.get("explanation", "No explanation available.")

    return (
        f"Incident: {incident_id} pada {timestamp}\n"
        f"Asset: {_safe_get(asset, 'role')} di {_safe_get(asset, 'rack')} "
        f"({_safe_get(asset, 'site')}), criticality {_safe_get(asset, 'criticality')}\n"
        f"Mode: {mode}\n"
        f"Root domain: {root_domain} (confidence={confidence}, entropy={entropy})\n"
        f"Causal chain: {chain}\n"
        f"Evidence: {evidence}\n\n"
        "Berikan output JSON valid dengan struktur persis:\n"
        "{\n"
        '  "summary": "Penjelasan root cause 2-3 kalimat",\n'
        '  "impact": "Estimasi dampak operasional",\n'
        '  "actions": ["tindakan 1", "tindakan 2", "tindakan 3"]\n'
        "}\n"
        f"Maksimum {MAX_ACTIONS} actions. Jangan tambah key lain."
    )


def build_rca_chat_messages(rca_result: Any) -> List[Dict[str, str]]:
    """Return payload OpenAI-compatible chat messages."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_rca_user_prompt(rca_result)},
    ]


def build_ollama_options() -> Dict[str, Any]:
    """Default deterministic options untuk RCA narrative automation."""
    return {
        "temperature": 0,
        "top_p": 0.9,
        "num_predict": 512,
    }


# ============================================================================
# Output validator
# ============================================================================


def _coerce_json(raw: Union[str, Mapping[str, Any]]) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    if isinstance(raw, Mapping):
        return dict(raw), []
    if not isinstance(raw, str):
        return None, ["LLM response must be JSON string or mapping."]
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [f"Invalid JSON: {exc}"]
    if not isinstance(parsed, dict):
        return None, ["LLM response JSON must be an object."]
    return parsed, []


def validate_rca_llm_response(raw: Union[str, Mapping[str, Any]]) -> LLMValidationResult:
    """
    Validasi output LLM agar aman dipakai downstream.

    Rules:
        - Harus JSON object.
        - Wajib punya `summary`, `impact`, `actions`.
        - `summary` & `impact` string non-empty.
        - `actions` list string, 1..3 item.
        - Key ekstra dianggap error untuk menjaga kontrak ketat.
    """
    payload, errors = _coerce_json(raw)
    if payload is None:
        return LLMValidationResult(valid=False, errors=errors, raw=raw)

    allowed_keys = set(REQUIRED_RESPONSE_KEYS)
    extra_keys = sorted(set(payload.keys()) - allowed_keys)
    if extra_keys:
        errors.append(f"Unexpected keys: {extra_keys}")

    missing = [key for key in REQUIRED_RESPONSE_KEYS if key not in payload]
    if missing:
        errors.append(f"Missing required keys: {missing}")

    summary = payload.get("summary")
    impact = payload.get("impact")
    actions = payload.get("actions")

    if not isinstance(summary, str) or not summary.strip():
        errors.append("summary must be a non-empty string.")
    if not isinstance(impact, str) or not impact.strip():
        errors.append("impact must be a non-empty string.")
    if not isinstance(actions, list):
        errors.append("actions must be a list.")
        actions = []
    else:
        if not (1 <= len(actions) <= MAX_ACTIONS):
            errors.append(f"actions must contain 1..{MAX_ACTIONS} items.")
        if any(not isinstance(item, str) or not item.strip() for item in actions):
            errors.append("actions items must be non-empty strings.")

    if errors:
        return LLMValidationResult(valid=False, errors=errors, raw=payload)

    narrative = RCAAlertNarrative(
        summary=summary.strip(),
        impact=impact.strip(),
        actions=[item.strip() for item in actions],
    )
    return LLMValidationResult(valid=True, narrative=narrative, raw=payload)


__all__ = [
    "SYSTEM_PROMPT",
    "REQUIRED_RESPONSE_KEYS",
    "MAX_ACTIONS",
    "RCAAlertNarrative",
    "LLMValidationResult",
    "build_rca_user_prompt",
    "build_rca_chat_messages",
    "build_ollama_options",
    "validate_rca_llm_response",
]
