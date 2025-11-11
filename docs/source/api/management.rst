Management Commands
===================

Logmancer provides management commands for maintaining your log database.

logmancer_cleanup
-----------------

.. automodule:: logmancer.management.commands.logmancer_cleanup
   :members:
   :undoc-members:
   :show-inheritance:

Command Class
^^^^^^^^^^^^^

.. autoclass:: logmancer.management.commands.logmancer_cleanup.Command
   :members:
   :special-members: __init__
   :exclude-members: __weakref__

Usage
^^^^^

Basic cleanup (uses ``CLEANUP_AFTER_DAYS`` setting, default 30 days):

.. code-block:: bash

   python manage.py logmancer_cleanup

Custom retention period:

.. code-block:: bash

   # Delete logs older than 60 days
   python manage.py logmancer_cleanup --days=60

Dry run (preview what would be deleted):

.. code-block:: bash

   python manage.py logmancer_cleanup --dry-run

Options
^^^^^^^

``--days``
    Number of days to retain logs. Logs older than this will be deleted.
    
    **Type:** ``int``
    
    **Default:** Uses ``LOGMANCER_CLEANUP_AFTER_DAYS`` setting (default: 30)
    
    **Example:**
    
    .. code-block:: bash
    
       python manage.py logmancer_cleanup --days=90

``--dry-run``
    Show how many logs would be deleted without actually deleting them.
    
    **Type:** ``flag``
    
    **Example:**
    
    .. code-block:: bash
    
       python manage.py logmancer_cleanup --dry-run

Examples
^^^^^^^^

**Clean up logs older than 7 days:**

.. code-block:: bash

   python manage.py logmancer_cleanup --days=7

**Preview cleanup without deleting:**

.. code-block:: bash

   python manage.py logmancer_cleanup --days=30 --dry-run

**Output:**

.. code-block:: text

   [Logmancer] 1,234 log entries older than 30 days would be deleted (dry run).

**Automated cleanup with cron:**

.. code-block:: bash

   # Run daily at 2 AM
   0 2 * * * cd /path/to/project && python manage.py logmancer_cleanup --days=30

**Windows Task Scheduler:**

.. code-block:: batch

   cd C:\path\to\project
   python manage.py logmancer_cleanup --days=30

Configuration
^^^^^^^^^^^^^

Set default cleanup period in ``settings.py``:

.. code-block:: python

   LOGMANCER = {
       'CLEANUP_AFTER_DAYS': 30,  # Default retention period
   }

.. note::
   The ``--days`` argument overrides the ``CLEANUP_AFTER_DAYS`` setting.

Behavior
^^^^^^^^

When executed, the command:

1. Calculates threshold date (current date - days)
2. Queries ``LogEntry`` records older than threshold
3. Deletes matching records (unless ``--dry-run``)
4. Logs cleanup action to database
5. Outputs summary to console

.. warning::
   This operation cannot be undone. Use ``--dry-run`` first to verify.

Integration with Django
^^^^^^^^^^^^^^^^^^^^^^^

The command integrates with Django's management framework:

.. code-block:: python

   from django.core.management import call_command
   
   # Call from Python code
   call_command('logmancer_cleanup', days=60)
   
   # With dry-run
   call_command('logmancer_cleanup', dry_run=True)

Testing
^^^^^^^

Test the command in your project:

.. code-block:: python

   from django.core.management import call_command
   from django.test import TestCase
   from logmancer.models import LogEntry
   
   class TestCleanup(TestCase):
       def test_cleanup_old_logs(self):
           # Create old log
           old_log = LogEntry.objects.create(message="Old")
           LogEntry.objects.filter(pk=old_log.pk).update(
               timestamp=timezone.now() - timedelta(days=31)
           )
           
           # Run cleanup
           call_command('logmancer_cleanup')
           
           # Verify deletion
           assert not LogEntry.objects.filter(pk=old_log.pk).exists()

Related Settings
^^^^^^^^^^^^^^^^

- :ref:`CLEANUP_AFTER_DAYS <config-cleanup-after-days>`
- :ref:`ENABLE_MIDDLEWARE <config-enable-middleware>`

See Also
^^^^^^^^

- :doc:`/guides/cleanup-strategy` - Best practices for log retention
- :doc:`/configuration` - Full configuration reference
- :doc:`/api/models` - LogEntry model documentation