"""
Executive Incident Postmortem & Root Cause Analysis (RCA) Exporter.

Generates standardized SRE postmortem reports ready for Jira, Confluence,
Notion, and Engineering Leadership reviews.
"""

from datetime import datetime, timezone
import json
from typing import Any


class PostmortemExporter:
    """
    Renders structured incident investigation results into a comprehensive
    SRE Postmortem / RCA document.
    """

    @classmethod
    def generate_markdown(
        cls,
        analysis: dict[str, Any],
        incident_text: str,
        telemetry: dict[str, float] | None = None,
        incident_id: str | None = None,
        author: str = "SRE Incident Commander",
    ) -> str:
        inc_id = incident_id or f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}"
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        service = analysis.get("service", "Unknown Service")
        severity = analysis.get("severity", "P2")
        category = analysis.get("category", "General")
        summary = analysis.get("incident_summary", "Production Outage")
        root_cause = analysis.get("root_cause", "Pending investigation")
        confidence = analysis.get("confidence", 85)
        root_cause_conf = analysis.get("root_cause_confidence", 85)
        uncertainty = analysis.get("uncertainty", "None reported.")
        reasoning = analysis.get("reasoning", "")

        immediate_actions = analysis.get("recommended_actions", [])
        short_term = analysis.get("short_term_actions", [])
        long_term = analysis.get("long_term_prevention", [])
        historical_evidence = analysis.get("historical_evidence", [])

        # Telemetry Markdown Table
        telemetry_rows = []
        if telemetry:
            for k, v in telemetry.items():
                telemetry_rows.append(f"| `{k}` | `{v}` |")
        telemetry_table = "\n".join(telemetry_rows) if telemetry_rows else "| Metric | Value |\n|---|---|\n| N/A | Telemetry Not Captured |"

        # Actions List
        rec_list = "\n".join([f"- [ ] {act}" for act in immediate_actions]) or "- None"
        short_list = "\n".join([f"- [ ] {act}" for act in short_term]) or "- None"
        long_list = "\n".join([f"- [ ] {act}" for act in long_term]) or "- None"

        # Historical Context
        history_list = []
        if historical_evidence:
            for item in historical_evidence:
                history_list.append(f"- **Reference:** {item.get('incident', 'N/A')}\n  - *Relevance:* {item.get('relevance', 'Informed diagnostic pattern')}")
        history_str = "\n".join(history_list) if history_list else "- No prior matching incident records were utilized."

        md = f"""# 📑 SRE Incident Postmortem & Root Cause Analysis (RCA)

| Property | Value |
| :--- | :--- |
| **Incident ID** | `{inc_id}` |
| **Date & Time** | `{date_str}` |
| **Severity Level** | **{severity}** |
| **Affected Service** | `{service}` |
| **Failure Category** | `{category}` |
| **Lead Investigator** | `{author}` |
| **Overall Confidence** | `{confidence}%` |

---

## 1. Executive Summary
{summary}

---

## 2. Technical Root Cause & Diagnostic Confidence
**Root Cause Hypothesis ({root_cause_conf}% Confidence):**
> {root_cause}

### Diagnostic Reasoning
{reasoning}

### Known Evidence Boundaries & Uncertainties
> ⚠️ **Uncertainty Note:** {uncertainty}

---

## 3. Incident Context & Symptoms
```text
{incident_text.strip()}
```

---

## 4. Telemetry & Metric Observations
| Metric | Value |
| :--- | :--- |
{telemetry_table}

---

## 5. Historical Precedents & Organizational Memory (Hindsight)
{history_str}

---

## 6. Action Items & Remediation Matrix

### 🚨 Immediate Containment (Blast Radius Mitigation)
{rec_list}

### 🛠️ Short-Term Stabilization
{short_list}

### 🛡️ Long-Term Architectural Hardening (Prevent Recurrence)
{long_list}

---

## 7. Five Whys Root Cause Decomposition
1. **Why did the outage occur?** `{summary}`
2. **Why did this system fail?** `Critical metrics exceeded operating thresholds in {category}.`
3. **Why did metrics exceed threshold?** `{root_cause}`
4. **Why was this not mitigated automatically?** `Deficiencies in circuit breaker policies or automated autoscaling limits.`
5. **Why was this vulnerability present?** `Requires implementation of permanent hardening items listed in Section 6.`

---
*Generated automatically by Hindsight Incident Intelligence Platform at {date_str}*
"""
        return md

    @classmethod
    def generate_json(
        cls,
        analysis: dict[str, Any],
        incident_text: str,
        telemetry: dict[str, float] | None = None,
        incident_id: str | None = None,
    ) -> str:
        data = {
            "postmortem_metadata": {
                "incident_id": incident_id or f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "exporter_version": "2.5.0-enterprise",
            },
            "incident_report": {
                "raw_text": incident_text,
                "telemetry": telemetry or {},
            },
            "ai_analysis": analysis,
        }
        return json.dumps(data, indent=2)
