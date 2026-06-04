"""
Test: Context Engine

Mengukur kemampuan model untuk:
1. Memanggil tool set_context untuk mengubah context
2. Menggunakan context yang tepat untuk task
3. Memahami perbedaan context (monitoring vs troubleshooting vs deployment)
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "set_context",
            "description": "Set active context and load relevant tools",
            "parameters": {
                "type": "object",
                "properties": {
                    "context_name": {"type": "string", "enum": ["monitoring", "troubleshooting", "deployment", "general"]}
                },
                "required": ["context_name"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "monitoring_context",
        "prompt": "Saya ingin monitoring server secara real-time",
        "expected_tool": "set_context",
        "expected_context": "monitoring",
    },
    {
        "name": "troubleshooting_context",
        "prompt": "Server bermasalah, saya perlu troubleshoot",
        "expected_tool": "set_context",
        "expected_context": "troubleshooting",
    },
    {
        "name": "deployment_context",
        "prompt": "Saya akan deploy aplikasi baru",
        "expected_tool": "set_context",
        "expected_context": "deployment",
    },
    {
        "name": "general_context",
        "prompt": "Saya butuh bantuan umum",
        "expected_tool": "set_context",
        "expected_context": "general",
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all context engine tests and return results."""
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

            score = _evaluate_context(tc, tool_calls)
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
        "capability": "context_engine",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_context(test_case: dict, tool_calls) -> float:
    """Evaluate context engine capability."""
    if tool_calls is None or len(tool_calls) == 0:
        return 0.0

    called_tools = [tc.function.name for tc in tool_calls if hasattr(tc, 'function')]

    # Check if expected tool is called
    if test_case.get("expected_tool") not in called_tools:
        return 0.0

    score = 0.5  # Base score for calling correct tool

    # Check parameters
    for tc in tool_calls:
        if hasattr(tc, 'function') and tc.function.name == "set_context":
            try:
                import json
                args = json.loads(tc.function.arguments)

                # Check context_name
                expected_context = test_case.get("expected_context")
                if expected_context and args.get("context_name") == expected_context:
                    score += 0.5

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
