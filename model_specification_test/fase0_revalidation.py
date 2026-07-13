"""
Fase 0 - Re-validasi capability test (raw output, bukan paste markdown).

Target capability yang di-retest sesuai PRE_EXECUTION_CHECKLIST Fase 0:
  - json_mode      : validasi raw output dengan json.loads (setara `jq`)
  - multiturn      : cek fabrikasi data / retensi konteks
  - memory         : cek penyimpanan fakta via tool call
  - context_engine : cek capability benar (bukan tertukar dengan skills)

Menjalankan langsung ke model live di endpoint llama.cpp.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent))

from tests import test_json_mode, test_multiturn, test_memory, test_context_engine

BASE_URL = "http://localhost:8080/v1"
API_KEY = "not-needed"
MODEL = "unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL"

TEST_CONFIG = {"timeout": 60, "temperature": 0.3, "max_tokens": 1024}

PASS_THRESHOLD = 0.60  # samakan dengan rubrik scoring


def strict_json_probe(client):
    """jq-equivalent: ambil raw output json_mode dan coba json.loads tanpa toleransi."""
    rows = []
    for tc in test_json_mode.TEST_CASES:
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Always respond with valid JSON only. No markdown, no explanation outside JSON."},
                    {"role": "user", "content": tc["prompt"]},
                ],
                temperature=TEST_CONFIG["temperature"],
                max_tokens=TEST_CONFIG["max_tokens"],
            )
            raw = resp.choices[0].message.content or ""
            stripped = raw.strip()
            # strict: tanpa ekstraksi code-fence
            try:
                json.loads(stripped)
                strict_ok = True
                err = ""
            except Exception as e:
                strict_ok = False
                err = str(e)
            rows.append({"test": tc["name"], "strict_valid": strict_ok, "error": err, "raw": raw})
        except Exception as e:
            rows.append({"test": tc["name"], "strict_valid": False, "error": f"API: {e}", "raw": ""})
    return rows


def main():
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

    print(f"Model : {MODEL}")
    print(f"Endpoint: {BASE_URL}\n")

    suites = [
        ("json_mode", test_json_mode),
        ("multiturn", test_multiturn),
        ("memory", test_memory),
        ("context_engine", test_context_engine),
    ]

    results = {}
    for name, mod in suites:
        print(f"== {name} ==")
        try:
            r = mod.run_test(client, MODEL, TEST_CONFIG)
        except Exception as e:
            print(f"  ERROR: {e}\n")
            results[name] = {"score": 0.0, "error": str(e), "results": []}
            continue
        score = r.get("score", 0.0)
        verdict = "PASS" if score >= PASS_THRESHOLD else "FAIL"
        print(f"  score={score:.3f}  [{verdict}]  passed={r.get('passed')}/{r.get('total_tests')}")
        for sub in r.get("results", []):
            line = f"    - {sub.get('test'):28s} {sub.get('score', 0):.2f}"
            if "is_valid_json" in sub:
                line += f"  valid_json={sub['is_valid_json']}"
            if sub.get("tool_calls"):
                line += f"  tools={[t['name'] for t in sub['tool_calls']]}"
            if sub.get("error"):
                line += f"  ERR={sub['error'][:60]}"
            print(line)
        results[name] = r
        print()

    # strict json probe (jq-equivalent)
    print("== json_mode STRICT probe (jq-equivalent, no code-fence extraction) ==")
    strict = strict_json_probe(client)
    strict_pass = sum(1 for s in strict if s["strict_valid"])
    for s in strict:
        print(f"    - {s['test']:28s} strict_valid={s['strict_valid']}" + (f"  {s['error'][:50]}" if s["error"] else ""))
    print(f"  strict valid: {strict_pass}/{len(strict)}\n")

    # write report
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(__file__).parent / "results" / "fase0"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / f"fase0_revalidation_{ts}.md"
    raw_dump = out_dir / f"fase0_raw_{ts}.json"

    lines = ["# Fase 0 - Re-validasi Capability", "",
             f"- Model: `{MODEL}`", f"- Endpoint: `{BASE_URL}`",
             f"- Waktu: {ts}", f"- Pass threshold: {PASS_THRESHOLD}", "",
             "## Hasil", "", "| Capability | Score | Verdict | Passed | Catatan re-test |",
             "|---|---:|---|---|---|"]
    notes = {
        "json_mode": "Sebelumnya L0 karena escape markdown saat paste. Re-test pakai raw API.",
        "multiturn": "Sebelumnya L1 karena fabrikasi srv-db-01. Cek retensi konteks asli.",
        "memory": "Sebelumnya L1 karena fakta tidak tersimpan. Cek tool memory_store/recall.",
        "context_engine": "Sebelumnya L0 karena output tertukar dengan skills. Cek set_context.",
    }
    for name, _ in suites:
        r = results.get(name, {})
        sc = r.get("score", 0.0)
        verdict = "PASS" if sc >= PASS_THRESHOLD else "FAIL"
        lines.append(f"| {name} | {sc:.3f} | {verdict} | {r.get('passed','-')}/{r.get('total_tests','-')} | {notes.get(name,'')} |")
    lines += ["", "## json_mode strict (jq-equivalent)", "",
              f"Raw output valid JSON tanpa ekstraksi code-fence: **{strict_pass}/{len(strict)}**", "",
              "| Test | strict_valid | error |", "|---|---|---|"]
    for s in strict:
        lines.append(f"| {s['test']} | {s['strict_valid']} | {s['error'][:60]} |")

    report.write_text("\n".join(lines))
    raw_dump.write_text(json.dumps({"suites": results, "strict_json": strict}, indent=2, default=str))
    print(f"Report : {report}")
    print(f"Raw    : {raw_dump}")


if __name__ == "__main__":
    main()
