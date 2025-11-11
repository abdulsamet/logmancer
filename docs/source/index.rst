Logmancer Documentation
=======================

.. image:: https://github.com/abdulsamet/logmancer/actions/workflows/test.yml/badge.svg?branch=main
   :target: https://github.com/abdulsamet/logmancer/actions/workflows/test.yml
   :alt: Test Status

.. image:: https://codecov.io/github/abdulsamet/logmancer/graph/badge.svg?token=D45NERJMAI
   :target: https://codecov.io/github/abdulsamet/logmancer
   :alt: Code Coverage

**Logmancer** is an advanced logging and monitoring solution for Django applications.

Features
--------

✨ **Database Logging** – Store logs in your Django database

🔄 **Middleware Integration** – Automatic HTTP request/response logging

📡 **Django Signals** – Monitor model changes automatically

🎨 **Admin Interface** – Beautiful Django admin integration

🔍 **Advanced Filtering** – Filter by level, source, timestamp, and more

🔒 **Sensitive Data Masking** – Automatically mask passwords and tokens

📨 **Notifications** – Email, Slack, Telegram integration

Quick Start
-----------

Installation:

.. code-block:: bash

   pip install django-logmancer

Add to your ``settings.py``:

.. code-block:: python

   INSTALLED_APPS = [
       # ... your apps
       'logmancer',
   ]

   MIDDLEWARE = [
       # ... your middleware
       'logmancer.middleware.DBLoggingMiddleware',
   ]

   LOGMANCER = {
       'ENABLE_MIDDLEWARE': True,
       'AUTO_LOG_EXCEPTIONS': True,
   }

Run migrations:

.. code-block:: bash

   python manage.py migrate logmancer

Start logging:

.. code-block:: python

   from logmancer.utils import LogEvent

   LogEvent.info("User login successful")
   LogEvent.error("Payment failed", meta={"user_id": 123})
   LogEvent.info("Payment successful", notify=True)

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting-started
   installation
   configuration

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
   api/models
   api/middleware
   api/utils
   api/signals
   api/management

.. toctree::
   :maxdepth: 1
   :caption: Additional

   changelog
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

