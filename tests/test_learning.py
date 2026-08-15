from app.incident_history import IncidentHistory


def test_incident_history_learning(tmp_path):

    history = IncidentHistory(
        file_path=tmp_path / "incidents.json"
    )

    analysis = {
        "severity": "P1",
        "service": "Payment API",
        "category": "Availability",
        "incident_summary": "Payment API unavailable",
        "root_cause": "Database connection exhaustion",
        "root_cause_confidence": 90,
        "historical_evidence": [],
        "recommended_actions": [
            "Reduce load"
        ],
        "short_term_actions": [
            "Investigate database connections"
        ],
        "long_term_prevention": [
            "Improve connection pool monitoring"
        ],
        "reasoning": "Historical evidence supports the diagnosis.",
        "confidence": 90,
        "uncertainty": "Exact trigger requires investigation.",
    }

    record = history.create_incident(
        incident="Payment API returned 503 errors.",
        analysis=analysis,
        historical_memories=[
            "Previous payment outage."
        ],
    )

    assert record["incident_id"]
    assert record["severity"] == "P1"
    assert record["learned"] is False

    updated = history.add_feedback(
        incident_id=record["incident_id"],
        helpful=True,
        resolution=(
            "Increased database connection pool "
            "and restarted the service."
        ),
    )

    assert updated["feedback"] == "helpful"

    assert updated["resolution"] is not None

    learned = history.mark_learned(
        record["incident_id"]
    )

    assert learned["learned"] is True