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


    .. todo::
        Needs the following further methods:

        * get_index - returns list of paths in the datasafe
        * check_integrity - check stored checksums against actual files

    .. todo::
        Class needs to be moved to other module, probably
        :mod:`datasafe.server`.

    """
    def __init__(self):
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
