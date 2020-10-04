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
        """
        Check if LOI belongs to datasafe.

        .. todo::
            Needs to go into loi module and to get converted there into a
            checker class!
            Needs to get removed from other modules

        """
        parts = loi.split('/')
        return parts[1] == 'ds'


class Server:
    pass
