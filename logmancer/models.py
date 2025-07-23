from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class LogEntry(models.Model):
    class LogLevel(models.TextChoices):
        INFO = "INFO", _("Info")
        DEBUG = "DEBUG", _("Debug")
        WARNING = "WARNING", _("Warning")
        ERROR = "ERROR", _("Error")
        FATAL = "FATAL", _("Fatal")
        CRITICAL = "CRITICAL", _("Critical")
        NOTSET = "NOTSET", _("Not Set")

    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(
        max_length=10, choices=LogLevel.choices, default=LogLevel.INFO, db_index=True
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
        help_text="Source of the log: 'middleware', 'signal',etc.",
    )

    actor_type = models.CharField(
        max_length=20,
        choices=[("user", _("User")), ("system", _("System"))],
        default="user",
        help_text="Type of source triggering the event",
    )
    meta = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = _("Log Entry")
        verbose_name_plural = _("Log Entries")

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {self.level}"
