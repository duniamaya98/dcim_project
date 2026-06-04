"""
Test: File Operations

Mengukur kemampuan model untuk:
1. Memanggil tool file_read untuk membaca file
2. Memanggil tool file_write untuk menulis file
3. Memanggil tool file_search untuk mencari pattern
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "file_read",
            "description": "Read file contents",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "lines": {"type": "integer"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_write",
            "description": "Write content to file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                    "mode": {"type": "string", "enum": ["write", "append"]}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_search",
            "description": "Search for pattern in file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "pattern": {"type": "string"},
                    "regex": {"type": "boolean"}
                },
                "required": ["path", "pattern"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "read_log_file",
        "prompt": "Baca file /var/log/syslog",
        "expected_tool": "file_read",
        "expected_path": "/var/log/syslog",
    },
    {
        "name": "read_last_lines",
        "prompt": "Baca 100 baris terakhir dari /var/log/nginx/error.log",
        "expected_tool": "file_read",
        "expected_path": "/var/log/nginx/error.log",
        "expected_lines": 100,
    },
    {
        "name": "write_config",
        "prompt": "Tulis konfigurasi nginx ke /etc/nginx/nginx.conf",
        "expected_tool": "file_write",
        "expected_path": "/etc/nginx/nginx.conf",
    },
    {
        "name": "search_error_pattern",
        "prompt": "Cari pattern 'ERROR' di file /var/log/app.log",
        "expected_tool": "file_search",
        "expected_path": "/var/log/app.log",
        "expected_pattern": "ERROR",
    },
    {
        "name": "search_regex",
        "prompt": "Cari semua IP address di file /var/log/access.log menggunakan regex",
        "expected_tool": "file_search",
        "expected_path": "/var/log/access.log",
        "expected_regex": True,
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all file operation tests and return results."""
    results = []
    total_score = 0
    max_score = len(TEST_CASES)

    for tc in TEST_CASES:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": tc["prompt"]}],
                tools=TOOLS,
                tool_choice="auto",
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            message = response.choices[0].message
            tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else None

            score = _evaluate_file_ops(tc, tool_calls)
            total_score += score

            results.append({
                "test": tc["name"],
                "score": score,
                "tool_calls": _serialize_tool_calls(tool_calls),
            })

        except Exception as e:
            results.append({
                "test": tc["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "file_operations",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_file_ops(test_case: dict, tool_calls) -> float:
    """Evaluate file operation capability."""
    if tool_calls is None or len(tool_calls) == 0:
        return 0.0

    called_tools = [tc.function.name for tc in tool_calls if hasattr(tc, 'function')]

    # Check if expected tool is called
    if test_case.get("expected_tool") not in called_tools:
        return 0.0

    score = 0.5  # Base score for calling correct tool

    # Check parameters
    for tc in tool_calls:
        if hasattr(tc, 'function'):
            try:
                import json
                args = json.loads(tc.function.arguments)

                # Check path
                expected_path = test_case.get("expected_path")
                if expected_path and expected_path in args.get("path", ""):
                    score += 0.2

                # Check lines parameter
                expected_lines = test_case.get("expected_lines")
                if expected_lines and args.get("lines") == expected_lines:
                    score += 0.15

                # Check pattern
                expected_pattern = test_case.get("expected_pattern")
                if expected_pattern and expected_pattern in args.get("pattern", ""):
                    score += 0.15

                # Check regex flag
                expected_regex = test_case.get("expected_regex")
                if expected_regex and args.get("regex") == True:
                    score += 0.15

            except:
                pass

    return min(score, 1.0)


def _serialize_tool_calls(tool_calls) -> list:
    """Serialize tool calls for JSON output."""
    if not tool_calls:
        return []
    result = []
    for tc in tool_calls:
        if hasattr(tc, 'function'):
            result.append({
                "name": tc.function.name,
                "arguments": tc.function.arguments,
            })
    return result
