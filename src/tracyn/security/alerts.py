import logging
import requests
import threading
from typing import Dict, Any

logger = logging.getLogger("tracyn")

class AlertDispatcher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("alerting", {})
        self.enabled = self.config.get("enabled", False)
        self.webhook_url = self.config.get("webhook_url", "")

    def _send_webhook_sync(self, payload: Dict[str, Any]):
        if not self.webhook_url or "placeholder" in self.webhook_url:
            logger.debug("Webhook URL not configured or is a placeholder. Skipping alert.")
            return

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"Successfully dispatched webhook alert (status {response.status_code})")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to dispatch webhook alert: {e}")

    def dispatch_incident_alert(self, incident_number: str, severity: str, risk_score: int):
        if not self.enabled:
            return

        color_map = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }
        icon = color_map.get(severity, "⚪")
        
        message = (
            f"{icon} **TRACYN SECURITY ALERT: {severity}**\n"
            f"**Incident ID:** `{incident_number}`\n"
            f"**Risk Score:** `{risk_score}/100`\n"
            f"Please check the TRACYN dashboard immediately for details."
        )

        # Discord uses 'content', Slack uses 'text'. Sending both maximizes compatibility.
        payload = {
            "content": message,
            "text": message
        }

        # Run in a separate thread so we don't block the file monitoring loop
        thread = threading.Thread(target=self._send_webhook_sync, args=(payload,))
        thread.daemon = True
        thread.start()
