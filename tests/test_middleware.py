import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client, RequestFactory, TransactionTestCase, override_settings

import pytest

from logmancer.middleware import DBLoggingMiddleware
from logmancer.models import LogEntry
from tests.urls import test_urlpatterns

# Common settings for middleware tests
MIDDLEWARE_TEST_SETTINGS = {
    "ROOT_URLCONF": "tests.test_middleware",
    "MIDDLEWARE": [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "logmancer.middleware.DBLoggingMiddleware",
    ],
    "LOGMANCER": {"ENABLE_MIDDLEWARE": True},
}

# Settings for exception handling tests
EXCEPTION_TEST_SETTINGS = {
    **MIDDLEWARE_TEST_SETTINGS,
    "LOGMANCER": {"ENABLE_MIDDLEWARE": True, "AUTO_LOG_EXCEPTIONS": True},
}

# Minimal middleware settings for simple tests
MINIMAL_MIDDLEWARE_SETTINGS = {
    "ROOT_URLCONF": "tests.test_middleware",
    "MIDDLEWARE": [
        "django.middleware.security.SecurityMiddleware",
        "logmancer.middleware.DBLoggingMiddleware",
    ],
    "LOGMANCER": {"ENABLE_MIDDLEWARE": True, "AUTO_LOG_EXCEPTIONS": True},
}


class BaseMiddlewareTest:
    """Base class with common setup for middleware tests"""

    @staticmethod
    def mock_transaction_commit():
        """Context manager to mock transaction.on_commit for immediate execution"""

        def execute_immediately(func):
            func()

        return patch("logmancer.utils.transaction.on_commit", side_effect=execute_immediately)


@pytest.mark.django_db
class TestDBLoggingMiddleware(BaseMiddlewareTest):
    """Test DBLoggingMiddleware functionality using pytest with override_settings context manager"""

    @override_settings(**MIDDLEWARE_TEST_SETTINGS)
    def test_middleware_logs_get_request(self):
        """Test that middleware logs GET requests"""
        with self.mock_transaction_commit():
            client = Client()
            initial_count = LogEntry.objects.count()

            response = client.get("/dummy/")

            assert response.status_code == 200
            assert json.loads(response.content) == {"msg": "ok"}

            new_count = LogEntry.objects.count()
            assert new_count > initial_count

            log = LogEntry.objects.filter(source="middleware", path="/dummy/").last()
            assert log is not None
            assert log.path == "/dummy/"
            assert log.status_code == 200
            assert log.method == "GET"
            assert log.level == "INFO"

    @override_settings(**MIDDLEWARE_TEST_SETTINGS)
    def test_middleware_logs_post_request(self):
        """Test middleware logs POST requests"""
        with self.mock_transaction_commit():
            client = Client()
            initial_count = LogEntry.objects.count()

            response = client.post("/test/", {"data": "test", "key": "value"})

            assert response.status_code == 200
            new_count = LogEntry.objects.count()
            assert new_count > initial_count

            log = LogEntry.objects.filter(source="middleware", method="POST", path="/test/").last()
            assert log is not None
            assert log.method == "POST"
            assert log.path == "/test/"
            assert log.status_code == 200

    @override_settings(**MIDDLEWARE_TEST_SETTINGS)
    def test_middleware_logs_authenticated_user(self):
        """Test middleware logs requests with authenticated user"""
        with self.mock_transaction_commit():
            user = User.objects.create_user(username="testuser", password="testpass")
            client = Client()
            client.login(username="testuser", password="testpass")

            response = client.get("/auth/")
            assert response.status_code == 200

            log = LogEntry.objects.filter(source="middleware", path="/auth/").last()
            assert log is not None
            # Check user is logged properly (might be user object or user.id)
            assert log.user == user or log.actor_id == str(user.id)

    def test_get_user_from_request_authenticated(self):
        """Test get_user_from_request with authenticated user"""
        middleware = DBLoggingMiddleware(lambda x: x)
        request = RequestFactory().get("/")
        request.user = User.objects.create_user(username="testuser")

        user = middleware.get_user_from_request(request)
        assert user == request.user

    def test_get_user_from_request_unauthenticated(self):
        """Test get_user_from_request with unauthenticated user"""
        middleware = DBLoggingMiddleware(lambda x: x)
        request = RequestFactory().get("/")
        request.user = MagicMock()
        request.user.is_authenticated = False

        user = middleware.get_user_from_request(request)
        assert user is None

    def test_get_user_from_request_no_user(self):
        """Test get_user_from_request when request has no user attribute"""
        middleware = DBLoggingMiddleware(lambda x: x)
        request = RequestFactory().get("/")
        # No user attribute

        user = middleware.get_user_from_request(request)
        assert user is None


@pytest.mark.django_db
class TestMiddlewareExceptionHandling(BaseMiddlewareTest):
    """Test middleware exception handling functionality"""

    def test_process_exception_exists(self):
        """Test that process_exception method exists"""
        middleware = DBLoggingMiddleware(lambda x: x)
        assert hasattr(middleware, "process_exception")
        assert callable(middleware.process_exception)

    def test_process_exception_logs_error_direct(self):
        """Test process_exception method directly"""
        with self.mock_transaction_commit():
            middleware = DBLoggingMiddleware(lambda x: x)
            request = RequestFactory().get("/error/")
            request.user = None  # No user
            exception = ValueError("Test exception")

            # Mock the configuration to enable exception logging
            with patch("logmancer.middleware.get_bool") as mock_get_bool:
                mock_get_bool.return_value = True  # Enable AUTO_LOG_EXCEPTIONS

                initial_count = LogEntry.objects.filter(source="exception").count()

                # Call process_exception directly
                middleware.process_exception(request, exception)

                new_count = LogEntry.objects.filter(source="exception").count()
                assert new_count > initial_count, "No exception log created"

                # Verify the log content
                log = LogEntry.objects.filter(source="exception").order_by("-timestamp").first()
                assert log is not None
                assert log.level == "ERROR"
                assert log.path == "/error/"
                assert log.method == "GET"
                assert log.status_code == 500

    def test_process_exception_with_user(self):
        """Test process_exception with authenticated user"""
        with self.mock_transaction_commit():
            user = User.objects.create_user(username="testuser", password="testpass")
            middleware = DBLoggingMiddleware(lambda x: x)
            request = RequestFactory().get("/error/")
            request.user = user
            exception = ValueError("Test exception")

            with patch("logmancer.middleware.get_bool") as mock_get_bool:
                mock_get_bool.return_value = True

                initial_count = LogEntry.objects.filter(source="exception").count()
                middleware.process_exception(request, exception)

                new_count = LogEntry.objects.filter(source="exception").count()
                assert new_count > initial_count

                log = LogEntry.objects.filter(source="exception").order_by("-timestamp").first()
                assert log.user == user
                assert log.actor_type == "user"

    def test_process_exception_disabled(self):
        """Test process_exception when AUTO_LOG_EXCEPTIONS is disabled"""
        middleware = DBLoggingMiddleware(lambda x: x)
        request = RequestFactory().get("/error/")
        exception = ValueError("Test exception")

        with patch("logmancer.middleware.get_bool") as mock_get_bool:
            mock_get_bool.return_value = False  # Disable AUTO_LOG_EXCEPTIONS

            initial_count = LogEntry.objects.filter(source="exception").count()
            middleware.process_exception(request, exception)

            # Should not create new logs when disabled
            new_count = LogEntry.objects.filter(source="exception").count()
            assert new_count == initial_count

    def test_process_exception_handles_log_error(self):
        """Test process_exception handles its own logging errors"""
        middleware = DBLoggingMiddleware(lambda x: x)
        request = RequestFactory().get("/error/")
        exception = ValueError("Test exception")

        with patch("logmancer.middleware.get_bool") as mock_get_bool:
            mock_get_bool.return_value = True

            # Mock LogEvent to raise exception
            with patch(
                "logmancer.middleware.LogEvent.error",
                side_effect=Exception("Log Error"),
            ):
                with patch("logmancer.middleware.logger") as mock_logger:
                    # Should not raise exception, just log it
                    middleware.process_exception(request, exception)
                    mock_logger.exception.assert_called_with("[Logmancer] process_exception failed")


# Use TransactionTestCase for real transaction testing
@override_settings(**MINIMAL_MIDDLEWARE_SETTINGS)
class TestMiddlewareTransactions(TransactionTestCase, BaseMiddlewareTest):
    """Test middleware with real transactions - using TransactionTestCase"""

    def test_process_exception_in_middleware_stack_with_transactions(self):
        """Test process_exception works in full middleware stack with real transactions"""
        with patch("logmancer.middleware.get_bool") as mock_get_bool:
            mock_get_bool.return_value = True

            with self.mock_transaction_commit():
                client = Client()
                initial_count = LogEntry.objects.filter(source="exception").count()

                # This will raise ValueError("Test exception")
                with self.assertRaises(ValueError):
                    client.get("/error/")

                new_count = LogEntry.objects.filter(source="exception").count()
                self.assertGreater(
                    new_count,
                    initial_count,
                    "No exception logs created in middleware stack",
                )

                # Find the exception log
                log = LogEntry.objects.filter(source="exception").order_by("-timestamp").first()
                self.assertIsNotNone(log)
                self.assertEqual(log.level, "ERROR")
                self.assertEqual(log.path, "/error/")

    def test_full_middleware_cycle_with_exception_transactions(self):
        """Test complete middleware cycle including exception handling with real transactions"""
        # Override settings for this specific test to include all middleware
        test_settings = {
            **MINIMAL_MIDDLEWARE_SETTINGS,
            "MIDDLEWARE": [
                "django.middleware.security.SecurityMiddleware",
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "logmancer.middleware.DBLoggingMiddleware",
            ],
        }

        with override_settings(**test_settings):
            with patch("logmancer.middleware.get_bool") as mock_get_bool:
                mock_get_bool.return_value = True

                with self.mock_transaction_commit():
                    client = Client()
                    User.objects.create_user(username="testuser", password="testpass")
                    client.login(username="testuser", password="testpass")

                    # First, test normal request logging
                    response = client.get("/dummy/")
                    self.assertEqual(response.status_code, 200)

                    middleware_log = LogEntry.objects.filter(
                        source="middleware", path="/dummy/"
                    ).last()
                    self.assertIsNotNone(middleware_log)

                    # Then test exception logging
                    initial_exception_count = LogEntry.objects.filter(source="exception").count()

                    with self.assertRaises(ValueError):
                        response = client.get("/error/")

                    new_exception_count = LogEntry.objects.filter(source="exception").count()
                    self.assertGreater(new_exception_count, initial_exception_count)

                    exception_log = LogEntry.objects.filter(
                        source="exception", path="/error/"
                    ).last()
                    self.assertIsNotNone(exception_log)
                    self.assertEqual(exception_log.level, "ERROR")


# Simple direct tests for middleware methods
@pytest.mark.django_db
class TestMiddlewareDirect(BaseMiddlewareTest):
    """Direct tests for middleware methods"""

    def test_middleware_initialization(self):
        """Test middleware can be initialized"""
        get_response = HttpResponse("test")
        middleware = DBLoggingMiddleware(get_response)
        assert middleware.get_response == get_response

    def test_middleware_call(self):
        """Test middleware __call__ method"""

        def get_response(request):
            return HttpResponse("test response")

        with self.mock_transaction_commit():
            middleware = DBLoggingMiddleware(get_response)
            request = RequestFactory().get("/test/")

            # Should not raise exception
            response = middleware(request)
            assert response.content == b"test response"


# Alternative test using synchronous logging
@pytest.mark.django_db
class TestMiddlewareSynchronous(BaseMiddlewareTest):
    """Test middleware with synchronous logging (no transaction.on_commit)"""

    def test_process_exception_synchronous(self):
        """Test process_exception with synchronous logging"""
        # Patch LogEvent to log synchronously instead of using transaction.on_commit
        with patch("logmancer.middleware.LogEvent.error") as mock_log_error:

            def sync_log_event(*args, **kwargs):
                # Create log entry directly without transaction.on_commit
                from logmancer.models import LogEntry

                LogEntry.objects.create(
                    message=kwargs.get("message", args[0] if args else "Test"),
                    level=kwargs.get("level", "ERROR"),
                    source=kwargs.get("source", "exception"),
                    path=kwargs.get("path", "/error/"),
                    method=kwargs.get("method", "GET"),
                    status_code=kwargs.get("status_code", 500),
                    meta=kwargs.get("meta", {}),
                )

            mock_log_error.side_effect = sync_log_event

            middleware = DBLoggingMiddleware(lambda x: x)
            request = RequestFactory().get("/error/")
            request.user = None
            exception = ValueError("Test exception")

            with patch("logmancer.middleware.get_bool") as mock_get_bool:
                mock_get_bool.return_value = True

                initial_count = LogEntry.objects.filter(source="exception").count()
                middleware.process_exception(request, exception)

                new_count = LogEntry.objects.filter(source="exception").count()
                assert new_count > initial_count, "No exception log created"

                # Verify LogEvent was called
                mock_log_error.assert_called_once()


# URL configuration for tests
urlpatterns = test_urlpatterns
