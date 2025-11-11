from unittest.mock import patch

import pytest

from logmancer.notifications.email import EmailBackend


class TestEmailBackend:
    """Test EmailBackend"""

    @pytest.fixture
    def backend(self, email_config):
        """Create EmailBackend instance"""
        return EmailBackend(email_config)

    def test_backend_initialization(self, backend, email_config):
        """Test EmailBackend initialization"""
        assert backend.config["to_emails"] == email_config["to_emails"]
        assert backend.config["from_email"] == email_config["from_email"]

    @pytest.mark.asyncio
    async def test_backend_no_recipients_warning(self, sample_log_entry):
        """Test EmailBackend with no recipients"""
        config = {"enabled": True, "to_emails": []}
        backend = EmailBackend(config)

        sample_log_entry.level = "ERROR"
        sample_log_entry.source = None
        sample_log_entry.path = None

        # Should handle gracefully, not raise
        await backend.send_notification(sample_log_entry)

    @pytest.mark.asyncio
    @patch("logmancer.notifications.email.send_mail")
    async def test_send_notification_success(self, mock_send_mail, backend, sample_log_entry):
        """Test successful email notification"""
        # Configure log entry to pass should_send check
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = None
        sample_log_entry.path = "/api/test/"

        await backend.send_notification(sample_log_entry)

        # Verify send_mail was called
        assert mock_send_mail.called, "send_mail should have been called"

        # Verify call arguments
        call_args = mock_send_mail.call_args
        if call_args:
            if call_args.kwargs:
                kwargs = call_args.kwargs
                assert "subject" in kwargs
                assert "message" in kwargs
                assert sample_log_entry.level in kwargs.get("subject", "")

    @pytest.mark.asyncio
    @patch("logmancer.notifications.email.send_mail")
    async def test_send_notification_skipped_low_level(
        self, mock_send_mail, backend, sample_log_entry
    ):
        """Test notification skipped for low level"""
        sample_log_entry.level = "DEBUG"
        sample_log_entry.source = None
        sample_log_entry.path = "/api/test/"

        await backend.send_notification(sample_log_entry)

        # Should NOT call send_mail
        assert not mock_send_mail.called, "send_mail should not be called for DEBUG level"

    @pytest.mark.asyncio
    @patch("logmancer.notifications.email.send_mail")
    async def test_send_notification_exception(self, mock_send_mail, backend, sample_log_entry):
        """Test email notification with exception"""
        sample_log_entry.level = "ERROR"
        sample_log_entry.source = None
        sample_log_entry.path = "/api/test/"

        mock_send_mail.side_effect = Exception("SMTP error")

        # The backend does NOT catch exceptions, so it should raise
        with pytest.raises(Exception, match="SMTP error"):
            await backend.send_notification(sample_log_entry)
