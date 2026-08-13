from app.agent import IncidentResponseAgent


new_incident = """
The Payment API is returning HTTP 503 errors.
Payment requests are failing and database connections are timing out.
Database connection pool utilization has reached 100%.
The service is experiencing high request latency.
"""

agent = IncidentResponseAgent()

try:
    results = agent.investigate(new_incident)

    print("\n========================================")
    print("INCIDENT MEMORY TEST COMPLETE")
    print("========================================")

    if results:
        print(f"\nFound {len(results)} relevant memories.")
    else:
        print("\nNo relevant memories found.")

finally:
    agent.close()