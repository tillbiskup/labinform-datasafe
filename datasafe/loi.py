import re

import datasafe.utils as utils


class AbstractChecker:
    def check(self, string):
        pass


class InListChecker(AbstractChecker):

    def __init__(self):
        self.list = None

    def check(self, string):
        return string in self.list


class StartsWithChecker(AbstractChecker):
    def __init__(self):
        self.string = ''

    def check(self, string=''):
        return string.startswith(self.string)


class IsPatternChecker(AbstractChecker):

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


class AbstractLoiChecker:
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


class LoiChecker(AbstractLoiChecker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiTypeChecker()

    def _check(self, string):
        checker = LoiStartsWith42Checker()
        return checker.check(string)


class LoiStartsWith42Checker(AbstractLoiChecker):

    def _check(self, string):
        checker = StartsWithChecker()
        checker.string = '42.'
        return checker.check(string)


class LoiTypeChecker(AbstractLoiChecker):

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['ds', 'rec', 'img', 'info']
        result = checker.check(string)
        if result:
            self.next_checker = utils.object_from_name(
                'datasafe.loi', 'Loi' + string.capitalize() + 'Checker')
        return result


class LoiRecChecker(AbstractLoiChecker):

    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiDsChecker(AbstractLoiChecker):

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['exp', 'calc']
        result = checker.check(string)
        if result:
            self.next_checker = utils.object_from_name(
                'datasafe.loi', 'Loi' + string.capitalize() + 'Checker')
        return result


class LoiExpChecker(AbstractLoiChecker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiExpMethodChecker()

    def _check(self, string):
        checker = IsDateChecker()
        result = checker.check(string)
        if not result:
            checker = BaSaChecker()
            result = checker.check(string)
            self.next_checker = BaSaNumberChecker()
        return result


class BaSaChecker(AbstractLoiChecker):

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['ba', 'sa']
        return checker.check(string)


class BaSaNumberChecker(AbstractLoiChecker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiExpMethodChecker()

    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiExpMethodChecker(AbstractLoiChecker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiMeasurementNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['cwepr', 'trepr']
        return checker.check(string)


class LoiMeasurementNumberChecker(AbstractLoiChecker):
    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiCalcChecker(AbstractLoiChecker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiCalcObjectNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['geo', 'result']
        return checker.check(string)


class LoiCalcObjectNumberChecker(AbstractLoiChecker):
    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiImgChecker(AbstractLoiChecker):

    def _check(self, string):
        return True


class LoiInfoChecker(AbstractLoiChecker):
    def __init__(self):
        super().__init__()
        self.next_checker = LoiInfoKindChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['tb', 'ms', 'jp', 'dm', 'cm']
        return checker.check(string)


class LoiInfoKindChecker(AbstractLoiChecker):
    def _check(self, string):
        checker = InListChecker()
        checker.list = ['sample', 'calculation', 'project', 'publication',
                        'grant', 'device', 'chemical', 'person']
        result = checker.check(string)
        if result:
            self.next_checker = utils.object_from_name(
                'datasafe.loi', 'LoiInfo' + string.capitalize() + 'Checker')
        return result


class LoiInfoFakeChecker(AbstractLoiChecker):
    def _check(self, string):
        return True


class LoiInfoProjectChecker(LoiInfoFakeChecker):
    pass


class LoiInfoPublicationChecker(LoiInfoFakeChecker):
    pass


class LoiInfoGrantChecker(LoiInfoFakeChecker):
    pass


class LoiInfoDeviceChecker(LoiInfoFakeChecker):
    pass


class LoiInfoChemicalChecker(LoiInfoFakeChecker):
    pass


class LoiInfoPersonChecker(LoiInfoFakeChecker):
    pass


class LoiInfoSampleChecker(AbstractLoiChecker):
    def __init__(self):
        super().__init__()
        self.next_checker = IsNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['batch', 'sample', 'substrate', 'synthesis', 'cell',
                        'tube']
        return checker.check(string)


class LoiInfoCalculationChecker(AbstractLoiChecker):
    def __init__(self):
        super().__init__()
        self.next_checker = IsNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ['molecule', 'geometry', 'calculation']
        return checker.check(string)
