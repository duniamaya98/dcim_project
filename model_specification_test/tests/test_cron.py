"""
Test: Cron Jobs

Mengukur kemampuan model untuk:
1. Memanggil tool cron_create untuk membuat scheduled task
2. Memanggil tool cron_list untuk melihat scheduled tasks
3. Membuat schedule yang sesuai dengan requirements
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "cron_create",
            "description": "Create a scheduled task",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "schedule": {"type": "string", "description": "Cron expression (e.g., '0 */5 * * *')"},
                    "task": {"type": "string"},
                    "skill": {"type": "string"}
                },
                "required": ["name", "schedule", "task"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cron_list",
            "description": "List all scheduled tasks",
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cron_delete",
            "description": "Delete a scheduled task",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "create_hourly_check",
        "prompt": "Buat cron job untuk check server health setiap jam",
        "expected_tool": "cron_create",
        "expected_schedule_keywords": ["hourly", "0 * * * *", "setiap jam"],
        "expected_task_keywords": ["health", "check", "server"],
    },
    {
        "name": "create_daily_report",
        "prompt": "Buat cron job untuk generate daily report setiap jam 6 pagi",
        "expected_tool": "cron_create",
        "expected_schedule_keywords": ["6", "morning", "0 6 * * *"],
        "expected_task_keywords": ["report", "daily", "generate"],
    },
    {
        "name": "create_5min_monitor",
        "prompt": "Buat cron job untuk monitor CPU setiap 5 menit",
        "expected_tool": "cron_create",
        "expected_schedule_keywords": ["5", "*/5", "minute"],
        "expected_task_keywords": ["cpu", "monitor"],
    },
    {
        "name": "list_cron_jobs",
        "prompt": "List semua cron job yang sudah dibuat",
        "expected_tool": "cron_list",
        "expected_schedule_keywords": [],
        "expected_task_keywords": [],
    },
    {
        "name": "delete_cron_job",
        "prompt": "Hapus cron job bernama 'hourly-health-check'",
        "expected_tool": "cron_delete",
        "expected_name": "hourly-health-check",
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all cron job tests and return results."""
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

            score = _evaluate_cron(tc, tool_calls)
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
        "capability": "cron",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_cron(test_case: dict, tool_calls) -> float:
    """Evaluate cron job capability."""
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

                # Check schedule
                expected_schedule_keywords = test_case.get("expected_schedule_keywords", [])
                if expected_schedule_keywords:
                    schedule = args.get("schedule", "").lower()
                    matched = sum(1 for kw in expected_schedule_keywords if kw.lower() in schedule)
                    schedule_score = matched / len(expected_schedule_keywords) if expected_schedule_keywords else 1.0
                    score += schedule_score * 0.25

                # Check task
                expected_task_keywords = test_case.get("expected_task_keywords", [])
                if expected_task_keywords:
                    task = args.get("task", "").lower()
                    matched = sum(1 for kw in expected_task_keywords if kw.lower() in task)
                    task_score = matched / len(expected_task_keywords) if expected_task_keywords else 1.0
                    score += task_score * 0.25

                # Check name for delete
                expected_name = test_case.get("expected_name")
                if expected_name and args.get("name") == expected_name:
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
