#!/usr/bin/env python3
"""
Level-Based Capability Testing System

Sistem pengujian yang menguji setiap capability di berbagai level kesulitan,
mirip dengan pengujian motor dengan beban berbeda.

Setiap capability diuji di 5 level:
- Level 1: Tugas sederhana, beban ringan (25% kapasitas)
- Level 2: Tugas sedang, beban normal (50% kapasitas)
- Level 3: Tugas kompleks, beban berat (75% kapasitas)
- Level 4: Tugas sangat kompleks, beban maksimal (100% kapasitas)
- Level 5: Tugas ekstrem, beban melebihi spesifikasi (125% kapasitas)

Sistem ini memberikan insight granular tentang:
- Seberapa jauh model dapat "berjalan" di masing-masing level
- Di level mana model mulai gagal
- Kemampuan maksimal model untuk setiap capability
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import IntEnum
import statistics
from datetime import datetime

class TestLevel(IntEnum):
    LEVEL_1 = 1  # Basic - 25% capacity
    LEVEL_2 = 2  # Intermediate - 50% capacity
    LEVEL_3 = 3  # Advanced - 75% capacity
    LEVEL_4 = 4  # Expert - 100% capacity
    LEVEL_5 = 5  # Master - 125% capacity

@dataclass
class LevelTestResult:
    """Hasil pengujian untuk satu level spesifik"""
    level: TestLevel
    test_name: str
    success: bool
    score: float  # 0.0 - 1.0
    distance: float  # Seberapa jauh model dapat "berjalan" (0-100%)
    max_possible_distance: float = 100.0  # Jarak maksimal untuk level ini
    notes: str = ""

@dataclass
class CapabilityLevelResults:
    """Hasil pengujian untuk satu capability di semua level"""
    capability: str
    level_results: Dict[TestLevel, List[LevelTestResult]]
    overall_score: float = 0.0
    max_completed_level: Optional[TestLevel] = None
    failure_point: Optional[TestLevel] = None

class LevelBasedTester:
    """Sistem pengujian level-based untuk model AI"""

    def __init__(self):
        self.capability_levels = self._define_levels()
        self.results = {}

    def _define_levels(self) -> Dict[str, Dict[TestLevel, List[Dict]]]:
        """Definisi level-level pengujian untuk setiap capability"""
        return {
            "tool_calling": {
                TestLevel.LEVEL_1: [
                    {"name": "single_tool_call", "distance_weight": 25},
                    {"name": "alert_tool_call", "distance_weight": 25}
                ],
                TestLevel.LEVEL_2: [
                    {"name": "log_check_tool_call", "distance_weight": 30},
                    {"name": "multi_tool_selection", "distance_weight": 40}
                ],
                TestLevel.LEVEL_3: [
                    {"name": "complex_multi_tool", "distance_weight": 50},
                    {"name": "conditional_tool_calling", "distance_weight": 50}
                ],
                TestLevel.LEVEL_4: [
                    {"name": "multi_step_workflow", "distance_weight": 75},
                    {"name": "error_handling_tools", "distance_weight": 75}
                ],
                TestLevel.LEVEL_5: [
                    {"name": "extreme_multi_tool", "distance_weight": 100},
                    {"name": "parallel_tool_execution", "distance_weight": 100}
                ]
            },
            "vision": {
                TestLevel.LEVEL_1: [
                    {"name": "simple_image_description", "distance_weight": 25},
                    {"name": "basic_object_detection", "distance_weight": 25}
                ],
                TestLevel.LEVEL_2: [
                    {"name": "dashboard_analysis", "distance_weight": 40},
                    {"name": "alert_interpretation", "distance_weight": 40}
                ],
                TestLevel.LEVEL_3: [
                    {"name": "complex_dashboard_analysis", "distance_weight": 60},
                    {"name": "multi_image_comparison", "distance_weight": 60}
                ],
                TestLevel.LEVEL_4: [
                    {"name": "detailed_visual_analysis", "distance_weight": 80},
                    {"name": "visual_data_extraction", "distance_weight": 80}
                ],
                TestLevel.LEVEL_5: [
                    {"name": "extreme_visual_reasoning", "distance_weight": 100},
                    {"name": "3d_visualization_interpretation", "distance_weight": 100}
                ]
            },
            "rag": {
                TestLevel.LEVEL_1: [
                    {"name": "simple_document_retrieval", "distance_weight": 25},
                    {"name": "basic_question_answering", "distance_weight": 25}
                ],
                TestLevel.LEVEL_2: [
                    {"name": "multi_document_retrieval", "distance_weight": 40},
                    {"name": "contextual_answering", "distance_weight": 40}
                ],
                TestLevel.LEVEL_3: [
                    {"name": "complex_rag_chain", "distance_weight": 60},
                    {"name": "multi_hop_reasoning", "distance_weight": 60}
                ],
                TestLevel.LEVEL_4: [
                    {"name": "advanced_context_understanding", "distance_weight": 80},
                    {"name": "document_comparison", "distance_weight": 80}
                ],
                TestLevel.LEVEL_5: [
                    {"name": "extreme_rag_scenario", "distance_weight": 100},
                    {"name": "multi_source_synthesis", "distance_weight": 100}
                ]
            },
            "code_execution": {
                TestLevel.LEVEL_1: [
                    {"name": "simple_python_script", "distance_weight": 25},
                    {"name": "basic_bash_command", "distance_weight": 25}
                ],
                TestLevel.LEVEL_2: [
                    {"name": "python_cpu_monitor", "distance_weight": 40},
                    {"name": "bash_log_parser", "distance_weight": 40}
                ],
                TestLevel.LEVEL_3: [
                    {"name": "complex_script_generation", "distance_weight": 60},
                    {"name": "multi_language_execution", "distance_weight": 60}
                ],
                TestLevel.LEVEL_4: [
                    {"name": "advanced_system_script", "distance_weight": 80},
                    {"name": "error_handling_code", "distance_weight": 80}
                ],
                TestLevel.LEVEL_5: [
                    {"name": "extreme_code_generation", "distance_weight": 100},
                    {"name": "parallel_execution", "distance_weight": 100}
                ]
            },
            "terminal": {
                TestLevel.LEVEL_1: [
                    {"name": "simple_command_execution", "distance_weight": 25},
                    {"name": "basic_process_listing", "distance_weight": 25}
                ],
                TestLevel.LEVEL_2: [
                    {"name": "check_cpu_usage", "distance_weight": 40},
                    {"name": "list_processes", "distance_weight": 40}
                ],
                TestLevel.LEVEL_3: [
                    {"name": "complex_terminal_workflow", "distance_weight": 60},
                    {"name": "multi_command_sequence", "distance_weight": 60}
                ],
                TestLevel.LEVEL_4: [
                    {"name": "advanced_system_monitoring", "distance_weight": 80},
                    {"name": "error_recovery_commands", "distance_weight": 80}
                ],
                TestLevel.LEVEL_5: [
                    {"name": "extreme_terminal_automation", "distance_weight": 100},
                    {"name": "parallel_command_execution", "distance_weight": 100}
                ]
            }
        }

    def run_level_tests(self, model_name: str, test_data: Dict) -> Dict[str, CapabilityLevelResults]:
        """Jalankan pengujian level-based untuk model"""
        results = {}

        for capability, level_tests in self.capability_levels.items():
            if capability not in test_data:
                continue

            capability_results = self._test_capability_levels(capability, level_tests, test_data[capability])
            results[capability] = capability_results

        return results

    def _test_capability_levels(self, capability: str, level_tests: Dict[TestLevel, List[Dict]],
                              test_data: List[Dict]) -> CapabilityLevelResults:
        """Test satu capability di semua level"""
        level_results = {}
        total_distance = 0
        max_completed_level = None
        failure_point = None

        # Group test data by level
        test_data_by_name = {test['test']: test for test in test_data}

        for level, tests in sorted(level_tests.items(), key=lambda x: x[0].value):
            level_test_results = []

            for test_config in tests:
                test_name = test_config['name']
                distance_weight = test_config['distance_weight']

                if test_name in test_data_by_name:
                    test_data_item = test_data_by_name[test_name]
                    score = test_data_item.get('score', 0.0)
                    success = score >= 0.5  # Consider success if score >= 50%

                    # Calculate distance based on score and weight
                    distance = score * distance_weight

                    level_test_results.append(LevelTestResult(
                        level=level,
                        test_name=test_name,
                        success=success,
                        score=score,
                        distance=distance,
                        max_possible_distance=distance_weight,
                        notes=f"Score: {score:.3f}"
                    ))
                else:
                    # Test not found - consider as failed
                    level_test_results.append(LevelTestResult(
                        level=level,
                        test_name=test_name,
                        success=False,
                        score=0.0,
                        distance=0.0,
                        max_possible_distance=distance_weight,
                        notes="Test not attempted"
                    ))

            level_results[level] = level_test_results

            # Calculate total distance for this level
            level_distance = sum(r.distance for r in level_test_results)
            total_distance += level_distance

            # Determine completion status
            if level_distance > 0:
                max_completed_level = level
            else:
                if failure_point is None:
                    failure_point = level

        # Calculate overall score (0-1 scale)
        max_possible_distance = sum(
            sum(test['distance_weight'] for test in tests)
            for tests in level_tests.values()
        )
        overall_score = total_distance / max_possible_distance if max_possible_distance > 0 else 0

        return CapabilityLevelResults(
            capability=capability,
            level_results=level_results,
            overall_score=overall_score,
            max_completed_level=max_completed_level,
            failure_point=failure_point
        )

    def generate_level_report(self, model_name: str, capability_results: Dict[str, CapabilityLevelResults]) -> str:
        """Generate detailed level-based report"""
        report = f"# Level-Based Capability Test Report\n\n"
        report += f"**Model:** {model_name}\n"
        report += f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Summary section
        report += "## Summary\n\n"
        report += "| Capability | Overall Score | Max Level | Failure Point | Distance Covered |\n"
        report += "|------------|---------------|-----------|---------------|------------------|\n"

        for capability, result in capability_results.items():
            max_level = result.max_completed_level.value if result.max_completed_level else 0
            failure_level = result.failure_point.value if result.failure_point else "N/A"
            distance_pct = result.overall_score * 100

            report += f"| {capability.replace('_', ' ').title()} | {result.overall_score:.3f} | Level {max_level} | Level {failure_level} | {distance_pct:.1f}% |\n"

        report += "\n"

        # Detailed level analysis
        for capability, result in capability_results.items():
            report += f"## {capability.replace('_', ' ').title()}\n\n"
            report += f"**Overall Score:** {result.overall_score:.3f}/1.000\n"
            report += f"**Max Completed Level:** Level {result.max_completed_level.value if result.max_completed_level else 0}\n"
            report += f"**Failure Point:** Level {result.failure_point.value if result.failure_point else 'N/A'}\n"
            report += f"**Distance Covered:** {result.overall_score * 100:.1f}%\n\n"

            # Level-by-level breakdown
            for level in sorted(result.level_results.keys(), key=lambda x: x.value):
                level_tests = result.level_results[level]
                level_distance = sum(r.distance for r in level_tests)
                max_level_distance = sum(r.max_possible_distance for r in level_tests)
                level_score = level_distance / max_level_distance if max_level_distance > 0 else 0

                report += f"### Level {level.value} - {self._get_level_description(level)}\n\n"
                report += f"**Level Score:** {level_score:.3f} ({level_distance:.1f}/{max_level_distance:.1f} distance)\n\n"

                for test_result in level_tests:
                    status = "✅ PASS" if test_result.success else "❌ FAIL"
                    distance_pct = (test_result.distance / test_result.max_possible_distance * 100) if test_result.max_possible_distance > 0 else 0
                    report += f"- **{test_result.test_name}**: {status} (Score: {test_result.score:.3f}, Distance: {distance_pct:.1f}%)\n"
                    if test_result.notes:
                        report += f"  - {test_result.notes}\n"

                report += "\n"

        return report

    def _get_level_description(self, level: TestLevel) -> str:
        """Get description for level"""
        descriptions = {
            TestLevel.LEVEL_1: "Basic Tasks - 25% Capacity (Simple operations, minimal complexity)",
            TestLevel.LEVEL_2: "Intermediate Tasks - 50% Capacity (Standard operations, moderate complexity)",
            TestLevel.LEVEL_3: "Advanced Tasks - 75% Capacity (Complex operations, high complexity)",
            TestLevel.LEVEL_4: "Expert Tasks - 100% Capacity (Very complex operations, maximum complexity)",
            TestLevel.LEVEL_5: "Master Tasks - 125% Capacity (Extreme operations, beyond normal specifications)"
        }
        return descriptions[level]

    def analyze_multiple_models(self, results_dir: str) -> Dict[str, Dict[str, CapabilityLevelResults]]:
        """Analyze multiple models from result files"""
        all_model_results = {}

        for json_file in Path(results_dir).glob("*.json"):
            if "comparison" in json_file.name or "level" in json_file.name:
                continue

            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    model_name = data['model_name']

                    # Extract capability test data
                    capability_data = {}
                    for capability in data['capabilities']:
                        cap_name = capability['capability']
                        capability_data[cap_name] = capability['results']

                    # Run level-based analysis
                    model_results = self.run_level_tests(model_name, capability_data)
                    all_model_results[model_name] = model_results

                    print(f"Processed: {model_name}")

            except Exception as e:
                print(f"Error processing {json_file}: {e}")

        return all_model_results

    def generate_comparative_level_report(self, model_results: Dict[str, Dict[str, CapabilityLevelResults]]) -> str:
        """Generate comparative report across multiple models"""
        report = "# Comparative Level-Based Analysis\n\n"
        report += f"**Models Analyzed:** {len(model_results)}\n"
        report += f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Find all capabilities
        all_capabilities = set()
        for model_data in model_results.values():
            for capability in model_data.keys():
                all_capabilities.add(capability)

        # Capability comparison matrix
        report += "## Capability Comparison Matrix\n\n"
        report += "| Capability | Best Model | Score | Max Level | Distance |\n"
        report += "|------------|------------|-------|-----------|----------|\n"

        for capability in sorted(all_capabilities):
            best_model = None
            best_score = 0
            best_max_level = 0
            best_distance = 0

            for model_name, model_data in model_results.items():
                if capability in model_data:
                    result = model_data[capability]
                    if result.overall_score > best_score:
                        best_score = result.overall_score
                        best_model = model_name
                        best_max_level = result.max_completed_level.value if result.max_completed_level else 0
                        best_distance = result.overall_score * 100

            if best_model:
                report += f"| {capability.replace('_', ' ').title()} | {best_model} | {best_score:.3f} | Level {best_max_level} | {best_distance:.1f}% |\n"

        report += "\n"

        # Model recommendations based on use cases
        use_cases = [
            {
                "name": "General Purpose Assistant",
                "required_capabilities": {
                    "tool_calling": TestLevel.LEVEL_4,
                    "rag": TestLevel.LEVEL_3,
                    "messaging": TestLevel.LEVEL_3
                }
            },
            {
                "name": "IT Operations Specialist",
                "required_capabilities": {
                    "tool_calling": TestLevel.LEVEL_5,
                    "terminal": TestLevel.LEVEL_4,
                    "file_operations": TestLevel.LEVEL_3
                }
            },
            {
                "name": "Multimodal Analyst",
                "required_capabilities": {
                    "vision": TestLevel.LEVEL_4,
                    "tool_calling": TestLevel.LEVEL_3,
                    "rag": TestLevel.LEVEL_3
                }
            }
        ]

        for use_case in use_cases:
            report += f"## {use_case['name']}\n\n"
            report += "**Required Capabilities:**\n"
            for cap, level in use_case['required_capabilities'].items():
                report += f"- {cap.replace('_', ' ').title()}: Level {level.value}\n"
            report += "\n"

            # Find models that meet requirements
            qualified_models = []
            for model_name, model_data in model_results.items():
                meets_requirements = True
                for cap, required_level in use_case['required_capabilities'].items():
                    if cap in model_data:
                        result = model_data[cap]
                        if not result.max_completed_level or result.max_completed_level.value < required_level.value:
                            meets_requirements = False
                            break
                    else:
                        meets_requirements = False
                        break

                if meets_requirements:
                    qualified_models.append(model_name)

            if qualified_models:
                report += "**Qualified Models:**\n"
                for model in qualified_models:
                    report += f"- {model}\n"
            else:
                report += "**No models meet all requirements**\n"

            report += "\n"

        return report

def main():
    """Main execution"""
    tester = LevelBasedTester()
    results_dir = "results/reports"

    print("Running Level-Based Capability Analysis...")
    print("=" * 50)

    # Analyze all models
    model_results = tester.analyze_multiple_models(results_dir)

    if not model_results:
        print("No model results found!")
        return

    print(f"\nAnalyzed {len(model_results)} models")
    print("=" * 50)

    # Generate individual reports
    output_dir = "results/level_analysis"
    os.makedirs(output_dir, exist_ok=True)

    for model_name, results in model_results.items():
        report = tester.generate_level_report(model_name, results)
        filename = f"{output_dir}/{model_name.replace('/', '_').replace(':', '_')}_level_analysis.md"
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Saved: {filename}")

    # Generate comparative report
    comparative_report = tester.generate_comparative_level_report(model_results)
    comparative_filename = f"{output_dir}/comparative_level_analysis.md"
    with open(comparative_filename, 'w') as f:
        f.write(comparative_report)
    print(f"Saved: {comparative_filename}")

    print("\nLevel-Based Analysis Complete!")
    print(f"Results saved in: {output_dir}")

if __name__ == "__main__":
    main()