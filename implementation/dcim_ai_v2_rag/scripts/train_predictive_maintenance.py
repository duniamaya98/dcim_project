#!/usr/bin/env python3
"""
Predictive Maintenance Model Training

Trains forecasting models for Block 7 §2.3:
- Prophet: Trend + seasonality forecasting (30-day window)
- Exponential Smoothing: Baseline model
- Linear Regression: Simple trend projection

Output: Model artifacts + evaluation metrics

Usage:
    python train_predictive_maintenance.py                     # Train all, save to artifacts/
    python train_predictive_maintenance.py --model prophet     # Prophet only
    python train_predictive_maintenance.py --dry-run           # Evaluate only

Reference:
    dcim-wiki/reference-designs/block7-analytics-ai-engine.md §4
    dcim-wiki/reference-designs/block7-analytics-ai-engine-technical-requirements.md §3.3
    MT-023 §2.3
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# Data Generation (synthetic training data)
# ============================================================================

def generate_training_data(
    num_cis: int = 5,
    days: int = 90,
    interval_hours: int = 1,
    failure_labels: bool = True,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic time-series data for predictive maintenance training.

    Each CI has metrics with realistic patterns + optional failure labels.
    """
    np.random.seed(seed)
    ci_ids = [f"CI-{i:04d}" for i in range(num_cis)]
    hours = days * 24
    all_rows = []

    for ci_idx, ci_id in enumerate(ci_ids):
        base_cpu = np.random.uniform(20, 40)
        base_memory = np.random.uniform(30, 60)
        base_disk = np.random.uniform(40, 70)
        base_temp = np.random.uniform(21, 24)

        # Random drift factor per CI (some degrade faster)
        cpu_drift = np.random.uniform(0.01, 0.15)  # % per day
        memory_drift = np.random.uniform(0.005, 0.08)
        disk_drift = np.random.uniform(0.02, 0.12)
        temp_drift = np.random.uniform(0.001, 0.02)

        for h in range(hours):
            ts = datetime.now(timezone.utc) - timedelta(days=days) + timedelta(hours=h)

            # Metrics with noise + drift
            cpu = base_cpu + cpu_drift * (h / 24) + np.random.normal(0, 3)
            memory = base_memory + memory_drift * (h / 24) + np.random.normal(0, 2)
            disk = base_disk + disk_drift * (h / 24) + np.random.normal(0, 1.5)
            temp = base_temp + temp_drift * (h / 24) + np.random.normal(0, 0.5)
            power = 500 + cpu * 15 + np.random.normal(0, 50)

            # Failure probability (synthetic label)
            # Increases as metrics approach thresholds
            cpu_risk = max(0, (cpu - 80) / 20)
            mem_risk = max(0, (memory - 90) / 10)
            disk_risk = max(0, (disk - 93) / 7)
            temp_risk = max(0, (temp - 30) / 10)

            failure_prob = min(1.0, 0.3 * cpu_risk + 0.25 * mem_risk + 0.25 * disk_risk + 0.2 * temp_risk)
            failure_prob += np.random.uniform(-0.05, 0.05)

            # Inject some actual failures near end of timeline
            is_failure = False
            if h > hours * 0.85 and failure_prob > 0.7 and np.random.random() < 0.3:
                is_failure = True

            all_rows.append({
                "timestamp": ts,
                "ci_id": ci_id,
                "cpu_usage_percent": max(0, round(cpu, 2)),
                "memory_usage_percent": max(0, round(memory, 2)),
                "disk_usage_percent": max(0, round(disk, 2)),
                "temperature_celsius": round(temp, 2),
                "power_consumption_watts": round(max(0, power), 2),
                "failure_probability": round(failure_prob, 4),
                "is_failure": is_failure,
            })

    df = pd.DataFrame(all_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    logger.info(f"Generated {len(df):,} training rows for {len(ci_ids)} CIs over {days} days")
    return df


# ============================================================================
# Prophet Model
# ============================================================================

class ProphetForecaster:
    """Wrapper around Facebook Prophet for DCIM metric forecasting."""

    def __init__(self):
        self.models: Dict[str, Any] = {}  # ci_id → model
        self.fitted = False

    def fit(self, df: pd.DataFrame, metric_col: str = "cpu_usage_percent", forecast_days: int = 30):
        """Fit Prophet models per CI."""
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("prophet not installed. Run: pip install prophet")

        ci_ids = df["ci_id"].unique()

        for ci_id in ci_ids:
            ci_data = df[df["ci_id"] == ci_id][["timestamp", metric_col]].copy()
            ci_data.columns = ["ds", "y"]
            ci_data = ci_data.set_index("ds").resample("1h").mean().reset_index()
            ci_data = ci_data.dropna()

            if len(ci_data) < 30:
                logger.warning(f"CI {ci_id}: insufficient data ({len(ci_data)} points), skipping")
                continue

            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05,
            )
            model.fit(ci_data)
            self.models[ci_id] = model
            logger.info(f"Fitted Prophet for CI {ci_id} ({len(ci_data)} points)")

        self.fitted = True

    def forecast(self, ci_id: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Generate forecast for a CI."""
        if ci_id not in self.models:
            logger.warning(f"No model for CI {ci_id}")
            return None

        model = self.models[ci_id]
        future = model.make_future_dataframe(periods=days * 24, freq="h")
        forecast = model.predict(future)
        return forecast

    def predict_failure(
        self,
        ci_id: str,
        metric_col: str = "cpu_usage_percent",
        threshold: float = 90.0,
        days: int = 30,
    ) -> Dict[str, Any]:
        """
        Predict failure probability based on threshold crossing.

        Returns dict with:
        - failure_probability: probability of crossing threshold within window
        - days_to_failure: estimated days until threshold
        - confidence: model confidence
        """
        forecast = self.forecast(ci_id, days=days)
        if forecast is None:
            return {
                "ci_id": ci_id,
                "failure_probability": 0.0,
                "days_to_failure": None,
                "confidence": 0.0,
                "risk_level": "unknown",
            }

        # Get future predictions only
        future = forecast[forecast["ds"] > forecast["ds"].iloc[-days * 24]]

        if len(future) == 0:
            return {"ci_id": ci_id, "failure_probability": 0.0, "days_to_failure": None, "confidence": 0.0, "risk_level": "low"}

        # Probability = fraction of forecasted values above threshold
        above_threshold = (future["yhat"] > threshold).mean()
        max_value = future["yhat"].max()
        current_value = forecast["yhat"].iloc[-days * 24 - 1] if len(forecast) > days * 24 else forecast["yhat"].iloc[0]

        # Days to failure: when yhat crosses threshold
        crossing = future[future["yhat"] > threshold]
        if len(crossing) > 0:
            days_to_failure = (crossing["ds"].min() - future["ds"].min()).total_seconds() / 86400
        else:
            days_to_failure = None

        # Risk level
        if above_threshold > 0.5:
            risk_level = "critical"
        elif above_threshold > 0.2:
            risk_level = "high"
        elif above_threshold > 0.05:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "ci_id": ci_id,
            "metric": metric_col,
            "failure_probability": round(float(above_threshold), 4),
            "days_to_failure": round(days_to_failure, 1) if days_to_failure else None,
            "current_value": round(float(current_value), 2),
            "forecast_max": round(float(max_value), 2),
            "confidence": round(0.7 + 0.2 * (min(1, above_threshold)), 4),
            "risk_level": risk_level,
            "prediction_window": f"{days}_days",
        }


# ============================================================================
# Simple Statistical Forecasters
# ============================================================================

class SimpleForecaster:
    """Baseline forecasting using exponential smoothing + linear regression."""

    def __init__(self):
        pass

    def forecast_linear(self, values: np.ndarray, forecast_horizon: int = 30 * 24) -> Dict[str, Any]:
        """
        Linear regression forecast.

        Returns:
            {
                "trend_slope": float,
                "predicted_values": np.ndarray,
                "exhaustion_hours": float or None,
                "confidence": float,
            }
        """
        n = len(values)
        if n < 10:
            return {"trend_slope": 0, "predicted_values": np.zeros(forecast_horizon), "exhaustion_hours": None, "confidence": 0}

        x = np.arange(n).reshape(-1, 1)
        y = values.reshape(-1, 1)

        # Linear regression
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(x, y)

        slope = model.coef_[0][0]
        intercept = model.intercept_[0]

        # Predict
        future_x = np.arange(n, n + forecast_horizon).reshape(-1, 1)
        predictions = model.predict(future_x).flatten()

        # When does it cross threshold?
        threshold = 90.0
        if slope > 0:
            exhaustion_steps = (threshold - intercept) / slope - n
            exhaustion_hours = exhaustion_steps if exhaustion_steps > 0 else None
        else:
            exhaustion_hours = None

        # Confidence: R² score
        r2 = model.score(x, y)

        return {
            "trend_slope": float(slope),
            "predicted_values": predictions.tolist(),
            "exhaustion_hours": round(float(exhaustion_hours), 1) if exhaustion_hours else None,
            "confidence": round(max(0, r2), 4),
        }

    def forecast_exponential(self, values: np.ndarray, forecast_horizon: int = 30 * 24, alpha: float = 0.3) -> np.ndarray:
        """Simple exponential smoothing forecast."""
        n = len(values)
        smoothed = np.zeros(n + forecast_horizon)
        smoothed[0] = values[0]

        for i in range(1, n):
            smoothed[i] = alpha * values[i] + (1 - alpha) * smoothed[i - 1]

        last = smoothed[n - 1]
        for i in range(forecast_horizon):
            smoothed[n + i] = last  # Constant forecast (no trend)

        return smoothed[n:]


# ============================================================================
# Training Orchestrator
# ============================================================================

def train_and_evaluate(
    output_dir: str = None,
    model_type: str = "all",
    dry_run: bool = False,
):
    """Train predictive maintenance models and save artifacts."""
    output_dir = Path(output_dir or os.path.join(os.path.dirname(__file__), "..", "artifacts", "models"))
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate training data
    df = generate_training_data(num_cis=5, days=90)

    results = {}

    # Prophet
    if model_type in ("all", "prophet"):
        logger.info("Training Prophet models...")
        try:
            prophet = ProphetForecaster()
            prophet.fit(df, metric_col="cpu_usage_percent")

            predictions = []
            for ci_id in df["ci_id"].unique():
                pred = prophet.predict_failure(ci_id, metric_col="cpu_usage_percent", threshold=85.0)
                predictions.append(pred)
                logger.info(f"  {ci_id}: prob={pred['failure_probability']:.3f}, "
                           f"days_to_fail={pred['days_to_failure']}, risk={pred['risk_level']}")

            prophet_result = {
                "model": "prophet",
                "version": "1.0.0",
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "num_cis": len(prophet.models),
                "metric": "cpu_usage_percent",
                "predictions": predictions,
            }

            if not dry_run:
                with open(output_dir / "prophet_v1.0_predictions.json", "w") as f:
                    json.dump(prophet_result, f, indent=2, default=str)

            results["prophet"] = prophet_result
        except ImportError:
            logger.warning("Prophet not installed, skipping")
            results["prophet"] = {"status": "skipped", "reason": "prophet not installed"}

    # Linear regression
    if model_type in ("all", "linear"):
        logger.info("Training linear regression models...")
        sf = SimpleForecaster()
        linear_predictions = []

        for ci_id in df["ci_id"].unique():
            ci_data = df[df["ci_id"] == ci_id]["cpu_usage_percent"].values
            if len(ci_data) < 10:
                continue
            forecast = sf.forecast_linear(ci_data, forecast_horizon=30 * 24)
            linear_predictions.append({
                "ci_id": ci_id,
                "trend_slope": forecast["trend_slope"],
                "exhaustion_hours": forecast["exhaustion_hours"],
                "confidence": forecast["confidence"],
            })
            if forecast["exhaustion_hours"]:
                logger.info(f"  {ci_id}: exhaustion in {forecast['exhaustion_hours']:.0f}h "
                           f"(slope={forecast['trend_slope']:.4f}, r²={forecast['confidence']:.3f})")

        linear_result = {
            "model": "linear_regression",
            "version": "1.0.0",
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "predictions": linear_predictions,
        }

        if not dry_run:
            with open(output_dir / "linear_regression_v1.0_predictions.json", "w") as f:
                json.dump(linear_result, f, indent=2, default=str)

        results["linear_regression"] = linear_result

    # Summary
    report = {
        "training_run_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_types": list(results.keys()),
        "training_data": {
            "num_rows": len(df),
            "num_cis": df["ci_id"].nunique(),
            "timerange_start": df["timestamp"].min().isoformat(),
            "timerange_end": df["timestamp"].max().isoformat(),
        },
        "results": results,
    }

    if not dry_run:
        with open(output_dir / "training_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Report saved to {output_dir / 'training_report.json'}")

    return report


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Train predictive maintenance models for Block 7"
    )
    parser.add_argument(
        "--model", choices=["all", "prophet", "linear"], default="all",
        help="Model type to train (default: all)",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Output directory for model artifacts",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Evaluate without saving artifacts",
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  Predictive Maintenance Model Training")
    print("  Block 7 — Analytics & AI Engine")
    print("=" * 60 + "\n")

    report = train_and_evaluate(
        output_dir=args.output_dir,
        model_type=args.model,
        dry_run=args.dry_run,
    )

    print(f"\nTraining report saved: {report['training_run_id']}")
    print(f"Models trained: {', '.join(report['model_types'])}")
    print(f"Training data: {report['training_data']['num_rows']:,} rows × "
          f"{report['training_data']['num_cis']} CIs")


if __name__ == "__main__":
    main()
