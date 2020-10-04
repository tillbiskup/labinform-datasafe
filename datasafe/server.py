import datasafe.loi as loi_


class Backend:
    """
    Provide backend functionality for the server part of the datasafe.

    The datasafe-server provides the actual file and directory structure
    within the datasafe. It retrieves datasets, stores them and should check,
    whether its content is complete and not compromised.

    The transfer occurs as bytes of the zipped dataset that is received by
    the server, decoded, unzipped, and archived into the correct directory.

    .. todo::
        Define and implement form of communication to pass commands from
        client to server. Might be URL-like.
    """
    def get(self, loi=''):
        if not loi:
            raise loi_.MissingLoiError('No LOI provided.')
        checker = loi_.LoiChecker()
        if not checker.check(loi):
            raise loi_.InvalidLoiError('String is not a valid LOI.')
        if not self._is_datasafe_loi(loi):
            raise loi_.InvalidLoiError('LOI is not a datasafe LOI.')

    @staticmethod
    def _is_datasafe_loi(loi):
        """ Check if LOI belongs to datasafe. """
        parser = loi_.Parser()
        return parser.parse(loi)['type'] == 'ds'


class Server:
    pass
