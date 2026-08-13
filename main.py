import streamlit as st

from app.agent import IncidentResponseAgent


st.set_page_config(
    page_title="Hindsight Incident Response Agent",
    page_icon="🚨",
    layout="wide",
)

st.title("🚨 Hindsight Incident Response Agent")
st.caption("AI-powered incident response using persistent organizational memory")

st.markdown(
    """
    Enter a production incident below. The agent will search historical
    incidents stored in Hindsight and use that experience to generate
    an incident response recommendation.
    """
)

incident = st.text_area(
    "Describe the incident",
    height=220,
    placeholder=(
        "Example:\n"
        "Payment API is returning HTTP 503 errors. "
        "Database connection pool utilization is at 100%..."
    ),
)

if st.button("🔎 Investigate Incident", type="primary"):
    if not incident.strip():
        st.warning("Please describe the incident first.")
    else:
        with st.spinner("Investigating incident using organizational memory..."):
            agent = IncidentResponseAgent()

            try:
                result = agent.investigate(incident)

                st.divider()

                st.subheader("🚨 AI Incident Response")

                st.markdown(result["analysis"])

                st.divider()

                st.subheader("🧠 Historical Evidence")

                memories = result["historical_memories"]

                if memories:
                    for i, memory in enumerate(memories, 1):
                        with st.expander(f"Historical Memory {i}"):
                            st.write(memory)
                else:
                    st.info("No relevant historical incidents were found.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

            finally:
                agent.close()