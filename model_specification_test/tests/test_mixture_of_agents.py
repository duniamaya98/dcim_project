"""
Test: Mixture of Agents

Mengukur kemampuan model untuk:
1. Mengidentifikasi kapan perlu menggunakan multiple agents
2. Memilih agent yang tepat untuk task
3. Mengkoordinasikan hasil dari multiple agents
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "mixture_of_agents",
            "description": "Use multiple specialized agents for complex tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "agents": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["code", "analysis", "vision", "general"]}
                    }
                },
                "required": ["task", "agents"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "complex_investigation",
        "prompt": "Investigasi incident kompleks: server down, database error, dan network issue. Gunakan multiple agents.",
        "expected_tool": "mixture_of_agents",
        "expected_agents": ["code", "analysis", "general"],
    },
    {
        "name": "multi_domain_analysis",
        "prompt": "Analisis masalah yang melibatkan multiple domain: application, database, dan infrastructure",
        "expected_tool": "mixture_of_agents",
        "expected_agents": ["code", "analysis", "general"],
    },
    {
        "name": "code_and_vision",
        "prompt": "Analisis screenshot error dan generate fix code",
        "expected_tool": "mixture_of_agents",
        "expected_agents": ["code", "vision"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all mixture of agents tests and return results."""
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

            score = _evaluate_mixture(tc, tool_calls)
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
        "capability": "mixture_of_agents",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_mixture(test_case: dict, tool_calls) -> float:
    """Evaluate mixture of agents capability."""
    if tool_calls is None or len(tool_calls) == 0:
        return 0.0

    called_tools = [tc.function.name for tc in tool_calls if hasattr(tc, 'function')]

    # Check if expected tool is called
    if test_case.get("expected_tool") not in called_tools:
        return 0.0

    score = 0.5  # Base score for calling correct tool

    # Check parameters
    for tc in tool_calls:
        if hasattr(tc, 'function') and tc.function.name == "mixture_of_agents":
            try:
                import json
                args = json.loads(tc.function.arguments)

                # Check agents
                expected_agents = test_case.get("expected_agents", [])
                actual_agents = args.get("agents", [])
                if expected_agents:
                    matched = sum(1 for agent in expected_agents if agent in actual_agents)
                    agent_score = matched / len(expected_agents)
                    score += agent_score * 0.5

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
