from datetime import datetime
from unittest.mock import Mock

import django
from django.conf import settings

import pytest


def pytest_configure():
    """Configure Django settings for tests"""
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "logmancer",
            ],
            MIDDLEWARE=[
                "logmancer.middleware.LogmancerMiddleware",
            ],
            ROOT_URLCONF="",
            SECRET_KEY="test-secret-key",
            LOGMANCER={
                "ENABLE_LOGGING": True,
                "ENABLE_NOTIFICATIONS": False,
                "RETENTION_DAYS": 30,
            },
        )
        django.setup()


@pytest.fixture
def telegram_config():
    """Telegram notification configuration"""
    return {
        "enabled": True,
        "bot_token": "123456:ABC-DEF",
        "chat_id": "123456",
        "min_level": "ERROR",
        "sources": ["exception"],
    }


@pytest.fixture
def slack_config():
    """Slack notification configuration"""
    return {
        "enabled": True,
        "webhook_url": "https://hooks.slack.com/services/test",
        "min_level": "WARNING",
    }


@pytest.fixture
def email_config():
    """Email notification configuration"""
    return {
        "enabled": True,
        "to_emails": ["test@example.com"],
        "from_email": "noreply@example.com",
        "min_level": "ERROR",
    }


@pytest.fixture
def sample_log_entry():
    """Sample log entry for testing"""
    log_entry = Mock()
    log_entry.level = "INFO"
    log_entry.source = None
    log_entry.path = None
    log_entry.message = "Test log message"
    log_entry.timestamp = datetime.now()
    log_entry.user_id = None
    log_entry.ip_address = "127.0.0.1"
    return log_entry


@pytest.fixture
def mock_user():
    """Create a mock user"""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_authenticated = True
    user.__str__ = Mock(return_value="testuser")
    return user
