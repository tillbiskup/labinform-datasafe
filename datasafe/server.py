"""
Server components of the LabInform datasafe.

Different server components can be distinguished:

* user-facing components
* backend components

Note that "user" is a broad term here, meaning any person and program
accessing the datasafe. In this respect, the clients contained in
:mod:`datasafe.client` are users as well.

The backend components deal with the actual storage of data (in the file
system) and the access to them.

Eventually, there will be a HTTP interface as user-facing component, probably
implemented using flask or similar, that can be run in a docker container or
on a local network.

But probably, there will be possibilities to access the datasafe locally as
well, without needing to fire up a HTTP server. This could even include a
CLI, although the CLI may be much more generic, allowing both, local and
HTTP access.

Some things that need to be decided about:

* Where to store configuration?

  At least the base directory for the datasafe needs to be defined in some way.

  Other configuration values could be the issuer (number after the "42." of
  a LOI)

Perhaps one could store the configuration in a separate configuration class
to start with and see how this goes...

"""

import os
import shutil
import tempfile

from datasafe import configuration
import datasafe.loi as loi_
from datasafe.manifest import Manifest
from datasafe.checksum import Generator
from datasafe.utils import change_working_dir


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


class Server:
    """
    Server part of the datasafe.

    The server interacts with the storage backend to store and retrieve
    contents and provides the user interface.

    It retrieves datasets, stores them and should check,
    whether its content is complete and not compromised.

    The transfer occurs as bytes of the zipped dataset that is received by
    the server, decoded, unzipped, and archived into the correct directory.

    Attributes
    ----------
    storage : :class:`StorageBackend`

    loi : :class:`datasafe.loi.Parser`

    """

    def __init__(self):
        self.storage = StorageBackend()
        self.loi = loi_.Parser()
        self._loi_checker = loi_.LoiChecker()

    def new(self, loi=''):
        """
        Create new LOI.

        The storage corresponding to the LOI will be created and the LOI
        returned if successful. This does, however, *not* add any data to
        the datasafe. Therefore, calling :meth:`new` will usually be
        followed by calling :meth:`upload` at some later point. On the other
        hand, before calling :meth:`upload`, you *need to* call :meth:`new`
        to create the new LOI storage space.

        Parameters
        ----------
        loi : :class:`str`
            LOI for which storage should be created

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
        date_checker = loi_.IsDateChecker()
        if date_checker.check(id_parts[1]):
            path = self.loi.separator.join(id_parts[0:3])
        else:
            path = self.loi.separator.join(id_parts[0:4])
        if not self.storage.exists(path):
            self.storage.create(path)
        new_path = self.storage.create_next_id(path)
        new_loi = self.loi.separator.join([
            self.loi.root_issuer_separator.join([self.loi.root,
                                                 self.loi.issuer]),
            self.loi.type, *new_path.split(os.sep)])
        return new_loi

    def upload(self, loi='', content=None):
        """
        Upload data to the datasafe.

        Data are upload as bytes of the zipped content (dataset).

        Parameters
        ----------
        loi : :class:`str`
            LOI the storage should be created for

        content : :class:`bytes`
            byte representation of a ZIP archive containing the contents to
            be extracted in the directory corresponding to path

        Raises
        ------
        datasafe.loi.MissingLoiError
            Raised if no LOI is provided

        ValueError
            Raised if storage corresponding to LOI does not exist

        FileExistsError
            Raised if storage corresponding to LOI is not empty

        """
        if not loi:
            raise loi_.MissingLoiError('No LOI provided.')
        self._check_loi(loi=loi)
        if not self.storage.exists(self.loi.id):
            raise ValueError('LOI does not exist.')
        if not self.storage.isempty(path=self.loi.id):
            raise FileExistsError('Directory not empty')
        self.storage.deposit(path=self.loi.id, content=content)

    def download(self, loi=''):
        """
        Download data from the datasafe.

        Parameters
        ----------
        loi : :class:`str`
            LOI the data should be downloaded for

        Returns
        -------
        content : :class:`bytes`
            byte representation of a ZIP archive containing the contents of
            the directory corresponding to path

        Raises
        ------
        datasafe.loi.MissingLoiError
            Raised if no LOI is provided

        ValueError
            Raised if storage corresponding to LOI does not exist or has no
            content

        """
        if not loi:
            raise loi_.MissingLoiError('No LOI provided.')
        self._check_loi(loi=loi)
        if not self.storage.exists(self.loi.id):
            raise ValueError('LOI does not exist.')
        if self.storage.isempty(self.loi.id):
            raise ValueError('LOI does not have content.')
        return self.storage.retrieve(path=self.loi.id)

    def _check_loi(self, loi='', validate=True):
        self.loi.parse(loi)
        if self.loi.type != 'ds':
            raise loi_.InvalidLoiError('LOI is not a datasafe LOI.')
        if validate:
            if not self._loi_checker.check(loi):
                raise loi_.InvalidLoiError('String is not a valid LOI.')


class StorageBackend:
    """
    File system backend for the datasafe, actually handling directories.

    The storage backend does not care at all about LOIs, but only operates
    on paths within the file system. As far as datasets are concerned,
    the backend requires a manifest file to accompany each dataset. However,
    it does *not* create such file. Furthermore, data are deposited (using
    :meth:`deposit`) and retrieved (using :meth:`retrieve`) as streams
    containing the contents of ZIP archives.

    Attributes
    ----------
    root_directory : :class:`str`
        base directory for the datasafe

    manifest_filename : :class:`str`
        name of manifest file

    """

    def __init__(self):
        self.config = configuration.StorageBackend()
        self.manifest_filename = \
            self.config.manifest_filename or Manifest().manifest_filename
        self.root_directory = self.config.root_directory or ''

    def working_path(self, path=''):
        """
        Full path to working directory in datasafe

        Returns
        -------
        working_path : :class:`str`
            full path to work on

        """
        return os.path.join(self.root_directory, path)

    def create(self, path=''):
        """
        Create directory for given path.

        Parameters
        ----------
        path : :class:`str`
            path to create directory for

        Raises
        ------
        datasafe.directory.MissingPathError
            Raised if no path is provided

        """
        if not path:
            raise MissingPathError
        os.makedirs(self.working_path(path))

    def exists(self, path=''):
        """
        Check whether given path exists

        Parameters
        ----------
        path : :class:`str`
            path to check

        """
        return os.path.exists(self.working_path(path))

    def isempty(self, path=''):
        """
        Check whether directory corresponding to path is empty

        Parameters
        ----------
        path : :class:`str`
            path to check

        Returns
        -------
        result : :class:`bool`
            Returns true if directory corresponding to ``path`` is empty.

        Raises
        ------
        FileNotFoundError
            Raised if no path is provided

        """
        if not os.path.exists(self.working_path(path)):
            raise FileNotFoundError
        return not os.listdir(self.working_path(path))

    def remove(self, path='', force=False):
        """
        Remove directory corresponding to path.

        Usually, non-empty directories will not be removed but raise an
        :class:`OSError` exception.

        Parameters
        ----------
        path : :class:`str`
            path that should be removed

        force : :class:`bool`
            set to `True` when non-empty directory should be removed

            default: `False`

        Raises
        ------
        OSError
            Raised if a non-empty directory should be removed and
            ``force`` is set to ``False``

        """
        if force:
            shutil.rmtree(self.working_path(path))
        else:
            os.rmdir(self.working_path(path))

    def get_highest_id(self, path=''):
        """
        Get number of subdirectory corresponding to path with highest number

        Return last element of a sorted list of directory contents, assuming the
        directory to only contain subdirectories with numeric IDs.

        In case there is no numeric ID yet in the directory, it returns 0.

        .. todo::
            Handle directories whose names are not convertible to integers


        Parameters
        ----------
        path : :class:`str`
            path to get subdirectory with highest number for

        Returns
        -------
        id : :class:`int`
            subdirectory with the highest number in the directory
            corresponding to ``path``

        """
        directory_contents = os.listdir(self.working_path(path))
        # Important: Convert first to integers, then sort
        directory_contents = list(map(int, directory_contents))
        if not directory_contents:
            highest_id = 0
        else:
            highest_id = sorted(directory_contents)[-1]
        return highest_id

    def create_next_id(self, path=''):
        """
        Create next subdirectory in directory corresponding to path

        Parameters
        ----------
        path : :class:`str`
            path the subdirectory should be created in

        """
        new_path = os.path.join(path, str(self.get_highest_id(path) + 1))
        self.create(new_path)
        return new_path

    def deposit(self, path='', content=None):
        """
        Deposit data provided as content in directory corresponding to path.

        Content is the byte representation of a ZIP archive containing the
        actual content. This byte representation is saved in a temporary
        file and afterwards unpacked in the directory corresponding to path.

        After depositing the content (including unzipping), the checksums in
        the manifest are checked for consistency with newly generated
        checksums, and in case of inconsistencies, an exception is raised.

        Parameters
        ----------
        path : :class:`str`
            path to deposit content to

        content : :class:`bytes`
            byte representation of a ZIP archive containing the contents to
            be extracted in the directory corresponding to path

        Raises
        ------
        datasafe.directory.MissingPathError
            Raised if no path is provided

        datasafe.directory.MissingContentError
            Raised if no content is provided

        """
        if not path:
            raise MissingPathError(message='No path provided.')
        if not content:
            raise MissingContentError(message='No content provided to deposit.')
        tmpfile = tempfile.mkstemp(suffix='.zip')
        with open(tmpfile[1], "wb") as file:
            file.write(content)
        shutil.unpack_archive(tmpfile[1], self.working_path(path))
        with change_working_dir(self.working_path(path)):
            manifest = Manifest()
            manifest.from_file(manifest.manifest_filename)
            manifest.check_integrity()
        os.remove(tmpfile[1])

    def retrieve(self, path=''):
        """
        Obtain data from directory corresponding to path

        The data are compressed as ZIP archive and the contents of the ZIP
        file is returned as bytes.

        Parameters
        ----------
        path : :class:`str`
            path the data should be retrieved for

        Returns
        -------
        content : :class:`bytes`
            byte representation of a ZIP archive containing the contents of
            the directory corresponding to path

        Raises
        ------
        datasafe.directory.MissingPathError
            Raised if no path is provided

        OSError
            Raised if path does not exist

        """
        if not path:
            raise MissingPathError(message='No path provided.')
        tmpfile = tempfile.mkstemp()
        zip_archive = shutil.make_archive(base_name=tmpfile[1], format='zip',
                                          root_dir=self.working_path(path))
        with open(zip_archive, 'rb') as zip_file:
            contents = zip_file.read()
        # noinspection PyTypeChecker
        os.remove(tmpfile[1] + '.zip')
        return contents

    def get_manifest(self, path=''):
        """
        Retrieve manifest of a dataset stored in path.

        Parameters
        ----------
        path : :class:`str`
            path to the dataset the manifest should be retrieved for

        Returns
        -------
        content : :class:`str`
            contents of the manifest file

        """
        if not path:
            raise MissingPathError(message='No path provided.')
        if not os.path.exists(path):
            raise OSError
        if not os.path.exists(os.path.join(path, self.manifest_filename)):
            raise MissingContentError(message='No MANIFEST file found.')
        with open(os.path.join(path, self.manifest_filename), 'r',
                  encoding='utf8') as file:
            manifest_contents = file.read()
        return manifest_contents

    def get_index(self):
        """
        Return list of paths to datasets

        Such a list of paths to datasets is pretty useful if one intends to
        check locally for existing LOIs (corresponding to paths in the
        datasafe).

        If a path has been created already, but no data yet saved in there,
        as may happen during an experiment to reserve the corresponding LOI,
        this path will nevertheless be included.

        Returns
        -------
        paths : :class:`list`
            list of paths to datasets

        """
        if self.root_directory:
            top = self.root_directory
        else:
            top = '.'
        paths = []
        for root, dirs, _ in os.walk(top):
            for dir_ in dirs:
                files_in_dir = os.listdir(os.path.join(root, dir_))
                if not files_in_dir or self.manifest_filename in files_in_dir:
                    paths.append(os.path.join(root, dir_).replace(os.path.join(
                        top, ''), ''))
        return paths

    def check_integrity(self, path=''):
        """
        Check integrity of dataset, comparing stored with generated checksums.

        To check the integrity of a dataset, the checksums stored within the
        manifest file will be compared to newly generated checksums over
        data and metadata together as well as over data alone.

        Parameters
        ----------
        path : :class:`str`
            path to the dataset the integrity should be checked for

        Returns
        -------
        integrity : :class:`dict`
            dict with fields ``data`` and ``all`` containing boolean values

        """
        if self.manifest_filename not in os.listdir(path):
            raise MissingContentError(message='No manifest file found.')
        manifest = Manifest()
        manifest.from_file(os.path.join(path, self.manifest_filename))
        return manifest.check_integrity()
