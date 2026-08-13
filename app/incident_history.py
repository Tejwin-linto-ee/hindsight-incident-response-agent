import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class IncidentHistory:

    def __init__(self, file_path="data/incident_history.json"):

        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.file_path.exists():

            self.file_path.write_text(
                "[]",
                encoding="utf-8",
            )

    def _load(self):

        try:

            content = self.file_path.read_text(
                encoding="utf-8"
            )

            return json.loads(content)

        except (
            json.JSONDecodeError,
            FileNotFoundError,
        ):

            return []

    def _save(self, incidents):

        self.file_path.write_text(
            json.dumps(
                incidents,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def create_incident(
        self,
        incident,
        analysis,
        historical_memories,
    ):

        incidents = self._load()

        record = {
            "incident_id": str(uuid4()),
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "incident": incident,

            "severity": analysis.get(
                "severity",
                "UNKNOWN",
            ),

            "service": analysis.get(
                "service",
                "Unknown",
            ),

            "category": analysis.get(
                "category",
                "Unknown",
            ),

            "root_cause": analysis.get(
                "root_cause",
                "",
            ),

            "confidence": analysis.get(
                "confidence",
                0,
            ),

            "root_cause_confidence": analysis.get(
                "root_cause_confidence",
                0,
            ),

            "historical_memory_count": len(
                historical_memories
            ),

            "analysis": analysis,

            "feedback": None,

            "resolution": None,

            "resolved_at": None,

            "learned": False,
        }

        incidents.append(record)

        self._save(incidents)

        return record

    def add_feedback(
        self,
        incident_id,
        helpful,
        resolution,
    ):

        incidents = self._load()

        for record in incidents:

            if record["incident_id"] == incident_id:

                record["feedback"] = (
                    "helpful"
                    if helpful
                    else "not_helpful"
                )

                record["resolution"] = resolution

                record["resolved_at"] = datetime.now(
                    timezone.utc
                ).isoformat()

                self._save(incidents)

                return record

        raise ValueError(
            f"Incident {incident_id} was not found."
        )

    def mark_learned(
        self,
        incident_id,
    ):

        incidents = self._load()

        for record in incidents:

            if record["incident_id"] == incident_id:

                record["learned"] = True

                self._save(incidents)

                return record

        raise ValueError(
            f"Incident {incident_id} was not found."
        )

    def get_all(self):

        return self._load()

    def get_by_id(
        self,
        incident_id,
    ):

        incidents = self._load()

        for record in incidents:

            if record["incident_id"] == incident_id:

                return record

        return None