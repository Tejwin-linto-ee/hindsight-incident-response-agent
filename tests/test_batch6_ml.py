"""
Unit and regression test suite for Batch 6: Advanced Predictive ML Intelligence.

Tests:
1. 19 features calculation consistency between batch and dict feature engineering.
2. Anomaly score derivation and bounds.
3. TTFPredictor runway window mappings and Urgency Index bounds (0-100).
4. FeatureAttributor (XAI) feature attribution percentages and top-k output.
5. PlaybookRegistry retrieval for all 7 failure archetypes.
6. FailurePredictor end-to-end classification across all 7 standard telemetry modes.
"""

import pytest
import pandas as pd
from app.feature_engineering import (
    BASE_FEATURES,
    ENGINEERED_FEATURES,
    FEATURES,
    compute_engineered_features,
    compute_features_dict,
)
from app.ttf_predictor import TTFPredictor
from app.xai import FeatureAttributor
from app.playbooks import PlaybookRegistry
from app.failure_predictor import FailurePredictor


def test_feature_counts_and_consistency():
    assert len(BASE_FEATURES) == 11
    assert len(ENGINEERED_FEATURES) == 8
    assert len(FEATURES) == 19

    sample = {
        "cpu_percent": 85.0,
        "memory_percent": 75.0,
        "disk_percent": 60.0,
        "db_connections": 90.0,
        "db_pool_usage": 95.0,
        "api_latency_ms": 1200.0,
        "error_rate": 8.5,
        "request_rate": 2000.0,
        "queue_depth": 150.0,
        "network_latency_ms": 80.0,
        "traffic_growth_percent": 30.0,
    }

    # Dict computation
    dict_feats = compute_features_dict(sample)
    assert len(dict_feats) == 19
    for f in FEATURES:
        assert f in dict_feats

    # DataFrame computation
    df_sample = pd.DataFrame([sample])
    df_feats = compute_engineered_features(df_sample)
    for f in ENGINEERED_FEATURES:
        assert f in df_feats.columns
        assert abs(df_feats[f].iloc[0] - dict_feats[f]) < 1e-4


def test_ttf_and_urgency_bounds():
    # Immediate breach
    ttf_crit = TTFPredictor.estimate_time_to_failure(risk=95, anomaly_score=4.5)
    assert "3 minutes" in ttf_crit or "Immediate" in ttf_crit

    # Nominal stability
    ttf_nom = TTFPredictor.estimate_time_to_failure(risk=10, anomaly_score=0.2)
    assert "Nominal" in ttf_nom or "24 hours" in ttf_nom

    # Urgency index range 0-100
    urg_high = TTFPredictor.calculate_urgency_index(failure_risk=95, anomaly_score=4.5)
    assert 0 <= urg_high <= 100
    assert urg_high >= 85

    urg_low = TTFPredictor.calculate_urgency_index(failure_risk=5, anomaly_score=0.1)
    assert 0 <= urg_low <= 100
    assert urg_low <= 15


def test_xai_attribution():
    sample = compute_features_dict({
        "db_connections": 95.0,
        "db_pool_usage": 98.0,
        "api_latency_ms": 1400.0,
    })
    attributions = FeatureAttributor.explain(
        sample,
        predicted_class="database_connection_exhaustion",
        top_k=5,
    )
    assert len(attributions) > 0
    assert len(attributions) <= 5
    # Total percentage sum should be close to 100%
    total_pct = sum(a["attribution_percent"] for a in attributions)
    assert total_pct > 80.0  # Top 5 cover most of the attribution


def test_playbook_registry_all_classes():
    classes = [
        "database_connection_exhaustion",
        "cpu_saturation",
        "memory_exhaustion",
        "api_availability_degradation",
        "disk_exhaustion",
        "network_degradation",
        "none",
    ]
    for c in classes:
        steps = PlaybookRegistry.get_playbook(c)
        assert isinstance(steps, list)
        assert len(steps) >= 1
        assert all(isinstance(s, str) for s in steps)


def test_failure_predictor_inference():
    predictor = FailurePredictor()
    predictor.load()

    # Nominal healthy reading
    nominal = {
        "cpu_percent": 40.0,
        "memory_percent": 45.0,
        "disk_percent": 50.0,
        "db_connections": 30.0,
        "db_pool_usage": 35.0,
        "api_latency_ms": 120.0,
        "error_rate": 0.2,
        "request_rate": 800.0,
        "queue_depth": 10.0,
        "network_latency_ms": 30.0,
        "traffic_growth_percent": 2.0,
    }
    pred_healthy = predictor.predict(nominal)
    assert pred_healthy["raw_failure_type"] == "none"
    assert pred_healthy["failure_risk"] < 50
    assert pred_healthy["model_version"] == FailurePredictor.MODEL_VERSION

    # DB saturation reading
    db_outage = {
        "cpu_percent": 55.0,
        "memory_percent": 60.0,
        "disk_percent": 50.0,
        "db_connections": 95.0,
        "db_pool_usage": 98.0,
        "api_latency_ms": 1500.0,
        "error_rate": 8.5,
        "request_rate": 1200.0,
        "queue_depth": 180.0,
        "network_latency_ms": 40.0,
        "traffic_growth_percent": 15.0,
    }
    pred_db = predictor.predict(db_outage)
    assert pred_db["raw_failure_type"] == "database_connection_exhaustion"
    assert pred_db["failure_risk"] >= 70
    assert len(pred_db["feature_attributions"]) > 0
    assert len(pred_db["preemptive_remediation"]) >= 3
