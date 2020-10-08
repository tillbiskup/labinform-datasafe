import os
import shutil
import tempfile


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingPathError(Error):
    """Exception raised when no path is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingContentError(Error):
    """Exception raised when no content is provided

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class StorageBackend:
    """
    File system backend for the datasafe, actually handling directories

    Attributes
    -----------
    root_directory : :class:`str`
        base directory for the datasafe

    manifest_filename : :class:`str`
        name of manifest file


    .. todo::
        Needs the following further methods:

        * check_integrity - check stored checksums against actual files

    .. todo::
        Class needs to be moved to other module, probably
        :mod:`datasafe.server`.

    """
    def __init__(self):
        self.checksum_filename = 'CHECKSUM'
        self.checksum_data_filename = 'CHECKSUM.data'
        self.manifest_filename = 'MANIFEST.yaml'
        self.root_directory = ''

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
        self.create(os.path.join(path, str(self.get_highest_id(path) + 1)))

    def deposit(self, path='', content=None):
        """
        Deposit data provided as content in directory corresponding to path

        Content is the byte representation of a ZIP archive containing the
        actual content. This byte representation is saved in a temporary
        file and afterwards unpacked in the directory corresponding to path.

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
        with open(tmpfile[1], "wb") as f:
            f.write(content)
        shutil.unpack_archive(tmpfile[1], self.working_path(path))
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
        with open(os.path.join(path, self.manifest_filename), 'r') as f:
            manifest_contents = f.read()
        return manifest_contents

    def get_checksum(self, path='', data=False):
        """
        Retrieve checksum for a dataset stored in path.

        To each dataset, two checksum files exist: one covering both,
        data and metadata, the other covering only the data. Usually,
        the former is returned. If you need to get the checksum covering the
        data only, set the second parameter ``data`` to ``True``.

        Parameters
        ----------
        path : :class:`str`
            path to the dataset the manifest should be retrieved for

        data : :class:`bool`
            switch for returning the checksum over data only

        Returns
        -------
        content : :class:`str`
            contents of the checksum file

        """
        if not path:
            raise MissingPathError(message='No path provided.')
        if not os.path.exists(path):
            raise OSError
        if data:
            checksum_filename = self.checksum_data_filename
        else:
            checksum_filename = self.checksum_filename
        if not os.path.exists(os.path.join(path, checksum_filename)):
            raise MissingContentError(message='No checksum file found.')
        with open(os.path.join(path, checksum_filename), 'r') as f:
            checksum_contents = f.read()
        return checksum_contents

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
        for root, dirs, files in os.walk(top):
            for dir_ in dirs:
                files_in_dir = os.listdir(os.path.join(root, dir_))
                if not files_in_dir or self.manifest_filename in files_in_dir:
                    paths.append(os.path.join(root, dir_).replace(os.path.join(
                        top, ''), ''))
        return paths

    def check_integrity(self, path=''):
        if self.manifest_filename not in os.listdir(path):
            raise MissingContentError(message='No manifest file found.')
        # Read (correct) manifest file into dict
        # retrieve list of data and metadata filenames from there
        # create checksums
        # compare checksums with stored ones
        #
        # TODO: Should better use a Manifest class that can be asked for the
        #  respective information
        integrity = {
            'data': '',
            'all': '',
            }
        return integrity
