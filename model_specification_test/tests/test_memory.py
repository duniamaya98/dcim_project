"""
Test: Memory (Persistent Memory)

Mengukur kemampuan model untuk:
1. Memanggil tool memory_store untuk menyimpan informasi
2. Memanggil tool memory_recall untuk mengambil informasi
3. Menggunakan informasi yang disimpan untuk menjawab pertanyaan
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "memory_store",
            "description": "Store information in persistent memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_recall",
            "description": "Recall information from persistent memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"}
                },
                "required": ["key"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "store_server_config",
        "prompt": "Simpan informasi: server srv-web-01 punya IP 192.168.1.10 dan role web server",
        "expected_tool": "memory_store",
        "expected_key_keywords": ["srv-web-01", "server", "config"],
        "expected_value_keywords": ["192.168.1.10", "web"],
    },
    {
        "name": "recall_stored_info",
        "prompt": "Apa IP address server srv-web-01?",
        "expected_tool": "memory_recall",
        "expected_key_keywords": ["srv-web-01"],
    },
    {
        "name": "store_incident",
        "prompt": "Catat incident: INC-001, server srv-db-01, memory leak, resolved by restart",
        "expected_tool": "memory_store",
        "expected_key_keywords": ["INC-001", "incident"],
        "expected_value_keywords": ["srv-db-01", "memory", "leak", "restart"],
    },
    {
        "name": "recall_incident",
        "prompt": "Cari informasi tentang incident INC-001",
        "expected_tool": "memory_recall",
        "expected_key_keywords": ["INC-001"],
    },
    {
        "name": "no_memory_needed",
        "prompt": "Apa itu CPU?",
        "expected_tool": None,
        "expected_key_keywords": [],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all memory tests and return results."""
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

            score = _evaluate_memory(tc, tool_calls)
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
        "capability": "memory",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_memory(test_case: dict, tool_calls) -> float:
    """Evaluate memory capability."""
    if tool_calls is None or len(tool_calls) == 0:
        if test_case.get("expected_tool") is None:
            return 1.0
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

                # Check key
                expected_key_keywords = test_case.get("expected_key_keywords", [])
                if expected_key_keywords:
                    key = args.get("key", "").lower()
                    matched = sum(1 for kw in expected_key_keywords if kw.lower() in key)
                    key_score = matched / len(expected_key_keywords)
                    score += key_score * 0.25

                # Check value (for store operations)
                expected_value_keywords = test_case.get("expected_value_keywords", [])
                if expected_value_keywords:
                    value = args.get("value", "").lower()
                    matched = sum(1 for kw in expected_value_keywords if kw.lower() in value)
                    value_score = matched / len(expected_value_keywords)
                    score += value_score * 0.25

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
