"""
Constrained JSON client untuk DCIM Operations Agent.

Strategi enforcement JSON (keputusan Fase 1): json_schema constrained decoding
+ validator + retry. llama.cpp meng-compile json_schema -> grammar secara
internal sehingga struktur output dipaksa benar. Sisa kegagalan (model Q4
sesekali nyangkut loop digit -> output truncated) ditangani dengan retry maks 2x;
jika tetap gagal, response ditandai invalid untuk di-flag, BUKAN diteruskan ke
tool execution.

Menutup gap json_mode tanpa bergantung pada GBNF tulis-tangan.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent))

from llm.production_readiness_contract import (  # noqa: E402
    SYSTEM_PROMPT,
    SCHEMA_VERSION,
    validate_dcim_agent_response,
)

DEFAULT_ENDPOINT = "http://localhost:8080/completion"
DEFAULT_SCHEMA = HERE / "schemas" / "dcim_agent_response.combined.schema.json"


@dataclass
class AgentResult:
    valid: bool
    response: Optional[Dict[str, Any]]   # parsed + schema-valid payload, else None
    raw: str                             # last raw model output
    attempts: int
    errors: List[str]


def _build_prompt(context: Dict[str, Any]) -> str:
    ctx = json.dumps(context, ensure_ascii=False, indent=2, sort_keys=True)
    user = (
        f"Analisis konteks DCIM berikut dan hasilkan JSON valid sesuai {SCHEMA_VERSION}. "
        "Jangan gunakan data di luar konteks.\n\n" + ctx
    )
    # Gemma chat template
    return f"<start_of_turn>user\n{SYSTEM_PROMPT}\n\n{user}<end_of_turn>\n<start_of_turn>model\n"


def _call(endpoint: str, prompt: str, schema: Dict[str, Any],
          n_predict: int, temperature: float, timeout: int) -> str:
    payload = {
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temperature,
        "json_schema": schema,
        "cache_prompt": True,
        # repeat_penalty memutus loop digit/karakter yang khas pada model Q4 ini
        # (lihat temuan Fase 1). Wajib agar generasi tidak degenerate.
        "repeat_penalty": 1.3,
        "repeat_last_n": 128,
    }
    req = urllib.request.Request(
        endpoint, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())["content"]


def complete_json(
    prompt: str,
    schema: Dict[str, Any],
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    max_attempts: int = 3,
    n_predict: int = 512,
    base_temperature: float = 0.2,
    timeout: int = 120,
) -> Optional[Dict[str, Any]]:
    """
    Low-level: minta JSON valid (parse-able) sesuai ``schema`` dari model.

    Dipakai untuk panggilan terdekomposisi (triage scalar, tool selection) yang
    skemanya kecil sehingga model Q4 andal. Mengembalikan dict ter-parse, atau
    None jika gagal setelah retry.
    """
    for attempt in range(1, max_attempts + 1):
        temp = max(0.0, base_temperature - 0.1 * (attempt - 1))
        try:
            raw = _call(endpoint, prompt, schema, n_predict, temp, timeout)
            return json.loads(raw)
        except Exception:
            continue
    return None


def generate_agent_response(
    context: Dict[str, Any],
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    schema_path: Path = DEFAULT_SCHEMA,
    max_attempts: int = 3,
    n_predict: int = 2048,
    base_temperature: float = 0.3,
    timeout: int = 120,
) -> AgentResult:
    """
    Generate a contract-valid DCIM agent response.

    Memanggil model dengan json_schema constrained decoding, lalu memvalidasi
    dengan validate_dcim_agent_response(). Retry sampai ``max_attempts``; tiap
    retry menurunkan temperature (loop digit lebih jarang muncul saat greedy).
    """
    schema = json.loads(Path(schema_path).read_text())
    prompt = _build_prompt(context)

    last_raw = ""
    errors: List[str] = []
    for attempt in range(1, max_attempts + 1):
        # turunkan temperature tiap retry: 0.3 -> 0.1 -> 0.0
        temp = max(0.0, base_temperature - 0.2 * (attempt - 1))
        try:
            last_raw = _call(endpoint, prompt, schema, n_predict, temp, timeout)
        except Exception as exc:  # network / server
            errors.append(f"attempt {attempt}: API error: {exc}")
            continue

        vr = validate_dcim_agent_response(last_raw)
        if vr.valid:
            return AgentResult(valid=True, response=vr.raw, raw=last_raw,
                               attempts=attempt, errors=[])
        errors.append(f"attempt {attempt} (temp={temp:.1f}): {vr.errors[:2]}")

    return AgentResult(valid=False, response=None, raw=last_raw,
                       attempts=max_attempts, errors=errors)


__all__ = ["AgentResult", "generate_agent_response", "complete_json", "_build_prompt"]
