"""
Test: Task Delegation

Mengukur kemampuan model untuk:
1. Mengidentifikasi task yang perlu didelegasikan
2. Memilih model/agent yang tepat untuk delegasi
3. Memanggil tool delegate_task dengan parameter yang benar
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "delegate_task",
            "description": "Delegate task to specialized agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "task_type": {"type": "string", "enum": ["code", "analysis", "vision", "general"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["task", "task_type"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "delegate_code_task",
        "prompt": "Buat script Python untuk monitoring server",
        "expected_tool": "delegate_task",
        "expected_task_type": "code",
        "expected_task_keywords": ["script", "python", "monitoring"],
    },
    {
        "name": "delegate_analysis_task",
        "prompt": "Analisis root cause dari incident srv-db-01",
        "expected_tool": "delegate_task",
        "expected_task_type": "analysis",
        "expected_task_keywords": ["analysis", "root cause", "incident"],
    },
    {
        "name": "delegate_vision_task",
        "prompt": "Analisis screenshot dashboard ini",
        "expected_tool": "delegate_task",
        "expected_task_type": "vision",
        "expected_task_keywords": ["analyze", "screenshot", "dashboard"],
    },
    {
        "name": "no_delegation_needed",
        "prompt": "Apa itu CPU?",
        "expected_tool": None,
        "expected_task_type": None,
        "expected_task_keywords": [],
    },
    {
        "name": "delegate_complex_task",
        "prompt": "Investigasi dan fix memory leak di srv-app-05",
        "expected_tool": "delegate_task",
        "expected_task_type": "analysis",
        "expected_task_keywords": ["investigate", "fix", "memory leak"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all delegation tests and return results."""
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

            score = _evaluate_delegation(tc, tool_calls)
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
        "capability": "delegation",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_delegation(test_case: dict, tool_calls) -> float:
    """Evaluate delegation capability."""
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
        if hasattr(tc, 'function') and tc.function.name == "delegate_task":
            try:
                import json
                args = json.loads(tc.function.arguments)

                # Check task_type
                expected_task_type = test_case.get("expected_task_type")
                if expected_task_type and args.get("task_type") == expected_task_type:
                    score += 0.25

                # Check task content
                expected_task_keywords = test_case.get("expected_task_keywords", [])
                if expected_task_keywords:
                    task = args.get("task", "").lower()
                    matched = sum(1 for kw in expected_task_keywords if kw.lower() in task)
                    task_score = matched / len(expected_task_keywords)
                    score += task_score * 0.25

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
