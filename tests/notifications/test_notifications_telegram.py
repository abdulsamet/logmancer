from unittest.mock import Mock, patch

import pytest

from logmancer.notifications.telegram import TelegramBackend


class TestTelegramBackend:
    """Test TelegramBackend"""

    @pytest.fixture
    def backend(self, telegram_config):
        """Create TelegramBackend instance"""
        return TelegramBackend(telegram_config)

    def test_init_with_valid_config(self, telegram_config):
        """Test initialization with valid config"""
        backend = TelegramBackend(telegram_config)

        assert backend.bot_token == telegram_config["bot_token"]
        assert backend.chat_id == telegram_config["chat_id"]
        assert backend.timeout == 10

    def test_init_without_bot_token(self):
        """Test initialization fails without bot_token"""
        config = {"chat_id": "123456"}

        with pytest.raises(ValueError, match="bot_token"):
            TelegramBackend(config)

    def test_init_without_chat_id(self):
        """Test initialization fails without chat_id"""
        config = {"bot_token": "123456:ABC-DEF"}

        with pytest.raises(ValueError, match="chat_id"):
            TelegramBackend(config)

    def test_init_with_custom_timeout(self):
        """Test initialization with custom timeout"""
        config = {"bot_token": "123456:ABC-DEF", "chat_id": "123456", "timeout": 30}
        backend = TelegramBackend(config)

        assert backend.timeout == 30

    @pytest.mark.asyncio
    @patch("logmancer.notifications.telegram.requests.post")
    async def test_send_notification_success(self, mock_post, backend, sample_log_entry):
        """Test successful notification sending"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "exception"
        sample_log_entry.path = "/api/test/"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        await backend.send_notification(sample_log_entry)

        assert mock_post.called

        # Verify payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["chat_id"] == backend.chat_id
        assert "ERROR" in payload["text"]
        assert payload["parse_mode"] == "HTML"
        assert payload["disable_web_page_preview"] is True

    @pytest.mark.asyncio
    @patch("logmancer.notifications.telegram.requests.post")
    async def test_send_notification_skipped_wrong_source(
        self, mock_post, backend, sample_log_entry
    ):
        """Test notification skipped for wrong source"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "manual"
        sample_log_entry.path = "/api/test/"

        await backend.send_notification(sample_log_entry)

        assert not mock_post.called

    @pytest.mark.asyncio
    @patch("logmancer.notifications.telegram.requests.post")
    @patch("logmancer.notifications.telegram.logger")
    async def test_send_notification_request_exception(
        self, mock_logger, mock_post, backend, sample_log_entry
    ):
        """Test handling of request exception"""
        import requests

        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "exception"

        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        await backend.send_notification(sample_log_entry)

        assert mock_logger.error.called

    @pytest.mark.asyncio
    @patch("logmancer.notifications.telegram.requests.post")
    async def test_send_notification_with_context(self, mock_post, backend, sample_log_entry):
        """Test notification with context"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = "exception"
        sample_log_entry.path = "/api/test/"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        context = {"request_id": "12345"}
        await backend.send_notification(sample_log_entry, context)

        assert mock_post.called

    def test_format_message_basic(self, backend, sample_log_entry):
        """Test basic message formatting"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.message = "Test error message"
        sample_log_entry.path = None
        sample_log_entry.method = None
        sample_log_entry.user = None
        sample_log_entry.source = None

        message = backend.format_message(sample_log_entry)

        assert "ERROR" in message
        assert "Test error message" in message
        assert "<b>" in message
        assert "Path:" not in message
        assert "Method:" not in message
        assert "User:" not in message
        assert "Source:" not in message

    def test_format_message_all_fields(self, backend, sample_log_entry, django_user_model):
        """Test message with all fields"""
        user = django_user_model.objects.create_user(username="testuser")
        sample_log_entry.level = "ERROR"
        sample_log_entry.message = "Test error"
        sample_log_entry.path = "/api/test/"
        sample_log_entry.method = "POST"
        sample_log_entry.user = user
        sample_log_entry.source = "middleware"

        message = backend.format_message(sample_log_entry)

        assert "ERROR" in message
        assert "/api/test/" in message
        assert "POST" in message
        assert "testuser" in message
        assert "middleware" in message

    def test_format_message_length_limit(self, backend, sample_log_entry):
        """Test message is truncated to 4000 chars"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.message = "A" * 5000

        message = backend.format_message(sample_log_entry)

        assert len(message) <= 4000

    @patch("logmancer.notifications.telegram.requests.get")
    def test_test_connection_success(self, mock_get, backend):
        """Test connection test with success"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = backend.test_connection()

        assert result is True
        assert mock_get.called

    @patch("logmancer.notifications.telegram.requests.get")
    @patch("logmancer.notifications.telegram.logger")
    def test_test_connection_exception(self, mock_logger, mock_get, backend):
        """Test connection test with exception"""
        mock_get.side_effect = Exception("Network error")

        result = backend.test_connection()

        assert result is False
        assert mock_logger.error.called
