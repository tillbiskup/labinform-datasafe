import unittest

import datasafe.configuration as config


class TestStorageBackendConfig(unittest.TestCase):
    def setUp(self):
        self.config = config.StorageBackend()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        for attribute in ["manifest_filename", "root_directory"]:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.config, attribute))
