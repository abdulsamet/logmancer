from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from logmancer.models import LogEntry

LEVEL_COLORS = {
    "DEFAULT": "#000000",
    "CRITICAL": "#d32f2f",
    "DEBUG": "#366092",
    "INFO": "#008000",
    "WARNING": "#f57c00",
    "ERROR": "#d32f2f",
    "FATAL": "#d32f2f",
    "NOTSET": "#000000",
}


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "formatted_timestamp",
        "colored_level",
        "user",
        "source",
        "path",
        "status_code",
        "short_message",
    )
    list_filter = (
        "level",
        "status_code",
        "actor_type",
        "source",
        "user",
    )
    search_fields = ("message", "path", "meta")
    ordering = ("-timestamp",)
    readonly_fields = (
        "timestamp",
        "level",
        "message",
        "user",
        "path",
        "method",
        "status_code",
        "meta",
        "source",
        "actor_type",
    )

    def formatted_timestamp(self, obj):
        dt = localtime(obj.timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")

    formatted_timestamp.short_description = _("Timestamp")

    def colored_level(self, obj):
        color = LEVEL_COLORS.get(obj.level.upper(), LEVEL_COLORS["DEFAULT"])
        return format_html('<b style="color: {}; font-weight: bold;">{}</b>', color, obj.level)

    colored_level.short_description = _("Level")

    def short_message(self, obj):
        msg = obj.message or ""
        return msg[:60] + "..." if len(msg) > 60 else msg

    short_message.short_description = _("Message")
