import os
import unittest
import shutil

import datasafe.client as client


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = client.Client()
        self.loi = '42.1001/ds/exp/sa/42/cwepr/1'
        self.path = ''

    def tearDown(self):
        if self.path:
            shutil.rmtree(self.path)

    def test_client_has_pull_method(self):
        self.assertTrue(hasattr(self.client, 'pull'))

    def test_pull_without_loi_raises(self):
        with self.assertRaises(client.MissingLoiError):
            self.client.pull()

    def test_pull_with_loi(self):
        self.path = self.client.pull(self.loi)

    def test_pull_with_invalid_loi_raises(self):
        with self.assertRaises(client.InvalidLoiError):
            self.client.pull('foo')

    def test_pull_with_no_datasafe_loi_raises(self):
        with self.assertRaises(client.InvalidLoiError):
            self.client.pull('42.1001/rec/42')

    def test_pull_returns_string(self):
        self.path = self.client.pull(self.loi)
        self.assertTrue(self.path)

    def test_pull_returns_path_to_tmp_folder(self):
        self.path = self.client.pull(self.loi)
        self.assertTrue(os.path.exists(self.path))

    def test_tmp_directory_contains_manifest(self):
        self.path = self.client.pull(self.loi)
        self.assertTrue(os.path.isfile(os.path.join(self.path,
                                                    'MANIFEST.yaml')))


if __name__ == '__main__':
    unittest.main()
