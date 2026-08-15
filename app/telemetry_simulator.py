import random
import time
from dataclasses import dataclass, asdict


@dataclass
class Telemetry:

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    db_connections: float
    db_pool_usage: float
    api_latency_ms: float
    error_rate: float
    request_rate: float
    queue_depth: float
    network_latency_ms: float
    traffic_growth_percent: float

    def to_dict(self):
        return asdict(self)


class TelemetrySimulator:

    def __init__(self, seed=42):

        random.seed(seed)

        self.step = 0

        self.mode = "healthy"

    # ========================================================
    # MODES
    # ========================================================

    def set_mode(self, mode):

        valid_modes = {
            "healthy",
            "database",
            "cpu",
            "memory",
            "network",
            "api",
        }

        if mode not in valid_modes:

            raise ValueError(
                f"Unknown telemetry mode: {mode}"
            )

        self.mode = mode

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(self):

        self.step += 1

        # ----------------------------------------------------
        # HEALTHY BASELINE
        # ----------------------------------------------------

        cpu = random.uniform(
            30,
            55,
        )

        memory = random.uniform(
            35,
            60,
        )

        disk = random.uniform(
            40,
            65,
        )

        db_connections = random.uniform(
            20,
            45,
        )

        db_pool = random.uniform(
            20,
            50,
        )

        api_latency = random.uniform(
            80,
            180,
        )

        error_rate = random.uniform(
            0.1,
            1.0,
        )

        request_rate = random.uniform(
            500,
            1000,
        )

        queue_depth = random.uniform(
            5,
            30,
        )

        network_latency = random.uniform(
            20,
            60,
        )

        traffic_growth = random.uniform(
            0,
            10,
        )

        # ====================================================
        # FAILURE SCENARIOS
        # ====================================================

        if self.mode == "database":

            progress = min(
                self.step / 20,
                1,
            )

            db_connections = (
                45
                + 50 * progress
                + random.uniform(-2, 2)
            )

            db_pool = (
                50
                + 47 * progress
                + random.uniform(-2, 2)
            )

            api_latency = (
                180
                + 950 * progress
                + random.uniform(-30, 30)
            )

            error_rate = (
                1
                + 8 * progress
                + random.uniform(
                    -0.5,
                    0.5,
                )
            )

            queue_depth = (
                30
                + 130 * progress
                + random.uniform(
                    -5,
                    5,
                )
            )

        elif self.mode == "cpu":

            progress = min(
                self.step / 20,
                1,
            )

            cpu = (
                50
                + 45 * progress
                + random.uniform(
                    -2,
                    2,
                )
            )

            api_latency = (
                150
                + 700 * progress
                + random.uniform(
                    -20,
                    20,
                )
            )

            error_rate = (
                1
                + 7 * progress
                + random.uniform(
                    -0.5,
                    0.5,
                )
            )

            queue_depth = (
                20
                + 120 * progress
                + random.uniform(
                    -5,
                    5,
                )
            )

        elif self.mode == "memory":

            progress = min(
                self.step / 20,
                1,
            )

            memory = (
                55
                + 40 * progress
                + random.uniform(
                    -2,
                    2,
                )
            )

            api_latency = (
                150
                + 700 * progress
                + random.uniform(
                    -20,
                    20,
                )
            )

            error_rate = (
                1
                + 7 * progress
                + random.uniform(
                    -0.5,
                    0.5,
                )
            )

            queue_depth = (
                20
                + 100 * progress
                + random.uniform(
                    -5,
                    5,
                )
            )

        elif self.mode == "network":

            progress = min(
                self.step / 20,
                1,
            )

            network_latency = (
                60
                + 340 * progress
                + random.uniform(
                    -10,
                    10,
                )
            )

            api_latency = (
                150
                + 650 * progress
                + random.uniform(
                    -20,
                    20,
                )
            )

            error_rate = (
                1
                + 7 * progress
                + random.uniform(
                    -0.5,
                    0.5,
                )
            )

            queue_depth = (
                20
                + 110 * progress
                + random.uniform(
                    -5,
                    5,
                )
            )

        elif self.mode == "api":

            progress = min(
                self.step / 20,
                1,
            )

            api_latency = (
                200
                + 1000 * progress
                + random.uniform(
                    -30,
                    30,
                )
            )

            error_rate = (
                1
                + 8 * progress
                + random.uniform(
                    -0.5,
                    0.5,
                )
            )

            queue_depth = (
                25
                + 130 * progress
                + random.uniform(
                    -5,
                    5,
                )
            )

            traffic_growth = (
                10
                + 60 * progress
                + random.uniform(
                    -2,
                    2,
                )
            )

        # ====================================================
        # CLAMP VALUES
        # ====================================================

        cpu = max(
            0,
            min(
                cpu,
                100,
            ),
        )

        memory = max(
            0,
            min(
                memory,
                100,
            ),
        )

        disk = max(
            0,
            min(
                disk,
                100,
            ),
        )

        db_connections = max(
            0,
            min(
                db_connections,
                100,
            ),
        )

        db_pool = max(
            0,
            min(
                db_pool,
                100,
            ),
        )

        error_rate = max(
            0,
            error_rate,
        )

        # ====================================================
        # RETURN TELEMETRY
        # ====================================================

        return Telemetry(

            cpu_percent=round(
                cpu,
                2,
            ),

            memory_percent=round(
                memory,
                2,
            ),

            disk_percent=round(
                disk,
                2,
            ),

            db_connections=round(
                db_connections,
                2,
            ),

            db_pool_usage=round(
                db_pool,
                2,
            ),

            api_latency_ms=round(
                api_latency,
                2,
            ),

            error_rate=round(
                error_rate,
                2,
            ),

            request_rate=round(
                request_rate,
                2,
            ),

            queue_depth=round(
                queue_depth,
                2,
            ),

            network_latency_ms=round(
                network_latency,
                2,
            ),

            traffic_growth_percent=round(
                traffic_growth,
                2,
            ),
        )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    simulator = TelemetrySimulator()

    simulator.set_mode(
        "database"
    )

    print()
    print("=" * 70)
    print("TELEMETRY SIMULATOR")
    print("=" * 70)

    for _ in range(20):

        telemetry = (
            simulator.generate()
        )

        print()
        print(
            telemetry.to_dict()
        )

        time.sleep(0.5)