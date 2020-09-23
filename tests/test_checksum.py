import os
import unittest

from datasafe import checksum


class TestChecksumGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = checksum.Generator()
        self.filenames = ['foo', 'bar']
        self.strings = ['foo', 'bar']

    def tearDown(self):
        for filename in self.filenames:
            if os.path.exists(filename):
                os.remove(filename)

    def _create_files(self):
        for idx, filename in enumerate(self.filenames):
            with open(filename, 'w+') as file:
                file.write(self.strings[idx])

    def test_instantiate_class(self):
        pass

    def test_checksum_module_has_hash_string_method(self):
        self.assertTrue(hasattr(self.generator, 'hash_string'))

    def test_hash_string_returns_hash(self):
        self.assertEqual(self.generator.hash_string('foobar'),
                         '3858f62230ac3c915f300c664312c63f')

    def test_hash_string_with_sha256_algorithm_returns_hash(self):
        self.generator.algorithm = 'sha256'
        self.assertEqual(self.generator.hash_string('foobar'),
                         'c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2')

    def test_checksum_module_has_hash_strings_method(self):
        self.assertTrue(hasattr(self.generator, 'hash_strings'))

    def test_hash_strings_returns_hash(self):
        self.assertEqual(self.generator.hash_strings(['foo', 'bar']),
                         '96948aad3fcae80c08a35c9b5958cd89')

    def test_hash_strings_returns_hash_independent_of_sorting(self):
        self.assertEqual(self.generator.hash_strings(['bar', 'foo']),
                         '96948aad3fcae80c08a35c9b5958cd89')

    def test_checksum_module_has_generate_method(self):
        self.assertTrue(hasattr(self.generator, 'generate'))

    def test_generate_with_md5_algorithm_returns_correct_checksum(self):
        self._create_files()
        self.generator.algorithm = 'md5'
        self.assertEqual(self.generator.generate(self.filenames[0]),
                         'acbd18db4cc2f85cedef654fccc4a4d8')

    def test_generate_with_sha256_algorithm_returns_correct_checksum(self):
        self._create_files()
        self.generator.algorithm = 'sha256'
        self.assertEqual(self.generator.generate(self.filenames[0]),
                         '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae')

    def test_generate_with_md5_with_files_returns_correct_checksum(self):
        self._create_files()
        self.assertEqual(self.generator.generate(self.filenames),
                         '7813987d9dc87851f49ecbed9f875968')


if __name__ == '__main__':
    unittest.main()

