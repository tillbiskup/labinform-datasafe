import unittest

import datasafe.exceptions
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
        self.assertTrue(self.checker.check('42.1001/ds/exp/sa/42/cwepr/1'))
        self.assertTrue(self.checker.check('42.1001/ds/calc/geo/42'))
        self.assertTrue(self.checker.check('42.1001/rec/42'))
        self.assertTrue(self.checker.check('42.1001/img/foo'))
        self.assertTrue(self.checker.check('42.1001/info/tb/sample/batch/42'))
        self.assertTrue(self.checker.check(
            '42.1001/info/tb/calculation/molecule/42'))
        self.assertTrue(self.checker.check('42.1001/info/tb/project/foo'))
        self.assertTrue(self.checker.check('42.1001/info/tb/publication/foo'))
        self.assertTrue(self.checker.check('42.1001/info/tb/grant/foo'))
        self.assertTrue(self.checker.check('42.1001/info/tb/device/foo'))
        self.assertTrue(self.checker.check('42.1001/info/tb/chemical/foo'))
        self.assertTrue(self.checker.check('42.1001/info/tb/person/foo'))

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

    def test_info_with_incorrect_initials_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/info/foo'))

    def test_info_with_incorrect_kind_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/info/tb/foo'))

    def test_info_with_incorrect_object_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/info/tb/sample/foo'))
        self.assertFalse(self.checker.check('42.1001/info/tb/calculation/foo'))

    def test_info_sample_without_number_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/info/tb/sample/batch/foo'))

    def test_info_calculation_without_number_returns_false(self):
        self.assertFalse(self.checker.check(
            '42.1001/info/tb/calculation/molecule/foo'))

    def test_info_kind_with_unfriendly_string_returns_false(self):
        self.assertFalse(self.checker.check('42.1001/info/tb/project/foo#'))
        self.assertFalse(self.checker.check('42.1001/info/tb/project/foo?'))
        self.assertFalse(self.checker.check('42.1001/info/tb/project/FOO'))

    def test_exp_loi_ignoring_wrong_ds(self):
        self.checker.ignore_check = 'LoiDsChecker'
        self.assertTrue(self.checker.check('42.1001/ds/foo'))

    def test_exp_loi_ignoring_wrong_exp(self):
        self.checker.ignore_check = 'LoiExpChecker'
        self.assertTrue(self.checker.check('42.1001/ds/exp/foo'))

    def test_exp_loi_ignoring_wrong_basa_number(self):
        self.checker.ignore_check = 'BaSaNumberChecker'
        self.assertTrue(self.checker.check('42.1001/ds/exp/sa/foo'))

    def test_exp_loi_ignoring_wrong_exp_method(self):
        self.checker.ignore_check = 'LoiExpMethodChecker'
        self.assertTrue(self.checker.check('42.1001/ds/exp/sa/42/foo'))

    def test_exp_loi_ignoring_wrong_measurement_number(self):
        self.checker.ignore_check = 'LoiMeasurementNumberChecker'
        self.assertTrue(self.checker.check('42.1001/ds/exp/sa/42/cwepr/foo'))

    def test_exp_loi_ignoring_missing_measurement_number(self):
        self.checker.ignore_check = 'LoiMeasurementNumberChecker'
        self.assertTrue(self.checker.check('42.1001/ds/exp/sa/42/cwepr'))


class TestLoiParser(unittest.TestCase):
    def setUp(self):
        self.parser = loi_.Parser()
        self.loi = '42.1001/ds/exp/sa/42/cwepr/1'

    def test_instantiate_class(self):
        pass

    def test_has_parse_method(self):
        self.assertTrue(hasattr(self.parser, 'parse'))
        self.assertTrue(callable(self.parser.parse))

    def test_parse_without_loi_raises(self):
        with self.assertRaises(datasafe.exceptions.MissingLoiError):
            self.parser.parse()

    def test_parse_with_invalid_loi_raises(self):
        with self.assertRaises(datasafe.exceptions.InvalidLoiError):
            self.parser.parse('FOO')

    def test_parse_sets_issuer(self):
        self.parser.parse(self.loi)
        self.assertEqual('1001', self.parser.issuer)

    def test_parse_sets_real_issuer(self):
        self.parser.parse(self.loi.replace('1001', '1002'))
        self.assertEqual('1002', self.parser.issuer)

    def test_parse_sets_issuer_length_independent(self):
        self.parser.parse(self.loi.replace('1001', '1001001'))
        self.assertEqual('1001001', self.parser.issuer)

    def test_parse_sets_type(self):
        self.parser.parse(self.loi)
        self.assertEqual('ds', self.parser.type)

    def test_parse_sets_id(self):
        self.parser.parse(self.loi)
        self.assertEqual('exp/sa/42/cwepr/1', self.parser.id)

    def test_parse_returns_dict(self):
        self.assertIsInstance(self.parser.parse(self.loi), dict)

    def test_parse_returns_dict_with_correct_keys(self):
        dict_ = self.parser.parse(self.loi)
        self.assertListEqual(list(dict_.keys()),
                             ['root', 'issuer', 'type', 'id'])

    def test_parse_returns_root(self):
        dict_ = self.parser.parse(self.loi)
        self.assertEqual(dict_['root'], '42')

    def test_parse_returns_issuer(self):
        dict_ = self.parser.parse(self.loi)
        self.assertEqual(dict_['issuer'], '1001')

    def test_parse_returns_real_issuer(self):
        dict_ = self.parser.parse(self.loi.replace('1001', '1002'))
        self.assertEqual(dict_['issuer'], '1002')

    def test_parse_returns_issuer_length_independent(self):
        dict_ = self.parser.parse(self.loi.replace('1001', '1001001'))
        self.assertEqual(dict_['issuer'], '1001001')

    def test_parse_returns_type(self):
        dict_ = self.parser.parse(self.loi)
        self.assertEqual(dict_['type'], 'ds')

    def test_parse_returns_id(self):
        dict_ = self.parser.parse(self.loi)
        self.assertEqual(dict_['id'], 'exp/sa/42/cwepr/1')

    def test_split_id_returns_list(self):
        self.assertIsInstance(self.parser.split_id(), list)

    def test_split_id_without_parsed_loi_returns_empty_list(self):
        self.assertEqual([], self.parser.split_id())

    def test_split_id_wit_parsed_loi_returns_id_parts(self):
        self.parser.parse(self.loi)
        self.assertEqual(self.parser.id.split(self.parser.separator),
                         self.parser.split_id())


if __name__ == '__main__':
    unittest.main()
