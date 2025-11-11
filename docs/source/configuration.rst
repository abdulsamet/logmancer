Configuration
=============

All Logmancer settings go into the ``LOGMANCER`` dictionary in your Django ``settings.py``.

Basic Configuration
-------------------

.. code-block:: python

   LOGMANCER = {
       'ENABLE_MIDDLEWARE': True,
       'ENABLE_SIGNALS': False,
       'AUTO_LOG_EXCEPTIONS': True,
       'CLEANUP_AFTER_DAYS': 30,
   }

Available Settings
------------------

ENABLE_MIDDLEWARE
^^^^^^^^^^^^^^^^^

**Type:** ``bool``  
**Default:** ``True``

Enable automatic HTTP request/response logging via middleware.

.. code-block:: python

   LOGMANCER = {
       'ENABLE_MIDDLEWARE': True,
   }

ENABLE_SIGNALS
^^^^^^^^^^^^^^

**Type:** ``bool``  
**Default:** ``False``

Enable automatic model change monitoring via Django signals.

.. code-block:: python

   LOGMANCER = {
       'ENABLE_SIGNALS': True,
   }

AUTO_LOG_EXCEPTIONS
^^^^^^^^^^^^^^^^^^^

**Type:** ``bool``  
**Default:** ``False``

Automatically log unhandled exceptions in middleware.

.. code-block:: python

   LOGMANCER = {
       'AUTO_LOG_EXCEPTIONS': True,
   }

CLEANUP_AFTER_DAYS
^^^^^^^^^^^^^^^^^^

**Type:** ``int``  
**Default:** ``30``

Number of days to keep logs before cleanup.

.. code-block:: python

   LOGMANCER = {
       'CLEANUP_AFTER_DAYS': 60,  # Keep logs for 60 days
   }

LOG_SENSITIVE_KEYS
^^^^^^^^^^^^^^^^^^

**Type:** ``list``  
**Default:** ``['password', 'token', 'authorization']``

List of keys to mask in logged data.

.. code-block:: python

   LOGMANCER = {
       'LOG_SENSITIVE_KEYS': [
           'password',
           'token',
           'secret',
           'api_key',
           'authorization',
           'credit_card',
       ]
   }

PATH_EXCLUDE_PREFIXES
^^^^^^^^^^^^^^^^^^^^^

**Type:** ``list``  
**Default:** ``[]``

HTTP paths to exclude from middleware logging.

.. code-block:: python

   LOGMANCER = {
       'PATH_EXCLUDE_PREFIXES': [
           '/admin/jsi18n/',
           '/static/',
           '/media/',
           '/health/',
       ]
   }

SIGNAL_EXCLUDE_MODELS
^^^^^^^^^^^^^^^^^^^^^

**Type:** ``list``  
**Default:** ``['logmancer.LogEntry']``

Models to exclude from signal monitoring.

.. code-block:: python

   LOGMANCER = {
       'SIGNAL_EXCLUDE_MODELS': [
           'logmancer.LogEntry',
           'sessions.Session',
           'contenttypes.ContentType',
       ]
   }

ENABLE_NOTIFICATIONS
^^^^^^^^^^^^^^^^^^^^

**Type:** ``bool``  
**Default:** ``False``

Enable the notification system.

.. code-block:: python

   LOGMANCER = {
       'ENABLE_NOTIFICATIONS': True,
   }

NOTIFICATIONS
^^^^^^^^^^^^^

**Type:** ``dict``  
**Default:** ``{}``

Notification backend configurations.

Email Example:

.. code-block:: python

   LOGMANCER = {
       'ENABLE_NOTIFICATIONS': True,
       'NOTIFICATIONS': {
           'email': {
               'enabled': True,
               'recipients': ['admin@example.com'],
               'from_email': 'noreply@example.com',
               'min_level': 'ERROR',
           }
       }
   }

Slack Example:

.. code-block:: python

   LOGMANCER = {
       'NOTIFICATIONS': {
           'slack': {
               'enabled': True,
               'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
               'min_level': 'WARNING',
           }
       }
   }

Telegram Example:

.. code-block:: python

   LOGMANCER = {
       'NOTIFICATIONS': {
           'telegram': {
               'enabled': True,
               'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
               'chat_id': '-1001234567890',
               'min_level': 'ERROR',
           }
       }
   }

Complete Example
----------------

.. code-block:: python

   LOGMANCER = {
       # Core settings
       'ENABLE_MIDDLEWARE': True,
       'ENABLE_SIGNALS': True,
       'AUTO_LOG_EXCEPTIONS': True,
       'CLEANUP_AFTER_DAYS': 60,
       
       # Filtering
       'LOG_SENSITIVE_KEYS': [
           'password', 'token', 'secret_key', 'api_key'
       ],
       'PATH_EXCLUDE_PREFIXES': [
           '/admin/', '/static/', '/media/', '/health/'
       ],
       'SIGNAL_EXCLUDE_MODELS': [
           'logmancer.LogEntry',
           'sessions.Session',
       ],
       
       # Notifications
       'ENABLE_NOTIFICATIONS': True,
       'NOTIFICATIONS': {
           'telegram': {
               'enabled': True,
               'bot_token': 'YOUR_BOT_TOKEN',
               'chat_id': 'YOUR_CHAT_ID',
               'min_level': 'ERROR',
           },
           'email': {
               'enabled': True,
               'recipients': ['admin@example.com'],
               'min_level': 'CRITICAL',
           }
       }
   }
