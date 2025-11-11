Installation
============

Requirements
------------

- Python 3.10 or higher
- Django 4.2 or higher

Using pip
---------

.. code-block:: bash

   pip install django-logmancer

Using uv
--------

.. code-block:: bash

   uv add django-logmancer

Using poetry
------------

.. code-block:: bash

   poetry add django-logmancer

From Source
-----------

.. code-block:: bash

   git clone https://github.com/abdulsamet/logmancer.git
   cd logmancer
   pip install -e .

Development Installation
------------------------

For development with all dependencies:

.. code-block:: bash

   git clone https://github.com/abdulsamet/logmancer.git
   cd logmancer
   uv sync --group dev --group docs

Verifying Installation
----------------------

.. code-block:: python

   import logmancer
   print(logmancer.__version__)

Next Steps
----------

Continue to :doc:`getting-started` to configure Logmancer.
