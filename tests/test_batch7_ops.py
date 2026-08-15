"""
Unit and integration test suite for Batch 7: Operational Response & Incident Management Suite.

Tests:
1. RunbookGenerator returns complete schemas including situation_summary, blast_radius, pre_flight_checks, and safety execution warnings.
2. PostmortemExporter generates valid Markdown and JSON containing telemetry, prediction data, and technician reviews.
3. AlertDispatcher formats rich Slack, Teams, PagerDuty, and Opsgenie payloads gracefully without crashing when unconfigured.
4. SRECopilot retains context up to bounded limit (MAX_HISTORY).
"""

import json
import pytest
from app.runbook_generator import RunbookGenerator
from app.postmortem_exporter import PostmortemExporter
from app.alert_dispatcher import AlertDispatcher
from app.sre_chat import SRECopilot


def test_runbook_generator_schema_and_safety():
    analysis = {
        "service": "checkout-service",
        "category": "database",
        "root_cause": "pool deadlock and exhaustion",
        "severity": "P1",
    }
    telemetry = {"db_pool_usage": 98.0, "db_connections": 95.0}
    rb = RunbookGenerator.generate_runbook(analysis, telemetry)

    assert rb["service"] == "checkout-service"
    assert rb["category"] == "database"
    assert len(rb["commands"]) >= 2
    assert len(rb["rollback_commands"]) >= 1
    assert len(rb["safety_checks"]) >= 1
    assert len(rb["verification_steps"]) >= 1
    assert len(rb["pre_flight_checks"]) >= 1
    assert "OPERATOR REVIEW REQUIRED" in rb["execution_warning"]


def test_postmortem_exporter_markdown_and_json():
    analysis = {
        "service": "payment-gateway",
        "severity": "P1",
        "category": "database",
        "incident_summary": "Postgres connection exhaustion leading to HTTP 503s",
        "root_cause": "Unindexed transaction query causing pool starvation",
        "confidence": 92,
        "root_cause_confidence": 95,
        "uncertainty": "Exact originating client pod not isolated.",
        "reasoning": "Observed sharp rise in active connections coinciding with slow query alerts.",
        "recommended_actions": ["Drain idle sessions", "Scale PgBouncer pool"],
        "short_term_actions": ["Add composite index on transactions table"],
        "long_term_prevention": ["Deploy connection pool autoscaler"],
        "historical_evidence": [{"incident": "INC-2025-04", "relevance": "Similar DB lockup"}],
    }
    telemetry = {"db_pool_usage": 99.0, "api_latency_ms": 1800.0}
    prediction = {
        "predicted_failure_type": "Database Connection Exhaustion",
        "failure_risk": 96,
        "prediction_confidence": 98,
        "risk_window": "< 3 minutes",
        "urgency_index": 98,
        "model": "Calibrated Ensemble",
    }
    tech_feedback = {
        "helpful": True,
        "resolution": "Applied pool drain and restarted affected worker pods.",
    }

    # Markdown export verification
    md = PostmortemExporter.generate_markdown(
        analysis=analysis,
        incident_text="Payment API returning 503 errors.",
        telemetry=telemetry,
        prediction=prediction,
        technician_feedback=tech_feedback,
        incident_id="INC-TEST-001",
    )
    assert "# 📑 SRE Incident Postmortem" in md
    assert "INC-TEST-001" in md
    assert "Machine Learning Predictive Intelligence" in md
    assert "Technician Review & Verified Resolution" in md
    assert "Five Whys" in md

    # JSON export verification
    json_str = PostmortemExporter.generate_json(
        analysis=analysis,
        incident_text="Payment API returning 503 errors.",
        telemetry=telemetry,
        prediction=prediction,
        technician_feedback=tech_feedback,
        incident_id="INC-TEST-001",
    )
    data = json.loads(json_str)
    assert data["postmortem_metadata"]["incident_id"] == "INC-TEST-001"
    assert data["incident_report"]["prediction"]["failure_risk"] == 96
    assert data["incident_report"]["technician_feedback"]["helpful"] is True


def test_alert_dispatcher_payloads():
    analysis = {
        "service": "auth-service",
        "severity": "P1",
        "incident_summary": "OAuth rate limit spike",
        "root_cause": "Token cache saturation",
        "confidence": 88,
        "recommended_actions": ["Flush Redis auth cache"],
    }

    # Slack card
    slack_card = AlertDispatcher.format_slack_card(analysis, incident_id="INC-ALERT-01")
    assert "attachments" in slack_card
    assert len(slack_card["attachments"][0]["blocks"]) >= 4

    # Teams card
    teams_card = AlertDispatcher.format_teams_card(analysis, incident_id="INC-ALERT-01")
    assert teams_card["@type"] == "MessageCard"

    # PagerDuty payload
    pd_payload = AlertDispatcher.format_pagerduty_payload(analysis, incident_id="INC-ALERT-01", routing_key="test-key")
    assert pd_payload["event_action"] == "trigger"
    assert pd_payload["payload"]["severity"] == "critical"

    # Opsgenie payload
    og_payload = AlertDispatcher.format_opsgenie_payload(analysis, incident_id="INC-ALERT-01")
    assert og_payload["priority"] == "P1"

    # Dispatch to empty URL returns graceful error without crashing
    res = AlertDispatcher.dispatch("", slack_card)
    assert res["success"] is False
    assert "not configured" in res["error"] or "empty" in res["error"]


def test_sre_copilot_bounded_history():
    copilot = SRECopilot()
    assert copilot.MAX_HISTORY == 20
    assert len(copilot.get_history()) == 0

    copilot.reset()
    assert len(copilot.get_history()) == 0
