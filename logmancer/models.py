import datetime as dt
import json
import logging
from decimal import Decimal
from uuid import UUID

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from logmancer.levels import LogLevel

logger = logging.getLogger("logmancer.models")


class SafeJSONField(models.JSONField):
    """JSONField that automatically sanitizes data"""

    def get_prep_value(self, value):
        """Prepare value for database - sanitize before saving"""
        if value is None:
            return value

        value = self.make_json_safe(value)
        return super().get_prep_value(value)

    @staticmethod
    def make_json_safe(data):
        """Convert data to JSON-serializable format"""

        def default_serializer(obj):
            if isinstance(obj, (dt.datetime, dt.date)):
                return obj.isoformat()
            elif isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, UUID):
                return str(obj)
            elif hasattr(obj, "__dict__"):
                return str(obj)
            return str(obj)

        try:
            json_str = json.dumps(data, default=default_serializer)
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"make_json_safe error: {e}")
            return {}


class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(
        max_length=10, choices=LogLevel.get_choices(), default=LogLevel.INFO.name, db_index=True
    )
    message = models.TextField(blank=True, null=True)

    path = models.CharField(max_length=500, blank=True, null=True)
    method = models.CharField(max_length=10, blank=True, null=True)
    status_code = models.PositiveSmallIntegerField(blank=True, null=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_entries",
    )
    source = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Source of the log: 'middleware', 'signal', etc.",
    )

    actor_type = models.CharField(
        max_length=20,
        choices=[("user", _("User")), ("system", _("System"))],
        default="user",
        help_text="Type of source triggering the event",
    )
    meta = SafeJSONField(
        blank=True,
        null=True,
        help_text="Additional metadata for the log entry in JSON format",
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = _("Log Entry")
        verbose_name_plural = _("Log Entries")

    def get_level_info(self):
        """Get full level information"""
        return LogLevel.from_name(self.level).value

    def get_emoji(self):
        """Get emoji for this log level"""
        return self.get_level_info().emoji

    def get_color(self):
        """Get color for this log level"""
        return self.get_level_info().color

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {self.level}"
