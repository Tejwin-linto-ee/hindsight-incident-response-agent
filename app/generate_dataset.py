import os
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42

NUMBER_OF_SAMPLES = 12000

OUTPUT_PATH = Path(
    "data/telemetry_dataset.csv"
)


# ============================================================
# RANDOM GENERATOR
# ============================================================

rng = np.random.default_rng(
    RANDOM_SEED
)


# ============================================================
# DATASET GENERATOR
# ============================================================

def generate_dataset(
    number_of_samples: int = NUMBER_OF_SAMPLES,
) -> pd.DataFrame:

    rows = []

    for _ in range(
        number_of_samples
    ):

        # ----------------------------------------------------
        # Base healthy system
        # ----------------------------------------------------

        cpu = rng.normal(
            45,
            15,
        )

        memory = rng.normal(
            50,
            12,
        )

        disk = rng.normal(
            55,
            15,
        )

        db_connections = rng.normal(
            45,
            15,
        )

        db_pool_usage = rng.normal(
            45,
            15,
        )

        api_latency = rng.normal(
            150,
            50,
        )

        error_rate = rng.normal(
            1.5,
            0.8,
        )

        request_rate = rng.normal(
            1000,
            250,
        )

        queue_depth = rng.normal(
            30,
            15,
        )

        network_latency = rng.normal(
            40,
            15,
        )

        traffic_growth = rng.normal(
            5,
            10,
        )

        # ----------------------------------------------------
        # Select system condition
        # ----------------------------------------------------

        condition = rng.choice(
            [
                "healthy",
                "database",
                "cpu",
                "memory",
                "api",
                "disk",
                "network",
            ],
            p=[
                0.50,
                0.12,
                0.10,
                0.08,
                0.08,
                0.06,
                0.06,
            ],
        )

        # ----------------------------------------------------
        # Healthy operation
        # ----------------------------------------------------

        failure_type = "none"

        # ----------------------------------------------------
        # Database failure pattern
        # ----------------------------------------------------

        if condition == "database":

            db_connections = rng.normal(
                92,
                5,
            )

            db_pool_usage = rng.normal(
                94,
                4,
            )

            api_latency = rng.normal(
                900,
                180,
            )

            error_rate = rng.normal(
                7,
                2,
            )

            queue_depth = rng.normal(
                120,
                30,
            )

            failure_type = (
                "database_connection_exhaustion"
            )

        # ----------------------------------------------------
        # CPU saturation pattern
        # ----------------------------------------------------

        elif condition == "cpu":

            cpu = rng.normal(
                94,
                4,
            )

            memory = rng.normal(
                70,
                10,
            )

            request_rate = rng.normal(
                1800,
                300,
            )

            queue_depth = rng.normal(
                150,
                40,
            )

            api_latency = rng.normal(
                650,
                150,
            )

            error_rate = rng.normal(
                5,
                2,
            )

            traffic_growth = rng.normal(
                35,
                10,
            )

            failure_type = (
                "cpu_saturation"
            )

        # ----------------------------------------------------
        # Memory exhaustion pattern
        # ----------------------------------------------------

        elif condition == "memory":

            cpu = rng.normal(
                75,
                10,
            )

            memory = rng.normal(
                94,
                3,
            )

            api_latency = rng.normal(
                600,
                150,
            )

            error_rate = rng.normal(
                5,
                2,
            )

            queue_depth = rng.normal(
                100,
                30,
            )

            failure_type = (
                "memory_exhaustion"
            )

        # ----------------------------------------------------
        # API degradation pattern
        # ----------------------------------------------------

        elif condition == "api":

            api_latency = rng.normal(
                1200,
                250,
            )

            error_rate = rng.normal(
                10,
                3,
            )

            queue_depth = rng.normal(
                180,
                50,
            )

            request_rate = rng.normal(
                1700,
                300,
            )

            traffic_growth = rng.normal(
                40,
                12,
            )

            failure_type = (
                "api_availability_degradation"
            )

        # ----------------------------------------------------
        # Disk exhaustion pattern
        # ----------------------------------------------------

        elif condition == "disk":

            disk = rng.normal(
                96,
                2,
            )

            error_rate = rng.normal(
                4,
                1.5,
            )

            api_latency = rng.normal(
                500,
                120,
            )

            failure_type = (
                "disk_exhaustion"
            )

        # ----------------------------------------------------
        # Network degradation pattern
        # ----------------------------------------------------

        elif condition == "network":

            network_latency = rng.normal(
                500,
                100,
            )

            api_latency = rng.normal(
                800,
                200,
            )

            error_rate = rng.normal(
                8,
                2,
            )

            queue_depth = rng.normal(
                130,
                35,
            )

            failure_type = (
                "network_degradation"
            )

        # ----------------------------------------------------
        # Clip realistic ranges
        # ----------------------------------------------------

        cpu = np.clip(
            cpu,
            0,
            100,
        )

        memory = np.clip(
            memory,
            0,
            100,
        )

        disk = np.clip(
            disk,
            0,
            100,
        )

        db_connections = np.clip(
            db_connections,
            0,
            100,
        )

        db_pool_usage = np.clip(
            db_pool_usage,
            0,
            100,
        )

        api_latency = max(
            10,
            api_latency,
        )

        error_rate = np.clip(
            error_rate,
            0,
            100,
        )

        request_rate = max(
            0,
            request_rate,
        )

        queue_depth = max(
            0,
            queue_depth,
        )

        network_latency = max(
            1,
            network_latency,
        )

        traffic_growth = np.clip(
            traffic_growth,
            -100,
            500,
        )

        # ----------------------------------------------------
        # Failure label
        # ----------------------------------------------------

        failure_in_next_window = (
            0
            if failure_type == "none"
            else 1
        )

        # ----------------------------------------------------
        # Add row
        # ----------------------------------------------------

        rows.append(
            {
                "cpu_percent": round(
                    cpu,
                    2,
                ),

                "memory_percent": round(
                    memory,
                    2,
                ),

                "disk_percent": round(
                    disk,
                    2,
                ),

                "db_connections": round(
                    db_connections,
                    2,
                ),

                "db_pool_usage": round(
                    db_pool_usage,
                    2,
                ),

                "api_latency_ms": round(
                    api_latency,
                    2,
                ),

                "error_rate": round(
                    error_rate,
                    2,
                ),

                "request_rate": round(
                    request_rate,
                    2,
                ),

                "queue_depth": round(
                    queue_depth,
                    2,
                ),

                "network_latency_ms": round(
                    network_latency,
                    2,
                ),

                "traffic_growth_percent": round(
                    traffic_growth,
                    2,
                ),

                "failure_type": failure_type,

                "failure_in_next_window":
                    failure_in_next_window,
            }
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print(
        "=" * 70
    )

    print(
        "GENERATING TELEMETRY DATASET"
    )

    print(
        "=" * 70
    )

    print()

    print(
        "Samples:",
        NUMBER_OF_SAMPLES,
    )

    print(
        "Random seed:",
        RANDOM_SEED,
    )

    print()

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    df = generate_dataset()

    # --------------------------------------------------------
    # Create directory
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    total = len(df)

    failures = int(
        df[
            "failure_in_next_window"
        ].sum()
    )

    healthy = (
        total
        - failures
    )

    print(
        "Dataset created successfully."
    )

    print()

    print(
        "File:",
        OUTPUT_PATH,
    )

    print(
        "Total samples:",
        total,
    )

    print(
        "Healthy samples:",
        healthy,
    )

    print(
        "Failure samples:",
        failures,
    )

    print()

    print(
        "Failure rate:",
        round(
            failures / total * 100,
            2,
        ),
        "%",
    )

    print()

    print(
        "Failure types:"
    )

    print(
        df[
            "failure_type"
        ].value_counts()
    )

    print()

    print(
        "First five rows:"
    )

    print(
        df.head()
    )

    print()

    print(
        "=" * 70
    )

    print(
        "DATASET GENERATION COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()