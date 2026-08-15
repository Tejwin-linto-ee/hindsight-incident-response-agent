import json
import sys
from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# ============================================================
# IMPORT
# ============================================================

from app.failure_predictor import (
    FailurePredictor,
)


# ============================================================
# PATHS
# ============================================================

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "telemetry_dataset.csv"
)

METRICS_PATH = (
    PROJECT_ROOT
    / "data"
    / "failure_predictor_metrics.json"
)


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print()
    print("=" * 70)
    print(
        "MULTICLASS FAILURE PREDICTION MODEL TRAINING"
    )
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            "Telemetry dataset was not found:\n"
            + str(DATASET_PATH)
            + "\n\n"
            "Run:\n"
            "python app\\generate_dataset.py"
        )

    print(
        "Loading dataset..."
    )

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        "Dataset shape:",
        df.shape,
    )

    print()

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required = [
        "failure_type",
        "failure_in_next_window",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(missing)
        )

    # --------------------------------------------------------
    # Distribution
    # --------------------------------------------------------

    print(
        "Failure type distribution:"
    )

    print(
        df[
            "failure_type"
        ].value_counts()
    )

    print()

    # --------------------------------------------------------
    # Predictor
    # --------------------------------------------------------

    predictor = FailurePredictor()

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    metrics = predictor.train(
        df,
        test_size=0.20,
        random_state=42,
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "MODEL PERFORMANCE"
    )
    print("=" * 70)
    print()

    print(
        "Accuracy :",
        round(
            metrics["accuracy"] * 100,
            2,
        ),
        "%",
    )

    print(
        "Precision:",
        round(
            metrics["precision"] * 100,
            2,
        ),
        "%",
    )

    print(
        "Recall   :",
        round(
            metrics["recall"] * 100,
            2,
        ),
        "%",
    )

    print(
        "F1 Score :",
        round(
            metrics["f1"] * 100,
            2,
        ),
        "%",
    )

    print()

    print(
        "Training samples:",
        metrics["training_samples"],
    )

    print(
        "Testing samples:",
        metrics["testing_samples"],
    )

    print()

    print(
        "Classes:"
    )

    for failure_class in metrics[
        "failure_classes"
    ]:

        print(
            "  •",
            failure_class,
        )

    print()

    print(
        "Classification report:"
    )

    print(
        metrics[
            "classification_report"
        ]
    )

    # --------------------------------------------------------
    # Save metrics
    # --------------------------------------------------------

    METRICS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2,
        )

    print(
        "Metrics saved to:",
        METRICS_PATH,
    )

    print()

    # --------------------------------------------------------
    # Verify model
    # --------------------------------------------------------

    if predictor.model_path.exists():

        print(
            "Model saved to:",
            predictor.model_path,
        )

    else:

        raise RuntimeError(
            "Model file was not created."
        )

    print()
    print("=" * 70)
    print(
        "MULTICLASS TRAINING COMPLETE"
    )
    print("=" * 70)
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()