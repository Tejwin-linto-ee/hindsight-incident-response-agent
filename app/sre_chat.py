"""
Interactive SRE Copilot Chat Session Manager.

Manages conversational state, message history, and contextual grounding
for live SRE triage dialogue with rich multi-system context.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from app.llm import IncidentLLM


class SRECopilot:
    """
    Supercharged SRE Copilot with multi-mode intelligence, telemetry context injection,
    and automated operational action parsing.
    """

    MAX_HISTORY: int = 20

    def __init__(self, llm: Optional[IncidentLLM] = None) -> None:
        self.llm = llm or IncidentLLM()
        self.history: List[Dict[str, str]] = []

    def reset(self) -> None:
        self.history.clear()

    def ask(
        self,
        user_message: str,
        incident_context: Optional[Dict[str, Any]] = None,
        live_telemetry: Optional[Dict[str, Any]] = None,
        slo_status: Optional[Dict[str, Any]] = None,
        topology_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not user_message or not user_message.strip():
            return "Please provide a valid question or command."

        clean_message = user_message.strip()
        self.history.append({"role": "user", "content": clean_message})

        # Keep context bounded to prevent unbounded token growth
        if len(self.history) > self.MAX_HISTORY:
            self.history = self.history[-self.MAX_HISTORY:]

        # Build enriched system prompt grounding
        system_context: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if incident_context:
            system_context["active_incident"] = incident_context
        if live_telemetry:
            system_context["live_telemetry"] = live_telemetry
        if slo_status:
            system_context["slo_budget"] = slo_status
        if topology_context:
            system_context["blast_radius"] = topology_context

        try:
            reply = self.llm.chat_reply(
                messages=self.history,
                incident_context=system_context,
            )
        except Exception as exc:
            reply = f"⚠️ **Copilot Diagnostic Engine Notice:** {type(exc).__name__}: {exc}"

        self.history.append({"role": "assistant", "content": reply})
        return reply

    def get_history(self) -> List[Dict[str, str]]:
        return list(self.history)

