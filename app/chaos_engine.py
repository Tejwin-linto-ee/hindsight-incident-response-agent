"""
Chaos Engineering & Fault Injection Simulator.

Injects synthetic infrastructure faults and observes the machine learning
anomaly model and Hindsight intelligence engine in real time.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ChaosScenario:
    id: str
    name: str
    category: str
    description: str
    target_service: str
    steps: list[dict[str, float]]
    symptoms: list[str]
    expected_failure_type: str


class ChaosEngine:
    """
    Manages chaos experiments and fault injection pipelines.
    """

    SCENARIOS: dict[str, ChaosScenario] = {
        "db_deadlock_storm": ChaosScenario(
            id="db_deadlock_storm",
            name="💥 Cascading Database Deadlock Storm",
            category="Database",
            description="Simulates an unindexed batch update locking rows, causing pool exhaustion and connection timeouts.",
            target_service="Payment API",
            expected_failure_type="Database Connection Exhaustion",
            symptoms=[
                "Database connection pool utilization spikes to 98%",
                "Active connection count reaches 96/100",
                "API latency climbs from 120ms to 1250ms",
                "HTTP 503 error rate reaches 10.5%",
            ],
            steps=[
                # Baseline
                {
                    "cpu_percent": 35.0,
                    "memory_percent": 45.0,
                    "disk_percent": 50.0,
                    "db_connections": 38.0,
                    "db_pool_usage": 40.0,
                    "api_latency_ms": 110.0,
                    "error_rate": 0.2,
                    "request_rate": 750.0,
                    "queue_depth": 15.0,
                    "network_latency_ms": 25.0,
                    "traffic_growth_percent": 2.0,
                },
                # Moderate Drift (Locks beginning)
                {
                    "cpu_percent": 48.0,
                    "memory_percent": 52.0,
                    "disk_percent": 50.0,
                    "db_connections": 72.0,
                    "db_pool_usage": 78.0,
                    "api_latency_ms": 480.0,
                    "error_rate": 3.5,
                    "request_rate": 820.0,
                    "queue_depth": 65.0,
                    "network_latency_ms": 30.0,
                    "traffic_growth_percent": 5.0,
                },
                # Full Outage (Deadlock saturation)
                {
                    "cpu_percent": 55.0,
                    "memory_percent": 55.0,
                    "disk_percent": 50.0,
                    "db_connections": 98.0,
                    "db_pool_usage": 99.0,
                    "api_latency_ms": 1450.0,
                    "error_rate": 11.2,
                    "request_rate": 850.0,
                    "queue_depth": 185.0,
                    "network_latency_ms": 35.0,
                    "traffic_growth_percent": 8.0,
                },
            ],
        ),
        "memory_leak_creep": ChaosScenario(
            id="memory_leak_creep",
            name="💧 Linear Memory Leak & Heap Creep",
            category="Memory",
            description="Simulates a cyclic reference leak in request cache causing progressive RSS memory climb to OOM.",
            target_service="User Profile Service",
            expected_failure_type="Memory Exhaustion",
            symptoms=[
                "Memory utilization steadily increases to 97%",
                "Garbage collection pause times degrade response latency",
                "Queue depth accumulates as worker threads stall",
            ],
            steps=[
                {
                    "cpu_percent": 40.0,
                    "memory_percent": 58.0,
                    "disk_percent": 50.0,
                    "db_connections": 45.0,
                    "db_pool_usage": 50.0,
                    "api_latency_ms": 140.0,
                    "error_rate": 0.5,
                    "request_rate": 900.0,
                    "queue_depth": 20.0,
                    "network_latency_ms": 30.0,
                    "traffic_growth_percent": 4.0,
                },
                {
                    "cpu_percent": 60.0,
                    "memory_percent": 82.0,
                    "disk_percent": 50.0,
                    "db_connections": 48.0,
                    "db_pool_usage": 52.0,
                    "api_latency_ms": 350.0,
                    "error_rate": 2.1,
                    "request_rate": 950.0,
                    "queue_depth": 60.0,
                    "network_latency_ms": 32.0,
                    "traffic_growth_percent": 6.0,
                },
                {
                    "cpu_percent": 78.0,
                    "memory_percent": 98.0,
                    "disk_percent": 50.0,
                    "db_connections": 50.0,
                    "db_pool_usage": 55.0,
                    "api_latency_ms": 820.0,
                    "error_rate": 6.8,
                    "request_rate": 980.0,
                    "queue_depth": 145.0,
                    "network_latency_ms": 38.0,
                    "traffic_growth_percent": 8.0,
                },
            ],
        ),
        "cpu_saturation_storm": ChaosScenario(
            id="cpu_saturation_storm",
            name="⚡ Flash Traffic Surge & CPU Saturation",
            category="Compute",
            description="Simulates a 40% viral traffic spike exhausting worker threads and pinning CPU to 98%.",
            target_service="Checkout Gateway",
            expected_failure_type="CPU Saturation",
            symptoms=[
                "CPU utilization hits 97.5%",
                "Incoming request rate surges to 1950 req/sec",
                "Queue depth accumulates to 160 items",
            ],
            steps=[
                {
                    "cpu_percent": 45.0,
                    "memory_percent": 50.0,
                    "disk_percent": 50.0,
                    "db_connections": 45.0,
                    "db_pool_usage": 50.0,
                    "api_latency_ms": 130.0,
                    "error_rate": 0.4,
                    "request_rate": 800.0,
                    "queue_depth": 20.0,
                    "network_latency_ms": 28.0,
                    "traffic_growth_percent": 5.0,
                },
                {
                    "cpu_percent": 76.0,
                    "memory_percent": 62.0,
                    "disk_percent": 50.0,
                    "db_connections": 50.0,
                    "db_pool_usage": 55.0,
                    "api_latency_ms": 380.0,
                    "error_rate": 2.5,
                    "request_rate": 1400.0,
                    "queue_depth": 85.0,
                    "network_latency_ms": 32.0,
                    "traffic_growth_percent": 22.0,
                },
                {
                    "cpu_percent": 98.0,
                    "memory_percent": 74.0,
                    "disk_percent": 50.0,
                    "db_connections": 55.0,
                    "db_pool_usage": 58.0,
                    "api_latency_ms": 780.0,
                    "error_rate": 7.4,
                    "request_rate": 2100.0,
                    "queue_depth": 175.0,
                    "network_latency_ms": 40.0,
                    "traffic_growth_percent": 45.0,
                },
            ],
        ),
        "network_partition_latency": ChaosScenario(
            id="network_partition_latency",
            name="🌐 Inter-AZ Network Congestion & Latency Spike",
            category="Network",
            description="Simulates cross-availability zone packet loss and routing degradation driving network latency to 550ms.",
            target_service="Order Fulfillment Service",
            expected_failure_type="Network Degradation",
            symptoms=[
                "Network RTT latency spikes from 30ms to 520ms",
                "Upstream gateway times out waiting on internal gRPC calls",
                "Error rate rises to 8.5%",
            ],
            steps=[
                {
                    "cpu_percent": 42.0,
                    "memory_percent": 48.0,
                    "disk_percent": 50.0,
                    "db_connections": 45.0,
                    "db_pool_usage": 50.0,
                    "api_latency_ms": 150.0,
                    "error_rate": 0.6,
                    "request_rate": 900.0,
                    "queue_depth": 25.0,
                    "network_latency_ms": 35.0,
                    "traffic_growth_percent": 4.0,
                },
                {
                    "cpu_percent": 46.0,
                    "memory_percent": 50.0,
                    "disk_percent": 50.0,
                    "db_connections": 48.0,
                    "db_pool_usage": 52.0,
                    "api_latency_ms": 450.0,
                    "error_rate": 4.0,
                    "request_rate": 920.0,
                    "queue_depth": 75.0,
                    "network_latency_ms": 220.0,
                    "traffic_growth_percent": 6.0,
                },
                {
                    "cpu_percent": 50.0,
                    "memory_percent": 52.0,
                    "disk_percent": 50.0,
                    "db_connections": 50.0,
                    "db_pool_usage": 55.0,
                    "api_latency_ms": 920.0,
                    "error_rate": 9.6,
                    "request_rate": 950.0,
                    "queue_depth": 140.0,
                    "network_latency_ms": 540.0,
                    "traffic_growth_percent": 8.0,
                },
            ],
        ),
        "disk_exhaustion_lock": ChaosScenario(
            id="disk_exhaustion_lock",
            name="💾 Runaway WAL / Debug Log Disk Exhaustion",
            category="Storage",
            description="Simulates verbose logging filling ephemeral EBS volumes to 98% capacity.",
            target_service="Audit Logging Worker",
            expected_failure_type="Disk Exhaustion",
            symptoms=[
                "Disk utilization reaches 98%",
                "I/O wait stalls disk writes",
                "Worker queues stop processing incoming events",
            ],
            steps=[
                {
                    "cpu_percent": 40.0,
                    "memory_percent": 45.0,
                    "disk_percent": 65.0,
                    "db_connections": 45.0,
                    "db_pool_usage": 50.0,
                    "api_latency_ms": 160.0,
                    "error_rate": 0.5,
                    "request_rate": 850.0,
                    "queue_depth": 20.0,
                    "network_latency_ms": 30.0,
                    "traffic_growth_percent": 3.0,
                },
                {
                    "cpu_percent": 45.0,
                    "memory_percent": 50.0,
                    "disk_percent": 88.0,
                    "db_connections": 48.0,
                    "db_pool_usage": 52.0,
                    "api_latency_ms": 320.0,
                    "error_rate": 2.2,
                    "request_rate": 900.0,
                    "queue_depth": 40.0,
                    "network_latency_ms": 32.0,
                    "traffic_growth_percent": 4.0,
                },
                {
                    "cpu_percent": 52.0,
                    "memory_percent": 55.0,
                    "disk_percent": 99.0,
                    "db_connections": 50.0,
                    "db_pool_usage": 55.0,
                    "api_latency_ms": 620.0,
                    "error_rate": 5.8,
                    "request_rate": 920.0,
                    "queue_depth": 65.0,
                    "network_latency_ms": 35.0,
                    "traffic_growth_percent": 5.0,
                },
            ],
        ),
    }

    @classmethod
    def get_all_scenarios(cls) -> list[ChaosScenario]:
        return list(cls.SCENARIOS.values())

    @classmethod
    def get_scenario(cls, scenario_id: str) -> ChaosScenario | None:
        return cls.SCENARIOS.get(scenario_id)
