"""
Time-To-Failure (TTF) & Risk Dynamics Predictor.

Estimates the projected runway window before critical SLO breach / catastrophic
failure based on calibrated risk percentages and multi-variate anomaly intensity.
"""

from __future__ import annotations


class TTFPredictor:
    """
    Translates risk levels and anomaly scores into actionable SRE runway windows and urgency indices.
    """

    @staticmethod
    def estimate_time_to_failure(risk: int, anomaly_score: float) -> str:
        """
        Estimate time-to-failure window based on multi-variate anomaly score and failure risk.
        """
        if risk >= 90 or anomaly_score >= 4.0:
            return "< 3 minutes (Immediate Breach Imminent)"
        if risk >= 75 or anomaly_score >= 2.8:
            return "5 – 15 minutes (Rapid Saturation Curve)"
        if risk >= 50 or anomaly_score >= 1.8:
            return "15 – 30 minutes (Moderate Degradation Velocity)"
        if risk >= 25:
            return "30 – 60 minutes (Slow Drift)"
        return "Nominal (> 24 hours baseline stability)"

    @staticmethod
    def calculate_urgency_index(failure_risk: int, anomaly_score: float) -> int:
        """
        Derives a normalized 0-100 composite urgency index combining failure risk
        with the multi-variate distance score.
        """
        urgency = (failure_risk * 0.7) + (min(5.0, anomaly_score) * 6.0)
        return min(100, max(0, int(round(urgency))))
