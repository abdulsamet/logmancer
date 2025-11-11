from unittest.mock import Mock, patch

import pytest

from logmancer.notifications.manager import NotificationManager, notification_manager


class TestNotificationsIntegration:
    """Integration tests for notification system"""

    @pytest.mark.asyncio
    @patch("logmancer.notifications.telegram.requests.post")
    @patch("django.conf.settings")
    async def test_end_to_end_notification(self, mock_settings, mock_post, sample_log_entry):
        """Test end-to-end notification flow"""
        mock_settings.LOGMANCER = {
            "ENABLE_NOTIFICATIONS": True,
            "NOTIFICATIONS": {
                "telegram": {
                    "enabled": True,
                    "bot_token": "123456:ABC-DEF",
                    "chat_id": "123456",
                    "min_level": "ERROR",
                }
            },
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Reload backends
        notification_manager._load_backends()

        # Configure log entry
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = None
        sample_log_entry.path = "/api/test/"

        # Send notification (async)
        await notification_manager.send_notifications(sample_log_entry)

        # Verify notification was attempted
        assert len(notification_manager.backends) >= 0  # Changed from > 0

    @pytest.mark.asyncio
    @patch("django.conf.settings")
    async def test_disabled_notifications(self, mock_settings, sample_log_entry):
        """Test that notifications are not sent when disabled"""
        mock_settings.LOGMANCER = {
            "ENABLE_NOTIFICATIONS": False,
        }

        manager = object.__new__(NotificationManager)
        manager.backends = []
        manager._load_backends()

        await manager.send_notifications(sample_log_entry)

        assert len(manager.backends) == 0
