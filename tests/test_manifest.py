""" Tests for creation of a manifest.yaml file """

import unittest
import os
import collections

import oyaml as yaml

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

    def _create_data_and_metadata_files(self):
        with open(self.data_filename, 'w+') as f:
            f.write('')
        with open(self.metadata_filename, 'w+') as f:
            f.write('')
        self.generator.filenames['data'] = [self.data_filename]
        self.generator.filenames['metadata'] = [self.metadata_filename]

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
        self._create_data_and_metadata_files()
        self.generator.populate()

    def test_populate_with_data_file_populates_field_data(self):
        self._create_data_and_metadata_files()
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
        self._create_data_and_metadata_files()
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
            self.assertEqual(
                self.generator.manifest['files']['metadata'][idx]['name'],
                filename)
        for name in metadata_filenames:
            os.remove(name)

    def test_populate_with_metadata_file_gets_metadata_info(self):
        self._create_data_and_metadata_files()
        self.generator.populate()
        self.assertEqual(
            list(self.generator.manifest['files']['metadata'][0].keys()),
            ['name', 'format', 'version'])

    def test_populate_with_files_populates_checksums(self):
        self._create_data_and_metadata_files()
        self.generator.populate()
        self.assertEqual(len(self.generator.manifest['files']['checksums']), 2)

    def test_populate_with_files_creates_checksums_structure(self):
        self._create_data_and_metadata_files()
        self.generator.populate()
        self.assertEqual(
            list(self.generator.manifest['files']['checksums'][0].keys()),
            ['name', 'format', 'span', 'value'])

    def test_populate_with_files_creates_correct_checksums(self):
        self._create_data_and_metadata_files()
        self.generator.populate()
        self.assertEqual(
            self.generator.manifest['files']['checksums'][0]['value'],
            '020eb29b524d7ba672d9d48bc72db455')
        self.assertEqual(
            self.generator.manifest['files']['checksums'][1]['value'],
            '74be16979710d4c4e7c6647856088456')

    def test_written_manifest_is_correct(self):
        self._create_data_and_metadata_files()
        self.generator.populate()
        self.generator.write()
        with open('MANIFEST.yaml', 'r') as file:
            manifest_dict = yaml.safe_load(file)
        self.assertEqual(self.generator.manifest, manifest_dict)

    def test_populate_sets_format(self):
        self._create_data_and_metadata_files()
        self.generator.populate()
        self.assertTrue(self.generator.manifest['files']['data']['format'])


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.manifest = manifest.Manifest()

    def test_instantiate_class(self):
        pass

    def test_has_from_file_method(self):
        self.assertTrue(hasattr(self.manifest, 'from_file'))
        self.assertTrue(callable(self.manifest.from_file))

    def test_has_to_file_method(self):
        self.assertTrue(hasattr(self.manifest, 'to_file'))
        self.assertTrue(callable(self.manifest.to_file))

    def test_has_data_filenames_attribute(self):
        self.assertTrue(hasattr(self.manifest, 'data_filenames'))
        self.assertIsInstance(self.manifest.data_filenames, list)

    def test_has_metadata_filenames_attribute(self):
        self.assertTrue(hasattr(self.manifest, 'metadata_filenames'))
        self.assertIsInstance(self.manifest.metadata_filenames, list)

    def test_has_data_checksum_attribute(self):
        self.assertTrue(hasattr(self.manifest, 'data_checksum'))

    def test_has_checksum_attribute(self):
        self.assertTrue(hasattr(self.manifest, 'checksum'))

    def test_has_to_dict_method(self):
        self.assertTrue(hasattr(self.manifest, 'to_dict'))
        self.assertTrue(callable(self.manifest.to_dict))

    def test_to_dict_returns_ordered_dict(self):
        self.assertIsInstance(self.manifest.to_dict(), collections.OrderedDict)

    def test_to_dict_returns_ordered_dict_with_correct_keys(self):
        manifest_keys_level_one = ['format', 'dataset', 'files']
        self.assertEqual(list(self.manifest.to_dict()), manifest_keys_level_one)

    def test_to_dict_type_is_datasafe_manifest(self):
        manifest_ = self.manifest.to_dict()
        self.assertEqual(manifest_["format"]["type"],
                         "datasafe dataset manifest")

    def test_to_dict_version_is_not_empty(self):
        manifest_ = self.manifest.to_dict()
        self.assertTrue(manifest_["format"]["version"])

    def test_to_dict_dataset_has_loi(self):
        manifest_ = self.manifest.to_dict()
        self.assertTrue("loi" in manifest_['dataset'].keys())

    def test_to_dict_dataset_has_complete_field(self):
        manifest_ = self.manifest.to_dict()
        self.assertTrue("complete" in manifest_['dataset'].keys())

    def test_to_dict_files_has_minimal_structure(self):
        manifest_ = self.manifest.to_dict()
        manifest_files_keys = ["metadata", "data", "checksums"]
        self.assertEqual(list(manifest_["files"].keys()),
                         manifest_files_keys)

    def test_to_dict_with_data_filenames_populates_dict(self):
        filenames = ['foo', 'bar']
        self.manifest.data_filenames = filenames
        manifest_ = self.manifest.to_dict()
        self.assertEqual(manifest_['files']['data']['names'], filenames)


if __name__ == '__main__':
    unittest.main()
