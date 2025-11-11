from django.contrib.admin.models import LogEntry as AdminLogEntry
from django.contrib.auth.models import Group, User
from django.test import override_settings

from logmancer.conf import (
    DEFAULTS,
    get,
    get_bool,
    get_dict,
    get_int,
    get_list,
    should_exclude_model,
    should_exclude_path,
)
from logmancer.models import LogEntry


class TestConfDefaults:
    """Test default configuration values"""

    def test_default_values_used(self):
        """Test that default values are returned when no settings are defined"""
        assert get_int("CLEANUP_AFTER_DAYS") == 30
        assert get_bool("ENABLE_MIDDLEWARE") is True
        assert get_bool("AUTO_LOG_EXCEPTIONS") is True
        assert get_bool("ENABLE_NOTIFICATIONS") is False
        assert get_list("LOG_SENSITIVE_KEYS") == ["password", "token", "authorization"]
        assert get("DEFAULT_LOG_LEVEL") == "INFO"
        assert get_dict("NOTIFICATIONS") == {}

    def test_get_list_returns_list(self):
        """Test get_list always returns a list"""
        assert isinstance(get_list("LOG_SENSITIVE_KEYS"), list)
        assert isinstance(get_list("NONEXISTENT_KEY"), list)
        assert get_list("NONEXISTENT_KEY") == []

    def test_get_returns_none_for_missing_key(self):
        """Test get returns None for missing key without default"""
        assert get("NONEXISTENT_KEY") is None

    def test_get_list_with_tuple(self):
        """Test get_list converts tuple to list"""
        with override_settings(LOGMANCER={"LOG_SENSITIVE_KEYS": ("pass", "token")}):
            result = get_list("LOG_SENSITIVE_KEYS")
            assert isinstance(result, list)
            assert result == ["pass", "token"]

    def test_get_list_with_non_list_value(self):
        """Test get_list returns empty list for non-list value"""
        with override_settings(LOGMANCER={"LOG_SENSITIVE_KEYS": "not_a_list"}):
            assert get_list("LOG_SENSITIVE_KEYS") == []


class TestConfCustomSettings:
    """Test custom configuration values"""

    @override_settings(
        LOGMANCER={
            "CLEANUP_AFTER_DAYS": 45,
            "ENABLE_MIDDLEWARE": False,
            "SIGNAL_EXCLUDE_MODELS": ["custom.AppModel", "auth.User"],
        }
    )
    def test_custom_settings_override_defaults(self):
        """Test that custom settings override defaults"""
        assert get_int("CLEANUP_AFTER_DAYS") == 45
        assert get_bool("ENABLE_MIDDLEWARE") is False
        assert "custom.AppModel" in get_list("SIGNAL_EXCLUDE_MODELS")
        assert "auth.User" in get_list("SIGNAL_EXCLUDE_MODELS")

    @override_settings(LOGMANCER={"CLEANUP_AFTER_DAYS": "invalid"})
    def test_get_int_with_invalid_value(self):
        """Test get_int with invalid value returns default"""
        # get_int returns default without warning in current implementation
        result = get_int("CLEANUP_AFTER_DAYS")
        # Should return default value (30) when invalid
        assert result == 30

    @override_settings(LOGMANCER={"CLEANUP_AFTER_DAYS": "45"})
    def test_get_int_with_string_number(self):
        """Test get_int with string returns default (not converted)"""
        # Current implementation doesn't convert strings
        result = get_int("CLEANUP_AFTER_DAYS")
        assert result == 30  # Returns default since "45" is not int

    @override_settings(LOGMANCER={"CLEANUP_AFTER_DAYS": 45.5})
    def test_get_int_with_float(self):
        """Test get_int with float returns default"""
        # Current implementation only accepts int type
        result = get_int("CLEANUP_AFTER_DAYS")
        assert result == 30

    @override_settings(LOGMANCER={})
    def test_get_int_uses_default(self):
        """Test get_int returns default when key not in settings"""
        assert get_int("CLEANUP_AFTER_DAYS") == 30

    @override_settings(LOGMANCER={"NONEXISTENT_INT_KEY": "value"})
    def test_get_int_missing_key_returns_zero(self):
        """Test get_int returns 0 for missing key without default"""
        assert get_int("NONEXISTENT_INT_KEY") == 0


class TestConfGetBool:
    """Test get_bool function"""

    @override_settings(LOGMANCER={"ENABLE_NOTIFICATIONS": True})
    def test_get_bool_true(self):
        """Test get_bool with True value"""
        assert get_bool("ENABLE_NOTIFICATIONS") is True

    @override_settings(LOGMANCER={"ENABLE_NOTIFICATIONS": False})
    def test_get_bool_false(self):
        """Test get_bool with False value"""
        assert get_bool("ENABLE_NOTIFICATIONS") is False

    @override_settings(LOGMANCER={"ENABLE_NOTIFICATIONS": "true"})
    def test_get_bool_with_string(self):
        """Test get_bool with string returns default"""
        # Current implementation doesn't convert strings
        assert get_bool("ENABLE_NOTIFICATIONS") is False  # Returns default

    @override_settings(LOGMANCER={})
    def test_get_bool_uses_default(self):
        """Test get_bool returns default when key not in settings"""
        assert get_bool("ENABLE_MIDDLEWARE") is True
        assert get_bool("ENABLE_NOTIFICATIONS") is False

    @override_settings(LOGMANCER={"NONEXISTENT_BOOL_KEY": 1})
    def test_get_bool_missing_key_returns_none(self):
        """Test get_bool returns None for missing key without default"""
        assert get_bool("NONEXISTENT_BOOL_KEY") is None


class TestConfGetDict:
    """Test get_dict function"""

    @override_settings(LOGMANCER={"NOTIFICATIONS": {"telegram": {"enabled": True}}})
    def test_get_dict_valid(self):
        """Test get_dict with valid dictionary"""
        result = get_dict("NOTIFICATIONS")
        assert isinstance(result, dict)
        assert "telegram" in result
        assert result["telegram"]["enabled"] is True

    @override_settings(LOGMANCER={"NOTIFICATIONS": "invalid"})
    def test_get_dict_invalid_value(self):
        """Test get_dict with invalid value returns default"""
        result = get_dict("NOTIFICATIONS")
        assert result == {}

    @override_settings(LOGMANCER={})
    def test_get_dict_missing_key(self):
        """Test get_dict with missing key returns default"""
        result = get_dict("NOTIFICATIONS")
        assert result == {}

    @override_settings(LOGMANCER={"CUSTOM_DICT": {"key": "value"}})
    def test_get_dict_custom_key(self):
        """Test get_dict with custom key"""
        result = get_dict("CUSTOM_DICT")
        assert result == {"key": "value"}

    def test_get_dict_nonexistent_key_returns_empty_dict(self):
        """Test get_dict returns empty dict for nonexistent key"""
        result = get_dict("NONEXISTENT_DICT_KEY")
        assert result == {}


class TestShouldExcludeModel:
    """Test should_exclude_model function"""

    def test_default_excluded_models(self):
        """Test that default models are excluded"""
        assert should_exclude_model(LogEntry) is True
        assert should_exclude_model(AdminLogEntry) is True

    def test_non_excluded_model(self):
        """Test that non-excluded models are not excluded"""
        assert should_exclude_model(User) is False
        assert should_exclude_model(Group) is False

    @override_settings(LOGMANCER={"SIGNAL_EXCLUDE_MODELS": ["auth.User", "auth.Group"]})
    def test_custom_excluded_models(self):
        """Test custom excluded models"""
        # Custom excluded models
        assert should_exclude_model(User) is True
        assert should_exclude_model(Group) is True

        # Default excluded models should still work
        assert should_exclude_model(LogEntry) is True
        assert should_exclude_model(AdminLogEntry) is True

    @override_settings(LOGMANCER={"SIGNAL_EXCLUDE_MODELS": []})
    def test_empty_custom_exclude_list(self):
        """Test with empty custom exclude list, defaults should still apply"""
        # Default exclusions should still work
        assert should_exclude_model(LogEntry) is True
        assert should_exclude_model(AdminLogEntry) is True
        # User should not be excluded
        assert should_exclude_model(User) is False

    @override_settings(LOGMANCER={"SIGNAL_EXCLUDE_MODELS": ["AUTH.USER"]})
    def test_case_insensitive_exclusion(self):
        """Test that model exclusion is case-insensitive"""
        assert should_exclude_model(User) is True

    @override_settings(LOGMANCER={"SIGNAL_EXCLUDE_MODELS": ["contenttypes.ContentType"]})
    def test_full_model_path_exclusion(self):
        """Test exclusion with full model path"""
        from django.contrib.contenttypes.models import ContentType

        assert should_exclude_model(ContentType) is True


class TestShouldExcludePath:
    """Test should_exclude_path function"""

    @override_settings(LOGMANCER={"PATH_EXCLUDE_PREFIXES": ["/admin/", "/static/", "/media/"]})
    def test_excluded_paths(self):
        """Test that configured paths are excluded"""
        assert should_exclude_path("/admin/") is True
        assert should_exclude_path("/admin/auth/user/") is True
        assert should_exclude_path("/static/css/style.css") is True
        assert should_exclude_path("/media/uploads/file.jpg") is True

    @override_settings(LOGMANCER={"PATH_EXCLUDE_PREFIXES": ["/admin/"]})
    def test_non_excluded_paths(self):
        """Test that non-configured paths are not excluded"""
        assert should_exclude_path("/api/users/") is False
        assert should_exclude_path("/home/") is False
        assert should_exclude_path("/") is False

    @override_settings(LOGMANCER={"PATH_EXCLUDE_PREFIXES": []})
    def test_empty_exclude_list(self):
        """Test with empty exclude list"""
        assert should_exclude_path("/admin/") is False
        assert should_exclude_path("/static/") is False

    def test_default_no_excluded_paths(self):
        """Test default configuration has no excluded paths"""
        assert should_exclude_path("/admin/") is False
        assert should_exclude_path("/any/path/") is False

    @override_settings(LOGMANCER={"PATH_EXCLUDE_PREFIXES": ["/api/v1/", "/api/v2/"]})
    def test_multiple_prefixes(self):
        """Test multiple path prefixes"""
        assert should_exclude_path("/api/v1/users/") is True
        assert should_exclude_path("/api/v2/posts/") is True
        assert should_exclude_path("/api/v3/comments/") is False

    @override_settings(LOGMANCER={"PATH_EXCLUDE_PREFIXES": ["/health"]})
    def test_partial_match(self):
        """Test that partial match works correctly"""
        assert should_exclude_path("/health") is True
        assert should_exclude_path("/health/check") is True
        assert should_exclude_path("/healthy") is True  # starts with /health
        assert should_exclude_path("/api/health") is False  # doesn't start with /health


class TestConfGet:
    """Test generic get function"""

    @override_settings(LOGMANCER={"CUSTOM_KEY": "custom_value"})
    def test_get_custom_setting(self):
        """Test get with custom setting"""
        assert get("CUSTOM_KEY") == "custom_value"

    def test_get_default_value(self):
        """Test get returns default value"""
        assert get("DEFAULT_LOG_LEVEL") == "INFO"
        assert get("CLEANUP_AFTER_DAYS") == 30

    def test_get_missing_key(self):
        """Test get returns None for missing key"""
        assert get("NONEXISTENT_KEY") is None

    @override_settings(LOGMANCER={"ENABLE_MIDDLEWARE": False})
    def test_get_boolean_value(self):
        """Test get with boolean value"""
        assert get("ENABLE_MIDDLEWARE") is False

    @override_settings(LOGMANCER={"CLEANUP_AFTER_DAYS": 60})
    def test_get_integer_value(self):
        """Test get with integer value"""
        assert get("CLEANUP_AFTER_DAYS") == 60


class TestDefaultsConstant:
    """Test DEFAULTS constant"""

    def test_defaults_contains_required_keys(self):
        """Test that DEFAULTS contains all required keys"""
        required_keys = [
            "LOG_SENSITIVE_KEYS",
            "ENABLE_MIDDLEWARE",
            "AUTO_LOG_EXCEPTIONS",
            "CLEANUP_AFTER_DAYS",
            "SIGNAL_EXCLUDE_MODELS",
            "PATH_EXCLUDE_PREFIXES",
            "DEFAULT_LOG_LEVEL",
            "NOTIFICATIONS",
            "ENABLE_NOTIFICATIONS",
        ]
        for key in required_keys:
            assert key in DEFAULTS

    def test_defaults_types(self):
        """Test that DEFAULTS values have correct types"""
        assert isinstance(DEFAULTS["LOG_SENSITIVE_KEYS"], list)
        assert isinstance(DEFAULTS["ENABLE_MIDDLEWARE"], bool)
        assert isinstance(DEFAULTS["AUTO_LOG_EXCEPTIONS"], bool)
        assert isinstance(DEFAULTS["CLEANUP_AFTER_DAYS"], int)
        assert isinstance(DEFAULTS["SIGNAL_EXCLUDE_MODELS"], list)
        assert isinstance(DEFAULTS["PATH_EXCLUDE_PREFIXES"], list)
        assert isinstance(DEFAULTS["DEFAULT_LOG_LEVEL"], str)
        assert isinstance(DEFAULTS["NOTIFICATIONS"], dict)
        assert isinstance(DEFAULTS["ENABLE_NOTIFICATIONS"], bool)

    def test_defaults_values(self):
        """Test specific default values"""
        assert DEFAULTS["CLEANUP_AFTER_DAYS"] == 30
        assert DEFAULTS["ENABLE_MIDDLEWARE"] is True
        assert DEFAULTS["AUTO_LOG_EXCEPTIONS"] is False
        assert DEFAULTS["ENABLE_NOTIFICATIONS"] is False
        assert DEFAULTS["DEFAULT_LOG_LEVEL"] == "INFO"
        assert "logmancer.LogEntry" in DEFAULTS["SIGNAL_EXCLUDE_MODELS"]
        assert "admin.LogEntry" in DEFAULTS["SIGNAL_EXCLUDE_MODELS"]
