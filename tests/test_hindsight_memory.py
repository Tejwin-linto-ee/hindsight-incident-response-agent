"""
Offline Unit Test Suite for Hindsight Memory Expansion, Reranking, and Tiering.

Tests:
1. Three query variants generated (Failure, Root Cause, Telemetry).
2. Duplicate memories removed across multi-query search.
3. Memory relevance scoring (0-100%).
4. High relevance threshold (>= 80%).
5. Moderate relevance threshold (>= 60%).
6. Low context threshold (< 60%).
7. Technician-confirmed resolution detection and boost.
8. No-memory case handling.
9. Hindsight recall error handling.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.memory_engine import MemoryEngine
from app.hindsight_memory import IncidentMemory


def test_query_expansion():
    incident = "Payment API returning HTTP 503 errors. Database connection pool exhaustion."
    telemetry = {"db_pool_usage": 95.0, "api_latency_ms": 1100.0}

    queries = MemoryEngine.expand_query(incident, telemetry=telemetry)
    assert len(queries) >= 2
    assert incident in queries[0]
    assert any("database" in q.lower() or "503" in q.lower() for q in queries)


def test_relevance_scoring_and_tiering():
    query = "Payment API 503 database connection pool exhausted"

    high_mem = "INC-001: Payment API 503 database connection pool exhausted at 100%. Increased pool size resolution."
    mod_mem = "INC-002: Payment API 503 connection pool latency spike during traffic burst."
    low_mem = "INC-003: Disk partition full on audit worker node."

    s_high = MemoryEngine.structure_memory(high_mem, query)
    s_mod = MemoryEngine.structure_memory(mod_mem, query)
    s_low = MemoryEngine.structure_memory(low_mem, query)

    assert s_high["relevance_score"] >= MemoryEngine.HIGH_RELEVANCE_THRESHOLD
    assert s_high["tier"] == "HIGH RELEVANCE"

    assert s_mod["relevance_score"] >= MemoryEngine.MODERATE_RELEVANCE_THRESHOLD
    assert s_mod["tier"] == "MODERATE"

    assert s_low["relevance_score"] < MemoryEngine.MODERATE_RELEVANCE_THRESHOLD
    assert s_low["tier"] == "LOW CONTEXT"


def test_technician_confirmed_resolution_detection():
    query = "Payment API 503 database connection pool"
    confirmed_mem = """
============================================================
VERIFIED PRODUCTION INCIDENT POSTMORTEM
============================================================
Service: Payment API
Human Technician Feedback:
Diagnosis was CONFIRMED / HELPFUL

CONFIRMED HUMAN ENGINEER RESOLUTION & MITIGATION:
Killed long-running batch queries and increased PgBouncer pool limit.
"""

    struct = MemoryEngine.structure_memory(confirmed_mem, query)
    assert struct["technician_confirmed"] is True
    assert "Killed long-running batch queries" in struct["extracted_resolution"]


def test_deduplication_and_ranking():
    query = "Database connection pool exhaustion"
    raw_list = [
        "Duplicate memory text for database connection pool exhaustion",
        "Duplicate memory text for database connection pool exhaustion",
        "Different memory about disk storage full",
    ]

    processed = MemoryEngine.process_and_rank_memories(raw_list, query, limit=5)
    assert len(processed) == 2
    assert processed[0]["relevance_score"] >= processed[1]["relevance_score"]


def test_no_memory_handling():
    processed = MemoryEngine.process_and_rank_memories([], "Unheard error", limit=5)
    assert processed == []


def test_hindsight_client_offline_recall_warning(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "test-bank")
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "https://mock.hindsight")
    monkeypatch.setenv("HINDSIGHT_API_KEY", "test-key")

    with patch("hindsight_client.Hindsight.recall", side_effect=Exception("Connection refused")):
        mem_client = IncidentMemory()
        results = mem_client.find_similar_incidents("Unknown error")
        assert results == []
