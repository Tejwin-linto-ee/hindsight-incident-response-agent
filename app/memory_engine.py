import re
from typing import Any


class MemoryEngine:
    """
    Advanced Multi-Tier Semantic Memory & Knowledge Retrieval Engine.
    
    Provides:
    - Contextual query expansion (extracting service, symptoms, error classes)
    - Hybrid keyword + semantic relevance scoring (0-100%)
    - Memory structuring, tiering (High / Moderate / Contextual)
    - Actionable resolution extraction from past incident postmortems
    """

    SERVICE_PATTERNS = [
        r"(payment[-_ ]?api|payments?)",
        r"(auth[-_ ]?service|auth(?:entication)?)",
        r"(user[-_ ]?service|users?)",
        r"(order[-_ ]?service|orders?)",
        r"(database|db|postgres|mysql|redis|mongodb)",
        r"(gateway|api[-_ ]?gateway|ingress|proxy)",
        r"(search[-_ ]?service|elasticsearch)",
        r"(notification[-_ ]?service|queue|worker)",
    ]

    SYMPTOM_PATTERNS = [
        r"(5\d{2}|503|500|502|504|timeout|timed?\s*out|connection\s*timeout)",
        r"(latency|slow\s*response|high\s*latency|p99)",
        r"(cpu\s*(?:saturation|spike|100%|>90%|high))",
        r"(memory\s*(?:exhaustion|leak|oom|out\s*of\s*memory))",
        r"(pool\s*(?:exhaustion|exhausted|full|100%))",
        r"(disk\s*(?:full|exhaustion|no\s*space))",
        r"(network\s*(?:congestion|partition|packet\s*loss|drop))",
        r"(error\s*rate|failure\s*rate)",
        r"(queue\s*(?:depth|backlog|overflow))",
    ]

    @classmethod
    def expand_query(cls, incident_text: str, telemetry: dict[str, Any] | None = None) -> list[str]:
        """
        Generate multi-angle search queries to maximize recall from vector & semantic memory.
        """
        queries = [incident_text.strip()]
        
        # Extract service keywords
        detected_services = []
        for pat in cls.SERVICE_PATTERNS:
            match = re.search(pat, incident_text, re.IGNORECASE)
            if match:
                detected_services.append(match.group(1))

        # Extract symptom keywords
        detected_symptoms = []
        for pat in cls.SYMPTOM_PATTERNS:
            match = re.search(pat, incident_text, re.IGNORECASE)
            if match:
                detected_symptoms.append(match.group(1))

        if detected_services and detected_symptoms:
            queries.append(f"{' '.join(detected_services)} {' '.join(detected_symptoms)} root cause resolution")

        if telemetry:
            telemetry_symptoms = []
            if telemetry.get("db_pool_usage", 0) > 80 or telemetry.get("db_connections", 0) > 80:
                telemetry_symptoms.append("database connection pool exhaustion")
            if telemetry.get("cpu_percent", 0) > 85:
                telemetry_symptoms.append("high cpu saturation spike")
            if telemetry.get("memory_percent", 0) > 85:
                telemetry_symptoms.append("memory exhaustion leak OOM")
            if telemetry.get("disk_percent", 0) > 85:
                telemetry_symptoms.append("disk storage exhaustion full")
            if telemetry.get("network_latency_ms", 0) > 200:
                telemetry_symptoms.append("network latency congestion packet loss")
            if telemetry.get("api_latency_ms", 0) > 800 or telemetry.get("error_rate", 0) > 5:
                telemetry_symptoms.append("api degradation 503 error rate spike")
            
            if telemetry_symptoms:
                queries.append(" ".join(telemetry_symptoms) + " resolution")

        return queries

    @classmethod
    def calculate_relevance_score(cls, memory_text: str, query_text: str) -> float:
        """
        Calculate a composite semantic & lexical relevance score between 0 and 100.
        """
        if not memory_text or not query_text:
            return 0.0

        query_tokens = set(re.findall(r"\w+", query_text.lower()))
        memory_tokens = set(re.findall(r"\w+", memory_text.lower()))

        if not query_tokens:
            return 0.0

        # Jaccard / Overlap
        overlap = query_tokens.intersection(memory_tokens)
        keyword_overlap_ratio = len(overlap) / len(query_tokens)

        # Key technical terms weight boost
        boost_terms = {
            "database", "connection", "pool", "exhaustion", "latency", "503", "500",
            "cpu", "saturation", "memory", "leak", "oom", "disk", "network", "queue",
            "resolution", "resolved", "restarted", "scaled", "index", "failover"
        }
        query_boost_matches = query_tokens.intersection(boost_terms)
        memory_boost_matches = memory_tokens.intersection(boost_terms)
        boost_overlap = query_boost_matches.intersection(memory_boost_matches)

        boost_score = len(boost_overlap) / (len(query_boost_matches) + 1e-5) if query_boost_matches else 0.5

        # Weighted composite score
        score = (keyword_overlap_ratio * 55.0) + (boost_score * 45.0)
        return min(100.0, max(15.0, round(score, 1)))

    @classmethod
    def structure_memory(cls, memory_text: str, query_text: str) -> dict[str, Any]:
        """
        Extract structured metadata from unstructured/semi-structured memory text.
        """
        relevance_score = cls.calculate_relevance_score(memory_text, query_text)

        if relevance_score >= 70:
            tier = "High Relevance"
            tier_badge = "HIGH"
        elif relevance_score >= 40:
            tier = "Moderate Relevance"
            tier_badge = "MODERATE"
        else:
            tier = "Contextual Background"
            tier_badge = "LOW"

        # Attempt to extract service, root cause, and resolution
        service = "Unknown Service"
        root_cause = "Not explicitly stated"
        resolution = "No resolution logged"

        service_match = re.search(r"Service:\s*([^\n\r]+)", memory_text, re.IGNORECASE)
        if service_match:
            service = service_match.group(1).strip()

        rc_match = re.search(r"(?:Root Cause|AI Suggested Root Cause):\s*([^\n\r]+)", memory_text, re.IGNORECASE)
        if rc_match:
            root_cause = rc_match.group(1).strip()

        res_match = re.search(r"(?:Resolution|ACTUAL RESOLUTION):\s*([^\n\r]+(?:\n[^\n\r]+){0,2})", memory_text, re.IGNORECASE)
        if res_match:
            resolution = res_match.group(1).strip()

        return {
            "raw_text": memory_text,
            "relevance_score": relevance_score,
            "tier": tier,
            "tier_badge": tier_badge,
            "extracted_service": service,
            "extracted_root_cause": root_cause,
            "extracted_resolution": resolution,
        }

    @classmethod
    def process_and_rank_memories(
        cls,
        raw_memories: list[Any],
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Process, deduplicate, structure, and rank memories by relevance score.
        """
        structured = []
        seen_texts = set()

        for item in raw_memories:
            text = ""
            if hasattr(item, "text") and item.text:
                text = item.text
            elif hasattr(item, "content") and item.content:
                text = item.content
            elif isinstance(item, str):
                text = item
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or str(item)

            text = text.strip()
            if not text or text in seen_texts:
                continue
            seen_texts.add(text)

            structured.append(cls.structure_memory(text, query))

        # Sort descending by relevance score
        structured.sort(key=lambda m: m["relevance_score"], reverse=True)
        return structured[:limit]
