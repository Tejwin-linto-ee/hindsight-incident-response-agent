from app.agent import IncidentResponseAgent


def test_incident_response():

    incident = """
    The Payment API is returning HTTP 503 errors.
    Payment requests are failing and database connections are timing out.
    Database connection pool utilization has reached 100%.
    The service is experiencing high request latency.
    """

    agent = IncidentResponseAgent()

    try:

        result = agent.investigate(
            incident
        )

        # -----------------------------------------------------
        # Validate overall response structure
        # -----------------------------------------------------

        assert isinstance(
            result,
            dict,
        )

        assert result["incident"] == incident

        assert "analysis" in result

        assert "historical_memories" in result

        # -----------------------------------------------------
        # Validate structured AI analysis
        # -----------------------------------------------------

        analysis = result["analysis"]

        assert isinstance(
            analysis,
            dict,
        )

        # -----------------------------------------------------
        # Validate severity
        # -----------------------------------------------------

        assert analysis["severity"] in [
            "P1",
            "P2",
            "P3",
            "P4",
        ]

        # -----------------------------------------------------
        # Validate core fields
        # -----------------------------------------------------

        assert isinstance(
            analysis["service"],
            str,
        )

        assert isinstance(
            analysis["category"],
            str,
        )

        assert isinstance(
            analysis["incident_summary"],
            str,
        )

        assert isinstance(
            analysis["root_cause"],
            str,
        )

        # -----------------------------------------------------
        # Validate confidence
        # -----------------------------------------------------

        assert isinstance(
            analysis["confidence"],
            int,
        )

        assert 0 <= analysis[
            "confidence"
        ] <= 100

        assert isinstance(
            analysis["root_cause_confidence"],
            int,
        )

        assert 0 <= analysis[
            "root_cause_confidence"
        ] <= 100

        # -----------------------------------------------------
        # Validate historical evidence
        # -----------------------------------------------------

        memories = result[
            "historical_memories"
        ]

        assert isinstance(
            memories,
            list,
        )

        assert len(memories) > 0

        assert isinstance(
            analysis["historical_evidence"],
            list,
        )

        # -----------------------------------------------------
        # Validate actions
        # -----------------------------------------------------

        assert isinstance(
            analysis["recommended_actions"],
            list,
        )

        assert len(
            analysis["recommended_actions"]
        ) > 0

        assert isinstance(
            analysis["short_term_actions"],
            list,
        )

        assert isinstance(
            analysis["long_term_prevention"],
            list,
        )

        # -----------------------------------------------------
        # Validate reasoning
        # -----------------------------------------------------

        assert isinstance(
            analysis["reasoning"],
            str,
        )

        assert len(
            analysis["reasoning"].strip()
        ) > 0

        # -----------------------------------------------------
        # Validate uncertainty
        # -----------------------------------------------------

        assert isinstance(
            analysis["uncertainty"],
            str,
        )

    finally:

        agent.close()


if __name__ == "__main__":
    test_incident_response()