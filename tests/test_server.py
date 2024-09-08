import os
import shutil
import unittest
from unittest import mock

import datasafe.loi as loi_
import datasafe.server as server
from datasafe.exceptions import (
    ExistingFileError,
    LoiNotFoundError,
    MissingContentError,
    NoFileError,
    MissingLoiError,
    InvalidLoiError,
    MissingPathError,
)
from datasafe.manifest import Manifest
from datasafe.utils import change_working_dir


class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = server.Server()
        self.loi = "42.1001/ds/exp/sa/42/cwepr/1"
        self.storage = server.StorageBackend()
        self.tempdir = "tmp"
        self.manifest_filename = Manifest().manifest_filename
        self.data_filename = "foo"
        self.metadata_filename = "bar"

    def tearDown(self):
        for directory in [self.storage.root_directory, self.tempdir]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
        for filename in [
            self.data_filename,
            self.metadata_filename,
            self.manifest_filename,
        ]:
            if os.path.exists(filename):
                os.remove(filename)

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

    def create_data_and_metadata_files(self, path=""):
        with open(os.path.join(path, self.data_filename), "w+") as f:
            f.write("")
        with open(os.path.join(path, self.metadata_filename), "w+") as f:
            f.write("")

    def test_instantiate_class(self):
        pass

    def test_server_has_new_method(self):
        self.assertTrue(hasattr(self.server, "new"))
        self.assertTrue(callable(self.server.new))

    def test_server_has_upload_method(self):
        self.assertTrue(hasattr(self.server, "upload"))
        self.assertTrue(callable(self.server.upload))

    def test_server_has_download_method(self):
        self.assertTrue(hasattr(self.server, "download"))
        self.assertTrue(callable(self.server.download))

    def test_server_has_update_method(self):
        self.assertTrue(hasattr(self.server, "update"))
        self.assertTrue(callable(self.server.update))

    def test_new_without_loi_raises(self):
        with self.assertRaises(MissingLoiError):
            self.server.new()

    def test_new_with_invalid_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.server.new("foo")

    def test_new_with_no_datasafe_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.server.new("42.1001/rec/42")

    def test_new_with_non_exp_loi_raises(self):
        message = "not a valid experiment LOI"
        with self.assertRaisesRegex(InvalidLoiError, message):
            self.server.new("42.1001/ds/calc")

    def test_new_with_invalid_exp_loi_raises(self):
        message = "not a valid LOI"
        with self.assertRaisesRegex(InvalidLoiError, message):
            self.server.new("42.1001/ds/exp/foo")

    def test_new_with_loi_returns_string(self):
        self.assertIsInstance(self.server.new(self.loi), str)

    def test_new_with_loi_returns_valid_loi(self):
        checker = loi_.LoiChecker()
        self.assertTrue(checker.check(self.server.new(self.loi)))

    def test_new_creates_directory_via_backend(self):
        loi = "42.1001/ds/exp/sa/42/cwepr/"
        self.server.new(loi)
        self.assertTrue(
            os.path.exists(
                os.path.join(self.storage.root_directory, "exp/sa/42/cwepr/1")
            )
        )

    def test_new_returns_loi_of_newly_created_directory(self):
        loi = "42.1001/ds/exp/sa/42/cwepr/"
        self.assertEqual(loi + "1", self.server.new(loi))

    def test_new_consecutively_creates_directory_via_backend(self):
        loi = "42.1001/ds/exp/sa/42/cwepr/"
        self.server.new(loi)
        self.server.new(loi)
        self.assertTrue(
            os.path.exists(
                os.path.join(self.storage.root_directory, "exp/sa/42/cwepr/2")
            )
        )

    def test_upload_without_loi_raises(self):
        with self.assertRaises(MissingLoiError):
            self.server.upload()

    def test_upload_with_invalid_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.server.upload("foo")

    def test_upload_with_no_datasafe_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.server.upload("42.1001/rec/42")

    def test_upload_with_inexisting_loi_raises(self):
        with self.assertRaisesRegex(LoiNotFoundError, "LOI does not exist."):
            self.server.upload("42.1001/ds/exp/sa/42/cwepr/1")

    def test_upload_with_existing_loi(self):
        self.server.new(self.loi)
        self.server.upload(loi=self.loi, content=self.create_zip_archive())
        storage_dir = os.path.join(
            self.storage.root_directory, *self.loi.split("/")[2:]
        )
        self.assertTrue(os.listdir(storage_dir))

    def test_upload_with_existing_files_raises(self):
        self.server.new(self.loi)
        content = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=content)
        with self.assertRaises(ExistingFileError):
            self.server.upload(loi=self.loi, content=content)

    def test_upload_returns_results_of_integrity_check(self):
        self.server.new(self.loi)
        integrity = self.server.upload(
            loi=self.loi, content=self.create_zip_archive()
        )
        self.assertCountEqual(["all", "data"], integrity.keys())

    def test_download_without_loi_raises(self):
        with self.assertRaises(MissingLoiError):
            self.server.download()

    def test_download_with_invalid_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.server.download("foo")

    def test_download_with_no_datasafe_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.server.download("42.1001/rec/42")

    def test_download_with_inexisting_loi_raises(self):
        with self.assertRaisesRegex(LoiNotFoundError, "LOI does not exist."):
            self.server.download("42.1001/ds/exp/sa/42/cwepr/1")

    def test_download_with_loi_with_empty_directory_raises(self):
        self.server.new(self.loi)
        with self.assertRaisesRegex(
            MissingContentError, "LOI does not have content."
        ):
            self.server.download(self.loi)

    def test_download_with_loi(self):
        self.server.new(self.loi)
        content = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=content)
        self.assertEqual(content, self.server.download(self.loi))

    def test_update_without_loi_raises(self):
        with self.assertRaises(MissingLoiError):
            self.server.update()

    def test_update_with_invalid_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.server.update("foo")

    def test_update_with_no_datasafe_loi_raises(self):
        with self.assertRaises(InvalidLoiError):
            self.server.update("42.1001/rec/42")

    def test_update_with_inexisting_loi_raises(self):
        with self.assertRaisesRegex(LoiNotFoundError, "LOI does not exist."):
            self.server.update("42.1001/ds/exp/sa/42/cwepr/1")

    def test_update_with_existing_loi(self):
        storage_dir = os.path.join(
            self.storage.root_directory, *self.loi.split("/")[2:]
        )
        data = self.create_zip_archive()
        self.server.new(self.loi)
        self.server.upload(loi=self.loi, content=data)
        with change_working_dir(storage_dir):
            os.rename(self.manifest_filename, "foo.yaml")
        self.server.update(loi=self.loi, content=data)
        self.assertNotIn("foo.yaml", os.listdir(storage_dir))

    def test_update_with_empty_resource_raises(self):
        self.server.new(self.loi)
        data = self.create_zip_archive()
        with self.assertRaises(NoFileError):
            self.server.update(loi=self.loi, content=data)

    def test_update_without_data_raises(self):
        self.server.new(self.loi)
        data = self.create_zip_archive()
        self.server.upload(loi=self.loi, content=data)
        with self.assertRaises(MissingContentError):
            self.server.update(loi=self.loi)

    def test_update_returns_results_of_integrity_check(self):
        data = self.create_zip_archive()
        self.server.new(self.loi)
        self.server.upload(loi=self.loi, content=data)
        integrity = self.server.update(loi=self.loi, content=data)
        self.assertCountEqual(["all", "data"], integrity.keys())


class TestStorageBackend(unittest.TestCase):

    def setUp(self):
        self.backend = server.StorageBackend()
        self.backend.root_directory = ""
        self.path = "path"
        self.subdir = "bla"
        self.root = "root"
        self.tempdir = "tmp"
        self.checksum_filename = "CHECKSUM"
        self.checksum_data_filename = "CHECKSUM.data"
        self.manifest_filename = Manifest().manifest_filename
        self.data_filename = "foo"
        self.metadata_filename = "bar"

    def tearDown(self):
        for directory in [self.path, self.root, self.tempdir, self.subdir]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
        for filename in [
            self.data_filename,
            self.metadata_filename,
            self.manifest_filename,
        ]:
            if os.path.exists(filename):
                os.remove(filename)

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

    def create_manifest_file(self, path=""):
        manifest = Manifest()
        manifest.data_filenames = [os.path.join(path, self.data_filename)]
        manifest.metadata_filenames = [
            os.path.join(path, self.metadata_filename)
        ]
        manifest.manifest_filename = os.path.join(
            path, self.manifest_filename
        )
        manifest.to_file()

    def create_data_and_metadata_files(self, path=""):
        with open(os.path.join(path, self.data_filename), "w+") as f:
            f.write("")
        with open(os.path.join(path, self.metadata_filename), "w+") as f:
            f.write("")

    def test_instantiate_class(self):
        pass

    def test_has_root_directory_property(self):
        self.assertTrue(hasattr(self.backend, "root_directory"))

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.backend, "create"))
        self.assertTrue(callable(self.backend.create))

    def test_create_without_path_raises(self):
        with self.assertRaises(MissingPathError):
            self.backend.create()

    def test_create_creates_directory(self):
        self.backend.create(self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_create_creates_directory_below_root_directory(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        self.assertTrue(os.path.exists(os.path.join(self.root, self.path)))

    def test_create_for_existing_directory_raises(self):
        self.backend.create(self.path)
        with self.assertRaises(FileExistsError):
            self.backend.create(self.path)

    def test_exists_with_existing_directory_returns_true(self):
        self.backend.create(self.path)
        self.assertTrue(self.backend.exists(self.path))

    def test_exists_with_non_existing_directory_returns_false(self):
        self.assertFalse(self.backend.exists(self.path))

    def test_exists_with_directory_below_root_directory_returns_true(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        self.assertTrue(self.backend.exists(self.path))

    def test_isempty_with_empty_directory_returns_true(self):
        self.backend.create(self.path)
        self.assertTrue(self.backend.isempty(self.path))

    def test_isempty_with_non_existing_directory_raises(self):
        with self.assertRaises(NoFileError):
            self.assertTrue(self.backend.isempty(self.path))

    def test_isempty_with_not_empty_directory_returns_false(self):
        self.backend.create(self.path)
        with open(os.path.join(self.path, "test"), "w+") as f:
            f.write("")
        self.assertFalse(self.backend.isempty(self.path))

    def test_isempty_with_empty_directory_below_root_returns_true(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        self.assertTrue(self.backend.isempty(self.path))

    def test_remove_removes_empty_directory(self):
        self.backend.create(self.path)
        self.backend.remove(self.path)
        self.assertFalse(os.path.exists(self.path))

    def test_remove_removes_empty_directory_below_root(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        self.backend.remove(self.path)
        self.assertFalse(os.path.exists(os.path.join(self.root, self.path)))

    def test_remove_removes_empty_directory_below_root_leaves_root(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        self.backend.remove(self.path)
        self.assertFalse(os.path.exists(os.path.join(self.root, self.path)))

    def test_remove_non_existing_directory_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.backend.remove(self.path)

    def test_remove_non_empty_directory_without_force_raises(self):
        self.backend.create(self.path)
        with open(os.path.join(self.path, "test"), "w+") as f:
            f.write("")
        with self.assertRaises(OSError):
            self.backend.remove(self.path)

    def test_remove_non_empty_directory_with_force_removes_directory(self):
        self.backend.create(self.path)
        with open(os.path.join(self.path, "test"), "w+") as f:
            f.write("")
        self.backend.remove(self.path, force=True)
        self.assertFalse(os.path.exists(self.path))

    def test_get_highest_id_in_empty_directory_returns_zero(self):
        self.backend.create(self.path)
        self.assertEqual(0, self.backend.get_highest_id(self.path))

    def test_get_highest_id_in_directory(self):
        self.backend.create(self.path)
        subpath = os.path.join(self.path, "1")
        self.backend.create(subpath)
        self.assertEqual(1, self.backend.get_highest_id(self.path))

    def test_get_highest_id_in_directory_below_root(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        subpath = os.path.join(self.path, "5")
        self.backend.create(subpath)
        self.assertEqual(5, self.backend.get_highest_id(self.path))

    def test_create_next_id_in_empty_directory_creates_directory_one(self):
        self.backend.create(self.path)
        self.backend.create_next_id(self.path)
        self.assertTrue(os.path.exists(os.path.join(self.path, "1")))

    def test_create_next_id_returns_new_directory(self):
        self.backend.create(self.path)
        self.assertEqual(
            os.path.join(self.path, "1"),
            self.backend.create_next_id(self.path),
        )

    def test_create_next_id_in_directory(self):
        self.backend.create(self.path)
        subpath = os.path.join(self.path, "5")
        self.backend.create(subpath)
        self.backend.create_next_id(self.path)
        self.assertTrue(os.path.exists(os.path.join(self.path, "6")))

    def test_create_next_id_in_directory_below_root(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        self.backend.create_next_id(self.path)
        self.assertTrue(
            os.path.exists(os.path.join(self.root, self.path, "1"))
        )

    def test_deposit_without_path_raises(self):
        with self.assertRaises(MissingPathError):
            self.backend.deposit(content=self.create_zip_archive())

    def test_deposit_without_content_raises(self):
        with self.assertRaises(MissingContentError):
            self.backend.deposit(path=self.path)

    def test_deposit_writes_files(self):
        self.backend.create(self.path)
        self.backend.deposit(
            path=self.path, content=self.create_zip_archive()
        )
        self.assertTrue(
            os.path.exists(
                os.path.join(self.path, Manifest().manifest_filename)
            )
        )

    def test_deposit_with_root_writes_files(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        self.backend.deposit(
            path=self.path, content=self.create_zip_archive()
        )
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    self.root, self.path, Manifest().manifest_filename
                )
            )
        )

    def test_deposit_checks_for_consistency_of_checksums(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        mock_ = mock.MagicMock()
        with mock.patch("datasafe.server.Manifest.check_integrity", mock_):
            self.backend.deposit(
                path=self.path, content=self.create_zip_archive()
            )
        mock_.assert_called()

    def test_deposit_returns_results_of_integrity_check(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        integrity = self.backend.deposit(
            path=self.path, content=self.create_zip_archive()
        )
        self.assertCountEqual(["all", "data"], integrity.keys())

    def test_retrieve_without_path_raises(self):
        self.backend.create(self.path)
        with self.assertRaises(MissingPathError):
            self.backend.retrieve()

    def test_retrieve_with_non_existing_path_raises(self):
        with self.assertRaises(OSError):
            self.backend.retrieve(path=self.path)

    def test_retrieve_returns_zipped_contents_as_bytearray(self):
        self.backend.create(self.path)
        content = self.create_zip_archive()
        self.backend.deposit(path=self.path, content=content)
        self.assertEqual(content, self.backend.retrieve(self.path))

    def test_retrieve_with_root_returns_zipped_contents_as_bytearray(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        content = self.create_zip_archive()
        self.backend.deposit(path=self.path, content=content)
        self.assertEqual(content, self.backend.retrieve(self.path))

    def test_get_manifest_without_path_raises(self):
        self.backend.create(self.path)
        with self.assertRaises(MissingPathError):
            self.backend.get_manifest()

    def test_get_manifest_with_non_existing_path_raises(self):
        with self.assertRaises(MissingPathError):
            self.backend.get_manifest(path=self.path)

    def test_get_manifest_with_non_existing_manifest_raises(self):
        self.backend.create(self.path)
        with self.assertRaises(MissingContentError):
            self.backend.get_manifest(path=self.path)

    def test_get_manifest_returns_contents_as_string(self):
        self.backend.create(self.path)
        manifest_contents = "foo"
        with open(os.path.join(self.path, self.manifest_filename), "w+") as f:
            f.write(manifest_contents)
        self.assertEqual(
            manifest_contents, self.backend.get_manifest(self.path)
        )

    def test_get_index_returns_list_of_paths(self):
        self.backend.create(self.path)
        self.assertEqual(self.path, self.backend.get_index()[0])

    def test_get_index_with_root_returns_list_of_paths(self):
        self.backend.root_directory = self.root
        paths = ["foo", "bar", "foobar"]
        for path in paths:
            self.backend.create(path)
        self.assertCountEqual(paths, self.backend.get_index())

    def test_get_index_with_subfolders_works(self):
        path = os.path.join(self.subdir, self.path)
        self.backend.create(path)
        self.assertEqual(path, self.backend.get_index()[0])
        self.backend.remove(path)

    def test_get_index_with_manifest_file_works(self):
        self.backend.create(self.path)
        self.create_data_and_metadata_files(path=self.path)
        self.create_manifest_file(path=self.path)
        self.assertEqual(self.path, self.backend.get_index()[0])

    def test_check_integrity_without_manifest_file_raises(self):
        self.backend.create(self.path)
        with self.assertRaises(MissingContentError):
            self.backend.check_integrity(self.path)

    def test_check_integrity_returns_dict(self):
        self.backend.create(self.path)
        self.create_data_and_metadata_files(path=self.path)
        self.create_manifest_file(path=self.path)
        self.assertIsInstance(self.backend.check_integrity(self.path), dict)

    def test_check_integrity_dict_contains_correct_fields(self):
        self.backend.create(self.path)
        self.create_data_and_metadata_files(path=self.path)
        self.create_manifest_file(path=self.path)
        self.assertCountEqual(
            ["data", "all"], self.backend.check_integrity(self.path).keys()
        )

    def test_check_integrity_returns_correct_answer_for_data(self):
        self.backend.create(self.path)
        self.create_data_and_metadata_files(path=self.path)
        self.create_manifest_file(path=self.path)
        integrity = self.backend.check_integrity(path=self.path)
        self.assertTrue(integrity["data"])
        self.assertTrue(integrity["all"])

    def test_check_integrity_w_wrong_checksum_in_manifest_returns_false(self):
        self.backend.create(self.path)
        self.create_data_and_metadata_files(path=self.path)
        self.create_manifest_file(path=self.path)
        # Create manifest containing fantasy checksum(s)
        import oyaml as yaml

        with open(
            os.path.join(self.path, self.manifest_filename), "r"
        ) as file:
            manifest_dict = yaml.safe_load(file)
        manifest_dict["checksums"][0]["value"] = "foo"
        manifest_dict["checksums"][1]["value"] = "bar"
        with open(os.path.join(self.path, self.manifest_filename), "w+") as f:
            yaml.dump(manifest_dict, f)
        # Check that integrity for both fields is False
        integrity = self.backend.check_integrity(path=self.path)
        self.assertFalse(integrity["data"])
        self.assertFalse(integrity["all"])
