from app.telemetry_simulator import TelemetrySimulator


class TelemetryManager:

    def __init__(self):

        self.simulator = TelemetrySimulator()

        self.active = False

        self.mode = "healthy"

        self.latest = None

    # ========================================================
    # START
    # ========================================================

    def start(
        self,
        mode: str,
    ):

        self.mode = mode

        self.simulator.set_mode(
            mode
        )

        self.simulator.step = 0

        self.active = True

        self.latest = (
            self.simulator.generate()
        )

        return self.latest.to_dict()

    # ========================================================
    # NEXT SAMPLE
    # ========================================================

    def next_sample(self):

        if not self.active:

            return None

        self.latest = (
            self.simulator.generate()
        )

        return self.latest.to_dict()

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        self.active = False

        self.latest = None

    # ========================================================
    # CURRENT
    # ========================================================

    def current(self):

        if self.latest is None:

            return None

        return self.latest.to_dict()

    def get_current_metrics(self):
        """Returns the latest telemetry dictionary or a standard baseline dictionary."""
        if self.latest is not None:
            try:
                return self.latest.to_dict()
            except Exception:
                return dict(self.latest)
        
        # Fallback healthy baseline
        return {
            "cpu_percent": 45.0,
            "memory_percent": 50.0,
            "disk_percent": 55.0,
            "db_connections": 45.0,
            "db_pool_usage": 45.0,
            "api_latency_ms": 150.0,
            "error_rate": 1.2,
            "request_rate": 1000.0,
            "queue_depth": 25.0,
            "network_latency_ms": 35.0,
            "traffic_growth_percent": 5.0,
        }