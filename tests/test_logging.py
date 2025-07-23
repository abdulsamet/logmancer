from django.db import transaction

import pytest

from logmancer.models import LogEntry
from logmancer.utils import LogEvent


@pytest.mark.django_db(transaction=True)
def test_log_event_creates_entry():
    """Test that LogEvent creates a LogEntry with transaction support"""
    initial_count = LogEntry.objects.count()

    with transaction.atomic():
        LogEvent.info("Test log message")
        transaction.on_commit(lambda: None)

    new_count = LogEntry.objects.count()
    assert new_count == initial_count + 1

    entry = LogEntry.objects.filter(message="Test log message").last()

    assert entry is not None
    assert entry.message == "Test log message"
    assert entry.level == "INFO"


@pytest.mark.django_db(transaction=True)
def test_log_event_with_meta():
    """Test LogEvent with meta parameter"""
    meta = {"key": "value", "number": 42}

    with transaction.atomic():
        LogEvent.debug("Test with meta", meta=meta)

    entry = LogEntry.objects.filter(message="Test with meta").last()
    assert entry is not None
    assert entry.meta == meta
    assert entry.level == "DEBUG"


@pytest.mark.django_db(transaction=True)
def test_log_event_with_actor():
    """Test LogEvent with actor_type"""
    with transaction.atomic():
        LogEvent.warning("Test with actor", actor_type="user")

    entry = LogEntry.objects.filter(message="Test with actor").last()
    assert entry is not None
    assert entry.actor_type == "user"
    assert entry.level == "WARNING"
