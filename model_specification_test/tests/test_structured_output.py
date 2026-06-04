"""
Test: Structured Output

Mengukur kemampuan model untuk:
1. Menghasilkan output sesuai format yang diminta
2. Mematuhi struktur yang ditentukan
3. Mengisi semua field yang diperlukan
"""

import json
import re
from openai import OpenAI


TEST_CASES = [
    {
        "name": "server_status_report",
        "prompt": "Buat laporan status server dalam format:\nSERVER: <hostname>\nCPU: <percentage>%\nMEMORY: <percentage>%\nSTATUS: <normal|warning|critical>\nRECOMMENDATION: <text>\n\nData: srv-web-01, CPU 85%, Memory 72%",
        "expected_sections": ["SERVER", "CPU", "MEMORY", "STATUS", "RECOMMENDATION"],
        "expected_values": {"SERVER": "srv-web-01"},
    },
    {
        "name": "incident_report",
        "prompt": "Buat incident report format:\n- Incident ID: <id>\n- Severity: <level>\n- Affected Server: <hostname>\n- Root Cause: <text>\n- Resolution: <text>\n\nData: INC-001, critical, srv-db-01, memory leak, restart service",
        "expected_sections": ["Incident ID", "Severity", "Affected Server", "Root Cause", "Resolution"],
        "expected_values": {"Incident ID": "INC-001", "Severity": "critical"},
    },
    {
        "name": "metrics_table",
        "prompt": "Buat tabel metrics dengan kolom: Server | CPU | Memory | Disk | Status\nData:\nsrv-web-01: CPU 45%, Memory 60%, Disk 30%, normal\nsrv-web-02: CPU 80%, Memory 75%, Disk 50%, warning\nsrv-db-01: CPU 90%, Memory 88%, Disk 70%, critical",
        "expected_sections": ["Server", "CPU", "Memory", "Disk", "Status"],
        "expected_values": None,
    },
    {
        "name": "yaml_output",
        "prompt": "Output dalam format YAML:\nserver:\n  hostname: <hostname>\n  metrics:\n    cpu: <number>\n    memory: <number>\n  alerts:\n    - type: <type>\n      severity: <level>\n\nData: srv-app-05, cpu=95, memory=80, alerts=[{type: cpu_high, severity: critical}]",
        "expected_sections": ["server", "hostname", "metrics", "cpu", "memory", "alerts"],
        "expected_values": {"hostname": "srv-app-05"},
    },
    {
        "name": "csv_output",
        "prompt": "Output dalam format CSV dengan header: hostname,cpu,memory,disk,status\nData:\nsrv-web-01,45,60,30,normal\nsrv-web-02,80,75,50,warning\nsrv-db-01,90,88,70,critical",
        "expected_sections": ["hostname", "cpu", "memory", "disk", "status"],
        "expected_values": None,
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all structured output tests and return results."""
    results = []
    total_score = 0
    max_score = len(TEST_CASES)

    for tc in TEST_CASES:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Follow the exact format requested."
                    },
                    {"role": "user", "content": tc["prompt"]}
                ],
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            content = response.choices[0].message.content.strip()
            score = _evaluate_structured_output(tc, content)
            total_score += score

            results.append({
                "test": tc["name"],
                "score": score,
                "output_preview": content[:200] if content else "",
            })

        except Exception as e:
            results.append({
                "test": tc["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "structured_output",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_structured_output(test_case: dict, content: str) -> float:
    """Evaluate structured output quality."""
    score = 0.0

    # Check expected sections/fields exist
    expected_sections = test_case.get("expected_sections", [])
    if expected_sections:
        matched_sections = 0
        for section in expected_sections:
            # Case-insensitive search
            if re.search(re.escape(section), content, re.IGNORECASE):
                matched_sections += 1
        section_score = matched_sections / len(expected_sections)
        score += section_score * 0.6  # 60% weight for structure

    # Check expected values
    expected_values = test_case.get("expected_values")
    if expected_values:
        matched_values = 0
        total_values = len(expected_values)
        for key, value in expected_values.items():
            if re.search(re.escape(value), content, re.IGNORECASE):
                matched_values += 1
        value_score = matched_values / total_values if total_values > 0 else 1.0
        score += value_score * 0.4  # 40% weight for value accuracy

    return min(score, 1.0)
