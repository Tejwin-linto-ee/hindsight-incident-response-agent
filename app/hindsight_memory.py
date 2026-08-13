import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()


class IncidentMemory:
    def __init__(self):
        self.bank_id = os.getenv("HINDSIGHT_BANK_ID")

        self.client = Hindsight(
            base_url=os.getenv("HINDSIGHT_BASE_URL"),
            api_key=os.getenv("HINDSIGHT_API_KEY"),
        )

    def remember_incident(self, incident: str):
        """Store a resolved incident in Hindsight."""
        return self.client.retain(
            bank_id=self.bank_id,
            content=incident,
            context="Production incident and resolution history",
        )

    def find_similar_incidents(self, query: str):
        """Retrieve relevant incidents from Hindsight."""
        return self.client.recall(
            bank_id=self.bank_id,
            query=query,
        )

    def close(self):
        """Close the Hindsight client connection."""
        self.client.close()