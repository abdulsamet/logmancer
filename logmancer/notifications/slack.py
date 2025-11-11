import asyncio
import logging
from typing import Any, Dict, Optional

import requests

from logmancer.notifications.base import NotificationBackend

logger = logging.getLogger("logmancer.notifications")


class SlackBackend(NotificationBackend):
    """Slack notification backend"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url")
        self.timeout = config.get("timeout", 10)

        if not self.webhook_url:
            raise ValueError("Slack backend requires 'webhook_url'")

    async def send_notification(self, log_entry, context: Optional[Dict] = None):
        """Send notification via Slack"""
        if not self.should_send(log_entry):
            return

        payload = self.format_message(log_entry, context)

        def _send():
            return requests.post(self.webhook_url, json=payload, timeout=self.timeout)

        try:
            response = await asyncio.to_thread(_send)
            if response.status_code != 200:
                logger.error(f"Slack notification failed with status {response.status_code}")
        except Exception as e:
            logger.error(f"Slack notification error: {e}")

    def format_message(self, log_entry, context: Optional[Dict] = None) -> Dict:
        """Format message for Slack"""
        color = self.get_slack_color(log_entry)

        attachment = {
            "color": color,
            "title": f"{log_entry.level}: {log_entry.message[:100]}",
            "fields": [
                {"title": "Level", "value": log_entry.level, "short": True},
                {"title": "Source", "value": log_entry.source or "Unknown", "short": True},
            ],
            "ts": log_entry.timestamp.timestamp(),
        }

        if log_entry.path:
            attachment["fields"].append({"title": "Path", "value": log_entry.path, "short": True})

        if log_entry.user:
            attachment["fields"].append(
                {"title": "User", "value": str(log_entry.user), "short": True}
            )

        return {"text": f"Logmancer Alert: {log_entry.level}", "attachments": [attachment]}
