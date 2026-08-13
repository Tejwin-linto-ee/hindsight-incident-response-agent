from app.hindsight_memory import IncidentMemory
from app.llm import IncidentLLM
from app.incident_history import IncidentHistory


class IncidentResponseAgent:

    def __init__(self):

        self.memory = IncidentMemory()

        self.llm = IncidentLLM()

        self.history = IncidentHistory()

    def investigate(
        self,
        incident: str,
    ):

        # ---------------------------------------------------------
        # Preserve original input
        # ---------------------------------------------------------

        original_incident = incident

        incident = incident.strip()

        if not incident:

            raise ValueError(
                "Incident description cannot be empty."
            )

        print("\n🔎 Investigating incident...")
        print("=" * 60)
        print(incident)

        # ---------------------------------------------------------
        # STEP 1
        # Retrieve historical memory
        # ---------------------------------------------------------

        results = self.memory.find_similar_incidents(
            incident
        )

        if results is None:

            results = []

        print(
            "\n🧠 Retrieved historical incidents:"
        )

        print(
            f"Found {len(results)} relevant memories."
        )

        top_results = results[:5]

        memories = []

        for result in top_results:

            if (
                hasattr(result, "text")
                and result.text
            ):

                memories.append(
                    result.text
                )

        print(
            f"Using {len(memories)} historical memories "
            "for analysis."
        )

        # ---------------------------------------------------------
        # STEP 2
        # Groq analysis
        # ---------------------------------------------------------

        print(
            "\n🤖 Analyzing incident with "
            "historical context..."
        )

        analysis = self.llm.analyze(
            incident=incident,
            memories=memories,
        )

        # ---------------------------------------------------------
        # STEP 3
        # Validate AI response
        # ---------------------------------------------------------

        if not isinstance(
            analysis,
            dict,
        ):

            raise ValueError(
                "The AI returned an invalid "
                "structured response."
            )

        required_fields = [
            "severity",
            "service",
            "category",
            "incident_summary",
            "root_cause",
            "root_cause_confidence",
            "historical_evidence",
            "recommended_actions",
            "short_term_actions",
            "long_term_prevention",
            "reasoning",
            "confidence",
            "uncertainty",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in analysis
        ]

        if missing_fields:

            raise ValueError(
                "The AI response is missing "
                f"required fields: {missing_fields}"
            )

        # ---------------------------------------------------------
        # Validate severity
        # ---------------------------------------------------------

        if analysis["severity"] not in {
            "P1",
            "P2",
            "P3",
            "P4",
        }:

            raise ValueError(
                "AI returned an invalid severity level."
            )

        # ---------------------------------------------------------
        # Validate confidence
        # ---------------------------------------------------------

        if not isinstance(
            analysis["root_cause_confidence"],
            int,
        ):

            raise ValueError(
                "root_cause_confidence "
                "must be an integer."
            )

        if not 0 <= analysis[
            "root_cause_confidence"
        ] <= 100:

            raise ValueError(
                "root_cause_confidence "
                "must be between 0 and 100."
            )

        if not isinstance(
            analysis["confidence"],
            int,
        ):

            raise ValueError(
                "confidence must be an integer."
            )

        if not 0 <= analysis[
            "confidence"
        ] <= 100:

            raise ValueError(
                "confidence must be between 0 and 100."
            )

        # ---------------------------------------------------------
        # Validate lists
        # ---------------------------------------------------------

        list_fields = [
            "historical_evidence",
            "recommended_actions",
            "short_term_actions",
            "long_term_prevention",
        ]

        for field in list_fields:

            if not isinstance(
                analysis[field],
                list,
            ):

                raise ValueError(
                    f"{field} must be a list."
                )

        # ---------------------------------------------------------
        # STEP 4
        # Persist investigation locally
        # ---------------------------------------------------------

        record = self.history.create_incident(
            incident=original_incident,
            analysis=analysis,
            historical_memories=memories,
        )

        print(
            "\n💾 Investigation saved."
        )

        print(
            f"Incident ID: "
            f"{record['incident_id']}"
        )

        # ---------------------------------------------------------
        # STEP 5
        # Terminal output
        # ---------------------------------------------------------

        print("\n" + "=" * 60)

        print(
            "🚨 INCIDENT RESPONSE ANALYSIS"
        )

        print("=" * 60)

        print(
            f"\nSeverity: "
            f"{analysis['severity']}"
        )

        print(
            f"Service: "
            f"{analysis['service']}"
        )

        print(
            f"Category: "
            f"{analysis['category']}"
        )

        print(
            f"\nIncident Summary:\n"
            f"{analysis['incident_summary']}"
        )

        print(
            f"\nLikely Root Cause:\n"
            f"{analysis['root_cause']}"
        )

        print(
            f"\nRoot Cause Confidence: "
            f"{analysis['root_cause_confidence']}%"
        )

        print("\nImmediate Actions:")

        for i, action in enumerate(
            analysis["recommended_actions"],
            1,
        ):

            print(
                f"{i}. {action}"
            )

        print("\nShort-Term Actions:")

        for i, action in enumerate(
            analysis["short_term_actions"],
            1,
        ):

            print(
                f"{i}. {action}"
            )

        print("\nLong-Term Prevention:")

        for i, action in enumerate(
            analysis["long_term_prevention"],
            1,
        ):

            print(
                f"{i}. {action}"
            )

        print(
            f"\nAI Reasoning:\n"
            f"{analysis['reasoning']}"
        )

        print(
            f"\nConfidence: "
            f"{analysis['confidence']}%"
        )

        print(
            f"\nUncertainty:\n"
            f"{analysis['uncertainty']}"
        )

        print("\n" + "=" * 60)

        # ---------------------------------------------------------
        # Return result
        # ---------------------------------------------------------

        return {
            "incident": original_incident,

            "incident_id": record[
                "incident_id"
            ],

            "created_at": record[
                "created_at"
            ],

            "historical_memories": memories,

            "analysis": analysis,
        }

    # =============================================================
    # RECORD HUMAN FEEDBACK
    # =============================================================

    def record_resolution(
        self,
        incident_id: str,
        helpful: bool,
        resolution: str,
    ):

        resolution = resolution.strip()

        if not resolution:

            raise ValueError(
                "Resolution cannot be empty."
            )

        # ---------------------------------------------------------
        # Save locally
        # ---------------------------------------------------------

        record = self.history.add_feedback(
            incident_id=incident_id,
            helpful=helpful,
            resolution=resolution,
        )

        # ---------------------------------------------------------
        # Build organizational memory
        # ---------------------------------------------------------

        learning_memory = f"""
RESOLVED PRODUCTION INCIDENT

Incident ID:
{incident_id}

Original Incident:
{record["incident"]}

Service:
{record["service"]}

Severity:
{record["severity"]}

Category:
{record["category"]}

AI Suggested Root Cause:
{record["root_cause"]}

AI Confidence:
{record["confidence"]}%

Human Feedback:
{"Helpful" if helpful else "Not Helpful"}

ACTUAL RESOLUTION:
{resolution}

This incident was reviewed by a human engineer.
The resolution represents confirmed organizational
experience and should be considered as historical
evidence for future similar incidents.
"""

        # ---------------------------------------------------------
        # Store in Hindsight
        # ---------------------------------------------------------

        self.memory.remember_incident(
            learning_memory
        )

        # ---------------------------------------------------------
        # Mark learned
        # ---------------------------------------------------------

        self.history.mark_learned(
            incident_id
        )

        print(
            "\n🧠 Organizational memory updated."
        )

        return {
            "incident_id": incident_id,
            "learned": True,
        }

    # =============================================================
    # HISTORY
    # =============================================================

    def get_history(self):

        return self.history.get_all()

    # =============================================================
    # CLEANUP
    # =============================================================

    def close(self):

        try:

            self.memory.close()

        except Exception as e:

            print(
                f"[MEMORY CLEANUP ERROR] "
                f"{type(e).__name__}: {e}"
            )