"""
Test: Multi-turn Conversation

Mengukur kemampuan model untuk:
1. Mengingat konteks percakapan sebelumnya
2. Menjawab follow-up questions dengan benar
3. Maintain context across multiple turns
"""

import json
from openai import OpenAI


CONVERSATION_SCENARIOS = [
    {
        "name": "server_investigation",
        "turns": [
            {
                "role": "user",
                "content": "Analisis server srv-web-01"
            },
            {
                "role": "assistant",
                "content": "Server srv-web-01: CPU 85%, Memory 72%, Disk I/O normal. Status: warning. CPU usage tinggi perlu diinvestigasi."
            },
            {
                "role": "user",
                "content": "Kenapa CPU tinggi?"
            },
        ],
        "expected_context": ["srv-web-01", "cpu", "85"],
        "expected_answer_keywords": ["process", "top", "load", "compute"],
    },
    {
        "name": "incident_followup",
        "turns": [
            {
                "role": "user",
                "content": "Ada incident di srv-db-01, memory 95%"
            },
            {
                "role": "assistant",
                "content": "Incident terdeteksi di srv-db-01: Memory usage 95% (critical). Kemungkinan memory leak. Rekomendasi: check process dengan top, restart service jika perlu."
            },
            {
                "role": "user",
                "content": "Sudah di-restart, sekarang memory 60%. Apakah masih perlu investigasi?"
            },
        ],
        "expected_context": ["srv-db-01", "memory", "restart"],
        "expected_answer_keywords": ["monitor", "watch", "check", "stable", "normal"],
    },
    {
        "name": "multi_server_comparison",
        "turns": [
            {
                "role": "user",
                "content": "Server srv-web-01 CPU 45%, srv-web-02 CPU 80%, srv-db-01 CPU 90%. Mana yang paling bermasalah?"
            },
            {
                "role": "assistant",
                "content": "srv-db-01 paling bermasalah dengan CPU 90% (critical). srv-web-02 warning (80%). srv-web-01 normal (45%)."
            },
            {
                "role": "user",
                "content": "Apa yang harus dilakukan untuk yang paling bermasalah?"
            },
        ],
        "expected_context": ["srv-db-01", "90", "cpu"],
        "expected_answer_keywords": ["investigate", "check", "process", "top", "restart"],
    },
    {
        "name": "clarification_chain",
        "turns": [
            {
                "role": "user",
                "content": "Server lambat"
            },
            {
                "role": "assistant",
                "content": "Server mana yang lambat? Dan metrik apa yang menunjukkan kelambatan (CPU, memory, disk, network)?"
            },
            {
                "role": "user",
                "content": "srv-app-05, CPU 95% dan response time 5 detik"
            },
        ],
        "expected_context": ["srv-app-05", "cpu", "95", "response"],
        "expected_answer_keywords": ["investigate", "process", "check", "analyze"],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all multi-turn conversation tests and return results."""
    results = []
    total_score = 0
    max_score = len(CONVERSATION_SCENARIOS)

    for scenario in CONVERSATION_SCENARIOS:
        try:
            messages = [{"role": "system", "content": "You are a DCIM assistant."}]

            # Play through conversation turns
            for turn in scenario["turns"]:
                messages.append({"role": turn["role"], "content": turn["content"]})

            # Get model response to last user message
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
            )

            content = response.choices[0].message.content.strip()
            score = _evaluate_multiturn(scenario, content)
            total_score += score

            results.append({
                "test": scenario["name"],
                "score": score,
                "response_preview": content[:200] if content else "",
                "turns": len(scenario["turns"]),
            })

        except Exception as e:
            results.append({
                "test": scenario["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "multi_turn",
        "score": round(final_score, 3),
        "total_tests": len(CONVERSATION_SCENARIOS),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_multiturn(scenario: dict, response: str) -> float:
    """Evaluate multi-turn conversation quality."""
    score = 0.0
    response_lower = response.lower()

    # Check if model remembers context
    expected_context = scenario.get("expected_context", [])
    if expected_context:
        context_matches = 0
        for ctx in expected_context:
            if ctx.lower() in response_lower:
                context_matches += 1
        context_score = context_matches / len(expected_context)
        score += context_score * 0.5  # 50% weight for context retention

    # Check if response contains expected answer keywords
    expected_keywords = scenario.get("expected_answer_keywords", [])
    if expected_keywords:
        keyword_matches = 0
        for kw in expected_keywords:
            if kw.lower() in response_lower:
                keyword_matches += 1
        keyword_score = keyword_matches / len(expected_keywords)
        score += keyword_score * 0.5  # 50% weight for answer quality

    return min(score, 1.0)
