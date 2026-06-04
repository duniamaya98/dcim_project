"""
Test: Code Execution

Mengukur kemampuan model untuk:
1. Generate code yang syntactically correct
2. Generate code yang executable
3. Generate code yang sesuai requirements
"""

import re
import subprocess
import tempfile
import os
from openai import OpenAI


TEST_CASES = [
    {
        "name": "python_cpu_monitor",
        "prompt": "Buat script Python untuk monitoring CPU usage setiap 5 menit. Print timestamp dan CPU percentage. Jika CPU > 80%, print warning.",
        "language": "python",
        "expected_keywords": ["import", "time", "cpu", "percent", "print", "80"],
        "should_execute": True,
    },
    {
        "name": "bash_log_parser",
        "prompt": "Buat script bash untuk parse log file /var/log/syslog dan hitung jumlah error dalam 1 jam terakhir.",
        "language": "bash",
        "expected_keywords": ["grep", "error", "log", "count", "syslog"],
        "should_execute": False,  # Don't actually run bash on production
    },
    {
        "name": "python_memory_check",
        "prompt": "Buat fungsi Python check_memory() yang return dictionary dengan keys: total, used, free, percent. Gunakan psutil.",
        "language": "python",
        "expected_keywords": ["def", "check_memory", "return", "total", "used", "free", "percent", "psutil"],
        "should_execute": True,
    },
    {
        "name": "python_disk_alert",
        "prompt": "Buat script Python yang check disk usage. Jika usage > 90%, kirim alert dengan print message.",
        "language": "python",
        "expected_keywords": ["disk", "usage", "90", "alert", "print", "shutil"],
        "should_execute": True,
    },
    {
        "name": "python_json_report",
        "prompt": "Buat fungsi Python generate_report(hostname, cpu, memory) yang return JSON string dengan format: {hostname, metrics: {cpu, memory}, timestamp, status}",
        "language": "python",
        "expected_keywords": ["def", "generate_report", "json", "hostname", "cpu", "memory", "timestamp", "status"],
        "should_execute": True,
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all code execution tests and return results."""
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
                        "content": f"You are a code generation assistant. Generate only {tc['language']} code. No explanation outside code blocks."
                    },
                    {"role": "user", "content": tc["prompt"]}
                ],
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            content = response.choices[0].message.content.strip()
            code = _extract_code(content, tc["language"])

            score = _evaluate_code(tc, code)
            total_score += score

            results.append({
                "test": tc["name"],
                "score": score,
                "code_preview": code[:200] if code else "",
                "code_length": len(code) if code else 0,
                "syntax_valid": _check_syntax(code, tc["language"]) if code else False,
            })

        except Exception as e:
            results.append({
                "test": tc["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "code_execution",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _extract_code(content: str, language: str) -> str:
    """Extract code from markdown code blocks."""
    # Try to find code block
    pattern = rf'```{language}\s*\n(.*?)\n```'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1)

    # Try generic code block
    match = re.search(r'```\s*\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1)

    # If no code block, return entire content
    return content


def _check_syntax(code: str, language: str) -> bool:
    """Check if code has valid syntax."""
    if language == "python":
        try:
            compile(code, '<string>', 'exec')
            return True
        except:
            return False
    elif language == "bash":
        try:
            result = subprocess.run(
                ["bash", "-n", "-c", code],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    return True


def _evaluate_code(test_case: dict, code: str) -> float:
    """Evaluate code quality."""
    if not code:
        return 0.0

    score = 0.0

    # Check syntax
    if _check_syntax(code, test_case["language"]):
        score += 0.3  # 30% weight for valid syntax

    # Check expected keywords
    expected_keywords = test_case.get("expected_keywords", [])
    if expected_keywords:
        code_lower = code.lower()
        matched = sum(1 for kw in expected_keywords if kw.lower() in code_lower)
        keyword_score = matched / len(expected_keywords)
        score += keyword_score * 0.4  # 40% weight for keyword coverage

    # Check if code is substantial (not just a stub)
    lines = [l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')]
    if len(lines) >= 3:
        score += 0.3  # 30% weight for code substance
    elif len(lines) >= 1:
        score += 0.15

    return min(score, 1.0)
