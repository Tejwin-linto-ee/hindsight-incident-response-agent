from app.agent import IncidentResponseAgent


new_incident = """
The Payment API is returning HTTP 503 errors.
Payment requests are failing and database connections are timing out.
Database connection pool utilization has reached 100%.
The service is experiencing high request latency.
"""

agent = IncidentResponseAgent()

try:
    result = agent.investigate(new_incident)

    print("\n========================================")
    print("INCIDENT MEMORY TEST COMPLETE")
    print("========================================")

    memories = result["historical_memories"]

    print(f"\nHistorical memories used by the AI: {len(memories)}")

    if memories:
        print("✓ Hindsight successfully provided historical context.")
        print("✓ Groq successfully analyzed the incident.")
        print("✓ End-to-end incident response completed.")
    else:
        print("⚠ No historical memories were available.")

finally:
    agent.close()