import os

from dotenv import load_dotenv
from hindsight_client import Hindsight


def test_hindsight_memory():
    load_dotenv()

    client = Hindsight(
        base_url=os.getenv("HINDSIGHT_BASE_URL"),
        api_key=os.getenv("HINDSIGHT_API_KEY"),
    )

    bank_id = os.getenv("HINDSIGHT_BANK_ID")

    try:
        assert bank_id is not None
        assert os.getenv("HINDSIGHT_BASE_URL") is not None
        assert os.getenv("HINDSIGHT_API_KEY") is not None

        test_memory = (
            "TEST INCIDENT: Payment API returned HTTP 503 because "
            "the database connection pool was exhausted. "
            "Increasing the connection pool from 50 to 100 "
            "successfully resolved the incident."
        )

        # Store memory
        result = client.retain(
            bank_id=bank_id,
            content=test_memory,
            context="Incident response automated test",
        )

        assert result is not None

        # Recall memory
        results = client.recall(
            bank_id=bank_id,
            query="Payment API HTTP 503 database connection pool exhausted",
        )

        # Verify that Hindsight actually returned something
        assert results is not None
        assert len(results) > 0

        # Verify the returned context contains relevant information
        recalled_text = str(results).lower()

        assert "payment" in recalled_text or "503" in recalled_text
        assert "database" in recalled_text or "connection" in recalled_text

    finally:
        client.close()