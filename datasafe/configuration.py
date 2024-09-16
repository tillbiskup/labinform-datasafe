"""Configuration for the datasafe components."""


class StorageBackend:
    """
    Configuration for the storage backend.

    Attributes
    ----------
    manifest_filename : :class:`str`
        Filename used for the manifest files.

        Default: ""

    root_directory : :class:`str`
        Root directory the backend stores the data to

        Default: ``datsafe_root``

    """

    def __init__(self):
        self.manifest_filename = ""
        self.root_directory = "datasafe_root"
