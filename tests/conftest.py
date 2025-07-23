import os
import sys
import uuid

import django
from django.core.management import call_command
from django.test import Client

import pytest

# Add project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")


def pytest_configure():
    """Configure pytest for Django"""
    django.setup()


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    """Setup Django database with migrations"""
    with django_db_blocker.unblock():
        # Ensure database file exists
        from django.conf import settings

        db_path = settings.DATABASES["default"]["NAME"]
        if hasattr(db_path, "parent"):
            db_path.parent.mkdir(parents=True, exist_ok=True)

        # Run migrations to create tables
        try:
            call_command("migrate", verbosity=1, interactive=False, run_syncdb=True)
            print("Database migrations completed successfully!")
        except Exception as e:
            print(f"Migration failed: {e}")
            # Try to create tables manually if migration fails
            try:
                call_command(
                    "migrate",
                    verbosity=1,
                    interactive=False,
                    run_syncdb=True,
                    fake_initial=True,
                )
                print("Database tables created with fake initial!")
            except Exception as e2:
                print(f"Table creation failed: {e2}")
                raise


@pytest.fixture(scope="session")
def django_db_keepdb():
    """Keep database between test runs"""
    return True


@pytest.fixture
def client():
    """Provide Django test client"""
    return Client()


@pytest.fixture
def user_factory():
    """Factory for creating test users using model_bakery"""
    # Import model_bakery after Django is configured
    from model_bakery import baker
    from django.contrib.auth.models import User

    def _create_user(**kwargs):
        # Set defaults if not provided
        defaults = {
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "is_active": True,
        }
        defaults.update(kwargs)

        # Use model_bakery to create user
        return baker.make(User, **defaults)

    return _create_user


@pytest.fixture
def simple_user_factory():
    """Simple factory for creating users without model_bakery"""
    from django.contrib.auth.models import User

    def _create_user(**kwargs):
        defaults = {
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "testpass123",
        }
        defaults.update(kwargs)

        # Use Django's create_user method
        return User.objects.create_user(**defaults)

    return _create_user


@pytest.fixture
def log_entry_factory():
    """Factory for creating test log entries"""
    # Import model_bakery after Django is configured
    from model_bakery import baker
    from logmancer.models import LogEntry

    def _create_log(**kwargs):
        defaults = {
            "message": f"Test log message {uuid.uuid4().hex[:8]}",
            "level": "INFO",
            "source": "test",
            "path": "/test/",
            "method": "GET",
            "status_code": 200,
            "actor_type": "user",
            "meta": {"test": True},
        }
        defaults.update(kwargs)

        # Use model_bakery to create log entry
        return baker.make(LogEntry, **defaults)

    return _create_log


@pytest.fixture
def simple_log_entry_factory():
    """Simple factory for creating log entries without model_bakery"""
    from logmancer.models import LogEntry

    def _create_log(**kwargs):
        defaults = {
            "message": f"Test log message {uuid.uuid4().hex[:8]}",
            "level": "INFO",
            "source": "test",
            "path": "/test/",
            "method": "GET",
            "status_code": 200,
            "actor_type": "user",
            "meta": {"test": True},
        }
        defaults.update(kwargs)

        # Use Django's create method
        return LogEntry.objects.create(**defaults)

    return _create_log


@pytest.fixture
def group_factory():
    """Factory for creating test groups"""
    # Import model_bakery after Django is configured
    from model_bakery import baker
    from django.contrib.auth.models import Group

    def _create_group(**kwargs):
        defaults = {
            "name": f"test_group_{uuid.uuid4().hex[:8]}",
        }
        defaults.update(kwargs)

        return baker.make(Group, **defaults)

    return _create_group


@pytest.fixture
def transaction_mock():
    """Mock transaction.on_commit for immediate execution"""
    from unittest.mock import patch

    def execute_immediately(func):
        func()

    with patch(
        "logmancer.utils.transaction.on_commit", side_effect=execute_immediately
    ) as mock:
        yield mock


# Additional fixtures for model_bakery
@pytest.fixture
def baker_user():
    """Simple fixture for creating a user with model_bakery"""
    from model_bakery import baker
    from django.contrib.auth.models import User

    return baker.make(User)


@pytest.fixture
def baker_admin_user():
    """Simple fixture for creating an admin user with model_bakery"""
    from model_bakery import baker
    from django.contrib.auth.models import User

    return baker.make(User, is_staff=True, is_superuser=True)


@pytest.fixture
def baker_log_entry():
    """Simple fixture for creating a log entry with model_bakery"""
    from model_bakery import baker
    from logmancer.models import LogEntry

    return baker.make(LogEntry)


@pytest.fixture
def multiple_users():
    """Fixture for creating multiple users at once"""
    from model_bakery import baker
    from django.contrib.auth.models import User

    return baker.make(User, _quantity=5)


@pytest.fixture
def multiple_log_entries():
    """Fixture for creating multiple log entries at once"""
    from model_bakery import baker
    from logmancer.models import LogEntry

    return baker.make(LogEntry, _quantity=10)


@pytest.fixture
def user_with_logs():
    """Fixture for creating a user with associated log entries"""
    from model_bakery import baker
    from django.contrib.auth.models import User
    from logmancer.models import LogEntry

    user = baker.make(User)
    logs = baker.make(LogEntry, user=user, _quantity=3)

    return {"user": user, "logs": logs}


@pytest.fixture
def complete_log_entry():
    """Fixture for creating a complete log entry with all fields"""
    from model_bakery import baker
    from django.contrib.auth.models import User
    from logmancer.models import LogEntry

    user = baker.make(User)
    return baker.make(
        LogEntry,
        user=user,
        message="Complete test log entry",
        level="INFO",
        source="test",
        path="/complete-test/",
        method="POST",
        status_code=201,
        actor_type="user",
        meta={"complete": True, "test_id": 123},
    )
