"""
Test: Web Search & Scraping

Mengukur kemampuan model untuk:
1. Memanggil tool web_search dengan query yang tepat
2. Memanggil tool web_extract dengan URL yang benar
3. Menggunakan hasil search untuk menjawab pertanyaan
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_extract",
            "description": "Extract content from a webpage",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "selector": {"type": "string"}
                },
                "required": ["url"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "search_documentation",
        "prompt": "Cari dokumentasi nginx error 502 bad gateway",
        "expected_tool": "web_search",
        "expected_query_keywords": ["nginx", "502", "bad gateway"],
    },
    {
        "name": "search_solution",
        "prompt": "Bagaimana cara fix memory leak di Java application? Cari solusinya.",
        "expected_tool": "web_search",
        "expected_query_keywords": ["memory", "leak", "java", "fix"],
    },
    {
        "name": "extract_specific_url",
        "prompt": "Extract konten dari https://docs.nginx.com/nginx/admin-guide/monitoring/debugging/",
        "expected_tool": "web_extract",
        "expected_url": "https://docs.nginx.com",
    },
    {
        "name": "search_and_extract",
        "prompt": "Cari informasi tentang Linux OOM killer, lalu extract dari dokumentasi kernel.org",
        "expected_tools": ["web_search", "web_extract"],
        "expected_query_keywords": ["oom", "killer", "linux"],
    },
    {
        "name": "no_search_needed",
        "prompt": "Apa itu CPU?",
        "expected_tool": None,
        "expected_query_keywords": [],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all web search tests and return results."""
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

            score = _evaluate_web_search(tc, tool_calls)
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
        "capability": "web_search",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_web_search(test_case: dict, tool_calls) -> float:
    """Evaluate web search capability."""
    if tool_calls is None or len(tool_calls) == 0:
        if test_case.get("expected_tool") is None:
            return 1.0
        return 0.0

    called_tools = [tc.function.name for tc in tool_calls if hasattr(tc, 'function')]

    # Check if expected tool is called
    if "expected_tool" in test_case and test_case["expected_tool"]:
        if test_case["expected_tool"] not in called_tools:
            return 0.0

    # Check if expected tools are called
    if "expected_tools" in test_case:
        matched = sum(1 for t in test_case["expected_tools"] if t in called_tools)
        if matched == 0:
            return 0.0

    # Check query quality
    score = 0.5  # Base score for calling correct tool

    for tc in tool_calls:
        if hasattr(tc, 'function') and tc.function.name == "web_search":
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
