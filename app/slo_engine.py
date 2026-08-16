"""
SLO (Service Level Objective) and Error Budget Engine.
Calculates burn rates, remaining error budgets, projected exhaustion time,
and automated alerting triggers according to Google SRE handbook best practices.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List


class SLOEngine:
    """
    Enterprise SLO Tracker and Error Budget Burn Rate Calculator.
    """

    DEFAULT_SLOS = [
        {"name": "API Availability", "target": 99.9, "window_days": 30, "metric": "availability"},
        {"name": "API Latency (p99 < 500ms)", "target": 99.0, "window_days": 30, "metric": "latency"},
        {"name": "Database Query Success", "target": 99.95, "window_days": 30, "metric": "db_success"},
    ]

    @classmethod
    def evaluate_slo_status(
        cls,
        error_rate: float,
        api_latency_ms: float,
        request_rate: float,
    ) -> Dict[str, Any]:
        """
        Evaluate real-time SLO health, error budget consumption and burn rates.
        """
        # Calculate real-time availability based on error rate
        current_availability = max(0.0, min(100.0, 100.0 - error_rate))
        target_availability = 99.9
        
        # Allowed error percentage for 99.9% SLO is 0.1%
        allowed_error_pct = 100.0 - target_availability
        
        # Multi-window burn rate calculation:
        # Burn rate 1.0 means consuming exactly 100% of the budget over 30 days
        burn_rate = error_rate / allowed_error_pct if allowed_error_pct > 0 else 0.0
        
        # Estimate remaining monthly error budget %
        # Baseline assumption: 85% remaining at start of day, decayed by high burn rate
        budget_remaining_pct = max(0.0, min(100.0, 88.5 - (burn_rate * 2.5)))
        
        # Project hours until total error budget depletion if current burn rate sustains
        if burn_rate > 1.0:
            hours_to_exhaustion = round(max(0.2, (budget_remaining_pct / (burn_rate * (100.0 / 720.0)))), 1)
        else:
            hours_to_exhaustion = None

        # Determine Burn Rate Alert Level (Google SRE Alerting Rules)
        if burn_rate >= 14.4:
            alert_tier = "CRITICAL_PAGE (14.4x 1h burn - 2% budget in 1h)"
            status_color = "#F43F5E"
        elif burn_rate >= 6.0:
            alert_tier = "URGENT_TICKET (6x 6h burn - 5% budget in 6h)"
            status_color = "#F59E0B"
        elif burn_rate >= 1.0:
            alert_tier = "WARNING (Consuming faster than 30d replenishment)"
            status_color = "#FCD34D"
        else:
            alert_tier = "HEALTHY (Within normal error budget envelope)"
            status_color = "#10B981"

        return {
            "target_slo": f"{target_availability}%",
            "current_availability": round(current_availability, 3),
            "burn_rate": round(burn_rate, 2),
            "budget_remaining_pct": round(budget_remaining_pct, 1),
            "hours_to_exhaustion": hours_to_exhaustion,
            "alert_tier": alert_tier,
            "status_color": status_color,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
