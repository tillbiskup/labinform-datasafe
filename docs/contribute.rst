Information for contributors
============================

We would be happy to receive contributions!

Setting up the development environment
--------------------------------------

It is highly recommended to (always) develop Python code in virtual environments.

Create a virtual environment, e.g., with ``virtualenv <environment>``, and activate it afterwards with ``<environment>/bin/activate``. Then install the package in development mode using ``pip`` with the ``-e`` switch.

.. code:: bash

    pip install -e .

Note that you need to be in the root directory of the package for the above command, otherwise specify the path to the Python package after the ``-e`` switch instead of ``.``.


Setting up the documentation build system
-----------------------------------------

The documentation is built using `Sphinx <https://sphinx-doc.org/>`_, `Python <https://python.org/>`_, and `sphinx_rtd_theme <https://pypi.python.org/pypi/sphinx_rtd_theme>`_. Building requires using a shell, for example ``bash``.


To install the necessary Python dependencies, create a virtual environment, e.g., with ``virtualenv <environment>``, and activate it afterwards with ``<environment>/bin/activate``. Then install the dependencies using ``pip``.

.. code:: bash

    pip install sphinx
    pip install sphinx_rtd_theme


To build the documentation:

    * Activate the virtual environment where the necessary dependencies are installed in.
    * ``cd`` to ``docs/``, then run ``make html``. (To clean previously built documentation, run ``make clean`` first).

