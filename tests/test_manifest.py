""" Tests for creation of a manifest.yaml file """

import unittest
import os
import collections

from datasafe import manifest


class TestManifestGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = manifest.Generator()
        self.filename = 'MANIFEST.yaml'
        self.data_filename = 'foo'
        self.metadata_filename = 'bar.info'

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.data_filename):
            os.remove(self.data_filename)
        if os.path.exists(self.metadata_filename):
            os.remove(self.metadata_filename)

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

    def test_populate_without_data_filenames_raises(self):
        self.generator.filenames['metadata'] = [self.metadata_filename]
        with self.assertRaises(manifest.MissingInformationError):
            self.generator.populate()

    def test_populate_without_metadata_filenames_raises(self):
        self.generator.filenames['data'] = [self.data_filename]
        with self.assertRaises(manifest.MissingInformationError):
            self.generator.populate()

    def test_populate_with_missing_data_files_raises(self):
        self.generator.filenames['data'] = [self.data_filename]
        self.generator.filenames['metadata'] = [self.metadata_filename]
        with self.assertRaises(manifest.MissingFileError):
            self.generator.populate()

    def test_populate_with_missing_metadata_files_raises(self):
        with open(self.data_filename, 'w+') as f:
            f.write('')
        self.generator.filenames['data'] = [self.data_filename]
        self.generator.filenames['metadata'] = [self.metadata_filename]
        with self.assertRaises(manifest.MissingFileError):
            self.generator.populate()

    def test_populate_with_filenames_does_not_raise(self):
        with open(self.data_filename, 'w+') as f:
            f.write('')
        with open(self.metadata_filename, 'w+') as f:
            f.write('')
        self.generator.filenames['data'] = [self.data_filename]
        self.generator.filenames['metadata'] = [self.metadata_filename]
        self.generator.populate()

    def test_populate_with_data_file_populates_field_data(self):
        with open(self.data_filename, 'w+') as f:
            f.write('')
        with open(self.metadata_filename, 'w+') as f:
            f.write('')
        self.generator.filenames['data'] = [self.data_filename]
        self.generator.filenames['metadata'] = [self.metadata_filename]
        self.generator.populate()
        self.assertEqual(self.generator.manifest['files']['data']['names'][0],
                         self.data_filename)

    def test_populate_with_data_files_populates_field_data(self):
        data_filenames = ['foo1', 'foo2', 'foo3']
        for name in data_filenames:
            with open(name, 'w+') as f:
                f.write('')
        with open(self.metadata_filename, 'w+') as f:
            f.write('')
        self.generator.filenames['data'] = data_filenames
        self.generator.filenames['metadata'] = [self.metadata_filename]
        self.generator.populate()
        self.assertEqual(self.generator.manifest['files']['data']['names'],
                         data_filenames)
        for name in data_filenames:
            os.remove(name)

    def test_populate_with_metadata_file_populates_field_metadata(self):
        with open(self.data_filename, 'w+') as f:
            f.write('')
        with open(self.metadata_filename, 'w+') as f:
            f.write('')
        self.generator.filenames['data'] = [self.data_filename]
        self.generator.filenames['metadata'] = [self.metadata_filename]
        self.generator.populate()
        self.assertEqual(self.generator.manifest['files']['metadata'][
                             0]['name'], self.metadata_filename)

    def test_populate_with_metadata_files_populates_field_metadata(self):
        metadata_filenames = ['foo1', 'foo2', 'foo3']
        for name in metadata_filenames:
            with open(name, 'w+') as f:
                f.write('')
        with open(self.data_filename, 'w+') as f:
            f.write('')
        self.generator.filenames['data'] = [self.data_filename]
        self.generator.filenames['metadata'] = metadata_filenames
        self.generator.populate()
        for idx, filename in enumerate(metadata_filenames):
            self.assertEqual(self.generator.manifest['files']['metadata'][idx][
                                 'name'], filename)
        for name in metadata_filenames:
            os.remove(name)


if __name__ == '__main__':
    unittest.main()
