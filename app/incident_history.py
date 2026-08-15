import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class IncidentHistory:

    def __init__(
        self,
        file_path="data/incident_history.json",
    ):

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


    # ========================================================
    # INTERNAL LOAD
    # ========================================================

    def _load(self):

        try:

            content = self.file_path.read_text(
                encoding="utf-8"
            )

            data = json.loads(content)

            if isinstance(data, list):

                return data

            return []

        except (
            json.JSONDecodeError,
            FileNotFoundError,
            TypeError,
        ):

            return []


    # ========================================================
    # INTERNAL SAVE
    # ========================================================

    def _save(
        self,
        incidents,
    ):

        self.file_path.write_text(
            json.dumps(
                incidents,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


    # ========================================================
    # CREATE INCIDENT
    # ========================================================

    def create_incident(
        self,
        incident,
        analysis,
        historical_memories,
        telemetry=None,
        prediction=None,
    ):

        incidents = self._load()

        record = {

            # ------------------------------------------------
            # BASIC INCIDENT INFORMATION
            # ------------------------------------------------

            "incident_id": str(uuid4()),

            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "incident": incident,

            # ------------------------------------------------
            # AI ANALYSIS
            # ------------------------------------------------

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

            # ------------------------------------------------
            # HISTORICAL INFORMATION
            # ------------------------------------------------

            "historical_memory_count": len(
                historical_memories
            ),

            "historical_memories": (
                historical_memories
                if historical_memories
                else []
            ),

            # ------------------------------------------------
            # TELEMETRY
            # ------------------------------------------------

            "telemetry": (
                telemetry
                if telemetry
                else {}
            ),

            # ------------------------------------------------
            # ML PREDICTION
            # ------------------------------------------------

            "prediction": (
                prediction
                if prediction
                else {}
            ),

            # ------------------------------------------------
            # COMPLETE AI ANALYSIS
            # ------------------------------------------------

            "analysis": analysis,

            # ------------------------------------------------
            # OLD FEEDBACK FIELDS
            #
            # Kept for backward compatibility.
            # ------------------------------------------------

            "feedback": None,

            "resolution": None,

            "resolved_at": None,

            "learned": False,

            # ------------------------------------------------
            # NEW ENGINEER REVIEW
            # ------------------------------------------------

            "engineer_review": {

                "diagnosis_correct": None,

                "actual_failure_type": None,

                "confirmed_root_cause": None,

                "actual_resolution": None,

                "resolution_successful": None,

                "time_to_resolution_minutes": None,

                "engineer_notes": None,

                "reviewed_at": None,
            },

            # ------------------------------------------------
            # LEARNING INFORMATION
            # ------------------------------------------------

            "learning": {

                "learned": False,

                "learning_source": None,

                "knowledge_confidence": 0,

                "successful_resolution": False,
            },
        }

        incidents.append(
            record
        )

        self._save(
            incidents
        )

        return record


    # ========================================================
    # OLD FEEDBACK METHOD
    #
    # Kept compatible with existing agent.py.
    # ========================================================

    def add_feedback(
        self,
        incident_id,
        helpful,
        resolution,
    ):

        incidents = self._load()

        for record in incidents:

            if (
                record["incident_id"]
                == incident_id
            ):

                # --------------------------------------------
                # OLD FEEDBACK
                # --------------------------------------------

                record["feedback"] = (
                    "helpful"
                    if helpful
                    else "not_helpful"
                )

                record["resolution"] = resolution

                record["resolved_at"] = (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )

                # --------------------------------------------
                # NEW ENGINEER REVIEW
                #
                # Preserve compatibility while adding
                # structured information.
                # --------------------------------------------

                review = record.setdefault(
                    "engineer_review",
                    {},
                )

                review["actual_resolution"] = (
                    resolution
                )

                review["resolution_successful"] = (
                    bool(helpful)
                )

                review["reviewed_at"] = (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )

                # --------------------------------------------
                # LEARNING
                # --------------------------------------------

                learning = record.setdefault(
                    "learning",
                    {},
                )

                learning["successful_resolution"] = (
                    bool(helpful)
                )

                self._save(
                    incidents
                )

                return record

        raise ValueError(
            f"Incident {incident_id} was not found."
        )


    # ========================================================
    # NEW STRUCTURED ENGINEER REVIEW
    # ========================================================

    def add_engineer_review(
        self,
        incident_id,
        diagnosis_correct,
        actual_failure_type,
        confirmed_root_cause,
        actual_resolution,
        resolution_successful,
        time_to_resolution_minutes=None,
        engineer_notes="",
    ):

        incidents = self._load()

        for record in incidents:

            if (
                record["incident_id"]
                != incident_id
            ):

                continue

            # ------------------------------------------------
            # NORMALIZE VALUES
            # ------------------------------------------------

            if isinstance(
                diagnosis_correct,
                str,
            ):

                diagnosis_correct = (
                    diagnosis_correct.strip()
                    .lower()
                )

            if isinstance(
                resolution_successful,
                str,
            ):

                resolution_successful = (
                    resolution_successful.strip()
                    .lower()
                )

            # ------------------------------------------------
            # ENGINEER REVIEW
            # ------------------------------------------------

            review = {

                "diagnosis_correct": (
                    diagnosis_correct
                ),

                "actual_failure_type": (
                    actual_failure_type
                ),

                "confirmed_root_cause": (
                    confirmed_root_cause
                ),

                "actual_resolution": (
                    actual_resolution
                ),

                "resolution_successful": (
                    resolution_successful
                ),

                "time_to_resolution_minutes": (
                    time_to_resolution_minutes
                ),

                "engineer_notes": (
                    engineer_notes
                ),

                "reviewed_at": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
            }

            record["engineer_review"] = review

            # ------------------------------------------------
            # UPDATE OLD FIELDS TOO
            #
            # This keeps your existing dashboard/history
            # compatible.
            # ------------------------------------------------

            record["resolution"] = (
                actual_resolution
            )

            record["resolved_at"] = (
                review["reviewed_at"]
            )

            # ------------------------------------------------
            # CONVERT REVIEW TO OLD FEEDBACK FORMAT
            # ------------------------------------------------

            if (
                resolution_successful
                in [True, "yes", "successful"]
            ):

                record["feedback"] = (
                    "helpful"
                )

            elif (
                resolution_successful
                in [False, "no", "failed"]
            ):

                record["feedback"] = (
                    "not_helpful"
                )

            else:

                record["feedback"] = (
                    "partially_helpful"
                )

            # ------------------------------------------------
            # LEARNING STATUS
            #
            # We only consider a confirmed successful
            # resolution as strong learning material.
            # ------------------------------------------------

            learning = record.setdefault(
                "learning",
                {},
            )

            learning["successful_resolution"] = (
                resolution_successful
                in [
                    True,
                    "yes",
                    "successful",
                ]
            )

            learning["learning_source"] = (
                "engineer_confirmed"
            )

            # ------------------------------------------------
            # KNOWLEDGE CONFIDENCE
            # ------------------------------------------------

            if (
                diagnosis_correct
                in [
                    True,
                    "yes",
                ]
            ):

                knowledge_confidence = 100

            elif (
                diagnosis_correct
                in [
                    "partially",
                    "partial",
                ]
            ):

                knowledge_confidence = 70

            else:

                knowledge_confidence = 50

            # Successful engineer-confirmed fixes
            # receive a higher knowledge confidence.

            if learning[
                "successful_resolution"
            ]:

                knowledge_confidence = min(
                    100,
                    knowledge_confidence + 10,
                )

            learning[
                "knowledge_confidence"
            ] = knowledge_confidence

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            self._save(
                incidents
            )

            return record

        raise ValueError(
            f"Incident {incident_id} was not found."
        )


    # ========================================================
    # MARK INCIDENT AS LEARNED
    # ========================================================

    def mark_learned(
        self,
        incident_id,
    ):

        incidents = self._load()

        for record in incidents:

            if (
                record["incident_id"]
                == incident_id
            ):

                record["learned"] = True

                # --------------------------------------------
                # Update learning object
                # --------------------------------------------

                learning = record.setdefault(
                    "learning",
                    {},
                )

                learning["learned"] = True

                if not learning.get(
                    "learning_source"
                ):

                    learning[
                        "learning_source"
                    ] = "hindsight"

                self._save(
                    incidents
                )

                return record

        raise ValueError(
            f"Incident {incident_id} was not found."
        )


    # ========================================================
    # GET ALL INCIDENTS
    # ========================================================

    def get_all(self):

        return self._load()


    # ========================================================
    # GET INCIDENT BY ID
    # ========================================================

    def get_by_id(
        self,
        incident_id,
    ):

        incidents = self._load()

        for record in incidents:

            if (
                record["incident_id"]
                == incident_id
            ):

                return record

        return None


    # ========================================================
    # GET LEARNED INCIDENTS
    # ========================================================

    def get_learned_incidents(self):

        incidents = self._load()

        learned = []

        for record in incidents:

            if record.get(
                "learned",
                False,
            ):

                learned.append(
                    record
                )

        return learned


    # ========================================================
    # GET SUCCESSFUL RESOLUTIONS
    # ========================================================

    def get_successful_resolutions(self):

        incidents = self._load()

        successful = []

        for record in incidents:

            review = record.get(
                "engineer_review",
                {},
            )

            learning = record.get(
                "learning",
                {},
            )

            successful_resolution = (
                review.get(
                    "resolution_successful"
                )
                in [
                    True,
                    "yes",
                    "successful",
                ]
                or learning.get(
                    "successful_resolution",
                    False,
                )
            )

            if successful_resolution:

                successful.append(
                    record
                )

        return successful


    # ========================================================
    # FIND HISTORICAL INCIDENTS BY FAILURE TYPE
    # ========================================================

    def find_by_failure_type(
        self,
        failure_type,
    ):

        incidents = self._load()

        matches = []

        if not failure_type:

            return matches

        failure_type = (
            str(failure_type)
            .strip()
            .lower()
        )

        for record in incidents:

            review = record.get(
                "engineer_review",
                {},
            )

            actual_type = review.get(
                "actual_failure_type"
            )

            predicted_type = record.get(
                "failure_type"
            )

            category = record.get(
                "category"
            )

            candidates = [
                actual_type,
                predicted_type,
                category,
            ]

            for candidate in candidates:

                if not candidate:

                    continue

                if (
                    failure_type
                    in str(
                        candidate
                    ).lower()
                ):

                    matches.append(
                        record
                    )

                    break

        return matches


    # ========================================================
    # GET PREVIOUS SUCCESSFUL FIXES
    # ========================================================

    def get_successful_fixes(
        self,
        failure_type=None,
    ):

        if failure_type:

            incidents = (
                self.find_by_failure_type(
                    failure_type
                )
            )

        else:

            incidents = self._load()

        successful_fixes = []

        for record in incidents:

            review = record.get(
                "engineer_review",
                {},
            )

            learning = record.get(
                "learning",
                {},
            )

            successful = (
                review.get(
                    "resolution_successful"
                )
                in [
                    True,
                    "yes",
                    "successful",
                ]
                or learning.get(
                    "successful_resolution",
                    False,
                )
            )

            if not successful:

                continue

            successful_fixes.append(
                {
                    "incident_id": record.get(
                        "incident_id"
                    ),

                    "service": record.get(
                        "service",
                        "Unknown",
                    ),

                    "failure_type": review.get(
                        "actual_failure_type",
                        record.get(
                            "category",
                            "Unknown",
                        ),
                    ),

                    "root_cause": review.get(
                        "confirmed_root_cause",
                        record.get(
                            "root_cause",
                            "",
                        ),
                    ),

                    "resolution": review.get(
                        "actual_resolution",
                        record.get(
                            "resolution",
                            "",
                        ),
                    ),

                    "time_to_resolution_minutes": (
                        review.get(
                            "time_to_resolution_minutes"
                        )
                    ),

                    "engineer_notes": review.get(
                        "engineer_notes",
                        "",
                    ),

                    "knowledge_confidence": (
                        learning.get(
                            "knowledge_confidence",
                            0,
                        )
                    ),

                    "created_at": record.get(
                        "created_at"
                    ),

                    "resolved_at": record.get(
                        "resolved_at"
                    ),
                }
            )

        # Highest-confidence successful fixes first.

        successful_fixes.sort(
            key=lambda x: x.get(
                "knowledge_confidence",
                0,
            ),
            reverse=True,
        )

        return successful_fixes