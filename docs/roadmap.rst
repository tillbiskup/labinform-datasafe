=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.1
===============

* Configuration handling: via configuration files or else

* CLI for client

* Documentation: How to setup a datasafe server and storage backend

* Probably: Implement another web server than the flask builtin server


For later versions
==================

* Generalise and subclass :class:`datasafe.manifest.Manifest` to work with items different from datasets.

* Backend worker updating a database with LOIs and corresponding checksums for easy checking of already existing datasets

* Implement delete methods.


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::
