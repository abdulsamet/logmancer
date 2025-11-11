from django.db import transaction
from django.test import override_settings

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


@pytest.mark.django_db(transaction=True)
@override_settings(LOGMANCER={"ENABLE_NOTIFICATIONS": True})
def test_log_event_notify_true_triggers_queue(monkeypatch):
    queued = {}

    def fake_queue(cls, log_entry, context):
        queued["called"] = True
        queued["log_entry"] = log_entry
        queued["context"] = context

    monkeypatch.setattr(LogEvent, "_queue_notification", classmethod(fake_queue))

    with transaction.atomic():
        LogEvent.error(
            "Notify me",
            notify=True,
            meta={"key": "value"},
            source="test",
        )
        transaction.on_commit(lambda: None)

    assert queued.get("called") is True
    assert queued["log_entry"].message == "Notify me"
    assert queued["context"]["meta"] == {"key": "value"}
    assert queued["context"]["source"] == "test"


@pytest.mark.django_db(transaction=True)
@override_settings(LOGMANCER={"ENABLE_NOTIFICATIONS": False})
def test_log_event_notify_true_respects_disabled_setting(monkeypatch):
    was_called = False

    def fake_queue(cls, log_entry, context):
        nonlocal was_called
        was_called = True

    monkeypatch.setattr(LogEvent, "_queue_notification", classmethod(fake_queue))

    with transaction.atomic():
        LogEvent.error("Do not notify", notify=True)
        transaction.on_commit(lambda: None)

    assert was_called is False
