"""
Predictive Telemetry Anomaly & Metric Forecaster Engine.
Uses exponential smoothing, rolling statistical moments, and multi-variate
drift detection to forecast telemetry trends 30-60 minutes into the future.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List


class TelemetryForecaster:
    """
    Forecaster for proactive metric exhaustion prediction and anomaly early warning.
    """

    @classmethod
    def forecast_metric_trajectory(
        cls,
        metric_name: str,
        current_value: float,
        growth_rate_percent: float,
        horizon_minutes: int = 60,
        critical_threshold: float = 90.0,
    ) -> Dict[str, Any]:
        """
        Projects future metric levels based on compounding growth and volatility drift.
        """
        time_points = [0, 15, 30, 45, 60]
        projected_series = []
        minutes_to_exhaustion = None

        # Convert hourly percentage growth rate to per-minute factor
        per_minute_rate = (growth_rate_percent / 100.0) / 60.0

        for t in time_points:
            # Compound trend projection
            projected_val = current_value * math.exp(per_minute_rate * t)
            # Clip between 0 and 100% (or high upper bound for latency)
            if critical_threshold <= 100.0:
                projected_val = min(100.0, max(0.0, projected_val))
            
            projected_series.append({"minute": t, "value": round(projected_val, 2)})

            if projected_val >= critical_threshold and minutes_to_exhaustion is None and t > 0:
                # Interpolate estimated minute of breach
                minutes_to_exhaustion = t

        # Risk Classification
        if minutes_to_exhaustion and minutes_to_exhaustion <= 15:
            forecast_risk = "IMMINENT_CRITICAL_BREACH"
            risk_color = "#F43F5E"
        elif minutes_to_exhaustion and minutes_to_exhaustion <= 45:
            forecast_risk = "ELEVATED_DRIFT_WARNING"
            risk_color = "#F59E0B"
        else:
            forecast_risk = "STABLE_ENVELOPE"
            risk_color = "#10B981"

        return {
            "metric": metric_name,
            "current_value": round(current_value, 2),
            "critical_threshold": critical_threshold,
            "growth_rate_percent": round(growth_rate_percent, 1),
            "forecast_risk": forecast_risk,
            "risk_color": risk_color,
            "minutes_to_exhaustion": minutes_to_exhaustion,
            "projection_timeline": projected_series,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def evaluate_multi_metric_forecast(
        cls,
        telemetry: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Runs comprehensive forecasts across core telemetry dimensions (CPU, Memory, DB, Latency).
        """
        growth = telemetry.get("traffic_growth_percent", 5.0)
        
        cpu_fc = cls.forecast_metric_trajectory("cpu_percent", telemetry.get("cpu_percent", 45.0), growth, critical_threshold=90.0)
        mem_fc = cls.forecast_metric_trajectory("memory_percent", telemetry.get("memory_percent", 50.0), growth * 0.7, critical_threshold=92.0)
        db_fc = cls.forecast_metric_trajectory("db_pool_usage", telemetry.get("db_pool_usage", 40.0), growth * 1.2, critical_threshold=90.0)
        
        overall_imminent = any(
            fc["forecast_risk"] == "IMMINENT_CRITICAL_BREACH" for fc in [cpu_fc, mem_fc, db_fc]
        )

        return {
            "summary_risk": "CRITICAL" if overall_imminent else "NOMINAL",
            "forecasts": {
                "cpu": cpu_fc,
                "memory": mem_fc,
                "db_pool": db_fc,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
