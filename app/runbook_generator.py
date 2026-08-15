"""
Actionable SRE Runbook & Remediation Script Generator.

Generates precise, copy-pasteable CLI commands, configuration patches,
and safety rollback procedures tailored to the diagnosed failure archetype.

IMPORTANT SAFETY CONSTRAINTS:
- All commands are recommendations and must be verified by an authorized human operator before execution.
- The platform NEVER executes these commands automatically.
"""

from typing import Any


class RunbookGenerator:
    """
    Generates actionable infrastructure remediation commands based on:
    - Service name
    - Incident severity
    - Failure category & root cause
    - Driving telemetry metrics
    """

    @classmethod
    def generate_runbook(
        cls,
        analysis: dict[str, Any],
        telemetry: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        service = (analysis.get("service") or "app-service").lower().replace(" ", "-")
        category = (analysis.get("category") or "General").lower()
        root_cause = analysis.get("root_cause", "").lower()
        severity = analysis.get("severity", "P2")

        commands: list[dict[str, str]] = []
        rollback_commands: list[dict[str, str]] = []
        safety_checks: list[str] = []
        verification_steps: list[str] = []
        pre_flight_checks: list[str] = []
        blast_radius: str = "Limited to target service pods and associated database client connections."
        situation_summary: str = f"Remediation procedure for {service} under {severity} {category} degradation."

        # -------------------------------------------------------------
        # DATABASE / CONNECTION EXHAUSTION RUNBOOK
        # -------------------------------------------------------------
        if "database" in category or "connection" in root_cause or "pool" in root_cause or "deadlock" in root_cause:
            situation_summary = f"Database connection pool exhaustion detected on {service}. Immediate connection draining and pool autoscaling required."
            blast_radius = "Direct impact on active database queries. Minor risk of aborting long-running client sessions."
            pre_flight_checks = [
                "Verify DB CPU and disk IOPS are below 85% on master RDS/Postgres instance.",
                "Confirm read replicas are healthy before redirecting analytical queries.",
                "Check current connection count via `SELECT count(*) FROM pg_stat_activity;`.",
            ]
            commands.extend([
                {
                    "title": "1. Terminate Idle / Blocking PostgreSQL Connections",
                    "type": "bash",
                    "command": (
                        f"psql $DATABASE_URL -c \"\n"
                        f"SELECT pg_terminate_backend(pid)\n"
                        f"FROM pg_stat_activity\n"
                        f"WHERE state = 'idle in transaction'\n"
                        f"  AND state_change < current_timestamp - INTERVAL '2 minutes';\""
                    ),
                    "description": "Frees exhausted pool connections immediately without restarting the database server.",
                },
                {
                    "title": "2. Scale PgBouncer Connection Pool",
                    "type": "bash",
                    "command": (
                        f"kubectl scale deployment pgbouncer-{service} --replicas=3 -n production\n"
                        f"kubectl set env deployment/{service} DB_POOL_SIZE=100 MAX_OVERFLOW=25 -n production"
                    ),
                    "description": "Expands client-side pool limits and adds PgBouncer routing capacity.",
                },
                {
                    "title": "3. Restart Unhealthy App Pods in Rolling Sequence",
                    "type": "bash",
                    "command": f"kubectl rollout restart deployment/{service} -n production",
                    "description": "Flushes stale socket descriptors and re-establishes clean database sessions.",
                },
            ])

            rollback_commands.extend([
                {
                    "title": "Revert Database Pool Configuration",
                    "type": "bash",
                    "command": (
                        f"kubectl set env deployment/{service} DB_POOL_SIZE=40 MAX_OVERFLOW=10 -n production\n"
                        f"kubectl rollout undo deployment/{service} -n production"
                    ),
                    "description": "Restores previous baseline connection pool limits.",
                }
            ])

            safety_checks.extend([
                "Verify database CPU and disk IOPS are below 80% before scaling client pool size.",
                "Ensure maximum database connections limit (max_connections) in RDS / Postgres is not exceeded.",
            ])

            verification_steps.extend([
                "Check connection pool usage drops below 60%: `SELECT count(*) FROM pg_stat_activity;`",
                f"Verify HTTP 503 error rate drops to <0.1% on service `{service}`.",
            ])

        # -------------------------------------------------------------
        # CPU / COMPUTE SATURATION RUNBOOK
        # -------------------------------------------------------------
        elif "compute" in category or "cpu" in root_cause or "saturation" in root_cause or "traffic" in root_cause:
            situation_summary = f"High CPU utilization and request queue buildup on {service}. Compute autoscaling and edge shedding required."
            blast_radius = "Cluster compute allocation increase. Potential temporary latency blip during pod startup."
            pre_flight_checks = [
                "Verify cluster nodes have spare allocatable vCPU headroom.",
                "Check that downstream databases can handle increased query concurrency.",
            ]
            commands.extend([
                {
                    "title": "1. Horizontal Pod Autoscaling (HPA) Emergency Override",
                    "type": "bash",
                    "command": (
                        f"kubectl scale deployment/{service} --replicas=12 -n production\n"
                        f"kubectl patch hpa {service}-hpa -n production --patch '{{\"spec\":{{\"minReplicas\":8}}}}'"
                    ),
                    "description": "Triples the compute replica capacity to distribute elevated traffic immediately.",
                },
                {
                    "title": "2. Enable Cloudflare Edge Rate Limiting & Shedding",
                    "type": "bash",
                    "command": (
                        f"curl -X POST \"https://api.cloudflare.com/client/v4/zones/$ZONE_ID/rate_limits\" \\\n"
                        f"     -H \"Authorization: Bearer $CF_API_TOKEN\" \\\n"
                        f"     -d '{{\"threshold\":2000,\"period\":60,\"action\":\"challenge\"}}'"
                    ),
                    "description": "Mitigates rogue scraping traffic and unblocks compute bandwidth.",
                },
                {
                    "title": "3. Tune Gunicorn / Uvicorn Concurrency Limits",
                    "type": "bash",
                    "command": f"kubectl set env deployment/{service} WEB_CONCURRENCY=8 TIMEOUT=30 -n production",
                    "description": "Increases per-pod worker processes to absorb burst latency.",
                },
            ])

            rollback_commands.extend([
                {
                    "title": "Revert Compute Scaling to Baseline HPA",
                    "type": "bash",
                    "command": (
                        f"kubectl patch hpa {service}-hpa -n production --patch '{{\"spec\":{{\"minReplicas\":3}}}}'\n"
                        f"kubectl scale deployment/{service} --replicas=3 -n production"
                    ),
                    "description": "Returns cluster compute sizing to normal steady-state cost profile.",
                }
            ])

            safety_checks.extend([
                "Ensure Kubernetes node group has sufficient cluster autoscaler headroom for new worker nodes.",
                "Verify downstream databases and caches can absorb 3x increased replica concurrency.",
            ])

            verification_steps.extend([
                f"Confirm pod CPU utilization drops under 65%: `kubectl top pods -l app={service} -n production`",
                "Verify p99 API latency normalizes below 250ms.",
            ])

        # -------------------------------------------------------------
        # MEMORY LEAK / OOM RUNBOOK
        # -------------------------------------------------------------
        elif "memory" in category or "leak" in root_cause or "oom" in root_cause:
            situation_summary = f"Memory exhaustion / memory leak progression on {service}. Garbage collection and rolling restart required."
            blast_radius = "Rolling pod termination. In-flight stateless requests might experience momentary retry."
            pre_flight_checks = [
                "Capture heap dump / profiler snapshot before restarting pods for root cause forensics.",
                "Verify readiness probes are functioning so traffic shifts gracefully during rolling restart.",
            ]
            commands.extend([
                {
                    "title": "1. Flush Application Cache & Local Temp In-Memory Buffers",
                    "type": "bash",
                    "command": (
                        f"redis-cli -u $REDIS_URL MEMORY PURGE\n"
                        f"kubectl exec -it deployment/{service} -n production -- python -c \"import gc; gc.collect()\""
                    ),
                    "description": "Reclaims unreferenced heap space and clears volatile cache keys.",
                },
                {
                    "title": "2. Patch Pod Memory Limits & Enable Fast Restart Policy",
                    "type": "bash",
                    "command": (
                        f"kubectl set resources deployment/{service} -n production \\\n"
                        f"    --limits=memory=4Gi --requests=memory=2Gi\n"
                        f"kubectl rollout restart deployment/{service} -n production"
                    ),
                    "description": "Prevents kernel OOM-killer thrashing while giving headroom for memory cleanup.",
                },
            ])

            rollback_commands.extend([
                {
                    "title": "Revert Pod Memory Allocation",
                    "type": "bash",
                    "command": f"kubectl rollout undo deployment/{service} -n production",
                    "description": "Restores original memory request limits once code patch is deployed.",
                }
            ])

            safety_checks.extend([
                "Monitor for heap dump files before pod restarts to preserve forensics for postmortem.",
            ])

            verification_steps.extend([
                f"Verify memory graph stabilizes at <60% RSS: `kubectl top pods -l app={service} -n production`",
                "Ensure zero OOMKilled events in `kubectl get events -n production --field-selector reason=OOMKilled`.",
            ])

        # -------------------------------------------------------------
        # DISK STORAGE EXHAUSTION RUNBOOK
        # -------------------------------------------------------------
        elif "disk" in category or "storage" in root_cause or "disk" in root_cause:
            situation_summary = f"Disk storage exhaustion approaching critical capacity on {service}. Log purging and volume expansion required."
            blast_radius = "Local disk volume. Log rotation may remove old rotated logs (>7 days)."
            pre_flight_checks = [
                "Identify high-disk consumer directories via `df -h` and `du -sh /var/log/*`.",
                "Confirm storage provider supports online volume expansion without pod restart.",
            ]
            commands.extend([
                {
                    "title": "1. Rotate & Purge Expired Log Files",
                    "type": "bash",
                    "command": (
                        f"kubectl exec -it deployment/{service} -n production -- "
                        f"find /var/log -type f -name '*.log' -mtime +2 -delete\n"
                        f"journalctl --vacuum-size=500M"
                    ),
                    "description": "Frees immediate disk headroom by purging old rotated container logs.",
                },
                {
                    "title": "2. Expand Persistent Volume Claim (PVC) Capacity",
                    "type": "bash",
                    "command": (
                        f"kubectl patch pvc data-{service} -n production -p '{{\"spec\":{{\"resources\":{{\"requests\":{{\"storage\":\"100Gi\"}}}}}}}}'"
                    ),
                    "description": "Expands PVC storage allocation to absorb long-term telemetry and state growth.",
                },
            ])

            rollback_commands.extend([
                {
                    "title": "Clean temporary cache mount points",
                    "type": "bash",
                    "command": f"kubectl exec -it deployment/{service} -n production -- rm -rf /tmp/scratch/*",
                    "description": "Clears scratch mount without altering persistent data volumes.",
                }
            ])

            safety_checks.extend([
                "Never delete active write-locked SQLite / Postgres WAL or data files.",
                "Ensure backup snapshot completed before truncating audit logs.",
            ])

            verification_steps.extend([
                f"Verify disk utilization drops below 70%: `df -h /data`",
                "Check filesystem read-only lock flags are cleared.",
            ])

        # -------------------------------------------------------------
        # NETWORK / LATENCY / API GATEWAY RUNBOOK
        # -------------------------------------------------------------
        else:
            situation_summary = f"Network congestion or API latency spike on {service}. Circuit breaker and route failover required."
            blast_radius = "Traffic routing and external API clients. Temporary retry responses."
            pre_flight_checks = [
                "Verify secondary multi-AZ target region is in healthy nominal state.",
                "Check latency probe between gateway and upstream services.",
            ]
            commands.extend([
                {
                    "title": "1. Enable Circuit Breakers & Upstream Fallback",
                    "type": "bash",
                    "command": (
                        f"kubectl set env deployment/{service} -n production \\\n"
                        f"    CIRCUIT_BREAKER_ENABLED=true REQUEST_TIMEOUT_MS=1500 RETRY_COUNT=1"
                    ),
                    "description": "Stops downstream timeout cascading and isolates failing external dependencies.",
                },
                {
                    "title": "2. Restart Ingress Controller & Clear Stale DNS Caches",
                    "type": "bash",
                    "command": (
                        "kubectl rollout restart daemonset/coredns -n kube-system\n"
                        "kubectl rollout restart deployment/ingress-nginx-controller -n ingress-nginx"
                    ),
                    "description": "Refreshes routing tables and flushes congested gateway keep-alive connections.",
                },
                {
                    "title": "3. Shift Traffic to Secondary Health Region / Canary",
                    "type": "bash",
                    "command": (
                        f"aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID \\\n"
                        f"    --change-batch '{{\"Changes\":[{{\"Action\":\"UPSERT\",\"ResourceRecordSet\":{{\"Name\":\"api.production.internal\",\"Type\":\"CNAME\",\"TTL\":60,\"ResourceRecords\":[{{\"Value\":\"secondary-lb.production.internal\"}}]}}}}]}}'"
                    ),
                    "description": "Reroutes traffic away from the degraded zone to healthy infrastructure.",
                },
            ])

            rollback_commands.extend([
                {
                    "title": "Revert DNS Route and Circuit Breaker Settings",
                    "type": "bash",
                    "command": (
                        f"kubectl set env deployment/{service} -n production CIRCUIT_BREAKER_ENABLED=false\n"
                        f"aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID --change-batch file://restore-primary-dns.json"
                    ),
                    "description": "Restores primary DNS routing and standard retry policies.",
                }
            ])

            safety_checks.extend([
                "Confirm secondary target region has capacity to absorb 100% of global traffic.",
            ])

            verification_steps.extend([
                "Execute health probe: `curl -s -o /dev/null -w \"%{http_code}\" https://api.production.internal/healthz`",
                "Verify ingress 5xx error rate returns to 0.00%.",
            ])

        return {
            "service": service,
            "category": category,
            "severity": severity,
            "situation_summary": situation_summary,
            "blast_radius": blast_radius,
            "pre_flight_checks": pre_flight_checks,
            "commands": commands,
            "rollback_commands": rollback_commands,
            "safety_checks": safety_checks,
            "verification_steps": verification_steps,
            "execution_warning": "⚠️ OPERATOR REVIEW REQUIRED: Commands are recommendations only. Do not execute without verifying authorization and parameters.",
        }
