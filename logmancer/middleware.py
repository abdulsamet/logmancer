import contextvars
import json
import logging
import threading
import traceback

from logmancer.conf import get_bool, get_list, should_exclude_path
from logmancer.models import LogEntry
from logmancer.utils import LogEvent

logger = logging.getLogger("logmancer.middleware")

# Sync (thread local) and async (contextvar) storage
_thread_user = threading.local()
_context_user = contextvars.ContextVar("current_user", default=None)


class DBLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sync context
        _thread_user.user = getattr(request, "user", None)

        # Async context
        _context_user.set(getattr(request, "user", None))

        try:
            response = self.get_response(request)
            self.log_request(request, response)
            return response
        finally:
            _thread_user.user = None
            _context_user.set(None)

    async def __acall__(self, request):
        # Async context
        _thread_user.user = getattr(request, "user", None)
        _context_user.set(getattr(request, "user", None))

        response = await self.get_response(request)
        self.log_request(request, response)

        _thread_user.user = None
        _context_user.set(None)

        return response

    def mask_sensitive_data(self, data):
        if not isinstance(data, (dict, list)):
            return data

        sensitive_keys = [k.lower() for k in get_list("LOG_SENSITIVE_KEYS")]

        if isinstance(data, list):
            return [self.mask_sensitive_data(item) for item in data]

        masked = {}
        for key, value in data.items():
            if key.lower() in sensitive_keys:
                masked[key] = "****"
            elif isinstance(value, (dict, list)):
                masked[key] = self.mask_sensitive_data(value)
            else:
                masked[key] = value

        return masked

    def get_user_from_request(self, request):
        if hasattr(request, "user") and getattr(request.user, "is_authenticated", False):
            return request.user
        return None

    def log_request(self, request, response):
        if should_exclude_path(request.path):
            return
        try:
            user = self.get_user_from_request(request)

            try:
                if request.content_type == "application/json":
                    body_data = json.loads(request.body.decode("utf-8"))
                else:
                    body_data = request.POST.dict()
            except Exception:
                body_data = {}

            meta = {
                "GET": self.mask_sensitive_data(request.GET.dict()),
                "POST": self.mask_sensitive_data(body_data),
                "headers": self.mask_sensitive_data(
                    {k: v for k, v in request.headers.items() if k.lower() != "authorization"}
                ),
                "remote_addr": request.META.get("REMOTE_ADDR"),
            }

            LogEntry.objects.create(
                level="INFO",
                message=f"{request.method} {request.path} - {response.status_code}",
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                user=user,
                meta=meta,
                source="middleware",
                actor_type="user" if user else "system",
            )
        except Exception as e:
            logger.exception(f"Middleware log error: {e}")

    def process_exception(self, request, exception):
        if not get_bool("AUTO_LOG_EXCEPTIONS"):
            return

        try:
            user = self.get_user_from_request(request)

            meta = {
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "stack": traceback.format_exc(),
            }

            LogEvent.error(
                message=f"Unhandled exception on {request.method} {request.path}",
                path=request.path,
                method=request.method,
                status_code=500,
                user=user,
                meta=meta,
                source="exception",
                actor_type="user" if user else "system",
            )
        except Exception as e:
            logger.exception(f"Process_exception failed: {e}")


def get_current_user():
    # Check async context
    user = _context_user.get(None)
    if user is not None:
        return user

    # Then check sync thread local
    return getattr(_thread_user, "user", None)
