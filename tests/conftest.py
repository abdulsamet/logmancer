import os
import sys

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
