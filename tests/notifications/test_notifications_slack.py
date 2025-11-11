from unittest.mock import Mock, patch

import pytest

from logmancer.notifications.slack import SlackBackend


class TestSlackBackend:
    """Test SlackBackend"""

    @pytest.fixture
    def backend(self, slack_config):
        """Create SlackBackend instance"""
        return SlackBackend(slack_config)

    @pytest.mark.asyncio
    @patch("logmancer.notifications.slack.requests.post")
    async def test_send_notification_success(self, mock_post, backend, sample_log_entry):
        """Test successful Slack notification"""
        # Configure to pass should_send
        sample_log_entry.level = "WARNING"  # Meets min_level
        sample_log_entry.source = None  # No source filter
        sample_log_entry.path = "/api/test/"  # Not excluded

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        await backend.send_notification(sample_log_entry)

        assert mock_post.called, "requests.post should have been called"

    @pytest.mark.asyncio
    @patch("logmancer.notifications.slack.requests.post")
    async def test_send_notification_failed_status(self, mock_post, backend, sample_log_entry):
        """Test Slack notification with failed status"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = None
        sample_log_entry.path = "/api/test/"

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        # Should not crash
        await backend.send_notification(sample_log_entry)

        assert mock_post.called

    @pytest.mark.asyncio
    @patch("logmancer.notifications.slack.requests.post")
    async def test_send_notification_skipped_low_level(self, mock_post, backend, sample_log_entry):
        """Test notification skipped for low level"""
        sample_log_entry.level = "DEBUG"  # Below WARNING
        sample_log_entry.source = None
        sample_log_entry.path = "/api/test/"

        await backend.send_notification(sample_log_entry)

        assert not mock_post.called, "Should not send for DEBUG level"

    def test_test_connection(self, backend):
        """Test Slack connection test"""
        with patch("logmancer.notifications.slack.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            result = backend.test_connection()

            assert result is True
