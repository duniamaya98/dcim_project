"""
Test: RAG (Retrieval Augmented Generation)

Mengukur kemampuan model untuk:
1. Menggunakan konteks yang diberikan untuk menjawab pertanyaan
2. Tidak mengabaikan konteks yang diberikan
3. Menjawab berdasarkan konteks, bukan knowledge internal
"""

import re
from openai import OpenAI


# Simulated RAG context (SOP documents)
RAG_CONTEXTS = [
    {
        "name": "sop_cpu_alert",
        "context": """SOP-001: Prosedur Handling CPU Alert
1. Jika CPU > 90% selama > 5 menit, lakukan:
   a. Identifikasi process dengan top command
   b. Check cron job dengan crontab -l
   c. Jika process adalah ETL job, biarkan selesai
   d. Jika process tidak dikenal, kill process
   e. Eskalasi ke tim jika tidak resolve dalam 10 menit
2. Jika CPU > 80% selama > 15 menit, lakukan:
   a. Monitor trend
   b. Check recent deployments
   c. Eskalasi jika trend meningkat
3. Dokumentasikan semua tindakan di incident log""",
        "questions": [
            {
                "question": "CPU server srv-web-01 95% selama 7 menit. Apa yang harus dilakukan sesuai SOP?",
                "expected_keywords": ["top", "process", "cron", "kill", "eskalasi", "10"],
                "expected_from_context": ["top", "cron", "kill", "eskalasi"],
            },
            {
                "question": "CPU 85% selama 20 menit. Apa langkahnya?",
                "expected_keywords": ["monitor", "trend", "deployment", "eskalasi"],
                "expected_from_context": ["monitor", "trend", "deployment"],
            },
        ],
    },
    {
        "name": "sop_memory_leak",
        "context": """SOP-002: Prosedur Handling Memory Leak
1. Tanda-tanda memory leak:
   a. Memory usage terus meningkat tanpa turun
   b. GC (Garbage Collection) frequency meningkat
   c. Swap usage meningkat
2. Langkah diagnosis:
   a. Check memory trend 24 jam terakhir
   b. Identifikasi process dengan memory usage tertinggi
   c. Check application logs untuk memory-related errors
   d. Run heap dump analysis jika Java application
3. Langkah mitigasi:
   a. Restart application service
   b. Jika leak persist, restart server
   c. Escalate ke development team untuk fix
4. Prevention:
   a. Set memory alert threshold di 80%
   b. Monitor memory trend weekly
   c. Review application memory usage monthly""",
        "questions": [
            {
                "question": "Memory server srv-app-05 terus naik dari 60% ke 90% dalam 6 jam. Apa yang harus dilakukan?",
                "expected_keywords": ["memory", "leak", "restart", "service", "heap", "escalate"],
                "expected_from_context": ["restart", "service", "heap", "escalate"],
            },
            {
                "question": "Apa tanda-tanda memory leak?",
                "expected_keywords": ["meningkat", "gc", "garbage", "swap"],
                "expected_from_context": ["meningkat", "gc", "swap"],
            },
        ],
    },
    {
        "name": "sop_disk_alert",
        "context": """SOP-003: Prosedur Handling Disk Alert
1. Jika disk usage > 90%:
   a. Check large files dengan du -sh /*
   b. Clean old logs (older than 30 days)
   c. Check untuk core dumps
   d. Jika masih > 90%, escalate ke storage team
2. Jika disk I/O > 2000 IOPS:
   a. Check untuk backup process
   b. Check untuk database queries berat
   c. Check untuk log writing berlebihan
   d. Jika I/O > 5000 selama > 10 menit, escalate
3. RAID degraded:
   a. Check SMART status dengan smartctl
   b. Identify failed disk
   c. Replace disk dan rebuild RAID
   d. Monitor rebuild progress""",
        "questions": [
            {
                "question": "Disk usage srv-db-01 92%. Apa langkahnya?",
                "expected_keywords": ["large", "files", "clean", "logs", "core", "dump", "escalate"],
                "expected_from_context": ["clean", "logs", "core", "dump", "escalate"],
            },
            {
                "question": "Disk I/O 3000 IOPS selama 15 menit. Apa yang harus dilakukan?",
                "expected_keywords": ["backup", "database", "log", "writing", "escalate"],
                "expected_from_context": ["backup", "database", "log", "escalate"],
            },
        ],
    },
]


def run_test(client: OpenAI, model: str, test_config: dict) -> dict:
    """Run all RAG tests and return results."""
    results = []
    total_score = 0
    max_score = 0

    for rag_context in RAG_CONTEXTS:
        for question in rag_context["questions"]:
            max_score += 1
            try:
                # Build RAG prompt
                prompt = f"""Based on the following SOP document, answer the question.

[Context]
{rag_context["context"]}

---

[Question]
{question["question"]}

[Answer based on the SOP document above. Be specific and cite the SOP steps.]"""

                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a DCIM assistant. Answer questions based on the provided SOP document."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=test_config.get("temperature", 0.3),
                    max_tokens=test_config.get("max_tokens", 1024),
                )

                content = response.choices[0].message.content.strip()
                score = _evaluate_rag(question, content)
                total_score += score

                results.append({
                    "test": f"{rag_context['name']}_{question['question'][:30]}",
                    "score": score,
                    "response_preview": content[:200] if content else "",
                })

            except Exception as e:
                results.append({
                    "test": f"{rag_context['name']}_{question['question'][:30]}",
                    "score": 0.0,
                    "error": str(e),
                })

    final_score = total_score / max_score if max_score > 0 else 0.0

    return {
        "capability": "rag",
        "score": round(final_score, 3),
        "total_tests": max_score,
        "passed": sum(1 for r in results if r["score"] > 0),
        "results": results,
    }


def _evaluate_rag(question: dict, content: str) -> float:
    """Evaluate RAG answer quality."""
    score = 0.0
    content_lower = content.lower()

    # Check if answer contains expected keywords from context
    expected_from_context = question.get("expected_from_context", [])
    if expected_from_context:
        context_matches = sum(1 for kw in expected_from_context if kw.lower() in content_lower)
        context_score = context_matches / len(expected_from_context)
        score += context_score * 0.6  # 60% weight for context usage

    # Check if answer contains general expected keywords
    expected_keywords = question.get("expected_keywords", [])
    if expected_keywords:
        keyword_matches = sum(1 for kw in expected_keywords if kw.lower() in content_lower)
        keyword_score = keyword_matches / len(expected_keywords)
        score += keyword_score * 0.4  # 40% weight for answer completeness

    return min(score, 1.0)
