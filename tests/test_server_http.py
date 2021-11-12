import json
import os
import shutil
import unittest

import flask_unittest

import datasafe.server as server
from datasafe.manifest import Manifest
from datasafe.utils import change_working_dir


class TestHTTPServerApp(flask_unittest.AppClientTestCase):

    def create_app(self):
        app = server.create_http_server({"TESTING": True})
        yield app

    def test_app_in_testing_mode(self, app, _):
        self.assertTrue(app.testing)

    def test_heartbeat_responds_with_status_ok(self, _, client):
        self.assertStatus(client.get("/heartbeat"), 200)

    def test_heartbeat_responds_with_alive(self, _, client):
        self.assertResponseEqual(client.get("/heartbeat"), b'alive')


class TestAPI(flask_unittest.ClientTestCase):
    app = server.create_http_server({"TESTING": True})

    def setUp(self, client):
        self.loi = '42.1001/ds/exp/sa/42/cwepr/1'
        self.storage = server.StorageBackend()
        self.tempdir = 'tmp'
        self.manifest_filename = Manifest().manifest_filename
        self.data_filename = 'foo'
        self.metadata_filename = 'bar'

    def tearDown(self, client):
        for directory in [self.storage.root_directory, self.tempdir]:
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
        with open(os.path.join(path, self.metadata_filename), 'w+') as f:
            f.write('')

    def test_api_responds_with_status_ok(self, client):
        self.assertStatus(client.get("/api"), 308)
        self.assertStatus(client.get("/api/"), 200)

    def test_post_with_invalid_loi_returns_404(self, client):
        response = client.post("/api/" + 'foo/bar/baz')
        self.assertStatus(response, 404)

    def test_post_with_valid_loi_returns_new_loi(self, client):
        response = client.post("/api/" + self.loi)
        self.assertStatus(response, 201)
        self.assertResponseEqual(response, self.loi.encode())

    def test_post_with_valid_loi_creates_directory_via_backend(self, client):
        loi = '42.1001/ds/exp/sa/42/cwepr/'
        self.assertStatus(client.post("/api/" + self.loi), 201)
        self.assertTrue(os.path.exists(os.path.join(
            self.storage.root_directory, 'exp/sa/42/cwepr/1')))

    def test_post_with_valid_loi_returns_returns_new_loi(self, client):
        loi = '42.1001/ds/exp/sa/42/cwepr/'
        response = client.post("/api/" + self.loi)
        self.assertResponseEqual(response, f"{loi}1".encode())

    def test_put_with_valid_loi_deposits_data(self, client):
        client.post("/api/" + self.loi)
        client.put("/api/" + self.loi, data=self.create_zip_archive())
        storage_dir = os.path.join(self.storage.root_directory,
                                   *self.loi.split('/')[2:])
        self.assertTrue(os.listdir(storage_dir))

    def test_put_with_valid_loi_returns_integrity(self, client):
        client.post("/api/" + self.loi)
        integrity = client.put("/api/" + self.loi,
                               data=self.create_zip_archive())
        self.assertDictEqual({'all': True, 'data': True},
                             json.loads(integrity.data))

    def test_put_with_invalid_loi_returns_404(self, client):
        response = client.put("/api/" + "foo/bar/baz")
        self.assertStatus(response, 404)

    def test_put_with_valid_loi_and_inexisting_directory(self, client):
        response = client.put("/api/" + self.loi,
                              data=self.create_zip_archive())
        self.assertStatus(response, 400)
        self.assertResponseEqual(response, 'LOI does not exist.'.encode())

    def test_put_with_valid_loi_and_no_payload(self, client):
        client.post("/api/" + self.loi)
        response = client.put("/api/" + self.loi)
        self.assertStatus(response, 400)
        self.assertResponseEqual(response,
                                 'No content provided to deposit.'.encode())

    def test_put_with_already_existing_content_at_loi(self, client):
        data = self.create_zip_archive()
        client.post("/api/" + self.loi)
        client.put("/api/" + self.loi, data=data)
        response = client.put("/api/" + self.loi, data=data)
        self.assertStatus(response, 405)
        self.assertResponseEqual(response,
                                 'Directory not empty'.encode())
        self.assertIn('UPDATE', response.allow)

    def test_get_non_existing_loi_returns_404(self, client):
        self.assertStatus(client.get("/api/" + self.loi), 404)

    def test_get_invalid_loi_returns_404(self, client):
        self.assertStatus(client.get("/api/" + "foo/bar/baz"), 404)

    def test_get_returns_dataset_zip(self, client):
        data = self.create_zip_archive()
        client.post("/api/" + self.loi)
        client.put("/api/" + self.loi, data=data)
        response = client.get("/api/" + self.loi)
        self.assertResponseEqual(response, data)

    def test_get_empty_loi(self, client):
        client.post("/api/" + self.loi)
        response = client.get("/api/" + self.loi)
        self.assertStatus(response, 204)
