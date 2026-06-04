"""
Test: Skills Management

Mengukur kemampuan model untuk:
1. Memanggil tool skills_list untuk melihat skills yang tersedia
2. Memanggil tool skills_view untuk melihat detail skill
3. Menggunakan skill yang tepat untuk task
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "skills_list",
            "description": "List all available skills",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "skills_view",
            "description": "View details of a specific skill",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_id": {"type": "string"}
                },
                "required": ["skill_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "skills_execute",
            "description": "Execute a skill",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_id": {"type": "string"},
                    "parameters": {"type": "object"}
                },
                "required": ["skill_id"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "list_available_skills",
        "prompt": "Apa saja skills yang tersedia?",
        "expected_tool": "skills_list",
        "expected_parameters": {},
    },
    {
        "name": "view_skill_detail",
        "prompt": "Tampilkan detail skill cpu_troubleshooting",
        "expected_tool": "skills_view",
        "expected_skill_id": "cpu_troubleshooting",
    },
    {
        "name": "execute_skill",
        "prompt": "Jalankan skill memory_leak_detection untuk server srv-app-05",
        "expected_tool": "skills_execute",
        "expected_skill_id": "memory_leak_detection",
        "expected_parameters_keywords": ["srv-app-05"],
    },
    {
        "name": "find_relevant_skill",
        "prompt": "Skill apa yang cocok untuk troubleshooting CPU tinggi?",
        "expected_tool": "skills_list",
        "expected_parameters": {},
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all skills management tests and return results."""
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

            score = _evaluate_skills(tc, tool_calls)
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
        "capability": "skills",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_skills(test_case: dict, tool_calls) -> float:
    """Evaluate skills management capability."""
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

                # Check skill_id
                expected_skill_id = test_case.get("expected_skill_id")
                if expected_skill_id and args.get("skill_id") == expected_skill_id:
                    score += 0.25

                # Check parameters
                expected_parameters_keywords = test_case.get("expected_parameters_keywords", [])
                if expected_parameters_keywords:
                    params_str = str(args.get("parameters", {})).lower()
                    matched = sum(1 for kw in expected_parameters_keywords if kw.lower() in params_str)
                    param_score = matched / len(expected_parameters_keywords)
                    score += param_score * 0.25

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
