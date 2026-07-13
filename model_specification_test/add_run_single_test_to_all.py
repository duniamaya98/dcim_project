#!/usr/bin/env python3
"""Auto-add run_single_test ke semua test modules."""

import os
from pathlib import Path

# Template untuk tool-based tests (yang pakai TOOLS)
TOOL_BASED_TEMPLATE = '''

def run_single_test(client: OpenAI, model: str, test_def: Dict, test_config: Dict) -> Dict[str, Any]:
    """Run single test case for level-based testing."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": test_def.get("prompt", "")}],
            tools={TOOLS},
            tool_choice="auto",
            temperature=test_config.get("temperature", 0.3),
            max_tokens=test_config.get("max_tokens", 1024),
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else None

        score = {EVAL_FUNC}(test_def, tool_calls)

        return {
            "score": score,
            "test_name": test_def["name"],
            "tool_calls": _serialize_tool_calls(tool_calls) if tool_calls else [],
        }
    except Exception as e:
        return {"score": 0.0, "test_name": test_def["name"], "error": str(e)}
'''

# Template untuk text-based tests (tanpa TOOLS)
TEXT_BASED_TEMPLATE = '''

def run_single_test(client: OpenAI, model: str, test_def: Dict, test_config: Dict) -> Dict[str, Any]:
    """Run single test case for level-based testing."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "{SYSTEM_PROMPT}"},
                {"role": "user", "content": test_def.get("prompt", "")}
            ],
            temperature=test_config.get("temperature", 0.3),
            max_tokens=test_config.get("max_tokens", 1024),
        )

        content = response.choices[0].message.content
        score = {EVAL_FUNC}(test_def, content)

        return {
            "score": score,
            "test_name": test_def["name"],
            "response_preview": content[:200] if content else "",
        }
    except Exception as e:
        return {"score": 0.0, "test_name": test_def["name"], "error": str(e)}
'''

# Mapping: filename -> (tools_var, eval_func, system_prompt, is_tool_based)
MODULE_CONFIGS = {
    # Tool-based tests
    "test_rag.py": ("None", "_evaluate_rag_response", None, False),
    "test_code_execution.py": ("None", "_evaluate_code", None, False),
    "test_json_mode.py": ("None", "_evaluate_json_output", None, False),
    "test_terminal.py": ("TOOLS", "_evaluate_terminal", None, True),
    "test_structured_output.py": ("None", "_evaluate_structured_output", None, False),
    "test_multiturn.py": ("None", "_evaluate_multiturn", None, False),
    "test_streaming.py": ("None", "_evaluate_streaming", None, False),
    "test_cot_reasoning.py": ("None", "_evaluate_cot_reasoning", None, False),
    "test_agent.py": ("AGENT_TOOLS", "_evaluate_agent", None, True),
    "test_web_search.py": ("TOOLS", "_evaluate_web_search", None, True),
    "test_file_ops.py": ("TOOLS", "_evaluate_file_ops", None, True),
    "test_memory.py": ("TOOLS", "_evaluate_memory", None, True),
    "test_task_planning.py": ("None", "_evaluate_task_planning", None, False),
    "test_cron.py": ("TOOLS", "_evaluate_cron", None, True),
    "test_messaging.py": ("TOOLS", "_evaluate_messaging", None, True),
    "test_session_search.py": ("TOOLS", "_evaluate_session_search", None, True),
    "test_clarifying.py": ("None", "_evaluate_clarifying", None, False),
    "test_delegation.py": ("TOOLS", "_evaluate_delegation", None, True),
    "test_skills.py": ("TOOLS", "_evaluate_skills", None, True),
    "test_context_engine.py": ("TOOLS", "_evaluate_context", None, True),
    "test_vision.py": ("None", "_evaluate_vision_response", None, False),
    "test_mixture_of_agents.py": ("None", "_evaluate_moa", None, False),
}

def main():
    tests_dir = Path(__file__).parent / "tests"

    for filename, config in MODULE_CONFIGS.items():
        filepath = tests_dir / filename
        tools_var, eval_func, system_prompt, is_tool_based = config

        if not filepath.exists():
            print(f"⏭️  Skip {filename} - file not found")
            continue

        with open(filepath, 'r') as f:
            content = f.read()

        if "def run_single_test" in content:
            print(f"⏭️  Skip {filename} - already has run_single_test")
            continue

        # Add typing import if needed
        if "from typing import Dict, Any" not in content:
            lines = content.split('\n')
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    import_idx = i + 1

            lines.insert(import_idx, "from typing import Dict, Any")
            content = '\n'.join(lines)

        # Generate template
        if is_tool_based:
            template = TOOL_BASED_TEMPLATE.format(
                TOOLS=tools_var,
                EVAL_FUNC=eval_func
            )
        else:
            template = TEXT_BASED_TEMPLATE.format(
                SYSTEM_PROMPT=system_prompt or "You are a helpful assistant.",
                EVAL_FUNC=eval_func
            )

        content += template

        with open(filepath, 'w') as f:
            f.write(content)

        print(f"✅ Added run_single_test to {filename}")

if __name__ == "__main__":
    main()
