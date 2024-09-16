"""
Configuration for the datasafe components.

There are three components of the LabInform datasafe that eventually need
to be configured: client, server, and storage backend.

There is only one exception that needs not be configured, and this is the
local client and server couple. However, these are not used by "normal"
users, but rather for maintenance purposes.


.. important::

    The configuration is currently not stored in and read from
    configuration files, but only in configuration objects implemented in
    this module. Furthermore, there exists only a configuration object for
    the :class:`StorageBackend <datasafe.server.StorageBackend>` class.
    Hence, the following description is more a plan how to proceed further
    than a description of the current implementation (as of 09/2024).


Necessary configuration
=======================

There are three components of the LabInform datasafe that eventually need
to be configured: client, server, and storage backend.


Client
------

The key value that needs to be defined is the URL of the server to connect
to. A further (optional) configuration value would the URL prefix,
although that us a function of the server and usually defaults to ``api/``.


Server
------

Currently, the built-in flask server component gets used and created by
the function :func:`datasafe.server.create_http_server`. This function can
consume a configuration dictionary, but its values need to be sensibly
defined.

Server configuration may, however, be something rather outside the Python
realm, as this involves configuring an HTTP server (such as nginx),
and potentially TLS certificates.


Storage backend
---------------

For details, see the :class:`StorageBackend` class.



Strategy for storing configuration
==================================

Configuration should be stored in individual files for the three different
components, as the client configuration usually lives in the user space,
while the server and storage backend configuration are typically
maintained by admin personnel.

For server and storage backend configuration, it would be possible to use
a dual approach, with either configuration file or environment variables.

Which format for the configuration files to use needs to be decided. YAML
may be a good choice, however, there are other choices available that are
particularly designed for storing configuration.


Roadmap
=======

As of 09/2024

* Implement :class:`Configuration` base class handling configuration IO
  from/to files in the file system and environment variables.

  * Handle different (default) places for the configuration files,
    depending on the operating system.

* Base :class:`StorageBackend` class on the newly created
  :class:`Configuration` class
* Implement :class:`Client` configuration class.
* Implement :class:`Server` configuration class and define sensible
  configuration values.
* Create configuration files with extensive internal documentation.

  * Decide upon sensible names and storage places.

* Describe the whole installation and setup in the necessary detail.
* Perhaps create install scripts for server and client configuration,
  to make it easier to get started. Those scripts should be CLIs asking the
  user/installer the crucial questions and providing sensible defaults.


Module documentation
====================

"""


class StorageBackend:
    """
    Configuration for the storage backend.

    Attributes
    ----------
    manifest_filename : :class:`str`
        Filename used for the manifest files.

        If empty, the value in
        :attr:`datasafe.manifest.Manifest.manifest_filename` will get used.

        Default: ""

    root_directory : :class:`str`
        Root directory the backend stores the data to

        Default: ``datsafe_root``

    """

    def __init__(self):
        self.manifest_filename = ""
        self.root_directory = "datasafe_root"
