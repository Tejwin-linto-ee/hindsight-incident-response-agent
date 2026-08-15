"""
Explainable AI (XAI) Attribution Module.

Computes local feature contribution scores to explain why the ensemble
model predicted a specific failure archetype, highlighting the top telemetry
signals that deviated from the healthy baseline.
"""

from __future__ import annotations
from typing import Any
from app.feature_engineering import BASE_FEATURES, NOMINAL_BASELINE, NOMINAL_STDS


class FeatureAttributor:
    """
    Computes local feature importance and drivers for a given prediction.
    """

    TYPE_AFFINITIES: dict[str, list[str]] = {
        "database_connection_exhaustion": [
            "db_pool_usage", "db_connections", "db_stress_index",
            "api_latency_ms", "queue_pressure",
        ],
        "cpu_saturation": [
            "cpu_percent", "request_rate", "traffic_growth_percent",
            "system_load_compound", "queue_depth",
        ],
        "memory_exhaustion": [
            "memory_percent", "system_load_compound", "resource_saturation_max",
            "api_latency_ms", "cpu_percent",
        ],
        "api_availability_degradation": [
            "error_rate", "api_latency_ms", "traffic_error_density",
            "latency_error_divergence", "queue_pressure",
        ],
        "disk_exhaustion": [
            "disk_percent", "resource_saturation_max", "api_latency_ms", "error_rate",
        ],
        "network_degradation": [
            "network_latency_ms", "network_congestion_ratio", "api_latency_ms",
            "queue_depth", "error_rate",
        ],
        "none": [
            "cpu_percent", "memory_percent", "db_pool_usage", "error_rate", "api_latency_ms",
        ],
    }

    @classmethod
    def explain(
        cls,
        full_features: dict[str, float],
        predicted_class: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Calculate local feature contribution scores highlighting which telemetry signals
        most aggressively pushed the prediction toward this failure class.
        """
        attributions: list[dict[str, Any]] = []
        affinities = cls.TYPE_AFFINITIES.get(predicted_class, BASE_FEATURES)

        for feat in BASE_FEATURES:
            val = float(full_features.get(feat, 0.0))
            baseline = NOMINAL_BASELINE.get(feat, 1.0)
            std = NOMINAL_STDS.get(feat, 1.0)

            # Relative deviation from baseline
            z = max(0.0, (val - baseline) / std)
            is_target_aff = feat in affinities
            weight = 1.6 if is_target_aff else 1.0
            impact = z * weight

            if impact > 0.1 or is_target_aff:
                attributions.append({
                    "feature": feat,
                    "value": round(val, 2),
                    "impact_score": round(impact, 2),
                    "is_driver": is_target_aff and z > 1.2,
                })

        # Normalize impact to percentage
        total_impact = sum(a["impact_score"] for a in attributions) + 1e-5
        for a in attributions:
            a["attribution_percent"] = round((a["impact_score"] / total_impact) * 100.0, 1)

        attributions.sort(key=lambda item: item["attribution_percent"], reverse=True)
        return attributions[:top_k]
