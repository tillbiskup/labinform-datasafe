import unittest

from datasafe import loi as loi_


class TestOldLoiChecker(unittest.TestCase):

    def setUp(self):
        self.checker = loi_.OldLoiChecker()
        self.loi = '42.1001/ds/exp/sa/42/cwepr/1'
        self.types = ['ds', 'recipe', 'img']
        self.dataset_kinds = ['exp', 'calc']
        self.dataset_exp_objects = ['sa', 'ba']

    def test_instantiate_class(self):
        pass

    def test_check_gets_loi(self):
        self.checker.check(self.loi)

    def test_loi_with_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            self.checker.check(1.0)

    def test_loi_starting_with_42_returns_true(self):
        self.assertTrue(self.checker.check(self.loi))

    def test_loi_not_starting_with_42_returns_false(self):
        self.assertFalse(self.checker.check('43.1001/ds/foo'))

    def test_type_known(self):
        for type_ in self.types:
            loi = '/'.join(['42.1001', type_, 'exp', 'sa', '4'])
            self.assertTrue(self.checker.check(loi))

    def test_type_unknown(self):
        self.assertFalse(self.checker.check('42.1001/foo/bar'))

    def test_ds_kind_known(self):
        for kind in self.dataset_kinds:
            loi = '/'.join(['42.1001', 'ds', kind, 'sa', '4'])
            self.assertTrue(self.checker.check(loi))

    def test_ds_kind_unknown(self):
        self.assertFalse(self.checker.check('42.1001/ds/foo/bar'))

    def test_ds_exp_object_known(self):
        for object_ in self.dataset_exp_objects:
            loi = '/'.join(['42.1001', 'ds', 'exp', object_, '4'])
            self.assertTrue(self.checker.check(loi))
        self.assertTrue(self.checker.check('42.1001/ds/exp/2020-04-24'))

    def test_ds_exp_object_unknown(self):
        self.assertFalse(self.checker.check('42.1001/ds/exp/foo'))

    def test_ds_exp_date_with_wrong_format(self):
        self.assertFalse(self.checker.check('42.1001/ds/exp/202-03-24'))

    def test_ds_exp_sa_ba_with_number(self):
        for object_ in ['sa', 'ba']:
            loi = '/'.join(['42.1001', 'ds', 'exp', object_, '5'])
            self.assertTrue(self.checker.check(loi))

    def test_ds_exp_sa_ba_with_no_number(self):
        for object_ in ['sa', 'ba']:
            loi = '/'.join(['42.1001', 'ds', 'exp', object_, 'cwepr'])
            self.assertFalse(self.checker.check(loi))


class TestListChecker(unittest.TestCase):
    def setUp(self):
        self.checker = loi_.InListChecker()
        self.list = ['foo', 'bar']
        self.checker.list = self.list

    def test_string_in_list_returns_true(self):
        for element in self.list:
            self.assertTrue(self.checker.check(element))

    def test_string_not_in_list_returns_false(self):
        self.assertFalse(self.checker.check('foobar'))


class TestPatternChecker(unittest.TestCase):
    def setUp(self):
        self.checker = loi_.IsPatternChecker()
        # noinspection PyPep8
        self.checker.pattern = "\d{2}"

    def test_string_conforms_with_pattern_returns_true(self):
        self.assertTrue(self.checker.check('42'))

    def test_string_does_not_conform_with_pattern_returns_false(self):
        self.assertFalse(self.checker.check('432'))


class TestStartsWithChecker(unittest.TestCase):
    def setUp(self):
        self.checker = loi_.StartsWithChecker()
        self.checker.string = '42.'

    def test_string_starts_with_substring_returns_true(self):
        self.assertTrue(self.checker.check('42.1001'))

    def test_string_does_not_start_with_substring_returns_false(self):
        self.assertFalse(self.checker.check('43.1001'))


class TestIsNumberChecker(unittest.TestCase):
    def setUp(self):
        self.checker = loi_.IsNumberChecker()

    def test_string_is_number_returns_true(self):
        self.assertTrue(self.checker.check('42'))

    def test_string_is_not_number_returns_false(self):
        self.assertFalse(self.checker.check('ab'))


class TestIsDateChecker(unittest.TestCase):
    def setUp(self):
        self.checker = loi_.IsDateChecker()

    def test_string_is_date_returns_true(self):
        self.assertTrue(self.checker.check('2020-04-25'))

    def test_string_is_not_date_returns_false(self):
        self.assertFalse(self.checker.check('2020-30-01'))


class TestLoiChecker(unittest.TestCase):
    def setUp(self):
        self.checker = loi_.LoiChecker()
        self.loi = '42.1001/ds/exp/sa/42/cwepr/1'

    def test_loi_starting_with_42_returns_true(self):
        self.assertTrue(self.checker.check(self.loi))

    def test_loi_not_starting_with_42_returns_false(self):
        self.assertFalse(self.checker.check('43.1001/foo'))

    def test_loi_with_correct_type_returns_true(self):
        self.assertTrue(self.checker.check(self.loi))

    def test_loi_with_incorrect_type_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/foo'))

    def test_ds_loi_with_correct_kind_returns_true(self):
        self.assertTrue(self.checker.check(self.loi))

    def test_ds_loi_with_incorrect_kind_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/ds/foo'))

    def test_rec_loi_with_kind_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/rec/exp'))

    def test_exp_loi_with_correct_object_returns_true(self):
        self.assertTrue(self.checker.check(self.loi))

    def test_exp_loi_with_incorrect_object_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/ds/exp/foo'))

    def test_exp_loi_with_date_object_returns_true(self):
        self.assertTrue(self.checker.check(
            '42.1001/ds/exp/2020-04-25/cwepr/1'))


if __name__ == '__main__':
    unittest.main()
