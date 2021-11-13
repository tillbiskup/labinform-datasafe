""" Tests for creation of a manifest.yaml file """

import unittest
import os
import collections

import oyaml as yaml

from datasafe import manifest
from datasafe.exceptions import NoFileError, MissingInformationError


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.manifest = manifest.Manifest()
        self.manifest_filename = 'MANIFEST.yaml'
        self.data_filename = 'foo'
        self.metadata_filename = 'bar'
        self.manifest.data_filenames = [self.data_filename]
        self.manifest.metadata_filenames = [self.metadata_filename]

    def tearDown(self):
        for filename in [self.data_filename, self.metadata_filename,
                         self.manifest_filename]:
            if os.path.exists(filename):
                os.remove(filename)

    def create_data_and_metadata_files(self):
        with open(self.data_filename, 'w+') as f:
            f.write('')
        with open(self.metadata_filename, 'w+') as f:
            f.write('')

    def create_magnettech_xml_file(self):
        self.data_filename = 'test.xml'
        with open(self.data_filename, 'w+') as file:
            file.write('<?xml version="1.0" encoding="utf-8"?>\n<ESRXmlFile '
                       'Version="1" Timestamp="2019-07-23T13:43:49.6413649Z">')
        self.manifest.data_filenames = [self.data_filename]

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

    def test_to_dict_returns_dict(self):
        self.create_data_and_metadata_files()
        self.assertIsInstance(self.manifest.to_dict(), dict)

    def test_to_dict_returns_dict_with_correct_keys(self):
        self.create_data_and_metadata_files()
        manifest_keys_level_one = ['format', 'dataset', 'files', 'checksums']
        self.assertEqual(list(self.manifest.to_dict()), manifest_keys_level_one)

    def test_to_dict_type_is_datasafe_manifest(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertEqual(manifest_["format"]["type"],
                         "datasafe dataset manifest")

    def test_to_dict_version_is_not_empty(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertTrue(manifest_["format"]["version"])

    def test_to_dict_dataset_has_loi(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertTrue("loi" in manifest_['dataset'].keys())

    def test_to_dict_dataset_has_complete_field(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertTrue("complete" in manifest_['dataset'].keys())

    def test_to_dict_files_has_minimal_structure(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        manifest_files_keys = ["metadata", "data"]
        self.assertEqual(list(manifest_["files"].keys()),
                         manifest_files_keys)

    def test_to_dict_with_data_filenames_populates_dict(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertEqual(manifest_['files']['data']['names'][0],
                         self.data_filename)

    def test_to_dict_with_data_filenames_sets_format(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertTrue(manifest_['files']['data']['format'])

    def test_to_dict_with_metadata_filename_populates_dict(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertEqual(manifest_['files']['metadata'][0]['name'],
                         self.metadata_filename)

    def test_to_dict_with_metadata_filename_gets_metadata_info(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertEqual(
            list(manifest_['files']['metadata'][0].keys()),
            ['name', 'format', 'version'])

    def test_to_dict_with_files_populates_checksums(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertEqual(len(manifest_['checksums']), 2)

    def test_to_dict_with_files_creates_checksums_structure(self):
        self.create_data_and_metadata_files()
        self.manifest.data_filenames = [self.data_filename]
        manifest_ = self.manifest.to_dict()
        self.assertEqual(
            list(manifest_['checksums'][0].keys()),
            ['name', 'format', 'span', 'value'])

    def test_to_dict_with_files_creates_correct_checksums(self):
        self.create_data_and_metadata_files()
        manifest_ = self.manifest.to_dict()
        self.assertEqual(
            manifest_['checksums'][0]['value'],
            '020eb29b524d7ba672d9d48bc72db455')
        self.assertEqual(
            manifest_['checksums'][1]['value'],
            '74be16979710d4c4e7c6647856088456')

    def test_to_dict_without_data_filenames_raises(self):
        self.manifest.data_filenames = []
        with self.assertRaises(MissingInformationError):
            self.manifest.to_dict()

    def test_to_dict_with_missing_data_files_raises(self):
        with self.assertRaisesRegex(NoFileError, self.data_filename):
            self.manifest.to_dict()

    def test_to_dict_with_missing_metadata_files_raises(self):
        with open(self.data_filename, 'w+') as f:
            f.write('')
        with self.assertRaisesRegex(NoFileError, self.metadata_filename):
            self.manifest.to_dict()

    def test_to_dict_with_filenames_does_not_raise(self):
        self.create_data_and_metadata_files()
        self.manifest.to_dict()

    def test_to_dict_with_data_files_populates_field_data(self):
        data_filenames = ['foo1', 'foo2', 'foo3']
        for name in data_filenames:
            with open(name, 'w+') as f:
                f.write('')
        with open(self.metadata_filename, 'w+') as f:
            f.write('')
        self.manifest.data_filenames = data_filenames
        self.manifest.metadata_filenames = [self.metadata_filename]
        manifest_ = self.manifest.to_dict()
        self.assertEqual(manifest_['files']['data']['names'], data_filenames)
        for name in data_filenames:
            os.remove(name)

    def test_to_dict_with_metadata_files_populates_field_metadata(self):
        metadata_filenames = ['foo1', 'foo2', 'foo3']
        for name in metadata_filenames:
            with open(name, 'w+') as f:
                f.write('')
        with open(self.data_filename, 'w+') as f:
            f.write('')
        self.manifest.data_filenames = [self.data_filename]
        self.manifest.metadata_filenames = metadata_filenames
        manifest_ = self.manifest.to_dict()
        for idx, filename in enumerate(metadata_filenames):
            self.assertEqual(manifest_['files']['metadata'][idx]['name'],
                             filename)
        for name in metadata_filenames:
            os.remove(name)

    def test_to_dict_with_loi_sets_loi(self):
        self.create_data_and_metadata_files()
        self.manifest.loi = '42.1001/ds/'
        dict_ = self.manifest.to_dict()
        self.assertEqual(self.manifest.loi, dict_['dataset']['loi'])

    def test_to_dict_with_unknown_file_format(self):
        self.create_data_and_metadata_files()
        dict_ = self.manifest.to_dict()
        self.assertEqual('undetected', dict_['files']['data']['format'])

    def test_to_dict_with_magnettech_xml_file_detects_file_format(self):
        self.create_data_and_metadata_files()
        self.create_magnettech_xml_file()
        dict_ = self.manifest.to_dict()
        self.assertEqual('Magnettech XML', dict_['files']['data']['format'])

    def test_to_file_creates_yaml_file(self):
        self.create_data_and_metadata_files()
        self.manifest.to_file()
        self.assertTrue(os.path.exists(self.manifest_filename))

    def test_written_manifest_is_correct(self):
        self.create_data_and_metadata_files()
        self.manifest.to_file()
        with open(self.manifest_filename, 'r') as file:
            manifest_dict = yaml.safe_load(file)
        self.assertEqual(self.manifest.to_dict(), manifest_dict)

    def test_has_from_dict_method(self):
        self.assertTrue(hasattr(self.manifest, 'from_dict'))
        self.assertTrue(callable(self.manifest.from_dict))

    def test_from_dict_sets_data_filenames(self):
        self.create_data_and_metadata_files()
        self.manifest.to_file()
        with open(self.manifest_filename, 'r') as file:
            manifest_dict = yaml.safe_load(file)
        new_manifest = manifest.Manifest()
        new_manifest.from_dict(manifest_dict)
        self.assertEqual(manifest_dict['files']['data']['names'],
                         new_manifest.data_filenames)

    def test_from_dict_sets_metadata_filenames(self):
        self.create_data_and_metadata_files()
        self.manifest.to_file()
        with open(self.manifest_filename, 'r') as file:
            manifest_dict = yaml.safe_load(file)
        new_manifest = manifest.Manifest()
        new_manifest.from_dict(manifest_dict)
        self.assertEqual([manifest_dict['files']['metadata'][0]['name']],
                         new_manifest.metadata_filenames)

    def test_from_dict_with_multiple_metadata_filenames_sets_metadata(self):
        metadata_filename_ = 'blub'
        with open(metadata_filename_, 'w+') as f:
            f.write('')
        self.manifest.metadata_filenames.append(metadata_filename_)
        self.create_data_and_metadata_files()
        self.manifest.to_file()
        with open(self.manifest_filename, 'r') as file:
            manifest_dict = yaml.safe_load(file)
        new_manifest = manifest.Manifest()
        new_manifest.from_dict(manifest_dict)
        self.assertEqual(manifest_dict['files']['metadata'][1]['name'],
                         new_manifest.metadata_filenames[1])
        if os.path.exists(metadata_filename_):
            os.remove(metadata_filename_)

    def test_from_dict_sets_loi(self):
        self.create_data_and_metadata_files()
        self.manifest.loi = '42.1001/ds/foo'
        self.manifest.to_file()
        with open(self.manifest_filename, 'r') as file:
            manifest_dict = yaml.safe_load(file)
        new_manifest = manifest.Manifest()
        new_manifest.from_dict(manifest_dict)
        self.assertEqual(self.manifest.loi, new_manifest.loi)

    def test_from_file_without_filename_uses_default_filename(self):
        self.create_data_and_metadata_files()
        self.manifest.to_file()
        self.manifest.from_file()
        self.assertTrue(self.manifest.data_filenames)

    def test_from_file_with_missing_file_raises(self):
        with self.assertRaises(NoFileError):
            self.manifest.from_file(filename="foobar")

    def test_from_file_with_file_sets_properties_from_manifest(self):
        self.create_data_and_metadata_files()
        self.manifest.to_file()
        new_manifest = manifest.Manifest()
        new_manifest.from_file(self.manifest_filename)
        with open(self.manifest_filename, 'r') as file:
            manifest_dict = yaml.safe_load(file)
        self.assertEqual(new_manifest.to_dict(), manifest_dict)

    def test_from_file_sets_checksum(self):
        self.create_data_and_metadata_files()
        self.manifest.to_file()
        new_manifest = manifest.Manifest()
        new_manifest.from_file(self.manifest_filename)
        with open(self.manifest_filename, 'r') as file:
            manifest_dict = yaml.safe_load(file)
        for checksum in manifest_dict['checksums']:
            if 'metadata' in checksum['span']:
                self.assertEqual(checksum['value'], new_manifest.checksum)
            else:
                self.assertEqual(checksum['value'], new_manifest.data_checksum)

    def test_has_check_integrity_method(self):
        self.assertTrue(hasattr(self.manifest, 'check_integrity'))
        self.assertTrue(callable(self.manifest.check_integrity))

    def test_check_integrity_with_missing_information_raises(self):
        with self.assertRaises(MissingInformationError):
            self.manifest.check_integrity()

    def test_check_integrity_returns_dict(self):
        self.create_data_and_metadata_files()
        self.manifest.from_dict(self.manifest.to_dict())
        self.assertIsInstance(self.manifest.check_integrity(), dict)

    def test_check_integrity_dict_contains_correct_fields(self):
        self.create_data_and_metadata_files()
        self.manifest.from_dict(self.manifest.to_dict())
        self.assertCountEqual(['data', 'all'],
                              self.manifest.check_integrity().keys())

    def test_check_integrity_with_incorrect_overall_checksum(self):
        self.create_data_and_metadata_files()
        self.manifest.from_dict(self.manifest.to_dict())
        self.manifest.checksum = 'foo'
        self.assertFalse(self.manifest.check_integrity()['all'])

    def test_check_integrity_with_incorrect_data_checksum(self):
        self.create_data_and_metadata_files()
        self.manifest.from_dict(self.manifest.to_dict())
        self.manifest.data_checksum = 'foo'
        self.assertFalse(self.manifest.check_integrity()['data'])


class TestFormatDetector(unittest.TestCase):

    def setUp(self):
        self.detector = manifest.FormatDetector()
        self.metadata_filename = ''

    def tearDown(self):
        if os.path.exists(self.metadata_filename):
            os.remove(self.metadata_filename)

    def test_instantiate_class(self):
        pass

    def test_has_data_filenames_attribute(self):
        self.assertTrue(hasattr(self.detector, 'data_filenames'))
        self.assertIsInstance(self.detector.data_filenames, list)

    def test_has_metadata_filenames_attribute(self):
        self.assertTrue(hasattr(self.detector, 'metadata_filenames'))
        self.assertIsInstance(self.detector.metadata_filenames, list)

    def test_has_metadata_format_method(self):
        self.assertTrue(hasattr(self.detector, 'metadata_format'))
        self.assertTrue(callable(self.detector.metadata_format))

    def test_has_data_format_method(self):
        self.assertTrue(hasattr(self.detector, 'data_format'))
        self.assertTrue(callable(self.detector.data_format))

    def test_metadata_format_without_metadata_returns_empty_list(self):
        self.assertEqual([], self.detector.metadata_format())

    def test_metadata_format_returns_list_of_dicts(self):
        self.detector.metadata_filenames = ['foo']
        self.assertIsInstance(self.detector.metadata_format(), list)
        self.assertIsInstance(self.detector.metadata_format()[0], dict)

    def test_metadata_format_dict_contains_filename(self):
        self.detector.metadata_filenames = ['foo']
        metadata_info = self.detector.metadata_format()
        self.assertEqual(self.detector.metadata_filenames[0],
                         metadata_info[0]['name'])

    def test_metadata_format_parses_info_file(self):
        self.metadata_filename = 'test.info'
        self.detector.metadata_filenames = [self.metadata_filename]
        with open(self.metadata_filename, 'w+') as file:
            file.write('cwEPR Info file - v. 0.1.4 (2020-01-21)')
        metadata_info = self.detector.metadata_format()
        self.assertEqual('cwEPR Info file', metadata_info[0]['format'])
        self.assertEqual('0.1.4', metadata_info[0]['version'])

    def test_metadata_format_parses_yaml_file(self):
        self.metadata_filename = 'test.yaml'
        self.detector.metadata_filenames = [self.metadata_filename]
        info_dict = {'format': {'type': 'info file', 'version': '0.1.2'}}
        with open(self.metadata_filename, 'w+') as file:
            yaml.dump(info_dict, file)
        metadata_info = self.detector.metadata_format()
        self.assertEqual('info file', metadata_info[0]['format'])
        self.assertEqual('0.1.2', metadata_info[0]['version'])

    def test_metadata_format_parses_yml_file(self):
        self.metadata_filename = 'test.yml'
        self.detector.metadata_filenames = [self.metadata_filename]
        info_dict = {'format': {'type': 'info file', 'version': '0.1.2'}}
        with open(self.metadata_filename, 'w+') as file:
            yaml.dump(info_dict, file)
        metadata_info = self.detector.metadata_format()
        self.assertEqual('info file', metadata_info[0]['format'])
        self.assertEqual('0.1.2', metadata_info[0]['version'])

    def test_data_format_without_filenames_raises(self):
        message = 'No data filenames'
        with self.assertRaisesRegex(NoFileError, message):
            self.detector.data_format()

    def test_data_format_returns_string(self):
        self.detector.data_filenames = ['foo']
        self.assertIsInstance(self.detector.data_format(), str)


class TestEPRFormatDetector(unittest.TestCase):

    def setUp(self):
        self.detector = manifest.EPRFormatDetector()
        self.metadata_filenames = ['test.info']
        self.data_filenames = []

    def tearDown(self):
        for filename in [*self.data_filenames, *self.metadata_filenames]:
            if os.path.exists(filename):
                os.remove(filename)

    def test_instantiate_class(self):
        pass

    def create_metadata_file(self):
        with open(self.metadata_filenames[0], 'w+') as f:
            f.write('cwEPR Info file - v. 0.1.4 (2020-01-21)')

    def create_esp_data_files(self):
        self.data_filenames = ['test.par', 'test.spc']
        with open('test.par', 'w+') as f:
            f.write('JSS  2\nADEV  1')
        with open('test.spc', 'w+') as f:
            f.write('')

    def create_emx_data_files(self):
        self.data_filenames = ['test.par', 'test.spc']
        with open('test.par', 'w+') as f:
            f.write('DOS  Format\nANZ 1024')
        with open('test.spc', 'w+') as f:
            f.write('')

    def create_bes3t_data_files(self):
        self.data_filenames = ['test.DSC', 'test.DTA']
        with open('test.DSC', 'w+') as f:
            f.write('#DESC	1.2 * DESCRIPTOR INFORMATION '
                    '***********************\n*')
        with open('test.DTA', 'w+') as f:
            f.write('')

    def create_magnettech_xml_file(self):
        self.data_filenames = ['test.xml']
        with open(self.data_filenames[0], 'w+') as file:
            file.write('<?xml version="1.0" encoding="utf-8"?>\n<ESRXmlFile '
                       'Version="1" Timestamp="2019-07-23T13:43:49.6413649Z">')

    def create_magnettech_csv_file(self):
        self.data_filenames = ['test.csv']
        with open(self.data_filenames[0], 'w+') as file:
            file.write('Name,20190723-Test\n\nRecipe')

    def test_has_check_format_method(self):
        self.assertTrue(hasattr(self.detector, 'detection_successful'))
        self.assertTrue(callable(self.detector.detection_successful))

    def test_check_format_returns_boolean_value(self):
        self.assertIsInstance(self.detector.detection_successful(), bool)

    def test_data_format_with_esp_files(self):
        self.create_esp_data_files()
        self.detector.data_filenames = self.data_filenames
        self.assertEqual('Bruker ESP', self.detector.data_format())
        self.assertTrue(self.detector.detection_successful())

    def test_data_format_with_emx_files(self):
        self.create_emx_data_files()
        self.detector.data_filenames = self.data_filenames
        self.assertEqual('Bruker EMX', self.detector.data_format())
        self.assertTrue(self.detector.detection_successful())

    def test_data_format_with_bes3t_files(self):
        self.create_bes3t_data_files()
        self.detector.data_filenames = self.data_filenames
        self.assertEqual('Bruker BES3T', self.detector.data_format())
        self.assertTrue(self.detector.detection_successful())

    def test_data_format_with_magnettech_xml_files(self):
        self.create_magnettech_xml_file()
        self.detector.data_filenames = self.data_filenames
        self.assertEqual('Magnettech XML', self.detector.data_format())
        self.assertTrue(self.detector.detection_successful())

    def test_data_format_with_magnettech_csv_files(self):
        self.create_magnettech_csv_file()
        self.detector.data_filenames = self.data_filenames
        self.assertEqual('Magnettech CSV', self.detector.data_format())
        self.assertTrue(self.detector.detection_successful())
