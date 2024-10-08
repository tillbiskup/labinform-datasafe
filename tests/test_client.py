import os
import shutil
import unittest
from unittest import mock

from datasafe import client, configuration
import datasafe.loi as loi_
from datasafe.exceptions import MissingLoiError, InvalidLoiError
from datasafe.manifest import Manifest
from datasafe.server import Server
from datasafe.utils import change_working_dir


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = client.Client()
        self.server = Server()
        self.loi = "42.1001/ds/exp/sa/42/cwepr/1"
        self.config = configuration.StorageBackend()
        self.storage_root = self.config.root_directory
        self.path = ""
        self.tempdir = "tmp"
        self.data_filename = "bar.dat"
        self.metadata_filename = "bar.info"
        self.manifest_filename = Manifest().manifest_filename

    def tearDown(self):
        for directory in [self.path, self.storage_root, self.tempdir]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
        for file in [
            self.data_filename,
            self.metadata_filename,
            self.manifest_filename,
        ]:
            if os.path.exists(file):
                os.remove(file)

    def create_data_and_metadata_files(self):
        with open(self.data_filename, "w+") as f:
            f.write("")
        with open(self.metadata_filename, "w+") as f:
            f.write("cwEPR Info file - v. 0.1.4 (2020-01-21)")

    def create_manifest_file(self):
        manifest = Manifest()
        manifest.data_filenames = [self.data_filename]
        manifest.metadata_filenames = [self.metadata_filename]
        manifest.to_file()

    def create_zip_archive(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.create_manifest_file()
        zip_archive = shutil.make_archive(
            base_name="test", format="zip", root_dir=self.tempdir
        )
        with open(zip_archive, "rb") as zip_file:
            contents = zip_file.read()
        os.remove("test.zip")
        return contents

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.client, "create"))
        self.assertTrue(callable(self.client.create))

    def test_has_upload_method(self):
        self.assertTrue(hasattr(self.client, "upload"))
        self.assertTrue(callable(self.client.upload))

    def test_has_download_method(self):
        self.assertTrue(hasattr(self.client, "download"))
        self.assertTrue(callable(self.client.download))

    def test_has_update_manifest_method(self):
        self.assertTrue(hasattr(self.client, "update"))
        self.assertTrue(callable(self.client.update))

    def test_has_create_manifest_method(self):
        self.assertTrue(hasattr(self.client, "create_manifest"))
        self.assertTrue(callable(self.client.create_manifest))

    def test_create_without_loi_raises(self):
        with self.assertRaises(MissingLoiError):
            self.client.create()

    def test_create_with_invalid_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.client.create("foo")

    def test_create_with_no_datasafe_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.client.create("42.1001/rec/42")

    def test_create_with_non_exp_loi_raises(self):
        message = "not a valid experiment LOI"
        with self.assertRaisesRegex(InvalidLoiError, message):
            self.client.create("42.1001/ds/calc")

    def test_create_with_invalid_exp_loi_raises(self):
        message = "not a valid LOI"
        with self.assertRaisesRegex(InvalidLoiError, message):
            self.client.create("42.1001/ds/exp/foo")

    def test_create_with_loi_returns_string(self):
        self.assertIsInstance(self.client.create(self.loi), str)

    def test_download_without_loi_raises(self):
        with self.assertRaises(MissingLoiError):
            self.client.download()

    def test_download_with_invalid_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.client.download("foo")

    def test_download_with_no_datasafe_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.client.download("42.1001/rec/42")

    def test_download_returns_string(self):
        self.server.new(loi=self.loi)
        data = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=data)
        mock_ = mock.MagicMock()
        mock_.return_value = data
        with mock.patch("datasafe.client.Client._server_download", mock_):
            self.path = self.client.download(self.loi)
        self.assertTrue(self.path)

    def test_download_returns_path_to_tmp_folder(self):
        self.server.new(loi=self.loi)
        data = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=data)
        mock_ = mock.MagicMock()
        mock_.return_value = data
        with mock.patch("datasafe.client.Client._server_download", mock_):
            self.path = self.client.download(self.loi)
        self.assertTrue(os.path.exists(self.path))

    def test_tmp_directory_contains_manifest(self):
        self.server.new(loi=self.loi)
        data = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=data)
        download = mock.MagicMock()
        download.return_value = data
        with mock.patch("datasafe.client.Client._server_download", download):
            self.path = self.client.download(self.loi)
        self.assertTrue(
            os.path.isfile(os.path.join(self.path, self.manifest_filename))
        )

    def test_download_checks_for_consistency_of_checksums(self):
        self.server.new(loi=self.loi)
        data = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=data)
        check = mock.MagicMock()
        download = mock.MagicMock()
        download.return_value = data
        with mock.patch("datasafe.client.Client._server_download", download):
            with mock.patch(
                "datasafe.client.Manifest.check_integrity", check
            ):
                self.path = self.client.download(self.loi)
        check.assert_called()

    def test_download_warns_if_only_overall_checksum_is_false(self):
        self.server.new(loi=self.loi)
        data = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=data)
        check = mock.MagicMock()
        check.return_value = {"all": False, "data": True}
        download = mock.MagicMock()
        download.return_value = data
        with mock.patch("datasafe.client.Client._server_download", download):
            with mock.patch(
                "datasafe.client.Manifest.check_integrity", check
            ):
                message = "Integrity check failed, metadata may be corrupted."
                with self.assertWarnsRegex(UserWarning, message):
                    self.path = self.client.download(self.loi)

    def test_download_warns_if_only_data_checksum_is_false(self):
        self.server.new(loi=self.loi)
        data = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=data)
        check = mock.MagicMock()
        check.return_value = {"all": True, "data": False}
        download = mock.MagicMock()
        download.return_value = data
        with mock.patch("datasafe.client.Client._server_download", download):
            with mock.patch(
                "datasafe.client.Manifest.check_integrity", check
            ):
                message = "Integrity check failed, data may be corrupted."
                with self.assertWarnsRegex(UserWarning, message):
                    self.path = self.client.download(self.loi)

    def test_download_warns_if_both_checksums_are_false(self):
        self.server.new(loi=self.loi)
        data = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=data)
        check = mock.MagicMock()
        check.return_value = {"all": False, "data": False}
        download = mock.MagicMock()
        download.return_value = data
        with mock.patch("datasafe.client.Client._server_download", download):
            with mock.patch(
                "datasafe.client.Manifest.check_integrity", check
            ):
                message = (
                    "Integrity check failed, data and metadata may be "
                    "corrupted."
                )
                with self.assertWarnsRegex(UserWarning, message):
                    self.path = self.client.download(self.loi)

    def test_create_manifest_creates_manifest(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create_manifest()
            self.assertTrue(os.path.isfile(self.manifest_filename))

    def test_create_manifest_autodetects_infofile_as_metadata(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create_manifest()
            manifest = Manifest()
            manifest.from_file()
            self.assertEqual(
                [self.metadata_filename], manifest.metadata_filenames
            )

    def test_create_manifest_sets_data_files_as_sum_of_non_metadata_files(
        self,
    ):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create_manifest()
            manifest = Manifest()
            manifest.from_file()
            self.assertEqual([self.data_filename], manifest.data_filenames)

    def test_create_manifest_excludes_manifest_file_from_metadata(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.create_manifest_file()
            self.client.create_manifest()
            manifest = Manifest()
            manifest.from_file()
            self.assertEqual(
                [self.metadata_filename], manifest.metadata_filenames
            )

    def test_create_manifest_with_given_filename(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            for filename in ["asdf", "sdfg"]:
                with open(filename, "w+") as f:
                    f.write("")
            self.client.create_manifest(filename="bar")
            manifest = Manifest()
            manifest.from_file()
            self.assertEqual([self.data_filename], manifest.data_filenames)

    def test_create_manifest_with_given_path(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
        self.client.create_manifest(path=self.tempdir)
        manifest = Manifest()
        manifest.from_file(
            os.path.join(self.tempdir, manifest.manifest_filename)
        )
        self.assertEqual([self.data_filename], manifest.data_filenames)

    def test_upload_without_loi_raises(self):
        with self.assertRaises(MissingLoiError):
            self.client.upload()

    def test_upload_with_invalid_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.client.upload(loi="foo")

    def test_upload_with_no_datasafe_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.client.upload(loi="42.1001/rec/42")

    def test_upload_creates_manifest(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.server.new(loi=self.loi)
            self.client.upload(loi=self.loi)
            self.assertTrue(os.path.isfile(self.manifest_filename))

    def test_upload_creates_manifest_only_if_it_does_not_exist(self):
        self.client.create(loi=self.loi)
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.create_manifest_file()
            self.client.create_manifest = mock.MagicMock()
            self.server.new(loi=self.loi)
            self.client.upload(loi=self.loi)
            self.client.create_manifest.assert_not_called()

    def test_upload_sets_loi_in_manifest(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.server.new(loi=self.loi)
            self.client.upload(loi=self.loi)
            manifest = Manifest()
            manifest.from_file(self.manifest_filename)
            self.assertTrue(manifest.loi)

    def test_upload_with_given_filename(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            for filename in ["asdf", "sdfg"]:
                with open(filename, "w+") as f:
                    f.write("")
            self.server.new(loi=self.loi)
            self.client.upload(loi=self.loi, filename="bar")
            manifest = Manifest()
            manifest.from_file()
            self.assertEqual([self.data_filename], manifest.data_filenames)

    def test_update_without_loi_raises(self):
        with self.assertRaises(MissingLoiError):
            self.client.update()

    def test_update_with_invalid_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.client.update(loi="foo")

    def test_update_with_no_datasafe_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.client.update(loi="42.1001/rec/42")

    def test_update_creates_manifest(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.server.new(loi=self.loi)
            self.client.update(loi=self.loi)
            self.assertTrue(os.path.isfile(self.manifest_filename))

    def test_update_creates_manifest_only_if_it_does_not_exist(self):
        self.client.create(loi=self.loi)
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.create_manifest_file()
            self.client.create_manifest = mock.MagicMock()
            self.server.new(loi=self.loi)
            self.client.update(loi=self.loi)
            self.client.create_manifest.assert_not_called()

    def test_update_sets_loi_in_manifest(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.server.new(loi=self.loi)
            self.client.update(loi=self.loi)
            manifest = Manifest()
            manifest.from_file(self.manifest_filename)
            self.assertTrue(manifest.loi)

    def test_update_with_given_filename(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            for filename in ["asdf", "sdfg"]:
                with open(filename, "w+") as f:
                    f.write("")
            self.server.new(loi=self.loi)
            self.client.update(loi=self.loi, filename="bar")
            manifest = Manifest()
            manifest.from_file()
            self.assertEqual([self.data_filename], manifest.data_filenames)


class TestLocalClient(unittest.TestCase):
    def setUp(self):
        self.client = client.LocalClient()
        self.loi = "42.1001/ds/exp/sa/42/cwepr/1"
        self.server = Server()
        self.config = configuration.StorageBackend()
        self.storage_root = self.config.root_directory
        self.tempdir = "tmp"
        self.manifest_filename = Manifest().manifest_filename
        self.data_filename = "bar.dat"
        self.metadata_filename = "bar.info"

    def tearDown(self):
        for directory in [self.storage_root, self.tempdir]:
            if os.path.exists(directory):
                shutil.rmtree(directory)

    def create_zip_archive(self):
        os.makedirs(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.create_manifest_file()
        zip_archive = shutil.make_archive(
            base_name="test", format="zip", root_dir=self.tempdir
        )
        with open(zip_archive, "rb") as zip_file:
            contents = zip_file.read()
        os.remove("test.zip")
        return contents

    def create_manifest_file(self):
        manifest = Manifest()
        manifest.data_filenames = [self.data_filename]
        manifest.metadata_filenames = [self.metadata_filename]
        manifest.to_file()

    def create_data_and_metadata_files(self):
        with open(self.data_filename, "w+") as f:
            f.write("")
        with open(self.metadata_filename, "w+") as f:
            f.write("cwEPR Info file - v. 0.1.4 (2020-01-21)")

    def test_instantiate_class(self):
        pass

    def test_create_with_loi_returns_valid_loi(self):
        checker = loi_.LoiChecker()
        self.assertTrue(checker.check(self.client.create(self.loi)))

    def test_create_creates_directory_via_backend(self):
        loi = "42.1001/ds/exp/sa/42/cwepr/"
        self.client.create(loi)
        self.assertTrue(
            os.path.exists(
                os.path.join(self.storage_root, "exp/sa/42/cwepr/1")
            )
        )

    def test_upload_with_given_path(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
        self.client.create(loi=self.loi)
        self.client.upload(loi=self.loi, path=self.tempdir)
        manifest = Manifest()
        manifest.from_file(
            os.path.join(self.tempdir, manifest.manifest_filename)
        )
        self.assertEqual([self.data_filename], manifest.data_filenames)

    def test_upload_creates_downloadable_items_in_datasafe(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            self.client.upload(loi=self.loi)
            self.path = self.client.download(self.loi)
        self.assertTrue(
            os.path.isfile(os.path.join(self.path, self.manifest_filename))
        )

    def test_upload_returns_results_of_integrity_check(self):
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
            self.client.create(loi=self.loi)
            integrity = self.client.upload(loi=self.loi)
        self.assertCountEqual(["all", "data"], integrity.keys())

    def test_download_contains_manifest(self):
        self.server.new(loi=self.loi)
        data = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=data)
        self.path = self.client.download(self.loi)
        self.assertTrue(
            os.path.isfile(os.path.join(self.path, self.manifest_filename))
        )

    def test_update_updates_data_at_resource(self):
        storage_dir = os.path.join(self.storage_root, "exp/sa/42/cwepr/1")
        os.mkdir(self.tempdir)
        with change_working_dir(self.tempdir):
            self.create_data_and_metadata_files()
        self.client.create(loi=self.loi)
        self.client.upload(loi=self.loi, path=self.tempdir)
        with change_working_dir(storage_dir):
            os.rename(self.manifest_filename, "foo.yaml")
        self.client.update(loi=self.loi, path=self.tempdir)
        self.assertNotIn("foo.yaml", os.listdir(storage_dir))
