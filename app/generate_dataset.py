import os
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42
NUMBER_OF_SAMPLES = 16000
OUTPUT_PATH = Path("data/telemetry_dataset.csv")

rng = np.random.default_rng(RANDOM_SEED)


from app.feature_engineering import compute_engineered_features


# ============================================================
# DATASET GENERATOR
# ============================================================

def generate_dataset(number_of_samples: int = NUMBER_OF_SAMPLES) -> pd.DataFrame:
    rows = []

    for _ in range(number_of_samples):
        # ----------------------------------------------------
        # Base healthy baseline with natural variability
        # ----------------------------------------------------
        cpu = rng.normal(45, 12)
        memory = rng.normal(50, 10)
        disk = rng.normal(55, 12)
        db_connections = rng.normal(45, 12)
        db_pool_usage = rng.normal(45, 12)
        api_latency = rng.normal(150, 40)
        error_rate = rng.normal(1.2, 0.6)
        request_rate = rng.normal(1000, 200)
        queue_depth = rng.normal(25, 10)
        network_latency = rng.normal(35, 10)
        traffic_growth = rng.normal(5, 8)

        # Select condition with balanced failure scenarios
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
                0.40,
                0.12,
                0.11,
                0.10,
                0.10,
                0.08,
                0.09,
            ],
        )

        failure_type = "none"

        # ----------------------------------------------------
        # 1. Database Connection Exhaustion Scenario
        # ----------------------------------------------------
        if condition == "database":
            failure_type = "database_connection_exhaustion"
            db_connections = rng.normal(95, 4)
            db_pool_usage = rng.normal(96, 3)
            api_latency = rng.normal(1200, 300)
            error_rate = rng.normal(9.5, 2.5)
            queue_depth = rng.normal(160, 35)
            if rng.random() > 0.4:
                cpu = rng.normal(65, 10)

        # ----------------------------------------------------
        # 2. CPU Saturation Scenario
        # ----------------------------------------------------
        elif condition == "cpu":
            failure_type = "cpu_saturation"
            cpu = rng.normal(96, 3)
            request_rate = rng.normal(1850, 200)
            queue_depth = rng.normal(140, 30)
            api_latency = rng.normal(680, 140)
            error_rate = rng.normal(5.5, 1.8)
            traffic_growth = rng.normal(40, 15)

        # ----------------------------------------------------
        # 3. Memory Exhaustion Scenario
        # ----------------------------------------------------
        elif condition == "memory":
            failure_type = "memory_exhaustion"
            memory = rng.normal(96, 3)
            cpu = rng.normal(78, 8)  # GC thrashing load
            api_latency = rng.normal(650, 150)
            error_rate = rng.normal(5.0, 1.5)
            queue_depth = rng.normal(115, 25)

        # ----------------------------------------------------
        # 4. API Availability Degradation Scenario
        # ----------------------------------------------------
        elif condition == "api":
            failure_type = "api_availability_degradation"
            api_latency = rng.normal(1350, 350)
            error_rate = rng.normal(14.0, 3.5)
            request_rate = rng.normal(1700, 250)
            queue_depth = rng.normal(185, 40)
            traffic_growth = rng.normal(35, 15)

        # ----------------------------------------------------
        # 5. Disk Exhaustion Scenario
        # ----------------------------------------------------
        elif condition == "disk":
            failure_type = "disk_exhaustion"
            disk = rng.normal(97, 2)
            api_latency = rng.normal(520, 120)
            error_rate = rng.normal(4.5, 1.5)
            queue_depth = rng.normal(55, 15)

        # ----------------------------------------------------
        # 6. Network Degradation Scenario
        # ----------------------------------------------------
        elif condition == "network":
            failure_type = "network_degradation"
            network_latency = rng.normal(520, 120)
            api_latency = rng.normal(850, 180)
            error_rate = rng.normal(8.5, 2.5)
            queue_depth = rng.normal(135, 30)

        # Clipping values to physically meaningful operational ranges
        row = {
            "cpu_percent": float(np.clip(cpu, 1.0, 100.0)),
            "memory_percent": float(np.clip(memory, 1.0, 100.0)),
            "disk_percent": float(np.clip(disk, 1.0, 100.0)),
            "db_connections": float(np.clip(db_connections, 1.0, 100.0)),
            "db_pool_usage": float(np.clip(db_pool_usage, 1.0, 100.0)),
            "api_latency_ms": float(np.clip(api_latency, 10.0, 4000.0)),
            "error_rate": float(np.clip(error_rate, 0.0, 100.0)),
            "request_rate": float(np.clip(request_rate, 50.0, 5000.0)),
            "queue_depth": float(np.clip(queue_depth, 0.0, 500.0)),
            "network_latency_ms": float(np.clip(network_latency, 1.0, 2000.0)),
            "traffic_growth_percent": float(np.clip(traffic_growth, -50.0, 200.0)),
            "failure_in_next_window": int(failure_type != "none"),
            "failure_type": failure_type,
        }

        rows.append(row)

    df = pd.DataFrame(rows)
    df = compute_engineered_features(df)
    return df


def main() -> None:
    print("\n" + "=" * 70)
    print("GENERATING ENTERPRISE HIGH-FIDELITY TELEMETRY DATASET")
    print("=" * 70)
    df = generate_dataset()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(df)} samples with {len(df.columns)} features.")
    print(f"Dataset saved to: {OUTPUT_PATH}")
    print("\nClass Distribution:\n", df["failure_type"].value_counts())
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()