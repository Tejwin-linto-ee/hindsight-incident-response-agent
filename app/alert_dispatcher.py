"""
Real-Time SRE Alert Dispatcher.

Dispatches formatted incident cards and alerts to Slack, Microsoft Teams,
Discord, PagerDuty, and custom webhook endpoints.
"""

from datetime import datetime, timezone
import json
from typing import Any
import urllib.error
import urllib.request


class AlertDispatcher:
    """
    Dispatches rich webhook notifications for critical incidents.
    """

    @classmethod
    def format_slack_card(
        cls,
        analysis: dict[str, Any],
        incident_id: str = "INC-AUTO",
    ) -> dict[str, Any]:
        severity = analysis.get("severity", "P2")
        service = analysis.get("service", "Unknown Service")
        summary = analysis.get("incident_summary", "Production Outage Detected")
        root_cause = analysis.get("root_cause", "Under investigation")
        conf = analysis.get("confidence", 85)
        actions = analysis.get("recommended_actions", ["Investigate logs"])

        color = "#F43F5E" if severity in ["P1", "CRITICAL"] else "#F59E0B"

        actions_text = "\n".join([f"• `{act}`" for act in actions[:3]])

        return {
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"🚨 [{severity}] {service} Incident Alert",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "section",
                            "fields": [
                                {"type": "mrkdwn", "text": f"*Incident ID:*\n`{incident_id}`"},
                                {"type": "mrkdwn", "text": f"*Severity:*\n*{severity}*"},
                                {"type": "mrkdwn", "text": f"*Service:*\n{service}"},
                                {"type": "mrkdwn", "text": f"*Confidence:*\n{conf}%"},
                            ],
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Summary:*\n{summary}\n\n*Likely Root Cause:*\n{root_cause}",
                            },
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Recommended Containment:*\n{actions_text}",
                            },
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"🧠 Diagnosed via *Hindsight SRE Intelligence* • {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}",
                                }
                            ],
                        },
                    ],
                }
            ]
        }

    @classmethod
    def format_teams_card(
        cls,
        analysis: dict[str, Any],
        incident_id: str = "INC-AUTO",
    ) -> dict[str, Any]:
        severity = analysis.get("severity", "P2")
        service = analysis.get("service", "Unknown Service")
        summary = analysis.get("incident_summary", "Production Outage Detected")
        root_cause = analysis.get("root_cause", "Under investigation")

        return {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "F43F5E" if severity == "P1" else "F59E0B",
            "summary": f"[{severity}] {service} Incident",
            "sections": [
                {
                    "activityTitle": f"🚨 [{severity}] Production Incident: {service}",
                    "activitySubtitle": f"Incident ID: {incident_id} | Hindsight SRE Intelligence",
                    "facts": [
                        {"name": "Severity", "value": severity},
                        {"name": "Service", "value": service},
                        {"name": "Root Cause", "value": root_cause},
                    ],
                    "text": summary,
                }
            ],
        }

    @classmethod
    def dispatch(
        cls,
        webhook_url: str,
        payload: dict[str, Any],
        timeout_seconds: float = 5.0,
    ) -> dict[str, Any]:
        """
        Sends payload to the provided webhook URL via standard library urllib.
        """
        if not webhook_url or not webhook_url.strip():
            return {"success": False, "error": "Webhook URL is empty."}

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            webhook_url.strip(),
            data=data_bytes,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Hindsight-Incident-Response/2.5.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
                status_code = response.getcode()
                return {
                    "success": 200 <= status_code < 300,
                    "status_code": status_code,
                    "message": "Alert dispatched successfully.",
                }
        except urllib.error.HTTPError as http_err:
            return {
                "success": False,
                "status_code": http_err.code,
                "error": f"HTTP Error {http_err.code}: {http_err.reason}",
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Dispatch failed: {type(exc).__name__}: {exc}",
            }
