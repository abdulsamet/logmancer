import asyncio
import logging
from enum import Enum
from importlib import import_module
from typing import Any, Dict, List

logger = logging.getLogger("logmancer.notifications")


class Backends(Enum):
    EMAIL = "logmancer.notifications.email.EmailBackend"
    TELEGRAM = "logmancer.notifications.telegram.TelegramBackend"
    SLACK = "logmancer.notifications.slack.SlackBackend"


class NotificationManager:
    """Manages all notification backends"""

    def __init__(self):
        self.backends: List = []
        self._load_backends()

    def _load_backends(self):
        """Load notification backends from settings"""
        from logmancer.conf import get_bool, get_dict

        enabled = get_bool("ENABLE_NOTIFICATIONS")

        if not enabled:
            logger.info("Notifications disabled")
            return

        notifications_config = get_dict("NOTIFICATIONS")

        for backend_name, config in notifications_config.items():
            self._load_single_backend(backend_name, config)

    def _load_single_backend(self, backend_name: str, config: Dict[str, Any]):
        """Load a single notification backend"""

        if not config.get("enabled", True):
            return

        try:
            backend_enum_name = backend_name.upper()

            if not hasattr(Backends, backend_enum_name):
                return

            backend_enum = getattr(Backends, backend_enum_name)
            backend_class_path = backend_enum.value

            module_path, class_name = backend_class_path.rsplit(".", 1)
            module = import_module(module_path)
            backend_class = getattr(module, class_name)

            backend = backend_class(config)
            self.backends.append(backend)

        except (ImportError, AttributeError, ValueError) as e:
            logger.error(f"Failed to load notification backend '{backend_name}': {e}")

    async def send_notifications(self, log_entry, context: Dict = None):
        """Send notifications to all configured backends"""
        if not self.backends:
            return

        coros = [backend.send_notification(log_entry, context) for backend in self.backends]
        # Run concurrently and swallow individual errors
        results = await asyncio.gather(*coros, return_exceptions=True)
        for backend, res in zip(self.backends, results):
            if isinstance(res, Exception):
                logger.error(f"Notification failed via {backend.__class__.__name__}: {res}")

    def list_available_backends(self):
        """List all available backend types"""
        return [backend.name.lower() for backend in Backends]

    def list_loaded_backends(self):
        """List all currently loaded backends"""
        return [backend.__class__.__name__ for backend in self.backends]


# Singleton instance
notification_manager = NotificationManager()
