import re


class ListChecker:

    def __init__(self):
        self.list = None

    def check(self, string):
        return string in self.list


class PatternChecker:

    def __init__(self):
        self.pattern = None

    def check(self, string):
        return re.fullmatch(self.pattern, string)


class LoiChecker:
    def __init__(self):
        self.loi_identifier = '42.'
        self.types = ['ds', 'recipe', 'img']
        self.dataset_kinds = ['exp', 'calc']
        self.exp_objects = ['sa', 'ba']

    def check(self, loi=''):
        if not isinstance(loi, str):
            raise TypeError

        check_result = [
            self._starts_with_42(loi),
            self._type_in_list_of_types(loi),
            ]

        # Only if we are a dataset, test for the correct kind
        if loi.split('/')[1] == 'ds':
            check_result.append(self._kind_in_list_of_kinds(loi))
            if loi.split('/')[2] == 'exp':
                check_result.append(self._exp_object_in_list_of_objects(loi))
                if loi.split('/')[3] in ['sa', 'ba']:
                    check_result.append(self._exp_sa_ba_has_number(loi))

        return all(check_result)

    def _starts_with_42(self, loi):
        result = False
        if loi.startswith(self.loi_identifier):
            result = True
        return result

    def _type_in_list_of_types(self, loi):
        checker = ListChecker()
        checker.list = self.types
        return checker.check(loi.split('/')[1])

    def _kind_in_list_of_kinds(self, loi):
        checker = ListChecker()
        checker.list = self.dataset_kinds
        return checker.check(loi.split('/')[2])

    def _exp_object_in_list_of_objects(self, loi):
        result = False
        string_to_test = loi.split('/')[3]
        if string_to_test in self.exp_objects:
            result = True
        else:
            checker = PatternChecker()
            checker.pattern = "\d{4}-\d{2}-\d{2}"
            result = checker.check(string_to_test)
        return result

    def _exp_sa_ba_has_number(self, loi):
        checker = PatternChecker()
        checker.pattern = "\d+"
        return checker.check(loi.split('/')[4])
