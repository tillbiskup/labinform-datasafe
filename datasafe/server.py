import io
import socketserver
import tempfile
import threading

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


class Backend:
    def get(self, loi=''):
        if not loi:
            raise MissingLoiError('No LOI provided.')
        checker = datasafe.loi.LoiChecker()
        if not checker.check(loi):
            raise InvalidLoiError('String is not a valid LOI.')
        if not self._is_datasafe_loi(loi):
            raise InvalidLoiError('LOI is not a datasafe LOI.')

    @staticmethod
    def _is_datasafe_loi(loi):
        """
        Check if LOI belongs to datasafe.

        .. todo::
            Needs to go into loi module and to get converted there into a
            checker class!
            Needs to get removed from other modules

        """
        parts = loi.split('/')
        return parts[1] == 'ds'


class Server(threading.Thread):
    def run(self):
        server = socketserver.ThreadingTCPServer(("", 50000),
                                                 socketserver.BaseRequestHandler)
        server.serve_forever()
