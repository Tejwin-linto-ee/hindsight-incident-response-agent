import json

from app.failure_predictor import FailurePredictor


predictor = FailurePredictor()


# ============================================================
# TEST CASES
# ============================================================

TEST_CASES = {

    "HEALTHY SYSTEM": {

        "cpu_percent": 40,
        "memory_percent": 45,
        "disk_percent": 50,
        "db_connections": 40,
        "db_pool_usage": 45,
        "api_latency_ms": 150,
        "error_rate": 1.0,
        "request_rate": 800,
        "queue_depth": 25,
        "network_latency_ms": 30,
        "traffic_growth_percent": 5,
    },


    "DATABASE FAILURE": {

        "cpu_percent": 40,
        "memory_percent": 45,
        "disk_percent": 50,
        "db_connections": 96,
        "db_pool_usage": 98,
        "api_latency_ms": 1100,
        "error_rate": 9,
        "request_rate": 800,
        "queue_depth": 160,
        "network_latency_ms": 30,
        "traffic_growth_percent": 5,
    },


    "CPU SATURATION": {

        "cpu_percent": 97,
        "memory_percent": 70,
        "disk_percent": 50,
        "db_connections": 50,
        "db_pool_usage": 55,
        "api_latency_ms": 650,
        "error_rate": 5,
        "request_rate": 1800,
        "queue_depth": 150,
        "network_latency_ms": 40,
        "traffic_growth_percent": 35,
    },


    "MEMORY EXHAUSTION": {

        "cpu_percent": 75,
        "memory_percent": 97,
        "disk_percent": 50,
        "db_connections": 50,
        "db_pool_usage": 55,
        "api_latency_ms": 600,
        "error_rate": 5,
        "request_rate": 1000,
        "queue_depth": 110,
        "network_latency_ms": 40,
        "traffic_growth_percent": 10,
    },


    "NETWORK DEGRADATION": {

        "cpu_percent": 45,
        "memory_percent": 50,
        "disk_percent": 50,
        "db_connections": 50,
        "db_pool_usage": 55,
        "api_latency_ms": 800,
        "error_rate": 8,
        "request_rate": 1000,
        "queue_depth": 130,
        "network_latency_ms": 500,
        "traffic_growth_percent": 10,
    },


    "API AVAILABILITY DEGRADATION": {

        "cpu_percent": 45,
        "memory_percent": 50,
        "disk_percent": 50,
        "db_connections": 50,
        "db_pool_usage": 55,
        "api_latency_ms": 1250,
        "error_rate": 12,
        "request_rate": 1700,
        "queue_depth": 180,
        "network_latency_ms": 40,
        "traffic_growth_percent": 40,
    },


    "DISK EXHAUSTION": {

        "cpu_percent": 45,
        "memory_percent": 50,
        "disk_percent": 98,
        "db_connections": 50,
        "db_pool_usage": 55,
        "api_latency_ms": 500,
        "error_rate": 4,
        "request_rate": 1000,
        "queue_depth": 50,
        "network_latency_ms": 40,
        "traffic_growth_percent": 5,
    },
}


# ============================================================
# RUN TESTS
# ============================================================

print()
print("=" * 70)
print("FAILURE TYPE CLASSIFICATION TEST")
print("=" * 70)


for test_name, telemetry in TEST_CASES.items():

    print()
    print("=" * 70)
    print(test_name)
    print("=" * 70)

    result = predictor.predict(
        telemetry
    )

    print()

    print(
        "Failure Risk:",
        f"{result['failure_risk']}%",
    )

    print(
        "Risk Level:",
        result["risk_level"],
    )

    print(
        "Predicted Failure:",
        result["predicted_failure"],
    )

    print(
        "Predicted Failure Type:",
        result["predicted_failure_type"],
    )

    print(
        "Type Probability:",
        f"{result['predicted_failure_probability']}%",
    )

    print(
        "Risk Window:",
        result["risk_window"],
    )

    print(
        "Prediction Confidence:",
        f"{result['prediction_confidence']}%",
    )

    print()

    print(
        "Failure Type Probabilities:"
    )

    for item in result[
        "failure_type_probabilities"
    ]:

        print(
            f"  {item['display_name']:<40}"
            f"{item['probability']:>7.2f}%"
        )

    print()

    print(
        "Important Indicators:"
    )

    for indicator in result[
        "evidence"
    ]:

        print(
            f"  {indicator['feature']:<30}"
            f"{indicator['value']:>8}"
            f"  [{indicator['status']}]"
        )

    print()


print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)