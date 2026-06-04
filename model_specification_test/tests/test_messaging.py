"""
Test: Cross-Platform Messaging

Mengukur kemampuan model untuk:
1. Memanggil tool send_message untuk mengirim pesan
2. Memilih platform yang tepat (Slack, Telegram, Discord, Email)
3. Menyusun pesan dengan format yang sesuai
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Send message to a platform",
            "parameters": {
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "enum": ["slack", "telegram", "discord", "email"]},
                    "channel": {"type": "string"},
                    "message": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                },
                "required": ["platform", "channel", "message"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "send_slack_alert",
        "prompt": "Kirim alert ke Slack channel #ops-alerts: server srv-web-01 down",
        "expected_tool": "send_message",
        "expected_platform": "slack",
        "expected_channel": "#ops-alerts",
        "expected_message_keywords": ["srv-web-01", "down", "alert"],
    },
    {
        "name": "send_telegram_notification",
        "prompt": "Kirim notifikasi ke Telegram chat ID 123456789: CPU usage tinggi di srv-db-01",
        "expected_tool": "send_message",
        "expected_platform": "telegram",
        "expected_channel": "123456789",
        "expected_message_keywords": ["cpu", "srv-db-01", "tinggi"],
    },
    {
        "name": "send_email_report",
        "prompt": "Kirim email ke ops-team@company.com dengan subject: Daily Report - Server Health",
        "expected_tool": "send_message",
        "expected_platform": "email",
        "expected_channel": "ops-team@company.com",
        "expected_message_keywords": ["report", "server", "health"],
    },
    {
        "name": "send_critical_alert",
        "prompt": "Kirim critical alert ke Discord channel #critical: database srv-db-01 down, customer impact",
        "expected_tool": "send_message",
        "expected_platform": "discord",
        "expected_channel": "#critical",
        "expected_priority": "critical",
        "expected_message_keywords": ["database", "down", "customer"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all messaging tests and return results."""
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

            score = _evaluate_messaging(tc, tool_calls)
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
        "capability": "messaging",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_messaging(test_case: dict, tool_calls) -> float:
    """Evaluate messaging capability."""
    if tool_calls is None or len(tool_calls) == 0:
        return 0.0

    called_tools = [tc.function.name for tc in tool_calls if hasattr(tc, 'function')]

    # Check if expected tool is called
    if test_case.get("expected_tool") not in called_tools:
        return 0.0

    score = 0.4  # Base score for calling correct tool

    # Check parameters
    for tc in tool_calls:
        if hasattr(tc, 'function'):
            try:
                import json
                args = json.loads(tc.function.arguments)

                # Check platform
                expected_platform = test_case.get("expected_platform")
                if expected_platform and args.get("platform") == expected_platform:
                    score += 0.2

                # Check channel
                expected_channel = test_case.get("expected_channel")
                if expected_channel and expected_channel in args.get("channel", ""):
                    score += 0.15

                # Check message content
                expected_message_keywords = test_case.get("expected_message_keywords", [])
                if expected_message_keywords:
                    message = args.get("message", "").lower()
                    matched = sum(1 for kw in expected_message_keywords if kw.lower() in message)
                    message_score = matched / len(expected_message_keywords)
                    score += message_score * 0.15

                # Check priority
                expected_priority = test_case.get("expected_priority")
                if expected_priority and args.get("priority") == expected_priority:
                    score += 0.1

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
