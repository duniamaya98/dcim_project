"""
Capacity Forecasting Service

Generates capacity forecasts for CPU, memory, storage, network resources.
Uses linear regression and trend analysis for projections.

Reference: block7-analytics-ai-engine.md §6
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.linear_model import LinearRegression
import uuid
import json

logger = logging.getLogger(__name__)


class CapacityForecastingService:
    """
    Capacity forecasting for data center resources.

    Forecasts:
    - CPU utilization
    - Memory utilization
    - Storage capacity
    - Network bandwidth
    - Power consumption
    - Rack space
    """

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.conn = None
        self._connect_db()

    def _connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                **self.db_config,
                cursor_factory=RealDictCursor
            )
            logger.info("Connected to TimescaleDB for capacity forecasting")
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            raise

    def get_historical_data(
        self,
        metric_name: str,
        ci_id: Optional[str] = None,
        days: int = 30
    ) -> List[Dict]:
        """Get historical metrics for forecasting"""
        try:
            cur = self.conn.cursor()

            query = """
                SELECT
                    time_bucket('1 day', time) AS bucket,
                    AVG(value) AS avg_value,
                    MAX(value) AS max_value
                FROM metrics
                WHERE metric_name = %s
                AND time > NOW() - INTERVAL '%s days'
            """
            params = [metric_name, days]

            if ci_id:
                query += " AND ci_id = %s"
                params.append(ci_id)

            query += " GROUP BY bucket ORDER BY bucket"

            cur.execute(query, params)
            rows = cur.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            return []

    def forecast_linear(
        self,
        historical_data: List[Dict],
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Linear regression forecast.

        Returns:
            {
                'projected_values': [...],
                'projected_dates': [...],
                'slope': float,
                'confidence': float
            }
        """
        if len(historical_data) < 7:
            raise ValueError("Not enough historical data (need at least 7 days)")

        # Prepare data
        X = np.array(range(len(historical_data))).reshape(-1, 1)
        y = np.array([d['avg_value'] for d in historical_data])

        # Fit linear model
        model = LinearRegression()
        model.fit(X, y)

        # Calculate R² score as confidence
        r2_score = model.score(X, y)

        # Project future
        future_X = np.array(range(len(historical_data), len(historical_data) + days_ahead)).reshape(-1, 1)
        projected_values = model.predict(future_X)

        # Calculate projected dates
        last_date = historical_data[-1]['bucket']
        projected_dates = [
            (last_date + timedelta(days=i)).isoformat()
            for i in range(1, days_ahead + 1)
        ]

        return {
            'projected_values': projected_values.tolist(),
            'projected_dates': projected_dates,
            'slope': float(model.coef_[0]),
            'intercept': float(model.intercept_),
            'confidence': float(r2_score)
        }

    def calculate_exhaustion_date(
        self,
        current_value: float,
        projected_values: List[float],
        projected_dates: List[str],
        threshold: float = 90.0
    ) -> Optional[str]:
        """Calculate when resource will exceed threshold"""
        for value, date in zip(projected_values, projected_dates):
            if value >= threshold:
                return date
        return None

    def generate_forecast(
        self,
        resource_type: str,
        ci_id: Optional[str] = None,
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Generate capacity forecast for a resource.

        Args:
            resource_type: 'cpu', 'memory', 'storage', 'network', 'power'
            ci_id: Optional CI ID filter
            days_ahead: Forecast window (default 30 days)

        Returns:
            Forecast report with exhaustion date and recommendations
        """
        try:
            # Map resource type to metric name
            metric_map = {
                'cpu': 'cpu_usage',
                'memory': 'memory_usage',
                'storage': 'disk_usage',
                'network': 'network_usage',
                'power': 'power_consumption'
            }

            metric_name = metric_map.get(resource_type)
            if not metric_name:
                raise ValueError(f"Unknown resource type: {resource_type}")

            # Get historical data
            historical_data = self.get_historical_data(metric_name, ci_id, days=30)

            if len(historical_data) < 7:
                return {
                    'status': 'insufficient_data',
                    'message': f'Need at least 7 days of data, got {len(historical_data)}'
                }

            # Current usage
            current_value = historical_data[-1]['avg_value']

            # Generate forecast
            forecast = self.forecast_linear(historical_data, days_ahead)

            # Calculate exhaustion date (90% threshold)
            exhaustion_date = self.calculate_exhaustion_date(
                current_value,
                forecast['projected_values'],
                forecast['projected_dates'],
                threshold=90.0
            )

            # Calculate projected usage at end of window
            projected_usage_pct = forecast['projected_values'][-1]

            # Generate recommendations
            recommendations = self._generate_recommendations(
                resource_type,
                current_value,
                projected_usage_pct,
                exhaustion_date
            )

            # Build report
            report = {
                'forecast_id': str(uuid.uuid4()),
                'resource_type': resource_type,
                'ci_id': ci_id,
                'forecast_date': datetime.now().date().isoformat(),
                'current_usage_pct': round(current_value, 2),
                'projected_usage_pct': round(projected_usage_pct, 2),
                'projected_exhaustion_date': exhaustion_date,
                'confidence': round(forecast['confidence'], 4),
                'model': 'linear_regression',
                'forecast_window_days': days_ahead,
                'trend': 'increasing' if forecast['slope'] > 0 else 'decreasing',
                'recommendations': recommendations,
                'created_at': datetime.now().isoformat()
            }

            # Store in database
            self._store_forecast(report)

            logger.info(f"Generated capacity forecast: {resource_type} (projected: {projected_usage_pct:.1f}%)")

            return report

        except Exception as e:
            logger.error(f"Failed to generate forecast: {e}", exc_info=True)
            raise

    def _generate_recommendations(
        self,
        resource_type: str,
        current_pct: float,
        projected_pct: float,
        exhaustion_date: Optional[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if exhaustion_date:
            recommendations.append(f"⚠️ Resource exhaustion projected on {exhaustion_date}")
            recommendations.append(f"Immediate action required to expand {resource_type} capacity")

        if projected_pct > 80:
            recommendations.append(f"High utilization projected ({projected_pct:.1f}%) - plan capacity expansion")

        if projected_pct > 90:
            recommendations.append(f"Critical: Projected usage exceeds 90% - urgent capacity planning needed")

        growth_rate = projected_pct - current_pct
        if growth_rate > 20:
            recommendations.append(f"High growth rate detected (+{growth_rate:.1f}%) - monitor closely")

        # Resource-specific recommendations
        if resource_type == 'cpu':
            if projected_pct > 75:
                recommendations.append("Consider horizontal scaling (add more nodes)")
        elif resource_type == 'memory':
            if projected_pct > 75:
                recommendations.append("Consider upgrading RAM or optimizing memory usage")
        elif resource_type == 'storage':
            if projected_pct > 75:
                recommendations.append("Plan storage expansion or implement data archival")
        elif resource_type == 'power':
            if projected_pct > 80:
                recommendations.append("Review power distribution and cooling capacity")

        if not recommendations:
            recommendations.append("✓ Capacity within normal range - continue monitoring")

        return recommendations

    def _store_forecast(self, report: Dict[str, Any]):
        """Store forecast in TimescaleDB"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO capacity_forecasts (
                    forecast_id, resource_type, ci_id, forecast_date,
                    current_usage_pct, projected_usage_pct, projected_exhaustion_date,
                    confidence, model, recommendations
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                report['forecast_id'],
                report['resource_type'],
                report.get('ci_id'),
                report['forecast_date'],
                report['current_usage_pct'],
                report['projected_usage_pct'],
                report['projected_exhaustion_date'],
                report['confidence'],
                report['model'],
                json.dumps(report['recommendations'])
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to store forecast: {e}")
            self.conn.rollback()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    import os

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    db_config = {
        "host": os.getenv("TIMESCALEDB_HOST", "10.70.0.56"),
        "port": int(os.getenv("TIMESCALEDB_PORT", "5433")),
        "database": os.getenv("TIMESCALEDB_DATABASE", "dcim_analytics"),
        "user": os.getenv("TIMESCALEDB_USER", "ai_team"),
        "password": os.environ["TIMESCALEDB_PASSWORD"]
    }

    service = CapacityForecastingService(db_config)

    # Test forecast
    result = service.generate_forecast('cpu', days_ahead=30)
    print(json.dumps(result, indent=2))

    service.close()
