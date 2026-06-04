"""
Test: Agent Capabilities

Mengukur kemampuan model untuk:
1. Merencanakan langkah-langkah untuk menyelesaikan task kompleks
2. Memanggil tools secara berurutan
3. Menggabungkan hasil dari multiple tool calls
4. Memberikan final answer berdasarkan semua informasi
"""

import json
from openai import OpenAI


# Define tools for agent testing
AGENT_TOOLS = [
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
                        "items": {"type": "string"}
                    }
                },
                "required": ["hostname"]
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
                    "level": {"type": "string"}
                },
                "required": ["hostname", "time_range"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_processes",
            "description": "Get top processes by resource usage",
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string"},
                    "resource": {"type": "string", "enum": ["cpu", "memory"]}
                },
                "required": ["hostname", "resource"]
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
                    "severity": {"type": "string"},
                    "message": {"type": "string"},
                    "hostname": {"type": "string"}
                },
                "required": ["severity", "message", "hostname"]
            }
        }
    }
]


AGENT_SCENARIOS = [
    {
        "name": "investigate_slow_server",
        "prompt": "Server srv-app-05 lambat. Investigasi dan berikan rekomendasi.",
        "expected_steps": [
            "get_server_metrics",
            "get_top_processes",
            "check_logs"
        ],
        "expected_final_action": "send_alert",
        "expected_keywords": ["investigate", "process", "cpu", "memory", "recommendation"],
    },
    {
        "name": "high_cpu_alert",
        "prompt": "CPU srv-web-01 95%. Investigasi dan ambil tindakan yang diperlukan.",
        "expected_steps": [
            "get_server_metrics",
            "get_top_processes"
        ],
        "expected_final_action": "send_alert",
        "expected_keywords": ["cpu", "process", "alert", "critical"],
    },
    {
        "name": "memory_leak_investigation",
        "prompt": "Memory srv-db-01 terus naik. Investigasi kemungkinan memory leak.",
        "expected_steps": [
            "get_server_metrics",
            "get_top_processes",
            "check_logs"
        ],
        "expected_final_action": "send_alert",
        "expected_keywords": ["memory", "leak", "process", "investigate"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all agent capability tests and return results."""
    results = []
    total_score = 0
    max_score = len(AGENT_SCENARIOS)

    for scenario in AGENT_SCENARIOS:
        try:
            # Simulate agent loop
            messages = [
                {
                    "role": "system",
                    "content": "You are a DCIM agent. Investigate issues step by step, call necessary tools, and provide final recommendations."
                },
                {"role": "user", "content": scenario["prompt"]}
            ]

            # First call - model should plan and call tools
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=AGENT_TOOLS,
                tool_choice="auto",
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            message = response.choices[0].message
            tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else None

            # Evaluate planning and tool selection
            score = _evaluate_agent_scenario(scenario, tool_calls, message.content if message.content else "")
            total_score += score

            results.append({
                "test": scenario["name"],
                "score": score,
                "tool_calls": _serialize_tool_calls(tool_calls),
                "response_preview": (message.content or "")[:200],
            })

        except Exception as e:
            results.append({
                "test": scenario["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "agent",
        "score": round(final_score, 3),
        "total_tests": len(AGENT_SCENARIOS),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_agent_scenario(scenario: dict, tool_calls, content: str) -> float:
    """Evaluate agent scenario performance."""
    score = 0.0

    # Check if model called expected tools
    if tool_calls:
        called_tools = [tc.function.name for tc in tool_calls if hasattr(tc, 'function')]
        expected_steps = scenario.get("expected_steps", [])

        if expected_steps:
            matched_tools = sum(1 for tool in expected_steps if tool in called_tools)
            tool_score = matched_tools / len(expected_steps)
            score += tool_score * 0.5  # 50% weight for tool selection

    # Check if response contains expected keywords
    if content:
        content_lower = content.lower()
        expected_keywords = scenario.get("expected_keywords", [])
        if expected_keywords:
            matched_keywords = sum(1 for kw in expected_keywords if kw.lower() in content_lower)
            keyword_score = matched_keywords / len(expected_keywords)
            score += keyword_score * 0.3  # 30% weight for response quality

    # Check if model provided reasoning/plan
    if content and len(content) > 50:
        score += 0.2  # 20% weight for providing explanation

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
