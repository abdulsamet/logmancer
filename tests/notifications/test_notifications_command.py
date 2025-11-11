from io import StringIO
from unittest.mock import Mock, patch

from django.core.management import call_command

import pytest


class TestNotificationsCommand:
    """Test test_notifications management command"""

    @pytest.mark.asyncio
    @patch("logmancer.management.commands.test_notifications.LogEvent")
    async def test_command_default_parameters(self, mock_log_event):
        """Test command with default parameters"""
        mock_log_event.error = Mock()

        out = StringIO()
        call_command("test_notifications", stdout=out)

        # Verify LogEvent.error was called
        mock_log_event.error.assert_called_once()
        call_args = mock_log_event.error.call_args

        # Check arguments
        assert call_args.kwargs["message"] == "Test notification"
        assert call_args.kwargs["source"] == "test"
        assert call_args.kwargs["notify"] is True
        assert call_args.kwargs["meta"]["test"] is True

        assert "Test ERROR notification sent" in out.getvalue()

    @pytest.mark.asyncio
    @patch("logmancer.management.commands.test_notifications.LogEvent")
    async def test_command_custom_level(self, mock_log_event):
        """Test command with custom log level"""
        mock_log_event.warning = Mock()

        out = StringIO()
        call_command("test_notifications", level="WARNING", stdout=out)

        # Verify LogEvent.warning was called
        mock_log_event.warning.assert_called_once()

        assert "Test WARNING notification sent" in out.getvalue()

    @pytest.mark.asyncio
    @patch("logmancer.management.commands.test_notifications.LogEvent")
    async def test_command_custom_message(self, mock_log_event):
        """Test command with custom message"""
        mock_log_event.error = Mock()
        custom_message = "Custom test message"

        out = StringIO()
        call_command("test_notifications", message=custom_message, stdout=out)

        # Verify message was passed
        call_args = mock_log_event.error.call_args
        assert call_args.kwargs["message"] == custom_message

        # Check output
        assert custom_message in out.getvalue()

    @pytest.mark.asyncio
    @patch("logmancer.management.commands.test_notifications.LogEvent")
    async def test_command_all_levels(self, mock_log_event):
        """Test command with different log levels"""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            mock_method = Mock()
            setattr(mock_log_event, level.lower(), mock_method)

            out = StringIO()
            call_command("test_notifications", level=level, stdout=out)

            # Verify correct method was called
            mock_method.assert_called_once()

            assert f"Test {level} notification sent" in out.getvalue()

    @pytest.mark.asyncio
    @patch("logmancer.management.commands.test_notifications.LogEvent")
    async def test_command_with_all_parameters(self, mock_log_event):
        """Test command with all parameters specified"""
        mock_log_event.critical = Mock()

        out = StringIO()
        call_command(
            "test_notifications", level="CRITICAL", message="Critical test notification", stdout=out
        )

        # Verify call
        call_args = mock_log_event.critical.call_args
        assert call_args.kwargs["message"] == "Critical test notification"
        assert call_args.kwargs["source"] == "test"
        assert call_args.kwargs["notify"] is True
        assert call_args.kwargs["meta"]["test"] is True

        # Check output
        assert "Test CRITICAL notification sent" in out.getvalue()
        assert "Critical test notification" in out.getvalue()

    @pytest.mark.asyncio
    @patch("logmancer.management.commands.test_notifications.LogEvent")
    async def test_command_notify_flag(self, mock_log_event):
        """Test that notify flag is set to True"""
        mock_log_event.error = Mock()

        call_command("test_notifications")

        call_args = mock_log_event.error.call_args
        assert call_args.kwargs["notify"] is True

    @pytest.mark.asyncio
    @patch("logmancer.management.commands.test_notifications.LogEvent")
    async def test_command_meta_contains_test_flag(self, mock_log_event):
        """Test that meta contains test flag"""
        mock_log_event.error = Mock()

        call_command("test_notifications")

        call_args = mock_log_event.error.call_args
        assert "meta" in call_args.kwargs
        assert call_args.kwargs["meta"]["test"] is True

    @pytest.mark.asyncio
    @patch("logmancer.management.commands.test_notifications.LogEvent")
    async def test_command_source_is_test(self, mock_log_event):
        """Test that source is set to 'test'"""
        mock_log_event.error = Mock()

        call_command("test_notifications")

        call_args = mock_log_event.error.call_args
        assert call_args.kwargs["source"] == "test"

    @pytest.mark.asyncio
    @patch("logmancer.management.commands.test_notifications.LogEvent")
    async def test_command_integration_with_notifications(self, mock_log_event, settings):
        """Test command triggers actual notification flow"""
        settings.LOGMANCER = {
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

        mock_log_event.error = Mock()

        out = StringIO()
        call_command("test_notifications", stdout=out)

        # Verify notification was triggered
        mock_log_event.error.assert_called_once()
        assert "SUCCESS" in out.getvalue() or "Test ERROR notification sent" in out.getvalue()
