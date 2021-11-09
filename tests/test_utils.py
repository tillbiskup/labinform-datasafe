import os
import unittest

from datasafe import utils


class TestObjectFromClassName(unittest.TestCase):

    def test_object_from_class_name(self):
        from datasafe.loi import LoiChecker
        object_ = utils.object_from_name(module_name='datasafe.loi',
                                         class_name='LoiChecker')
        self.assertTrue(isinstance(object_, LoiChecker))


class TestChangeWorkingDir(unittest.TestCase):

    def test_change_working_dir_changes_working_dir(self):
        with utils.change_working_dir('..'):
            working_dir = os.path.abspath(os.getcwd())
        self.assertEqual(os.path.split(os.getcwd())[0], working_dir)

    def test_change_working_dir_returns_to_original_dir(self):
        oldpwd = os.getcwd()
        with utils.change_working_dir('..'):
            pass
        self.assertEqual(oldpwd, os.getcwd())

    def test_change_working_dir_with_empty_path(self):
        with utils.change_working_dir(''):
            working_dir = os.path.abspath(os.getcwd())
        self.assertEqual(os.getcwd(), working_dir)
