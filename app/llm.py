import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class IncidentLLM:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY was not found in .env")

        self.client = Groq(api_key=api_key)

    def analyze(self, incident: str, memories: list[str]) -> str:
        memory_context = "\n\n".join(
            f"Historical Incident {i + 1}:\n{memory}"
            for i, memory in enumerate(memories)
        )

        prompt = f"""
You are an incident response engineer.

Analyze the following production incident using the historical incidents
retrieved from the organization's memory.

NEW INCIDENT:
{incident}

HISTORICAL INCIDENTS:
{memory_context}

Provide your response using exactly these sections:

1. INCIDENT ASSESSMENT
2. LIKELY ROOT CAUSE
3. RECOMMENDED ACTION
4. WHY THIS ACTION
5. CONFIDENCE
6. RELEVANT HISTORICAL INCIDENTS

Important:
- Base your reasoning on the historical incidents when relevant.
- Do not claim certainty when the evidence is insufficient.
- Prefer previously successful resolutions when the circumstances are similar.
- Clearly distinguish historical evidence from your own inference.
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a careful production incident response engineer.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content