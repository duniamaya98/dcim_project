#!/usr/bin/env python3
"""
Level-Based Test Runner

Runner untuk menjalankan pengujian level-based untuk semua 23 capabilities.
Mengintegrasikan dengan test suite yang sudah ada dan menghasilkan laporan granular.

Usage:
    python run_level_tests.py --model "model_name" --level all
    python run_level_tests.py --model "model_name" --level 1 2 3
    python run_level_tests.py --model "model_name" --capability tool_calling vision --level all
    python run_level_tests.py --analyze-all  # Analyze existing test results
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import MODELS, DEFAULT_MODEL, TEST_CONFIG, OUTPUT_DIR, RAW_DIR, REPORT_DIR
from level_test_definitions import (
    LEVEL_DEFINITIONS, LEVEL_METADATA, TestLevel,
    get_level_name, get_level_description, get_level_icon,
    get_all_capabilities, get_capability_description,
    get_tests_for_level, get_total_distance_weight
)

# Auto-detect running models

LEVEL_PASS_THRESHOLD = 0.60

def format_level_badge(level_value: int) -> str:
    """Format level safely, including capabilities that do not pass Level 1."""
    if level_value <= 0:
        return "Level 0 - Not Qualified"
    level = TestLevel(level_value)
    return f"{get_level_icon(level)} Level {level_value} - {get_level_name(level)}"

def recommendation_for_level(level_value: int) -> str:
    """Human-readable usage recommendation for a capability level."""
    recommendations = {
        0: "Tidak direkomendasikan untuk capability ini",
        1: "Cocok untuk tugas sederhana dan validasi dasar",
        2: "Cocok untuk workflow standar dengan risiko rendah",
        3: "Cocok untuk pekerjaan operasional harian yang cukup kompleks",
        4: "Cocok untuk skenario produksi kompleks dengan pengawasan",
        5: "Cocok untuk skenario berat, multi-step, dan penggunaan utama",
    }
    return recommendations.get(level_value, recommendations[0])

def auto_detect_model():
    """Auto-detect model yang sedang running, return model name atau None"""
    try:
        from detect_models import detect_all_models
        detected = detect_all_models()
        # Get first running model
        for platform, models in detected.items():
            for model in models:
                if model["status"] == "running":
                    # Add to MODELS if not exists
                    model_name = model["model_name"]
                    if model_name not in MODELS:
                        MODELS[model_name] = {
                            "base_url": model["base_url"],
                            "api_key": model["api_key"],
                            "platform": model["platform"],
                            "enabled": True,
                        }
                    return model_name
    except Exception:
        pass
    return None

@dataclass
class LevelTestResult:
    """Hasil pengujian untuk satu test case di level tertentu"""
    test_name: str
    level: int
    capability: str
    score: float
    success: bool
    distance_achieved: float
    max_distance: float
    details: Dict[str, Any]
    error: Optional[str] = None

@dataclass
class CapabilityLevelSummary:
    """Summary hasil untuk satu capability di satu level"""
    capability: str
    level: int
    level_name: str
    tests_run: int
    tests_passed: int
    average_score: float
    total_distance_achieved: float
    total_max_distance: float
    distance_percentage: float
    test_results: List[LevelTestResult]

@dataclass
class CapabilitySummary:
    """Summary hasil untuk satu capability di semua level"""
    capability: str
    description: str
    level_summaries: Dict[int, CapabilityLevelSummary]
    max_level_completed: int
    failure_level: Optional[int]
    overall_score: float
    overall_distance_percentage: float
    total_tests: int
    total_passed: int

@dataclass
class ModelLevelReport:
    """Laporan lengkap untuk satu model"""
    model_name: str
    test_date: str
    capability_summaries: Dict[str, CapabilitySummary]
    overall_statistics: Dict[str, Any]

class LevelTestRunner:
    """Runner untuk level-based testing"""

    def __init__(self, model_name: str, model_config: Dict):
        self.model_name = model_name
        self.model_config = model_config
        self.client = self._init_client()
        self.results = {}

    def _init_client(self):
        """Initialize OpenAI client"""
        from openai import OpenAI
        return OpenAI(
            base_url=self.model_config["base_url"],
            api_key=self.model_config["api_key"]
        )

    def run_capability_level_tests(
        self,
        capability: str,
        levels: Optional[List[TestLevel]] = None
    ) -> CapabilitySummary:
        """Run level tests for a specific capability"""
        if levels is None:
            levels = list(TestLevel)

        level_summaries = {}
        max_level_completed = 0
        failure_level = None
        all_test_results = []

        for level in levels:
            tests = get_tests_for_level(capability, level)
            if not tests:
                continue

            level_results = []
            for test_def in tests:
                result = self._run_single_test(capability, level, test_def)
                level_results.append(result)
                all_test_results.append(result)

            # Calculate level summary
            tests_run = len(level_results)
            tests_passed = sum(1 for r in level_results if r.success)
            avg_score = sum(r.score for r in level_results) / tests_run if tests_run > 0 else 0
            total_distance = sum(r.distance_achieved for r in level_results)
            max_distance = sum(r.max_distance for r in level_results)
            distance_pct = (total_distance / max_distance * 100) if max_distance > 0 else 0

            level_summary = CapabilityLevelSummary(
                capability=capability,
                level=level.value,
                level_name=get_level_name(level),
                tests_run=tests_run,
                tests_passed=tests_passed,
                average_score=avg_score,
                total_distance_achieved=total_distance,
                total_max_distance=max_distance,
                distance_percentage=distance_pct,
                test_results=level_results
            )
            level_summaries[level.value] = level_summary

            # Track max level completed and first level that does not meet the pass threshold.
            pass_ratio = tests_passed / tests_run if tests_run else 0
            level_completed = (
                avg_score >= LEVEL_PASS_THRESHOLD
                and distance_pct >= LEVEL_PASS_THRESHOLD * 100
                and pass_ratio >= 0.5
            )
            if level_completed:
                max_level_completed = max(max_level_completed, level.value)
            elif failure_level is None:
                failure_level = level.value

        # Calculate overall capability summary
        total_tests = len(all_test_results)
        total_passed = sum(1 for r in all_test_results if r.success)
        overall_score = sum(r.score for r in all_test_results) / total_tests if total_tests > 0 else 0
        total_distance = sum(r.distance_achieved for r in all_test_results)
        max_total_distance = sum(r.max_distance for r in all_test_results)
        overall_distance_pct = (total_distance / max_total_distance * 100) if max_total_distance > 0 else 0

        return CapabilitySummary(
            capability=capability,
            description=get_capability_description(capability),
            level_summaries=level_summaries,
            max_level_completed=max_level_completed,
            failure_level=failure_level,
            overall_score=overall_score,
            overall_distance_percentage=overall_distance_pct,
            total_tests=total_tests,
            total_passed=total_passed
        )

    def _run_single_test(
        self,
        capability: str,
        level: TestLevel,
        test_def: Dict
    ) -> LevelTestResult:
        """Run a single test case"""
        test_name = test_def["name"]
        max_distance = test_def["distance_weight"]

        try:
            # Import and run the actual test
            score, details = self._execute_test(capability, test_def)

            distance_achieved = score * max_distance
            success = score >= 0.5

            return LevelTestResult(
                test_name=test_name,
                level=level.value,
                capability=capability,
                score=score,
                success=success,
                distance_achieved=distance_achieved,
                max_distance=max_distance,
                details=details
            )

        except Exception as e:
            return LevelTestResult(
                test_name=test_name,
                level=level.value,
                capability=capability,
                score=0.0,
                success=False,
                distance_achieved=0.0,
                max_distance=max_distance,
                details={},
                error=str(e)
            )

    def _execute_test(self, capability: str, test_def: Dict) -> tuple:
        """Execute a test and return (score, details).

        Prefer capability-specific run_single_test when available. For modules that
        only support the old one-shot run_test flow, use a generic level-aware
        executor so every capability in level_test_definitions.py can be tested.
        """
        test_module = self._get_test_module(capability)
        if not test_module:
            return 0.0, {"error": f"No test module for {capability}"}

        try:
            if hasattr(test_module, "run_single_test"):
                result = test_module.run_single_test(self.client, self.model_name, test_def, TEST_CONFIG)
            else:
                result = self._run_generic_level_test(capability, test_def, test_module)
            return result.get("score", 0.0), result
        except Exception as e:
            return 0.0, {"error": str(e), "test_name": test_def.get("name")}

    def _run_generic_level_test(self, capability: str, test_def: Dict, test_module) -> Dict[str, Any]:
        """Run a single level definition without requiring per-module glue code."""
        if capability == "streaming":
            return self._run_streaming_level_test(test_def)

        messages = self._build_messages(test_def, capability)
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": TEST_CONFIG.get("temperature", 0.3),
            "max_tokens": TEST_CONFIG.get("max_tokens", 1024),
        }

        tools = self._tools_for_test(test_def, test_module)
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        if capability in {"json_mode", "structured_output"} or test_def.get("expected_format") == "json":
            kwargs["response_format"] = {"type": "json_object"}

        used_response_format_fallback = False
        try:
            response = self.client.chat.completions.create(**kwargs)
        except Exception:
            if "response_format" not in kwargs:
                raise
            kwargs.pop("response_format")
            used_response_format_fallback = True
            response = self.client.chat.completions.create(**kwargs)

        message = response.choices[0].message
        content = message.content or ""
        tool_calls = message.tool_calls if hasattr(message, "tool_calls") else None
        serialized_tools = self._serialize_tool_calls(tool_calls)
        score, scoring_details = self._score_generic_response(test_def, content, serialized_tools, capability)

        return {
            "score": round(score, 3),
            "test_name": test_def["name"],
            "capability": capability,
            "response_preview": content[:300],
            "tool_calls": serialized_tools,
            "used_response_format_fallback": used_response_format_fallback,
            "scoring_details": scoring_details,
        }

    def _run_streaming_level_test(self, test_def: Dict) -> Dict[str, Any]:
        """Run a level test with streaming enabled and score responsiveness."""
        start_time = time.time()
        first_token_time = None
        chunks = []
        token_count = 0

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self._build_messages(test_def, "streaming"),
            temperature=TEST_CONFIG.get("temperature", 0.3),
            max_tokens=TEST_CONFIG.get("max_tokens", 1024),
            stream=True,
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                if first_token_time is None:
                    first_token_time = time.time()
                chunks.append(chunk.choices[0].delta.content)
                token_count += 1

        total_time = time.time() - start_time
        ttft = first_token_time - start_time if first_token_time else total_time
        content = "".join(chunks)

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

        stream_score = 1.0 if token_count > 1 and total_time > 0 else 0.0
        content_score, content_details = self._score_generic_response(test_def, content, [], "streaming")
        score = (ttft_score * 0.35) + (stream_score * 0.35) + (content_score * 0.30)

        return {
            "score": round(min(score, 1.0), 3),
            "test_name": test_def["name"],
            "response_preview": content[:300],
            "ttft_seconds": round(ttft, 3),
            "total_time_seconds": round(total_time, 3),
            "token_chunks": token_count,
            "scoring_details": {
                "ttft_score": round(ttft_score, 3),
                "stream_score": round(stream_score, 3),
                "content_score": round(content_score, 3),
                **content_details,
            },
        }

    def _build_messages(self, test_def: Dict, capability: str) -> List[Dict[str, Any]]:
        system_prompt = test_def.get("system_prompt")
        if not system_prompt:
            if capability in {"json_mode", "structured_output"} or test_def.get("expected_format") == "json":
                system_prompt = "Respond with valid JSON only. Do not include markdown or prose outside JSON."
            else:
                system_prompt = "You are an IT operations assistant. Answer precisely and follow the user's requested format."

        prompt = test_def.get("prompt", "")
        if test_def.get("context"):
            prompt = f"Context:\n{test_def['context']}\n\nTask:\n{prompt}"
        elif test_def.get("context_type"):
            prompt = f"Use the referenced context type '{test_def['context_type']}' if applicable.\n\nTask:\n{prompt}"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

    def _tools_for_test(self, test_def: Dict, test_module) -> List[Dict[str, Any]]:
        tools = list(getattr(test_module, "TOOLS", []) or test_def.get("tools", []) or [])
        existing = {tool.get("function", {}).get("name") for tool in tools}
        expected = []
        if test_def.get("expected_tool"):
            expected.append(test_def["expected_tool"])
        expected.extend(test_def.get("expected_tools", []))

        for tool_name in expected:
            if tool_name and tool_name not in existing:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": f"Synthetic tool for evaluating {tool_name} capability",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "hostname": {"type": "string"},
                                "query": {"type": "string"},
                                "severity": {"type": "string"},
                                "message": {"type": "string"},
                            },
                        },
                    },
                })
                existing.add(tool_name)

        return tools

    def _score_generic_response(
        self,
        test_def: Dict,
        content: str,
        tool_calls: List[Dict[str, Any]],
        capability: str,
    ) -> tuple:
        checks = []

        expected_tools = []
        if test_def.get("expected_tool"):
            expected_tools.append(test_def["expected_tool"])
        expected_tools.extend(test_def.get("expected_tools", []))
        if expected_tools:
            called = [tc.get("name") for tc in tool_calls]
            tool_score = sum(1 for t in expected_tools if t in called) / len(expected_tools)
            param_score = self._score_expected_params(test_def.get("expected_params", {}), tool_calls)
            checks.append(("tool_match", tool_score, 0.70))
            checks.append(("param_match", param_score, 0.30))

        keyword_terms = []
        keyword_terms.extend(test_def.get("expected_keywords", []))
        keyword_terms.extend(test_def.get("expected_output_contains", []))
        keyword_terms.extend(test_def.get("expected_behavior", []))
        keyword_terms.extend(test_def.get("expected_context", []))
        keyword_terms.extend(test_def.get("expected_reasoning", []))
        if keyword_terms:
            checks.append(("keyword_match", self._score_terms(content, keyword_terms), 0.45))

        if test_def.get("expected_fields"):
            checks.append(("field_match", self._score_expected_fields(content, test_def["expected_fields"]), 0.35))

        if test_def.get("expected_format"):
            checks.append(("format_match", self._score_expected_format(content, test_def["expected_format"]), 0.20))

        if test_def.get("language"):
            checks.append(("code_language", self._score_code_language(content, test_def["language"]), 0.20))

        if not checks:
            checks.append(("non_empty_response", 1.0 if content.strip() or tool_calls else 0.0, 1.0))

        total_weight = sum(weight for _, _, weight in checks)
        score = sum(value * weight for _, value, weight in checks) / total_weight if total_weight else 0.0
        return min(score, 1.0), {name: round(value, 3) for name, value, _ in checks}

    def _score_expected_params(self, expected_params: Dict[str, Any], tool_calls: List[Dict[str, Any]]) -> float:
        if not expected_params:
            return 1.0
        if not tool_calls:
            return 0.0

        serialized_args = " ".join(str(tc.get("arguments", "")).lower() for tc in tool_calls)
        matched = 0
        for key, value in expected_params.items():
            key_match = key.lower() in serialized_args
            value_match = str(value).lower() in serialized_args
            matched += 1 if key_match or value_match else 0
        return matched / len(expected_params)

    def _score_terms(self, content: str, terms: List[str]) -> float:
        if not terms:
            return 1.0
        text = content.lower()
        matched = sum(1 for term in terms if str(term).lower() in text)
        return matched / len(terms)

    def _score_expected_fields(self, content: str, fields: List[str]) -> float:
        if not fields:
            return 1.0
        data = self._extract_json(content)
        if isinstance(data, list) and data:
            data = data[0]
        if isinstance(data, dict):
            keys = set(data.keys())
            matched = sum(1 for field in fields if field in keys)
            return matched / len(fields)
        return self._score_terms(content, fields) * 0.5

    def _score_expected_format(self, content: str, expected_format: str) -> float:
        fmt = expected_format.lower()
        if "json" in fmt:
            return 1.0 if self._extract_json(content) is not None else 0.0
        if "markdown" in fmt:
            return 1.0 if any(marker in content for marker in ["#", "- ", "|", "```"] ) else 0.4
        if "yaml" in fmt:
            return 1.0 if ":" in content and "{" not in content[:50] else 0.4
        return 1.0 if content.strip() else 0.0

    def _score_code_language(self, content: str, language: str) -> float:
        lang = language.lower()
        text = content.lower()
        if f"```{lang}" in text:
            return 1.0
        language_markers = {
            "python": ["def ", "import ", "print(", "subprocess", "psutil"],
            "bash": ["#!/bin/bash", "grep", "awk", "ps ", "top", "systemctl"],
            "sql": ["select ", "from ", "where "],
        }
        markers = language_markers.get(lang, [lang])
        return min(sum(1 for marker in markers if marker in text) / max(1, min(3, len(markers))), 1.0)

    def _extract_json(self, content: str):
        text = content.strip()
        if "```" in text:
            match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
            if match:
                text = match.group(1).strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                return None
        return None

    def _serialize_tool_calls(self, tool_calls) -> List[Dict[str, Any]]:
        if not tool_calls:
            return []
        result = []
        for tc in tool_calls:
            if hasattr(tc, "function"):
                result.append({
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                })
        return result

    def _get_test_module(self, capability: str):
        """Get the test module for a capability"""
        module_mapping = {
            "tool_calling": "tests.test_tool_calling",
            "vision": "tests.test_vision",
            "rag": "tests.test_rag",
            "code_execution": "tests.test_code_execution",
            "terminal": "tests.test_terminal",
            "json_mode": "tests.test_json_mode",
            "structured_output": "tests.test_structured_output",
            "multiturn": "tests.test_multiturn",
            "streaming": "tests.test_streaming",
            "cot_reasoning": "tests.test_cot_reasoning",
            "agent": "tests.test_agent",
            "web_search": "tests.test_web_search",
            "file_ops": "tests.test_file_ops",
            "memory": "tests.test_memory",
            "task_planning": "tests.test_task_planning",
            "cron": "tests.test_cron",
            "messaging": "tests.test_messaging",
            "session_search": "tests.test_session_search",
            "clarifying": "tests.test_clarifying",
            "delegation": "tests.test_delegation",
            "skills": "tests.test_skills",
            "context_engine": "tests.test_context_engine",
            "mixture_of_agents": "tests.test_mixture_of_agents",
        }

        module_name = module_mapping.get(capability)
        if not module_name:
            return None

        try:
            import importlib
            return importlib.import_module(module_name)
        except ImportError:
            return None

    def run_all_tests(
        self,
        capabilities: Optional[List[str]] = None,
        levels: Optional[List[TestLevel]] = None
    ) -> ModelLevelReport:
        """Run all level tests"""
        if capabilities is None:
            capabilities = get_all_capabilities()

        capability_summaries = {}

        for capability in capabilities:
            print(f"\n{'='*60}")
            print(f"Testing capability: {capability}")
            print(f"Description: {get_capability_description(capability)}")
            print(f"{'='*60}")

            summary = self.run_capability_level_tests(capability, levels)
            capability_summaries[capability] = summary

            # Print progress
            print(f"Max Level Completed: {summary.max_level_completed}")
            print(f"Failure Level: {summary.failure_level or 'None'}")
            print(f"Overall Score: {summary.overall_score:.3f}")
            print(f"Distance Covered: {summary.overall_distance_percentage:.1f}%")

        # Calculate overall statistics
        all_tests = sum(s.total_tests for s in capability_summaries.values())
        all_passed = sum(s.total_passed for s in capability_summaries.values())
        avg_score = sum(s.overall_score for s in capability_summaries.values()) / len(capability_summaries) if capability_summaries else 0

        overall_stats = {
            "total_tests": all_tests,
            "total_passed": all_passed,
            "pass_rate": all_passed / all_tests if all_tests > 0 else 0,
            "average_score": avg_score,
            "capabilities_tested": len(capability_summaries),
            "max_level_distribution": self._calculate_level_distribution(capability_summaries)
        }

        return ModelLevelReport(
            model_name=self.model_name,
            test_date=datetime.now().isoformat(),
            capability_summaries=capability_summaries,
            overall_statistics=overall_stats
        )

    def _calculate_level_distribution(self, summaries: Dict[str, CapabilitySummary]) -> Dict:
        """Calculate distribution of max levels across capabilities"""
        distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for summary in summaries.values():
            distribution[summary.max_level_completed] += 1
        return distribution

    def generate_level_report(self, report: ModelLevelReport) -> str:
        """Generate markdown report"""
        md = []
        md.append(f"# Level-Based Capability Test Report\n")
        md.append(f"**Model:** {report.model_name}")
        md.append(f"**Test Date:** {report.test_date}")
        md.append(f"**Capabilities Tested:** {report.overall_statistics['capabilities_tested']}")
        md.append(f"**Overall Pass Rate:** {report.overall_statistics['pass_rate']:.1%}")
        md.append(f"**Average Score:** {report.overall_statistics['average_score']:.3f}")
        md.append(f"**Level Pass Threshold:** {LEVEL_PASS_THRESHOLD:.0%}\n")

        # Summary table
        md.append("## Summary\n")
        md.append("| Capability | Description | Assessed Level | Failure Level | Score | Distance | Tests | Recommendation |")
        md.append("|------------|-------------|----------------|---------------|-------|----------|-------|----------------|")

        for cap, summary in report.capability_summaries.items():
            md.append(
                f"| {cap.replace('_', ' ').title()} "
                f"| {summary.description} "
                f"| {format_level_badge(summary.max_level_completed)} "
                f"| {format_level_badge(summary.failure_level) if summary.failure_level else 'None'} "
                f"| {summary.overall_score:.3f} "
                f"| {summary.overall_distance_percentage:.1f}% "
                f"| {summary.total_passed}/{summary.total_tests} "
                f"| {recommendation_for_level(summary.max_level_completed)} |"
            )

        # Level distribution
        md.append("\n## Level Distribution\n")
        md.append("| Level | Name | Capabilities | Percentage |")
        md.append("|-------|------|--------------|------------|")

        for level_value in range(0, 6):
            count = report.overall_statistics['max_level_distribution'][level_value]
            pct = count / len(report.capability_summaries) * 100 if report.capability_summaries else 0
            level_name = "Not Qualified" if level_value == 0 else get_level_name(TestLevel(level_value))
            md.append(f"| {level_value} | {level_name} | {count} | {pct:.1f}% |")

        # Detailed capability reports
        for cap, summary in report.capability_summaries.items():
            md.append(f"\n## {cap.replace('_', ' ').title()}\n")
            md.append(f"**Description:** {summary.description}")
            md.append(f"**Assessed Level:** {format_level_badge(summary.max_level_completed)}")
            md.append(f"**Failure Level:** {f'Level {summary.failure_level}' if summary.failure_level else 'None'}")
            md.append(f"**Overall Score:** {summary.overall_score:.3f}")
            md.append(f"**Distance Covered:** {summary.overall_distance_percentage:.1f}%")
            md.append(f"**Tests Passed:** {summary.total_passed}/{summary.total_tests}")
            md.append(f"**Recommendation:** {recommendation_for_level(summary.max_level_completed)}\n")

            # Level breakdown
            for level_val, level_summary in sorted(summary.level_summaries.items()):
                level = TestLevel(level_val)
                md.append(f"### {get_level_icon(level)} Level {level_val} - {get_level_name(level)}\n")
                md.append(f"**Level Score:** {level_summary.average_score:.3f}")
                md.append(f"**Distance:** {level_summary.distance_percentage:.1f}%")
                md.append(f"**Tests:** {level_summary.tests_passed}/{level_summary.tests_run}\n")

                md.append("| Test | Score | Status | Distance |")
                md.append("|------|-------|--------|----------|")

                for test_result in level_summary.test_results:
                    status = "✅ PASS" if test_result.success else "❌ FAIL"
                    dist_pct = (test_result.distance_achieved / test_result.max_distance * 100) if test_result.max_distance > 0 else 0
                    md.append(
                        f"| {test_result.test_name} "
                        f"| {test_result.score:.3f} "
                        f"| {status} "
                        f"| {dist_pct:.1f}% |"
                    )

        return "\n".join(md)

    def save_report(self, report: ModelLevelReport, output_dir: str = "results/level_reports"):
        """Save report to files"""
        os.makedirs(output_dir, exist_ok=True)

        # Generate markdown report
        md_report = self.generate_level_report(report)
        md_filename = f"{output_dir}/{self.model_name.replace('/', '_').replace(':', '_')}_level_report.md"
        with open(md_filename, 'w') as f:
            f.write(md_report)
        print(f"\nSaved markdown report: {md_filename}")

        # Generate JSON report
        json_data = {
            "model_name": report.model_name,
            "test_date": report.test_date,
            "overall_statistics": report.overall_statistics,
            "capabilities": []
        }

        for cap, summary in report.capability_summaries.items():
            cap_data = {
                "capability": cap,
                "description": summary.description,
                "max_level_completed": summary.max_level_completed,
                "assessed_level_name": "Not Qualified" if summary.max_level_completed == 0 else get_level_name(TestLevel(summary.max_level_completed)),
                "recommendation": recommendation_for_level(summary.max_level_completed),
                "failure_level": summary.failure_level,
                "overall_score": summary.overall_score,
                "overall_distance_percentage": summary.overall_distance_percentage,
                "total_tests": summary.total_tests,
                "total_passed": summary.total_passed,
                "levels": []
            }

            for level_val, level_summary in summary.level_summaries.items():
                level_data = {
                    "level": level_val,
                    "level_name": level_summary.level_name,
                    "tests_run": level_summary.tests_run,
                    "tests_passed": level_summary.tests_passed,
                    "average_score": level_summary.average_score,
                    "distance_percentage": level_summary.distance_percentage,
                    "test_results": [asdict(r) for r in level_summary.test_results]
                }
                cap_data["levels"].append(level_data)

            json_data["capabilities"].append(cap_data)

        json_filename = f"{output_dir}/{self.model_name.replace('/', '_').replace(':', '_')}_level_report.json"
        with open(json_filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        print(f"Saved JSON report: {json_filename}")

        return md_filename, json_filename

def main():
    parser = argparse.ArgumentParser(description="Level-Based Test Runner")
    parser.add_argument("--model", type=str, default=None, help="Model name to test")
    parser.add_argument("--level", type=str, nargs="+", default=["all"],
                       help="Levels to test: 1 2 3 4 5 or 'all'")
    parser.add_argument("--capability", type=str, nargs="+", default=None,
                       help="Specific capabilities to test")
    parser.add_argument("--analyze-all", action="store_true",
                       help="Analyze all existing test results")
    parser.add_argument("--output-dir", type=str, default="results/level_reports",
                       help="Output directory for reports")

    args = parser.parse_args()

    # Parse levels
    if "all" in args.level:
        levels = list(TestLevel)
    else:
        levels = [TestLevel(int(l)) for l in args.level]

    if args.analyze_all:
        # Analyze existing results
        print("Analyzing all existing test results...")
        # TODO: Implement analysis of existing results
        print("Analysis complete!")
        return

    # Run tests for specified model (auto-detect if not specified)
    model_name = args.model

    if model_name is None:
        # Auto-detect running model
        print("🔍 Auto-detecting running models...")
        detected = auto_detect_model()
        if detected:
            model_name = detected
            print(f"✅ Detected running model: {model_name}")
        else:
            print("⚠️  No running model detected, using DEFAULT_MODEL from config.py")
            model_name = DEFAULT_MODEL

    if model_name not in MODELS:
        print(f"Error: Model '{model_name}' not found in configuration")
        print(f"Available models: {list(MODELS.keys())}")
        sys.exit(1)

    model_config = MODELS[model_name]

    if not model_config.get("enabled", False):
        print(f"Error: Model '{model_name}' is not enabled")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Level-Based Testing for Model: {model_name}")
    print(f"Levels: {[get_level_name(l) for l in levels]}")
    print(f"Capabilities: {args.capability or 'All'}")
    print(f"{'='*60}\n")

    runner = LevelTestRunner(model_name, model_config)
    report = runner.run_all_tests(args.capability, levels)
    md_file, json_file = runner.save_report(report, args.output_dir)

    print(f"\n{'='*60}")
    print(f"Testing Complete!")
    print(f"Overall Statistics:")
    print(f"  Total Tests: {report.overall_statistics['total_tests']}")
    print(f"  Tests Passed: {report.overall_statistics['total_passed']}")
    print(f"  Pass Rate: {report.overall_statistics['pass_rate']:.1%}")
    print(f"  Average Score: {report.overall_statistics['average_score']:.3f}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
