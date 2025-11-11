Getting Started
===============

Welcome to Logmancer! This guide will help you get started quickly.

Installation
------------

Install using pip:

.. code-block:: bash

   pip install django-logmancer

Or with uv:

.. code-block:: bash

   uv add django-logmancer

Basic Setup
-----------

1. Add to ``INSTALLED_APPS`` in your ``settings.py``:

.. code-block:: python

   INSTALLED_APPS = [
       # ... your apps
       'logmancer',
   ]

2. Add middleware (optional but recommended):

.. code-block:: python

   MIDDLEWARE = [
       # ... your middleware
       'logmancer.middleware.DBLoggingMiddleware',
   ]

3. Configure Logmancer:

.. code-block:: python

   LOGMANCER = {
       'ENABLE_MIDDLEWARE': True,
       'AUTO_LOG_EXCEPTIONS': True,
       'CLEANUP_AFTER_DAYS': 30,
   }

4. Run migrations:

.. code-block:: bash

   python manage.py migrate logmancer

First Steps
-----------

Manual Logging
^^^^^^^^^^^^^^

.. code-block:: python

   from logmancer.utils import LogEvent

   # Simple logging
   LogEvent.info("Application started")
   LogEvent.warning("Cache miss detected")
   LogEvent.error("Database connection failed")

   # With metadata
   LogEvent.error("Payment failed", meta={
       "user_id": 123,
       "amount": 99.99,
       "error_code": "CARD_DECLINED"
   })

   # With notifications
   LogEvent.critical("System overload", notify=True)

View Logs in Admin
^^^^^^^^^^^^^^^^^^

1. Navigate to ``/admin/logmancer/logentry/``
2. View, filter, and search logs
3. Export logs as needed

Next Steps
----------

- Read the :doc:`configuration` guide for all available options
- Check the :doc:`api/index` for detailed API documentation
- See examples in the examples section
