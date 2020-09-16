import unittest

from datasafe import checksum


class TestChecksumGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = checksum.ChecksumGenerator()
        path_to_files = '../tests/files/'
        self.filename = path_to_files + 'sa620-01.xml'

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

    def test_generate_returns_checksum_of_file(self):
        self.assertEqual(self.generator.generate(self.filename),
                         'db432cd074fe817703c87d34676332cd')

    def test_generate_with_md5_algorithm_returns_correct_checksum(self):
        self.generator.algorithm = 'md5'
        self.assertEqual(self.generator.generate(self.filename),
                         'db432cd074fe817703c87d34676332cd')

    def test_generate_with_sha256_algorithm_returns_correct_checksum(self):
        self.generator.algorithm = 'sha256'
        self.assertEqual(self.generator.generate(self.filename),
                         '23c202ee031d74d1f22ce321517f2b34e310bd05df30fe87adc2d330916bc9fa')


if __name__ == '__main__':
    unittest.main()
