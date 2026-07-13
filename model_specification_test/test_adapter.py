"""
Test Adapter for Level-Based Testing

Adapter yang memungkinkan test modules existing digunakan dengan level-based testing system.
Setiap test module perlu mengimplementasikan fungsi run_single_test() yang menerima test definition.
"""

from typing import Dict, Any, Optional
from openai import OpenAI

def adapt_test_for_level(
    client: OpenAI,
    model: str,
    test_def: Dict,
    test_config: Dict,
    capability: str
) -> Dict[str, Any]:
    """
    Adapt existing test to run with level-based test definition.

    Args:
        client: OpenAI client
        model: Model name
        test_def: Test definition from level_test_definitions.py
        test_config: Test configuration
        capability: Capability name

    Returns:
        Dict with score and details
    """

    # Import the appropriate test module
    module_mapping = {
        "tool_calling": "tests.test_tool_calling",
        "vision": "tests.test_vision",
        "rag": "tests.test_rag",
        "code_execution": "tests.test_code_execution",
        "terminal": "tests.test_terminal",
        "json_mode": "tests.test_json_mode",
        "structured_output": "tests.test_structured_output",
        "multiturn": "tests.test_multiturn",
        "streaming": "tests.test_streaming",
        "cot_reasoning": "tests.test_cot_reasoning",
        "agent": "tests.test_agent",
        "web_search": "tests.test_web_search",
        "file_ops": "tests.test_file_ops",
        "memory": "tests.test_memory",
        "task_planning": "tests.test_task_planning",
        "cron": "tests.test_cron",
        "messaging": "tests.test_messaging",
        "session_search": "tests.test_session_search",
        "clarifying": "tests.test_clarifying",
        "delegation": "tests.test_delegation",
        "skills": "tests.test_skills",
        "context_engine": "tests.test_context_engine",
        "mixture_of_agents": "tests.test_mixture_of_agents",
    }

    module_name = module_mapping.get(capability)
    if not module_name:
        return {"score": 0.0, "error": f"No test module for {capability}"}

    try:
        import importlib
        test_module = importlib.import_module(module_name)

        # Check if module has run_single_test function
        if hasattr(test_module, "run_single_test"):
            return test_module.run_single_test(client, model, test_def, test_config)
        else:
            # Fallback: use existing run_test function with adapted test case
            return _fallback_run_test(test_module, client, model, test_def, test_config)

    except ImportError as e:
        return {"score": 0.0, "error": f"Failed to import {module_name}: {str(e)}"}
    except Exception as e:
        return {"score": 0.0, "error": str(e)}

def _fallback_run_test(test_module, client: OpenAI, model: str, test_def: Dict, test_config: Dict) -> Dict[str, Any]:
    """
    Fallback method to run test using existing test infrastructure.
    """
    try:
        # Create a test case that matches the existing test format
        test_case = {
            "name": test_def["name"],
            "prompt": test_def.get("prompt", ""),
        }

        # Add capability-specific fields
        if "expected_tool" in test_def:
            test_case["expected_tool"] = test_def["expected_tool"]
        if "expected_params" in test_def:
            test_case["expected_params"] = test_def["expected_params"]
        if "expected_keywords" in test_def:
            test_case["expected_keywords"] = test_def["expected_keywords"]
        if "expected_tools" in test_def:
            test_case["expected_tools"] = test_def["expected_tools"]

        # Try to run with existing run_test function
        if hasattr(test_module, "run_test"):
            result = test_module.run_test(client, model, test_config)

            # Find the specific test in results
            for test_result in result.get("results", []):
                if test_result.get("test") == test_def["name"]:
                    return {
                        "score": test_result.get("score", 0.0),
                        "details": test_result
                    }

            # If not found, return average score
            results = result.get("results", [])
            if results:
                avg_score = sum(r.get("score", 0.0) for r in results) / len(results)
                return {"score": avg_score, "details": result}

        return {"score": 0.0, "error": "No suitable test function found"}

    except Exception as e:
        return {"score": 0.0, "error": str(e)}
