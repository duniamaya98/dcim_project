"""
Scoring utilities for model specification tests
"""


def calculate_rating(score: float) -> str:
    """Convert numeric score to rating string."""
    if score >= 0.9:
        return "✅ Perfect"
    elif score >= 0.75:
        return "✅ Good"
    elif score >= 0.5:
        return "🟡 Acceptable"
    elif score >= 0.25:
        return "🔴 Poor"
    else:
        return "❌ Failed"


def calculate_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 0.9:
        return "A"
    elif score >= 0.8:
        return "B+"
    elif score >= 0.7:
        return "B"
    elif score >= 0.6:
        return "C+"
    elif score >= 0.5:
        return "C"
    elif score >= 0.4:
        return "D+"
    elif score >= 0.3:
        return "D"
    else:
        return "F"


def aggregate_scores(results: list) -> dict:
    """Aggregate scores from multiple test results."""
    if not results:
        return {
            "total_score": 0.0,
            "average_score": 0.0,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
        }

    total_score = sum(r.get("score", 0.0) for r in results)
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get("score", 0.0) >= 0.5)
    failed_tests = total_tests - passed_tests

    return {
        "total_score": round(total_score, 3),
        "average_score": round(total_score / total_tests, 3) if total_tests > 0 else 0.0,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "pass_rate": round(passed_tests / total_tests, 3) if total_tests > 0 else 0.0,
    }


def rank_capabilities(results: list) -> list:
    """Rank capabilities by score."""
    sorted_results = sorted(results, key=lambda x: x.get("score", 0.0), reverse=True)
    for i, result in enumerate(sorted_results, 1):
        result["rank"] = i
    return sorted_results
