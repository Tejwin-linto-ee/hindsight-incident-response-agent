"""
Automated Dependency Impact & Topology Graph Engine.
Constructs service topology, models blast radius cascades, and estimates
upstream/downstream impacted microservices during outages.
"""

from typing import Any, Dict, List, Set


class ServiceTopologyEngine:
    """
    Enterprise microservice dependency graph & blast radius analyzer.
    """

    # Microservice Dependency Graph
    SERVICE_GRAPH: Dict[str, Dict[str, Any]] = {
        "payment-api": {
            "tier": "Tier-0 (Mission Critical)",
            "owner": "Team FinOps",
            "dependencies": ["database-cluster", "redis-cache", "fraud-detection-service"],
            "dependents": ["checkout-service", "mobile-gateway", "subscription-billing"],
        },
        "database-cluster": {
            "tier": "Tier-0 (Core Infrastructure)",
            "owner": "Database Reliability Engineering",
            "dependencies": ["storage-ebs-volume"],
            "dependents": ["payment-api", "user-auth-service", "order-fulfillment", "analytics-pipeline"],
        },
        "redis-cache": {
            "tier": "Tier-1 (High Availability)",
            "owner": "Platform Core",
            "dependencies": [],
            "dependents": ["payment-api", "user-auth-service", "recommendation-service"],
        },
        "user-auth-service": {
            "tier": "Tier-0 (Identity)",
            "owner": "SecOps & IAM",
            "dependencies": ["database-cluster", "redis-cache"],
            "dependents": ["mobile-gateway", "web-portal", "checkout-service", "admin-console"],
        },
        "checkout-service": {
            "tier": "Tier-0 (Revenue Impacting)",
            "owner": "Team Checkout",
            "dependencies": ["payment-api", "user-auth-service", "inventory-service"],
            "dependents": ["web-portal", "mobile-gateway"],
        },
        "fraud-detection-service": {
            "tier": "Tier-1 (Risk)",
            "owner": "ML Ops & Risk",
            "dependencies": ["redis-cache"],
            "dependents": ["payment-api"],
        },
        "inventory-service": {
            "tier": "Tier-1 (Core Commerce)",
            "owner": "Team Supply",
            "dependencies": ["database-cluster"],
            "dependents": ["checkout-service"],
        },
    }

    @classmethod
    def calculate_blast_radius(cls, root_service: str) -> Dict[str, Any]:
        """
        Calculates downstream blast radius cascade and financial risk estimation.
        """
        service_key = root_service.lower().strip()
        if service_key not in cls.SERVICE_GRAPH:
            # Fallback to general payment-api if unknown
            service_key = "payment-api"

        root_info = cls.SERVICE_GRAPH[service_key]
        
        # Traverse downstream dependents BFS
        visited: Set[str] = set()
        queue: List[str] = list(root_info.get("dependents", []))
        
        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.add(current)
                if current in cls.SERVICE_GRAPH:
                    queue.extend(cls.SERVICE_GRAPH[current].get("dependents", []))

        impacted_services = list(visited)
        
        # Financial impact estimation
        revenue_risk_tier = "EXTREME" if "checkout-service" in impacted_services or service_key == "payment-api" else "MODERATE"
        estimated_downtime_cost_per_min = 4500 if revenue_risk_tier == "EXTREME" else 850

        return {
            "root_service": service_key,
            "root_tier": root_info.get("tier"),
            "owner_team": root_info.get("owner"),
            "direct_dependencies": root_info.get("dependencies", []),
            "direct_dependents": root_info.get("dependents", []),
            "total_downstream_blast_radius": impacted_services,
            "blast_radius_count": len(impacted_services) + 1,
            "revenue_risk_tier": revenue_risk_tier,
            "estimated_cost_per_minute_usd": estimated_downtime_cost_per_min,
        }
