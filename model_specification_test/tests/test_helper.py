"""
Helper functions untuk menambahkan run_single_test ke semua test modules.
Import ini di setiap test module untuk menambahkan fungsi run_single_test.
"""

from typing import Dict, Any
from openai import OpenAI

def create_run_single_test(evaluate_func, test_cases_attr="TEST_CASES"):
    """
    Factory function untuk membuat run_single_test.

    Args:
        evaluate_func: Function untuk evaluate hasil test
        test_cases_attr: Nama attribute yang berisi test cases

    Returns:
        Function run_single_test
    """
    def run_single_test(
        client: OpenAI,
        model: str,
        test_def: Dict,
        test_config: Dict
    ) -> Dict[str, Any]:
        """
        Run single test case untuk level-based testing.

        Args:
            client: OpenAI client
            model: Model name
            test_def: Test definition dari level_test_definitions.py
            test_config: Test configuration

        Returns:
            Dict dengan score dan details
        """
        try:
            # Build messages based on test definition
            messages = _build_messages(test_def)

            # Add tools if needed
            tools = test_def.get("tools")
            tool_choice = test_def.get("tool_choice", "auto")

            # Add response format for JSON mode
            response_format = test_def.get("response_format")

            # Call the model
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": test_config.get("temperature", 0.3),
                "max_tokens": test_config.get("max_tokens", 1024),
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice

            if response_format:
                kwargs["response_format"] = response_format

            response = client.chat.completions.create(**kwargs)

            # Get response content
            content = response.choices[0].message.content
            tool_calls = response.choices[0].message.tool_calls if hasattr(response.choices[0].message, 'tool_calls') else None

            # Evaluate the response
            score = evaluate_func(test_def, content, tool_calls)

            return {
                "score": score,
                "test_name": test_def["name"],
                "response_preview": content[:200] if content else "",
                "tool_calls": _serialize_tool_calls(tool_calls) if tool_calls else [],
            }

        except Exception as e:
            return {
                "score": 0.0,
                "test_name": test_def["name"],
                "error": str(e),
            }

    return run_single_test

def _build_messages(test_def: Dict) -> list:
    """Build messages from test definition"""
    messages = []

    # Add system message if provided
    if "system_prompt" in test_def:
        messages.append({"role": "system", "content": test_def["system_prompt"]})

    # Add user message
    if "prompt" in test_def:
        messages.append({"role": "user", "content": test_def["prompt"]})

    # Add context for RAG tests
    if "context" in test_def:
        # Insert context before the question
        if messages and messages[-1]["role"] == "user":
            user_content = messages[-1]["content"]
            messages[-1]["content"] = f"Context:\n{test_def['context']}\n\nQuestion: {user_content}"
        else:
            messages.append({"role": "user", "content": test_def["context"]})

    # Add image for vision tests
    if "image_path" in test_def:
        import base64
        with open(test_def["image_path"], "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()

        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": test_def.get("prompt", "Describe this image")},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                }
            ]
        })

    return messages

def _serialize_tool_calls(tool_calls) -> list:
    """Serialize tool calls for JSON output"""
    if not tool_calls:
        return []

    result = []
    for tc in tool_calls:
        if hasattr(tc, 'function'):
            result.append({
                "name": tc.function.name,
                "arguments": tc.function.arguments
            })
    return result
