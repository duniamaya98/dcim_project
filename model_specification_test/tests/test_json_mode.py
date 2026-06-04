"""
Test: JSON Mode

Mengukur kemampuan model untuk:
1. Menghasilkan output JSON yang valid
2. Mematuhi schema yang diminta
3. Mengisi field dengan benar
"""

import json
import re
from openai import OpenAI


TEST_CASES = [
    {
        "name": "simple_json",
        "prompt": "Output server status sebagai JSON: hostname=srv-web-01, cpu=85, memory=72, status=warning",
        "expected_fields": ["hostname", "cpu", "memory", "status"],
        "expected_values": {"hostname": "srv-web-01", "status": "warning"},
    },
    {
        "name": "nested_json",
        "prompt": "Output sebagai JSON: server srv-db-01 dengan metrics {cpu: 90, memory: 88} dan anomalies [{type: memory_leak, severity: high}]",
        "expected_fields": ["server", "metrics", "anomalies"],
        "expected_values": {"server": "srv-db-01"},
    },
    {
        "name": "array_json",
        "prompt": "Output sebagai JSON array: 3 server dengan hostname, cpu, memory. srv-web-01 (cpu:45, mem:60), srv-web-02 (cpu:80, mem:75), srv-db-01 (cpu:90, mem:88)",
        "expected_fields": ["hostname", "cpu", "memory"],
        "expected_values": None,
        "is_array": True,
    },
    {
        "name": "schema_compliance",
        "prompt": "Output JSON sesuai schema: {hostname: string, metrics: {cpu: number, memory: number}, alerts: array of {type: string, severity: string}}. Data: srv-app-05, cpu=95, memory=80, alerts=[{type: cpu_high, severity: critical}]",
        "expected_fields": ["hostname", "metrics", "alerts"],
        "expected_values": {"hostname": "srv-app-05"},
    },
    {
        "name": "json_with_explanation",
        "prompt": "Jelaskan kondisi server srv-web-01 (cpu: 95%, memory: 88%) dalam format JSON dengan fields: summary, metrics, recommendations",
        "expected_fields": ["summary", "metrics", "recommendations"],
        "expected_values": None,
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all JSON mode tests and return results."""
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
                        "content": "You are a helpful assistant. Always respond with valid JSON only. No markdown, no explanation outside JSON."
                    },
                    {"role": "user", "content": tc["prompt"]}
                ],
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            content = response.choices[0].message.content.strip()
            score = _evaluate_json_output(tc, content)
            total_score += score

            results.append({
                "test": tc["name"],
                "score": score,
                "output_preview": content[:200] if content else "",
                "is_valid_json": _is_valid_json(content),
            })

        except Exception as e:
            results.append({
                "test": tc["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "json_mode",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _is_valid_json(text: str) -> bool:
    """Check if text is valid JSON."""
    try:
        # Try to extract JSON from markdown code blocks
        if "```" in text:
            match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
            if match:
                text = match.group(1)
        json.loads(text)
        return True
    except:
        return False


def _extract_json(text: str) -> dict | list | None:
    """Extract JSON from text."""
    try:
        if "```" in text:
            match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
            if match:
                text = match.group(1)
        return json.loads(text)
    except:
        return None


def _evaluate_json_output(test_case: dict, content: str) -> float:
    """Evaluate JSON output quality."""
    # Check if valid JSON
    if not _is_valid_json(content):
        return 0.0

    data = _extract_json(content)
    if data is None:
        return 0.0

    score = 0.0

    # Check expected fields exist
    expected_fields = test_case.get("expected_fields", [])
    if expected_fields:
        if isinstance(data, list):
            # For array, check first element
            if len(data) > 0:
                data = data[0]
            else:
                return 0.0

        matched_fields = sum(1 for f in expected_fields if f in data)
        field_score = matched_fields / len(expected_fields)
        score += field_score * 0.6  # 60% weight for field presence

    # Check expected values
    expected_values = test_case.get("expected_values")
    if expected_values:
        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        matched_values = 0
        total_values = len(expected_values)
        for key, value in expected_values.items():
            if key in data:
                # Case-insensitive string comparison
                if isinstance(data[key], str) and isinstance(value, str):
                    if value.lower() in data[key].lower():
                        matched_values += 1
                elif data[key] == value:
                    matched_values += 1

        value_score = matched_values / total_values if total_values > 0 else 1.0
        score += value_score * 0.4  # 40% weight for value accuracy

    return min(score, 1.0)
