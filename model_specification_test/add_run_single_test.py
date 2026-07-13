#!/usr/bin/env python3
"""
Script untuk menambahkan fungsi run_single_test ke semua test modules.
Jalankan script ini sekali untuk setup.
"""

import os
from pathlib import Path

TEST_MODULES = {
    "test_rag.py": """
def run_single_test(client: OpenAI, model: str, test_def: Dict, test_config: Dict) -> Dict[str, Any]:
    \"\"\"Run single test case untuk level-based testing.\"\"\"
    try:
        # Get context based on context_type
        context_type = test_def.get("context_type", "sop_cpu_alert")
        context = None
        for ctx in RAG_CONTEXTS:
            if ctx["name"] == context_type:
                context = ctx["context"]
                break

        if not context:
            context = RAG_CONTEXTS[0]["context"]

        # Build messages with context
        messages = [
            {"role": "system", "content": "Jawab berdasarkan konteks yang diberikan. Jangan gunakan pengetahuan di luar konteks."},
            {"role": "user", "content": f"Context:\\n{context}\\n\\nQuestion: {test_def['prompt']}"}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=test_config.get("temperature", 0.3),
            max_tokens=test_config.get("max_tokens", 1024),
        )

        content = response.choices[0].message.content
        score = _evaluate_rag_response(test_def, content)

        return {
            "score": score,
            "test_name": test_def["name"],
            "response_preview": content[:200] if content else "",
        }
    except Exception as e:
        return {"score": 0.0, "test_name": test_def["name"], "error": str(e)}
""",
    "test_vision.py": """
def run_single_test(client: OpenAI, model: str, test_def: Dict, test_config: Dict) -> Dict[str, Any]:
    \"\"\"Run single test case untuk level-based testing.\"\"\"
    try:
        # Create test images if needed
        image_dir = os.path.join(os.path.dirname(__file__), "..", "test_images")
        os.makedirs(image_dir, exist_ok=True)

        # Use existing test images
        image_map = {
            "dashboard_mockup.png": "dashboard_mockup.png",
            "alert_notification.png": "alert_notification.png",
        }

        # For simplicity, use dashboard_mockup for most tests
        image_name = test_def.get("image", "dashboard_mockup.png")
        image_path = os.path.join(image_dir, image_name)

        # Create image if not exists
        if not os.path.exists(image_path):
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            draw.rectangle([50, 50, 750, 150], fill='lightblue', outline='black')
            draw.text((100, 80), "Server Dashboard - CPU: 85%, Memory: 72%", fill='black')
            img.save(image_path)

        # Encode image
        import base64
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()

        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": test_def["prompt"]},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        }]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=test_config.get("temperature", 0.3),
            max_tokens=test_config.get("max_tokens", 1024),
        )

        content = response.choices[0].message.content
        score = _evaluate_vision_response(test_def, content)

        return {
            "score": score,
            "test_name": test_def["name"],
            "response_preview": content[:200] if content else "",
        }
    except Exception as e:
        return {"score": 0.0, "test_name": test_def["name"], "error": str(e)}
""",
    "test_code_execution.py": """
def run_single_test(client: OpenAI, model: str, test_def: Dict, test_config: Dict) -> Dict[str, Any]:
    \"\"\"Run single test case untuk level-based testing.\"\"\"
    try:
        messages = [
            {"role": "system", "content": f"You are a code generation assistant. Generate only {test_def.get('language', 'python')} code."},
            {"role": "user", "content": test_def["prompt"]}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=test_config.get("temperature", 0.3),
            max_tokens=test_config.get("max_tokens", 2048),
        )

        content = response.choices[0].message.content
        code = _extract_code(content, test_def.get("language", "python"))
        score = _evaluate_code(test_def, code)

        return {
            "score": score,
            "test_name": test_def["name"],
            "code_preview": code[:200] if code else "",
        }
    except Exception as e:
        return {"score": 0.0, "test_name": test_def["name"], "error": str(e)}
""",
    "test_json_mode.py": """
def run_single_test(client: OpenAI, model: str, test_def: Dict, test_config: Dict) -> Dict[str, Any]:
    \"\"\"Run single test case untuk level-based testing.\"\"\"
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Always respond with valid JSON only."},
            {"role": "user", "content": test_def["prompt"]}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=test_config.get("temperature", 0.3),
            max_tokens=test_config.get("max_tokens", 1024),
        )

        content = response.choices[0].message.content
        score = _evaluate_json_output(test_def, content)

        return {
            "score": score,
            "test_name": test_def["name"],
            "output_preview": content[:200] if content else "",
            "is_valid_json": _is_valid_json(content),
        }
    except Exception as e:
        return {"score": 0.0, "test_name": test_def["name"], "error": str(e)}
""",
    "test_terminal.py": """
def run_single_test(client: OpenAI, model: str, test_def: Dict, test_config: Dict) -> Dict[str, Any]:
    \"\"\"Run single test case untuk level-based testing.\"\"\"
    try:
        messages = [
            {"role": "system", "content": "You are a terminal assistant. Provide bash commands."},
            {"role": "user", "content": test_def["prompt"]}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=test_config.get("temperature", 0.3),
            max_tokens=test_config.get("max_tokens", 1024),
        )

        content = response.choices[0].message.content
        score = _evaluate_terminal_output(test_def, content)

        return {
            "score": score,
            "test_name": test_def["name"],
            "output_preview": content[:200] if content else "",
        }
    except Exception as e:
        return {"score": 0.0, "test_name": test_def["name"], "error": str(e)}
""",
}

# Generic template for other modules
GENERIC_TEMPLATE = """
def run_single_test(client: OpenAI, model: str, test_def: Dict, test_config: Dict) -> Dict[str, Any]:
    \"\"\"Run single test case untuk level-based testing.\"\"\"
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": test_def["prompt"]}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=test_config.get("temperature", 0.3),
            max_tokens=test_config.get("max_tokens", 1024),
        )

        content = response.choices[0].message.content
        score = _evaluate_response(test_def, content)

        return {
            "score": score,
            "test_name": test_def["name"],
            "response_preview": content[:200] if content else "",
        }
    except Exception as e:
        return {"score": 0.0, "test_name": test_def["name"], "error": str(e)}
"""

def main():
    tests_dir = Path(__file__).parent / "tests"

    for filename, function_code in TEST_MODULES.items():
        filepath = tests_dir / filename

        if not filepath.exists():
            print(f"Skipping {filename} - file not found")
            continue

        # Read existing content
        with open(filepath, 'r') as f:
            content = f.read()

        # Check if run_single_test already exists
        if "def run_single_test" in content:
            print(f"Skipping {filename} - run_single_test already exists")
            continue

        # Add imports if needed
        if "from typing import Dict, Any" not in content:
            # Find the import section
            lines = content.split('\\n')
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    import_idx = i + 1

            lines.insert(import_idx, "from typing import Dict, Any")
            content = '\\n'.join(lines)

        # Append the function
        content += "\\n" + function_code

        # Write back
        with open(filepath, 'w') as f:
            f.write(content)

        print(f"Added run_single_test to {filename}")

if __name__ == "__main__":
    main()
