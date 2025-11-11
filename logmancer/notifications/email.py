import asyncio

from django.conf import settings
from django.core.mail import send_mail

from logmancer.notifications import NotificationBackend


class EmailBackend(NotificationBackend):
    """Email notification backend"""

    async def send_notification(self, log_entry, context=None):
        """Send notification via email"""
        if not self.should_send(log_entry):
            self.logger.info("Email notification not sent due to filtering")
            return

        subject = f"[{log_entry.level}] {log_entry.message[:50]}..."
        message = self.format_message(log_entry, context)
        recipients = self.config.get("to_emails", [])

        if not recipients:
            self.logger.error("Email backend requires 'to_emails' in configuration")
            return

        def _send():
            send_mail(
                subject=subject,
                message=message,
                from_email=self.config.get("from_email", settings.DEFAULT_FROM_EMAIL),
                recipient_list=recipients,
                fail_silently=False,
            )

        await asyncio.to_thread(_send)

    def format_message(self, log_entry, context=None):
        """Format email message"""
        message = f"Level: {log_entry.level}\n"
        message += f"Message: {log_entry.message}\n"
        message += f"Time: {log_entry.timestamp}\n"

        if log_entry.path:
            message += f"Path: {log_entry.path}\n"
        if log_entry.user:
            message += f"User: {log_entry.user}\n"
        if log_entry.source:
            message += f"Source: {log_entry.source}\n"

        return message
