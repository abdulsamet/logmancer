from datetime import timedelta

from django.core.management import call_command
from django.utils import timezone

import pytest

from logmancer.models import LogEntry


@pytest.mark.django_db(transaction=True)
def test_cleanup_deletes_old_entries():
    log = LogEntry.objects.create(message="Old", level="INFO")
    LogEntry.objects.filter(pk=log.pk).update(timestamp=timezone.now() - timedelta(days=31))
    LogEntry.objects.create(message="Recent", level="INFO")

    call_command("logmancer_cleanup")
    messages = [log.message for log in LogEntry.objects.all()]
    assert "Old" not in messages
    assert "Recent" in messages


@pytest.mark.django_db(transaction=True)
def test_cleanup_days_argument():
    log = LogEntry.objects.create(message="Old", level="INFO")
    LogEntry.objects.filter(pk=log.pk).update(timestamp=timezone.now() - timedelta(days=10))
    LogEntry.objects.create(message="Recent", level="INFO")

    call_command("logmancer_cleanup", days=7)
    messages = [log.message for log in LogEntry.objects.all()]
    assert "Old" not in messages  # 10 > 7
    assert "Recent" in messages

    log2 = LogEntry.objects.create(message="Old2", level="INFO")
    LogEntry.objects.filter(pk=log2.pk).update(timestamp=timezone.now() - timedelta(days=10))
    call_command("logmancer_cleanup", days=9)
    messages = [log.message for log in LogEntry.objects.all()]
    assert "Old2" not in messages  # 10 > 9


@pytest.mark.django_db(transaction=True)
def test_cleanup_dry_run(capsys):
    log = LogEntry.objects.create(message="Old", level="INFO")
    LogEntry.objects.filter(pk=log.pk).update(timestamp=timezone.now() - timedelta(days=31))
    LogEntry.objects.create(message="Recent", level="INFO")

    call_command("logmancer_cleanup", dry_run=True)
    messages = [log.message for log in LogEntry.objects.all()]
    assert "Old" in messages  # dry-run
    assert "Recent" in messages

    out = capsys.readouterr().out
    assert "would be deleted" in out
