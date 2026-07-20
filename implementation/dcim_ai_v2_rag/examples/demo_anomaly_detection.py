#!/usr/bin/env python3
"""
Anomaly Detection Demo - Demonstrates Z-score anomaly detection

Jalankan: python examples/demo_anomaly_detection.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from datetime import datetime, timedelta
import random

class AnomalyDetector:
    """Z-score based anomaly detector"""
    
    def __init__(self, threshold=3.0, window_size=100):
        self.threshold = threshold
        self.window_size = window_size
        self.history = []
    
    def detect(self, value):
        """Detect if value is anomaly"""
        # Add to history
        self.history.append(value)
        
        # Keep only window_size
        if len(self.history) > self.window_size:
            self.history = self.history[-self.window_size:]
        
        # Need at least 10 samples
        if len(self.history) < 10:
            return {
                "is_anomaly": False,
                "z_score": 0,
                "reason": "Not enough data"
            }
        
        # Calculate statistics
        mean = np.mean(self.history)
        std = np.std(self.history)
        
        # Calculate Z-score
        if std == 0:
            z_score = 0
        else:
            z_score = (value - mean) / std
        
        # Detect anomaly
        is_anomaly = abs(z_score) > self.threshold
        
        return {
            "is_anomaly": is_anomaly,
            "z_score": round(z_score, 2),
            "mean": round(mean, 2),
            "std": round(std, 2),
            "threshold": self.threshold,
            "value": value,
            "reason": "Anomaly detected!" if is_anomaly else "Normal"
        }

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_metric(value, result):
    """Print metric with visual indicator"""
    status = "🔴 ANOMALY" if result['is_anomaly'] else "🟢 NORMAL"
    print(f"  Value: {value:6.1f} | Z-score: {result['z_score']:6.2f} | {status}")

def demo_normal_distribution():
    """Demo: Normal distribution with occasional anomalies"""
    print_header("Demo 1: Normal Distribution with Anomalies")
    
    detector = AnomalyDetector(threshold=3.0, window_size=50)
    
    # Generate normal data (mean=50, std=5)
    print("Generating metrics with mean=50, std=5...")
    print("Anomalies will be values > 3 standard deviations from mean\n")
    
    for i in range(100):
        # Normal distribution
        value = random.gauss(50, 5)
        
        # Inject anomalies at specific points
        if i == 30:
            value = 75  # Anomaly (Z-score ~5)
        elif i == 60:
            value = 20  # Anomaly (Z-score ~-6)
        elif i == 90:
            value = 80  # Anomaly (Z-score ~6)
        
        result = detector.detect(value)
        print_metric(value, result)

def demo_seasonal_pattern():
    """Demo: Seasonal pattern (CPU usage throughout the day)"""
    print_header("Demo 2: Seasonal Pattern (CPU Usage)")
    
    detector = AnomalyDetector(threshold=2.5, window_size=24)
    
    print("Simulating CPU usage over 48 hours...")
    print("Pattern: Low at night, high during business hours\n")
    
    for hour in range(48):
        # Base pattern: low at night, high during day
        base = 30 + 40 * np.sin((hour % 24 - 6) * np.pi / 12)
        base = max(10, min(90, base))  # Clamp
        
        # Add noise
        value = base + random.gauss(0, 5)
        
        # Inject anomaly at hour 20 (should be low, but spike)
        if hour == 20:
            value = 95  # Spike anomaly
        
        result = detector.detect(value)
        print(f"  Hour {hour:2d}: ", end="")
        print_metric(value, result)

def demo_gradual_increase():
    """Demo: Gradual increase (disk usage filling up)"""
    print_header("Demo 3: Gradual Increase (Disk Usage)")
    
    detector = AnomalyDetector(threshold=2.0, window_size=30)
    
    print("Simulating disk usage over 60 days...")
    print("Pattern: Gradual increase with sudden spike\n")
    
    base = 50
    for day in range(60):
        # Gradual increase
        base += 0.5
        value = base + random.gauss(0, 2)
        
        # Inject sudden spike at day 45
        if day == 45:
            value = 95  # Sudden spike
        
        result = detector.detect(value)
        print(f"  Day {day:2d}: ", end="")
        print_metric(value, result)

def main():
    print_header("Anomaly Detection Demo")
    print("Demonstrasi Z-score anomaly detection")
    print("Threshold: 3.0 (default)")
    print("Window size: 100 samples (default)")
    
    demo_normal_distribution()
    demo_seasonal_pattern()
    demo_gradual_increase()
    
    print_header("Summary")
    print("Z-score Formula:")
    print("  z = (value - mean) / std_dev")
    print()
    print("Anomaly Detection:")
    print("  if |z_score| > threshold → ANOMALY")
    print()
    print("Threshold Interpretation:")
    print("  Z=1.0 → 68% of data within range")
    print("  Z=2.0 → 95% of data within range")
    print("  Z=3.0 → 99.7% of data within range (default)")
    print("  Z=4.0 → 99.99% of data within range")
    print()

if __name__ == "__main__":
    main()
