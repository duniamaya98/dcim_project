"""
Report generation utilities for model specification tests
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from utils.scoring import calculate_rating, calculate_grade, aggregate_scores, rank_capabilities


def generate_markdown_report(
    model_name: str,
    results: List[Dict[str, Any]],
    output_path: str
) -> str:
    """Generate a markdown report from test results."""
    
    # Aggregate scores
    aggregated = aggregate_scores(results)
    ranked = rank_capabilities(results)
    
    # Build report
    report_lines = []
    
    # Header
    report_lines.append(f"# Model Specification Test Report: {model_name}")
    report_lines.append("")
    report_lines.append(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Model:** {model_name}")
    report_lines.append("")
    
    # Summary
    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append(f"- **Total Score:** {aggregated['total_score']:.3f}")
    report_lines.append(f"- **Average Score:** {aggregated['average_score']:.3f}")
    report_lines.append(f"- **Grade:** {calculate_grade(aggregated['average_score'])}")
    report_lines.append(f"- **Rating:** {calculate_rating(aggregated['average_score'])}")
    report_lines.append(f"- **Total Tests:** {aggregated['total_tests']}")
    report_lines.append(f"- **Passed:** {aggregated['passed_tests']}")
    report_lines.append(f"- **Failed:** {aggregated['failed_tests']}")
    report_lines.append(f"- **Pass Rate:** {aggregated['pass_rate']:.1%}")
    report_lines.append("")
    
    # Detailed Results
    report_lines.append("## Detailed Results")
    report_lines.append("")
    report_lines.append("| Rank | Capability | Score | Rating | Grade |")
    report_lines.append("|------|------------|-------|--------|-------|")
    
    for result in ranked:
        capability = result.get("capability", "Unknown")
        score = result.get("score", 0.0)
        rating = calculate_rating(score)
        grade = calculate_grade(score)
        rank = result.get("rank", "-")
        
        report_lines.append(f"| {rank} | {capability} | {score:.3f} | {rating} | {grade} |")
    
    report_lines.append("")
    
    # Failed Tests
    failed_results = [r for r in results if r.get("score", 0.0) < 0.5]
    if failed_results:
        report_lines.append("## Failed Tests (Score < 0.5)")
        report_lines.append("")
        for result in failed_results:
            capability = result.get("capability", "Unknown")
            score = result.get("score", 0.0)
            report_lines.append(f"### {capability} (Score: {score:.3f})")
            report_lines.append("")
            
            # Add test details if available
            if "test_results" in result:
                for test in result["test_results"]:
                    test_name = test.get("test", "Unknown")
                    test_score = test.get("score", 0.0)
                    report_lines.append(f"- **{test_name}**: {test_score:.3f}")
            
            report_lines.append("")
    
    # Write report
    report_content = "\n".join(report_lines)
    Path(output_path).write_text(report_content, encoding="utf-8")
    
    return report_content


def generate_json_report(
    model_name: str,
    results: List[Dict[str, Any]],
    output_path: str
) -> Dict[str, Any]:
    """Generate a JSON report from test results."""
    
    # Aggregate scores
    aggregated = aggregate_scores(results)
    ranked = rank_capabilities(results)
    
    # Build report data
    report_data = {
        "model_name": model_name,
        "test_date": datetime.now().isoformat(),
        "summary": aggregated,
        "grade": calculate_grade(aggregated["average_score"]),
        "rating": calculate_rating(aggregated["average_score"]),
        "capabilities": ranked,
    }
    
    # Write report
    Path(output_path).write_text(
        json.dumps(report_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    return report_data


def generate_comparison_report(
    results_by_model: Dict[str, List[Dict[str, Any]]],
    output_path: str
) -> str:
    """Generate a comparison report across multiple models."""
    
    report_lines = []
    
    # Header
    report_lines.append("# Model Comparison Report")
    report_lines.append("")
    report_lines.append(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Models Tested:** {len(results_by_model)}")
    report_lines.append("")
    
    # Summary table
    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append("| Model | Total Score | Average | Grade | Rating | Pass Rate |")
    report_lines.append("|-------|-------------|---------|-------|--------|-----------|")
    
    model_summaries = []
    for model_name, results in results_by_model.items():
        aggregated = aggregate_scores(results)
        grade = calculate_grade(aggregated["average_score"])
        rating = calculate_rating(aggregated["average_score"])
        
        model_summaries.append({
            "model": model_name,
            "total_score": aggregated["total_score"],
            "average": aggregated["average_score"],
            "grade": grade,
            "rating": rating,
            "pass_rate": aggregated["pass_rate"],
        })
        
        report_lines.append(
            f"| {model_name} | {aggregated['total_score']:.3f} | "
            f"{aggregated['average_score']:.3f} | {grade} | {rating} | "
            f"{aggregated['pass_rate']:.1%} |"
        )
    
    report_lines.append("")
    
    # Capability comparison
    report_lines.append("## Capability Comparison")
    report_lines.append("")
    
    # Get all unique capabilities
    all_capabilities = set()
    for results in results_by_model.values():
        for result in results:
            all_capabilities.add(result.get("capability", "Unknown"))
    
    # Build comparison table
    header = "| Capability |"
    separator = "|------------|"
    for model_name in results_by_model.keys():
        header += f" {model_name} |"
        separator += "-------|"
    
    report_lines.append(header)
    report_lines.append(separator)
    
    for capability in sorted(all_capabilities):
        row = f"| {capability} |"
        for model_name, results in results_by_model.items():
            # Find capability score
            score = 0.0
            for result in results:
                if result.get("capability") == capability:
                    score = result.get("score", 0.0)
                    break
            row += f" {score:.3f} |"
        report_lines.append(row)
    
    report_lines.append("")
    
    # Write report
    report_content = "\n".join(report_lines)
    Path(output_path).write_text(report_content, encoding="utf-8")
    
    return report_content
