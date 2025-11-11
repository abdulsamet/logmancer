Models
======

.. automodule:: logmancer.models
   :members:
   :undoc-members:
   :show-inheritance:

LogEntry Model
--------------

.. autoclass:: logmancer.models.LogEntry
   :members:
   :special-members: __str__
   :exclude-members: DoesNotExist, MultipleObjectsReturned

   The main log entry model that stores all logged events in the database.

   **Fields:**

   .. autoattribute:: timestamp
   .. autoattribute:: level
   .. autoattribute:: message
   .. autoattribute:: path
   .. autoattribute:: method
   .. autoattribute:: status_code
   .. autoattribute:: user
   .. autoattribute:: source
   .. autoattribute:: actor_type
   .. autoattribute:: meta

   **Methods:**

   .. automethod:: get_level_info
   .. automethod:: get_emoji
   .. automethod:: get_color

SafeJSONField
-------------

.. autoclass:: logmancer.models.SafeJSONField
   :members:
   :show-inheritance:
