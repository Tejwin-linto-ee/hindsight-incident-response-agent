import sys
from typing import Any

from app.hindsight_memory import IncidentMemory
from app.incident_history import IncidentHistory
from app.llm import IncidentLLM
from app.memory_engine import MemoryEngine


def _safe_print(text: str) -> None:
    """Safely print text on Windows CP1252 terminal without crashing on emojis."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


class IncidentResponseAgent:
    """
    Enterprise Incident Response Agent orchestrating:
    - Real-time telemetry & ML failure forecasting
    - Multi-angle Hindsight vector recall & semantic re-ranking
    - Deep SRE reasoning via Kimi K2 (Moonshot AI) on Groq
    - Continuous organizational learning loop from human technician reviews
    """

    def __init__(self):
        self.memory = IncidentMemory()
        self.llm = IncidentLLM()
        self.history = IncidentHistory()

    # =============================================================
    # INVESTIGATE INCIDENT
    # =============================================================

    def investigate(
        self,
        incident: str,
        telemetry: dict[str, float] | None = None,
        prediction: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        original_incident = incident
        incident = incident.strip()

        if not incident:
            raise ValueError("Incident description cannot be empty.")

        _safe_print("\n[*] Investigating incident...")
        _safe_print("=" * 60)
        _safe_print(incident)

        # ---------------------------------------------------------
        # STEP 1: Evaluate Failure Prediction from Telemetry
        # ---------------------------------------------------------
        if telemetry and prediction is None:
            try:
                from app.failure_predictor import FailurePredictor
                predictor = FailurePredictor()
                prediction = predictor.predict(telemetry)
                _safe_print(f"\n[+] Evaluated failure prediction: {prediction.get('predicted_failure_type', 'Unknown')} (Risk: {prediction.get('failure_risk', 0)}%)")
            except Exception as pred_err:
                _safe_print(f"\n[!] Could not evaluate failure prediction: {pred_err}")

        # ---------------------------------------------------------
        # STEP 2: Multi-Angle Semantic Memory Recall & Re-ranking
        # ---------------------------------------------------------
        try:
            raw_memories = self.memory.find_similar_incidents(
                incident,
                telemetry=telemetry,
                top_k=5,
            )
        except Exception as memory_err:
            _safe_print(f"\n[!] Hindsight memory recall warning: {memory_err}")
            raw_memories = []

        if raw_memories is None:
            raw_memories = []

        # Process and rank memories using MemoryEngine
        structured_memories = MemoryEngine.process_and_rank_memories(
            raw_memories,
            query=incident,
            limit=5,
        )

        # Extract plain text list for backward compatibility
        text_memories = [m["raw_text"] for m in structured_memories]

        _safe_print(f"\n[+] Retrieved & ranked {len(structured_memories)} historical memories from Hindsight.")
        for i, sm in enumerate(structured_memories, 1):
            _safe_print(f"   [{i}] Relevance: {sm['relevance_score']}% ({sm['tier']}) | Service: {sm['extracted_service']}")

        # ---------------------------------------------------------
        # STEP 3: AI Incident Triage & Root Cause Analysis
        # ---------------------------------------------------------
        _safe_print("\n[+] Analyzing incident with deep organizational context & ML telemetry...")
        analysis = self.llm.analyze(
            incident=incident,
            memories=structured_memories,
            prediction=prediction,
        )

        if not isinstance(analysis, dict):
            raise ValueError("The AI returned an invalid structured response.")

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
            "reasoning_summary",
            "confidence",
            "uncertainty",
        ]

        for field in required_fields:
            if field not in analysis:
                raise ValueError(f"AI response is missing required field: {field}")

        # ---------------------------------------------------------
        # STEP 4: Persist Investigation Locally
        # ---------------------------------------------------------
        record = self.history.create_incident(
            incident=original_incident,
            analysis=analysis,
            historical_memories=text_memories,
            telemetry=telemetry,
            prediction=prediction,
        )

        _safe_print("\n[+] Investigation saved locally.")
        _safe_print(f"Incident ID: {record['incident_id']}")

        # ---------------------------------------------------------
        # STEP 5: Terminal Output & Summary
        # ---------------------------------------------------------
        _safe_print("\n" + "=" * 60)
        _safe_print("INCIDENT RESPONSE ANALYSIS")
        _safe_print("=" * 60)
        _safe_print(f"\nSeverity: {analysis['severity']} | Service: {analysis['service']} | Category: {analysis['category']}")
        _safe_print(f"Root Cause: {analysis['root_cause']} (Confidence: {analysis['root_cause_confidence']}%)")
        _safe_print("\nImmediate Actions:")
        for i, action in enumerate(analysis["recommended_actions"], 1):
            _safe_print(f"  {i}. {action}")
        _safe_print("=" * 60 + "\n")

        from app.runbook_generator import RunbookGenerator
        runbook = RunbookGenerator.generate_runbook(analysis, telemetry=telemetry)

        return {
            "incident": original_incident,
            "incident_id": record["incident_id"],
            "created_at": record["created_at"],
            "historical_memories": text_memories,
            "structured_memories": structured_memories,
            "analysis": analysis,
            "telemetry": telemetry,
            "prediction": prediction,
            "runbook": runbook,
        }

    # =============================================================
    # RECORD ENGINEER / TECHNICIAN REVIEW & CONTINUOUS LEARNING
    # =============================================================

    def record_resolution(
        self,
        incident_id: str,
        helpful: bool,
        resolution: str,
    ) -> dict[str, Any]:
        resolution = resolution.strip()
        if not resolution:
            raise ValueError("Resolution cannot be empty.")

        # Update local history record
        record = self.history.add_feedback(
            incident_id=incident_id,
            helpful=helpful,
            resolution=resolution,
        )

        # Build high-fidelity postmortem memory for Hindsight
        learning_memory = f"""
============================================================
VERIFIED PRODUCTION INCIDENT POSTMORTEM
============================================================
Incident ID: {incident_id}
Service: {record.get('service', 'Unknown')}
Severity: {record.get('severity', 'P3')}
Category: {record.get('category', 'Unknown')}

Original Incident Symptoms:
{record.get('incident', '')}

AI Diagnostic Hypothesis:
{record.get('root_cause', '')} (AI Confidence: {record.get('confidence', 0)}%)

Human Technician Feedback:
Diagnosis was {'CONFIRMED / HELPFUL' if helpful else 'REJECTED / UNHELPFUL'}

CONFIRMED HUMAN ENGINEER RESOLUTION & MITIGATION:
{resolution}

Organizational Lesson Learned:
This resolution represents verified institutional engineering experience.
Future similar incidents should prioritize this remediation strategy.
"""

        # Store in Hindsight knowledge bank
        try:
            self.memory.remember_incident(learning_memory)
            _safe_print("\n[+] Hindsight organizational memory successfully reinforced.")
        except Exception as e:
            _safe_print(f"\n[!] Could not push learning to Hindsight: {e}")

        # Mark learned in local storage
        self.history.mark_learned(incident_id)

        return {
            "incident_id": incident_id,
            "learned": True,
            "resolution": resolution,
        }

    def get_history(self):
        return self.history.get_all()

    def close(self):
        try:
            self.memory.close()
        except Exception as e:
            _safe_print(f"[MEMORY CLEANUP ERROR] {type(e).__name__}: {e}")