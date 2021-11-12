"""
Exceptions for the datasafe package.

For preventing cyclic imports and for a better overview, all exception
classes of the datasafe package are collected in this module. It is save for
every other module to import this module, as this module does *not* depend
on any other modules.

"""


class Error(Exception):
    """Base class for exceptions in this module."""


class MissingPathError(Error):
    """Exception raised when no path is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class MissingContentError(Error):
    """Exception raised when no content is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class MissingLoiError(Error):
    """Exception raised when no LOI is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class LoiNotFoundError(Error):
    """Exception raised when LOI cannot be found provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class InvalidLoiError(Error):
    """Exception raised when invalid LOI is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class MissingInformationError(Error):
    """Exception raised when necessary information is not provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class NoFileError(Error):
    """Exception raised when file does not exist

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class ExistingFileError(Error):
    """Exception raised when file does not exist

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__(message)
        self.message = message
