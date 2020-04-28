Datasafe
========

...


.. warning::
  The dataset component of the LabInform project is currently under active development and still considered in Alpha development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.



Developers
----------

If you would like to contribute, the easiest may be to clone the repository. In this case, don't forget to add the version incrementer residing in ``./bin/incrementVersion.sh`` to your git pre-commit hook in `./.git/hooks/pre-commit`` (or create this file if it doesn't exist yet)::

    #!/usr/bin/env bash
    ./bin/incrementVersion.sh

In case you needed to create the file ``pre-commit``, don't forget to make it executable (using ``chmod +x <file>``).
