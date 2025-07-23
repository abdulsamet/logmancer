import datetime
import json
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from logmancer.conf import get_list
from logmancer.models import LogEntry


def make_json_safe(data):
    """
    Converts datetime, Decimal, and UUID objects in data to strings before writing to JSONField.
    """

    def default_serializer(obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, UUID):
            return str(obj)
        return str(obj)

    try:
        json_str = json.dumps(data, default=default_serializer)
        return json.loads(json_str)
    except Exception as e:
        print(f"[Logmancer] make_json_safe failed: {e}")
        return {}


def mask_sensitive_data(data):
    """
    Returns data with sensitive keys masked.
    """
    if not isinstance(data, (dict, list)):
        return data

    sensitive_keys = [k.lower() for k in get_list("LOG_SENSITIVE_KEYS")]

    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]

    masked = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys:
            masked[key] = "****"
        elif isinstance(value, (dict, list)):
            masked[key] = mask_sensitive_data(value)
        else:
            masked[key] = value

    return masked


class LogEvent:
    @staticmethod
    def _log(message, level="INFO", **kwargs):
        user = kwargs.get("user")
        meta = kwargs.get("meta")
        path = kwargs.get("path")
        method = kwargs.get("method")
        status_code = kwargs.get("status_code")
        source = kwargs.get("source", "manual")
        actor_type = kwargs.get("actor_type")
        if actor_type is None:
            actor_type = "user" if user else "system"
        clean_meta = make_json_safe(mask_sensitive_data(meta or {}))

        def _write_log():
            try:
                LogEntry.objects.create(
                    message=message,
                    level=level.upper(),
                    user=user,
                    meta=clean_meta,
                    path=path,
                    method=method,
                    status_code=status_code,
                    source=source,
                    actor_type=actor_type,
                )
            except Exception as e:
                print(f"[Logmancer] LogEvent raised an error: {e}")

        transaction.on_commit(_write_log)

    @classmethod
    def info(cls, message, **kwargs):
        cls._log(message, level="INFO", **kwargs)

    @classmethod
    def warning(cls, message, **kwargs):
        cls._log(message, level="WARNING", **kwargs)

    @classmethod
    def error(cls, message, **kwargs):
        cls._log(message, level="ERROR", **kwargs)

    @classmethod
    def debug(cls, message, **kwargs):
        cls._log(message, level="DEBUG", **kwargs)

    @classmethod
    def critical(cls, message, **kwargs):
        cls._log(message, level="CRITICAL", **kwargs)

    @classmethod
    def fatal(cls, message, **kwargs):
        cls._log(message, level="FATAL", **kwargs)

    @classmethod
    def notset(cls, message, **kwargs):
        cls._log(message, level="NOTSET", **kwargs)
