"""
Test: Terminal & Process Operations

Mengukur kemampuan model untuk:
1. Memanggil tool terminal_execute dengan command yang tepat
2. Memanggil tool process_list untuk melihat processes
3. Memanggil tool process_kill untuk menghentikan process
"""

from openai import OpenAI


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "terminal_execute",
            "description": "Execute a terminal command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {"type": "integer", "default": 30}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "process_list",
            "description": "List running processes",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "process_kill",
            "description": "Kill a process by PID",
            "parameters": {
                "type": "object",
                "properties": {
                    "pid": {"type": "integer"}
                },
                "required": ["pid"]
            }
        }
    }
]


TEST_CASES = [
    {
        "name": "check_cpu_usage",
        "prompt": "Cek CPU usage server saat ini",
        "expected_tool": "terminal_execute",
        "expected_command_keywords": ["top", "ps", "cpu", "htop"],
    },
    {
        "name": "list_processes",
        "prompt": "List semua process yang sedang berjalan",
        "expected_tool": "process_list",
        "expected_command_keywords": [],
    },
    {
        "name": "find_java_process",
        "prompt": "Cari process Java yang sedang berjalan",
        "expected_tool": "process_list",
        "expected_filter": "java",
    },
    {
        "name": "kill_process",
        "prompt": "Kill process dengan PID 12345",
        "expected_tool": "process_kill",
        "expected_pid": 12345,
    },
    {
        "name": "check_disk_space",
        "prompt": "Cek disk space yang tersedia",
        "expected_tool": "terminal_execute",
        "expected_command_keywords": ["df", "disk", "space"],
    },
    {
        "name": "check_memory",
        "prompt": "Cek memory usage saat ini",
        "expected_tool": "terminal_execute",
        "expected_command_keywords": ["free", "memory", "mem"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all terminal tests and return results."""
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

            score = _evaluate_terminal(tc, tool_calls)
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
        "capability": "terminal",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_terminal(test_case: dict, tool_calls) -> float:
    """Evaluate terminal operation capability."""
    if tool_calls is None or len(tool_calls) == 0:
        return 0.0

    called_tools = [tc.function.name for tc in tool_calls if hasattr(tc, 'function')]

    # Check if expected tool is called
    if test_case.get("expected_tool") not in called_tools:
        return 0.0

    score = 0.5  # Base score for calling correct tool

    # Check command quality for terminal_execute
    for tc in tool_calls:
        if hasattr(tc, 'function'):
            if tc.function.name == "terminal_execute":
                try:
                    import json
                    args = json.loads(tc.function.arguments)
                    command = args.get("command", "").lower()
                    expected_keywords = test_case.get("expected_command_keywords", [])
                    if expected_keywords:
                        matched = sum(1 for kw in expected_keywords if kw.lower() in command)
                        query_score = matched / len(expected_keywords)
                        score = 0.5 + (query_score * 0.5)
                except:
                    pass

            elif tc.function.name == "process_list":
                try:
                    import json
                    args = json.loads(tc.function.arguments)
                    filter_val = args.get("filter", "").lower()
                    expected_filter = test_case.get("expected_filter", "")
                    if expected_filter and expected_filter.lower() in filter_val:
                        score = 1.0
                except:
                    pass

            elif tc.function.name == "process_kill":
                try:
                    import json
                    args = json.loads(tc.function.arguments)
                    pid = args.get("pid")
                    expected_pid = test_case.get("expected_pid")
                    if expected_pid and pid == expected_pid:
                        score = 1.0
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
