"""
Test: Chain-of-Thought Reasoning

Mengukur kemampuan model untuk:
1. Berpikir step-by-step sebelum memberikan jawaban
2. Menjelaskan reasoning process secara eksplisit
3. Memberikan jawaban final yang benar setelah reasoning
"""

import re
from openai import OpenAI


TEST_CASES = [
    {
        "name": "dependency_chain",
        "prompt": "Server A terhubung ke Server B, Server B terhubung ke Server C. Server C down. Server mana saja yang terpengaruh? Jelaskan step by step.",
        "expected_steps": ["C down", "B affected", "A affected"],
        "expected_answer": ["A", "B", "C"],
    },
    {
        "name": "arithmetic_reasoning",
        "prompt": "Server punya 64GB RAM. Process A pakai 20GB, Process B pakai 15GB, Process C pakai 25GB, OS pakai 10GB. Apakah cukup? Jelaskan step by step.",
        "expected_steps": ["20", "15", "25", "10", "70", "64"],
        "expected_answer": ["tidak", "tidak cukup", "insufficient", "kurang"],
    },
    {
        "name": "temporal_reasoning",
        "prompt": "Server mulai overheating jam 10:00. Suhu naik 2°C per jam. Suhu awal 22°C. Threshold critical 35°C. Jam berapa server mencapai critical? Jelaskan step by step.",
        "expected_steps": ["22", "2", "35", "13", "6.5"],
        "expected_answer": ["13", "16:30", "jam 13", "6.5"],
    },
    {
        "name": "proportional_reasoning",
        "prompt": "Load balancer mendistribusikan traffic: Server A 40%, Server B 30%, Server C 30%. Server C down. Berapa persen traffic yang harus ditanggung Server A dan B? Jelaskan step by step.",
        "expected_steps": ["40", "30", "30", "60", "70"],
        "expected_answer": ["57", "43", "60", "40"],
    },
    {
        "name": "root_cause_reasoning",
        "prompt": "Server srv-app-05: CPU 95%, Memory 45%, Disk I/O normal, Network normal. Apa kemungkinan root cause? Jelaskan step by step eliminasi.",
        "expected_steps": ["cpu", "memory", "disk", "network", "eliminate", "process"],
        "expected_answer": ["cpu", "process", "compute", "encoding", "compression"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all CoT reasoning tests and return results."""
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
                        "content": "Think step by step. Explain your reasoning process before giving the final answer."
                    },
                    {"role": "user", "content": tc["prompt"]}
                ],
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            content = response.choices[0].message.content.strip()
            score = _evaluate_cot_reasoning(tc, content)
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
        "capability": "cot_reasoning",
        "score": round(final_score, 3),
        "total_tests": len(TEST_CASES),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_cot_reasoning(test_case: dict, content: str) -> float:
    """Evaluate chain-of-thought reasoning quality."""
    score = 0.0
    content_lower = content.lower()

    # Check if model shows step-by-step reasoning
    step_indicators = ["step", "langkah", "first", "pertama", "second", "kedua", "third", "ketiga", "finally", "akhirnya", "therefore", "oleh karena", "kesimpulan"]
    step_count = sum(1 for indicator in step_indicators if indicator in content_lower)
    step_score = min(step_count / 3, 1.0)  # At least 3 step indicators
    score += step_score * 0.3  # 30% weight for step-by-step structure

    # Check if expected steps/concepts are mentioned
    expected_steps = test_case.get("expected_steps", [])
    if expected_steps:
        step_matches = sum(1 for step in expected_steps if step.lower() in content_lower)
        step_match_score = step_matches / len(expected_steps)
        score += step_match_score * 0.3  # 30% weight for step coverage

    # Check if final answer is correct
    expected_answers = test_case.get("expected_answer", [])
    if expected_answers:
        answer_matches = sum(1 for ans in expected_answers if ans.lower() in content_lower)
        answer_score = min(answer_matches / 2, 1.0)  # At least 2 answer keywords
        score += answer_score * 0.4  # 40% weight for answer correctness

    return min(score, 1.0)
