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
import glob
import json
import os
import shutil
import tempfile
import warnings

import requests

from datasafe.exceptions import InvalidLoiError, MissingLoiError, \
    LoiNotFoundError, ExistingFileError, MissingContentError
import datasafe.loi as loi_
from datasafe.manifest import Manifest
from datasafe import server
from datasafe.utils import change_working_dir


class Client:
    """
    Client part of the datasafe.

    The client interacts with a server to transfer data from and to the
    datasafe.

    This class provides all functionality that is local to the client. The
    actual connection to the server is done in non-public methods that need
    to be implemented in concrete classes.

    There are currently two concrete client classes available:

    * :class:`LocalClient`

      A client connecting locally directly within Python to a local server.

    * :class:`HTTPClient`

      A client connecting via HTTP protocol to an HTTP server.

    Attributes
    ----------
    loi_parser : :class:`datasafe.loi.Parser`

        Parser for lab object identifiers (LOIs). Used to check a given LOI
        for complying to certain criteria (and be a valid LOI).

    metadata_extensions : :class:`tuple`
        File extensions that are regarded as metadata files.

        Used when automatically creating manifest files to distinguish
        between data and metadata files of a dataset.

        Default: ('.info', '.yaml')

    """

    def __init__(self):
        self.loi_parser = loi_.Parser()
        self.metadata_extensions = ('.info', '.yaml')
        self._loi_checker = loi_.LoiChecker()

    def create(self, loi=''):
        """
        Create new LOI.

        Useful to "reserve" and register a LOI in the datasafe, *e.g.* at
        the start of a new measurement.

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
            raise MissingLoiError('No LOI provided.')
        self._check_loi(loi=loi, validate=False)
        id_parts = self.loi_parser.split_id()
        if id_parts[0] != 'exp':
            raise InvalidLoiError('Loi ist not a valid experiment LOI')
        self._loi_checker.ignore_check = 'LoiMeasurementNumberChecker'
        if not self._loi_checker.check(loi):
            raise InvalidLoiError('String is not a valid LOI.')
        return self._server_create(loi=loi)

    def _server_create(self, loi=''):  # noqa
        return ''

    def create_manifest(self, filename='', path=''):
        """
        Create a manifest file for a given dataset.

        Different scenarios for determining which files belong to the
        dataset and for distinguishing between data and metadata files are:

        * Neither parameter ``filename`` nor ``path`` given

          All files of the current directory will be assumed to belong to
          the dataset.

        * Parameter ``filename`` given

          Only files starting with the value of ``filename`` will be
          considered. Note that the value is used as pattern.

        * Parameter ``path``, but no parameter ``filename`` given

          Only files in the directory given by ``path`` will be considered.

        * Both parameters, ``filename`` and ``path`` given

          Only files starting with the value of ``filename`` and located in
          the directory given by ``path`` will be considered. Note that the
          value is used as pattern.

        Metadata will be identified by using the :attr:`metadata_extensions`
        attribute of the class. For details see there.

        .. note::

            As the manifest file has always the same name, it is generally a
            good idea to have one dataset per directory. Otherwise, only one
            manifest file (for one dataset) at a time can be created.


        Things to decide about and implement:

        * How to define or detect the file format?


        Parameters
        ----------
        filename : :class:`str`
            Name of the file(s) belonging to a dataset.

            This is taken as pattern and extended with ".*" and used with
            :func:`glob.glob` if given.

        path : :class:`str`
            File system path where to look for files belonging to a dataset

        """
        manifest = Manifest()
        with change_working_dir(path):
            file_pattern = filename + '.*' if filename else '*'
            filenames = glob.glob(file_pattern)
            manifest.metadata_filenames = \
                [x for x in filenames if x.endswith(self.metadata_extensions)]
            manifest.data_filenames = \
                [x for x in filenames if x not in manifest.metadata_filenames]
            if manifest.manifest_filename in manifest.metadata_filenames:
                manifest.metadata_filenames.remove(manifest.manifest_filename)
            manifest.to_file()

    def upload(self, loi='', filename='', path=''):
        """
        Upload data belonging to a dataset to the datasafe.

        If no manifest file exists, it will automatically be created.

        Different scenarios for determining which files belong to the
        dataset and for distinguishing between data and metadata files are:

        * Neither parameter ``filename`` nor ``path`` given

          All files of the current directory will be assumed to belong to
          the dataset.

        * Parameter ``filename`` given

          Only files starting with the value of ``filename`` will be
          considered. Note that the value is used as pattern.

        * Parameter ``path``, but no parameter ``filename`` given

          Only files in the directory given by ``path`` will be considered.

        * Both parameters, ``filename`` and ``path`` given

          Only files starting with the value of ``filename`` and located in
          the directory given by ``path`` will be considered. Note that the
          value is used as pattern.


        Parameters
        ----------
        loi : :class:`str`
            LOI the data should be downloaded for

        filename : :class:`str`
            Name of the file(s) belonging to a dataset.

            This is taken as pattern and extended with ".*" and used with
            :func:`glob.glob` if given.

        path : :class:`str`
            File system path where to look for files belonging to a dataset


        Returns
        -------
        integrity : :class:`dict`
            dict with fields ``data`` and ``all`` containing boolean values

            For details see :meth:`datasafe.manifest.Manifest.check_integrity`.

        Raises
        ------
        datasafe.loi.MissingLoiError
            Raised if no LOI is provided

        """
        if not loi:
            raise MissingLoiError('No LOI provided.')
        self._check_loi(loi=loi, validate=False)
        with change_working_dir(path):
            if not os.path.exists(Manifest().manifest_filename):
                self.create_manifest(filename=filename)
            manifest = Manifest()
            manifest.from_file(manifest.manifest_filename)
            manifest.loi = loi
            manifest.to_file()
            filenames = manifest.metadata_filenames
            filenames.extend(manifest.data_filenames)
            filenames.append(manifest.manifest_filename)
            content = self._create_zip_archive(filenames)
        return self._server_upload(loi=loi,
                                   content=content)

    def _server_upload(self, loi='', content=None):  # noqa
        return {'data': True, 'all': True}

    def download(self, loi=''):
        """
        Download data from the datasafe.

        The LOI is checked for belonging to the datasafe. Further checks
        will be done on the server side, resulting in exceptions raised if
        there are some problems.

        Upon successful download data are checked for integrity and in case
        of possible data or metadata corruption a warning is issued. Take
        care of handling this warning downstream accordingly.


        Parameters
        ----------
        loi : :class:`str`
            LOI the data should be downloaded for

        Returns
        -------
        download_dir : :class:`str`
            Directory the data obtained from the datasafe have been saved to

        Warns
        -----
        UserWarning
            Issued if the consistency check fails, *i.e.* data or metadata
            may be corrupted

        Raises
        ------
        datasafe.loi.MissingLoiError
            Raised if no LOI is provided

        """
        if not loi:
            raise MissingLoiError('No LOI provided.')
        self._check_loi(loi=loi, validate=False)
        content = self._server_download(loi=loi)
        download_dir = tempfile.mkdtemp()
        with change_working_dir(download_dir):
            archive_file = 'archive.zip'
            with open(archive_file, "wb") as file:
                file.write(content)
            shutil.unpack_archive(archive_file, '.')
            os.remove(archive_file)
            manifest = Manifest()
            manifest.from_file(manifest.manifest_filename)
            integrity = manifest.check_integrity()
        if not all(integrity.values()):
            if not any(integrity.values()):
                message = 'Integrity check failed, data and metadata may be ' \
                          'corrupted.'
            elif integrity['data']:
                message = 'Integrity check failed, metadata may be corrupted.'
            else:
                message = 'Integrity check failed, data may be corrupted.'
            warnings.warn(message)
        return download_dir

    def _server_download(self, loi=''):  # noqa
        return self._create_zip_archive(filenames=[])

    def _check_loi(self, loi='', validate=True):
        """
        Check a LOI.

        Parameters
        ----------
        loi : :class:`str`
            LOI to be checked

        validate : :class:`bool`
            Whether to validate the LOI

            If False, the LOI will only be checked to be a datasafe LOI.

            Default: True

        Raises
        ------
        datasafe.loi.InvalidLoiError
            Raised if LOI is not a datasafe LOI/not valid

        """
        self.loi_parser.parse(loi)
        if self.loi_parser.type != 'ds':
            raise InvalidLoiError('LOI is not a datasafe LOI.')
        if validate:
            if not self._loi_checker.check(loi):
                raise InvalidLoiError('String is not a valid LOI.')

    def _create_zip_archive(self, filenames=None):
        with tempfile.TemporaryDirectory() as tmpdir:
            for filename in filenames:
                self._copy_file(filename, tmpdir)
            zip_archive = shutil.make_archive(base_name='dataset', format='zip',
                                              root_dir=tmpdir)
            with open(zip_archive, 'rb') as zip_file:
                contents = zip_file.read()
        return contents

    def _copy_file(self, source, destination):
        if os.path.isdir(source):
            os.mkdir(os.path.join(destination, source))
            for item in os.listdir(source):
                self._copy_file(os.path.join(source, item), destination)
        else:
            shutil.copy(source, destination)


class LocalClient(Client):
    """
    Client connecting locally directly within Python to a local server.

    Attributes
    ----------
    server : :class:`datasafe.server.Server`

        Datasafe server component to talk to. The server itself will
        communicate with a backend to do the actual storage.

    """

    def __init__(self):
        super().__init__()
        self.server = server.Server()

    def _server_create(self, loi=''):
        return self.server.new(loi=loi)

    def _server_upload(self, loi='', content=None):
        return self.server.upload(loi=loi, content=content)

    def _server_download(self, loi=''):
        return self.server.download(loi=loi)


class HTTPClient(Client):
    """
    Client connecting via HTTP to a remote server.

    Attributes
    ----------
    server_url : :class:`str`
        URL of a database HTTP server to connect to.

        Default: 'http://127.0.0.1:5000/'

    url_prefix : :class:`str`
        Prefix of the URLs appended to :attr:`server_url`

        Default: 'api/'

    """

    def __init__(self):
        super().__init__()
        self.server_url = 'http://127.0.0.1:5000/'
        self.url_prefix = 'api/'

    def _server_create(self, loi=''):
        response = requests.post(self.server_url + self.url_prefix + loi)
        return response.content.decode()

    def _server_upload(self, loi='', content=None):
        response = requests.put(self.server_url + self.url_prefix + loi,
                                data=content)
        if response.status_code == 404:
            raise InvalidLoiError(message=response.content.decode())
        if response.status_code == 400:
            if 'does not exist' in response.content.decode():
                raise LoiNotFoundError(message=response.content.decode())
        if response.status_code == 405:
            raise ExistingFileError(message=response.content.decode())
        return json.loads(response.content)

    def _server_download(self, loi=''):
        response = requests.get(self.server_url + self.url_prefix + loi)
        if response.status_code == 204:
            # Note: 204 returns no content (obviously!)
            raise MissingContentError('LOI does not have any content')
        if response.status_code == 404:
            if 'does not exist' in response.content.decode():
                raise LoiNotFoundError(message=response.content.decode())
            if 'not a valid LOI' in response.content.decode():
                raise InvalidLoiError(message=response.content.decode())
        return response.content
