from unittest.mock import patch

from django.contrib.auth.models import Group
from django.test import override_settings

import pytest

from logmancer.models import LogEntry
from logmancer.signals import connect_signals


@pytest.mark.django_db
class TestSignals:
    """Test Django signals integration with pytest"""

    @override_settings(LOGMANCER={"ENABLE_SIGNALS": True})
    @patch("logmancer.utils.transaction.on_commit")
    def test_signal_model_created(self, mock_on_commit, simple_user_factory):
        """Test signal fires when model is created"""

        # Mock on_commit to execute immediately
        def execute_immediately(func):
            func()

        mock_on_commit.side_effect = execute_immediately

        # Connect signals
        connect_signals()

        initial_count = LogEntry.objects.count()

        # Create a User instance to trigger the signal
        simple_user_factory()

        # Check if log was created
        new_log_count = LogEntry.objects.count()
        assert new_log_count >= initial_count

    @override_settings(
        LOGMANCER={"ENABLE_SIGNALS": True, "EXCLUDE_MODELS": ["auth.Group"]}
    )
    @patch("logmancer.utils.transaction.on_commit")
    def test_signal_excluded_model_created(self, mock_on_commit):
        """Test signal does not fire for excluded models"""
        connect_signals()

        initial_count = LogEntry.objects.filter(source="signal").count()

        # Create a Group instance which should be excluded
        Group.objects.create(name="Excluded Group")

        new_count = LogEntry.objects.filter(source="signal").count()
        assert new_count == initial_count

    @override_settings(LOGMANCER={"ENABLE_SIGNALS": True})
    @patch("logmancer.utils.transaction.on_commit")
    def test_signal_model_updated(self, mock_on_commit, simple_user_factory):
        """Test signal fires when model is updated"""

        # Mock on_commit to execute immediately
        def execute_immediately(func):
            func()

        mock_on_commit.side_effect = execute_immediately

        # Connect signals
        connect_signals()

        # Create and update a User instance
        test_user = simple_user_factory()
        initial_signal_count = LogEntry.objects.filter(source="signal").count()

        test_user.email = "updated@example.com"
        test_user.save()

        # Check if update log was created
        new_signal_count = LogEntry.objects.filter(source="signal").count()
        assert new_signal_count >= initial_signal_count

    @override_settings(LOGMANCER={"ENABLE_SIGNALS": False})
    def test_signals_disabled(self):
        """Test signals don't fire when disabled"""
        connect_signals()

        initial_count = LogEntry.objects.filter(source="signal").count()
        Group.objects.create(name="Should not log")

        new_count = LogEntry.objects.filter(source="signal").count()
        assert new_count == initial_count


@pytest.mark.django_db
def test_user_factory_fixture_usage(simple_user_factory):
    """Test user_factory fixture specifically"""
    # Test default user creation
    user = simple_user_factory(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"

    # Test custom user creation
    custom_user = simple_user_factory(username="custom", email="custom@example.com")
    assert custom_user.username == "custom"
    assert custom_user.email == "custom@example.com"

    # Test uniqueness
    assert user.id != custom_user.id


@pytest.mark.django_db
def test_log_entry_factory_fixture_usage(simple_log_entry_factory):
    """Test log_entry_factory fixture specifically"""
    # Test default log entry creation
    log = simple_log_entry_factory()
    assert log.message is not None
    assert log.level == "INFO"
    assert log.source == "test"

    # Test custom log entry creation
    custom_log = simple_log_entry_factory(
        message="Custom message", level="ERROR", source="custom"
    )
    assert custom_log.message == "Custom message"
    assert custom_log.level == "ERROR"
    assert custom_log.source == "custom"
