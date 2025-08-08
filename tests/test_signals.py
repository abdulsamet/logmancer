from unittest.mock import patch

from django.contrib.auth.models import Group, User

import pytest
from model_bakery import baker

from logmancer.signals import log_model_delete, log_model_save


@pytest.mark.django_db
class TestSignals:
    """Test Django signals integration"""

    @patch("logmancer.signals.get_bool", return_value=True)
    @patch("logmancer.signals.LogEvent.info")
    def test_signal_handler_for_create(self, mock_log_info, mock_get_bool):
        """Test signal handler function directly for create"""
        user = User(username="testuser")
        user.pk = 40  # Simulate a primary key for the instance

        log_model_save(sender=User, instance=user, created=True)

        # Verify LogEvent.info was called exactly once
        mock_log_info.assert_called_once()

        # Get call arguments
        args, kwargs = mock_log_info.call_args

        # Check message - either in args[0] or kwargs['message']
        message = args[0] if args else kwargs.get("message", "")
        assert "created" in message

        # Additional checks
        assert kwargs.get("source") == "signal"
        assert kwargs.get("actor_type") == "system"

    @patch("logmancer.signals.get_bool", return_value=True)
    @patch("logmancer.signals.LogEvent.warning")
    def test_signal_handler_for_delete(self, mock_log_warning, mock_get_bool):
        """Test signal handler function directly for delete"""
        user = baker.make(User, username="testuser")

        log_model_delete(sender=User, instance=user)

        # Verify LogEvent.warning was called exactly once
        assert mock_log_warning.call_count == 1

        # Check if call_args exists and has the expected structure
        assert mock_log_warning.call_args is not None
        args, kwargs = mock_log_warning.call_args

        # Verify the message contains "deleted"
        if args:
            assert "deleted" in args[0]
        else:
            assert "deleted" in kwargs.get("message", "")

    @patch("logmancer.signals.get_bool", return_value=True)
    @patch("logmancer.signals.should_exclude_model", return_value=True)
    @patch("logmancer.signals.LogEvent.info")
    def test_excluded_model_handler(self, mock_log_info, mock_should_exclude, mock_get_bool):
        """Test signal handler respects excluded models"""
        group = Group.objects.create(name="test")

        log_model_save(sender=Group, instance=group, created=True)

        # Should not call LogEvent.info for excluded model
        assert not mock_log_info.called

    @patch("logmancer.signals.get_bool", return_value=False)
    @patch("logmancer.signals.LogEvent.info")
    def test_disabled_signals_handler(self, mock_log_info, mock_get_bool):
        """Test signal handler respects disabled setting"""
        user = baker.make(User, username="testuser")

        log_model_save(sender=User, instance=user, created=True)

        # Should not call LogEvent.info when disabled
        assert not mock_log_info.called
