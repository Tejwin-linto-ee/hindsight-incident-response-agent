import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from app.memory_engine import MemoryEngine

load_dotenv()


class IncidentLLM:
    """
    Next-Generation AI Incident Reasoning & Triage Engine.
    
    Inputs:
    1. Current production incident & telemetry context
    2. Structured, multi-faceted historical memories from Hindsight
    3. Machine-learning failure prediction with Explainable AI attribution
    
    Output:
    - Structured, validated incident analysis with hypothesis evaluation,
      evidence correlation, immediate containment, and long-term prevention.
    """

    def __init__(
        self,
        model: str = "moonshotai/kimi-k2",
        timeout_seconds: float = 90.0,
        max_retries: int = 2,
        max_memories: int = 8,
        max_memory_chars: int = 4000,
    ) -> None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY was not found.\n"
                "Get a free key at https://openrouter.ai/keys\n"
                "Then add to your .env file: OPENROUTER_API_KEY=your_key_here"
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=timeout_seconds,
            max_retries=max_retries,
        )
        self.model = model
        self.max_memories = max_memories
        self.max_memory_chars = max_memory_chars

    # ========================================================
    # STRUCTURED MEMORY CONTEXT
    # ========================================================

    def _build_memory_context(
        self,
        memories: list[Any],
        query: str = "",
    ) -> str:
        if not memories:
            return "No relevant historical incidents were retrieved from Hindsight."

        # If memories are not already structured, structure them
        if memories and not isinstance(memories[0], dict):
            structured = MemoryEngine.process_and_rank_memories(
                memories,
                query=query,
                limit=self.max_memories,
            )
        else:
            structured = memories[:self.max_memories]

        formatted = []
        for index, mem in enumerate(structured, start=1):
            raw = mem.get("raw_text", str(mem))[:self.max_memory_chars]
            rel = mem.get("relevance_score", 50.0)
            tier = mem.get("tier", "Contextual")
            service = mem.get("extracted_service", "Unknown")
            res = mem.get("extracted_resolution", "N/A")

            entry = (
                f"--- [MEMORY #{index} | Relevance: {rel}% ({tier})] ---\n"
                f"Service Context: {service}\n"
                f"Historical Content:\n{raw}\n"
                f"Historical Confirmed Resolution: {res}\n"
            )
            formatted.append(entry)

        return "\n".join(formatted)

    # ========================================================
    # PREDICTION CONTEXT WITH EXPLAINABLE AI
    # ========================================================

    def _build_prediction_context(
        self,
        prediction: dict[str, Any] | None,
    ) -> str:
        if prediction is None:
            return (
                "No machine-learning failure prediction is currently available.\n"
                "Do not fabricate ML prediction values."
            )

        pred_summary = {
            "failure_risk_percent": prediction.get("failure_risk", 0),
            "predicted_failure_type": prediction.get("predicted_failure_type", "Unknown"),
            "risk_level": prediction.get("risk_level", "LOW"),
            "time_to_failure_window": prediction.get("time_to_failure", prediction.get("risk_window", "Unknown")),
            "urgency_index": prediction.get("urgency_index", 0),
            "multivariate_anomaly_score": prediction.get("anomaly_score", 0.0),
            "model_confidence_percent": prediction.get("prediction_confidence", 0),
            "top_driving_telemetry_attributions": prediction.get("feature_attributions", []),
            "preemptive_remediation_playbook": prediction.get("preemptive_remediation", []),
        }

        return (
            "A calibrated machine-learning failure prediction & Explainable AI analysis is available below:\n\n"
            "<ml_prediction_intelligence>\n"
            + json.dumps(pred_summary, indent=2)
            + "\n</ml_prediction_intelligence>"
        )

    # ========================================================
    # NORMALIZERS
    # ========================================================

    @staticmethod
    def _normalize_severity(severity: Any) -> str:
        if not severity:
            return "P3"
        val = str(severity).strip().upper()
        if "P1" in val or "CRITICAL" in val:
            return "P1"
        if "P2" in val or "HIGH" in val:
            return "P2"
        if "P3" in val or "MEDIUM" in val:
            return "P3"
        if "P4" in val or "LOW" in val:
            return "P4"
        return "P3"

    @staticmethod
    def _normalize_int(value: Any, default: int = 80) -> int:
        try:
            return max(0, min(100, int(float(value))))
        except Exception:
            return default

    # ========================================================
    # MAIN ANALYZE METHOD
    # ========================================================

    def analyze(
        self,
        incident: str,
        memories: list[Any],
        prediction: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not incident or not incident.strip():
            raise ValueError("Incident description cannot be empty.")

        memory_context = self._build_memory_context(memories, query=incident)
        prediction_context = self._build_prediction_context(prediction)

        system_prompt = (
            "You are a Staff Site Reliability Engineer and Senior Production Incident Commander. "
            "You diagnose critical production outages by synthesizing real-time telemetry, "
            "calibrated machine-learning predictions, and historical postmortems from Hindsight memory. "
            "Be rigorous, evidence-driven, concise, and structured. Always communicate uncertainty and "
            "provide immediately actionable containment steps."
        )

        user_prompt = f"""
Analyze the following production incident using the provided intelligence feeds.

============================================================
1. CURRENT INCIDENT REPORT & OBSERVATIONS
============================================================
<incident>
{incident}
</incident>

============================================================
2. HISTORICAL INCIDENT RECALL (Hindsight Memory)
============================================================
<historical_memory>
{memory_context}
</historical_memory>

============================================================
3. PREDICTIVE ML INTELLIGENCE & TELEMETRY XAI
============================================================
{prediction_context}

============================================================
REASONING PROTOCOL
============================================================
1. Synthesize the current incident symptoms with historical memories and ML telemetry attributions.
2. Cross-reference past resolutions in the historical memory: what worked before in similar incidents?
3. Clearly state the primary root cause and confidence (0-100%).
4. Categorize actions into:
   - Immediate Containment / Blast Radius Mitigation (actions within 5 minutes)
   - Short-Term Remediation (actions within 30 minutes)
   - Long-Term Architectural Hardening (preventative actions)
5. Highlight any conflicts or uncertainties in the evidence.

============================================================
REQUIRED JSON FORMAT
============================================================
Return a single JSON object with EXACTLY these fields:
{{
  "severity": "P1" | "P2" | "P3" | "P4",
  "service": "Name of the affected primary service",
  "category": "Failure category (e.g., Database, Compute, Memory, API, Network)",
  "incident_summary": "Concise summary of the production incident",
  "root_cause": "Detailed technical root cause identification",
  "root_cause_confidence": 90,
  "historical_evidence": [
    {{
      "incident": "Description or reference to past incident",
      "relevance": "How it informed this diagnosis"
    }}
  ],
  "recommended_actions": [
    "Immediate action 1",
    "Immediate action 2"
  ],
  "short_term_actions": [
    "Short term action 1",
    "Short term action 2"
  ],
  "long_term_prevention": [
    "Long term architectural hardening 1",
    "Long term architectural hardening 2"
  ],
  "reasoning": "In-depth technical reasoning synthesizing telemetry, ML prediction, and historical memory",
  "reasoning_summary": "High-level 2-sentence takeaway for engineering leadership",
  "confidence": 92,
  "uncertainty": "Explicit boundaries of what is known vs. assumptions requiring human verification",
  "failure_prediction": {json.dumps(prediction) if prediction else "null"}
}}

Return ONLY valid JSON.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=2500,
            )
        except Exception as exc:
            raise RuntimeError(f"OpenRouter API request failed: {type(exc).__name__}: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenRouter returned empty response.")

        clean_text = content.strip()
        # Strip markdown fences if present
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r"\s*```$", "", clean_text)
        
        # Try direct parse
        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError:
            # Locate the outermost JSON object bounds
            first_brace = clean_text.find("{")
            last_brace = clean_text.rfind("}")
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str = clean_text[first_brace : last_brace + 1]
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    # Clean up common JSON syntax issues like trailing commas or unescaped newlines
                    json_str_cleaned = re.sub(r",\s*([\]}])", r"\1", json_str)
                    data = json.loads(json_str_cleaned)
            else:
                raise ValueError(f"Could not parse valid JSON from model response: {content[:300]}...")

        # Normalize required fields
        data["severity"] = self._normalize_severity(data.get("severity"))
        data["service"] = str(data.get("service", "Core Services"))
        data["category"] = str(data.get("category", "General Availability"))
        data["incident_summary"] = str(data.get("incident_summary", ""))
        data["root_cause"] = str(data.get("root_cause", ""))
        data["root_cause_confidence"] = self._normalize_int(data.get("root_cause_confidence"), 85)
        data["confidence"] = self._normalize_int(data.get("confidence"), 85)
        data["reasoning"] = str(data.get("reasoning", ""))
        data["reasoning_summary"] = str(data.get("reasoning_summary", data["reasoning"][:200]))
        data["uncertainty"] = str(data.get("uncertainty", "No critical uncertainties reported."))

        for list_field in ["recommended_actions", "short_term_actions", "long_term_prevention"]:
            if not isinstance(data.get(list_field), list):
                data[list_field] = [str(data.get(list_field))] if data.get(list_field) else []

        if not isinstance(data.get("historical_evidence"), list):
            data["historical_evidence"] = []

        if data.get("failure_prediction") is None and prediction:
            data["failure_prediction"] = prediction

        return data