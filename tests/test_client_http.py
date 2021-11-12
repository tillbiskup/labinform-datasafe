import os
import shutil
import unittest

import flask_unittest
import requests

import datasafe.loi as loi_
from datasafe import server
from datasafe import client as datasafe_client
from datasafe.manifest import Manifest
from datasafe.utils import change_working_dir


class TestHTTPClient(unittest.TestCase):
    def setUp(self):
        self.client = datasafe_client.HTTPClient()

    def test_instantiate_class(self):
        pass


def server_is_running():
    try:
        requests.get('http://127.0.0.1:5000')
        return True
    except:  # noqa
        return False


@unittest.skipUnless(server_is_running(), reason='No HTTP server running')
class TestHTTPClientConnection(flask_unittest.LiveTestCase):
    app = server.create_http_server({"TESTING": True})

    def setUp(self):
        self.client = datasafe_client.HTTPClient()
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
        checker = loi_.LoiChecker()
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

    def test_download_contains_manifest(self):
        self.client.create(loi=self.loi)
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            self.client.upload(loi=self.loi)
        self.path = self.client.download(self.loi)
        self.assertTrue(os.path.isfile(os.path.join(self.path,
                                                    self.manifest_filename)))

