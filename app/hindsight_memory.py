import os

from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()


class IncidentMemory:

    def __init__(self):

        self.bank_id = os.getenv(
            "HINDSIGHT_BANK_ID"
        )

        base_url = os.getenv(
            "HINDSIGHT_BASE_URL"
        )

        api_key = os.getenv(
            "HINDSIGHT_API_KEY"
        )

        if not self.bank_id:
            raise ValueError(
                "HINDSIGHT_BANK_ID was not found in .env"
            )

        if not base_url:
            raise ValueError(
                "HINDSIGHT_BASE_URL was not found in .env"
            )

        if not api_key:
            raise ValueError(
                "HINDSIGHT_API_KEY was not found in .env"
            )

        self.client = Hindsight(
            base_url=base_url,
            api_key=api_key,
        )

    def remember_incident(
        self,
        incident: str,
    ):

        return self.client.retain(
            bank_id=self.bank_id,
            content=incident,
            context=(
                "Production incident and "
                "resolution history"
            ),
        )

    def find_similar_incidents(
        self,
        query: str,
    ):

        return self.client.recall(
            bank_id=self.bank_id,
            query=query,
        )

    def close(self):

        try:

            self.client.close()

        except Exception as e:

            print(
                f"[HINDSIGHT CLEANUP ERROR] "
                f"{type(e).__name__}: {e}"
            )