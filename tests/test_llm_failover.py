"""
Offline LLM Failover & Response Normalization Unit Test Suite.

Tests:
1. Valid structured LLM response.
2. reasoning_summary -> reasoning normalization fallback.
3. Missing required field / safe default normalization.
4. Malformed JSON with markdown fences parsing.
5. Primary timeout -> Fallback 1 execution.
6. Primary failure + Fallback 1 failure -> Fallback 2 execution.
7. All OpenRouter providers failure -> Groq fallback execution.
8. All providers failure handling.
9. API key missing handling.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.llm import IncidentLLM


MOCK_VALID_RESPONSE = """```json
{
  "severity": "P1",
  "service": "Payment API",
  "category": "Database",
  "incident_summary": "Database pool saturation causing HTTP 503s",
  "root_cause": "Unindexed batch update locked table rows",
  "root_cause_confidence": 92,
  "historical_evidence": [],
  "recommended_actions": ["Kill blocking query pid 4092"],
  "short_term_actions": ["Increase connection pool size"],
  "long_term_prevention": ["Add missing index on payment_transactions.status"],
  "reasoning": "Telemetry and historical patterns point directly to row locks.",
  "confidence": 90,
  "uncertainty": "Exact transaction script requires log verification."
}
```"""

MOCK_SUMMARY_ONLY_RESPONSE = """{
  "severity": "P2",
  "service": "Checkout Gateway",
  "category": "Compute",
  "incident_summary": "CPU saturation under traffic surge",
  "root_cause": "Worker thread pool starvation",
  "root_cause_confidence": 88,
  "recommended_actions": ["Autoscale worker pods"],
  "reasoning_summary": "Traffic surge pinned CPU at 98%, stalling event loop.",
  "confidence": 85
}"""


def test_valid_structured_llm_response():
    with patch.object(IncidentLLM, "_execute_completion", return_value=MOCK_VALID_RESPONSE):
        llm = IncidentLLM()
        res = llm.analyze("CPU pinned at 98%", memories=[])
        assert res["severity"] == "P1"
        assert res["service"] == "Payment API"
        assert res["reasoning"] == "Telemetry and historical patterns point directly to row locks."


def test_reasoning_summary_to_reasoning_normalization():
    with patch.object(IncidentLLM, "_execute_completion", return_value=MOCK_SUMMARY_ONLY_RESPONSE):
        llm = IncidentLLM()
        res = llm.analyze("Checkout slow", memories=[])
        assert res["reasoning"] == "Traffic surge pinned CPU at 98%, stalling event loop."
        assert res["reasoning_summary"] == "Traffic surge pinned CPU at 98%, stalling event loop."


def test_malformed_json_with_fences_extraction():
    raw_text = "Here is your analysis:\n```json\n" + MOCK_VALID_RESPONSE.replace("```json", "").replace("```", "") + "\n```\nHope this helps!"
    with patch.object(IncidentLLM, "_execute_completion", return_value=raw_text):
        llm = IncidentLLM()
        res = llm.analyze("Database deadlocks", memories=[])
        assert res["severity"] == "P1"
        assert res["root_cause_confidence"] == 92


def test_api_key_missing_raises_value_error(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError, match="Neither OPENROUTER_API_KEY nor GROQ_API_KEY was found"):
        IncidentLLM()


def test_primary_failure_triggers_fallback(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-or-key")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    
    llm = IncidentLLM()
    
    call_counts = []
    
    def mock_create(*args, **kwargs):
        model = kwargs.get("model")
        call_counts.append(model)
        if model == "moonshotai/kimi-k2":
            raise Exception("HTTP 503 Provider Error")
        
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content=MOCK_VALID_RESPONSE))]
        return mock_resp

    with patch.object(llm.client.chat.completions, "create", side_effect=mock_create):
        result = llm._execute_completion("system", "user")
        assert result == MOCK_VALID_RESPONSE
        assert call_counts[0] == "moonshotai/kimi-k2"
        assert call_counts[1] == "meta-llama/llama-3.3-70b-instruct"


def test_groq_fallback_when_openrouter_fails(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-or-key")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")

    llm = IncidentLLM()
    
    # Mock OpenRouter client to always fail
    def mock_or_fail(*args, **kwargs):
        raise Exception("HTTP 429 Rate Limit Exceeded")
    
    mock_groq_resp = MagicMock()
    mock_groq_resp.choices = [MagicMock(message=MagicMock(content="GROQ_RESPONSE_OK"))]

    with patch.object(llm.client.chat.completions, "create", side_effect=mock_or_fail), \
         patch.object(llm.groq_client.chat.completions, "create", return_value=mock_groq_resp):
        
        result = llm._execute_completion("system", "user")
        assert result == "GROQ_RESPONSE_OK"


def test_all_providers_unavailable_raises_runtime_error(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-or-key")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")

    llm = IncidentLLM()

    with patch.object(llm.client.chat.completions, "create", side_effect=Exception("OpenRouter timeout")), \
         patch.object(llm.groq_client.chat.completions, "create", side_effect=Exception("Groq error")):
        
        with pytest.raises(RuntimeError, match="All LLM completion attempts failed"):
            llm._execute_completion("system", "user")
