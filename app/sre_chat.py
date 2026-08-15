"""
Interactive SRE Copilot Chat Session Manager.

Manages conversational state, message history, and contextual grounding
for live SRE triage dialogue.
"""

from typing import Any
from app.llm import IncidentLLM


class SRECopilot:
    """
    Manages multi-turn incident copilot sessions.
    """

    def __init__(self, llm: IncidentLLM | None = None) -> None:
        self.llm = llm or IncidentLLM()
        self.history: list[dict[str, str]] = []

    def reset(self) -> None:
        self.history.clear()

    def ask(
        self,
        user_message: str,
        incident_context: dict[str, Any] | None = None,
    ) -> str:
        if not user_message or not user_message.strip():
            return "Please provide a valid question or command."

        self.history.append({"role": "user", "content": user_message.strip()})

        try:
            reply = self.llm.chat_reply(
                messages=self.history,
                incident_context=incident_context,
            )
        except Exception as exc:
            reply = f"⚠️ Copilot failed to generate response: {type(exc).__name__}: {exc}"

        self.history.append({"role": "assistant", "content": reply})
        return reply

    def get_history(self) -> list[dict[str, str]]:
        return list(self.history)
