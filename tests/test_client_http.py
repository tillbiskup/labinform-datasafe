import os
import shutil
import unittest

import requests

from datasafe import server, client
from datasafe.exceptions import InvalidLoiError, LoiNotFoundError, \
    ExistingFileError, MissingContentError, NoFileError
from datasafe.loi import LoiChecker
from datasafe.manifest import Manifest
from datasafe.utils import change_working_dir


def server_is_running():
    try:
        requests.get('http://127.0.0.1:5000')
        return True
    except:  # noqa
        return False


@unittest.skipUnless(server_is_running(), reason='No HTTP server running')
class TestHTTPClient(unittest.TestCase):

    def setUp(self):
        self.client = client.HTTPClient()
        self.loi = '42.1001/ds/exp/sa/42/cwepr/1'
        self.storage = server.StorageBackend()
        self.storage_root = \
            os.path.realpath(os.path.join('../', self.storage.root_directory))
        self.tempdir = 'tmp'
        self.manifest_filename = Manifest().manifest_filename
        self.data_filename = 'bar.dat'
        self.metadata_filename = 'bar.info'

    def tearDown(self):
        for directory in [self.storage_root, self.tempdir]:
            if os.path.exists(directory):
                shutil.rmtree(directory)

    def create_zip_archive(self):
        os.makedirs(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.create_manifest_file()
        zip_archive = shutil.make_archive(base_name='test', format='zip',
                                          root_dir=self.tempdir)
        with open(zip_archive, 'rb') as zip_file:
            contents = zip_file.read()
        os.remove('test.zip')
        return contents

    def create_manifest_file(self):
        manifest = Manifest()
        manifest.data_filenames = [self.data_filename]
        manifest.metadata_filenames = [self.metadata_filename]
        manifest.to_file()

    def create_data_and_metadata_files(self, path=''):
        with open(os.path.join(path, self.data_filename), 'w+') as f:
            f.write('')
        with open(self.metadata_filename, 'w+') as f:
            f.write('cwEPR Info file - v. 0.1.4 (2020-01-21)')

    def test_create_with_loi_returns_valid_loi(self):
        checker = LoiChecker()
        self.assertTrue(checker.check(self.client.create(self.loi)))

    def test_create_creates_directory_via_backend(self):
        loi = '42.1001/ds/exp/sa/42/cwepr/'
        self.client.create(loi)
        self.assertTrue(os.path.exists(os.path.join(
            self.storage_root, 'exp/sa/42/cwepr/1')))

    def test_upload_with_given_path(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
        self.client.create(loi=self.loi)
        self.client.upload(loi=self.loi, path=self.tempdir)
        manifest = Manifest()
        manifest.from_file(os.path.join(self.tempdir,
                                        manifest.manifest_filename))
        self.assertEqual([self.data_filename], manifest.data_filenames)

    def test_upload_creates_downloadable_items_in_datasafe(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            self.client.upload(loi=self.loi)
            self.path = self.client.download(self.loi)
        self.assertTrue(os.path.isfile(os.path.join(self.path,
                                                    self.manifest_filename)))

    def test_upload_returns_results_of_integrity_check(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            integrity = self.client.upload(loi=self.loi)
        self.assertCountEqual(['all', 'data'], integrity.keys())

    def test_upload_with_invalid_loi_raises(self):
        loi = '42.1001/ds/foo/bar/baz'
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            with self.assertRaisesRegex(InvalidLoiError, 'not a valid LOI'):
                self.client.upload(loi=loi)

    def test_upload_with_not_existing_resource_raises(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            with self.assertRaisesRegex(LoiNotFoundError, 'LOI does not exist'):
                self.client.upload(loi=self.loi)

    def test_upload_with_existing_resource_content_raises(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            self.client.upload(loi=self.loi)
            with self.assertRaisesRegex(ExistingFileError, 'Directory not '
                                                           'empty'):
                self.client.upload(loi=self.loi)

    def test_download_contains_manifest(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            self.client.upload(loi=self.loi)
        self.path = self.client.download(self.loi)
        self.assertTrue(os.path.isfile(os.path.join(self.path,
                                                    self.manifest_filename)))

    def test_download_with_not_existing_resource_raises(self):
        with self.assertRaisesRegex(LoiNotFoundError, 'does not exist'):
            self.path = self.client.download(self.loi)

    def test_download_with_invalid_loi_raises(self):
        loi = '42.1001/ds/foo/bar/baz'
        with self.assertRaisesRegex(InvalidLoiError, 'not a valid LOI'):
            self.path = self.client.download(loi)

    def test_download_empty_resource_raises(self):
        self.client.create(loi=self.loi)
        with self.assertRaises(MissingContentError):
            self.path = self.client.download(self.loi)

    def test_update_updates_data_at_resource(self):
        storage_dir = os.path.join(self.storage_root, 'exp/sa/42/cwepr/1')
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
        self.client.create(loi=self.loi)
        self.client.upload(loi=self.loi, path=self.tempdir)
        with change_working_dir(storage_dir):
            os.rename(self.manifest_filename, 'foo.yaml')
        self.client.update(loi=self.loi, path=self.tempdir)
        self.assertNotIn('foo.yaml', os.listdir(storage_dir))

    def test_update_returns_results_of_integrity_check(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            self.client.upload(loi=self.loi)
            integrity = self.client.update(loi=self.loi)
        self.assertCountEqual(['all', 'data'], integrity.keys())

    def test_update_with_invalid_loi_raises(self):
        loi = '42.1001/ds/foo/bar/baz'
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            with self.assertRaisesRegex(InvalidLoiError, 'not a valid LOI'):
                self.client.update(loi=loi)

    def test_update_with_not_existing_resource_raises(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            with self.assertRaisesRegex(LoiNotFoundError, 'LOI does not exist'):
                self.client.update(loi=self.loi)

    def test_update_with_not_existing_resource_content_raises(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            with self.assertRaisesRegex(NoFileError, 'Directory empty'):
                self.client.update(loi=self.loi)
