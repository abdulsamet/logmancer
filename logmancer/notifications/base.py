import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from logmancer.levels import LogLevel

logger = logging.getLogger("logmancer.notifications")


class NotificationBackend(ABC):
    """Base class for all notification backends"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.logger = logger

    @abstractmethod
    async def send_notification(self, log_entry, context: Optional[Dict] = None):
        """Send notification for a log entry"""
        raise NotImplementedError

    @abstractmethod
    def format_message(self, log_entry, context: Optional[Dict] = None) -> Any:
        """Format log entry into notification message"""
        raise NotImplementedError

    def should_send(self, log_entry) -> bool:
        """Check if notification should be sent for this log entry"""
        if not self.enabled:
            return False

        min_level_name = self.config.get("min_level", "ERROR")

        if not LogLevel.should_log(log_entry.level, min_level_name):
            return False

        # Check source filter
        allowed_sources = self.config.get("sources", [])
        if allowed_sources and log_entry.source not in allowed_sources:
            self.logger.debug(
                f"Source {log_entry.source} not in allowed sources: {allowed_sources}"
            )
            return False

        # Check path filter
        excluded_paths = self.config.get("excluded_paths", [])
        if log_entry.path:
            for excluded_path in excluded_paths:
                if log_entry.path.startswith(excluded_path):
                    self.logger.debug(
                        f"Path {log_entry.path} matches excluded path: {excluded_path}"
                    )
                    return False

        return True

    def get_level_emoji(self, log_entry) -> str:
        try:
            return LogLevel.from_name(log_entry.level).emoji
        except ValueError:
            return "📝"

    def get_level_color(self, log_entry) -> str:
        try:
            return LogLevel.from_name(log_entry.level).color
        except ValueError:
            return "#808080"

    def get_slack_color(self, log_entry) -> str:
        try:
            return LogLevel.from_name(log_entry.level).slack_color
        except ValueError:
            return "danger"

    def test_connection(self) -> bool:
        return True
