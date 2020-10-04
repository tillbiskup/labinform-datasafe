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
    def __init__(self):
        self.root_directory = ''
        self.path = ''

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
        if not path:
            raise MissingPathError
        os.makedirs(self.working_path(path))

    def exists(self, path=''):
        return os.path.exists(self.working_path(path))

    def isempty(self, path=''):
        if not os.path.exists(self.working_path(path)):
            raise FileNotFoundError
        return not os.listdir(self.working_path(path))

    def remove(self, path='', force=False):
        if force:
            shutil.rmtree(self.working_path(path))
        else:
            os.rmdir(self.working_path(path))

    def get_highest_id(self, path=''):
        directory_contents = os.listdir(self.working_path(path))
        # Important: Convert first to integers, then sort
        directory_contents = list(map(int, directory_contents))
        if not directory_contents:
            highest_id = 0
        else:
            highest_id = sorted(directory_contents)[-1]
        return highest_id

    def create_next_id(self, path=''):
        self.create(os.path.join(path, str(self.get_highest_id(path) + 1)))

    def deposit(self, path='', content=None):
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
        if not path:
            raise MissingPathError(message='No path provided.')
        tmpfile = tempfile.mkstemp()
        zip_archive = shutil.make_archive(base_name=tmpfile[1], format='zip',
                                          root_dir=self.working_path(path))
        with open(zip_archive, 'rb') as zip_file:
            contents = zip_file.read()
        os.remove(tmpfile[1] + '.zip')
        return contents


class OldGenerator:
    """
    Class for (physically) creating directories in the datasafe

    Attributes
    ----------
    path : :class:`str`
        temporary path within the datasafe to work on

    base_directory : :class:`str`
        base directory for the datasafe

    .. todo::
        Reimplement test-driven!

    """

    def __init__(self):
        self.path = ''
        self.base_directory = ''

    @property
    def working_path(self):
        """
        Full path to working directory in datasafe

        Returns
        -------
        full_path : :class:`str`
            full path to work on
        """
        full_path = os.path.join(self.base_directory, self.path)
        return full_path

    def find_last_id(self):
        """
        Find last (numeric) ID used in a particular directory of the datasafe

        Return last element of a sorted list of directory contents, assuming the
        directory to only contain subdirectories with numeric IDs.

        In case there is no numeric ID yet in the directory, it returns 0.

        Returns
        -------
        last_id : :class:`int`
            Highest ID in current directory

        """
        directory_contents = os.listdir(self.working_path)
        # Important: Convert first to integers, then sort
        directory_contents = list(map(int, directory_contents))
        if not directory_contents:
            highest_id = 0
        else:
            highest_id = sorted(directory_contents)[-1]
        return highest_id

    def create_new_directory(self, new_dir=''):
        """
        Create a new directory within the given path.

        Parameters
        ----------
        new_dir : :class:`str`
            Name of new directory to create

        """
        complete_path = os.path.join(self.working_path, new_dir)
        os.mkdir(path=complete_path)
        return

    def create_directory_for_new_dataset(self):
        """
        Create directory in datasafe for new dataset.

        Returns
        -------
        new_id : :class:`int`
            ID of newly created directory

        """
        highest_id = self.find_last_id()
        new_id = highest_id + 1
        self.create_new_directory(new_dir=str(new_id))
        return new_id

    def path_from_loi(self, loi):
        """
        Set path corresponding to LOI

        Parameters
        ----------
        loi : :class:`str`
            Lab Object Identifier (LOI)

        """
        short_loi = loi.split('/', 1)[1]
        self.path = os.sep.join(short_loi.split('/'))


if __name__ == '__main__':
    datasafe_root = '../tests/files/'
    working_dir = 'tmpsafe'

    irgendwas = StorageBackend()
    irgendwas.path = working_dir
    irgendwas.base_directory = datasafe_root

    last_id = irgendwas.find_last_id()
    print(last_id)

    print(irgendwas.create_directory_for_new_dataset())
