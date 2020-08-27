""" Tests for creation of a manifest.yaml file """

import unittest
import os
import collections

from datasafe import manifest


class TestManifestGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = manifest.Generator()
        self.filename = 'MANIFEST.yaml'

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_has_write_method(self):
        self.assertTrue(hasattr(self.generator, 'write'))
        self.assertTrue(callable(self.generator.write))

    def test_write_creates_yaml_file(self):
        self.generator.write()
        self.assertTrue(os.path.exists(self.filename))

    def test_has_manifest_attribute(self):
        self.assertTrue(hasattr(self.generator, 'manifest'))

    def test_manifest_attribute_is_ordered_dict(self):
        self.assertTrue(isinstance(self.generator.manifest,
                                   collections.OrderedDict))

    def test_manifest_has_minimal_structure(self):
        manifest_keys_level_one = ['format', 'dataset', 'files']
        self.assertEqual(list(self.generator.manifest.keys()),
                         manifest_keys_level_one)

    def test_manifest_type_is_datasafe_manifest(self):
        self.assertEqual(self.generator.manifest["format"]["type"],
                         "datasafe dataset manifest")

    def test_manifest_version_is_not_empty(self):
        self.assertTrue(self.generator.manifest["format"]["version"])

    def test_manifest_dataset_has_loi(self):
        self.assertTrue("loi" in self.generator.manifest["dataset"].keys())

    def test_manifest_dataset_has_complete_field(self):
        self.assertTrue("complete" in self.generator.manifest["dataset"].keys())

    def test_manifest_files_has_minimal_structure(self):
        manifest_files_keys = ["metadata", "data", "checksums"]
        self.assertEqual(list(self.generator.manifest["files"].keys()),
                         manifest_files_keys)

    def test_manifest_has_populate_method(self):
        self.assertTrue(hasattr(self.generator, 'populate'))
        self.assertTrue(callable(self.generator.populate))

    @unittest.skip
    def test_populate_without_files_raises(self):
        with self.assertRaises(MissingInformationError):
            self.generator.populate()


if __name__ == '__main__':
    unittest.main()
