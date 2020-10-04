import os
import tempfile

import datasafe.loi as loi_


class Client:

    def pull(self, loi=''):
        if not loi:
            raise loi_.MissingLoiError('No LOI provided.')
        checker = loi_.LoiChecker()
        if not checker.check(loi):
            raise loi_.InvalidLoiError('String is not a valid LOI.')
        if not self._is_datasafe_loi(loi):
            raise loi_.InvalidLoiError('LOI is not a datasafe LOI.')
        tmpdir = tempfile.mkdtemp()
        self._retrieve_data_from_datasafe_server(loi, tmpdir)
        return tmpdir

    @staticmethod
    def _is_datasafe_loi(loi):
        """ Check if LOI belongs to datasafe. """
        parser = loi_.Parser()
        return parser.parse(loi)['type'] == 'ds'

    def _retrieve_data_from_datasafe_server(self, loi, tmpdir):
        """ Retrieve dataset from datasafe and store it in tmpdir.

        .. todo::
            connect to server and retrieve dataset.
        """
        with open(os.path.join(tmpdir, 'MANIFEST.yaml'), 'w+') as file:
            file.write('')