from app.llm import IncidentLLM


incident = """
The Payment API is returning HTTP 503 errors.
Payment requests are failing.
Database connection pool utilization has reached 100%.
"""

memories = [
    """
Payment API previously returned HTTP 503 errors because the database
connection pool was exhausted. Increasing the connection pool from
50 to 100 successfully resolved the incident.
"""
]

llm = IncidentLLM()

print("Sending incident to Groq...\n")

answer = llm.analyze(incident, memories)

print("========== AI INCIDENT ANALYSIS ==========\n")
print(answer)