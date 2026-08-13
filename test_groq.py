from app.llm import IncidentLLM


def test_groq_analysis():

    incident = """
    The Payment API is returning HTTP 503 errors.
    Payment requests are failing.
    Database connection pool utilization has reached 100%.
    """

    memories = [
        """
        Payment API previously returned HTTP 503 errors because the
        database connection pool was exhausted. Increasing the
        connection pool from 50 to 100 successfully resolved the incident.
        """
    ]

    llm = IncidentLLM()

    answer = llm.analyze(
        incident,
        memories,
    )

    # ---------------------------------------------------------
    # Basic response validation
    # ---------------------------------------------------------

    assert isinstance(answer, dict)

    assert len(answer) > 0

    # ---------------------------------------------------------
    # Validate severity
    # ---------------------------------------------------------

    assert answer["severity"] in [
        "P1",
        "P2",
        "P3",
        "P4",
    ]

    # ---------------------------------------------------------
    # Validate basic text fields
    # ---------------------------------------------------------

    assert isinstance(
        answer["service"],
        str,
    )

    assert len(
        answer["service"].strip()
    ) > 0

    assert isinstance(
        answer["category"],
        str,
    )

    assert len(
        answer["category"].strip()
    ) > 0

    assert isinstance(
        answer["incident_summary"],
        str,
    )

    assert len(
        answer["incident_summary"].strip()
    ) > 0

    assert isinstance(
        answer["root_cause"],
        str,
    )

    assert len(
        answer["root_cause"].strip()
    ) > 0

    # ---------------------------------------------------------
    # Validate confidence
    # ---------------------------------------------------------

    assert isinstance(
        answer["root_cause_confidence"],
        int,
    )

    assert 0 <= answer[
        "root_cause_confidence"
    ] <= 100

    assert isinstance(
        answer["confidence"],
        int,
    )

    assert 0 <= answer[
        "confidence"
    ] <= 100

    # ---------------------------------------------------------
    # Validate historical evidence
    # ---------------------------------------------------------

    assert isinstance(
        answer["historical_evidence"],
        list,
    )

    # ---------------------------------------------------------
    # Validate recommended actions
    # ---------------------------------------------------------

    assert isinstance(
        answer["recommended_actions"],
        list,
    )

    assert len(
        answer["recommended_actions"]
    ) > 0

    # ---------------------------------------------------------
    # Validate short-term actions
    # ---------------------------------------------------------

    assert isinstance(
        answer["short_term_actions"],
        list,
    )

    # ---------------------------------------------------------
    # Validate long-term prevention
    # ---------------------------------------------------------

    assert isinstance(
        answer["long_term_prevention"],
        list,
    )

    # ---------------------------------------------------------
    # Validate reasoning
    # ---------------------------------------------------------

    assert isinstance(
        answer["reasoning"],
        str,
    )

    assert len(
        answer["reasoning"].strip()
    ) > 0

    # ---------------------------------------------------------
    # Validate uncertainty
    # ---------------------------------------------------------

    assert isinstance(
        answer["uncertainty"],
        str,
    )