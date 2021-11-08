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
import shutil
import tempfile

import datasafe.loi as loi_
import datasafe.server as server
from datasafe.utils import change_working_dir


class Client:
    """
    Client part of the datasafe.

    The client interacts with a server to transfer data from and to the
    datasafe.


    Attributes
    ----------
    server : :class:`datasafe.server.Server`

    loi : :class:`datasafe.loi.Parser`

    """

    def __init__(self):
        self.server = server.Server()
        self.loi = loi_.Parser()
        self._loi_checker = loi_.LoiChecker()

    def create(self, loi=''):
        """
        Create new LOI.

        The storage corresponding to the LOI will be created and the LOI
        returned if successful. This does, however, *not* add any data to
        the datasafe. Therefore, calling :meth:`create` will usually be
        followed by calling :meth:`upload` at some later point. On the other
        hand, before calling :meth:`upload`, you *need to* call :meth:`create`
        to create the new LOI storage space.

        Parameters
        ----------
        loi : :class:`str`
            LOI the storage should be created for

        Returns
        -------
        loi : :class:`str`
            LOI the storage has been created for

        Raises
        ------
        datasafe.loi.MissingLoiError
            Raised if no LOI is provided

        datasafe.loi.InvalidLoiError
            Raised if LOI is not valid (for the given operation)

        """
        if not loi:
            raise loi_.MissingLoiError('No LOI provided.')
        self._check_loi(loi=loi, validate=False)
        id_parts = self.loi.split_id()
        if id_parts[0] != 'exp':
            raise loi_.InvalidLoiError('Loi ist not a valid experiment LOI')
        self._loi_checker.ignore_check = 'LoiMeasurementNumberChecker'
        if not self._loi_checker.check(loi):
            raise loi_.InvalidLoiError('String is not a valid LOI.')
        return self.server.new(loi=loi)

    def create_manifest(self):
        """
        Create a manifest file for a given dataset.

        Things to decide about and implement:

        * How to define which data belong to the dataset?

          Perhaps two parameters: file and path; where file is a file
          (base)name and path is a directory assumed to only contain files
          belonging to a single dataset

        * How to define which files are metadata and which are data files?

          Probably, for info and yaml files (the latter excluding
          Manifest.yaml), this can be done entirely automatically. Data
          files will be the remaining files.

        * How to define or detect the file format?

        """
        pass

    def upload(self):
        """
        Upload data belonging to a dataset to the datasafe.

        Should probably automatically create a Manifest file if it does not
        exist, alternatively raise an exception if no Manifest file exists.

        Should create checksums/look them up in the Manifest file and check
        after the upload that they are identical to those for the datasafe.
        """
        pass

    def download(self, loi=''):
        """
        Download data from the datasafe.

        The LOI is checked for belonging to the datasafe. Further checks
        will be done on the server side, resulting in exceptions raised if
        there are some problems.

        .. todo::

            Check checksums obtained for downloaded data with those contained
            in the manifest file and warn/raise if differences are detected.

            In case of differences, one might even obtain new checksums from
            the datasafe and compare them, thus detecting whether the
            problem was during transit or is more severe, *i.e.* corrupted
            data storage.

        Parameters
        ----------
        loi : :class:`str`
            LOI the data should be downloaded for

        Returns
        -------
        download_dir : :class:`str`
            Directory the data obtained from the datasafe have been saved to

        Raises
        ------
        datasafe.loi.MissingLoiError
            Raised if no LOI is provided

        """
        if not loi:
            raise loi_.MissingLoiError('No LOI provided.')
        self._check_loi(loi=loi, validate=False)
        content = self.server.download(loi=loi)
        download_dir = tempfile.mkdtemp()
        with change_working_dir(download_dir):
            archive_file = 'archive.zip'
            with open(archive_file, "wb") as file:
                file.write(content)
            shutil.unpack_archive(archive_file, '.')
            os.remove(archive_file)
        return download_dir

    def _check_loi(self, loi='', validate=True):
        self.loi.parse(loi)
        if not self.loi.type == 'ds':
            raise loi_.InvalidLoiError('LOI is not a datasafe LOI.')
        if validate:
            if not self._loi_checker.check(loi):
                raise loi_.InvalidLoiError('String is not a valid LOI.')
