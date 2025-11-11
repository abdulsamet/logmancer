import asyncio
import logging
import queue
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from django.db import transaction

from logmancer.conf import get_bool
from logmancer.models import LogEntry
from logmancer.notifications.manager import notification_manager

logger = logging.getLogger("logmancer.utils")


class LogEvent:
    _notification_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="logmancer_notif")
    _notification_queue = queue.Queue(maxsize=1000)
    _worker_started = False

    @classmethod
    def _log(cls, level, message, **kwargs):
        """Internal log method with notification support"""

        def create_log():
            try:
                log_entry = LogEntry.objects.create(
                    message=message,
                    level=level,
                    source=kwargs.get("source", "manual"),
                    path=kwargs.get("path"),
                    method=kwargs.get("method"),
                    status_code=kwargs.get("status_code"),
                    meta=kwargs.get("meta", {}),
                    user=kwargs.get("user"),
                    actor_type=kwargs.get("actor_type", "user"),
                )

                notify = kwargs.pop("notify", False)
                enabled = get_bool("ENABLE_NOTIFICATIONS")

                if notify and enabled:
                    cls._queue_notification(log_entry, kwargs)

                return log_entry
            except Exception as e:
                logger.error(f"LogEvent _log error: {e}")

        transaction.on_commit(create_log)

    @classmethod
    def _queue_notification(cls, log_entry, context):
        """Queue notification for async processing"""
        try:
            cls._notification_queue.put_nowait((log_entry, context))

            if not cls._worker_started:
                cls._start_notification_worker()
                cls._worker_started = True

        except queue.Full:
            logger.error("Notification queue is full, dropping notification")

    @classmethod
    def _start_notification_worker(cls):
        """Start background worker for processing notifications"""

        def notification_worker():
            while True:
                try:
                    log_entry, context = cls._notification_queue.get(timeout=30)

                    cls._notification_executor.submit(
                        cls._send_notification_async, log_entry, context
                    )

                    cls._notification_queue.task_done()

                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Notification worker error: {e}")

        worker_thread = Thread(target=notification_worker, daemon=True, name="logmancer_worker")
        worker_thread.start()

    @classmethod
    def _send_notification_async(cls, log_entry, context):
        """Run async notifications inside this worker thread"""
        try:
            asyncio.run(notification_manager.send_notifications(log_entry, context))
        except Exception as e:
            logger.error(f"Sending notification failed: {e}")

    @classmethod
    def info(cls, message, **kwargs):
        cls._log("INFO", message, **kwargs)

    @classmethod
    def warning(cls, message, **kwargs):
        cls._log("WARNING", message, **kwargs)

    @classmethod
    def error(cls, message, **kwargs):
        cls._log("ERROR", message, **kwargs)

    @classmethod
    def debug(cls, message, **kwargs):
        cls._log("DEBUG", message, **kwargs)

    @classmethod
    def critical(cls, message, **kwargs):
        cls._log("CRITICAL", message, **kwargs)

    @classmethod
    def fatal(cls, message, **kwargs):
        cls._log("FATAL", message, **kwargs)

    @classmethod
    def notset(cls, message, **kwargs):
        cls._log("NOTSET", message, **kwargs)
