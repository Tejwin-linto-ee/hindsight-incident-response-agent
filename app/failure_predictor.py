import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split


class FailurePredictor:

    FEATURES = [
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

    MODEL_PATH = Path(
        "data/failure_predictor.joblib"
    )

    METRICS_PATH = Path(
        "data/failure_predictor_metrics.json"
    )

    FAILURE_TYPES = [
        "none",
        "database_connection_exhaustion",
        "cpu_saturation",
        "memory_exhaustion",
        "api_availability_degradation",
        "disk_exhaustion",
        "network_degradation",
    ]

    def __init__(
        self,
        model_path: str | None = None,
    ) -> None:

        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = self.MODEL_PATH

        self.model = None
        self.metrics: dict[str, Any] = {}

        self.training_columns = self.FEATURES.copy()

    # ============================================================
    # DATA VALIDATION
    # ============================================================

    def _validate_dataframe(
        self,
        df: pd.DataFrame,
    ) -> None:

        required_columns = (
            self.FEATURES
            + [
                "failure_in_next_window",
                "failure_type",
            ]
        )

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                "Dataset is missing required columns: "
                + ", ".join(missing)
            )

        if df.empty:
            raise ValueError(
                "Dataset is empty."
            )

    # ============================================================
    # CLEAN FEATURES
    # ============================================================

    def _clean_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        X = df[
            self.FEATURES
        ].copy()

        X = X.replace(
            [
                np.inf,
                -np.inf,
            ],
            np.nan,
        )

        X = X.fillna(
            X.median(
                numeric_only=True
            )
        )

        return X

    # ============================================================
    # TRAIN MULTICLASS MODEL
    # ============================================================

    def train(
        self,
        df: pd.DataFrame,
        test_size: float = 0.20,
        random_state: int = 42,
    ) -> dict[str, Any]:

        self._validate_dataframe(df)

        X = self._clean_features(df)

        y = (
            df["failure_type"]
            .astype(str)
        )

        print()
        print(
            "Failure type distribution:"
        )
        print(
            y.value_counts()
        )
        print()

        # --------------------------------------------------------
        # Split
        # --------------------------------------------------------

        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=random_state,
                stratify=y,
            )
        )

        # --------------------------------------------------------
        # Random Forest
        # --------------------------------------------------------

        base_model = RandomForestClassifier(
            n_estimators=400,
            max_depth=14,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )

        # --------------------------------------------------------
        # Calibration
        # --------------------------------------------------------

        model = CalibratedClassifierCV(
            estimator=base_model,
            method="sigmoid",
            cv=3,
        )

        print(
            "Training calibrated multiclass Random Forest..."
        )

        model.fit(
            X_train,
            y_train,
        )

        # --------------------------------------------------------
        # Predictions
        # --------------------------------------------------------

        predictions = model.predict(
            X_test
        )

        probabilities = model.predict_proba(
            X_test
        )

        # --------------------------------------------------------
        # Metrics
        # --------------------------------------------------------

        accuracy = accuracy_score(
            y_test,
            predictions,
        )

        precision = precision_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        )

        recall = recall_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        )

        f1 = f1_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        )

        report = classification_report(
            y_test,
            predictions,
            zero_division=0,
        )

        # --------------------------------------------------------
        # Save
        # --------------------------------------------------------

        self.model = model

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            model,
            self.model_path,
        )

        # --------------------------------------------------------
        # Metrics
        # --------------------------------------------------------

        self.metrics = {
            "model":
                "Calibrated Multiclass Random Forest",

            "model_type":
                "multiclass_failure_classifier",

            "accuracy":
                float(accuracy),

            "precision":
                float(precision),

            "recall":
                float(recall),

            "f1":
                float(f1),

            "training_samples":
                int(len(X_train)),

            "testing_samples":
                int(len(X_test)),

            "failure_classes":
                list(
                    model.classes_
                ),

            "classification_report":
                report,
        }

        self.METRICS_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            self.METRICS_PATH,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.metrics,
                file,
                indent=2,
            )

        return self.metrics

    # ============================================================
    # LOAD MODEL
    # ============================================================

    def load(self) -> None:

        if not self.model_path.exists():

            raise FileNotFoundError(
                "Failure prediction model was not found:\n"
                + str(self.model_path)
                + "\n\nTrain the model first."
            )

        self.model = joblib.load(
            self.model_path
        )

    # ============================================================
    # ENSURE MODEL
    # ============================================================

    def _ensure_model(
        self,
    ) -> None:

        if self.model is None:
            self.load()

    # ============================================================
    # TELEMETRY ROW
    # ============================================================

    def _build_telemetry_row(
        self,
        telemetry: dict[str, float],
    ) -> pd.DataFrame:

        missing = [
            feature
            for feature in self.FEATURES
            if feature not in telemetry
        ]

        if missing:

            raise ValueError(
                "Telemetry is missing required features: "
                + ", ".join(missing)
            )

        values = {}

        for feature in self.FEATURES:

            try:

                values[feature] = float(
                    telemetry[feature]
                )

            except (
                TypeError,
                ValueError,
            ):

                raise ValueError(
                    "Telemetry value for "
                    + feature
                    + " must be numeric."
                )

        return pd.DataFrame(
            [values],
            columns=self.FEATURES,
        )

    # ============================================================
    # RISK LEVEL
    # ============================================================

    @staticmethod
    def _risk_level(
        risk: int,
    ) -> str:

        if risk >= 80:
            return "CRITICAL"

        if risk >= 60:
            return "HIGH"

        if risk >= 30:
            return "MEDIUM"

        return "LOW"

    # ============================================================
    # RISK WINDOW
    # ============================================================

    @staticmethod
    def _risk_window(
        risk: int,
    ) -> str:

        if risk >= 90:
            return "Less than 5 minutes"

        if risk >= 80:
            return "5-15 minutes"

        if risk >= 60:
            return "15-30 minutes"

        if risk >= 40:
            return "30-60 minutes"

        if risk >= 20:
            return "1-2 hours"

        return "No immediate failure window detected"

    # ============================================================
    # TELEMETRY INDICATOR
    # ============================================================

    @staticmethod
    def _indicator(
        feature: str,
        value: float,
    ) -> str:

        percentage_thresholds = {

            "cpu_percent": (
                80,
                90,
            ),

            "memory_percent": (
                80,
                90,
            ),

            "disk_percent": (
                80,
                90,
            ),

            "db_connections": (
                75,
                90,
            ),

            "db_pool_usage": (
                75,
                90,
            ),
        }

        if feature in percentage_thresholds:

            warning, critical = (
                percentage_thresholds[
                    feature
                ]
            )

            if value >= critical:
                return "CRITICAL"

            if value >= warning:
                return "WARNING"

            return "NORMAL"

        if feature == "api_latency_ms":

            if value >= 1000:
                return "CRITICAL"

            if value >= 500:
                return "WARNING"

            return "NORMAL"

        if feature == "error_rate":

            if value >= 8:
                return "CRITICAL"

            if value >= 3:
                return "WARNING"

            return "NORMAL"

        if feature == "queue_depth":

            if value >= 150:
                return "CRITICAL"

            if value >= 75:
                return "WARNING"

            return "NORMAL"

        if feature == "network_latency_ms":

            if value >= 300:
                return "CRITICAL"

            if value >= 100:
                return "WARNING"

            return "NORMAL"

        if feature == "traffic_growth_percent":

            if value >= 50:
                return "CRITICAL"

            if value >= 25:
                return "WARNING"

            return "NORMAL"

        if feature == "request_rate":

            if value >= 2000:
                return "CRITICAL"

            if value >= 1500:
                return "WARNING"

            return "NORMAL"

        return "NORMAL"

    # ============================================================
    # BUILD INDICATORS
    # ============================================================

    def _build_indicators(
        self,
        telemetry: dict[str, float],
    ) -> list[dict[str, Any]]:

        indicators = []

        for feature in self.FEATURES:

            value = float(
                telemetry[feature]
            )

            status = self._indicator(
                feature,
                value,
            )

            indicators.append(
                {
                    "feature": feature,
                    "value": round(
                        value,
                        2,
                    ),
                    "status": status,
                }
            )

        priority = {
            "CRITICAL": 0,
            "WARNING": 1,
            "NORMAL": 2,
        }

        indicators.sort(
            key=lambda item:
                priority[item["status"]]
        )

        return indicators

    # ============================================================
    # FEATURE IMPORTANCE
    # ============================================================

    def _get_feature_importance(
        self,
    ) -> dict[str, float]:

        if not hasattr(
            self.model,
            "calibrated_classifiers_",
        ):
            return {}

        classifiers = (
            self.model.calibrated_classifiers_
        )

        if not classifiers:
            return {}

        base = (
            classifiers[0].estimator
        )

        if not hasattr(
            base,
            "feature_importances_",
        ):
            return {}

        importance = (
            base.feature_importances_
        )

        result = {}

        for index, feature in enumerate(
            self.FEATURES
        ):

            result[feature] = round(
                float(
                    importance[index]
                ),
                4,
            )

        return result

    # ============================================================
    # FAILURE TYPE DISPLAY
    # ============================================================

    @staticmethod
    def _friendly_failure_name(
        failure_type: str,
    ) -> str:

        names = {

            "none":
                "No Failure",

            "database_connection_exhaustion":
                "Database Connection Exhaustion",

            "cpu_saturation":
                "CPU Saturation",

            "memory_exhaustion":
                "Memory Exhaustion",

            "api_availability_degradation":
                "API Availability Degradation",

            "disk_exhaustion":
                "Disk Exhaustion",

            "network_degradation":
                "Network Degradation",
        }

        return names.get(
            failure_type,
            failure_type.replace(
                "_",
                " ",
            ).title(),
        )

    # ============================================================
    # PREDICT
    # ============================================================

    def predict(
        self,
        telemetry: dict[str, float],
    ) -> dict[str, Any]:

        self._ensure_model()

        X = self._build_telemetry_row(
            telemetry
        )

        # --------------------------------------------------------
        # Multiclass probabilities
        # --------------------------------------------------------

        probabilities = (
            self.model.predict_proba(
                X
            )[0]
        )

        classes = list(
            self.model.classes_
        )

        probability_map = {
            str(label):
                float(probability)
            for label, probability
            in zip(
                classes,
                probabilities,
            )
        }

        # --------------------------------------------------------
        # Most likely class
        # --------------------------------------------------------

        highest_index = int(
            np.argmax(
                probabilities
            )
        )

        predicted_type = str(
            classes[highest_index]
        )

        predicted_type_probability = float(
            probabilities[
                highest_index
            ]
        )

        # --------------------------------------------------------
        # Failure probability
        #
        # Everything except "none"
        # --------------------------------------------------------

        failure_probability = 1.0 - (
            probability_map.get(
                "none",
                0.0,
            )
        )

        failure_risk = int(
            round(
                failure_probability
                * 100
            )
        )

        prediction = int(
            failure_risk >= 50
        )

        # --------------------------------------------------------
        # Risk
        # --------------------------------------------------------

        risk_level = self._risk_level(
            failure_risk
        )

        risk_window = self._risk_window(
            failure_risk
        )

        # --------------------------------------------------------
        # Confidence
        # --------------------------------------------------------

        prediction_confidence = int(
            round(
                predicted_type_probability
                * 100
            )
        )

        # --------------------------------------------------------
        # Indicators
        # --------------------------------------------------------

        indicators = (
            self._build_indicators(
                telemetry
            )
        )

        # --------------------------------------------------------
        # Feature importance
        # --------------------------------------------------------

        feature_importance = (
            self._get_feature_importance()
        )

        top_features = sorted(
            feature_importance.items(),
            key=lambda item:
                item[1],
            reverse=True,
        )[:5]

        # --------------------------------------------------------
        # Human-readable prediction
        # --------------------------------------------------------

        if prediction:

            predicted_failure = (
                "Production failure likely"
            )

            predicted_failure_type = (
                self._friendly_failure_name(
                    predicted_type
                )
            )

        else:

            predicted_failure = (
                "No immediate failure predicted"
            )

            predicted_failure_type = (
                "No Failure"
            )

        # --------------------------------------------------------
        # Evidence
        # --------------------------------------------------------

        active_indicators = [
            item
            for item in indicators
            if item["status"]
            != "NORMAL"
        ]

        evidence = [
            {
                "feature":
                    item["feature"],

                "value":
                    item["value"],

                "status":
                    item["status"],
            }

            for item
            in active_indicators[:5]
        ]

        # --------------------------------------------------------
        # Failure probabilities
        # --------------------------------------------------------

        failure_type_probabilities = []

        for label, probability in sorted(
            probability_map.items(),
            key=lambda item:
                item[1],
            reverse=True,
        ):

            failure_type_probabilities.append(
                {
                    "failure_type":
                        str(label),

                    "display_name":
                        self._friendly_failure_name(
                            str(label)
                        ),

                    "probability":
                        round(
                            probability * 100,
                            2,
                        ),
                }
            )

        # --------------------------------------------------------
        # Return
        # --------------------------------------------------------

        return {

            "failure_risk":
                failure_risk,

            "predicted_failure":
                predicted_failure,

            "predicted_failure_type":
                predicted_failure_type,

            "predicted_failure_type_raw":
                predicted_type,

            "predicted_failure_probability":
                round(
                    predicted_type_probability
                    * 100,
                    2,
                ),

            "failure_type_probabilities":
                failure_type_probabilities,

            "risk_window":
                risk_window,

            "prediction_confidence":
                prediction_confidence,

            "risk_level":
                risk_level,

            "model":
                "Calibrated Multiclass Random Forest",

            "evidence":
                evidence,

            "top_model_features":
                [
                    {
                        "feature":
                            feature,

                        "importance":
                            importance,
                    }

                    for feature, importance
                    in top_features
                ],

            "feature_importance":
                feature_importance,

            "telemetry_indicators":
                indicators,

            "prediction":
                prediction,
        }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("MULTICLASS FAILURE PREDICTION ENGINE")
    print("=" * 70)
    print()

    predictor = FailurePredictor()

    print(
        "Model path:",
        predictor.model_path,
    )

    test_telemetry = {

        "cpu_percent": 40,

        "memory_percent": 45,

        "disk_percent": 50,

        "db_connections": 96,

        "db_pool_usage": 98,

        "api_latency_ms": 1100,

        "error_rate": 9,

        "request_rate": 800,

        "queue_depth": 160,

        "network_latency_ms": 35,

        "traffic_growth_percent": 6,
    }

    result = predictor.predict(
        test_telemetry
    )

    print()

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    print()
    print("=" * 70)