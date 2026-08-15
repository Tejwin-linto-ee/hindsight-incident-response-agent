import os
from typing import Any

from dotenv import load_dotenv
from hindsight_client import Hindsight

from app.memory_engine import MemoryEngine

load_dotenv()


class IncidentMemory:
    """
    Enterprise Incident Memory client connecting to Hindsight vector bank
    with query expansion, multi-vector recall, and relevance ranking.
    """

    def __init__(self):
        self.bank_id = os.getenv("HINDSIGHT_BANK_ID")
        base_url = os.getenv("HINDSIGHT_BASE_URL")
        api_key = os.getenv("HINDSIGHT_API_KEY")

        if not self.bank_id:
            raise ValueError("HINDSIGHT_BANK_ID was not found in .env")

        if not base_url:
            raise ValueError("HINDSIGHT_BASE_URL was not found in .env")

        if not api_key:
            raise ValueError("HINDSIGHT_API_KEY was not found in .env")

        self.client = Hindsight(
            base_url=base_url,
            api_key=api_key,
        )

    def remember_incident(
        self,
        incident: str,
        context: str = "Production incident and resolution history",
    ):
        """
        Retain an incident memory in the Hindsight knowledge bank.
        """
        return self.client.retain(
            bank_id=self.bank_id,
            content=incident,
            context=context,
        )

    def find_similar_incidents(
        self,
        query: str,
        telemetry: dict[str, Any] | None = None,
        top_k: int = 5,
    ) -> list[Any]:
        """
        Multi-angle recall using query expansion and deduplication.
        """
        queries = MemoryEngine.expand_query(query, telemetry=telemetry)
        all_results = []
        seen_texts = set()

        for q in queries:
            try:
                results = self.client.recall(
                    bank_id=self.bank_id,
                    query=q,
                )
                if results:
                    for r in results:
                        text = getattr(r, "text", "") or getattr(r, "content", "") or str(r)
                        if text not in seen_texts:
                            seen_texts.add(text)
                            all_results.append(r)
            except Exception as recall_err:
                print(f"[HINDSIGHT RECALL WARNING] Query '{q[:40]}...': {recall_err}")

        # If multi-query didn't yield items, fallback to primary query
        if not all_results:
            try:
                fallback_results = self.client.recall(
                    bank_id=self.bank_id,
                    query=query,
                )
                if fallback_results:
                    return fallback_results
            except Exception:
                pass

        return all_results[:top_k * 2]

    def close(self):
        try:
            self.client.close()
        except Exception as e:
            print(f"[HINDSIGHT CLEANUP ERROR] {type(e).__name__}: {e}")