#!/usr/bin/env python3
"""
DCIM Analytics Demo - Contoh penggunaan API

Jalankan: python examples/demo_api.py
"""

import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_json(data):
    print(json.dumps(data, indent=2, default=str))

def demo_health_check():
    """Demo: Health check endpoint"""
    print_header("1. Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"GET {BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print_json(response.json())

def demo_list_anomalies():
    """Demo: List anomalies endpoint"""
    print_header("2. List Anomalies")
    
    response = requests.get(f"{BASE_URL}/api/v1/analytics/anomalies")
    print(f"GET {BASE_URL}/api/v1/analytics/anomalies")
    print(f"Status: {response.status_code}")
    print_json(response.json())

def demo_list_predictions():
    """Demo: List predictions endpoint"""
    print_header("3. List Predictions")
    
    response = requests.get(f"{BASE_URL}/api/v1/analytics/predictions")
    print(f"GET {BASE_URL}/api/v1/analytics/predictions")
    print(f"Status: {response.status_code}")
    print_json(response.json())

def demo_rca_analyze():
    """Demo: Trigger RCA analysis"""
    print_header("4. RCA Analysis")
    
    payload = {
        "incident_id": "INC-001",
        "ci_id": "server-001",
        "timeframe_minutes": 60,
        "mode": "reactive"
    }
    
    print(f"POST {BASE_URL}/api/v1/analytics/rca/analyze")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/rca/analyze",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print_json(response.json())
    except Exception as e:
        print(f"Error: {e}")

def demo_capacity_forecast():
    """Demo: Capacity forecast"""
    print_header("5. Capacity Forecast")
    
    payload = {
        "ci_id": "server-001",
        "metric_name": "disk_usage",
        "forecast_days": 30
    }
    
    print(f"POST {BASE_URL}/api/v1/analytics/capacity/forecast")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/capacity/forecast",
            json=payload
        )
        print(f"Status: {response.status_code}")
        print_json(response.json())
    except Exception as e:
        print(f"Error: {e}")

def demo_energy_pue():
    """Demo: PUE calculation"""
    print_header("6. Energy PUE")
    
    print(f"GET {BASE_URL}/api/v1/analytics/energy/pue")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/analytics/energy/pue")
        print(f"Status: {response.status_code}")
        print_json(response.json())
    except Exception as e:
        print(f"Error: {e}")

def demo_openapi_docs():
    """Demo: OpenAPI documentation"""
    print_header("7. OpenAPI Documentation")
    
    print(f"Swagger UI: {BASE_URL}/api/v1/docs")
    print(f"ReDoc:      {BASE_URL}/api/v1/redoc")
    print(f"OpenAPI:    {BASE_URL}/api/v1/openapi.json")

def main():
    print_header("DCIM Analytics & AI Engine - Demo")
    print("Mendemonstrasikan semua endpoint yang tersedia...")
    print(f"Base URL: {BASE_URL}")
    
    # Run demos
    demo_health_check()
    demo_list_anomalies()
    demo_list_predictions()
    demo_rca_analyze()
    demo_capacity_forecast()
    demo_energy_pue()
    demo_openapi_docs()
    
    print_header("Demo Selesai!")
    print("Untuk dokumentasi interaktif, buka browser ke:")
    print(f"  {BASE_URL}/api/v1/docs")
    print()

if __name__ == "__main__":
    main()
