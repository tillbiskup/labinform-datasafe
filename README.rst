LabInform Datasafe
==================

*A local repository for "warm" research data.*

The LabInform datasafe is the **data store for "warm" research data** that is part of the `LabInform laboratory information and management system <https://www.labinform.de/>`_ (LIMS). One key aspect of handling data is to store them in one place and access them via unique identifiers (here: a *Lab Object Identifier*, LOI).



Features
========

A list of features, not all implemented yet but aimed at for the first public release:

* Client-server architecture

* Local install as well as network install possible

* Automatic generation of unique LOIs


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.7)

* Developed fully test-driven

* Extensive user and API documentation


Warning

The dataset component of the LabInform project is currently under active development and still considered in Alpha development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Requirements
============

The LabInform datasafe package comes with a rather minimal set of requirements:

* Python >= 3.7
* flask and oyaml packages


Installation
============

To install the LabInform datasafe package on your computer (sensibly within a Python virtual environment), open a terminal (activate your virtual environment), and type in the following:

.. code-block:: bash

    pip install labinform-datasafe


License
=======

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**.


Contributing
============

If you would like to contribute, the easiest may be to clone the repository. In this case, don't forget to add the version incrementer residing in ``./bin/incrementVersion.sh`` to your git pre-commit hook in `./.git/hooks/pre-commit`` (or create this file if it doesn't exist yet)::

    #!/usr/bin/env bash
    ./bin/incrementVersion.sh

In case you needed to create the file ``pre-commit``, don't forget to make it executable (using ``chmod +x <file>``).
