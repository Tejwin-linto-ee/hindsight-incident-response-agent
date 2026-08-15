"""
Pre-emptive SRE Remediation Playbook Registry.

Maps classified failure archetypes to recommended, non-destructive,
reviewable operational playbooks.
"""

from __future__ import annotations


class PlaybookRegistry:
    """
    Registry of pre-emptive remediation procedures per failure archetype.
    """

    PLAYBOOKS: dict[str, list[str]] = {
        "database_connection_exhaustion": [
            "Drain idle client pool connections & raise max_connections ceiling by 30%",
            "Enable Redis query response cache to shed 40% read load from master DB",
            "Kill slow long-running analytical queries (>5000ms) holding pool locks",
        ],
        "cpu_saturation": [
            "Trigger horizontal pod autoscaling (HPA) to scale replica count +50%",
            "Temporarily shed non-critical background jobs and batch sync pipelines",
            "Enable API rate-limiting tier-1 on heavy unauthenticated endpoints",
        ],
        "memory_exhaustion": [
            "Force graceful container rolling restart to release leaked heap allocations",
            "Reduce in-memory caching TTL and trim worker concurrency thresholds",
            "Collect heap dump snapshot before OOMKill for immediate memory leak RCA",
        ],
        "api_availability_degradation": [
            "Enable circuit breaker on downstream upstream microservice dependencies",
            "Route non-critical traffic to cached static fallback endpoints",
            "Scale out API Gateway ingress proxies to absorb queue backlog",
        ],
        "disk_exhaustion": [
            "Trigger automated log rotation and compress expired stdout/stderr logs",
            "Purge temporary scratch buffers and obsolete build cache artifacts",
            "Expand provisioned EBS/PV storage volume quota before I/O freeze",
        ],
        "network_degradation": [
            "Switch egress routing to secondary standby multi-AZ transit gateway",
            "Enable HTTP/2 keep-alive connection reuse to minimize TCP handshake overhead",
            "Engage Cloudflare/CDN edge caching to absorb anomalous regional traffic",
        ],
        "none": [
            "System metrics within nominal SLO thresholds — maintain continuous telemetry monitoring.",
        ],
    }

    @classmethod
    def get_playbook(cls, failure_type: str) -> list[str]:
        return cls.PLAYBOOKS.get(
            failure_type,
            ["Monitor system telemetry continuously and maintain alert standbys."],
        )
