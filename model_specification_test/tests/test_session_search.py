"""
Test: Session Search

Mengukur kemampuan model untuk:
1. Memanggil tool session_search untuk mencari percakapan sebelumnya
2. Menggunakan hasil search untuk menjawab pertanyaan
3. Mengidentifikasi relevansi hasil search
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "session_search",
            "description": "Search past conversations",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "search_previous_incident",
        "prompt": "Cari percakapan sebelumnya tentang incident srv-db-01",
        "expected_tool": "session_search",
        "expected_query_keywords": ["incident", "srv-db-01"],
    },
    {
        "name": "search_solution",
        "prompt": "Cari solusi yang pernah dibahas untuk memory leak",
        "expected_tool": "session_search",
        "expected_query_keywords": ["memory", "leak", "solusi"],
    },
    {
        "name": "search_server_config",
        "prompt": "Cari informasi konfigurasi server srv-web-01 dari percakapan sebelumnya",
        "expected_tool": "session_search",
        "expected_query_keywords": ["config", "srv-web-01"],
    },
    {
        "name": "no_search_needed",
        "prompt": "Apa itu CPU?",
        "expected_tool": None,
        "expected_query_keywords": [],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all session search tests and return results."""
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

            score = _evaluate_session_search(tc, tool_calls)
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
        "capability": "session_search",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_session_search(test_case: dict, tool_calls) -> float:
    """Evaluate session search capability."""
    if tool_calls is None or len(tool_calls) == 0:
        if test_case.get("expected_tool") is None:
            return 1.0
        return 0.0

    called_tools = [tc.function.name for tc in tool_calls if hasattr(tc, 'function')]

    # Check if expected tool is called
    if test_case.get("expected_tool") not in called_tools:
        return 0.0

    score = 0.5  # Base score for calling correct tool

    # Check query quality
    for tc in tool_calls:
        if hasattr(tc, 'function') and tc.function.name == "session_search":
            try:
                import json
                args = json.loads(tc.function.arguments)
                query = args.get("query", "").lower()
                expected_keywords = test_case.get("expected_query_keywords", [])
                if expected_keywords:
                    matched = sum(1 for kw in expected_keywords if kw.lower() in query)
                    query_score = matched / len(expected_keywords)
                    score = 0.5 + (query_score * 0.5)
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
