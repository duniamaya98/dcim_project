"""
Test: Streaming

Mengukur kemampuan model untuk:
1. Time To First Token (TTFT) - waktu sampai token pertama
2. Token streaming - apakah token datang secara bertahap
3. Total generation time
"""

import time
from openai import OpenAI


TEST_PROMPTS = [
    {
        "name": "short_response",
        "prompt": "Apa itu CPU spike? Jawab dalam 1 kalimat.",
        "expected_tokens_min": 10,
        "expected_tokens_max": 50,
    },
    {
        "name": "medium_response",
        "prompt": "Jelaskan 3 langkah troubleshooting untuk server dengan CPU 95%.",
        "expected_tokens_min": 50,
        "expected_tokens_max": 200,
    },
    {
        "name": "long_response",
        "prompt": "Buat laporan lengkap analisis server srv-db-01 dengan metrics: CPU 90%, Memory 88%, Disk I/O 2500. Sertakan root cause analysis, impact assessment, dan rekomendasi tindakan.",
        "expected_tokens_min": 150,
        "expected_tokens_max": 500,
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all streaming tests and return results."""
    results = []
    total_score = 0
    max_score = len(TEST_PROMPTS)

    for tp in TEST_PROMPTS:
        try:
            # Measure TTFT and streaming
            start_time = time.time()
            first_token_time = None
            token_count = 0
            content_chunks = []

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": tp["prompt"]}],
                temperature=test_config.get("temperature", 0.3),
                max_tokens=test_config.get("max_tokens", 1024),
                stream=True,
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        if first_token_time is None:
                            first_token_time = time.time()
                        content_chunks.append(delta.content)
                        token_count += 1

            end_time = time.time()
            ttft = first_token_time - start_time if first_token_time else 0
            total_time = end_time - start_time
            full_content = "".join(content_chunks)

            score = _evaluate_streaming(tp, ttft, total_time, token_count, full_content)
            total_score += score

            results.append({
                "test": tp["name"],
                "score": score,
                "ttft_seconds": round(ttft, 3),
                "total_time_seconds": round(total_time, 3),
                "token_count": token_count,
                "tokens_per_second": round(token_count / total_time, 2) if total_time > 0 else 0,
                "content_preview": full_content[:100] if full_content else "",
            })

        except Exception as e:
            results.append({
                "test": tp["name"],
                "score": 0.0,
                "error": str(e),
            })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "streaming",
        "score": round(final_score, 3),
        "total_tests": len(TEST_PROMPTS),
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_streaming(test_prompt: dict, ttft: float, total_time: float, token_count: int, content: str) -> float:
    """Evaluate streaming quality."""
    score = 0.0

    # TTFT scoring (lower is better)
    if ttft < 0.5:
        ttft_score = 1.0
    elif ttft < 1.5:
        ttft_score = 0.75
    elif ttft < 3.0:
        ttft_score = 0.5
    elif ttft < 5.0:
        ttft_score = 0.25
    else:
        ttft_score = 0.0
    score += ttft_score * 0.4  # 40% weight for TTFT

    # Token count scoring (within expected range)
    expected_min = test_prompt.get("expected_tokens_min", 10)
    expected_max = test_prompt.get("expected_tokens_max", 500)
    if expected_min <= token_count <= expected_max:
        token_score = 1.0
    elif token_count < expected_min:
        token_score = max(0, token_count / expected_min)
    else:
        token_score = max(0, expected_max / token_count)
    score += token_score * 0.3  # 30% weight for token count

    # Streaming verification (tokens came in chunks, not all at once)
    if total_time > 0.1 and token_count > 1:
        streaming_score = 1.0  # If we got chunks, streaming works
    else:
        streaming_score = 0.5
    score += streaming_score * 0.3  # 30% weight for streaming

    return min(score, 1.0)
