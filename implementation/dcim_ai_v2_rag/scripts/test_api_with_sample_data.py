#!/usr/bin/env python3
"""
Quick Sample Data Generator via API

Generate sample data dan test semua API endpoints.
Tidak butuh Kafka atau TimescaleDB - langsung test lewat API.

Usage:
    python scripts/test_api_with_sample_data.py

Requires: API server running on localhost:8000
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_json(data):
    print(json.dumps(data, indent=2, default=str))

def test_health():
    """Test health endpoint"""
    print_header("1. Health Check")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {r.status_code}")
        print_json(r.json())
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rca():
    """Test RCA with multiple scenarios"""
    print_header("2. Root Cause Analysis")

    scenarios = [
        {
            "name": "Server CPU Issue",
            "data": {
                "incident_id": "INC-001",
                "ci_id": "srv-web-001",
                "active_domains": ["server", "network", "storage", "power", "cooling"],
                "mode": "reactive"
            }
        },
        {
            "name": "Network Latency Issue",
            "data": {
                "incident_id": "INC-002",
                "ci_id": "srv-app-001",
                "active_domains": ["network", "server", "storage"],
                "mode": "reactive"
            }
        },
        {
            "name": "Storage Full Issue",
            "data": {
                "incident_id": "INC-003",
                "ci_id": "srv-db-001",
                "active_domains": ["storage", "server"],
                "mode": "reactive"
            }
        }
    ]

    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        try:
            r = requests.post(
                f"{BASE_URL}/api/v1/analytics/rca/analyze",
                json=scenario["data"],
                timeout=10
            )
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                result = r.json()
                print(f"Root Cause: {result['root_cause']}")
                print(f"Confidence: {result['confidence']:.2%}")
                print(f"Domains: {result['ranked_domains']}")
            else:
                print_json(r.json())
        except Exception as e:
            print(f"❌ Error: {e}")

def test_capacity():
    """Test capacity forecasting with different metrics"""
    print_header("3. Capacity Forecasting")

    metrics = [
        {"ci_id": "srv-web-001", "metric_name": "cpu_usage", "forecast_days": 30},
        {"ci_id": "srv-db-001", "metric_name": "disk_usage", "forecast_days": 60},
        {"ci_id": "srv-app-001", "metric_name": "memory_usage", "forecast_days": 90},
    ]

    for metric in metrics:
        print(f"\n--- {metric['ci_id']} / {metric['metric_name']} ---")
        try:
            r = requests.post(
                f"{BASE_URL}/api/v1/analytics/capacity/forecast",
                json=metric,
                timeout=10
            )
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                result = r.json()
                print(f"Current: {result['current_value']:.1f}%")
                print(f"30d: {result.get('predicted_value_30d', 'N/A')}")
                print(f"60d: {result.get('predicted_value_60d', 'N/A')}")
                print(f"90d: {result.get('predicted_value_90d', 'N/A')}")
                print(f"Trend: {result['trend']}")
                print(f"Exhaustion: {result.get('exhaustion_date', 'N/A')}")
                print(f"R²: {result['r_squared']:.3f}")
                print(f"Rec: {result['recommendation']}")
            else:
                print_json(r.json())
        except Exception as e:
            print(f"❌ Error: {e}")

def test_energy():
    """Test energy optimization"""
    print_header("4. Energy Optimization")

    # Test PUE
    print("--- PUE Calculation ---")
    try:
        r = requests.get(
            f"{BASE_URL}/api/v1/analytics/energy/pue",
            params={"datacenter_id": "dc-001"},
            timeout=10
        )
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"PUE: {result['pue']}")
            print(f"Rating: {result['rating']}")
            print(f"Total Power: {result['total_power_kw']} kW")
            print(f"IT Power: {result['it_power_kw']} kW")
            print(f"Cooling: {result['cooling_power_kw']} kW")
            print(f"Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
        else:
            print_json(r.json())
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test Optimization
    print("\n--- Optimization Recommendations ---")
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/analytics/energy/optimize",
            params={"datacenter_id": "dc-001", "target_pue": 1.3},
            timeout=10
        )
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"Current PUE: {result['current_pue']}")
            print(f"Target PUE: {result['target_pue']}")
            print(f"Savings: {result['potential_savings_pct']:.1f}%")
            print(f"Monthly Savings: {result['estimated_monthly_savings_kwh']:.0f} kWh")
            print(f"Actions:")
            for action in result['actions']:
                print(f"  [{action['priority'].upper()}] {action['action']}")
                print(f"    Impact: -{action['estimated_pue_impact']} PUE")
        else:
            print_json(r.json())
    except Exception as e:
        print(f"❌ Error: {e}")

def test_anomalies():
    """Test anomaly listing"""
    print_header("5. Anomalies & Predictions")

    try:
        r = requests.get(f"{BASE_URL}/api/v1/analytics/anomalies", timeout=5)
        print(f"Anomalies: {r.status_code} → {r.json()}")
    except Exception as e:
        print(f"Anomalies: ❌ {e}")

    try:
        r = requests.get(f"{BASE_URL}/api/v1/analytics/predictions", timeout=5)
        print(f"Predictions: {r.status_code} → {r.json()}")
    except Exception as e:
        print(f"Predictions: ❌ {e}")

def test_models():
    """Test model registry"""
    print_header("6. Model Registry")

    try:
        r = requests.get(f"{BASE_URL}/api/v1/analytics/models", timeout=5)
        print(f"Models: {r.status_code} → {r.json()}")
    except Exception as e:
        print(f"Models: ❌ {e}")

def main():
    print_header("DCIM Analytics API - Sample Data Test")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")

    # Check if API is running
    if not test_health():
        print("\n❌ API not running! Start with:")
        print("  cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag")
        print("  uvicorn api.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # Run all tests
    test_rca()
    test_capacity()
    test_energy()
    test_anomalies()
    test_models()

    print_header("Test Complete!")
    print("All endpoints tested. Check results above.")
    print(f"\nSwagger UI: {BASE_URL}/api/v1/docs")

if __name__ == "__main__":
    main()
