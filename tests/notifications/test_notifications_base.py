import pytest

from logmancer.notifications.base import NotificationBackend


class MockBackend(NotificationBackend):
    """Mock backend for testing"""

    async def send_notification(self, log_entry, extra_context=None):
        """Mock send_notification"""
        pass

    def format_message(self, log_entry, context=None):
        """Mock format_message"""
        return "Mock message"


class TestNotificationBackend:
    """Test NotificationBackend base class"""

    @pytest.fixture
    def backend_config(self):
        """Backend configuration with filters"""
        return {
            "enabled": True,
            "min_level": "WARNING",
            "sources": ["exception", "middleware"],
            "excluded_paths": ["/health/", "/metrics/"],
        }

    @pytest.fixture
    def backend(self, backend_config):
        """Create mock backend instance"""
        return MockBackend(backend_config)

    def test_backend_initialization(self, backend, backend_config):
        """Test backend initialization"""
        assert backend.config == backend_config
        assert backend.enabled is True

    def test_should_send_below_min_level(self, backend, sample_log_entry):
        """Test should_send returns False for level below minimum"""
        sample_log_entry.level = "INFO"
        sample_log_entry.source = "exception"
        sample_log_entry.path = "/api/test/"

        assert backend.should_send(sample_log_entry) is False

    def test_should_send_meets_criteria(self, backend, sample_log_entry):
        """Test should_send returns True when all criteria met"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "exception"
        sample_log_entry.path = "/api/test/"

        assert backend.should_send(sample_log_entry) is True

    def test_should_send_source_not_allowed(self, backend, sample_log_entry):
        """Test should_send returns False for non-allowed source"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "manual"
        sample_log_entry.path = "/api/test/"

        # If allowed_sources is set and source doesn't match, should return False
        assert backend.should_send(sample_log_entry) is False

    def test_should_send_excluded_path(self, backend, sample_log_entry):
        """Test should_send returns False for excluded path"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "exception"
        sample_log_entry.path = "/health/check"  # Starts with /health/

        assert backend.should_send(sample_log_entry) is False

    def test_should_send_no_source_filter(self, sample_log_entry):
        """Test should_send with no source filter"""
        config = {
            "enabled": True,
            "min_level": "WARNING",
            # No allowed_sources specified
        }
        backend = MockBackend(config)

        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "anything"
        sample_log_entry.path = "/api/test/"

        assert backend.should_send(sample_log_entry) is True

    def test_should_send_disabled_backend(self, sample_log_entry):
        """Test should_send returns False when backend disabled"""
        config = {"enabled": False}
        backend = MockBackend(config)

        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "exception"

        assert backend.should_send(sample_log_entry) is False

    def test_should_send_no_path(self, backend, sample_log_entry):
        """Test should_send with no path on log entry"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "exception"
        sample_log_entry.path = None

        assert backend.should_send(sample_log_entry) is True

    def test_get_level_emoji(self, backend, sample_log_entry):
        """Test get_level_emoji returns correct emoji"""
        sample_log_entry.level = "ERROR"
        emoji = backend.get_level_emoji(sample_log_entry)
        assert emoji == "❌"

        sample_log_entry.level = "WARNING"
        emoji = backend.get_level_emoji(sample_log_entry)
        assert emoji == "⚠️"

        sample_log_entry.level = "INFO"
        emoji = backend.get_level_emoji(sample_log_entry)
        assert emoji == "ℹ️"

    def test_get_level_emoji_invalid(self, backend, sample_log_entry):
        """Test get_level_emoji with invalid level"""
        sample_log_entry.level = "INVALID_LEVEL"
        emoji = backend.get_level_emoji(sample_log_entry)
        assert emoji == "📝"

    def test_get_level_color(self, backend, sample_log_entry):
        """Test get_level_color returns correct color"""
        sample_log_entry.level = "ERROR"
        color = backend.get_level_color(sample_log_entry)
        assert color == "#F44336"

        sample_log_entry.level = "WARNING"
        color = backend.get_level_color(sample_log_entry)
        assert color == "#FFC107"

    def test_get_level_color_invalid(self, backend, sample_log_entry):
        """Test get_level_color with invalid level"""
        sample_log_entry.level = "INVALID_LEVEL"
        color = backend.get_level_color(sample_log_entry)
        assert color == "#808080"

    def test_get_slack_color(self, backend, sample_log_entry):
        """Test get_slack_color returns correct color"""
        sample_log_entry.level = "ERROR"
        color = backend.get_slack_color(sample_log_entry)
        assert color == "danger"

        sample_log_entry.level = "WARNING"
        color = backend.get_slack_color(sample_log_entry)
        assert color == "warning"

        sample_log_entry.level = "INFO"
        color = backend.get_slack_color(sample_log_entry)
        assert color == "good"

    def test_get_slack_color_invalid(self, backend, sample_log_entry):
        """Test get_slack_color with invalid level"""
        sample_log_entry.level = "INVALID_LEVEL"
        color = backend.get_slack_color(sample_log_entry)
        assert color == "danger"

    def test_test_connection(self, backend):
        """Test default test_connection returns True"""
        assert backend.test_connection() is True
