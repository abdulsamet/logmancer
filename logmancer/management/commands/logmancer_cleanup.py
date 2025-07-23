from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from logmancer.conf import get_int
from logmancer.models import LogEntry
from logmancer.utils import LogEvent


class Command(BaseCommand):
    help = "Logmancer: Cleans up old log entries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            help="Delete logs older than this many days",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many logs would be deleted, but do not delete.",
        )

    def handle(self, *args, **options):
        days = options.get("days") or get_int("CLEANUP_AFTER_DAYS")
        dry_run = options.get("dry_run", False)
        threshold_date = timezone.now() - timedelta(days=days)

        old_logs = LogEntry.objects.filter(timestamp__lt=threshold_date)
        count = old_logs.count()

        if dry_run:
            msg = (
                f"[Logmancer] {count} log entries older than {days} days "
                "would be deleted (dry run)."
            )
            self.stdout.write(self.style.WARNING(msg))
        else:
            with transaction.atomic():
                old_logs.delete()
                LogEvent.info(
                    message=f"{count} old logs cleaned up (>{days} days)",
                    meta={"days": days, "count": count},
                    source="cleanup",
                    actor_type="system",
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"[Logmancer] Deleted {count} log entries older than {days} days."
                )
            )
