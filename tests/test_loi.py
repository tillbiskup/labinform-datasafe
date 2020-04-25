import unittest

from datasafe import loi as loi_


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

    def test_with_correct_loi_returns_true(self):
        self.assertTrue(self.checker.check(self.loi))
        self.assertTrue(self.checker.check('42.1001/ds/exp/2020-04-25/cwepr/1'))
        self.assertTrue(self.checker.check('42.1001/ds/calc/geo/42'))
        self.assertTrue(self.checker.check('42.1001/rec/42'))
        self.assertTrue(self.checker.check('42.1001/img/foo'))
        self.assertTrue(self.checker.check('42.1001/info/foo'))

    def test_loi_not_starting_with_42_returns_false(self):
        self.assertFalse(self.checker.check('43.1001/foo'))

    def test_loi_with_incorrect_type_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/foo'))

    def test_ds_loi_with_incorrect_kind_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/ds/foo'))

    def test_rec_loi_with_kind_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/rec/exp'))

    def test_exp_loi_with_incorrect_object_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/ds/exp/foo'))

    def test_exp_loi_with_date_object_returns_true(self):
        self.assertTrue(self.checker.check(
            '42.1001/ds/exp/2020-04-25/cwepr/1'))

    def test_ba_sa_loi_without_number_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/ds/exp/ba/foo'))
        self.assertFalse(self.checker.check('42.1001/ds/exp/sa/foo'))

    def test_exp_loi_with_wrong_method_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/ds/exp/sa/42/foo'))
        self.assertFalse(self.checker.check('42.1001/ds/exp/2020-04-25/foo'))

    def test_exp_loi_without_measurement_number_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/ds/exp/sa/42/cwepr/a'))
        self.assertFalse(self.checker.check(
            '42.1001/ds/exp/2020-04-25/cwepr/a'))

    def test_calc_with_incorrect_object_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/ds/calc/foo'))

    def test_calc_without_object_number_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/ds/calc/geo/foo'))
        self.assertFalse(self.checker.check('42.1001/ds/calc/result/foo'))

    def test_rec_without_number_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/rec/foo'))


if __name__ == '__main__':
    unittest.main()
