.. image:: https://github.com/abdulsamet/logmancer/actions/workflows/test.yml/badge.svg?branch=master
   :target: https://github.com/abdulsamet/logmancer/actions/workflows/test.yml
   :alt: Test Status

.. image:: https://img.shields.io/pypi/pyversions/django-logmancer.svg
   :target: https://pypi.org/project/django-logmancer/
   :alt: Python Versions

.. image:: https://img.shields.io/github/license/abdulsamet/logmancer.svg
   :target: https://github.com/abdulsamet/logmancer/blob/master/LICENSE
   :alt: License

Logmancer
=========

Advanced logging and monitoring for Django applications.

Features
--------

- **Database Logging** – Store logs in your Django database  
- **Middleware Integration** – Automatic HTTP request/response logging  
- **Django Signals** – Monitor model changes automatically  
- **Admin Interface** – Beautiful Django admin integration  
- **Advanced Filtering** – Filter logs by level, source, timestamp, and more  
- **Sensitive Data Masking** – Automatically mask passwords and sensitive data  
- **Configurable** – Extensive configuration options  
- **JSON Support** – Store structured data with JSON fields  
- **Cleanup Commands** – Built-in management commands for maintenance  

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
    }

Run migrations:

::

    python manage.py migrate logmancer

Manual Logging Example
----------------------

::

    from logmancer.utils import LogEvent

    LogEvent.info("User login successful")
    LogEvent.error("Payment failed", meta={"user_id": 123, "amount": 99.99})

Admin Interface
---------------

- Navigate to ``/admin/logmancer/logentry/``
- Filter by level, source, timestamp, actor type
- Search through log messages
- View detailed metadata in JSON format

License
-------

MIT License. See ``LICENSE`` for details.
