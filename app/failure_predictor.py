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

from app.feature_engineering import (
    BASE_FEATURES,
    ENGINEERED_FEATURES,
    FEATURES,
    NOMINAL_BASELINE,
    NOMINAL_STDS,
    compute_engineered_features,
    compute_features_dict,
)
from app.playbooks import PlaybookRegistry
from app.ttf_predictor import TTFPredictor
from app.xai import FeatureAttributor


class FailurePredictor:
    """
    Calibrated Ensemble Failure Prediction & Explainable AI Engine.
    
    Combines:
    - Base Telemetry features + Domain-Specific Compound Stress Indices (19 total)
    - Calibrated Multi-Class Probability Distribution (Random Forest + Extra Trees)
    - Local Feature Attribution (Explainable AI / SHAP-style importance)
    - Time-To-Failure (TTF) & Multivariate Anomaly Dynamics
    - Pre-emptive SRE Remediation Playbooks
    """

    MODEL_VERSION = "2.6.0-enterprise"
    BASE_FEATURES = BASE_FEATURES
    ENGINEERED_FEATURES = ENGINEERED_FEATURES
    FEATURES = FEATURES

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

    NOMINAL_BASELINE = NOMINAL_BASELINE
    NOMINAL_STDS = NOMINAL_STDS

    def __init__(self, model_path: str | None = None) -> None:
        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = self.MODEL_PATH

        self.model = None
        self.metrics: dict[str, Any] = {}
        self.training_columns = self.FEATURES.copy()

    # ============================================================
    # FEATURE EXTRACTION (delegated to canonical feature_engineering)
    # ============================================================

    @classmethod
    def compute_features_dict(cls, telemetry: dict[str, float]) -> dict[str, float]:
        """
        Derive interaction terms and anomaly indicators from raw telemetry metrics.
        """
        return compute_features_dict(telemetry)

    def _clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure all feature columns exist and are sanitized.
        """
        missing_engineered = [f for f in self.ENGINEERED_FEATURES if f not in df.columns]
        if missing_engineered:
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

        # Base estimators for robust high-capacity ensemble (~400 RF trees)
        rf = RandomForestClassifier(
            n_estimators=400,
            max_depth=16,
            min_samples_split=4,
            min_samples_leaf=1,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )

        et = ExtraTreesClassifier(
            n_estimators=250,
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

        print("Training calibrated ensemble failure predictor (Random Forest ~400 + Extra Trees ~250)...")
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
            "model_version": self.MODEL_VERSION,
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
    # DELEGATED METHODS (backward compatibility & modules)
    # ============================================================

    def _calculate_feature_attributions(
        self,
        full_features: dict[str, float],
        predicted_class: str,
    ) -> list[dict[str, Any]]:
        return FeatureAttributor.explain(full_features, predicted_class, top_k=5)

    @staticmethod
    def _get_preemptive_remediation(failure_type: str) -> list[str]:
        return PlaybookRegistry.get_playbook(failure_type)

    @staticmethod
    def _estimate_time_to_failure(risk: int, anomaly_score: float) -> str:
        return TTFPredictor.estimate_time_to_failure(risk, anomaly_score)

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
        time_to_failure = TTFPredictor.estimate_time_to_failure(failure_risk, anomaly_score)
        urgency_index = TTFPredictor.calculate_urgency_index(failure_risk, anomaly_score)

        prediction_confidence = int(round(predicted_type_prob * 100))

        # Explainable AI Feature Attributions
        feature_attributions = FeatureAttributor.explain(full_features, predicted_type, top_k=5)
        preemptive_playbook = PlaybookRegistry.get_playbook(predicted_type)

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
            "model_version": self.MODEL_VERSION,
            "feature_attributions": feature_attributions,
            "preemptive_remediation": preemptive_playbook,
            "failure_type_probabilities": ranked_probabilities,
            "evidence": active_indicators[:5],
            "indicators": indicators,
        }
