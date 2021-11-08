"""Configuration for datasafe."""


class StorageBackend:

    def __init__(self):
        self.checksum_filename = ''
        self.checksum_data_filename = ''
        self.manifest_filename = ''
        self.root_directory = 'datasafe_root'
