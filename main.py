import streamlit as st

from app.agent import IncidentResponseAgent


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hindsight Incident Command Center",
    page_icon="🚨",
    layout="wide",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
"""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
}

.hero-subtitle {
    font-size: 1.1rem;
    opacity: 0.7;
}

.metric-card {
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 14px;
    padding: 1rem;
    min-height: 110px;
    background: rgba(128,128,128,0.05);
}

.metric-label {
    font-size: 0.8rem;
    opacity: 0.65;
    text-transform: uppercase;
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 750;
    margin-top: 0.4rem;
}

.section-title {
    font-size: 1.45rem;
    font-weight: 750;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}

.reasoning {
    border-left: 4px solid #4da3ff;
    padding: 1rem;
    border-radius: 8px;
    background: rgba(77,163,255,0.08);
}

</style>
""",
unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "last_result" not in st.session_state:

    st.session_state.last_result = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🧠 Hindsight")

    st.caption(
        "Incident Command Center"
    )

    st.divider()

    st.markdown("### Architecture")

    st.markdown(
        """
Incident

↓

Hindsight Recall

↓

Historical Evidence

↓

Groq Reasoning

↓

Human Review

↓

Confirmed Resolution

↓

Hindsight Learning
"""
    )

    st.divider()

    st.markdown("### Persistent Learning")

    st.caption(
        "Resolved incidents are stored as organizational "
        "experience and can influence future investigations."
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
"""
<div class="hero-title">
🚨 Hindsight Incident Command Center
</div>

<div class="hero-subtitle">
AI-powered incident response that learns from
organizational experience.
</div>
""",
unsafe_allow_html=True,
)


st.write(
    "Investigate production incidents using historical "
    "evidence and record confirmed resolutions for future learning."
)


# ============================================================
# NEW INCIDENT
# ============================================================

st.markdown(
    '<div class="section-title">📋 New Incident</div>',
    unsafe_allow_html=True,
)


incident = st.text_area(
    "Incident description",
    height=200,
    placeholder=(
        "Payment API is returning HTTP 503 errors.\n"
        "Database connections are timing out.\n"
        "Connection pool utilization has reached 100%."
    ),
    label_visibility="collapsed",
)


# ============================================================
# INVESTIGATE
# ============================================================

if st.button(
    "🔎 Investigate Incident",
    type="primary",
    use_container_width=True,
):

    if not incident.strip():

        st.warning(
            "Please describe the incident."
        )

        st.stop()

    if len(incident.strip()) < 20:

        st.warning(
            "Please provide more information about the incident."
        )

        st.stop()

    agent = None

    try:

        with st.spinner(
            "Searching Hindsight and analyzing incident..."
        ):

            agent = IncidentResponseAgent()

            result = agent.investigate(
                incident
            )

        st.session_state.last_result = result

        st.success(
            "Investigation completed."
        )

    except Exception as e:

        st.error(
            "Investigation failed."
        )

        st.caption(
            f"{type(e).__name__}: {e}"
        )

    finally:

        if agent is not None:

            agent.close()


# ============================================================
# DISPLAY LAST RESULT
# ============================================================

result = st.session_state.last_result


if result:

    analysis = result["analysis"]

    memories = result[
        "historical_memories"
    ]

    incident_id = result[
        "incident_id"
    ]

    # ========================================================
    # INCIDENT ID
    # ========================================================

    st.divider()

    st.caption(
        f"Incident ID: `{incident_id}`"
    )

    # ========================================================
    # METRICS
    # ========================================================

    severity = analysis.get(
        "severity",
        "UNKNOWN",
    )

    service = analysis.get(
        "service",
        "Unknown",
    )

    category = analysis.get(
        "category",
        "Unknown",
    )

    confidence = analysis.get(
        "confidence",
        0,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-label">Severity</div>
<div class="metric-value">{severity}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-label">Service</div>
<div class="metric-value">{service}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-label">Category</div>
<div class="metric-value">{category}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col4:

        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-label">Confidence</div>
<div class="metric-value">{confidence}%</div>
</div>
""",
            unsafe_allow_html=True,
        )

    # ========================================================
    # ASSESSMENT
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">📊 Incident Assessment</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Incident Summary"
        )

        st.write(
            analysis.get(
                "incident_summary",
                "Unavailable",
            )
        )

    with col2:

        st.subheader(
            "Likely Root Cause"
        )

        st.write(
            analysis.get(
                "root_cause",
                "Unknown",
            )
        )

        root_confidence = int(
            analysis.get(
                "root_cause_confidence",
                0,
            )
        )

        st.progress(
            root_confidence / 100
        )

        st.caption(
            f"Root cause confidence: "
            f"{root_confidence}%"
        )

    # ========================================================
    # REASONING
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">🧠 AI Reasoning</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="reasoning">
{analysis.get("reasoning", "Unavailable")}
</div>
""",
        unsafe_allow_html=True,
    )

    # ========================================================
    # ACTIONS
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">⚡ Immediate Actions</div>',
        unsafe_allow_html=True,
    )

    for i, action in enumerate(
        analysis.get(
            "recommended_actions",
            [],
        ),
        1,
    ):

        st.markdown(
            f"**{i}.** {action}"
        )

    st.markdown(
        '<div class="section-title">🔧 Short-Term Remediation</div>',
        unsafe_allow_html=True,
    )

    for i, action in enumerate(
        analysis.get(
            "short_term_actions",
            [],
        ),
        1,
    ):

        st.markdown(
            f"**{i}.** {action}"
        )

    st.markdown(
        '<div class="section-title">🛡️ Long-Term Prevention</div>',
        unsafe_allow_html=True,
    )

    for i, action in enumerate(
        analysis.get(
            "long_term_prevention",
            [],
        ),
        1,
    ):

        st.markdown(
            f"**{i}.** {action}"
        )

    # ========================================================
    # HISTORICAL EVIDENCE
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">🧠 Historical Evidence</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        f"{len(memories)} historical memories retrieved."
    )

    for i, memory in enumerate(
        memories,
        1,
    ):

        with st.expander(
            f"Historical Memory {i}"
        ):

            st.write(
                memory
            )

    # ========================================================
    # UNCERTAINTY
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">⚠️ Uncertainty</div>',
        unsafe_allow_html=True,
    )

    st.warning(
        analysis.get(
            "uncertainty",
            "No uncertainty reported.",
        )
    )

    # ========================================================
    # HUMAN FEEDBACK
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">👨‍💻 Human Resolution Review</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "The AI recommendation should be reviewed by an "
        "engineer. Once the incident is resolved, record "
        "what actually fixed the problem."
    )

    feedback = st.radio(
        "Was the AI recommendation helpful?",
        [
            "Helpful",
            "Not Helpful",
        ],
        horizontal=True,
        key=f"feedback_{incident_id}",
    )

    resolution = st.text_area(
        "What actually resolved the incident?",
        placeholder=(
            "Example:\n"
            "Increased the database connection pool from "
            "50 to 100 and restarted the affected service. "
            "Latency returned to normal."
        ),
        key=f"resolution_{incident_id}",
    )

    if st.button(
        "🧠 Record Resolution & Teach Hindsight",
        type="primary",
        use_container_width=True,
        key=f"learn_{incident_id}",
    ):

        if not resolution.strip():

            st.warning(
                "Please describe the actual resolution "
                "before teaching the system."
            )

        else:

            agent = None

            try:

                with st.spinner(
                    "Recording resolution and updating organizational memory..."
                ):

                    agent = IncidentResponseAgent()

                    agent.record_resolution(
                        incident_id=incident_id,
                        helpful=(
                            feedback == "Helpful"
                        ),
                        resolution=resolution,
                    )

                st.success(
                    "🧠 Resolution stored. "
                    "Hindsight has learned from this incident."
                )

            except Exception as e:

                st.error(
                    "The resolution could not be stored."
                )

                st.caption(
                    f"{type(e).__name__}: {e}"
                )

            finally:

                if agent is not None:

                    agent.close()


# ============================================================
# INCIDENT HISTORY
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">📚 Incident Learning History</div>',
    unsafe_allow_html=True,
)


history_agent = None

try:

    history_agent = IncidentResponseAgent()

    history = history_agent.get_history()

finally:

    if history_agent is not None:

        history_agent.close()


if not history:

    st.info(
        "No incidents have been recorded yet."
    )

else:

    st.caption(
        f"{len(history)} incident(s) stored locally."
    )

    for record in reversed(history):

        status = (
            "🧠 Learned"
            if record.get("learned")
            else "⏳ Awaiting resolution"
        )

        with st.expander(
            f"{status} · "
            f"{record['severity']} · "
            f"{record['service']} · "
            f"{record['incident_id'][:8]}"
        ):

            st.markdown(
                f"**Incident ID:** "
                f"`{record['incident_id']}`"
            )

            st.markdown(
                f"**Created:** "
                f"{record['created_at']}"
            )

            st.markdown(
                f"**Severity:** "
                f"{record['severity']}"
            )

            st.markdown(
                f"**Service:** "
                f"{record['service']}"
            )

            st.markdown(
                f"**Category:** "
                f"{record['category']}"
            )

            st.markdown(
                f"**Root Cause:** "
                f"{record['root_cause']}"
            )

            st.markdown(
                f"**AI Confidence:** "
                f"{record['confidence']}%"
            )

            if record.get("feedback"):

                st.markdown(
                    f"**Human Feedback:** "
                    f"{record['feedback']}"
                )

            if record.get("resolution"):

                st.markdown(
                    "**Actual Resolution:**"
                )

                st.write(
                    record["resolution"]
                )

            st.markdown(
                f"**Hindsight Learned:** "
                f"{'Yes' if record.get('learned') else 'No'}"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Hindsight Incident Command Center · "
    "AI-assisted incident response · "
    "Human review required for production actions"
)