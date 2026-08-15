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