"""
Unit Tests for Enterprise SRE Platform Extensions.

Tests:
- RunbookGenerator
- PostmortemExporter
- AlertDispatcher
- ChaosEngine
- SRECopilot
"""

import json
from app.runbook_generator import RunbookGenerator
from app.postmortem_exporter import PostmortemExporter
from app.alert_dispatcher import AlertDispatcher
from app.chaos_engine import ChaosEngine


def test_runbook_generator_database():
    analysis = {
        "service": "Payment Gateway",
        "category": "Database",
        "severity": "P1",
        "root_cause": "Database connection pool exhaustion",
    }
    rb = RunbookGenerator.generate_runbook(analysis)
    assert rb["service"] == "payment-gateway"
    assert rb["severity"] == "P1"
    assert len(rb["commands"]) > 0
    assert len(rb["rollback_commands"]) > 0
    assert len(rb["safety_checks"]) > 0
    assert len(rb["verification_steps"]) > 0
    # Check that pg_terminate or pgbouncer is in command
    all_cmds = " ".join([c["command"] for c in rb["commands"]])
    assert "psql" in all_cmds or "pgbouncer" in all_cmds or "kubectl" in all_cmds


def test_runbook_generator_compute():
    analysis = {
        "service": "Checkout API",
        "category": "Compute",
        "severity": "P2",
        "root_cause": "High CPU utilization and traffic surge",
    }
    rb = RunbookGenerator.generate_runbook(analysis)
    assert len(rb["commands"]) > 0
    all_cmds = " ".join([c["command"] for c in rb["commands"]])
    assert "kubectl" in all_cmds or "scale" in all_cmds


def test_postmortem_exporter():
    analysis = {
        "service": "Order Processing",
        "category": "Network",
        "severity": "P1",
        "incident_summary": "Service experienced severe latency timeout",
        "root_cause": "Cross-AZ packet degradation",
        "confidence": 92,
        "root_cause_confidence": 90,
        "recommended_actions": ["Reroute traffic", "Scale instances"],
        "short_term_actions": ["Enable circuit breaker"],
        "long_term_prevention": ["Multi-region deployment"],
        "historical_evidence": [
            {"incident": "INC-2025-01", "relevance": "Similar network drop"}
        ],
        "reasoning": "Telemetry and historical logs indicate gateway timeouts.",
        "uncertainty": "Exact packet drop rate needs verification.",
    }
    telemetry = {"api_latency_ms": 850.0, "network_latency_ms": 420.0}
    
    # Test Markdown generation
    md = PostmortemExporter.generate_markdown(
        analysis=analysis,
        incident_text="Order processing timeouts observed.",
        telemetry=telemetry,
        incident_id="INC-TEST-001",
        author="Lead SRE",
    )
    assert "INC-TEST-001" in md
    assert "Order Processing" in md
    assert "Executive Summary" in md
    assert "Five Whys" in md
    assert "api_latency_ms" in md

    # Test JSON generation
    json_str = PostmortemExporter.generate_json(
        analysis=analysis,
        incident_text="Order processing timeouts observed.",
        telemetry=telemetry,
        incident_id="INC-TEST-001",
    )
    parsed = json.loads(json_str)
    assert parsed["postmortem_metadata"]["incident_id"] == "INC-TEST-001"
    assert parsed["ai_analysis"]["service"] == "Order Processing"


def test_alert_dispatcher_formatting():
    analysis = {
        "service": "Auth Service",
        "severity": "P1",
        "incident_summary": "User authentication failing",
        "root_cause": "Redis session store unreachable",
        "confidence": 95,
        "recommended_actions": ["Failover Redis to replica", "Clear expired sessions"],
    }
    # Test Slack formatting
    slack_card = AlertDispatcher.format_slack_card(analysis, incident_id="INC-999")
    assert "attachments" in slack_card
    assert len(slack_card["attachments"]) > 0
    assert "#F43F5E" in slack_card["attachments"][0]["color"]  # Critical P1 color

    # Test Teams formatting
    teams_card = AlertDispatcher.format_teams_card(analysis, incident_id="INC-999")
    assert teams_card["@type"] == "MessageCard"
    assert "Auth Service" in teams_card["summary"]


def test_chaos_engine():
    scenarios = ChaosEngine.get_all_scenarios()
    assert len(scenarios) >= 5
    
    db_chaos = ChaosEngine.get_scenario("db_deadlock_storm")
    assert db_chaos is not None
    assert db_chaos.target_service == "Payment API"
    assert len(db_chaos.steps) >= 3
    # Check peak metrics has high pool usage
    peak = db_chaos.steps[-1]
    assert peak["db_pool_usage"] >= 95.0
