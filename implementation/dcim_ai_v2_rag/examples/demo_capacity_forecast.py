#!/usr/bin/env python3
"""
Capacity Forecasting Demo - Demonstrates linear regression forecasting

Jalankan: python examples/demo_capacity_forecast.py
"""

import numpy as np
from datetime import datetime, timedelta
import random

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def linear_regression(x, y):
    """Simple linear regression"""
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x * x)
    
    # Calculate slope and intercept
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    intercept = (sum_y - slope * sum_x) / n
    
    # Calculate R-squared
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return slope, intercept, r_squared

def predict_exhaustion(current_value, slope, threshold=100):
    """Predict when resource will reach threshold"""
    if slope <= 0:
        return None  # Not increasing
    
    days_to_exhaustion = (threshold - current_value) / slope
    exhaustion_date = datetime.now() + timedelta(days=days_to_exhaustion)
    
    return {
        "days": round(days_to_exhaustion, 1),
        "date": exhaustion_date.strftime("%Y-%m-%d"),
        "threshold": threshold
    }

def demo_disk_usage():
    """Demo: Disk usage forecast"""
    print_header("Demo: Disk Usage Forecast")
    
    # Generate historical data (90 days)
    days = np.arange(90)
    
    # Pattern: Linear increase with noise
    base = 50  # Starting at 50%
    slope_actual = 0.3  # 0.3% per day
    noise = np.random.normal(0, 2, 90)
    
    values = base + slope_actual * days + noise
    values = np.clip(values, 0, 100)
    
    # Fit linear regression
    slope, intercept, r_squared = linear_regression(days, values)
    
    # Predict future (30, 60, 90 days)
    future_days = np.array([90, 120, 150, 180])
    predictions = slope * future_days + intercept
    
    # Calculate exhaustion
    current_value = values[-1]
    exhaustion = predict_exhaustion(current_value, slope)
    
    # Print results
    print(f"Resource: server-001 disk_usage")
    print(f"Current Value: {current_value:.1f}%")
    print(f"Historical Data: 90 days")
    print()
    
    print("Trend Analysis:")
    print(f"  Slope: {slope:.3f}% per day")
    print(f"  R² Score: {r_squared:.3f}")
    print(f"  Trend: {'Increasing ↑' if slope > 0 else 'Decreasing ↓'}")
    print()
    
    print("Forecast:")
    print(f"  {'Day':<10} {'Date':<15} {'Predicted':<15} {'Status'}")
    print(f"  {'-'*50}")
    
    for i, (day, pred) in enumerate(zip(future_days, predictions)):
        date = datetime.now() + timedelta(days=int(day))
        status = "🔴 CRITICAL" if pred > 90 else "🟡 WARNING" if pred > 80 else "🟢 OK"
        print(f"  {day:<10} {date.strftime('%Y-%m-%d'):<15} {pred:.1f}%{'':<10} {status}")
    
    print()
    if exhaustion:
        print(f"⚠️  Resource Exhaustion Prediction:")
        print(f"   Will reach 100% in {exhaustion['days']} days")
        print(f"   Estimated date: {exhaustion['date']}")
        print()
        print(f"   Recommendation: Add storage before {exhaustion['date']}")
    else:
        print(f"✅ No exhaustion predicted (trend is decreasing)")

def demo_cpu_usage():
    """Demo: CPU usage forecast"""
    print_header("Demo: CPU Usage Forecast")
    
    # Generate historical data (60 days)
    days = np.arange(60)
    
    # Pattern: Seasonal with increasing trend
    base = 40
    seasonal = 20 * np.sin(days * 2 * np.pi / 7)  # Weekly cycle
    trend = 0.2 * days  # Increasing trend
    noise = np.random.normal(0, 3, 60)
    
    values = base + seasonal + trend + noise
    values = np.clip(values, 0, 100)
    
    # Fit linear regression
    slope, intercept, r_squared = linear_regression(days, values)
    
    # Predict future
    future_days = np.array([60, 90, 120])
    predictions = slope * future_days + intercept
    
    # Calculate exhaustion
    current_value = values[-1]
    exhaustion = predict_exhaustion(current_value, slope)
    
    # Print results
    print(f"Resource: server-001 cpu_usage")
    print(f"Current Value: {current_value:.1f}%")
    print(f"Historical Data: 60 days")
    print()
    
    print("Trend Analysis:")
    print(f"  Slope: {slope:.3f}% per day")
    print(f"  R² Score: {r_squared:.3f}")
    print(f"  Trend: {'Increasing ↑' if slope > 0 else 'Decreasing ↓'}")
    print()
    
    print("Forecast:")
    for day, pred in zip(future_days, predictions):
        date = datetime.now() + timedelta(days=int(day))
        status = "🔴 CRITICAL" if pred > 90 else "🟡 WARNING" if pred > 80 else "🟢 OK"
        print(f"  {date.strftime('%Y-%m-%d')}: {pred:.1f}% {status}")

def demo_memory_usage():
    """Demo: Memory usage forecast"""
    print_header("Demo: Memory Usage Forecast")
    
    # Generate historical data (30 days)
    days = np.arange(30)
    
    # Pattern: Sudden jump then stable
    base = 60
    jump = np.where(days >= 15, 15, 0)  # Jump at day 15
    noise = np.random.normal(0, 2, 30)
    
    values = base + jump + noise
    values = np.clip(values, 0, 100)
    
    # Fit linear regression
    slope, intercept, r_squared = linear_regression(days, values)
    
    # Predict future
    future_days = np.array([30, 60, 90])
    predictions = slope * future_days + intercept
    
    # Calculate exhaustion
    current_value = values[-1]
    exhaustion = predict_exhaustion(current_value, slope)
    
    # Print results
    print(f"Resource: server-001 memory_usage")
    print(f"Current Value: {current_value:.1f}%")
    print(f"Historical Data: 30 days")
    print()
    
    print("Trend Analysis:")
    print(f"  Slope: {slope:.3f}% per day")
    print(f"  R² Score: {r_squared:.3f}")
    print(f"  Trend: {'Increasing ↑' if slope > 0 else 'Decreasing ↓'}")
    print()
    
    print("Forecast:")
    for day, pred in zip(future_days, predictions):
        date = datetime.now() + timedelta(days=int(day))
        status = "🔴 CRITICAL" if pred > 90 else "🟡 WARNING" if pred > 80 else "🟢 OK"
        print(f"  {date.strftime('%Y-%m-%d')}: {pred:.1f}% {status}")

def main():
    print_header("Capacity Forecasting Demo")
    print("Demonstrasi linear regression untuk prediksi resource exhaustion")
    print()
    print("Formula:")
    print("  y = mx + b")
    print("  where:")
    print("    y = predicted value")
    print("    m = slope (trend)")
    print("    x = time (days)")
    print("    b = intercept")
    print()
    print("Confidence:")
    print("  R² Score measures how well the line fits the data")
    print("  R² = 1.0 → Perfect fit")
    print("  R² > 0.8 → Good fit")
    print("  R² < 0.5 → Poor fit (data may not be linear)")
    
    demo_disk_usage()
    demo_cpu_usage()
    demo_memory_usage()
    
    print_header("Summary")
    print("Key Metrics:")
    print("  1. Slope: Rate of change per day")
    print("  2. R² Score: Confidence in prediction")
    print("  3. Exhaustion Date: When resource reaches 100%")
    print()
    print("Recommendations:")
    print("  - If slope > 0 and R² > 0.8: Plan capacity expansion")
    print("  - If slope > 0 and R² < 0.5: Investigate data quality")
    print("  - If slope ≤ 0: No immediate action needed")
    print()

if __name__ == "__main__":
    main()
