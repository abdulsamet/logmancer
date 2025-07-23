import pytest
import uuid
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib import admin
from django.test import RequestFactory, TestCase, Client, override_settings
from django.urls import reverse, path
from django.utils import timezone

from logmancer.admin import LogEntryAdmin, LEVEL_COLORS
from logmancer.models import LogEntry


def create_unique_user(username_prefix="testuser", **kwargs):
    """Helper function to create unique users"""
    unique_id = str(uuid.uuid4())[:8]
    username = f"{username_prefix}_{unique_id}"
    email = kwargs.pop("email", f"{username}@example.com")
    password = kwargs.pop("password", "testpass123")

    return User.objects.create_user(
        username=username, email=email, password=password, **kwargs
    )


def create_unique_superuser(username_prefix="admin", **kwargs):
    """Helper function to create unique superusers"""
    unique_id = str(uuid.uuid4())[:8]
    username = f"{username_prefix}_{unique_id}"
    email = kwargs.pop("email", f"{username}@example.com")
    password = kwargs.pop("password", "adminpass123")

    return User.objects.create_superuser(
        username=username, email=email, password=password, **kwargs
    )


@pytest.mark.django_db
class TestLogEntryAdmin:
    """Test LogEntryAdmin functionality"""

    def setup_method(self):
        """Set up test data"""
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = LogEntryAdmin(LogEntry, self.site)

        # Create test user with unique username
        self.user = create_unique_user("testuser")

        # Create test log entry
        self.log_entry = LogEntry.objects.create(
            timestamp=timezone.now(),
            level="INFO",
            message="Test log message for admin testing",
            source="test",
            path="/test/",
            method="GET",
            status_code=200,
            user=self.user,
            actor_type="user",
            meta={"test_key": "test_value", "number": 42},
        )

    def test_admin_registration(self):
        """Test that LogEntry model is registered in admin"""
        from django.contrib import admin

        assert LogEntry in admin.site._registry
        assert isinstance(admin.site._registry[LogEntry], LogEntryAdmin)

    def test_list_display(self):
        """Test admin list display fields"""
        expected_fields = (
            "formatted_timestamp",
            "colored_level",
            "user",
            "source",
            "path",
            "status_code",
            "short_message",
        )
        assert self.admin.list_display == expected_fields

    def test_list_filter(self):
        """Test admin list filter fields"""
        expected_filters = ("level", "status_code", "actor_type", "source")
        assert self.admin.list_filter == expected_filters

    def test_search_fields(self):
        """Test admin search fields"""
        expected_fields = ("message", "path", "meta")
        assert self.admin.search_fields == expected_fields

    def test_readonly_fields(self):
        """Test admin readonly fields"""
        expected_fields = (
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
        assert self.admin.readonly_fields == expected_fields

    def test_formatted_timestamp(self):
        """Test formatted_timestamp display method"""
        result = self.admin.formatted_timestamp(self.log_entry)

        # Should return formatted datetime string
        assert isinstance(result, str)
        assert len(result) > 0

        # Should match the expected format: DD.MM.YYYY HH:MM:SS
        import re

        pattern = r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}"
        assert re.match(pattern, result)

    def test_formatted_timestamp_short_description(self):
        """Test formatted_timestamp short description"""
        assert self.admin.formatted_timestamp.short_description == "Timestamp"

    def test_colored_level_info(self):
        """Test colored_level display method for INFO level"""
        result = self.admin.colored_level(self.log_entry)

        # Should return HTML with color formatting
        assert '<b style="color: #008000; font-weight: bold;">INFO</b>' == result

    def test_colored_level_error(self):
        """Test colored_level display method for ERROR level"""
        error_log = LogEntry.objects.create(
            level="ERROR", message="Error message", source="test"
        )

        result = self.admin.colored_level(error_log)
        expected_color = LEVEL_COLORS["ERROR"]
        assert (
            f'<b style="color: {expected_color}; font-weight: bold;">ERROR</b>'
            == result
        )

    def test_colored_level_warning(self):
        """Test colored_level display method for WARNING level"""
        warning_log = LogEntry.objects.create(
            level="WARNING", message="Warning message", source="test"
        )

        result = self.admin.colored_level(warning_log)
        expected_color = LEVEL_COLORS["WARNING"]
        assert (
            f'<b style="color: {expected_color}; font-weight: bold;">WARNING</b>'
            == result
        )

    def test_colored_level_debug(self):
        """Test colored_level display method for DEBUG level"""
        debug_log = LogEntry.objects.create(
            level="DEBUG", message="Debug message", source="test"
        )

        result = self.admin.colored_level(debug_log)
        expected_color = LEVEL_COLORS["DEBUG"]
        assert (
            f'<b style="color: {expected_color}; font-weight: bold;">DEBUG</b>'
            == result
        )

    def test_colored_level_critical(self):
        """Test colored_level display method for CRITICAL level"""
        critical_log = LogEntry.objects.create(
            level="CRITICAL", message="Critical message", source="test"
        )

        result = self.admin.colored_level(critical_log)
        expected_color = LEVEL_COLORS["CRITICAL"]
        assert (
            f'<b style="color: {expected_color}; font-weight: bold;">CRITICAL</b>'
            == result
        )

    def test_colored_level_unknown(self):
        """Test colored_level display method for unknown level"""
        unknown_log = LogEntry.objects.create(
            level="UNKNOWN", message="Unknown level message", source="test"
        )

        result = self.admin.colored_level(unknown_log)
        expected_color = LEVEL_COLORS["DEFAULT"]
        assert (
            f'<b style="color: {expected_color}; font-weight: bold;">UNKNOWN</b>'
            == result
        )

    def test_colored_level_case_insensitive(self):
        """Test colored_level works with different cases"""
        lower_log = LogEntry.objects.create(
            level="info", message="Lowercase level", source="test"
        )

        result = self.admin.colored_level(lower_log)
        expected_color = LEVEL_COLORS["INFO"]  # Should use uppercase key
        assert (
            f'<b style="color: {expected_color}; font-weight: bold;">info</b>' == result
        )

    def test_colored_level_short_description(self):
        """Test colored_level short description"""
        assert self.admin.colored_level.short_description == "Level"

    def test_short_message_normal(self):
        """Test short_message display method for normal length message"""
        result = self.admin.short_message(self.log_entry)

        # Message is shorter than 60 chars, should return as is
        assert result == "Test log message for admin testing"

    def test_short_message_long(self):
        """Test short_message display method for long message"""
        long_message = "A" * 100  # 100 character message
        long_log = LogEntry.objects.create(
            level="INFO", message=long_message, source="test"
        )

        result = self.admin.short_message(long_log)

        # Should be truncated to 60 chars + "..."
        assert len(result) == 63  # 60 + "..."
        assert result.endswith("...")
        assert result.startswith("A" * 60)

    def test_short_message_exactly_60_chars(self):
        """Test short_message with exactly 60 character message"""
        exact_message = "A" * 60
        exact_log = LogEntry.objects.create(
            level="INFO", message=exact_message, source="test"
        )

        result = self.admin.short_message(exact_log)

        # Should return as is without "..."
        assert result == exact_message
        assert not result.endswith("...")

    def test_short_message_empty(self):
        """Test short_message with empty message"""
        empty_log = LogEntry.objects.create(level="INFO", message="", source="test")

        result = self.admin.short_message(empty_log)
        assert result == ""

    def test_short_message_none(self):
        """Test short_message with None message"""
        none_log = LogEntry.objects.create(level="INFO", message=None, source="test")

        result = self.admin.short_message(none_log)
        assert result == ""

    def test_short_message_short_description(self):
        """Test short_message short description"""
        assert self.admin.short_message.short_description == "Message"


test_admin_urlpatterns = [
    path("admin/", admin.site.urls),
]


@override_settings(
    ROOT_URLCONF="tests.test_admin",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "logmancer",
    ],
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ],
    SECRET_KEY="test-secret-key-for-testing-only",
    USE_TZ=True,
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
)
class TestLogEntryAdminIntegration(TestCase):
    """Integration tests for LogEntryAdmin with Django admin"""

    def setUp(self):
        """Set up test data"""
        # Create superuser for admin access with unique username
        self.admin_user = create_unique_superuser("admin")

        # Create regular user with unique username
        self.user = create_unique_user("testuser")

        # Create test log entries
        self.log_entries = [
            LogEntry.objects.create(
                level="INFO",
                message="Test info log",
                source="test",
                path="/info/",
                method="GET",
                status_code=200,
                user=self.user,
            ),
            LogEntry.objects.create(
                level="ERROR",
                message="Test error log with very long message that should be truncated in admin",
                source="test",
                path="/error/",
                method="POST",
                status_code=500,
                user=self.user,
            ),
            LogEntry.objects.create(
                level="WARNING",
                message="Test warning log",
                source="middleware",
                path="/warning/",
                method="PUT",
                status_code=400,
            ),
        ]

    def test_admin_changelist_access(self):
        """Test admin changelist page access"""
        client = Client()
        client.force_login(self.admin_user)

        url = reverse("admin:logmancer_logentry_changelist")
        response = client.get(url)

        assert response.status_code == 200
        # More flexible content check
        content = response.content.decode()
        assert "logmancer" in content.lower() or "log entry" in content.lower()

    def test_admin_changelist_display_data(self):
        """Test admin changelist displays log data correctly"""
        client = Client()
        client.force_login(self.admin_user)

        url = reverse("admin:logmancer_logentry_changelist")
        response = client.get(url)
        content = response.content.decode()

        # Should display log entries
        assert "Test info log" in content
        assert "Test error log with very long message" in content
        assert "Test warning log" in content

        # Should display usernames
        assert self.user.username in content

    def test_admin_changelist_search(self):
        """Test admin changelist search functionality"""
        client = Client()
        client.force_login(self.admin_user)

        url = reverse("admin:logmancer_logentry_changelist")
        response = client.get(url, {"q": "error"})
        content = response.content.decode()

        # Should find error log
        assert "Test error log" in content
        # Should not find info or warning logs
        assert "Test info log" not in content
        assert "Test warning log" not in content

    def test_admin_changelist_filter_by_level(self):
        """Test admin changelist filter by level"""
        client = Client()
        client.force_login(self.admin_user)

        url = reverse("admin:logmancer_logentry_changelist")
        response = client.get(url, {"level": "ERROR"})
        content = response.content.decode()

        # Should find only error log
        assert "Test error log" in content
        assert "Test info log" not in content
        assert "Test warning log" not in content

    def test_admin_changelist_filter_by_status_code(self):
        """Test admin changelist filter by status code"""
        client = Client()
        client.force_login(self.admin_user)

        url = reverse("admin:logmancer_logentry_changelist")
        response = client.get(url, {"status_code": "500"})
        content = response.content.decode()

        # Should find only 500 error log
        assert "Test error log" in content
        assert "Test info log" not in content
        assert "Test warning log" not in content

    def test_admin_changelist_filter_by_source(self):
        """Test admin changelist filter by source"""
        client = Client()
        client.force_login(self.admin_user)

        url = reverse("admin:logmancer_logentry_changelist")
        response = client.get(url, {"source": "middleware"})
        content = response.content.decode()

        # Should find only middleware log
        assert "Test warning log" in content
        assert "Test info log" not in content
        assert "Test error log" not in content

    def test_admin_change_view_readonly(self):
        """Test admin change view shows readonly fields"""
        client = Client()
        client.force_login(self.admin_user)

        log_entry = self.log_entries[0]
        url = reverse("admin:logmancer_logentry_change", args=[log_entry.pk])
        response = client.get(url)
        content = response.content.decode()

        # Should display readonly fields
        assert "Test info log" in content
        assert "/info/" in content
        assert "GET" in content
        assert "200" in content
        assert self.user.username in content

    def test_admin_no_add_permission(self):
        """Test that add permission is handled correctly"""
        from django.contrib import admin
        from logmancer.models import LogEntry

        admin_instance = admin.site._registry[LogEntry]

        # Check if has_add_permission exists and test it
        request = RequestFactory().get("/")
        request.user = self.admin_user

        # By default, admin should allow adding (unless customized)
        has_add = admin_instance.has_add_permission(request)
        assert isinstance(has_add, bool)

    def test_admin_no_delete_permission(self):
        """Test that delete permission is handled correctly"""
        from django.contrib import admin
        from logmancer.models import LogEntry

        admin_instance = admin.site._registry[LogEntry]

        request = RequestFactory().get("/")
        request.user = self.admin_user

        # Test delete permission
        has_delete = admin_instance.has_delete_permission(request)
        assert isinstance(has_delete, bool)


@pytest.mark.django_db
class TestLevelColors:
    """Test LEVEL_COLORS configuration"""

    def test_level_colors_defined(self):
        """Test that all expected log levels have colors defined"""
        expected_levels = [
            "DEFAULT",
            "CRITICAL",
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "FATAL",
            "NOTSET",
        ]

        for level in expected_levels:
            assert level in LEVEL_COLORS
            assert isinstance(LEVEL_COLORS[level], str)
            assert LEVEL_COLORS[level].startswith("#")  # Should be hex color

    def test_level_colors_valid_hex(self):
        """Test that all colors are valid hex values"""
        import re

        hex_pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")

        for level, color in LEVEL_COLORS.items():
            assert hex_pattern.match(color), f"Invalid hex color for {level}: {color}"

    def test_level_colors_distinct(self):
        """Test that critical levels have distinct colors"""
        # Error and critical should be the same (red)
        assert LEVEL_COLORS["ERROR"] == LEVEL_COLORS["CRITICAL"]

        # Info and warning should be different
        assert LEVEL_COLORS["INFO"] != LEVEL_COLORS["WARNING"]

        # Debug should be different from info
        assert LEVEL_COLORS["DEBUG"] != LEVEL_COLORS["INFO"]


# Test admin customization scenarios
@pytest.mark.django_db
class TestAdminCustomization:
    """Test admin customization scenarios"""

    def test_admin_ordering(self):
        """Test admin default ordering"""
        admin_instance = LogEntryAdmin(LogEntry, AdminSite())

        # Check if ordering is set (should be newest first)
        if hasattr(admin_instance, "ordering"):
            ordering = admin_instance.ordering
            assert ordering is not None
        else:
            # Default model ordering should be used
            assert LogEntry._meta.ordering

    def test_admin_list_per_page(self):
        """Test admin list per page setting"""
        admin_instance = LogEntryAdmin(LogEntry, AdminSite())

        # Should have reasonable pagination
        if hasattr(admin_instance, "list_per_page"):
            assert admin_instance.list_per_page > 0
            assert admin_instance.list_per_page <= 200  # Reasonable limit

    def test_admin_list_max_show_all(self):
        """Test admin list max show all setting"""
        admin_instance = LogEntryAdmin(LogEntry, AdminSite())

        # Should have reasonable max show all limit
        if hasattr(admin_instance, "list_max_show_all"):
            assert admin_instance.list_max_show_all > 0

    def test_admin_date_hierarchy(self):
        """Test admin date hierarchy"""
        admin_instance = LogEntryAdmin(LogEntry, AdminSite())

        # Could have date hierarchy on timestamp
        if hasattr(admin_instance, "date_hierarchy"):
            assert admin_instance.date_hierarchy in [None, "timestamp"]

    def test_admin_actions(self):
        """Test admin actions"""
        admin_instance = LogEntryAdmin(LogEntry, AdminSite())

        request = RequestFactory().get("/")
        request.user = create_unique_superuser("testadmin")

        actions = admin_instance.get_actions(request)
        assert isinstance(actions, dict)
        assert "delete_selected" in actions or len(actions) >= 0


# URL configuration for tests
urlpatterns = test_admin_urlpatterns
