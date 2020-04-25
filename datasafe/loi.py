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


class LoiDsChecker(Checker):

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['exp', 'calc']
        result = checker.check(string)
        if result:
            self.next_checker = utils.object_from_name(
                'datasafe.loi', 'Loi' + string.capitalize() + 'Checker')
        return result


class LoiExpChecker(Checker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiMethodChecker()

    def _check(self, string):
        checker = IsDateChecker()
        result = checker.check(string)
        if not result:
            checker = BaSaChecker()
            result = checker.check(string)
            self.next_checker = BaSaNumberChecker()
        return result


class BaSaChecker(Checker):

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['ba', 'sa']
        return checker.check(string)


class BaSaNumberChecker(Checker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiMethodChecker()

    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiMethodChecker(Checker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiMeasurementNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['cwepr', 'trepr']
        return checker.check(string)


class LoiMeasurementNumberChecker(Checker):
    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiCalcChecker(Checker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiCalcObjectNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['geo', 'result']
        return checker.check(string)


class LoiCalcObjectNumberChecker(Checker):
    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiImgChecker(Checker):

    def _check(self, string):
        return True


class LoiInfoChecker(Checker):

    def _check(self, string):
        return True
