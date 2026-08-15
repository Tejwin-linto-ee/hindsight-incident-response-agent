"""
Offline Mock Unit Test Suite for SRE Incident Response Agent & Copilot.

Runs instantaneously in CI/CD without external API keys or network calls.
"""

from unittest.mock import MagicMock, patch
from app.agent import IncidentResponseAgent
from app.incident_history import IncidentHistory
from app.llm import IncidentLLM
from app.sre_chat import SRECopilot


MOCK_AI_RESPONSE = """{
  "severity": "P1",
  "service": "Payment API",
  "category": "Database",
  "incident_summary": "Payment API 503 outage due to pool exhaustion",
  "root_cause": "Database connection pool saturated at 100%",
  "root_cause_confidence": 95,
  "historical_evidence": [
    {
      "incident": "INC-001: Previous pool saturation",
      "relevance": "Direct match to 503 error symptoms"
    }
  ],
  "recommended_actions": [
    "Increase PgBouncer pool limits",
    "Restart stale worker pods"
  ],
  "short_term_actions": [
    "Audit slow SQL queries"
  ],
  "long_term_prevention": [
    "Implement read replicas"
  ],
  "reasoning": "Symptoms match historical incident signature perfectly.",
  "reasoning_summary": "Database connection pool exhaustion driving 503s.",
  "confidence": 94,
  "uncertainty": "Exact query causing deadlock requires trace analysis.",
  "failure_prediction": null
}"""


def test_incident_llm_offline_parsing():
    with patch.object(IncidentLLM, "_execute_completion", return_value=MOCK_AI_RESPONSE):
        llm = IncidentLLM()
        result = llm.analyze(
            incident="Payment API 503 database timeout",
            memories=["Historical payment outage"],
        )
        assert result["severity"] == "P1"
        assert result["service"] == "Payment API"
        assert result["confidence"] == 94
        assert len(result["recommended_actions"]) == 2


def test_agent_investigate_offline(tmp_path):
    mock_memory_results = [
        MagicMock(text="INC-001: Payment API pool exhausted. Increased pool to 100.")
    ]

    with patch("app.hindsight_memory.IncidentMemory.find_similar_incidents", return_value=mock_memory_results), \
         patch.object(IncidentLLM, "_execute_completion", return_value=MOCK_AI_RESPONSE):
        
        agent = IncidentResponseAgent()
        agent.history = IncidentHistory(file_path=tmp_path / "test_history.json")

        result = agent.investigate(
            incident="Payment API returning 503 errors and connection timeouts.",
            telemetry={"db_pool_usage": 98.0, "api_latency_ms": 1100.0},
        )

        assert result["analysis"]["severity"] == "P1"
        assert result["incident_id"] is not None
        assert "runbook" in result
        assert len(result["runbook"]["commands"]) > 0


def test_sre_copilot_offline():
    copilot = SRECopilot(llm=MagicMock())
    copilot.llm.chat_reply.return_value = "Scaling pods to 10 replicas will relieve immediate compute pressure without risking DB lockups."

    reply = copilot.ask("What is the impact of scaling the pods now?", incident_context={"service": "Payment API"})
    assert "Scaling pods" in reply
    assert len(copilot.get_history()) == 2
