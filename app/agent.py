from app.hindsight_memory import IncidentMemory


class IncidentResponseAgent:
    def __init__(self):
        self.memory = IncidentMemory()

    def investigate(self, incident: str):
        print("\n🔎 Investigating incident...")
        print(f"Incident: {incident}")

        results = self.memory.find_similar_incidents(incident)

        print("\n🧠 Hindsight Memory Results:")

        if not results:
            print("No similar incidents found.")
            return []

        for result in results:
            print("\n--- Similar Incident ---")
            print(result.text)

        return results

    def close(self):
        self.memory.close()