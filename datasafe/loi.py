import re

import datasafe.utils as utils


class AbstractChecker:
    """ Base class for different types of checkers

    The LOI is analysed using basic checkers that look for specific elements
    or patterns.

    Parameters
    ----------
    string : :class:`str`
        Part of the LOI that should be checked.
    """
    def check(self, string):
        pass


class InListChecker(AbstractChecker):
    """
    Check whether the given string is contained in a given list.

    Attributes
    ----------
    list : :class:`list`
        List of strings that are possible options for the given string.
    """

    def __init__(self):
        self.list = None

    def check(self, string):
        """
        Return boolean if string is contained in given list.

        Parameters
        ----------
        string : :class:`str`
            part of the LOI to check

        Returns
        -------
        : :class:`bool`
            bool True if string in list. (??)
        """
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


class IsFriendlyStringChecker(IsPatternChecker):
    def __init__(self):
        super().__init__()
        self.pattern = "[a-z0-9-_]+"

    def check(self, string):
        return super().check(string)


class AbstractLoiChecker:
    """
    Abstract checker class to check if LOI is supposed to exist.

    The Laboratory Object Identifier (LOI) is a persistent identifier or
    handle to identify various samples, objects and projects that are linked
    to a laboratory and its working group. The aim of it is a unique
    connection between those objects and actions performed on or with them.

    The checker works recursive-like: If the attribute :attr:`next_checker`
    is given in the respective class, checking continues.

    This class contains the public method :meth:`check` which calls the private
    method :meth:`_check` that is to be overwritten in derived checkers.

    Attributes
    ----------
    next_checker: :class:`str`
        Next checker class that should be called
    separator : :class:`str`
        Sign that separates different parts of the LOI. Standard: /
    """
    def __init__(self):
        self.next_checker = None
        self.separator = '/'

    def check(self, string):
        """

        Parameters
        ----------
        string : :class:`str`
            Part of the LOI to check.

        Returns
        -------
        result : :class: `bool`
            Returns true if part of the string is valid.

        """
        result = self._check(string.split(self.separator)[0])
        if result and self.next_checker:
            substring = self.separator.join(string.split(self.separator)[1:])
            result = self.next_checker.check(substring)
        return result

    def _check(self, string):
        """
        Private checking method, has to be overwritten in derived classes.
        """
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


class LoiInfoOtherKindChecker(AbstractLoiChecker):
    def _check(self, string):
        checker = IsFriendlyStringChecker()
        return checker.check(string)


class LoiInfoProjectChecker(LoiInfoOtherKindChecker):
    pass


class LoiInfoPublicationChecker(LoiInfoOtherKindChecker):
    pass


class LoiInfoGrantChecker(LoiInfoOtherKindChecker):
    pass


class LoiInfoDeviceChecker(LoiInfoOtherKindChecker):
    pass


class LoiInfoChemicalChecker(LoiInfoOtherKindChecker):
    pass


class LoiInfoPersonChecker(LoiInfoOtherKindChecker):
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
