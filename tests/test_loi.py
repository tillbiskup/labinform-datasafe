import unittest

from datasafe import loi as loi_


class TestLoiChecker(unittest.TestCase):

    def setUp(self):
        self.checker = loi_.LoiChecker()
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
            
    

if __name__ == '__main__':
    unittest.main()
