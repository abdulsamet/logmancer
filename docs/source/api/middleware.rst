Middleware
==========

.. automodule:: logmancer.middleware
   :members:
   :undoc-members:
   :show-inheritance:

DBLoggingMiddleware
-------------------

.. autoclass:: logmancer.middleware.DBLoggingMiddleware
   :members:
   :special-members: __init__, __call__, __acall__

   Django middleware for automatic HTTP request/response logging.

   **Methods:**

   .. automethod:: __call__
   .. automethod:: __acall__
   .. automethod:: log_request
   .. automethod:: process_exception
   .. automethod:: mask_sensitive_data
   .. automethod:: get_user_from_request

get_current_user
----------------

.. autofunction:: logmancer.middleware.get_current_user

   Get the current user from context (works in both sync and async contexts).

   **Returns:**
      User instance or None
