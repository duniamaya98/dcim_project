"""
Test: Clarifying Questions

Mengukur kemampuan model untuk:
1. Mengidentifikasi ketika informasi tidak cukup
2. Mengajukan pertanyaan klarifikasi yang relevan
3. Tidak membuat asumsi tanpa konfirmasi
"""

from openai import OpenAI


TEST_CASES = [
    {
        "name": "vague_server_issue",
        "prompt": "Server lambat",
        "should_ask_clarification": True,
        "expected_question_keywords": ["server", "mana", "which", "metrik", "metric", "kapan", "when"],
    },
    {
        "name": "missing_hostname",
        "prompt": "Cek CPU usage",
        "should_ask_clarification": True,
        "expected_question_keywords": ["server", "hostname", "mana", "which"],
    },
    {
        "name": "ambiguous_action",
        "prompt": "Fix masalahnya",
        "should_ask_clarification": True,
        "expected_question_keywords": ["masalah", "problem", "issue", "apa", "what", "server"],
    },
    {
        "name": "clear_request",
        "prompt": "Cek CPU usage server srv-web-01",
        "should_ask_clarification": False,
        "expected_question_keywords": [],
    },
    {
        "name": "incomplete_time_range",
        "prompt": "Cek logs server srv-app-05",
        "should_ask_clarification": True,
        "expected_question_keywords": ["time", "range", "waktu", "berapa", "how long"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all clarifying question tests and return results."""
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
                        "content": "You are a DCIM assistant. If the user's request is unclear or missing important information, ask clarifying questions before proceeding."
                    },
                    {"role": "user", "content": tc["prompt"]}
                ],
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            content = response.choices[0].message.content.strip()
            score = _evaluate_clarifying(tc, content)
            total_score += score

            results.append({
                "test": tc["name"],
                "score": score,
                "response_preview": content[:200] if content else "",
                "asked_clarification": _has_question_mark(content),
            })

        except Exception as e:
            results.append({
                "test": tc["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "clarifying",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _has_question_mark(content: str) -> bool:
    """Check if response contains question marks."""
    return "?" in content or "？" in content


def _evaluate_clarifying(test_case: dict, content: str) -> float:
    """Evaluate clarifying question capability."""
    score = 0.0
    content_lower = content.lower()
    has_question = _has_question_mark(content)

    # Check if model asked clarification when needed
    if test_case.get("should_ask_clarification"):
        if has_question:
            score += 0.5  # Asked a question

            # Check if question contains expected keywords
            expected_keywords = test_case.get("expected_question_keywords", [])
            if expected_keywords:
                matched = sum(1 for kw in expected_keywords if kw.lower() in content_lower)
                keyword_score = matched / len(expected_keywords)
                score += keyword_score * 0.5
        else:
            score = 0.0  # Should have asked but didn't
    else:
        # Should not ask clarification
        if not has_question:
            score = 1.0  # Correctly didn't ask
        else:
            score = 0.5  # Asked unnecessarily

    return min(score, 1.0)
