"""
Client components of the LabInform datasafe.

Clients of the datasafe connect to a server component of the datasafe and
are responsible for a series of different tasks:

* Deposit and retrieve items (currently: datasets) to and from the datasafe.

* Prepare items (currently: datasets) for depositing in the datasafe.

  For datasets, this means that a manifest needs to be written. And for a
  manifest to be written, at least the format of the actual data needs to be
  provided. In case of info or YAML files as metadata files,
  the :class:`datasafe.manifest.Manifest` class should be able to
  auto-detect the format and version of the metadata format,
  using :class:`datasafe.manifest.FormatDetector`. See there for details.

Probably, clients will be able to work both, with local servers and those
using the HTTP(S) protocol.

"""
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
        # This is just to make the test run
        with open(os.path.join(tmpdir, 'MANIFEST.yaml'), 'w+') as file:
            file.write('')
