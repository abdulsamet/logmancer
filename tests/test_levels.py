import pytest

from logmancer.levels import LevelInfo, LogLevel


class TestLevelInfo:
    """Test LevelInfo NamedTuple"""

    def test_level_info_creation(self):
        """Test LevelInfo can be created with all fields"""
        info = LevelInfo(
            name="TEST",
            value=99,
            color="#FFFFFF",
            emoji="🧪",
            slack_color="good",
            css_class="log-test",
        )

        assert info.name == "TEST"
        assert info.value == 99
        assert info.color == "#FFFFFF"
        assert info.emoji == "🧪"
        assert info.slack_color == "good"
        assert info.css_class == "log-test"

    def test_level_info_immutable(self):
        """Test LevelInfo is immutable"""
        info = LevelInfo(
            name="TEST",
            value=99,
            color="#FFFFFF",
            emoji="🧪",
            slack_color="good",
            css_class="log-test",
        )

        with pytest.raises(AttributeError):
            info.name = "CHANGED"


class TestLogLevel:
    """Test LogLevel enum"""

    def test_all_levels_exist(self):
        """Test all expected log levels exist"""
        expected_levels = ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"]

        for level_name in expected_levels:
            assert hasattr(LogLevel, level_name)
            level = getattr(LogLevel, level_name)
            assert isinstance(level.value, LevelInfo)

    def test_level_values(self):
        """Test log level numeric values"""
        assert LogLevel.NOTSET.value.value == 0
        assert LogLevel.DEBUG.value.value == 10
        assert LogLevel.INFO.value.value == 20
        assert LogLevel.WARNING.value.value == 30
        assert LogLevel.ERROR.value.value == 40
        assert LogLevel.CRITICAL.value.value == 50
        assert LogLevel.FATAL.value.value == 50

    def test_level_names(self):
        """Test log level names"""
        assert LogLevel.DEBUG.value.name == "DEBUG"
        assert LogLevel.INFO.value.name == "INFO"
        assert LogLevel.WARNING.value.name == "WARNING"
        assert LogLevel.ERROR.value.name == "ERROR"
        assert LogLevel.CRITICAL.value.name == "CRITICAL"

    def test_level_colors(self):
        """Test log level colors are defined"""
        for level in LogLevel:
            assert level.value.color.startswith("#") or level.value.color
            assert len(level.value.color) > 0

    def test_level_emojis(self):
        """Test log level emojis are defined"""
        expected_emojis = {
            "NOTSET": "⚪",
            "DEBUG": "🐛",
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🔥",
            "FATAL": "💀",
        }

        for level_name, emoji in expected_emojis.items():
            level = getattr(LogLevel, level_name)
            assert level.value.emoji == emoji

    def test_level_slack_colors(self):
        """Test Slack colors are defined"""
        assert LogLevel.INFO.value.slack_color == "good"
        assert LogLevel.WARNING.value.slack_color == "warning"
        assert LogLevel.ERROR.value.slack_color == "danger"
        assert LogLevel.CRITICAL.value.slack_color == "danger"

    def test_level_css_classes(self):
        """Test CSS classes are defined"""
        assert LogLevel.DEBUG.value.css_class == "log-debug"
        assert LogLevel.INFO.value.css_class == "log-info"
        assert LogLevel.WARNING.value.css_class == "log-warning"
        assert LogLevel.ERROR.value.css_class == "log-error"
        assert LogLevel.CRITICAL.value.css_class == "log-critical"


class TestLogLevelClassMethods:
    """Test LogLevel class methods"""

    def test_from_name_valid(self):
        """Test from_name with valid names"""
        assert LogLevel.from_name("DEBUG") == LogLevel.DEBUG
        assert LogLevel.from_name("debug") == LogLevel.DEBUG
        assert LogLevel.from_name("INFO") == LogLevel.INFO
        assert LogLevel.from_name("warning") == LogLevel.WARNING
        assert LogLevel.from_name("ERROR") == LogLevel.ERROR

    def test_from_name_invalid(self):
        """Test from_name with invalid name"""
        with pytest.raises(ValueError, match="Unknown log level"):
            LogLevel.from_name("INVALID")

    def test_from_value_valid(self):
        """Test from_value with valid values"""
        assert LogLevel.from_value(0) == LogLevel.NOTSET
        assert LogLevel.from_value(10) == LogLevel.DEBUG
        assert LogLevel.from_value(20) == LogLevel.INFO
        assert LogLevel.from_value(30) == LogLevel.WARNING
        assert LogLevel.from_value(40) == LogLevel.ERROR
        assert LogLevel.from_value(50) == LogLevel.CRITICAL

    def test_from_value_invalid(self):
        """Test from_value with invalid value"""
        with pytest.raises(ValueError, match="Unknown log level value"):
            LogLevel.from_value(999)

    def test_get_choices(self):
        """Test get_choices returns proper Django choices"""
        choices = LogLevel.get_choices()

        assert isinstance(choices, list)
        assert len(choices) == 7  # All levels

        # Check format
        for choice in choices:
            assert isinstance(choice, tuple)
            assert len(choice) == 2
            assert isinstance(choice[0], str)
            assert isinstance(choice[1], str)

        # Check specific values
        assert ("DEBUG", "DEBUG") in choices
        assert ("INFO", "INFO") in choices
        assert ("ERROR", "ERROR") in choices

    def test_get_level_map(self):
        """Test get_level_map returns correct mapping"""
        level_map = LogLevel.get_level_map()

        assert isinstance(level_map, dict)
        assert level_map["NOTSET"] == 0
        assert level_map["DEBUG"] == 10
        assert level_map["INFO"] == 20
        assert level_map["WARNING"] == 30
        assert level_map["ERROR"] == 40
        assert level_map["CRITICAL"] == 50

    def test_compare_levels_less_than(self):
        """Test compare_levels with less than"""
        assert LogLevel.compare_levels("DEBUG", "INFO") == -1
        assert LogLevel.compare_levels("INFO", "WARNING") == -1
        assert LogLevel.compare_levels("WARNING", "ERROR") == -1

    def test_compare_levels_equal(self):
        """Test compare_levels with equal"""
        assert LogLevel.compare_levels("DEBUG", "DEBUG") == 0
        assert LogLevel.compare_levels("INFO", "INFO") == 0
        assert LogLevel.compare_levels("ERROR", "ERROR") == 0

    def test_compare_levels_greater_than(self):
        """Test compare_levels with greater than"""
        assert LogLevel.compare_levels("ERROR", "WARNING") == 1
        assert LogLevel.compare_levels("WARNING", "INFO") == 1
        assert LogLevel.compare_levels("INFO", "DEBUG") == 1

    def test_compare_levels_invalid(self):
        """Test compare_levels with invalid levels"""
        assert LogLevel.compare_levels("INVALID", "DEBUG") == 0
        assert LogLevel.compare_levels("DEBUG", "INVALID") == 0

    def test_should_log_true(self):
        """Test should_log returns True when level is high enough"""
        assert LogLevel.should_log("ERROR", "WARNING") is True
        assert LogLevel.should_log("CRITICAL", "ERROR") is True
        assert LogLevel.should_log("ERROR", "ERROR") is True
        assert LogLevel.should_log("WARNING", "DEBUG") is True

    def test_should_log_false(self):
        """Test should_log returns False when level is too low"""
        assert LogLevel.should_log("DEBUG", "INFO") is False
        assert LogLevel.should_log("INFO", "WARNING") is False
        assert LogLevel.should_log("WARNING", "ERROR") is False

    def test_should_log_invalid(self):
        """Test should_log with invalid levels"""
        assert LogLevel.should_log("INVALID", "DEBUG") is False
        assert LogLevel.should_log("DEBUG", "INVALID") is False


class TestLogLevelProperties:
    """Test LogLevel instance properties"""

    def test_emoji_property(self):
        """Test emoji property"""
        assert LogLevel.DEBUG.emoji == "🐛"
        assert LogLevel.INFO.emoji == "ℹ️"
        assert LogLevel.WARNING.emoji == "⚠️"
        assert LogLevel.ERROR.emoji == "❌"
        assert LogLevel.CRITICAL.emoji == "🔥"

    def test_color_property(self):
        """Test color property"""
        assert LogLevel.DEBUG.color == "#36a64f"
        assert LogLevel.INFO.color == "#2196F3"
        assert LogLevel.WARNING.color == "#FFC107"
        assert LogLevel.ERROR.color == "#F44336"
        assert LogLevel.CRITICAL.color == "#9C27B0"

    def test_slack_color_property(self):
        """Test slack_color property"""
        assert LogLevel.INFO.slack_color == "good"
        assert LogLevel.WARNING.slack_color == "warning"
        assert LogLevel.ERROR.slack_color == "danger"

    def test_css_class_property(self):
        """Test css_class property"""
        assert LogLevel.DEBUG.css_class == "log-debug"
        assert LogLevel.INFO.css_class == "log-info"
        assert LogLevel.ERROR.css_class == "log-error"


class TestLogLevelComparisons:
    """Test LogLevel comparison operators"""

    def test_less_than(self):
        """Test less than operator"""
        assert LogLevel.DEBUG < LogLevel.INFO
        assert LogLevel.INFO < LogLevel.WARNING
        assert LogLevel.WARNING < LogLevel.ERROR
        assert LogLevel.ERROR < LogLevel.CRITICAL

    def test_less_than_with_non_loglevel(self):
        """Test less than with non-LogLevel returns NotImplemented"""
        result = LogLevel.DEBUG.__lt__(42)
        assert result == NotImplemented

        result = LogLevel.ERROR.__lt__("ERROR")
        assert result == NotImplemented

        result = LogLevel.INFO.__lt__(None)
        assert result == NotImplemented

    def test_less_than_with_non_loglevel_raises_typeerror(self):
        """Test less than with non-LogLevel raises TypeError in comparison"""
        with pytest.raises(TypeError):
            LogLevel.DEBUG < 42

        with pytest.raises(TypeError):
            LogLevel.ERROR < "ERROR"

    def test_greater_than(self):
        """Test greater than operator"""
        assert LogLevel.ERROR > LogLevel.WARNING
        assert LogLevel.WARNING > LogLevel.INFO
        assert LogLevel.INFO > LogLevel.DEBUG
        assert LogLevel.CRITICAL > LogLevel.ERROR

    def test_greater_than_with_non_loglevel(self):
        """Test greater than with non-LogLevel returns NotImplemented"""
        result = LogLevel.ERROR.__gt__(42)
        assert result == NotImplemented

        result = LogLevel.DEBUG.__gt__("DEBUG")
        assert result == NotImplemented

        result = LogLevel.INFO.__gt__(None)
        assert result == NotImplemented

    def test_greater_than_with_non_loglevel_raises_typeerror(self):
        """Test greater than with non-LogLevel raises TypeError in comparison"""
        with pytest.raises(TypeError):
            LogLevel.ERROR > 42

        with pytest.raises(TypeError):
            LogLevel.DEBUG > "DEBUG"

    def test_less_than_or_equal(self):
        """Test less than or equal operator"""
        assert LogLevel.DEBUG <= LogLevel.INFO
        assert LogLevel.DEBUG <= LogLevel.DEBUG
        assert LogLevel.ERROR <= LogLevel.ERROR

    def test_less_than_or_equal_with_non_loglevel(self):
        """Test less than or equal with non-LogLevel returns NotImplemented"""
        result = LogLevel.DEBUG.__le__(42)
        assert result == NotImplemented

        result = LogLevel.ERROR.__le__("ERROR")
        assert result == NotImplemented

    def test_less_than_or_equal_with_non_loglevel_raises_typeerror(self):
        """Test less than or equal with non-LogLevel raises TypeError"""
        with pytest.raises(TypeError):
            LogLevel.DEBUG <= 42

    def test_greater_than_or_equal(self):
        """Test greater than or equal operator"""
        assert LogLevel.ERROR >= LogLevel.WARNING
        assert LogLevel.ERROR >= LogLevel.ERROR
        assert LogLevel.CRITICAL >= LogLevel.CRITICAL

    def test_greater_than_or_equal_with_non_loglevel(self):
        """Test greater than or equal with non-LogLevel returns NotImplemented"""
        result = LogLevel.ERROR.__ge__(42)
        assert result == NotImplemented

        result = LogLevel.DEBUG.__ge__("DEBUG")
        assert result == NotImplemented

    def test_greater_than_or_equal_with_non_loglevel_raises_typeerror(self):
        """Test greater than or equal with non-LogLevel raises TypeError"""
        with pytest.raises(TypeError):
            LogLevel.ERROR >= 42

    def test_equal(self):
        """Test equality"""
        assert LogLevel.DEBUG == LogLevel.DEBUG
        assert LogLevel.INFO == LogLevel.INFO
        assert not (LogLevel.DEBUG == LogLevel.INFO)

    def test_equal_with_non_loglevel(self):
        """Test equality with non-LogLevel types"""
        assert not (LogLevel.DEBUG == 10)
        assert not (LogLevel.ERROR == "ERROR")
        assert LogLevel.INFO is not None
        assert not (LogLevel.WARNING == 30)

    def test_not_equal(self):
        """Test inequality"""
        assert LogLevel.DEBUG != LogLevel.INFO
        assert LogLevel.ERROR != LogLevel.WARNING
        assert not (LogLevel.DEBUG != LogLevel.DEBUG)

    def test_not_equal_with_non_loglevel(self):
        """Test inequality with non-LogLevel types"""
        assert LogLevel.DEBUG != 10
        assert LogLevel.ERROR != "ERROR"
        assert LogLevel.INFO is not None
        assert LogLevel.WARNING != 30

    def test_sorting(self):
        """Test levels can be sorted"""
        levels = [LogLevel.ERROR, LogLevel.DEBUG, LogLevel.WARNING, LogLevel.INFO]
        sorted_levels = sorted(levels)

        assert sorted_levels[0] == LogLevel.DEBUG
        assert sorted_levels[1] == LogLevel.INFO
        assert sorted_levels[2] == LogLevel.WARNING
        assert sorted_levels[3] == LogLevel.ERROR

    def test_comparison_chain(self):
        """Test chained comparisons work correctly"""
        assert LogLevel.DEBUG < LogLevel.INFO < LogLevel.WARNING < LogLevel.ERROR
        assert LogLevel.ERROR > LogLevel.WARNING > LogLevel.INFO > LogLevel.DEBUG


class TestLogLevelStringRepresentation:
    """Test LogLevel string representation"""

    def test_str(self):
        """Test __str__ method"""
        assert str(LogLevel.DEBUG) == "DEBUG"
        assert str(LogLevel.INFO) == "INFO"
        assert str(LogLevel.WARNING) == "WARNING"
        assert str(LogLevel.ERROR) == "ERROR"
        assert str(LogLevel.CRITICAL) == "CRITICAL"

    def test_repr(self):
        """Test __repr__ method"""
        assert "DEBUG" in repr(LogLevel.DEBUG)
        assert "INFO" in repr(LogLevel.INFO)


class TestLogLevelEdgeCases:
    """Test edge cases and special scenarios"""

    def test_critical_and_fatal_same_value(self):
        """Test CRITICAL and FATAL have same numeric value"""
        assert LogLevel.CRITICAL.value.value == LogLevel.FATAL.value.value
        assert LogLevel.CRITICAL.value.value == 50

    def test_critical_and_fatal_different_emoji(self):
        """Test CRITICAL and FATAL have different emojis"""
        assert LogLevel.CRITICAL.emoji != LogLevel.FATAL.emoji
        assert LogLevel.CRITICAL.emoji == "🔥"
        assert LogLevel.FATAL.emoji == "💀"

    def test_critical_and_fatal_comparison(self):
        """Test CRITICAL and FATAL can be compared despite same value"""
        # They have same numeric value, so they're equal in comparison
        assert not (LogLevel.CRITICAL < LogLevel.FATAL)
        assert not (LogLevel.CRITICAL > LogLevel.FATAL)
        assert LogLevel.CRITICAL <= LogLevel.FATAL
        assert LogLevel.CRITICAL >= LogLevel.FATAL

    def test_enum_iteration(self):
        """Test can iterate over all levels"""
        levels = list(LogLevel)
        assert len(levels) == 7
        assert LogLevel.DEBUG in levels
        assert LogLevel.ERROR in levels

    def test_enum_membership(self):
        """Test enum membership"""
        import sys
        
        assert LogLevel.DEBUG in LogLevel
        assert LogLevel.ERROR in LogLevel
        
        # Python 3.11 and earlier: string in enum raises TypeError
        # Python 3.12+: string in enum returns False
        if sys.version_info >= (3, 12):
            assert "DEBUG" not in LogLevel  # String is not a member
        else:
            with pytest.raises(TypeError):
                "DEBUG" in LogLevel

    def test_level_immutability(self):
        """Test enum values cannot be changed"""
        with pytest.raises(AttributeError):
            LogLevel.DEBUG.value = LevelInfo("CHANGED", 99, "#000", "X", "good", "test")


class TestLogLevelIntegration:
    """Test LogLevel integration scenarios"""

    def test_use_in_dict(self):
        """Test LogLevel can be used as dict key"""
        level_counts = {LogLevel.DEBUG: 10, LogLevel.INFO: 20, LogLevel.ERROR: 5}

        assert level_counts[LogLevel.DEBUG] == 10
        assert level_counts[LogLevel.ERROR] == 5

    def test_use_in_set(self):
        """Test LogLevel can be used in set"""
        levels = {LogLevel.DEBUG, LogLevel.INFO, LogLevel.ERROR}

        assert LogLevel.DEBUG in levels
        assert LogLevel.WARNING not in levels

    def test_filter_by_level(self):
        """Test filtering by log level"""
        all_levels = [
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARNING,
            LogLevel.ERROR,
            LogLevel.CRITICAL,
        ]

        # Filter levels >= WARNING
        filtered = [lev for lev in all_levels if lev >= LogLevel.WARNING]

        assert len(filtered) == 3
        assert LogLevel.WARNING in filtered
        assert LogLevel.ERROR in filtered
        assert LogLevel.CRITICAL in filtered
        assert LogLevel.DEBUG not in filtered
