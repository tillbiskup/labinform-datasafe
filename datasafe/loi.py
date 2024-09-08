"""
Lab Object Identifiers (LOIs)

Accessing objects in a laboratory via unique identifiers (here: a *Lab Object
Identifier*, LOI) is a key concept of the LabInform framework. "Object" may
be thought of in a very broad and general way, ranging from (physically
existing) samples via datasets represented as files on a computer storage
system to abstract concepts such as projects.

Currently, the classes implemented in this module can check a LOI for
consistency and compliance to the LOI scheme developed so far.

.. todo::
    structure of the LOI that is implemented in this module needs to be 
    described.

.. note::
    This module should probably eventually be moved to a separate subpackage
    dealing with LOIs. See the `LabInform documentation
    <https://docs.labinform.de/subpackages.html>`_ containing already hints of
    such a subpackage of the LabInform package for details.
"""

import re

from datasafe import utils
from datasafe.exceptions import MissingLoiError, InvalidLoiError


class LoiMixin:
    """
    Define basic properties for LOIs.

    Every class handling LOIs should inherit/mixin this class.

    Attributes
    ----------
    separator : :class:`str`
        Character that separates different parts of the LOI. Defaults to ``/``.

    root : :class:`str`
        Number identifying a LOI; default: 42

    root_issuer_separator : :class:`str`
        Character separating root and issuer; default: ``.``

    """

    def __init__(self):
        self.separator = "/"
        self.root = "42"
        self.root_issuer_separator = "."


class AbstractChecker:
    """
    Base class for different types of checkers.

    A given string is analysed using basic checkers that look for specific
    elements or patterns.

    Derived classes should implement the concrete and private method
    :meth:`check`. This method returns a Boolean value depending on the
    test results.
    """

    def check(self, string):
        """
        Return result of private method :meth:`_check`

        Parameters
        ----------
        string : :class:`str`
            string to check

        Returns
        -------
        : :class:`bool`
            Bool True if string fulfills criteria.

        """
        return self._check(string)

    def _check(self, string):  # noqa
        return False


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

    def _check(self, string):
        return string in self.list


class StartsWithChecker(AbstractChecker):
    """
    Check whether a string starts with the given string.

    Attributes
    ----------
    string : :class:`str`
        Pattern the string should start with

    """

    def __init__(self):
        self.string = ""

    def _check(self, string=""):
        return string.startswith(self.string)


class IsPatternChecker(AbstractChecker):
    """
    Check whether a string matches the given pattern.

    Attributes
    ----------
    pattern : :class:`str`
        Pattern the string should match

    """

    def __init__(self):
        self.pattern = ""

    def _check(self, string):
        return re.fullmatch(self.pattern, string)


class IsNumberChecker(IsPatternChecker):
    r"""
    Check whether a string contains only numbers.

    Attributes
    ----------
    pattern : :class:`str`
        Pattern defining numbers: "\d+"

    """

    def __init__(self):
        super().__init__()
        self.pattern = r"\d+"


class IsDateChecker(IsPatternChecker):
    """
    Check for date in given form (YYYY-MM-DD).

    Note that currently, the checker doesn't validate if the date is valid date.
    """

    def __init__(self):
        super().__init__()
        self.pattern = r"\d{4}-[0-1][0-9]-[0-3][0-9]"


class IsFriendlyStringChecker(IsPatternChecker):
    """Check whether the string contains only "friendly" characters."""

    def __init__(self):
        super().__init__()
        self.pattern = "[a-z0-9-_]+"


class AbstractLoiChecker(LoiMixin):
    """
    Abstract checker class to check if LOI is supposed to exist.

    The Laboratory Object Identifier (LOI) is a persistent identifier or
    handle to identify various samples, objects and projects that are linked
    to a laboratory and its working group. The aim of it is a unique
    connection between those objects and actions performed on or with them.
    The LOI is part of the LabInform framework. For more information see
    `<https://www.labinform.de/>`_

    The checker works recursive-like: If the attribute :attr:`next_checker`
    is given in the respective class, checking continues.

    This class contains the public method :meth:`check` which calls the private
    method :meth:`_check` that is to be overwritten in derived checkers.
    """

    def __init__(self):
        super().__init__()
        self._ignore_check = ""
        self._next_checker = None

    @property
    def ignore_check(self):
        """Check that should be ignored."""
        return self._ignore_check

    @ignore_check.setter
    def ignore_check(self, ignore_check):
        self._ignore_check = ignore_check
        if ignore_check and self._next_checker:
            self._next_checker.ignore_check = ignore_check
            self.next_checker = self._next_checker

    @property
    def next_checker(self):
        """Next checker class that should be called."""
        return self._next_checker

    @next_checker.setter
    def next_checker(self, next_checker):
        if not self.ignore_check or self.ignore_check not in str(
            next_checker
        ):
            self._next_checker = next_checker
            self._next_checker.ignore_check = self.ignore_check
        else:
            self._next_checker = None

    def check(self, string):
        """
        Split string, check first part, give the rest over to next checker.

        Initiates checking cascade by checking the first part of the LOI and
        pass the following string to the next checker (if given) which
        performs the next checking step in a recursive-like way.
        Key element of the LOI validating cascade.

        Parameters
        ----------
        string : :class:`str`
            Part of the LOI to check.

        Returns
        -------
        result : :class:`bool`
            Returns true if part of the string is valid.

        """
        result = self._check(string.split(self.separator)[0])
        if result and self.next_checker:
            substring = self.separator.join(string.split(self.separator)[1:])
            result = self.next_checker.check(substring)
        return result

    def _check(self, string):  # noqa
        """Private checking method, has to be overridden in derived classes."""
        return False


class LoiChecker(AbstractLoiChecker):
    """
    Check a lab object identifier (LOI) to conform to scheme.

    A user only needs to instantiate this class for checking a LOI.

    Begin of the cascading chain to validate a given LOI. Checking starts
    with the first part of the LOI that should start with 42. Following,
    the data type will be surveyed and depending on the result, further
    downstream checkers will be involved. Returns `True` if string is valid
    LOI.
    """

    def __init__(self):
        super().__init__()
        self.next_checker = LoiTypeChecker()

    def _check(self, string):
        """
        Check beginning of LOI and start cascading chain if true.

        A string beginning with correct root that is defined in
        :class:`LoiMixin` indicates a LOI per definition.

        Parameters
        ----------
        string : :class:`str`
            Full LOI to be checked.

        Returns
        -------
        result : :class:`bool`
            Returns true if string is valid LOI.

        """
        checker = LoiStartsWithCorrectRootChecker()
        return checker.check(string)


class LoiStartsWithCorrectRootChecker(AbstractLoiChecker):
    """Check root of LOI."""

    def _check(self, string):
        checker = StartsWithChecker()
        checker.string = self.root + self.root_issuer_separator
        return checker.check(string)


class LoiTypeChecker(AbstractLoiChecker):
    """Check type of LOI."""

    def _check(self, string):
        checker = InListChecker()
        checker.list = ["ds", "rec", "img", "info"]
        result = checker.check(string)
        if result:
            self.next_checker = utils.object_from_name(
                "datasafe.loi", "Loi" + string.capitalize() + "Checker"
            )
        return result


class LoiRecChecker(AbstractLoiChecker):
    """Check rec type of LOI."""

    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiDsChecker(AbstractLoiChecker):
    """Check ds type of LOI."""

    def _check(self, string):
        checker = InListChecker()
        checker.list = ["exp", "calc"]
        result = checker.check(string)
        if result:
            self.next_checker = utils.object_from_name(
                "datasafe.loi", "Loi" + string.capitalize() + "Checker"
            )
        return result


class LoiExpChecker(AbstractLoiChecker):
    """Check exp type of LOI."""

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
    """Check ba/sa of LOI."""

    def _check(self, string):
        checker = InListChecker()
        checker.list = ["ba", "sa"]
        return checker.check(string)


class BaSaNumberChecker(AbstractLoiChecker):
    """Check ba/sa number type of LOI."""

    def __init__(self):
        super().__init__()
        self.next_checker = LoiExpMethodChecker()

    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiExpMethodChecker(AbstractLoiChecker):
    """Check experimental method of LOI."""

    def __init__(self):
        super().__init__()
        self.next_checker = LoiMeasurementNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ["cwepr", "trepr"]
        return checker.check(string)


class LoiMeasurementNumberChecker(AbstractLoiChecker):
    """Check measurement number of LOI."""

    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiCalcChecker(AbstractLoiChecker):
    """Check calc of LOI."""

    def __init__(self):
        super().__init__()
        self.next_checker = LoiCalcObjectNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ["geo", "result"]
        return checker.check(string)


class LoiCalcObjectNumberChecker(AbstractLoiChecker):
    """Check calc object number of LOI."""

    def _check(self, string):
        checker = IsNumberChecker()
        return checker.check(string)


class LoiImgChecker(AbstractLoiChecker):
    """Check img of LOI."""

    def _check(self, string):
        return True


class LoiInfoChecker(AbstractLoiChecker):
    """Check info of LOI."""

    def __init__(self):
        super().__init__()
        self.next_checker = LoiInfoKindChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ["tb", "ms", "jp", "dm", "cm"]
        return checker.check(string)


class LoiInfoKindChecker(AbstractLoiChecker):
    """Check info kind of LOI."""

    def _check(self, string):
        checker = InListChecker()
        checker.list = [
            "sample",
            "calculation",
            "project",
            "publication",
            "grant",
            "device",
            "chemical",
            "person",
        ]
        result = checker.check(string)
        if result:
            self.next_checker = utils.object_from_name(
                "datasafe.loi", "LoiInfo" + string.capitalize() + "Checker"
            )
        return result


class LoiInfoOtherKindChecker(AbstractLoiChecker):
    """Check info other kind of LOI."""

    def _check(self, string):
        checker = IsFriendlyStringChecker()
        return checker.check(string)


class LoiInfoProjectChecker(LoiInfoOtherKindChecker):
    """Check info project of LOI."""


class LoiInfoPublicationChecker(LoiInfoOtherKindChecker):
    """Check info publication of LOI."""


class LoiInfoGrantChecker(LoiInfoOtherKindChecker):
    """Check info grant of LOI."""


class LoiInfoDeviceChecker(LoiInfoOtherKindChecker):
    """Check info device of LOI."""


class LoiInfoChemicalChecker(LoiInfoOtherKindChecker):
    """Check info chemical of LOI."""


class LoiInfoPersonChecker(LoiInfoOtherKindChecker):
    """Check info person of LOI."""


class LoiInfoSampleChecker(AbstractLoiChecker):
    """Check info sample of LOI."""

    def __init__(self):
        super().__init__()
        self.next_checker = IsNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = [
            "batch",
            "sample",
            "substrate",
            "synthesis",
            "cell",
            "tube",
        ]
        return checker.check(string)


class LoiInfoCalculationChecker(AbstractLoiChecker):
    """Check info calculation of LOI."""

    def __init__(self):
        super().__init__()
        self.next_checker = IsNumberChecker()

    def _check(self, string):
        checker = InListChecker()
        checker.list = ["molecule", "geometry", "calculation"]
        return checker.check(string)


class Parser(LoiMixin):
    """
    Parse LOIs, allowing to handle different parts correctly.

    A LOI consists of four parts:

      * root
      * issuer
      * type
      * id

    Generally, a LOI could be written like this::

        <root>.<issuer>/<type>/<id>

    Typically, root is fixed for LOIs (42) and issuer is a number. Type is a
    single string, and id usually consists of several parts separated by a "/".

    For general aspects of LOIs, such as root and separator(s), refer to the
    :class:`LoiMixin` class.
    """

    def __init__(self):
        super().__init__()
        self.issuer = ""
        self.type = ""
        self.id = ""  # noqa

    def parse(self, loi=""):
        """
        Parse given LOI and create dict with the four parts described above.

        Parameters
        ----------
        loi : :class:`str`
            LOI to parse.

        Returns
        -------
        parser_dict : :class:`dict`
            Dict with parts of the LOI as key:value pairs.

        Raises
        ------
        datasafe.loi.MissingLoiError
            Raised if no LOI is provided.

        datasafe.loi.InvalidLoiError
            Raised if given string is not a valid LOI.

        """
        if not loi:
            raise MissingLoiError("No LOI provided.")
        checker = LoiChecker()
        checker.ignore_check = "LoiDsChecker"
        if not checker.check(loi):
            raise InvalidLoiError("String is not a valid LOI.")
        self.issuer = loi.split(self.separator)[0].split(
            self.root_issuer_separator
        )[1]
        self.type = loi.split(self.separator)[1]
        self.id = self.separator.join(loi.split(self.separator)[2:])
        parser_dict = {
            "root": loi.split(self.separator)[0].split(
                self.root_issuer_separator
            )[0],
            "issuer": self.issuer,
            "type": self.type,
            "id": self.id,
        }

        return parser_dict

    def split_id(self):
        """
        Split id part of LOI at separator and return list of components.

        Returns
        -------
        id_parts : :class:`list`
            List (of strings) with parts of ID split at separator

            Empty list if no LOI has been parsed

        """
        id_parts = []
        if self.id:
            id_parts = self.id.split(self.separator)
        return id_parts
