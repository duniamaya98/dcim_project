#!/usr/bin/env python3
"""
Model Capability Comparison Tool

Script ini menganalisis hasil test dari multiple model dan membuat:
1. Perbandingan performa per capability
2. Rekomendasi model berdasarkan kebutuhan capability
3. Matriks perbandingan yang mudah dibaca
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

def load_all_results(results_dir: str) -> Dict[str, Dict]:
    """Load all JSON result files from results directory"""
    results = {}

    for json_file in Path(results_dir).glob("*.json"):
        if "comparison" in json_file.name:
            continue

        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                model_name = data['model_name']
                results[model_name] = data
        except Exception as e:
            print(f"Error loading {json_file}: {e}")

    return results

def extract_capability_scores(results: Dict[str, Dict]) -> Dict[str, Dict[str, float]]:
    """Extract capability scores from results"""
    capability_scores = defaultdict(dict)

    for model_name, model_data in results.items():
        for capability in model_data['capabilities']:
            cap_name = capability['capability']
            score = capability['score']
            capability_scores[cap_name][model_name] = score

    return capability_scores

def rank_models_by_capability(capability_scores: Dict[str, Dict[str, float]]) -> Dict[str, List[Tuple[str, float]]]:
    """Rank models for each capability"""
    rankings = {}

    for capability, model_scores in capability_scores.items():
        # Sort by score descending
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        rankings[capability] = sorted_models

    return rankings

def generate_comparison_matrix(rankings: Dict[str, List[Tuple[str, float]]]) -> str:
    """Generate markdown comparison matrix"""
    matrix = "# Model Capability Comparison Matrix\n\n"

    matrix += "| Capability | Best Model | Score | Runner-up | Score |\n"
    matrix += "|------------|------------|-------|-----------|-------|\n"

    for capability, ranked_models in sorted(rankings.items()):
        best_model, best_score = ranked_models[0]
        if len(ranked_models) > 1:
            runner_up, runner_score = ranked_models[1]
        else:
            runner_up, runner_score = "-", 0.0

        # Format capability name for display
        display_name = capability.replace('_', ' ').title()

        matrix += f"| {display_name} | {best_model} | {best_score:.3f} | {runner_up} | {runner_score:.3f} |\n"

    return matrix

def generate_model_recommendation(rankings: Dict[str, List[Tuple[str, float]]],
                                required_capabilities: Dict[str, int]) -> str:
    """Generate model recommendation based on required capabilities"""
    recommendation = "# Model Recommendation Engine\n\n"

    # Add use case description
    recommendation += "**Use Case Requirements:**\n"
    for capability, importance in required_capabilities.items():
        importance_text = {
            1: "Low",
            2: "Medium-Low",
            3: "Medium",
            4: "Medium-High",
            5: "High"
        }[importance]
        recommendation += f"- {capability.replace('_', ' ').title()}: {importance_text}\n"
    recommendation += "\n"

    # Score each model based on requirements
    model_scores = defaultdict(float)
    capability_weights = {cap: weight for cap, weight in required_capabilities.items()}

    # Get all models
    all_models = set()
    for ranked_models in rankings.values():
        for model, _ in ranked_models:
            all_models.add(model)

    # Calculate weighted scores
    for model in all_models:
        total_score = 0
        total_weight = 0

        for capability, weight in capability_weights.items():
            if capability in rankings:
                # Find model's score for this capability
                model_score = 0
                for m, s in rankings[capability]:
                    if m == model:
                        model_score = s
                        break

                total_score += model_score * weight
                total_weight += weight

        if total_weight > 0:
            model_scores[model] = total_score / total_weight

    # Rank models by weighted score
    ranked_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)

    # Generate recommendation
    recommendation += "**Recommendations:**\n"
    for rank, (model, score) in enumerate(ranked_models, 1):
        grade = get_grade(score)
        recommendation += f"\n{rank}. **{model}** (Score: {score:.2f}/5.0 - {grade})\n"

        # Show capability breakdown
        for capability, weight in sorted(capability_weights.items(), key=lambda x: x[1], reverse=True):
            model_cap_score = 0
            for m, s in rankings[capability]:
                if m == model:
                    model_cap_score = s
                    break

            level = get_capability_level(model_cap_score)
            importance = {1: "Low", 2: "Medium-Low", 3: "Medium", 4: "Medium-High", 5: "High"}[weight]
            recommendation += f"   - {capability.replace('_', ' ').title()}: {model_cap_score:.3f} (Level {level}, {importance})\n"

    return recommendation

def get_grade(score: float) -> str:
    """Convert score to letter grade"""
    if score >= 4.5:
        return "A+ (Excellent)"
    elif score >= 4.0:
        return "A (Very Good)"
    elif score >= 3.5:
        return "B+ (Good)"
    elif score >= 3.0:
        return "B (Above Average)"
    elif score >= 2.5:
        return "C+ (Average)"
    elif score >= 2.0:
        return "C (Below Average)"
    elif score >= 1.5:
        return "D+ (Poor)"
    elif score >= 1.0:
        return "D (Very Poor)"
    else:
        return "F (Failed)"

def get_capability_level(score: float) -> int:
    """Convert capability score to level 1-5"""
    if score >= 0.9:
        return 5  # Master
    elif score >= 0.7:
        return 4  # Expert
    elif score >= 0.5:
        return 3  # Advanced
    elif score >= 0.3:
        return 2  # Intermediate
    else:
        return 1  # Basic

def main():
    results_dir = "results/reports"
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)

    # Load all results
    print("Loading test results...")
    results = load_all_results(results_dir)

    if not results:
        print("No results found!")
        return

    print(f"Found {len(results)} model results")

    # Extract capability scores
    capability_scores = extract_capability_scores(results)
    print(f"Found {len(capability_scores)} capabilities")

    # Rank models by capability
    rankings = rank_models_by_capability(capability_scores)

    # Generate comparison matrix
    matrix = generate_comparison_matrix(rankings)

    # Generate recommendations for common use cases
    use_cases = [
        {
            "name": "General Purpose AI Assistant",
            "requirements": {
                "tool_calling": 5,
                "rag": 4,
                "messaging": 4,
                "memory": 3,
                "session_search": 3
            }
        },
        {
            "name": "IT Operations Monitoring",
            "requirements": {
                "tool_calling": 5,
                "terminal": 4,
                "file_operations": 4,
                "cron": 3,
                "agent": 3
            }
        },
        {
            "name": "Multimodal Analysis",
            "requirements": {
                "vision": 5,
                "tool_calling": 4,
                "rag": 4,
                "mixture_of_agents": 4,
                "delegation": 3
            }
        },
        {
            "name": "Code Generation",
            "requirements": {
                "code_execution": 5,
                "tool_calling": 4,
                "file_operations": 4,
                "terminal": 3,
                "json_mode": 3
            }
        }
    ]

    # Generate all recommendations
    recommendations = ""
    for use_case in use_cases:
        recommendations += f"## {use_case['name']}\n\n"
        recommendations += generate_model_recommendation(rankings, use_case['requirements'])
        recommendations += "\n---\n\n"

    # Save results
    comparison_file = os.path.join(output_dir, "model_comparison_matrix.md")
    with open(comparison_file, 'w') as f:
        f.write(matrix)

    recommendation_file = os.path.join(output_dir, "model_recommendations.md")
    with open(recommendation_file, 'w') as f:
        f.write(recommendations)

    print(f"\nResults saved to:")
    print(f"- {comparison_file}")
    print(f"- {recommendation_file}")
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()