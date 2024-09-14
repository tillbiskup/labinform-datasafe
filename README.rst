LabInform Datasafe
==================

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.13763299.svg
   :target: https://doi.org/10.5281/zenodo.13763299
   :align: right

*A local repository for "warm" research data.*

The LabInform datasafe is the **local repository for "warm" research data** that is part of the `LabInform laboratory information and management system <https://www.labinform.de/>`_ (LIMS). One key aspect of handling data is to safely store them in one place and access them via **unique and stable identifiers** (here: a *Lab Object Identifier*, LOI). While data belonging to (textual) publications can often be stored in public repositories, we need a safe place for all our (unpublished) data, starting with their acquisition and independent of their current state. This is meant by "warm" research data -- a term coined by `scientists from KIT <https://doi.org/10.5334/dsj-2021-008>`_.


Features
========

A list of features, not all implemented yet but aimed at for the first public release:

* Repository for "warm" research data: one central place

* Access to data using unique and persistent IDs (*Lab Object Identifier*, LOI)

* Client-server architecture, supporting local and network operation

* Full control over the data: runs locally on your own hardware

* Automatic generation of unique IDs for data

* Pre-register IDs before starting the data acquisition.

* Checksums for automatically checking data integrity


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.9)

* Developed fully test-driven

* Extensive user and API documentation


Warning

The dataset component of the LabInform project is currently under active development and still considered in Beta development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Requirements
============

The LabInform datasafe package comes with a rather minimal set of requirements:

* Python >= 3.9
* flask and oyaml packages


How to cite
===========

The LabInform datasafe is free software. However, if you use it for your own research, you may cite it:

* Mirjam Schröder, Till Biskup. LabInform datasafe (2024). `doi:10.5281/zenodo.13763299 <https://doi.org/10.5281/zenodo.13763299>`_

To make things easier, the LabInform datasafe has a `DOI <https://doi.org/10.5281/zenodo.13763299>`_ provided by `Zenodo <https://zenodo.org/>`_, and you may click on the badge below to directly access the record associated with it. Note that this DOI refers to the package as such and always forwards to the most current version.

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.13763299.svg
   :target: https://doi.org/10.5281/zenodo.13763299


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
