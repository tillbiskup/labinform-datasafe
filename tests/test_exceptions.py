import unittest

from datasafe import exceptions


class TestMissingPathError(unittest.TestCase):

    def setUp(self):
        self.exception = exceptions.MissingPathError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingContentError(unittest.TestCase):

    def setUp(self):
        self.exception = exceptions.MissingContentError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingLoiError(unittest.TestCase):

    def setUp(self):
        self.exception = exceptions.MissingLoiError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestLoiNotFoundError(unittest.TestCase):

    def setUp(self):
        self.exception = exceptions.LoiNotFoundError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestMissingInformationError(unittest.TestCase):

    def setUp(self):
        self.exception = exceptions.MissingInformationError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestNoFileError(unittest.TestCase):

    def setUp(self):
        self.exception = exceptions.NoFileError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')


class TestExistingFileError(unittest.TestCase):

    def setUp(self):
        self.exception = exceptions.ExistingFileError

    def test_prints_message(self):
        with self.assertRaisesRegex(self.exception, 'bla'):
            raise self.exception('bla')
