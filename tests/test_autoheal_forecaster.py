"""
Tests for Auto-Heal Controller and Predictive Telemetry Forecaster.
"""

from app.auto_heal import AutoHealController
from app.forecaster import TelemetryForecaster


def test_auto_heal_action_selection():
    plan = AutoHealController.select_remediation_plan("database_connection_exhaustion")
    assert len(plan) >= 1
    assert any("db" in act["name"].lower() or "pool" in act["name"].lower() for act in plan)


def test_auto_heal_execution_low_risk():
    res = AutoHealController.execute_action("restart_pod_deployment", user_role="sre_engineer")
    assert res["success"] is True
    assert res["status"] == "EXECUTED"
    assert "kubectl" in res["command_executed"]


def test_auto_heal_execution_high_risk_policy_gate():
    # Regular SRE cannot execute high-risk database failover without approval
    res = AutoHealController.execute_action("trigger_database_failover", user_role="sre_engineer")
    assert res["success"] is False
    assert res["status"] == "APPROVAL_REQUIRED"

    # Commander can execute
    res_admin = AutoHealController.execute_action("trigger_database_failover", user_role="Incident Commander")
    assert res_admin["success"] is True
    assert res_admin["status"] == "EXECUTED"


def test_auto_heal_verification_loop():
    # Successful recovery
    res_recovered = AutoHealController.verify_remediation(pre_metric_error_rate=12.5, current_error_rate=0.4)
    assert res_recovered["verdict"] == "RECOVERY_VERIFIED"

    # Failed recovery triggers rollback
    res_failed = AutoHealController.verify_remediation(pre_metric_error_rate=12.5, current_error_rate=15.0)
    assert res_failed["verdict"] == "RECOVERY_FAILED_TRIGGER_ROLLBACK"


def test_telemetry_forecaster_trajectory():
    fc = TelemetryForecaster.forecast_metric_trajectory(
        metric_name="cpu_percent",
        current_value=82.0,
        growth_rate_percent=60.0,
        critical_threshold=90.0,
    )
    assert fc["forecast_risk"] in ["IMMINENT_CRITICAL_BREACH", "ELEVATED_DRIFT_WARNING"]
    assert len(fc["projection_timeline"]) == 5


def test_telemetry_forecaster_multi_metric():
    telemetry = {
        "cpu_percent": 88.0,
        "memory_percent": 60.0,
        "db_pool_usage": 92.0,
        "traffic_growth_percent": 50.0,
    }
    result = TelemetryForecaster.evaluate_multi_metric_forecast(telemetry)
    assert "summary_risk" in result
    assert "cpu" in result["forecasts"]
    assert "db_pool" in result["forecasts"]
