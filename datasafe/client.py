import os
import tempfile

import datasafe.loi



class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingLoiError(Error):
    """Exception raised when no LOI is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class InvalidLoiError(Error):
    """Exception raised when invalid LOI is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Client:

    def pull(self, loi=''):
        if not loi:
            raise MissingLoiError('No LOI provided.')
        checker = datasafe.loi.LoiChecker()
        if not checker.check(loi):
            raise InvalidLoiError('String is not a valid LOI.')
        if not self._is_datasafe_loi(loi):
            raise InvalidLoiError('LOI is not a datasafe LOI.')
        tmpdir = tempfile.mkdtemp()
        self._retrieve_data_from_datasafe_server(loi, tmpdir)
        return tmpdir


    @staticmethod
    def _is_datasafe_loi(loi):
        """
        Check if LOI belongs to datasafe.

        .. todo::
            Needs to go into loi module and to get converted there into a
            checker class.

        """
        parts = loi.split('/')
        return parts[1] == 'ds'

    def _retrieve_data_from_datasafe_server(self, loi, tmpdir):
        """ Retrieve dataset from datasafe and store it in tmpdir.

        .. todo::
            connect to server and retrieve dataset.
        """
        with open(os.path.join(tmpdir, 'MANIFEST.yaml'), 'w+') as file:
            file.write('')