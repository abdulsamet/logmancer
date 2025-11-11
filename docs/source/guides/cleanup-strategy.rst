Log Cleanup Strategy
====================

Overview
--------

Logmancer stores all logs in your database. Over time, this can grow significantly. This guide covers strategies for managing log retention.

Default Behavior
----------------

By default, Logmancer retains logs indefinitely. You must manually clean up old logs.

Configuration
-------------

Set Retention Period
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # settings.py
   LOGMANCER = {
       'CLEANUP_AFTER_DAYS': 30,  # Retain last 30 days
   }

Manual Cleanup
~~~~~~~~~~~~~~

.. code-block:: bash

   # Use configured retention period
   python manage.py logmancer_cleanup

   # Custom period
   python manage.py logmancer_cleanup --days=60

Automated Cleanup
-----------------

Linux/macOS (Cron)
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Edit crontab
   crontab -e

   # Add daily cleanup at 2 AM
   0 2 * * * cd /path/to/project && /path/to/venv/bin/python manage.py logmancer_cleanup

Windows Task Scheduler
~~~~~~~~~~~~~~~~~~~~~~~

1. Open **Task Scheduler**
2. Create **Basic Task**
3. Set trigger: **Daily at 2:00 AM**
4. Action: **Start a program**

   * Program: ``C:\path\to\python.exe``
   * Arguments: ``manage.py logmancer_cleanup``
   * Start in: ``C:\path\to\project``

Django Management Command
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # myapp/management/commands/daily_tasks.py
   from django.core.management import call_command
   from django.core.management.base import BaseCommand

   class Command(BaseCommand):
       def handle(self, *args, **options):
           call_command('logmancer_cleanup', days=30)
           self.stdout.write('Logs cleaned up')

Celery Beat (Recommended for Production)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # settings.py
   from celery.schedules import crontab

   CELERY_BEAT_SCHEDULE = {
       'cleanup-logs': {
           'task': 'myapp.tasks.cleanup_logs',
           'schedule': crontab(hour=2, minute=0),  # 2 AM daily
       },
   }

.. code-block:: python

   # myapp/tasks.py
   from celery import shared_task
   from django.core.management import call_command

   @shared_task
   def cleanup_logs():
       call_command('logmancer_cleanup', days=30)

Retention Strategies
--------------------

By Environment
~~~~~~~~~~~~~~

.. code-block:: python

   # settings.py
   import os

   ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

   LOGMANCER = {
       'CLEANUP_AFTER_DAYS': {
           'production': 90,   # 3 months
           'staging': 30,      # 1 month
           'development': 7,   # 1 week
       }[ENVIRONMENT]
   }

By Log Level
~~~~~~~~~~~~

Archive critical logs separately:

.. code-block:: python

   # Before cleanup
   from logmancer.models import LogEntry
   import json

   critical_logs = LogEntry.objects.filter(
       level__in=['ERROR', 'CRITICAL'],
       timestamp__lt=threshold_date
   )

   # Export to JSON
   with open('archived_logs.json', 'w') as f:
       json.dump(list(critical_logs.values()), f)

   # Then run cleanup
   call_command('logmancer_cleanup')

Selective Retention
~~~~~~~~~~~~~~~~~~~

Keep important logs longer:

.. code-block:: python

   # Custom cleanup script
   from datetime import timedelta
   from django.utils import timezone
   from logmancer.models import LogEntry

   # Delete DEBUG logs after 7 days
   LogEntry.objects.filter(
       level='DEBUG',
       timestamp__lt=timezone.now() - timedelta(days=7)
   ).delete()

   # Delete INFO logs after 30 days
   LogEntry.objects.filter(
       level='INFO',
       timestamp__lt=timezone.now() - timedelta(days=30)
   ).delete()

   # Keep ERROR/CRITICAL for 90 days
   LogEntry.objects.filter(
       level__in=['ERROR', 'CRITICAL'],
       timestamp__lt=timezone.now() - timedelta(days=90)
   ).delete()

Database Optimization
---------------------

Add Indexes
~~~~~~~~~~~

.. code-block:: python

   # migrations/0002_add_cleanup_indexes.py
   from django.db import migrations, models

   class Migration(migrations.Migration):
       dependencies = [
           ('logmancer', '0001_initial'),
       ]

       operations = [
           migrations.AddIndex(
               model_name='logentry',
               index=models.Index(
                   fields=['timestamp', 'level'],
                   name='cleanup_idx'
               ),
           ),
       ]

Vacuum Database (PostgreSQL)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # After large cleanup
   python manage.py dbshell
   VACUUM ANALYZE logmancer_logentry;

Optimize Table (MySQL)
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py dbshell
   OPTIMIZE TABLE logmancer_logentry;

Monitoring Cleanup
------------------

Log Cleanup Activity
~~~~~~~~~~~~~~~~~~~~

The command automatically logs cleanup actions:

.. code-block:: python

   from logmancer.models import LogEntry

   cleanup_logs = LogEntry.objects.filter(
       source='cleanup',
       level='INFO'
   )

   for log in cleanup_logs:
       print(f"{log.timestamp}: {log.meta['count']} logs deleted")

Database Size Tracking
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Track database growth
   from django.db import connection

   def get_table_size():
       with connection.cursor() as cursor:
           cursor.execute("""
               SELECT pg_size_pretty(pg_total_relation_size('logmancer_logentry'))
           """)
           return cursor.fetchone()[0]

   print(f"LogEntry table size: {get_table_size()}")

Best Practices
--------------

1. ✅ **Use dry-run first**: Test with ``--dry-run`` before actual cleanup
2. ✅ **Automate**: Set up scheduled cleanup (cron/Celery)
3. ✅ **Archive critical logs**: Export ERROR/CRITICAL before deletion
4. ✅ **Monitor size**: Track database growth
5. ✅ **Environment-specific**: Different retention for dev/prod
6. ✅ **Index optimization**: Ensure timestamps are indexed
7. ❌ **Don't delete manually**: Use management command for consistency

Troubleshooting
---------------

Cleanup Taking Too Long
~~~~~~~~~~~~~~~~~~~~~~~~

Use batching for large deletions:

.. code-block:: python

   from logmancer.models import LogEntry
   from datetime import timedelta
   from django.utils import timezone

   threshold = timezone.now() - timedelta(days=30)
   batch_size = 1000

   while True:
       ids = list(
           LogEntry.objects.filter(timestamp__lt=threshold)
           .values_list('id', flat=True)[:batch_size]
       )
       if not ids:
           break
       LogEntry.objects.filter(id__in=ids).delete()

Out of Memory
~~~~~~~~~~~~~

Lower batch size or use raw SQL:

.. code-block:: python

   from django.db import connection

   with connection.cursor() as cursor:
       cursor.execute("""
           DELETE FROM logmancer_logentry
           WHERE timestamp < NOW() - INTERVAL '30 days'
       """)