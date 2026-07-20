#!/usr/bin/env python3
"""
API Integration Test Suite for Block 7 Analytics & AI Engine

Tests all ~20 endpoints across 7 groups:
1. Anomaly Detection  (2 endpoints)
2. Predictive Maintenance (2 endpoints)
3. RCA Engine         (3 endpoints)
4. Capacity Forecasting (2 endpoints)
5. Energy Optimization (2 endpoints)
6. Model Registry     (3 endpoints)
7. LLM/RAG           (2 endpoints)

Usage:
    python test_api_endpoints.py                    # Test all endpoints
    python test_api_endpoints.py --base-url http://localhost:8000  # Custom URL
    python test_api_endpoints.py --group rca         # Test single group
    python test_api_endpoints.py --skip llm,models   # Skip groups

Reference:
    MT-023 §8 (Acceptance Criteria)
    dcim-wiki/reference-designs/block7-analytics-ai-engine.md
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin

# ============================================================================
# HTTP Client
# ============================================================================

class APIClient:
    """Simple HTTP client for API testing."""

    def __init__(self, base_url: str = "http://localhost:8000", verbose: bool = False):
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose

    def _request(
        self,
        method: str,
        path: str,
        body: dict = None,
        params: dict = None,
    ) -> Tuple[int, Any]:
        """Make HTTP request. Returns (status_code, response_data)."""
        url = urljoin(self.base_url + "/", path.lstrip("/"))

        if params:
            import urllib.parse
            url += "?" + urllib.parse.urlencode(params)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        data = None
        if body:
            data = json.dumps(body).encode("utf-8")

        req = Request(url, data=data, headers=headers, method=method)
        start = time.time()

        try:
            with urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                duration = time.time() - start
                if self.verbose:
                    print(f"  {method} {path} → {resp.status} ({duration:.2f}s)")
                try:
                    return resp.status, json.loads(raw)
                except json.JSONDecodeError:
                    return resp.status, raw
        except HTTPError as e:
            duration = time.time() - start
            try:
                error_body = json.loads(e.read().decode("utf-8"))
            except Exception:
                error_body = str(e)
            return e.code, {"error": True, "detail": error_body, "duration": duration}
        except URLError as e:
            return 0, {"error": True, "detail": f"Connection failed: {e.reason}"}
        except Exception as e:
            return 0, {"error": True, "detail": str(e)}

    def get(self, path: str, params: dict = None) -> Tuple[int, Any]:
        return self._request("GET", path, params=params)

    def post(self, path: str, body: dict = None) -> Tuple[int, Any]:
        return self._request("POST", path, body=body)

    def put(self, path: str, body: dict = None) -> Tuple[int, Any]:
        return self._request("PUT", path, body=body)


# ============================================================================
# Test Runner
# ============================================================================

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results = []

    def record(self, name: str, status_code: int, expected: int, detail: str = ""):
        passed = status_code == expected or (expected == 0 and status_code != 0)
        if passed:
            self.passed += 1
            symbol = "✅"
        else:
            self.failed += 1
            symbol = "❌"
        self.results.append((symbol, name, status_code, expected, detail))

    def summary(self) -> bool:
        total = self.passed + self.failed + self.skipped
        print(f"\n{'─' * 60}")
        print(f"  {self.name}")
        print(f"  Passed: {self.passed} | Failed: {self.failed} | Skipped: {self.skipped}")
        if total > 0:
            print(f"  Score: {self.passed}/{total} ({100*self.passed//total}%)")
        for symbol, name, status, expected, detail in self.results:
            print(f"  {symbol} {name} ({status} ≠ {expected})" if not symbol.startswith("✅") else f"  {symbol} {name}")
        print(f"{'─' * 60}")
        return self.failed == 0


class APITestRunner:
    def __init__(self, client: APIClient, skip_groups: list = None, only_group: str = None):
        self.client = client
        self.skip_groups = set(skip_groups or [])
        self.only_group = only_group

    def test_health(self) -> TestResult:
        result = TestResult("Health & Connectivity")
        if "health" in self.skip_groups:
            result.skipped = 2
            return result

        code, data = self.client.get("/health")
        result.record("GET /health", code, 200)

        code, data = self.client.get("/api/v1/health")
        result.record("GET /api/v1/health", code, 200)
        return result

    def test_anomalies(self) -> TestResult:
        result = TestResult("Anomaly Detection")
        if "anomalies" in self.skip_groups:
            return result

        code, data = self.client.get("/api/v1/analytics/anomalies")
        result.record("GET /anomalies", code, 200)

        code, data = self.client.post(
            "/api/v1/analytics/anomalies/detect",
            body={
                "metric_name": "cpu_usage_percent",
                "value": 95.5,
                "ci_id": str(uuid.uuid4()),
            },
        )
        result.record("POST /anomalies/detect", code, 200)

        return result

    def test_predictions(self) -> TestResult:
        result = TestResult("Predictive Maintenance")
        if "predictions" in self.skip_groups:
            return result

        code, data = self.client.get("/api/v1/analytics/predictions")
        result.record("GET /predictions", code, 200)

        code, data = self.client.post(
            "/api/v1/analytics/predictions/forecast",
            body={
                "ci_id": str(uuid.uuid4()),
                "metric": "cpu_usage_percent",
                "days": 30,
            },
        )
        result.record("POST /predictions/forecast", code, 200)

        return result

    def test_rca(self) -> TestResult:
        result = TestResult("Root Cause Analysis (RCA)")
        if "rca" in self.skip_groups:
            return result

        incident_id = f"INC-{uuid.uuid4().hex[:8]}"
        ci_id = str(uuid.UUID("11111111-1111-1111-1111-111111111111"))

        code, data = self.client.post(
            "/api/v1/analytics/rca/analyze",
            body={
                "incident_id": incident_id,
                "ci_id": ci_id,
                "active_domains": ["server", "network", "storage", "power", "cooling"],
                "timeframe_minutes": 60,
                "mode": "reactive",
            },
        )
        result.record("POST /rca/analyze", code, 200)

        code, data = self.client.get(f"/api/v1/analytics/rca/{incident_id}")
        result.record(f"GET /rca/{incident_id}", code, [200, 404, 503])

        code, data = self.client.get("/api/v1/analytics/rca/history", params={"per_page": 5})
        result.record("GET /rca/history", code, [200, 503])

        return result

    def test_capacity(self) -> TestResult:
        result = TestResult("Capacity Forecasting")
        if "capacity" in self.skip_groups:
            return result

        code, data = self.client.get("/api/v1/analytics/capacity")
        result.record("GET /capacity", code, 200)

        code, data = self.client.post(
            "/api/v1/analytics/capacity/forecast",
            body={
                "resource_type": "cpu",
                "days": 30,
                "ci_id": str(uuid.uuid4()),
            },
        )
        result.record("POST /capacity/forecast", code, 200)

        return result

    def test_energy(self) -> TestResult:
        result = TestResult("Energy Optimization")
        if "energy" in self.skip_groups:
            return result

        code, data = self.client.get("/api/v1/analytics/energy/pue")
        result.record("GET /energy/pue", code, 200)

        code, data = self.client.post(
            "/api/v1/analytics/energy/optimize",
            body={
                "total_power_kw": 1500,
                "it_power_kw": 1200,
            },
        )
        result.record("POST /energy/optimize", code, 200)

        return result

    def test_models(self) -> TestResult:
        result = TestResult("Model Registry")
        if "models" in self.skip_groups:
            return result

        code, data = self.client.get("/api/v1/analytics/models")
        result.record("GET /models", code, 200)

        code, data = self.client.post(
            "/api/v1/analytics/models",
            body={
                "model_name": f"test_model_{uuid.uuid4().hex[:6]}",
                "model_type": "anomaly_detection",
                "version": "1.0.0",
                "domain": "server",
                "accuracy": 0.95,
            },
        )
        result.record("POST /models", code, 200)

        code, data = self.client.put(
            "/api/v1/analytics/models/test/deploy",
            body={"version": "1.0.0"},
        )
        result.record("PUT /models/{id}/deploy", code, [200, 400, 404])

        return result

    def test_llm(self) -> TestResult:
        result = TestResult("LLM/RAG")
        if "llm" in self.skip_groups:
            return result

        code, data = self.client.post(
            "/api/v1/analytics/llm/query",
            body={"query": "Why is CPU spiking?"},
        )
        result.record("POST /llm/query", code, 200)

        code, data = self.client.post(
            "/api/v1/analytics/llm/explain",
            body={
                "metric_name": "cpu_usage_percent",
                "current_value": 95.5,
                "expected_min": 10.0,
                "expected_max": 60.0,
                "severity": "high",
                "detection_method": "z_score",
            },
        )
        result.record("POST /llm/explain", code, 200)

        return result

    def run_all(self) -> bool:
        """Run all test groups. Returns True if all passed."""
        print("╔" + "═" * 58 + "╗")
        print("║  Block 7 API Integration Test Suite" + " " * 22 + "║")
        print("║  " + self.client.base_url + " " * (56 - len(self.client.base_url)) + "║")
        print("╚" + "═" * 58 + "╝")

        results = []

        # Always test health first
        results.append(self.test_health())

        groups = [
            ("anomalies", self.test_anomalies),
            ("predictions", self.test_predictions),
            ("rca", self.test_rca),
            ("capacity", self.test_capacity),
            ("energy", self.test_energy),
            ("models", self.test_models),
            ("llm", self.test_llm),
        ]

        for name, test_fn in groups:
            if self.only_group and name != self.only_group:
                continue
            results.append(test_fn())

        # Overall summary
        total_passed = sum(r.passed for r in results)
        total_failed = sum(r.failed for r in results)
        total_skipped = sum(r.skipped for r in results)
        total = total_passed + total_failed + total_skipped

        print(f"\n{'═' * 60}")
        print(f"  OVERALL RESULTS")
        print(f"  Passed: {total_passed} | Failed: {total_failed} | Skipped: {total_skipped}")
        if total > 0:
            print(f"  Success Rate: {total_passed}/{total} ({100*total_passed//(total-total_skipped) if total > total_skipped else 'N/A'}%)")
        print(f"{'═' * 60}")

        all_passed = total_failed == 0
        if all_passed:
            print(f"\n✅  ALL TESTS PASSED!")
        else:
            print(f"\n❌  {total_failed} TESTS FAILED")

        return all_passed


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Block 7 API Integration Test Suite")
    parser.add_argument("--base-url", default=os.getenv("API_BASE_URL", "http://localhost:8000"))
    parser.add_argument("--skip", default="", help="Comma-separated groups to skip (e.g., 'llm,models')")
    parser.add_argument("--group", default="", help="Test only this group (e.g., 'rca')")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    client = APIClient(base_url=args.base_url, verbose=args.verbose)
    skip_groups = [g.strip() for g in args.skip.split(",") if g.strip()]

    runner = APITestRunner(
        client=client,
        skip_groups=skip_groups,
        only_group=args.group or None,
    )

    success = runner.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
