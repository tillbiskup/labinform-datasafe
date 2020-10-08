import os
import shutil
import unittest

from datasafe import directory


class TestStorageBackend(unittest.TestCase):

    def setUp(self):
        self.backend = directory.StorageBackend()
        self.path = 'path'
        self.subdir = 'bla'
        self.root = 'root'
        self.tempdir = 'tmp'
        self.manifest_filename = 'MANIFEST.yaml'
        self.checksum_filename = 'CHECKSUM'
        self.checksum_data_filename = 'CHECKSUM.data'

    def tearDown(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
        if os.path.exists(self.root):
            shutil.rmtree(self.root)
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)
        if os.path.exists(self.subdir):
            shutil.rmtree(self.subdir)

    def create_tmp_file(self):
        os.makedirs(self.tempdir)
        with open(os.path.join(self.tempdir, 'test.txt'), 'w+') as f:
            f.write('Test')

    def create_zip_archive(self):
        self.create_tmp_file()
        zip_archive = shutil.make_archive(base_name='test', format='zip',
                                          root_dir=self.tempdir)
        with open(zip_archive, 'rb') as zip_file:
            contents = zip_file.read()
        os.remove('test.zip')
        return contents

    def test_instantiate_class(self):
        pass

    def test_has_root_directory_property(self):
        self.assertTrue(hasattr(self.backend, 'root_directory'))

    def test_has_create_method(self):
        self.assertTrue(hasattr(self.backend, 'create'))
        self.assertTrue(callable(self.backend.create))

    def test_create_without_path_raises(self):
        with self.assertRaises(directory.MissingPathError):
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
        with self.assertRaises(FileNotFoundError):
            self.assertTrue(self.backend.isempty(self.path))

    def test_isempty_with_not_empty_directory_returns_false(self):
        self.backend.create(self.path)
        with open(os.path.join(self.path, 'test'), 'w+') as f:
            f.write('')
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
        with open(os.path.join(self.path, 'test'), 'w+') as f:
            f.write('')
        with self.assertRaises(OSError):
            self.backend.remove(self.path)

    def test_remove_non_empty_directory_with_force_removes_directory(self):
        self.backend.create(self.path)
        with open(os.path.join(self.path, 'test'), 'w+') as f:
            f.write('')
        self.backend.remove(self.path, force=True)
        self.assertFalse(os.path.exists(self.path))

    def test_get_highest_id_in_empty_directory_returns_zero(self):
        self.backend.create(self.path)
        self.assertEqual(0, self.backend.get_highest_id(self.path))

    def test_get_highest_id_in_directory(self):
        self.backend.create(self.path)
        subpath = os.path.join(self.path, '1')
        self.backend.create(subpath)
        self.assertEqual(1, self.backend.get_highest_id(self.path))

    def test_get_highest_id_in_directory_below_root(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        subpath = os.path.join(self.path, '5')
        self.backend.create(subpath)
        self.assertEqual(5, self.backend.get_highest_id(self.path))

    def test_create_next_id_in_empty_directory_creates_directory_one(self):
        self.backend.create(self.path)
        self.backend.create_next_id(self.path)
        self.assertTrue(os.path.exists(os.path.join(self.path, '1')))

    def test_create_next_id_in_directory(self):
        self.backend.create(self.path)
        subpath = os.path.join(self.path, '5')
        self.backend.create(subpath)
        self.backend.create_next_id(self.path)
        self.assertTrue(os.path.exists(os.path.join(self.path, '6')))

    def test_create_next_id_in_directory_below_root(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        self.backend.create_next_id(self.path)
        self.assertTrue(os.path.exists(os.path.join(self.root, self.path, '1')))

    def test_deposit_without_path_raises(self):
        with self.assertRaises(directory.MissingPathError):
            self.backend.deposit(content=self.create_zip_archive())

    def test_deposit_without_content_raises(self):
        with self.assertRaises(directory.MissingContentError):
            self.backend.deposit(path=self.path)

    def test_deposit_writes_files(self):
        self.backend.create(self.path)
        self.backend.deposit(path=self.path, content=self.create_zip_archive())
        self.assertTrue(os.path.exists(os.path.join(self.path, 'test.txt')))

    def test_deposit_with_root_writes_files(self):
        self.backend.root_directory = self.root
        self.backend.create(self.path)
        self.backend.deposit(path=self.path, content=self.create_zip_archive())
        self.assertTrue(os.path.exists(os.path.join(self.root, self.path,
                                                    'test.txt')))

    def test_retrieve_without_path_raises(self):
        self.backend.create(self.path)
        with self.assertRaises(directory.MissingPathError):
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
        with self.assertRaises(directory.MissingPathError):
            self.backend.get_manifest()

    def test_get_manifest_with_non_existing_path_raises(self):
        with self.assertRaises(OSError):
            self.backend.get_manifest(path=self.path)

    def test_get_manifest_with_non_existing_manifest_raises(self):
        self.backend.create(self.path)
        with self.assertRaises(directory.MissingContentError):
            self.backend.get_manifest(path=self.path)

    def test_get_manifest_returns_contents_as_string(self):
        self.backend.create(self.path)
        manifest_contents = 'foo'
        with open(os.path.join(self.path, self.manifest_filename), 'w+') as f:
            f.write(manifest_contents)
        self.assertEqual(manifest_contents, self.backend.get_manifest(
            self.path))

    def test_get_checksum_without_path_raises(self):
        self.backend.create(self.path)
        with self.assertRaises(directory.MissingPathError):
            self.backend.get_checksum()

    def test_get_checksum_with_non_existing_path_raises(self):
        with self.assertRaises(OSError):
            self.backend.get_checksum(path=self.path)

    def test_get_checksum_with_non_existing_checksum_file_raises(self):
        self.backend.create(self.path)
        with self.assertRaises(directory.MissingContentError):
            self.backend.get_checksum(path=self.path)

    def test_get_checksum_returns_contents_as_string(self):
        self.backend.create(self.path)
        checksum_contents = 'bar'
        with open(os.path.join(self.path, self.checksum_filename), 'w+') as f:
            f.write(checksum_contents)
        self.assertEqual(checksum_contents,
                         self.backend.get_checksum(self.path))

    def test_get_checksum_for_data_returns_contents_as_string(self):
        self.backend.create(self.path)
        checksum_contents = 'bar'
        with open(os.path.join(self.path, self.checksum_data_filename),
                  'w+') as f:
            f.write(checksum_contents)
        self.assertEqual(checksum_contents, self.backend.get_checksum(
            self.path, data=True))

    def test_get_index_returns_list_of_paths(self):
        self.backend.create(self.path)
        self.assertEqual(self.path, self.backend.get_index()[0])

    def test_get_index_with_root_returns_list_of_paths(self):
        self.backend.root_directory = self.root
        paths = ['foo', 'bar', 'foobar']
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
        with open(os.path.join(self.path, self.manifest_filename), 'w+') as f:
            f.write('foo')
        self.assertEqual(self.path, self.backend.get_index()[0])


if __name__ == '__main__':
    unittest.main()
