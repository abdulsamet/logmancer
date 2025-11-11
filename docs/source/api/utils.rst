Utils
=====

.. automodule:: logmancer.utils
   :members:
   :undoc-members:
   :show-inheritance:

LogEvent Class
--------------

.. autoclass:: logmancer.utils.LogEvent
   :members:

   Utility class for manual logging throughout your Django application.

Logging Methods
^^^^^^^^^^^^^^^

.. automethod:: logmancer.utils.LogEvent.info

   Log an informational message.

   **Parameters:**
      - **message** (str): The log message
      - **source** (str, optional): Log source identifier (default: "manual")
      - **path** (str, optional): HTTP path
      - **method** (str, optional): HTTP method
      - **status_code** (int, optional): HTTP status code
      - **meta** (dict, optional): Additional metadata
      - **user** (User, optional): Django user instance
      - **actor_type** (str, optional): "user" or "system" (default: "user")
      - **notify** (bool, optional): Send notification if enabled (default: False)

   **Example:**

   .. code-block:: python

      from logmancer.utils import LogEvent

      LogEvent.info("User logged in", 
          user=request.user,
          meta={"ip": request.META.get("REMOTE_ADDR")}
      )

.. automethod:: logmancer.utils.LogEvent.warning

   Log a warning message.

.. automethod:: logmancer.utils.LogEvent.error

   Log an error message.

.. automethod:: logmancer.utils.LogEvent.critical

   Log a critical message.

.. automethod:: logmancer.utils.LogEvent.debug

   Log a debug message.

.. automethod:: logmancer.utils.LogEvent.fatal

   Log a fatal message.

.. automethod:: logmancer.utils.LogEvent.notset

   Log with NOTSET level.
