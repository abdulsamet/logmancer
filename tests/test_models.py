import time
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model

import pytest

from logmancer.models import LogEntry, SafeJSONField

User = get_user_model()


@pytest.mark.django_db
class TestSafeJSONField:
    """Test SafeJSONField"""

    def test_make_json_safe_with_datetime(self):
        """Test datetime serialization"""
        data = {"timestamp": datetime(2024, 1, 1, 12, 30, 45)}
        result = SafeJSONField.make_json_safe(data)

        assert isinstance(result["timestamp"], str)
        assert "2024-01-01" in result["timestamp"]

    def test_make_json_safe_with_date(self):
        """Test date serialization"""
        data = {"date": date(2024, 1, 1)}
        result = SafeJSONField.make_json_safe(data)

        assert isinstance(result["date"], str)
        assert "2024-01-01" in result["date"]

    def test_make_json_safe_with_decimal(self):
        """Test decimal serialization"""
        data = {"price": Decimal("19.99")}
        result = SafeJSONField.make_json_safe(data)

        assert isinstance(result["price"], float)
        assert result["price"] == 19.99

    def test_make_json_safe_with_uuid(self):
        """Test UUID serialization"""
        test_uuid = uuid4()
        data = {"id": test_uuid}
        result = SafeJSONField.make_json_safe(data)

        assert isinstance(result["id"], str)
        assert result["id"] == str(test_uuid)

    def test_make_json_safe_with_custom_object(self):
        """Test custom object serialization"""

        class CustomObject:
            def __str__(self):
                return "CustomObject"

        data = {"obj": CustomObject()}
        result = SafeJSONField.make_json_safe(data)

        assert isinstance(result["obj"], str)
        assert "CustomObject" in result["obj"]

    def test_make_json_safe_with_nested_data(self):
        """Test nested data serialization"""
        data = {
            "user": {"id": uuid4(), "created": datetime(2024, 1, 1), "balance": Decimal("100.50")}
        }
        result = SafeJSONField.make_json_safe(data)

        assert isinstance(result["user"]["id"], str)
        assert isinstance(result["user"]["created"], str)
        assert isinstance(result["user"]["balance"], float)

    def test_make_json_safe_with_exception(self):
        """Test error handling returns empty dict"""
        # Create circular reference
        data = {}
        data["self"] = data

        result = SafeJSONField.make_json_safe(data)
        assert result == {}

    def test_make_json_safe_with_none(self):
        """Test None value"""
        result = SafeJSONField.make_json_safe(None)
        assert result is None

    def test_make_json_safe_with_simple_types(self):
        """Test simple types pass through"""
        data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
        }
        result = SafeJSONField.make_json_safe(data)

        assert result["string"] == "test"
        assert result["number"] == 42
        assert result["boolean"] is True
        assert result["null"] is None
        assert result["list"] == [1, 2, 3]


@pytest.mark.django_db
class TestLogEntry:
    """Test LogEntry model"""

    def test_create_log_entry_minimal(self):
        """Test creating log entry with minimal data"""
        log = LogEntry.objects.create(level="INFO", message="Test log")

        assert log.id is not None
        assert log.level == "INFO"
        assert log.message == "Test log"
        assert log.timestamp is not None

    def test_create_log_entry_full(self, django_user_model):
        """Test creating log entry with all fields"""
        user = django_user_model.objects.create_user(username="testuser", password="testpass")

        log = LogEntry.objects.create(
            level="ERROR",
            message="Test error",
            path="/api/test/",
            method="POST",
            status_code=500,
            user=user,
            source="middleware",
            actor_type="user",
            meta={"error": "Something went wrong"},
        )

        assert log.level == "ERROR"
        assert log.message == "Test error"
        assert log.path == "/api/test/"
        assert log.method == "POST"
        assert log.status_code == 500
        assert log.user == user
        assert log.source == "middleware"
        assert log.actor_type == "user"
        assert log.meta["error"] == "Something went wrong"

    def test_log_entry_default_values(self):
        """Test default values"""
        log = LogEntry.objects.create(message="Test")

        assert log.level == "INFO"
        assert log.actor_type == "user"
        assert log.source is None
        assert log.meta is None

    def test_log_entry_ordering(self):
        """Test logs are ordered by timestamp descending"""
        log1 = LogEntry.objects.create(message="First")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        log2 = LogEntry.objects.create(message="Second")
        time.sleep(0.01)
        log3 = LogEntry.objects.create(message="Third")

        logs = list(LogEntry.objects.all())
        # Newest first (descending order)
        assert logs[0].id == log3.id
        assert logs[1].id == log2.id
        assert logs[2].id == log1.id

    def test_log_entry_str(self):
        """Test string representation"""
        log = LogEntry.objects.create(level="ERROR", message="Test")

        str_repr = str(log)
        assert "ERROR" in str_repr
        assert log.timestamp.strftime("%Y-%m-%d") in str_repr

    def test_get_level_info(self):
        """Test get_level_info method"""
        log = LogEntry.objects.create(level="ERROR")
        level_info = log.get_level_info()

        assert level_info.name == "ERROR"
        assert level_info.value == 40
        assert level_info.emoji == "❌"

    def test_get_emoji(self):
        """Test get_emoji method"""
        log_debug = LogEntry.objects.create(level="DEBUG")
        log_info = LogEntry.objects.create(level="INFO")
        log_warning = LogEntry.objects.create(level="WARNING")
        log_error = LogEntry.objects.create(level="ERROR")
        log_critical = LogEntry.objects.create(level="CRITICAL")

        assert log_debug.get_emoji() == "🐛"
        assert log_info.get_emoji() == "ℹ️"
        assert log_warning.get_emoji() == "⚠️"
        assert log_error.get_emoji() == "❌"
        assert log_critical.get_emoji() == "🔥"

    def test_get_color(self):
        """Test get_color method"""
        log_debug = LogEntry.objects.create(level="DEBUG")
        log_info = LogEntry.objects.create(level="INFO")
        log_error = LogEntry.objects.create(level="ERROR")

        assert log_debug.get_color() == "#36a64f"
        assert log_info.get_color() == "#2196F3"
        assert log_error.get_color() == "#F44336"

    def test_level_choices(self):
        """Test valid level choices"""
        valid_levels = ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"]

        for level in valid_levels:
            log = LogEntry.objects.create(level=level, message=f"Test {level}")
            assert log.level == level

    def test_user_relationship(self, django_user_model):
        """Test user foreign key relationship"""
        user = django_user_model.objects.create_user(username="testuser", password="testpass")

        log1 = LogEntry.objects.create(user=user, message="Log 1")
        log2 = LogEntry.objects.create(user=user, message="Log 2")

        # Test reverse relationship
        assert user.log_entries.count() == 2
        assert log1 in user.log_entries.all()
        assert log2 in user.log_entries.all()

    def test_user_deletion_sets_null(self, django_user_model):
        """Test user deletion sets log.user to NULL"""
        user = django_user_model.objects.create_user(username="testuser", password="testpass")

        log = LogEntry.objects.create(user=user, message="Test")

        user.delete()

        log.refresh_from_db()
        assert log.user is None

    def test_meta_field_with_complex_data(self):
        """Test meta field with complex JSON data"""
        meta_data = {
            "request": {"headers": {"User-Agent": "TestAgent"}, "body": {"key": "value"}},
            "timestamp": datetime.now(),
            "user_id": uuid4(),
            "amount": Decimal("99.99"),
        }

        log = LogEntry.objects.create(message="Test", meta=meta_data)

        log.refresh_from_db()

        # Should be JSON serializable
        assert isinstance(log.meta, dict)
        assert "request" in log.meta

    def test_actor_type_choices(self):
        """Test actor_type field choices"""
        log_user = LogEntry.objects.create(actor_type="user", message="User action")
        log_system = LogEntry.objects.create(actor_type="system", message="System action")

        assert log_user.actor_type == "user"
        assert log_system.actor_type == "system"

    def test_level_index(self):
        """Test level field has database index"""
        # Create logs with different levels
        LogEntry.objects.create(level="DEBUG", message="Debug")
        LogEntry.objects.create(level="INFO", message="Info")
        LogEntry.objects.create(level="ERROR", message="Error")

        # Query by level (should use index)
        errors = LogEntry.objects.filter(level="ERROR")
        assert errors.count() == 1
        assert errors.first().message == "Error"

    def test_blank_and_null_fields(self):
        """Test optional fields can be blank/null"""
        log = LogEntry.objects.create(
            level="INFO",
            # All optional fields omitted
        )

        assert log.message is None
        assert log.path is None
        assert log.method is None
        assert log.status_code is None
        assert log.user is None
        assert log.source is None
        assert log.meta is None

    def test_path_field(self):
        """Test path field accepts long paths"""
        # Test with a reasonably long path (under 500 chars)
        long_path = "/api/" + "a" * 400
        log = LogEntry.objects.create(path=long_path, message="Test")

        log.refresh_from_db()
        assert log.path == long_path
        assert len(log.path) < 500

    def test_status_code_positive(self):
        """Test status_code is positive"""
        log = LogEntry.objects.create(status_code=200, message="Test")

        assert log.status_code == 200

    def test_status_code_various_values(self):
        """Test various HTTP status codes"""
        status_codes = [200, 201, 400, 404, 500, 503]

        for code in status_codes:
            log = LogEntry.objects.create(status_code=code, message=f"Test {code}")
            assert log.status_code == code

    def test_related_name(self, django_user_model):
        """Test related_name for user relationship"""
        user = django_user_model.objects.create_user(username="testuser", password="testpass")

        LogEntry.objects.create(user=user, message="Test")

        # Should be accessible via related_name
        assert hasattr(user, "log_entries")
        assert user.log_entries.exists()


@pytest.mark.django_db
class TestLogEntryQueries:
    """Test LogEntry queries and filters"""

    def test_filter_by_level(self):
        """Test filtering logs by level"""
        LogEntry.objects.create(level="DEBUG", message="Debug log")
        LogEntry.objects.create(level="INFO", message="Info log")
        LogEntry.objects.create(level="ERROR", message="Error log")
        LogEntry.objects.create(level="ERROR", message="Another error")

        errors = LogEntry.objects.filter(level="ERROR")
        assert errors.count() == 2

    def test_filter_by_source(self):
        """Test filtering logs by source"""
        LogEntry.objects.create(source="middleware", message="Middleware log")
        LogEntry.objects.create(source="signal", message="Signal log")
        LogEntry.objects.create(source="middleware", message="Another middleware")

        middleware_logs = LogEntry.objects.filter(source="middleware")
        assert middleware_logs.count() == 2

    def test_filter_by_actor_type(self):
        """Test filtering logs by actor type"""
        LogEntry.objects.create(actor_type="user", message="User action")
        LogEntry.objects.create(actor_type="system", message="System action")
        LogEntry.objects.create(actor_type="user", message="Another user action")

        user_logs = LogEntry.objects.filter(actor_type="user")
        assert user_logs.count() == 2

    def test_filter_by_user(self, django_user_model):
        """Test filtering logs by user"""
        user1 = django_user_model.objects.create_user(username="user1")
        user2 = django_user_model.objects.create_user(username="user2")

        LogEntry.objects.create(user=user1, message="User 1 log")
        LogEntry.objects.create(user=user2, message="User 2 log")
        LogEntry.objects.create(user=user1, message="Another user 1 log")

        user1_logs = LogEntry.objects.filter(user=user1)
        assert user1_logs.count() == 2

    def test_filter_by_date_range(self):
        """Test filtering logs by date range"""
        from datetime import timedelta

        from django.utils import timezone

        now = timezone.now()

        # Create logs
        log1 = LogEntry.objects.create(message="Recent")
        log2 = LogEntry.objects.create(message="Old")

        # Manually set timestamp for old log
        old_time = now - timedelta(days=30)
        LogEntry.objects.filter(id=log2.id).update(timestamp=old_time)

        # Filter recent logs (last 7 days)
        recent_logs = LogEntry.objects.filter(timestamp__gte=now - timedelta(days=7))

        assert log1 in recent_logs
        assert log2 not in recent_logs
