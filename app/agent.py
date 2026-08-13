from app.hindsight_memory import IncidentMemory
from app.llm import IncidentLLM


class IncidentResponseAgent:
    def __init__(self):
        self.memory = IncidentMemory()
        self.llm = IncidentLLM()

    def investigate(self, incident: str):
        print("\n🔎 Investigating incident...")
        print("=" * 60)
        print(incident.strip())

        # Step 1: Search organizational memory
        results = self.memory.find_similar_incidents(incident)

        print("\n🧠 Retrieved historical incidents:")
        print(f"Found {len(results)} relevant memories.")

        # Limit the context sent to the LLM
        top_results = results[:5]

        memories = []

        for result in top_results:
            memories.append(result.text)

        # Step 2: Ask the LLM to reason using historical memory
        print("\n🤖 Analyzing incident with historical context...")

        analysis = self.llm.analyze(
            incident=incident,
            memories=memories,
        )

        print("\n" + "=" * 60)
        print("🚨 INCIDENT RESPONSE ANALYSIS")
        print("=" * 60)
        print(analysis)

        return {
            "incident": incident,
            "historical_memories": memories,
            "analysis": analysis,
        }

    def close(self):
        self.memory.close()