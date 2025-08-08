from django.contrib.auth.models import Group, User
from django.test import override_settings

import pytest

from logmancer.conf import get_bool, get_int, get_list, should_exclude_model
from logmancer.models import LogEntry


class TestConfDefaults:
    """Test default configuration values"""

    def test_default_values_used(self):
        """Test that default values are returned when no settings are defined"""
        assert get_int("CLEANUP_AFTER_DAYS") == 30
        assert get_bool("ENABLE_MIDDLEWARE") is True
        assert get_bool("AUTO_LOG_EXCEPTIONS") is True
        assert get_list("LOG_SENSITIVE_KEYS") == ["password", "token", "authorization"]

    def test_get_list_returns_list(self):
        """Test get_list always returns a list"""
        assert isinstance(get_list("LOG_SENSITIVE_KEYS"), list)
        assert isinstance(get_list("NONEXISTENT_KEY"), list)
        assert get_list("NONEXISTENT_KEY") == []


class TestConfCustomSettings:
    """Test custom configuration values"""

    @override_settings(
        LOGMANCER_CLEANUP_AFTER_DAYS=45,
        LOGMANCER_ENABLE_MIDDLEWARE=False,
        LOGMANCER_SIGNAL_EXCLUDE_MODELS=["custom.AppModel", "auth.User"],
    )
    def test_custom_settings_override_defaults(self):
        """Test that custom settings override defaults"""
        assert get_int("CLEANUP_AFTER_DAYS") == 45
        assert get_bool("ENABLE_MIDDLEWARE") is False
        assert "custom.AppModel" in get_list("SIGNAL_EXCLUDE_MODELS")
        assert "auth.User" in get_list("SIGNAL_EXCLUDE_MODELS")

    @override_settings(LOGMANCER_CLEANUP_AFTER_DAYS="invalid")
    def test_get_int_with_invalid_value(self):
        """Test get_int with invalid value returns default"""
        with pytest.warns(UserWarning, match="LOGMANCER_CLEANUP_AFTER_DAYS value is not integer"):
            result = get_int("CLEANUP_AFTER_DAYS")
        assert result == 30  # Default value


class TestShouldExcludeModel:
    """Test should_exclude_model function"""

    def test_default_excluded_models(self):
        """Test that default models are excluded"""
        assert should_exclude_model(LogEntry) is True

    def test_non_excluded_model(self):
        """Test that non-excluded models are not excluded"""
        assert should_exclude_model(User) is False

    @override_settings(LOGMANCER_SIGNAL_EXCLUDE_MODELS=["auth.User", "auth.Group"])
    def test_custom_excluded_models(self):
        """Test custom excluded models"""
        # Custom excluded models
        assert should_exclude_model(User) is True
        assert should_exclude_model(Group) is True

        # Default excluded models should still work
        assert should_exclude_model(LogEntry) is True

    @override_settings(LOGMANCER_SIGNAL_EXCLUDE_MODELS=[])
    def test_empty_custom_exclude_list(self):
        """Test with empty custom exclude list, defaults should still apply"""
        # Default exclusions should still work
        assert should_exclude_model(LogEntry) is True
        # User should not be excluded
        assert should_exclude_model(User) is False
