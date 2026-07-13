"""
Energy Optimization Service

Calculates PUE, cooling efficiency, power load balance, and provides optimization recommendations.

Reference: block7-analytics-ai-engine.md §7
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import uuid
import json

logger = logging.getLogger(__name__)


class EnergyOptimizationService:
    """
    Energy optimization for data center operations.

    Calculates:
    - PUE (Power Usage Effectiveness)
    - Cooling efficiency
    - Power load balance
    - Carbon intensity

    Provides recommendations for energy optimization.
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
            logger.info("Connected to TimescaleDB for energy optimization")
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            raise

    def get_power_metrics(self, time_range_hours: int = 24) -> Dict[str, float]:
        """Get latest power consumption metrics"""
        try:
            cur = self.conn.cursor()

            # Total facility power
            cur.execute("""
                SELECT AVG(value) as avg_value
                FROM metrics
                WHERE metric_name = 'total_facility_power'
                AND time > NOW() - INTERVAL '%s hours'
            """, (time_range_hours,))
            total_power_row = cur.fetchone()
            total_power = total_power_row['avg_value'] if total_power_row else 0.0

            # IT equipment power
            cur.execute("""
                SELECT AVG(value) as avg_value
                FROM metrics
                WHERE metric_name = 'it_equipment_power'
                AND time > NOW() - INTERVAL '%s hours'
            """, (time_range_hours,))
            it_power_row = cur.fetchone()
            it_power = it_power_row['avg_value'] if it_power_row else 0.0

            # Cooling power
            cur.execute("""
                SELECT AVG(value) as avg_value
                FROM metrics
                WHERE metric_name = 'cooling_power'
                AND time > NOW() - INTERVAL '%s hours'
            """, (time_range_hours,))
            cooling_power_row = cur.fetchone()
            cooling_power = cooling_power_row['avg_value'] if cooling_power_row else 0.0

            return {
                'total_power_kw': float(total_power),
                'it_power_kw': float(it_power),
                'cooling_power_kw': float(cooling_power)
            }

        except Exception as e:
            logger.error(f"Failed to fetch power metrics: {e}")
            return {
                'total_power_kw': 0.0,
                'it_power_kw': 0.0,
                'cooling_power_kw': 0.0
            }

    def calculate_pue(self, total_power_kw: float, it_power_kw: float) -> Dict[str, Any]:
        """
        Calculate PUE (Power Usage Effectiveness).

        PUE = Total Facility Power / IT Equipment Power

        Rating:
        - 3.0+: Very inefficient
        - 2.0-3.0: Inefficient
        - 1.5-2.0: Average
        - 1.2-1.5: Good
        - < 1.2: Excellent
        """
        if it_power_kw == 0:
            return {
                'pue': None,
                'rating': 'unknown',
                'message': 'IT power is zero - cannot calculate PUE'
            }

        pue = total_power_kw / it_power_kw

        # Rating
        if pue >= 3.0:
            rating = 'very_inefficient'
        elif pue >= 2.0:
            rating = 'inefficient'
        elif pue >= 1.5:
            rating = 'average'
        elif pue >= 1.2:
            rating = 'good'
        else:
            rating = 'excellent'

        return {
            'pue': round(pue, 3),
            'rating': rating,
            'total_power_kw': round(total_power_kw, 2),
            'it_power_kw': round(it_power_kw, 2),
            'overhead_power_kw': round(total_power_kw - it_power_kw, 2),
            'efficiency_pct': round((it_power_kw / total_power_kw) * 100, 2) if total_power_kw > 0 else 0
        }

    def calculate_cooling_efficiency(
        self,
        cooling_power_kw: float,
        it_power_kw: float
    ) -> Dict[str, Any]:
        """
        Calculate cooling efficiency.

        Cooling Efficiency = Cooling Power / IT Power

        Target: < 0.5 (cooling uses less than 50% of IT power)
        """
        if it_power_kw == 0:
            return {
                'cooling_efficiency': None,
                'rating': 'unknown'
            }

        cooling_efficiency = cooling_power_kw / it_power_kw

        # Rating
        if cooling_efficiency < 0.3:
            rating = 'excellent'
        elif cooling_efficiency < 0.5:
            rating = 'good'
        elif cooling_efficiency < 0.7:
            rating = 'average'
        else:
            rating = 'poor'

        return {
            'cooling_efficiency': round(cooling_efficiency, 4),
            'rating': rating,
            'cooling_power_kw': round(cooling_power_kw, 2),
            'it_power_kw': round(it_power_kw, 2),
            'cooling_to_it_ratio_pct': round(cooling_efficiency * 100, 2)
        }

    def calculate_power_load_balance(self) -> Dict[str, Any]:
        """
        Calculate power load balance across power distribution units (PDUs).

        Imbalance > 20% indicates potential issues.
        """
        try:
            cur = self.conn.cursor()

            # Get power per PDU
            cur.execute("""
                SELECT
                    source,
                    AVG(value) as avg_power
                FROM metrics
                WHERE metric_name = 'pdu_power'
                AND time > NOW() - INTERVAL '1 hour'
                GROUP BY source
            """)
            rows = cur.fetchall()

            if not rows:
                return {
                    'status': 'no_data',
                    'message': 'No PDU power data available'
                }

            powers = [float(row['avg_power']) for row in rows]
            avg_power = sum(powers) / len(powers)
            max_power = max(powers)
            min_power = min(powers)

            # Calculate imbalance
            imbalance_pct = ((max_power - min_power) / avg_power) * 100 if avg_power > 0 else 0

            # Rating
            if imbalance_pct < 10:
                rating = 'balanced'
            elif imbalance_pct < 20:
                rating = 'acceptable'
            else:
                rating = 'imbalanced'

            return {
                'imbalance_pct': round(imbalance_pct, 2),
                'rating': rating,
                'pdu_count': len(powers),
                'avg_power_kw': round(avg_power, 2),
                'max_power_kw': round(max_power, 2),
                'min_power_kw': round(min_power, 2)
            }

        except Exception as e:
            logger.error(f"Failed to calculate power load balance: {e}")
            return {'status': 'error', 'message': str(e)}

    def generate_optimization_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive energy optimization report.

        Returns:
            Report with PUE, cooling efficiency, power balance, and recommendations
        """
        try:
            # Get power metrics
            power_metrics = self.get_power_metrics(time_range_hours=24)

            # Calculate PUE
            pue_result = self.calculate_pue(
                power_metrics['total_power_kw'],
                power_metrics['it_power_kw']
            )

            # Calculate cooling efficiency
            cooling_result = self.calculate_cooling_efficiency(
                power_metrics['cooling_power_kw'],
                power_metrics['it_power_kw']
            )

            # Calculate power load balance
            balance_result = self.calculate_power_load_balance()

            # Generate recommendations
            recommendations = self._generate_recommendations(
                pue_result,
                cooling_result,
                balance_result
            )

            # Build report
            report = {
                'report_id': str(uuid.uuid4()),
                'report_date': date.today().isoformat(),
                'pue': pue_result.get('pue'),
                'pue_rating': pue_result.get('rating'),
                'total_power_kw': power_metrics['total_power_kw'],
                'it_power_kw': power_metrics['it_power_kw'],
                'cooling_power_kw': power_metrics['cooling_power_kw'],
                'cooling_efficiency': cooling_result.get('cooling_efficiency'),
                'cooling_rating': cooling_result.get('rating'),
                'power_load_balance': balance_result.get('imbalance_pct'),
                'balance_rating': balance_result.get('rating'),
                'carbon_intensity_gco2_kwh': None,  # TODO: Integrate with carbon intensity API
                'recommendations': recommendations,
                'created_at': datetime.now().isoformat()
            }

            # Store in database
            self._store_report(report)

            logger.info(f"Generated energy optimization report: PUE={pue_result.get('pue')}, Cooling={cooling_result.get('cooling_efficiency')}")

            return report

        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}", exc_info=True)
            raise

    def _generate_recommendations(
        self,
        pue_result: Dict,
        cooling_result: Dict,
        balance_result: Dict
    ) -> List[str]:
        """Generate actionable optimization recommendations"""
        recommendations = []

        # PUE recommendations
        pue = pue_result.get('pue')
        if pue and pue >= 2.0:
            recommendations.append(f"⚠️ PUE is {pue:.2f} (inefficient) - review cooling and power distribution")
            recommendations.append("Consider implementing hot aisle/cold aisle containment")
            recommendations.append("Review CRAC/CRAH unit efficiency and airflow")
        elif pue and pue >= 1.5:
            recommendations.append(f"PUE is {pue:.2f} (average) - room for improvement")
            recommendations.append("Optimize cooling setpoints and airflow management")

        # Cooling recommendations
        cooling_eff = cooling_result.get('cooling_efficiency')
        if cooling_eff and cooling_eff > 0.7:
            recommendations.append(f"⚠️ Cooling efficiency is poor ({cooling_eff:.2f}) - cooling using {cooling_eff*100:.1f}% of IT power")
            recommendations.append("Consider free cooling / economizer mode if ambient allows")
            recommendations.append("Review chiller efficiency and cooling tower performance")
        elif cooling_eff and cooling_eff > 0.5:
            recommendations.append("Cooling efficiency acceptable but can be improved")
            recommendations.append("Increase cold aisle temperature if within equipment specs")

        # Power balance recommendations
        imbalance = balance_result.get('imbalance_pct')
        if imbalance and imbalance > 20:
            recommendations.append(f"⚠️ Power load imbalance detected ({imbalance:.1f}%) - redistribute loads across PDUs")
            recommendations.append("Review rack placement and power distribution strategy")

        # General recommendations
        if not recommendations:
            recommendations.append("✓ Energy metrics within acceptable range")
            recommendations.append("Continue monitoring and maintain current practices")

        recommendations.append("Schedule quarterly energy audit to maintain efficiency")

        return recommendations

    def _store_report(self, report: Dict[str, Any]):
        """Store energy report in TimescaleDB"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO energy_reports (
                    report_id, report_date, pue, total_power_kw, it_power_kw,
                    cooling_power_kw, cooling_efficiency, power_load_balance,
                    carbon_intensity_gco2_kwh, recommendations
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                report['report_id'],
                report['report_date'],
                report['pue'],
                report['total_power_kw'],
                report['it_power_kw'],
                report['cooling_power_kw'],
                report['cooling_efficiency'],
                report['power_load_balance'],
                report['carbon_intensity_gco2_kwh'],
                json.dumps(report['recommendations'])
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to store energy report: {e}")
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

    service = EnergyOptimizationService(db_config)

    # Test report generation
    result = service.generate_optimization_report()
    print(json.dumps(result, indent=2))

    service.close()
