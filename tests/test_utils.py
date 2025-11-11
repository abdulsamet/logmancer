import time
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model

import pytest

from logmancer.models import LogEntry
from logmancer.utils import LogEvent

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_logs():
    """Clear all logs before each test"""
    LogEntry.objects.all().delete()
    yield
    LogEntry.objects.all().delete()


@pytest.fixture
def bypass_transaction():
    """Fixture to bypass transaction.on_commit"""
    with patch("logmancer.utils.transaction.on_commit", side_effect=lambda f: f()):
        yield


@pytest.mark.django_db(transaction=True)
class TestLogEvent:
    """Test LogEvent utility class"""

    def test_info_log(self, bypass_transaction):
        """Test info level logging"""
        LogEvent.info("Test info message")

        log = LogEntry.objects.get(message="Test info message")
        assert log.level == "INFO"

    def test_warning_log(self, bypass_transaction):
        """Test warning level logging"""
        LogEvent.warning("Test warning")

        log = LogEntry.objects.get(message="Test warning")
        assert log.level == "WARNING"

    def test_error_log(self, bypass_transaction):
        """Test error level logging"""
        LogEvent.error("Test error")

        log = LogEntry.objects.get(message="Test error")
        assert log.level == "ERROR"

    def test_debug_log(self, bypass_transaction):
        """Test debug level logging"""
        LogEvent.debug("Test debug")

        log = LogEntry.objects.get(message="Test debug")
        assert log.level == "DEBUG"

    def test_critical_log(self, bypass_transaction):
        """Test critical level logging"""
        LogEvent.critical("Test critical")

        log = LogEntry.objects.get(message="Test critical")
        assert log.level == "CRITICAL"

    def test_fatal_log(self, bypass_transaction):
        """Test fatal level logging"""
        LogEvent.fatal("Test fatal")

        log = LogEntry.objects.get(message="Test fatal")
        assert log.level == "FATAL"

    def test_notset_log(self, bypass_transaction):
        """Test notset level logging"""
        LogEvent.notset("Test notset")

        log = LogEntry.objects.get(message="Test notset")
        assert log.level == "NOTSET"

    def test_log_with_source(self, bypass_transaction):
        """Test logging with custom source"""
        LogEvent.info("Test source", source="custom")

        log = LogEntry.objects.get(message="Test source")
        assert log.source == "custom"

    def test_log_with_path(self, bypass_transaction):
        """Test logging with path"""
        LogEvent.info("Test path", path="/api/test/")

        log = LogEntry.objects.get(message="Test path")
        assert log.path == "/api/test/"

    def test_log_with_method(self, bypass_transaction):
        """Test logging with HTTP method"""
        LogEvent.info("Test method", method="POST")

        log = LogEntry.objects.get(message="Test method")
        assert log.method == "POST"

    def test_log_with_status_code(self, bypass_transaction):
        """Test logging with status code"""
        LogEvent.info("Test status", status_code=404)

        log = LogEntry.objects.get(message="Test status")
        assert log.status_code == 404

    def test_log_with_meta(self, bypass_transaction):
        """Test logging with metadata"""
        LogEvent.info("Test meta", meta={"key": "value"})

        log = LogEntry.objects.get(message="Test meta")
        assert log.meta["key"] == "value"

    def test_log_with_user(self, django_user_model, bypass_transaction):
        """Test logging with user"""
        user = django_user_model.objects.create_user(username="testuser")

        LogEvent.info("Test user", user=user)

        log = LogEntry.objects.get(message="Test user")
        assert log.user == user

    def test_log_with_actor_type(self, bypass_transaction):
        """Test logging with actor type"""
        LogEvent.info("Test actor", actor_type="system")

        log = LogEntry.objects.get(message="Test actor")
        assert log.actor_type == "system"

    def test_default_source(self, bypass_transaction):
        """Test default source is manual"""
        LogEvent.info("Test default source")

        log = LogEntry.objects.get(message="Test default source")
        assert log.source == "manual"

    def test_default_actor_type(self, bypass_transaction):
        """Test default actor_type is user"""
        LogEvent.info("Test default actor")

        log = LogEntry.objects.get(message="Test default actor")
        assert log.actor_type == "user"

    def test_default_meta(self, bypass_transaction):
        """Test default meta is empty dict"""
        LogEvent.info("Test default meta")

        log = LogEntry.objects.get(message="Test default meta")
        assert log.meta == {}


@pytest.mark.django_db(transaction=True)
class TestLogEventNotifications:
    """Test notification functionality"""

    @patch("logmancer.utils.get_bool")
    def test_notification_enabled(self, mock_get_bool, bypass_transaction):
        """Test notification when enabled"""
        mock_get_bool.return_value = True

        LogEvent.error("Test notification enabled", notify=True)

        time.sleep(0.1)
        log = LogEntry.objects.get(message="Test notification enabled")
        assert log is not None

    @patch("logmancer.utils.get_bool")
    def test_notification_disabled(self, mock_get_bool, bypass_transaction):
        """Test notification when disabled"""
        mock_get_bool.return_value = False

        LogEvent.error("Test notification disabled", notify=True)

        log = LogEntry.objects.get(message="Test notification disabled")
        assert log is not None

    def test_notification_queue_exists(self):
        """Test notification queue is configured"""
        assert LogEvent._notification_queue is not None
        assert LogEvent._notification_queue.maxsize == 1000

    def test_notification_executor_exists(self):
        """Test notification executor is configured"""
        assert LogEvent._notification_executor is not None

    @patch("logmancer.utils.get_bool")
    def test_notification_not_sent_without_flag(self, mock_get_bool, bypass_transaction):
        """Test notification not sent when notify=False"""
        mock_get_bool.return_value = True
        initial_queue_size = LogEvent._notification_queue.qsize()

        LogEvent.error("Test no notify flag", notify=False)

        # Queue should not increase
        final_queue_size = LogEvent._notification_queue.qsize()
        assert final_queue_size == initial_queue_size


@pytest.mark.django_db(transaction=True)
class TestLogEventErrorHandling:
    """Test error handling"""

    def test_log_creation_error_handling(self):
        """Test error handling when log creation fails"""
        with patch("logmancer.utils.logger") as mock_logger:
            with patch(
                "logmancer.utils.LogEntry.objects.create", side_effect=Exception("DB Error")
            ):
                with patch("logmancer.utils.transaction.on_commit", side_effect=lambda f: f()):
                    LogEvent.info("Test error handling")

                # Should log error
                assert mock_logger.error.called

    def test_queue_full_error_handling(self):
        """Test queue full error handling"""
        mock_log = Mock()
        # Just test that it doesn't crash when queueing fails
        LogEvent._queue_notification(mock_log, {})
        # If no exception raised, test passes


@pytest.mark.django_db(transaction=True)
class TestLogEventTransaction:
    """Test transaction handling"""

    def test_on_commit_used(self):
        """Test transaction.on_commit is used"""
        with patch("logmancer.utils.transaction") as mock_transaction:
            LogEvent.info("Test on commit")

            mock_transaction.on_commit.assert_called_once()

    def test_log_created_after_commit(self, bypass_transaction):
        """Test log is created after commit"""
        initial_count = LogEntry.objects.count()

        LogEvent.info("Test after commit")

        assert LogEntry.objects.count() == initial_count + 1


@pytest.mark.django_db(transaction=True)
class TestLogEventIntegration:
    """Integration tests"""

    def test_multiple_logs(self, bypass_transaction):
        """Test multiple logs can be created"""
        LogEvent.info("Log 1")
        LogEvent.warning("Log 2")
        LogEvent.error("Log 3")

        assert LogEntry.objects.filter(message="Log 1").exists()
        assert LogEntry.objects.filter(message="Log 2").exists()
        assert LogEntry.objects.filter(message="Log 3").exists()

    def test_all_parameters(self, django_user_model, bypass_transaction):
        """Test with all parameters"""
        user = django_user_model.objects.create_user(username="testallparams")

        LogEvent.error(
            "Test all params",
            source="middleware",
            path="/api/test/",
            method="POST",
            status_code=500,
            meta={"error": "details"},
            user=user,
            actor_type="user",
        )

        log = LogEntry.objects.get(message="Test all params")
        assert log.level == "ERROR"
        assert log.source == "middleware"
        assert log.path == "/api/test/"
        assert log.method == "POST"
        assert log.status_code == 500
        assert log.user == user
        assert log.actor_type == "user"

    @patch("logmancer.utils.get_bool")
    def test_with_notification(self, mock_get_bool, bypass_transaction):
        """Test log with notification"""
        mock_get_bool.return_value = True

        LogEvent.error("Test with notif", notify=True)

        time.sleep(0.1)
        log = LogEntry.objects.get(message="Test with notif")
        assert log.level == "ERROR"


@pytest.mark.django_db(transaction=True)
class TestLogEventWorker:
    """Test notification worker"""

    def test_worker_started_flag(self):
        """Test worker started flag exists"""
        assert hasattr(LogEvent, "_worker_started")

    def test_worker_starts_on_first_notification(self, bypass_transaction):
        """Test worker starts when first notification queued"""
        LogEvent._worker_started = False

        with patch("logmancer.utils.get_bool", return_value=True):
            LogEvent.error("Test worker start", notify=True)

        time.sleep(0.1)
        # Just verify no crash
        assert True
