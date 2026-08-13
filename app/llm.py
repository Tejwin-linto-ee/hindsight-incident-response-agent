import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class IncidentLLM:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY was not found in .env"
            )

        self.client = Groq(api_key=api_key)

    def analyze(
        self,
        incident: str,
        memories: list[str],
    ) -> dict:

        # ---------------------------------------------------------
        # Build historical evidence context
        # ---------------------------------------------------------

        if memories:

            memory_context = "\n\n".join(
                f"Historical Incident {i + 1}:\n{memory}"
                for i, memory in enumerate(memories)
            )

        else:

            memory_context = (
                "No relevant historical incidents were found."
            )

        # ---------------------------------------------------------
        # AI Prompt
        # ---------------------------------------------------------

        prompt = f"""
You are a senior production incident response engineer.

Your task is to analyze a new production incident using historical
organizational incidents retrieved from persistent memory.

NEW INCIDENT:
{incident}

HISTORICAL INCIDENTS:
{memory_context}

You must produce a structured incident analysis.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "severity": "P1 | P2 | P3 | P4",
    "service": "affected service or system",
    "category": "incident category",
    "incident_summary": "short summary of what is happening",
    "root_cause": "most likely root cause",
    "root_cause_confidence": 0,
    "historical_evidence": [
        {{
            "incident": "historical incident reference",
            "relevance": "why it is relevant"
        }}
    ],
    "recommended_actions": [
        "immediate action 1",
        "immediate action 2",
        "immediate action 3"
    ],
    "short_term_actions": [
        "short-term action 1",
        "short-term action 2"
    ],
    "long_term_prevention": [
        "long-term prevention 1",
        "long-term prevention 2"
    ],
    "reasoning": "explain how the evidence supports the diagnosis",
    "confidence": 0,
    "uncertainty": "state what is unknown or cannot be confirmed"
}}

Rules:

1. severity must be one of P1, P2, P3, or P4.

2. root_cause_confidence and confidence must be integers
   between 0 and 100.

3. Do not invent historical incidents.

4. Only use historical incidents provided in the
   HISTORICAL INCIDENTS section.

5. Clearly distinguish historical evidence from AI inference.

6. If historical evidence is weak or unavailable, say so.

7. Do not claim that a root cause is confirmed unless
   the provided evidence actually confirms it.

8. Prioritize actions that are safe and appropriate for
   a production incident.

9. Immediate actions should focus on stabilization
   and reducing impact.

10. Short-term actions should focus on diagnosis and
    remediation.

11. Long-term actions should focus on preventing recurrence.

12. Keep the reasoning concise but technically meaningful.

13. Return ONLY JSON.
"""

        # ---------------------------------------------------------
        # Call Groq
        # ---------------------------------------------------------

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful senior production "
                        "incident response engineer. "
                        "You prioritize evidence, safety, "
                        "and uncertainty."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0.2,

            response_format={
                "type": "json_object"
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Groq returned an empty response."
            )

        # ---------------------------------------------------------
        # Parse JSON
        # ---------------------------------------------------------

        try:

            parsed = json.loads(content)

        except json.JSONDecodeError as e:

            raise ValueError(
                "Groq returned an invalid JSON response."
            ) from e

        # ---------------------------------------------------------
        # Validate required fields
        # ---------------------------------------------------------

        required_fields = [
            "severity",
            "service",
            "category",
            "incident_summary",
            "root_cause",
            "root_cause_confidence",
            "historical_evidence",
            "recommended_actions",
            "short_term_actions",
            "long_term_prevention",
            "reasoning",
            "confidence",
            "uncertainty",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in parsed
        ]

        if missing_fields:

            raise ValueError(
                f"AI response is missing fields: "
                f"{missing_fields}"
            )

        # ---------------------------------------------------------
        # Validate severity
        # ---------------------------------------------------------

        if parsed["severity"] not in [
            "P1",
            "P2",
            "P3",
            "P4",
        ]:

            raise ValueError(
                "AI returned an invalid severity."
            )

        # ---------------------------------------------------------
        # Validate confidence values
        # ---------------------------------------------------------

        for field in [
            "confidence",
            "root_cause_confidence",
        ]:

            value = parsed[field]

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or not 0 <= value <= 100
            ):

                raise ValueError(
                    f"{field} must be an integer "
                    "between 0 and 100."
                )

        # ---------------------------------------------------------
        # Validate list fields
        # ---------------------------------------------------------

        list_fields = [
            "historical_evidence",
            "recommended_actions",
            "short_term_actions",
            "long_term_prevention",
        ]

        for field in list_fields:

            if not isinstance(parsed[field], list):

                raise ValueError(
                    f"{field} must be a list."
                )

        # ---------------------------------------------------------
        # Return structured Python dictionary
        # ---------------------------------------------------------

        return parsed