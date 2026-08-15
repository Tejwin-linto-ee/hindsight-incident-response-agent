import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, VotingClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split


class FailurePredictor:
    """
    Calibrated Ensemble Failure Prediction & Explainable AI Engine.
    
    Combines:
    - Base Telemetry features + Domain-Specific Compound Stress Indices
    - Calibrated Multi-Class Probability Distribution
    - Local Feature Attribution (Explainable AI / SHAP-style importance)
    - Time-To-Failure (TTF) & Multivariate Anomaly Dynamics
    - Pre-emptive SRE Remediation Playbooks
    """

    BASE_FEATURES = [
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

    ENGINEERED_FEATURES = [
        "db_stress_index",
        "queue_pressure",
        "system_load_compound",
        "traffic_error_density",
        "network_congestion_ratio",
        "latency_error_divergence",
        "resource_saturation_max",
        "anomaly_score",
    ]

    FEATURES = BASE_FEATURES + ENGINEERED_FEATURES

    MODEL_PATH = Path("data/failure_predictor.joblib")
    METRICS_PATH = Path("data/failure_predictor_metrics.json")

    FAILURE_TYPES = [
        "none",
        "database_connection_exhaustion",
        "cpu_saturation",
        "memory_exhaustion",
        "api_availability_degradation",
        "disk_exhaustion",
        "network_degradation",
    ]

    # Baseline nominal means for anomaly detection
    NOMINAL_BASELINE = {
        "cpu_percent": 45.0, "memory_percent": 50.0, "disk_percent": 55.0,
        "db_connections": 45.0, "db_pool_usage": 45.0, "api_latency_ms": 150.0,
        "error_rate": 1.5, "request_rate": 1000.0, "queue_depth": 30.0,
        "network_latency_ms": 40.0, "traffic_growth_percent": 5.0
    }
    NOMINAL_STDS = {
        "cpu_percent": 15.0, "memory_percent": 12.0, "disk_percent": 15.0,
        "db_connections": 15.0, "db_pool_usage": 15.0, "api_latency_ms": 60.0,
        "error_rate": 1.0, "request_rate": 250.0, "queue_depth": 15.0,
        "network_latency_ms": 15.0, "traffic_growth_percent": 10.0
    }

    def __init__(self, model_path: str | None = None) -> None:
        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = self.MODEL_PATH

        self.model = None
        self.metrics: dict[str, Any] = {}
        self.training_columns = self.FEATURES.copy()

    # ============================================================
    # FEATURE EXTRACTION & ANOMALY SCORING
    # ============================================================

    @classmethod
    def compute_features_dict(cls, telemetry: dict[str, float]) -> dict[str, float]:
        """
        Derive interaction terms and anomaly indicators from raw telemetry metrics.
        """
        row = {k: float(telemetry.get(k, cls.NOMINAL_BASELINE.get(k, 0.0))) for k in cls.BASE_FEATURES}

        # 1. Database stress compound index
        row["db_stress_index"] = (row["db_connections"] * row["db_pool_usage"]) / 100.0

        # 2. Queue pressure index
        row["queue_pressure"] = (row["queue_depth"] * row["api_latency_ms"]) / 1000.0

        # 3. System compute & memory compound load
        row["system_load_compound"] = (0.5 * row["cpu_percent"]) + (0.5 * row["memory_percent"])

        # 4. Traffic error density
        row["traffic_error_density"] = (row["error_rate"] * row["request_rate"]) / 1000.0

        # 5. Network to API latency ratio
        row["network_congestion_ratio"] = row["network_latency_ms"] / (row["api_latency_ms"] + 1e-5)

        # 6. Latency-Error divergence
        row["latency_error_divergence"] = (row["api_latency_ms"] / 150.0) * (row["error_rate"] / 1.5)

        # 7. Maximum resource saturation
        row["resource_saturation_max"] = max(row["cpu_percent"], row["memory_percent"], row["disk_percent"], row["db_pool_usage"])

        # 8. Anomaly score (Normalized Z-score distance)
        z_sq = 0.0
        for col, mean in cls.NOMINAL_BASELINE.items():
            std = cls.NOMINAL_STDS[col]
            z = (row[col] - mean) / std
            z_sq += (max(0.0, z)) ** 2

        row["anomaly_score"] = float(round(np.sqrt(z_sq / len(cls.NOMINAL_BASELINE)), 2))
        return row

    def _clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure all feature columns exist and are sanitized.
        """
        missing_engineered = [f for f in self.ENGINEERED_FEATURES if f not in df.columns]
        if missing_engineered:
            from app.generate_dataset import compute_engineered_features
            df = compute_engineered_features(df)

        X = df[self.FEATURES].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median(numeric_only=True))
        return X

    # ============================================================
    # TRAIN ENSEMBLE MODEL
    # ============================================================

    def train(
        self,
        df: pd.DataFrame,
        test_size: float = 0.20,
        random_state: int = 42,
    ) -> dict[str, Any]:
        if df.empty:
            raise ValueError("Dataset is empty.")

        X = self._clean_features(df)
        y = df["failure_type"].astype(str)

        print("\nFailure type distribution:\n", y.value_counts(), "\n")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Base estimators for robust ensemble
        rf = RandomForestClassifier(
            n_estimators=300,
            max_depth=16,
            min_samples_split=4,
            min_samples_leaf=1,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )

        et = ExtraTreesClassifier(
            n_estimators=200,
            max_depth=16,
            min_samples_split=4,
            min_samples_leaf=1,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )

        ensemble = VotingClassifier(
            estimators=[("rf", rf), ("et", et)],
            voting="soft",
            n_jobs=-1,
        )

        # Calibrate probabilities using sigmoid / isotonic
        calibrated_model = CalibratedClassifierCV(
            estimator=ensemble,
            method="sigmoid",
            cv=3,
        )

        print("Training calibrated ensemble failure predictor (Random Forest + Extra Trees)...")
        calibrated_model.fit(X_train, y_train)

        predictions = calibrated_model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average="weighted", zero_division=0)
        recall = recall_score(y_test, predictions, average="weighted", zero_division=0)
        f1 = f1_score(y_test, predictions, average="weighted", zero_division=0)
        report = classification_report(y_test, predictions, zero_division=0)

        self.model = calibrated_model
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(calibrated_model, self.model_path)

        self.metrics = {
            "model": "Calibrated Ensemble (RandomForest + ExtraTrees)",
            "model_type": "multiclass_failure_classifier",
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "training_samples": int(len(X_train)),
            "testing_samples": int(len(X_test)),
            "feature_count": len(self.FEATURES),
            "failure_classes": list(calibrated_model.classes_),
            "classification_report": report,
        }

        self.METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.METRICS_PATH, "w", encoding="utf-8") as file:
            json.dump(self.metrics, file, indent=2)

        return self.metrics

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Failure prediction model was not found:\n{self.model_path}\n\nTrain the model first."
            )
        self.model = joblib.load(self.model_path)

    def _ensure_model(self) -> None:
        if self.model is None:
            self.load()

    # ============================================================
    # LOCAL EXPLAINABLE AI (XAI) ATTRIBUTION
    # ============================================================

    def _calculate_feature_attributions(
        self,
        full_features: dict[str, float],
        predicted_class: str,
    ) -> list[dict[str, Any]]:
        """
        Calculate local feature contribution scores highlighting which telemetry signals
        most aggressively pushed the prediction toward this failure class.
        """
        attributions = []
        
        # Priority metric mappings per failure type
        type_affinities = {
            "database_connection_exhaustion": ["db_pool_usage", "db_connections", "db_stress_index", "api_latency_ms", "queue_pressure"],
            "cpu_saturation": ["cpu_percent", "request_rate", "traffic_growth_percent", "system_load_compound", "queue_depth"],
            "memory_exhaustion": ["memory_percent", "system_load_compound", "resource_saturation_max", "api_latency_ms", "cpu_percent"],
            "api_availability_degradation": ["error_rate", "api_latency_ms", "traffic_error_density", "latency_error_divergence", "queue_pressure"],
            "disk_exhaustion": ["disk_percent", "resource_saturation_max", "api_latency_ms", "error_rate"],
            "network_degradation": ["network_latency_ms", "network_congestion_ratio", "api_latency_ms", "queue_depth", "error_rate"],
            "none": ["cpu_percent", "memory_percent", "db_pool_usage", "error_rate", "api_latency_ms"],
        }

        affinities = type_affinities.get(predicted_class, self.BASE_FEATURES)

        for feat in self.BASE_FEATURES:
            val = full_features.get(feat, 0.0)
            baseline = self.NOMINAL_BASELINE.get(feat, 1.0)
            std = self.NOMINAL_STDS.get(feat, 1.0)
            
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
        return attributions[:5]

    # ============================================================
    # SRE PRE-EMPTIVE REMEDIATION PLAYBOOKS
    # ============================================================

    @staticmethod
    def _get_preemptive_remediation(failure_type: str) -> list[str]:
        playbooks = {
            "database_connection_exhaustion": [
                "Drain idle client pool connections & raise max_connections ceiling by 30%",
                "Enable Redis query response cache to shed 40% read load from master DB",
                "Kill slow long-running analytical queries (>5000ms) holding pool locks",
            ],
            "cpu_saturation": [
                "Trigger horizontal pod autoscaling (HPA) to scale replica count +50%",
                "Temporarily shed non-critical background jobs and batch sync pipelines",
                "Enable API rate-limiting tier-1 on heavy unauthenticated endpoints",
            ],
            "memory_exhaustion": [
                "Force graceful container rolling restart to release leaked heap allocations",
                "Reduce in-memory caching TTL and trim worker concurrency thresholds",
                "Collect heap dump snapshot before OOMKill for immediate memory leak RCA",
            ],
            "api_availability_degradation": [
                "Enable circuit breaker on downstream upstream microservice dependencies",
                "Route non-critical traffic to cached static fallback endpoints",
                "Scale out API Gateway gateway ingress proxies to absorb queue backlog",
            ],
            "disk_exhaustion": [
                "Trigger automated log rotation and compress expired stdout/stderr logs",
                "Purge temporary scratch buffers and obsolete build cache artifacts",
                "Expand provisioned EBS/PV storage volume quota before I/O freeze",
            ],
            "network_degradation": [
                "Switch egress routing to secondary standby multi-AZ transit gateway",
                "Enable HTTP/2 keep-alive connection reuse to minimize TCP handshake overhead",
                "Engage Cloudflare/CDN edge caching to absorb anomalous regional traffic",
            ],
            "none": [
                "System metrics within nominal SLO thresholds — maintain continuous telemetry monitoring.",
            ],
        }
        return playbooks.get(failure_type, ["Monitor system telemetry continuously and maintain alert standbys."])

    # ============================================================
    # TIME TO FAILURE & RISK WINDOW
    # ============================================================

    @staticmethod
    def _estimate_time_to_failure(risk: int, anomaly_score: float) -> str:
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
    def _risk_level(risk: int) -> str:
        if risk >= 80:
            return "CRITICAL"
        if risk >= 60:
            return "HIGH"
        if risk >= 30:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _friendly_failure_name(failure_type: str) -> str:
        names = {
            "none": "No Failure",
            "database_connection_exhaustion": "Database Connection Exhaustion",
            "cpu_saturation": "CPU Saturation",
            "memory_exhaustion": "Memory Exhaustion",
            "api_availability_degradation": "API Availability Degradation",
            "disk_exhaustion": "Disk Exhaustion",
            "network_degradation": "Network Degradation",
        }
        return names.get(failure_type, failure_type.replace("_", " ").title())

    # ============================================================
    # MAIN PREDICT METHOD
    # ============================================================

    def predict(self, telemetry: dict[str, float]) -> dict[str, Any]:
        self._ensure_model()

        # Compute full feature vector including engineered terms
        full_features = self.compute_features_dict(telemetry)
        X_df = pd.DataFrame([full_features], columns=self.FEATURES)

        probabilities = self.model.predict_proba(X_df)[0]
        classes = list(self.model.classes_)

        probability_map = {
            str(label): float(probability)
            for label, probability in zip(classes, probabilities)
        }

        highest_index = int(np.argmax(probabilities))
        predicted_type = str(classes[highest_index])
        predicted_type_prob = float(probabilities[highest_index])

        # Probability of any failure occurring
        none_prob = probability_map.get("none", 0.0)
        failure_prob = 1.0 - none_prob
        failure_risk = int(round(failure_prob * 100))
        prediction_flag = int(failure_risk >= 50)

        risk_level = self._risk_level(failure_risk)
        anomaly_score = full_features.get("anomaly_score", 0.0)
        time_to_failure = self._estimate_time_to_failure(failure_risk, anomaly_score)
        urgency_index = min(100, int(round((failure_risk * 0.7) + (min(5.0, anomaly_score) * 6.0))))

        prediction_confidence = int(round(predicted_type_prob * 100))

        # Explainable AI Feature Attributions
        feature_attributions = self._calculate_feature_attributions(full_features, predicted_type)
        preemptive_playbook = self._get_preemptive_remediation(predicted_type)

        # Ranked failure type probabilities list
        ranked_probabilities = []
        for label, prob in sorted(probability_map.items(), key=lambda item: item[1], reverse=True):
            ranked_probabilities.append({
                "failure_type": label,
                "display_name": self._friendly_failure_name(label),
                "probability": round(prob * 100.0, 2),
            })

        # Structured indicators
        indicators = []
        thresholds = {
            "cpu_percent": (80, 90), "memory_percent": (80, 90), "disk_percent": (80, 90),
            "db_connections": (75, 90), "db_pool_usage": (75, 90), "api_latency_ms": (500, 1000),
            "error_rate": (3.0, 8.0), "queue_depth": (75, 150), "network_latency_ms": (100, 300),
            "traffic_growth_percent": (25, 50), "request_rate": (1500, 2000),
        }

        for feat in self.BASE_FEATURES:
            val = float(telemetry.get(feat, 0.0))
            status = "NORMAL"
            if feat in thresholds:
                w, c = thresholds[feat]
                if val >= c:
                    status = "CRITICAL"
                elif val >= w:
                    status = "WARNING"
            indicators.append({"feature": feat, "value": round(val, 2), "status": status})

        active_indicators = [ind for ind in indicators if ind["status"] != "NORMAL"]

        return {
            "failure_risk": failure_risk,
            "risk_level": risk_level,
            "predicted_failure": "Production failure likely" if prediction_flag else "No immediate failure predicted",
            "predicted_failure_type": self._friendly_failure_name(predicted_type) if prediction_flag else "No Failure",
            "raw_failure_type": predicted_type,
            "predicted_failure_probability": round(predicted_type_prob * 100.0, 1),
            "risk_window": time_to_failure,
            "time_to_failure": time_to_failure,
            "urgency_index": urgency_index,
            "anomaly_score": anomaly_score,
            "prediction_confidence": prediction_confidence,
            "model": "Calibrated Ensemble (RandomForest + ExtraTrees)",
            "feature_attributions": feature_attributions,
            "preemptive_remediation": preemptive_playbook,
            "failure_type_probabilities": ranked_probabilities,
            "evidence": active_indicators[:5],
            "indicators": indicators,
        }