"""
Test: Tool Calling / Function Calling

Mengukur kemampuan model untuk:
1. Memanggil fungsi yang benar berdasarkan konteks
2. Mengisi parameter dengan akurat
3. Menghasilkan syntax function call yang valid
"""

import json
import re
from openai import OpenAI


def get_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=api_key)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_server_metrics",
            "description": "Get current server metrics",
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string"},
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "enum": ["cpu", "memory", "disk", "network"]
                    }
                },
                "required": ["hostname"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_alert",
            "description": "Send alert to operations team",
            "parameters": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "message": {"type": "string"},
                    "hostname": {"type": "string"}
                },
                "required": ["severity", "message", "hostname"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_logs",
            "description": "Check server logs for errors",
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string"},
                    "time_range": {"type": "string"},
                    "level": {"type": "string", "enum": ["error", "warning", "info"]}
                },
                "required": ["hostname", "time_range"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "single_tool_call",
        "prompt": "Cek CPU usage server srv-web-01",
        "expected_tool": "get_server_metrics",
        "expected_params": {"hostname": "srv-web-01"},
        "required_keys": ["hostname"],
    },
    {
        "name": "alert_tool_call",
        "prompt": "Kirim alert critical ke tim: server srv-db-01 down",
        "expected_tool": "send_alert",
        "expected_params": {"severity": "critical", "hostname": "srv-db-01"},
        "required_keys": ["severity", "message", "hostname"],
    },
    {
        "name": "log_check_tool_call",
        "prompt": "Cek error logs server srv-app-05 dalam 1 jam terakhir",
        "expected_tool": "check_logs",
        "expected_params": {"hostname": "srv-app-05", "level": "error"},
        "required_keys": ["hostname", "time_range"],
    },
    {
        "name": "multi_tool_selection",
        "prompt": "Server srv-web-03 lambat, cek metrics dan logs",
        "expected_tools": ["get_server_metrics", "check_logs"],
        "expected_params": {"hostname": "srv-web-03"},
        "required_keys": ["hostname"],
    },
    {
        "name": "no_tool_needed",
        "prompt": "Apa itu CPU?",
        "expected_tool": None,
        "expected_params": {},
        "required_keys": [],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all tool calling tests and return results."""
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

            score = _evaluate_tool_call(tc, tool_calls)
            total_score += score

            results.append({
                "test": tc["name"],
                "score": score,
                "tool_calls": _serialize_tool_calls(tool_calls),
                "expected": tc.get("expected_tool", tc.get("expected_tools")),
            })

        except Exception as e:
            results.append({
                "test": tc["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "tool_calling",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_tool_call(test_case: dict, tool_calls) -> float:
    """Evaluate tool calling accuracy."""
    if tool_calls is None or len(tool_calls) == 0:
        if test_case.get("expected_tool") is None:
            return 1.0  # Correctly no tool call
        return 0.0

    # Check if expected tool is called
    called_tools = []
    for tc in tool_calls:
        if hasattr(tc, 'function'):
            called_tools.append(tc.function.name)

    # Single tool expected
    if "expected_tool" in test_case and test_case["expected_tool"]:
        if test_case["expected_tool"] in called_tools:
            # Check parameters
            for tc in tool_calls:
                if hasattr(tc, 'function') and tc.function.name == test_case["expected_tool"]:
                    try:
                        args = json.loads(tc.function.arguments)
                        required_keys = test_case.get("required_keys", [])
                        matched = sum(1 for k in required_keys if k in args)
                        return matched / len(required_keys) if required_keys else 1.0
                    except:
                        return 0.5
            return 0.5
        return 0.0

    # Multiple tools expected
    if "expected_tools" in test_case:
        matched = sum(1 for t in test_case["expected_tools"] if t in called_tools)
        return matched / len(test_case["expected_tools"])

    return 0.5


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
