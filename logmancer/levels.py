from enum import Enum
from typing import Dict, NamedTuple


class LevelInfo(NamedTuple):
    """Log level information"""

    name: str
    value: int
    color: str
    emoji: str
    slack_color: str
    css_class: str


class LogLevel(Enum):
    """Centralized log level definitions with all metadata"""

    NOTSET = LevelInfo(
        name="NOTSET",
        value=0,
        color="#808080",
        emoji="⚪",
        slack_color="#808080",
        css_class="log-notset",
    )

    DEBUG = LevelInfo(
        name="DEBUG",
        value=10,
        color="#36a64f",
        emoji="🐛",
        slack_color="#36a64f",
        css_class="log-debug",
    )

    INFO = LevelInfo(
        name="INFO", value=20, color="#2196F3", emoji="ℹ️", slack_color="good", css_class="log-info"
    )

    WARNING = LevelInfo(
        name="WARNING",
        value=30,
        color="#FFC107",
        emoji="⚠️",
        slack_color="warning",
        css_class="log-warning",
    )

    ERROR = LevelInfo(
        name="ERROR",
        value=40,
        color="#F44336",
        emoji="❌",
        slack_color="danger",
        css_class="log-error",
    )

    CRITICAL = LevelInfo(
        name="CRITICAL",
        value=50,
        color="#9C27B0",
        emoji="🔥",
        slack_color="danger",
        css_class="log-critical",
    )

    FATAL = LevelInfo(
        name="FATAL",
        value=50,
        color="#9C27B0",
        emoji="💀",
        slack_color="danger",
        css_class="log-fatal",
    )

    @classmethod
    def from_name(cls, name: str) -> "LogLevel":
        """Get LogLevel from name string"""
        name_upper = name.upper()
        for level in cls:
            if level.value.name == name_upper:
                return level
        raise ValueError(f"Unknown log level: {name}")

    @classmethod
    def from_value(cls, value: int) -> "LogLevel":
        """Get LogLevel from numeric value"""
        for level in cls:
            if level.value.value == value:
                return level
        raise ValueError(f"Unknown log level value: {value}")

    @classmethod
    def get_choices(cls):
        """Get choices for Django model field"""
        return [(level.value.name, level.value.name) for level in cls]

    @classmethod
    def get_level_map(cls) -> Dict[str, int]:
        """Get name to value mapping"""
        return {level.value.name: level.value.value for level in cls}

    @classmethod
    def compare_levels(cls, level1: str, level2: str) -> int:
        """Compare two log levels. Returns -1, 0, or 1"""
        try:
            l1 = cls.from_name(level1)
            l2 = cls.from_name(level2)
            if l1 < l2:
                return -1
            elif l1 > l2:
                return 1
            return 0
        except ValueError:
            return 0

    @classmethod
    def should_log(cls, current_level: str, min_level: str) -> bool:
        try:
            return cls.from_name(current_level) >= cls.from_name(min_level)
        except ValueError:
            return False

    @property
    def emoji(self) -> str:
        return self.value.emoji

    @property
    def color(self) -> str:
        return self.value.color

    @property
    def slack_color(self) -> str:
        return self.value.slack_color

    @property
    def css_class(self) -> str:
        return self.value.css_class

    def __str__(self):
        return self.value.name

    def __lt__(self, other):
        """Allow level comparison"""
        if isinstance(other, LogLevel):
            return self.value.value < other.value.value
        return NotImplemented

    def __gt__(self, other):
        """Allow level comparison"""
        if isinstance(other, LogLevel):
            return self.value.value > other.value.value
        return NotImplemented

    def __le__(self, other):
        """Allow level comparison"""
        if isinstance(other, LogLevel):
            return self.value.value <= other.value.value
        return NotImplemented

    def __ge__(self, other):
        """Allow level comparison"""
        if isinstance(other, LogLevel):
            return self.value.value >= other.value.value
        return NotImplemented
