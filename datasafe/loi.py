import re

import datasafe.utils as utils


class InListChecker:

    def __init__(self):
        self.list = None

    def check(self, string):
        return string in self.list


class IsPatternChecker:

    def __init__(self):
        self.pattern = ''

    def check(self, string):
        return re.fullmatch(self.pattern, string)


class IsNumberChecker(IsPatternChecker):
    def __init__(self):
        super().__init__()
        self.pattern = "\d+"

    def check(self, string=''):
        return super().check(string)


class IsDateChecker(IsPatternChecker):
    def __init__(self):
        super().__init__()
        self.pattern = "\d{4}-[0-1][0-9]-[0-3][0-9]"

    def check(self, string):
        return super().check(string)


class StartsWithChecker:
    def __init__(self):
        self.string = ''

    def check(self, string=''):
        return string.startswith(self.string)


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


class OldLoiChecker:
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


class Checker:
    def __init__(self):
        self.next_checker = None
        self.separator = '/'

    def check(self, string):
        result = self._check(string.split(self.separator)[0])
        if result and self.next_checker:
            substring = self.separator.join(string.split(self.separator)[1:])
            result = self.next_checker.check(substring)
        return result

    def _check(self, string):
        return False


class LoiChecker(Checker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiTypeChecker()

    def _check(self, string):
        checker = LoiStartsWith42Checker()
        return checker.check(string)


class LoiStartsWith42Checker(Checker):

    def _check(self, string):
        checker = StartsWithChecker()
        checker.string = '42.'
        return checker.check(string)


class LoiTypeChecker(Checker):

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['ds', 'rec', 'img', 'info']
        result = checker.check(string)
        if result:
            self.next_checker = utils.object_from_name(
                'datasafe.loi', 'Loi' + string.capitalize() + 'Checker')
        return result


class LoiRecChecker(Checker):

    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiExpChecker(Checker):
    def _check(self, string):
        checker = IsDateChecker()
        result = checker.check(string)
        if not result:
            checker = InListChecker()
            checker.list = ['ba', 'sa']
            result = checker.check(string)
        return result


class LoiDsChecker(Checker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiExpChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['exp', 'calc']
        return checker.check(string)
