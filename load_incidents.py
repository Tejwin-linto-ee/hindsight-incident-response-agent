import json

from app.hindsight_memory import IncidentMemory


def load_incidents():
    with open("data/incidents.json", "r", encoding="utf-8") as file:
        incidents = json.load(file)

    memory = IncidentMemory()

    try:
        for incident in incidents:
            incident_text = f"""
Incident ID: {incident['incident_id']}
Service: {incident['service']}
Severity: {incident['severity']}
Error: {incident['error']}

Symptoms:
{', '.join(incident['symptoms'])}

Root Cause:
{incident['root_cause']}

Resolution:
{incident['resolution']}

Outcome:
{incident['outcome']}
"""

            print(f"Storing {incident['incident_id']}...")

            result = memory.remember_incident(incident_text)

            if result.success:
                print(f"✓ {incident['incident_id']} stored successfully")
            else:
                print(f"✗ Failed to store {incident['incident_id']}")

    finally:
        memory.close()


if __name__ == "__main__":
    load_incidents()