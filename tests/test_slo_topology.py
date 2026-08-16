"""
Tests for SLO Engine and Service Topology Blast Radius Engine.
"""

from app.slo_engine import SLOEngine
from app.topology_engine import ServiceTopologyEngine


def test_slo_evaluation_normal():
    result = SLOEngine.evaluate_slo_status(error_rate=0.05, api_latency_ms=120.0, request_rate=1500.0)
    assert result["burn_rate"] <= 1.0
    assert "HEALTHY" in result["alert_tier"]
    assert result["budget_remaining_pct"] > 80.0


def test_slo_evaluation_critical_burn():
    result = SLOEngine.evaluate_slo_status(error_rate=5.5, api_latency_ms=2500.0, request_rate=3000.0)
    assert result["burn_rate"] >= 14.4
    assert "CRITICAL_PAGE" in result["alert_tier"]
    assert result["hours_to_exhaustion"] is not None


def test_service_topology_blast_radius():
    blast = ServiceTopologyEngine.calculate_blast_radius("database-cluster")
    assert "payment-api" in blast["direct_dependents"]
    assert blast["blast_radius_count"] >= 4
    assert blast["revenue_risk_tier"] == "EXTREME"
    assert blast["estimated_cost_per_minute_usd"] > 1000


def test_service_topology_unknown_service_fallback():
    blast = ServiceTopologyEngine.calculate_blast_radius("unknown-service")
    assert blast["root_service"] == "payment-api"
    assert blast["blast_radius_count"] >= 1
