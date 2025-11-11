.. image:: https://github.com/abdulsamet/logmancer/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/abdulsamet/logmancer/actions/workflows/test.yml
    :alt: Test Status

.. image:: https://badge.fury.io/gh/abdulsamet%2Flogmancer.svg
    :target: https://badge.fury.io/gh/abdulsamet%2Flogmancer
    :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/django-logmancer.svg
    :target: https://pypi.org/project/django-logmancer/
    :alt: Python Versions

.. image:: https://img.shields.io/github/license/abdulsamet/logmancer.svg
    :target: https://github.com/abdulsamet/logmancer/blob/main/LICENSE
    :alt: License

.. image:: https://codecov.io/github/abdulsamet/logmancer/graph/badge.svg?token=D45NERJMAI 
    :target: https://codecov.io/github/abdulsamet/logmancer
    :alt: Code Coverage

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Black

.. image:: https://readthedocs.org/projects/logmancer/badge/?version=latest
    :target: https://logmancer.readthedocs.io/en/latest/
    :alt: Documentation Status

Logmancer
=========

Advanced logging and monitoring for Django applications with real-time notifications.

Features
--------

- **Database Logging** – Store logs in your Django database  
- **Middleware Integration** – Automatic HTTP request/response logging  
- **Django Signals** – Monitor model changes automatically  
- **Real-time Notifications** – Email, Slack, and Telegram integration
- **Admin Interface** – Beautiful Django admin integration  
- **Advanced Filtering** – Filter logs by level, source, timestamp, and more  
- **Sensitive Data Masking** – Automatically mask passwords and sensitive data  
- **Configurable** – Extensive configuration options  
- **JSON Support** – Store structured data with JSON fields  
- **Cleanup Commands** – Built-in management commands for maintenance
- **Comprehensive Documentation** – Full Sphinx documentation with Read the Docs  

Quick Start
-----------

Install:

::

    pip install django-logmancer

Add to your ``settings.py``:

::

    INSTALLED_APPS = [
        # ... your apps
        'logmancer',
    ]

    MIDDLEWARE = [
        # ... your middleware
        'logmancer.middleware.DBLoggingMiddleware',
    ]

    LOGMANCER = {
        'ENABLE_SIGNALS': True,
        'ENABLE_MIDDLEWARE': True,
        'LOG_LEVEL': 'INFO',
        'EXCLUDE_PATHS': ['/admin/jsi18n/', '/static/', '/media/'],
        'EXCLUDE_MODELS': ['logmancer.LogEntry', 'auth.Session'],
        'MASK_SENSITIVE_DATA': ['password', 'token', 'secret', 'key'],
        'CLEANUP_AFTER_DAYS': 30,
        'NOTIFICATIONS': {
            'ENABLED': True,
            'BACKENDS': {
                'email': {
                    'class': 'logmancer.notifications.email.EmailBackend',
                    'enabled': True,
                    'recipients': ['admin@example.com'],
                },
                'slack': {
                    'class': 'logmancer.notifications.slack.SlackBackend',
                    'enabled': True,
                    'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
                },
                'telegram': {
                    'class': 'logmancer.notifications.telegram.TelegramBackend',
                    'enabled': True,
                    'bot_token': 'YOUR_BOT_TOKEN',
                    'chat_id': 'YOUR_CHAT_ID',
                },
            },
        },
    }

Run migrations:

::

    python manage.py migrate logmancer

Manual Logging Example
----------------------

::

    from logmancer.utils import LogEvent

    # Simple logging
    LogEvent.info("User login successful")
    LogEvent.error("Payment failed", meta={"user_id": 123, "amount": 99.99})
    
    # With notifications
    LogEvent.critical(
        "Database connection lost",
        notify=True,  # Send notifications to configured backends
        meta={"host": "db-server-01"}
    )

Notifications
-------------

Configure multiple notification backends:

- **Email** – Send alerts via Django's email system
- **Slack** – Post messages to Slack channels
- **Telegram** – Send messages via Telegram bot

Test your notification setup:

::

    python manage.py test_notifications --level critical

Admin Interface
---------------

- Navigate to ``/admin/logmancer/logentry/``
- Filter by level, source, timestamp, actor type
- Search through log messages
- View detailed metadata in JSON format

Cleanup Management
------------------

Automatically clean up old log entries:

::

    python manage.py logmancer_cleanup --days 30 --dry-run

Documentation
-------------

Full documentation is available at: https://logmancer.readthedocs.io/

- `Getting Started <https://logmancer.readthedocs.io/en/latest/getting-started.html>`_
- `Configuration <https://logmancer.readthedocs.io/en/latest/configuration.html>`_
- `API Reference <https://logmancer.readthedocs.io/en/latest/api/index.html>`_
- `Cleanup Strategy Guide <https://logmancer.readthedocs.io/en/latest/guides/cleanup-strategy.html>`_

License
-------

MIT License. See ``LICENSE`` for details.
