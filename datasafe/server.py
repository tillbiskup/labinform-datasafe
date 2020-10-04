import datasafe.loi as loi_


class Backend:
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
