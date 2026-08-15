"""
Centralized Feature Engineering Module.

Single canonical source of all 19 ML features used by both the training
pipeline (generate_dataset.py) and real-time inference (failure_predictor.py).

Having one module prevents training/inference mismatch -- both paths call the
same formulas with the same normalization constants.

Feature groups
--------------
BASE_FEATURES  (11)  -- raw telemetry metrics streamed from the simulator
ENGINEERED_FEATURES (8) -- domain-specific compound indices derived from base
FEATURES (19)  -- full vector fed to the ML model
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ============================================================
# FEATURE LISTS  (single source of truth)
# ============================================================

BASE_FEATURES: list[str] = [
    "cpu_percent",
    "memory_percent",
    "disk_percent",
    "db_connections",
    "db_pool_usage",
    "api_latency_ms",
    "error_rate",
    "request_rate",
    "queue_depth",
    "network_latency_ms",
    "traffic_growth_percent",
]

ENGINEERED_FEATURES: list[str] = [
    "db_stress_index",
    "queue_pressure",
    "system_load_compound",
    "traffic_error_density",
    "network_congestion_ratio",
    "latency_error_divergence",
    "resource_saturation_max",
    "anomaly_score",
]

FEATURES: list[str] = BASE_FEATURES + ENGINEERED_FEATURES

# ============================================================
# NOMINAL HEALTHY BASELINE  (for anomaly scoring)
# ============================================================

NOMINAL_BASELINE: dict[str, float] = {
    "cpu_percent": 45.0,
    "memory_percent": 50.0,
    "disk_percent": 55.0,
    "db_connections": 45.0,
    "db_pool_usage": 45.0,
    "api_latency_ms": 150.0,
    "error_rate": 1.5,
    "request_rate": 1000.0,
    "queue_depth": 30.0,
    "network_latency_ms": 40.0,
    "traffic_growth_percent": 5.0,
}

NOMINAL_STDS: dict[str, float] = {
    "cpu_percent": 15.0,
    "memory_percent": 12.0,
    "disk_percent": 15.0,
    "db_connections": 15.0,
    "db_pool_usage": 15.0,
    "api_latency_ms": 60.0,
    "error_rate": 1.0,
    "request_rate": 250.0,
    "queue_depth": 15.0,
    "network_latency_ms": 15.0,
    "traffic_growth_percent": 10.0,
}


# ============================================================
# DATAFRAME-BASED  (used during training)
# ============================================================

def compute_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all 8 engineered features for a DataFrame of raw telemetry.
    Returns a copy of the DataFrame with 8 new feature columns appended.

    Formulas
    --------
    db_stress_index          = (db_connections x db_pool_usage) / 100
    queue_pressure           = (queue_depth x api_latency_ms) / 1000
    system_load_compound     = 0.5*cpu + 0.5*memory
    traffic_error_density    = (error_rate x request_rate) / 1000
    network_congestion_ratio = network_latency_ms / (api_latency_ms + eps)
    latency_error_divergence = (api_latency_ms/150) x (error_rate/1.5)
    resource_saturation_max  = max(cpu, memory, disk, db_pool_usage)
    anomaly_score            = sqrt(mean of squared positive z-scores)
    """
    df = df.copy()

    df["db_stress_index"] = (df["db_connections"] * df["db_pool_usage"]) / 100.0
    df["queue_pressure"] = (df["queue_depth"] * df["api_latency_ms"]) / 1000.0
    df["system_load_compound"] = 0.5 * df["cpu_percent"] + 0.5 * df["memory_percent"]
    df["traffic_error_density"] = (df["error_rate"] * df["request_rate"]) / 1000.0
    df["network_congestion_ratio"] = df["network_latency_ms"] / (df["api_latency_ms"] + 1e-5)
    df["latency_error_divergence"] = (df["api_latency_ms"] / 150.0) * (df["error_rate"] / 1.5)
    df["resource_saturation_max"] = df[
        ["cpu_percent", "memory_percent", "disk_percent", "db_pool_usage"]
    ].max(axis=1)

    z_sq = 0.0
    for col, mean in NOMINAL_BASELINE.items():
        std = NOMINAL_STDS[col]
        z = (df[col] - mean) / std
        z_sq += np.clip(z, 0, None) ** 2

    df["anomaly_score"] = np.sqrt(z_sq / len(NOMINAL_BASELINE)).round(2)
    return df


# ============================================================
# DICT-BASED  (used during real-time inference)
# ============================================================

def compute_features_dict(telemetry: dict[str, float]) -> dict[str, float]:
    """
    Compute all 19 features from a single raw telemetry reading.
    Returns a dict with all 19 feature keys suitable for model.predict_proba().
    Missing keys fall back to NOMINAL_BASELINE values.
    """
    row: dict[str, float] = {
        k: float(telemetry.get(k, NOMINAL_BASELINE.get(k, 0.0)))
        for k in BASE_FEATURES
    }

    row["db_stress_index"] = (row["db_connections"] * row["db_pool_usage"]) / 100.0
    row["queue_pressure"] = (row["queue_depth"] * row["api_latency_ms"]) / 1000.0
    row["system_load_compound"] = 0.5 * row["cpu_percent"] + 0.5 * row["memory_percent"]
    row["traffic_error_density"] = (row["error_rate"] * row["request_rate"]) / 1000.0
    row["network_congestion_ratio"] = row["network_latency_ms"] / (row["api_latency_ms"] + 1e-5)
    row["latency_error_divergence"] = (row["api_latency_ms"] / 150.0) * (row["error_rate"] / 1.5)
    row["resource_saturation_max"] = max(
        row["cpu_percent"], row["memory_percent"],
        row["disk_percent"], row["db_pool_usage"],
    )

    z_sq = 0.0
    for col, mean in NOMINAL_BASELINE.items():
        std = NOMINAL_STDS[col]
        z = (row[col] - mean) / std
        z_sq += (max(0.0, z)) ** 2

    row["anomaly_score"] = float(round(np.sqrt(z_sq / len(NOMINAL_BASELINE)), 2))
    return row
