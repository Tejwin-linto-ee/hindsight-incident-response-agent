import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)

BANK_ID = os.getenv("HINDSIGHT_BANK_ID")

print("Testing Hindsight...")

# Store a test memory
result = client.retain(
    bank_id=BANK_ID,
    content=(
        "TEST INCIDENT: Payment API returned HTTP 503 because "
        "the database connection pool was exhausted. "
        "Increasing the connection pool from 50 to 100 successfully "
        "resolved the incident."
    ),
    context="Incident response test",
)

print("Memory stored successfully!")
print(result)

# Recall the memory
results = client.recall(
    bank_id=BANK_ID,
    query="What happened when the Payment API returned HTTP 503?"
)

print("\nMemory recalled:")
print(results)