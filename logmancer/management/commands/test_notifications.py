from django.core.management.base import BaseCommand

from logmancer.utils import LogEvent


class Command(BaseCommand):
    help = "Test notification backends"

    def add_arguments(self, parser):
        parser.add_argument("--level", default="ERROR", help="Log level to test")
        parser.add_argument("--message", default="Test notification", help="Test message")

    def handle(self, *args, **options):
        level = options["level"]
        message = options["message"]

        # Send test notification
        getattr(LogEvent, level.lower())(
            message=message, source="test", notify=True, meta={"test": True}
        )

        self.stdout.write(self.style.SUCCESS(f"Test {level} notification sent: {message}"))
