Signals
=======

.. automodule:: logmancer.signals
   :members:
   :undoc-members:
   :show-inheritance:

Signal Handlers
---------------

.. autofunction:: logmancer.signals.log_model_save

   Signal handler that logs model save events.

   **Parameters:**
      - **sender**: Model class
      - **instance**: Model instance being saved
      - **created** (bool): True if a new record was created

.. autofunction:: logmancer.signals.log_model_delete

   Signal handler that logs model delete events.

   **Parameters:**
      - **sender**: Model class
      - **instance**: Model instance being deleted
