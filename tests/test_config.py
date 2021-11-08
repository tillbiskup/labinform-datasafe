import unittest

import datasafe.config as config


class TestStorageBackendConfig(unittest.TestCase):
    def setUp(self):
        self.config = config.StorageBackend()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        for attribute in ['checksum_filename', 'checksum_data_filename',
                          'manifest_filename', 'root_directory']:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.config, attribute))
