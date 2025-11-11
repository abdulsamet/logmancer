from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from logmancer.notifications.manager import Backends, NotificationManager


class TestNotificationManager:
    """Test NotificationManager"""

    def test_manager_singleton(self):
        """Test NotificationManager is a singleton"""
        from logmancer.notifications.manager import notification_manager

        manager1 = notification_manager
        manager2 = notification_manager
        assert manager1 is manager2

    @patch("logmancer.conf.get_bool")
    @patch("logmancer.conf.get_dict")
    def test_load_backends_disabled(self, mock_get_dict, mock_get_bool):
        """Test backends not loaded when notifications disabled"""
        mock_get_bool.return_value = False
        mock_get_dict.return_value = {}

        manager = object.__new__(NotificationManager)
        manager.backends = []
        manager._load_backends()

        assert len(manager.backends) == 0

    @patch("logmancer.conf.get_bool")
    @patch("logmancer.conf.get_dict")
    def test_load_backends_no_config(self, mock_get_dict, mock_get_bool):
        """Test backends with empty config"""
        mock_get_bool.return_value = True
        mock_get_dict.return_value = {}

        manager = object.__new__(NotificationManager)
        manager.backends = []
        manager._load_backends()

        assert len(manager.backends) == 0

    @patch("logmancer.notifications.manager.import_module")
    @patch("logmancer.conf.get_dict")
    @patch("logmancer.conf.get_bool")
    def test_load_single_backend(self, mock_get_bool, mock_get_dict, mock_import):
        """Test loading a single backend"""
        mock_get_bool.return_value = True
        mock_get_dict.return_value = {
            "telegram": {"enabled": True, "bot_token": "test", "chat_id": "123"}
        }

        mock_backend = MagicMock()
        mock_module = MagicMock()
        mock_module.TelegramBackend = MagicMock(return_value=mock_backend)
        mock_import.return_value = mock_module

        manager = object.__new__(NotificationManager)
        manager.backends = []
        manager._load_backends()

        assert len(manager.backends) == 1

    @patch("logmancer.notifications.manager.import_module")
    @patch("logmancer.conf.get_dict")
    @patch("logmancer.conf.get_bool")
    def test_load_disabled_backend(self, mock_get_bool, mock_get_dict, mock_import):
        """Test disabled backend is not loaded"""
        mock_get_bool.return_value = True
        mock_get_dict.return_value = {"telegram": {"enabled": False, "bot_token": "test"}}

        manager = object.__new__(NotificationManager)
        manager.backends = []
        manager._load_backends()

        assert len(manager.backends) == 0

    @patch("logmancer.notifications.manager.import_module")
    @patch("logmancer.conf.get_dict")
    @patch("logmancer.conf.get_bool")
    def test_load_invalid_backend(self, mock_get_bool, mock_get_dict, mock_import):
        """Test invalid backend is skipped"""
        mock_get_bool.return_value = True
        mock_get_dict.return_value = {"invalid": {"enabled": True}}

        manager = object.__new__(NotificationManager)
        manager.backends = []
        manager._load_backends()

        assert len(manager.backends) == 0

    @pytest.mark.asyncio
    async def test_send_notifications_no_backends(self, sample_log_entry):
        """Test send with no backends"""
        manager = object.__new__(NotificationManager)
        manager.backends = []

        await manager.send_notifications(sample_log_entry, {})
        # Should not raise

    @pytest.mark.asyncio
    async def test_send_notifications_success(self, sample_log_entry):
        """Test successful notification sending"""
        mock_backend = Mock()
        mock_backend.send_notification = AsyncMock()

        manager = object.__new__(NotificationManager)
        manager.backends = [mock_backend]

        await manager.send_notifications(sample_log_entry, {})

        mock_backend.send_notification.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notifications_with_exception(self, sample_log_entry):
        """Test backend exception is handled"""
        mock_backend = Mock()
        mock_backend.send_notification = AsyncMock(side_effect=Exception("Error"))

        manager = object.__new__(NotificationManager)
        manager.backends = [mock_backend]

        await manager.send_notifications(sample_log_entry, {})
        # Should not raise

    def test_backends_enum(self):
        """Test Backends enum values"""
        assert Backends.EMAIL.value == "logmancer.notifications.email.EmailBackend"
        assert Backends.TELEGRAM.value == "logmancer.notifications.telegram.TelegramBackend"
        assert Backends.SLACK.value == "logmancer.notifications.slack.SlackBackend"

    def test_list_available_backends(self):
        """Test list available backends"""
        manager = object.__new__(NotificationManager)
        manager.backends = []

        available = manager.list_available_backends()

        assert "email" in available
        assert "telegram" in available
        assert "slack" in available

    def test_list_loaded_backends(self):
        """Test list loaded backends"""
        mock_backend = Mock()
        mock_backend.__class__.__name__ = "TelegramBackend"

        manager = object.__new__(NotificationManager)
        manager.backends = [mock_backend]

        loaded = manager.list_loaded_backends()

        assert "TelegramBackend" in loaded
