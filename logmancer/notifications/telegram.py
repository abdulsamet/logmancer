import asyncio
import logging
from typing import Any, Dict, Optional

import requests

from logmancer.notifications.base import NotificationBackend

logger = logging.getLogger("logmancer.notifications")


class TelegramBackend(NotificationBackend):
    """Telegram notification backend using requests"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bot_token = config.get("bot_token")
        self.chat_id = config.get("chat_id")
        self.timeout = config.get("timeout", 10)

        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram backend requires 'bot_token' and 'chat_id'")

    async def send_notification(self, log_entry, context: Optional[Dict] = None):
        """Send notification via Telegram (synchronous)"""
        if not self.should_send(log_entry):
            logger.debug(f"Skipping notification for level {log_entry.level}")
            return

        message = self.format_message(log_entry, context)

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        def _send():
            return requests.post(url, json=payload, timeout=self.timeout)

        try:
            await asyncio.to_thread(_send)
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram notification failed: {e}")
        except Exception as e:
            logger.error(f"Telegram notification error: {e}")

    def format_message(self, log_entry, context: Optional[Dict] = None) -> str:
        """Format message for Telegram"""
        emoji = self.get_level_emoji(log_entry)

        message = f"{emoji} <b>{log_entry.level}</b>\n"
        message += f"<b>Message:</b> {log_entry.message}\n"

        if log_entry.path:
            message += f"<b>Path:</b> {log_entry.path}\n"

        if log_entry.method:
            message += f"<b>Method:</b> {log_entry.method}\n"

        if log_entry.user:
            message += f"<b>User:</b> {log_entry.user}\n"

        message += f"<b>Time:</b> {log_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"

        if log_entry.source:
            message += f"<b>Source:</b> {log_entry.source}\n"

        return message[:4000]  # Telegram message limit

    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
