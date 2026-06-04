"""
Test: Task Planning

Mengukur kemampuan model untuk:
1. Break down complex tasks menjadi actionable steps
2. Mengidentifikasi dependencies antar steps
3. Memberikan estimasi waktu dan resources
"""

from openai import OpenAI


TEST_CASES = [
    {
        "name": "investigate_high_cpu",
        "prompt": "Buat plan untuk investigasi dan fix high CPU di server srv-app-05",
        "expected_steps": ["check", "metrics", "process", "top", "analyze", "fix"],
        "expected_keywords": ["step", "langkah", "first", "pertama", "second", "kedua"],
    },
    {
        "name": "deploy_new_service",
        "prompt": "Buat plan untuk deploy service baru ke production",
        "expected_steps": ["test", "staging", "deploy", "monitor", "rollback"],
        "expected_keywords": ["step", "phase", "stage", "tahap"],
    },
    {
        "name": "incident_response",
        "prompt": "Buat plan untuk incident response: server down, customer impact",
        "expected_steps": ["assess", "communicate", "investigate", "fix", "postmortem"],
        "expected_keywords": ["step", "action", "priority", "urgent"],
    },
    {
        "name": "server_migration",
        "prompt": "Buat plan untuk migrate server dari on-premise ke cloud",
        "expected_steps": ["assess", "plan", "test", "migrate", "validate"],
        "expected_keywords": ["step", "phase", "migration", "plan"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all task planning tests and return results."""
    results = []
    total_score = 0
    max_score = len(TEST_CASES)

    for tc in TEST_CASES:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a task planning assistant. Break down complex tasks into clear, actionable steps."
                    },
                    {"role": "user", "content": tc["prompt"]}
                ],
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            content = response.choices[0].message.content.strip()
            score = _evaluate_task_planning(tc, content)
            total_score += score

            results.append({
                "test": tc["name"],
                "score": score,
                "response_preview": content[:200] if content else "",
            })

        except Exception as e:
            results.append({
                "test": tc["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "task_planning",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_task_planning(test_case: dict, content: str) -> float:
    """Evaluate task planning quality."""
    score = 0.0
    content_lower = content.lower()

    # Check if response has step-by-step structure
    step_indicators = ["step", "langkah", "phase", "tahap", "1.", "2.", "3.", "first", "second", "third"]
    step_count = sum(1 for indicator in step_indicators if indicator in content_lower)
    structure_score = min(step_count / 3, 1.0)
    score += structure_score * 0.3  # 30% weight for structure

    # Check if expected steps are covered
    expected_steps = test_case.get("expected_steps", [])
    if expected_steps:
        matched_steps = sum(1 for step in expected_steps if step.lower() in content_lower)
        step_score = matched_steps / len(expected_steps)
        score += step_score * 0.4  # 40% weight for step coverage

    # Check if response contains planning keywords
    expected_keywords = test_case.get("expected_keywords", [])
    if expected_keywords:
        matched_keywords = sum(1 for kw in expected_keywords if kw.lower() in content_lower)
        keyword_score = matched_keywords / len(expected_keywords)
        score += keyword_score * 0.3  # 30% weight for planning language

    return min(score, 1.0)
